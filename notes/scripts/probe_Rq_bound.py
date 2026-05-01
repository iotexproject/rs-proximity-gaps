"""probe_Rq_bound.py — search for above-Johnson f where |V_δ|/q^R > R/q.

If this happens, the prize-relevant bound ε_FRI ≤ R/q + (1-δ)^q is FALSE for FRI.
If it never happens across exhaustive adversarial sweep, strengthens the claim.

For each adversarial input family + several δ in open zone, brute-force enumerate
V_δ via dist_to_code_full.

Usage: python3 probe_Rq_bound.py <p> <n_0> <k_0> <R> [delta_frac]
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


def evaluate_dft(fhat, L, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L[j], i, p) for i in range(n)) % p for j in range(n)]


def craft_adversarial_inputs(p, n0, k0, R, rng):
    """Build many above-Johnson adversarial f's for the search."""
    L0 = [1]  # placeholder, get actual later
    inputs = []

    # CS lift family
    for r_cs in range(k0 + 2, min(n0 + 1, k0 + 5)):
        # Will eval on actual L0 below
        inputs.append(('cs_lift_r' + str(r_cs), 'cs_lift', r_cs))

    # Sparse syndrome at strategic positions
    for s in [3, 5, 7, 10]:
        if s <= n0 - k0:
            for trial in range(3):
                positions = rng.sample(range(k0, n0), s)
                vals = [rng.randrange(1, p) for _ in range(s)]
                inputs.append((f'sparse_s{s}_t{trial}', 'sparse', (positions, vals)))

    # Stripe with α-aligned support (DEEP attack on Q_b structure)
    block = 1 << R
    for b in range(min(block, 4)):
        positions = list(range(k0, n0))
        positions = [p for p in positions if p % block == b]
        if positions:
            vals = [1] * len(positions)
            inputs.append((f'stripe_b{b}', 'sparse', (positions, vals)))

    # Dual stripe
    for b1 in range(min(block, 2)):
        for b2 in range(b1 + 1, min(block, 3)):
            pos1 = [p for p in range(k0, n0) if p % block == b1]
            pos2 = [p for p in range(k0, n0) if p % block == b2]
            positions = pos1 + pos2
            vals = [1] * len(positions)
            inputs.append((f'dual_b{b1}_b{b2}', 'sparse', (positions, vals)))

    # Random above-Johnson
    rho0 = k0 / n0
    delta_J0 = 1 - math.sqrt(rho0)
    w_target = max(int(delta_J0 * n0) + 1, 1)
    for trial in range(5):
        positions = rng.sample(range(k0, n0), min(w_target + trial, n0 - k0))
        vals = [rng.randrange(1, p) for _ in range(len(positions))]
        inputs.append((f'random_aj_t{trial}', 'sparse', (positions, vals)))

    return inputs


def materialize(inp, p, n0, k0, L0):
    label, mode, payload = inp
    if mode == 'cs_lift':
        r_cs = payload
        return [(pow(x, r_cs, p) + pow(x, r_cs - 1, p)) % p for x in L0], label
    elif mode == 'sparse':
        positions, vals = payload
        fhat = [0] * n0
        for pos, val in zip(positions, vals):
            fhat[pos] = val
        return evaluate_dft(fhat, L0, p), label


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 probe_Rq_bound.py <p> <n0> <k0> <R> [delta_frac]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1])
    n0 = int(sys.argv[2])
    k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    delta_frac = float(sys.argv[5]) if len(sys.argv) > 5 else None

    chain = setup_chain(p, n0, k0, R=R)
    L_R = chain[R][0]
    k_R = chain[R][1]
    n_R = len(L_R)
    L0 = chain[0][0]
    H0 = parity_check(L0, n0, k0, p)
    H_R = parity_check(L_R, n_R, k_R, p)

    rho = k_R / n_R
    delta_J = 1 - math.sqrt(rho)
    rho0 = k0 / n0
    delta_J0 = 1 - math.sqrt(rho0)
    w_target0 = max(int(delta_J0 * n0) + 1, 1)

    if delta_frac is None:
        delta = min(delta_J + 0.1, (1 - rho) * 0.95)
    else:
        delta = delta_frac

    w_R = int(delta * n_R)
    s = n_R - w_R

    Rq_bound = R / p

    print(f"# R/q probe: p={p}, n_0={n0}, k_0={k0}, R={R}", flush=True)
    print(f"# n_R={n_R}, k_R={k_R}, ρ={rho:.4f}, δ={delta:.4f}, w_R={w_R}", flush=True)
    print(f"# Above-Johnson threshold: dist > {w_target0} (δ_J0={delta_J0:.3f})", flush=True)
    print(f"# Prize bound R/q = {R}/{p} = {Rq_bound:.6e}", flush=True)
    print(f"# Total α to enumerate: q^R = {p**R}", flush=True)
    print("", flush=True)

    rng = random.Random(123)
    inputs = craft_adversarial_inputs(p, n0, k0, R, rng)

    violations = []
    above_J_inputs_tested = 0

    for inp in inputs:
        f, label = materialize(inp, p, n0, k0, L0)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p)
        if d0 is None or d0 <= w_target0:
            print(f"  SKIP {label:25s}  dist(f,C_0) = {d0} ≤ Johnson {w_target0}", flush=True)
            continue
        above_J_inputs_tested += 1

        bad_count = 0
        t0 = time.time()
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
            if d is not None and d <= w_R:
                bad_count += 1
        elapsed = time.time() - t0

        ratio = bad_count / (p ** R)
        ratio_to_Rq = ratio / Rq_bound
        flag = " ⚠ VIOLATION" if ratio > Rq_bound else ""
        print(f"  {label:25s}  dist(f,C_0)={d0:3d}  |V_δ|/q^R={ratio:.4e}  "
              f"vs R/q={Rq_bound:.4e} (ratio {ratio_to_Rq:.2f})  ({elapsed:.1f}s){flag}",
              flush=True)
        if ratio > Rq_bound:
            violations.append((label, d0, ratio))

    print("", flush=True)
    print(f"# Above-Johnson inputs tested: {above_J_inputs_tested}", flush=True)
    print(f"# R/q violations: {len(violations)}", flush=True)
    for v in violations:
        print(f"  ⚠ {v}", flush=True)
    if not violations:
        print(f"# *** NO violation of R/q bound found across {above_J_inputs_tested} adversarial f's. ***", flush=True)


if __name__ == '__main__':
    main()
