#!/usr/bin/env python3
"""
GPU-accelerated M_actual search for n=24.
C(24,8) = 735471 subsets — large but feasible with MPS.
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


def interpolate_codeword(n, k, p, L, c_vals, B):
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
    for row in range(len(pivot_cols), m):
        if aug[row][k] % p != 0:
            return None
    a = [0] * k
    for idx2, col in enumerate(pivot_cols):
        a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
    f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
    d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
    return f_vals, d


def gpu_search(n, k, p, w, max_centers=200000, batch_size=500):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w
    n_B = math.comb(n, w)

    t0 = time.time()
    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] F_{p}, w={w}, conds={conds}, C({n},{w})={n_B}")

    # Precompute σ
    print(f"Precomputing σ for {n_B} subsets...")
    all_B = list(combinations(range(n), w))
    sigma_cpu = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_cpu.append([es[j] % p for j in range(w + 1)])

    t1 = time.time()
    print(f"σ precomputation: {t1-t0:.1f}s")

    # T[B, j] = (-1)^j σ_j (mod p)
    T_list = []
    for b_idx in range(n_B):
        row = [pow(-1, j, p) * sigma_cpu[b_idx][j] % p for j in range(w + 1)]
        T_list.append(row)

    T_gpu = torch.tensor(T_list, dtype=torch.long, device=device)
    mem_mb = T_gpu.element_size() * T_gpu.nelement() / 1e6
    print(f"GPU tensor: {T_gpu.shape}, {mem_mb:.1f} MB")

    # For large n_B, process B in chunks to avoid OOM
    B_chunk = min(n_B, 100000)  # process 100K B's at a time

    best_M_alg = 0
    candidates = []
    total_checked = 0

    print(f"Searching {max_centers} centers (batch={batch_size}, B_chunk={B_chunk})...")

    for batch_start in range(0, max_centers, batch_size):
        batch_end = min(batch_start + batch_size, max_centers)
        actual_batch = batch_end - batch_start

        centers = torch.randint(0, p, (actual_batch, nk), dtype=torch.long, device=device)

        # Process B in chunks
        all_compat = torch.ones(actual_batch, n_B, dtype=torch.bool, device=device)

        for m_off in range(conds):
            max_j = min(w + 1, nk - m_off)
            if max_j <= 0:
                continue

            C_m = torch.zeros(actual_batch, w + 1, dtype=torch.long, device=device)
            for j in range(max_j):
                C_m[:, j] = centers[:, m_off + j]

            # Process B in chunks to avoid large intermediate
            for b_start in range(0, n_B, B_chunk):
                b_end = min(b_start + B_chunk, n_B)
                T_chunk = T_gpu[b_start:b_end]  # (chunk, w+1)

                val_f = torch.matmul(C_m.float(), T_chunk.float().T)
                val = val_f.long() % p

                all_compat[:, b_start:b_end] &= (val == 0)

        compat_counts = all_compat.sum(dim=1)
        interesting = (compat_counts >= 2).nonzero(as_tuple=True)[0]

        for ii in interesting:
            m_alg = compat_counts[ii].item()
            c_h = centers[ii].cpu().tolist()
            if m_alg > 500:
                continue  # overcounting
            candidates.append((m_alg, c_h))
            best_M_alg = max(best_M_alg, m_alg)

        total_checked += actual_batch
        if total_checked % (batch_size * 20) == 0 or total_checked >= max_centers:
            print(f"  {total_checked}/{max_centers}, cands={len(candidates)}, best_M_alg={best_M_alg}")

    t2 = time.time()
    print(f"GPU search: {t2-t1:.1f}s, {total_checked/(t2-t1):.0f} centers/sec")

    # Verify top candidates
    candidates.sort(key=lambda x: -x[0])
    n_verify = min(len(candidates), 100)
    print(f"\nVerifying M_actual for top {n_verify} candidates...")

    best_M_actual = 0
    best_center = None

    for rank, (m_alg, c_high) in enumerate(candidates[:n_verify]):
        c_coeffs = [0] * k + c_high
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p for i in range(n)]

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
            print(f"  [rank {rank}] M_alg={m_alg}, M_actual={M_actual} ({oc})")

    t3 = time.time()
    print(f"Verification: {t3-t2:.1f}s")
    print(f"\n*** RESULT: n={n}, p={p}, best M_actual = {best_M_actual} ***")

    return best_M_actual


# ===== Main =====
print("=" * 70)
print("M_actual GPU SEARCH — n=24")
print("=" * 70)

# n=24, p=73 (smallest valid prime)
gpu_search(24, 12, 73, 8, max_centers=100000, batch_size=200)
