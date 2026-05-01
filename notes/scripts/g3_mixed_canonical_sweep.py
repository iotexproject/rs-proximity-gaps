"""g3_mixed_canonical_sweep.py — sweep ALL 1584 mixed mod-4 3-pos
sparse supports at q=97 with CANONICAL d_2 ≤ w_J(L_2) measurement.

Goal: confirm |V_δ|/q ≤ 9 = n_1 - s + 1 universally for above-J f.
Use efficient analytic d_2 method (compute_d2_count from
g3_pacc_qscaling.py).
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

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


def precompute_lagrange_pairs(L2_arr, info_sets_n2, p):
    n2 = len(L2_arr); pairs = []
    for T_idx, T in enumerate(info_sets_n2):
        i, j = int(T[0]), int(T[1])
        yi, yj = int(L2_arr[i]), int(L2_arr[j])
        denom_i = (yi - yj) % p; denom_j = (yj - yi) % p
        inv_di = modinv(denom_i, p); inv_dj = modinv(denom_j, p)
        T_set = {i, j}; kpairs = []
        for k in range(n2):
            if k in T_set: continue
            yk = int(L2_arr[k])
            c_ik = ((yk - yj) * inv_di) % p
            c_jk = ((yk - yi) * inv_dj) % p
            kpairs.append((k, c_ik, c_jk))
        pairs.append((T_idx, (i, j), kpairs))
    return pairs


def compute_V_delta(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    """Returns |{α_2 : d_2(fold² with this α_1) ≤ w_J(L_2)}|."""
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, (i, j), kpairs in lagrange_pairs:
        always_count = 0; targets = []
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0: always_count += 1
            else:
                inv_do = modinv(do, p)
                alpha2 = (-de * inv_do) % p
                targets.append(alpha2)
        if always_count > 0: extras_per_T[T_idx, :] += always_count
        if targets:
            bc = np.bincount(np.array(targets, dtype=np.int64), minlength=p)
            extras_per_T[T_idx, :] += bc.astype(np.int32)
    max_extras = extras_per_T.max(axis=0)
    d2_vec = (n2 - k2 - max_extras).astype(np.int64)
    return int((d2_vec <= w_J_L2).sum())


def main():
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
    p = 97
    n0, k0 = 32, 8
    R = 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L0 = 16; w_J_L1 = 8; w_J_L2 = 4

    print(f"=== Mixed mod-4 canonical sweep at q={p} (32, 8) ===")
    print(f"  Goal: verify |V_δ|/q ≤ 9 universally for above-J f")

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    rng_l0 = np.random.default_rng(2026)
    all_T_n0 = list(combinations(range(n0), k0))
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    # ALL mixed mod-4 3-pos supports
    mixed_supports = []
    for sup in combinations(range(8, 32), 3):
        mod4 = [j % 4 for j in sup]
        in01 = sum(1 for m in mod4 if m in (0, 1))
        if 0 < in01 < 3:
            mixed_supports.append(sup)
    print(f"  Total mixed mod-4 supports: {len(mixed_supports)}")

    # Sweep all
    n_above_J = 0
    n_violate_9q = 0
    max_ratio = 0
    max_violations = []  # (sup, |V_δ|, |V_δ|/q)
    big_violations = []  # |V_δ|/q > 9

    cnt_dist = Counter()
    t0 = time.time()
    for sup_idx, sup in enumerate(mixed_supports):
        sup_rng = random.Random(hash(sup) & 0xFFFFFFFF)
        coefs = [sup_rng.randrange(1, 10**6) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        f = evaluate_dft(fhat, L0, p)
        f_arr = np.array(f, dtype=np.int64)
        ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
        d_f = n0 - k0 - int(ext.max())
        if d_f <= w_J_L0:
            continue  # not above-J (sampled), skip
        n_above_J += 1

        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        V_delta = 0
        for a1 in range(p):
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
            bc = compute_V_delta(fold1_e, fold1_o, lagrange_pairs,
                                  p, n2, k2, w_J_L2)
            V_delta += bc

        ratio = V_delta / p
        cnt_dist[round(ratio, 2)] += 1
        if ratio > max_ratio:
            max_ratio = ratio
            max_violations = [(sup, V_delta, ratio)]
        elif ratio == max_ratio:
            max_violations.append((sup, V_delta, ratio))

        if ratio > 9.0:
            big_violations.append((sup, V_delta, ratio))
            print(f"  >>> VIOLATE 9q: sup={sup} mod4={tuple(j%4 for j in sup)} |V_δ|={V_delta} ratio={ratio:.2f}")

        if (sup_idx + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  [{sup_idx+1}/{len(mixed_supports)}] above-J: {n_above_J}, "
                  f"max ratio: {max_ratio:.2f}, big violations: {len(big_violations)}, "
                  f"elapsed: {elapsed:.0f}s")

    elapsed = time.time() - t0
    print(f"\n=== Done in {elapsed:.0f}s ===")
    print(f"Total mixed: {len(mixed_supports)}")
    print(f"Above-J (sampled): {n_above_J}")
    print(f"Big 9q violations: {len(big_violations)}")
    print(f"Max ratio: {max_ratio:.2f}")
    print(f"Top max-ratio supports:")
    for sup, V, r in max_violations[:10]:
        print(f"  sup={sup} mod4={tuple(j%4 for j in sup)} |V_δ|={V} ratio={r:.2f}")
    print(f"\nRatio distribution (rounded to 0.01):")
    for r, c in sorted(cnt_dist.items()):
        print(f"  {r:6.2f}: {c}")


if __name__ == "__main__":
    main()
