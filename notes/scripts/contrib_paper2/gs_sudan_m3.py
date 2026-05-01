"""Sudan GS list-decoder at multiplicity m=3 with Hasse-derivative interpolation.

For (32, 8) Johnson exact: 6n=192 constraints, d=48, τ ≤ n - d/m = 32 - 16 = 16 = J.

Constraints per point at m=3: 6 Hasse derivatives:
  (0,0), (1,0), (0,1), (2,0), (1,1), (0,2)
"""
from __future__ import annotations

from math import comb
import numpy as np

from gs_sudan import poly_eval, monomials_weighted
from gs_sudan_m2 import find_d_for_n_m, encode_rs, hamming, primitive_root_of_unity
from gs_sudan_m2_np import (
    gauss_kernel_mod_np, hasse_constraint, Q_at_X_zero_Y, find_roots_in_Fp,
    shift_Q, roth_ruckenstein,
)


def find_d_for_n_m3(n, k):
    """Smallest d with #monos > 6n (m=3 has 6 constraints/point)."""
    constraints = 6 * n
    d = 0
    while True:
        if len(monomials_weighted(d, k)) > constraints:
            return d
        d += 1


HASSE_M3 = [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]


def sudan_interpolate_m3(p, n, k, points, d=None):
    if d is None:
        d = find_d_for_n_m3(n, k)
    monos = monomials_weighted(d, k)
    M = []
    for (xi, yi) in points:
        for (i, j) in HASSE_M3:
            M.append(hasse_constraint(xi, yi, monos, p, i, j))
    sol = gauss_kernel_mod_np(M, p)
    if sol is None:
        return None, monos
    Q = {monos[i]: sol[i] for i in range(len(monos)) if sol[i] != 0}
    return Q, monos


def gs_decode_m3(p, omega, n, k, received, d=None):
    points = [(pow(omega, j, p), received[j]) for j in range(n)]
    Q, monos = sudan_interpolate_m3(p, n, k, points, d=d)
    if Q is None:
        return []
    return roth_ruckenstein(Q, p, k)


def self_test():
    import random
    p, n, k = 257, 32, 8
    omega = primitive_root_of_unity(p, n)
    d = find_d_for_n_m3(n, k)
    tau = (n * 3 - d - 1) // 3
    print(f"Sudan(m=3) on RS({n}, {k}) GF({p})")
    print(f"  d = {d}, τ = {tau}, J = {n - int((n*k)**0.5)}")

    msg = [1, 2, 3, 4, 5, 6, 7, 8]
    cw = encode_rs(p, omega, n, k, msg)
    rng = random.Random(11)
    for n_errors in [14, 15, 16]:
        err_pos = rng.sample(range(n), n_errors)
        rcvd = list(cw)
        for pos in err_pos:
            rcvd[pos] = (rcvd[pos] + rng.randint(1, p - 1)) % p
        import time
        t0 = time.time()
        decoded = gs_decode_m3(p, omega, n, k, rcvd, d=d)
        elapsed = time.time() - t0
        ok = msg in decoded
        print(f"  {n_errors} errors: list size {len(decoded)}, recovered: {'✓' if ok else '✗'} [{elapsed:.1f}s]")


if __name__ == '__main__':
    self_test()
