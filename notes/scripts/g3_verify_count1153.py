"""g3_verify_count1153.py — independently verify the count=1153 witness at q=1153.

The sweep g3_cyclotomic_sweep.py reported (idx 25 in receive order):
  pos=[19, 20, 23], dist=21, count=1153 (every α ∈ F_q is bad)

If real, this BREAKS:
  - Conjecture D (bad-α set as multiplicative coset): impossible since {0,...,q-1}
    contains 0, can't be β + λ·H for any subgroup H ≤ F_q*.
  - PR #373's M_aff(f)·(n_1 - s + 1) bound: would require M_aff ≥ 128.

Verify carefully:
1. Reproduce candidate list with seed=3179 (=2026+1153) — this is DETERMINISTIC
   even though sweep used imap_unordered (pool order ≠ receive order).
2. Find candidates with positions={19,20,23}.
3. For each, recompute:
   - dist(f, RS_8) on L_0 (independent path)
   - dist(f_e, RS_4) on L_1 (single-α=0 sanity)
   - dist(fold_α, RS_4) for ALL α in F_q (full distance distribution)
4. Print distance histogram + bad-α set explicitly.

Sanity expectations:
  - α=0 → fold_0 = c_20·y^10. By BCH bound, weight ≥ 7 for any (fold_0 - codeword).
    So dist(c_20 y^10, RS_4) ≥ 7. 8 is achievable IF 6 polynomial constraints on
    8-subset σ_k(S) are satisfied (~1/q^4 probability). For RANDOM c_20 it should
    be rare.
  - α generic → fold_α has DFT support {9,10,11}, BCH weight ≥ 6.

Single-threaded; no multiprocessing. Should run in <2 minutes for the verification.
"""
import sys, os, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def generate_candidates(p, n0, k0, n_candidates, seed):
    rng = random.Random(seed)
    out = []
    while len(out) < n_candidates:
        n_pos = rng.choice([3, 4, 5, 6, 7])
        positions = sorted(rng.sample(range(k0, n0), n_pos))
        has_even = any(j % 2 == 0 for j in positions)
        has_odd = any(j % 2 == 1 for j in positions)
        if not (has_even and has_odd):
            continue
        coeffs = [rng.randrange(1, p) for _ in positions]
        out.append((tuple(positions), tuple(coeffs)))
    return out


def dist_to_rs(f_arr, L_arr, n, k, D, inv_D, p):
    info_sets = list(combinations(range(n), k))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    extras = batched_extras(info_sets_arr, f_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def main():
    p = 1153
    n0, k0 = 32, 8
    n_candidates = 300
    seed = 2026 + p

    print(f"=== Reproducing candidates: q={p}, seed={seed} ===")
    candidates = generate_candidates(p, n0, k0, n_candidates, seed)
    target = (19, 20, 23)
    matches = [(i, c) for i, c in enumerate(candidates) if c[0] == target]
    print(f"Candidates with pos={target}: {len(matches)}")
    for i, (pos, coeffs) in matches:
        print(f"  idx {i}: coeffs={coeffs}")
    if not matches:
        print("FATAL: no exact match; partial:")
        for i, (pos, coeffs) in enumerate(candidates):
            if set([19, 20, 23]).issubset(pos):
                print(f"  idx {i}: pos={pos}, coeffs={coeffs}")
        return

    print("\n=== Setup chain ===")
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    print(f"  n_0={n0}, k_0={k0}, n_1={n1}, k_1={k1}")

    threshold = 8  # n_1 - sqrt(k_1·n_1) = 16 - 8

    for idx, (pos, coeffs) in matches:
        print(f"\n=== Candidate idx={idx}, pos={pos}, coeffs={coeffs} ===")

        fhat = [0] * n0
        for ps, c in zip(pos, coeffs):
            fhat[ps] = c
        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)

        n_zeros = sum(1 for v in f if v == 0)
        print(f"  f n_zeros = {n_zeros}")

        d_f = dist_to_rs(f_arr, L0_arr, n0, k0, D0, inv_D0, p)
        print(f"  dist(f, RS_8 on L_0) = {d_f}  (w_J=16; should be 21 to match sweep)")

        f_e, f_o = even_odd_parts(f, L0, p)
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)

        d_e = dist_to_rs(f_e_arr, L1_arr, n1, k1, D1, inv_D1, p)
        d_o = dist_to_rs(f_o_arr, L1_arr, n1, k1, D1, inv_D1, p)
        print(f"  dist(f_e, RS_4 on L_1) = {d_e}  [single-α=0 fold]")
        print(f"  dist(f_o, RS_4 on L_1) = {d_o}")

        print(f"\n  Scanning all {p} alphas...")
        t0 = time.time()
        bad = []
        dist_hist = Counter()
        for a in range(p):
            fold = (f_e_arr + a * f_o_arr) % p
            d1 = dist_to_rs(fold, L1_arr, n1, k1, D1, inv_D1, p)
            dist_hist[d1] += 1
            if d1 <= threshold:
                bad.append(a)
        elapsed = time.time() - t0
        print(f"  Scan complete in {elapsed:.1f}s")
        print(f"  |bad α| = {len(bad)} (threshold ≤ {threshold})")
        print(f"  Distance histogram:")
        for d in sorted(dist_hist):
            print(f"    d={d:2d}: {dist_hist[d]:4d} alphas{'  *BAD*' if d <= threshold else ''}")
        if 0 < len(bad) < 30:
            print(f"  bad: {bad}")
        elif len(bad) == p:
            print(f"  bad = ALL of F_q  ← BREAKS Conjecture D and PR #373's M_aff bound")
        else:
            print(f"  bad first 30: {bad[:30]}")

        # If d_e ≤ 8, single-α=0 is bad. Sanity: BCH bound says d_e ≥ 7.
        # Compare to BCH lower bound from {0,1,2,3} ∪ {10}:
        # null DFT positions: {4..9, 11..15}, longest cyclic run 6 → weight ≥ 7.
        print(f"\n  BCH check: f_e=c_20·y^10. Min wt(c_0+c_1y+c_2y²+c_3y³ - c_20·y^10) ≥ 7.")
        print(f"  So dist(f_e, RS_4) ≥ 7. Got {d_e} (consistent if d_e ≥ 7).")


if __name__ == "__main__":
    main()
