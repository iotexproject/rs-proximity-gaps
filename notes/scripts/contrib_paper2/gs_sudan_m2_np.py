"""NumPy-accelerated Sudan(m=2) — 10-30× faster Gaussian elim mod p.

For (32, 8) p=257 K-sweep: per-K-call goes from ~8s to ~0.3s,
enabling n_random ≥ 100 in reasonable time.
"""
from __future__ import annotations

from math import comb
import numpy as np

from gs_sudan import poly_eval, monomials_weighted
from gs_sudan_m2 import find_d_for_n_m


def gauss_kernel_mod_np(M_list, p):
    """Find a non-trivial kernel element of M mod p using numpy.

    M_list: list of rows. Returns list (kernel element) or None if full rank.
    """
    if not M_list or not M_list[0]:
        return None
    M = np.array(M_list, dtype=np.int64) % p
    rows, cols = M.shape
    pivot_col = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        # find first non-zero in column c at row >= r
        col = M[r:, c] % p
        idxs = np.where(col != 0)[0]
        if len(idxs) == 0:
            continue
        piv = r + int(idxs[0])
        if piv != r:
            M[[r, piv]] = M[[piv, r]]
        # normalize pivot row
        inv_p = pow(int(M[r, c]), p - 2, p)
        M[r] = (M[r] * inv_p) % p
        # eliminate other rows
        # mask out the pivot row
        for i in range(rows):
            if i == r:
                continue
            f = int(M[i, c]) % p
            if f != 0:
                M[i] = (M[i] - f * M[r]) % p
        pivot_col.append(c)
        r += 1
    if r == cols:
        return None
    free_cols = [c for c in range(cols) if c not in pivot_col]
    if not free_cols:
        return None
    free_c = free_cols[0]
    sol = [0] * cols
    sol[free_c] = 1
    for ridx, c in enumerate(pivot_col):
        sol[c] = int((-M[ridx, free_c]) % p)
    return sol


def hasse_constraint(x0, y0, monos, p, i, j):
    row = []
    for (a, b) in monos:
        if a < i or b < j:
            row.append(0)
            continue
        coef = (comb(a, i) * comb(b, j)) % p
        coef = (coef * pow(x0, a - i, p) * pow(y0, b - j, p)) % p
        row.append(coef)
    return row


def sudan_interpolate_m2_np(p, n, k, points, d=None):
    m = 2
    if d is None:
        d = find_d_for_n_m(n, k, m)
    monos = monomials_weighted(d, k)
    M = []
    for (xi, yi) in points:
        for (i, j) in [(0, 0), (1, 0), (0, 1)]:
            M.append(hasse_constraint(xi, yi, monos, p, i, j))
    sol = gauss_kernel_mod_np(M, p)
    if sol is None:
        return None, monos
    Q = {monos[i]: sol[i] for i in range(len(monos)) if sol[i] != 0}
    return Q, monos


# --- factorization (re-use from gs_sudan_m2) ---
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


def gs_decode_m2_np(p, omega, n, k, received, d=None):
    points = [(pow(omega, j, p), received[j]) for j in range(n)]
    Q, monos = sudan_interpolate_m2_np(p, n, k, points, d=d)
    if Q is None:
        return []
    return roth_ruckenstein(Q, p, k)


# --- timing test ---

if __name__ == '__main__':
    import time
    import random
    from gs_sudan_m2 import primitive_root_of_unity, encode_rs, hamming
    p, n, k = 257, 32, 8
    omega = primitive_root_of_unity(p, n)
    msg = [1, 2, 3, 4, 5, 6, 7, 8]
    cw = encode_rs(p, omega, n, k, msg)
    rng = random.Random(7)
    err_pos = rng.sample(range(n), 14)
    rcvd = list(cw)
    for pos in err_pos:
        rcvd[pos] = (rcvd[pos] + rng.randint(1, p - 1)) % p
    print(f"Timing (32,8) p=257, 14 errors:")
    t0 = time.time()
    decoded = gs_decode_m2_np(p, omega, n, k, rcvd)
    print(f"  numpy version: {time.time()-t0:.2f}s")
    print(f"  list size: {len(decoded)}, recovered: {msg in decoded}")

    from gs_sudan_m2 import gs_decode_m2
    t0 = time.time()
    decoded2 = gs_decode_m2(p, omega, n, k, rcvd)
    print(f"  pure python: {time.time()-t0:.2f}s")
    assert sorted(map(tuple, decoded)) == sorted(map(tuple, decoded2)), "results differ!"
    print(f"  ✓ results match")
