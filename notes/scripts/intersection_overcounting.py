"""
intersection_overcounting.py — Decompose M (σ-count) into M_actual (distinct codewords).

At p ≡ 1 mod n: all C(n,w) subsets of L are valid B-sets.
For a center v, M = #{B-sets compatible with v}.
M_actual = #{distinct codewords f with d(v,f) ≤ w}.

Key question: what is the max M_actual / avg M_actual ratio?
And: does M_actual = O(1) even when M = O(n)?
"""

import random
from math import comb
from itertools import combinations
from collections import Counter

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = (val * g) % p
        if len(seen) == p - 1:
            return g
    return None

def poly_eval(coeffs, x, p):
    r = 0
    xp = 1
    for c in coeffs:
        r = (r + c * xp) % p
        xp = (xp * x) % p
    return r

def poly_eval_all(coeffs, L, p):
    return tuple(poly_eval(coeffs, x, p) for x in L)

def hamming_dist(v1, v2):
    return sum(1 for a, b in zip(v1, v2) if a != b)

def main():
    print("=" * 70)
    print("OVERCOUNTING ANALYSIS: M vs M_actual")
    print("=" * 70)

    test_cases = [
        # (n, w, c)
        (8, 3, 1),
        (8, 3, 2),
        (10, 3, 1),
        (10, 3, 2),
        (10, 4, 1),
        (10, 4, 2),
        (12, 3, 1),
        (12, 3, 2),
        (12, 4, 1),
        (12, 4, 2),
    ]

    for n, w, c in test_cases:
        k = n - w - c
        if k <= 0:
            continue

        # Find smallest prime p ≡ 1 mod n, p > n
        p = n + 1
        while True:
            if all(p % i != 0 for i in range(2, int(p**0.5) + 2)):
                if (p - 1) % n == 0:
                    break
            p += 1
            if p > 500:
                break
        if p > 200:
            continue

        g = find_primitive_root(p)
        omega = pow(g, (p - 1) // n, p)
        L = [pow(omega, i, p) for i in range(n)]

        print(f"\n{'='*60}")
        print(f"n={n}, w={w}, c={c}, k={k}, p={p}")
        print(f"d_min = n-k+1 = {n-k+1}, Johnson bound on list size")
        print(f"C(n,w) = {comb(n,w)}, C(n,w)/p^c = {comb(n,w)/p**c:.2f}")
        print(f"{'='*60}")

        # Enumerate ALL codewords (polynomials of degree < k)
        # For small p and k, this is feasible: p^k codewords
        if p**k > 500000:
            print(f"  p^k = {p**k} too large, skipping full enumeration")
            continue

        codewords = {}
        for code_idx in range(p**k):
            coeffs = []
            tmp = code_idx
            for _ in range(k):
                coeffs.append(tmp % p)
                tmp //= p
            cw = poly_eval_all(coeffs, L, p)
            codewords[code_idx] = cw

        print(f"  {len(codewords)} codewords enumerated")

        # For each random center, compute M_actual and M_alg
        random.seed(456)
        n_centers = 200

        M_actual_list = []
        M_bset_list = []

        for trial in range(n_centers):
            # Random center vector
            v = tuple(random.randrange(p) for _ in range(n))

            # M_actual: count codewords within distance w
            close_codewords = []
            for cw_idx, cw in codewords.items():
                d = hamming_dist(v, cw)
                if d <= w:
                    close_codewords.append((cw_idx, d))
            M_actual = len(close_codewords)

            # M_bset: count B-sets compatible with v
            # B-set of codeword f at distance d: the d disagreement positions
            # can be chosen as C(d, w) ways? No — the B-set IS the set of
            # positions where v and f agree? No — B is the ERROR set (disagreement).
            # Actually, B = {positions where v ≠ f} has size d ≤ w.
            # The "compatible B-set" has size EXACTLY w and includes the d disagreements
            # plus w-d "chosen" positions from the agreements.
            # So each codeword at distance d contributes C(n-d, w-d) compatible B-sets.
            M_bset = sum(comb(n - d, w - d) for _, d in close_codewords)

            M_actual_list.append(M_actual)
            M_bset_list.append(M_bset)

        print(f"\n  M_actual (distinct codewords within d ≤ w):")
        print(f"    min={min(M_actual_list)}, max={max(M_actual_list)}, avg={sum(M_actual_list)/len(M_actual_list):.2f}")
        dist_actual = Counter(M_actual_list)
        print(f"    distribution: {dict(sorted(dist_actual.items()))}")

        print(f"\n  M_bset (B-set count, with overcounting):")
        print(f"    min={min(M_bset_list)}, max={max(M_bset_list)}, avg={sum(M_bset_list)/len(M_bset_list):.2f}")
        dist_bset = Counter(M_bset_list)
        items = sorted(dist_bset.items())
        if len(items) > 20:
            print(f"    distribution (sample): {dict(items[:10])} ... {dict(items[-5:])}")
        else:
            print(f"    distribution: {dict(items)}")

        # Show the decomposition for the worst case
        worst_idx = M_actual_list.index(max(M_actual_list))
        v = tuple(random.randrange(p) for _ in range(n))  # won't be the same... let me fix

    # Re-run for specific case to show decomposition
    print("\n" + "="*70)
    print("DETAILED DECOMPOSITION for worst-case centers")
    print("="*70)

    for n, w, c in [(10, 3, 1), (10, 4, 2), (12, 3, 1)]:
        k = n - w - c
        if k <= 0:
            continue

        p = n + 1
        while True:
            if all(p % i != 0 for i in range(2, int(p**0.5) + 2)):
                if (p - 1) % n == 0:
                    break
            p += 1
            if p > 200:
                break
        if p > 200:
            continue

        g = find_primitive_root(p)
        omega = pow(g, (p - 1) // n, p)
        L = [pow(omega, i, p) for i in range(n)]

        if p**k > 500000:
            continue

        codewords = {}
        for code_idx in range(p**k):
            coeffs = []
            tmp = code_idx
            for _ in range(k):
                coeffs.append(tmp % p)
                tmp //= p
            cw = poly_eval_all(coeffs, L, p)
            codewords[code_idx] = cw

        print(f"\n--- n={n}, w={w}, c={c}, k={k}, p={p} ---")

        # Find worst center
        random.seed(456)
        worst_M = 0
        worst_v = None
        worst_detail = None
        for trial in range(500):
            v = tuple(random.randrange(p) for _ in range(n))
            close = []
            for cw_idx, cw in codewords.items():
                d = hamming_dist(v, cw)
                if d <= w:
                    close.append((d, cw_idx))
            if len(close) > worst_M:
                worst_M = len(close)
                worst_v = v
                worst_detail = close

        print(f"  Worst center: M_actual = {worst_M}")
        print(f"  Codewords by distance:")
        dist_breakdown = Counter(d for d, _ in worst_detail)
        for d in sorted(dist_breakdown.keys()):
            bsets = comb(n - d, w - d)
            print(f"    d={d}: {dist_breakdown[d]} codewords, each → C({n-d},{w-d})={bsets} B-sets, total={dist_breakdown[d]*bsets}")
        total_bsets = sum(comb(n-d, w-d) * dist_breakdown[d] for d in dist_breakdown)
        print(f"  Total M_bset = {total_bsets}")
        print(f"  Overcounting ratio = M_bset/M_actual = {total_bsets/worst_M:.1f}")

main()
