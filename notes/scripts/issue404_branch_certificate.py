#!/usr/bin/env python3
"""Produce fixed nonempty-open certificates for the Note 0308 branch family.

For each codimension-one branch r, this script finds a deterministic
coefficient specialization over F_p where:
  * the eight closed-form alphas are defined, nonzero, and distinct;
  * the pair is joint-admissible at weight w=9;
  * the Paper 3 joint support size is S*=10;
  * the exact K value is computed.

A successful specialization over a prime p with a primitive 16-th root
certifies that the corresponding nonvanishing polynomials are not identically
zero over the cyclotomic coefficient ring.
"""

from __future__ import annotations

import argparse
import random

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


def closed_form_alpha(
    r: int,
    x: int,
    coeffs: tuple[int, int, int, int, int, int],
    omega: int,
    n: int,
    p: int,
) -> int | None:
    a9, a11, a12, _b6, b8, b12 = coeffs
    rho = pow(omega, r, p)
    tau = pow(omega, x, p)
    numerator = ((tau * tau - rho * rho) % p) * (a9 + a11 * tau * tau + a12 * pow(tau, 3, p)) % p
    denominator = (b8 * tau + b12 * ((tau * tau - rho * rho) % p) * pow(tau, 3, p)) % p
    if denominator == 0:
        return None
    return (-numerator * pow(denominator, -1, p)) % p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--seed", type=int, default=40410)
    parser.add_argument("--max-trials", type=int, default=5000)
    args = parser.parse_args()

    n, k, c = 16, 4, 3
    syndrome_len = n - k
    w = syndrome_len - c
    if (args.p - 1) % n != 0:
        raise SystemExit("need n | p-1")

    rng = random.Random(args.seed)
    generator = primitive_root(args.p)
    omega = pow(generator, (args.p - 1) // n, args.p)
    domain = [pow(omega, index, args.p) for index in range(n)]
    ev = [[pow(z, degree, args.p) for degree in range(syndrome_len)] for z in domain]
    mono_syndromes = {exp: syndrome_of_monomial(exp, n, k, args.p, domain) for exp in range(k, n)}
    normal_sets = precompute_normals(ev, w, args.p)
    support_normals_by_size = precompute_support_normals_by_size(ev, args.p, syndrome_len)

    print(f"PARAM n={n} k={k} p={args.p} D={syndrome_len} w={w} omega={omega}")
    for r in range(n // 2):
        ratio = pow(omega, (-2 * r) % n, args.p)
        base, movers = branch_base_and_movers(r, n)
        found = None
        for trial in range(args.max_trials):
            a9, a11, a12 = [rng.randrange(1, args.p) for _ in range(3)]
            b6 = rng.randrange(1, args.p)
            b8 = ratio * b6 % args.p
            b12 = rng.randrange(1, args.p)
            coeffs = (a9, a11, a12, b6, b8, b12)
            terms1 = ((9, a9), (11, a11), (12, a12))
            terms2 = ((6, b6), (8, b8), (12, b12))
            s1 = syndrome_from_terms(terms1, mono_syndromes, args.p)
            s2 = syndrome_from_terms(terms2, mono_syndromes, args.p)
            alphas: list[int] = []
            ok = True
            for x in movers:
                complement = tuple(sorted(base + (x,)))
                feasible, actual_alpha, _equations = feasible_alpha_for_complement(complement, s1, s2, ev, args.p)
                predicted_alpha = closed_form_alpha(r, x, coeffs, omega, n, args.p)
                if not feasible or actual_alpha is None or predicted_alpha != actual_alpha:
                    ok = False
                    break
                alphas.append(actual_alpha)
            if not ok or 0 in alphas or len(set(alphas)) != len(alphas):
                continue
            if not joint_above_delta(s1, s2, normal_sets, args.p):
                continue
            sstar = minimal_joint_support_size(s1, s2, support_normals_by_size, args.p, syndrome_len)
            if sstar != w + 1:
                continue
            kval = k_value(s1, s2, normal_sets, args.p)
            if kval < w:
                continue
            found = (trial, terms1, terms2, alphas, sstar, kval)
            break
        if found is None:
            raise SystemExit(f"no certificate found for r={r}")
        trial, terms1, terms2, alphas, sstar, kval = found
        print(
            f"r={r} ratio=omega^{(-2 * r) % n}={ratio} trial={trial} "
            f"K={kval} Sstar={sstar} terms1={terms1} terms2={terms2} alphas={alphas}"
        )
    print("branch_certificate=PASS")


if __name__ == "__main__":
    main()
