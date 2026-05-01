"""Cycle 3: verify parity-aligned 3-pos sparse construction at (16, 4, c=4).

Theoretical claim: at (n, k, c) = (16, 4, 4) (D=12, w=8, T=5):
- Q_E = z^8 - 1 (E = even positions in [16]) has 4 normal directions.
- For x ∈ F_q^D=F_q^12, the V_E orthogonality conditions are
    x[j] - x[j+8] = 0 for j=0,1,2,3.
- For ev_v with v even: ev_v[j+8] = ω^{(j+8)v} = ω^{jv}·ω^{8v} = ω^{jv}·1 = ev_v[j]. ✓
- So ev_v ∈ V_E for v even.
- Similarly ω^{8v} = -1 for v odd, so ev_v ∉ V_{even} but ev_v ∈ V_{odd}.

Therefore: any (s_1, s_2) with both supported on EVEN positions has
x_α = s_1+α s_2 ∈ V_E for E = even positions, all α. K(s_1, s_2) = q-1 (or q
if α=0 also works).

Same for odd-supported.

But: paper2 K10 doesn't apply because (16, 4, c=4) has δ = w/n = 1/2 = J/n,
NOT strictly above-J. Above-J means δ > 1 - √ρ = 1/2. So this construction
is at Johnson boundary, outside paper2 K10's scope.

For paper3, this is a structural finding: at (16, 4, c=4) Johnson-boundary,
sparse 3-pos pairs can saturate K = q-1 via parity alignment, reaching paper3
V_bad sub-leading stratum (|S*| = 8 < w+1 = 9).

This script verifies the construction empirically.

Cell: (n=16, k=4, c=4), F_p with 16 | (p-1). Test at p=17, 97, 113, 193.
"""

import sys

def primitive_root_of_unity(p, n):
    """Find a primitive n-th root of unity in F_p."""
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        # Test if g has order n
        if pow(g, n, p) == 1 and all(pow(g, n // q, p) != 1 for q in [2, 3, 5, 7] if n % q == 0):
            return g
    return None


def evaluate_syndrome(supp_coeffs, p, omega, D):
    """Compute syndrome s ∈ F_p^D given support-coefficient pairs.

    s = sum_v ξ_v · ev_v, where ev_v = (1, ω^v, ..., ω^{(D-1)v}).
    """
    s = [0] * D
    for v, xi in supp_coeffs:
        for j in range(D):
            s[j] = (s[j] + xi * pow(omega, j * v, p)) % p
    return s


def syndrome_in_VE(s, E, p, omega, D):
    """Test if s ∈ V_E = span{ev_v : v ∈ E}.

    Equivalent: s is in the F_p-row-span of the |E| × D Vandermonde matrix
    M[i][j] = ω^{j v_i} for v_i ∈ E.

    Test via rank: rank(M) = rank(M with s appended).
    """
    rows = [[pow(omega, j * v, p) for j in range(D)] for v in E]
    rows_aug = [list(row) for row in rows] + [list(s)]

    def rank(matrix):
        # Row-reduce over F_p.
        m = [list(r) for r in matrix]
        nrows = len(m)
        ncols = len(m[0]) if nrows else 0
        r = 0
        for c in range(ncols):
            piv = None
            for i in range(r, nrows):
                if m[i][c] % p != 0:
                    piv = i
                    break
            if piv is None:
                continue
            m[r], m[piv] = m[piv], m[r]
            inv = pow(m[r][c], p - 2, p)
            m[r] = [(x * inv) % p for x in m[r]]
            for i in range(nrows):
                if i != r and m[i][c] % p != 0:
                    factor = m[i][c]
                    m[i] = [(m[i][j] - factor * m[r][j]) % p for j in range(ncols)]
            r += 1
            if r == nrows:
                break
        return r

    return rank(rows) == rank(rows_aug)


def compute_M(s1, s2, w, p, omega, n, D):
    """Compute M(s1, s2) = #{γ ∈ F_p^* : ∃ E ⊂ [n], |E|=w, s1 + γ·s2 ∈ V_E}.

    Brute force: for each γ, search all C(n, w) subsets E for membership.
    For (n, w) = (16, 8): C(16, 8) = 12,870. Manageable for verification.
    """
    from itertools import combinations
    M = 0
    for gamma in range(1, p):
        x_gamma = [(s1[j] + gamma * s2[j]) % p for j in range(D)]
        # Skip x_gamma = 0 (would be vacuous realizer; per paper3 §sec:setup
        # convention, ξ ≠ 0 required, so x_gamma = 0 has no realizer).
        if all(c == 0 for c in x_gamma):
            continue
        # Search for E with x_gamma ∈ V_E.
        found = False
        for E in combinations(range(n), w):
            if syndrome_in_VE(x_gamma, E, p, omega, D):
                found = True
                break
        if found:
            M += 1
    return M


def test_parity_construction(p):
    n = 16
    k = 4
    D = n - k  # 12
    w = D - 4  # = 8 for c=4
    T = (2 * D - 1) // 4  # 5

    omega = primitive_root_of_unity(p, n)
    if omega is None:
        print(f"  p={p}: no primitive {n}-th root, skipping.")
        return None

    # Pick s1 supported on 3 ODD positions in [k, n-1] = [4, 15].
    # Odd positions in [4, 15]: {5, 7, 9, 11, 13, 15}.
    odd_positions = [5, 7, 9, 11, 13, 15]
    s1_supp = [(odd_positions[0], 1), (odd_positions[1], 2), (odd_positions[2], 3)]
    s2_supp = [(odd_positions[3], 5), (odd_positions[4], 7), (odd_positions[5], 11)]

    s1 = evaluate_syndrome(s1_supp, p, omega, D)
    s2 = evaluate_syndrome(s2_supp, p, omega, D)

    # Verify: s1, s2 satisfy parity orthogonality s_i[j] + s_i[j+8] = 0 for j=0..3
    # Wait — for ODD support, s_i[j+8] = -s_i[j], so s_i[j] + s_i[j+8] = 0.
    # So orthogonality with z^8 + 1 (E = odd positions).
    for j in range(4):
        for s, name in [(s1, "s1"), (s2, "s2")]:
            r = (s[j] + s[j + 8]) % p
            assert r == 0, f"Parity check failed: {name}[{j}] + {name}[{j+8}] = {r} mod {p}"

    # Now compute M(s1, s2). Expected: q-1 (since x_α ∈ V_{odd} for all α).
    M = compute_M(s1, s2, w, p, omega, n, D)
    expected_min = p - 2  # Allow for at most one γ with x_γ = 0.

    print(f"  p={p}: M(s1,s2) = {M}, expected ≥ {expected_min} (q-1={p-1}); T={T}; {'PASS' if M >= expected_min else 'FAIL'}")
    return M


def main():
    print(f"Cell: (n=16, k=4, c=4, w=8, T=5)")
    print(f"Construction: s1, s2 each 3-pos with all support on odd positions in [4,15].")
    print(f"Theoretical: M = q-1 (saturation via parity alignment).")
    print()

    primes = [17, 97, 113, 193]
    results = {}
    for p in primes:
        results[p] = test_parity_construction(p)

    print()
    all_pass = all(r is None or r >= p - 2 for p, r in results.items())
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
