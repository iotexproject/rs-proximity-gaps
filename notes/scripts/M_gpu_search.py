#!/usr/bin/env python3
"""
GPU-accelerated M search using PyTorch + MPS (Apple Silicon).
Key insight: compatibility check = batch modular matrix multiplication.

For each center c_high, conditions are A·σ = b (mod p).
We batch over centers and parallelize the σ check.
"""

import torch
import math
from itertools import combinations
import time

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")


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


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def primes_cong_1(n, count=5):
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


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def gpu_search(n, k, p, w, max_centers=500000, batch_size=5000):
    """
    GPU-accelerated search for worst-case M.
    Uses batch modular arithmetic on MPS.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k
    nk = n - k
    n_B = math.comb(n, w)

    t0 = time.time()

    # Precompute σ values (n_B × w) as torch tensor
    all_B = list(combinations(range(n), w))
    sigma_list = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        sigma_list.append([sigma[j] % p for j in range(1, w + 1)])

    # σ tensor on device: shape (n_B, w)
    sigma_t = torch.tensor(sigma_list, dtype=torch.long, device=device)

    # Sign vector: signs[j] = (-1)^{j+1} mod p
    signs = torch.tensor([pow(-1, j + 1, p) for j in range(w)], dtype=torch.long, device=device)

    # Precompute: for conditions at m = k+w+m_off (m_off=0,...,conds-1):
    # A[m_off, j] = (-1)^{j+1} * c_high[m_off + j + 1]  (j=0,...,w-1, for σ_{j+1})
    # b[m_off] = -c_high[m_off]
    # Wait, let me re-derive:
    # Condition at m = k+w+m_off:
    # Σ_{j=0}^w (-1)^j σ_j c[m-w+j] = 0
    # = c[m-w] + Σ_{j=1}^w (-1)^j σ_j c[m-w+j] = 0
    # where c[idx] = c_high[idx - k] for k ≤ idx < n
    # m - w = k + m_off, so c[m-w] = c_high[m_off]
    # m - w + j = k + m_off + j, so c[m-w+j] = c_high[m_off + j]
    # A[m_off, j-1] = (-1)^j c_high[m_off + j]  (for j=1,...,w)
    # b[m_off] = -c_high[m_off]

    # Index mapping: for c_high of length nk, the c_high index used is:
    # A: m_off + j  (j=1,...,w)
    # b: m_off
    # Range check: m_off + w ≤ nk - 1 → m_off ≤ nk - w - 1 = conds - 1 ✓

    # For batch: C shape (batch, nk)
    # A_batch[i, m_off, j-1] = (-1)^j * C[i, m_off + j]
    # b_batch[i, m_off] = -C[i, m_off]

    # Precompute index tensors for gather
    # A indices: for each (m_off, j), the c_high index is m_off + j + 1... wait
    # j goes from 1 to w, so j-1 from 0 to w-1
    # c_high index = m_off + j where j = 1,...,w
    a_indices = torch.zeros(conds, w, dtype=torch.long, device=device)
    for m_off in range(conds):
        for jj in range(w):
            a_indices[m_off, jj] = m_off + jj + 1  # c_high[m_off + j], j = jj+1

    # sign[j] for j=1,...,w: (-1)^j mod p
    a_signs = torch.tensor([pow(-1, j + 1, p) for j in range(w)], dtype=torch.long, device=device)
    # signs[0] = (-1)^1 = p-1, signs[1] = (-1)^2 = 1, etc.

    total = p ** nk
    is_exhaustive = total <= max_centers
    n_centers = min(total, max_centers)

    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] F_{p}, w={w}, conds/B={conds}, C({n},{w})={n_B}")
    print(f"Centers to check: {n_centers} ({'exhaustive' if is_exhaustive else 'random'})")

    best_M_alg = 0
    best_center = None

    for batch_start in range(0, n_centers, batch_size):
        batch_end = min(batch_start + batch_size, n_centers)
        actual_batch = batch_end - batch_start

        # Generate centers
        if is_exhaustive:
            # Systematic enumeration
            centers = torch.zeros(actual_batch, nk, dtype=torch.long, device=device)
            for ii in range(actual_batch):
                idx = batch_start + ii
                temp = idx
                for jj in range(nk):
                    centers[ii, jj] = temp % p
                    temp //= p
        else:
            centers = torch.randint(0, p, (actual_batch, nk), dtype=torch.long, device=device)

        # Build A_batch: (batch, conds, w)
        # A[i, m_off, j] = a_signs[j] * centers[i, m_off + j + 1]
        A_batch = torch.zeros(actual_batch, conds, w, dtype=torch.long, device=device)
        for m_off in range(conds):
            for jj in range(w):
                c_idx = int(a_indices[m_off, jj].item())
                if c_idx < nk:
                    A_batch[:, m_off, jj] = (a_signs[jj] * centers[:, c_idx]) % p

        # Build b_batch: (batch, conds)
        b_batch = torch.zeros(actual_batch, conds, dtype=torch.long, device=device)
        for m_off in range(conds):
            b_batch[:, m_off] = (-centers[:, m_off]) % p

        # Compatibility check: A_batch @ sigma_t.T → (batch, conds, n_B)
        # Then check (result - b_batch.unsqueeze(2)) % p == 0
        # MPS doesn't support int64 matmul well, use float32
        A_f = A_batch.float()
        S_f = sigma_t.float().T  # (w, n_B)
        dots = torch.matmul(A_f, S_f)  # (batch, conds, n_B)

        # Convert back to int and mod p
        # For small p and small values, float32 should be exact
        dots_int = dots.long() % p  # (batch, conds, n_B)

        # Check: dots_int == b_batch.unsqueeze(2)
        b_exp = b_batch.unsqueeze(2).expand_as(dots_int)
        matches = (dots_int == b_exp)  # (batch, conds, n_B)

        # All conditions satisfied: AND over dim 1
        all_match = matches.all(dim=1)  # (batch, n_B)

        # Count compatible B's per center
        compat_counts = all_match.sum(dim=1)  # (batch,)

        # Find centers with interesting compat counts (2-50)
        mask = (compat_counts >= 2) & (compat_counts <= 50)
        interesting = mask.nonzero(as_tuple=True)[0]

        for ii in interesting:
            cnt = compat_counts[ii].item()
            if cnt > best_M_alg:
                best_M_alg = cnt
                best_center = centers[ii].cpu().tolist()

    t1 = time.time()
    print(f"Search time: {t1-t0:.1f}s")
    print(f"Best M_alg = {best_M_alg}")

    # Now verify M_actual for the best center (CPU, with interpolation)
    if best_center and best_M_alg > 0:
        c_high = best_center
        c_coeffs = [0] * k + c_high
        c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
                  for i in range(n)]

        codewords = set()
        has_close = False
        compat_B = []

        for idx in range(n_B):
            B = all_B[idx]
            sv = sigma_list[idx]
            # Check conditions
            ok = True
            for m_off in range(conds):
                val = c_high[m_off]  # σ_0 term
                for jj in range(w):
                    c_idx = m_off + jj + 1
                    if c_idx < nk:
                        val += pow(-1, jj + 1, p) * c_high[c_idx] * sv[jj]
                if val % p != 0:
                    ok = False
                    break
            if not ok:
                continue
            compat_B.append(B)

            # Interpolate
            S = [i for i in range(n) if i not in B]
            m_sys = len(S)
            aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
                   for i in range(m_sys)]
            pivot_cols = []
            for col in range(k):
                piv = -1
                for row in range(len(pivot_cols), m_sys):
                    if aug[row][col] % p != 0:
                        piv = row
                        break
                if piv == -1:
                    continue
                r2 = len(pivot_cols)
                aug[r2], aug[piv] = aug[piv], aug[r2]
                inv_p = pow(aug[r2][col], p - 2, p)
                for row in range(m_sys):
                    if row != r2 and aug[row][col] % p != 0:
                        f2 = aug[row][col] * inv_p % p
                        for j2 in range(k + 1):
                            aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
                pivot_cols.append(col)
            consistent = True
            for row in range(len(pivot_cols), m_sys):
                if aug[row][k] % p != 0:
                    consistent = False
                    break
            if not consistent:
                continue
            a = [0] * k
            for idx2, col in enumerate(pivot_cols):
                a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
            f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                          for i in range(n))
            d_val = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
            if d_val < w:
                has_close = True
            codewords.add(f_vals)

        M_actual = len(codewords)
        print(f"M_actual = {M_actual} (M_alg = {best_M_alg}, overcount={'YES' if has_close else 'NO'})")
        print(f"c_high = {best_center}")
        if not has_close:
            print(f"Compatible B's: {compat_B[:20]}")

    return best_M_alg, best_center


# ===== Main =====
print("=" * 70)
print("GPU-ACCELERATED M SEARCH (p-independence check)")
print("=" * 70)

for n in [10, 12, 14]:
    k = n // 2
    w = johnson_radius(n, k)
    conds = n - w - k
    ps = primes_cong_1(n, 4)

    print(f"\n>>> n={n}, k={k}, w={w}, conds/B={conds}")
    for p in ps:
        gpu_search(n, k, p, w, max_centers=300000, batch_size=2000)
