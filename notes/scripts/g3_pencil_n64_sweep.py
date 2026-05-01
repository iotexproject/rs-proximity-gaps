"""g3_pencil_n64_sweep.py — sweep (a,b) at n=64, k=16 to find MAX |B|.

Focus: identify if |B| can exceed 4 for some (a, b) at n=64, k=16, q=193.
Sample diverse (a, b) with gcd(a-b, n) ∈ {2, 4, 8} and gcd(a, n)=gcd(b, n)=1.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import modinv
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


def count_N(a, b, n, k, q, n_samples=20000):
    L = find_subgroup(q, n)
    L_arr = np.array(L, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, q)
    w_J = n - int(round(np.sqrt(k * n)))

    z_a = np.array([pow(int(x), a, q) for x in L], dtype=np.int64)
    z_b = np.array([pow(int(x), b, q) for x in L], dtype=np.int64)

    rng = np.random.default_rng(2026)
    sample = []; seen = set()
    while len(sample) < n_samples:
        T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)

    count = 0
    for alpha in range(q):
        h = (z_a + alpha * z_b) % q
        ext = batched_extras(info_arr, h, L_arr, D, inv_D, q)
        d = n - k - int(ext.max())
        if d <= w_J:
            count += 1
    return count


def main():
    n, k, q = 64, 16, 193
    w_J = n - int(round(np.sqrt(k * n)))
    M_max = w_J + 1

    print(f"=== Pencil count |B| at n={n}, k={k}, q={q}, w_J={w_J}, M_max={M_max} ===\n")
    print(f"{'(a,b)':>10} {'gcd(a-b,n)':>11} {'|B|':>5}  {'note':30}")
    print("-" * 65)

    # gcd(a, n) = 1 means a coprime to 64 → a odd
    odd_a = [j for j in range(1, n) if np.gcd(j, n) == 1]
    # Sample diverse (a, b) pairs with gcd(a-b, n) ∈ {2, 4, 8, 16, 32}
    test_cases = []
    for diff_target in [2, 4, 8, 16, 32]:
        # Find pairs (a, b) with gcd(a-b, n) = diff_target
        for a in odd_a[:8]:
            for b in odd_a[:8]:
                if a == b: continue
                if np.gcd(abs(a - b), n) == diff_target:
                    test_cases.append((a, b))
                    if len([c for c in test_cases if np.gcd(abs(c[0]-c[1]), n) == diff_target]) >= 4:
                        break
            else: continue
            break

    # Also add (43, 47) baseline
    test_cases = list(set(test_cases + [(43, 47), (3, 7), (5, 11), (3, 5), (3, 19), (3, 35)]))

    max_B = 0
    max_case = None
    t0 = time.time()
    for (a, b) in test_cases:
        if np.gcd(a, n) != 1 or np.gcd(b, n) != 1: continue
        gcd_ab = np.gcd(abs(a - b), n)
        try:
            B = count_N(a, b, n, k, q)
            note = f"gcd(a-b,n)={gcd_ab}"
            print(f"{f'({a},{b})':>10} {gcd_ab:>11} {B:>5}  {note}")
            if B < q and B > max_B:
                max_B = B
                max_case = (a, b)
        except Exception as e:
            print(f"  ERROR for (a={a}, b={b}): {e}")

    print(f"\nMax |B| (excluding at-J) = {max_B} at (a,b) = {max_case}")
    print(f"Total elapsed: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
