"""Sudan GS list-decoder at multiplicity m=2 with Hasse-derivative interpolation.

Each (x_i, y_i) gets multiplicity m=2 → 3 constraints per point:
  H^{0,0} Q(x_i, y_i) = 0   (value)
  H^{1,0} Q(x_i, y_i) = 0   (X-derivative)
  H^{0,1} Q(x_i, y_i) = 0   (Y-derivative)
where H^{i,j} Q(x_0, y_0) = sum_{a≥i, b≥j} c_{a,b} · C(a, i) · C(b, j) · x_0^{a-i} · y_0^{b-j}.

For (16, 4) m=2: 3*16=48 constraints, smallest d with #monos>48 is d=15.
Decoding radius τ ≤ d/m = 15/2 = 7.5 ⟹ τ ≤ 7. WAIT — that's same as m=1 τ=7.

Re-checking: with m=2 we need d=15 (vs d=8 at m=1), and τ ≤ d/m. So at m=2 d=15, τ ≤ 7.5 ⟹ 7. Same!

Actually, the GS decoding-radius condition is more nuanced. The condition for the
decoder to succeed: 'sum of multiplicities at agreement points ≤ d', i.e.,
  m · (n - τ) ≤ d.
At m=1 d=8 (16,4): 1·(16-τ) ≤ 8 ⟹ τ ≥ 8 ⟹ decoder works for τ ≥ 8 (Johnson)
                      AND we need #monos > n*1 = 16 (smallest d=8). These are consistent at d=8: τ ≥ 16-8=8.

Hmm earlier I said d=8 τ=7 at m=1 — let me recompute. The condition:
  Q(X, f(X)) ≡ 0 in F[X], where deg Q(X, f(X)) ≤ d (using f of deg < k makes weighted-degree
  contributions add).
  Q(X, f(X)) = 0 ⟺ Q has roots at all agreement points x_i, with multiplicity m at each.
  Total roots (with mult): m·(n - τ).
  Q(X, f(X)) is non-zero polynomial of degree ≤ d, so can't have more than d roots.
  Therefore: m·(n - τ) > d  ⟹  Q(X, f(X)) ≢ 0 ⟹ contradiction.
  Equivalently, Q(X, f(X)) = 0 forces m·(n - τ) ≤ d.
  But for the DECODER to succeed, we need to FORCE Q(X, f(X)) = 0, which requires
  m·(n - τ) > d (so polynomial can't be non-zero).

So: τ < n - d/m ⟹ decoder fails (Q can be nonzero).
    τ > n - d/m ⟹ decoder succeeds (Q must be zero, root extraction works).
At m=2 (16,4) d=15: τ ≥ n - d/m = 16 - 7.5 = 8.5 ⟹ τ = 8 ⟹ ✓ Johnson reachable.
At m=1 (16,4) d=8: τ ≥ 16 - 8 = 8 ⟹ τ = 8 ⟹ Johnson reachable too.

OK so re-examining: Sudan(m=1) at (16,4) DOES reach τ=8 = Johnson. My earlier claim
"τ=n-d-1=7" was WRONG. Let me re-verify with the self-test. Actually my self-test
recovered the message at 7 errors — but it might recover at 8 too. Let me test that.
"""
from __future__ import annotations

from math import comb
from gs_sudan import (
    gauss_kernel_mod, gf_inv,
    poly_eval, monomials_weighted,
)


def find_d_for_n_m(n, k, m):
    """Smallest d with #weighted monomials > n * m(m+1)/2."""
    constraints = n * m * (m + 1) // 2
    d = 0
    while True:
        if len(monomials_weighted(d, k)) > constraints:
            return d
        d += 1


def hasse_constraint(x0, y0, monos, p, i, j):
    """Row of Hasse derivative H^{i,j} Q(x_0, y_0) over monomial basis.

    H^{i,j} Q(x, y) = sum_{a≥i, b≥j} c_{a,b} · C(a,i) · C(b,j) · x^{a-i} · y^{b-j}.
    """
    row = []
    for (a, b) in monos:
        if a < i or b < j:
            row.append(0)
            continue
        coef = (comb(a, i) * comb(b, j)) % p
        coef = (coef * pow(x0, a - i, p) * pow(y0, b - j, p)) % p
        row.append(coef)
    return row


def sudan_interpolate_m2(p, n, k, points, d=None):
    """Build Q(X, Y) of (1, k-1)-weighted degree ≤ d s.t. each (x_i, y_i) is a
    multiplicity-2 zero. Returns Q as dict {(a, b): coef}.
    """
    m = 2
    if d is None:
        d = find_d_for_n_m(n, k, m)
    monos = monomials_weighted(d, k)
    M = []
    for (xi, yi) in points:
        # 3 constraints per point at m=2
        for (i, j) in [(0, 0), (1, 0), (0, 1)]:
            M.append(hasse_constraint(xi, yi, monos, p, i, j))
    sol = gauss_kernel_mod(M, p)
    if sol is None:
        return None, monos
    Q = {monos[i]: sol[i] for i in range(len(monos)) if sol[i] != 0}
    return Q, monos


def Q_at_X_zero_Y(Q, p):
    coeffs = {}
    for (a, b), c in Q.items():
        if a == 0:
            coeffs[b] = c
    if not coeffs:
        return [0]
    max_b = max(coeffs.keys())
    return [coeffs.get(j, 0) % p for j in range(max_b + 1)]


def find_roots_in_Fp(coeffs, p):
    return [x for x in range(p) if poly_eval(coeffs, x, p) == 0]


def shift_Q(Q, root, p):
    new_Q = {}
    for (a, b), c in Q.items():
        for t in range(b + 1):
            coef = (c * comb(b, t) * pow(root, b - t, p)) % p
            if coef == 0:
                continue
            new_a = a + t
            new_b = t
            new_Q[(new_a, new_b)] = (new_Q.get((new_a, new_b), 0) + coef) % p
    new_Q = {k: v for k, v in new_Q.items() if v != 0}
    if not new_Q:
        return new_Q
    min_a = min(a for (a, b) in new_Q)
    if min_a > 0:
        new_Q = {(a - min_a, b): c for (a, b), c in new_Q.items()}
    return new_Q


def roth_ruckenstein(Q, p, k, prefix=None, depth=0):
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
            for j in range(depth + 1, k):
                new_prefix.append(0)
            out.append(list(new_prefix))
            continue
        sub = roth_ruckenstein(new_Q, p, k, new_prefix, depth + 1)
        out.extend(sub)
    return out


def gs_decode_m2(p, omega, n, k, received, d=None):
    points = [(pow(omega, j, p), received[j]) for j in range(n)]
    Q, monos = sudan_interpolate_m2(p, n, k, points, d=d)
    if Q is None:
        return []
    return roth_ruckenstein(Q, p, k)


# ---------------------------------------------------------------------------
# Test: also re-validate Sudan(m=1) reaches Johnson
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
    from gs_sudan import gs_decode, find_d_for_n
    p, n, k = 17, 16, 4
    omega = primitive_root_of_unity(p, n)

    print(f"Self-test (m=2): GS Sudan on RS({n}, {k}) GF({p})")
    d_m1 = find_d_for_n(n, k)
    d_m2 = find_d_for_n_m(n, k, m=2)
    print(f"  m=1: d={d_m1}, τ_max ≤ d = {d_m1}")
    print(f"  m=2: d={d_m2}, τ_max ≤ d/m = {d_m2 // 2}")
    print(f"  Johnson J = n - sqrt(nk) = {n - int((n*k)**0.5)}")

    msg = [1, 2, 3, 4]
    cw = encode_rs(p, omega, n, k, msg)
    rng = random.Random(11)
    for n_errors in [7, 8]:
        err_pos = rng.sample(range(n), n_errors)
        rcvd = list(cw)
        for pos in err_pos:
            rcvd[pos] = (rcvd[pos] + rng.randint(1, p - 1)) % p

        print(f"\n  --- {n_errors} errors at {sorted(err_pos)} ---")
        # m=1
        decoded_m1 = gs_decode(p, omega, n, k, rcvd)
        print(f"  m=1 list ({len(decoded_m1)}): {decoded_m1[:5]}{'...' if len(decoded_m1)>5 else ''}")
        ok_m1 = msg in decoded_m1
        print(f"    m=1 recovered: {'✓' if ok_m1 else '✗'}")

        # m=2
        decoded_m2 = gs_decode_m2(p, omega, n, k, rcvd)
        print(f"  m=2 list ({len(decoded_m2)}): {decoded_m2[:5]}{'...' if len(decoded_m2)>5 else ''}")
        ok_m2 = msg in decoded_m2
        print(f"    m=2 recovered: {'✓' if ok_m2 else '✗'}")


if __name__ == '__main__':
    self_test()
