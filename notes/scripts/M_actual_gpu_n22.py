#!/usr/bin/env python3
"""
GPU-accelerated M_actual search for n=22,24.
Uses PyTorch MPS for batch compatibility check, CPU for interpolation.

Strategy:
1. Precompute σ for all C(n,w) subsets (CPU)
2. Batch random centers, check compatibility (GPU)
3. For centers with M_alg ≥ 2, compute M_actual via interpolation (CPU)
4. Track max M_actual

Memory-conscious: process conditions one at a time to avoid large intermediates.
"""

import torch
import math
from itertools import combinations
import time
import random

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Device: {device}")


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
    return pow(find_primitive_root(p), (p - 1) // n, p)


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def primes_cong_1(n, count=3):
    result = []
    pp = n + 1
    while len(result) < count:
        if pp % n == 1:
            is_prime = pp > 1
            for d in range(2, int(pp ** 0.5) + 1):
                if pp % d == 0:
                    is_prime = False
                    break
            if is_prime:
                result.append(pp)
        pp += 1
    return result


def interpolate_codeword(n, k, p, L, c_vals, B):
    """Interpolate c on S = L\\B to find codeword. Returns (f_vals, dist) or None."""
    S = [i for i in range(n) if i not in B]
    m = len(S)
    aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]] for i in range(m)]

    pivot_cols = []
    for col in range(k):
        piv = -1
        for row in range(len(pivot_cols), m):
            if aug[row][col] % p != 0:
                piv = row
                break
        if piv == -1:
            continue
        r2 = len(pivot_cols)
        aug[r2], aug[piv] = aug[piv], aug[r2]
        inv_p = pow(aug[r2][col], p - 2, p)
        for row in range(m):
            if row != r2 and aug[row][col] % p != 0:
                f2 = aug[row][col] * inv_p % p
                for j2 in range(k + 1):
                    aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
        pivot_cols.append(col)

    # Check consistency
    for row in range(len(pivot_cols), m):
        if aug[row][k] % p != 0:
            return None

    a = [0] * k
    for idx2, col in enumerate(pivot_cols):
        a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p

    f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
    d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
    return f_vals, d


def gpu_search_M_actual(n, k, p, w, max_centers=500000, batch_size=2000):
    """GPU-accelerated search returning M_actual (distinct codewords)."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w
    n_B = math.comb(n, w)

    t0 = time.time()
    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] F_{p}, w={w}, conds={conds}, C({n},{w})={n_B}")
    print(f"Precomputing σ for {n_B} subsets...")

    # Precompute σ values: (n_B, w+1) — σ_0=1, σ_1, ..., σ_w
    all_B = list(combinations(range(n), w))
    sigma_cpu = []  # list of (σ_0=1, σ_1, ..., σ_w)
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_cpu.append([es[j] % p for j in range(w + 1)])

    t1 = time.time()
    print(f"σ precomputation: {t1-t0:.1f}s")

    # Precompute sign-adjusted σ: T[B, j] = (-1)^j σ_j (mod p)
    # T has shape (n_B, w+1)
    T_list = []
    for b_idx in range(n_B):
        row = []
        for j in range(w + 1):
            row.append(pow(-1, j, p) * sigma_cpu[b_idx][j] % p)
        T_list.append(row)

    # Move to GPU (use long for exact arithmetic with small p)
    T_gpu = torch.tensor(T_list, dtype=torch.long, device=device)  # (n_B, w+1)
    print(f"GPU tensor: {T_gpu.shape}, {T_gpu.element_size() * T_gpu.nelement() / 1e6:.1f} MB")

    # Search
    total_checked = 0
    best_M_actual = 0
    best_M_alg = 0
    best_center = None
    candidates = []  # (M_alg, c_high) pairs to verify

    print(f"Searching {max_centers} centers (batch={batch_size})...")

    for batch_start in range(0, max_centers, batch_size):
        batch_end = min(batch_start + batch_size, max_centers)
        actual_batch = batch_end - batch_start

        # Generate random centers
        centers = torch.randint(0, p, (actual_batch, nk), dtype=torch.long, device=device)

        # For each condition m_off, compute:
        # val[center, B] = Σ_{j=0}^w T[B,j] * centers[center, m_off+j]
        # = T @ C_m^T  where C_m[center, j] = centers[center, m_off+j]

        # Check all conditions: val ≡ 0 (mod p) for all m_off
        all_compat = torch.ones(actual_batch, n_B, dtype=torch.bool, device=device)

        for m_off in range(conds):
            # Gather: C_m[center, j] = centers[center, m_off + j] for j=0,...,w
            # Need m_off + j < nk
            max_j = min(w + 1, nk - m_off)
            if max_j <= 0:
                continue

            C_m = torch.zeros(actual_batch, w + 1, dtype=torch.long, device=device)
            for j in range(max_j):
                C_m[:, j] = centers[:, m_off + j]

            # val = C_m @ T^T  — (batch, w+1) @ (w+1, n_B) = (batch, n_B)
            # Use float for MPS matmul, then convert back
            val_f = torch.matmul(C_m.float(), T_gpu.float().T)
            val = val_f.long() % p  # (batch, n_B)

            # Update compatibility: must be 0 for all conditions
            all_compat &= (val == 0)

        # Count compatible B's per center
        compat_counts = all_compat.sum(dim=1)  # (batch,)

        # Find interesting centers (M_alg ≥ 2)
        interesting = (compat_counts >= 2).nonzero(as_tuple=True)[0]

        for ii in interesting:
            m_alg = compat_counts[ii].item()
            c_h = centers[ii].cpu().tolist()

            # Quick filter: skip overcounting-heavy centers
            # (centers where M_alg > 2*w are likely close to a codeword)
            if m_alg > 3 * n_B / p ** conds + 50:
                continue  # almost certainly overcounting

            candidates.append((m_alg, c_h))
            if m_alg > best_M_alg:
                best_M_alg = m_alg

        total_checked += actual_batch
        if (batch_start + actual_batch) % (batch_size * 50) == 0 or batch_start + actual_batch >= max_centers:
            print(f"  Checked {total_checked}/{max_centers}, "
                  f"candidates={len(candidates)}, best_M_alg={best_M_alg}")

    t2 = time.time()
    print(f"GPU search: {t2-t1:.1f}s, {total_checked/(t2-t1):.0f} centers/sec")

    # Sort candidates by M_alg, verify top ones
    candidates.sort(key=lambda x: -x[0])
    n_verify = min(len(candidates), 200)  # verify top 200
    print(f"\nVerifying M_actual for top {n_verify} candidates...")

    for rank, (m_alg, c_high) in enumerate(candidates[:n_verify]):
        # Build full center
        c_coeffs = [0] * k + c_high
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
                  for i in range(n)]

        # Find compatible B's and interpolate
        codewords = set()
        has_close = False

        for b_idx in range(n_B):
            es = sigma_cpu[b_idx]
            ok = True
            for m_off in range(conds):
                val = 0
                for j in range(w + 1):
                    c_idx = m_off + j
                    if c_idx < nk:
                        val += pow(-1, j, p) * es[j] * c_high[c_idx]
                if val % p != 0:
                    ok = False
                    break
            if not ok:
                continue

            B = set(all_B[b_idx])
            result = interpolate_codeword(n, k, p, L, c_vals, B)
            if result is None:
                continue
            f_vals, d = result
            if d < w:
                has_close = True
            codewords.add(f_vals)

        M_actual = len(codewords)
        if M_actual > best_M_actual:
            best_M_actual = M_actual
            best_center = c_high
            oc = "OVERCOUNT" if has_close else "exact"
            print(f"  [rank {rank}] M_alg={m_alg}, M_actual={M_actual} ({oc}), "
                  f"c_high={c_high[:6]}...")

    t3 = time.time()
    print(f"Verification: {t3-t2:.1f}s")
    print(f"\n*** RESULT: n={n}, p={p}, best M_actual = {best_M_actual} ***")
    if best_center:
        print(f"    center = {best_center}")

    return best_M_actual


# ===== Main =====
print("=" * 70)
print("M_actual GPU SEARCH — Large n")
print("=" * 70)

# n=22: feasible, C(22,7) = 170K
gpu_search_M_actual(22, 11, 23, 7, max_centers=500000, batch_size=2000)

# Also try n=22 with a larger prime
ps_22 = primes_cong_1(22, 3)
print(f"\nAll primes for n=22: {ps_22}")
if len(ps_22) > 1:
    gpu_search_M_actual(22, 11, ps_22[1], 7, max_centers=200000, batch_size=2000)

# n=20 (verification: known M=0)
gpu_search_M_actual(20, 10, 41, 6, max_centers=200000, batch_size=2000)
