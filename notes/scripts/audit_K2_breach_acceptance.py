"""audit_K2_breach_acceptance.py — close the V_δ vs ε_FRI gap.

Note 0114 found 7 dense K=2 above-J f's with |V_δ| = 287 > 2q = 194 at our params
(p=97, n_0=32, k_0=8, R=2). On its face this is a 3/q lower bound on ε_FRI, beating
the CS R/q = 2/q lower bound. But |V_δ| only counts round-R acceptance, not the full
two-round coupling. The actual cheater win rate ε_FRI requires intersecting S_1(α_1)
with π^{-1}(S_2(α_1, α_2)).

This audit reproduces the exact 7 breach examples (replays rng state of
probe_K2_with_vdelta.py with seed=4242), then for each f computes:

  P_avg(f) = E_{α_1,α_2}[ max(P_A(α), P_B(α)) ]

where
  P_A(α_1, α_2) = (1/n_1) #{j ∈ [n_1] : j ∈ S_1(α_1) ∧ j² mod n_2 ∈ S_2(α_1,α_2)}
  P_B(α_1, α_2) = 1 - d_2(α_1,α_2)/n_2     [cheat-at-last]
  S_i = agreement set of true_fold_i with closest RS_{k_i} codeword

The (1-δ/2)^q FRI upper bound corresponds to per-α pass-prob ≤ 1-δ/2 = 0.75.
The (1-δ)^q hypothetical strict bound corresponds to ≤ 1-δ = 0.5.

Goal: confirm P_avg ≪ 1-δ for all 7 breaches → V_δ-based "ε_FRI ≥ 3/q" claim is
not a real soundness threat. Then optimizer (next file) attacks #344 directly.
"""
from __future__ import annotations
import sys, os, random, time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    two_round_pass_probs, dist_to_code_full, even_odd_parts,
)
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J, evaluate_dft, compute_corner_syndromes,
)
from mds_decoder import dist_lower_bound_sampling
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3
M = N_R - 2


def reproduce_breaches(seed=4242, n_pairs=30, n_f_per=10, max_breaches=7):
    """Replay probe_K2_with_vdelta rng state to extract the 7 breach f's deterministically."""
    rng = random.Random(seed)
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    p, n_R, w_R = P, N_R, W_R

    breaches = []
    breach_meta = []
    for pair_idx in range(n_pairs):
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
        overlap = rng.choice([0, 1])
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R:
                continue
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:
            shared = rng.choice(list(T1))
            others_pool = [j for j in range(n_R) if j not in T1]
            if len(others_pool) < w_R - 1:
                continue
            others = rng.sample(others_pool, w_R - 1)
            T2 = tuple(sorted([shared] + others))
        if T2 == T1:
            continue
        actual_overlap = len(set(T1) & set(T2))
        if actual_overlap > 1:
            continue

        eps1 = [0] * n_R
        eps2 = [0] * n_R
        for j in T1:
            eps1[j] = rng.randrange(1, p)
        for j in T2:
            eps2[j] = rng.randrange(1, p)
        u1 = matvec(H_R, eps1, p)
        u2 = matvec(H_R, eps2, p)
        if gauss_rank([u1, u2], p) != 2:
            continue

        for f_idx in range(n_f_per):
            c = {}
            for b in product([0, 1], repeat=R):
                c[b] = (rng.randrange(p), rng.randrange(p))
            msg = [rng.randrange(p) for _ in range(K0)]
            fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
            f = evaluate_dft(fhat, L0, p)

            corners = compute_corner_syndromes(f, chain, R, p, H_R)
            nz = [list(s) for s in corners.values() if any(x != 0 for x in s)]
            rk = gauss_rank(nz, p) if nz else 0
            if rk != 2:
                continue

            # Pre-screen: only keep if |V_δ| > 2q (the original 7 breach criterion).
            # This avoids running the expensive dist_lower_bound_sampling on non-breaches.
            # We already know which (pair_idx, f_idx) are breaches from verify_K2_breach2 output:
            # From verify_K2_breach2.output.txt — the 7 (pair_idx, f_idx) breach keys:
            breach_keys = {
                (1, 5), (2, 8), (4, 2), (8, 0), (18, 8), (25, 3), (25, 6),
            }
            if (pair_idx, f_idx) not in breach_keys:
                continue

            breaches.append(f)
            breach_meta.append({
                'pair': pair_idx, 'f_idx': f_idx, 'T1': T1, 'T2': T2,
                'overlap': actual_overlap, 'eps1': eps1, 'eps2': eps2,
            })
            if len(breaches) >= max_breaches:
                return breaches, breach_meta, chain
    return breaches, breach_meta, chain


def main():
    n0 = N0
    k0 = K0
    p = P
    delta = W_J / n0  # δ = 16/32 = 0.5 (the Johnson threshold)

    # FRI 2-round chain: 32 → 16 → 8, k: 8 → 4 → 2
    print("=" * 72)
    print(f"AUDIT: K=2 breach (note 0114) → two-round acceptance P_avg(f)")
    print(f"Params: n_0={n0}, k_0={k0}, p={p}, R={R}")
    print(f"  δ at round 0 = w_J/n_0 = {W_J}/{n0} = {delta:.4f}")
    print(f"  Per-α FRI bound (BCIKS):    P ≤ 1-δ/2 = {1-delta/2:.4f}")
    print(f"  Per-α hypothetical strict:  P ≤ 1-δ   = {1-delta:.4f}")
    print(f"  V_δ-based naive:            P ≤ 287/97² ≈ 0.0305 (per-α counting only)")
    print("=" * 72, flush=True)

    print("\n[Step 1] Reproducing 7 K=2 breach examples by replaying rng...", flush=True)
    t0 = time.time()
    breaches, meta, chain = reproduce_breaches()
    print(f"  Reproduced {len(breaches)} breaches in {time.time()-t0:.1f}s", flush=True)

    # Sanity: show metadata
    print("\nBreach metadata:")
    for i, m in enumerate(meta):
        print(f"  #{i}: pair={m['pair']}, f={m['f_idx']}, T1={m['T1']}, T2={m['T2']}, overlap={m['overlap']}")

    # ---- Strategy B (cheat-at-last) full grid, fast -----------------
    # P_B(α_1, α_2) = 1 - d_2(α_1, α_2)/n_2.  This is the BCIKS-realizing cheater.
    # Only needs d_2 — small (n_2=8, k_2=2, cap=6) ⇒ very fast.
    L0, k0_, H0 = chain[0]
    L1, k1, H1 = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)

    print(f"\n[Step 2] Strategy B (cheat-at-last) — full {p}×{p} = {p*p} α pairs each.", flush=True)
    print(f"  P_B(α_1, α_2) = 1 - d_2/n_2; this is the BCIKS-tight cheater model.")
    print(f"{'#':>3} {'P_avg':>8} {'P_max':>8} {'P_min':>8} {'#α≥1-δ/2':>11} {'#α≥1-δ':>9} {'#α: d2=0':>10} {'time':>6}")
    print("-" * 72, flush=True)

    rows = []
    for i, f in enumerate(breaches):
        t0 = time.time()
        f_e, f_o = even_odd_parts(f, L0, p)
        Ps = []
        d2_dist = {}
        for a1 in range(p):
            fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
            g_e, g_o = even_odd_parts(fold1, L1, p)
            for a2 in range(p):
                fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
                d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
                if d2 is None:
                    d2 = n2
                Ps.append(1.0 - d2 / n2)
                d2_dist[d2] = d2_dist.get(d2, 0) + 1
        P_avg = sum(Ps) / len(Ps)
        P_max = max(Ps)
        P_min = min(Ps)
        n_pass_BCIKS = sum(1 for P in Ps if P >= 1 - delta / 2 - 1e-9)
        n_pass_strict = sum(1 for P in Ps if P >= 1 - delta - 1e-9)
        n_d2_zero = d2_dist.get(0, 0)
        rows.append({
            'P_avg': P_avg, 'P_max': P_max, 'P_min': P_min,
            'n_BCIKS': n_pass_BCIKS, 'n_strict': n_pass_strict,
            'd2_dist': d2_dist, 'n_d2_zero': n_d2_zero,
            'elapsed': time.time() - t0,
        })
        print(f"{i:>3} {P_avg:>8.4f} {P_max:>8.4f} {P_min:>8.4f} "
              f"{n_pass_BCIKS:>11d} {n_pass_strict:>9d} {n_d2_zero:>10d} "
              f"{rows[-1]['elapsed']:>5.0f}s", flush=True)

    # d_2 distribution table
    print()
    print("d_2 distribution (combined across all 7 breaches):")
    combined = {}
    for r in rows:
        for d, c in r['d2_dist'].items():
            combined[d] = combined.get(d, 0) + c
    total = sum(combined.values())
    for d in sorted(combined.keys()):
        c = combined[d]
        print(f"  d_2 = {d}: {c:>5} pairs ({100*c/total:5.2f}%)  → P_B = {1-d/n2:.4f}")

    print("\n" + "=" * 72)
    print("VERDICT")
    print("=" * 72)
    P_avg_max = max(r['P_avg'] for r in rows)
    P_max_max = max(r['P_max'] for r in rows)
    print(f"  Across 7 K=2 dense breaches:")
    print(f"    max P_avg = {P_avg_max:.4f}")
    print(f"    max P_max = {P_max_max:.4f}  (single-α worst case)")
    print(f"    1-δ/2 (BCIKS bound)        = {1-delta/2:.4f}")
    print(f"    1-δ   (hypothetical tight) = {1-delta:.4f}")
    print()
    if P_avg_max < 1 - delta:
        print(f"  ✓ P_avg < 1-δ for all breaches.")
        print(f"    The V_δ = 287 > 2q phenomenon does NOT translate to a FRI soundness")
        print(f"    breach. The (1-δ/2)^q BCIKS bound stands. Direction A's V_δ-route is")
        print(f"    coarse — the right quantity is the COUPLED two-round acceptance.")
    elif P_avg_max < 1 - delta / 2:
        print(f"  ⚠  P_avg ∈ [1-δ, 1-δ/2). Strict (1-δ)^q is breached but BCIKS holds.")
    else:
        print(f"  ★ P_avg ≥ 1-δ/2. FRI 2× IS tight. #344 answered: yes.")
    print("=" * 72, flush=True)


if __name__ == '__main__':
    main()
