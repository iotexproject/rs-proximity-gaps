"""Empirical total-K survey for stratum (B) admissible cases.

For each K=12, 14, 16 cross-side rank-def case at L_2=(32,8) over p=257:
1. Classify case as (A), (B), or (C) per Note 0461.
2. For (B) cases: compute K_lb via 0 codeword + BW K_BW for additional alphas.
3. Verify K_lb + K_BW ≤ 10 empirically across all cases.
"""

from __future__ import annotations

import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S
from issue419_K16_K_count import split_kernel, evaluate_at_L0, hamming_zero
from issue419_case3_BW_total_K import berlekamp_welch, poly_div


def zeros_on_L2(terms, omega_L2, p, n2):
    return [s for s in range(n2) if sum(c_r * pow(omega_L2, r * s, p) for r, c_r in terms) % p == 0]


def stratify(c, rs, p, omega_L2, n2):
    """Classify as (A), (B), or (C)."""
    u_terms, v_terms = split_kernel(c, rs)
    Z_u = set(zeros_on_L2(u_terms, omega_L2, p, n2))
    Z_v = set(zeros_on_L2(v_terms, omega_L2, p, n2))
    T = Z_u & Z_v
    if Z_u != Z_v:
        return 'C', len(T), len(Z_u), len(Z_v)
    if len(T) >= n2 // 2:
        return 'A', len(T), len(Z_u), len(Z_v)
    return 'B', len(T), len(Z_u), len(Z_v)


def main():
    n2, k2 = 32, 8
    p = 257
    n0, k0 = 128, 32
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]
    L0 = subgroup(n0, p)
    omega_L0 = L0[1]

    samples = sample_no_full_S(n2, k2, 1000)  # larger sample
    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    rng = random.Random(0xC0FFEE)
    threshold = 64
    t_BW = (n0 - k0) // 2

    test_K_parities = [(12, 6, 6), (14, 7, 7), (16, 8, 8)]

    all_K_counts = []

    for K, n_u, n_v in test_K_parities:
        print(f"\n=== K={K} cross-side ({n_u}, {n_v}) ===")
        configs = []
        for _ in range(100):
            u_cfg = rng.sample(u_side, n_u)
            v_cfg = rng.sample(v_side, n_v)
            configs.append(sorted(u_cfg + v_cfg))

        case_count = 0
        stratum_counts = {'A': 0, 'B': 0, 'C': 0}
        max_K_lb = 0
        max_K_BW = 0
        for rs in configs:
            for S in samples[:80]:
                M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
                if rank_mod_p(M, p) < len(rs):
                    c = kernel_mod_p(M, p)
                    if c:
                        case_count += 1
                        if case_count > 30:  # limit per K parity
                            break

                        stratum, T_size, Zu_size, Zv_size = stratify(c, rs, p, omega_L2, n2)
                        stratum_counts[stratum] += 1

                        # Compute K_lb via 0 codeword
                        u_terms, v_terms = split_kernel(c, rs)
                        f1 = evaluate_at_L0(u_terms, omega_L0, p, n0)
                        f2 = evaluate_at_L0(v_terms, omega_L0, p, n0)

                        K_lb = 0
                        K_BW = 0
                        for alpha in range(p):
                            g = [(f1[i] + alpha * f2[i]) % p for i in range(n0)]
                            agr = hamming_zero(g, p)
                            if agr > threshold:
                                K_lb += 1
                            # BW
                            result = berlekamp_welch(g, omega_L0, p, n0, k0, t_BW)
                            if result is not None:
                                Q, E = result
                                quot, rem = poly_div(Q, E, p)
                                if all(r % p == 0 for r in rem):
                                    deg_q = len(quot)
                                    while deg_q > 0 and quot[deg_q-1] % p == 0:
                                        deg_q -= 1
                                    if deg_q <= k0:
                                        K_BW += 1

                        max_K_lb = max(max_K_lb, K_lb)
                        max_K_BW = max(max_K_BW, K_BW)
                        all_K_counts.append((K, stratum, T_size, K_lb, K_BW))
                        if K_lb + K_BW > 10:
                            print(f"  *** K_lb + K_BW = {K_lb + K_BW} > 10! "
                                  f"(K_lb={K_lb}, K_BW={K_BW}) rs={rs}")

            if case_count > 30:
                break

        print(f"  Cases: {case_count}, Strata: {stratum_counts}")
        print(f"  Max K_lb (via 0 cw, agreement > {threshold}): {max_K_lb}")
        print(f"  Max K_BW (BW-decoded): {max_K_BW}")

    print(f"\n=== SUMMARY ===")
    print(f"Total cases analyzed: {len(all_K_counts)}")
    max_K_lb_overall = max(x[3] for x in all_K_counts) if all_K_counts else 0
    max_K_BW_overall = max(x[4] for x in all_K_counts) if all_K_counts else 0
    print(f"Max K_lb across all cases: {max_K_lb_overall}")
    print(f"Max K_BW across all cases: {max_K_BW_overall}")
    print(f"All K_lb <= 10? {all(x[3] <= 10 for x in all_K_counts)}")
    print(f"All K_BW <= 10? {all(x[4] <= 10 for x in all_K_counts)}")
    print(f"All K_lb + K_BW <= 10? {all(x[3] + x[4] <= 10 for x in all_K_counts)}")
    max_sum = max((x[3] + x[4] for x in all_K_counts), default=0)
    print(f"Max K_lb + K_BW across all cases: {max_sum}")
    print(f"\nNote: K_lb counts agreement > Johnson with 0 codeword.")
    print(f"K_BW counts unique-decoded codewords (agreement >= 80 = n_0 - t).")
    print(f"True K(f_1,f_2;delta_J+eps) is bounded above by sum + list-decoding contribution.")


if __name__ == "__main__":
    main()
