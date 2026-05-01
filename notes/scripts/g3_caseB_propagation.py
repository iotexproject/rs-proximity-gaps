"""g3_caseB_propagation.py — case (b) is closed under FRI folding.

Test: take case-(b) f at L_0 with DFT supp ⊂ {16..23}, n_0=32.
For each (α_1, α_2) pair: compute fold_α_1 on L_1, then fold_{α_1, α_2} on L_2.
Verify dist at each level is ≤ Johnson radius.

R=3 rounds: L_0 (32, 8) → L_1 (16, 4) → L_2 (8, 2) → L_3 (4, 1).
"""
import sys, os, random
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


def dist_to_rs(f_arr, L_arr, n, k, D, inv_D, p):
    info_sets = list(combinations(range(n), k))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    extras = batched_extras(info_sets_arr, f_arr, L_arr, D, inv_D, p)
    return n - k - int(extras.max())


def dft_support(f_vec, L, p):
    """Compute DFT support of f given by values on L."""
    n = len(L)
    # Inverse DFT: for L = μ_n, hat_f[j] = (1/n) Σ_i f[i] · ω^{-ij}
    # We just need to find which positions have nonzero coefficient.
    # f[i] = Σ_j hat_f[j] · L[i]^j → solve for hat_f.
    # Use Lagrange or matrix inversion. For simplicity, compute via DFT formula.
    omega = L[1]  # primitive n-th root
    inv_n = pow(n, p - 2, p)
    hat = []
    for j in range(n):
        v = 0
        for i in range(n):
            v = (v + f_vec[i] * pow(L[i], -j % (p-1), p)) % p
        v = (v * inv_n) % p
        if v != 0:
            hat.append((j, v))
    return hat


def main():
    p = 1153
    n0, k0 = 32, 8

    chain = setup_chain(p, n0, k0, R=3)
    L0 = chain[0][0]; L0_arr = np.array(L0, dtype=np.int64)
    L1 = chain[1][0]; L1_arr = np.array(L1, dtype=np.int64)
    L2 = chain[2][0]; L2_arr = np.array(L2, dtype=np.int64)
    L3 = chain[3][0]; L3_arr = np.array(L3, dtype=np.int64)
    n1, k1 = len(L1), k0 // 2  # 16, 4
    n2, k2 = len(L2), k1 // 2  # 8, 2
    n3, k3 = len(L3), k2 // 2  # 4, 1
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    D3, inv_D3 = precompute_diff_inv(L3_arr, p)
    print(f"L_0 size={n0}, L_1 size={n1}, L_2 size={n2}, L_3 size={n3}")
    print(f"k_0={k0}, k_1={k1}, k_2={k2}, k_3={k3}")
    print(f"Johnson radii: w_J(L_0)={n0-int(np.sqrt(k0*n0))}, w_J(L_1)={n1-int(np.sqrt(k1*n1))}, w_J(L_2)={n2-int(np.sqrt(k2*n2))}, w_J(L_3)={n3-int(np.sqrt(k3*n3))}")
    print()

    # Construct case-(b) f at L_0
    pos = (19, 20, 23)
    coeffs = (1, 1, 1)
    fhat = [0] * n0
    for ps, c in zip(pos, coeffs):
        fhat[ps] = c
    f = evaluate_dft(fhat, L0, p)

    print(f"f: pos={pos}, coeffs={coeffs}")

    rng = random.Random(2026)
    n_alpha_trials = 5

    for trial in range(n_alpha_trials):
        a1 = rng.randint(0, p-1)
        a2 = rng.randint(0, p-1)

        # Round 1: L_0 → L_1 with α_1
        f_e, f_o = even_odd_parts(f, L0, p)
        fold1 = [(f_e[i] + a1 * f_o[i]) % p for i in range(n1)]
        fold1_arr = np.array(fold1, dtype=np.int64)
        d_l1 = dist_to_rs(fold1_arr, L1_arr, n1, k1, D1, inv_D1, p)

        # Round 2: L_1 → L_2 with α_2
        fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
        fold2 = [(fold1_e[i] + a2 * fold1_o[i]) % p for i in range(n2)]
        fold2_arr = np.array(fold2, dtype=np.int64)
        d_l2 = dist_to_rs(fold2_arr, L2_arr, n2, k2, D2, inv_D2, p)

        print(f"  α_1={a1:5d}, α_2={a2:5d}: dist on L_1 = {d_l1} (J={n1-int(np.sqrt(k1*n1))}), dist on L_2 = {d_l2} (J={n2-int(np.sqrt(k2*n2))})")

    print()
    print(f"Conclusion: if case-(b) is closed under folding, dist on L_1 always ≤ {n1-int(np.sqrt(k1*n1))} and dist on L_2 always ≤ {n2-int(np.sqrt(k2*n2))}.")


if __name__ == "__main__":
    main()
