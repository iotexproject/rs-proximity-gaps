#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Step 2: What predicts large M_alg?

Key question from Step 1:
  - σ_w alignment gives LOWER max M (not higher!)
  - σ_1 alignment gives HUGE max M at n=12
  - Which structural property of the affine subspace predicts large M?

Experiments:
  E1. Systematic σ_j fiber analysis: which fibers are structured?
  E2. Full alignment sweep: zero out each PAIR of coordinates
  E3. Spectral analysis: eigenvalues of the "σ_j correlation matrix" on fibers
  E4. RS Toeplitz matrix vs dangerous subspaces: does Toeplitz avoid σ_1-alignment?
  E5. M_actual (not M_alg) for RS vs random — the real comparison
"""

import itertools
import random
from collections import Counter, defaultdict

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def find_omega(p, n):
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

def make_inv(p):
    inv = [0] * p
    for a in range(1, p):
        inv[a] = pow(a, p-2, p)
    return inv

def elem_sym(B, omega, p):
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * r) % p
    return e[1:]

def compute_all_sigma(n, w, p, omega):
    results = []
    for B in itertools.combinations(range(n), w):
        sig = elem_sym(B, omega, p)
        results.append((B, tuple(sig)))
    return results

def count_on_affine(all_sigma, A_mat, b_vec, p):
    """Count σ-images on affine subspace Ax = b."""
    count = 0
    for _, sig in all_sigma:
        ok = True
        for i in range(len(A_mat)):
            val = sum(A_mat[i][j] * sig[j] for j in range(len(sig))) % p
            if val != b_vec[i] % p:
                ok = False
                break
        if ok:
            count += 1
    return count

def rs_codewords_near(n, k, p, omega, c_eval, w):
    """Find all RS[n,k] codewords f with d(f, c) <= w. Returns (f_coeffs, distance)."""
    inv = make_inv(p)
    # Enumerate all degree < k polynomials (too many for large k,p)
    # Instead: for small p^k, enumerate directly
    if p**k > 500000:
        return None  # too large

    L = [pow(omega, i, p) for i in range(n)]
    results = []

    def eval_poly(coeffs, x, p):
        val = 0
        for c in reversed(coeffs):
            val = (val * x + c) % p
        return val

    # Enumerate f as coefficient vectors
    for idx in range(p**k):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        # Evaluate at L
        f_eval = tuple(eval_poly(coeffs, x, p) for x in L)
        d = sum(1 for i in range(n) if f_eval[i] != c_eval[i])
        if d <= w:
            results.append((tuple(coeffs), d))

    return results

def experiment_1_fiber_structure(n, w, p, omega, all_sigma):
    """E1: Analyze fibers of each σ_j projection."""
    print(f"\n=== E1: σ_j fiber structure ===")
    N = len(all_sigma)

    for j in range(w):
        # Group by σ_{j+1} value
        fibers = defaultdict(list)
        for B, sig in all_sigma:
            fibers[sig[j]].append(sig)

        sizes = [len(v) for v in fibers.values()]
        # For each fiber, check if the remaining coordinates are "aligned"
        # (e.g., lie on a low-dim subspace)
        max_collinear = 0
        for v, sigs in fibers.items():
            if len(sigs) < 3:
                continue
            # Project to remaining coordinates
            remaining = [tuple(s[i] for i in range(w) if i != j) for s in sigs]
            # Check collinearity (for w-1=2: all on a line)
            if w - 1 == 2:
                max_on_line = check_max_collinear_2d(remaining, p)
                max_collinear = max(max_collinear, max_on_line)
            elif w - 1 == 1:
                max_collinear = max(max_collinear, len(remaining))
            else:
                # For higher dim, check if they lie in a hyperplane
                pass

        print(f"  σ_{j+1}: {len(fibers)} distinct values, "
              f"fiber sizes {min(sizes)}-{max(sizes)} (avg {N/len(fibers):.1f}), "
              f"max collinear in remaining coords: {max_collinear}")

def check_max_collinear_2d(points, p):
    """Max number of points on a line in F_p^2."""
    if len(points) <= 2:
        return len(points)
    max_on_line = 2
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            # Line through points[i] and points[j]
            dx = (points[j][0] - points[i][0]) % p
            dy = (points[j][1] - points[i][1]) % p
            count = 2
            for k2 in range(j+1, len(points)):
                dx2 = (points[k2][0] - points[i][0]) % p
                dy2 = (points[k2][1] - points[i][1]) % p
                # Collinear iff dx*dy2 = dy*dx2 mod p
                if (dx * dy2 - dy * dx2) % p == 0:
                    count += 1
            max_on_line = max(max_on_line, count)
    return max_on_line

def experiment_2_pair_alignment(n, k, w, p, omega, all_sigma, n_trials=200):
    """E2: Zero out pairs of coordinates — which pairs give large M?"""
    conds = n - k - w
    print(f"\n=== E2: Pair alignment (zero out 2 coords in each condition) ===")

    if w < 3 or conds < 1:
        print("  SKIP: need w >= 3 and conds >= 1")
        return

    for j1 in range(w):
        for j2 in range(j1+1, w):
            M_vals = []
            for _ in range(n_trials):
                A = []
                for r in range(conds):
                    row = [random.randint(0, p-1) for _ in range(w)]
                    row[j1] = 0
                    row[j2] = 0
                    A.append(row)
                b = [random.randint(0, p-1) for _ in range(conds)]
                M = count_on_affine(all_sigma, A, b, p)
                M_vals.append(M)
            print(f"  σ_{j1+1},σ_{j2+1}=0: avg={sum(M_vals)/len(M_vals):.2f}, max={max(M_vals)}")

def experiment_4_toeplitz_vs_dangerous(n, k, w, p, omega, all_sigma, inv_table, n_trials=500):
    """E4: RS Toeplitz matrix — does it avoid σ_1-alignment?"""
    conds = n - k - w
    print(f"\n=== E4: RS Toeplitz structure analysis ===")

    # Analyze the coefficient matrix for random centers
    # A[r, j-1] = (-1)^j * c_{k+r+j} for j=1,...,w; r=0,...,conds-1
    # σ_1 coefficient: A[r, 0] = (-1)^1 * c_{k+r+1} = -c_{k+r+1}
    # σ_w coefficient: A[r, w-1] = (-1)^w * c_{k+r+w}

    # For σ_1 coeff to be 0 in ALL rows: c_{k+1} = c_{k+2} = ... = c_{k+conds} = 0
    # For σ_w coeff to be 0 in ALL rows: c_{k+w} = c_{k+w+1} = ... = c_{k+w+conds-1} = 0

    print(f"  Syndrome range: c_{k} to c_{n-1} ({n-k} coefficients)")
    print(f"  σ_1 coefficients from: c_{k+1} to c_{k+conds}")
    print(f"  σ_w coefficients from: c_{k+w} to c_{k+w+conds-1} = c_{n-1}")
    print(f"  σ_1-alignment: need c_{k+1}=...=c_{k+conds}=0 ({conds} of {n-k} syndrome)")
    print(f"  σ_w-alignment: need c_{k+w}=...=c_{n-1}=0 ({conds} of {n-k} syndrome)")

    # Key question: is σ_1 alignment "more dangerous" than σ_w alignment?
    # And does the Toeplitz structure correlate these?

    # Test: for RS centers, what's the CORRELATION between σ_1 and σ_w coefficients?
    print(f"\n  Toeplitz constraint: A[r,j-1] = (-1)^j c_{{k+r+j}}")
    print(f"  So A[r,0] = -c_{{k+r+1}} and A[r,{w-1}] = (-1)^{w} c_{{k+r+{w}}}")
    print(f"  These involve DIFFERENT c's: σ_1 uses c_{k+1}..c_{k+conds}, σ_w uses c_{k+w}..c_{n-1}")

    if w > conds:
        print(f"\n  ** w ({w}) > conds ({conds}): σ_1 and σ_w use DISJOINT c coefficients!")
        print(f"  So zeroing σ_1 doesn't affect σ_w and vice versa.")
        print(f"  The Toeplitz structure does NOT couple σ_1 and σ_w for this case.")
    else:
        overlap_start = k + w
        overlap_end = k + conds
        print(f"\n  Overlap: c_{overlap_start}..c_{overlap_end} affect BOTH σ_1 and σ_w")
        print(f"  But through different rows. The Toeplitz shift couples them.")

    # Actually run the comparison
    print(f"\n  Empirical RS M distribution:")
    rs_M = []
    rs_M_actual = []

    # For M_actual, we need to find actual codewords
    L = [pow(omega, i, p) for i in range(n)]

    for trial in range(n_trials):
        c_coeffs = [random.randint(0, p-1) for _ in range(n)]
        A, b = rs_coefficient_matrix(n, k, w, c_coeffs, p)
        M_alg = count_on_affine(all_sigma, A, b, p)
        rs_M.append(M_alg)

    ctr = Counter(rs_M)
    print(f"    M_alg: avg={sum(rs_M)/len(rs_M):.2f}, max={max(rs_M)}, dist={ctr.most_common(8)}")

    # Now try σ_1-aligned centers (c_{k+1}=...=c_{k+conds}=0)
    print(f"\n  σ_1-aligned RS centers (c_{k+1}=...=c_{k+conds}=0):")
    aligned_M = []
    for trial in range(n_trials):
        c_coeffs = [random.randint(0, p-1) for _ in range(n)]
        for r in range(conds):
            c_coeffs[k + 1 + r] = 0  # Zero out σ_1 coefficients
        A, b = rs_coefficient_matrix(n, k, w, c_coeffs, p)
        M_alg = count_on_affine(all_sigma, A, b, p)
        aligned_M.append(M_alg)

    ctr = Counter(aligned_M)
    print(f"    M_alg: avg={sum(aligned_M)/len(aligned_M):.2f}, max={max(aligned_M)}, dist={ctr.most_common(8)}")

    return rs_M, aligned_M

def experiment_5_Mactual(n, k, w, p, omega, all_sigma, n_trials=50):
    """E5: M_actual comparison — RS vs random subspaces."""
    conds = n - k - w
    print(f"\n=== E5: M_actual (true list size) ===")

    if p**k > 200000:
        print(f"  SKIP: p^k = {p**k} too large for exhaustive codeword search")
        return

    L = [pow(omega, i, p) for i in range(n)]

    def eval_poly(coeffs, x, p):
        val = 0
        for c in reversed(coeffs):
            val = (val * x + c) % p
        return val

    # Precompute all codewords
    print(f"  Precomputing all {p**k} RS[{n},{k}] codewords...")
    codewords = []
    for idx in range(p**k):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        f_eval = tuple(eval_poly(coeffs, x, p) for x in L)
        codewords.append(f_eval)
    print(f"  Done. {len(codewords)} codewords.")

    rs_Mactual = []
    for trial in range(n_trials):
        # Random center
        c_eval = tuple(random.randint(0, p-1) for _ in range(n))
        # Count codewords within distance w
        count = sum(1 for f in codewords if sum(1 for i in range(n) if f[i] != c_eval[i]) <= w)
        rs_Mactual.append(count)

    print(f"  RS M_actual: avg={sum(rs_Mactual)/len(rs_Mactual):.2f}, max={max(rs_Mactual)}")

    # Also compute M_alg for the same centers to see overcounting ratio
    rs_Malg = []
    for trial in range(n_trials):
        c_eval = tuple(random.randint(0, p-1) for _ in range(n))
        # Get c_coeffs via DFT
        c_coeffs = [0] * n
        omega_inv = pow(omega, p-2, p)
        n_inv = pow(n, p-2, p)
        for j in range(n):
            val = 0
            for i in range(n):
                val = (val + c_eval[i] * pow(omega_inv, i*j, p)) % p
            c_coeffs[j] = (val * n_inv) % p
        A, b = rs_coefficient_matrix(n, k, w, c_coeffs, p)
        M_alg = count_on_affine(all_sigma, A, b, p)
        rs_Malg.append(M_alg)

    print(f"  RS M_alg:    avg={sum(rs_Malg)/len(rs_Malg):.2f}, max={max(rs_Malg)}")
    print(f"  Overcounting: avg ratio = {sum(rs_Malg)/max(sum(rs_Mactual),1):.2f}")

    # Worst-case analysis
    print(f"\n  Searching for worst-case center (max M_actual)...")
    best_M = 0
    best_center = None
    for trial in range(200):
        c_eval = tuple(random.randint(0, p-1) for _ in range(n))
        count = sum(1 for f in codewords if sum(1 for i in range(n) if f[i] != c_eval[i]) <= w)
        if count > best_M:
            best_M = count
            best_center = c_eval
            # Also check M_alg
            c_coeffs = [0] * n
            for j in range(n):
                val = 0
                for i in range(n):
                    val = (val + c_eval[i] * pow(omega_inv, i*j, p)) % p
                c_coeffs[j] = (val * n_inv) % p
            A, b = rs_coefficient_matrix(n, k, w, c_coeffs, p)
            M_alg = count_on_affine(all_sigma, A, b, p)
            print(f"    Trial {trial}: M_actual={count}, M_alg={M_alg}")

    return rs_Mactual

def rs_coefficient_matrix(n, k, w, c_coeffs, p):
    conds = n - k - w
    A = []
    b = []
    for r in range(conds):
        m = k + w + r
        row = []
        for j in range(1, w + 1):
            coeff = ((-1)**j * c_coeffs[m - w + j]) % p
            row.append(coeff)
        A.append(row)
        b.append((-c_coeffs[m - w]) % p)
    return A, b

def experiment_6_which_direction(n, k, w, p, omega, all_sigma, n_trials=2000):
    """E6: For HIGH-M subspaces, characterize the normal vectors."""
    conds = n - k - w
    N = len(all_sigma)
    threshold = max(3 * N / p**conds, 3)

    print(f"\n=== E6: Normal vector analysis of high-M subspaces ===")
    print(f"  threshold = {threshold:.1f}")

    high_M_normals = []
    low_M_normals = []

    for _ in range(n_trials):
        A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(conds)]
        b = [random.randint(0, p-1) for _ in range(conds)]
        M = count_on_affine(all_sigma, A, b, p)

        if M > threshold:
            high_M_normals.append((M, A))
        else:
            low_M_normals.append((M, A))

    print(f"  High-M cases: {len(high_M_normals)}/{n_trials}")

    if not high_M_normals:
        print("  No high-M cases found.")
        return

    # Analyze the normal vectors (rows of A) for high-M cases
    # Key question: do high-M normals avoid certain directions?
    print(f"\n  High-M normal vector analysis:")
    for M, A in sorted(high_M_normals, reverse=True)[:10]:
        # Normalize first nonzero entry to 1
        norm_rows = []
        inv_table = make_inv(p)
        for row in A:
            first_nz = next((j for j in range(w) if row[j] != 0), None)
            if first_nz is not None:
                scale = inv_table[row[first_nz]]
                norm_row = tuple((row[j] * scale) % p for j in range(w))
            else:
                norm_row = tuple(row)
            norm_rows.append(norm_row)
        print(f"    M={M}: normals = {norm_rows}")

    # Statistical: distribution of each coordinate's magnitude
    print(f"\n  Coordinate magnitude distribution (high-M vs low-M):")
    for j in range(w):
        high_nz = sum(1 for _, A in high_M_normals for row in A if row[j] != 0)
        high_total = len(high_M_normals) * conds
        low_nz = sum(1 for _, A in low_M_normals for row in A if row[j] != 0)
        low_total = len(low_M_normals) * conds
        print(f"    σ_{j+1} nonzero: high-M = {high_nz}/{high_total} ({high_nz/max(high_total,1):.3f}), "
              f"low-M = {low_nz}/{low_total} ({low_nz/max(low_total,1):.3f})")

def main():
    test_cases = [
        (10, 5, 3, 11),   # conds=2, p^k manageable
        (12, 6, 4, 13),   # conds=2
    ]

    for n, k, w, p in test_cases:
        omega = find_omega(p, n)
        inv_table = make_inv(p)
        conds = n - k - w

        print(f"\n{'='*70}")
        print(f"n={n}, k={k}, w={w}, p={p}, conds={conds}, omega={omega}")
        print(f"{'='*70}")

        all_sigma = compute_all_sigma(n, w, p, omega)
        N = len(all_sigma)
        print(f"N = C({n},{w}) = {N}, N/p^c = {N/p**conds:.2f}")

        experiment_1_fiber_structure(n, w, p, omega, all_sigma)
        if w >= 3:
            experiment_2_pair_alignment(n, k, w, p, omega, all_sigma)
        experiment_4_toeplitz_vs_dangerous(n, k, w, p, omega, all_sigma, inv_table)
        experiment_5_Mactual(n, k, w, p, omega, all_sigma)
        experiment_6_which_direction(n, k, w, p, omega, all_sigma)

if __name__ == '__main__':
    main()
