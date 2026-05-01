"""probe_image_in_Bw_fast.py — sampling-based fast version.

For each above-J f, sample K random α's. If ANY α has dist(g(α), C_R) > w_test,
then image ⊄ B_w (proven for THIS f).

If image_in_Bw_for_all_K = True for ALL K samples → suspicious, do full enumeration.

Much faster than full enumeration since most α's have large dist.
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full
)


def true_fold_R(f, chain, alphas, p):
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); w_test = int(sys.argv[5])
    n_trials = int(sys.argv[6]) if len(sys.argv) > 6 else 100
    K = int(sys.argv[7]) if len(sys.argv) > 7 else 20  # samples per f

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, w_test={w_test}")
    print(f"# n_R={n_R}, k_R={k_R}, m={n_R-k_R}, w_J={w_J}")
    print(f"# Sampling K={K} α's per f")
    print()

    rng = random.Random(2026)
    n_above = 0
    n_image_might_be_in_Bw = 0  # all K samples in B_w

    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue
        n_above += 1

        all_in_Bw = True
        for s in range(K):
            alphas = [rng.randrange(p) for _ in range(R)]
            g = true_fold_R(f, chain, alphas, p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_test)
            if d is None or d > w_test:
                all_in_Bw = False
                break
        if all_in_Bw:
            n_image_might_be_in_Bw += 1
            print(f"  ★ ALL {K} samples ≤ w: trial {trial}, sparse_{sorted(positions)}", flush=True)

        if trial % 10 == 0:
            print(f"  trial {trial}: {n_above} above-J, {n_image_might_be_in_Bw} all-K-in-Bw", flush=True)

    print()
    print(f"# === SUMMARY ===")
    print(f"# Trials: {n_trials}, above-J: {n_above}")
    print(f"# All-K-samples-in-B_w: {n_image_might_be_in_Bw}")
    if n_image_might_be_in_Bw == 0:
        print(f"# *** ALL above-J f's had at least one α with g(α) far from C_R. ***")
        print(f"# *** Strongly supports: image ⊄ B_{w_test} for above-J f. ***")


if __name__ == '__main__':
    main()
