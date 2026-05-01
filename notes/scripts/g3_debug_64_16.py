"""g3_debug_64_16.py — debug case (b) at (64, 16). Verify each step manually."""
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
    n0, k0 = 64, 16
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2

    print(f"L_0[0..7] = {L0[:8]}")
    print(f"L_1[0..7] = {L1[:8]}")
    print(f"L_1[i+16] vs L_1[i]: {[L1[(i+16) % 32] for i in range(8)]}")

    # ω_2 = L_1[1]; check ω_2^32 = 1 and ω_2^16 = -1 mod p
    omega_2 = L1[1]
    print(f"\nω_2 = L_1[1] = {omega_2}")
    print(f"ω_2^16 mod {p} = {pow(omega_2, 16, p)}")
    print(f"ω_2^32 mod {p} = {pow(omega_2, 32, p)}")

    # For y ∈ L_1, when does y^16 = -1?
    print(f"\nFor each L_1[i], y^16 mod {p}:")
    for i in range(32):
        v = pow(L1[i], 16, p)
        print(f"  L_1[{i}] = {L1[i]:5d}, y^16 = {v}{'  (=−1 → odd-index T)' if v == p-1 else '  (=+1 → μ_16)'}")

    # Construct f with pos=(35, 36, 39), coeffs=(1, 1, 1)
    pos = (35, 36, 39)
    coeffs = (1, 1, 1)
    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    print(f"\nf_e on L_1: {f_e}")
    print(f"f_o on L_1: {f_o}")

    # DFT of f_e on L_1: should have support {18} (from L_0 pos 36)
    # Verify: f_e[i] = 1 * L_1[i]^18 mod p
    print(f"\nVerify f_e[i] = L_1[i]^18 mod p:")
    for i in range(8):
        expected = pow(L1[i], 18, p)
        print(f"  i={i}: f_e[i]={f_e[i]}, L_1[i]^18={expected}, match={f_e[i] == expected}")

    # For α=0, fold = f_e = y^18.
    # Check structural prediction: on T = {L_1[i] : i odd}, y^18 = -y^2
    print(f"\nFor α=0, structural prediction: f_e(y) = -y^2 on T (odd indices)")
    for i in [1, 3, 5, 7, 9]:
        actual = f_e[i]
        predicted = (- pow(L1[i], 2, p)) % p
        print(f"  i={i}: f_e[i]={actual}, -L_1[i]^2={predicted}, match={actual == predicted}")

    # If f_e = -y^2 on T, then the codeword Q(y) = -y^2 should agree with f_e on T (16 positions).
    # Compute Q on full L_1 and check agreement.
    Q = [(- pow(L1[i], 2, p)) % p for i in range(n1)]
    print(f"\nCodeword Q(y) = -y^2 on L_1: {Q[:8]}...")
    agreements = sum(1 for i in range(n1) if Q[i] == f_e[i])
    print(f"Agreements between Q and f_e: {agreements}/32")

    odd_idx = [i for i in range(n1) if i % 2 == 1]
    even_idx = [i for i in range(n1) if i % 2 == 0]
    odd_match = sum(1 for i in odd_idx if Q[i] == f_e[i])
    even_match = sum(1 for i in even_idx if Q[i] == f_e[i])
    print(f"  agreements on odd indices: {odd_match}/16")
    print(f"  agreements on even indices: {even_match}/16")


if __name__ == "__main__":
    main()
