#!/usr/bin/env python3
"""
Compute B_j(c) = sum_{v in RS^perp, wt(v)=j} psi(<v,c>) for all syndromes c
via FFT over (Z/pZ)^{n-k}.

Key quantities:
- A_j^perp = |Omega_j| (weight distribution of dual code)
- max|B_j(s)| vs sqrt(A_j^perp) (square-root cancellation?)
- E_j = additive energy of Omega_j
- E_j / (A_j^perp)^2 (flatness ratio; =1 iff |B_j| constant)
"""

import numpy as np
from collections import Counter
import sys
import time

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
        ok = True
        for q in factors:
            if pow(g, (p-1)//q, p) == 1:
                ok = False
                break
        if ok:
            return g
    return None

def find_omega(n, p):
    """Primitive n-th root of unity in F_p. Requires n | p-1."""
    assert (p - 1) % n == 0, f"n={n} does not divide p-1={p-1}"
    g = find_primitive_root(p)
    m = (p - 1) // n
    return pow(g, m, p)

def compute_Bj_analysis(n, k, p, verbose=True):
    """Full analysis of B_j(s) for RS[n,k] over F_p."""
    t0 = time.time()
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d = n - k  # dual code dimension
    total = p ** d  # syndrome space size

    if verbose:
        print(f"Parameters: n={n}, k={k}, p={p}, omega={omega}")
        print(f"L = {L}")
        print(f"Dual code: RS[{n},{d}], min dist {k+1}")
        print(f"Syndrome space: F_{p}^{d}, size {total}")

    # Precompute L_powers[i][r] = L[i]^r mod p
    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    # Enumerate all u in F_p^d, compute weight of dual codeword
    # P_u(omega^i) = sum_r u_r * L[i]^r mod p
    # weight = number of nonzero evaluations

    # Create all u vectors using numpy
    # u[idx] = multi-index (u_0, ..., u_{d-1})
    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)

    # Generate all coefficient vectors
    # For each u, compute eval on L and count nonzeros
    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    # Compute evaluations: eval_matrix[idx, i] = P_u(L[i]) mod p
    # = sum_r u_matrix[idx, r] * L_powers[i, r] mod p
    eval_matrix = u_matrix @ L_powers.T % p  # shape (total, n)

    # Weight = number of nonzero evals
    weights = np.count_nonzero(eval_matrix, axis=1)  # shape (total,)

    # Fill weight array
    for idx in range(total):
        u_tuple = tuple(u_matrix[idx])
        wt_array[u_tuple] = weights[idx]

    # Weight distribution
    weight_dist = Counter(weights.tolist())
    if verbose:
        print(f"\nDual code weight distribution (A_j^perp):")
        for j in sorted(weight_dist.keys()):
            print(f"  A_{j} = {weight_dist[j]}")

    # Compute B_j(s) via FFT for each weight j >= k+1
    results = {}

    for j in sorted(weight_dist.keys()):
        if j < k + 1 and j > 0:
            continue
        if j == 0:
            continue  # skip zero codeword

        Aj = weight_dist[j]
        if Aj == 0:
            continue

        # Indicator array
        indicator = (wt_array == j).astype(np.complex128)

        # FFT
        fft_result = np.fft.fftn(indicator)
        Bj_abs = np.abs(fft_result)

        rms = np.sqrt(Aj)
        max_Bj = np.max(Bj_abs)
        min_Bj = np.min(Bj_abs)

        # Parseval check: sum |B_j|^2 = total * A_j
        second_moment = np.sum(Bj_abs ** 2)
        parseval_ratio = second_moment / (total * Aj)

        # Fourth moment / additive energy
        fourth_moment = np.sum(Bj_abs ** 4)
        Ej = fourth_moment / total
        energy_ratio = Ej / (Aj ** 2)

        # Distribution of |B_j| values
        rounded = np.round(Bj_abs, 4)
        val_counts = Counter(rounded.flatten().tolist())
        n_distinct = len(val_counts)

        ratio = max_Bj / rms

        results[j] = {
            'Aj': Aj, 'rms': rms, 'max': max_Bj, 'min': min_Bj,
            'ratio': ratio, 'Ej': Ej, 'energy_ratio': energy_ratio,
            'parseval_ok': abs(parseval_ratio - 1.0) < 1e-6,
            'n_distinct': n_distinct, 'val_counts': val_counts,
        }

        if verbose:
            print(f"\n--- j = {j} ---")
            print(f"  A_j = {Aj}, sqrt(A_j) = {rms:.4f}")
            print(f"  max|B_j| = {max_Bj:.6f}, min|B_j| = {min_Bj:.6f}")
            print(f"  ratio max/sqrt(A_j) = {ratio:.6f}")
            print(f"  Parseval: {'OK' if results[j]['parseval_ok'] else 'FAIL'} ({parseval_ratio:.8f})")
            print(f"  Additive energy E_j = {Ej:.2f}")
            print(f"  E_j / A_j^2 = {energy_ratio:.8f} (=1 iff |B_j| constant)")
            print(f"  Distinct |B_j| values: {n_distinct}")

            if n_distinct <= 20:
                print(f"  |B_j| distribution:")
                for val, cnt in sorted(val_counts.items()):
                    pct = cnt / total * 100
                    print(f"    |B_j| = {val:.4f}: {cnt} syndromes ({pct:.1f}%)")

    elapsed = time.time() - t0
    if verbose:
        print(f"\nTotal time: {elapsed:.2f}s")

    return results, weight_dist

def compute_Nw_and_list_size(n, k, p, results, weight_dist, verbose=True):
    """
    From B_j(s), compute N_w(c) = (1/p^k) sum_j B_j(c) K_w(j)
    and the list size M = max_c sum_{w <= delta*n} N_w(c).
    """
    d = n - k
    total = p ** d
    omega_root = find_omega(n, p)
    L = [pow(omega_root, i, p) for i in range(n)]

    # Krawtchouk polynomials K_w(j; n, p)
    # K_w(j) = sum_{s=0}^{j} (-1)^s (p-1)^{j-s} C(j,s) C(n-j, w-s)  [wrong]
    # Standard: K_w(j; n, q) = sum_{s=0}^{w} (-1)^s (q-1)^{w-s} C(j,s) C(n-j,w-s)

    from math import comb

    def krawtchouk(w, j, n, q):
        """Krawtchouk polynomial K_w(j; n, q)."""
        val = 0
        for s in range(min(w, j) + 1):
            if w - s > n - j:
                continue
            val += (-1)**s * (q-1)**(w-s) * comb(j, s) * comb(n-j, w-s)
        return val

    # Compute K_w(j) for all w, j
    K = np.zeros((n+1, n+1), dtype=np.float64)
    for w in range(n+1):
        for j in range(n+1):
            K[w, j] = krawtchouk(w, j, n, p)

    # Main term for N_w: (1/p^k) * K_w(0) = (1/p^k) * C(n,w) * (p-1)^w
    if verbose:
        print(f"\n{'='*60}")
        print(f"List size analysis for n={n}, k={k}, p={p}")
        print(f"{'='*60}")

        # Johnson bound
        rho = k / n
        delta_J = 1 - np.sqrt(rho)
        print(f"Rate rho = {rho:.4f}, Johnson bound delta_J = {delta_J:.4f}")
        print(f"Johnson radius = {delta_J * n:.2f}")

    # For each syndrome s, compute N_w(s) for all w
    # N_w(s) = (1/p^k) * [K_w(0) + sum_{j>=k+1} B_j(s) K_w(j)]
    # We need to reconstruct B_j(s) for each s from the FFT results.

    # Actually, let's recompute: enumerate all syndromes via direct computation
    # For small cases, enumerate all c in F_p^n, compute syndrome and weight to codeword

    # Alternative: use the FFT results directly
    # B_j(s) for each s is stored in the FFT arrays
    # But we didn't save them. Let me recompute.

    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)

    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    eval_matrix = u_matrix @ L_powers.T % p
    weights = np.count_nonzero(eval_matrix, axis=1)

    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    # For each j, compute B_j(s) as complex array
    Bj_arrays = {}
    for j in range(k+1, n+1):
        if weight_dist[j] == 0:
            continue
        indicator = (wt_array == j).astype(np.complex128)
        # B_j(s) = conj(FFT(indicator)[s])
        Bj_arrays[j] = np.conj(np.fft.fftn(indicator))

    # Compute N_w(s) for each w and s
    # N_w(s) = (1/p^k) * [K_w(0) + sum_j B_j(s) K_w(j)]
    # K_w(0) = C(n,w) * (p-1)^w

    pk = p ** k

    if verbose:
        print(f"\nN_w(c) analysis:")
        print(f"{'w':>4} {'main':>12} {'max_Nw':>8} {'max_err':>10} {'#Nw>0':>8}")

    max_list = {}
    for w in range(n+1):
        main_term = K[w, 0] / pk

        # Compute R_w(s) = (1/p^k) sum_{j>=k+1} B_j(s) K_w(j)
        Rw = np.zeros(shape, dtype=np.complex128)
        for j, Bj in Bj_arrays.items():
            Rw += Bj * K[w, j]
        Rw /= pk

        Nw = main_term + Rw.real  # should be real and integer

        max_Nw = np.max(Nw)
        max_err = np.max(np.abs(Rw))
        n_positive = np.sum(Nw > 0.5)

        max_list[w] = max_Nw

        if verbose and (max_Nw > 0.5 or w <= k+2):
            print(f"{w:4d} {main_term:12.4f} {max_Nw:8.1f} {max_err:10.6f} {n_positive:8d}")

    # List size M(delta) = max_s sum_{w <= delta*n} N_w(s)
    if verbose:
        print(f"\nList size M(delta) = max_s |{{codewords within delta*n of s}}|:")
        for delta_pct in range(10, 100, 5):
            delta = delta_pct / 100.0
            w_max = int(delta * n)

            M_array = np.zeros(shape, dtype=np.float64)
            for w in range(w_max + 1):
                main_term = K[w, 0] / pk
                Rw = np.zeros(shape, dtype=np.complex128)
                for j, Bj in Bj_arrays.items():
                    Rw += Bj * K[w, j]
                Rw /= pk
                M_array += main_term + Rw.real

            M = np.max(M_array)
            M_avg = np.mean(M_array)

            above_J = " <-- above Johnson" if delta > 1 - np.sqrt(k/n) else ""
            print(f"  delta={delta:.2f} (w<={w_max}): M_max={M:.1f}, M_avg={M_avg:.2f}{above_J}")

# ====================================================================
# RUN
# ====================================================================

print("=" * 70)
print("CASE 1: n=4, k=2, p=5  (tiny)")
print("=" * 70)
r1, wd1 = compute_Bj_analysis(4, 2, 5)
compute_Nw_and_list_size(4, 2, 5, r1, wd1)

print("\n" + "=" * 70)
print("CASE 2: n=6, k=3, p=7")
print("=" * 70)
r2, wd2 = compute_Bj_analysis(6, 3, 7)
compute_Nw_and_list_size(6, 3, 7, r2, wd2)

print("\n" + "=" * 70)
print("CASE 3: n=6, k=3, p=13")
print("=" * 70)
r3, wd3 = compute_Bj_analysis(6, 3, 13)
compute_Nw_and_list_size(6, 3, 13, r3, wd3)

print("\n" + "=" * 70)
print("CASE 4: n=8, k=4, p=17")
print("=" * 70)
r4, wd4 = compute_Bj_analysis(8, 4, 17)
compute_Nw_and_list_size(8, 4, 17, r4, wd4)

# Scaling: same n,k, increasing p
print("\n" + "=" * 70)
print("SCALING: n=6, k=3, p varies")
print("=" * 70)
print(f"{'p':>5} {'j':>3} {'A_j':>8} {'sqrt(Aj)':>10} {'max|Bj|':>10} {'ratio':>8} {'E/A^2':>10}")
for p_val in [7, 13, 19, 31, 37, 43]:
    if (p_val - 1) % 6 != 0:
        continue
    r, wd = compute_Bj_analysis(6, 3, p_val, verbose=False)
    for j in sorted(r.keys()):
        rr = r[j]
        print(f"{p_val:5d} {j:3d} {rr['Aj']:8d} {rr['rms']:10.4f} {rr['max']:10.4f} {rr['ratio']:8.4f} {rr['energy_ratio']:10.6f}")
