# Note 0514 — Q2 GLOBAL drill: final synthesis (Notes 0504-0513)

**Date:** 2026-05-05 (Q2 drill iter 37, post Note 0513 resolution)
**Status:** **Q2 GLOBAL drill complete**. paper2 v24 §7.5 deployed with K_1 ≤ 3 RIGOROUS theorem. K_2 ≤ 7 conjecture remains open structurally but is now well-characterized empirically.

## The 10-note arc

| # | Note | Content | Status |
|---|---|---|---|
| 0504 | K_1 universal budget | $K_1 \leq 3$ RIGOROUS via universal budget identity | ✅ THEOREM |
| 0505 | K_2 attack — Helleseth + Gong consult | vLW (D_α) + WG (resultant Φ) approaches | identified |
| 0506 | paper2 v24 update proposal | Decompose Q2 = K_1 + K_2; concrete LaTeX edits | proposal |
| 0507 | Helleseth |D_α| ≥ 4 REFUTED | At (8,2): 17.4% witnesses have |D_α| = 0 | dead end |
| 0508 | K_2 ≤ 7 verified at (16,4) | Brute force F_17 confirms margin | ✅ empirical |
| 0509 | Gong resultant tested | deg Φ = 14 (not ≤ 7); K_1 ≤ rat.map.deg insight | partial |
| 0510 | K_2 = 7 saturation found | At (4,6,8) and (6,10,14) | empirical |
| 0511 | K_2 = q-1 saturation correction | Some supports give K_2 = 16 | concern |
| 0512 | Saturation Δ_joint(to 0) = 1 caution | Suggests strict above-J | concern |
| 0513 | RESOLVED: max d(f_i,C) ≤ Johnson boundary | Saturating cases NOT strict above-J | ✅ closed |

## paper2 v24 patch (committed)

**commit 2ee9d35** + LaTeX fix in **e1a20df**:
- New §7.5 `ssec:K1-universal-budget` (lines 2926-3030)
- New `thm:K1-universal-budget`: $K_1 \leq 3$ unconditional for above-J pairs
- 3-lemma proof (~half page): universal budget identity + saturation pigeonhole + above-J implies |T| < n_0/2
- 2 supporting remarks
- §sec:open Q2 paragraph updated with K = K_1 + K_2 decomposition
- §1.4 Layer 3 status table: row 3a' added for K_1 RIGOROUS

## Strategic Q2 GLOBAL position (FINAL)

paper2 §7 Conjecture~\ref{conj:sparse-worst} (Q2 GLOBAL):
$$\max_{\text{action-non-stab strict above-J}} K(f_1, f_2; \delta) = \max_{\text{3-pos sparse}} K = 10.$$

**Decomposition** $K = K_1 + K_2$:
- **$K_1 \leq 3$** for ANY above-J pair: **RIGOROUS** (paper2 v24 Theorem K1-universal-budget).
- **$K_2 \leq 7$** for action-non-stab strict above-J pairs at deployment scale: **CONJECTURED** with overwhelming empirical evidence:
  - 4.6M support-prime certificates at (32, 8) over q ∈ {97, 193, 257}: 0 cex
  - 615M-trial deployment-scale empirical: 0 cex
  - Brute-force at (16, 4)/F_17 across all 220 3-pos supports: K_2 ≤ 7 at strict above-J pairs (saturating cases all in Johnson boundary, EXCLUDED)

## Critical insights from drill

1. **K_1 ≤ 3 generalizes Note 0471's K_1 ≤ 2** (which was specific to stratum (B) cross-side K=16 lifted from L_2). The universal version drops the lift/stratum hypothesis at the cost of constant 3 vs 2.

2. **vLW approach (Helleseth) DEAD**: |D_α| can be 0 for dense pairs; pigeonhole bound K_2 ≤ (n-k)/r doesn't apply.

3. **WG approach (Gong) more nuanced**: deg of resultant Φ is large (~14 at (16,4)); the relevant bound is on rat.map.deg or "coincidences", not deg Φ directly.

4. **K_2 saturation phenomenon**:
   - K_2 = 7 occurs for "sparse-shared AP" supports at strict above-J — matches conjecture margin EXACTLY.
   - K_2 = q-1 saturation occurs for Johnson boundary (NOT strict above-J), excluded by conjecture.
   - Conjecture's strict-above-J condition is ESSENTIAL.

5. **paper2 v24 conjecture is CALIBRATED CORRECTLY**: cannot be improved to K ≤ 9, K ≤ 10 is tight margin (with K_1 ≤ 3 + K_2 ≤ 7 saturating).

## Open structural problem

**Prove K_2 ≤ 7 for action-non-stab strict above-J pairs at deployment scale (32, 8)+.**

Estimated timeline (per Helleseth + Gong consults, Note 0505): 1-3 months focused work.

Promising approaches:
- **Refined Gong/WG resultant** with cyclotomic mod-4 chop calibrated for non-mod-4-symmetric supports (Note 0509 partial).
- **Action-stab classification via fold-quadrant analysis** to separate K=q saturating cases from action-non-stab K ≤ 7 cases.
- **Sequence-school cluster mobilization** (Tang Xiaohu, Cunsheng Ding) per paper2 v24 §sec:open Q2 paragraph.

## Recommended next moves

1. **Compile paper2 v24 PDF on studio** (laptop has no LaTeX). Verify §7.5 typesetting.

2. **Push paper2 v24 to GitHub PR** for codex review:
   - `git push origin main` (if user agrees) OR
   - Create branch `paper2-v24-K1-universal-budget` + PR
   - Trigger codex/colleague review

3. **Update STATE.md** to reflect Q2 drill complete (already done in 1ca1208).

4. **Issue tracker**: open Issue #441 "Prove K_2 ≤ 7 structurally for action-non-stab" with full attack plan from Note 0505 + lessons from Notes 0507/0509/0513.

5. **paper2 §sec:open Q2 paragraph** (already updated): emphasize K_2 ≤ 7 reduction as "named open structural problem" similar to Q1's reduction to K_0 class field NT problem.

## Empirical artifacts (for companion repo)

Scripts in `notes/scripts/`:
- `g3_K1_universal_bound_check.py` — Note 0504 K_1 ≤ 3 verification
- `g3_K2_brute_force_n8k2.py` — Note 0507 (8,2) brute force
- `g3_K2_full_support_n16k4.py` — Note 0508 full-support (16,4)
- `g3_K2_resultant_phi.py` — Note 0509 Gong resultant
- `g3_K2_specific_pencil_brute.py` — Note 0509 pencil-specific
- `g3_K2_strategic_supports.py` — Note 0510 strategic AP sweep
- `g3_K2_structural_sweep.py` — Note 0511 full 220-support sweep
- `g3_K2_max_16_classify.py` — Note 0511 K=q-1 classification
- `g3_K2_saturating_above_J_check.py` — Note 0513 above-J resolution

## Q2 GLOBAL drill: deliverables summary

| Deliverable | Status |
|---|---|
| K_1 ≤ 3 RIGOROUS theorem | ✅ paper2 v24 §7.5 |
| paper2 v24 patch | ✅ commit 2ee9d35 + e1a20df |
| Empirical K_2 verification at (16,4) | ✅ Notes 0508, 0510 |
| K_2 saturation question resolved | ✅ Note 0513 (Johnson boundary) |
| Subagent expert consults (Helleseth + Gong) | ✅ Notes 0505, 0509 |
| Strategic synthesis | ✅ This note |
| K_2 ≤ 7 structural proof | ⏸ OPEN (1-3 mo) |
| paper2 v24 PDF compile + review | ⏸ PENDING (user / studio) |
| GitHub PR for paper2 v24 | ⏸ PENDING (user decision) |

## Bottom line for user

**paper2 §7 Q2 GLOBAL position substantially strengthened**:
- Was: "K ≤ 10 fully conditional on Q2 conjecture"
- Now: "K_1 ≤ 3 unconditional + K_2 ≤ 7 conjectured with brute-force + 4.6M cert + 615M trial empirical evidence"

The **K_1 contribution is rigorous and uncontroversial**. The **K_2 conjecture statement is empirically well-supported and structurally well-defined** (with explicit characterization of Johnson-boundary edge cases excluded by strict above-J).

This is the largest improvement to Q2 GLOBAL since Note 0502 killed Conjecture A in iter 26.
