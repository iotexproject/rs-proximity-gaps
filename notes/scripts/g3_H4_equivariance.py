"""g3_H4_equivariance.py — test PR #373's prediction:

For supports where f_e, f_o L_1-DFT positions all lie in single residue class
mod h (h ∈ {2, 4, 8}):
  - Bad-α set should have σ_k vanishing pattern determined by h.

Specifically:
  - h=2 (positions all even mod 2 OR all odd mod 2): predicts α↔-α symmetry
    after some normalization → σ_1, σ_3, ... possibly vanish.
  - h=4: stronger constraint, may force more σ_k vanish.

Across all 1584 3-pos supports, classify by (h_e, h_o) where h_e is the
residue class of f_e DFT supp on L_1 mod 4 (or "mixed" if not single class).
Then test σ_k vanishing for each class.
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter, defaultdict
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft_local(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def power_sum_to_elementary(power_sums, p):
    n = len(power_sums)
    e = [0] * (n + 1)
    e[0] = 1
    for k in range(1, n + 1):
        s = 0
        for i in range(1, k + 1):
            s = (s + (-1)**(i-1) * e[k-i] * power_sums[i-1]) % p
        e[k] = (s * pow(k, p - 2, p)) % p
    return e[1:]


def L1_positions_classes(positions, mod_h):
    """For 3-pos support (a,b,c) ⊂ [0..31], compute L_1 DFT positions split by
    even/odd of original, and return their residue classes mod h."""
    fe_pos = []
    fo_pos = []
    for j in positions:
        if j % 2 == 0:
            fe_pos.append(j // 2)
        else:
            fo_pos.append((j - 1) // 2)
    fe_classes = sorted(set(p % mod_h for p in fe_pos))
    fo_classes = sorted(set(p % mod_h for p in fo_pos))
    return tuple(fe_classes), tuple(fo_classes), tuple(sorted(fe_pos)), tuple(sorted(fo_pos))


def bad_alpha_full(positions, coeffs, p, n0, k0, threshold,
                   L0, L1_arr, all_T, D1, inv_D1):
    fhat = [0] * n0
    for ps, c in zip(positions, coeffs):
        fhat[ps] = c
    f = evaluate_dft_local(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)
    n1 = len(L1_arr)
    k1 = k0 // 2

    bad = []
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            bad.append(alpha)
    return bad


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 8

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    # Classify all 3-pos supports in syndrome window {8..31} by (mod-4 residue classes
    # of f_e DFT and f_o DFT positions on L_1).
    sup_class = defaultdict(list)
    for sup in combinations(range(8, 32), 3):
        fe_c, fo_c, fe_pos, fo_pos = L1_positions_classes(sup, 4)
        # need at least one even and at least one odd j (else single fold component)
        if not fe_pos or not fo_pos:
            continue
        # classify by both f_e and f_o being concentrated in single mod-4 class
        # OR mod-2 class
        fe_mod4_single = len(fe_c) == 1
        fo_mod4_single = len(fo_c) == 1
        fe_mod2_single = len(set(p % 2 for p in fe_pos)) == 1
        fo_mod2_single = len(set(p % 2 for p in fo_pos)) == 1
        key = (fe_mod4_single, fo_mod4_single, fe_mod2_single, fo_mod2_single)
        sup_class[key].append(sup)

    print(f"=== H_h equivariance classification at q={p}, ({n0},{k0}) ===\n")
    print(f"{'fe_m4 fo_m4 fe_m2 fo_m2':25s} | count_supports")
    for key in sorted(sup_class):
        print(f"  {str(key):23s} | {len(sup_class[key])}")
    print()

    # Now for each class, sample a few supports and report bad-α σ-pattern
    rng = random.Random(2026)
    print("=== Sampled σ-patterns per class ===\n")
    for key in sorted(sup_class, reverse=True):
        sups = sup_class[key]
        n_sample = min(5, len(sups))
        idx = rng.sample(range(len(sups)), n_sample)
        sample = [sups[i] for i in idx]
        cls_bits = ['fe_mod4_single', 'fo_mod4_single', 'fe_mod2_single', 'fo_mod2_single']
        active = [name for name, b in zip(cls_bits, key) if b]
        active_str = ', '.join(active) if active else 'NO equivariance'
        print(f"--- class {key}: {active_str} ({len(sups)} total) ---")
        for sup in sample:
            for trial in range(2):
                coeffs = tuple(rng.randrange(1, p) for _ in range(3))
                bad = bad_alpha_full(sup, coeffs, p, n0, k0, threshold,
                                      L0, L1_arr, all_T, D1, inv_D1)
                cnt = len(bad)
                if cnt == 0:
                    print(f"  sup={sup} trial {trial}: count=0")
                    continue
                ps = []
                for k in range(1, min(cnt, 5) + 1):
                    ps.append(sum(pow(a, k, p) for a in bad) % p)
                # σ_1..σ_5
                e = power_sum_to_elementary(ps, p)
                vanish = [k+1 for k in range(len(e)) if e[k] == 0]
                # also check coset closure under -1
                bad_set = set(bad)
                closed_neg = all(((-a) % p in bad_set) for a in bad)
                print(f"  sup={sup} trial {trial}: count={cnt}, σ vanish={vanish[:5]}, "
                      f"closed under α→-α: {closed_neg}")
            print()


if __name__ == "__main__":
    main()
