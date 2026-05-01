"""g3_pencil_n64_qsweep.py — focused q-sweep at n=64.

Test: is N(43, 47, 64, 16, q) = 4 for all q ≡ 1 mod 64?
Compare also to other (a, b) gcd-4 cases.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from mds_decoder import precompute_diff_inv, batched_extras


def find_subgroup(p, n):
    assert (p - 1) % n == 0
    g = None
    for cand in range(2, p):
        ok = True
        for d in range(1, n):
            if pow(cand, (p - 1) * d // n, p) == 1: ok = False; break
        if ok: g = cand; break
    if g is None: g = 3
    w = pow(g, (p - 1) // n, p)
    return [pow(w, i, p) for i in range(n)]


def count_N(a, b, n, k, q, info_arr, L_arr, D, inv_D, w_J):
    z_a = np.array([pow(int(x), a, q) for x in L_arr.tolist()], dtype=np.int64)
    z_b = np.array([pow(int(x), b, q) for x in L_arr.tolist()], dtype=np.int64)
    count = 0
    for alpha in range(q):
        h = (z_a + alpha * z_b) % q
        ext = batched_extras(info_arr, h, L_arr, D, inv_D, q)
        d = n - k - int(ext.max())
        if d <= w_J:
            count += 1
    return count


def main():
    n, k = 64, 16
    w_J = n - int(round(np.sqrt(k * n)))

    # Try q ≡ 1 mod 64
    valid_q = [q for q in [193, 257, 449, 577, 641, 769, 1153, 1217]
               if (q - 1) % n == 0]
    print(f"Testing N(a, b, {n}, {k}, q) at q ∈ {valid_q}")

    # Generate sample info_sets ONCE per q (different L per q)
    sample_size = 20000
    rng = np.random.default_rng(2026)
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)

    test_pairs = [
        (43, 47),  # known to give |B|=4 at q=193, 257
        (45, 49),  # gcd-4 variant
        (3, 7),    # small gcd-4
        (1, 5),    # small gcd-4
        (47, 51),  # another gcd-4
    ]

    print(f"\n{'(a,b)':>10}  {'q':>5}  {'|B|':>4}  {'gcd':>4}")
    print("-" * 38)
    for (a, b) in test_pairs:
        gcd_ab = np.gcd(abs(a - b), n)
        if gcd_ab == 0 or np.gcd(a, n) != 1 or np.gcd(b, n) != 1: continue
        for q in valid_q:
            L = find_subgroup(q, n)
            L_arr = np.array(L, dtype=np.int64)
            D, inv_D = precompute_diff_inv(L_arr, q)
            t0 = time.time()
            B = count_N(a, b, n, k, q, info_arr, L_arr, D, inv_D, w_J)
            print(f"{f'({a},{b})':>10}  {q:>5}  {B:>4}  {gcd_ab:>4}  [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
