"""g3_pattern_A_alpha2star.py — for sup=(9, 11, 20) (paradigmatic mixed-parity):
explicitly compute α_2* = -(c_9·s_9) / (c_11·s_11) where s_j is the
DFT-to-L_2 transfer scalar, and verify fold²(α_1, α_2*) is a single-monomial
c_{20}·z^5 on L_2 for ALL α_1, hence saturating column at α_2*.
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations

from fri_2round_attack import setup_chain, even_odd_parts, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def dft_inverse(f, L, p):
    """Compute DFT coefficients ĉ[k] = sum_i f[i] · ω^{-ki} / n.
    Returns array of length n."""
    n = len(f)
    inv_n = modinv(n, p)
    fhat = [0]*n
    for k in range(n):
        v = 0
        for i in range(n):
            v = (v + f[i] * pow(L[i], -k, p)) % p
        fhat[k] = (v * inv_n) % p
    return fhat


def main():
    p = 97
    n0, k0, R = 32, 8, 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L2 = 4

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    # Use sup=(9, 11, 20) with seeded coefs from the sweep
    sup = (9, 11, 20)
    sup_rng = random.Random(hash(sup) & 0xFFFFFFFF)
    coefs = [sup_rng.randrange(1, 10**6) for _ in range(3)]
    fhat = [0]*n0
    for j, c in zip(sup, coefs): fhat[j] = c % p

    print(f"=== Pattern A α_2* mechanism for sup={sup} ===")
    print(f"  c_9={fhat[9]}, c_11={fhat[11]}, c_20={fhat[20]}")
    print(f"  parities: 9-odd, 11-odd, 20-even (mixed parity ✓)")
    print(f"  mod 4: 9≡1, 11≡3, 20≡0")
    print(f"  L_2 destinations:")
    print(f"    j=9  (≡1 mod 4) → (f_o)_e on L_2 at pos (9-1)/4 = 2")
    print(f"    j=11 (≡3 mod 4) → (f_o)_o on L_2 at pos (11-3)/4 = 2")
    print(f"    j=20 (≡0 mod 4) → (f_e)_e on L_2 at pos 20/4 = 5")

    # Compute f, f_e, f_o, then on L_1: (f_e), (f_o)
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)

    # On L_1: f_o evaluated at L_1 positions. Compute its DFT on L_1.
    fo_dft_L1 = dft_inverse(f_o, L1, p)
    fe_dft_L1 = dft_inverse(f_e, L1, p)
    print(f"\n  f_e on L_1 DFT: nonzero indices: {[(k, fe_dft_L1[k]) for k in range(n1) if fe_dft_L1[k]]}")
    print(f"  f_o on L_1 DFT: nonzero indices: {[(k, fo_dft_L1[k]) for k in range(n1) if fo_dft_L1[k]]}")

    # Now even-odd split f_o on L_1 → (f_o)_e, (f_o)_o on L_2
    fo_e_L2, fo_o_L2 = even_odd_parts(f_o, L1, p)
    fe_e_L2, fe_o_L2 = even_odd_parts(f_e, L1, p)

    # DFT on L_2
    fo_e_dft_L2 = dft_inverse(fo_e_L2, L2, p)
    fo_o_dft_L2 = dft_inverse(fo_o_L2, L2, p)
    fe_e_dft_L2 = dft_inverse(fe_e_L2, L2, p)
    fe_o_dft_L2 = dft_inverse(fe_o_L2, L2, p)

    print(f"\n  L_2 DFT supports:")
    print(f"    (f_o)_e: {[(k, fo_e_dft_L2[k]) for k in range(n2) if fo_e_dft_L2[k]]}")
    print(f"    (f_o)_o: {[(k, fo_o_dft_L2[k]) for k in range(n2) if fo_o_dft_L2[k]]}")
    print(f"    (f_e)_e: {[(k, fe_e_dft_L2[k]) for k in range(n2) if fe_e_dft_L2[k]]}")
    print(f"    (f_e)_o: {[(k, fe_o_dft_L2[k]) for k in range(n2) if fe_o_dft_L2[k]]}")

    # The α_2* is at shared L_2 pos = 2 (where (f_o)_e and (f_o)_o both have coefs)
    pos_shared = 2
    s_9 = fo_e_dft_L2[pos_shared]   # transfer of c_9 to L_2 pos 2
    s_11 = fo_o_dft_L2[pos_shared]  # transfer of c_11 to L_2 pos 2

    print(f"\n  At shared L_2 pos {pos_shared}:")
    print(f"    (f_o)_e@{pos_shared} = {s_9}  (← from c_9 = {fhat[9]})")
    print(f"    (f_o)_o@{pos_shared} = {s_11} (← from c_11 = {fhat[11]})")

    inv_s11 = modinv(s_11, p)
    alpha2_star = (-s_9 * inv_s11) % p
    print(f"  α_2* = -(f_o)_e@{pos_shared} / (f_o)_o@{pos_shared} = {alpha2_star}")

    # Verify: at α_2 = α_2*, fold²(α_1, α_2*) DFT should have NO mass at pos 2,
    # only mass at pos 5
    print(f"\n  Verification at α_2 = α_2* = {alpha2_star}:")
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)
    sat_count = 0
    for a1 in [0, 1, 5, 13, 50, 96]:
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        fold1_e_l2, fold1_o_l2 = even_odd_parts(fold1_arr.tolist(), L1, p)
        fold2 = [(fold1_e_l2[i] + alpha2_star * fold1_o_l2[i]) % p for i in range(n2)]
        fold2_dft = dft_inverse(fold2, L2, p)
        nz = [(k, fold2_dft[k]) for k in range(n2) if fold2_dft[k]]
        f2_arr = np.array(fold2, dtype=np.int64)
        extras = batched_extras(info_sets_n2, f2_arr, L2_arr, D2, inv_D2, p)
        d2 = n2 - k2 - int(extras.max())
        bad = "BAD" if d2 <= w_J_L2 else "good"
        if bad == "BAD": sat_count += 1
        print(f"    α_1={a1}: fold² DFT support = {nz}, d_2 = {d2} ({bad})")

    # Now over all α_1, count bad
    bad_at_star = 0
    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        fold1_e_l2, fold1_o_l2 = even_odd_parts(fold1_arr.tolist(), L1, p)
        fold2 = [(fold1_e_l2[i] + alpha2_star * fold1_o_l2[i]) % p for i in range(n2)]
        f2_arr = np.array(fold2, dtype=np.int64)
        extras = batched_extras(info_sets_n2, f2_arr, L2_arr, D2, inv_D2, p)
        d2 = n2 - k2 - int(extras.max())
        if d2 <= w_J_L2: bad_at_star += 1
    print(f"\n  Total bad α_1's at α_2*: {bad_at_star}/{p}")
    print(f"  → α_2* is {'SATURATING' if bad_at_star == p else f'partial ({bad_at_star})'}")


if __name__ == "__main__":
    main()
