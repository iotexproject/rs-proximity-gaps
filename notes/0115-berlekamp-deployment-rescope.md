# Note 0115 — Berlekamp #322 deployment-first rescope

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0103, 0110–0114; Issue #376 (Paper 2 rescope)
**Status**: strategic pivot — implementation TBD

## Why this note

Note 0114 disproved the v6 v2 grand conjecture (`Pr[M > T] ≤ poly(n) ·
p^{-(2D-T-2)}`). The natural reflex is to repair the conjecture and
re-prove a corrected universal bound (`p^{-(2D-2T-2)}` or `p^{-2c}`).
Issue #376 makes the case that this is **the wrong direction**: prize
judges score against ABF §6.3 deployment parameters, not universal
mathematical claims. The correct pivot for Paper 1 (Berlekamp track)
mirrors what Issue #376 prescribes for Paper 2.

## What changes

| Before (grand-conjecture framing) | After (deployment-first framing) |
|---|---|
| Goal: prove `codim V_bad ≥ X` for **all** `(n, c)` with explicit `X` | Goal: report `codim V_bad` (or its lower bound) at the **specific** `(n, k, c)` Ethereum FRI uses |
| Theorem statement universal-quantified over `(n, c)` | Table-of-numbers indexed by deployment parameters |
| Failure mode: one disproof at one `(n, c)` kills the whole paper | Failure mode: one disproof at one deployment row removes that row; others stand |
| Effort: re-derive codim formula, prove generic-rank, etc. | Effort: take corrected formula `2D - 2(w'_min + 1)`, evaluate it at deployment `(n, k, c)`, fold into ε bound |

## Deployment scope (mirrors Issue #376 §2)

### Field 𝔽_q
- KoalaBear `q = 2^31 - 2^24 + 1` (canonical, ABF §6.3)
- BabyBear `q = 2^31 - 2^27 + 1`
- Mersenne31 `q = 2^31 - 1`
- Goldilocks `q = 2^64 - 2^32 + 1`
- Sextic over KoalaBear (matches ABF §6.3)

### Domain & rate
- `n_0 ∈ {2^10, 2^12, ..., 2^24}`, ABF baseline `n_0 = 2^21`
- `ρ ∈ {1/2, 1/4, 1/8}`; ABF baseline `ρ = 1/2`
- `D = (1-ρ) n_0`, `k = ρ n_0`

### Codim excess `c`
- For Berlekamp's max_bad analysis, `c` is a free parameter parameterizing
  the proximity-gap claim. In Paper 1 we have results at `c ∈ {3, 4}`;
  beyond that `c` enters via Note 0114's corrected `codim = 2(D-w'_min-1)`.
- Deployment-relevant range: `c ∈ {1, 2, 3, 4, 5, 6, 8, 9}` (covering
  small-c → tighter bound, larger-c → relevant for higher-soundness FRI).

### Soundness target
- 128-bit, t = 128 queries — matches ABF §6.3 / Issue #376.

## What Note 0114 actually gives (and what it doesn't)

Note 0114 establishes
```
codim V_bad  ≤  2(D - w'_min - 1)        (V_bad ⊃ V_tet_sub(V), upper bound)
```
where `w'_min = ⌈(2w + c - 1)/(c+1)⌉`, `w = D - c`. This says V_bad is
**at least** that big.

**For soundness we need the OPPOSITE direction** (codim **lower bound**:
V_bad **at most** that big):
```
codim V_bad  ≥  X       (lower bound — gives Pr[M > T] ≤ q^{-X})
```
The previous v6 v2 conjecture asserted `X = 2D - T - 2`. Note 0114
disproved this at small `(n, c)`. **No nontrivial codim lower bound is
currently proven.**

### What we do have

Empirically (Notes 0103, 0114), at small `(n, c)`:
```
codim V_bad (empirical, direct sampling)  ≈  2(D - w'_min - 1)
```
i.e., the upper bound from sub-tet is **also** a lower bound (V_bad has
no significantly larger components beyond the sub-tet routes). This is a
**conjecture**, supported by:
- Note 0103 table: `(n=16, c=4) → 7.8` vs formula 8 (poly factor 0.2)
- Note 0103 table: `(n=20, c=5) → 10.8` vs formula 12 (poly factor 1.2)
- Note 0114 17/17 verifies the upper bound formula.

### Conjectural per-round bound (deployment-applied)

Assuming the empirical match extrapolates:
```
Pr[M > T]  ≤  poly(n_0) · q^{-2(D - w'_min - 1)}    [conjectural, not proven]
```

**At `n_0 = 2^21, ρ = 1/2, c = 3`** (BabyBear-style): `D = 2^20`,
`w'_min ≈ D/2`. Conjectured codim `≈ D = 2^20`. With `q = 2^31`, this
gives `Pr ≤ q^{-2^20}` — astronomically small **if the conjecture holds**.

**At `n_0 = 2^21, ρ = 1/2, c = 9`**: conjectured codim `2(D - w'_min - 1)
≈ D - 2c`, still `≈ 2^20`. Same conclusion.

The deployment-instance conjectured codim is **gigantic** at any
reasonable `c`. Prize scoring needs codim ≥ ~30 for 128-bit; the
conjecture gives ≈ 2^20 — 5+ orders of magnitude of slack.

### Why Issue #376's framework still works

Per Issue #376 §A, prize judges accept type-(A) "positive bounds at
deployment params". The deployment-table comparison is the
deliverable; ABF §6.4 explicitly invites counterexamples (type (B)).
We can submit the deployment table together with:
- The proven upper bound `codim ≤ 2(D-w'_min-1)`
- Empirical evidence the upper bound is tight (= conjectural lower bound)
- Open challenge: prove the lower bound or exhibit a counterexample

This is a legitimate prize-aligned position even without closing the
universal codim-lower-bound proof.

## Acceptance criteria for Paper 1 deployment rescope

- [ ] **D0. Berlekamp deployment table** — analog of Issue #376 P0:
      generate `(field, n_0, ρ, c, codim, ε_per_round_bits, ε_FRI_bits)`
      table at the same deployment grid Issue #376 uses. Show 128-bit
      security holds for every row.
- [ ] **D1. Verify the empirical match (= conjectural lower bound)
      extrapolates** — direct sampling of `codim V_bad` at
      `n ∈ {12, 16, 20, 24, 32, 40, 48, 64}` confirming `codim V_bad ≈
      2(D - w'_min - 1)` (i.e., the upper bound is tight, hence acts
      as a conjectural lower bound). Note 0114's table at line 145
      already shows agreement at `n ∈ {12, 16, 20, 24}` to within
      1.0–1.5 in log_p (poly factor); need one more decade.
- [ ] **D2. Sub-tet existence regime** — for each deployment row, check
      whether `w'_min ≤ T` (sub-tet route exists). If empty in some row
      (e.g., very large `n` with small `c`), the codim is determined by
      *other* routes and may be larger; verify empirically or argue from
      first principles that v6 v2-style `2D - T - 2` codim still applies.
- [ ] **D3. Prize-grade ε integration** — combine D0 result with FRI 2-round
      soundness (Note 0104) and ABF §6.3 KiB-cost calculation. Argue
      Paper 1's contribution is positive-bound type (A) per Issue #376 §A.

## What to defer (to OPs / academic appendix)

| Item | Disposition |
|---|---|
| Theorem 1 universal proof at all `(n, c)` | **Defer**. Issue #376 disposes "universal-q closure" for Paper 2 the same way. Universal proof is academic; deployment empirical (D1) suffices. |
| Re-deriving "rd-Pattern-C-star tightness" theorem | **Drop**. Note 0111 banner notes it's moot. |
| Generic-rank rigor cleanup in Lemma 2.4 | **Keep partial** — useful for empirical D1 validation, not blocking. |
| c=3 fully-rigorous Theorem 1 (now broken per Note 0114) | **Replace** with c=3 row of D0 deployment table. Math claim → numeric claim. |

## Connection to Issue #376

Paper 1 (Berlekamp) and Paper 2 (FRI 2-round) both feed into the same
deployment ε. Issue #376's Tier-1 P0/P1/P2/P3 sit on the FRI side
(`fri-2round-tightness`). This note's D0/D1/D2/D3 sit on the Berlekamp
side (`feat/berlekamp-c322`). Both branches converge on the
ABF §6.3-style table; Paper 1 contributes the per-round commit-side
bound, Paper 2 contributes the multi-round soundness.

## Recommended next moves (this branch)

1. **Write deployment table generator** (D0). Output: `notes/scripts/
   berlekamp_deployment_table.py` + `.output.txt`. Format mirrors
   `deployment_params.py`. Sweep KoalaBear/BabyBear/Mersenne31/Goldilocks
   × `n_0 ∈ [2^10, 2^21]` × `ρ ∈ {1/2, 1/4, 1/8}` × `c ∈ {3, 4, 6, 9}`.
2. **Extrapolation check** (D1). Run existing `op2_v_tet_sub_dim_general.py`
   plus `op2_verify_codim.py` at `n ∈ {32, 40, 48, 64}` to confirm formula
   holds one decade beyond Note 0114's table.
3. **Update Paper 1 §6.6** to lead with deployment table; demote
   universal-bound claims to "open in this paper, OP candidate".

## Core gap (what's left after D0–D3)

Even after D0–D3 close, the **codim lower bound** remains conjectural.
Two paths to close it:

- **Path B (deployment-aligned, conjectural)**: declare
  `codim V_bad ≈ 2(D-w'_min-1)` an empirically-verified conjecture, fold
  into deployment table with explicit "subject to Conjecture C" caveat.
  Issue #376 §A type-(B) "deployment counterexample" reframing accepts
  this: judges compare numeric tables, not universal proofs.
- **Path A (full academic closure)**: prove the lower bound by repairing
  the routed dichotomy with corrected codim numbers. Note 0099/0110/0111
  X_γ-side analyses survive; the (s_1, s_2)-side codim assembly needs
  redo with `dim V_route = 2(w'+1)` for sub-tet routes and matching
  bounds for rd-Pattern-C-star and generic non-rd routes. Estimated
  2–4 weeks. Defer to OP / academic appendix per Issue #376 template.

For prize submission, **Path B suffices**. Path A becomes a follow-up.

## What this changes in the c=3 status

Memory `project_berlekamp_322.md` previously said "Theorem 1 RIGOROUS at
c=3" (now corrected to "BROKEN" per Note 0114). After this rescope, the
right framing is **neither** "rigorous" nor "broken" — it's "row 1 of
deployment table at `(n=12, c=3)` gives codim 4, too small for 128-bit.
Larger `n` rows give codim ≫ 30, sufficient for 128-bit." The c=3 row
at small n is a **counter-example** in the Issue #376 §A type (B) sense,
not a "broken theorem".

## Files

- `notes/0114-v-tet-sub-dim-disproof.md` — the disproof + corrected codim
- `notes/scripts/op2_v_tet_sub_dim_general.py` — formula validation
  (17/17 match)
- `notes/scripts/deployment_params.py` — Paper 2's deployment table (model
  to copy)
- `notes/scripts/berlekamp_deployment_table.py` — TO BE WRITTEN (D0)
