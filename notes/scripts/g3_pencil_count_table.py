"""g3_pencil_count_table.py — direct count of N(a, b, n, k, q).

For 2-monomial pencil h(α) = z^a + α·z^b on L_n (order-n subgroup of F_q^*),
count #{α ∈ F_q : dist(h(α), RS_k(L_n)) ≤ w_J(L_n) = n - sqrt(kn)}.

Goal: tabulate across n ∈ {8, 16, 32, 64} at FRI rate (k = n/4) and identify
pattern. Conjecture: universal = 9 = M_max(order-16) when (a, b) generic.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import modinv
from mds_decoder import precompute_diff_inv, batched_extras


def find_subgroup(p, n):
    """Find a primitive n-th root of unity in F_p^*; return [w^0, w^1, ..., w^{n-1}]."""
    assert (p - 1) % n == 0, f"n={n} doesn't divide p-1={p-1}"
    g = None
    for cand in range(2, p):
        if pow(cand, (p - 1) // 2, p) != 1 and pow(cand, p - 1, p) == 1:
            g = cand; break
    if g is None: g = 3
    w = pow(g, (p - 1) // n, p)
    while pow(w, n, p) != 1 or any(pow(w, d, p) == 1 for d in range(1, n)):
        g += 1
        if g >= p: raise RuntimeError("no primitive n-th root found")
        w = pow(g, (p - 1) // n, p)
    return [pow(w, i, p) for i in range(n)]


def count_N(a, b, n, k, q, n_alpha_sample=None):
    """Count alpha in F_q with dist(z^a + alpha*z^b, RS_k(L_n)) <= w_J(L_n)."""
    L = find_subgroup(q, n)
    L_arr = np.array(L, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, q)
    w_J = n - int(round(np.sqrt(k * n)))

    z_a = np.array([pow(int(x), a, q) for x in L], dtype=np.int64)
    z_b = np.array([pow(int(x), b, q) for x in L], dtype=np.int64)

    # Enumerate or sample info_sets (size k) of L
    if n <= 16:
        info_sets = list(combinations(range(n), k))
    else:
        # Sample up to 5000 info_sets — adequate to find max
        sample_size = 5000 if n <= 32 else 20000
        rng = np.random.default_rng(2026)
        sample = []; seen = set()
        while len(sample) < sample_size:
            T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
            if T not in seen: seen.add(T); sample.append(T)
        info_sets = sample
    info_arr = np.array(info_sets, dtype=np.int64)

    # For each alpha, compute h_alpha = z^a + alpha*z^b, then check dist
    alphas = list(range(q)) if n_alpha_sample is None else list(range(0, q, q // n_alpha_sample))

    count = 0
    for alpha in alphas:
        h = (z_a + alpha * z_b) % q
        ext = batched_extras(info_arr, h, L_arr, D, inv_D, q)
        d = n - k - int(ext.max())
        if d <= w_J:
            count += 1
    return count


def main():
    # FRI rate 1/4: k = n/4
    print(f"{'n':>5} {'k':>4} {'q':>5} {'(a,b)':>8} {'w_J':>5} {'M_max':>6} {'|B|':>5}  {'note':30}")
    print("-" * 80)

    test_cases = [
        # (n, q, (a, b))  — pencils that come from Reverse Pattern at (n_0, k_0)
        # n_2 = n_0/4. Indices on L_2 from j_0 → j_2 = (j_0 mod n_2)/<lifts>
        # Try various odd-position pencils (gcd-1 with n)
        (8,  97,  (3, 1)),  (8,  97,  (5, 3)),  (8,  97,  (7, 5)),
        (8,  193, (3, 1)),  (8,  193, (5, 3)),
        (8,  449, (3, 1)),  (8,  449, (5, 3)),

        (16, 97,  (5, 3)),  (16, 97,  (5, 7)),  (16, 97,  (9, 11)),
        (16, 193, (5, 3)),  (16, 193, (5, 7)),  (16, 193, (11, 9)),
        (16, 449, (5, 3)),  (16, 449, (11, 9)),

        # n=32 with specific pencil from (87, 102, 103) at (128,32): pos {21, 25} on L_2
        (32, 97,  (21, 25)),  (32, 97,  (3, 5)),  (32, 97,  (15, 17)),
        (32, 193, (21, 25)),  (32, 193, (3, 5)),
        (32, 257, (21, 25)),  (32, 257, (3, 5)),
        (32, 449, (21, 25)),  (32, 449, (3, 5)),

        # n=64
        (64, 193, (43, 47)),  (64, 193, (3, 5)),
        (64, 257, (43, 47)),  (64, 257, (3, 5)),
        (64, 449, (43, 47)),
    ]

    for n, q, (a, b) in test_cases:
        k = n // 4
        if (q - 1) % n != 0: continue
        w_J = n - int(round(np.sqrt(k * n)))
        M_max = w_J + 1
        gcd_ab = np.gcd(abs(a - b), n)
        gcd_a = np.gcd(a, n)
        gcd_b = np.gcd(b, n)
        note = f"gcd(a-b,n)={gcd_ab}, gcd(a,n)={gcd_a}, gcd(b,n)={gcd_b}"
        try:
            t0 = time.time()
            N = count_N(a, b, n, k, q)
            elapsed = time.time() - t0
            print(f"{n:5d} {k:4d} {q:5d} {f'({a},{b})':>8} {w_J:5d} {M_max:6d} {N:5d}  {note} [{elapsed:.0f}s]")
        except Exception as e:
            print(f"{n:5d} {k:4d} {q:5d} {f'({a},{b})':>8} ERROR: {e}")


if __name__ == "__main__":
    main()
