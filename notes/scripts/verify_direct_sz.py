"""verify_direct_sz.py — Empirical check of note 0096's direct-SZ bound on |V_δ|.

Claim:
  |V_δ| ≤ C(n_R, δn_R) · R^{min(R, s-k_R)} · q^{max(0, R-(s-k_R))}
  where s = (1-δ)n_R, V_δ = {α : dist(true_fold_R(α), C_R) ≤ δn_R}.

We brute-force enumerate α ∈ F_p^R, count |V_δ|, compare to the bound.

Usage:  python3 verify_direct_sz.py <p> <n_0> <k_0> <R> [num_inputs] [delta_frac]
"""
from __future__ import annotations
import sys, time, random, math
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import setup_chain, even_odd_parts, dist_to_code_full, parity_check


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
    return c


def sample_far_input(p, n0, k0, w, rng, chain):
    L0 = chain[0][0]
    c0 = random_codeword(L0, k0, p, rng)
    e_pos = rng.sample(range(n0), w)
    e_val = [rng.randrange(1, p) for _ in range(w)]
    f = list(c0)
    for pos, val in zip(e_pos, e_val):
        f[pos] = (f[pos] + val) % p
    return f


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 verify_direct_sz.py <p> <n0> <k0> <R> [num_inputs] [delta_frac]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1])
    n0 = int(sys.argv[2])
    k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    num_inputs = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    delta_frac = float(sys.argv[6]) if len(sys.argv) > 6 else None

    chain = setup_chain(p, n0, k0, R=R)
    L_R = chain[R][0]
    k_R = chain[R][1]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho = k_R / n_R

    # Choose delta in open zone if not given
    if delta_frac is None:
        delta_J = 1 - math.sqrt(rho)
        delta = min(delta_J + 0.1, (1 - rho) * 0.95)  # In open zone
    else:
        delta = delta_frac

    w_R = int(delta * n_R)
    s = n_R - w_R  # agreement set size
    s_minus_k = s - k_R

    print(f"# Direct-SZ verification: p={p}, n_0={n0}, k_0={k0}, R={R}, n_R={n_R}, k_R={k_R}", flush=True)
    print(f"# δ = {delta:.4f} (= {w_R}/{n_R}), s = (1-δ)n_R = {s}, s-k_R = {s_minus_k}", flush=True)
    print(f"# ρ = {rho:.4f}, δ_J ≈ {1-math.sqrt(rho):.4f}, capacity 1-ρ = {1-rho:.4f}", flush=True)

    # Direct-SZ bound: C(n_R, w_R) · R^min(R, s_minus_k) · q^max(0, R-s_minus_k) / q^R
    # = C(n_R, w_R) · (R/q)^min(R, s_minus_k)
    log_C = sum(math.log(n_R - i + 1) - math.log(i) for i in range(1, w_R + 1))
    log_bound_ratio = log_C + min(R, s_minus_k) * math.log(R / p) if s_minus_k > 0 else 0
    bound_ratio = math.exp(log_bound_ratio) if s_minus_k > 0 else float('inf')

    print(f"# Direct-SZ bound: |V_δ|/q^R ≤ C({n_R},{w_R}) · (R/q)^{min(R, s_minus_k)} = {bound_ratio:.6e}", flush=True)
    print(f"# (Phase 1 SZ alone: |V_exact|/q^R ≤ R^R/q^R = {(R/p)**R:.6e})", flush=True)
    print(f"# Brute-forcing |V_δ|/q^R = #(bad α) / {p**R}", flush=True)
    print("", flush=True)

    rng = random.Random(42)

    # Choose w_target for input distance
    rho0 = k0 / n0
    delta_J0 = 1 - math.sqrt(rho0)
    w_target = max(int(delta_J0 * n0) + 1, 1)
    mode = sys.argv[7] if len(sys.argv) > 7 else 'random'

    total_alphas = p ** R
    if total_alphas > 5_000_000:
        print(f"# WARNING: {total_alphas} α's, too many to enumerate; sampling instead", flush=True)
        sample_size = 100_000
        sample_mode = True
    else:
        sample_mode = False
        sample_size = total_alphas

    H0 = parity_check(chain[0][0], n0, k0, p)

    for inp_idx in range(num_inputs):
        if mode == 'cs_lift':
            r_cs = k0 + 2; s_cs = n0
            L0 = chain[0][0]
            f = [(pow(x, r_cs, p) + pow(x, r_cs - 1, p)) % p for x in L0]
            d0, _ = dist_to_code_full(f, H0, n0, k0, p)
            print(f"#   cs_lift input dist(f, C_0) = {d0} (need > {w_target} for above-Johnson)", flush=True)
        elif mode == 'monomial':
            j = k0 + (inp_idx % (n0 - k0))
            L0 = chain[0][0]
            f = [pow(x, j, p) for x in L0]
            d0, _ = dist_to_code_full(f, H0, n0, k0, p)
            print(f"#   monomial X^{j} input dist(f, C_0) = {d0}", flush=True)
        elif mode == 'aligned':
            L0 = chain[0][0]
            n_R_local = len(chain[R][0])
            block = 1 << R
            target_b = inp_idx % block
            fhat = [0] * n0
            for i in range(target_b, n0, block):
                if i >= k0:
                    fhat[i] = 1
            f = [0] * n0
            for j in range(n0):
                x = L0[j]; v = 0; xi = 1
                for i in range(n0):
                    v = (v + fhat[i] * xi) % p
                    xi = (xi * x) % p
                f[j] = v
            d0, _ = dist_to_code_full(f, H0, n0, k0, p)
            print(f"#   aligned input dist(f, C_0) = {d0}", flush=True)
        else:
            f = sample_far_input(p, n0, k0, w_target, rng, chain)
            d0, _ = dist_to_code_full(f, H0, n0, k0, p)
            print(f"#   random above-Johnson input dist(f, C_0) = {d0}", flush=True)
        bad_count = 0
        t0 = time.time()
        if sample_mode:
            # Random sample
            for _ in range(sample_size):
                alphas = [rng.randrange(p) for _ in range(R)]
                g = true_fold_R(f, chain, alphas, p)
                d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
                if d is not None and d <= w_R:
                    bad_count += 1
        else:
            # Full enumeration
            for alphas in product(range(p), repeat=R):
                g = true_fold_R(f, chain, list(alphas), p)
                d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
                if d is not None and d <= w_R:
                    bad_count += 1
        elapsed = time.time() - t0
        emp_ratio = bad_count / sample_size

        # Compare against bound
        ratio_compared = emp_ratio / bound_ratio if bound_ratio > 0 else float('inf')
        flag = " ⚠ EXCEEDS BOUND" if emp_ratio > bound_ratio * 2 else ""
        print(f"  input {inp_idx+1}: |V_δ|/q^R ≈ {emp_ratio:.6e} ({bad_count}/{sample_size})"
              f"  ratio vs SZ bound: {ratio_compared:.3f}  ({elapsed:.1f}s){flag}", flush=True)

    print("", flush=True)
    print(f"# Bound is conservative if ratio < 1; tight at ~1; violated at > 1.", flush=True)


if __name__ == '__main__':
    main()
