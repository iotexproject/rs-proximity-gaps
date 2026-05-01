#!/usr/bin/env python3 -u
"""Analyze the n=8 c=2 witness deeper.

Witness: n=8, k=4, c=2, p=113
  s1 = [94, 77, 100, 104]
  s2 = [66, 86, 13, 43]
  E = (3,6), (5,6), (0,1), (3,5)
  γ = [22, 31, 60, 104]
  rank A = 7 (deficient by 1)
  All ⟨n_0(E_i), s_2⟩ = [79, 79, 19, 100] nonzero

Questions:
1. What is the kernel direction of A? (1-dim kernel)
2. Does this kernel direction have ANY special structure?
3. What's the corresponding row dependency in A?
4. Why doesn't the lemma's "∃i a_0 ≡ 0" branch save us here?
"""

import sys
import numpy as np
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp

n, k, c, p = 8, 4, 2, 113
D = n - k; w = D - c

s1 = np.array([94, 77, 100, 104], dtype=np.int64)
s2 = np.array([66, 86, 13, 43], dtype=np.int64)
E_list = [(3,6), (5,6), (0,1), (3,5)]
gammas = [22, 31, 60, 104]

omega = find_omega(n, p)
L = [pow(omega, i, p) for i in range(n)]
print(f"L = {L}")

# Build N_{E_i}
NE_list = []
for E in E_list:
    lam = elp(E, L, p)
    print(f"E={E}: ELP coeffs = {lam}  (length {len(lam)})")
    N = np.zeros((c, D), dtype=np.int64)
    for r in range(c):
        for j in range(D):
            t = j - r
            if 0 <= t <= w:
                N[r, j] = lam[t] % p
    NE_list.append(N)
    print(f"  N_E = \n{N}")

# Build matrix A
A = np.zeros((4 * c, 2 * D), dtype=np.int64)
for i in range(4):
    A[i*c:(i+1)*c, :D] = NE_list[i]
    A[i*c:(i+1)*c, D:] = (gammas[i] * NE_list[i]) % p

print(f"\nMatrix A ({A.shape}):")
print(A)

# Find kernel of A via Gauss
def gauss_kernel(M, p):
    """Returns (rank, basis of kernel) of M over F_p."""
    M = M.copy() % p
    rows, cols = M.shape
    pivot_cols = []
    M_work = M.copy()
    rank = 0
    for col in range(cols):
        pivot = None
        for r in range(rank, rows):
            if M_work[r, col] != 0:
                pivot = r; break
        if pivot is None:
            continue
        M_work[[rank, pivot]] = M_work[[pivot, rank]]
        inv = pow(int(M_work[rank, col]), p - 2, p)
        M_work[rank] = (M_work[rank] * inv) % p
        for r in range(rows):
            if r != rank and M_work[r, col] != 0:
                M_work[r] = (M_work[r] - M_work[r, col] * M_work[rank]) % p
        pivot_cols.append(col)
        rank += 1
    # Free cols → kernel basis
    free_cols = [c_ for c_ in range(cols) if c_ not in pivot_cols]
    kernel = []
    for fc in free_cols:
        v = np.zeros(cols, dtype=np.int64)
        v[fc] = 1
        for i, pc in enumerate(pivot_cols):
            v[pc] = (-M_work[i, fc]) % p
        kernel.append(v)
    return rank, kernel

rank, kernel = gauss_kernel(A, p)
print(f"\nrank A = {rank}, ker dim = {len(kernel)}")
for i, v in enumerate(kernel):
    print(f"\nker basis vec {i}:")
    print(f"  v = {v.tolist()}")
    s1_k = v[:D]; s2_k = v[D:]
    print(f"  s1_k = {s1_k.tolist()}")
    print(f"  s2_k = {s2_k.tolist()}")
    # Check: A · v = 0 mod p
    Av = (A @ v) % p
    print(f"  A·v = {Av.tolist()} (all 0? {np.all(Av == 0)})")

# Now check row dependence of A
# rank A < 8 means rows of A are linearly dependent
# Find a row dependency
print("\n=== Row dependence ===")
A_T = A.T  # 8 × 8 matrix
rank_T, kernel_T = gauss_kernel(A_T, p)
print(f"rank A^T = {rank_T}")
print(f"Number of row dependencies = {len(kernel_T)}")
for j, w in enumerate(kernel_T):
    print(f"  row coeffs: {w.tolist()}")
    # Check: w^T · A = 0
    wA = (w @ A) % p
    print(f"  w^T · A = {wA.tolist()} (all 0? {np.all(wA == 0)})")
    # Decompose by E: each E contributes c=2 rows
    for i, E in enumerate(E_list):
        coeffs_for_E = w[i*c:(i+1)*c]
        print(f"    E={E}: row coeffs {coeffs_for_E.tolist()}")

# Verify: a_0(E_i) ≠ 0 for all i (i.e. all open conditions hold)
print("\n=== Open conditions ===")
for i, E in enumerate(E_list):
    n0 = NE_list[i][0]  # leading row of N_{E_i}
    a0 = int((n0 @ s2) % p)
    print(f"  E={E}: n_0 = {n0.tolist()}, ⟨n_0, s_2⟩ = {a0}")

# Now, the lemma's "second branch" requires:
# for EVERY (s_1', s_2') ∈ ker A, ∃i such that ⟨n_0(E_i), s_2'⟩ = 0
# Test on the ker basis vector
print("\n=== Lemma second branch test ===")
for i, v in enumerate(kernel):
    print(f"ker vec {i}: s_2 part = {v[D:].tolist()}")
    for j, E in enumerate(E_list):
        a0_k = int((NE_list[j][0] @ v[D:]) % p)
        print(f"  E={E}: ⟨n_0, s_2_k⟩ = {a0_k}")
    s2_kernel = v[D:] % p
    a0_all = [int((NE_list[j][0] @ s2_kernel) % p) for j in range(4)]
    print(f"  All a_0 on ker s_2: {a0_all} — any zero? {0 in a0_all}")
