"""g3_verify_count4_noncyclic.py — verify count=4 NON-cyclotomic finding at q=1153.

Sweep reported: pos=[8, 9, 25], dist=22, count=4, bad=[748, 898, 1009, 1090], NON-cyclotomic.

Reproduce candidate, recompute count, verify whether bad is truly NOT a coset.
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


def is_subgroup(S, p):
    Sset = set(S)
    for a in S:
        for b in S:
            if (a * b) % p not in Sset:
                return False
    return True


def find_coset_thorough(bad, p):
    """Try every (β, λ) more thoroughly: for each β, see if (bad - β)/λ is subgroup for SOME λ."""
    bad = sorted(bad)
    n = len(bad)
    if n == 0: return None
    for beta in range(p):
        translates = sorted([(b - beta) % p for b in bad])
        if 0 in translates:
            continue
        # Try every translates[i] as the divisor (λ = translates[i])
        for i, first in enumerate(translates):
            first_inv = pow(first, p - 2, p)
            ratios = sorted({(t * first_inv) % p for t in translates})
            if len(ratios) != n:  # collisions, can't be a free coset
                continue
            if is_subgroup(ratios, p):
                return (beta, first, len(ratios), ratios)
    return None


def reproduce_candidate(p, n0, k0, n_candidates, seed, target_pos):
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
    matches = [(i, c) for i, c in enumerate(out) if c[0] == target_pos]
    return matches


def main():
    p = 1153
    n0, k0 = 32, 8
    target_pos = (8, 9, 25)
    expected_bad = [748, 898, 1009, 1090]

    # Sweep uses seed = 2026 + p = 3179
    seed = 2026 + p
    matches = reproduce_candidate(p, n0, k0, 300, seed, target_pos)
    print(f"Candidates with pos={target_pos}: {len(matches)}")
    for i, (pos, coeffs) in matches:
        print(f"  idx {i}: coeffs={coeffs}")

    if not matches:
        print("FATAL: no match")
        return

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n1 = list(combinations(range(n1), k1))
    info_sets_arr_n1 = np.array(info_sets_n1, dtype=np.int64)

    for idx, (pos, coeffs) in matches:
        print(f"\n=== Verifying idx={idx}, pos={pos}, coeffs={coeffs} ===")

        fhat = [0] * n0
        for ps, c in zip(pos, coeffs):
            fhat[ps] = c
        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)

        # Check dist exhaustively (with bug-fixed batched_extras)
        all_T = list(combinations(range(n0), k0))
        max_extras = 0
        for start in range(0, len(all_T), 200000):
            batch = all_T[start:start + 200000]
            T_arr = np.array(batch, dtype=np.int64)
            extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
            max_extras = max(max_extras, int(extras.max()))
        d_f = n0 - k0 - max_extras
        print(f"  dist(f, RS_8) = {d_f}  (w_J=16; strict above-J? {d_f > 16})")

        f_e, f_o = even_odd_parts(f, L0, p)
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)

        bad = []
        dist_hist = Counter()
        for a in range(p):
            fold = (f_e_arr + a * f_o_arr) % p
            extras = batched_extras(info_sets_arr_n1, fold, L1_arr, D1, inv_D1, p)
            d1 = n1 - k1 - int(extras.max())
            dist_hist[d1] += 1
            if d1 <= 8:
                bad.append(a)

        print(f"  count = {len(bad)}, bad = {sorted(bad)}")
        print(f"  Match expected? {sorted(bad) == sorted(expected_bad)}")
        print(f"  Distance histogram: {dict(sorted(dist_hist.items()))}")

        # Thorough cyclotomic check
        coset = find_coset_thorough(bad, p)
        if coset is not None:
            beta, lam, h_ord, H = coset
            print(f"  CYCLOTOMIC: β={beta}, λ={lam}, |H|={h_ord}")
            print(f"  H = {H}")
        else:
            print(f"  ✗ NOT a cyclotomic coset (verified thoroughly)")

        # Try other coset structures: additive coset?
        if len(bad) == 4:
            # Test if bad is an additive subgroup or coset (in F_p with prime order)
            # F_p has no additive subgroups other than {0} and itself, so no additive coset.
            # Try other group structures:
            # - Difference set: {a-b mod p : a, b ∈ bad, a≠b}
            diffs = sorted({(a - b) % p for a in bad for b in bad if a != b})
            print(f"  Pairwise differences: {len(diffs)} unique: {diffs[:8]}...")

            # Test if bad is on an arithmetic progression
            d = (bad[1] - bad[0]) % p
            ap_test = all((bad[i] - bad[0]) % p == (i*d) % p for i in range(len(bad)))
            print(f"  Arithmetic progression? {ap_test}")


if __name__ == "__main__":
    main()
