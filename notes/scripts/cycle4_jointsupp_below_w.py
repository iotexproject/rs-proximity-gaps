"""Cycle 4: verify the structural observation that |S*| ≤ w → M = q-1.

Theoretical claim:
For any (s_1, s_2) ∈ F_q^{2D} with joint Vandermonde support
|S*(s_1, s_2)| ≤ w, the realizer count M(s_1, s_2) = q - 1 (or q if
α=0 also has a non-trivial realizer; but per paper3 §sec:setup ξ ≠ 0
convention, x_α = 0 has no realizer, so M ≤ q - 1).

Reason: x_α = s_1 + α s_2 ∈ V_{S*}. For E ⊇ S* with |E| = w,
V_{S*} ⊆ V_E. So x_α ∈ V_E. The realizer (E, ξ) has ξ supported on
S* ⊆ E with non-trivial coefficients (whenever x_α ≠ 0). Hence M
counts every α with x_α ≠ 0, i.e., q - 1 (excluding the unique α
with x_α = 0 if s_2 ≠ 0).

This is a structural observation about V_bad: V_bad ⊇ {(s_1, s_2) :
|S*(s_1, s_2)| ≤ w} for any T ≥ 1 deployment. In particular, the
SPARSE-PAIR sub-locus (joint Vandermonde support ≤ const) is
TRIVIALLY in V_bad at deployment scale where w → ∞.

This implies paper3's V_bad has a TRIVIAL sub-locus structure that is
independent of the leading codim-2(c-1) analysis. The leading
analysis is for |S*| = w+1 (just-above-trivial-saturation regime).

Note: this does NOT contradict paper2 K10 because paper2's K(f)
counts CURVE traversals of V_bad, not point-membership. Sparse f's
curves don't extensively pass through the trivial sub-locus.

This script empirically verifies M = q-1 at multiple (n, k, c)
cells with controlled |S*|.
"""

from itertools import combinations


def primitive_root_of_unity(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        if pow(g, n, p) == 1 and all(pow(g, n // q, p) != 1 for q in [2, 3, 5, 7] if n % q == 0):
            return g
    return None


def evaluate_syndrome(supp_coeffs, p, omega, D):
    s = [0] * D
    for v, xi in supp_coeffs:
        for j in range(D):
            s[j] = (s[j] + xi * pow(omega, j * v, p)) % p
    return s


def matrix_rank(M, p):
    if not M or not M[0]:
        return 0
    A = [list(row) for row in M]
    rows, cols = len(A), len(A[0])
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        piv = None
        for i in range(r, rows):
            if A[i][c] % p != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] % p != 0:
                factor = A[i][c]
                A[i] = [(A[i][j] - factor * A[r][j]) % p for j in range(cols)]
        r += 1
    return r


def syndrome_in_VE(s, E, p, omega, D):
    rows = [[pow(omega, j * v, p) for j in range(D)] for v in E]
    rank_M = matrix_rank(rows, p)
    rank_aug = matrix_rank(rows + [list(s)], p)
    return rank_M == rank_aug


def compute_M(s1, s2, w, p, omega, n, D, max_subsets=None):
    """Brute-force M. Returns count of γ ∈ F_p^* with x_γ ∈ V_E for some |E|=w.

    For verification, we also accept early termination once we find one E for x_γ.
    max_subsets: limit on # subsets to check (None = exhaustive C(n,w)).
    """
    M = 0
    for gamma in range(1, p):
        x_gamma = [(s1[j] + gamma * s2[j]) % p for j in range(D)]
        if all(c == 0 for c in x_gamma):
            continue
        found = False
        count = 0
        for E in combinations(range(n), w):
            if syndrome_in_VE(x_gamma, E, p, omega, D):
                found = True
                break
            count += 1
            if max_subsets and count >= max_subsets:
                break
        if found:
            M += 1
    return M


def test_cell(p, n, k, c, supp1, supp2, max_subsets=None):
    """Test one cell with given (s_1, s_2) supports.

    Verify: |S*| = |supp1 ∪ supp2| ≤ w → M = q-1 (saturated).
    """
    D = n - k
    w = D - c
    T = (2 * D - 1) // c

    omega = primitive_root_of_unity(p, n)
    if omega is None:
        return None, "no_primitive_root"

    # Joint support
    joint = sorted(set(supp1) | set(supp2))
    if len(joint) > w:
        return None, f"|S*|={len(joint)} > w={w}, skipping"

    # Build (s1, s2)
    coeffs1 = [(v, i + 1) for i, v in enumerate(supp1)]
    coeffs2 = [(v, (i + 1) * 7) for i, v in enumerate(supp2)]
    s1 = evaluate_syndrome(coeffs1, p, omega, D)
    s2 = evaluate_syndrome(coeffs2, p, omega, D)

    M = compute_M(s1, s2, w, p, omega, n, D, max_subsets=max_subsets)
    expected = p - 1  # q - 1 (excluding α=0 case)
    # Allow off-by-one for α with x_α = 0
    return M, "PASS" if M >= expected - 1 else f"FAIL (M={M} < {expected-1})"


def main():
    cells = [
        # (p, n, k, c, supp1, supp2, max_subsets)
        # (16, 4, c=3): w=9, supp ⊆ [4, 15]. Joint ≤ 9.
        (17,   16, 4, 3, [4, 5, 6], [7, 8, 9], None),
        (97,   16, 4, 3, [4, 5, 6], [7, 8, 9], None),
        # Joint = 6, ≤ w=9, expect M = q-1.
        # (16, 4, c=2): w=10, supp ⊆ [4, 15]. Joint ≤ 10.
        (17,   16, 4, 2, [4, 5, 6, 7], [8, 9, 10, 11], None),
        # Joint = 8, ≤ w=10, expect M = q-1.
        # (16, 4, c=4): w=8, supp ⊆ [4, 15]. Joint ≤ 8.
        (17,   16, 4, 4, [4, 5, 6, 7], [8, 9, 10, 11], None),
        # Joint = 8, = w=8 (boundary, trivial).
        # (12, 3, c=3): w=6, supp ⊆ [3, 11]. Joint ≤ 6.
        (13,   12, 3, 3, [3, 4, 5], [6, 7, 8], None),
        # Joint = 6, = w=6 (boundary).
    ]

    print(f"Verifying |S*| ≤ w ⇒ M = q-1 (saturated) across multiple cells:")
    print(f"{'p':>4} {'(n,k,c)':>10} {'w':>3} {'T':>4} {'|S*|':>5} {'M':>4} {'q-1':>5} {'status':>10}")

    for cfg in cells:
        p, n, k, c, supp1, supp2, ms = cfg
        D = n - k
        w = D - c
        T = (2 * D - 1) // c
        joint_size = len(set(supp1) | set(supp2))
        M, status = test_cell(p, n, k, c, supp1, supp2, max_subsets=ms)
        if M is None:
            print(f"{p:>4} ({n},{k},{c}): SKIP ({status})")
            continue
        print(f"{p:>4} ({n:>2},{k},{c:>2}) {w:>4} {T:>4} {joint_size:>5} {M:>4} {p-1:>5}   {status}")


if __name__ == "__main__":
    main()
