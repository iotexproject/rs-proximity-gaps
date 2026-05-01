"""g3_above_vs_at_J_compare.py — compare structural properties of:
  (87, 102, 103) — above-J at L_2 → K = 10 SATURATING
  (67, 90, 91)  — at-J at L_2 → K = 2q (pathological)

Both are Reverse Pattern at (128, 32). What makes one above-J the other at-J?

Look at:
  (a) Polynomial degrees on L_2 of c=(f_e)_o and d=(f_o)_o
  (b) Linear independence of c, d on L_2
  (c) Sign-character / cyclotomic structure (z^k where k|16)
  (d) Pencil c + α·d as α varies — what's the dist signature?
"""
import sys, os, random, time
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


def main():
    p = 257
    n0, k0 = 128, 32
    n1, k1 = 64, 16
    n2, k2 = 32, 8
    w_J_L2 = 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    test_cases = [
        ((87, 102, 103), "ABOVE-J K=10"),
        ((67, 90, 91), "AT-J K=2q"),
    ]

    for sup, label in test_cases:
        print(f"\n{'='*64}\n=== sup={sup} ({label}) ===\n{'='*64}")
        random.seed(2026 + hash(sup) % 1000)
        coefs = [random.randrange(1, p-1) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        # Compute DFT degrees on L_2 of (f_e)_o = c and (f_o)_o = d
        # By taking DFT of the L_2 function
        def dft_at_L2(arr):
            dft = []
            for k in range(n2):
                v = 0
                for i, z in enumerate(L2):
                    v = (v + int(arr[i]) * pow(int(z), -k, p)) % p
                dft.append(v)
            # divide by n_2
            inv_n2 = modinv(n2, p)
            return [(v * inv_n2) % p for v in dft]

        c_dft = dft_at_L2(fe_o)
        d_dft = dft_at_L2(fo_o)

        c_supp = [(j, c_dft[j]) for j in range(n2) if c_dft[j] != 0]
        d_supp = [(j, d_dft[j]) for j in range(n2) if d_dft[j] != 0]

        print(f"  c = (f_e)_o DFT supp on L_2 (positions, coefs):")
        for j, v in c_supp[:5]:
            print(f"    j={j}: {v}")
        print(f"  d = (f_o)_o DFT supp on L_2:")
        for j, v in d_supp[:5]:
            print(f"    j={j}: {v}")

        # Check sign-character: positions = n2/2 = 16 means z^16 = -1
        c_signchar = [j for j, _ in c_supp if 16 <= j and (j % 16 == 0 or j == 16)]
        d_signchar = [j for j, _ in d_supp if 16 <= j and (j % 16 == 0 or j == 16)]
        print(f"  c sign-char positions (j ≡ 16): {c_signchar}")
        print(f"  d sign-char positions (j ≡ 16): {d_signchar}")

        # Check linear dependence on L_2
        # c proportional to d? c[i] = λ·d[i] all i?
        nz_idx = next((i for i in range(n2) if int(fo_o[i]) != 0), None)
        if nz_idx is not None and int(fo_o[nz_idx]) != 0:
            d0 = int(fo_o[nz_idx])
            c0 = int(fe_o[nz_idx])
            lam = (c0 * modinv(d0, p)) % p
            proportional = all(
                (int(fe_o[i]) - lam * int(fo_o[i])) % p == 0
                for i in range(n2)
            )
            print(f"  Proportional? {proportional} (λ={lam})")

        # Probe pencil c + α·d at L_2 for many α
        print(f"\n  Pencil dist signature:")
        info_sets = list(combinations(range(n2), k2))
        # Sample 2000 if too many
        if len(info_sets) > 5000:
            rng = random.Random(2026)
            info_sets = rng.sample(info_sets, 5000)
        info_sets_arr = np.array(info_sets, dtype=np.int64)

        c_arr = np.array(fe_o, dtype=np.int64)
        d_arr = np.array(fo_o, dtype=np.int64)

        for alpha in [0, 1, 2, 3, 5, 7, 11, 13]:
            pv = (c_arr + alpha * d_arr) % p
            ext = batched_extras(info_sets_arr, pv, L2_arr, D2, inv_D2, p)
            d_pencil = n2 - k2 - int(ext.max())
            print(f"    α={alpha}: dist(pencil, RS_8) = {d_pencil}")

        # Compute z^16 on L_2 — check if relevant for our case
        z16_on_L2 = [pow(int(z), 16, p) for z in L2]
        print(f"\n  z^16 on L_2 (first 8): {z16_on_L2[:8]}")
        print(f"  Set: {set(z16_on_L2)} — sign character if {{1, p-1}}")


if __name__ == "__main__":
    main()
