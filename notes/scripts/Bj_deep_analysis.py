#!/usr/bin/env python3
"""
Deep analysis of B_j(c):
1. Exclude s=0, study second-largest |B_j| scaling with p
2. Identify WHICH syndromes give extreme |B_j| (coset weight?)
3. Study the Krawtchouk-weighted sum R_w(s) directly
4. Check normalization: N_w = (1/q^{n-k}) sum_j B_j K_w(j) (CORRECT formula)
5. Test whether |B_j| is determined by the minimum coset weight
"""

import numpy as np
from collections import Counter, defaultdict
from math import comb
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
        if all(pow(g, (p-1)//q, p) != 1 for q in factors):
            return g

def find_omega(n, p):
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def krawtchouk(w, j, n, q):
    val = 0
    for s in range(min(w, j) + 1):
        if w - s > n - j:
            continue
        val += (-1)**s * (q-1)**(w-s) * comb(j, s) * comb(n-j, w-s)
    return val

def deep_analysis(n, k, p):
    """Full analysis excluding s=0, with syndrome structure identification."""
    t0 = time.time()
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d = n - k
    total = p ** d

    # Precompute L_powers
    L_powers = np.zeros((n, d), dtype=np.int64)
    for i in range(n):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p

    # All coefficient vectors u in F_p^d
    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p ** dim)) % p

    # Evaluate P_u on L: eval_matrix[idx, i] = P_u(L[i]) mod p
    eval_matrix = u_matrix @ L_powers.T % p
    weights = np.count_nonzero(eval_matrix, axis=1)

    # Weight distribution
    shape = tuple([p] * d)
    wt_array = np.zeros(shape, dtype=np.int32)
    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    weight_dist = Counter(weights.tolist())

    print(f"=== n={n}, k={k}, p={p} ===")
    print(f"Dual code RS[{n},{d}], d_min={k+1}")

    # --------------------------------------------------------
    # PART 1: Compute B_j(s) via FFT, analyze excluding s=0
    # --------------------------------------------------------
    Bj_complex = {}  # j -> complex FFT array (B_j(s))

    for j in sorted(weight_dist.keys()):
        if j == 0 or weight_dist[j] == 0:
            continue
        indicator = (wt_array == j).astype(np.complex128)
        fft_result = np.fft.fftn(indicator)
        Bj_complex[j] = np.conj(fft_result)  # B_j(s) = conj(FFT)

    print(f"\nB_j analysis (excluding s=0):")
    print(f"{'j':>3} {'A_j':>8} {'sqrt':>8} {'max*':>10} {'ratio*':>8} {'2nd':>10} {'3rd':>10} {'#vals':>6}")

    for j in sorted(Bj_complex.keys()):
        if j < k+1:
            continue
        Aj = weight_dist[j]
        Bj_abs = np.abs(Bj_complex[j])

        # Get all |B_j| values, sorted descending
        flat = Bj_abs.flatten()
        sorted_vals = np.sort(flat)[::-1]

        # sorted_vals[0] should be A_j (at s=0)
        max_all = sorted_vals[0]
        max_excl = sorted_vals[1] if len(sorted_vals) > 1 else 0
        third = sorted_vals[2] if len(sorted_vals) > 2 else 0

        rms = np.sqrt(Aj)
        ratio_excl = max_excl / rms if rms > 0 else 0

        # Count distinct values
        unique = len(np.unique(np.round(flat, 4)))

        print(f"{j:3d} {Aj:8d} {rms:8.2f} {max_excl:10.4f} {ratio_excl:8.4f} {sorted_vals[2] if len(sorted_vals)>2 else 0:10.4f} {sorted_vals[min(3,len(sorted_vals)-1)]:10.4f} {unique:6d}")

    # --------------------------------------------------------
    # PART 2: Identify syndromes by minimum coset weight
    # --------------------------------------------------------
    print(f"\n--- Syndrome → minimum coset weight ---")

    # For each syndrome s, compute the minimum weight of vectors in the coset
    # This is expensive for large cases, so only do for small ones
    if total <= 100000:
        # Compute syndrome for each vector in F_p^n
        # Syndrome s_r = sum_i c_i * L[i]^{k+r} for r=0,...,d-1
        # Use parity check matrix H: H[r][i] = L[i]^{k+r}

        H = np.zeros((d, n), dtype=np.int64)
        for r in range(d):
            for i in range(n):
                H[r, i] = pow(L[i], k + r, p)

        # For each syndrome, find minimum weight coset representative
        # Enumerate vectors of increasing weight until all syndromes covered
        syn_min_wt = {}  # syndrome tuple -> min weight

        # Weight 0: only the zero vector, syndrome = (0,...,0)
        syn_min_wt[tuple([0]*d)] = 0

        # Weight 1: vectors with one nonzero coordinate
        for i in range(n):
            for v in range(1, p):
                syn = tuple((v * H[:, i]) % p)
                if syn not in syn_min_wt:
                    syn_min_wt[syn] = 1

        # Weight 2: vectors with two nonzero coordinates
        if len(syn_min_wt) < total:
            for i in range(n):
                for j in range(i+1, n):
                    for vi in range(1, p):
                        for vj in range(1, p):
                            syn = tuple((vi * H[:, i] + vj * H[:, j]) % p)
                            if syn not in syn_min_wt:
                                syn_min_wt[syn] = 2
                if len(syn_min_wt) >= total:
                    break

        # Weight 3 if needed (for small cases)
        if len(syn_min_wt) < total and n <= 10:
            for i in range(n):
                for j in range(i+1, n):
                    for l in range(j+1, n):
                        for vi in range(1, p):
                            for vj in range(1, p):
                                for vl in range(1, p):
                                    syn = tuple((vi * H[:, i] + vj * H[:, j] + vl * H[:, l]) % p)
                                    if syn not in syn_min_wt:
                                        syn_min_wt[syn] = 3
                        if len(syn_min_wt) >= total:
                            break
                    if len(syn_min_wt) >= total:
                        break
                if len(syn_min_wt) >= total:
                    break

        # For remaining (weight >= d_min/2 or higher)
        remaining = total - len(syn_min_wt)
        if remaining > 0:
            max_known_wt = max(syn_min_wt.values()) if syn_min_wt else -1
            print(f"  Covered {len(syn_min_wt)}/{total} syndromes up to weight {max_known_wt}")
            print(f"  Remaining {remaining} syndromes have min weight >= {max_known_wt + 1}")

        # Map syndrome -> |B_j| value for each j
        # Check: does |B_j(s)| depend only on min_wt(s)?
        for j in sorted(Bj_complex.keys()):
            if j < k+1:
                continue
            Bj_abs = np.abs(Bj_complex[j])

            # Group by min_wt
            wt_to_bj_vals = defaultdict(list)
            for syn_tuple, min_wt in syn_min_wt.items():
                bj_val = round(Bj_abs[syn_tuple], 4)
                wt_to_bj_vals[min_wt].append(bj_val)

            print(f"\n  j={j}: |B_j| grouped by min coset weight:")
            for w in sorted(wt_to_bj_vals.keys()):
                vals = wt_to_bj_vals[w]
                val_counts = Counter(vals)
                print(f"    min_wt={w}: {dict(val_counts)}")

    # --------------------------------------------------------
    # PART 3: Direct computation of R_w(s) and list size
    # --------------------------------------------------------
    print(f"\n--- List size analysis (correct normalization: 1/p^{{n-k}}) ---")

    # Precompute Krawtchouk values
    K = np.zeros((n+1, n+1), dtype=np.float64)
    for w in range(n+1):
        for j in range(n+1):
            K[w, j] = krawtchouk(w, j, n, p)

    # For each w, compute N_w(s) for all s
    # N_w(s) = (1/p^{n-k}) sum_j K_w(j) * conj(B_j(s))
    # But B_j(s) is already computed as conj(FFT), so conj(B_j(s)) = FFT result
    # Actually let's just use: N_w = (1/p^{n-k}) Re[sum_j K_w(j) * conj(B_j)]

    delta_J = 1 - np.sqrt(k / n)
    print(f"Rate rho = {k/n:.4f}, Johnson bound delta_J = {delta_J:.4f}")
    print(f"Johnson radius = {delta_J * n:.2f}")

    print(f"\n{'w':>3} {'delta':>6} {'main':>10} {'max_Nw':>8} {'max_Nw*':>8} {'max_err':>10} {'max_err*':>10} {'above_J':>8}")

    zero_syn = tuple([0]*d)

    for w in range(n+1):
        Nw = np.zeros(shape, dtype=np.float64)
        for j, Bj in Bj_complex.items():
            Nw += K[w, j] * np.real(np.conj(Bj))
        # Add j=0 contribution
        Nw += K[w, 0]  # B_0 = 1 for all s
        Nw /= p**(n-k)

        main = K[w, 0] / p**(n-k)
        delta = w / n

        max_Nw = np.max(Nw)

        # Exclude s=0
        Nw_excl = Nw.copy()
        Nw_excl[zero_syn] = main  # replace with main to exclude from max
        max_Nw_excl = np.max(Nw_excl)

        max_err = np.max(np.abs(Nw - main))
        Nw_excl2 = Nw.copy()
        Nw_excl2[zero_syn] = main
        max_err_excl = np.max(np.abs(Nw_excl2 - main))

        above_J = "***" if delta > delta_J and w > 0 else ""

        if max_Nw > 0.5 or w <= k+2:
            print(f"{w:3d} {delta:6.3f} {main:10.4f} {max_Nw:8.1f} {max_Nw_excl:8.1f} {max_err:10.4f} {max_err_excl:10.4f} {above_J:>8}")

    # Cumulative list size M(delta)
    print(f"\nCumulative list size M(delta) = max_s sum_{{w<=delta*n}} N_w(s):")
    print(f"{'delta':>6} {'w_max':>5} {'main_cum':>10} {'M':>6} {'M*':>6} {'above_J':>8}")

    for delta_pct in [20, 25, 29, 30, 33, 35, 40, 45, 50]:
        delta = delta_pct / 100.0
        w_max = int(delta * n)

        M_array = np.zeros(shape, dtype=np.float64)
        main_cum = 0
        for w in range(w_max + 1):
            Nw = np.zeros(shape, dtype=np.float64)
            for j, Bj in Bj_complex.items():
                Nw += K[w, j] * np.real(np.conj(Bj))
            Nw += K[w, 0]
            Nw /= p**(n-k)
            M_array += Nw
            main_cum += K[w, 0] / p**(n-k)

        M = np.max(M_array)

        M_excl = M_array.copy()
        M_excl[zero_syn] = main_cum
        M_star = np.max(M_excl)

        above_J = "***" if delta > delta_J else ""
        print(f"{delta:6.2f} {w_max:5d} {main_cum:10.4f} {M:6.1f} {M_star:6.1f} {above_J:>8}")

    print(f"\nTime: {time.time()-t0:.2f}s")
    return Bj_complex, weight_dist

# ================================================================
# RUN CASES
# ================================================================

# Case 1: n=6, k=3, p=7
deep_analysis(6, 3, 7)

print("\n" + "="*70 + "\n")

# Case 2: n=8, k=4, p=17
deep_analysis(8, 4, 17)

print("\n" + "="*70 + "\n")

# Case 3: n=6, k=3, p=13
deep_analysis(6, 3, 13)

# Case 4: Scaling study - fixed n=6, k=3, varying p
print("\n" + "="*70)
print("SCALING: n=6, k=3, second-largest |B_j| vs p")
print("="*70)
print(f"{'p':>5} {'j':>3} {'A_j':>8} {'sqrt':>8} {'max*':>10} {'ratio*':>8}")

for p_val in [7, 13, 19, 31, 37, 43, 61, 67, 73, 79, 97]:
    if (p_val - 1) % 6 != 0:
        continue

    omega = find_omega(6, p_val)
    L = [pow(omega, i, p_val) for i in range(6)]
    d = 3
    total = p_val ** d

    L_powers = np.zeros((6, d), dtype=np.int64)
    for i in range(6):
        L_powers[i, 0] = 1
        for r in range(1, d):
            L_powers[i, r] = L_powers[i, r-1] * L[i] % p_val

    indices = np.arange(total)
    u_matrix = np.zeros((total, d), dtype=np.int64)
    for dim in range(d):
        u_matrix[:, dim] = (indices // (p_val ** dim)) % p_val

    eval_matrix = u_matrix @ L_powers.T % p_val
    weights = np.count_nonzero(eval_matrix, axis=1)

    shape = tuple([p_val] * d)
    wt_array = np.zeros(shape, dtype=np.int32)
    for idx in range(total):
        wt_array[tuple(u_matrix[idx])] = weights[idx]

    weight_dist = Counter(weights.tolist())

    for j in [4, 5, 6]:
        if weight_dist.get(j, 0) == 0:
            continue
        Aj = weight_dist[j]
        indicator = (wt_array == j).astype(np.complex128)
        fft_result = np.fft.fftn(indicator)
        Bj_abs = np.abs(fft_result)
        flat = np.sort(Bj_abs.flatten())[::-1]
        max_excl = flat[1]
        rms = np.sqrt(Aj)
        ratio = max_excl / rms
        print(f"{p_val:5d} {j:3d} {Aj:8d} {rms:8.2f} {max_excl:10.4f} {ratio:8.4f}")
