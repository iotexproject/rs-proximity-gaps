"""Cyclotomic block-interpolant normal form for issue #396.

For a post-two-fold domain L of size n=4k, split L into the four residue
classes C_r={omega^(r+4t)}.  A polynomial P on L has a unique degree-<k
representative R_r(P) on each block C_r.  This script verifies the closed
formula

    R_r(P)_a = sum_m P_{a+mk} zeta^(r m),  zeta=omega^k,  0<=a<k,

and checks that the two-block and defect-root tests used in Notes 0321-0322
are exactly this quotient-C4 Fourier transform.
"""

from __future__ import annotations

import os
import random
import sys
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root
from issue396_component_polynomial_audit import generator_poly, poly_mod, subgroup


def eval_poly(coeffs, x, p):
    acc = 0
    power = 1
    for c in coeffs:
        acc = (acc + c * power) % p
        power = (power * x) % p
    return acc


def block_indices(n, r):
    return tuple(i for i in range(n) if i % 4 == r)


def local_coeff_formula(coeffs, r, omega, k, p):
    zeta = pow(omega, k, p)
    out = []
    for a in range(k):
        total = 0
        m = 0
        idx = a
        while idx < len(coeffs):
            total = (total + coeffs[idx] * pow(zeta, r * m, p)) % p
            m += 1
            idx += k
        out.append(total)
    return tuple(out)


def local_coeff_lagrange(coeffs, H, L, p, k):
    g = generator_poly(H, L, p)
    return tuple(poly_mod(coeffs, g, p)[:k])


def normalize_coeffs(coeffs, n, p):
    out = [0] * n
    for i, c in enumerate(coeffs):
        out[i % n] = (out[i % n] + c) % p
    return tuple(out)


def random_sparse_poly(n, p, rng, weight):
    coeffs = [0] * n
    for idx in rng.sample(range(n), weight):
        coeffs[idx] = rng.randrange(1, p)
    return tuple(coeffs)


def check_local_formula(n, p, trials=100):
    k = n // 4
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError((p, n))
    L = subgroup(n, p)
    rng = random.Random(0x3960323 + n + p)
    for trial in range(trials):
        coeffs = random_sparse_poly(n, p, rng, rng.randrange(1, min(n, 12) + 1))
        coeffs = normalize_coeffs(coeffs, n, p)
        for r in range(4):
            H = block_indices(n, r)
            via_formula = local_coeff_formula(coeffs, r, omega, k, p)
            via_lagrange = local_coeff_lagrange(coeffs, H, L, p, k)
            if via_formula != via_lagrange:
                raise AssertionError((n, p, trial, r, via_formula, via_lagrange))
            for i in H:
                if eval_poly(via_formula, L[i], p) != eval_poly(coeffs, L[i], p):
                    raise AssertionError(("eval", n, p, trial, r, i))


def coeff_diff(a, b, p):
    return tuple((x - y) % p for x, y in zip(a, b))


def check_two_block_and_defect(n, p, trials=100):
    k = n // 4
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError((p, n))
    L = subgroup(n, p)
    rng = random.Random(0x396D323 + n + p)
    for trial in range(trials):
        coeffs = random_sparse_poly(n, p, rng, rng.randrange(1, min(n, 14) + 1))
        coeffs = normalize_coeffs(coeffs, n, p)
        locals_by_r = [local_coeff_formula(coeffs, r, omega, k, p) for r in range(4)]
        for r, s in combinations(range(4), 2):
            H = tuple(i for i in range(n) if i % 4 in {r, s})
            two_block_tail = tuple(poly_mod(coeffs, generator_poly(H, L, p), p)[k : 2 * k])
            local_equal = locals_by_r[r] == locals_by_r[s]
            if (not any(two_block_tail)) != local_equal:
                raise AssertionError(("two-block", n, p, trial, r, s, two_block_tail))

            if local_equal:
                common = locals_by_r[r]
                for t in set(range(4)) - {r, s}:
                    defect = coeff_diff(locals_by_r[t], common, p)
                    for i in block_indices(n, t):
                        direct = (eval_poly(coeffs, L[i], p) - eval_poly(common, L[i], p)) % p
                        via_defect = eval_poly(defect, L[i], p)
                        if direct != via_defect:
                            raise AssertionError(("defect", n, p, trial, r, s, t, i))


def main():
    cases = [
        (16, 193),
        (32, 193),
        (64, 257),
    ]
    print("Issue #396 block-interpolant normal form")
    for n, p in cases:
        check_local_formula(n, p)
        check_two_block_and_defect(n, p)
        print(f"verified n={n}, k={n//4}, q={p}: local formula, two-block equality, defect roots")


if __name__ == "__main__":
    main()
