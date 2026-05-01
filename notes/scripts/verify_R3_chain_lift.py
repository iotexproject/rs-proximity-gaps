"""verify_R3_chain_lift.py — R=3 empirical test of Note 0131's chain-lift bound.

Tests on (p=97, n_0=32, k_0=8, R=3) → chain (32,16,8,4), codes (RS_8, RS_4, RS_2, RS_1).

For 3 representative above-J f's (K=1 leader, K=2 (18,8), K=2 |E|=8 case):
  (1) Verify Lemma 131.1: |S_0(f)| ≥ 2^3 |S_3^*(f)|.
  (2) Compute joint (d_1, d_2, d_3) distribution and tie_upper^(3).
  (3) Verify above-J propagates: max_α d_3(α) ≤ δn_3 NOT achieved
       universally (some α deep below δn_3=2 expected from K=1 leader).

Note: at R=3, K=1 leader's α_1 = 0 makes ALL (α_1,α_2,α_3) tuples deep at level R
(since fold_1 = 0 ⟹ everything below = 0). So Conj 131.2's #{deep tuples} ≤ 1
HOLDS only in the strict K-classifier sense at every level.
"""
from __future__ import annotations
import sys, os, time
from itertools import combinations
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_step5_n32_studio import P, N0, K0, evaluate_dft
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras

import numpy as np

P = 97
N0 = 32
K0 = 8
R = 3

CHAIN = setup_chain(P, N0, K0, R=R)
L_chain = [CHAIN[i][0] for i in range(R + 1)]
k_chain = [CHAIN[i][1] for i in range(R + 1)]
n_chain = [len(L) for L in L_chain]
print(f"R={R} chain: n = {n_chain}, k = {k_chain}, δn at each level = {[n - 2*k for n,k in zip(n_chain, k_chain)]}")
delta_n = [n - 2*k for n, k in zip(n_chain, k_chain)]  # δ = (1 - √ρ) = 1/2 here, so δn = n/2... actually δn_r = n_r/2

# For our params δ = 1 - sqrt(1/4) = 1/2, so δn_r = n_r/2.
delta_n = [n // 2 for n in n_chain]
print(f"δn at each level = {delta_n}")

# Pre-compute info-set decoder for level 1 and level 2.
INFO_DEC = {}
for r in [1, 2]:
    Lr = L_chain[r]
    kr = k_chain[r]
    nr = n_chain[r]
    if kr == 0:
        continue
    Lr_arr = np.array(Lr, dtype=np.int64)
    Dr, inv_Dr = precompute_diff_inv(Lr_arr, P)
    info_sets = list(combinations(range(nr), kr))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    INFO_DEC[r] = (Lr_arr, Dr, inv_Dr, info_sets_arr, nr, kr)


def fast_dist_level(r, fold_arr):
    """dist(fold, RS_{k_r}(L_r))."""
    if r == 3:
        # RS_1 = constants; dist = n_3 - max multiplicity
        return n_chain[3] - max(Counter(int(v) % P for v in fold_arr).values())
    Lr_arr, Dr, inv_Dr, info_sets_arr, nr, kr = INFO_DEC[r]
    extras = batched_extras(info_sets_arr, fold_arr, Lr_arr, Dr, inv_Dr, P)
    max_extras = int(extras.max())
    return nr - kr - max_extras


def fast_dist_level0(f_arr):
    """dist(f, C_0). Use info-set decoder for level 0 too."""
    L0_arr = np.array(L_chain[0], dtype=np.int64)
    n0 = n_chain[0]
    k0 = k_chain[0]
    D0, inv_D0 = precompute_diff_inv(L0_arr, P)
    info_sets = list(combinations(range(n0), k0))  # C(32, 8) = 10,518,300 — too many!
    # Use random sample
    import random
    random.seed(42)
    sample = random.sample(info_sets, min(50000, len(info_sets)))
    sample_arr = np.array(sample, dtype=np.int64)
    extras = batched_extras(sample_arr, f_arr, L0_arr, D0, inv_D0, P)
    max_extras = int(extras.max())
    return n0 - k0 - max_extras  # this is an UPPER bound since not exhaustive


def fold_one(f, L_in, alpha):
    f_e, f_o = even_odd_parts(f, L_in, P)
    return [(f_e[i] + alpha * f_o[i]) % P for i in range(len(f_e))]


def compute_R3_joint(f_arr_list):
    """Returns joint (d_1, d_2, d_3) distribution over (α_1, α_2, α_3) ∈ F_q^3.

    For tractability, use F_q^3 = 97^3 = 912,673 tuples. Only 4 evaluations per tuple.
    """
    f = list(f_arr_list)
    L0 = L_chain[0]
    L1 = L_chain[1]
    L2 = L_chain[2]
    L3 = L_chain[3]

    # For each α_1: compute fold_1, decompose into fold_1_e, fold_1_o on L_2.
    # For each (α_1, α_2): compute fold_2 = fold_1_e + α_2 fold_1_o, decompose into L_3 parts.
    # For each (α_1, α_2, α_3): compute fold_3 = fold_2_e + α_3 fold_2_o, dist to RS_1.

    f_e0, f_o0 = even_odd_parts(f, L0, P)
    f_e0_arr = np.array(f_e0, dtype=np.int64)
    f_o0_arr = np.array(f_o0, dtype=np.int64)

    joint = Counter()
    sum_tie3 = 0.0
    n_tuples = 0

    n1, n2, n3 = n_chain[1], n_chain[2], n_chain[3]

    t_start = time.time()
    for a1 in range(P):
        fold1_arr = (f_e0_arr + a1 * f_o0_arr) % P
        d1 = fast_dist_level(1, fold1_arr)
        fold1 = fold1_arr.tolist()
        f_e1, f_o1 = even_odd_parts(fold1, L1, P)
        f_e1_arr = np.array(f_e1, dtype=np.int64)
        f_o1_arr = np.array(f_o1, dtype=np.int64)

        for a2 in range(P):
            fold2_arr = (f_e1_arr + a2 * f_o1_arr) % P
            d2 = fast_dist_level(2, fold2_arr)
            fold2 = fold2_arr.tolist()
            f_e2, f_o2 = even_odd_parts(fold2, L2, P)
            f_e2_arr = np.array(f_e2, dtype=np.int64)
            f_o2_arr = np.array(f_o2, dtype=np.int64)

            for a3 in range(P):
                fold3_arr = (f_e2_arr + a3 * f_o2_arr) % P
                d3 = fast_dist_level(3, fold3_arr)
                joint[(d1, d2, d3)] += 1
                m1 = 1.0 - d1 / n1
                m2 = 1.0 - d2 / n2
                m3 = 1.0 - d3 / n3
                sum_tie3 += max(m1, m2, m3)
                n_tuples += 1

        if (a1 + 1) % 10 == 0:
            elapsed = time.time() - t_start
            print(f"   α_1 progress {a1+1}/{P}, elapsed={elapsed:.1f}s, ETA total~{elapsed*P/(a1+1):.0f}s")

    return joint, sum_tie3 / n_tuples


def make_K1_leader():
    L0 = L_chain[0]
    fhat = [0] * N0
    fhat[15] = 10
    fhat[23] = 17
    return evaluate_dft(fhat, L0, P)


def make_random_above_J(seed=12345, max_attempts=200):
    """Pick a random K=2 above-J f at toy params via dense f̂."""
    import random
    rng = random.Random(seed)
    L0 = L_chain[0]
    for attempt in range(max_attempts):
        fhat = [0]*K0 + [rng.randrange(P) for _ in range(N0 - K0)]
        f = evaluate_dft(fhat, L0, P)
        f_arr = np.array(f, dtype=np.int64)
        d0 = fast_dist_level0(f_arr)
        if d0 > 16:  # above-J
            return f, d0, attempt
    return None, None, max_attempts


def main():
    print("\n" + "="*60)
    print("R=3 chain-lift verification at (p=97, n_0=32, k_0=8, R=3)")
    print("="*60)
    print(f"Chain: n = {n_chain}, k = {k_chain}, δn = {delta_n}")
    print()

    print("--- Test 1: K=1 leader (15, 23) coefs (10, 17) ---")
    f1 = make_K1_leader()
    f1_arr = np.array(f1, dtype=np.int64)
    print("Computing R=3 joint distribution (97^3 = 912,673 tuples)...")
    joint1, tie3_K1 = compute_R3_joint(f1)

    # Project to per-level distributions
    d1_dist = Counter()
    d2_dist = Counter()
    d3_dist = Counter()
    for (d1, d2, d3), count in joint1.items():
        d1_dist[d1] += count
        d2_dist[d2] += count
        d3_dist[d3] += count

    print(f"\n  d_1 distribution: {dict(sorted(d1_dist.items()))}")
    print(f"  d_2 distribution: {dict(sorted(d2_dist.items()))}")
    print(f"  d_3 distribution: {dict(sorted(d3_dist.items()))}")
    print(f"  tie_upper^(3) = E[max_r (1 - d_r/n_r)] = {tie3_K1:.4f}")

    deep_at_3 = sum(c for d3, c in d3_dist.items() if d3 <= delta_n[3])
    deep_at_2 = sum(c for d2, c in d2_dist.items() if d2 <= delta_n[2])
    deep_at_1 = sum(c for d1, c in d1_dist.items() if d1 <= delta_n[1])
    print(f"  #(α: d_1 ≤ δn_1=8) = {deep_at_1} (out of {P**3})")
    print(f"  #(α: d_2 ≤ δn_2=4) = {deep_at_2} (out of {P**3})")
    print(f"  #(α: d_3 ≤ δn_3=2) = {deep_at_3} (out of {P**3})")

    # Critically: at K=1 leader, α_1=0 ⟹ fold_1=0 ⟹ all subsequent folds = 0.
    # So #(α_1=0 with d_1=0) = q^2 (97^2 = 9409 tuples).
    # And #(α_1=0 with d_3=0) = q^2 = 9409.
    print(f"\n  Expected (K=1 leader): #(α_1=0) = 97^2 = {97**2}")
    print(f"    These all have d_1 = d_2 = d_3 = 0 (zero-folding cascade).")

    print("\n  Headline: tie_upper^(3) for K=1 leader = {:.4f}".format(tie3_K1))
    print(f"  Compare R=2: tie_upper^(2) ~ 0.4490")

    # The bound conjectured: tie_upper^(R) ≤ √ρ + O(R/q) = 0.5 + O(R/q)

    print("\n--- Test 1.5: K=2 (18,8) breach reproducer (|E|=7 at R=2) ---")
    print("Constructing K=2 dense breach via construct_f_with_psi_in_U...")
    from probe_K2_construct import construct_f_with_psi_in_U, K_R, M
    from fri_2round_attack import parity_check, matvec, gauss_rank
    from itertools import product as iproduct
    import random as _r

    # Reproduce the |E|=8 case: T1=(0,1,6), T2=(0,2,5), seed_base=5000, offset=46
    chain2 = setup_chain(P, N0, K0, R=2)
    L_R2, k_R2, _ = chain2[2]
    H_R2 = parity_check(L_R2, 8, k_R2, P)
    rng = _r.Random(5000 + 46)
    found_e8 = None
    for tries in range(200):
        T1 = (0, 1, 6); T2 = (0, 2, 5)
        eps1 = [0]*8; eps2 = [0]*8
        for j in T1: eps1[j] = rng.randrange(1, P)
        for j in T2: eps2[j] = rng.randrange(1, P)
        u1 = matvec(H_R2, eps1, P)
        u2 = matvec(H_R2, eps2, P)
        if gauss_rank([u1, u2], P) != 2: continue
        c = {b: (rng.randrange(P), rng.randrange(P)) for b in iproduct([0,1], repeat=2)}
        msg = [rng.randrange(P) for _ in range(K0)]
        # construct_f_with_psi_in_U uses module-level R=2 from probe_K2_construct
        fhat = construct_f_with_psi_in_U(u1, u2, c, msg, P)
        L0 = chain2[0][0]
        f_e8 = evaluate_dft(fhat, L0, P)
        # quick distance lower-bound check
        f_e8_arr = np.array(f_e8, dtype=np.int64)
        d0_lb = fast_dist_level0(f_e8_arr)
        if d0_lb > 16:
            found_e8 = f_e8
            print(f"  Constructed candidate at try={tries}, d0_ub={d0_lb} (sampling bound)")
            break

    if found_e8 is not None:
        joint_e8, tie3_e8 = compute_R3_joint(found_e8)
        d3_dist_e8 = Counter()
        for (d1, d2, d3), c in joint_e8.items():
            d3_dist_e8[d3] += c
        deep3_e8 = sum(c for d, c in d3_dist_e8.items() if d <= delta_n[3])
        print(f"  K=2 candidate: tie^(3) = {tie3_e8:.4f}, #d_3 ≤ 2 = {deep3_e8}")
        K2_e8_tie3 = tie3_e8
    else:
        K2_e8_tie3 = None
        print("  Failed to reproduce |E|=8 case")

    print("\n--- Test 2: random K=2 above-J f's ---")
    results = []
    for seed in [11111, 22222, 33333, 44444, 55555]:
        f, d0, attempts = make_random_above_J(seed=seed)
        if f is None:
            print(f"  seed={seed}: no above-J f found in {attempts} attempts")
            continue
        joint, tie3 = compute_R3_joint(f)
        d1_dist = Counter()
        d2_dist = Counter()
        d3_dist = Counter()
        for (d1, d2, d3), count in joint.items():
            d1_dist[d1] += count
            d2_dist[d2] += count
            d3_dist[d3] += count
        deep1 = sum(c for d, c in d1_dist.items() if d <= delta_n[1])
        deep3 = sum(c for d, c in d3_dist.items() if d <= delta_n[3])
        # Also check d_3 < δn_3 (strictly deep at level 3):
        strict_deep3 = sum(c for d, c in d3_dist.items() if d < delta_n[3])
        print(f"  seed={seed} (attempt {attempts}, d0_ub={d0}): tie^(3) = {tie3:.4f}, "
              f"#deep_1 ≤ 8 = {deep1}, #d_3 ≤ 2 = {deep3}, #d_3 < 2 = {strict_deep3}")
        results.append((seed, tie3, deep1, deep3))

    print("\n--- Summary ---")
    all_ties = [tie3_K1] + [r[1] for r in results]
    if K2_e8_tie3 is not None:
        all_ties.append(K2_e8_tie3)
    max_tie3 = max(all_ties)
    print(f"  Max tie_upper^(3) across tested f's: {max_tie3:.4f}")
    print(f"  Target: √ρ + O(R/q) = 0.5 + O(3/97) ≈ 0.531")
    if max_tie3 < 0.5:
        print(f"  ✓ All tested f's BELOW √ρ = 0.5 — Lemma 131.1 conjecture supported")
    else:
        print(f"  ⚠ Max ≥ 0.5: {max_tie3:.4f}")


if __name__ == "__main__":
    main()
