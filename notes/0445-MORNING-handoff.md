# Note 0445 -- Morning HANDOFF: Q2 LOCAL closure status

**Date:** 2026-05-03 morning (final consolidation)
**Branch:** `main`
**Status:** Q2 LOCAL closure FULLY RIGOROUS at base $L_2 = (16, 4)$;
structurally extended to deployment $L_2 = (32, 8)$; scale-uniform Narrow
Lemma covering most configurations at all scales; remaining "wide" configs
empirical at $> 250k$ trials.

---

## 1.  Per-scale rigor table (FINAL)

| Scale $L_2$ | $k=3$ same-q | $k=4$ p(2,2) | $k=4$ p(3,1)/(1,3) | $k=5,6$ same-side | $k=7..\max$ |
|---|---|---|---|---|---|
| $(16, 4)$ | THEOREM | THEOREM | THEOREM | THEOREM | THEOREM |
| $(32, 8)$ | THEOREM | THEOREM | empirical | empirical | empirical |
| $(64, 16)$ | Narrow part THEOREM | empirical | empirical | empirical | N/A |
| $(128, 32)$ | Narrow part THEOREM | empirical | empirical | empirical | N/A |

"Narrow" = spread $D < n_2/8$ (Note 0444).

Empirical at deployment: $> 250{,}000$ trials, $0$ rank-def (Note 0441).

---

## 2.  Note family this session

**Overnight (yesterday)** — Notes 0407-0437:
- Tier 1c at L_2=(16, 4): pairwise lemma essentially field-uniform.
- HT Pencil Rigidity (Notes 0421-0423): structural, scale-uniform.
- Tier 3 supports 4-12 at L_2=(16, 4): structural with empirical atoms.

**This morning** — Notes 0438-0445:
- **0438**: Side-Row Vanishing Lemma framework (Cases A-D for k=4..12).
- **0439**: Closed-form proof of (4,8,12)/(5,9,13)/(6,10,14)/(7,11,15) rank-3.
- **0440**: Closed-form proof of same-side k-vec rank-k for k ∈ {4, 5, 6} at L_2=(16, 4).
- **0441**: Empirical scale-lift to L_2 ∈ {(32,8), (64,16), (128,32)}.
- **0442**: Structural scale-lift to L_2=(32, 8) for k=3 (all 20 triples) + k=4 parity (2,2) (all 225 configs).
- **0443**: Final tally.
- **0444**: Scale-uniform Narrow Lemma (D < n_2/8 closes at any scale).
- **0445**: This handoff.

Total: 38 new notes (0407-0445) + ~75 commits.

---

## 3.  Remaining gaps

### Gap 1: Wide $k$-vec at $L_2 \ge (32, 8)$

For $k$-vec configurations at deployment with spread $D \ge n_2/8$:
empirical only ($> 250k$ trials, 0 fail).

**Closing approach** (estimated 1-3 weeks):
- Sign-analysis with case-by-case reasoning (extended Note 0442 §3a-bis).
- Or Galois-invariance + generalized Vandermonde resultant computation.
- Or refined no-full bookkeeping per mod-(n_2/16)-class structure.

### Gap 2: Q2 GLOBAL (sparse-worst dominance)

The reduction K(general f) ≤ K(sparse f) is paper2's open
`conj:sparse-worst`. Not addressed by Tier 3 LOCAL closure.

**Closing approach**: connect via paper2's `thm:action-orbit` showing
the bad-α set has sparse-Fourier obstruction structure.

---

## 4.  paper2 v22 integration recommendations

**Drop**:
- Q2 LOCAL caveat for support sizes 4-12 at base (now THEOREM via Notes 0438-0440).

**Narrow**:
- Q2 LOCAL caveat at deployment to "wide configurations only" (Notes 0441, 0444).
- Q2 GLOBAL conjecture remains.

**New Theorems for v22**:
- Theorem 2.5: HT Pencil Rigidity, scale-uniform (Note 0423).
- Theorem 2.6: 4-supp closure, scale-uniform (Note 0423 + Note 0394).
- Theorem 2.7: All-supp closure at L_2=(16, 4) (Notes 0438-0440).
- Theorem 2.8: All-supp narrow-spread closure scale-uniform (Note 0444).
- Theorem 2.9: All-supp closure at L_2=(32, 8) for 3-vec + 4-vec parity (2,2) (Note 0442).
- Conjecture 2.10: All-supp wide-spread closure at L_2 ≥ (32, 8) (empirical >250k trials).
- Conjecture 2.11 (= old Q2 GLOBAL): sparse-worst-case dominance.

This is a substantial restructuring that significantly narrows the conditional
basis of Theorem-K10.

---

## 5.  Strategic position for prize attack

**Before this session** (paper2 v21):
- $K \le 10$ "rate-1/4 conditional on Q2 (sparse-worst-case dominance)".
- Q2 = single open conjecture.

**After this session** (paper2 v22 proposed):
- $K \le 10$ "rate-1/4 conditional on Q2 GLOBAL only + wide-config conjecture".
- Q2 LOCAL: theorem at base + structural at deployment for narrow + empirical for wide.

**Substantial narrowing of the conditional**, with the LOCAL part now
MUCH stronger than before.

For prize judges (Boneh, Fenzi, Arnon) to assess: the structural rigor
of Notes 0438-0444 is visible; the remaining empirical is at $> 250k$
trials with 0 failures.

**Recommended mobilization**:
1. **Gong (Waterloo)**: review Notes 0421-0423 (HT Pencil Rigidity) and
   Notes 0438-0444 (Side-Row Vanishing) — sequence-school perspective.
2. **Helleseth (Bergen)**: cross-correlation analogue and σ-action
   character structure.
3. **Tang Xiaohu, Cunsheng Ding cluster**: extension to non-rate-1/4
   cells and higher cyclotomic fields.

---

## 6.  Quick navigation for resumption

To continue where I left off:
1. Read STATE.md (top section) for current status.
2. Read Notes 0438-0445 in order.
3. Verify with scripts in `notes/scripts/issue419_*` (Notes 0441, 0442 outputs).

Next concrete task (if continuing tonight or tomorrow):
- **Extend Note 0442 to L_2=(32, 8) for k=5, 6**: should follow same
  framework with more case analysis.
- **Or extend to L_2=(64, 16) for k=3**: scale-lift the Note 0442 §3a-bis
  argument with refined no-full bookkeeping.

---

## 7.  Honest final assessment

The user's morning expectation was "L3 100% rigor at deployment scale".

**Achieved**:
- 100% rigor at base $L_2 = (16, 4)$ for all support sizes 4-12 (theorem).
- Structural rigor at $L_2 = (32, 8)$ for k=3 (all 20 triples) and k=4
  parity (2,2) (all 225 configs).
- Scale-uniform "narrow" rigor at all dyadic deployment cells (Note 0444).
- Empirical scale-lift at all scales: $> 250k$ trials, $0$ failures.

**Not yet achieved**:
- Full structural rigor for wide $k$-vec at $L_2 \ge (32, 8)$.
- Q2 GLOBAL closure.

**Estimate to full deployment-scale rigor**: 1-3 weeks of focused algebra
(case-by-case sign analysis at higher scales, plus Galois-Vandermonde
generalization).

**This is a substantial advance** — the Q2 LOCAL question is now
essentially solved at base, with a clear path to deployment-scale via
empirically-confirmed structural extension.
