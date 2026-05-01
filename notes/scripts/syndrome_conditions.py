#!/usr/bin/env python3
"""
Syndrome conditions analysis:

Each error set B of size w (with |[n]\B| = n-w ≥ k+1) imposes
ONE linear condition on the syndrome s ∈ F_p^{n-k}:

  "The Lagrange interpolant through c|_{[n]\B} has degree < k"

This is equivalent to: the LEADING COEFFICIENT of the degree-(n-w-1)
Lagrange interpolant through n-w points is zero.

So each error set B corresponds to a HYPERPLANE H_B in the syndrome
space F_p^{n-k}. The center c achieves M list codewords iff its
syndrome lies in the intersection of M hyperplanes H_{B_1} ∩ ... ∩ H_{B_M}.

Question: what is the maximum M such that M hyperplanes H_B have
a non-empty intersection?

For GENERIC hyperplanes: max M = n-k (dimension of syndrome space).
For the SPECIFIC hyperplanes from RS structure: max M could be larger
(if some hyperplanes are linearly dependent).

This analysis explains M and should give a PROOF of M = O(1).

Let me compute the hyperplane normals (one per error set B) and
check their rank.
"""

import numpy as np
from itertools import combinations
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
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)

def modinv(a, p):
    return pow(a % p, p - 2, p)

def syndrome_analysis(n, k, p, w):
    """
    For each error set B (|B| = w), compute the hyperplane normal
    in syndrome space.

    The syndrome space: s ∈ F_p^{n-k}.
    The parity check matrix: H[r][i] = L[i]^{k+r} for r=0,...,n-k-1.
    Syndrome: s = Hc.

    For agreement set S = [n]\B (|S| = n-w):
    The condition "exists degree-<k polynomial through c|_S" is:
    the first n-w-k+1 ... hmm, let me think differently.

    Actually: a polynomial of degree < k is determined by k coefficients.
    Given n-w ≥ k evaluation points, the polynomial is overdetermined.
    The extra conditions: n-w-k linear equations on the syndrome.

    For n-w = k+1 (i.e., w = n-k-1 = d-2): ONE extra condition.
    For n-w = k (i.e., w = n-k = d-1): ZERO extra conditions (always solvable).
    For n-w > k+1: MULTIPLE extra conditions per error set.

    The extra conditions for agreement set S:
    The Vandermonde system V_S * a = c|_S where V_S is (n-w) x k.
    For this to be consistent: c|_S must be in the column space of V_S.
    The column space has dimension k (since MDS: any k columns are independent).
    The codimension: n-w-k.
    So: n-w-k linear conditions on c|_S.

    In terms of the syndrome s = Hc: the conditions become LINEAR in s.
    Each condition is a hyperplane in F_p^{n-k}.

    Total conditions per error set B: n-w-k = n-k-w.
    For w at Johnson (w ≈ 0.29n): n-k-w ≈ 0.5n - 0.29n = 0.21n.

    So each error set contributes 0.21n conditions.
    For M error sets: M × 0.21n conditions in n-k = n/2 dimensional space.
    Max M: n/2 / (0.21n) ≈ 2.4.

    Wait, that's too small! The data shows M up to 7.

    The issue: the conditions from different error sets are NOT independent.
    They share common structure (through the Vandermonde matrix).
    """

    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    d_code = n - k + 1

    # Parity check matrix H: H[r][i] = L[i]^{k+r}
    H = np.zeros((n-k, n), dtype=np.int64)
    for r in range(n-k):
        for i in range(n):
            H[r, i] = pow(L[i], k + r, p)

    # Vandermonde matrix V: V[i][j] = L[i]^j for j=0,...,k-1
    V = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        for j in range(k):
            V[i, j] = pow(L[i], j, p)

    print(f"n={n}, k={k}, p={p}, w={w}")
    print(f"d={d_code}, |S|=n-w={n-w}, conditions per B: {n-w-k}")
    print(f"Syndrome space dim: {n-k}")
    print(f"Total error sets: C({n},{w}) = {comb(n,w)}")

    # For each error set B, compute the condition normals
    # For S = [n]\B: the condition is c|_S ∈ col(V_S).
    # Equivalently: (I - V_S (V_S^T V_S)^{-1} V_S^T) c|_S = 0.
    # In syndrome coordinates: this becomes linear in s.

    # More directly: the conditions are that certain minors of an augmented
    # matrix vanish. Each condition is a LINEAR function of s.

    # Let me compute: for each B, what linear conditions on s = Hc are imposed?

    # V_S is the (n-w) x k submatrix of V with rows from S.
    # The condition: c|_S ∈ col(V_S).
    # Equivalently: for each vector u in the LEFT KERNEL of V_S (dim n-w-k):
    # u^T c|_S = 0.

    # In terms of s = Hc: s_r = sum_i H[r][i] c_i = sum_i L[i]^{k+r} c_i.
    # And u^T c|_S = sum_{i in S} u_i c_i.

    # We need to express sum_{i in S} u_i c_i in terms of s.
    # This requires expressing the "indicator" sum over S as a linear combination
    # of the syndrome components s_r.

    # Actually, let me use a more direct approach.
    # For each B: the condition that a degree-<k polynomial passes through c|_S
    # is equivalent to the DETERMINANT of a specific (n-w) x (n-w) matrix being zero
    # (when n-w > k: the augmented Vandermonde matrix).

    # For n-w = k+1 (w = d-2): one condition.
    # The determinant of the (k+1) x (k+1) matrix:
    # [V_S | c|_S] where V_S is (k+1) x k and c|_S is (k+1) x 1.
    # det([V_S, c|_S]) = 0.

    # This determinant, expanded along the last column, gives:
    # sum_{i in S} (-1)^i c_{S_i} * M_i = 0
    # where M_i is the k x k minor of V_S with row i removed.

    # Since V is Vandermonde: M_i = det(V_{S\{i}}) = product_{a<b in S\{i}} (L[a] - L[b]).

    # So the condition is: sum_{i in S} c_{S_i} * cofactor_i = 0.

    # For n-w > k+1: there are n-w-k such conditions (from n-w-k independent
    # rows of the left kernel of V_S).

    # Let me compute the RANK of the condition matrix for all error sets.

    # For each B: compute the (n-w-k) x n condition matrix C_B
    # such that C_B * c = 0 for c in the correct coset.

    # Then: the total condition matrix for M error sets is the vertical stack
    # of their C_B matrices. Its rank determines the codimension of the
    # feasible set of centers.

    # If rank = R: the feasible set has dimension n - R.
    # For the set to be nonempty: we need R ≤ n (or n-k in syndrome space).

    conditions_per_B = n - w - k
    total_error_sets = comb(n, w)

    # Compute all condition normals
    all_normals = []  # list of (n-k)-dimensional vectors (in syndrome space)

    for B in combinations(range(n), w):
        S = [i for i in range(n) if i not in B]
        assert len(S) == n - w

        # V_S: (n-w) x k submatrix
        V_S = np.array([[pow(L[i], j, p) for j in range(k)] for i in S], dtype=np.int64) % p

        # Left kernel of V_S: vectors u with u^T V_S = 0 mod p
        # Compute via row reduction of V_S^T
        # V_S^T is k x (n-w). Left kernel of V_S = right kernel of V_S^T.

        # Actually, let me use the augmented approach.
        # For each "extra" basis vector e_l (l = k, k+1, ..., n-w-1 indexing into S):
        # The condition: can we extend the first k columns to include the l-th column?

        # More directly: V_S has rank k (MDS). The left kernel has dimension n-w-k.
        # A basis for the left kernel: compute via Gaussian elimination on V_S^T.

        # Let me compute the left kernel mod p.
        VS_T = V_S.T.copy() % p  # k x (n-w)

        # Row reduce VS_T to find kernel
        # ... complex mod p linear algebra. Let me use a different approach.

        # For each condition: it's a linear function of c.
        # In syndrome coordinates: express as a linear function of s.

        # The syndrome s = H c. So c = H^{-1} s + (element of RS_k).
        # Since the conditions are on the COSET (independent of the RS_k part),
        # they only depend on s.

        # Let me compute: for each u in the left kernel of V_S,
        # express sum_{i in S} u_i c_i as a linear function of s.

        # sum_{i in S} u_i c_i = u^T c|_S
        # We need to express this in terms of s = Hc.

        # Let e_S be the (n-w)-to-n embedding: (e_S)_{j,l} = delta_{S[j], l}.
        # Then c|_S = e_S c, and u^T c|_S = u^T e_S c = (e_S^T u)^T c.

        # We need (e_S^T u)^T c = 0. In terms of s = Hc:
        # We need v = e_S^T u such that v^T c = 0 for all c with Hc = s.
        # This means v must be in the span of the rows of H.
        # So v = H^T w for some w ∈ F_p^{n-k}.
        # Then v^T c = w^T H c = w^T s.
        # So the condition is w^T s = 0.

        # We need to find w such that H^T w = e_S^T u, i.e., w = (H^T)^{-1} (e_S^T u).
        # But H^T is n x (n-k), not square. We need (e_S^T u) to be in col(H^T).

        # Since H has rank n-k and v = e_S^T u has n components:
        # v ∈ col(H^T) iff v ⊥ ker(H) = RS_k.
        # So v ⊥ RS_k iff v is in the image of the parity check.

        # Is v ⊥ RS_k? v = sum_{j in S} u_j e_{S[j]}. And u^T V_S = 0.
        # V_S = (L[S[j]]^l)_{j,l}. So sum_j u_j L[S[j]]^l = 0 for l=0,...,k-1.
        # This means: sum_j u_j f(L[S[j]]) = 0 for all polynomials f of degree < k.
        # I.e., v = sum u_j e_{S[j]} ⊥ RS_k. ✓

        # So v is in col(H^T), and w = (H H^T)^{-1} H v.

        # For each left kernel vector u: compute w and record it as a syndrome condition.
        pass

    # This is getting complex. Let me just compute the RANK of all conditions directly.
    # Build the matrix: rows = conditions, columns = syndrome coordinates.

    # Alternative approach: compute the "condition map" numerically.
    # For each error set B: compute the affine subspace of syndromes that allow B.
    # Then: M = max |{B_1, ..., B_M}| such that intersection is nonempty.

    # Since we already know M from the FFT computation, let me just verify
    # the dimension analysis.

    # For the worst-case syndrome s*: how many hyperplanes does it lie on?
    # This is exactly M.

    # Approach: for each syndrome s, count how many error sets B are "valid" for s.
    # Valid B: the Lagrange interpolant through c|_{[n]\B} has degree < k.

    # For each s, compute M(s) = number of valid B.
    # Then M = max_s M(s).

    # We can compute this via the FFT (already done) or by direct enumeration.

    # Let me instead analyze the ALGEBRAIC DIMENSION.
    # For n-w = k+1 (one condition per B):
    # The C(n,w) hyperplanes in F_p^{n-k} have some intersection pattern.
    # M = max number of hyperplanes through a common point.

    # This is the "maximum point-hyperplane incidence" problem.

    # For C(n,w) hyperplanes in F_p^{n-k}:
    # Average incidence per point: C(n,w) * p^{n-k-1} / p^{n-k} = C(n,w) / p.
    # For p >> C(n,w): average < 1, so most points are on 0 hyperplanes.
    # But some points could be on many.

    # The max incidence is bounded by the RANK of the normal matrix.
    # If the C(n,w) normals span F_p^{n-k}: max incidence ≤ n-k (dimension).
    # If they don't span: max incidence could be larger.

    # For our case (n-w = k+1): the normals are determined by Vandermonde cofactors.
    # Let me compute the rank of the normal matrix.

    # For n=6, k=3, w=2 (n-w=4=k+1, one condition per B):
    # C(6,2) = 15 error sets. 15 normals in F_p^3.
    # Max normals through a point: M = 3 (from our data).

    # For n=8, k=4, w=3 (n-w=5=k+1, one condition per B):
    # C(8,3) = 56 error sets. 56 normals in F_p^4.
    # Max normals through a point: M = 7.

    # Let me compute the actual normals for the small cases.

    # For n-w = k+1: the condition for error set B is:
    # det([V_S, c|_S]) = 0 where S = [n]\B, |S| = k+1.
    # This is a linear condition on c: sum_{i in S} c_i * cofactor_i(V_S) = 0.
    # The cofactor_i = (-1)^{k+i} det(V_{S\{i}}).

    print(f"\nComputing hyperplane normals for n-w = k+1 case (w={n-k-1})...")
    w_special = n - k - 1  # n-w = k+1

    normals = []
    error_sets = []

    for B in combinations(range(n), w_special):
        S = [i for i in range(n) if i not in B]
        assert len(S) == k + 1

        # Compute cofactors of the (k+1) x (k+1) augmented Vandermonde
        # [V_S] where V_S[j][l] = L[S[j]]^l for l=0,...,k-1, and the
        # (k+1)-th column is the c|_S values.
        # The condition: sum_j c_{S[j]} * cofactor_j = 0.
        # cofactor_j = (-1)^{k+j} det(V_{S without row j}).

        # V_{S without row j}: k x k Vandermonde with points {L[i] : i in S, i ≠ S[j]}
        cofactors = []
        for j in range(k + 1):
            # Points: L[S[0]], ..., L[S[j-1]], L[S[j+1]], ..., L[S[k]]
            points = [L[S[m]] for m in range(k + 1) if m != j]
            # det of Vandermonde = prod_{a<b} (points[b] - points[a])
            det_val = 1
            for a in range(k):
                for b in range(a + 1, k):
                    det_val = det_val * (points[b] - points[a]) % p
            sign = (-1) ** (k + j)
            cofactors.append(sign * det_val % p)

        # The condition: sum_j c_{S[j]} * cofactor[j] = 0
        # In terms of the FULL c vector (length n):
        # normal[i] = cofactor[j] if i = S[j], 0 otherwise.
        normal_full = [0] * n
        for j in range(k + 1):
            normal_full[S[j]] = cofactors[j]

        # Convert to syndrome space: the normal in syndrome space is
        # n_s such that n_s^T s = 0 iff the original condition holds.
        # Since s = Hc: n_full^T c = 0 iff (H^+ n_full)^T s = 0
        # where H^+ = (HH^T)^{-1} H.

        # But we already know n_full ⊥ RS_k, so n_full ∈ RS_k^⊥ = Im(H^T).
        # So n_full = H^T w for some w ∈ F_p^{n-k}.
        # The syndrome condition is w^T s = 0.

        # Solve H^T w = n_full for w.
        # H^T is n x (n-k). We need to solve (n-k) unknowns from n equations.
        # Since H^T has rank n-k: the solution is unique.

        # Use the first (n-k) rows of H^T (which are independent):
        HT_sub = np.array([[H[r, i] for r in range(n-k)] for i in range(n)], dtype=np.int64)
        # HT_sub is n x (n-k). Take first n-k rows:
        HT_square = HT_sub[:n-k, :].copy() % p  # (n-k) x (n-k)
        n_sub = np.array(normal_full[:n-k], dtype=np.int64) % p

        # Solve HT_square^T w = n_sub... actually this is complex.
        # Let me just use the normal in the FULL c-space and project to syndrome space.

        # Simpler: just record the normals in c-space and compute rank/incidence there.
        normals.append(normal_full)
        error_sets.append(B)

    # Convert normals to numpy
    normal_matrix = np.array(normals, dtype=np.int64) % p  # C(n,w) x n

    print(f"Number of hyperplanes: {len(normals)}")
    print(f"Normal matrix shape: {normal_matrix.shape}")

    # The normals are in F_p^n but live in the (n-k)-dimensional subspace RS_k^⊥.
    # Project to syndrome space by multiplying by H^{-T} (or equivalent).

    # Actually, let me just compute: for the WORST-CASE syndrome s,
    # how many normals are orthogonal to c (where Hc = s)?

    # This is equivalent to: find c ∈ F_p^n that is in the kernel of the
    # maximum number of row vectors of normal_matrix.

    # For each c: the number of satisfied conditions = number of rows r
    # with (normal_matrix[r] * c) % p == 0.

    # Brute force: try all c ∈ F_p^n. Too large.
    # Better: try all syndromes s ∈ F_p^{n-k} and count conditions.

    # For each syndrome s: pick ANY c with Hc = s.
    # Then count: |{B : normal_B^T c = 0}|.

    # Since normal_B ⊥ RS_k: the count depends only on s, not the specific c.

    if p ** (n-k) <= 10_000_000:
        print(f"Exhaustive syndrome search (p^{{n-k}} = {p**(n-k)})...")
        max_count = 0
        best_syndrome = None

        # Find a specific c for each syndrome: use c = H^{pseudo-inv} * s
        # or just iterate over c directly (expensive but correct).

        # Actually: normal_B^T c = sum_i normal_B[i] c_i.
        # This depends on c, not just s = Hc.
        # But: normal_B ∈ RS_k^⊥, so normal_B^T c = normal_B^T (c - f) for any f ∈ RS_k.
        # And c - f = some syndrome representative.

        # Let's just compute: for each c ∈ F_p^n, count satisfied conditions.
        # But p^n is way too large.

        # Use the syndrome: for each s, pick the UNIQUE c in the zero coset
        # (the canonical representative with c_i = 0 for i >= n-k... no, this
        # doesn't work because we need specific coordinates).

        # Instead: use the FFT result directly.
        # We already know M from FFT. Let me just verify the dimension analysis.

        # The rank of the normal matrix:
        # normal_matrix is C(n,w_special) x n. Its rank in F_p:
        # (Using Gaussian elimination mod p)

        def rank_mod_p(mat, p):
            """Compute rank of matrix mod p."""
            m, nn = mat.shape
            M = mat.copy() % p
            rank = 0
            for col in range(nn):
                # Find pivot
                pivot = -1
                for row in range(rank, m):
                    if M[row, col] % p != 0:
                        pivot = row
                        break
                if pivot == -1:
                    continue
                # Swap
                M[[rank, pivot]] = M[[pivot, rank]]
                # Eliminate
                inv_pivot = pow(int(M[rank, col]), p-2, p)
                for row in range(m):
                    if row != rank and M[row, col] % p != 0:
                        factor = M[row, col] * inv_pivot % p
                        M[row] = (M[row] - factor * M[rank]) % p
                rank += 1
            return rank

        r = rank_mod_p(normal_matrix, p)
        print(f"Rank of normal matrix: {r} (out of {n-k} syndrome dims)")
        print(f"Normals span a {r}-dimensional subspace of F_p^{n}")
        print(f"Expected M from dimension: ≤ dim(syndrome) + dependencies = ???")

    # Let me also check: for n-w > k+1 (the Johnson radius case),
    # how many conditions per error set?
    if w != w_special:
        print(f"\nFor w={w} (Johnson radius): conditions per B = {n-w-k}")
        print(f"Total conditions: C({n},{w}) * {n-w-k} = {comb(n,w) * (n-w-k)}")
        print(f"Syndrome dim: {n-k}")
        print(f"Naive bound: M ≤ {(n-k) // (n-w-k)} (if conditions independent)")

# ================================================================
# Run analysis
# ================================================================
syndrome_analysis(6, 3, 7, 2)
print("\n" + "="*60)
syndrome_analysis(8, 4, 17, 3)
print("\n" + "="*60)
syndrome_analysis(10, 5, 11, 3)
print("\n" + "="*60)
syndrome_analysis(12, 6, 13, 4)
