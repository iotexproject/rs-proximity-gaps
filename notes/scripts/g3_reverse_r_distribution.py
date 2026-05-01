"""g3_reverse_r_distribution.py — distribution of pencil position diff r for Reverse Pattern.

For 3-pos Reverse supports at (n_0, k_0), compute the L_2-pencil position diff r.
If r ≥ 4 always, we get tight K bound via gcd(r, n_2) ≥ 4.

Track:
- r values across all Reverse triples
- (a, a-r) positions on L_2

Quick (no per-α dist computation needed).
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
    n = len(L_subgroup); n_inv = pow(n, p-2, p)
    supp = []
    for k in range(n):
        v = 0
        for i, z in enumerate(L_subgroup):
            v = (v + int(arr[i]) * pow(int(z), -k, p)) % p
        v = v * n_inv % p
        if v != 0:
            supp.append((k, v))
    return supp


def analyze_scale(p, n0, k0, n_samples=1000):
    n2 = n0 // 4
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]

    rev_pos = [j for j in range(n0) if j % 4 in (2, 3)]
    rng = random.Random(2026)
    all_triples = list(combinations(rev_pos, 3))
    rng.shuffle(all_triples)
    sample = all_triples[:n_samples]

    r_dist = {}
    structure_dist = {}  # (|c_supp|, |d_supp|) → count
    pencil_pairs = []

    for idx, sup in enumerate(sample):
        coefs = [(idx*7 + 11) % (p-1) + 1, (idx*13 + 17) % (p-1) + 1, (idx*19 + 23) % (p-1) + 1]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c

        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)

        c_supp = find_dft_supp(fe_o, L2, p)
        d_supp = find_dft_supp(fo_o, L2, p)

        c_pos = sorted([j for j, _ in c_supp])
        d_pos = sorted([j for j, _ in d_supp])

        sig = (len(c_pos), len(d_pos))
        structure_dist[sig] = structure_dist.get(sig, 0) + 1

        # For (1, 2) or (2, 1) cases, extract r (= |a - b| = position diff)
        all_pos = sorted(set(c_pos + d_pos))
        if len(all_pos) == 2:
            r = (all_pos[1] - all_pos[0])  # signed positive
            r_mod = min(r, n2 - r)
            r_dist[r_mod] = r_dist.get(r_mod, 0) + 1
            pencil_pairs.append((sup, c_pos, d_pos, r_mod))

    return r_dist, structure_dist, pencil_pairs


def main():
    for p, n0, k0, label in [(97, 32, 8, '(32, 8)'), (257, 128, 32, '(128, 32)'), (257, 256, 64, '(256, 64)')]:
        n2 = n0 // 4
        print(f"\n=== Scale {label}, p={p}, n_2 = {n2} ===")
        r_dist, struct_dist, pairs = analyze_scale(p, n0, k0, n_samples=500)
        print(f"DFT structure (|c_supp|, |d_supp|) distribution: {sorted(struct_dist.items())}")
        print(f"r distribution (for 2-position pencils): {sorted(r_dist.items())}")
        if r_dist:
            r_min = min(r_dist.keys())
            print(f"r_min = {r_min}, gcd(r_min, n_2) = {int(np.gcd(r_min, n2))}")
            orbit_max = n2 // int(np.gcd(r_min, n2))
            print(f"Worst orbit size = n_2/gcd(r_min, n_2) = {orbit_max}")
            print(f"Predicted K ≤ 1 + {orbit_max} + 1 = {orbit_max + 2}")

        print(f"Sample pencil structures (first 5):")
        for sup, cp, dp, r in pairs[:5]:
            print(f"  sup={sup}: c_pos={cp}, d_pos={dp}, r={r}")


if __name__ == "__main__":
    main()
