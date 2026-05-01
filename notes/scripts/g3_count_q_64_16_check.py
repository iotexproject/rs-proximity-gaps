"""g3_count_q_64_16_check.py — verify μ_{n_1/2}-subdomain theorem at (64, 16).

Predicts: count_α = q ⟺ DFT supp ⊂ {32, 33, ..., 47}.

Spot-check on a few supports:
  - YES side: a few sup ⊂ {32..47} → expect count = q.
  - NO side: a few sup outside {32..47} → expect count < q (sample verify).

At (64, 16), n_1 = 32, k_1 = 8. C(32, 8) = 10518300 info sets at L_1 — too many
for full enum. Use SAMPLED info sets (50000) for d_1 estimation. This gives a
LOWER bound on max_extras, which may underestimate count for "borderline" supports.
But for the count=q theorem, we expect d_1 ≤ n_1/2 = 16 to hold trivially via
the subdomain mechanism — so the L_1-DFT structure forces d_1 ≤ 16 deterministically,
detected easily by sampling.

Use small q = 257 to keep alpha range manageable.
"""
import sys, os, math, random, time
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


def count_bad_alpha_sampled(positions, coeffs, p, n0, k0, threshold,
                             L0, L1_arr, info_sets, D1, inv_D1):
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
        extras = batched_extras(info_sets, fold, L1_arr, D1, inv_D1, p)
        d1_estimate = n1 - k1 - int(extras.max())  # upper bound on true d_1
        if d1_estimate <= threshold:
            cnt += 1
    return cnt


def main():
    # smallest q with 64 | q-1
    p = 257
    n0, k0 = 64, 16
    n1, k1 = 32, 8
    threshold = n1 - int(math.isqrt(k1 * n1))  # = 32 - 16 = 16

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L1_arr = np.array(L1, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    # sample info sets (50k)
    rng = np.random.default_rng(42)
    all_T = list(combinations(range(n1), k1))  # 10.5M total
    n_sample = 50000
    idx = rng.choice(len(all_T), size=n_sample, replace=False)
    info_sets = np.array([all_T[i] for i in idx], dtype=np.int64)

    rng_p = random.Random(2026)

    print(f"=== Verify μ_{{n_1/2}} subdomain theorem at (64, 16), q={p} ===")
    print(f"  Predicts: count_α = q ⟺ DFT supp ⊂ {{32..47}}")
    print(f"  Threshold for d_1 ≤ {threshold}, sampled {n_sample} info sets at L_1\n")

    # YES side: 5 supports ⊂ {32..47} (with mixed parity)
    target = list(range(32, 48))
    yes_sups = []
    for sup in combinations(target, 3):
        has_e = any(j % 2 == 0 for j in sup)
        has_o = any(j % 2 == 1 for j in sup)
        if has_e and has_o:
            yes_sups.append(sup)
    print(f"YES side: {len(yes_sups)} mixed-parity 3-pos supports ⊂ {{32..47}}")
    sample_yes = rng_p.sample(yes_sups, 5)
    for sup in sample_yes:
        coeffs = tuple(rng_p.randrange(1, p) for _ in range(3))
        t0 = time.time()
        cnt = count_bad_alpha_sampled(sup, coeffs, p, n0, k0, threshold,
                                       L0, L1_arr, info_sets, D1, inv_D1)
        elapsed = time.time() - t0
        tag = "count=q ✓" if cnt == p else f"count={cnt} ≠ q ✗"
        print(f"  sup={sup} coeffs={coeffs}: {tag}  [{elapsed:.0f}s]")

    # NO side: 5 supports outside {32..47}
    print(f"\nNO side: 5 supports outside {{32..47}}")
    other = []
    for sup in combinations(range(16, 64), 3):
        if all(j in target for j in sup):
            continue
        has_e = any(j % 2 == 0 for j in sup)
        has_o = any(j % 2 == 1 for j in sup)
        if has_e and has_o:
            other.append(sup)
    sample_no = rng_p.sample(other, 5)
    for sup in sample_no:
        coeffs = tuple(rng_p.randrange(1, p) for _ in range(3))
        t0 = time.time()
        cnt = count_bad_alpha_sampled(sup, coeffs, p, n0, k0, threshold,
                                       L0, L1_arr, info_sets, D1, inv_D1)
        elapsed = time.time() - t0
        tag = f"count={cnt}"
        if cnt < p / 2:
            tag += " ✓ (count < q)"
        else:
            tag += " ⚠ (count near q)"
        print(f"  sup={sup} coeffs={coeffs}: {tag}  [{elapsed:.0f}s]")


if __name__ == "__main__":
    main()
