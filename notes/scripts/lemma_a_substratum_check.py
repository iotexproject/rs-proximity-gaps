#!/usr/bin/env python3 -u
"""Lemma A — sub-stratum cancellation test.

Question: of the R_lead = #{S : line ∩ V_S × V_S ≠ ∅} crossings, how
many actually land inside V_bad (i.e., have M > T at the crossing α),
versus being absorbed by the M ≤ T "boundary" of V_S × V_S?

Lemma A's conjectured polynomial bound on N(ℓ) := #{α : ℓ(α) ∈ V_bad}
combined with Note 0128's uniform-tightness (Pr[M > T] prefactor =
binom(n, w+1) exactly) FORCES the relation

    N(ℓ)  ≪  R_lead(ℓ)

for generic line, i.e., a curve-measure-specific cancellation that
does not appear in uniform measure. This script tests it directly.

For each S resonance (line crosses V_S × V_S at some α_S), we compute
M(ℓ(α_S)) exactly using the full M-counter from
op2_curve_measure_prefactor.count_M (which considers all |E|=w
supports in [n], not just E ⊂ S). Three outcomes:

  (a) M(ℓ(α_S)) ≤ T  :  α_S in (V_S × V_S) \ V_bad. Cancellation.
  (b) M(ℓ(α_S)) > T  :  α_S contributes to N(ℓ). Not cancelled.
  (c) M(ℓ(α_S)) ≥ T+1 specifically due to E ⊄ S terms : sub-stratum
      bonus from a different S' adding γ-realizers.

We tally R_lead, N, and M-distribution at the crossings to test path
(1) of Note 0129.
"""

import os
import sys
import random
import time
from itertools import combinations
from math import comb

random.seed(2026)

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from op2_curve_measure_prefactor import (  # type: ignore  # noqa: E402
    small_field_subgroup,
    precompute_E_kernels,
    count_M,
)
from lemma_a_stratum_count import (  # type: ignore  # noqa: E402
    p_S_coeffs,
    shifted_basis_inner,
)


def crossing_alpha(p_S, u1, v1, u2, v2, c, D, p):
    """Return α ∈ F_p such that ℓ(α) ∈ V_S × V_S, or None.

    This duplicates the test in lemma_a_stratum_count.line_crosses_VS_squared
    but returns the α value (or None) instead of just a 0/1 indicator.
    """
    A = shifted_basis_inner(p_S, u1, c, D, p)
    B = shifted_basis_inner(p_S, v1, c, D, p)
    C = shifted_basis_inner(p_S, u2, c, D, p)
    Dv = shifted_basis_inner(p_S, v2, c, D, p)

    nz = next((i for i in range(c - 1) if B[i] != 0), None)
    if nz is None:
        if any(a != 0 for a in A):
            return None
        nz2 = next((i for i in range(c - 1) if Dv[i] != 0), None)
        if nz2 is None:
            return 0 if all(c_ == 0 for c_ in C) else None
        alpha2 = (-C[nz2] * pow(Dv[nz2], p - 2, p)) % p
        for i in range(c - 1):
            if (C[i] + alpha2 * Dv[i]) % p != 0:
                return None
        return alpha2
    alpha = (-A[nz] * pow(B[nz], p - 2, p)) % p
    for i in range(c - 1):
        if i == nz:
            continue
        if (A[i] + alpha * B[i]) % p != 0:
            return None
    for i in range(c - 1):
        if (C[i] + alpha * Dv[i]) % p != 0:
            return None
    return alpha


def line_at(u1, v1, u2, v2, alpha, p):
    s1 = [(u1[j] + alpha * v1[j]) % p for j in range(len(u1))]
    s2 = [(u2[j] + alpha * v2[j]) % p for j in range(len(u2))]
    return s1, s2


def cell_test(n, c, p, n_lines, max_n_alpha=None):
    L = small_field_subgroup(p, n)
    if L is None:
        return None
    k = n // 2
    D = (n + k) // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1 or w + 1 > n:
        return None

    # Pre-compute weight-w E-kernels for the M-counter (all E ⊂ [n], |E|=w).
    all_kers = precompute_E_kernels(L, p, D, w)

    # Pre-compute (w+1)-supports' p_S polynomial coefficients.
    pS_table = []
    for S_idx in combinations(range(n), w + 1):
        pS_table.append(p_S_coeffs(S_idx, L, p, D))

    R_lead_total = 0
    R_in_Vbad_total = 0
    R_outside_Vbad_total = 0
    M_at_crossing_hist = {}  # M -> count

    t0 = time.time()
    for line_idx in range(n_lines):
        u1 = [random.randrange(p) for _ in range(D)]
        v1 = [random.randrange(p) for _ in range(D)]
        u2 = [random.randrange(p) for _ in range(D)]
        v2 = [random.randrange(p) for _ in range(D)]
        for pS in pS_table:
            alpha = crossing_alpha(pS, u1, v1, u2, v2, c, D, p)
            if alpha is None:
                continue
            R_lead_total += 1
            s1, s2 = line_at(u1, v1, u2, v2, alpha, p)
            M = count_M(s1, s2, p, D, c, w, all_kers)
            M_at_crossing_hist[M] = M_at_crossing_hist.get(M, 0) + 1
            if M > T:
                R_in_Vbad_total += 1
            else:
                R_outside_Vbad_total += 1
        if (line_idx + 1) % max(1, n_lines // 10) == 0:
            print(
                f"    line {line_idx+1}/{n_lines}: "
                f"R_lead={R_lead_total} (Vbad={R_in_Vbad_total}, "
                f"outside={R_outside_Vbad_total}), "
                f"elapsed={time.time()-t0:.1f}s",
                flush=True,
            )

    elapsed = time.time() - t0
    return {
        "n": n, "c": c, "p": p, "D": D, "w": w, "T": T,
        "n_lines": n_lines,
        "R_lead": R_lead_total,
        "R_in_Vbad": R_in_Vbad_total,
        "R_outside_Vbad": R_outside_Vbad_total,
        "M_hist": M_at_crossing_hist,
        "elapsed": elapsed,
    }


def main():
    print("Lemma A — sub-stratum cancellation test")
    print("=" * 80)
    print("For each S-resonance, compute M(ℓ(α_S)) and check if M > T.")
    print("Tests path (1) of Note 0129: does V_bad ⊊ ∪ V_S × V_S strictly")
    print("on the curve, even though they agree as Zariski closures?")
    print()

    cases = [
        # (n, c, p, n_lines)
        # Stay in feasibility w ≥ T (only c ≥ 3 with D large enough).
        ( 8, 3,  17, 1000),  # T=3, q/T=5.7. Pred R_lead/line ≈ 0.014.
        (10, 3,  31, 1000),  # T=4, q/T=7.8. C(10,5)=252. Pred ≈ 0.0085.
        (12, 3,  37, 1000),  # T=5, q/T=7.4. C(12,7)=792. Pred ≈ 0.0156.
        (16, 3,  97,  500),  # T=7, q/T=13.9. C(16,10)=8008. Pred ≈ 0.0088.
        ( 8, 4,  17,  500),  # T=2.  D=6 means w=2, w+1=3. Hmm marginal.
                             # actually D=6, w=2, T=2 (=w), feasibility OK.
        (10, 4,  31,  500),  # T=3.
        (12, 4,  37,  500),  # T=4.
    ]
    rows = []
    for n, c, p, nl in cases:
        print(f"--- (n={n}, c={c}, p={p}, n_lines={nl}) ---", flush=True)
        r = cell_test(n, c, p, nl)
        if r is not None:
            rows.append(r)
        print()

    print("=" * 80)
    print("SUMMARY: cancellation ratio R_in_Vbad / R_lead")
    print("=" * 80)
    print(f"{'(n,c,p)':<14} {'D':>3} {'w':>3} {'T':>3}  "
          f"{'lines':>5}  {'R_lead':>8} {'R_in':>8} {'R_out':>8}  "
          f"{'in/lead':>8}  {'Hist M':>20}")
    for r in rows:
        ratio = r['R_in_Vbad'] / max(1, r['R_lead'])
        hist_str = ", ".join(
            f"{m}:{c}" for m, c in sorted(r['M_hist'].items())
        )
        if not hist_str:
            hist_str = "-"
        print(
            f"({r['n']},{r['c']},{r['p']})".ljust(14)
            + f" {r['D']:>3} {r['w']:>3} {r['T']:>3}  "
            + f"{r['n_lines']:>5}  "
            + f"{r['R_lead']:>8} {r['R_in_Vbad']:>8} {r['R_outside_Vbad']:>8}  "
            + f"{ratio:>8.3f}  {hist_str:>20}"
        )
    print()
    print("Interpretation:")
    print("  - Hist M shows the M-distribution at S-resonance crossings.")
    print("  - At the leading stratum |S|=w+1, generic crossings yield")
    print("    M = w+1 (fan from all E ⊂ S of size w). For c ≥ 3 with")
    print("    w+1 > T, this means R_in_Vbad / R_lead ≈ 1 generically.")
    print("    A ratio significantly below 1 would indicate sub-stratum")
    print("    cancellation — path (1) of Note 0129.")
    print("  - A ratio ≈ 1 means N(ℓ) ≈ R_lead generically, so the")
    print("    polynomial bound on N(ℓ) requires R_lead to be polynomial,")
    print("    which (per the lemma_a_stratum_count.py sweep) it is NOT")
    print("    in the C(n,w+1) ≫ poly(n) regime.")


if __name__ == "__main__":
    main()
