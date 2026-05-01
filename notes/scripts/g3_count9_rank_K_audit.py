"""g3_count9_rank_K_audit.py — for each of 24 count=9 supports at q=1153,
compute (rank, K, joint (d_1, d_2) histogram, |V_δ|, P_avg).

Setup: p=1153, n_0=32, k_0=8, R=2 → (n_1, k_1)=(16, 4), (n_2, k_2)=(8, 2).
w_J(L_1) = 16 - sqrt(64) = 8. w_J(L_2) = 8 - sqrt(16) = 4.

Algorithm:
  Level 1: batched_extras (existing helper) for d_1.
  Level 2: analytic — for fixed α_1 and T = info set on L_2,
           interp_T(fold²)(y_k) - fold²(y_k) = δ_e(T, k) + α_2 · δ_o(T, k).
           Match at (T, k) for α_2 ⟺ δ_e + α_2 δ_o = 0.
           Aggregate by α_2 → extras_T(α_2) → max over T → d_2(α_2).
  Rank: split f's coefficients into 4 mod-4 blocks Q_b on L_2,
        compute syndromes ψ_b ∈ F_q^{n_R - k_R} = F_q^6,
        rank = dim_{F_q} span{ψ_b}.

Memory: ~20MB peak. Time: ~1 min for 24 supports.
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts, parity_check, gauss_rank, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    """fhat[j] = c_j (DFT coefs at L_0 positions). Compute f(x) = Σ c_j x^j on L."""
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def compute_d1(fold1, L1_arr, info_sets_n1, D1, inv_D1, p):
    """d_1 = n_1 - k_1 - max_extras over info sets at L_1."""
    n1 = len(fold1)
    k1 = 4
    fold1_arr = np.array(fold1, dtype=np.int64) % p
    extras = batched_extras(info_sets_n1, fold1_arr, L1_arr, D1, inv_D1, p)
    max_extras = int(extras.max())
    return n1 - k1 - max_extras


def precompute_lagrange_pairs(L2_arr, info_sets_n2, p):
    """For each T = (i, j) ∈ C(8, 2) and each k ∉ T, compute Lagrange weights
    c_ik, c_jk such that interp_T(v)(y_k) = c_ik · v[i] + c_jk · v[j]
    for any v: L_2 → F_q.

    Returns:
      pairs: list of (T_idx, T, [(k, c_ik, c_jk) for k ∉ T])
    """
    n2 = len(L2_arr)
    pairs = []
    for T_idx, T in enumerate(info_sets_n2):
        i, j = int(T[0]), int(T[1])
        yi, yj = int(L2_arr[i]), int(L2_arr[j])
        denom_i = (yi - yj) % p
        denom_j = (yj - yi) % p
        inv_di = modinv(denom_i, p)
        inv_dj = modinv(denom_j, p)
        T_set = {i, j}
        kpairs = []
        for k in range(n2):
            if k in T_set:
                continue
            yk = int(L2_arr[k])
            c_ik = ((yk - yj) * inv_di) % p
            c_jk = ((yk - yi) * inv_dj) % p
            kpairs.append((k, c_ik, c_jk))
        pairs.append((T_idx, (i, j), kpairs))
    return pairs


def compute_d2_vector_for_alpha1(fold1_e, fold1_o, lagrange_pairs, p, q_for_bincount):
    """For fixed α_1 (i.e., fixed fold1_e, fold1_o on L_2), compute d_2(α_2)
    for ALL α_2 ∈ F_q via analytic match on (T, k) pairs.

    Returns:
      d2_vec (np.array of shape (q,)): d_2 for each α_2 ∈ {0, ..., q-1}.
    """
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, q_for_bincount), dtype=np.int32)
    fe = [int(x) for x in fold1_e]
    fo = [int(x) for x in fold1_o]

    for T_idx, (i, j), kpairs in lagrange_pairs:
        always_count = 0
        targets = []  # list of α_2 values where some k gives agreement
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0:
                    always_count += 1
                # else: no α_2 gives agreement at this (T, k). skip.
            else:
                # match at α_2 = -de/do
                inv_do = modinv(do, p)
                alpha2 = (-de * inv_do) % p
                targets.append(alpha2)
        if always_count > 0:
            extras_per_T[T_idx, :] += always_count
        if targets:
            bc = np.bincount(np.array(targets, dtype=np.int64), minlength=q_for_bincount)
            extras_per_T[T_idx, :] += bc.astype(np.int32)

    max_extras = extras_per_T.max(axis=0)  # (q,)
    n2 = 8
    k2 = 2
    d2_vec = (n2 - k2 - max_extras).astype(np.int64)
    return d2_vec


def compute_rank(fhat, n0, k0, R, chain, p):
    """Split f̂ into 4 mod-4 blocks → Q_b on L_2 → syndromes ψ_b → rank.

    For 3-pos sparse f at L_0 syndrome window {k_0..n_0-1}, position j ≡ b₁ + 2 b₂ mod 4
    where b = (b₁, b₂) ∈ {0,1}², b₁ = parity at L_0, b₂ = parity at L_1.
    """
    n_R = n0 // (2**R)
    k_R = k0 // (2**R)
    L_R = chain[R][0]
    H_R = chain[R][2]

    # Q_b: function on L_R obtained by collecting f̂_j for j with j mod 4 = b₁ + 2 b₂,
    # mapped to L_R-DFT position ⌊j/4⌋.
    Q_blocks = {}
    for b1 in (0, 1):
        for b2 in (0, 1):
            Q_hat = [0] * n_R  # DFT representation of Q on L_R
            for j in range(n0):
                if fhat[j] != 0 and j % 4 == (b1 + 2 * b2):
                    Q_hat[j // 4] = fhat[j]
            # Evaluate Q on L_R
            Q_vals = [0] * n_R
            for i, y in enumerate(L_R):
                v = 0
                for m in range(n_R):
                    if Q_hat[m] != 0:
                        v = (v + Q_hat[m] * pow(y, m, p)) % p
                Q_vals[i] = v
            Q_blocks[(b1, b2)] = Q_vals

    # ψ_b = H_R · Q_b ∈ F_q^{n_R - k_R}
    psi_vectors = []
    for b in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        Q = Q_blocks[b]
        psi = [0] * (n_R - k_R)
        for r in range(n_R - k_R):
            s = 0
            for c in range(n_R):
                s = (s + H_R[r][c] * Q[c]) % p
            psi[r] = s
        psi_vectors.append(psi)

    # rank = dim span{ψ_b}
    rank = gauss_rank(psi_vectors, p)
    nonzero_blocks = [b for b in [(0, 0), (1, 0), (0, 1), (1, 1)]
                      if any(v != 0 for v in Q_blocks[b])]
    return rank, len(nonzero_blocks), psi_vectors


def main():
    p = 1153
    n0, k0 = 32, 8
    R = 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))  # 8
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))  # 4

    print(f"=== Audit 24 count=9 supports at q={p}, (n_0, k_0)=({n0}, {k0}), R={R} ===")
    print(f"  w_J(L_1) = {w_J_L1}, w_J(L_2) = {w_J_L2}")
    print(f"  level-1 bad α_1: d_1 ≤ {w_J_L1}")
    print(f"  level-2 bad (α_1, α_2): d_2 ≤ {w_J_L2}")
    print()

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L2 = chain[2][0]
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    # The 24 count=9 supports from g3_count9_structure.output.txt
    sigma_empty_supports = [
        (8, 9, 20), (8, 9, 21), (10, 11, 22), (10, 11, 23),
        (12, 13, 16), (12, 13, 17), (14, 15, 18), (14, 15, 19),
        (16, 28, 29), (17, 28, 29), (18, 30, 31), (19, 30, 31),
        (20, 24, 25), (21, 24, 25), (22, 26, 27), (23, 26, 27),
    ]
    sigma_9_supports = [
        (9, 20, 21), (11, 22, 23), (13, 16, 17), (15, 18, 19),
        (16, 17, 29), (18, 19, 31), (20, 21, 25), (22, 23, 27),
    ]
    all_supports = [(s, 'σ=()') for s in sigma_empty_supports] + \
                   [(s, 'σ_9=0') for s in sigma_9_supports]

    rng = random.Random(2026)

    for sup, label in all_supports:
        coefs = tuple(rng.randrange(1, p) for _ in range(3))
        fhat = [0] * n0
        for j, c in zip(sup, coefs):
            fhat[j] = c

        # rank classification
        rank, n_nonzero_blocks, psi_vectors = compute_rank(fhat, n0, k0, R, chain, p)
        sup_mod4 = tuple(j % 4 for j in sup)

        # Evaluate f on L_0
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_arr = np.array(f_e, dtype=np.int64)
        fo_arr = np.array(f_o, dtype=np.int64)

        # For each α_1, compute d_1 and d_2 vector
        joint_hist = Counter()
        d1_dist = Counter()
        bad_a1_count = 0
        V_delta_count = 0
        P_avg_sum = 0.0
        t0 = time.time()

        for a1 in range(p):
            # fold1 on L_1 = f_e + a1 · f_o
            fold1_arr = (fe_arr + a1 * fo_arr) % p
            fold1 = fold1_arr.tolist()

            # d_1
            extras = batched_extras(info_sets_n1, fold1_arr, L1_arr, D1, inv_D1, p)
            max_extras_l1 = int(extras.max())
            d1 = n1 - k1 - max_extras_l1
            d1_dist[d1] += 1
            if d1 <= w_J_L1:
                bad_a1_count += 1

            # fold1_e, fold1_o on L_2
            fold1_e, fold1_o = even_odd_parts(fold1, L1, p)

            # d_2 vector via analytic approach
            d2_vec = compute_d2_vector_for_alpha1(fold1_e, fold1_o, lagrange_pairs,
                                                    p, p)

            # Joint histogram update
            for d2_val in range(int(d2_vec.min()), int(d2_vec.max()) + 1):
                cnt = int((d2_vec == d2_val).sum())
                if cnt > 0:
                    joint_hist[(d1, d2_val)] += cnt

            # |V_δ|: count α_2 with d_2 ≤ w_J(L_2)
            V_delta_count += int((d2_vec <= w_J_L2).sum())

            # P_avg contribution: P_B(α_1, α_2) = 1 - d_2/n_2.
            # For audit, use P_B as proxy (P_A requires nearest-codeword stuff).
            P_B = 1.0 - d2_vec.astype(np.float64) / n2
            P_avg_sum += float(P_B.sum())

        elapsed = time.time() - t0
        P_avg = P_avg_sum / (p * p)

        # Print row
        print(f"sup={sup} mod4={sup_mod4} ({label}) coefs={coefs}")
        print(f"  rank={rank}, nonzero_blocks={n_nonzero_blocks}")
        print(f"  count_α_1 (d_1≤{w_J_L1}): {bad_a1_count}")
        print(f"  d_1 distribution: {dict(sorted(d1_dist.items()))}")
        # show top 8 entries of joint hist
        sorted_joint = sorted(joint_hist.items())
        print(f"  joint (d_1, d_2) histogram (top entries by mass):")
        for (d1_v, d2_v), cnt in sorted(joint_hist.items(),
                                          key=lambda x: -x[1])[:8]:
            print(f"    (d_1={d1_v}, d_2={d2_v}): {cnt}")
        print(f"  |V_δ| = {V_delta_count}, |V_δ|/q² = {V_delta_count / (p*p):.5f}")
        print(f"  P_avg (= E[P_B]) = {P_avg:.6f}, 2q = {2*p}, R q^(R-1) = {R*p}")
        print(f"  [{elapsed:.1f}s]")
        print()


if __name__ == "__main__":
    main()
