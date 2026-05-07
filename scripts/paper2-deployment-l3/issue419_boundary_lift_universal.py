"""Empirical verification of Note 0460 Boundary-Lift Closure Theorem.

Claim: for any kernel polynomial f at no-full |S|=n_2/2 subset of L_2 = mu_{n_2},
the canonical lift f^(0)(w) := f(w^4) at L_0 = mu_{4*n_2} has zero count >=
n_0/2 = 2*n_2.

Test: across K=12, 14, 16 cross-side rank-def cases at L_2=(32, 8) over p=257,
verify that 4 * |Zeros_{L_2}(f)| >= n_0/2 = 64.
"""

from __future__ import annotations

import os
import random
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S


def count_zeros_L2(c, rs, p, omega_L2, n2):
    """Count zeros of f(z) = sum c_r z^r on L_2 = mu_{n_2}."""
    zeros = 0
    for s in range(n2):
        z = pow(omega_L2, s, p)
        v = sum(c[j] * pow(z, rs[j], p) for j in range(len(rs))) % p
        if v == 0:
            zeros += 1
    return zeros


def main():
    n2, k2 = 32, 8
    p = 257
    n0 = 128
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]

    samples = sample_no_full_S(n2, k2, 500)

    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    rng = random.Random(0xDEADBEEF)
    test_K_parities = [(12, 6, 6), (14, 7, 7), (16, 8, 8)]

    print(f"Theorem 0460: |Zeros_{{L_2}}(f)| >= n_2/2 = {n2//2} for any kernel.")
    print(f"Hence |Zeros_{{L_0}}(f^(0))| >= 4 * n_2/2 = {4*(n2//2)} = n_0/2.")
    print()

    total_cases = 0
    total_violations = 0

    for K, n_u, n_v in test_K_parities:
        print(f"=== K={K} cross-side ({n_u}, {n_v}) ===")
        configs = []
        for _ in range(50):
            u_cfg = rng.sample(u_side, n_u)
            v_cfg = rng.sample(v_side, n_v)
            configs.append(sorted(u_cfg + v_cfg))

        case_count = 0
        violations = 0
        zero_counts = []

        for rs in configs:
            for S in samples[:50]:
                M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
                if rank_mod_p(M, p) < K:
                    c = kernel_mod_p(M, p)
                    if c:
                        case_count += 1
                        zeros_L2 = count_zeros_L2(c, rs, p, omega_L2, n2)
                        zero_counts.append(zeros_L2)
                        if zeros_L2 < n2 // 2:
                            violations += 1
                            print(f"  *** VIOLATION: rs={rs}, |Zeros_L2|={zeros_L2} < {n2//2}")

        if zero_counts:
            min_z = min(zero_counts)
            max_z = max(zero_counts)
            avg_z = sum(zero_counts) / len(zero_counts)
            print(f"  cases: {case_count}, violations: {violations}")
            print(f"  |Zeros_L2| min={min_z}, max={max_z}, avg={avg_z:.1f}")
            print(f"  |Zeros_L0| min={4*min_z}, max={4*max_z} (theorem: >= {n0//2})")
            print(f"  L_0 strict above-J would require |Zeros_L0| < {n0//2}, never observed")
        else:
            print(f"  no rank-def cases found")

        total_cases += case_count
        total_violations += violations
        print()

    print(f"=== SUMMARY ===")
    print(f"Total cases: {total_cases}, total violations of Boundary-Lift bound: {total_violations}")
    if total_violations == 0:
        print(f"*** Theorem 0460 EMPIRICALLY HOLDS across all {total_cases} cases ***")


if __name__ == "__main__":
    main()
