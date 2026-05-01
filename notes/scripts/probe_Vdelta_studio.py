"""probe_Vdelta_studio.py — STUDIO version: parallel verification of |V_δ| ≤ R q^{R-1}.

Properly filters above-Johnson f's (skips below-Johnson degenerate cases).
Uses multiprocessing for per-f parallelism.

Usage:
  python3 probe_Vdelta_studio.py <p> <n_0> <k_0> <R> <delta_frac> [n_random=200] [n_workers=auto]

Output: notes/scripts/probe_Vdelta_studio_p{p}_n{n0}_R{R}.output.txt
"""
from __future__ import annotations
import sys, os, time, random, math
from itertools import product, combinations
from multiprocessing import Pool, cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


def is_above_johnson(f, H0, n0, k0, p):
    """Returns (is_above, dist_to_C_0)."""
    rho = k0 / n0
    w_J = int((1 - math.sqrt(rho)) * n0)
    d, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J + 2)
    if d is None:
        return True, None  # dist > w_J + 2, definitely above-J
    return d > w_J, d


def measure_Vdelta_for_f(args):
    """Worker: computes |V_δ| for a single f. Returns (label, v_delta, ratio_to_phase1, dist_C0)."""
    fname, f, p, n0, k0, R, delta = args
    chain = setup_chain(p, n0, k0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    H0 = chain[0][2]
    w_R = int(delta * n_R)
    bound_phase1 = R * p**(R-1)

    # Filter
    is_above, d0 = is_above_johnson(f, H0, n0, k0, p)
    if not is_above:
        return (fname, None, None, d0, "BELOW-JOHNSON")

    v_delta = 0
    for alphas in product(range(p), repeat=R):
        g = true_fold_R(f, chain, list(alphas), p)
        d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
        if d is not None and d <= w_R:
            v_delta += 1
    ratio = v_delta / bound_phase1
    return (fname, v_delta, ratio, d0, None)


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 probe_Vdelta_studio.py <p> <n_0> <k_0> <R> <delta_frac> [n_random=200] [n_workers=auto]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])
    n_random = int(sys.argv[6]) if len(sys.argv) > 6 else 200
    n_workers = int(sys.argv[7]) if len(sys.argv) > 7 else max(1, cpu_count() - 1)

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    w_R = int(delta * n_R)
    qR = p ** R
    bound_phase1 = R * p**(R-1)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, q^R={qR}")
    print(f"# Phase 1 bound R q^{{R-1}} = {bound_phase1}")
    print(f"# Johnson w_J = {w_J} (only test f with dist(f, C_0) > {w_J})")
    print(f"# n_workers = {n_workers}")
    print()

    # Build candidate f-list (above-Johnson only)
    rng = random.Random(2026)
    candidate_f_list = []

    # Pairs in syndrome window
    for a, b in combinations(range(k0, n0), 2):
        fhat = [0]*n0; fhat[a] = 1; fhat[b] = 1
        candidate_f_list.append((f"pair:X^{a}+X^{b}", evaluate_dft(fhat, L0, p)))

    # Random sparse with random nonzero coeffs
    for trial in range(n_random):
        sparsity = rng.choice([2, 3, 4, 5])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        candidate_f_list.append((f"sparse_{sorted(positions)}_{trial}", evaluate_dft(fhat, L0, p)))

    print(f"# Built {len(candidate_f_list)} candidate f's. Filtering above-Johnson + measuring V_δ...")

    # Parallel
    args_list = [(fname, f, p, n0, k0, R, delta) for fname, f in candidate_f_list]

    t0 = time.time()
    print(f"# {'f':40s} {'dist_C0':>8s} {'|V_δ|':>10s} {'ratio':>8s}")
    print("-" * 75)
    max_ratio = 0.0; max_f = None; falsifiers = 0; n_above = 0
    with Pool(n_workers) as pool:
        for result in pool.imap_unordered(measure_Vdelta_for_f, args_list):
            fname, v_delta, ratio, d0, status = result
            if status == "BELOW-JOHNSON":
                continue
            n_above += 1
            d_str = f"{d0}" if d0 is not None else ">w_J"
            if ratio > max_ratio:
                max_ratio = ratio; max_f = fname
            if ratio > 1.001:
                falsifiers += 1
                print(f"  {fname:40s} {d_str:>8s} {v_delta:10d} {ratio:8.4f} ★FALSIFIER★", flush=True)
            elif ratio > 0.5 or n_above % 50 == 0:
                print(f"  {fname:40s} {d_str:>8s} {v_delta:10d} {ratio:8.4f}", flush=True)
    print("-" * 75)
    print(f"# Tested {len(candidate_f_list)} candidates, {n_above} above-Johnson")
    print(f"# Time: {time.time()-t0:.0f}s")
    print(f"# Max ratio |V_δ|/(R q^{{R-1}}): {max_ratio:.4f} ({max_f})")
    print(f"# Falsifiers: {falsifiers}")


if __name__ == '__main__':
    main()
