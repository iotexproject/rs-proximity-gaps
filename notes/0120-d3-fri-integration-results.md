# Note 0120 — D3: Berlekamp #322 × FRI 2-round integration

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0104, 0117, 0119
**Status**: D3 complete. Quantifies Berlekamp commit-gain in FRI deployment.

## Setup

The FRI 2-round NI bound (Note 0104, deployment_params.py):
```
ε_NI ≤ Q · (R · ε_round_commit + (1 − δ/2)^t + 3(Q²+1)/2^κ)
```
with R = log_2 n FRI rounds, Q = 2^{q_loss} FS-loss, t Merkle queries,
κ-bit hash binding.

The COMMIT term breakdown:
```
OLD (BCIKS-generic):       ε_round_commit ≤ n / |F|         (c-independent)
NEW (Note 0117/0119):      ε_round_commit ≤ T/|F| + q^{-2(c−1)} · poly(n)
                           T = ⌊(2D−1)/c⌋
```

The **dominant term in NEW** at deployment (q ≫ n) is `T/|F|`. So the
Berlekamp gain over OLD on the commit term is:
```
gain = -log_2(T/|F|) − (-log_2(n/|F|)) = log_2(n/T) ≈ log_2(c)
```
**a constant log_2(c) bits per round**. For c ∈ {3, 4, 6, 9}: gain ≈
{1.58, 2.0, 2.58, 3.17} bits. The `q^{-2(c−1)}` tail is sub-dominant
(suppressed by extra factor q^{2c−3}) and only matters when the FRI
protocol changes.

## Quantitative result (op2_d3_fri_integration.py)

NI-128 target, q_loss=64, κ=384, δ=0.40 (BCIKS-Johnson). Sweep across
8 FRI fields × {n=2^20, 2^21} × ρ=1/2 × c ∈ {3, 4, 6, 9} = 80 rows.

**Summary**:
| Metric                          | OLD | NEW | Δ  |
|----------------------------------|-----|-----|-----|
| Total rows                       | 80  | 80  | —  |
| Feasible at NI-128               | 4   | 8   | +4 |
| Configs flipped by Berlekamp     | —   | —   | 4  |

**Flipped configs** (BabyBear-ext7 = 217-bit, the next-largest after Goldilocks):
- (n=2^21, ρ=1/2, c=3): cap_old=127.0, cap_new=128.5, t=597 ✓
- (n=2^21, ρ=1/2, c=4): cap_old=127.0, cap_new=129.0, t=597 ✓
- (n=2^21, ρ=1/2, c=6): cap_old=127.0, cap_new=129.5, t=597 ✓
- (n=2^21, ρ=1/2, c=9): cap_old=127.0, cap_new=130.1, t=597 ✓

These are configs where OLD commit-cap is **just barely below 128** and
Berlekamp's log_2(c) gain pushes them over the line. Real but narrow win.

## ABF §6.3 baseline (KoalaBear-ext6, 186-bit)

| c | cap_old | cap_new | gain | t_old | t_new | KiB_new |
|---|---------|---------|------|-------|-------|---------|
| 3 | 96.5    | 98.1    | +1.58| —     | —     | —       |
| 4 | 96.5    | 98.5    | +2.00| —     | —     | —       |
| 6 | 96.5    | 99.1    | +2.58| —     | —     | —       |
| 9 | 96.5    | 99.7    | +3.17| —     | —     | —       |

KoalaBear-ext6 caps **30 bits short of NI-128** under both OLD and NEW
in vanilla 2-round FRI accounting. The Berlekamp gain (≈ 3 bits) is
real but insufficient.

**Why this doesn't kill ABF**: ABF §6.3 uses (essentially) the **BCIKS-tight
codim-c commit bound** ε_round_commit ≤ poly(n) · q^{-c}, NOT the n/|F|
union bound. With BCIKS-tight, KoalaBear-ext6 has commit_cap ≈
3·186 − log_2(n·R) − q_loss ≈ 558 − 26 − 64 ≈ 468 bits, way enough.

The Berlekamp result is consistent with this BCIKS-tight value: **codim
V_bad = 2(c−1)** (Note 0117 + 0119) corresponds to ε_round_commit ≤
q^{-2(c−1)}, the tight bound. So Berlekamp **reaffirms** ABF's claim,
just within the alternative "tail" term in our 2-round accounting.

## What Berlekamp DOES improve in vanilla FRI

The improvement matters when the **leading T/|F| commit term** is the
binding constraint. This happens precisely at BORDERLINE configs:
- Small extension fields (≈ 200-bit) with large n
- Small κ relative to q_loss (binding term dominates the security)

At these borderline points, Berlekamp's log_2(c)-bit gain is the
difference between feasibility and infeasibility for NI-128.

## What Berlekamp ENABLES (beyond vanilla FRI)

The full q^{-2(c−1)} commit bound matters in protocol variants:
1. **STIR / WHIR**: per-round commit can use the q^{-c} bound directly,
   removing the T/|F| ceiling. Berlekamp's result extends to these.
2. **Multi-γ batching**: if the verifier tests against m γ's per round,
   the commit term becomes ε^m where ε is per-γ. Berlekamp's V_bad bound
   gives ε per-γ ≤ T/q (deterministic) plus q^{-2(c−1)} (V_bad event).
   At m large, the V_bad event dominates.
3. **Capacity-δ proximity proofs**: at δ approaching 1−ρ, traditional
   commit bounds break (T/|F| not tight); Berlekamp's tight q^{-2(c−1)}
   gives the sharpest published bound.

## Conclusion

D3 deliverable:
- **Quantitative**: log_2(c) bits commit gain in vanilla FRI; flips 4
  borderline rows infeasible→feasible at NI-128 at BabyBear-ext7 n=2^21.
- **Qualitative**: confirms BCIKS-tight ε_round_commit ≤ q^{-2(c−1)}
  rigorously (modulo Conjecture B, empirical 280/280). This ratifies
  ABF §6.3's commit-side claim from a fresh sequence-school direction.
- **Open**: Closing Conjecture B (Case B rigor in Note 0119) for c≥5 at
  large D. Three approaches noted there.

## Files

- `notes/scripts/op2_d3_fri_integration.py` — sweep and comparison table
- `notes/scripts/op2_d3_fri_integration.output.txt` — output (80 rows)
- `notes/0104-fri-soundness-application.md` — original 2-round framework
- `notes/0117-V_S-rigorous-codim-upper-bound.md` — codim ≤ 2(c−1) RIGOROUS
- `notes/0119-S-star-size-bound-algebraic.md` — codim ≥ 2(c−1) modulo CB
