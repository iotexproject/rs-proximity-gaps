#!/usr/bin/env python3
"""Verify fixed Issue #404 codimension-one branch certificates.

This is the deterministic companion to issue404_branch_certificate.py.  It
contains the eight F_193 certificates recorded in Note 0310 and verifies,
without random search, that each certificate:

  * lies on the r-th branch b8 = omega^(-2r) b6;
  * has the eight forced closed-form branch challenges;
  * has those challenges defined, nonzero, and distinct;
  * is joint-above at w=9;
  * has S* = 10 and exact K = 9.
"""

from __future__ import annotations

from issue404_branch_certificate import closed_form_alpha
from issue404_branch_family import branch_base_and_movers, feasible_alpha_for_complement, syndrome_from_terms
from issue404_stratum_classifier import (
    joint_above_delta,
    k_value,
    minimal_joint_support_size,
    precompute_normals,
    precompute_support_normals_by_size,
    primitive_root,
    syndrome_of_monomial,
)


CERTIFICATES: dict[int, dict[str, object]] = {
    0: {
        "terms1": ((9, 127), (11, 76), (12, 6)),
        "terms2": ((6, 63), (8, 63), (12, 180)),
        "alphas": (161, 100, 41, 162, 8, 174, 26, 30),
    },
    1: {
        "terms1": ((9, 174), (11, 96), (12, 124)),
        "terms2": ((6, 191), (8, 175), (12, 24)),
        "alphas": (178, 181, 32, 93, 129, 25, 149, 47),
    },
    2: {
        "terms1": ((9, 190), (11, 34), (12, 84)),
        "terms2": ((6, 3), (8, 50), (12, 157)),
        "alphas": (156, 136, 62, 84, 67, 181, 74, 91),
    },
    3: {
        "terms1": ((9, 123), (11, 130), (12, 93)),
        "terms2": ((6, 40), (8, 17), (12, 130)),
        "alphas": (45, 77, 82, 27, 180, 46, 92, 107),
    },
    4: {
        "terms1": ((9, 173), (11, 131), (12, 82)),
        "terms2": ((6, 51), (8, 142), (12, 53)),
        "alphas": (170, 38, 155, 100, 4, 3, 40, 123),
    },
    5: {
        "terms1": ((9, 89), (11, 56), (12, 153)),
        "terms2": ((6, 5), (8, 148), (12, 10)),
        "alphas": (130, 192, 128, 7, 111, 113, 66, 94),
    },
    6: {
        "terms1": ((9, 50), (11, 182), (12, 163)),
        "terms2": ((6, 176), (8, 26), (12, 187)),
        "alphas": (2, 88, 53, 90, 161, 109, 80, 155),
    },
    7: {
        "terms1": ((9, 166), (11, 170), (12, 108)),
        "terms2": ((6, 16), (8, 109), (12, 12)),
        "alphas": (6, 128, 73, 69, 23, 163, 60, 141),
    },
}


def main() -> None:
    n, k, p, c = 16, 4, 193, 3
    syndrome_len = n - k
    w = syndrome_len - c
    generator = primitive_root(p)
    omega = pow(generator, (p - 1) // n, p)
    domain = [pow(omega, index, p) for index in range(n)]
    ev = [[pow(z, degree, p) for degree in range(syndrome_len)] for z in domain]
    mono_syndromes = {exp: syndrome_of_monomial(exp, n, k, p, domain) for exp in range(k, n)}
    normal_sets = precompute_normals(ev, w, p)
    support_normals_by_size = precompute_support_normals_by_size(ev, p, syndrome_len)

    print(f"PARAM n={n} k={k} p={p} D={syndrome_len} w={w} omega={omega}")
    for r, certificate in CERTIFICATES.items():
        terms1 = tuple(certificate["terms1"])
        terms2 = tuple(certificate["terms2"])
        expected_alphas = list(certificate["alphas"])
        a9, a11, a12 = [coeff for _exp, coeff in terms1]
        b6, b8, b12 = [coeff for _exp, coeff in terms2]
        ratio = pow(omega, (-2 * r) % n, p)
        if b8 != ratio * b6 % p:
            raise SystemExit(f"r={r}: branch ratio mismatch")

        s1 = syndrome_from_terms(terms1, mono_syndromes, p)
        s2 = syndrome_from_terms(terms2, mono_syndromes, p)
        base, movers = branch_base_and_movers(r, n)
        actual_alphas: list[int] = []
        for x in movers:
            complement = tuple(sorted(base + (x,)))
            feasible, linear_alpha, _equations = feasible_alpha_for_complement(complement, s1, s2, ev, p)
            formula_alpha = closed_form_alpha(r, x, (a9, a11, a12, b6, b8, b12), omega, n, p)
            if not feasible or linear_alpha is None:
                raise SystemExit(f"r={r}, x={x}: forced incidence missing")
            if formula_alpha != linear_alpha:
                raise SystemExit(f"r={r}, x={x}: formula alpha {formula_alpha} != linear alpha {linear_alpha}")
            actual_alphas.append(linear_alpha)

        if actual_alphas != expected_alphas:
            raise SystemExit(f"r={r}: alpha list mismatch {actual_alphas} != {expected_alphas}")
        if 0 in actual_alphas or len(set(actual_alphas)) != len(actual_alphas):
            raise SystemExit(f"r={r}: alphas are not nonzero and distinct")
        if not joint_above_delta(s1, s2, normal_sets, p):
            raise SystemExit(f"r={r}: certificate is not joint-above at w={w}")
        sstar = minimal_joint_support_size(s1, s2, support_normals_by_size, p, syndrome_len)
        kval = k_value(s1, s2, normal_sets, p)
        if sstar != w + 1 or kval != 9:
            raise SystemExit(f"r={r}: expected K=9,S*={w + 1}; got K={kval},S*={sstar}")
        print(f"r={r} ratio=omega^{(-2 * r) % n}={ratio} K={kval} Sstar={sstar} alphas={actual_alphas}")
    print("fixed_branch_certificates=PASS")


if __name__ == "__main__":
    main()

