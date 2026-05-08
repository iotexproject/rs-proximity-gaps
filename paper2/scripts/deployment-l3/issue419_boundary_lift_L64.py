"""Scale-uniform verification of Note 0460 Boundary-Lift Closure at L_2=(64, 16).

Test at L_2=(64, 16): for any kernel f at no-full |S|=32, |Zeros_{L_0}(f^(0))|
>= n_0/2 = 128 (where n_0 = 4*64 = 256, k_0 = 4*16 = 64).
"""

from __future__ import annotations

import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S


def count_zeros_L2(c, rs, p, omega_L2, n2):
    zeros = 0
    for s in range(n2):
        z = pow(omega_L2, s, p)
        v = sum(c[j] * pow(z, rs[j], p) for j in range(len(rs))) % p
        if v == 0:
            zeros += 1
    return zeros


def main():
    # L_2 = (64, 16), L_0 = (256, 64)
    # Need p with 256 | p-1. Smallest: p = 257 (256 = 2^8, 257 = 2^8 + 1).
    n2, k2 = 64, 16
    p = 257
    n0 = 256
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]

    samples = sample_no_full_S(n2, k2, 200)
    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    print(f"Theorem 0460 at L_2=({n2},{k2}): |Zeros_L2(f)| >= {n2//2}, |Zeros_L0| >= {n0//2}")
    print()

    rng = random.Random(0xDEADBEEF)
    # Try larger K where rank-def is more common
    # |S|=32 at L_2=(64,16); K > k_2=16 needed; K close to |S|=32 gives more rank-def
    test_K_parities = [(28, 14, 14), (30, 15, 15), (32, 16, 16)]

    total_cases = 0
    total_violations = 0

    for K, n_u, n_v in test_K_parities:
        print(f"=== K={K} cross-side ({n_u},{n_v}) at L_2=({n2},{k2}) ===")
        configs = []
        for _ in range(20):
            u_cfg = rng.sample(u_side, n_u)
            v_cfg = rng.sample(v_side, n_v)
            configs.append(sorted(u_cfg + v_cfg))

        case_count = 0
        violations = 0
        zero_counts = []

        for rs in configs:
            for S in samples[:30]:
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
                        if case_count > 30:
                            break
            if case_count > 30:
                break

        if zero_counts:
            min_z = min(zero_counts)
            max_z = max(zero_counts)
            print(f"  cases: {case_count}, violations: {violations}")
            print(f"  |Zeros_L2| min={min_z}, max={max_z}, theorem bound: >= {n2//2}")
            print(f"  |Zeros_L0| min={4*min_z}, theorem bound: >= {n0//2}")
        else:
            print(f"  no rank-def cases found")

        total_cases += case_count
        total_violations += violations
        print()

    print(f"=== SUMMARY ===")
    print(f"Total cases: {total_cases}, violations: {total_violations}")
    if total_violations == 0 and total_cases > 0:
        print(f"*** Theorem 0460 EMPIRICALLY HOLDS at L_2=({n2},{k2}) across {total_cases} cases ***")
        print(f"*** Scale-uniform verification SUCCESS ***")


if __name__ == "__main__":
    main()
