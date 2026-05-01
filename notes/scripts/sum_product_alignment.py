#!/usr/bin/env python3
"""
Direction D — Round 2: RS vs Random subspace alignment test

KEY QUESTION: Are the RS compatibility conditions "generic" affine subspaces,
or do they have special alignment with the σ-image?

If generic → proof reduces to σ-image equidistribution (standard technique might work)
If aligned → need structure-specific proof

Test: compare M distribution for RS conditions vs random codim-c subspaces,
specifically at the TAIL (max M).

Also: the σ_w DEGENERACY (only (p-1)/gcd(w,n) distinct values) is key.
Explore whether RS conditions are orthogonal to this degeneracy.
"""

import itertools, math, random
from collections import defaultdict

def find_primitive_root(p):
    for g in range(2, p):
        seen = set(); val = 1
        for _ in range(p - 1):
            seen.add(val); val = val * g % p
        if len(seen) == p - 1: return g

def find_omega(g, p, n):
    return pow(g, (p - 1) // n, p)

def poly_eval(coeffs, x, p):
    val = 0; xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p; xpow = xpow * x % p
    return val

def johnson_w(n, k):
    return int(math.floor(n - math.sqrt(n * (k - 1))))

def elem_sym(values, p):
    w = len(values); sigma = [0] * (w + 1); sigma[0] = 1
    for v in values:
        for j in range(w, 0, -1):
            sigma[j] = (sigma[j] + sigma[j-1] * v) % p
    return sigma[1:]

def lagrange_interp(xs, ys, p):
    n = len(xs); result = [0] * n
    for i in range(n):
        basis = [1]; denom = 1
        for j in range(n):
            if j == i: continue
            new_basis = [0] * (len(basis) + 1)
            for k_idx, c in enumerate(basis):
                new_basis[k_idx + 1] = (new_basis[k_idx + 1] + c) % p
                new_basis[k_idx] = (new_basis[k_idx] - c * xs[j]) % p
            basis = new_basis; denom = denom * (xs[i] - xs[j]) % p
        denom_inv = pow(denom, p - 2, p)
        for k_idx in range(len(basis)):
            result[k_idx] = (result[k_idx] + ys[i] * denom_inv * basis[k_idx]) % p
    while len(result) > 1 and result[-1] == 0: result.pop()
    return result


def alignment_test(n, p):
    """Compare RS conditions vs random subspaces for M distribution."""
    k = n // 2
    w = johnson_w(n, k)
    c = n - k - w

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    N = math.comb(n, w)
    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] over F_{p}, w={w}, c={c}, N={N}, N/p^c={N/p**c:.3f}")
    print(f"{'='*70}")

    # Precompute ALL σ-images
    all_B = list(itertools.combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        vals = [L[i] for i in B]
        all_sigma.append(elem_sym(vals, p))

    # =====================================================
    # TEST 1: RS structured conditions
    # =====================================================
    # For each center c (random vector on L), compute M_actual
    random.seed(42)
    num_trials = min(2000, p**min(c+1, 4))

    rs_M_values = []
    for _ in range(num_trials):
        center = [random.randint(0, p-1) for _ in range(n)]
        count = 0
        for B_idx, B in enumerate(all_B):
            A = [i for i in range(n) if i not in B]
            xs = [L[j] for j in A[:k]]
            ys = [center[j] for j in A[:k]]

            # Fast interpolation check: compute f at remaining A positions
            coeffs = [0] * k
            for i_idx in range(k):
                num = ys[i_idx]
                for j_idx in range(k):
                    if j_idx == i_idx: continue
                    num = num * pow(xs[i_idx] - xs[j_idx], p-2, p) % p
                xprod = [num]
                for j_idx in range(k):
                    if j_idx == i_idx: continue
                    new_xprod = [0] * (len(xprod) + 1)
                    for l, cv in enumerate(xprod):
                        new_xprod[l + 1] = (new_xprod[l + 1] + cv) % p
                        new_xprod[l] = (new_xprod[l] - cv * xs[j_idx]) % p
                    xprod = new_xprod
                for l in range(k):
                    coeffs[l] = (coeffs[l] + xprod[l]) % p

            ok = True
            for j_idx in range(k, len(A)):
                j = A[j_idx]
                fval = poly_eval(coeffs, L[j], p)
                if fval != center[j]:
                    ok = False
                    break
            if ok:
                count += 1
        rs_M_values.append(count)

    rs_hist = defaultdict(int)
    for m in rs_M_values:
        rs_hist[m] += 1

    print(f"\n  RS structured conditions ({num_trials} random centers):")
    print(f"    M distribution: {dict(sorted(rs_hist.items()))}")
    print(f"    Max M_alg: {max(rs_M_values)}")
    print(f"    Mean M_alg: {sum(rs_M_values)/len(rs_M_values):.2f}")

    # Now compute M_actual (distinct codewords)
    rs_M_actual = []
    for _ in range(min(500, num_trials)):
        center = [random.randint(0, p-1) for _ in range(n)]
        f_set = set()
        for B in all_B:
            A = [i for i in range(n) if i not in B]
            xs = [L[j] for j in A[:k]]
            ys = [center[j] for j in A[:k]]
            coeffs = [0] * k
            for i_idx in range(k):
                num = ys[i_idx]
                for j_idx in range(k):
                    if j_idx == i_idx: continue
                    num = num * pow(xs[i_idx] - xs[j_idx], p-2, p) % p
                xprod = [num]
                for j_idx in range(k):
                    if j_idx == i_idx: continue
                    new_xprod = [0] * (len(xprod) + 1)
                    for l, cv in enumerate(xprod):
                        new_xprod[l + 1] = (new_xprod[l + 1] + cv) % p
                        new_xprod[l] = (new_xprod[l] - cv * xs[j_idx]) % p
                    xprod = new_xprod
                for l in range(k):
                    coeffs[l] = (coeffs[l] + xprod[l]) % p

            ok = True
            for j_idx in range(k, len(A)):
                j = A[j_idx]
                fval = poly_eval(coeffs, L[j], p)
                if fval != center[j]:
                    ok = False
                    break
            if ok:
                f_set.add(tuple(coeffs))
        rs_M_actual.append(len(f_set))

    actual_hist = defaultdict(int)
    for m in rs_M_actual:
        actual_hist[m] += 1
    print(f"\n  M_actual ({len(rs_M_actual)} trials):")
    print(f"    Distribution: {dict(sorted(actual_hist.items()))}")
    print(f"    Max M_actual: {max(rs_M_actual)}")

    # =====================================================
    # TEST 2: Random codim-c subspaces
    # =====================================================
    rand_M_values = []
    for _ in range(num_trials):
        # Random c × w matrix A and c × 1 vector b
        A_mat = [[random.randint(0, p-1) for _ in range(w)] for _ in range(c)]
        b_vec = [random.randint(0, p-1) for _ in range(c)]
        count = 0
        for sigma in all_sigma:
            ok = True
            for m in range(c):
                val = sum(A_mat[m][j] * sigma[j] for j in range(w)) % p
                if val != b_vec[m]:
                    ok = False
                    break
            if ok:
                count += 1
        rand_M_values.append(count)

    rand_hist = defaultdict(int)
    for m in rand_M_values:
        rand_hist[m] += 1

    print(f"\n  Random codim-{c} subspaces ({num_trials} trials):")
    print(f"    M distribution: {dict(sorted(rand_hist.items()))}")
    print(f"    Max M: {max(rand_M_values)}")
    print(f"    Mean M: {sum(rand_M_values)/len(rand_M_values):.2f}")

    # =====================================================
    # TEST 3: σ_w-aligned subspaces (worst case?)
    # =====================================================
    print(f"\n  σ_w structure analysis:")
    # How many distinct σ_w values?
    sw_vals = set(s[w-1] for s in all_sigma)
    sw_counts = defaultdict(int)
    for s in all_sigma:
        sw_counts[s[w-1]] += 1
    print(f"    Distinct σ_w values: {len(sw_vals)}")
    for v in sorted(sw_counts.keys()):
        print(f"      σ_w={v}: {sw_counts[v]} subsets")

    # For codim-c subspace that fixes σ_w = v:
    # How many B satisfy the remaining c-1 conditions?
    if c >= 1:
        print(f"\n  Worst case when σ_w is fixed:")
        for v in sorted(sw_counts.keys()):
            if sw_counts[v] == 0:
                continue
            # Among B with σ_w = v, what's max intersection with codim-(c-1)?
            filtered = [s for s in all_sigma if s[w-1] == v]
            if c == 1:
                # Fixing σ_w IS the one condition → M = sw_counts[v]
                print(f"      σ_w={v}: M = {sw_counts[v]} (one condition used)")
            else:
                # Additional c-1 conditions on σ_1,...,σ_{w-1}
                max_M_given_sw = 0
                for _ in range(200):
                    A_mat = [[random.randint(0, p-1) for _ in range(w-1)] for _ in range(c-1)]
                    b_vec = [random.randint(0, p-1) for _ in range(c-1)]
                    count = 0
                    for sigma in filtered:
                        ok = True
                        for m in range(c-1):
                            val = sum(A_mat[m][j] * sigma[j] for j in range(w-1)) % p
                            if val != b_vec[m]:
                                ok = False
                                break
                        if ok:
                            count += 1
                    if count > max_M_given_sw:
                        max_M_given_sw = count
                print(f"      σ_w={v}: {sw_counts[v]} subsets, max M after {c-1} more conditions: {max_M_given_sw}")


if __name__ == "__main__":
    for n, p in [(6, 7), (8, 17), (10, 11)]:
        alignment_test(n, p)
