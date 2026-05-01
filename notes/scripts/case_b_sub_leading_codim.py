"""
Session 3: validate Note 0132 sub-leading codim bound.

For c=5 (smallest c with sub-leading possible: ⌊w/T⌋ ≥ 2),
sample (s_1, s_2) ∈ V_S × V_S with |S| = w+2 (sub-leading d=1)
and measure V_bad density. Predicted: codim within V_S^2 ≥ 2d = 2.

Equivalently: V_bad density inside V_S × V_S should be ≤ p^{-2}.
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


def count_realizers_distinct_gamma(s1, s2, n, w, D, p, evals):
    """Count distinct γ ∈ F_p* with x_γ ∈ V_E for some |E|=w. Return count."""
    seen = set()
    for gamma in range(1, p):
        x_gamma = [(s1[k] + gamma * s2[k]) % p for k in range(D)]
        for E_idx in combinations(range(n), w):
            mat_E = [evals[i][:] for i in E_idx]
            mat_E_x = mat_E + [x_gamma[:]]
            r1 = mat_rank(mat_E, p)
            r2 = mat_rank(mat_E_x, p)
            if r2 == r1:
                seen.add(gamma)
                break
    return len(seen)


def joint_vandermonde_support_size(s1, s2, n, D, p, evals):
    for size in range(0, D + 1):
        for S_idx in combinations(range(n), size):
            mat = [evals[i][:] for i in S_idx]
            r1 = mat_rank(mat, p)
            mat_s1 = mat + [s1[:]]
            mat_s12 = mat_s1 + [s2[:]]
            if mat_rank(mat_s1, p) == r1 and mat_rank(mat_s12, p) == r1:
                return len(S_idx)
    return None


def run_sub_leading_density(n, c, p, n_trials=200, seed=42, target_d=1):
    random.seed(seed)
    D = 2 * c + 1  # ensure unique-ish decoding setup
    w = D - c
    T = (2 * D - 1) // c
    target_S_size = w + 1 + target_d

    if target_S_size > n:
        return None

    L = list(range(1, n + 1))
    evals = make_evals(L, D, p)

    print(f"=== n={n}, c={c}, p={p}, D={D}, w={w}, T={T}, target |S|={target_S_size} (d={target_d}) ===")

    n_in_V_bad = 0
    n_total_with_correct_S_size = 0
    M_distrib = []

    for trial in range(n_trials):
        S = random.sample(range(n), target_S_size)
        alpha = [random.randint(1, p - 1) for _ in range(target_S_size)]
        beta = [random.randint(1, p - 1) for _ in range(target_S_size)]
        s1 = [0] * D
        s2 = [0] * D
        for j, v_idx in enumerate(S):
            for k in range(D):
                s1[k] = (s1[k] + alpha[j] * evals[v_idx][k]) % p
                s2[k] = (s2[k] + beta[j] * evals[v_idx][k]) % p

        actual_S_size = joint_vandermonde_support_size(s1, s2, n, D, p, evals)
        if actual_S_size != target_S_size:
            continue
        n_total_with_correct_S_size += 1

        M = count_realizers_distinct_gamma(s1, s2, n, w, D, p, evals)
        M_distrib.append(M)
        if M > T:
            n_in_V_bad += 1

    if n_total_with_correct_S_size == 0:
        print(f"  No samples with |S*| = {target_S_size}")
        return

    bad_density = n_in_V_bad / n_total_with_correct_S_size
    predicted_density = 1.0 / (p ** (2 * target_d))  # codim 2d prediction

    print(f"  Samples with |S*|={target_S_size}: {n_total_with_correct_S_size}")
    print(f"  V_bad density: {n_in_V_bad}/{n_total_with_correct_S_size} = {bad_density:.6f}")
    print(f"  Predicted (p^{{-2d}} = p^{{-{2*target_d}}}): {predicted_density:.6f}")
    print(f"  Ratio actual/predicted: {bad_density/predicted_density:.2f} (should be O(1))")
    if M_distrib:
        from collections import Counter
        c2 = Counter(M_distrib)
        print(f"  M distribution: {dict(sorted(c2.items()))}")
    print()


if __name__ == "__main__":
    # c=5 needed for d ≥ 1 to be reachable
    for n, c, p, target_d in [
        (12, 5, 17, 1),
        (12, 5, 41, 1),
        (14, 5, 41, 1),
    ]:
        run_sub_leading_density(n, c, p, n_trials=100, target_d=target_d)
