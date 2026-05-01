"""fri_3round_attack.py — Issue #344 follow-up: 3-round FRI cheating prob.

Test whether the empirical (1-δ)^q rate (from 2-round, n=16,32) holds at R=3.

For n_0 = 32, k_0 = 16: chain L_0(32) → L_1(16) → L_2(8) → L_3(4).
Code RS_2(L_3, size 4). Cheater commits g_3 = closest codeword to true_fold_3.

Per-query pass = 1 - d_3 / n_3, where d_3 = dist(true_fold_3, RS_2(L_3)).

Compare to:
  paper bound (1-δ/2)^q  baseline
  zero-loss (1-δ)^q
  empirical typical
"""

from __future__ import annotations
import sys
import time
import random
from math import comb

# Reuse infrastructure from fri_2round_attack
sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, dist_to_code_full, even_odd_parts, true_dist,
    sample_far_input, monomial_inputs, R_round_pass_probs,
    poly_eval_horner,
)


def main():
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 97
    delta_num = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    n_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    mode = sys.argv[4] if len(sys.argv) > 4 else 'random'
    n0 = int(sys.argv[5]) if len(sys.argv) > 5 else 32
    k0 = int(sys.argv[6]) if len(sys.argv) > 6 else 16
    R = int(sys.argv[7]) if len(sys.argv) > 7 else 3

    delta = delta_num / n0
    rho = k0 / n0
    delta_J = 1 - rho ** 0.5

    print(f"=" * 70, flush=True)
    print(f"FRI {R}-round attack: n0={n0}, k0={k0}, p={p}, R={R}, δ={delta:.4f} (δ_J={delta_J:.4f})", flush=True)
    print(f"  Per-paper bound (1-δ/2)^q baseline: 1-δ/2 = {1 - delta/2:.4f}", flush=True)
    print(f"  Zero-loss target  (1-δ)^q baseline:  1-δ   = {1 - delta:.4f}", flush=True)
    print(f"=" * 70, flush=True)

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    omega = L0[1]
    n_R = len(chain[R][0])
    k_R = chain[R][1]
    print(f"  Chain: " + " → ".join([f"L_{i}({len(chain[i][0])},k={chain[i][1]})" for i in range(R + 1)]), flush=True)
    print(f"  Final: L_{R} size {n_R}, RS_{k_R}", flush=True)

    rng = random.Random(2026)

    inputs = []
    if mode == 'random':
        w_target = delta_num + 1
        for trial in range(n_samples):
            f, _ = sample_far_input(p, n0, k0, w_target, rng, chain, verify=False)
            inputs.append((f"random+wt{w_target}", f))
    elif mode == 'monomial':
        inputs = monomial_inputs(p, n0, omega, deg_range=(k0, n0))[:n_samples or 5]
    else:
        raise ValueError(f"unknown mode {mode}")

    # Sample-grid count: for R=3 at p=97, p^R = 9.1e5 too many; use 6 per dim = 216 tuples.
    sample_alphas = 6 ** R if n0 > 16 or R >= 3 else None

    summaries = []
    t_start = time.time()
    for trial, (label, f) in enumerate(inputs):
        print(f"\n--- trial {trial} [{label}]", flush=True)
        t0 = time.time()
        results = R_round_pass_probs(f, chain, p, R=R, sample_alphas=sample_alphas, rng=rng)
        elapsed_trial = time.time() - t0
        d_Rs = [r[1] for r in results]
        Ps = [r[2] for r in results]
        d_R_min = min(d_Rs)
        d_R_max = max(d_Rs)
        P_avg = sum(Ps) / len(Ps)
        P_max = max(Ps)
        P_min = min(Ps)
        # Histogram of d_R
        hist = {}
        for d in d_Rs:
            hist[d] = hist.get(d, 0) + 1
        # P_typical: exclude the bottom 10% by d_R (the "bad rounds")
        d_R_sorted = sorted(d_Rs)
        thresh = max(1, int(0.1 * len(d_Rs)))
        d_R_typ = d_R_sorted[thresh]
        typical_Ps = [r[2] for r in results if r[1] >= d_R_typ]
        P_typical = max(typical_Ps) if typical_Ps else P_avg
        print(f"  d_R range [{d_R_min}, {d_R_max}] / {n_R}, hist {dict(sorted(hist.items()))}", flush=True)
        print(f"  P_avg = {P_avg:.4f}, P_max = {P_max:.4f}, P_min = {P_min:.4f}", flush=True)
        print(f"  P_typical = {P_typical:.4f} (d_R ≥ {d_R_typ})", flush=True)
        print(f"  elapsed: {elapsed_trial:.1f}s", flush=True)
        summaries.append({
            "label": label, "P_avg": P_avg, "P_max": P_max, "P_typical": P_typical,
            "d_R_min": d_R_min, "d_R_max": d_R_max, "hist": hist,
        })

    elapsed = time.time() - t_start
    print(f"\n{'='*70}", flush=True)
    print(f"SUMMARY ({len(summaries)} inputs, {elapsed:.1f}s, {sample_alphas or 'full'} α-tuples each)", flush=True)
    print(f"{'='*70}", flush=True)
    if summaries:
        print(f"  Theoretical baselines: (1-δ/2)={1-delta/2:.4f}, (1-δ)={1-delta:.4f}", flush=True)
        worst_Pavg = max(s["P_avg"] for s in summaries)
        worst_Pmax = max(s["P_max"] for s in summaries)
        worst_Ptyp = max(s["P_typical"] for s in summaries)
        print(f"  Worst-case P_avg     (over f): {worst_Pavg:.4f}", flush=True)
        print(f"  Worst-case P_max     (over f): {worst_Pmax:.4f}", flush=True)
        print(f"  Worst-case P_typical (over f): {worst_Ptyp:.4f}", flush=True)
        if worst_Ptyp >= 1 - delta / 2 - 1e-6:
            print(f"  ⇒ {R}-round: 2× tight at this n", flush=True)
        elif worst_Ptyp <= 1 - delta + 1e-6:
            print(f"  ⇒ {R}-round: zero-loss achievable, bound improvable", flush=True)
        else:
            c_eff = delta / (1 - worst_Ptyp) if worst_Ptyp < 1 else float('inf')
            print(f"  ⇒ {R}-round effective c ≈ {c_eff:.3f}", flush=True)


if __name__ == "__main__":
    main()
