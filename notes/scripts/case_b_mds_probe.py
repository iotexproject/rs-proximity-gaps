"""
Session 1 (case-B attack): probe the MDS-syzygy observation empirically.

Claim (MDS-syzygy lemma): If realizer (γ, E) has |E|=w, intrinsic
representation T_γ ≠ E in S*-basis, and the syzygy
  Σ_{v∈T_γ} c_v ev_v - Σ_{u∈E} ξ_u ev_u = 0
is non-trivial, then |T_γ ∪ E| ≥ D+1 by Vandermonde MDS.

Corollary: |T_γ \ E| ≥ D+1-w = c+1.
Hence |T_γ| ≥ c+1 in any case-B-with-alt-support realizer.

Empirical check: enumerate small (n, c, q), find V_bad witnesses,
classify realizers as A/B, measure |T_γ| and |T_γ ∪ E|.
"""

from itertools import combinations, product
import random


def vandermonde_basis(L, D):
    """L is list of evaluation points, return list of ev_v vectors of length D."""
    return [tuple(v**k % p for k in range(D)) for v in L]  # caller injects p via mod


def make_evals(L, D, p):
    return [[pow(v, k, p) for k in range(D)] for v in L]


def matvec(M, v, p):
    """M is list of rows (vectors); v is a column vector. Compute Mᵀ v as flat sum (here, treat M as basis vectors and v as coefs)."""
    pass  # not needed; we work directly with coefficient vectors


def hankel_rank(seq, p):
    """Return rank of Hankel matrix from sequence."""
    D = len(seq)
    # H_k is k×k Hankel matrix [seq[i+j]] for i,j=0..k-1; needs 2k-1 ≤ D, so k ≤ (D+1)/2
    # rank = max k such that H_k is full rank, capped at (D+1)//2
    # But we want rank = combinatorial Hankel rank ≤ D/2
    # Simpler: compute rank of D×D Toeplitz... actually use standard rank
    # of D × D Hankel. The Hankel rank ≤ D/2 corresponds to recurrence existence.
    max_k = (D + 1) // 2
    rk = 0
    for k in range(1, max_k + 1):
        H = [[seq[i + j] for j in range(k)] for i in range(k)]
        # Compute rank mod p via Gaussian elim
        if mat_rank(H, p) == k:
            rk = k
        else:
            break  # Hankel rank stops where determinant first vanishes
    return rk


def mat_rank(M, p):
    """Rank of integer matrix mod p via Gaussian elimination."""
    M = [row[:] for row in M]
    rows = len(M)
    if rows == 0:
        return 0
    cols = len(M[0])
    rk = 0
    col = 0
    while rk < rows and col < cols:
        # Find pivot
        pivot = None
        for r in range(rk, rows):
            if M[r][col] % p != 0:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        M[rk], M[pivot] = M[pivot], M[rk]
        inv = pow(M[rk][col], p - 2, p)
        for r in range(rows):
            if r != rk and M[r][col] % p != 0:
                factor = (M[r][col] * inv) % p
                for c in range(cols):
                    M[r][c] = (M[r][c] - factor * M[rk][c]) % p
        rk += 1
        col += 1
    return rk


def find_realizers(s1, s2, n, w, D, p):
    """For (s1, s2), enumerate (γ, E) with γ ∈ F_p*, E ⊂ [n] of size w, x_γ ∈ V_E.
    Returns dict γ -> list of E supports.
    """
    L = list(range(1, n + 1))  # evaluation points 1..n
    evals = make_evals(L, D, p)  # evals[i] = [v^0, v^1, ..., v^{D-1}] for v = L[i]
    realizers = {}
    for gamma in range(1, p):
        x_gamma = [(s1[k] + gamma * s2[k]) % p for k in range(D)]
        # Check x_gamma ∈ V_E for any E ⊂ [n] of size w
        for E_idx in combinations(range(n), w):
            # V_E = span of {evals[i] for i in E}: is x_gamma in this span?
            # i.e., does the system "x_gamma = Σ ξ_i evals[i]" have solution
            # Equivalently: rank([evals|x_gamma]) = rank([evals])
            mat_E = [evals[i][:] for i in E_idx]  # w rows of length D
            mat_E_x = mat_E + [x_gamma[:]]
            r1 = mat_rank(mat_E, p)
            r2 = mat_rank(mat_E_x, p)
            if r2 == r1:
                realizers.setdefault(gamma, []).append(E_idx)
                break  # one E per γ enough for counting; remove if want all
    return realizers


def joint_vandermonde_support(s1, s2, n, D, p):
    """Smallest S ⊂ [n] with s_1, s_2 ∈ V_S. Brute force over all S of increasing size."""
    L = list(range(1, n + 1))
    evals = make_evals(L, D, p)
    for size in range(0, D + 1):
        for S_idx in combinations(range(n), size):
            mat = [evals[i][:] for i in S_idx]
            r1 = mat_rank(mat, p)
            mat_s1 = mat + [s1[:]]
            mat_s12 = mat_s1 + [s2[:]]
            if mat_rank(mat_s1, p) == r1 and mat_rank(mat_s12, p) == r1:
                return list(S_idx)
    return None


def s_star_basis_coords(s1, s2, S, n, D, p):
    """Express s1, s2 in basis {ev_v : v ∈ S}. Return (alpha, beta) lists indexed by S position."""
    L = list(range(1, n + 1))
    evals = make_evals(L, D, p)
    if len(S) == 0:
        return [], []
    # Build system mat * coef = s. mat is D × |S|.
    mat = [[evals[i][k] for i in S] for k in range(D)]  # D rows, |S| cols
    # Solve for s1: mat * α = s1
    alpha = solve_linear(mat, s1, p)
    beta = solve_linear(mat, s2, p)
    return alpha, beta


def solve_linear(A, b, p):
    """Solve A x = b mod p; A may be over-determined (rank = ncols)."""
    rows = len(A)
    if rows == 0:
        return []
    cols = len(A[0])
    M = [A[r][:] + [b[r]] for r in range(rows)]
    # Gaussian elimination
    rk = 0
    col = 0
    pivots = []
    while rk < rows and col < cols:
        pivot = None
        for r in range(rk, rows):
            if M[r][col] % p != 0:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        M[rk], M[pivot] = M[pivot], M[rk]
        inv = pow(M[rk][col], p - 2, p)
        for r in range(rows):
            if r != rk and M[r][col] % p != 0:
                factor = (M[r][col] * inv) % p
                for c in range(cols + 1):
                    M[r][c] = (M[r][c] - factor * M[rk][c]) % p
        pivots.append(col)
        rk += 1
        col += 1
    # Back-substitute (reduced row echelon already due to elimination above all rows)
    x = [0] * cols
    for i, c in enumerate(pivots):
        x[c] = (M[i][cols] * pow(M[i][c], p - 2, p)) % p
    return x


def case_label(E_idx, S, D):
    """A or B based on |E ∪ S| ≤ D."""
    union = set(E_idx) | set(S)
    return 'A' if len(union) <= D else 'B'


def t_gamma_support(alpha, beta, S, gamma, p):
    """Return T_γ = {v ∈ S : α_v + γβ_v ≠ 0}, as indices into S."""
    return [j for j in range(len(S)) if (alpha[j] + gamma * beta[j]) % p != 0]


def run_sweep(n, c, p, n_trials=50, seed=0):
    """Sample (s1, s2) ∈ V_bad and check MDS observation in case-B realizers."""
    random.seed(seed)
    D = (n + 1) // 2  # placeholder; really D depends on FRI parameters
    # For paper 3 setup: pick D such that w = D - c is non-trivial
    D = 2 * c  # gives w = c, so unique decoding w ≤ (D-1)/2 = c - 0.5; w = c violates, use D = 2c+1
    D = 2 * c + 1
    w = D - c
    T = (2 * D - 1) // c

    print(f"=== n={n}, c={c}, p={p}, D={D}, w={w}, T={T} ===")

    L = list(range(1, n + 1))
    evals = make_evals(L, D, p)

    case_b_realizers_seen = 0
    case_b_alt_support_seen = 0
    mds_violations = 0
    t_gamma_size_in_case_b = []

    for trial in range(n_trials):
        # Sample (s1, s2) by picking a small S and then random V_S × V_S coords
        # Try V_S × V_S with |S| = w+1 (leading) for higher V_bad density
        S_size = w + 1
        S = random.sample(range(n), S_size)
        # Random alpha, beta in F_p^{|S|}
        alpha = [random.randint(1, p - 1) for _ in range(S_size)]
        beta = [random.randint(1, p - 1) for _ in range(S_size)]
        # Build s1, s2 in F^D
        s1 = [0] * D
        s2 = [0] * D
        for j, v_idx in enumerate(S):
            for k in range(D):
                s1[k] = (s1[k] + alpha[j] * evals[v_idx][k]) % p
                s2[k] = (s2[k] + beta[j] * evals[v_idx][k]) % p

        realizers = find_realizers(s1, s2, n, w, D, p)
        M = len(realizers)
        if M <= T:
            continue  # not in V_bad

        # Found V_bad witness; analyze
        S_star = joint_vandermonde_support(s1, s2, n, D, p)
        if S_star is None:
            continue
        alpha_s, beta_s = s_star_basis_coords(s1, s2, S_star, n, D, p)

        for gamma, E_list in realizers.items():
            for E_idx in E_list:
                label = case_label(E_idx, S_star, D)
                T_gamma = t_gamma_support(alpha_s, beta_s, S_star, gamma, p)
                if label == 'B':
                    case_b_realizers_seen += 1
                    # Check if it's case-B WITH alt support (T_γ ≠ E_idx-image-in-S*)
                    # Simpler: |T_γ| > w means alt support
                    if len(T_gamma) > w:
                        case_b_alt_support_seen += 1
                        t_gamma_size_in_case_b.append(len(T_gamma))
                        # Verify MDS: |T_γ ∪ E| ≥ D+1
                        T_gamma_pts = set(S_star[j] for j in T_gamma)
                        E_pts = set(E_idx)
                        union_size = len(T_gamma_pts | E_pts)
                        if union_size < D + 1:
                            mds_violations += 1
                            print(f"  [VIOLATION] trial {trial}, γ={gamma}: |T_γ ∪ E| = {union_size} < D+1 = {D+1}")

    print(f"  Case-B realizers seen: {case_b_realizers_seen}")
    print(f"  Case-B with alt-support (|T_γ| > w): {case_b_alt_support_seen}")
    if t_gamma_size_in_case_b:
        print(f"  |T_γ| distribution in case-B-alt: min={min(t_gamma_size_in_case_b)}, max={max(t_gamma_size_in_case_b)}, n={len(t_gamma_size_in_case_b)}")
    print(f"  MDS observation violations: {mds_violations}")


if __name__ == "__main__":
    # Small cases first
    for n, c, p in [(8, 3, 17), (10, 3, 41), (12, 3, 41)]:
        run_sweep(n, c, p, n_trials=20)
        print()
