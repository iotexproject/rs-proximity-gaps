#!/usr/bin/env python3 -u
"""S5 — Empirical FRI-attack adversary smoke test (paper 3 §3 verification).

Reviewer C's concern (rephrased): paper 3 bounds Pr[M > T] (V_bad event),
but the FRI commit-side bad event is Pr[M ≥ 1]. Are these the same? If
not, what's the gap?

This script empirically separates the two events at small parameters and
verifies:

  (i)  Pr[M ≥ 1] is governed by the BCIKS-style union bound C(n, w) ·
       |F|^{-(c-1)}  (codim c-1 for the leading "single-realizer" event).
  (ii) Pr[M > T]  is governed by the paper's codim bound |F|^{-2(c-1)}
       times a poly(n, c) prefactor (codim 2(c-1)).

The gap between (i) and (ii) is exactly |F|^{c-1} — the codim improvement
this paper extracts. We confirm this gap empirically by sweeping p.

We also report the *full M-histogram*:  Pr[M = 0], Pr[M = 1], …, Pr[M > T].
This histogram is informative for the §8.1 threshold-mismatch follow-up
(Reviewer C#2): the codim of the {M = 1} stratum can be read off directly
from the slope of Pr[M = 1] versus p.

Method: small (n, c) with subgroup-friendly p ∈ {p : n | p-1}. Sample
N random (s_1, s_2) ∈ F_p^{2D} uniformly; compute M(s_1, s_2) using
the precomputed weight-w kernel infrastructure from
op2_curve_measure_prefactor.py.

Output: stdout (pipe to fri_adversary_smoke.output.txt).

Runtime estimate: at (n=8, c=3) and N=300_000 samples per p, with
6 p-values, expect ~10–15 minutes total in pure Python.
"""

import sys
import random
import time
from math import comb

sys.path.insert(0, 'notes/scripts')

from op2_curve_measure_prefactor import (  # type: ignore
    small_field_subgroup,
    precompute_E_kernels,
    count_M,
)


def smoke_row(n, c, p, n_samples):
    L = small_field_subgroup(p, n)
    if L is None:
        return None
    k = n // 2
    D = (n + k) // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1:
        return None

    t0 = time.time()
    all_kers = precompute_E_kernels(L, p, D, w)
    t_pre = time.time() - t0

    # Histogram up to M = T + 3.  Tail captures M > T entries.
    H_LEN = T + 4
    hist = [0] * H_LEN
    tail = 0  # M ≥ H_LEN

    t0 = time.time()
    for i in range(n_samples):
        s1 = [random.randrange(p) for _ in range(D)]
        s2 = [random.randrange(p) for _ in range(D)]
        M = count_M(s1, s2, p, D, c, w, all_kers)
        if M < H_LEN:
            hist[M] += 1
        else:
            tail += 1
    t_samp = time.time() - t0

    pr = [h / n_samples for h in hist]
    pr_tail = tail / n_samples

    pr_ge1 = 1.0 - pr[0]
    pr_gt_T = sum(pr[T + 1:]) + pr_tail

    # Theoretical predictions (asymptotic-codim, no poly factor).
    pred_M_ge_1 = comb(n, w) * (p ** (-(c - 1)))  # BCIKS-style
    pred_M_gt_T = (p ** (-2 * (c - 1)))            # asymptotic-codim
    pred_unif = comb(n, w + 1) * (p ** (-2 * (c - 1)))  # uniform-measure

    return {
        "n": n, "c": c, "p": p, "D": D, "w": w, "T": T,
        "n_samples": n_samples,
        "hist": hist, "tail": tail,
        "pr": pr, "pr_tail": pr_tail,
        "pr_ge1": pr_ge1, "pr_gt_T": pr_gt_T,
        "pred_M_ge_1": pred_M_ge_1,
        "pred_M_gt_T": pred_M_gt_T,
        "pred_unif": pred_unif,
        "t_pre": t_pre, "t_samp": t_samp,
    }


def fmt_row(r):
    p = r["p"]
    out = f"  p={p:>4}: D={r['D']} w={r['w']} T={r['T']}  "
    out += f"Pr[M=0]={r['pr'][0]:.4e}  "
    out += f"Pr[M=1]={r['pr'][1]:.4e}  "
    if len(r["pr"]) > 2:
        out += f"Pr[M=2]={r['pr'][2]:.4e}  "
    out += f"Pr[M≥1]={r['pr_ge1']:.4e}  "
    out += f"Pr[M>T]={r['pr_gt_T']:.4e}"
    return out


def main():
    random.seed(20260430)
    print("=" * 90)
    print("S5 — FRI adversary smoke test")
    print("Empirically separating Pr[M ≥ 1] (BCIKS regime) from Pr[M > T] (V_bad)")
    print("=" * 90)
    print()

    # Test grid: subgroup-friendly p sweeps for fixed (n, c).
    # Sample sizes calibrated to per-row runtime ≤ 5 min.
    test_grid = [
        # (n, c, p_list, n_samples)
        (8, 3, [17, 41, 73, 89, 113, 137], 200_000),  # main scaling sweep
        (10, 3, [11, 31, 41, 61],          100_000),  # n-dependence
        (12, 3, [13, 37],                   30_000),  # heavy case
    ]

    all_results = []
    for n, c, p_list, n_samp in test_grid:
        print(f"--- (n={n}, c={c}) sweep over p ∈ {p_list}, N={n_samp:,} samples each ---")
        rows = []
        for p in p_list:
            t0 = time.time()
            r = smoke_row(n, c, p, n_samp)
            if r is None:
                print(f"  p={p}: skip (no subgroup)")
                continue
            print(fmt_row(r) + f"  ({time.time()-t0:.1f}s)", flush=True)
            rows.append(r)
        all_results.append({"n": n, "c": c, "rows": rows})
        print()

    # Detailed scaling analysis.
    print("=" * 90)
    print("SCALING ANALYSIS — predictions vs observations")
    print("=" * 90)
    for block in all_results:
        n, c = block["n"], block["c"]
        rows = block["rows"]
        if not rows:
            continue
        print(f"\n(n={n}, c={c}): codim Pr[M ≥ 1] expected = {c-1}; "
              f"codim Pr[M > T] expected = {2*(c-1)}.")
        print(f"  {'p':>5} {'Pr[M≥1]':>12} {'pred_BCIKS':>12} {'ratio':>10} "
              f"{'Pr[M>T]':>12} {'pred_codim':>12} {'unif_pred':>12} "
              f"{'unif_ratio':>10}")
        for r in rows:
            p = r["p"]
            pr_ge1, pr_gt_T = r["pr_ge1"], r["pr_gt_T"]
            pred_b = r["pred_M_ge_1"]
            pred_c = r["pred_M_gt_T"]
            pred_u = r["pred_unif"]
            ratio_b = pr_ge1 / pred_b if pred_b > 0 else float("inf")
            ratio_u = (pr_gt_T / pred_u) if pred_u > 0 else float("inf")
            print(f"  {p:>5} {pr_ge1:>12.4e} {pred_b:>12.4e} {ratio_b:>10.2f} "
                  f"{pr_gt_T:>12.4e} {pred_c:>12.4e} {pred_u:>12.4e} "
                  f"{ratio_u:>10.2f}")

    print()
    print("=" * 90)
    print("HISTOGRAM (Pr[M = j] for j = 0, 1, ..., T+3, plus tail)")
    print("=" * 90)
    for block in all_results:
        n, c = block["n"], block["c"]
        for r in block["rows"]:
            p, T = r["p"], r["T"]
            hist_str = " ".join(f"{p_j:.3e}" for p_j in r["pr"])
            print(f"(n={n}, c={c}, p={p}, T={T}): {hist_str}  tail={r['pr_tail']:.3e}")

    print()
    print("Interpretation:")
    print(" - Pr[M ≥ 1] should track ≈ C(n,w)/p^{c-1} (BCIKS-style union bound).")
    print(" - Pr[M > T]  should track ≈ p^{-2(c-1)} (this paper's codim bound),")
    print("   modulo the binom(n, w+1) prefactor (uniform-measure pred_unif column).")
    print(" - The ratio Pr[M ≥ 1] / Pr[M > T] should grow as p^{c-1} — the codim")
    print("   improvement this paper extracts over the BCIKS baseline.")
    print(" - If Pr[M = 1] / Pr[M > T] ≈ p^{c-1} as p grows, the {M = 1}-stratum")
    print("   has codim (c-1), not 2(c-1) — confirming the threshold-mismatch")
    print("   caveat in §8.1.")


if __name__ == "__main__":
    main()
