"""Empirical verification for Note 0458.

For K=16 (8,8) cross-side random no-full S rank-def cases at L_2=(32,8):
take the kernel polynomial f and lift to L_0 = (128, 32) via f^(0)(w) := f(w^4).
Verify Δ(f^(0), 0) = 64 = Johnson at L_0, NOT strictly above.

Also check Δ(f^(0), C_0) (distance to nearest C_0 codeword) by brute-force
RS decoding via Berlekamp-Welch / agreement counting on small candidates.
For a quick sanity test, just check: # positions where f^(0)(w) = 0.
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


def lift_kernel_to_L0(c, rs, p, omega_L0):
    """Given kernel f(z) = sum c_r z^r at L_2 = mu_{n_2}, with n_2 = 32,
    construct f^(0)(w) := f(w^4) at L_0 = mu_{128}.
    Returns the values [f^(0)(omega_L0^i) for i in range(128)].
    """
    n0 = 128
    K = len(rs)
    values = []
    for i in range(n0):
        w = pow(omega_L0, i, p)  # w in mu_{128}
        z = pow(w, 4, p)         # z = w^4 in mu_{32}
        # f(z) = sum c_r * z^r
        v = 0
        for j in range(K):
            v = (v + c[j] * pow(z, rs[j], p)) % p
        values.append(v)
    return values


def hamming_weight(values, p):
    return sum(1 for v in values if v % p != 0)


def main():
    n2, k2 = 32, 8
    p = 257  # need p with 128 | p-1; 257 = 2^8 + 1 works
    n0 = 128
    k0 = 32
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]
    L0 = subgroup(n0, p)
    omega_L0 = L0[1]

    # sanity: omega_L0^4 should be omega_L2 (or some primitive 32-th root)
    assert pow(omega_L0, 4, p) == omega_L2 or pow(pow(omega_L0, 4, p), 8, p) == 1

    samples = sample_no_full_S(n2, k2, 500)

    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    rng = random.Random(0xDEADBEEF)
    n_u, n_v = 8, 8

    # Find one K=16 (8,8) rank-def case
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

    print(f"Found {len(found_cases)} K=16 (8,8) rank-def cases at L_2=(32,8)")
    print(f"L_2 Johnson agreement = sqrt(n_2 * k_2) = sqrt({n2}*{k2}) = {int((n2*k2)**0.5)}")
    print(f"L_0 Johnson agreement = sqrt(n_0 * k_0) = sqrt({n0}*{k0}) = {int((n0*k0)**0.5)}")
    print()

    for idx, (rs, S, c) in enumerate(found_cases):
        # Verify f vanishes on S at L_2
        verify_count = 0
        for s in S:
            v = sum(c[j] * pow(omega_L2, rs[j] * s, p) for j in range(len(rs))) % p
            if v == 0:
                verify_count += 1
        print(f"Case {idx+1}: rs={rs}")
        print(f"  |S|={len(S)}, f vanishes on {verify_count}/{len(S)} of S at L_2")

        # Lift to L_0
        f0_values = lift_kernel_to_L0(c, rs, p, omega_L0)
        zeros_L0 = n0 - hamming_weight(f0_values, p)
        agreement_with_zero = zeros_L0
        disagreement_with_zero = n0 - zeros_L0

        print(f"  Lift f^(0)(w)=f(w^4) at L_0=mu_128: ")
        print(f"    zeros = {zeros_L0} (expected {4*len(S)} = 4*|S|)")
        print(f"    agreement with zero codeword = {agreement_with_zero}")
        print(f"    disagreement = {disagreement_with_zero}")
        print(f"    Johnson agreement = 64; strictly above-J requires agreement > 64")
        if agreement_with_zero > 64:
            print(f"    *** STRICTLY ABOVE JOHNSON ***")
        elif agreement_with_zero == 64:
            print(f"    AT Johnson boundary -- excluded by paper2 (ii).")
        else:
            print(f"    Below Johnson.")
        print()


if __name__ == "__main__":
    main()
