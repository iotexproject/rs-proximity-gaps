"""g3_4mono_267_exhaust_q.py — exhaustive Φ_{(1,2,6,7)} F_q-root sweep.

Issue #406: close K_4 ≤ 9 RIGOROUS for the (1, 2, 6, 7) case.

Note 0298 found that for ρ_2 = ρ_3, Φ has only 9 distinct α-roots
(via β = α^4 cubic factoring as β · (β - 4ρ²²) · (β + 4ρ²²)).
Generic ρ has algebraically 12 roots in F̄_q. The 1000-sample
empirical sweep (Notes 0293/0296) found max = 9 across 5 primes.

Question: is empirical 9 the true max in F_q, or did the sample miss
the case where all 3 cubic β-roots are 4th powers in F_q (giving 12)?

This script does exhaustive enum over (ρ_2, ρ_3) ∈ F_q^2 at small q
to determine the true max.

For q=97: 97² = 9409 pairs, fast.
For q=193: 193² = 37249 pairs, ~10s.
"""
from __future__ import annotations

import argparse
import sys
import time


def cubic_psi_coeffs(rho2: int, rho3: int, q: int) -> tuple[int, int, int]:
    """Cubic ψ(β) = β³ + a₂β² + a₁β + a₀, return (a₀, a₁, a₂) mod q."""
    a2 = (24 * rho2**3 * rho3 - 24 * rho2 * rho3**3) % q
    a1 = (-180 * rho2**6 * rho3**2 - 86 * rho2**4 * rho3**4
          + 204 * rho2**2 * rho3**6 + 46 * rho3**8) % q
    a0 = (-64 * rho2**7 * rho3**5 + 32 * rho2**5 * rho3**7
          + 64 * rho2**3 * rho3**9 - 32 * rho2 * rho3**11) % q
    return a0, a1, a2


def cubic_roots(a0: int, a1: int, a2: int, q: int) -> list[int]:
    """Return F_q-rational roots of β³ + a₂β² + a₁β + a₀ via brute search."""
    return [b for b in range(q) if (b**3 + a2*b*b + a1*b + a0) % q == 0]


def fourth_roots(beta: int, q: int) -> list[int]:
    """Return F_q-rational 4th roots of β (i.e., α with α^4 = β)."""
    return [a for a in range(q) if pow(a, 4, q) == beta % q]


def alpha_roots_count(rho2: int, rho3: int, q: int) -> int:
    """Total F_q-rational distinct α with Φ_{(1,2,6,7)}(α; ρ_2, ρ_3) = 0."""
    a0, a1, a2 = cubic_psi_coeffs(rho2, rho3, q)
    betas = cubic_roots(a0, a1, a2, q)
    alphas = set()
    for b in betas:
        for a in fourth_roots(b, q):
            alphas.add(a)
    return len(alphas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, nargs="+", default=[97, 193])
    parser.add_argument("--report-top", type=int, default=10)
    args = parser.parse_args()

    for q in args.q:
        print(f"\n=== q = {q} ===")
        if (q - 1) % 4 != 0:
            print(f"  skip: 4 ∤ q-1 = {q-1} (no 4th roots framework)")
            continue
        t0 = time.time()
        max_K = 0
        max_witnesses = []
        K_dist = {}
        for rho2 in range(1, q):  # nonzero
            for rho3 in range(1, q):  # nonzero
                K = alpha_roots_count(rho2, rho3, q)
                K_dist[K] = K_dist.get(K, 0) + 1
                if K > max_K:
                    max_K = K
                    max_witnesses = [(rho2, rho3)]
                elif K == max_K and len(max_witnesses) < args.report_top:
                    max_witnesses.append((rho2, rho3))
        elapsed = time.time() - t0
        print(f"  exhaustive ({(q-1)**2} (ρ_2, ρ_3) pairs, ρ_2, ρ_3 ≠ 0): {elapsed:.1f}s")
        print(f"  Max K_4 over F_{q}: {max_K}")
        print(f"  Distribution: {dict(sorted(K_dist.items()))}")
        print(f"  Top witnesses (first {args.report_top}):")
        for (r2, r3) in max_witnesses[:args.report_top]:
            print(f"    (ρ_2, ρ_3) = ({r2}, {r3})")

    print()
    print("=== INTERPRETATION ===")
    print("If max ≤ 9 across all q tested → strong evidence K_4 ≤ 9 RIGOROUS at deployment q.")
    print("If max = 12 at any q → generic case realizes; K_4 = 12 RIGOROUS, paper2 keeps current bound.")


if __name__ == "__main__":
    main()
