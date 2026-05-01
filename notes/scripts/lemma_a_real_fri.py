#!/usr/bin/env python3 -u
"""Lemma A — real FRI curve + Johnson-regime δ-far f ratio test.

Closes the c322 Note 0134 loophole:
  c322 measured "FRI/uniform ratio ≈ 1.40" using
    (i) abstract zero-pad of even/odd splits (NOT real FRI fold)
    (ii) uniform f ∈ F_q^{2n} (NOT Johnson-regime δ-far)
  But Lemma A (paper3 §8.2) is quantified over
    (i) real FRI fold: s(α) = f_even + α f_odd on L^2 subgroup
    (ii) Johnson-regime δ-far f: Δ(f, RS_k) ∈ (δ_J n, (1-ρ) n)

This script implements both fixes and reruns the ratio test.

Setup (matches c322's L = subgroup of size n_round1 for V_E construction):
  L_0 of size 4*n_round1 (round-0 domain).
  L_1 = L_0^2 of size 2*n_round1.
  L_2 = L_1^2 of size n_round1 (= c322's "L").
  Initial code RS_(|L_0|, k_0) with k_0 = n_round1, rate ρ = 1/4.
    → Distance d_0 = 3n_round1 + 1, Johnson radius δ_J = 0.5.

Real FRI 2-fold:
  f^(0) ∈ F_p^|L_0| (evaluations).
  Fold step: g(X) = g_e(X^2) + X · g_o(X^2). Decompose g into (g_e, g_o) on next domain:
    g_e[j] = (g[j] + g[j + n/2]) / 2          for j ∈ [0, n/2).
    g_o[j] = (g[j] - g[j + n/2]) / (2 · v_j)  where v_j = current-domain[j].
  Apply 2 folds to f^(0) (without challenge — just decomposing):
    Step 1: f^(0) → ((f^(0))_e, (f^(0))_o) on L_1.
    Step 2: each → ((..)_e, (..)_o) on L_2. Get 4 functions on L_2.
  These 4 functions on L_2 = c322's "fe_e, fo_e, fe_o, fo_o" but as REAL EVALUATIONS, not abstract coefficients.
  Compute syndromes on L_2 of length D against RS_(n_round1, n_round1/4) — these are the (u_1, v_1, u_2, v_2) of the real-FRI commit-curve.

Then sweep α ∈ F_p, compute (s_1, s_2) = (u_1 + α v_1, u_2 + α v_2), test V_bad.

Two test branches:
  (a) f ~ uniform on F_p^|L_0|.
  (b) f := random codeword c in RS_(|L_0|, k_0) + flip ⌈δ|L_0|⌉ positions, δ = 0.625 (Johnson midpoint).

Compare ratio FRI(a)/uniform-line, FRI(b)/uniform-line, FRI(b)/FRI(a).
"""

import os
import random
import sys
import time
from math import comb

random.seed(2026)

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from op2_curve_measure_prefactor import (  # type: ignore
    small_field_subgroup,
    precompute_E_kernels,
    count_M,
)


# ---------------------------------------------------------------------------
# Real FRI fold infrastructure
# ---------------------------------------------------------------------------

def fold_evals_one_step(g_evals, L_curr, p):
    """Given g: L_curr → F_p (length n), return (g_e, g_o) on L_next = L_curr^2 (length n/2).
    g_e[j] = (g[j] + g[j + n/2]) / 2.
    g_o[j] = (g[j] - g[j + n/2]) / (2 · L_curr[j]).
    Uses convention L_curr[j + n/2] = -L_curr[j] (since L_curr is mult subgroup of even order).
    """
    n = len(L_curr)
    assert n % 2 == 0, f"need even-order domain, got {n}"
    assert len(g_evals) == n
    half = n // 2
    inv2 = pow(2, p - 2, p)
    g_e = [0] * half
    g_o = [0] * half
    for j in range(half):
        a = g_evals[j]
        b = g_evals[j + half]
        g_e[j] = ((a + b) * inv2) % p
        v_j = L_curr[j]
        # 1 / (2 * v_j) = inv2 * inv(v_j)
        inv_vj = pow(v_j, p - 2, p)
        g_o[j] = ((a - b) * inv2 % p * inv_vj) % p
    return g_e, g_o


def vandermonde_syndrome(g_evals, L, D, p):
    """Compute syndrome s_j = sum_v g(v) · v^j  for v ∈ L, j = 0, ..., D-1.
    Treats g_evals as the values of g at L's points (length |L|)."""
    n = len(L)
    assert len(g_evals) == n
    s = [0] * D
    for i in range(n):
        v = L[i]
        gv = g_evals[i]
        if gv == 0:
            continue
        v_pow = 1
        for j in range(D):
            s[j] = (s[j] + gv * v_pow) % p
            v_pow = (v_pow * v) % p
    return s


def fri_curve_real(f_evals, L0, L1, L2, D, p):
    """Real-FRI 2-fold decomposition. Returns (u_1, v_1, u_2, v_2) such that
    (s_1(α), s_2(α)) = (u_1 + α v_1, u_2 + α v_2) is the syndrome decomp of
    f^(1) := (f^(0))_e + α (f^(0))_o, evaluated as syndromes on L_2 of length D.
    """
    fe1, fo1 = fold_evals_one_step(f_evals, L0, p)         # on L_1
    fee, feo = fold_evals_one_step(fe1, L1, p)              # on L_2
    foe, foo = fold_evals_one_step(fo1, L1, p)              # on L_2
    u_1 = vandermonde_syndrome(fee, L2, D, p)
    v_1 = vandermonde_syndrome(foe, L2, D, p)
    u_2 = vandermonde_syndrome(feo, L2, D, p)
    v_2 = vandermonde_syndrome(foo, L2, D, p)
    return u_1, v_1, u_2, v_2


def n_hits_along_line(u_1, v_1, u_2, v_2, p, D, c, w, T, all_kers):
    """N(ℓ) = #{α ∈ F_p : count_M(s_1(α), s_2(α)) > T}."""
    hits = 0
    for alpha in range(p):
        s1 = [(u_1[j] + alpha * v_1[j]) % p for j in range(D)]
        s2 = [(u_2[j] + alpha * v_2[j]) % p for j in range(D)]
        if count_M(s1, s2, p, D, c, w, all_kers) > T:
            hits += 1
    return hits


# ---------------------------------------------------------------------------
# Johnson-regime δ-far f generator
# ---------------------------------------------------------------------------

def evaluate_polynomial(coeffs, L, p):
    """Evaluate poly(X) = sum_i coeffs[i] X^i on each v ∈ L."""
    out = []
    for v in L:
        val = 0
        v_pow = 1
        for c in coeffs:
            val = (val + c * v_pow) % p
            v_pow = (v_pow * v) % p
        out.append(val)
    return out


def random_codeword_evals(L, k, p):
    """Sample a uniform random codeword c ∈ RS_(|L|, k) by sampling coeffs of
    degree < k poly and evaluating on L."""
    coeffs = [random.randrange(p) for _ in range(k)]
    return evaluate_polynomial(coeffs, L, p)


def johnson_regime_f(L0, k0, p, delta, rng=random):
    """Generate f ∈ F_p^|L_0| at distance ≈ ⌈δ|L_0|⌉ from a random codeword in RS_(|L_0|, k_0).
    No rigorous Johnson-distance verification — just construction-based.
    For δ > δ_J this gives f outside Johnson radius of c_0; for OTHER codewords c ≠ c_0,
    Δ(f, c) ≥ |d - ⌈δ|L_0|⌉| ≥ |L_0|(1 - ρ) - δ|L_0| = (1 - ρ - δ)|L_0|.
    With δ = 0.625 and ρ = 1/4 (so 1-ρ = 0.75): lower bound (0.125)|L_0| — not Johnson.
    But probabilistically over random flips, δ-far holds w.h.p. for moderate |L_0|.
    """
    n0 = len(L0)
    n_flip = int(round(delta * n0))
    c_evals = random_codeword_evals(L0, k0, p)
    f_evals = list(c_evals)
    flip_positions = rng.sample(range(n0), n_flip)
    for pos in flip_positions:
        # Pick a different value uniformly from F_p \ {c_evals[pos]}.
        new_val = rng.randrange(p)
        while new_val == c_evals[pos]:
            new_val = rng.randrange(p)
        f_evals[pos] = new_val
    return f_evals, c_evals, flip_positions


def hamming_distance(u, v, p=None):
    return sum(1 for a, b in zip(u, v) if a != b)


def verify_distance_above_johnson(f_evals, L0, k0, p, johnson_radius_n,
                                  n_codeword_samples=200, rng=random):
    """Probabilistic verification: sample n_codeword_samples random codewords c,
    and assert Δ(f, c) ≥ johnson_radius_n for all of them. NOT rigorous (only
    checks the sample) but a reasonable sanity check."""
    min_dist = len(f_evals)
    closest = None
    for _ in range(n_codeword_samples):
        c_evals = random_codeword_evals(L0, k0, p)
        d = hamming_distance(f_evals, c_evals)
        if d < min_dist:
            min_dist = d
            closest = c_evals
    return min_dist, min_dist >= johnson_radius_n


# ---------------------------------------------------------------------------
# Ratio test driver
# ---------------------------------------------------------------------------

def setup_cell(n_round1, c, p):
    """Set up the cell: domains, code, parameters. Returns dict or None if infeasible."""
    n0 = 4 * n_round1
    if (p - 1) % n0 != 0:
        return None  # need 4n | p-1 for two-fold real FRI
    L0 = small_field_subgroup(p, n0)
    if L0 is None:
        return None
    # L_1 = L_0^2 (mult subgroup of order 2*n_round1).
    n1 = 2 * n_round1
    L1 = [pow(v, 2, p) for v in L0[:n1]]  # L_1 = {ω_0^{2j} : j ∈ [0, n1)}
    # L_2 = L_1^2 (order n_round1).
    n2 = n_round1
    L2 = [pow(v, 2, p) for v in L1[:n2]]
    # Sanity check: L_2 has n_round1 distinct elements.
    assert len(set(L2)) == n2, f"L_2 not distinct: {L2}"
    # Match c322 convention: D = (n + n/2) / 2 = 3n/4 (or floor variant).
    k_L_pap = n_round1 // 2
    D = (n_round1 + k_L_pap) // 2
    k2 = n_round1 - D  # code dim at L_2 (rate kept consistent)
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1 or w + 1 > n_round1:
        return None
    # Initial code RS_(|L_0|, k_0). Rate-preserving FRI: ρ_0 = ρ_2 = k_2 / n.
    rho = k2 / n_round1
    k0 = int(round(rho * n0))
    delta_J = 1.0 - rho ** 0.5
    delta_target = (delta_J + (1 - rho)) / 2  # Johnson regime midpoint
    return {
        "n_round1": n_round1, "c": c, "p": p,
        "n0": n0, "n1": n1, "n2": n2,
        "L0": L0, "L1": L1, "L2": L2,
        "k0": k0, "k2": k2, "D": D, "w": w, "T": T,
        "rho": rho, "delta_J": delta_J, "delta_target": delta_target,
    }


def sweep_cell(cell, n_lines):
    """Run uniform-line + real-FRI(uniform f) + real-FRI(Johnson f) sweeps.
    Returns dict with averages, totals, ratios, SEs."""
    p = cell["p"]
    L0, L1, L2 = cell["L0"], cell["L1"], cell["L2"]
    D, c, w, T = cell["D"], cell["c"], cell["w"], cell["T"]
    n_round1 = cell["n_round1"]
    n0, k0 = cell["n0"], cell["k0"]
    delta_target = cell["delta_target"]

    bin_nw1 = comb(n_round1, w + 1)
    pred_per_line = bin_nw1 / (p ** (2 * c - 3))

    print(f"=== (n={n_round1}, c={c}, p={p}, D={D}, w={w}, T={T}) ===", flush=True)
    print(f"  |L_0|={n0}, |L_1|={cell['n1']}, |L_2|={cell['n2']}, k_0={k0}", flush=True)
    print(f"  rate ρ={cell['rho']:.4f}, Johnson δ_J={cell['delta_J']:.4f}, "
          f"target δ={delta_target:.4f}", flush=True)
    print(f"  C(n,w+1)={bin_nw1}, pred E[N]/line={pred_per_line:.4e}", flush=True)

    all_kers = precompute_E_kernels(L2, p, D, w)
    print(f"  precomputed {len(all_kers)} support kernels on L_2", flush=True)

    # === Test 0: uniform line in F_p^{2D} ===
    t0 = time.time()
    rand_total = 0
    rand_max = 0
    for _ in range(n_lines):
        u_1 = [random.randrange(p) for _ in range(D)]
        v_1 = [random.randrange(p) for _ in range(D)]
        u_2 = [random.randrange(p) for _ in range(D)]
        v_2 = [random.randrange(p) for _ in range(D)]
        h = n_hits_along_line(u_1, v_1, u_2, v_2, p, D, c, w, T, all_kers)
        rand_total += h
        rand_max = max(rand_max, h)
    rand_avg = rand_total / n_lines
    print(f"  [0] uniform line:        avg={rand_avg:.4f}, max={rand_max:>3}, "
          f"total={rand_total} ({time.time()-t0:.1f}s)", flush=True)

    # === Test (a): real-FRI curve with uniform f ===
    t0 = time.time()
    fri_uniform_total = 0
    fri_uniform_max = 0
    for _ in range(n_lines):
        f_evals = [random.randrange(p) for _ in range(n0)]
        u_1, v_1, u_2, v_2 = fri_curve_real(f_evals, L0, L1, L2, D, p)
        h = n_hits_along_line(u_1, v_1, u_2, v_2, p, D, c, w, T, all_kers)
        fri_uniform_total += h
        fri_uniform_max = max(fri_uniform_max, h)
    fri_uniform_avg = fri_uniform_total / n_lines
    print(f"  [a] real-FRI + uniform f: avg={fri_uniform_avg:.4f}, max={fri_uniform_max:>3}, "
          f"total={fri_uniform_total} ({time.time()-t0:.1f}s)", flush=True)

    # === Test (b): real-FRI curve with Johnson-regime δ-far f ===
    t0 = time.time()
    fri_johnson_total = 0
    fri_johnson_max = 0
    for _ in range(n_lines):
        f_evals, _c_evals, _ = johnson_regime_f(L0, k0, p, delta_target)
        u_1, v_1, u_2, v_2 = fri_curve_real(f_evals, L0, L1, L2, D, p)
        h = n_hits_along_line(u_1, v_1, u_2, v_2, p, D, c, w, T, all_kers)
        fri_johnson_total += h
        fri_johnson_max = max(fri_johnson_max, h)
    fri_johnson_avg = fri_johnson_total / n_lines
    print(f"  [b] real-FRI + Johnson f: avg={fri_johnson_avg:.4f}, max={fri_johnson_max:>3}, "
          f"total={fri_johnson_total} ({time.time()-t0:.1f}s)", flush=True)

    def ratio_with_se(num_tot, den_tot, num_avg, den_avg):
        if den_tot == 0:
            return None, None
        r = num_avg / max(den_avg, 1e-12)
        if num_tot == 0:
            return r, None
        se = r * (1.0 / num_tot + 1.0 / den_tot) ** 0.5
        return r, se

    r_a, se_a = ratio_with_se(fri_uniform_total, rand_total, fri_uniform_avg, rand_avg)
    r_b, se_b = ratio_with_se(fri_johnson_total, rand_total, fri_johnson_avg, rand_avg)
    r_ba, se_ba = ratio_with_se(fri_johnson_total, fri_uniform_total, fri_johnson_avg, fri_uniform_avg)

    def fmt(r, se):
        if r is None: return "n/a"
        if se is None: return f"{r:.3f} (SE n/a)"
        return f"{r:.3f} ± {se:.3f}"

    print(f"  RATIO (a) FRI-uniform/line  = {fmt(r_a, se_a)}", flush=True)
    print(f"  RATIO (b) FRI-Johnson/line  = {fmt(r_b, se_b)}", flush=True)
    print(f"  RATIO (b)/(a) Johnson/uniform = {fmt(r_ba, se_ba)}", flush=True)

    return {
        "cell": cell, "n_lines": n_lines,
        "rand_total": rand_total, "rand_avg": rand_avg, "rand_max": rand_max,
        "fri_uniform_total": fri_uniform_total, "fri_uniform_avg": fri_uniform_avg,
        "fri_johnson_total": fri_johnson_total, "fri_johnson_avg": fri_johnson_avg,
        "ratio_a": r_a, "ratio_a_se": se_a,
        "ratio_b": r_b, "ratio_b_se": se_b,
        "ratio_ba": r_ba, "ratio_ba_se": se_ba,
    }


def main():
    print("lemma_a_real_fri.py — Phase 1.3 ratio test")
    print("Real FRI 2-fold + uniform-vs-Johnson f")
    print("=" * 78)
    cells_to_run = [
        # (n_round1, c, p) — need 4n | (p-1).
        # Hit rate per line at uniform = C(n,w+1)/p^(2c-3).
        (10, 3, 41),   # primary: pred ≈ 3.7e-3/line, ~18 hits per 5000 lines per branch
        (8, 3, 97),    # low signal: pred ≈ 7.7e-5/line — supplementary only
        (12, 3, 97),   # low signal: pred ≈ 8.7e-4/line — supplementary
    ]
    n_lines_per_cell = {
        (10, 3, 41): 5000,
        (8, 3, 97): 2000,
        (12, 3, 97): 200,
    }
    for tup in cells_to_run:
        cell = setup_cell(*tup)
        if cell is None:
            print(f"\n*** Skip: {tup} infeasible.\n")
            continue
        n_lines = n_lines_per_cell[tup]
        result = sweep_cell(cell, n_lines)
        print()


if __name__ == "__main__":
    main()
