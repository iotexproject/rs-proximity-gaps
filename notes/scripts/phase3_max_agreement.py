"""phase3_max_agreement.py — Issue #343 Phase 3: directly measure max_c A_c(α).

For each α-tuple, find dist(true_fold_R, C_R) via brute force; then max_c A_c(α) = n_R - dist.
Compare to (1-δ) n_R (the cheater's target).

Outputs histogram: (max_c A_c / n_R) - (1-δ).
- Negative: zero-loss (cheater can't beat (1-δ)).
- Zero: matches (1-δ) exactly.
- Positive: cheater beats (1-δ); rare event (would falsify Phase 3 conjecture).
"""

from __future__ import annotations
import sys
import time
import random
import math

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, dist_to_code_full,
)
from phase2_charsum_sweep import sample_far_input, true_fold_R


def sweep(p, n0, k0, R, num_inputs, num_alphas, w_target=None, rng=None, mode='random'):
    if rng is None:
        rng = random.Random(0)
    if w_target is None:
        rho = k0 / n0
        delta_J = 1 - math.sqrt(rho)
        w_target = max(int(delta_J * n0) + 1, 1)
    delta = w_target / n0

    chain = setup_chain(p, n0, k0, R=R)
    L_R, k_R, H_R = chain[R]
    n_R = len(L_R)

    print(f"# Phase 3: max_c A_c(α) sweep", flush=True)
    print(f"# p={p}, n_0={n0}, k_0={k0}, R={R}, n_R={n_R}, k_R={k_R}", flush=True)
    print(f"# w_target={w_target} (δ={delta:.4f}), (1-δ)·n_R = {(1-delta)*n_R:.2f}", flush=True)
    print(f"# {num_inputs} inputs × {num_alphas} α-tuples", flush=True)
    print("", flush=True)

    # Track: max_A - (1-δ)·n_R (positive = cheater wins)
    margins = []  # margin = δ·n_R - dist_R; positive = cheater wins (dist < δ·n_R)
    dists = []
    t0 = time.time()
    bad_records = []  # α-tuples that beat (1-δ)

    for inp_idx in range(num_inputs):
        if mode == 'random':
            f = sample_far_input(p, n0, k0, w_target, rng, chain)
        elif mode == 'monomial':
            j = k0 + (inp_idx % (n0 - k0))
            f = [pow(x, j, p) for x in chain[0][0]]
        elif mode == 'cs_lift':
            r_cs = k0 + 2
            f = [(pow(x, r_cs, p) + pow(x, r_cs - 1, p)) % p for x in chain[0][0]]
        else:
            raise ValueError(mode)

        for alpha_idx in range(num_alphas):
            alphas = [rng.randrange(p) for _ in range(R)]
            g = true_fold_R(f, chain, alphas, p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p)
            if d is None:
                d = n_R  # very far (max possible)
            dists.append(d)
            margin = delta * n_R - d  # positive ⇒ cheater wins (dist below δ·n_R)
            margins.append(margin)
            if margin > 0:
                bad_records.append((inp_idx, tuple(alphas), d, margin))

        if (inp_idx + 1) % max(1, num_inputs // 5) == 0:
            elapsed = time.time() - t0
            print(f"# input {inp_idx+1}/{num_inputs}, elapsed {elapsed:.1f}s", flush=True)

    print("", flush=True)
    print(f"Total trials: {len(dists)}", flush=True)
    print(f"  min dist: {min(dists)}", flush=True)
    print(f"  max dist: {max(dists)}", flush=True)
    print(f"  mean dist: {sum(dists)/len(dists):.3f}", flush=True)
    print(f"  δ·n_R    : {delta*n_R:.3f}", flush=True)
    print(f"  Empirical Pr[cheater beats (1-δ)] = {len(bad_records)}/{len(dists)} = {len(bad_records)/len(dists):.6f}", flush=True)
    print(f"  Theoretical bound 1/q = {1/p:.6f}", flush=True)
    print(f"  R/q                   = {R/p:.6f}", flush=True)

    # Histogram of dists
    print("", flush=True)
    print(f"Dist histogram (relative to δ·n_R = {delta*n_R:.2f}):", flush=True)
    hist = {}
    for d in dists:
        hist[d] = hist.get(d, 0) + 1
    for d in sorted(hist.keys()):
        marker = " <- δ·n_R" if abs(d - delta*n_R) < 0.5 else ""
        marker += " <- BAD" if d < delta*n_R else ""
        frac = hist[d] / len(dists)
        print(f"  dist = {d:3d}: {hist[d]:6d} ({frac*100:6.2f}%){marker}", flush=True)

    if bad_records:
        print("", flush=True)
        print(f"BAD α-tuples (cheater beat (1-δ)): {len(bad_records)}", flush=True)
        for rec in bad_records[:20]:
            print(f"  inp={rec[0]}, α={rec[1]}, d={rec[2]}, margin={rec[3]:.3f}", flush=True)


if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Usage: python3 phase3_max_agreement.py <p> <n0> <k0> <R> <num_inputs> <num_alphas> [mode]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1])
    n0 = int(sys.argv[2])
    k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    num_inputs = int(sys.argv[5])
    num_alphas = int(sys.argv[6])
    mode = sys.argv[7] if len(sys.argv) > 7 else 'random'
    sweep(p, n0, k0, R, num_inputs, num_alphas, mode=mode)
