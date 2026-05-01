"""
fiber_rs_compatible.py — Test fiber bound using ACTUAL RS-compatible flats.

The key question: does the KST bound C(n,d)/C(w,d) hold for RS-compatible
flats (with Toeplitz structure), even when it fails for random flats?

For an RS center c with syndrome (c_k,...,c_{n-1}), the compatible
σ-values form a codim-c affine subspace V_c ⊂ F_p^w defined by:
  Σ_j (-1)^j σ_j c_{m-w+j} = -c_m  for m = k+w, ..., n-1  (c conditions)

The coefficient matrix has Toeplitz-like structure.
"""

import itertools
from collections import Counter
from math import comb
import random

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p-1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p-1:
            return g
    return None

def elem_sym(B, p):
    w = len(B)
    e = [0] * (w + 1)
    e[0] = 1
    for b in B:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * b) % p
    return tuple(e[1:])

def rs_center_to_syndrome(center_coeffs, L, p):
    """Evaluate polynomial with coeffs center_coeffs at each T ∈ L.
    center_coeffs = [a_0, a_1, ..., a_{n-1}] in the DFT basis.
    Actually, center is a function c: L → F_p, given as a list of values.
    """
    # Just return the values directly
    return center_coeffs

def poly_eval(coeffs, x, p):
    """Evaluate polynomial a_0 + a_1 x + ... + a_d x^d at x mod p."""
    result = 0
    power = 1
    for a in coeffs:
        result = (result + a * power) % p
        power = (power * x) % p
    return result

def test_rs_compatible(n, p, w, c):
    """Test fiber bound using actual RS-compatible flats.

    An RS center c(x) is a polynomial of degree < n evaluated on L.
    The syndrome is (c_k, ..., c_{n-1}) where c_j = Σ_{i=0}^{n-1} c(ω^i) ω^{-ij}.

    Actually, simpler: just enumerate ALL centers and compute M.
    But this is too expensive. Instead, sample random centers.
    """
    d = w - c
    k = n - w - c
    if k < 1 or d < 2:
        return None

    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]
    omega_inv = pow(omega, p-2, p)

    # All w-subsets and σ-images
    subsets = list(itertools.combinations(range(n), w))
    sigma_images = []
    for B_idx in subsets:
        B = tuple(L[i] for i in B_idx)
        sigma_images.append(elem_sym(B, p))
    N = len(sigma_images)

    # DFT: compute center values → syndrome coefficients
    # c_j = (1/n) Σ_i c(ω^i) ω^{-ij} (DFT)
    n_inv = pow(n, p-2, p)

    # The compatibility condition for a center c = (c(ω^0), ..., c(ω^{n-1})):
    # A w-subset B = {i_1,...,i_w} (indices) with σ = elem_sym(L[i_1],...,L[i_w])
    # is compatible if f(ω^j) = c(ω^j) for j ∉ B, where f = the closest codeword.
    #
    # More directly: σ lies on the affine subspace V defined by
    # Σ_{j=0}^{w} (-1)^j σ_j hat_c_{m-w+j} = 0  for m = k+w,...,n-1
    # where hat_c are the DFT coefficients of c.
    #
    # Simpler approach: for each center c, check which σ-images are compatible.
    # A σ-image σ(B) is compatible with center c if there exists f ∈ RS_k with
    # f(ω^j) = c(ω^j) for j ∉ B.
    #
    # This means: the polynomial f-c vanishes at positions {0,...,n-1}\B (n-w positions).
    # Since deg(f-c) < n (and f has deg < k), we need f(ω^j) = c(ω^j) for j ∉ B.
    #
    # Equivalently: the syndrome conditions are satisfied.

    # For each B = {i_1,...,i_w}, the syndrome of c with error set B is:
    # hat{e}_m = hat{c}_m for m = k,...,n-1 where e is the error pattern.
    # And e has support B with values c(ω^j) - f(ω^j) for j ∈ B.

    # The compatibility condition is LINEAR in σ:
    # The matrix A (c × w) with entries A[r][j] = (-1)^{j+1} c_{k+r+j+1}
    # multiplied by σ gives the RHS.
    # (This is the Toeplitz matrix from Note 0070.)

    # Let me just use the direct approach: for each center c and each subset B,
    # check if there exists an RS codeword f of degree < k agreeing with c outside B.

    print(f"\nn={n}, p={p}, w={w}, c={c}, d={d}, k={k}")
    print(f"  N = C({n},{w}) = {N}")
    print(f"  KST bound = C(n,{d})/C(w,{d}) = {comb(n,d)}/{comb(w,d)} = {comb(n,d)/comb(w,d):.1f}")

    random.seed(42)
    max_M_all = 0
    max_M_nonpinned = 0

    M_rs_nonpinned = []

    num_centers = min(2000, p**k)

    for trial in range(num_centers):
        # Random center: polynomial of degree < n (actually, any function L → F_p)
        # For a proper test, the center should be an ARBITRARY function, not just a polynomial.
        center_vals = [random.randint(0, p-1) for _ in range(n)]

        # For each w-subset B, check compatibility:
        # Is there f ∈ RS_k (degree < k polynomial) with f(ω^j) = center_vals[j] for j ∉ B?
        #
        # The positions outside B: {0,...,n-1} \ B, which has n-w = k+c points.
        # We need f to interpolate center at n-w points. f has k unknowns (coeffs).
        # Since n-w = k+c > k: the system is overdetermined.
        # It has a solution iff the (k+c)×k matrix has a certain rank condition.

        # Efficient: compute the syndrome of center.
        # DFT: hat_c_m = Σ_j c(ω^j) ω^{-mj}
        hat_c = [0] * n
        for m in range(n):
            for j in range(n):
                hat_c[m] = (hat_c[m] + center_vals[j] * pow(omega_inv, m*j, p)) % p

        # The syndrome is (hat_c_k, hat_c_{k+1}, ..., hat_c_{n-1}).
        # Compatible σ's satisfy: Σ_j (-1)^j σ_j * hat_c_{m+j} = hat_c_m for m = k,...,k+c-1
        # Wait, I need to be more careful about the exact linear system.

        # Direct approach: for each w-subset, check compatibility.
        compatible = []
        for idx, B_idx in enumerate(subsets):
            B_set = set(B_idx)
            outside = [j for j in range(n) if j not in B_set]

            # Interpolation check: is there a poly f of deg < k passing through
            # (ω^j, center_vals[j]) for j ∈ outside?
            # We have |outside| = n-w = k+c points, and deg(f) < k, so k coefficients.
            # Build the Vandermonde system.

            # V_{ij} = (ω^{outside[i]})^j for i=0,...,k+c-1, j=0,...,k-1
            # y_i = center_vals[outside[i]]
            # Solve V f_coeffs = y (overdetermined, k+c × k)

            # Use Gaussian elimination on the augmented matrix
            rows = k + c
            cols = k
            mat = [[0]*(cols+1) for _ in range(rows)]
            for i in range(rows):
                x_val = L[outside[i]]
                power = 1
                for j in range(cols):
                    mat[i][j] = power
                    power = (power * x_val) % p
                mat[i][cols] = center_vals[outside[i]]

            # Row reduce
            pivot_row = 0
            for col in range(cols):
                # Find pivot
                found = False
                for row in range(pivot_row, rows):
                    if mat[row][col] != 0:
                        mat[pivot_row], mat[row] = mat[row], mat[pivot_row]
                        found = True
                        break
                if not found:
                    continue
                inv = pow(mat[pivot_row][col], p-2, p)
                for j in range(cols+1):
                    mat[pivot_row][j] = (mat[pivot_row][j] * inv) % p
                for row in range(rows):
                    if row != pivot_row and mat[row][col] != 0:
                        factor = mat[row][col]
                        for j in range(cols+1):
                            mat[row][j] = (mat[row][j] - factor * mat[pivot_row][j]) % p
                pivot_row += 1

            # Check consistency: rows from pivot_row onwards should have RHS = 0
            is_compatible = True
            for row in range(min(pivot_row, cols), rows):
                if mat[row][cols] != 0:
                    is_compatible = False
                    break

            if is_compatible:
                compatible.append(B_idx)

        M = len(compatible)
        if M == 0:
            continue

        # Check pinned
        if M == 1:
            M_rs_nonpinned.append(M)
            max_M_nonpinned = max(max_M_nonpinned, M)
            continue

        common = set(compatible[0])
        for B in compatible[1:]:
            common &= set(B)
        is_pinned = len(common) > 0

        if is_pinned:
            max_M_all = max(max_M_all, M)
        else:
            M_rs_nonpinned.append(M)
            max_M_nonpinned = max(max_M_nonpinned, M)

    print(f"  Tested {num_centers} random RS centers:")
    print(f"    max M (pinned)      = {max_M_all}")
    print(f"    max M (non-pinned)  = {max_M_nonpinned}")
    print(f"    KST bound           = {comb(n,d)/comb(w,d):.1f}")

    if M_rs_nonpinned:
        np_counter = Counter(M_rs_nonpinned)
        top5 = sorted(np_counter.items(), key=lambda x: -x[0])[:5]
        print(f"    Non-pinned M dist:  {top5}")

    return max_M_nonpinned, comb(n,d)/comb(w,d)


# Test the problematic case first
print("=" * 70)
print("RS-COMPATIBLE FLATS: does Toeplitz structure enforce KST bound?")
print("=" * 70)

results = []
for n, p, w in [(10, 11, 4), (10, 13, 4), (10, 31, 4),
                (12, 13, 4), (12, 13, 5),
                (14, 17, 5), (14, 29, 5)]:
    c = w - 2
    if p > n and n - w - c >= 1:
        r = test_rs_compatible(n, p, w, c)
        if r:
            results.append((n, p, w, c, r[0], r[1]))

print("\n" + "=" * 70)
print("SUMMARY: RS-compatible flats")
print("=" * 70)
print(f"{'n':>3} {'p':>3} {'w':>3} {'c':>3} {'d':>3} {'maxM':>6} {'KST':>8} {'OK?':>5}")
for n, p, w, c, maxM, bound in results:
    ok = "YES" if maxM <= bound + 0.5 else "NO"
    print(f"{n:>3} {p:>3} {w:>3} {c:>3} {w-c:>3} {maxM:>6} {bound:>8.1f} {ok:>5}")
