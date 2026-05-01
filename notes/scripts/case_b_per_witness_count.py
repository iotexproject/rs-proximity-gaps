"""
Session 2 (case-B attack): extend session-1 probe to count per-witness M_B.

Per Lemma 2 (Note 0131 follow-up):
  V_bad witness has M = T+1 realizers; M_A case-A (or case-B no-alt), M_B case-B alt.
  If M_A ≥ 2, then |S*| ≤ w + ⌊w/(M_A - 1)⌋.
  Goal: empirically check if M_B is bounded across witnesses.

If M_B is always small (e.g., ≤ D/6 for c=3), case-A bound recovers leading-stratum.
"""

from itertools import combinations
import random


def make_evals(L, D, p):
    return [[pow(v, k, p) for k in range(D)] for v in L]


def mat_rank(M, p):
    M = [row[:] for row in M]
    rows = len(M)
    if rows == 0:
        return 0
    cols = len(M[0])
    rk = 0
    col = 0
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
                for c in range(cols):
                    M[r][c] = (M[r][c] - factor * M[rk][c]) % p
        rk += 1
        col += 1
    return rk


def find_all_realizers(s1, s2, n, w, D, p, evals):
    """For each γ ∈ F_p*, find ALL E ⊂ [n] of size w with x_γ ∈ V_E.
    Returns dict γ -> list of E supports."""
    realizers = {}
    for gamma in range(1, p):
        x_gamma = [(s1[k] + gamma * s2[k]) % p for k in range(D)]
        E_list = []
        for E_idx in combinations(range(n), w):
            mat_E = [evals[i][:] for i in E_idx]
            mat_E_x = mat_E + [x_gamma[:]]
            r1 = mat_rank(mat_E, p)
            r2 = mat_rank(mat_E_x, p)
            if r2 == r1:
                E_list.append(E_idx)
        if E_list:
            realizers[gamma] = E_list
    return realizers


def joint_vandermonde_support(s1, s2, n, D, p, evals):
    for size in range(0, D + 1):
        for S_idx in combinations(range(n), size):
            mat = [evals[i][:] for i in S_idx]
            r1 = mat_rank(mat, p)
            mat_s1 = mat + [s1[:]]
            mat_s12 = mat_s1 + [s2[:]]
            if mat_rank(mat_s1, p) == r1 and mat_rank(mat_s12, p) == r1:
                return list(S_idx)
    return None


def s_star_basis_coords(s1, s2, S, evals, D, p):
    if not S:
        return [], []
    A = [[evals[i][k] for i in S] for k in range(D)]
    return solve_linear(A, s1, p), solve_linear(A, s2, p)


def solve_linear(A, b, p):
    rows = len(A)
    if rows == 0:
        return []
    cols = len(A[0])
    M = [A[r][:] + [b[r]] for r in range(rows)]
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
    x = [0] * cols
    for i, c in enumerate(pivots):
        x[c] = (M[i][cols] * pow(M[i][c], p - 2, p)) % p
    return x


def classify_realizer(E_idx, S_star, alpha_s, beta_s, gamma, p, w):
    """
    Returns ('A', 'B-no-alt', 'B-alt')
    A: |E ∪ S*| ≤ D ⟹ T_γ ⊂ E
    B-no-alt: case B but T_γ = E (rare?)
    B-alt: case B with T_γ ≠ E (the gap-causing case)
    """
    # T_γ in S*-coords
    T_gamma_local = [j for j in range(len(S_star)) if (alpha_s[j] + gamma * beta_s[j]) % p != 0]
    T_gamma_pts = set(S_star[j] for j in T_gamma_local)
    E_pts = set(E_idx)
    union_size = len(E_pts | set(S_star))
    # D from caller; use heuristic: case-A if union ≤ D
    return T_gamma_pts, union_size, len(T_gamma_local)


def run_witness_sweep(n, c, p, n_trials=30, seed=42, S_size_offset=0):
    random.seed(seed)
    D = 2 * c + 1
    w = D - c  # = c + 1
    T = (2 * D - 1) // c

    L = list(range(1, n + 1))
    evals = make_evals(L, D, p)

    print(f"=== n={n}, c={c}, p={p}, D={D}, w={w}, T={T}, S_size={w+1+S_size_offset} ===")

    n_witnesses = 0
    M_B_distribution = []
    M_A_distribution = []
    S_star_sizes = []
    bound_violations = []

    for trial in range(n_trials):
        S_size = w + 1 + S_size_offset
        if S_size > n:
            continue
        S = random.sample(range(n), S_size)
        alpha = [random.randint(1, p - 1) for _ in range(S_size)]
        beta = [random.randint(1, p - 1) for _ in range(S_size)]
        s1 = [0] * D
        s2 = [0] * D
        for j, v_idx in enumerate(S):
            for k in range(D):
                s1[k] = (s1[k] + alpha[j] * evals[v_idx][k]) % p
                s2[k] = (s2[k] + beta[j] * evals[v_idx][k]) % p

        realizers = find_all_realizers(s1, s2, n, w, D, p, evals)
        M_total = sum(len(El) for El in realizers.values())
        M_distinct_gamma = len(realizers)
        if M_distinct_gamma <= T:
            continue

        n_witnesses += 1
        S_star = joint_vandermonde_support(s1, s2, n, D, p, evals)
        if S_star is None:
            continue
        alpha_s, beta_s = s_star_basis_coords(s1, s2, S_star, evals, D, p)

        M_A = 0
        M_B_no_alt = 0
        M_B_alt = 0
        for gamma, E_list in realizers.items():
            for E_idx in E_list:
                T_gamma_pts, union_size, T_size = classify_realizer(
                    E_idx, S_star, alpha_s, beta_s, gamma, p, w
                )
                if union_size <= D:
                    M_A += 1
                else:
                    if T_size > w:
                        M_B_alt += 1
                    else:
                        M_B_no_alt += 1

        S_star_sizes.append(len(S_star))
        M_A_distribution.append(M_A + M_B_no_alt)  # both contribute to "case-A bound" effectively
        M_B_distribution.append(M_B_alt)

        # Verify Lemma 2 bound
        M_A_eff = M_A + M_B_no_alt
        if M_A_eff >= 2:
            bound = w + w // (M_A_eff - 1)
            if len(S_star) > bound:
                bound_violations.append((trial, len(S_star), bound, M_A_eff, M_B_alt))

    print(f"  Witnesses found: {n_witnesses}")
    if S_star_sizes:
        print(f"  |S*| distribution: min={min(S_star_sizes)}, max={max(S_star_sizes)}, "
              f"mean={sum(S_star_sizes)/len(S_star_sizes):.1f}")
        print(f"  M_A_eff (case-A + B-no-alt): min={min(M_A_distribution)}, max={max(M_A_distribution)}")
        print(f"  M_B_alt: min={min(M_B_distribution)}, max={max(M_B_distribution)}, "
              f"mean={sum(M_B_distribution)/len(M_B_distribution):.2f}")
        print(f"  Lemma 2 bound violations: {len(bound_violations)}")
        if bound_violations:
            print(f"    Examples: {bound_violations[:3]}")
    print()


if __name__ == "__main__":
    for n, c, p in [(8, 3, 17), (10, 3, 41), (12, 3, 41), (14, 3, 61)]:
        run_witness_sweep(n, c, p, n_trials=30)
