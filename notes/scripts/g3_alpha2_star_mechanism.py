"""g3_alpha2_star_mechanism.py — for the 48 mixed-mod-4 supports that hit
|V_δ| ≈ 10q-9, identify the structural mechanism: a special "α_2* line"
along which |{α_1 : (α_1, α_2*) ∈ V_δ}| = q (or near q), giving the
"+q column" mass on top of the generic 9q.

For each violator support sup:
  1. Compute count_α_1 = |B_1(f)| (level-1 bad α_1 set; gives q copies via PR373).
  2. For each α_2 ∈ F_q, count |{α_1 : d_2(fold²(α_1, α_2)) ≤ w_J(L_2)}|.
  3. Identify the "row distribution" of |V_δ| across α_2's columns.
     Hypothesis: most α_2's give count_α_1 (the PR373 floor), but ONE
     α_2* gives ~q (saturating column).
  4. Verify fold²(·, α_2*) becomes structurally degenerate.
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


def per_alpha2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    """Returns array of length p giving, for each α_2, indicator whether
    d_2(fold²(this α_1, α_2)) ≤ w_J(L_2)."""
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
    return (d2_vec <= w_J_L2).astype(np.int32)  # length-p indicator over α_2


def compute_alpha2_column_dist(fhat, L0, L1, L2, L0_arr, lagrange_pairs,
                                 D0, inv_D0, info_sets_n0, p, n2, k2,
                                 w_J_L0, w_J_L2):
    """For one f̂, compute:
      - d_f at L_0 (above-J check)
      - column[α_2] = #{α_1 : d_2 ≤ w_J(L_2)}  (length-p array)
      - count_α_1 = |B_1(f)| via union: α_1 ∈ B_1 iff column-mass for that
        α_1 row equals p (PR373: α_1 bad ⟹ ALL α_2 bad)."""
    f = evaluate_dft(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    ext = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
    d_f = n0 - k0 - int(ext.max())
    if d_f <= w_J_L0:
        return None, None, None  # not above-J

    f_e, f_o = even_odd_parts(f, L0, p)
    fe_arr = np.array(f_e, dtype=np.int64); fo_arr = np.array(f_o, dtype=np.int64)

    # rows: per α_1, per α_2 indicator. shape (p, p) = 9409 ints, 36KB. fine.
    bad = np.zeros((p, p), dtype=np.int32)
    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        fold1 = fold1_arr.tolist()
        fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
        bad[a1, :] = per_alpha2_count(fold1_e, fold1_o, lagrange_pairs,
                                       p, n2, k2, w_J_L2)
    column = bad.sum(axis=0)  # column[α_2] = #{α_1 : bad}
    row    = bad.sum(axis=1)  # row[α_1]    = #{α_2 : bad}
    return d_f, column, row


def main():
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
    p = 97
    global n0, k0
    n0, k0 = 32, 8
    R = 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L0 = 16; w_J_L1 = 8; w_J_L2 = 4

    print(f"=== α_2* mechanism analysis at q={p} (32, 8) ===")
    print(f"  Targets: 48 mixed mod-4 violators with |V_δ| ≥ 953 (9.82q–9.91q)")

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    rng_l0 = np.random.default_rng(2026)
    all_T_n0 = list(combinations(range(n0), k0))
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)

    # 48 violators from the canonical sweep output (manually extracted)
    violators = [
        (9, 11, 20),  (9, 11, 21),  (9, 11, 23),  (10, 11, 20),
        (11, 20, 23), (11, 21, 23), (12, 22, 27), (13, 15, 16),
        (13, 15, 17), (13, 15, 19), (13, 15, 22), (13, 15, 24),
        (13, 15, 26), (13, 15, 28), (13, 15, 30), (13, 16, 18),
        (13, 17, 18), (13, 18, 19), (13, 18, 22), (13, 18, 30),
        (15, 16, 17), (15, 17, 24), (15, 17, 26), (15, 22, 23),
        (15, 23, 24), (16, 22, 31), (16, 23, 25), (16, 23, 31),
        (16, 30, 31), (17, 18, 31), (17, 19, 31), (17, 29, 31),
        (17, 30, 31), (18, 29, 31), (19, 29, 31), (20, 21, 27),
        (20, 22, 27), (20, 23, 27), (20, 24, 27), (20, 25, 27),
        (20, 26, 27), (20, 27, 30), (21, 22, 27), (21, 23, 27),
        (21, 25, 27), (21, 26, 27), (22, 25, 27), (23, 25, 27),
    ]

    # We'll use the same coefficient seed as the sweep
    print(f"\n  {'sup':<14} {'mod4':<12} {'|V_δ|':<6} {'|B_1|':<5} "
          f"{'col-saturated':<14} {'col-eq-|B_1|':<12} {'mechanism'}")
    print("  " + "-"*96)

    all_results = []
    for sup in violators:
        sup_rng = random.Random(hash(sup) & 0xFFFFFFFF)
        coefs = [sup_rng.randrange(1, 10**6) for _ in range(3)]
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c % p

        d_f, column, row = compute_alpha2_column_dist(
            fhat, L0, L1, L2, L0_arr, lagrange_pairs,
            D0, inv_D0, info_sets_n0, p, n2, k2, w_J_L0, w_J_L2)
        if column is None:
            print(f"  sup={sup} NOT above-J (sampled), skip")
            continue

        V_delta = int(column.sum())

        # |B_1(f)| = #{α_1 : row[α_1] == p}
        B1 = int((row == p).sum())

        # Column distribution
        col_dist = Counter(column.tolist())
        # Pretty: how many columns saturate (== p), how many == B1, how many other
        n_col_eq_p = col_dist[p]
        n_col_eq_B1 = col_dist[B1]
        n_col_other = p - n_col_eq_p - n_col_eq_B1

        # Try to identify mechanism
        if n_col_eq_p >= 1:
            mechanism = f"sat-col(s)={n_col_eq_p}"
        elif col_dist.most_common(1)[0][0] >= B1 + 1:
            top_val, top_cnt = col_dist.most_common(1)[0]
            mechanism = f"max-col={top_val} ({top_cnt}x)"
        else:
            mechanism = "uniform"

        # Get the top-3 column values
        top_cols = col_dist.most_common(5)
        mod4 = tuple(j % 4 for j in sup)
        print(f"  {str(sup):<14} {str(mod4):<12} {V_delta:<6} {B1:<5} "
              f"{n_col_eq_p:<14} {n_col_eq_B1:<12} {mechanism}")
        all_results.append((sup, mod4, V_delta, B1, col_dist, top_cols))

    print(f"\n=== Summary ===")
    n_sat_col = sum(1 for r in all_results if r[4][p] >= 1)
    n_no_sat = len(all_results) - n_sat_col
    print(f"  total violators analyzed:     {len(all_results)}")
    print(f"  with ≥1 saturating col (q):   {n_sat_col}")
    print(f"  WITHOUT saturating col:       {n_no_sat}")

    print(f"\n=== Top-5 column distributions for first 8 violators ===")
    for sup, mod4, V_delta, B1, col_dist, top_cols in all_results[:8]:
        print(f"  sup={sup} mod4={mod4} |V_δ|={V_delta} |B_1|={B1}")
        print(f"    top-5 columns: {top_cols}")


if __name__ == "__main__":
    main()
