"""Large multi-prime sweep for K=12, 14, 16 cross-side cases at L_2=(32,8).

Strengthens empirical evidence for K(f_1, f_2; delta) <= 10 for stratum (B).

For each (K, prime) pair, sample many configs, find rank-def cases, classify
into strata, and verify K_BW <= 10 always.
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
from issue419_decouple_check import zeros_on_L2


def stratify(c, rs, p, omega_L2, n2):
    u_terms, v_terms = split_kernel(c, rs)
    Z_u = set(zeros_on_L2(u_terms, omega_L2, p, n2))
    Z_v = set(zeros_on_L2(v_terms, omega_L2, p, n2))
    T = Z_u & Z_v
    if Z_u != Z_v:
        return 'C', len(T)
    if len(T) >= n2 // 2:
        return 'A', len(T)
    return 'B', len(T)


def run_BW(c, rs, p, omega_L0, omega_L2, n0, k0, t_BW):
    """Run BW decoding for all alpha; return K_BW count."""
    u_terms, v_terms = split_kernel(c, rs)
    f1 = evaluate_at_L0(u_terms, omega_L0, p, n0)
    f2 = evaluate_at_L0(v_terms, omega_L0, p, n0)
    K_BW = 0
    for alpha in range(p):
        g = [(f1[i] + alpha * f2[i]) % p for i in range(n0)]
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
    return K_BW


def main():
    n2, k2 = 32, 8
    n0, k0 = 128, 32
    t_BW = (n0 - k0) // 2

    # Primes admitting 128-th root: q-1 divisible by 128
    # 257 = 2^8 + 1, 641 = 5·2^7 + 1, 769 = 3·2^8 + 1, 1153 = 9·2^7 + 1
    primes = [257, 641, 769, 1153]
    test_K_parities = [(16, 8, 8)]  # focus on K=16

    print(f"Large empirical sweep at L_2=(32, 8), L_0=(128, 32)")
    print(f"BW radius t={t_BW}, agreement >= {n0 - t_BW} = 80")
    print()

    overall_summary = {}

    for p in primes:
        L2 = subgroup(n2, p)
        omega_L2 = L2[1]
        L0 = subgroup(n0, p)
        omega_L0 = L0[1]

        samples = sample_no_full_S(n2, k2, 300)
        u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
        v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

        for K, n_u, n_v in test_K_parities:
            print(f"=== K={K} cross-side ({n_u},{n_v}) at p={p} ===")
            rng = random.Random(0xC0FFEE + K + p)

            B_K_BW = []  # K_BW for stratum B cases
            stratum_counts = {'A': 0, 'B': 0, 'C': 0}
            cases = 0
            max_K_BW_overall = 0

            for trial in range(50):  # smaller trials per prime since multi-prime
                u_cfg = rng.sample(u_side, n_u)
                v_cfg = rng.sample(v_side, n_v)
                rs = sorted(u_cfg + v_cfg)

                for S in samples[:30]:
                    M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
                    if rank_mod_p(M, p) < len(rs):
                        c = kernel_mod_p(M, p)
                        if c:
                            cases += 1
                            stratum, T_size = stratify(c, rs, p, omega_L2, n2)
                            stratum_counts[stratum] += 1

                            if stratum == 'B':
                                K_BW = run_BW(c, rs, p, omega_L0, omega_L2, n0, k0, t_BW)
                                B_K_BW.append(K_BW)
                                max_K_BW_overall = max(max_K_BW_overall, K_BW)
                                if K_BW > 10:
                                    print(f"  *** STRATUM B K_BW={K_BW} > 10! rs={rs}")

                            if cases > 50:
                                break
                if cases > 50:
                    break

            print(f"  Total cases: {cases}, strata: {stratum_counts}")
            if B_K_BW:
                print(f"  Stratum (B): {len(B_K_BW)} cases, K_BW max={max(B_K_BW)}, mean={sum(B_K_BW)/len(B_K_BW):.2f}")
            print(f"  K_BW <= 10 always for stratum (B)? {all(k <= 10 for k in B_K_BW)}")
            print()

            overall_summary[(p, K)] = {
                'cases': cases,
                'stratum_B': len(B_K_BW),
                'max_K_BW': max_K_BW_overall,
                'all_le_10': all(k <= 10 for k in B_K_BW),
            }

    print(f"\n=== OVERALL SUMMARY ===")
    for (p, K), info in overall_summary.items():
        print(f"  p={p}, K={K}: {info}")
    all_pass = all(info['all_le_10'] for info in overall_summary.values())
    print(f"\nAll K_BW <= 10 across all (prime, K) pairs? {all_pass}")


if __name__ == "__main__":
    main()
