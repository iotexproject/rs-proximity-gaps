"""g3_adversarial_count2.py — try to construct strict above-J f with count_α ≥ 2.

Approach: explicit constructions where 2 distinct α's would give |V_i| ≥ s.

Setup at (n_0, k_0) = (32, 8), s = √(k_1 n_1) = 8:
- Pick S ⊂ L_1 of size 7 (one less than s).
- Define f_e, f_o vanishing on S + extra positions.
- For each i ∈ L_1 \ S: equation A(i) + α B(i) = 0 has unique α (or none).
  → potentially many α's with |V_α| ≥ 8 (= |S| + 1 from extras).

If count ≥ 2 found WITH strict above-J: refutes count ≤ 1 conjecture.
If no count ≥ 2 found across many constructions: empirical evidence.

We sweep:
- S of size 6, 7
- Many choices of extra zeros for f_e and f_o
- Multiple q's
"""
import sys, os, math, random
import numpy as np
from itertools import combinations, product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def construct_f(p, S_idx, e_zeros, o_zeros, scale_e=1, scale_o=1, P_e=None, P_o=None):
    """Build f with f_e|_S = P_e|_S and f_o|_S = P_o|_S.

    Concretely: f_e(y) = P_e(y) + scale_e * prod (y - z) for z in (S ∪ e_zeros).
              f_o(y) = P_o(y) + scale_o * prod (y - z) for z in (S ∪ o_zeros).
    where the prod factor vanishes on S, ensuring f_e|_S = P_e|_S.
    """
    n0, k0 = 32, 8
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    n1 = len(L1); k1 = k0 // 2

    S_vals = [L1[i] for i in S_idx]
    all_e_zeros = S_vals + [L1[i] for i in e_zeros if i not in S_idx]
    all_o_zeros = S_vals + [L1[i] for i in o_zeros if i not in S_idx]

    if P_e is None: P_e = [0] * n1
    if P_o is None: P_o = [0] * n1
    f_e = [0] * n1
    f_o = [0] * n1
    for i in range(n1):
        y = L1[i]
        ve = scale_e
        for z in all_e_zeros:
            ve = (ve * (y - z)) % p
        f_e[i] = (P_e[i] + ve) % p
        vo = scale_o
        for z in all_o_zeros:
            vo = (vo * (y - z)) % p
        f_o[i] = (P_o[i] + vo) % p

    f = [0] * n0
    for i, x in enumerate(L0):
        x2 = (x * x) % p
        j = L1.index(x2)
        f[i] = (f_e[j] + x * f_o[j]) % p
    return f, f_e, f_o, L0, L1


def check_above_J(f_arr, L0_arr, p, w_J=16):
    n0, k0 = 32, 8
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    threshold = n0 - k0 - w_J
    max_extras = 0
    all_T = list(combinations(range(n0), k0))
    batch_size = 200000
    for start in range(0, len(all_T), batch_size):
        batch = all_T[start:start + batch_size]
        T_arr = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_arr, f_arr, L0_arr, D0, inv_D0, p)
        m = int(extras.max())
        if m > max_extras: max_extras = m
        if max_extras >= threshold:
            return False, n0 - k0 - max_extras
    return max_extras < threshold, n0 - k0 - max_extras


def count_alpha(f_e_arr, f_o_arr, L1_arr, p, n1=16, k1=4, sqrt_k1n1=8):
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    threshold_d1 = n1 - sqrt_k1n1
    bad_alphas = []
    for a in range(p):
        fold = (f_e_arr + a * f_o_arr) % p
        extras = batched_extras(info_sets_arr, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold_d1:
            bad_alphas.append((a, d1))
    return bad_alphas


def main():
    p = 97
    print(f"Adversarial sweep at q={p}, params (32,8)")

    n0, k0 = 32, 8
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    n1 = len(L1); k1 = k0 // 2

    found_count_geq_2 = []
    n_strict_above_J = 0
    n_total = 0

    rng = random.Random(2026)

    # Strategy: S of size 7 ⊂ L_1, plus 2 extra zeros for f_e and 2 for f_o.
    # For each α, count how many extras (in L_1 \ S) satisfy A(i) + α B(i) = 0.
    S_idx = list(range(7))

    # Try many (e_zeros, o_zeros, P_e, P_o, scale_e, scale_o) combinations
    extras_pool = list(range(7, n1))  # L_1 \ S
    n_attempts = 0
    while n_attempts < 200:
        n_attempts += 1
        # Pick e_zeros and o_zeros (sizes 1-3 each)
        n_e = rng.choice([1, 2, 3])
        n_o = rng.choice([1, 2, 3])
        e_zeros = rng.sample(extras_pool, n_e)
        o_zeros = rng.sample(extras_pool, n_o)
        scale_e = rng.randrange(1, p)
        scale_o = rng.randrange(1, p)
        # Sometimes also add a P_e, P_o ∈ C_1 (deg<4 polys)
        use_P = rng.random() < 0.5
        if use_P:
            P_e_coefs = [rng.randrange(0, p) for _ in range(k1)]
            P_o_coefs = [rng.randrange(0, p) for _ in range(k1)]
            P_e = [sum(P_e_coefs[d] * pow(y, d, p) for d in range(k1)) % p for y in L1]
            P_o = [sum(P_o_coefs[d] * pow(y, d, p) for d in range(k1)) % p for y in L1]
        else:
            P_e = None; P_o = None

        f, f_e, f_o, _, _ = construct_f(p, S_idx, e_zeros, o_zeros, scale_e, scale_o, P_e, P_o)
        f_arr = np.array(f, dtype=np.int64)
        n_zeros = sum(1 for v in f if v == 0)
        if n_zeros >= 16:
            n_total += 1
            continue  # below-J via zero codeword
        above_J, dist_f = check_above_J(f_arr, L0_arr, p)
        n_total += 1
        if not above_J:
            continue
        n_strict_above_J += 1
        f_e_arr = np.array(f_e, dtype=np.int64)
        f_o_arr = np.array(f_o, dtype=np.int64)
        bad = count_alpha(f_e_arr, f_o_arr, L1_arr, p, n1, k1)
        if len(bad) >= 2:
            found_count_geq_2.append({
                'e_zeros': e_zeros, 'o_zeros': o_zeros,
                'scale_e': scale_e, 'scale_o': scale_o,
                'use_P': use_P, 'dist_f': dist_f,
                'count': len(bad), 'bad_alphas': bad[:10]
            })
            print(f"  COUNT ≥ 2 FOUND: e_zeros={e_zeros}, o_zeros={o_zeros}, dist={dist_f}, count={len(bad)}")
            print(f"    bad α: {bad[:10]}")
        elif len(bad) == 1:
            pass  # expected
        else:
            pass  # count = 0
        if n_attempts % 50 == 0:
            print(f"  [{n_attempts}/200] strict_above_J={n_strict_above_J}, count≥2 cases={len(found_count_geq_2)}")

    print(f"\n=== Summary ===")
    print(f"  Attempts: {n_attempts}, strict above-J: {n_strict_above_J}, count ≥ 2: {len(found_count_geq_2)}")
    if found_count_geq_2:
        print("  Counterexamples to count ≤ 1 conjecture FOUND:")
        for case in found_count_geq_2:
            print(f"    {case}")
    else:
        print("  No counterexample found — count ≤ 1 conjecture survives at this scale.")


if __name__ == "__main__":
    main()
