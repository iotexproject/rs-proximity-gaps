"""g3_conjE_test.py — test Conjecture E: # orbits m ≤ 1 at n=64.

Sweep ~40 (a, b) pairs at n=64, k=16, q=193. For each:
- compute sampled |B|
- check if it's 0, 16 (m=1 with gcd-4 orbits), 32 (m=2), or other

Looking for any pair with m ≥ 2 (would refute Conjecture E).
"""
import sys, os, time, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from mds_decoder import precompute_diff_inv, batched_extras


def find_subgroup(p, n):
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
    q = 193
    n, k = 64, 16
    w_J = n - int(round(np.sqrt(k * n)))
    L = find_subgroup(q, n)
    L_arr = np.array(L, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, q)

    rng = np.random.default_rng(2026)
    sample = []; seen = set()
    while len(sample) < 50000:
        T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)
    print(f"Sample 50K info_sets at L_64. q={q}, w_J={w_J}.\n")

    # Above-J: both a, b > k-1 = 15
    above_J_pairs = []
    rng_p = random.Random(2026)
    for _ in range(60):
        while True:
            a = rng_p.randint(16, n-1)
            b = rng_p.randint(16, n-1)
            if a == b: continue
            if (a, b) in above_J_pairs or (b, a) in above_J_pairs: continue
            break
        above_J_pairs.append((a, b))

    # Also include known cases for sanity
    above_J_pairs = [(43, 47), (45, 49), (47, 51), (139 - 116, 154 - 116)] + above_J_pairs[:30]
    above_J_pairs = list(set(above_J_pairs))
    above_J_pairs = above_J_pairs[:30]

    print(f"{'(a,b)':>10}  {'gcd':>4}  {'sampled N':>10}  {'predicted orbit':>16}  {'m est':>5}")
    print("-" * 60)

    m_distribution = {}
    interesting = []
    t0 = time.time()
    for (a, b) in above_J_pairs:
        if min(a, b) < 16: continue
        gcd_ab = int(np.gcd(abs(a - b), n))
        orbit_size = n // gcd_ab
        try:
            B = count_N(a, b, n, k, q, info_arr, L_arr, D, inv_D, w_J)
            # Estimate m: if true N is m·orbit_size, and sampling missed some...
            # Conservative estimate: m_est = floor(B / orbit_size) or 0
            if B == 0:
                m_est = 0
            elif B == q:
                m_est = "at-J"
            else:
                # Sampling underestimate; m_true >= ceil(B/orbit_size) probably
                m_est = max(1, round(B / orbit_size))
            print(f"{f'({a},{b})':>10}  {gcd_ab:>4}  {B:>10}  {orbit_size:>16}  {str(m_est):>5}")
            if isinstance(m_est, int) and m_est >= 2:
                interesting.append((a, b, B, orbit_size, m_est))
            key = m_est if isinstance(m_est, int) else m_est
            m_distribution[key] = m_distribution.get(key, 0) + 1
        except Exception as e:
            print(f"  ERROR for ({a}, {b}): {e}")

    print(f"\nTotal elapsed: {time.time()-t0:.0f}s")
    print(f"\nm distribution: {m_distribution}")
    if interesting:
        print(f"\nINTERESTING (m ≥ 2 candidates): {interesting}")
    else:
        print(f"\nNo m ≥ 2 found. Conjecture E supported.")


if __name__ == "__main__":
    main()
