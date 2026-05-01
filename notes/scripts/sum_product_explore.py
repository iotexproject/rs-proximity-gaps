#!/usr/bin/env python3
"""
Direction D — Sum-Product Structure of σ-image

The CORE QUESTION: given the σ-image S = {(σ_1(B),...,σ_w(B)) : B ∈ C(n,w)} ⊂ F_p^w,
prove that |S ∩ V| ≤ O(1) for any codimension-c affine subspace V.

KEY INSIGHT: σ_1 = SUM, σ_w = PRODUCT of elements of B.
The joint (σ_1, σ_w) image combines ADDITIVE and MULTIPLICATIVE structure.

Sum-product theory (Bourgain-Katz-Tao): for A ⊂ F_p, max(|A+A|, |A·A|) ≥ c·|A|^{1+ε}.
This prevents A from being concentrated in both additive and multiplicative substructures.

For our problem: the σ-image combines σ_1 (additive) and σ_w (multiplicative).
An affine subspace V imposes LINEAR conditions on the σ_j's.
If V constrains σ_1 to a small set AND σ_w to a related small set,
sum-product prevents too many B's from satisfying both.

Experiments:
A. Analyze σ_1 and σ_w distributions (projections of σ-image)
B. Conditional distribution: σ_w | σ_1 = v (fiber structure)
C. Additive energy of σ-image (measure of additive structure)
D. Multiplicative energy (measure of multiplicative structure)
E. Sum-product type estimate on σ-fibers
F. Projection to (σ_1, σ_w) only — what do the codimension-c intersections look like?
"""

import itertools, math
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


def full_sigma_image(n, p):
    """Compute the full σ-image of C(n,w) and analyze its structure."""
    k = n // 2
    w = johnson_w(n, k)
    c = n - k - w  # number of conditions

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    N = math.comb(n, w)
    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] over F_{p}, w={w}, c={c}")
    print(f"N=C({n},{w})={N}, p^c={p**c}, N/p^c={N/p**c:.3f}")
    print(f"{'='*70}")

    # Compute σ-image for ALL w-subsets
    sigma_images = []
    sigma_1_dist = defaultdict(int)
    sigma_w_dist = defaultdict(int)
    sigma_1w_dist = defaultdict(int)  # joint (σ_1, σ_w)

    for B in itertools.combinations(range(n), w):
        vals = [L[i] for i in B]
        sigma = elem_sym(vals, p)
        sigma_images.append(sigma)
        sigma_1_dist[sigma[0]] += 1
        sigma_w_dist[sigma[w-1]] += 1
        sigma_1w_dist[(sigma[0], sigma[w-1])] += 1

    # A. Distribution analysis
    print(f"\n  A. Distribution of σ_1 (sum of elements):")
    s1_values = sorted(sigma_1_dist.keys())
    max_s1 = max(sigma_1_dist.values())
    min_s1 = min(sigma_1_dist.values())
    print(f"    #distinct values: {len(s1_values)}/{p}")
    print(f"    max count: {max_s1}, min count: {min_s1}, avg: {N/p:.1f}")
    print(f"    ratio max/avg: {max_s1*p/N:.2f}")

    print(f"\n  A'. Distribution of σ_{w} (product of elements):")
    sw_values = sorted(sigma_w_dist.keys())
    max_sw = max(sigma_w_dist.values())
    min_sw = min(sigma_w_dist.values())
    print(f"    #distinct values: {len(sw_values)}/{p}")
    print(f"    max count: {max_sw}, min count: {min_sw}, avg: {N/p:.1f}")
    print(f"    ratio max/avg: {max_sw*p/N:.2f}")

    # B. Conditional σ_w | σ_1
    print(f"\n  B. Conditional σ_w given σ_1:")
    sigma_1_fibers = defaultdict(list)  # σ_1 → list of σ_w values
    for sigma in sigma_images:
        sigma_1_fibers[sigma[0]].append(sigma[w-1])

    max_fiber_size = 0
    for v, fiber in sigma_1_fibers.items():
        counts = defaultdict(int)
        for x in fiber:
            counts[x] += 1
        max_count = max(counts.values())
        if max_count > max_fiber_size:
            max_fiber_size = max_count
            max_fiber_v = v

    print(f"    Max fiber multiplicity (max_v |{{B: σ_1=v, σ_w=u}}|): {max_fiber_size} at σ_1={max_fiber_v}")
    print(f"    Expected (N/p^2): {N/p**2:.2f}")

    # Joint (σ_1, σ_w) distribution
    print(f"\n  B'. Joint (σ_1, σ_w) distribution:")
    max_joint = max(sigma_1w_dist.values())
    num_joint = len(sigma_1w_dist)
    print(f"    #distinct pairs: {num_joint}/{p**2}")
    print(f"    max joint count: {max_joint}")
    print(f"    Expected (N/p^2): {N/p**2:.2f}")
    print(f"    ratio max/expected: {max_joint*p**2/N:.2f}")

    # C. Additive energy of σ_1 image
    print(f"\n  C. Additive energy of σ_1 projection:")
    # E+(A) = |{(a,b,c,d) ∈ A^4 : a+b=c+d}|
    # = Σ_s |{(a,b): a+b=s}|^2
    sum_counts = defaultdict(int)
    s1_multiset = [s[0] for s in sigma_images]
    for i in range(len(s1_multiset)):
        for j in range(i, len(s1_multiset)):
            s = (s1_multiset[i] + s1_multiset[j]) % p
            sum_counts[s] += 1 if i == j else 2

    additive_energy = sum(c**2 for c in sum_counts.values())
    # For random set: E+ ≈ N^3/p
    print(f"    E+(σ_1) = {additive_energy}")
    print(f"    Random baseline N^3/p: {N**3/p:.0f}")
    print(f"    Ratio: {additive_energy*p/N**3:.2f}")

    # D. Multiplicative energy of σ_w image
    print(f"\n  D. Multiplicative energy of σ_w projection:")
    prod_counts = defaultdict(int)
    sw_multiset = [s[w-1] for s in sigma_images]
    for i in range(len(sw_multiset)):
        if sw_multiset[i] == 0:
            continue
        for j in range(i, len(sw_multiset)):
            if sw_multiset[j] == 0:
                continue
            # a*b mod p
            prod = sw_multiset[i] * sw_multiset[j] % p
            prod_counts[prod] += 1 if i == j else 2

    mult_energy = sum(c**2 for c in prod_counts.values())
    Nstar = sum(1 for s in sw_multiset if s != 0)  # exclude zeros
    print(f"    E×(σ_w) = {mult_energy} (excluding σ_w=0 entries)")
    print(f"    Random baseline N*^3/p: {Nstar**3/p:.0f}")
    print(f"    Ratio: {mult_energy*p/max(1,Nstar**3):.2f}")

    # E. Sum-product on σ_1-fibers
    print(f"\n  E. Sum-product analysis of σ_1-fibers:")
    for v in sorted(sigma_1_fibers.keys())[:5]:
        fiber = sigma_1_fibers[v]
        if len(fiber) < 3:
            continue
        fiber_set = set(fiber)
        # Sumset
        sumset = set()
        for a in fiber_set:
            for b in fiber_set:
                sumset.add((a + b) % p)
        # Product set
        prodset = set()
        for a in fiber_set:
            for b in fiber_set:
                prodset.add(a * b % p)

        print(f"    σ_1={v}: |fiber|={len(fiber)}, |fiber_set|={len(fiber_set)}, "
              f"|A+A|={len(sumset)}, |A·A|={len(prodset)}")

    # F. Codimension-c intersections: for each center (syndrome),
    # count how many B satisfy ALL c conditions
    print(f"\n  F. Codimension-c affine subspace intersections:")
    print(f"    (This is M_actual for various centers)")

    # For a random center: the c conditions are D_m(σ(B)) = t_m for m = k,...,n-w-1
    # Each condition is linear in σ_1,...,σ_w

    # Compute compatibility conditions explicitly
    # From the translation theorem: the conditions are that
    # Σ_j σ_j(B) · c_{m-j} = 0 for certain m
    # where c_j are DFT coefficients of center

    # For simplicity, let's just count MAX_M by trying random subspaces
    import random
    random.seed(42)

    # A codimension-c affine subspace in F_p^w:
    # defined by c linear equations: Σ_j a_{m,j} σ_j = b_m for m=1,...,c

    max_M_random = 0
    M_histogram = defaultdict(int)

    for trial in range(min(5000, p**c)):
        # Random codimension-c subspace (c random linear constraints)
        A_mat = [[random.randint(0, p-1) for _ in range(w)] for _ in range(c)]
        b_vec = [random.randint(0, p-1) for _ in range(c)]

        count = 0
        for sigma in sigma_images:
            # Check all c conditions
            ok = True
            for m in range(c):
                val = sum(A_mat[m][j] * sigma[j] for j in range(w)) % p
                if val != b_vec[m]:
                    ok = False
                    break
            if ok:
                count += 1

        M_histogram[count] += 1
        if count > max_M_random:
            max_M_random = count

    print(f"    Tested {sum(M_histogram.values())} random codim-{c} subspaces")
    print(f"    Max M over random subspaces: {max_M_random}")
    print(f"    Expected M = N/p^c = {N/p**c:.2f}")
    print(f"    M distribution: {dict(sorted(M_histogram.items()))}")

    # G. NOW TEST STRUCTURED subspaces (from actual RS conditions)
    print(f"\n  G. Structured subspaces (RS compatibility):")
    # The RS conditions for a center with given high coefficients
    # Condition: Σ_j c_{high,m-j} · σ_j(B) = some value
    # For simplicity, just enumerate over random P_c high parts

    max_M_structured = 0
    M_hist_struct = defaultdict(int)

    for trial in range(min(1000, p**c)):
        # Random high coefficients c_k, ..., c_{n-1}
        c_high = [random.randint(0, p-1) for _ in range(n - k)]

        # Build the compatibility matrix
        # The conditions involve σ and the high coefficients
        # From the key relation: for B compatible with c_high,
        # the syndrome at position m (for m=k,...,n-w-1) must be zero.
        #
        # σ_j(B) · c_{m-j} summed appropriately...
        #
        # Actually, let me use the EVALUATION approach:
        # A B is compatible if the interpolation from [n]\B gives a codeword
        # matching c at ALL of [n]\B.
        # For B of size w and [n]\B of size n-w ≥ k:
        # interpolate f from k points of [n]\B,
        # then check remaining n-w-k = c points.

        count = 0
        for B_idx, B in enumerate(itertools.combinations(range(n), w)):
            A = [i for i in range(n) if i not in B]
            # Use first k positions to interpolate
            xs = [L[i] for i in A[:k]]
            ys_B = []  # center values at these positions
            # Center on L: for position i, c_val = Σ_{j=0}^{n-1} P_c_coeff[j] · L[i]^j
            # But we need P_c from the high coefficients...
            # This is getting complicated. Let me use a simpler approach.
            pass

        # Simpler: just use the σ-conditions directly
        # The ACTUAL compatibility conditions from RS structure are:
        # For m in syndrome window:
        #   (-1)^w · σ_w(B) · coefficient_extraction(c, m, B) = 0
        # This depends on the specific RS structure.

        # Actually, the simplest is: c_high determines a codim-c affine subspace
        # in σ-space. The matrix A and vector b depend on c_high in a SPECIFIC way.

        # Let me just directly compute M for a random center.
        center = [random.randint(0, p-1) for _ in range(n)]
        count = 0
        for B in itertools.combinations(range(n), w):
            A = [i for i in range(n) if i not in B]
            # Interpolate on first k points of A
            xs = [L[j] for j in A[:k]]
            ys = [center[j] for j in A[:k]]

            # Lagrange interpolation (simplified for speed)
            f_vals_on_A = list(ys)  # first k are given
            # Compute f(x) for remaining A positions
            # Need interpolation coefficients
            coeffs = [0] * k
            for i in range(k):
                basis_val = 1
                for j in range(k):
                    if j == i: continue
                    basis_val = basis_val * pow(xs[i] - xs[j], p-2, p) % p
                basis_val = ys[i] * basis_val % p
                # Build coefficient contribution
                prod = [basis_val]
                for j in range(k):
                    if j == i: continue
                    new_prod = [0] * (len(prod) + 1)
                    for l, c_val in enumerate(prod):
                        new_prod[l + 1] = (new_prod[l + 1] + c_val) % p
                        new_prod[l] = (new_prod[l] - c_val * xs[j]) % p
                    prod = new_prod
                for l in range(k):
                    coeffs[l] = (coeffs[l] + prod[l]) % p

            # Check remaining positions in A
            ok = True
            for j_idx in range(k, len(A)):
                j = A[j_idx]
                fval = poly_eval(coeffs, L[j], p)
                if fval != center[j]:
                    ok = False
                    break
            if ok:
                count += 1

        M_hist_struct[count] += 1
        if count > max_M_structured:
            max_M_structured = count

        if trial < 5 or count > 0:
            pass  # don't print individual

    print(f"    Tested {sum(M_hist_struct.values())} random centers")
    print(f"    Max M_actual: {max_M_structured}")
    print(f"    M distribution: {dict(sorted(M_hist_struct.items()))}")

    return sigma_images, sigma_1_dist, sigma_w_dist


if __name__ == "__main__":
    for n, p in [(6, 7), (8, 17), (10, 11)]:
        full_sigma_image(n, p)
