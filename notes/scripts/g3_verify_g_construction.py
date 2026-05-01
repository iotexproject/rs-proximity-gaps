"""g3_verify_g_construction.py — direct check Theorem 0146's g-construction on case (b).

For f(x) = c_19 x^19 + c_20 x^20 + c_23 x^23 (case (b) at q=1153):
  Theorem 0146 claims: ∃ g ∈ RS_8 (deg≤7) with dist(f, g) ≤ 16, hence f NOT strict above-J.

  Construction: g(x) = -c_19 x^3 - c_20 x^4 - c_23 x^7.

But empirically dist(f, RS_8) = 21 > 16. CONTRADICTION!

Verify directly: count agreements between f and g.
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations

from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def main():
    p = 1153
    n0, k0 = 32, 8
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L0_arr = np.array(L0, dtype=np.int64)

    pos_f = (19, 20, 23)
    coeffs_f = (153, 252, 208)

    fhat = [0] * n0
    for ps, c in zip(pos_f, coeffs_f):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)

    # g(x) = -c_19 x^3 - c_20 x^4 - c_23 x^7
    ghat = [0] * n0
    ghat[3] = (- coeffs_f[0]) % p   # -c_19
    ghat[4] = (- coeffs_f[1]) % p   # -c_20
    ghat[7] = (- coeffs_f[2]) % p   # -c_23
    g = evaluate_dft(ghat, L0, p)

    print(f"f: pos={pos_f}, coeffs={coeffs_f}")
    print(f"g: pos=(3,4,7), coeffs=({ghat[3]},{ghat[4]},{ghat[7]})")
    print()

    print(f"Position-by-position comparison f vs g on L_0:")
    print(f"{'i':<4} {'L_0[i]':<8} {'L_0[i]^16':<12} {'f(L_0[i])':<12} {'g(L_0[i])':<12} {'agree?':<8}")
    print("-" * 70)
    n_agree = 0
    for i in range(n0):
        x = L0[i]
        x16 = pow(x, 16, p)
        agree = f[i] == g[i]
        if agree:
            n_agree += 1
        print(f"{i:<4} {x:<8} {x16:<12} {f[i]:<12} {g[i]:<12} {'YES' if agree else 'no':<8}")

    print(f"\nTotal agreements: {n_agree}/{n0}")
    print(f"dist(f, g) = {n0 - n_agree}")
    print(f"Predicted by Thm 0146: dist ≤ 16. Empirical dist(f, C_0) was 21.")


if __name__ == "__main__":
    main()
