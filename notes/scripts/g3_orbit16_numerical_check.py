"""Numerical check: for each orbit-16 irreducible (a, b) at (n, k) = (16, 4),
enumerate ρ ∈ F_q* and check dist(h_ρ, RS_4(L_16)) ≤ 8 (Johnson radius).

If any ρ found with this property: |B| ≥ orbit_size = 16, breaking K ≤ 8.
If NO ρ across all (a, b): empirically |B| = 0 for all orbit-16, K ≤ 8 stands.

Test over multiple primes q where 16 | q-1: q ∈ {17, 97, 193, 241, ...}
"""
from math import gcd as ggcd
import itertools


def find_root_of_unity(q, n):
    """Find primitive n-th root of unity in F_q*."""
    if (q - 1) % n != 0:
        return None
    g = 2
    while True:
        if pow(g, n, q) == 1 and all(pow(g, n // p, q) != 1 for p in [2, 3, 5] if n % p == 0):
            return g
        g += 1
        if g >= q:
            return None


def lagrange_interp_modq(L, k, q):
    """Build interpolation matrix M: F_q^k → F_q^n via M_{i,j} = L_i^j for j in [0, k)."""
    n = len(L)
    M = [[pow(L[i], j, q) for j in range(k)] for i in range(n)]
    return M


def gauss_solve_F_q(M_with_rhs, q):
    """Gaussian elimination on M (n x (k+1)). Return solution if consistent,
    or None if inconsistent."""
    rows = [list(r) for r in M_with_rhs]
    n_rows = len(rows)
    n_cols = len(rows[0]) - 1  # last col is rhs
    pivot_col = 0
    pivot_row = 0
    for c in range(n_cols):
        if pivot_row >= n_rows:
            break
        # find pivot
        p = pivot_row
        while p < n_rows and rows[p][c] % q == 0:
            p += 1
        if p == n_rows:
            continue
        rows[pivot_row], rows[p] = rows[p], rows[pivot_row]
        inv = pow(rows[pivot_row][c], -1, q)
        rows[pivot_row] = [(x * inv) % q for x in rows[pivot_row]]
        for r in range(n_rows):
            if r != pivot_row and rows[r][c] % q != 0:
                f = rows[r][c]
                rows[r] = [(rows[r][i] - f * rows[pivot_row][i]) % q for i in range(n_cols + 1)]
        pivot_row += 1
    # Check consistency: rows where all M cols zero but rhs nonzero
    for r in range(pivot_row, n_rows):
        if rows[r][-1] % q != 0:
            return None
    # Solution exists. Read off (we don't need actual coefs, just consistency).
    return True


def dist_to_RS_k(values, L, k, q, max_J):
    """For values on L, return dist ≤ max_J? (yes if any subset of size n - max_J
    has values consistent with degree-< k polynomial.

    Brute force: try all C(n, n - max_J) = C(n, max_J)-many subsets.
    For n = 16, max_J = 8: C(16, 8) = 12870. Per subset ~k^3 = 64 ops. Per ρ ~10^6 ops.
    For 16-prime, q ~ 17, total q * cases ~ 17 * 12870 * 64 ≈ 14M ops, fast.
    """
    n = len(values)
    target_size = n - max_J  # = 8
    M_full = lagrange_interp_modq(L, k, q)
    for S in itertools.combinations(range(n), target_size):
        M_sub = [list(M_full[i]) + [values[i]] for i in S]
        sol = gauss_solve_F_q(M_sub, q)
        if sol is not None:
            return True
    return False


def count_bad_rho(n, k, a, b, q):
    """Count ρ ∈ F_q* with dist(h_ρ, RS_k) ≤ J on L_n."""
    omega = find_root_of_unity(q, n)
    if omega is None:
        return None
    L = [pow(omega, i, q) for i in range(n)]
    J = n - n * k // n  # n - sqrt(k * n) for at-Johnson; for FRI rate 1/4, J = n/2 = 8.
    # at (n=16, k=4): J = 16 - sqrt(4 * 16) = 16 - 8 = 8.
    J = n // 2  # n - sqrt(k*n) at rate 1/4 gives n/2.
    bad = 0
    for rho in range(1, q):
        h_vals = [(rho * pow(L[i], a, q) + pow(L[i], b, q)) % q for i in range(n)]
        if dist_to_RS_k(h_vals, L, k, q, J):
            bad += 1
    return bad


def main():
    n, k = 16, 4
    cases = []
    for a in range(k, n - 1):
        for b in range(a + 1, n):
            if (b - a) % 2 == 1 and ggcd(ggcd(a, b), n) == 1:
                cases.append((a, b))

    primes = [17, 97]
    for q in primes:
        omega = find_root_of_unity(q, n)
        if omega is None:
            print(f"q = {q}: no primitive {n}-th root, skip.")
            continue
        print(f"\n=== q = {q}, ω = {omega} (primitive {n}-th root of 1) ===")
        for a, b in cases:
            bad = count_bad_rho(n, k, a, b, q)
            marker = ""
            if bad is not None and bad > 0:
                marker = f"  <<< |B| = {bad}"
            print(f"  ({a:>2},{b:>2}): |B| = {bad}{marker}", flush=True)


if __name__ == "__main__":
    main()
