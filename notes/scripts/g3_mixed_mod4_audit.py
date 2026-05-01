"""g3_mixed_mod4_audit.py — for 3-pos sparse f̂ at (32, 8) with MIXED
mod-4 supports (positions in BOTH {0,1} and {2,3}), check whether
Theorem 0170's closed form |V_δ| = |B_1|·q + ε·(q − |B_1|) still holds.

Conjecture: it DOESN'T — fold² is genuinely α_2-dependent, so the
analysis differs. The deviation should reveal where character-sum bounds
are needed for #343.
"""
import sys, os, math, random, time
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


def compute_d2_count(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
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
    return int((d2_vec <= w_J_L2).sum()), d2_vec


def classify_mod4(sup):
    """Return one of: 'all{0,1}', 'all{2,3}', 'mixed_01_2', 'mixed_01_3',
    'mixed_2_01', 'mixed_3_01', 'mixed_general'."""
    classes = [j % 4 for j in sup]
    in_01 = sum(1 for c in classes if c in (0, 1))
    in_23 = sum(1 for c in classes if c in (2, 3))
    if in_23 == 0: return 'all{0,1}', classes
    if in_01 == 0: return 'all{2,3}', classes
    return f'mixed[{in_01}:{in_23}]', classes


def main():
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)

    p = 97
    n0, k0 = 32, 8
    R = 2
    n1, k1 = 16, 4
    n2, k2 = 8, 2
    w_J_L0 = n0 - int(math.isqrt(k0 * n0))  # 16
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))  # 8
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))  # 4

    print(f"=== Mixed mod-4 audit at q={p} (32, 8) ===")
    print(f"  w_J(L_0)={w_J_L0}, w_J(L_1)={w_J_L1}, w_J(L_2)={w_J_L2}")

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    L2_arr = np.array(L2, dtype=np.int64)
    D0, inv_D0 = precompute_diff_inv(L0_arr, p)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    # SAMPLED L_0 info sets (full 10.5M too slow). 30K sample is enough
    # to certify above-J empirically.
    all_T_n0 = list(combinations(range(n0), k0))
    rng_l0 = np.random.default_rng(2026)
    idx = rng_l0.choice(len(all_T_n0), size=30000, replace=False)
    info_sets_n0 = np.array([all_T_n0[i] for i in idx], dtype=np.int64)
    info_sets_n1 = np.array(list(combinations(range(n1), k1)), dtype=np.int64)
    info_sets_n2 = np.array(list(combinations(range(n2), k2)), dtype=np.int64)
    lagrange_pairs = precompute_lagrange_pairs(L2_arr, info_sets_n2, p)

    # Enumerate all 3-pos supports in {8, ..., 31}, classify by mod-4
    all_sups = list(combinations(range(8, 32), 3))
    print(f"  Total 3-pos supports in {{8..31}}: {len(all_sups)}")

    # Group by mod-4 classification
    from collections import defaultdict
    classification = defaultdict(list)
    for sup in all_sups:
        cl, _ = classify_mod4(sup)
        classification[cl].append(sup)
    print(f"  Mod-4 class counts:")
    for cl, sups in sorted(classification.items()):
        print(f"    {cl}: {len(sups)}")

    # For each MIXED class, sample some supports and check |V_δ| structure
    print(f"\n=== Mixed-class samples: |V_δ| structure ===")
    rng = random.Random(42)
    rows = []  # for analysis

    classes_to_sample = sorted([cl for cl in classification if cl.startswith('mixed')])
    print(f"  Mixed classes: {classes_to_sample}")
    samples_per_class = 8

    for cl in classes_to_sample:
        sups_in_class = classification[cl]
        sample = rng.sample(sups_in_class, min(samples_per_class, len(sups_in_class)))
        print(f"\n  --- Class {cl} (sampling {len(sample)}/{len(sups_in_class)}) ---")
        for sup in sample:
            sup_mod4 = tuple(j % 4 for j in sup)
            # Use deterministic seeded coefs
            sup_rng = random.Random(hash(sup) & 0xFFFFFFFF)
            coefs = [sup_rng.randrange(1, 10**6) for _ in range(3)]
            fhat = [0]*n0
            for j, c in zip(sup, coefs): fhat[j] = c % p

            f = evaluate_dft(fhat, L0, p)
            f_arr = np.array(f, dtype=np.int64)
            # exact L_0 above-J check
            extras_l0 = batched_extras(info_sets_n0, f_arr, L0_arr, D0, inv_D0, p)
            d_f = n0 - k0 - int(extras_l0.max())
            if d_f <= w_J_L0:
                continue

            f_e, f_o = even_odd_parts(f, L0, p)
            fe_arr = np.array(f_e, dtype=np.int64)
            fo_arr = np.array(f_o, dtype=np.int64)

            bad_a1 = 0
            V_delta = 0
            B_1 = []
            # also track per-α_1 V_δ slice for stratification
            per_a1_bad_count = []
            for a1 in range(p):
                fold1_arr = (fe_arr + a1 * fo_arr) % p
                e1 = batched_extras(info_sets_n1, fold1_arr, L1_arr, D1, inv_D1, p)
                d1 = n1 - k1 - int(e1.max())
                if d1 <= w_J_L1:
                    bad_a1 += 1
                    B_1.append(a1)
                fold1 = fold1_arr.tolist()
                fold1_e, fold1_o = even_odd_parts(fold1, L1, p)
                bc, _ = compute_d2_count(fold1_e, fold1_o, lagrange_pairs,
                                          p, n2, k2, w_J_L2)
                V_delta += bc
                per_a1_bad_count.append(bc)

            # Check closed form match
            # mod-4 uniform predictions
            cl_uniform = (cl == 'all{0,1}') or (cl == 'all{2,3}')
            if cl == 'all{0,1}': eps_pred = 0
            elif cl == 'all{2,3}': eps_pred = 1
            else: eps_pred = None  # mixed

            pred_uniform = bad_a1 * p + (eps_pred if eps_pred is not None else 0) * (p - bad_a1) if eps_pred is not None else None
            pred_uniform_str = f"closed pred={pred_uniform}" if pred_uniform is not None else "MIXED — no closed pred"
            deviation = V_delta - pred_uniform if pred_uniform is not None else None

            # For mixed: distribution of per-α_1 |V_δ slice| sizes
            from collections import Counter
            per_a1_dist = Counter(per_a1_bad_count)
            # Show top 5 most common slice sizes
            top_slices = sorted(per_a1_dist.items(), key=lambda x: -x[1])[:5]

            print(f"    sup={sup} mod4={sup_mod4} d_f≥{d_f}")
            print(f"      |B_1|={bad_a1}, |V_δ|={V_delta}, |V_δ|/q={V_delta/p:.2f}")
            print(f"      per-α₁ slice dist (top 5): {top_slices}")
            print(f"      vs closed form: {pred_uniform_str}, deviation = {deviation}")
            rows.append({
                'sup': sup, 'mod4': sup_mod4, 'class': cl,
                'd_f': d_f, 'B1': bad_a1, 'V_delta': V_delta,
                'per_a1_dist': dict(per_a1_dist),
                'pred_uniform': pred_uniform, 'deviation': deviation,
            })

    # Summary table
    print(f"\n\n=== SUMMARY: deviation from closed-form by mixed class ===")
    print(f"{'class':>20} {'sup':>20} {'B_1':>4} {'|V_δ|':>7} {'|V_δ|/q':>9} {'V_δ - 0·q':>12}")
    for r in rows:
        v_q = r['V_delta'] / p
        # baseline: |B_1| · q (mod-4⊂{0,1} closed form)
        baseline = r['B1'] * p
        excess = r['V_delta'] - baseline
        print(f"{r['class']:>20} {str(r['sup']):>20} {r['B1']:>4} {r['V_delta']:>7} "
              f"{v_q:>9.2f} {excess:>12}")


if __name__ == "__main__":
    main()
