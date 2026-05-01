"""g3_3mono_timeout_numerical.py — numerical resolution of the 2
self-reflective TIMEOUT cases at (8, 2): (2, 3, 6) and (2, 5, 6).

For each (a, b, c), iterate (ρ, α) ∈ F_q² and check if pencil
h(α, ρ)(z) = z^a + ρ z^b + α z^c is bad on L_8 (dist ≤ J(L_8) = 4).

|B(α | ρ)| := #{α ∈ F_q : pencil bad} per generic ρ.

Output: max |B| across ρ.
"""
import itertools


def find_root_of_unity(q, n):
    if (q - 1) % n != 0:
        return None
    g = 2
    while True:
        if pow(g, n, q) == 1 and all(pow(g, n // p, q) != 1 for p in [2, 3, 5] if n % p == 0):
            return g
        g += 1
        if g >= q:
            return None


def gauss_consistent(M_with_rhs, q):
    rows = [list(r) for r in M_with_rhs]
    n_rows = len(rows)
    n_cols = len(rows[0]) - 1
    pivot_row = 0
    for c in range(n_cols):
        if pivot_row >= n_rows:
            break
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
    for r in range(pivot_row, n_rows):
        if rows[r][-1] % q != 0:
            return False
    return True


def dist_le_J(values, L, k, q, J):
    n = len(values)
    target = n - J
    M_full = [[pow(L[i], j, q) for j in range(k)] for i in range(n)]
    for S in itertools.combinations(range(n), target):
        M_sub = [list(M_full[i]) + [values[i]] for i in S]
        if gauss_consistent(M_sub, q):
            return True
    return False


def count_bad_alpha(n, k, a, b, c, q, rho_val):
    omega = find_root_of_unity(q, n)
    L = [pow(omega, i, q) for i in range(n)]
    J = n // 2  # FRI rate 1/4
    bad = 0
    for alpha in range(q):
        h = [(pow(L[i], a, q) + rho_val * pow(L[i], b, q) + alpha * pow(L[i], c, q)) % q for i in range(n)]
        if dist_le_J(h, L, k, q, J):
            bad += 1
    return bad


def main():
    n, k = 8, 2
    print(f"=== (n, k) = ({n}, {k}), TIMEOUT case resolution ===")
    for q in [97]:
        print(f"\nq = {q}:")
        for a, b, c in [(2, 3, 6), (2, 5, 6)]:
            max_bad = 0
            argmax_rho = None
            print(f"\n  ({a}, {b}, {c}):")
            # sweep rho over a few values to get max |B(α)|
            rho_samples = list(range(min(20, q)))
            for rho_val in rho_samples:
                bad = count_bad_alpha(n, k, a, b, c, q, rho_val)
                if bad > max_bad:
                    max_bad = bad
                    argmax_rho = rho_val
                if bad > 0:
                    print(f"    ρ = {rho_val}: |B(α)| = {bad}")
            print(f"    >>> max |B(α)| = {max_bad} at ρ = {argmax_rho}")


if __name__ == "__main__":
    main()
