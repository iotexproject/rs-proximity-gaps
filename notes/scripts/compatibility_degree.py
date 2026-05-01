#!/usr/bin/env python3
"""
Analyze the compatibility conditions as polynomials in P_S's coefficients.

For each B (|B|=w), the system A*q = rhs has n-k equations in w unknowns.
A[j-k][l] = P_S[j-l], rhs[j-k] = c_j.

The compatibility condition is: rank([A | rhs]) = rank(A).
Equivalently: all (w+1) x (w+1) minors of [A | rhs] vanish.

Since rank(A) = w generically: exactly conds/B = (n-k-w) minors must vanish.

The minors are polynomials in P_S's coefficients.
P_S coefficients = elementary symmetric polynomials of {ω^i : i ∈ S}.

Total degree of each minor in P_S coefficients: w+1 (determinant of (w+1) x (w+1) matrix
where each entry is a P_S coefficient, hence degree 1 in the e_j's).

But the e_j's themselves have varying degrees in the root set {ω^i : i ∈ S}:
e_1 has degree 1, e_2 degree 2, ..., e_{n-w} degree n-w.

The TOTAL degree of the compatibility condition as a function of the ROOTS:
each minor involves w+1 entries from P_S, each entry being some e_j.
The total degree ≤ sum of degrees of the w+1 entries involved.

For the Toeplitz-like structure: entry A[row][l] = P_S[j-l] where j = k + row.
P_S[m] = (-1)^{n-w-m} e_{n-w-m} has degree n-w-m in the roots.

So the degree of each matrix entry:
A[row][l] = P_S[k + row - l]. Degree = n-w - (k + row - l) = n-w-k-row+l = (n-w-k) - row + l.

For l=0,...,w-1 and row=0,...,n-k-1.

The determinant degree: sum of degrees of selected entries.

Let me compute this more carefully.
"""

from itertools import combinations
from math import comb


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


def rank_mod_p(mat, p):
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    nn = len(mat[0])
    M_mat = [row[:] for row in mat]
    for i in range(m):
        for j in range(nn):
            M_mat[i][j] %= p
    rank = 0
    for col in range(nn):
        pivot = -1
        for row in range(rank, m):
            if M_mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        M_mat[rank], M_mat[pivot] = M_mat[pivot], M_mat[rank]
        inv_pivot = pow(M_mat[rank][col], p - 2, p)
        for row in range(m):
            if row != rank and M_mat[row][col] % p != 0:
                factor = M_mat[row][col] * inv_pivot % p
                for j in range(nn):
                    M_mat[row][j] = (M_mat[row][j] - factor * M_mat[rank][j]) % p
        rank += 1
    return rank


def poly_coeffs(roots, p):
    result = [1]
    for r in roots:
        new = [0] * (len(result) + 1)
        for i in range(len(result)):
            new[i] = (new[i] + (-r) * result[i]) % p
            new[i+1] = (new[i+1] + result[i]) % p
        result = new
    return result


def lagrange_poly(values, points, p):
    n = len(values)
    result = [0] * n
    for i in range(n):
        denom = 1
        for j in range(n):
            if j != i:
                denom = denom * (points[i] - points[j]) % p
        denom_inv = pow(denom, p - 2, p)
        basis = [denom_inv * values[i] % p]
        for j in range(n):
            if j != i:
                new_basis = [0] * (len(basis) + 1)
                for kk in range(len(basis)):
                    new_basis[kk] = (new_basis[kk] + (-points[j]) * basis[kk]) % p
                    new_basis[kk+1] = (new_basis[kk+1] + basis[kk]) % p
                basis = new_basis
        for j in range(len(basis)):
            if j < n:
                result[j] = (result[j] + basis[j]) % p
    return result


def analyze_structure(n, k, p, w):
    """
    For conds/B = 1: the compatibility condition is a SINGLE determinant.
    det([A | rhs]) = 0 where [A | rhs] is (w+1) x (w+1).
    (Using the w+1 equations that include the incompatible one.)

    Actually, A has n-k rows and w columns. For rank(A) = w (generic):
    the compatibility requires rhs to be in col(A).
    This is: for every (w+1)-subset of rows, the augmented (w+1) x (w+1)
    determinant vanishes.

    For conds/B = 1: only 1 extra equation beyond w. So there are C(n-k, w+1)
    minors that should vanish, but they all reduce to 1 condition (since
    the non-compatible part is 1-dimensional).

    Let me compute the EXPLICIT determinant for conds/B = 1 cases.
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}, conds/B={n-w-k}")

    # Use a specific center
    # For simplicity: c = (1, 0, 0, ..., 0, 0) (weight 1)
    # This has M = 0 (weight 1 < w). Need weight w.

    # Use structured center: c_i = 1 for i < w, 0 otherwise (weight w)
    # But this might not be worst-case.

    # Instead, let me parametrize the system symbolically.
    # The system A*q = rhs where A depends on P_S and rhs depends on c.
    #
    # For conds/B = 1 (n-w-k = 1):
    # A is (n-k) x w. The system has n-k equations in w unknowns.
    # Since n-k = w+1: it's (w+1) x w. Overdetermined by 1.
    #
    # The compatibility condition: det([A | rhs]) = 0.
    # This is a SINGLE polynomial in P_S's coefficients and c's coefficients.

    if n - w - k != 1:
        print(f"  conds/B = {n-w-k} ≠ 1, skipping detailed analysis")
        # For conds/B = 2: the condition involves 2x2 minors etc.
        # More complex but similar.

        # Let me just compute: for each B, the RANK of A.
        # If rank(A) = w for all B: then there are exactly conds/B conditions.

        # Use a worst-case center
        codewords = []
        for idx in range(p**k):
            a = []
            temp = idx
            for _ in range(k):
                a.append(temp % p)
                temp //= p
            f = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
            codewords.append(f)

        best_M = 0
        best_e = None
        import random
        random.seed(42)
        for _ in range(500):
            positions = sorted(random.sample(range(n), w))
            vals = [random.randint(1, p-1) for _ in range(w)]
            e = [0] * n
            for j, pos in enumerate(positions):
                e[pos] = vals[j]
            M = sum(1 for f in codewords if sum(1 for i in range(n) if (e[i] - f[i]) % p != 0) <= w)
            if M > best_M:
                best_M = M
                best_e = e[:]

        if best_M <= 1:
            print(f"  M ≤ 1, skip")
            return

        c_poly = lagrange_poly(best_e, L, p)

        # Compute compatibility for all B
        compatible = 0
        for B in combinations(range(n), w):
            S = [i for i in range(n) if i not in B]
            P_S = poly_coeffs([L[i] for i in S], p)
            A = [[0] * w for _ in range(n - k)]
            rhs = [0] * (n - k)
            for eq_idx in range(n - k):
                j = k + eq_idx
                rhs[eq_idx] = c_poly[j] if j < len(c_poly) else 0
                for l in range(w):
                    ps_idx = j - l
                    if 0 <= ps_idx < len(P_S):
                        A[eq_idx][l] = P_S[ps_idx] % p
            r_A = rank_mod_p(A, p)
            aug = [A[i][:] + [rhs[i]] for i in range(n - k)]
            r_aug = rank_mod_p(aug, p)
            if r_aug == r_A:
                compatible += 1

        print(f"  M = {best_M}, algebraic M = {compatible}")
        return

    # === conds/B = 1 case ===
    print(f"  conds/B = 1: analyzing the single determinant condition")

    # The (w+1) x (w+1) matrix [A | rhs]:
    # Row j (j = k, ..., n-1 = k+w):
    #   [P_S[j], P_S[j-1], ..., P_S[j-w+1], c_j]
    # where P_S has degree n-w, so P_S[m] = 0 for m > n-w or m < 0.

    # Note: n-k = w+1, so there are exactly w+1 rows.
    # The matrix is (w+1) x (w+1).
    # Entry in row r (0-indexed), column l (0-indexed):
    #   for l < w: P_S[k+r - l]
    #   for l = w: c_{k+r}

    # The entries P_S[k+r-l]: these are coefficients of P_S at index k+r-l.
    # P_S has degree n-w = k+1. So P_S[m] for m = 0, ..., k+1.
    # k+r-l ranges from k (r=0,l=0) to k+w-0 = k+w = n-1 (r=w, l=0).
    # Maximum: n-1. But P_S has degree k+1 = n-w. So P_S[m] = 0 for m > k+1.
    # k+r-l > k+1 iff r-l > 1, i.e., r > l+1.

    # For the Toeplitz structure: the matrix is ALMOST upper-triangular.
    # Let me write it out explicitly.

    # For n=8, k=4, w=3: 4x4 matrix.
    # Row 0 (j=4): [P_S[4], P_S[3], P_S[2], c_4]
    # Row 1 (j=5): [P_S[5], P_S[4], P_S[3], c_5]
    # Row 2 (j=6): [P_S[6], P_S[5], P_S[4], c_6]
    # Row 3 (j=7): [P_S[7], P_S[6], P_S[5], c_7]
    #
    # P_S has degree 5 (n-w = 5). So P_S[0..5] are the coefficients.
    # P_S[6] = P_S[7] = 0.
    #
    # Row 0: [P_S[4], P_S[3], P_S[2], c_4]
    # Row 1: [P_S[5], P_S[4], P_S[3], c_5]  (P_S[5] = leading coeff = 1)
    # Row 2: [0,       P_S[5], P_S[4], c_6]
    # Row 3: [0,       0,       P_S[5], c_7]

    # This is UPPER TRIANGULAR (with P_S[5]=1 on the subdiagonal past row 1).
    # Actually, rows 1-3 have a shifted pattern.

    # The determinant: expand...
    # For this specific structure: the determinant is a polynomial in
    # P_S[0],...,P_S[5] and c_4,...,c_7.

    # Since P_S[5] = 1 (monic polynomial), the structure is nice.
    # The determinant is an AFFINE polynomial in P_S[0],...,P_S[4]
    # (since P_S[5] = 1 is fixed).

    # The elementary symmetric polynomials of the agreement points:
    # P_S(x) = x^{k+1} - e_1 x^k + e_2 x^{k-1} - ... + (-1)^{k+1} e_{k+1}
    # where e_j = e_j({ω^i : i ∈ S}).
    #
    # So P_S[k+1] = 1, P_S[k] = -e_1, P_S[k-1] = e_2, ..., P_S[0] = (-1)^{k+1} e_{k+1}.
    #
    # In the (w+1) x (w+1) determinant:
    # the entries involve e_1, ..., e_{k+1} (polynomials in the agreement points).

    # For a SPECIFIC center c: the determinant is a polynomial D(e_1, ..., e_{k+1}).
    # D = 0 is the compatibility condition. The degree of D bounds M.

    # DEGREE ANALYSIS:
    # Each entry P_S[m] has degree (k+1-m) in the elementary symmetric polys.
    # Wait, P_S[m] = (-1)^{k+1-m} e_{k+1-m}.
    # So degree of P_S[m] (in the roots) = k+1-m.

    # In the determinant: we pick one entry per row and column.
    # Entry at (row r, col l) for l < w: P_S[k+r-l], degree = k+1-(k+r-l) = 1-r+l.
    # For l = w: c_{k+r}, degree 0 (constant).

    # The determinant degree = sum of degrees of selected entries.
    # For a term of the Leibniz formula: sum_{r=0}^{w} degree(entry at (r, σ(r))).

    # For the identity permutation (if it contributes):
    # sum = sum_{r=0}^{w-1} (1-r+r) + 0 = sum_{r=0}^{w-1} 1 + 0 = w.

    # Actually, not all entries have the right structure. Let me be more precise.

    # The matrix M[r][l]:
    # For l = 0, ..., w-1: M[r][l] = P_S[k+r-l]
    # For l = w: M[r][w] = c_{k+r}

    # P_S[m] = coefficient of x^m in P_S(x) = ∏_{i∈S}(x - ω^i).
    # P_S[m] is the (k+1-m)-th elementary symmetric polynomial (times ±1).
    # Degree in the roots: k+1-m.

    # For m = k+r-l:
    # Degree = k+1-(k+r-l) = 1-r+l = l-r+1.
    # For l ≥ r-1: degree ≥ 0.
    # For l < r-1: P_S[k+r-l] = 0 (since k+r-l > k+1 iff r-l > 1).

    # So the matrix is UPPER HESSENBERG (entries below the first subdiagonal are 0).

    # The determinant's maximum degree (in the roots):
    # For a permutation σ contributing to det:
    #   sum_r deg(M[r][σ(r)]) = sum_r max(σ(r)-r+1, 0) when σ(r) < w
    #                          + 0 when σ(r) = w (the c column).

    # The maximum degree is achieved by the permutation that maximizes the sum.
    # Since deg(M[r][l]) = max(l-r+1, 0) for l < w and 0 for l = w:
    # the max sum is sum_{r: σ(r)<w} (σ(r)-r+1).

    # For the IDENTITY permutation (σ(r) = r for all r, except one goes to w):
    # We must send exactly one row to column w (the rhs column).
    # For σ: one r* has σ(r*) = w, others have σ(r) = some permutation of {0,...,w-1}\{???}.

    # The degree of the determinant is at most max over permutations of the sum.
    # This is a combinatorial optimization problem.

    # For n=8, k=4, w=3: 4x4 matrix.
    # Degrees:
    #   col 0: deg = 1-r+0 = 1-r. Row 0: 1, Row 1: 0, Row 2: -1 (=0), Row 3: -2 (=0).
    #   col 1: deg = 1-r+1 = 2-r. Row 0: 2, Row 1: 1, Row 2: 0, Row 3: -1 (=0).
    #   col 2: deg = 1-r+2 = 3-r. Row 0: 3, Row 1: 2, Row 2: 1, Row 3: 0.
    #   col 3: deg = 0 (rhs). All rows: 0.

    # Degree matrix:
    #   [1, 2, 3, 0]
    #   [0, 1, 2, 0]
    #   [0, 0, 1, 0]
    #   [0, 0, 0, 0]

    # Max determinant degree: choose one entry per row and column.
    # We need a permutation of {0,1,2,3}.
    # Feasible (nonzero entries only):
    #   σ = (0,1,2,3): all diagonal. Sum = 1+1+1+0 = 3.
    #   σ = (1,0,2,3): Sum = 2+0+1+0 = 3.
    #   σ = (2,1,0,3): Sum = 3+1+0+0 = 4.
    #   σ = (0,2,3,1): row0→0, row1→2, row2→3, row3→1. But col 3 row 2: deg=0. col 1 row 3: deg=0.
    #     Sum = 1+2+0+0 = 3.
    #   σ = (1,2,3,0): row0→1, row1→2, row2→3, row3→0. But M[3][0]=0 (nonexistent). Skip.
    #   σ = (2,0,3,1): row0→2, row1→0, row2→3, row3→1. M[1][0]: P_S[4]=P_S[k]=P_S[4].
    #     deg = 3+0+0+0 = 3.

    # Wait, M[3][0] = P_S[k+3-0] = P_S[7]. P_S has degree 5. P_S[7] = 0. So σ sending row 3 to col 0 gives 0.

    # OK so the maximum degree is 4 from σ = (2,1,0,3): row0→col2 (deg 3), row1→col1 (deg 1), row2→col0 (deg 0), row3→col3 (deg 0).

    # Wait, M[2][0] = P_S[k+2-0] = P_S[6] = 0 (since deg P_S = 5). So this σ doesn't work.

    # Let me redo with the actual nonzero entries.
    # M[0][0] = P_S[4], M[0][1] = P_S[3], M[0][2] = P_S[2], M[0][3] = c_4
    # M[1][0] = P_S[5]=1, M[1][1] = P_S[4], M[1][2] = P_S[3], M[1][3] = c_5
    # M[2][0] = 0, M[2][1] = P_S[5]=1, M[2][2] = P_S[4], M[2][3] = c_6
    # M[3][0] = 0, M[3][1] = 0, M[3][2] = P_S[5]=1, M[3][3] = c_7

    # Nonzero entries per row:
    # Row 0: cols 0,1,2,3
    # Row 1: cols 0,1,2,3
    # Row 2: cols 1,2,3
    # Row 3: cols 2,3

    # Valid permutations (every entry nonzero):
    # row3 must go to col 2 or 3.
    # row2 must go to col 1, 2, or 3.

    # Case row3→col3: row2 can go to 1 or 2.
    #   row2→1: row0,1 permute {0,2}. (0,2) or (2,0).
    #     σ=(0,2,1,3): row0→0(P_S[4]), row1→2(P_S[3]), row2→1(1), row3→3(c_7).
    #       det term: P_S[4]*P_S[3]*1*c_7 * sign. Degree: 1+2+0+0 = 3.
    #     σ=(2,0,1,3): row0→2(P_S[2]), row1→0(1), row2→1(1), row3→3(c_7).
    #       det term: P_S[2]*1*1*c_7. Degree: 3+0+0+0 = 3.
    #   row2→2: row0,1 permute {0,1}.
    #     σ=(0,1,2,3): diag. P_S[4]*P_S[4]*P_S[4]*c_7. Degree: 1+1+1+0 = 3.
    #     σ=(1,0,2,3): P_S[3]*1*P_S[4]*c_7. Degree: 2+0+1+0 = 3.

    # Case row3→col2: row2 goes to 1 or 3.
    #   row2→1: row0,1 permute {0,3}.
    #     σ=(0,3,1,2): P_S[4]*c_5*1*1. Degree: 1+0+0+0 = 1.
    #     σ=(3,0,1,2): c_4*1*1*1. Degree: 0+0+0+0 = 0.
    #   row2→3: row0,1 permute {0,1}.
    #     σ=(0,1,3,2): P_S[4]*P_S[4]*c_6*1. Degree: 1+1+0+0 = 2.
    #     σ=(1,0,3,2): P_S[3]*1*c_6*1. Degree: 2+0+0+0 = 2.

    # Maximum degree = 3. So the determinant is a polynomial of TOTAL DEGREE 3
    # in the elementary symmetric polynomials of the agreement points.
    # Degree 3 in the roots means: at most 3 * (n-w) possible zero sets?
    # No, the bound is more subtle.

    # For e_j of degree j: total degree 3 in the e_j's means the polynomial
    # has degree ≤ 3 when substituting e_j → degree-j polynomial in roots.
    # The actual degree in the ROOTS is at most 3 * max_j deg(e_j) = 3*(k+1).
    # But this is an over-estimate.

    # The correct degree bound:
    # The determinant as a polynomial in (ω^{i_1}, ..., ω^{i_{n-w}}) (the agreement points)
    # is a SYMMETRIC polynomial of total degree = 3 in the elementary symmetric polys.
    # Converting to power sums: degree ≤ 3*(n-w)? No...

    # Actually, the degree in EACH root variable ω^{i_j} is bounded.
    # P_S[m] = e_{k+1-m}({ω^i : i ∈ S}). Each e_l is a degree-l polynomial
    # in the |S| = n-w variables.

    # The determinant is a polynomial in e_1, ..., e_{k+1} of degree ≤ 3.
    # Since e_j has degree j in each root: the determinant has degree ≤ 3*(k+1)
    # in the root variables. But it's SYMMETRIC, so it depends only on the e_j's.

    # For bounding M: M is the number of (n-w)-subsets S of L satisfying the condition.
    # The condition is a polynomial D(e_1(S), ..., e_{k+1}(S)) = 0.
    # The number of solutions: bounded by the "degree" of D viewed as a constraint on subsets.

    # This is related to the SCHWARTZ-ZIPPEL lemma for set systems.
    # For a degree-d polynomial in n-w variables: at most d * p^{n-w-1} zeros.
    # But we're counting SUBSETS of a FIXED set (L = {1,ω,...,ω^{n-1}}), not arbitrary points.

    # The number of (n-w)-subsets S with D(e_1(S),...,e_{k+1}(S)) = 0:
    # is bounded by the degree of D in the e_j's times C(n, n-w-1) / ...
    # This is non-trivial.

    # For now, let me just verify the degree computation.

    print(f"\n  For conds/B = 1:")
    print(f"  Matrix is (w+1) x (w+1) = {w+1} x {w+1}")
    print(f"  P_S degree: n-w = {n-w}")

    # Use a specific center and compute the determinant values
    # for all C(n,w) error sets.

    codewords = []
    for idx in range(p**k):
        a = []
        temp = idx
        for _ in range(k):
            a.append(temp % p)
            temp //= p
        f = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p for i in range(n))
        codewords.append(f)

    best_M = 0
    best_e = None
    import random
    random.seed(42)
    for _ in range(1000):
        positions = sorted(random.sample(range(n), w))
        vals = [random.randint(1, p-1) for _ in range(w)]
        e = [0] * n
        for j, pos in enumerate(positions):
            e[pos] = vals[j]
        M = sum(1 for f in codewords if sum(1 for i in range(n) if (e[i] - f[i]) % p != 0) <= w)
        if M > best_M:
            best_M = M
            best_e = e[:]

    c_poly = lagrange_poly(best_e, L, p)
    print(f"  Center M = {best_M}")

    # Compute determinant for all B
    det_values = {}
    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        P_S = poly_coeffs([L[i] for i in S], p)

        # Build (w+1) x (w+1) matrix [A | rhs]
        mat = [[0] * (w + 1) for _ in range(w + 1)]
        for r in range(w + 1):
            j = k + r
            for l in range(w):
                ps_idx = j - l
                if 0 <= ps_idx < len(P_S):
                    mat[r][l] = P_S[ps_idx] % p
            mat[r][w] = c_poly[j] if j < len(c_poly) else 0

        # Compute determinant mod p
        # Using row reduction
        det_val = 1
        M_det = [row[:] for row in mat]
        for col in range(w + 1):
            pivot = -1
            for row in range(col, w + 1):
                if M_det[row][col] % p != 0:
                    pivot = row
                    break
            if pivot == -1:
                det_val = 0
                break
            if pivot != col:
                M_det[col], M_det[pivot] = M_det[pivot], M_det[col]
                det_val = (-det_val) % p
            det_val = det_val * M_det[col][col] % p
            inv_pivot = pow(M_det[col][col], p - 2, p)
            for row in range(col + 1, w + 1):
                if M_det[row][col] % p != 0:
                    factor = M_det[row][col] * inv_pivot % p
                    for j2 in range(col, w + 1):
                        M_det[row][j2] = (M_det[row][j2] - factor * M_det[col][j2]) % p

        det_values[B] = det_val

    zeros = [B for B, d in det_values.items() if d == 0]
    nonzeros = [B for B, d in det_values.items() if d != 0]
    print(f"  det = 0: {len(zeros)} error sets (these are compatible)")
    print(f"  det ≠ 0: {len(nonzeros)} error sets")
    print(f"  M = {len(zeros)}")

    # Check: does M match?
    actual_M = sum(1 for f in codewords if sum(1 for i in range(n) if (best_e[i] - f[i]) % p != 0) == w)
    print(f"  Actual M (distance exactly w): {actual_M}")

    # Show the det values
    if len(zeros) <= 15:
        print(f"  Compatible error sets:")
        for B in zeros:
            print(f"    B = {B}")


analyze_structure(6, 3, 7, 2)
analyze_structure(8, 4, 17, 3)
# For conds/B = 2
analyze_structure(10, 5, 11, 3)
analyze_structure(12, 6, 13, 4)
