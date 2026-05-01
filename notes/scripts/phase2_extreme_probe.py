"""phase2_extreme_probe.py — Extreme adversarial D-constant probe.

Goal: try to falsify the empirical claim D ≤ 2.6.

We build f's whose syndrome / Q_b structure is deliberately crafted to
maximize |S_c(t, α)| / √n_R for SOME α and SOME (t, c).

Strategies tested:
  S1. Sparse syndrome at lowest positions (concentrate energy into few Q_b)
  S2. Sparse syndrome at α-aligned positions (entries in single |b|_2 stripe)
  S3. Lacunary monomial sums  Σ_j δ_j x^{i_j}
  S4. Single-stripe-of-1 input  fhat_i = 1 for i ∈ stripe, 0 else
  S5. Random-coefficient sparse syndromes of varying sparsity
  S6. Stripe + carrier wave (f = baseline + amplitude sin)
  S7. Hand-crafted "Welch" type: fhat = αχ for χ a character

For each f, sweep α uniformly, compute max_{t,c} |S(t,α)|/√n_R.

Output: per-f extreme record, top-10 D values overall, any case D > 4.
"""
from __future__ import annotations
import sys
import time
import random
import math
import cmath
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import setup_chain, even_odd_parts, modinv, find_prim_root


def true_fold_R(f, chain, alphas, p):
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def random_codeword(L, k, p, rng):
    coeffs = [rng.randrange(p) for _ in range(k)]
    n = len(L)
    c = [0] * n
    for i in range(n):
        x = L[i]; v = 0; xj = 1
        for j in range(k):
            v = (v + coeffs[j] * xj) % p
            xj = (xj * x) % p
        c[i] = v
    return c, coeffs


def char_sum(f, t, p):
    s = 0+0j
    for v in f:
        s += cmath.exp(2j * math.pi * (t * v % p) / p)
    return s


def evaluate_from_dft_l0(fhat, L0, p):
    """Evaluate inverse DFT on L_0 from given fhat ∈ F_p^n."""
    n = len(fhat)
    f = [0] * n
    for j in range(n):
        x = L0[j]
        v = 0
        xi = 1
        for i in range(n):
            v = (v + fhat[i] * xi) % p
            xi = (xi * x) % p
        # Note: standard inverse DFT divides by n, but for Weil-style structure
        # we drop normalization (just affects overall scale, not |S|/√n_R ratio)
        f[j] = v
    return f


# ----------------------- Strategies for crafting fhat -----------------------

def craft_S1_low_concentrated(p, n0, k0, sparsity):
    """All energy in lowest syndrome positions."""
    fhat = [0] * n0
    positions = list(range(k0, k0 + sparsity))
    for pos in positions:
        fhat[pos] = 1
    return fhat, f"S1_low_concentrated_s{sparsity}"


def craft_S2_alpha_aligned(p, n0, k0, R, sparsity, target_b):
    """Place fhat at positions {i : i ∈ syndrome ∧ i mod 2^R == target_b}.
    These all map into Q_{target_b in {0,1}^R representation} on L_R.
    Effect: Q_b for one specific b is FULL, others are zero — extreme rank-1.
    """
    fhat = [0] * n0
    block = 1 << R
    placed = 0
    for i in range(k0, n0):
        if i % block == target_b and placed < sparsity:
            fhat[i] = 1
            placed += 1
    return fhat, f"S2_alpha_aligned_b{target_b}_s{sparsity}"


def craft_S3_lacunary_monomials(p, n0, k0, sparsity, rng):
    """fhat = sum of δ at random subset of syndrome positions."""
    fhat = [0] * n0
    positions = rng.sample(range(k0, n0), min(sparsity, n0 - k0))
    for pos in positions:
        fhat[pos] = 1
    return fhat, f"S3_lacunary_s{sparsity}"


def craft_S4_full_stripe(p, n0, k0, R, target_b):
    """All n_R positions in a single |b|_2 = target_b stripe set to 1."""
    fhat = [0] * n0
    block = 1 << R
    for i in range(target_b, n0, block):
        if i >= k0:
            fhat[i] = 1
    return fhat, f"S4_full_stripe_b{target_b}"


def craft_S5_random_sparse(p, n0, k0, sparsity, rng):
    """Random-coefficient sparse: fhat[pos] = random ∈ [1, p-1]."""
    fhat = [0] * n0
    positions = rng.sample(range(k0, n0), min(sparsity, n0 - k0))
    for pos in positions:
        fhat[pos] = rng.randrange(1, p)
    return fhat, f"S5_random_sparse_s{sparsity}"


def craft_S6_stripe_carrier(p, n0, k0, R, target_b, rng):
    """fhat = stripe + random low-amplitude carrier on other positions."""
    fhat = [0] * n0
    block = 1 << R
    for i in range(target_b, n0, block):
        if i >= k0:
            fhat[i] = 1
    # Add random small amplitude carrier on all syndrome positions
    for i in range(k0, n0):
        if fhat[i] == 0:
            fhat[i] = rng.randrange(1, max(2, p // 10))
    return fhat, f"S6_stripe_carrier_b{target_b}"


def craft_S7_welch(p, n0, k0, R, rng):
    """Welch-style: fhat[i] = ω^{i*c} for primitive ω, character of order n0."""
    omega = find_prim_root(p, n0)
    if omega is None:
        return None, "S7_skip"
    c = rng.randrange(1, n0)
    fhat = [0] * n0
    for i in range(k0, n0):
        fhat[i] = pow(omega, i * c, p)
    return fhat, f"S7_welch_c{c}"


def craft_S8_dual_alpha_aligned(p, n0, k0, R, target_b1, target_b2):
    """Two stripes: |b|_2 = b1 and b2. Forces interaction between two Q_b's."""
    fhat = [0] * n0
    block = 1 << R
    for i in range(target_b1, n0, block):
        if i >= k0:
            fhat[i] = 1
    for i in range(target_b2, n0, block):
        if i >= k0:
            fhat[i] = 1
    return fhat, f"S8_dual_aligned_b{target_b1}_b{target_b2}"


def craft_S9_geometric_progression(p, n0, k0, ratio, length):
    """fhat[k0+j] = ratio^j for j=0..length-1, else 0.
    Highly correlated coefficients across α-monomials.
    """
    fhat = [0] * n0
    for j in range(length):
        if k0 + j >= n0:
            break
        fhat[k0 + j] = pow(ratio, j, p)
    return fhat, f"S9_geom_r{ratio}_l{length}"


# ----------------------- Probe -----------------------

def probe_one_input(fhat, label, p, n0, k0, R, num_alphas, num_codewords, rng, chain):
    """For one f, sweep α and codewords; return max |S|/√n_R, mean |S|/√n_R."""
    L0 = chain[0][0]
    f = evaluate_from_dft_l0(fhat, L0, p)

    L_R = chain[R][0]
    k_R = chain[R][1]
    n_R = len(L_R)
    sqrtnR = math.sqrt(n_R)

    max_D = 0.0
    max_record = None
    sum_D = 0.0
    n_samples = 0
    n_violation = 0  # |S|/√n_R > 4

    for alpha_idx in range(num_alphas):
        alphas = [rng.randrange(p) for _ in range(R)]
        g = true_fold_R(f, chain, alphas, p)

        for cw_idx in range(num_codewords):
            c, _ = random_codeword(L_R, k_R, p, rng)
            h = [(g[j] - c[j]) % p for j in range(n_R)]

            # Test all t ∈ F_p* (or sample for large p)
            ts = list(range(1, p)) if p <= 200 else [rng.randrange(1, p) for _ in range(50)]
            for t in ts:
                S = char_sum(h, t, p)
                modS = abs(S)
                D = modS / sqrtnR
                sum_D += D
                n_samples += 1
                if D > 4:
                    n_violation += 1
                if D > max_D:
                    max_D = D
                    max_record = (label, alphas, t, modS, n_R)

    mean_D = sum_D / n_samples if n_samples else 0
    return {'label': label, 'max_D': max_D, 'mean_D': mean_D,
            'max_record': max_record, 'n_samples': n_samples,
            'n_violation': n_violation, 'n_R': n_R, 'sqrtnR': sqrtnR}


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 phase2_extreme_probe.py <p> <n0> <k0> <R> [num_alphas] [num_codewords]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1])
    n0 = int(sys.argv[2])
    k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    num_alphas = int(sys.argv[5]) if len(sys.argv) > 5 else 50
    num_codewords = int(sys.argv[6]) if len(sys.argv) > 6 else 5

    rng = random.Random(42)
    chain = setup_chain(p, n0, k0, R=R)
    n_R = len(chain[R][0])

    print(f"# Extreme probe: p={p}, n_0={n0}, k_0={k0}, R={R}, n_R={n_R}", flush=True)
    print(f"# {num_alphas} α × {num_codewords} c × full t (or 50 random)", flush=True)
    print(f"# √n_R = {math.sqrt(n_R):.3f}", flush=True)
    print("", flush=True)

    block = 1 << R
    n_blocks = n0 // block

    # Build the strategy list
    inputs = []
    # S1: low-concentrated
    for s in [1, 2, 3, 4, 8]:
        if s <= n0 - k0:
            inputs.append(craft_S1_low_concentrated(p, n0, k0, s))
    # S2: α-aligned single stripe
    for b in range(min(block, 8)):
        inputs.append(craft_S2_alpha_aligned(p, n0, k0, R, n_R, b))
    # S3: lacunary
    for s in [2, 3, 5]:
        for trial in range(3):
            inputs.append(craft_S3_lacunary_monomials(p, n0, k0, s, rng))
    # S4: full stripe (=S2 with full sparsity)
    for b in range(min(block, 4)):
        inputs.append(craft_S4_full_stripe(p, n0, k0, R, b))
    # S5: random sparse
    for s in [3, 5, 8]:
        for trial in range(2):
            inputs.append(craft_S5_random_sparse(p, n0, k0, s, rng))
    # S6: stripe + carrier
    for b in range(min(block, 2)):
        inputs.append(craft_S6_stripe_carrier(p, n0, k0, R, b, rng))
    # S7: Welch
    for trial in range(3):
        result = craft_S7_welch(p, n0, k0, R, rng)
        if result[0] is not None:
            inputs.append(result)
    # S8: dual aligned
    if block >= 2:
        for trial in range(min(4, block * (block - 1) // 2)):
            b1 = rng.randrange(block)
            b2 = rng.randrange(block)
            if b1 != b2:
                inputs.append(craft_S8_dual_alpha_aligned(p, n0, k0, R, b1, b2))
    # S9: geometric progression
    for r_val in [2, 3, 5]:
        inputs.append(craft_S9_geometric_progression(p, n0, k0, r_val, min(8, n0 - k0)))

    print(f"# Total adversarial inputs: {len(inputs)}", flush=True)
    print("", flush=True)

    t0 = time.time()
    all_results = []
    for idx, (fhat, label) in enumerate(inputs):
        if fhat is None:
            continue
        r = probe_one_input(fhat, label, p, n0, k0, R, num_alphas, num_codewords, rng, chain)
        all_results.append(r)
        elapsed = time.time() - t0
        flag = " ⚠ VIOLATION" if r['max_D'] > 4 else ""
        print(f"  [{idx+1:3d}/{len(inputs)}] {label:35s}  max_D={r['max_D']:.3f}  "
              f"mean_D={r['mean_D']:.3f}  viol={r['n_violation']:5d}/{r['n_samples']:5d}  "
              f"({elapsed:.1f}s){flag}", flush=True)

    # Sort by max_D
    all_results.sort(key=lambda r: r['max_D'], reverse=True)

    print("", flush=True)
    print("=" * 80, flush=True)
    print("TOP 10 max_D records:", flush=True)
    print("=" * 80, flush=True)
    for i, r in enumerate(all_results[:10]):
        print(f"  #{i+1}  {r['label']:40s}  max_D={r['max_D']:.4f}", flush=True)
        if r['max_record']:
            label, alphas, t, modS, nR = r['max_record']
            print(f"        @ alphas={alphas}, t={t}, |S|={modS:.3f}, n_R={nR}", flush=True)

    print("", flush=True)
    n_overall_violation = sum(r['n_violation'] for r in all_results)
    n_overall_samples = sum(r['n_samples'] for r in all_results)
    n_above_2_6 = sum(1 for r in all_results if r['max_D'] > 2.6)
    n_above_4 = sum(1 for r in all_results if r['max_D'] > 4)

    print(f"OVERALL: {n_overall_samples} samples, {n_overall_violation} violations (D > 4)", flush=True)
    print(f"  Inputs with max_D > 2.6: {n_above_2_6}/{len(all_results)}", flush=True)
    print(f"  Inputs with max_D > 4.0: {n_above_4}/{len(all_results)}", flush=True)
    print(f"  Universal max_D: {all_results[0]['max_D']:.4f}", flush=True)
    print(f"  Total time: {time.time() - t0:.1f}s", flush=True)


if __name__ == '__main__':
    main()
