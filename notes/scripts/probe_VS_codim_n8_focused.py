"""probe_VS_codim_n8_focused.py — focused test on n_R=8, w_R=3 case.

Only checks |V_δ| (not per-T breakdown) for fast iteration.

Usage: python3 probe_VS_codim_n8_focused.py <p> <n_0> <k_0> <R> <delta>
"""
from __future__ import annotations
import sys, time, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, dist_to_code_full
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
    R = int(sys.argv[4]); delta = float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    qR = p ** R
    Rq = R / p
    bound_phase1 = R * p**(R-1)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, q^R={qR}, R q^{{R-1}}={bound_phase1}")
    print()

    # f's
    rng = random.Random(2026)
    f_list = []
    cs_a = 2 * (2**R) - 1; cs_b = 2 * (2**R) - 2
    if cs_a < n0 and cs_b < n0:
        fhat = [0]*n0; fhat[cs_a] = 1; fhat[cs_b] = 1
        f_list.append((f"CS:X^{cs_a}+X^{cs_b}", evaluate_dft(fhat, L0, p)))

    # All pairs in syndrome window (truncated)
    pairs = list(combinations(range(k0, n0), 2))
    pairs = pairs[:30]  # take first 30 only
    for a, b in pairs:
        fhat = [0]*n0; fhat[a] = 1; fhat[b] = 1
        f_list.append((f"pair:X^{a}+X^{b}", evaluate_dft(fhat, L0, p)))

    # Random sparse
    for trial in range(20):
        sparsity = rng.choice([2, 3, 4])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f_list.append((f"sparse_{sorted(positions)}", evaluate_dft(fhat, L0, p)))

    print(f"# {'f':40s} {'|V_δ|':>10s} {'ratio':>8s}")
    print("-" * 70)
    max_ratio = 0.0; max_f = None; falsifiers = 0
    t0 = time.time()
    for fname, f in f_list:
        v_delta = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
            if d is not None and d <= w_R:
                v_delta += 1
        ratio = v_delta / bound_phase1
        if ratio > max_ratio:
            max_ratio = ratio; max_f = fname
        if ratio > 1.001:
            falsifiers += 1
            print(f"  {fname:40s} {v_delta:10d} {ratio:8.4f} ★FALSIFIER★")
        else:
            print(f"  {fname:40s} {v_delta:10d} {ratio:8.4f}")
    print("-" * 70)
    print(f"# Tested {len(f_list)} f's. Time {time.time()-t0:.0f}s")
    print(f"# Max ratio: {max_ratio:.4f} ({max_f})")
    print(f"# Falsifiers: {falsifiers}")


if __name__ == '__main__':
    main()
