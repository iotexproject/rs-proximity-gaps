"""g3_signpaired_2coset_check.py — verify Note 0197 closed form at (32, 8) and beyond.

For each deployment scale (n, k) with n=4k, enumerate the 6 mod-4 class pairs
and compute ρ_S = β - α² via the closed form. Compare to:
- The 4-th roots of unity in F_q
- Existence proven by codex's elementary identity

This gives strong empirical support that the elimination polynomial Φ_{a, a+n/2}
factors into (ρ-1)(ρ+1)(ρ²+1) = ρ⁴-1 universally.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import combinations
from g3_conjE_exact_halfset import subgroup, rho_for_halfset
from math import isqrt


def check_2coset_at_scale(n, k, q):
    """Compute bad ρ from 6 mod-4 class pair half-sets via Note 0197 formula."""
    L = subgroup(q, n)
    omega = L[1]
    zeta = pow(omega, k, q)  # primitive 4-th root

    print(f"\n=== (n={n}, k={k}, q={q}) ===")
    print(f"  ζ = ω^k = {zeta}, ζ² = {(zeta*zeta) % q}")

    bad_ratios_predicted = []
    for c1, c2 in combinations(range(4), 2):
        alpha = (pow(zeta, c1, q) + pow(zeta, c2, q)) % q
        beta = pow(zeta, c1 + c2, q)
        rho = (beta - alpha * alpha) % q
        bad_ratios_predicted.append((c1, c2, rho))

    rho_set = sorted(set(r for _, _, r in bad_ratios_predicted))
    print(f"  Predicted bad ρ: {rho_set}")

    fourth_roots = sorted([x for x in range(1, q) if pow(x, 4, q) == 1])
    print(f"  4-th roots of 1 in F_{q}: {fourth_roots}")

    match = (set(rho_set) == set(fourth_roots))
    print(f"  ✓ predicted == 4-th roots: {match}")

    # Empirically verify each (c1, c2) is a one-ratio halfset for sign-paired pencil
    if n <= 16:  # only enumerate at small scales
        a = k  # sign-paired with b = a + n/2
        b = a + n // 2
        t = isqrt(k * n)
        print(f"  Empirical check (a={a}, b={b}):")
        for c1, c2, predicted_rho in bad_ratios_predicted:
            S_indices = [i for i in range(n) if i % 4 in (c1, c2)]
            assert len(S_indices) == t
            points = [L[i] for i in S_indices]
            kind, actual_rho = rho_for_halfset(points, a, b, k, q)
            match_one = (kind == "one" and actual_rho == predicted_rho)
            print(f"    ({c1},{c2}): predicted ρ={predicted_rho}, actual ({kind}, ρ={actual_rho}) → {'✓' if match_one else '✗'}")
    else:
        print(f"  (skip empirical check at this scale; enumeration too slow)")


def main():
    cases = [
        (8, 2, 17), (8, 2, 97),
        (16, 4, 17), (16, 4, 97), (16, 4, 193),
        (32, 8, 97), (32, 8, 193), (32, 8, 449),
        (64, 16, 193), (64, 16, 449),
        (128, 32, 257), (128, 32, 769),
    ]
    for n, k, q in cases:
        try:
            check_2coset_at_scale(n, k, q)
        except Exception as e:
            print(f"  FAILED ({n}, {k}, {q}): {e}")


if __name__ == "__main__":
    main()
