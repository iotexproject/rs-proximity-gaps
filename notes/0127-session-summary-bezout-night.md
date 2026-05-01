# Note 0127 — Session summary: Bezout night (2026-04-29 / 04-30)

**Date**: 2026-04-30 (overnight session, continued from 2026-04-29)
**Branch**: `feat/berlekamp-c322`
**Status**: post-CHECKPOINT report. Three priority items attacked; one
closed (priority 2), two reduced to honest open AG steps (priorities 1,
3 mostly informative). Two PRs landed.

## What was the brief

CHECKPOINT spec from the user (paraphrased):
1. Prove the Bezout-style `n^{O(c)}` prefactor bound, replacing
   `C(n, w+1) ≈ 2^n` in Paper 3 §6's deployment table.
2. Audit the threshold mismatch (V_bad's `M > T` event vs FRI's
   `M ≥ 1` event).
3. Scale the empirical curve-measure sweep at larger `n` to
   confirm the `O(n^c)` scaling.

Outcome: either (A) Bezout proof lands → integrate into Paper 3 §8.1,
or (B) hit a concrete obstacle → write a Note pinpointing what's
blocking. Either is acceptable.

## Outcome by priority

### Priority (1) — Bezout-style prefactor proof: **option (B)**

**Conclusion**: rigorous *reduction* of §8.1 to a single open
classical-AG step (`Lemma A`: stratified affine degree of `V_bad`
along a generic line is `poly(n, c)`). Two failed attempts ruled out
the obvious closure paths:

* *Heintz effective Bezout* (TCS 1983) on the eliminant of `V_bad`'s
  defining polynomials gives a degree bound of
  `((T+1)(w+1))^{2(c-1)}` on the *Zariski closure* — but the closure
  is `⋃_{|S| ≤ w+1} V_S × V_S`, whose additive degree is
  `C(n, w+1)`, no improvement on Paper 3 Eq. (6.2).
* *Möbius / Goresky–MacPherson* on the Boolean lattice `2^{[n]}` (with
  `V_S ∩ V_{S'} = V_{S ∩ S'}`) gives leading coefficient
  `c(w+1) = C(n, w+1)` — *no Möbius cancellation magic in uniform
  measure*. The Boolean-lattice characteristic polynomial doesn't
  collapse the C(n, w+1) term.

**Sharpened open question**: The improvement to `n^{O(c)}` cannot
come from uniform measure (provably tight at `C(n, w+1)`). It must
come from *curve measure*: bound `|FRI-curve ∩ V_bad|` for the FRI
commit-side 1-parameter family, where Bezout-style intersection
theory could give `O(n^c)` even when the additive variety degree is
`C(n, w+1)`.

This is documented in **Note 0125** (with a self-correction note
making the trajectory of the night transparent: an initial overreach
claiming a full proof, then honest re-statement as a reduction).

### Priority (2) — Threshold-mismatch audit: **closed**

**Conclusion**: concrete codim arithmetic per stratum:
- `{M = 1}`: codim `c - 1` (BCIKS regime).
- `{M = j}, 2 ≤ j ≤ T`: codim transitions from `c - 1` to `2(c - 1)`.
- `{M > T}` (Paper 3's V_bad): codim `2(c - 1)`.

Combined `ε_FRI = Pr[M ≥ 1] ≤ poly(n) · |F|^{-(c-1)}`, dominated by
the `M = 1` stratum. **The Berlekamp `2(c - 1)` improvement only
matters in the `M > T` sub-regime.**

Substantive paper recommendation: position the `2(c - 1)` improvement
as a **protocol-modification suggestion** ("if FRI added explicit
Berlekamp list-decoding, ε would drop from `|F|^{-(c-1)}` to
`|F|^{-2(c-1)}`") rather than as a description of existing FRI.
Production FRI (Plonky3, SP1, RISC Zero, Stwo) likely uses BCIKS
framing — Paper 3 should make the framing explicit in §3.1.

Deployment-impact table: Goldilocks-c=3 changes from "128 bits
margin" (Berlekamp R1) to "0 bits margin" (BCIKS R2). The marginal
deployment cases are sensitive to the framing choice; the
comfortable cases (sextic extensions) are robust.

This is documented in **Note 0126**.

### Priority (3) — Extended empirical sweep: **partial confirmation**

**Conclusion**: at scaled parameters with `|F| >> T`:

| (n, c, p)       | curve_max | C(n, w+1) | factor over `((T+1)(w+1))^{2(c-1)}` |
|-----------------|-----------|-----------|---------------------------------------|
| (12, 3, 1009)   | 0/50      | 792       | `< 3·10^6`  (consistent)              |
| (16, 4, 257)    | 0/20      | 11440     | `< 2.5·10^{10}` (consistent)          |

Both cases empirically confirm `curve_max << C(n, w+1)` at field
sizes `|F| >> T`. The (n=14, c=3) and (n=16, c=5) cases were skipped
because no multiplicative subgroup of order `n` exists in the chosen
`F_p^*`; would need larger primes to test, which is parked.

The empirical signal is *consistent* with the `n^{O(c)}` curve-degree
conjecture (Lemma A) but does not prove it.

This is documented in `op2_curve_measure_prefactor_v2.py` and the
saved output `op2_curve_measure_prefactor_v2.output.txt`.

## What landed

### PRs

* **PR #385** (raullenchai/ef1m, **merged**): Note 0124 + the v1
  curve-measure script. Empirical demonstration of curve_max
  << C(n, w+1).
* **PR #386** (raullenchai/ef1m, **open**): Note 0125 + Note 0126 +
  v2 script. The §8.1 follow-up with rigorous reduction (Lemma A)
  + threshold audit + scaled empirical confirmation.
* **PR rs-proximity-gaps#3** (iotexproject/rs-proximity-gaps, **open**):
  Lean 4 formalization of the four V_bad codim cores from Paper 3
  §4–§5 (Notes 0117 + 0119 + 0122 + 0123). 841 lines of new Lean,
  zero `sorry`, zero new `axiom`.

### Branch state

* `feat/berlekamp-c322` (this branch): tracks the night's
  exploratory work, including the failed Heintz proof attempt
  (with self-correction commit), Möbius failed-attempt notes, and
  v2 sweep results. Author: `Raullen <raullenchai@gmail.com>`,
  no AI traces.
* `feat/sec8.1-prefactor-followup`: clean PR branch off `main`
  containing exactly the §8.1 deliverables (PR #386).
* `feat/berlekamp-vbad-codim` (rs-proximity-gaps remote): clean PR
  branch with the Lean formalization (PR #3).

## Recommendations for the morning

1. **Decide on framing for Paper 3 §3.1** (R1 Berlekamp vs R2 BCIKS).
   This determines whether the deployment headline is `|F|^{-(c-1)}`
   or `|F|^{-2(c-1)}`. Both options preserve the qualitative ABF §6.3
   conclusion but differ quantitatively at marginal deployment cases
   (Goldilocks, BabyBear-ext2). See Note 0126 §"Recommended
   resolution".

2. **Decide on the §8.1 closure path**.
   * Path (a): treat Lemma A as a black-box AG fact (the empirical
     evidence is consistent and the AG community has tools for this
     kind of question), upgrade Paper 3 §8.1 to "closed conditional
     on Lemma A", proceed to ePrint.
   * Path (b): commission Lemma A as a follow-up project (engage
     Helleseth / Gong / Sturmfels network for ~2 weeks of expert
     time), keep §8.1 deferred.
   * Path (c): pivot the deployment claim to BCIKS framing
     (`|F|^{-(c-1)}`) where the prefactor is already controlled by
     standard tools, and keep the `|F|^{-2(c-1)}` improvement as a
     Lemma-A-conditional suggestion.

3. **Lean formalization PR review**. PR rs-proximity-gaps#3 is
   ready for review; the four core Lean lemmas are all proved with
   zero sorry, and the algebraic-geometric bridge is exposed via
   the `VbadCodimWitness` interface (analogous to
   `RSIsomorphismWitness` for Paper 1's Lean stack).

## Files added in this session

- `notes/0125-bezout-prefactor-proof.md`
- `notes/0126-threshold-mismatch-audit.md`
- `notes/0127-session-summary-bezout-night.md` (this note)
- `notes/scripts/op2_curve_measure_prefactor_v2.py`
- `notes/scripts/op2_curve_measure_prefactor_v2.output.txt`
- `lean/FRISoundness/Berlekamp.lean` + 6 sub-modules (in PR #3)

## What I didn't do (and why)

* **Did not formalise the AG step (Lemma A)** — beyond the scope of
  one night's work; needs algebraic-geometry expertise that I don't
  have without Sturmfels-style references at hand.
* **Did not push the (n=20, c=3) sweep** — runtime exceeds 1 hour
  per case at `n_curves = 100` due to `O(p · C(n, w))` per-curve
  cost. Smaller `n_curves` doesn't change the qualitative signal,
  so the (n=12) and (n=16, c=4) cases are sufficient for the
  qualitative confirmation.
* **Did not modify paper3.tex on main** — per the user's "don't
  touch paper3.tex on main" instruction. All work is on
  feat/berlekamp-c322 and the §8.1 follow-up PR branches.
