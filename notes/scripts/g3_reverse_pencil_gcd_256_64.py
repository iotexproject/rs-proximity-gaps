"""g3_reverse_pencil_gcd_256_64.py — characterize gcd_min of Reverse-Pattern pencils at (256, 64).

For each 3-pos Reverse support (s_0, s_1, s_2) with all s_i mod 4 in {2, 3}:
- compute c = (f_e)_o, d = (f_o)_o on L_2
- find DFT supports of c, d on L_2 (each should be 1 position → pencil (a, b))
- compute gcd(b - a, n_2) where n_2 = 64
- tally gcd distribution

Goal: find gcd_min over all Reverse supports. If gcd_min ≥ 4, then orbit ≤ 16,
K ≤ 18 under Conjecture E (rigorous prize bound at (256, 64)).
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def find_dft_supp(arr, L_subgroup, p):
    """DFT-on-subgroup support. Returns list of (position, value)."""
    n = len(L_subgroup)
    n_inv = pow(n, p-2, p)
    supp = []
    for k in range(n):
        v = 0
        for i, z in enumerate(L_subgroup):
            v = (v + int(arr[i]) * pow(int(z), -k, p)) % p
        v = v * n_inv % p
        if v != 0:
            supp.append((k, v))
    return supp


def main():
    p = 257
    n0, k0 = 256, 64
    n1, k1 = 128, 32
    n2, k2 = 64, 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]

    # Reverse Pattern: positions mod 4 ∈ {2, 3}
    pos_set = [j for j in range(n0) if j % 4 in (2, 3)]
    print(f"Reverse positions in L_0: {len(pos_set)} (out of {n0})")

    # Sample 2000 triples to make this manageable
    rng = random.Random(2026)
    all_triples = list(combinations(pos_set, 3))
    rng.shuffle(all_triples)
    sample_triples = all_triples[:2000]
    print(f"Sample {len(sample_triples)} triples out of {len(all_triples)} total")

    # For each, compute pencil and gcd
    gcd_dist = {}
    pencil_dist = {}
    one_pos_count = 0
    multi_pos_count = 0

    # Use random coefficients (don't matter for support structure if we only care about positions)
    # Actually they do matter — let's use generic coefs
    for idx, sup in enumerate(sample_triples):
        # Use coefs that won't trigger degenerate cancellation
        coefs = [(idx*7 + 1) % (p-1) + 1, (idx*11 + 3) % (p-1) + 1, (idx*13 + 5) % (p-1) + 1]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        c_arr = fe_o  # "odd part of even part" on L_2
        d_arr = fo_o  # "odd part of odd part" on L_2

        c_supp = find_dft_supp(c_arr, L2, p)
        d_supp = find_dft_supp(d_arr, L2, p)

        c_pos = [j for j, _ in c_supp]
        d_pos = [j for j, _ in d_supp]

        # Pencil structure: c + α·d. For pure 2-monomial, c and d each have 1 DFT pos.
        if len(c_pos) == 1 and len(d_pos) == 1:
            a = c_pos[0]; b = d_pos[0]
            if a == b:
                # Single-monomial — degenerate, not 2-monomial pencil
                key = "1-mono"
            else:
                gcd_ab = int(np.gcd(abs(a - b), n2))
                gcd_dist[gcd_ab] = gcd_dist.get(gcd_ab, 0) + 1
                pencil_dist[(a, b)] = pencil_dist.get((a, b), 0) + 1
                one_pos_count += 1
        else:
            # More complex (3+ DFT positions in c or d)
            multi_pos_count += 1

        if idx < 5 or idx % 200 == 0:
            print(f"  sup={sup}: c_supp={c_pos}, d_supp={d_pos}")

    print(f"\nTotal 2-monomial pencils: {one_pos_count}")
    print(f"Total multi-pos (3+ DFT pos): {multi_pos_count}")
    print(f"\ngcd distribution: {sorted(gcd_dist.items())}")

    # If gcd_min ≥ 4 → K ≤ 18 at (256, 64) under Conjecture E
    if gcd_dist:
        gcd_min = min(gcd_dist.keys())
        print(f"\ngcd_min = {gcd_min}")
        print(f"  → orbit_size_max = {n2 // gcd_min}")
        print(f"  → K_max (under Conj E) = {1 + n2 // gcd_min + 1}")
        print(f"  → ε_ca ≤ {1 + n2 // gcd_min + 1}/q at (256, 64)")

    # Show a few extreme pencils
    if gcd_dist:
        for target_gcd in sorted(gcd_dist.keys())[:3]:
            print(f"\nSample pencils with gcd={target_gcd}:")
            samples = [pair for pair, _ in pencil_dist.items() if int(np.gcd(abs(pair[0]-pair[1]), n2)) == target_gcd][:5]
            for s in samples:
                print(f"  (a, b) = {s}")


if __name__ == "__main__":
    main()
