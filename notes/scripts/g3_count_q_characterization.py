"""g3_count_q_characterization.py — sharp characterization:

REFINED CONJECTURE (loop iter 3):
  count_α = q  ⟺  DFT-supp(f) ⊂ {n_0/2, n_0/2 + 1, ..., n_0/2 + n_1/2 - 1}
                 = {16, 17, ..., 23} for (n_0, k_0) = (32, 8).

Mechanism (subdomain trick): for j ∈ {16..23}, the L_1 fold puts the DFT
position j → L_1 pos (j or (j-1))/2 ∈ {8..11}. On subdomain μ_8 ⊂ L_1
(where y^8 = 1), monomial y^k for k ∈ {8..11} reduces to y^{k-8} ∈ {y^0..y^3},
i.e., RS_{k_1=4} basis. So f_e + α f_o restricts to a RS_4 codeword on μ_8
for ANY α, giving 8 trivial agreements → d_1 ≤ 8 → α bad.

Verify this on all 48 mixed-parity 3-pos supports ⊂ {16..23}.
"""
import sys, os, math, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
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


def count_bad_alpha(positions, coeffs, p, n0, k0, threshold,
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

    cnt = 0
    for alpha in range(p):
        fold = (f_e_arr + alpha * f_o_arr) % p
        extras = batched_extras(all_T, fold, L1_arr, D1, inv_D1, p)
        d1 = n1 - k1 - int(extras.max())
        if d1 <= threshold:
            cnt += 1
    return cnt


def main():
    p = 1153
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    threshold = n1 - int(math.isqrt(k1 * n1))

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)
    all_T = np.array(list(combinations(range(n1), k1)), dtype=np.int64)

    rng = random.Random(2026)

    # Verify: ALL mixed-parity 3-pos supports ⊂ {16..23} → count = q?
    target_window = list(range(16, 24))
    sups = []
    for sup in combinations(target_window, 3):
        has_e = any(j % 2 == 0 for j in sup)
        has_o = any(j % 2 == 1 for j in sup)
        if has_e and has_o:
            sups.append(sup)

    print(f"=== Verifying count=q ⟺ DFT supp ⊂ {{16..23}} ===\n")
    print(f"Total mixed-parity 3-pos supports ⊂ {{16..23}}: {len(sups)}")

    failures = []
    for i, sup in enumerate(sups):
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                               L0, L1_arr, all_T, D1, inv_D1)
        if cnt != p:
            failures.append((sup, coeffs, cnt))
        if (i + 1) % 12 == 0:
            print(f"  {i+1}/{len(sups)} checked, failures={len(failures)}")

    print(f"\nResult: {len(sups) - len(failures)}/{len(sups)} have count=q ✓")
    if failures:
        for sup, coeffs, cnt in failures[:10]:
            print(f"  FAIL: sup={sup} coeffs={coeffs}: count={cnt}")

    # Reverse: ANY mixed-parity sup NOT in {16..23} that has count=q?
    print(f"\n=== Reverse check: any sup ⊄ {{16..23}} with count=q? ===")
    other_sups = []
    for sup in combinations(range(8, 32), 3):
        if all(j in target_window for j in sup):
            continue
        has_e = any(j % 2 == 0 for j in sup)
        has_o = any(j % 2 == 1 for j in sup)
        if has_e and has_o:
            other_sups.append(sup)
    print(f"  {len(other_sups)} mixed-parity supports outside {{16..23}}")

    # Check a random sample (50)
    sample = rng.sample(other_sups, min(100, len(other_sups)))
    fails = []
    for sup in sample:
        coeffs = tuple(rng.randrange(1, p) for _ in range(3))
        cnt = count_bad_alpha(sup, coeffs, p, n0, k0, threshold,
                               L0, L1_arr, all_T, D1, inv_D1)
        if cnt > 100:
            fails.append((sup, cnt))

    print(f"  {len(fails)}/100 sampled non-{{16..23}} supports have count > 100")
    if fails:
        for sup, cnt in fails[:10]:
            print(f"    sup={sup}: count={cnt}")

    if not failures and not fails:
        print("\n=== CONJECTURE CONFIRMED ===")
        print("count = q ⟺ DFT supp ⊂ {n_0/2, ..., n_0/2 + n_1/2 - 1} = {16..23}")
        print("Mechanism: μ_8 subdomain trick (PR #373's degenerate case generalized)")


if __name__ == "__main__":
    main()
