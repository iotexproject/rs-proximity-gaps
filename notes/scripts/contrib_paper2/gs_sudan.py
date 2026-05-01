"""Sudan GS list-decoder for plain RS over multiplicative subgroup.

Multiplicity m=1, list size L bounded by floor(d / (k-1)) where d is the
smallest weighted-degree with #monomials > n.

For (16, 4): d=8, τ=7, L=2. Reaches above unique radius (6) but below
Johnson (8).

For (32, 8): d=17, τ=14, L=2. Below Johnson (16) but above unique (12).

Algorithm:
  1. Build Q(X, Y) of (1, k-1)-weighted degree ≤ d with Q(x_i, r_i) = 0 for
     each (x_i, r_i). Linear system: # unknowns > n constraints.
  2. Roth-Ruckenstein: find all polynomial roots f(X) ∈ F[X] of degree < k
     such that Q(X, f(X)) = 0 in F[X]. These are candidate codewords at
     Hamming distance ≤ τ from received.
"""
from __future__ import annotations

from typing import Dict, List


def gf_inv(a, p):
    return pow(a % p, p - 2, p)


def poly_eval(coeffs, x, p):
    r = 0
    for c in reversed(coeffs):
        r = (r * x + c) % p
    return r


def poly_add(a, b, p):
    n = max(len(a), len(b))
    return [( (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) ) % p
            for i in range(n)]


def poly_sub(a, b, p):
    n = max(len(a), len(b))
    return [( (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) ) % p
            for i in range(n)]


def poly_mul(a, b, p):
    if not a or not b:
        return [0]
    c = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            c[i + j] = (c[i + j] + ai * bj) % p
    return c


def poly_strip(a):
    while len(a) > 1 and a[-1] == 0:
        a = a[:-1]
    return a


def poly_divmod(a, b, p):
    """a = q*b + r."""
    a = list(a)
    db = len(b) - 1
    while db >= 0 and b[db] == 0:
        db -= 1
    if db < 0:
        raise ZeroDivisionError
    inv_lead = gf_inv(b[db], p)
    q = [0] * max(1, len(a) - db)
    while True:
        a = poly_strip(a)
        da = len(a) - 1
        if a == [0] or da < db:
            break
        shift = da - db
        coef = (a[da] * inv_lead) % p
        q[shift] = (q[shift] + coef) % p
        for j in range(db + 1):
            a[shift + j] = (a[shift + j] - coef * b[j]) % p
    return q, a


def gauss_solve_mod(M, b, p):
    """Solve M @ x = b mod p. Returns particular solution (free vars = 0)
    or None if inconsistent."""
    rows = len(M)
    cols = len(M[0]) if rows else 0
    A = [list(row) + [bv] for row, bv in zip(M, b)]
    r = 0
    pivot_col = []
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
        inv = gf_inv(A[r][c], p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] % p != 0:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(cols + 1)]
        pivot_col.append(c)
        r += 1
    for i in range(r, rows):
        if A[i][cols] % p != 0:
            return None
    sol = [0] * cols
    for ridx, c in enumerate(pivot_col):
        sol[c] = A[ridx][cols] % p
    return sol


def gauss_kernel_mod(M, p):
    """Find a non-trivial element of the kernel of M mod p (or None if empty)."""
    rows = len(M)
    cols = len(M[0]) if rows else 0
    A = [list(row) for row in M]
    r = 0
    pivot_col = []
    pivot_row = []
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
        inv = gf_inv(A[r][c], p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] % p != 0:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(cols)]
        pivot_col.append(c)
        pivot_row.append(r)
        r += 1
    if r == cols:
        return None  # full rank
    free_cols = [c for c in range(cols) if c not in pivot_col]
    if not free_cols:
        return None
    free_c = free_cols[0]
    sol = [0] * cols
    sol[free_c] = 1
    for ridx, c in enumerate(pivot_col):
        sol[c] = (- A[ridx][free_c]) % p
    return sol


# ---------------------------------------------------------------------------
# (1, k-1)-weighted-degree monomial enumeration
# ---------------------------------------------------------------------------

def monomials_weighted(d, k):
    """List all (i, j) with i + (k-1)*j ≤ d."""
    out = []
    j = 0
    while (k - 1) * j <= d:
        max_i = d - (k - 1) * j
        for i in range(max_i + 1):
            out.append((i, j))
        j += 1
    return out


def find_d_for_n(n, k):
    """Smallest d with #weighted monomials > n."""
    d = 0
    while True:
        if len(monomials_weighted(d, k)) > n:
            return d
        d += 1


# ---------------------------------------------------------------------------
# Sudan interpolation (m=1)
# ---------------------------------------------------------------------------

def sudan_interpolate(p, n, k, points, d=None):
    """Build Q(X, Y) of (1, k-1)-weighted degree ≤ d s.t. Q(x_i, y_i) = 0 ∀i.

    Returns Q as dict {(i, j): coef} (monomials i in X, j in Y).
    """
    if d is None:
        d = find_d_for_n(n, k)
    monos = monomials_weighted(d, k)  # list of (i, j)
    # Build constraint matrix: row per (x_i, y_i), col per monomial.
    M = []
    for (xi, yi) in points:
        row = []
        for (a, b) in monos:
            row.append((pow(xi, a, p) * pow(yi, b, p)) % p)
        M.append(row)
    # Find non-trivial kernel element.
    sol = gauss_kernel_mod(M, p)
    if sol is None:
        return None, monos
    Q = {monos[i]: sol[i] for i in range(len(monos)) if sol[i] != 0}
    return Q, monos


# ---------------------------------------------------------------------------
# Roth-Ruckenstein factorization
# ---------------------------------------------------------------------------

def Q_eval_X_Y(Q, x, y, p):
    """Evaluate Q at (x, y)."""
    r = 0
    for (a, b), c in Q.items():
        r = (r + c * pow(x, a, p) * pow(y, b, p)) % p
    return r


def Q_at_X_zero_Y(Q, p):
    """Q(0, Y) — extract coefs for X^0."""
    coeffs = {}
    for (a, b), c in Q.items():
        if a == 0:
            coeffs[b] = c
    if not coeffs:
        return [0]
    max_b = max(coeffs.keys())
    return [coeffs.get(j, 0) % p for j in range(max_b + 1)]


def find_roots_in_Fp(coeffs, p):
    """Find all roots in F_p of a polynomial over F_p (brute-force, ok for small p)."""
    return [x for x in range(p) if poly_eval(coeffs, x, p) == 0]


def shift_Q(Q, root, p):
    """Substitute Y = X*Y' + root in Q. Returns new Q'(X, Y') with degrees
    shifted appropriately. Then divide by smallest power of X (= valuation of
    Q'(X, 0))."""
    # Q(X, X*Y' + root) = sum_{a, b} c · X^a · (X*Y' + root)^b
    new_Q = {}
    from math import comb
    for (a, b), c in Q.items():
        # (X*Y' + root)^b expansion
        for t in range(b + 1):
            coef = (c * comb(b, t) * pow(root, b - t, p)) % p
            if coef == 0:
                continue
            new_a = a + t  # X^t from (XY')^t
            new_b = t      # Y'^t
            new_Q[(new_a, new_b)] = (new_Q.get((new_a, new_b), 0) + coef) % p
    # Strip zeros
    new_Q = {k: v for k, v in new_Q.items() if v != 0}
    # Find min X-degree (valuation in X)
    if not new_Q:
        return new_Q
    min_a = min(a for (a, b) in new_Q)
    if min_a > 0:
        new_Q = {(a - min_a, b): c for (a, b), c in new_Q.items()}
    return new_Q


def roth_ruckenstein(Q, p, k, prefix=None, depth=0):
    """Find all f(X) of degree < k with Q(X, f(X)) = 0 in F[X].

    Recursive: try each root of Q(0, Y), shift, recurse.
    """
    if prefix is None:
        prefix = []
    if depth >= k:
        return [list(prefix)]
    Q0 = Q_at_X_zero_Y(Q, p)
    roots = find_roots_in_Fp(Q0, p)
    out = []
    for root in roots:
        new_Q = shift_Q(Q, root, p)
        new_prefix = prefix + [root]
        if not new_Q:
            # Q became 0 — any continuation works; just pad with zeros.
            for j in range(depth + 1, k):
                new_prefix.append(0)
            out.append(list(new_prefix))
            continue
        sub = roth_ruckenstein(new_Q, p, k, new_prefix, depth + 1)
        out.extend(sub)
    return out


def gs_decode(p, omega, n, k, received, d=None):
    """Sudan GS decode.

    Returns list of message coefficient vectors f = (f_0, ..., f_{k-1}).
    """
    points = [(pow(omega, j, p), received[j]) for j in range(n)]
    Q, monos = sudan_interpolate(p, n, k, points, d=d)
    if Q is None:
        return []
    return roth_ruckenstein(Q, p, k)


# ---------------------------------------------------------------------------
# Self-test on (16, 4) RS
# ---------------------------------------------------------------------------

def primitive_root_of_unity(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        if pow(g, n, p) == 1:
            ok = True
            for q in range(2, n + 1):
                if n % q == 0 and pow(g, n // q, p) == 1:
                    ok = False
                    break
            if ok:
                return g
    return None


def encode_rs(p, omega, n, k, msg):
    return [poly_eval(list(msg), pow(omega, j, p), p) for j in range(n)]


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def self_test():
    import random
    p, n, k = 17, 16, 4
    omega = primitive_root_of_unity(p, n)
    print(f"Self-test: GS Sudan(m=1) on RS({n}, {k}) over GF({p})")
    print(f"  ω = {omega}; d = {find_d_for_n(n, k)}; τ ≤ {n - find_d_for_n(n, k) - 1}")
    msg = [1, 2, 3, 4]
    cw = encode_rs(p, omega, n, k, msg)
    rng = random.Random(7)
    # 7 errors (above unique radius t=6, within Sudan τ=7)
    err_pos = rng.sample(range(n), 7)
    rcvd = list(cw)
    for pos in err_pos:
        rcvd[pos] = (rcvd[pos] + rng.randint(1, p - 1)) % p
    print(f"  encoded message: {msg}")
    print(f"  errors at: {err_pos}")
    decoded = gs_decode(p, omega, n, k, rcvd)
    print(f"  GS decoded list: {decoded}")
    if any(d == msg for d in decoded):
        print("  ✓ message recovered")
    else:
        print("  ✗ message NOT in list")


if __name__ == '__main__':
    self_test()
