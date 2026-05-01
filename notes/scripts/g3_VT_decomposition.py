"""g3_VT_decomposition.py — for sampled mixed mod-4 above-J 3-pos sparse
supports, decompose V_δ as union of V_T sets and count how many T's give
non-empty V_T.

For each (T, c) where T ⊂ L_2 of size k_2+1=3 and c ∈ RS_{k_2}:
   V_{T,c} := {(α_1, α_2) : interp_T(fold²(α_1, α_2)) = fold²(α_1, α_2) on L_2 \\ T,
                          AND fold²(α_1, α_2)(z) = c(z) for z ∈ T}

By a different decomposition, each (α_1, α_2) ∈ V_δ has a witness T (size-3 info
set) and a codeword c such that the level-2 fold matches c on T plus
≥ 1 extra L_2 position.

Question: how many (T, c) give nontrivial V_{T,c}? If ≤ M_max(L_1) = 9,
then |V_δ| ≤ 9·q + small terms.

For each support:
- compute V_δ exhaustively (already done)
- for each (α_1, α_2) ∈ V_δ, find ALL (T, c) witnesses
- bin them — see how many distinct (T, c) give non-empty V_{T,c}
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import defaultdict, Counter

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
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
    p = 97
    n0, k0, R = 32, 8, 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L0, w_J_L1, w_J_L2 = 16, 8, 4

    chain = setup_chain(p, n0, k0, R=R)
    L0, L1, L2 = chain[0][0], chain[1][0], chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    D2, inv_D2 = precompute_diff_inv(L2_arr, p)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)

    rng_l0 = np.random.default_rng(2026)
    all_T_n0 = list(combinations(range(n0), k0))
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)

    # For each (α_1, α_2), determine V_T witness (one size-3 subset of L_2
    # where level-2 fold has agreement = 4 with closest codeword.)
    # Easier: compute extras at each size-(k_2+1)=3 info-set on L_2 (these
    # define a cup-of-w_J ball). Each T_2 ∈ C(8, 3) gives an interpolation
    # codeword c_T = polynomial of deg ≤ 1 through T's values. The "extras"
    # = number of L_2 positions outside T where fold²(z) = c_T(z).
    # If extras ≥ k_2+1 = 3 (for w_J=4 = n_2-(k_2+1)) then |agreement set|
    # ≥ 3 + (k_2+1) ... wait actually d_2 ≤ w_J = 4 means agreement ≥ 4.
    # So we want extras ≥ 1 (= 4 - 3 = 1 extra beyond T's k_2+1=3).

    # For each (α_1, α_2), find T's with extras ≥ 1. Each such T is a
    # witness pointing to a different codeword (via interp_T).
    info_sets_n2_3 = np.array(list(combinations(range(n2), k2+1)),
                                dtype=np.int64)  # 3-subsets, C(8,3)=56

    # Sample 5 mixed mod-4 supports
    mixed_supports = []
    for sup in combinations(range(8, 32), 3):
        mod4 = [j % 4 for j in sup]
        in01 = sum(1 for m in mod4 if m in (0, 1))
        if 0 < in01 < 3:
            mixed_supports.append(sup)
    rng_pick = random.Random(2026)
    sample = rng_pick.sample(mixed_supports, 6)
    print(f"=== V_T decomposition: {len(sample)} mixed mod-4 sparse supports at q={p} ===\n")

    for sup in sample:
        sup_rng = random.Random(hash(sup) & 0xFFFFFFFF)
        coefs = [sup_rng.randrange(1, 10**6) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p
        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        # above-J check
        ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext.max())
        if d_f <= w_J_L0:
            print(f"sup={sup} mod4={tuple(j%4 for j in sup)}: NOT above-J (d_f≥{d_f})")
            continue

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        per_a1_count = []
        # which T's are "active" for each α_1?
        T_activity = defaultdict(int)  # T_idx → total # α_1's where T contributes
        T_alpha2_pairs = defaultdict(list)  # T_idx → list of (α_1, α_2)
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            fe_l2 = np.array(fold1_e, dtype=np.int64)
            fo_l2 = np.array(fold1_o, dtype=np.int64)
            bad_a2_count = 0
            for a2 in range(p):
                fold2 = (fe_l2 + a2 * fo_l2) % p
                # check d_2 ≤ 4 ⟺ agreement ≥ 4. For each 3-info-set T,
                # extras at T = #{z ∉ T : fold2 matches interp_T at z}.
                # If max extras over T ≥ 1, then d_2 ≤ 8 - (3+1) = 4 ✓
                extras = batched_extras(info_sets_n2_3, fold2, L2_arr,
                                          D2, inv_D2, p)
                max_ext = int(extras.max())
                if max_ext >= 1:  # agreement ≥ 4 = 8 - 4
                    bad_a2_count += 1
                    # find which T's saturate
                    best_T_idxs = np.where(extras == max_ext)[0]
                    for T_idx in best_T_idxs:
                        T_alpha2_pairs[int(T_idx)].append((a1, a2))
                        T_activity[int(T_idx)] += 1
            per_a1_count.append(bad_a2_count)

        cnt_dist = Counter(per_a1_count)
        T_active_count = len([T for T, n in T_activity.items() if n > 0])
        # how many T's are responsible for most pairs?
        T_pair_counts = sorted(((len(v), T_idx) for T_idx, v in T_alpha2_pairs.items()), reverse=True)
        top_T = T_pair_counts[:12] if len(T_pair_counts) >= 12 else T_pair_counts

        print(f"sup={sup} mod4={tuple(j%4 for j in sup)} d_f≥{d_f}")
        print(f"  per-α_1 bad α_2 dist: {dict(sorted(cnt_dist.items()))}")
        print(f"  uniform 9-per-line? {set(per_a1_count) == {9}}")
        print(f"  total |V_δ| = {sum(per_a1_count)}")
        print(f"  # active T_2's (size-3 info sets): {T_active_count} / {len(info_sets_n2_3)}")
        print(f"  top-12 T_2's by # (α_1, α_2) pairs hit:")
        for cnt, T_idx in top_T:
            T = info_sets_n2_3[T_idx].tolist()
            print(f"    T={T}: {cnt} pairs")
        print()


if __name__ == "__main__":
    main()
