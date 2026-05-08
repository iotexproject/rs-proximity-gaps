"""Check structural decoupling for K=16 (8,8) kernel cases.

For each kernel f = f_u + alpha * f_v at L_2, check:
1. Does f_u alone vanish on S? (u-side individually rank-deficient)
2. Does f_v alone vanish on S? (v-side individually rank-deficient)
3. Is Zeros(f_u) ∩ L_2 = Zeros(f_v) ∩ L_2?

If both individually side-pure: kernel is decoupled → NOT primitive rank-2.
If neither individually side-pure: genuine primitive rank-2 candidate.

Hypothesis: 4/5 boundary cases are decoupled, 1/5 admissible case is not.
"""

from __future__ import annotations

import os
import random
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S


def split_kernel(c, rs):
    u_terms = [(r, c[j]) for j, r in enumerate(rs) if r % 4 in (0, 1)]
    v_terms = [(r, c[j]) for j, r in enumerate(rs) if r % 4 in (2, 3)]
    return u_terms, v_terms


def eval_at_S(terms, omega_L2, p, S):
    """Evaluate sum c_r * z^r at z=omega^s for each s in S."""
    return [sum(c_r * pow(omega_L2, r * s, p) for r, c_r in terms) % p for s in S]


def zeros_on_L2(terms, omega_L2, p, n2):
    """Find zeros of sum c_r * z^r on L_2 = mu_{n_2}."""
    return [s for s in range(n2) if sum(c_r * pow(omega_L2, r * s, p) for r, c_r in terms) % p == 0]


def main():
    n2, k2 = 32, 8
    p = 257
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]

    samples = sample_no_full_S(n2, k2, 500)
    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    rng = random.Random(0xDEADBEEF)
    n_u, n_v = 8, 8

    print("Decoupling check for K=16 (8,8) cases:")
    print("=" * 70)

    found = 0
    decoupled_count = 0
    primitive_count = 0
    for _ in range(50):
        if found >= 5:
            break
        u_cfg = rng.sample(u_side, n_u)
        v_cfg = rng.sample(v_side, n_v)
        rs = sorted(u_cfg + v_cfg)
        for S in samples[:50]:
            M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
            if rank_mod_p(M, p) < len(rs):
                c = kernel_mod_p(M, p)
                if c:
                    found += 1
                    u_terms, v_terms = split_kernel(c, rs)

                    fu_on_S = eval_at_S(u_terms, omega_L2, p, S)
                    fv_on_S = eval_at_S(v_terms, omega_L2, p, S)

                    fu_vanish_on_S = all(v == 0 for v in fu_on_S)
                    fv_vanish_on_S = all(v == 0 for v in fv_on_S)

                    Z_u = zeros_on_L2(u_terms, omega_L2, p, n2)
                    Z_v = zeros_on_L2(v_terms, omega_L2, p, n2)

                    print(f"\nCase {found}: rs={rs}")
                    print(f"  S={list(S)[:8]}...")
                    print(f"  f_u alone vanishes on S? {fu_vanish_on_S}")
                    print(f"  f_v alone vanishes on S? {fv_vanish_on_S}")
                    print(f"  |Zeros(f_u)| = {len(Z_u)}, |Zeros(f_v)| = {len(Z_v)}")
                    print(f"  Z(f_u) = Z(f_v)? {set(Z_u) == set(Z_v)}")
                    print(f"  S ⊆ Z(f_u)? {set(S).issubset(set(Z_u))}")
                    print(f"  S ⊆ Z(f_v)? {set(S).issubset(set(Z_v))}")
                    if fu_vanish_on_S and fv_vanish_on_S:
                        decoupled_count += 1
                        print(f"  ==> DECOUPLED (each side individually rank-def): NOT primitive")
                    else:
                        primitive_count += 1
                        print(f"  ==> NOT decoupled: genuine primitive rank-2 candidate")
                    break

    print(f"\n{'='*70}")
    print(f"Summary: {decoupled_count} decoupled / {primitive_count} primitive (out of {found} K=16 cases)")
    print(f"\nIf ALL boundary cases are decoupled, paper2's side-pure exclusion")
    print(f"(rank ≤ 1 each) covers them STRUCTURALLY -- no admissibility needed.")


if __name__ == "__main__":
    main()
