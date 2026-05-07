"""Action-orbit stabilization check per paper2 conj:sparse-worst admissibility (i).

For each K=16 (8,8) case at L_2=(32,8), use the proper L_0 lift
  L_2 position r -> L_0 position 4r + (r mod 4)
that respects post-fold-2 mod-4 classes.

For each pair (a, b) in the joint L_0 support, check if the support is closed
under translation by (b - a) mod n_0 (= cyclotomic subgroup orbit on L_0 = mu_{128}).

If ANY pair gives translation-invariance -> support is fixed pointwise by
<omega^{b-a}> -> case is action-stabilized -> excluded by paper2 admissibility (i).
"""

from __future__ import annotations

import os
import random
import sys
from math import gcd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S


def lift_to_L0(rs):
    """L_2 position r -> L_0 position 4*r + (r mod 4) (proper mod-4-respecting lift).

    Note: For r in u-side (r mod 4 in {0,1}), L_0 position has p mod 4 in {0,1}.
    For r in v-side (r mod 4 in {2,3}), L_0 position has p mod 4 in {2,3}.
    """
    return [4 * r + (r % 4) for r in rs]


def action_orbit_stabilized(L0_support, n0):
    """Check if L_0 support is closed under translation by (b - a) mod n_0
    for some pair (a, b) in support. Returns list of stabilizing differences.
    """
    support_set = set(L0_support)
    stabilizing_diffs = []
    seen_diffs = set()
    for a in L0_support:
        for b in L0_support:
            if a == b:
                continue
            d = (b - a) % n0
            if d == 0 or d in seen_diffs:
                continue
            seen_diffs.add(d)
            # Check if support + d (mod n0) == support
            shifted = {(p + d) % n0 for p in support_set}
            if shifted == support_set:
                orbit_size = n0 // gcd(d, n0)
                stabilizing_diffs.append((d, orbit_size))
    return stabilizing_diffs


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
    n_u, n_v = 8, 8

    print(f"Action-orbit check for K=16 (8,8) cases at L_2=(32,8) -> L_0=(128,32)")
    print(f"Using proper lift: L_2 r -> L_0 4r + (r mod 4)")
    print("=" * 70)

    found = 0
    stabilized_count = 0
    non_stabilized_cases = []

    for _ in range(50):
        if found >= 10:
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
                    L0_support = lift_to_L0(rs)
                    stab = action_orbit_stabilized(L0_support, n0)

                    print(f"\nCase {found}: rs={rs}")
                    print(f"  L_0 support: {sorted(L0_support)}")
                    print(f"  Stabilizing translations (d, orbit_size): {stab[:5]}")
                    if stab:
                        stabilized_count += 1
                        print(f"  ==> ACTION-STABILIZED (admissibility (i) excludes)")
                    else:
                        non_stabilized_cases.append(rs)
                        print(f"  ==> action-NON-stabilized (genuinely admissible)")
                    break

    print(f"\n{'='*70}")
    print(f"Summary: {stabilized_count}/{found} cases action-stabilized")
    print(f"Non-stabilized cases: {len(non_stabilized_cases)}")
    if non_stabilized_cases:
        for rs in non_stabilized_cases[:5]:
            print(f"  rs = {rs}")


if __name__ == "__main__":
    main()
