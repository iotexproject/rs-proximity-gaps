"""g3_67_90_91_investigate.py — investigate (67, 90, 91) K = 2q at (128, 32).

Tests:
  1. Verify K = 2q with INCREASED info_sets sampling.
  2. Check if doubly recursive above-J fails (g pencil at L_2 above-J?).
  3. Compare structurally to (87, 102, 103) K = 10.
  4. Check (f_o)_e + α_2·(f_o)_o on L_2 — is it identically zero or trivial?
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


def precompute_lagrange_pairs(L2_arr, info_sets_n2, p):
    n2 = len(L2_arr); pairs = []
    for T_idx, T in enumerate(info_sets_n2):
        idxs = [int(t) for t in T]
        T_set = set(idxs)
        kpairs = []
        for k in range(n2):
            if k in T_set: continue
            yk = int(L2_arr[k])
            coeffs = []
            for ii in idxs:
                yi = int(L2_arr[ii])
                num = 1; den = 1
                for jj in idxs:
                    if jj == ii: continue
                    yj = int(L2_arr[jj])
                    num = (num * (yk - yj)) % p
                    den = (den * (yi - yj)) % p
                coeffs.append((ii, (num * modinv(den, p)) % p))
            kpairs.append((k, coeffs))
        pairs.append((T_idx, idxs, kpairs))
    return pairs


def per_alpha2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]; fo = [int(x) for x in fold1_o]
    for T_idx, idxs, kpairs in lagrange_pairs:
        always_count = 0; targets = []
        for k, coeffs in kpairs:
            pred_e = 0; pred_o = 0
            for (ii, c_ii) in coeffs:
                pred_e = (pred_e + c_ii * fe[ii]) % p
                pred_o = (pred_o + c_ii * fo[ii]) % p
            de = (pred_e - fe[k]) % p
            do = (pred_o - fo[k]) % p
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
    return (d2_vec <= w_J_L2).astype(np.int32)


def main():
    p = 257
    n0, k0, R = 128, 32, 2
    n1, k1 = 64, 16
    n2, k2 = 32, 8
    w_J_L0, w_J_L1, w_J_L2 = 64, 32, 16

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    print(f"=== Investigate (67, 90, 91) K=2q at (128, 32), q={p} ===\n")

    # Use the EXACT same coef seed as the sweep
    sup = (67, 90, 91)
    random.seed(2026 + hash(sup) % 1000)
    coefs = [random.randrange(1, p-1) for _ in range(3)]
    print(f"sup={sup}, coefs={coefs}, mod-4={tuple(j%4 for j in sup)}")

    fhat = [0]*n0
    for j, c in zip(sup, coefs): fhat[j] = c % p
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    # Print f_e, f_o on L_1 (length 64)
    print(f"\nf_e on L_1 (first 16 entries): {[int(x) for x in f_e[:16]]}")
    print(f"f_o on L_1 (first 16 entries): {[int(x) for x in f_o[:16]]}")

    # Compute (f_e)_e, (f_e)_o, (f_o)_e, (f_o)_o on L_2 (length 32)
    fe_e, fe_o = even_odd_parts(f_e, L1, p)
    fo_e, fo_o = even_odd_parts(f_o, L1, p)
    print(f"\nOn L_2 (length 32):")
    print(f"  a = (f_e)_e (zero?): {all(int(x) == 0 for x in fe_e)}")
    print(f"  b = (f_o)_e (zero?): {all(int(x) == 0 for x in fo_e)}")
    print(f"  c = (f_e)_o (zero?): {all(int(x) == 0 for x in fe_o)}")
    print(f"  d = (f_o)_o (zero?): {all(int(x) == 0 for x in fo_o)}")
    print(f"  c first 8: {[int(x) for x in fe_o[:8]]}")
    print(f"  d first 8: {[int(x) for x in fo_o[:8]]}")

    # Check linear dependence: is c proportional to d on L_2?
    # i.e., ∃λ: c[i] = λ·d[i] for all i
    nonzero_idx = next((i for i in range(n2) if int(fo_o[i]) != 0), None)
    if nonzero_idx is not None:
        d0 = int(fo_o[nonzero_idx])
        c0 = int(fe_o[nonzero_idx])
        if d0 != 0:
            lam = (c0 * modinv(d0, p)) % p
            proportional = all(
                (int(fe_o[i]) - lam * int(fo_o[i])) % p == 0
                for i in range(n2)
            )
            print(f"\nLinear dependence test: c = λ·d with λ = {lam}? {proportional}")

    # Check d_f at L_0
    info_sample_n0 = []; seen = set(); rng = np.random.default_rng(2026)
    while len(info_sample_n0) < 50000:
        T = tuple(sorted(rng.choice(n0, size=k0, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n0.append(T)
    info_sets_n0 = np.array(info_sample_n0, dtype=np.int64)
    f_arr = np.array(f, dtype=np.int64)
    ext_n0 = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
    d_f = n0 - k0 - int(ext_n0.max())
    print(f"\nd_f at L_0 = {d_f} (need > {w_J_L0})")

    # Check fold¹(α_1) above-J at L_1 for many α_1
    info_sample_n1 = []; seen = set()
    while len(info_sample_n1) < 10000:
        T = tuple(sorted(rng.choice(n1, size=k1, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n1.append(T)
    info_sets_n1 = np.array(info_sample_n1, dtype=np.int64)

    print(f"\nd(fold¹(α_1)) at L_1 for various α_1:")
    d_fold_max = 0
    for a1 in [0, 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        fold1 = (fe_arr + a1 * fo_arr) % p
        ext = batched_extras(info_sets_n1, fold1, L1_arr, D1, inv_D1, p)
        d_t = n1 - k1 - int(ext.max())
        if d_t > d_fold_max: d_fold_max = d_t
        print(f"  α_1={a1}: d = {d_t}")
    print(f"max d(fold¹) = {d_fold_max} (need > {w_J_L1})")

    # Check g pencil at L_2: g(α_2) = b + α_2·d on L_2
    # Pencil above-J at L_2 means ∃α_2: dist(g(α_2), RS_8(L_2)) > w_J_L2 = 16
    info_sample_n2 = []; seen = set()
    while len(info_sample_n2) < 5000:
        T = tuple(sorted(rng.choice(n2, size=k2, replace=False).tolist()))
        if T not in seen: seen.add(T); info_sample_n2.append(T)
    info_sets_n2 = np.array(info_sample_n2, dtype=np.int64)

    D2, inv_D2 = precompute_diff_inv(L2_arr, p)

    # Need to determine which pencil.
    # For Reverse (a=b=0): h(α_1) = c + α_1·d at L_2.
    # For Pattern B (a=c=0): g(α_2) = b + α_2·d at L_2.
    # Mixed: depends on which components are zero.

    a_zero = all(int(x) == 0 for x in fe_e)
    b_zero = all(int(x) == 0 for x in fo_e)
    c_zero = all(int(x) == 0 for x in fe_o)
    d_zero = all(int(x) == 0 for x in fo_o)
    print(f"\nPencil structure:")
    print(f"  a={int(not a_zero)}, b={int(not b_zero)}, c={int(not c_zero)}, d={int(not d_zero)}")

    if a_zero and b_zero:
        # Reverse: h(α_1) = c + α_1·d
        print(f"  Reverse Pattern: h(α_1) = c + α_1·d at L_2")
        pencil_c = fe_o; pencil_d = fo_o
        pencil_var = "α_1"
    elif a_zero and c_zero:
        # Pattern B: g(α_2) = b + α_2·d
        print(f"  Pattern B: g(α_2) = b + α_2·d at L_2")
        pencil_c = fo_e; pencil_d = fo_o
        pencil_var = "α_2"
    else:
        print(f"  Other pattern (mixed)")
        pencil_c = fe_o; pencil_d = fo_o; pencil_var = "α_1"

    # Compute pencil dist at L_2 for many α
    pencil_c_arr = np.array(pencil_c, dtype=np.int64)
    pencil_d_arr = np.array(pencil_d, dtype=np.int64)
    print(f"\ndist(pencil({pencil_var}), RS_8(L_2)) at L_2:")
    d_pencil_max = 0
    pencil_dist = []
    for alpha in [0, 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        pencil_val = (pencil_c_arr + alpha * pencil_d_arr) % p
        ext = batched_extras(info_sets_n2, pencil_val, L2_arr, D2, inv_D2, p)
        d_t = n2 - k2 - int(ext.max())
        if d_t > d_pencil_max: d_pencil_max = d_t
        pencil_dist.append((alpha, d_t))
        print(f"  α={alpha}: d = {d_t}")
    print(f"max d(pencil) at L_2 = {d_pencil_max} (need > {w_J_L2}={w_J_L2} for above-J)")
    print(f"Doubly recursive above-J? {'YES' if d_pencil_max > w_J_L2 else 'NO'}")


if __name__ == "__main__":
    main()
