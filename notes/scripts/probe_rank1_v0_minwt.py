"""probe_rank1_v0_minwt.py — for rank-1 above-J f's, compute min-wt of image-line v_0.

Goal: empirically verify min-wt(v_0) > w_R for ALL above-J f's with rank-1 image.
This would confirm Path γ structural claim.
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full,
    gauss_rank, modinv
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


def min_wt_for_syndrome(target, H, n_R, p, max_w):
    """Find min-wt e with H · e = target. Return None if > max_w."""
    if all(x == 0 for x in target):
        return 0
    for w in range(1, max_w + 1):
        for T in combinations(range(n_R), w):
            for vals in product(range(1, p), repeat=w):
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = vals[idx]
                syn = tuple(matvec(H, e, p))
                if syn == tuple(target):
                    return w
    return None  # > max_w


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    n_trials = int(sys.argv[5]) if len(sys.argv) > 5 else 200

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)
    m = n_R - k_R

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}")
    print(f"# n_R={n_R}, k_R={k_R}, m={m}, w_J={w_J}")
    print()

    rng = random.Random(2026)
    n_above = 0
    rank1_data = []  # list of (label, dist_C0, v_0, min_wt)

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

        # Compute image
        image_set = set()
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image_set.add(syn)
        nonzero = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero, p) if nonzero else 0

        if r == 1:
            v_0 = nonzero[0]
            min_w = min_wt_for_syndrome(v_0, H_R, n_R, p, max_w=m)
            d0_str = f"{d0}" if d0 is not None else f">{w_J}"
            rank1_data.append((sorted(positions), d0_str, v_0, min_w))

        if trial % 20 == 0:
            print(f"  trial {trial}: {n_above} above-J, {len(rank1_data)} rank-1", flush=True)

    print()
    print(f"# === Rank-1 cases: ({len(rank1_data)} found) ===")
    print(f"# {'positions':<25s} {'dist_C0':>8s} {'v_0_normalized':<25s} {'min_wt':>8s}")
    print("-" * 75)
    for sp, d0, v0, mw in rank1_data:
        # normalize v_0
        for x in v0:
            if x != 0:
                inv = modinv(x, p)
                v0_n = tuple((y * inv) % p for y in v0)
                break
        mw_str = f"{mw}" if mw is not None else f">{m}"
        print(f"  sparse_{str(sp):<20s} {d0:>8s} {str(v0_n):<25s} {mw_str:>8s}")

    print()
    if rank1_data:
        wts = [mw for _, _, _, mw in rank1_data if mw is not None]
        print(f"# Min weights distribution: min={min(wts)}, max={max(wts)}, n={len(wts)}")
        print(f"# Path γ holds for w_test < min_wt: {min(wts)}")


if __name__ == '__main__':
    main()
