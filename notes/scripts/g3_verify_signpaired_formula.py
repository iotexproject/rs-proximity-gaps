"""g3_verify_signpaired_formula.py — verify Theorem 0197 closed-form bad ratio.

Theorem: for sign-paired pencil h_ρ(z) = ρz^a + z^b on L_n with b − a = n/2,
half-set S = C_{c1} ∪ C_{c2} (mod-4 class pair) gives bad ratio
    ρ_S = β − α²   where α = ζ^{c1} + ζ^{c2}, β = ζ^{c1+c2}, ζ = ω^k
independent of (a, b).

Verify against empirical exact_bad_ratios on multiple (n, k, q).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import combinations
from math import isqrt

from g3_conjE_exact_halfset import subgroup, exact_bad_ratios


def predicted_signpaired_ratios(n, k, q, omega):
    """Compute predicted ρ_S = β − α² for each mod-4 class pair."""
    zeta = pow(omega, k, q)
    out = {}
    for c1, c2 in combinations(range(4), 2):
        alpha = (pow(zeta, c1, q) + pow(zeta, c2, q)) % q
        beta = pow(zeta, c1 + c2, q)
        rho = (beta - alpha * alpha) % q
        out[(c1, c2)] = rho
    return out


def main():
    cases = [
        (8, 2, 17),
        (8, 2, 97),
        (16, 4, 17),
        (16, 4, 97),
        (16, 4, 193),
        (32, 8, 97),  # half-sets too big for full enumeration; only check formula
    ]

    for n, k, q in cases:
        L = subgroup(q, n)
        omega = L[1]
        preds = predicted_signpaired_ratios(n, k, q, omega)
        unique_preds = set(preds.values())
        print(f"\n=== (n={n}, k={k}, q={q}) ===")
        print(f"  predicted ρ_S = β − α² for 6 mod-4 pairs:")
        for (c1, c2), rho in preds.items():
            print(f"    ({c1},{c2}) → {rho}")
        print(f"  unique predicted ratios: {sorted(unique_preds)}")
        # Verify these are exactly the 4-th roots of unity
        roots4 = set(x for x in range(1, q) if pow(x, 4, q) == 1)
        match = unique_preds == roots4
        print(f"  4-th roots of 1 in F_{q}: {sorted(roots4)}")
        print(f"  predicted == 4-th roots: {match}")

        # If small enough, run empirical comparison
        if n <= 16:
            print(f"  Empirical check (a=k+0, b=a+n/2 = sign-paired):")
            a = k
            b = (a + n // 2) % n
            t = isqrt(k * n)
            assert t * t == k * n
            result = exact_bad_ratios(n, k, q, a, b)
            empirical_bad = set(result["bad"].keys())
            print(f"    pencil (a={a}, b={b}): empirical bad ρ = {sorted(empirical_bad)}")
            print(f"    matches predicted: {empirical_bad == unique_preds}")


if __name__ == "__main__":
    main()
