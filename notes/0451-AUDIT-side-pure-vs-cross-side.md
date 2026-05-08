# Note 0451 -- AUDIT: Side-pure vs Cross-side, and what L3 closure actually needs

**Date:** 2026-05-03 evening (after targeted construction reveals subtle issue)
**Branch:** `main`
**Status:** Clarification of what "L3 100% structural" actually requires.
Re-categorization of Notes 0438-0450 by side-pure vs cross-side.

---

## 1.  The conceptual distinction

For an obstruction polynomial $f(t)$ at $L_2 = (n_2, n_2/4)$ with high-tail
support $\mathrm{supp}(f) \subset \{n_2/4, \ldots, n_2 - 1\}$:

- **Side-pure**: $\mathrm{supp}(f) \subset $ u-side ($r \bmod 4 \in \{0, 1\}$)
  OR $\mathrm{supp}(f) \subset $ v-side ($r \bmod 4 \in \{2, 3\}$).
- **Cross-side**: $\mathrm{supp}(f)$ has elements in BOTH u-side AND v-side.

paper2's `thm:no-full-base-closure` states: every saturated no-full
candidate is either zero-row OR side-pure (rank $\le 1$).  Side-pure
configurations are automatically excluded from primitive rank-2.

**Therefore**: only cross-side configurations need new structural analysis
for Q2 LOCAL closure.

---

## 2.  Targeted construction reveals the issue

Script `issue419_k6_sameq_targeted.py` constructs a no-full $S$ at $L_2 = (32, 8)$
where the 6-vec same-q-class (q=0 evens at $\{8, 12, 16, 20, 24, 28\}$) has
**rank 5**, not 6.  Specifically:

```
S = {0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 24}
mod-8 distribution: {0: 4, 4: 3, 1: 3, 2: 3, 3: 3}
mod-4 distribution: {0: 7, 1: 3, 2: 3, 3: 3}  (no-full ✓)
6-vec rank: 5/6 across q ∈ {97, 193, 257}
```

This contradicts the naive reading of "Side-Row Vanishing Lemma for $k=6$
same-side at $L_2 = (32, 8)$" (Notes 0438, 0442, 0450 §3a).

**But this is NOT a counter-example to Q2 LOCAL.**  The 6-vec polynomial is
side-pure (all u-side q=0), so paper2's `thm:no-full-base-closure` gives
rank $\le 1$ in the W(α) sense — not primitive rank-2.

The empirical scan in Note 0450 ("0 rank-def at 1200 trials") was
**undersampling**: random no-full $S$ rarely concentrates mod-8 distribution
narrowly enough to give rank-def, but constructed $S$ does.

---

## 3.  Re-categorization of Notes 0438-0450

| Note | Configuration | Side-pure or Cross-side? | Status post-audit |
|---|---|---|---|
| 0438 | "Side-Row Vanishing Lemma" same-side $k$-vec | **Side-pure** | Auto-covered by paper2 (the lemma is bonus, not required) |
| 0439 | q-restricted same-parity 3-vec at $L_2=(16,4)$ | **Side-pure** | Auto-covered |
| 0440 | same-side $k$-vec rank $k$ at $L_2=(16,4)$ | **Side-pure** | Auto-covered |
| 0442 | k=3 same-q-class + k=4 parity (2,2) at $L_2=(32,8)$ same-side | **Side-pure** | Auto-covered (lemma still proves rank=k bonus) |
| 0444 | Narrow Lemma (D < n_2/8) | **Side-pure** | Auto-covered |
| 0446 | k=5 parity (3,2)/(2,3) same-side at $L_2=(32,8)$ | **Side-pure** | Auto-covered |
| 0447-0448 | k=12 joint u/v rank-def at $L_2=(32,8)$ | **Cross-side (joint)** | (1+ct²) extension closure (Note 0448) — **GENUINE structural contribution** |
| 0449 | parity (k-1, 1)/(1, k-1) within same-side | **Side-pure** | Auto-covered (lemma is bonus) |
| 0450 | k=6 (3,3) same-side, same-q-class various | **Side-pure** | Auto-covered (empirical was misleading, but moot) |

**Net structural contribution to Q2 LOCAL** (beyond paper2's `thm:no-full-base-closure`):
- Note 0448's $(1 + ct^2)$ trivial extension argument for joint u/v k=12 → primitive rank-2 exclusion.

The bulk of Notes 0438-0440, 0442, 0444, 0446, 0449, 0450 prove
**stronger statements** than paper2 needs (specifically: same-side rank=k
where applicable), but these are **bonus**, not load-bearing for Q2 LOCAL.

---

## 4.  What L3 100% structural closure ACTUALLY requires

**Cross-side configurations at $L_2 = (32, 8)$**, for all support sizes $K = 2$
through $24$:

| $K$ | Cross-side parity $(n_u, n_v)$ | Configurations | Coverage |
|---|---|---|---|
| 2 | (1, 1) | $12 \times 12 = 144$ | ? |
| 3 | (1, 2), (2, 1) | $\sim 1500$ | ? |
| 4 | (1, 3), (2, 2), (3, 1) | $\sim 4000$ | Note 0394 (?), Note 0432 (?) |
| 5 | (1, 4), (2, 3), (3, 2), (4, 1) | $\sim 5000$ | ? |
| 6 | (1, 5), (2, 4), (3, 3), (4, 2), (5, 1) | $\sim 8000$ | Note 0432 §1 (1536 cases) |
| 7 | ... | ... | ? |
| 8 | side-(4,4) parity-(2,2) etc. | $\sim 12000$ | Note 0394, 0435 (partial) |
| ... | ... | ... | ... |
| 24 | (12, 12) full high-tail | 1 | **Note 0448 ✓** |

**Genuine remaining structural gaps**: cross-side $K = 2, 3, 4, 5, 6, 7, ..., 23$
configurations not yet covered.

Existing partial structural coverage:
- Note 0432: cross-side 6-supp 1536-case (specific decomposition).
- Note 0394: side-(2,2) closure (K=4 cross-side).
- Note 0435: 8-supp side-(4,4) parity-(2,2) (K=8 cross-side, specific).

---

## 5.  Honest current L3 status

**STRUCTURAL** (genuine cross-side closures):
- $K = 24$ full high-tail: Note 0448 (1+ct²) extension.
- $K = 4$ side-(2,2): Note 0394.
- $K = 6$ specific 1536-case: Note 0432.
- $K = 8$ side-(4,4) parity-(2,2): Note 0435 (partial).

**EMPIRICAL** (cross-side, paper2's 4.6M certs cover):
- $K = 2, 3, 5, 7, 9, 10, 11, 13-23$ cross-side.
- $K = 4$ cross-side parities other than (2,2).
- $K = 6$ cross-side parities other than the 1536-case.
- $K = 8$ cross-side parities other than (4,4) (2,2).

**Side-pure** (auto-covered by paper2's `thm:no-full-base-closure`):
- ALL same-side configurations at any $K$ — no new structural work needed.

---

## 6.  Path forward to TRUE L3 100% structural

For Q2 LOCAL closure at $L_2 = (32, 8)$, structurally close ALL cross-side
configurations.  Approach:

1. **Generalize Note 0448's $(1+ct^2)$ extension argument**: applies to any
   cross-side configuration where v-side kernel = +2 shift of u-side kernel.

2. **Generalize Note 0432's structural framework**: for cross-side with
   small support ($K \le 6$), the side-(2,2)-style decomposition usually
   gives closure via Vandermonde / sign-relation arguments.

3. **Pencil-rigidity arguments (Notes 0421-0423, 0438)**: HT pencil
   rigidity gives strong constraints on (u_α, v_α) cross-side structure.

4. **Action-orbit decomposition**: σ-action on cross-side configurations
   yields orbit-decomposition theorems.

Estimated effort: **2-5 days of focused analysis** for all cross-side $K$.

---

## 7.  Strategic recommendation

Given the complexity, **incremental approach**:

**Phase 1 (1 day)**: Audit all cross-side configurations at $L_2 = (32, 8)$,
classify by structural coverage (Note 0432 / 0394 / 0435 / new) vs empirical.
Identify the smallest-K gaps first.

**Phase 2 (1-2 days)**: Close $K = 2, 3, 4$ cross-side via direct algebra
(small support, few configurations).  These should be tractable.

**Phase 3 (1-2 days)**: Close $K = 5, 6, 7, 8$ cross-side via Vandermonde /
pencil-rigidity arguments.  Note 0432 already does $K=6$ partial.

**Phase 4 (1 day)**: $K \ge 9$ cross-side via inductive scheme + Note 0448
$(1+ct^2)$ generalization.

**Phase 5 (0.5 day)**: Write up unified Note 0452 documenting full L3
structural closure.

---

## 8.  Files

* This Note: `0451-AUDIT-side-pure-vs-cross-side.md`
* Targeted construction script: `issue419_k6_sameq_targeted.py`
* Same-q-class enumeration: `issue419_k6_sameq_enumerate.py`

---

## 9.  Lesson learned

**Empirical scans over random no-full $S$ undersample edge cases.**  The
Note 0450 scan found 0 rank-def at 226k trials, but constructed $S$ shows
rank-def DOES occur.

For **all future structural claims**: use targeted constructions or
exhaustive enumeration over polynomial coefficient space + S-space, NOT
random sampling alone.

The good news: side-pure rank-defs (which random scans miss) are
**already covered by paper2's `thm:no-full-base-closure`**, so the
undersampling doesn't change Q2 LOCAL conclusions for side-pure cases.
But it does mean the morning's "Side-Row Vanishing for k ≤ 11" claim was
overstated for $L_2 = (32, 8)$.
