#!/usr/bin/env python3
"""
GPU-accelerated (MPS/Metal) list size computation for RS codes.
Uses PyTorch for batch distance computation.

Strategy: for RS[n,k] on multiplicative subgroup L of order n in F_p,
enumerate all p^k codewords, then batch-compute distances to many test points.
"""

import torch
import numpy as np
from math import comb
import time
import sys

# Use MPS if available
DEVICE = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print(f"Using device: {DEVICE}")

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
    assert (p - 1) % n == 0, f"n={n} does not divide p-1={p-1}"
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def generate_codewords(n, k, p):
    """Generate all p^k codewords of RS[n,k] over F_p."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Evaluation matrix: L_eval[i,j] = L[i]^j mod p
    L_eval = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        L_eval[i, 0] = 1
        for j in range(1, k):
            L_eval[i, j] = L_eval[i, j-1] * L[i] % p

    # All coefficient vectors
    num_cw = p ** k
    coeff = np.zeros((num_cw, k), dtype=np.int64)
    idx = np.arange(num_cw)
    for dim in range(k):
        coeff[:, dim] = (idx // (p ** dim)) % p

    # Codewords: coeff @ L_eval^T mod p
    # For large matrices, do in chunks to avoid overflow
    chunk_size = 100000
    cw = np.zeros((num_cw, n), dtype=np.int64)
    for start in range(0, num_cw, chunk_size):
        end = min(start + chunk_size, num_cw)
        cw[start:end] = coeff[start:end] @ L_eval.T % p

    return cw

def compute_list_sizes_gpu(codewords, n, k, p, test_points, delta_list):
    """
    GPU-accelerated: compute list size for each test point and delta.
    Returns max list size for each delta.
    """
    num_cw = codewords.shape[0]
    num_tests = test_points.shape[0]

    # Move to GPU
    cw_gpu = torch.tensor(codewords, dtype=torch.int32, device=DEVICE)  # (num_cw, n)

    max_M = {d: 0 for d in delta_list}

    batch_size = min(5000, num_tests)

    for start in range(0, num_tests, batch_size):
        end = min(start + batch_size, num_tests)
        batch = torch.tensor(test_points[start:end], dtype=torch.int32, device=DEVICE)  # (batch, n)

        # Compute agreements: (batch, num_cw)
        # agreements[i,j] = number of positions where batch[i] == cw[j]
        # Do this in sub-batches over codewords if num_cw is large
        cw_batch_size = min(num_cw, 50000)

        agreements = torch.zeros(end - start, dtype=torch.int32, device=DEVICE)
        # For each delta, track the list size per test point
        list_sizes = {d: torch.zeros(end - start, dtype=torch.int32, device=DEVICE) for d in delta_list}

        for cw_start in range(0, num_cw, cw_batch_size):
            cw_end = min(cw_start + cw_batch_size, num_cw)
            cw_sub = cw_gpu[cw_start:cw_end]  # (cw_sub_size, n)

            # Compute distances
            # batch: (batch, n), cw_sub: (cw_sub, n)
            # agreements: (batch, cw_sub)
            agree = (batch.unsqueeze(1) == cw_sub.unsqueeze(0)).sum(dim=2)  # (batch, cw_sub)
            dist = n - agree  # (batch, cw_sub)

            for d in delta_list:
                w_max = int(d * n)
                list_sizes[d] += (dist <= w_max).sum(dim=1)

        for d in delta_list:
            batch_max = list_sizes[d].max().item()
            if batch_max > max_M[d]:
                max_M[d] = batch_max

    return max_M

def full_analysis(n, k, p, n_random=50000, verbose=True):
    """Full list size analysis with GPU acceleration."""
    t0 = time.time()

    if verbose:
        print(f"\n{'='*60}")
        print(f"n={n}, k={k}, p={p}, rate={k/n:.3f}")
        print(f"p^k = {p**k} codewords")
        print(f"Johnson bound: delta_J = {1-np.sqrt(k/n):.4f}")
        print(f"{'='*60}")

    # Generate all codewords
    t1 = time.time()
    cw = generate_codewords(n, k, p)
    if verbose:
        print(f"Generated {cw.shape[0]} codewords in {time.time()-t1:.2f}s")

    delta_list = [round(d/100, 2) for d in range(20, 55, 5)]
    delta_J = 1 - np.sqrt(k / n)

    # --- Test 1: Random points ---
    rng = np.random.default_rng(42)
    test_points = rng.integers(0, p, size=(n_random, n)).astype(np.int64)

    t2 = time.time()
    max_M_random = compute_list_sizes_gpu(cw, n, k, p, test_points, delta_list)
    t_random = time.time() - t2

    if verbose:
        print(f"\nRandom points ({n_random}), computed in {t_random:.2f}s:")
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for d in delta_list:
            w_max = int(d * n)
            above = "***" if d > delta_J else ""
            print(f"{d:6.2f} {w_max:5d} {max_M_random[d]:6d} {above:>8}")

    # --- Test 2: Weight-1 error vectors (known worst case from our analysis) ---
    wt1_points = []
    for i in range(n):
        for v in range(1, p):
            vec = np.zeros(n, dtype=np.int64)
            vec[i] = v
            wt1_points.append(vec)
    wt1_points = np.array(wt1_points)

    t3 = time.time()
    max_M_wt1 = compute_list_sizes_gpu(cw, n, k, p, wt1_points, delta_list)
    t_wt1 = time.time() - t3

    if verbose:
        print(f"\nWeight-1 errors ({wt1_points.shape[0]}), computed in {t_wt1:.2f}s:")
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for d in delta_list:
            w_max = int(d * n)
            above = "***" if d > delta_J else ""
            print(f"{d:6.2f} {w_max:5d} {max_M_wt1[d]:6d} {above:>8}")

    # --- Test 3: Weight-2 error vectors (sample) ---
    wt2_points = []
    for i in range(n):
        for j in range(i+1, n):
            for _ in range(min(10, p-1)):
                vi = rng.integers(1, p)
                vj = rng.integers(1, p)
                vec = np.zeros(n, dtype=np.int64)
                vec[i] = vi
                vec[j] = vj
                wt2_points.append(vec)
    wt2_points = np.array(wt2_points)

    t4 = time.time()
    max_M_wt2 = compute_list_sizes_gpu(cw, n, k, p, wt2_points, delta_list)
    t_wt2 = time.time() - t4

    if verbose:
        print(f"\nWeight-2 errors ({wt2_points.shape[0]}), computed in {t_wt2:.2f}s:")
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for d in delta_list:
            w_max = int(d * n)
            above = "***" if d > delta_J else ""
            print(f"{d:6.2f} {w_max:5d} {max_M_wt2[d]:6d} {above:>8}")

    # --- Test 4: Near-codeword points (codeword + small error) ---
    near_cw = []
    sample_cw = cw[rng.choice(cw.shape[0], min(100, cw.shape[0]), replace=False)]
    for c in sample_cw:
        for _ in range(10):
            err_wt = rng.integers(1, 4)
            err_pos = rng.choice(n, err_wt, replace=False)
            err_vec = c.copy()
            for pos in err_pos:
                err_vec[pos] = (err_vec[pos] + rng.integers(1, p)) % p
            near_cw.append(err_vec)
    near_cw = np.array(near_cw)

    t5 = time.time()
    max_M_near = compute_list_sizes_gpu(cw, n, k, p, near_cw, delta_list)
    t_near = time.time() - t5

    if verbose:
        print(f"\nNear-codeword ({near_cw.shape[0]}), computed in {t_near:.2f}s:")
        print(f"{'delta':>6} {'w_max':>5} {'M_max':>6} {'above_J':>8}")
        for d in delta_list:
            w_max = int(d * n)
            above = "***" if d > delta_J else ""
            print(f"{d:6.2f} {w_max:5d} {max_M_near[d]:6d} {above:>8}")

    # --- Summary ---
    if verbose:
        print(f"\n{'='*60}")
        print(f"SUMMARY for n={n}, k={k}, p={p}")
        print(f"{'='*60}")
        print(f"{'delta':>6} {'random':>8} {'wt1':>8} {'wt2':>8} {'near_cw':>8} {'WORST':>8} {'above_J':>8}")
        for d in delta_list:
            worst = max(max_M_random[d], max_M_wt1[d], max_M_wt2[d], max_M_near[d])
            above = "***" if d > delta_J else ""
            print(f"{d:6.2f} {max_M_random[d]:8d} {max_M_wt1[d]:8d} {max_M_wt2[d]:8d} {max_M_near[d]:8d} {worst:8d} {above:>8}")

    print(f"\nTotal time: {time.time()-t0:.2f}s")
    return max_M_random, max_M_wt1, max_M_wt2, max_M_near

# ================================================================
# RUN
# ================================================================

# Feasible exact cases (p^k codewords must fit in memory)
cases = [
    (6, 3, 7),
    (6, 3, 13),
    (6, 3, 31),
    (6, 3, 61),
    (6, 3, 97),
    (8, 4, 17),
    (8, 4, 41),
    (8, 4, 73),
    (10, 5, 11),
    (10, 5, 31),
    (10, 5, 41),  # 41^5 = 115M — might be too large
    (12, 6, 13),
    (12, 6, 37),
    (14, 7, 29),
    (14, 7, 43),
    (16, 8, 17),
    (20, 10, 11),  # 11^10 = 25B — too large
    (20, 10, 41),  # 41^10 — way too large
]

# Filter to feasible cases
MAX_CODEWORDS = 5_000_000  # 5M codewords max
feasible = [(n, k, p) for n, k, p in cases if p**k <= MAX_CODEWORDS and (p-1) % n == 0]

print(f"Feasible cases (p^k <= {MAX_CODEWORDS}):")
for n, k, p in feasible:
    print(f"  n={n}, k={k}, p={p}: {p**k} codewords")

# Summary table
print(f"\n{'='*70}")
print(f"SCALING TABLE: M at delta=0.35 (just above Johnson for rate 1/2)")
print(f"{'='*70}")
print(f"{'n':>4} {'k':>4} {'p':>5} {'p^k':>10} {'M_worst':>10} {'delta_J':>8}")

for n, k, p in feasible:
    results = full_analysis(n, k, p, n_random=20000, verbose=True)
    max_M_random, max_M_wt1, max_M_wt2, max_M_near = results
    delta = 0.35
    worst = max(max_M_random.get(delta, 0), max_M_wt1.get(delta, 0),
                max_M_wt2.get(delta, 0), max_M_near.get(delta, 0))
    delta_J = 1 - np.sqrt(k/n)
    print(f"\n>>> n={n}, k={k}, p={p}: M_worst(0.35) = {worst}, delta_J = {delta_J:.4f}")
