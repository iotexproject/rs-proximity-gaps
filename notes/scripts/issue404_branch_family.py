#!/usr/bin/env python3
"""Analyze the issue #404 high-K branch family for (n,k)=(16,4)."""

from __future__ import annotations

import argparse
import random

from issue404_stratum_classifier import (
    dot,
    joint_above_delta,
    k_value,
    minimal_joint_support_size,
    modinv,
    nullspace_mod_p,
    precompute_normals,
    precompute_support_normals_by_size,
    primitive_root,
    syndrome_of_monomial,
)


def add_scaled(target: list[int], source: list[int], scalar: int, p: int) -> list[int]:
    return [(x + scalar * y) % p for x, y in zip(target, source)]


def syndrome_from_terms(
    terms: tuple[tuple[int, int], ...],
    mono_syndromes: dict[int, list[int]],
    p: int,
) -> list[int]:
    syndrome = [0] * len(next(iter(mono_syndromes.values())))
    for exp, coeff in terms:
        syndrome = add_scaled(syndrome, mono_syndromes[exp], coeff, p)
    return syndrome


def feasible_alpha_for_complement(
    complement: tuple[int, ...],
    s1: list[int],
    s2: list[int],
    ev: list[list[int]],
    p: int,
) -> tuple[bool, int | None, list[tuple[int, int]]]:
    support = tuple(index for index in range(len(ev)) if index not in complement)
    normals = nullspace_mod_p([ev[index] for index in support], p, len(ev[0]))
    forced_alpha: int | None = None
    equations: list[tuple[int, int]] = []
    for normal in normals:
        left = dot(normal, s1, p)
        slope = dot(normal, s2, p)
        equations.append((left, slope))
        if slope == 0:
            if left != 0:
                return False, None, equations
            continue
        alpha = (-left * modinv(slope, p)) % p
        if forced_alpha is None:
            forced_alpha = alpha
        elif forced_alpha != alpha:
            return False, None, equations
    return forced_alpha is not None, forced_alpha, equations


def branch_base_and_movers(r: int, n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    parity = r % 2
    base = tuple(index for index in range(parity, n, 2) if index not in {r % n, (r + n // 2) % n})
    movers = tuple(index for index in range(1 - parity, n, 2))
    return base, movers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=40408)
    parser.add_argument(
        "--full-k-samples",
        type=int,
        default=1,
        help="number of samples per branch for the slower exact K and S* checks",
    )
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
    print("family: base parity class minus {r,r+8}; movers are opposite parity; impose b8=omega^(-2r)b6")
    for r in range(n // 2):
        base, movers = branch_base_and_movers(r, n)
        ratio = pow(omega, (-2 * r) % n, args.p)
        incidence_ok = 0
        distinct_ok = 0
        joint_ok = 0
        k_dist: dict[int, int] = {}
        sstar_dist: dict[int | str | None, int] = {}
        representative = None
        for trial in range(args.trials):
            a9, a11, a12 = [rng.randrange(1, args.p) for _ in range(3)]
            b6 = rng.randrange(1, args.p)
            b8 = ratio * b6 % args.p
            b12 = rng.randrange(1, args.p)
            terms1 = ((9, a9), (11, a11), (12, a12))
            terms2 = ((6, b6), (8, b8), (12, b12))
            s1 = syndrome_from_terms(terms1, mono_syndromes, args.p)
            s2 = syndrome_from_terms(terms2, mono_syndromes, args.p)
            alphas: list[int] = []
            ok = True
            for mover in movers:
                complement = tuple(sorted(base + (mover,)))
                feasible, alpha, _equations = feasible_alpha_for_complement(complement, s1, s2, ev, args.p)
                if not feasible or alpha is None:
                    ok = False
                    break
                alphas.append(alpha)
            if ok:
                incidence_ok += 1
                if len(set(alphas)) == len(alphas) and 0 not in alphas:
                    distinct_ok += 1
                    if representative is None:
                        representative = (terms1, terms2, alphas)
            if joint_above_delta(s1, s2, normal_sets, args.p):
                joint_ok += 1
            if trial < args.full_k_samples:
                kval = k_value(s1, s2, normal_sets, args.p)
                k_dist[kval] = k_dist.get(kval, 0) + 1
                sstar = minimal_joint_support_size(s1, s2, support_normals_by_size, args.p, syndrome_len)
                sstar_dist[sstar] = sstar_dist.get(sstar, 0) + 1
        print(
            f"r={r:2d} base={base} ratio=omega^{(-2 * r) % n:2d}={ratio:3d} "
            f"incidence={incidence_ok}/{args.trials} distinct={distinct_ok}/{args.trials} "
            f"joint={joint_ok}/{args.trials} fullK={k_dist} Sstar={sstar_dist}"
        )
        if representative is not None:
            terms1, terms2, alphas = representative
            print(f"  representative terms1={terms1} terms2={terms2} alphas={alphas}")


if __name__ == "__main__":
    main()
