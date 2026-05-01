#!/usr/bin/env python3
"""
Systematic sweep of M(n, k, w, p) to find the exact formula.

Key questions:
1. How does M depend on 2w-d (the "overlap budget")?
2. How does M scale with n for fixed rate and fixed delta?
3. Does M depend on p? If so, how?
4. What is M_∞ = lim_{p→∞} M(n,k,w,p)?

Use PyTorch MPS for GPU acceleration on M3 Ultra.
"""

import torch
import numpy as np
import time
import sys

DEVICE = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

def find_primitive_root(p):
    for g in range(2, p):
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
        if all(pow(g, (p-1)//q, p) != 1 for q in factors):
            return g

def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def compute_M_exact(n, k, p, w_list, n_test=50000):
    """Compute M(w) for each w in w_list by testing many centers."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Generate codewords
    L_eval = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        L_eval[i, 0] = 1
        for j in range(1, k):
            L_eval[i, j] = L_eval[i, j-1] * L[i] % p

    num_cw = p ** k
    coeff = np.zeros((num_cw, k), dtype=np.int64)
    idx = np.arange(num_cw)
    for dim in range(k):
        coeff[:, dim] = (idx // (p ** dim)) % p

    # Generate codewords in chunks
    chunk = 200000
    cw_list = []
    for start in range(0, num_cw, chunk):
        end = min(start + chunk, num_cw)
        cw_list.append(coeff[start:end] @ L_eval.T % p)
    cw = np.vstack(cw_list)

    cw_gpu = torch.tensor(cw, dtype=torch.int16, device=DEVICE)

    max_M = {w: 0 for w in w_list}
    rng = np.random.default_rng(42)

    # Test centers: random + near-codeword + weight-1/2 errors
    batch_size = min(5000, n_test)

    for batch_start in range(0, n_test, batch_size):
        actual = min(batch_size, n_test - batch_start)

        # Mix of test strategies
        test = np.zeros((actual, n), dtype=np.int64)
        split = actual // 3

        # Random
        test[:split] = rng.integers(0, p, size=(split, n))

        # Near-codeword (small errors from random codewords)
        for i in range(split, 2*split):
            base_idx = rng.integers(0, num_cw)
            test[i] = cw[base_idx].copy()
            err_wt = rng.integers(1, max(w_list) + 1)
            err_pos = rng.choice(n, min(err_wt, n), replace=False)
            for pos in err_pos:
                test[i, pos] = (test[i, pos] + rng.integers(1, p)) % p

        # Structured: codeword + weight-2 error at specific positions
        for i in range(2*split, actual):
            base_idx = rng.integers(0, num_cw)
            test[i] = cw[base_idx].copy()
            pos1, pos2 = rng.choice(n, 2, replace=False)
            test[i, pos1] = (test[i, pos1] + rng.integers(1, p)) % p
            test[i, pos2] = (test[i, pos2] + rng.integers(1, p)) % p

        test_gpu = torch.tensor(test, dtype=torch.int16, device=DEVICE)

        # Compute distances in sub-batches
        cw_batch = 100000
        for cw_start in range(0, num_cw, cw_batch):
            cw_end = min(cw_start + cw_batch, num_cw)
            cw_sub = cw_gpu[cw_start:cw_end]

            # agreements: (actual, cw_sub_size)
            agree = (test_gpu.unsqueeze(1) == cw_sub.unsqueeze(0)).sum(dim=2)
            dist = n - agree

            for w in w_list:
                counts = (dist <= w).sum(dim=1)
                batch_max = counts.max().item()
                if batch_max > max_M[w]:
                    max_M[w] = int(batch_max)

    return max_M

def find_primes_with_subgroup(n, min_p=None, count=5):
    """Find primes p such that n | p-1."""
    if min_p is None:
        min_p = n + 1
    primes = []
    candidate = min_p
    while len(primes) < count:
        if candidate > 1:
            is_prime = True
            for d in range(2, int(candidate**0.5) + 1):
                if candidate % d == 0:
                    is_prime = False
                    break
            if is_prime and (candidate - 1) % n == 0:
                primes.append(candidate)
        candidate += 1
    return primes

# ================================================================
# SWEEP 1: Fixed rate 1/2, vary n, find M for each w
# ================================================================
print("=" * 80)
print("SWEEP 1: Rate 1/2, M(n, w) for various n")
print("=" * 80)

MAX_CW = 2_000_000  # max codewords that fit in GPU memory

results = []

for n in [4, 6, 8, 10, 12, 14]:
    k = n // 2
    d = n - k + 1  # MDS minimum distance

    # Find smallest suitable prime
    primes = find_primes_with_subgroup(n, count=3)

    for p in primes:
        if p ** k > MAX_CW:
            continue

        w_list = list(range(1, n))
        delta_J = 1 - np.sqrt(k / n)
        w_J = int(np.ceil(delta_J * n))

        t0 = time.time()
        M = compute_M_exact(n, k, p, w_list, n_test=30000)
        elapsed = time.time() - t0

        print(f"\nn={n}, k={k}, p={p}, d={d}, delta_J={delta_J:.4f}, w_J={w_J}")
        print(f"  {'w':>3} {'2w-d':>5} {'M':>4} {'⌊n/w⌋':>6} {'above_J':>8} {'notes':>20}")
        for w in w_list:
            overlap = 2 * w - d
            floor_nw = n // w if w > 0 else 0
            above_J = "***" if w >= w_J else ""
            note = ""
            if overlap <= 0:
                note = f"disjoint (t={overlap})"
            else:
                note = f"overlap≤{overlap}"

            if M[w] > 0:
                print(f"  {w:3d} {overlap:5d} {M[w]:4d} {floor_nw:6d} {above_J:>8} {note:>20}")
                results.append((n, k, p, w, d, overlap, M[w], floor_nw))

        print(f"  Time: {elapsed:.1f}s")

# ================================================================
# SWEEP 2: Fixed n=8, k=4, vary p to see M(p) trend
# ================================================================
print("\n" + "=" * 80)
print("SWEEP 2: n=8, k=4, M vs p")
print("=" * 80)

n, k = 8, 4
primes_8 = find_primes_with_subgroup(8, count=15)
primes_8 = [p for p in primes_8 if p**k <= MAX_CW]

print(f"Testing p = {primes_8}")
print(f"{'p':>5} {'w=2':>5} {'w=3':>5} {'w=4':>5} {'w=5':>5}")

for p in primes_8:
    M = compute_M_exact(8, 4, p, [2, 3, 4, 5], n_test=30000)
    print(f"{p:5d} {M[2]:5d} {M[3]:5d} {M[4]:5d} {M[5]:5d}")

# ================================================================
# SWEEP 3: Fixed n=6, k=3, many p values
# ================================================================
print("\n" + "=" * 80)
print("SWEEP 3: n=6, k=3, M vs p (checking p-independence)")
print("=" * 80)

primes_6 = find_primes_with_subgroup(6, count=20)
primes_6 = [p for p in primes_6 if p**3 <= MAX_CW]

print(f"{'p':>5} {'w=1':>5} {'w=2':>5} {'w=3':>5} {'w=4':>5}")
for p in primes_6:
    M = compute_M_exact(6, 3, p, [1, 2, 3, 4], n_test=20000)
    print(f"{p:5d} {M[1]:5d} {M[2]:5d} {M[3]:5d} {M[4]:5d}")

# ================================================================
# SWEEP 4: Different rates, fixed n=12
# ================================================================
print("\n" + "=" * 80)
print("SWEEP 4: n=12, different rates")
print("=" * 80)

n = 12
for k in [3, 4, 6, 8, 9]:
    d = n - k + 1
    primes = find_primes_with_subgroup(n, count=3)
    for p in primes:
        if p**k > MAX_CW:
            continue
        delta_J = 1 - np.sqrt(k / n)
        w_J = int(np.ceil(delta_J * n))
        w_list = list(range(max(1, w_J - 1), min(n, w_J + 4)))

        M = compute_M_exact(n, k, p, w_list, n_test=20000)
        print(f"n={n}, k={k}, p={p}, d={d}, delta_J={delta_J:.3f}, w_J={w_J}")
        for w in w_list:
            overlap = 2 * w - d
            above = "***" if w >= w_J else ""
            print(f"  w={w}, 2w-d={overlap}, M={M[w]}, ⌊n/w⌋={n//w} {above}")
        print()

# ================================================================
# Summary table
# ================================================================
print("\n" + "=" * 80)
print("SUMMARY: M at first w above Johnson, rate 1/2")
print("=" * 80)
print(f"{'n':>4} {'k':>3} {'d':>3} {'w_J':>3} {'w':>3} {'2w-d':>5} {'M':>4} {'⌊n/w⌋':>6}")

for entry in results:
    n, k, p, w, d, overlap, M_val, floor_nw = entry
    delta_J = 1 - np.sqrt(k / n)
    w_J = int(np.ceil(delta_J * n))
    if w == w_J and k == n // 2:  # first w above Johnson, rate 1/2
        print(f"{n:4d} {k:3d} {d:3d} {w_J:3d} {w:3d} {overlap:5d} {M_val:4d} {floor_nw:6d}")
