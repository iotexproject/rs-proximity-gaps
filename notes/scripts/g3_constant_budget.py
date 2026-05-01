"""Compute the G3 exact level-sum constant for the R-round z_T bound.

The paper's general theorem first gives

    Pr[ever below-J] <= sum_j C(n_j, k_j) / q,

then often relaxes this to R * C(n_1, k_1) / q.  This script keeps the exact
level sum and uses the sharpened nondegenerate (k+1)-witness constant.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class LevelBudget:
    level: int
    n: int
    k: int
    s: int
    legacy_exact: Fraction
    legacy_floor: int
    sharp_exact: Fraction
    sharp_floor: int


def legacy_c_rational(n: int, k: int) -> Fraction:
    s = math.isqrt(n * k)
    if s * s != n * k:
        raise ValueError(f"n*k must be a square, got n={n}, k={k}")
    return Fraction(math.comb(n, k) * (n - s + 1), math.comb(s, k))


def sharp_c_rational(n: int, k: int) -> Fraction:
    s = math.isqrt(n * k)
    if s * s != n * k:
        raise ValueError(f"n*k must be a square, got n={n}, k={k}")
    return Fraction(math.comb(n, k + 1), math.comb(s - 1, k))


def level_budgets(n0: int, k0: int, rounds: int) -> list[LevelBudget]:
    out: list[LevelBudget] = []
    for j in range(1, rounds + 1):
        n = n0 // (2**j)
        k = k0 // (2**j)
        if k < 1:
            break
        s = math.isqrt(n * k)
        legacy = legacy_c_rational(n, k)
        sharp = sharp_c_rational(n, k)
        # The exceptional count is integral, so N <= c_exact implies
        # N <= floor(c_exact).  This matches the existing paper table.
        out.append(
            LevelBudget(
                j,
                n,
                k,
                s,
                legacy,
                legacy.numerator // legacy.denominator,
                sharp,
                sharp.numerator // sharp.denominator,
            )
        )
    return out


def fmt_int(x: int) -> str:
    return f"{x:,}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", nargs="*", default=["32,8,2", "64,16,3", "128,32,4", "256,64,5"])
    parser.add_argument("--q-bits", type=int, default=31)
    args = parser.parse_args()

    q = 2**args.q_bits
    print("# G3 exact level-sum constant budget")
    print(f"# q = 2^{args.q_bits}")
    print()
    header = (
        "n0,k0,R | sharp C_j floors | Sigma_C | legacy Sigma | "
        "legacy/sharp | (1-tau1)Sigma_C/q | qbits@1% | qbits@2^-20"
    )
    print(header)
    print("-" * len(header))
    for spec in args.params:
        n0, k0, rounds = (int(x) for x in spec.split(","))
        budgets = level_budgets(n0, k0, rounds)
        sigma = sum(b.sharp_floor for b in budgets)
        legacy_sigma = sum(b.legacy_floor for b in budgets)
        n1 = n0 // 2
        k1 = k0 // 2
        tau1 = Fraction(math.isqrt(n1 * k1) - 1, n1)
        correction = (Fraction(1, 1) - tau1) * sigma
        qbits_1pct = math.ceil(math.log2(float(correction * 100)))
        qbits_2m20 = math.ceil(math.log2(float(correction)) + 20)
        print(
            f"{n0},{k0},{rounds} | "
            f"{[b.sharp_floor for b in budgets]} | "
            f"{fmt_int(sigma)} | {fmt_int(legacy_sigma)} | "
            f"{float(Fraction(legacy_sigma, sigma)):.3f}x | "
            f"{float(correction / q):.6g} | "
            f"{qbits_1pct} | {qbits_2m20}"
        )


if __name__ == "__main__":
    main()
