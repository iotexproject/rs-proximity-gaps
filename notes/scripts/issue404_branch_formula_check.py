#!/usr/bin/env python3
"""Check the closed-form alpha formula in Note 0308.

This is a proof-audit helper, not a random search for new witnesses. It
compares the explicit formula for the codimension-one branch family against
the raw normal-equation linear algebra for all eight branches and all moving
points.
"""

from __future__ import annotations

import argparse
import random

from issue404_branch_family import branch_base_and_movers, feasible_alpha_for_complement, syndrome_from_terms
from issue404_stratum_classifier import primitive_root, syndrome_of_monomial


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--trials", type=int, default=40)
    parser.add_argument("--seed", type=int, default=40409)
    args = parser.parse_args()

    n, k = 16, 4
    syndrome_len = n - k
    if (args.p - 1) % n != 0:
        raise SystemExit("need n | p-1")

    rng = random.Random(args.seed)
    generator = primitive_root(args.p)
    omega = pow(generator, (args.p - 1) // n, args.p)
    domain = [pow(omega, index, args.p) for index in range(n)]
    ev = [[pow(z, degree, args.p) for degree in range(syndrome_len)] for z in domain]
    mono_syndromes = {exp: syndrome_of_monomial(exp, n, k, args.p, domain) for exp in range(k, n)}

    checked = 0
    denominator_zero = 0
    alpha_zero = 0
    failures: list[tuple[object, ...]] = []
    for r in range(n // 2):
        rho = pow(omega, r, args.p)
        ratio = pow(omega, (-2 * r) % n, args.p)
        base, movers = branch_base_and_movers(r, n)
        for _trial in range(args.trials):
            a9, a11, a12 = [rng.randrange(1, args.p) for _ in range(3)]
            b6 = rng.randrange(1, args.p)
            b8 = ratio * b6 % args.p
            b12 = rng.randrange(1, args.p)
            s1 = syndrome_from_terms(((9, a9), (11, a11), (12, a12)), mono_syndromes, args.p)
            s2 = syndrome_from_terms(((6, b6), (8, b8), (12, b12)), mono_syndromes, args.p)
            for x in movers:
                tau = pow(omega, x, args.p)
                complement = tuple(sorted(base + (x,)))
                feasible, actual_alpha, _equations = feasible_alpha_for_complement(complement, s1, s2, ev, args.p)
                numerator = (
                    ((tau * tau - rho * rho) % args.p)
                    * (a9 + a11 * tau * tau + a12 * pow(tau, 3, args.p))
                ) % args.p
                denominator = (b8 * tau + b12 * ((tau * tau - rho * rho) % args.p) * pow(tau, 3, args.p)) % args.p
                if denominator == 0:
                    denominator_zero += 1
                    predicted_alpha = None
                else:
                    predicted_alpha = (-numerator * pow(denominator, -1, args.p)) % args.p
                    if predicted_alpha == 0:
                        alpha_zero += 1
                checked += 1
                if (not feasible and predicted_alpha is not None) or (feasible and actual_alpha != predicted_alpha):
                    failures.append((r, x, feasible, actual_alpha, predicted_alpha, numerator, denominator))
                    if len(failures) >= 8:
                        break
            if failures:
                break
        if failures:
            break

    print(
        f"PARAM n={n} k={k} p={args.p} omega={omega} "
        f"trials_per_branch={args.trials} checked={checked}"
    )
    print(f"denominator_zero={denominator_zero} alpha_zero={alpha_zero} failures={len(failures)}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(1)
    print("closed_form_alpha_check=PASS")


if __name__ == "__main__":
    main()
