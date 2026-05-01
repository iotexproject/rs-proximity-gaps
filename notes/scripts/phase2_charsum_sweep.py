"""phase2_charsum_sweep.py — Issue #343 Phase 2: empirical character-sum scaling.

Goal: verify that for "above-Johnson" f and typical α, the agreement count
  A_c(α) := #{y ∈ L_R : c(y) = true_fold_R(α; y)}
satisfies |A_c(α) - n_R/q| = O(√n_R) for typical codeword c ∈ C_R.

This is the "Phase 2" Weil-type bound; combined with Phase 1 SZ count,
it would give ε_FRI ≤ R/q + (1-δ)^q.

Method:
  1. Build chain L_0 → ... → L_R as in fri_2round_attack.py
  2. Pick adversarial f (random "syndrome-supported" or CS-construction)
  3. For many α-tuples and many random codewords c ∈ C_R:
     - Compute true_fold_R(α; ·) on L_R
     - For each c, compute A_c(α) and the character sum |S_c(t, α)| for t ∈ F_p*
     - Record deviation A_c(α) - n_R/q vs √n_R
  4. Output histograms + extreme cases.

Outputs raw stats to stdout.  Aggregation script: phase2_charsum_summary.py.
"""

from __future__ import annotations
import sys
import time
import random
import math
import cmath
from itertools import combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, modinv, find_prim_root,
    dist_to_code_full, parity_check
)


# ----------------------- DFT / IDFT on L_R -----------------------

def dft(f, L, p):
    """Compute DFT: f̂_i = Σ_j f(L[j]) · L[j]^{-i}.
    L = [ω^0, ω^1, ..., ω^{n-1}] for primitive n-th root ω.
    """
    n = len(L)
    fhat = [0] * n
    for i in range(n):
        s = 0
        for j in range(n):
            s = (s + f[j] * pow(L[j], (-i) % n, p)) % p
        fhat[i] = s
    return fhat


def random_codeword(L, k, p, rng):
    """Random c ∈ RS_k(L): pick random a_0, ..., a_{k-1} ∈ F_p and evaluate."""
    coeffs = [rng.randrange(p) for _ in range(k)]
    n = len(L)
    c = [0] * n
    for i in range(n):
        x = L[i]
        v = 0
        xj = 1
        for j in range(k):
            v = (v + coeffs[j] * xj) % p
            xj = (xj * x) % p
        c[i] = v
    return c, coeffs


def true_fold_R(f, chain, alphas, p):
    """Compute true_fold_R(α_1, ..., α_R)(f) on L_R."""
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


# ----------------------- Character sum -----------------------

def char_sum(f, t, p):
    """S(t) = Σ_y ψ(t · f(y)) where ψ(x) = exp(2πi x / p) and y ranges
    over indices of f. Returns complex number.
    """
    s = 0+0j
    for v in f:
        s += cmath.exp(2j * math.pi * (t * v % p) / p)
    return s


def agreement_count(f, c, p):
    """#{i : f[i] == c[i] mod p}."""
    return sum(1 for a, b in zip(f, c) if (a - b) % p == 0)


# ----------------------- Sample adversarial f -----------------------

def sample_far_input(p, n0, k0, w, rng, chain):
    """f = c_0 + e where c_0 ∈ RS_{k_0}(L_0) random codeword, e weight w random.
    Then dist(f, C_0) ≤ w; usually exactly w if w ≤ d_min/2.
    """
    L0 = chain[0][0]
    c0, _ = random_codeword(L0, k0, p, rng)
    e_pos = rng.sample(range(n0), w)
    e_val = [rng.randrange(1, p) for _ in range(w)]
    f = list(c0)
    for pos, val in zip(e_pos, e_val):
        f[pos] = (f[pos] + val) % p
    return f


# ----------------------- Sweep -----------------------

def sweep(p, n0, k0, R, num_alphas, num_codewords, num_inputs,
          w_target=None, rng=None, mode='random'):
    """Massive sweep over (input f, α-tuple, codeword c).

    Outputs per-trial stats.
    """
    if rng is None:
        rng = random.Random(0)
    if w_target is None:
        # Choose w just above unique decoding (Johnson-ish)
        rho = k0 / n0
        delta_J = 1 - math.sqrt(rho)
        w_target = max(int(delta_J * n0) + 1, 1)

    chain = setup_chain(p, n0, k0, R=R)
    L_R = chain[R][0]
    k_R = chain[R][1]
    n_R = len(L_R)
    delta = w_target / n0

    print(f"# Phase 2 sweep: p={p}, n_0={n0}, k_0={k0}, R={R}", flush=True)
    print(f"# w_target={w_target} (δ={delta:.4f}), n_R={n_R}, k_R={k_R}", flush=True)
    print(f"# {num_inputs} inputs × {num_alphas} α-tuples × {num_codewords} codewords", flush=True)
    print(f"# Expected n_R/q = {n_R/p:.4f}, √n_R = {math.sqrt(n_R):.3f}", flush=True)
    print(f"# Mode: {mode}", flush=True)
    print("", flush=True)

    all_devs = []  # All deviations (for histogram)
    all_max_dev = []  # Per-α max deviation across codewords
    extreme_records = []  # Most extreme (α, c, deviation) tuples

    t0 = time.time()
    for inp_idx in range(num_inputs):
        if mode == 'random':
            f = sample_far_input(p, n0, k0, w_target, rng, chain)
        elif mode == 'monomial':
            # f = X^{k_0 + (inp_idx mod (n0-k0))}
            j = k0 + (inp_idx % (n0 - k0))
            f = [pow(x, j, p) for x in chain[0][0]]
        elif mode == 'cs_lift':
            # CS construction: f = X^{rm} + X^{(r-1)m} on L_0
            # k_0 = (r-2)m, n_0 = sm, δ = 1 - r/s
            # Choose m=1, r = k_0 + 2, s = n_0
            r_cs = k0 + 2
            s_cs = n0
            f = [(pow(x, r_cs, p) + pow(x, r_cs - 1, p)) % p for x in chain[0][0]]
        else:
            raise ValueError(mode)

        # Sample α-tuples
        for alpha_idx in range(num_alphas):
            alphas = [rng.randrange(p) for _ in range(R)]
            g = true_fold_R(f, chain, alphas, p)

            max_dev_for_alpha = 0
            for cw_idx in range(num_codewords):
                c, _ = random_codeword(L_R, k_R, p, rng)
                A = agreement_count(g, c, p)
                dev = A - n_R / p
                all_devs.append(dev)
                if abs(dev) > abs(max_dev_for_alpha):
                    max_dev_for_alpha = dev
                # Track extreme cases
                if abs(dev) > 0.5 * n_R:  # huge spike
                    extreme_records.append((inp_idx, tuple(alphas), A, dev))

            all_max_dev.append(max_dev_for_alpha)

        if (inp_idx + 1) % max(1, num_inputs // 10) == 0:
            elapsed = time.time() - t0
            print(f"# input {inp_idx+1}/{num_inputs}, elapsed {elapsed:.1f}s", flush=True)

    # Stats
    print("", flush=True)
    print(f"Total deviations recorded: {len(all_devs)}", flush=True)
    if all_devs:
        mean_dev = sum(all_devs) / len(all_devs)
        var_dev = sum((d - mean_dev)**2 for d in all_devs) / len(all_devs)
        rms = math.sqrt(var_dev)
        max_abs = max(abs(d) for d in all_devs)
        print(f"  mean(dev) = {mean_dev:.4f}", flush=True)
        print(f"  RMS(dev)  = {rms:.4f}", flush=True)
        print(f"  max|dev|  = {max_abs:.4f}", flush=True)
        print(f"  √n_R = {math.sqrt(n_R):.4f}", flush=True)
        print(f"  RMS / √n_R = {rms / math.sqrt(n_R):.4f}", flush=True)
        print(f"  max|dev| / √n_R = {max_abs / math.sqrt(n_R):.4f}", flush=True)

    if all_max_dev:
        mean_max = sum(abs(d) for d in all_max_dev) / len(all_max_dev)
        max_max = max(abs(d) for d in all_max_dev)
        print(f"  E_α[max_c |dev|] = {mean_max:.4f}", flush=True)
        print(f"  max_α max_c |dev| = {max_max:.4f}", flush=True)

    # Histogram of |dev| / √n_R
    bins = [0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, float('inf')]
    hist = [0] * (len(bins) - 1)
    sqn = math.sqrt(n_R)
    for d in all_devs:
        x = abs(d) / sqn
        for i in range(len(bins) - 1):
            if bins[i] <= x < bins[i+1]:
                hist[i] += 1
                break
    print("", flush=True)
    print("Histogram of |dev| / √n_R:", flush=True)
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i+1]
        frac = hist[i] / len(all_devs) if all_devs else 0
        print(f"  [{lo:5.2f}, {hi:5.2f}): {hist[i]:6d} ({frac*100:5.2f}%)", flush=True)

    if extreme_records:
        print("", flush=True)
        print(f"Extreme records (|dev| > 0.5·n_R): {len(extreme_records)}", flush=True)
        for rec in extreme_records[:10]:
            print(f"  {rec}", flush=True)


# ----------------------- Direct character sum mode -----------------------

def char_sum_sweep(p, n0, k0, R, num_alphas, num_inputs, mode='random', rng=None):
    """Compute |S(t, α)| = |Σ_{y ∈ L_R} ψ(t·g_α(y) - t·c(y))| for many (α, c, t).

    This is the actual character sum. Smaller than the agreement count method
    since we don't count agreement; we measure the underlying Weil sum directly.
    """
    if rng is None:
        rng = random.Random(0)
    rho = k0 / n0
    delta_J = 1 - math.sqrt(rho)
    w_target = max(int(delta_J * n0) + 1, 1)

    chain = setup_chain(p, n0, k0, R=R)
    L_R = chain[R][0]
    k_R = chain[R][1]
    n_R = len(L_R)

    print(f"# Direct char sum sweep: p={p}, n_0={n0}, k_0={k0}, R={R}", flush=True)
    print(f"# w_target={w_target}, n_R={n_R}, k_R={k_R}", flush=True)
    print(f"# {num_inputs} inputs × {num_alphas} α-tuples × full t∈F_p*", flush=True)
    print(f"# √n_R = {math.sqrt(n_R):.3f}, n_R = {n_R}", flush=True)
    print("", flush=True)

    all_S = []  # All |S(t, α, c)| values
    weil_violations = []  # Records where |S| > 4·√n_R (suspicious)

    for inp_idx in range(num_inputs):
        if mode == 'random':
            f = sample_far_input(p, n0, k0, w_target, rng, chain)
        elif mode == 'monomial':
            j = k0 + inp_idx
            f = [pow(x, j, p) for x in chain[0][0]]
        else:
            raise ValueError(mode)

        for alpha_idx in range(num_alphas):
            alphas = [rng.randrange(p) for _ in range(R)]
            g = true_fold_R(f, chain, alphas, p)

            # Random codeword c
            c, _ = random_codeword(L_R, k_R, p, rng)
            h = [(g[j] - c[j]) % p for j in range(n_R)]

            # |S(t)| for t ∈ F_p*
            for t in range(1, p):
                S = char_sum(h, t, p)
                modS = abs(S)
                all_S.append(modS)
                if modS > 4 * math.sqrt(n_R):
                    weil_violations.append((inp_idx, tuple(alphas), t, modS))

    print(f"Total |S| values: {len(all_S)}", flush=True)
    if all_S:
        mean_S = sum(all_S) / len(all_S)
        rms_S = math.sqrt(sum(s**2 for s in all_S) / len(all_S))
        max_S = max(all_S)
        print(f"  mean |S|        = {mean_S:.4f}", flush=True)
        print(f"  RMS  |S|        = {rms_S:.4f}", flush=True)
        print(f"  max  |S|        = {max_S:.4f}", flush=True)
        print(f"  √n_R            = {math.sqrt(n_R):.4f}", flush=True)
        print(f"  RMS|S|/√n_R     = {rms_S/math.sqrt(n_R):.4f}", flush=True)
        print(f"  max|S|/√n_R     = {max_S/math.sqrt(n_R):.4f}", flush=True)

    print("", flush=True)
    print(f"Weil-violation candidates (|S| > 4√n_R): {len(weil_violations)}", flush=True)
    for rec in weil_violations[:10]:
        print(f"  {rec}", flush=True)


# ----------------------- Main -----------------------

if __name__ == '__main__':
    if len(sys.argv) < 7:
        print("Usage: python3 phase2_charsum_sweep.py <p> <n0> <k0> <R> <num_inputs> <num_alphas> [num_codewords] [mode] [submode]", file=sys.stderr)
        print("  submode: 'agree' (default) or 'charsum'", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1])
    n0 = int(sys.argv[2])
    k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    num_inputs = int(sys.argv[5])
    num_alphas = int(sys.argv[6])
    num_codewords = int(sys.argv[7]) if len(sys.argv) > 7 else 20
    mode = sys.argv[8] if len(sys.argv) > 8 else 'random'
    submode = sys.argv[9] if len(sys.argv) > 9 else 'agree'

    if submode == 'charsum':
        char_sum_sweep(p, n0, k0, R, num_alphas, num_inputs, mode=mode)
    else:
        sweep(p, n0, k0, R, num_alphas, num_codewords, num_inputs, mode=mode)
