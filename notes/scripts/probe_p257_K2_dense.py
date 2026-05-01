"""probe_p257_K2_dense.py — test Bezout prediction at larger q.

Hypothesis (from note 0115): if ε_FRI ≈ poly(R)/q^R (not nR/q), then increasing q
should leave the per-α d_2 distribution roughly invariant (chain dims unchanged) but
the BOOST from #(α: d_2=0) ≤ R perfect-codeword α should shrink as R/q² → 0.

At p=97 (q²=9409): K=2 dense overlap=1 caps at P_avg = 0.385, with #(d_2=0) ∈ {0,2}.
At p=257 (q²=66049): predicted P_avg cap should drop because:
  - Bezout-bounded #(d_2=0) ≤ R = 2 contributes ≤ 2/q² ≈ 0.00003 vs 2/9409 ≈ 0.0002
  - "Wide-decoder wins" (d_2 ≤ w_R = 3) likewise scale as O(R · n_R^{w_R})/q^something
  - Baseline (d_2 ∈ {5,6}) → P_B ≈ 0.30 — q-independent

If P_avg cap shrinks from 0.385 → ~0.27 at p=257 → strong signal that #343 has yes
answer (i.e., (1-δ)^q achievable, true ε_FRI ~ poly(R)/q^R).

If P_avg cap stays at ~0.38 → BCIKS bound might be tight after all, #344 has yes
answer.

Each P_avg eval at p=257 costs ~p²·4ms ≈ 280s (vs 40s at p=97). Budget: 6 examples
× 5min = 30min.

Usage: python3 probe_p257_K2_dense.py [n_examples=6] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time, math
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full,
)
from mds_decoder import dist_lower_bound_sampling
from probe_K2_construct import construct_f_with_psi_in_U


# Reuse the SAME chain dims (n_0=32, k_0=8, R=2, n_R=8, w_R=3) — only q scales.
N0 = 32
K0 = 8
R = 2
N_R = N0 // (2**R)            # 8
W_J = int((1 - math.sqrt(K0/N0)) * N0)  # 16
W_R = 3


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def P_avg_strategy_B(f, chain, p):
    """Full F_p² grid, Strategy B: P_B(α) = 1 - d_2(α)/n_2."""
    L0, _, _ = chain[0]
    L1, _, _ = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    total_d2 = 0
    n_pairs = 0
    d2_dist = {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            total_d2 += d2
            n_pairs += 1
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
    P_avg = 1.0 - (total_d2 / n_pairs) / n2
    return P_avg, d2_dist


def build_K2_overlap1(rng, p, n_R, w_R, H_R):
    """Build a K=2 dense construction with overlap=1 (the empirical-best mode)."""
    T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
    shared = rng.choice(list(T1))
    others_pool = [j for j in range(n_R) if j not in T1]
    others = rng.sample(others_pool, w_R - 1)
    T2 = tuple(sorted([shared] + others))
    if T2 == T1:
        return None
    eps1 = [0] * n_R
    eps2 = [0] * n_R
    for j in T1:
        eps1[j] = rng.randrange(1, p)
    for j in T2:
        eps2[j] = rng.randrange(1, p)
    u1 = matvec(H_R, eps1, p)
    u2 = matvec(H_R, eps2, p)
    if gauss_rank([u1, u2], p) != 2:
        return None
    return T1, T2, eps1, eps2, u1, u2


def main():
    p = 257
    n_examples = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026

    delta = W_J / N0  # 0.5
    n0, k0 = N0, K0

    print("=" * 72)
    print(f"P_avg at p=257 — Bezout prediction test (K=2 dense, overlap=1)")
    print(f"  Chain: n_0={n0}, k_0={k0}, R={R}, n_R={N_R}, w_R={W_R}, w_J={W_J}, δ={delta:.4f}")
    print(f"  q² = {p*p} pairs (vs 9409 at p=97 — {p*p/9409:.1f}× more)")
    print(f"  Bezout cap: #(α: d_2=0) ≤ R = {R}, contributes ≤ R/q² = {R/(p*p):.6f}")
    print(f"  Reference (p=97): K=2 ov=1 → P_avg cap = 0.3852")
    print(f"  Prediction: at p=257, P_avg → baseline only ≈ 0.27 (Bezout boost vanishes)")
    print("=" * 72, flush=True)

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)

    rng = random.Random(seed)
    results = []
    n_above_j = 0
    n_tries = 0
    t_start = time.time()

    while n_above_j < n_examples and n_tries < 100:
        n_tries += 1
        res = build_K2_overlap1(rng, p, N_R, W_R, H_R)
        if res is None:
            continue
        T1, T2, eps1, eps2, u1, u2 = res
        c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
        msg = [rng.randrange(p) for _ in range(K0)]
        fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
        f = evaluate_dft(fhat, L0, p)
        d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed + n_tries)
        if d_lb <= W_J:
            continue
        n_above_j += 1
        t0 = time.time()
        P_avg, d2_dist = P_avg_strategy_B(f, chain, p)
        eval_time = time.time() - t0
        n_zero = d2_dist.get(0, 0)
        n_le_3 = sum(c for d, c in d2_dist.items() if d <= 3)
        results.append({
            'try': n_tries, 'T1': T1, 'T2': T2, 'd_lb': d_lb,
            'P_avg': P_avg, 'n_zero': n_zero, 'n_le_3': n_le_3,
            'd2_dist': dict(d2_dist), 'time': eval_time,
        })
        print(f"  ex={n_above_j}/{n_examples} try={n_tries} T1={T1} T2={T2} d_lb={d_lb}: "
              f"P_avg={P_avg:.4f}  d2=0:{n_zero}  d2≤3:{n_le_3}  ({eval_time:.0f}s, "
              f"total {(time.time()-t_start)/60:.1f}min)", flush=True)

    print()
    print("=" * 72)
    print(f"RESULTS (p={p}, {len(results)} above-J K=2 dense overlap=1 examples):")
    print("=" * 72)
    if results:
        P_avg_list = [r['P_avg'] for r in results]
        n_zero_list = [r['n_zero'] for r in results]
        print(f"  max P_avg = {max(P_avg_list):.4f}")
        print(f"  min P_avg = {min(P_avg_list):.4f}")
        print(f"  mean P_avg = {sum(P_avg_list)/len(P_avg_list):.4f}")
        print(f"  max #(α: d_2=0) = {max(n_zero_list)}  (Bezout cap = R = {R})")
        print()
        print(f"  Reference at p=97 (K=2 ov=1): max P_avg = 0.3852  (#(d_2=0) ∈ {{0,2}})")
        print(f"  Δ P_avg = {max(P_avg_list) - 0.3852:+.4f}")
        print()

        # combined d_2 dist
        combined = {}
        for r in results:
            for d, c in r['d2_dist'].items():
                combined[d] = combined.get(d, 0) + c
        total = sum(combined.values())
        print(f"  d_2 distribution (combined {len(results)} f's, {total} α-pairs):")
        for d in sorted(combined.keys()):
            c = combined[d]
            print(f"    d_2 = {d}: {c:>7} ({100*c/total:5.2f}%)  → P_B = {1-d/N_R:.4f}")
        print()
        if max(P_avg_list) < 0.35:
            print("  ★ P_avg cap DROPPED — Bezout prediction confirmed.")
            print("    Bezout-style ε_FRI ≤ poly(R)/q^R is the correct upper-bound shape.")
            print("    Strong signal: published nR/|F| bound is loose by O(n) factor.")
            print("    Direction toward #343 'yes' (FRI (1-δ)^q achievable).")
        elif max(P_avg_list) >= 0.38:
            print("  ⚠ P_avg cap stable at ~0.38 — Bezout argument incomplete.")
            print("    Per-α boost is q-INSENSITIVE somehow → BCIKS bound likely tight.")
        else:
            print(f"  ◎ P_avg cap = {max(P_avg_list):.4f} — partial shrink, mixed signal.")
    print("=" * 72, flush=True)


if __name__ == '__main__':
    main()
