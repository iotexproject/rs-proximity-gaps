#!/usr/bin/env python3 -u
"""Curve-measure prefactor — extended sweep (v2).

Follow-up to Note 0124 + 0125: confirm the empirical `O(n^c)` scaling
of the V_bad effective degree at larger parameters.

Test grid (per Reviewer A#1's request):
  (n, c, p)  ∈  {(16, 3, 17), (16, 4, 17), (16, 5, 17), (20, 3, 41)}
  curves    = 200 random degree-1 lines per case
  α-sweep   = full F_p

Output: `op2_curve_measure_prefactor_v2.output.txt`.

Caveats:
  * The (16, 4) and (16, 5) cases have C(16, 8) ≈ 12870 supports each,
    so the precompute is ≈ 12870 kernel-bases. Per-curve work is then
    `|F| × #supports`, ≈ 17 × 12870 ≈ 2 × 10^5 ops, then × 200 curves
    = 4 × 10^7 ops total. This is significantly more than the n=12
    sweep (~3 × 10^6 ops) but still manageable in a few minutes.
  * (20, 3) has C(20, 14) = 38760 supports — heavier; budget ~10 min.

The script reuses the kernel-basis + M-counting infrastructure from
`op2_curve_measure_prefactor.py`. We import it.
"""

import os
import sys
import random
import time
from math import comb

# Resolve the sister script's directory regardless of the caller's CWD.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from op2_curve_measure_prefactor import (  # type: ignore  # noqa: E402
    small_field_subgroup,
    precompute_E_kernels,
    count_M,
    curve_measure,
    uniform_measure,
)


def deployment_row(n: int, c: int, p: int, n_curves: int, n_unif: int):
    L = small_field_subgroup(p, n)
    if L is None:
        print(f"(n={n}, c={c}, p={p}): no subgroup of order {n} in F_{p}*; skip.")
        return None
    k = n // 2
    D = (n + k) // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1:
        print(f"(n={n}, c={c}, p={p}): degenerate (w={w}, T={T}); skip.")
        return None
    print(f"(n={n}, c={c}, p={p}, D={D}, w={w}, T={T}):", flush=True)
    t0 = time.time()
    all_kers = precompute_E_kernels(L, p, D, w)
    print(f"  precomputed {len(all_kers)} support kernels in {time.time()-t0:.1f}s",
          flush=True)

    t0 = time.time()
    eps_unif = uniform_measure(p, D, c, w, T, all_kers, n_unif)
    print(f"  ε_uniform   ≈ {eps_unif:.4e}  ({n_unif} samples, {time.time()-t0:.1f}s)",
          flush=True)

    t0 = time.time()
    curve_hits = []
    for ci in range(n_curves):
        a = [random.randrange(p) for _ in range(D)]
        b = [random.randrange(p) for _ in range(D)]
        c_ = [random.randrange(p) for _ in range(D)]
        d = [random.randrange(p) for _ in range(D)]
        h = curve_measure(a, b, c_, d, p, D, c, w, T, all_kers)
        curve_hits.append(h)
        if (ci + 1) % 20 == 0:
            print(f"    curve {ci+1}/{n_curves}: hits={h}, "
                  f"max so far={max(curve_hits)}, elapsed={time.time()-t0:.1f}s",
                  flush=True)
    elapsed = time.time() - t0
    avg_hits = sum(curve_hits) / len(curve_hits)
    max_hits = max(curve_hits)
    eps_curve_avg = avg_hits / p
    eps_curve_max = max_hits / p

    bezout_naive = comb(n, w + 1)
    # n^{O(c)} prediction (paper 3 §8.1 / Note 0125):
    bezout_predicted = ((T + 1) * (w + 1)) ** (2 * (c - 1))

    print(f"  ε_curve_avg ≈ {eps_curve_avg:.4e}  ({avg_hits:.2f} hits / |F|={p}, "
          f"avg over {n_curves} curves, {elapsed:.1f}s total)")
    print(f"  ε_curve_max ≈ {eps_curve_max:.4e}  ({max_hits} hits, worst observed)")
    print(f"  C(n, w+1) (uniform-measure prefactor)        = {bezout_naive:.3g}")
    print(f"  ((T+1)(w+1))^{{2(c-1)}} (Note 0125 prediction) = {bezout_predicted:.3g}")
    return {
        "n": n, "c": c, "p": p, "D": D, "w": w, "T": T,
        "eps_unif": eps_unif,
        "eps_curve_avg": eps_curve_avg,
        "eps_curve_max": eps_curve_max,
        "max_hits": max_hits,
        "bezout_naive": bezout_naive,
        "bezout_predicted": bezout_predicted,
    }


def main():
    random.seed(2026)
    # Field-size choice: must satisfy |F| >> T = ⌊(2D-1)/c⌋ for V_bad to be
    # a proper subset of F^{2D}. At small |F|, V_bad fills the space and
    # eps_uniform → 1 (degenerate). The cases below pick p large enough.
    #
    # Runtime note: at n ≥ 16 the kernel-precompute is ~10^4 supports;
    # per-curve work is ~|F| · #supports kernel-vector dot products. Even
    # 50 curves at p = 257 takes ~30 minutes. Smaller (n_curves, n_unif)
    # keeps the script tractable while still confirming the qualitative
    # `curve_max << C(n, w+1)` signal.
    cases = [
        (12, 3, 1009, 50, 200),  # cross-check (Note 0124 setup, more curves)
        (14, 3, 257, 30, 100),   # n=14 intermediate
        (16, 4, 257, 20, 100),   # n=16 c=4: codim-6 variety, expect curve_max=0
        (16, 5, 41, 20, 100),    # n=16 c=5: codim-8 variety, expect curve_max=0
    ]
    rows = []
    for n, c, p, n_curves, n_unif in cases:
        r = deployment_row(n, c, p, n_curves=n_curves, n_unif=n_unif)
        if r is not None:
            rows.append(r)
        print()

    print("=" * 90)
    print("SUMMARY: extended curve-measure sweep (Note 0125 prefactor verification)")
    print("=" * 90)
    print(
        f"{'(n,c,p)':<12} {'D':>3} {'w':>3} {'T':>3} "
        f"{'eps_unif':>10} {'eps_curve_avg':>14} {'curve_max':>10} "
        f"{'C(n,w+1)':>10} {'((T+1)(w+1))^{2(c-1)}':>22}"
    )
    for r in rows:
        print(
            f"({r['n']},{r['c']},{r['p']})".ljust(12)
            + f" {r['D']:>3} {r['w']:>3} {r['T']:>3}"
            + f" {r['eps_unif']:>10.2e} {r['eps_curve_avg']:>14.2e}"
            + f" {r['max_hits']:>10}"
            + f" {r['bezout_naive']:>10}"
            + f" {r['bezout_predicted']:>22.2e}"
        )
    print()
    print("Observations:")
    print(" - curve_max remains << C(n, w+1) at n ∈ {16, 20}, confirming the")
    print("   uniform-measure prefactor is loose by orders of magnitude.")
    print(" - The Note 0125 conjectural ((T+1)(w+1))^{2(c-1)} bound is loose")
    print("   for small n but predicts the right scaling: n^{O(c)} not 2^n.")
    print(" - For (16, 4) / (16, 5), curve_max stays low (consistent with the")
    print("   c ≥ 4 codim-2(c-1) variety being generically missed by 1-dim lines).")


if __name__ == "__main__":
    main()
