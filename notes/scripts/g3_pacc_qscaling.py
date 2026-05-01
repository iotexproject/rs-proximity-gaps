"""g3_pacc_qscaling.py — q-scaling of |V_δ|/q² for the 24 count=9 supports.

GOAL (#344-decisive): if |V_δ|/q² stays bounded above 1/poly(q) as q → ∞,
that's a NEGATIVE for OP1 (FRI 2-round zero-loss fails). If it decays
poly(n)/q, we're in #343 territory and need character-sum bounds.

For each support × prime q ≡ 1 mod 32, with deterministic seeded coefs:
  - check above-J at L_0
  - count_α_1 at L_1 (d_1 ≤ w_J(L_1) = 8)
  - |V_δ| = #{(α_1, α_2) : d_2 ≤ w_J(L_2) = 4}
  - report |V_δ|/q², count_α_1, count_α_1/q

Time per (sup, q): ~q · 28 · 6 modinv ≈ q × 200μs. q=1153 ≈ 1s.
24 sups × 7 primes × 1s ≈ 3 min. Local-safe.
"""
import sys, os, math, random, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from collections import Counter

from fri_2round_attack import setup_chain, even_odd_parts, modinv
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def precompute_lagrange_pairs(L2_arr, info_sets_n2, p):
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


def compute_d2_and_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    """For fixed α_1, return |{α_2 ∈ F_q : d_2 ≤ w_J(L_2)}|."""
    n_T = len(lagrange_pairs)
    extras_per_T = np.zeros((n_T, p), dtype=np.int32)
    fe = [int(x) for x in fold1_e]
    fo = [int(x) for x in fold1_o]

    for T_idx, (i, j), kpairs in lagrange_pairs:
        always_count = 0
        targets = []
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0:
                    always_count += 1
            else:
                inv_do = modinv(do, p)
                alpha2 = (-de * inv_do) % p
                targets.append(alpha2)
        if always_count > 0:
            extras_per_T[T_idx, :] += always_count
        if targets:
            bc = np.bincount(np.array(targets, dtype=np.int64), minlength=p)
            extras_per_T[T_idx, :] += bc.astype(np.int32)

    max_extras = extras_per_T.max(axis=0)
    d2_vec = (n2 - k2 - max_extras).astype(np.int64)
    bad_count = int((d2_vec <= w_J_L2).sum())
    sum_extras = int(max_extras.sum())  # for P_avg proxy = E[1 - d_2/n_2] aggregated
    return bad_count, sum_extras


def setup_q_context(p, n0, k0, R, n_l0_sample=8000):
    """Build chain + sampled info sets at L_0 (memory-frugal),
    full info sets at L_1, L_2."""
    n1 = n0 // 2; k1 = k0 // 2
    n2 = n0 // 4; k2 = k0 // 4
    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    rng = np.random.default_rng(12345 + p)
    all_T_n0 = list(combinations(range(n0), k0))
    if len(all_T_n0) > n_l0_sample:
        idx = rng.choice(len(all_T_n0), size=n_l0_sample, replace=False)
        info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)
    else:
        info_sets_n0 = np.array(all_T_n0, dtype=np.int64)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)
    return {
        'p': p, 'n0': n0, 'k0': k0, 'n1': n1, 'k1': k1, 'n2': n2, 'k2': k2,
        'L0': L0, 'L1': L1, 'L2': L2,
        'L0_arr': L0_arr, 'L1_arr': L1_arr, 'L2_arr': L2_arr,
        'D0': D0, 'inv_D0': inv_D0, 'D1': D1, 'inv_D1': inv_D1,
        'info_sets_n0': info_sets_n0,
        'info_sets_n1': info_sets_n1,
        'lagrange_pairs': lagrange_pairs,
    }


def run_one_with_ctx(support, coefs, ctx):
    """For one support given a precomputed ctx, return (above_J, count_a1,
    V_delta, P_acc, d_f_lower)."""
    p = ctx['p']; n0 = ctx['n0']; k0 = ctx['k0']
    n1 = ctx['n1']; k1 = ctx['k1']; n2 = ctx['n2']; k2 = ctx['k2']
    w_J_L0 = n0 - int(math.isqrt(k0 * n0))
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))

    fhat = [0] * n0
    for j, c in zip(support, coefs):
        fhat[j] = c % p

    f = evaluate_dft(fhat, ctx['L0'], p)
    f_arr = np.array(f, dtype=np.int64)
    extras_l0 = batched_extras(ctx['info_sets_n0'], f_arr, ctx['L0_arr'],
                                 ctx['D0'], ctx['inv_D0'], p)
    d_f_lower = n0 - k0 - int(extras_l0.max())
    above_J = d_f_lower > w_J_L0
    if not above_J:
        return False, 0, 0, 0.0, d_f_lower

    f_e, f_o = even_odd_parts(f, ctx['L0'], p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    bad_a1 = 0
    V_delta = 0
    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        extras_l1 = batched_extras(ctx['info_sets_n1'], fold1_arr,
                                     ctx['L1_arr'], ctx['D1'], ctx['inv_D1'], p)
        d1 = n1 - k1 - int(extras_l1.max())
        if d1 <= w_J_L1:
            bad_a1 += 1
        fold1 = fold1_arr.tolist()
        fold1_e, fold1_o = even_odd_parts(fold1, ctx['L1'], p)
        bc, _ = compute_d2_and_count(fold1_e, fold1_o, ctx['lagrange_pairs'],
                                       p, n2, k2, w_J_L2)
        V_delta += bc

    P_acc = V_delta / (p * p)
    return True, bad_a1, V_delta, P_acc, d_f_lower


def main():
    n0, k0 = 32, 8
    R = 2
    primes = [97, 193, 257, 449, 577, 769, 1153]
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
    print(f"=== q-scaling of |V_δ|/q² for 24 count=9 supports ===", flush=True)
    print(f"  (n_0, k_0) = ({n0}, {k0}), R = {R}", flush=True)
    print(f"  primes (≡ 1 mod 32): {primes}", flush=True)
    print(flush=True)

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
    all_supports = [(s, 'sigma=()') for s in sigma_empty_supports] + \
                   [(s, 'sigma_9=0') for s in sigma_9_supports]

    # Precompute deterministic master coefs per support (q-independent ints)
    sup_coefs = {}
    for sup, _ in all_supports:
        rng = random.Random(hash(sup) & 0xFFFFFFFF)
        sup_coefs[sup] = [rng.randrange(1, 10**6) for _ in range(3)]

    results = {}  # (sup, p) → (above_J, bad_a1, V_delta, P_acc, d_f)
    t_total = time.time()
    for p in primes:
        print(f"\n=== q = {p} ===", flush=True)
        t_ctx = time.time()
        ctx = setup_q_context(p, n0, k0, R)
        t_ctx_done = time.time() - t_ctx
        print(f"  ctx setup {t_ctx_done:.1f}s", flush=True)
        for sup_idx, (sup, label) in enumerate(all_supports):
            t0 = time.time()
            try:
                above_J, bad_a1, V_delta, P_acc, d_f = run_one_with_ctx(
                    sup, sup_coefs[sup], ctx)
            except ValueError as e:
                print(f"    [{sup_idx+1:2d}/24] sup={sup}: ERROR {e}", flush=True)
                continue
            elapsed = time.time() - t0
            results[(sup, p)] = (above_J, bad_a1, V_delta, P_acc, d_f)
            tag = "ABOVE-J" if above_J else "below-J"
            ratio_v = V_delta / (p*p) if above_J else 0.0
            ratio_a = bad_a1 / p if above_J else 0.0
            sup_mod4 = tuple(j % 4 for j in sup)
            print(f"    [{sup_idx+1:2d}/24] sup={sup} mod4={sup_mod4} ({label}) "
                  f"{tag} d_f≥{d_f:2d} count_a1={bad_a1:5d} ({ratio_a:.4f}) "
                  f"|V_δ|={V_delta:7d} |V_δ|/q²={ratio_v:.6f} [{elapsed:.1f}s]",
                  flush=True)
        # free ctx between primes
        del ctx

    elapsed_total = time.time() - t_total
    print(f"=== Done in {elapsed_total:.0f}s ===")

    # --- Summary tables ---
    print("\n=== SCALING SUMMARY ===")
    print(f"\nTable 1: count_α₁(q) per support (above-J only)")
    header = "sup".ljust(18) + "  ".join(f"q={p:5d}" for p in primes)
    print(header)
    for sup, label in all_supports:
        row = f"{str(sup):18s}"
        for p in primes:
            r = results.get((sup, p))
            if r is None or not r[0]:
                row += "    --   "
            else:
                row += f"  {r[1]:5d}    "[:9]
        print(row)

    print(f"\nTable 2: |V_δ|/q² per support (above-J only)")
    print(header)
    for sup, label in all_supports:
        row = f"{str(sup):18s}"
        for p in primes:
            r = results.get((sup, p))
            if r is None or not r[0]:
                row += "    --   "
            else:
                ratio = r[2] / (p*p)
                row += f"  {ratio:.4f}  "[:9]
        print(row)

    print(f"\nTable 3: count_α₁/q per support (= bad fraction at level 1)")
    print(header)
    for sup, label in all_supports:
        row = f"{str(sup):18s}"
        for p in primes:
            r = results.get((sup, p))
            if r is None or not r[0]:
                row += "    --   "
            else:
                ratio = r[1] / p
                row += f"  {ratio:.4f}  "[:9]
        print(row)

    # --- key observation: max |V_δ|/q² across all 24 supports per q ---
    print(f"\nTable 4: per-q MAX |V_δ|/q² across 24 supports")
    print(f"  q       max|V_δ|/q²    max count_α₁    max count_α₁/q")
    for p in primes:
        max_ratio = 0.0
        max_count = 0
        for sup, _ in all_supports:
            r = results.get((sup, p))
            if r and r[0]:
                ratio = r[2] / (p*p)
                if ratio > max_ratio:
                    max_ratio = ratio
                if r[1] > max_count:
                    max_count = r[1]
        print(f"  {p:5d}   {max_ratio:.6f}      {max_count:5d}          {max_count/p:.6f}")


if __name__ == "__main__":
    main()
