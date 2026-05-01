"""g3_lift_K2_counterexample.py — lift the rank-2 K=2 low-overlap
counterexample from reviewed-branch Note 0114 (q=97) to larger primes.

Original counterexample (Note 0114):
  q=97, n_0=32, k_0=8, fhat = dense over positions 8..31 with specific
  small-int coefs. |V_δ| = 287 = 3q - 4 > 2q = 194 at q=97.

Question: as q grows along q ≡ 1 mod 32, does this construction still
give above-J f, and does |V_δ|/q grow, shrink, or stay constant?

If |V_δ|/q^2 stays ≥ const → #344 NEGATIVE counterexample (prize-grade).
If |V_δ|/q^2 ~ const/q → zero-loss preserved with tighter constant.
"""
import sys, os, math, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations

from fri_2round_attack import setup_chain, even_odd_parts, modinv
from mds_decoder import precompute_diff_inv, batched_extras


# Dense coefficients from reviewed-branch Note 0114 (q=97 origin)
K2_COEFS = {
    8: 85, 9: 73, 10: 61, 11: 25,
    12: 53, 13: 9, 14: 62, 15: 80,
    16: 21, 17: 42, 18: 63, 19: 22,
    20: 4, 21: 8, 22: 12, 23: 91,
    24: 63, 25: 29, 26: 92, 27: 13,
    28: 6, 29: 12, 30: 18, 31: 89,
}


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


def compute_d2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
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
    return int((d2_vec <= w_J_L2).sum())


def run_at_q(p, n0=32, k0=8, R=2, exact_l0=True):
    """Compute count_α₁, |V_δ| for the K=2 lift at prime q.
    exact_l0=True uses full C(32,8) info-set enumeration (memory hungry,
    ~340MB array). Otherwise sampled."""
    n1 = n0 // 2; k1 = k0 // 2
    n2 = n0 // 4; k2 = k0 // 4
    w_J_L0 = n0 - int(math.isqrt(k0 * n0))
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))

    chain = setup_chain(p, n0, k0, R=R)
    L0, L1, L2 = chain[0][0], chain[1][0], chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    if exact_l0:
        info_sets_n0 = np.array(list(combinations(range(n0), k0)),
                                  dtype=np.int64)
    else:
        all_T = list(combinations(range(n0), k0))
        rng = np.random.default_rng(42)
        idx = rng.choice(len(all_T), size=20000, replace=False)
        info_sets_n0 = np.array([all_T[i] for i in idx], dtype=np.int64)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    fhat = [0] * n0
    for j, c in K2_COEFS.items():
        fhat[j] = c % p

    f = evaluate_dft(fhat, L0, p)
    f_arr = np.array(f, dtype=np.int64)

    # Above-J check (memory frugal: chunk the info_sets if large)
    chunk = 1_000_000
    max_extras_l0 = 0
    for s in range(0, len(info_sets_n0), chunk):
        end = min(s + chunk, len(info_sets_n0))
        ext = batched_extras(info_sets_n0[s:end], f_arr, L0_arr,
                              D0, inv_D0, p)
        m = int(ext.max())
        if m > max_extras_l0:
            max_extras_l0 = m
    d_f_lower = n0 - k0 - max_extras_l0
    above_J = d_f_lower > w_J_L0
    info_sets_n0 = None  # free

    if not above_J:
        return {'q': p, 'above_J': False, 'd_f_lower': d_f_lower,
                'count_a1': 0, 'V_delta': 0}

    f_e, f_o = even_odd_parts(f, L0, p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    bad_a1 = 0
    V_delta = 0
    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        extras_l1 = batched_extras(info_sets_n1, fold1_arr,
                                     L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras_l1.max())
        if d1 <= w_J_L1:
            bad_a1 += 1
        fold1 = fold1_arr.tolist()
        fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
        bc = compute_d2_count(fold1_e, fold1_o, lagrange_pairs,
                                p, n2, k2, w_J_L2)
        V_delta += bc

    return {'q': p, 'above_J': True, 'd_f_lower': d_f_lower,
            'count_a1': bad_a1, 'V_delta': V_delta}


def main():
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
    primes = [97, 193, 257, 449, 577, 769, 1153]
    print(f"=== Lift K=2 low-overlap counterexample (Note 0114) to multi-q ===",
          flush=True)
    print(f"  Source: |V_δ|=287=3q-4 at q=97, dense coefs in {{8..31}}",
          flush=True)
    print(f"  Coefs all <97, so mod q just stays as integers for q≥97",
          flush=True)
    print()

    rows = []
    for p in primes:
        # Use sampled L_0 above-J check at all q (20K info sets, plenty);
        # exact only at q=97 to confirm reproduction of Note 0114's count
        exact = (p == 97)
        t0 = time.time()
        try:
            r = run_at_q(p, exact_l0=exact)
        except MemoryError as e:
            print(f"  q={p}: MEM ERROR {e}", flush=True)
            continue
        elapsed = time.time() - t0
        rows.append(r)
        if r['above_J']:
            ratio_v = r['V_delta'] / (p * p)
            ratio_v_q = r['V_delta'] / p
            ratio_a = r['count_a1'] / p
            print(f"q={p:5d} (exact_l0={exact}): ABOVE-J d_f≥{r['d_f_lower']:2d}  "
                  f"count_a1={r['count_a1']:5d} ({ratio_a:.4f})  "
                  f"|V_δ|={r['V_delta']:7d}  |V_δ|/q={ratio_v_q:.3f}  "
                  f"|V_δ|/q²={ratio_v:.5f}  [{elapsed:.0f}s]", flush=True)
        else:
            print(f"q={p:5d}: below-J d_f≥{r['d_f_lower']}  [{elapsed:.0f}s]",
                  flush=True)

    print(f"\n=== Summary table ===")
    print(f"{'q':>6}  {'above_J':>8}  {'d_f':>5}  {'count_a1':>10}  "
          f"{'|V_δ|':>8}  {'|V_δ|/q':>8}  {'|V_δ|/q²':>10}")
    for r in rows:
        if r['above_J']:
            ratio_v = r['V_delta'] / (r['q'] * r['q'])
            ratio_v_q = r['V_delta'] / r['q']
            print(f"{r['q']:6d}  {'YES':>8}  {r['d_f_lower']:5d}  "
                  f"{r['count_a1']:10d}  {r['V_delta']:8d}  "
                  f"{ratio_v_q:8.3f}  {ratio_v:10.5f}")
        else:
            print(f"{r['q']:6d}  {'NO':>8}  {r['d_f_lower']:5d}  "
                  f"{'-':>10}  {'-':>8}  {'-':>8}  {'-':>10}")


if __name__ == "__main__":
    main()
