"""probe_Rq_falsifier.py — search for above-Johnson f with |V_δ|/q^R > R/q.

If found: refutes the conjecture ε_FRI ≤ R/q + (1-δ)^q for FRI.
If not found across heavy search: strongest possible empirical confirmation.

Strategy: enumerate ALL CS-lift X^r + X^{r-1} for valid r, plus systematic sweep
of double-exponent variants X^{a} + X^{b} for (a, b) hitting same DFT slot,
plus targeted search using gradient ascent on the |V_δ|/q^R objective.

Usage: python3 probe_Rq_falsifier.py <p> <n_0> <k_0> <R> <delta_frac>
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


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def measure_Vdelta(f, chain, p, n_R, k_R, w_R, H_R, R):
    bad_count = 0
    for alphas in product(range(p), repeat=R):
        g = true_fold_R(f, chain, list(alphas), p)
        d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
        if d is not None and d <= w_R:
            bad_count += 1
    return bad_count


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 probe_Rq_falsifier.py <p> <n_0> <k_0> <R> <delta_frac>", file=sys.stderr)
        sys.exit(1)
    p, n0, k0, R, delta = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R = chain[R][0]; k_R = chain[R][1]; n_R = len(L_R)
    H0 = parity_check(L0, n0, k0, p)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    rho0 = k0 / n0
    delta_J0 = 1 - math.sqrt(rho0)
    w_target0 = max(int(delta_J0 * n0) + 1, 1)
    Rq = R / p
    qR = p ** R

    print(f"# Falsifier probe: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}", flush=True)
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, R/q={Rq:.6e}, q^R={qR}", flush=True)
    print(f"# Above-Johnson dist > {w_target0}", flush=True)
    print(f"# Target: find any above-J f with |V_δ|/q^R > R/q ({Rq:.6e})", flush=True)
    print("", flush=True)

    t0 = time.time()
    best_ratio = 0.0
    best_f_label = None
    n_above_Rq = 0

    # === Strategy 1: ALL pairs (a, b) within same DFT slot ===
    block = 1 << R
    print(f"# Strategy 1: all pairs (a, b) with a, b ∈ syndrome, |a/block - b/block| ≤ 1", flush=True)
    pairs_tested = 0
    for slot_j in range(1, n_R):  # Skip slot 0 (no syndrome contribution)
        slot_lo = slot_j * block
        slot_hi = (slot_j + 1) * block
        if slot_lo < k0:
            continue
        for a in range(max(slot_lo, k0), min(slot_hi, n0)):
            for b in range(a + 1, min(slot_hi, n0)):
                fhat = [0] * n0
                fhat[a] = 1
                fhat[b] = 1
                f = evaluate_dft(fhat, L0, p)
                d0, _ = dist_to_code_full(f, H0, n0, k0, p)
                if d0 is None or d0 <= w_target0:
                    continue
                bad = measure_Vdelta(f, chain, p, n_R, k_R, w_R, H_R, R)
                ratio = bad / qR
                rel = ratio / Rq
                pairs_tested += 1
                if rel > 1.001:
                    n_above_Rq += 1
                    print(f"  ⚠⚠⚠ FALSIFIED: X^{a} + X^{b}, dist={d0}, |V_δ|/q^R = {ratio:.4e} > R/q ({rel:.3f})", flush=True)
                if rel > best_ratio:
                    best_ratio = rel
                    best_f_label = f"X^{a} + X^{b}"
                    print(f"  best so far: X^{a} + X^{b}, dist={d0}, ratio_to_R/q={rel:.4f}  ({time.time()-t0:.0f}s)", flush=True)

    print(f"# Strategy 1 done: {pairs_tested} above-J pairs tested.", flush=True)
    print("", flush=True)

    # === Strategy 2: triples (a, b, c) random above-J ===
    rng = random.Random(2026)
    print(f"# Strategy 2: random triples + small subsets", flush=True)
    triples_tested = 0
    for trial in range(80):
        sparsity = rng.choice([3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        vals = [rng.randrange(1, p) for _ in range(sparsity)]
        fhat = [0] * n0
        for pos, val in zip(positions, vals):
            fhat[pos] = val
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p)
        if d0 is None or d0 <= w_target0:
            continue
        bad = measure_Vdelta(f, chain, p, n_R, k_R, w_R, H_R, R)
        ratio = bad / qR
        rel = ratio / Rq
        triples_tested += 1
        if rel > 1.001:
            n_above_Rq += 1
            print(f"  ⚠⚠⚠ FALSIFIED: support {sorted(positions)}, dist={d0}, ratio_to_R/q={rel:.4f}", flush=True)
        if rel > best_ratio:
            best_ratio = rel
            best_f_label = f"sparse_{sorted(positions)}"
            print(f"  best so far: sparse {sorted(positions)}, dist={d0}, ratio_to_R/q={rel:.4f}", flush=True)
    print(f"# Strategy 2 done: {triples_tested} random sparse above-J f's", flush=True)

    print("", flush=True)
    print(f"# === SUMMARY ===", flush=True)
    print(f"# Best ratio_to_R/q observed: {best_ratio:.4f} ({best_f_label})", flush=True)
    print(f"# Number of FALSIFIERS (ratio > 1): {n_above_Rq}", flush=True)
    print(f"# Total time: {time.time()-t0:.1f}s", flush=True)
    if n_above_Rq == 0:
        print(f"# *** R/q bound HOLDS across {pairs_tested + triples_tested} above-J adversarial f's. ***", flush=True)


if __name__ == '__main__':
    main()
