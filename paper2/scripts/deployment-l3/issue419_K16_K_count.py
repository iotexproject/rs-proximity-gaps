"""K-count check for K=16 (8,8) cross-side cases.

For each K=16 case, lift to (f_1, f_2) at L_0=(128,32):
  f_1(w) = sum_{r in u-side rs} c_r * w^{4r}     (u-side lift)
  f_2(w) = sum_{r in v-side rs} c_r * w^{4r}     (v-side lift)

For alpha in F_p, compute g_alpha(w) := f_1(w) + alpha * f_2(w).
Count K_lb := #{alpha : agreement(g_alpha, 0) >= Johnson agreement = 64}.

K_lb is a LOWER bound on K(f_1, f_2; delta_J) since 0 in C_0.
If K_lb > 10: candidate refutation of conj:sparse-worst.
If K_lb <= 10: residual not threatening.
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


def split_kernel(c, rs):
    """Split kernel into u-side and v-side."""
    u_terms = []
    v_terms = []
    for j, r in enumerate(rs):
        if r % 4 in (0, 1):
            u_terms.append((r, c[j]))
        else:
            v_terms.append((r, c[j]))
    return u_terms, v_terms


def evaluate_at_L0(terms, omega_L0, p, n0=128):
    """Compute [sum c_r * w^{4r} for w in L_0] for terms = [(r, c_r), ...]."""
    values = [0] * n0
    for i in range(n0):
        w = pow(omega_L0, i, p)
        v = 0
        for r, c_r in terms:
            v = (v + c_r * pow(w, 4 * r, p)) % p
        values[i] = v
    return values


def hamming_zero(values, p):
    return sum(1 for v in values if v % p == 0)


def main():
    n2, k2 = 32, 8
    p = 257
    n0 = 128
    k0 = 32
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]
    L0 = subgroup(n0, p)
    omega_L0 = L0[1]

    samples = sample_no_full_S(n2, k2, 500)

    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    rng = random.Random(0xDEADBEEF)
    n_u, n_v = 8, 8

    found_cases = []
    for _ in range(50):
        if len(found_cases) >= 5:
            break
        u_cfg = rng.sample(u_side, n_u)
        v_cfg = rng.sample(v_side, n_v)
        rs = sorted(u_cfg + v_cfg)
        for S in samples[:50]:
            M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
            if rank_mod_p(M, p) < len(rs):
                c = kernel_mod_p(M, p)
                if c:
                    found_cases.append((rs, S, c))
                    break

    print(f"Found {len(found_cases)} K=16 (8,8) rank-def cases at L_2=(32,8), p={p}")
    print(f"L_0 Johnson agreement = sqrt({n0}*{k0}) = 64")
    print()

    threshold = 64

    for idx, (rs, S, c) in enumerate(found_cases):
        u_terms, v_terms = split_kernel(c, rs)
        print(f"Case {idx+1}: |u-side|={len(u_terms)}, |v-side|={len(v_terms)}")

        f1_vals = evaluate_at_L0(u_terms, omega_L0, p, n0)
        f2_vals = evaluate_at_L0(v_terms, omega_L0, p, n0)

        # Admissibility check: Δ(f_i, 0) at L_0
        agr_f1 = hamming_zero(f1_vals, p)
        agr_f2 = hamming_zero(f2_vals, p)
        print(f"  agreement(f_1, 0) = {agr_f1}; agreement(f_2, 0) = {agr_f2}")
        print(f"  Strictly above-J at f_i (agr > {threshold})? "
              f"f_1: {agr_f1 > threshold}, f_2: {agr_f2 > threshold}")
        # joint agreement with (0, 0): #{w : f_1(w)=0 AND f_2(w)=0}
        joint_agree = sum(1 for i in range(n0) if f1_vals[i] % p == 0 and f2_vals[i] % p == 0)
        print(f"  joint agreement with (0,0) = {joint_agree}")
        print(f"  joint disagreement = {n0 - joint_agree}")
        print(f"  Strictly above-J jointly (Δ_joint > 64)? {n0 - joint_agree > threshold}")

        # K_count at various thresholds
        agreements = []
        for alpha in range(p):
            g = [(f1_vals[i] + alpha * f2_vals[i]) % p for i in range(n0)]
            zeros = hamming_zero(g, p)
            agreements.append(zeros)

        max_agr = max(agreements)
        K_at_J = sum(1 for a in agreements if a >= threshold)
        K_strict = sum(1 for a in agreements if a > threshold)

        print(f"  max agreement(g_alpha, 0) = {max_agr}")
        print(f"  #alpha with agreement >= 64 (Johnson or above) = {K_at_J}")
        print(f"  #alpha with agreement >  64 (strictly above Johnson) = {K_strict}")
        agr_counts = Counter(agreements)
        top_5 = sorted(agr_counts.items(), key=lambda x: -x[0])[:5]
        print(f"  top-5 (agreement, count): {top_5}")
        print()

    # Summary
    print(f"\nSummary: K_lb is a LOWER BOUND on K(f_1, f_2; delta_J). If K_lb > 10:")
    print(f"  candidate refutation of conj:sparse-worst.")
    print(f"If K_lb <= 10: residual likely not threatening to paper2.")


if __name__ == "__main__":
    main()
