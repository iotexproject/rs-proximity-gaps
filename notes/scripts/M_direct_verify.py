#!/usr/bin/env python3
"""
DIRECT M computation: for a given center c, count |{f ∈ RS_k : d(c,f) ≤ w}|.
No parity check, no syndrome, no DFT. Just brute force.
"""
from itertools import combinations


def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def compute_M(n, k, p, w, center):
    """Count codewords at distance ≤ w from center."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    count = 0
    list_f = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        f = [sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n)]
        dist = sum(1 for i in range(n) if center[i] != f[i])
        if dist <= w:
            count += 1
            if dist == w:
                B = tuple(i for i in range(n) if center[i] != f[i])
                list_f.append((B, f))

    return count, list_f


def find_worst_case(n, k, p, w):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Generate all codewords
    codewords = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        f = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
        codewords.append(f)

    print(f"n={n}, k={k}, p={p}, w={w}: {len(codewords)} codewords")

    # Find worst case by trying many centers
    best_M = 0
    best_c = None
    best_list = None

    # Try weight-w error vectors (centers = codeword + weight-w perturbation)
    # For efficiency: c = (v_0, ..., v_{w-1}, 0, ..., 0) for all value combos
    import random
    random.seed(42)

    trials = 0
    # Structured: first w positions
    for vals_idx in range(min((p-1)**w, 5000)):
        vals = []
        temp = vals_idx
        for _ in range(w):
            vals.append(temp % (p-1) + 1)
            temp //= (p-1)
        c = [0] * n
        for j in range(w):
            c[j] = vals[j]
        M = sum(1 for f in codewords if sum(1 for i in range(n) if c[i] != f[i]) <= w)
        if M > best_M:
            best_M = M
            best_c = c[:]
        trials += 1

    # Random positions
    for _ in range(2000):
        positions = sorted(random.sample(range(n), w))
        vals = [random.randint(1, p-1) for _ in range(w)]
        c = [0] * n
        for j, pos in enumerate(positions):
            c[pos] = vals[j]
        M = sum(1 for f in codewords if sum(1 for i in range(n) if c[i] != f[i]) <= w)
        if M > best_M:
            best_M = M
            best_c = c[:]
        trials += 1

    print(f"  Best M = {best_M} (after {trials} trials)")
    print(f"  Center: {best_c}")

    # Get the actual list
    M_total, list_w = compute_M(n, k, p, w, best_c)
    print(f"  M(≤{w}) = {M_total}, M(={w}) = {len(list_w)}")
    for B, f in list_w[:15]:
        print(f"    B = {B}")

    return best_M, best_c, list_w


# Test cases
print("="*60)
find_worst_case(6, 3, 7, 2)
print()
find_worst_case(8, 4, 17, 3)
print()
# For n=10: p=11, k=5. p^k = 161051. Feasible.
find_worst_case(10, 5, 11, 3)
