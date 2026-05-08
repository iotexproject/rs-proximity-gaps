# Note 0395 -- Issue #419: Note 0394 3-vector lemma refuted; corrected closure scope

**Date:** 2026-05-02 (Q2 attack iteration 7 — honest refinement)  
**Branch:** `main`  
**Status:** Note 0394's "3-vector parity lemma" extension is **REFUTED**;
mixed-parity triples DO admit linear dependences at $\sim 8\%$ of no-full S.
Note 0394's "all 4-supp at $L_2=(16,4)$ closes" was OVERSTATED — only
covers side-(2,2) configurations.  This note corrects scope and identifies
the next algebraic gap.

---

## Refuted statement

Note 0394 conjectured:

> **(REFUTED).**  For every no-full $S$ and every triple
> $(r_0, r_1, r_2)$ with $r_0, r_1$ same parity AND $r_2$ opposite parity,
> the three vectors $\mathrm{HT}(t^{r_0}), \mathrm{HT}(t^{r_1}),
> \mathrm{HT}(t^{r_2})$ are linearly INDEPENDENT in $\mathbb{F}_q^{k_2}$.

Empirical refutation:

```text
notes/scripts/issue419_three_vector_parity_audit.py --q 97 --mode mixed-3
notes/scripts/issue419_three_vector_parity_audit.py --q 193 --mode mixed-3
```

At $L_2 = (16, 4)$:

```text
(8, 10, 9)  rank 2: 896 S out of 10896  (q=97 and q=193)
(8, 10, 11) rank 2: 896 S
(9, 11, 8)  rank 2: 896 S
(9, 11, 10) rank 2: 896 S
... plus several smaller dependence buckets
```

The 896-count (and prime-uniformity) shows that mixed-parity 3-vector
dependences are STRUCTURAL — they arise from the same $L_2$-arithmetic
that gives the (8,10) and (9,11) same-parity proportionalities at
128 S each.

---

## Corrected scope of Note 0394

The pairwise lemma (Note 0393) is correct and structural.  The
extension claim "all 4-supp at $L_2 = (16, 4)$ closes via pairwise" was
**overstated**.  The correct statement:

> **Corollary (corrected, side-(2,2) closure).**  Every 4-support at
> $L_2 = (16, 4)$ with **side counts $(2, 2)$** (i.e., $\leq 2$ positions
> on each $\alpha_2$ side) admitting a rank-2 nonzero-$\alpha$ saturated
> solution has each side entirely on one parity class — half-turn
> parity-split.

This still covers:
* Quadrant pattern $(1,1,1,1)$ — one position per quadrant.
* Quadrant pattern $(2,0,1,1)$ — 2 in $u$-side, 1+1 in $v$-side.
* Quadrant pattern $(1,1,2,0)$ — 1+1 in $u$-side, 2 in $v$-side
  (the catalog half-turn shape).
* Other (2,2) configurations.

The (3,1), (1,3), (4,0), (0,4) configurations require 3-vector dependence
analysis and are **NOT** covered by the pairwise lemma alone.

---

## Why the empirical 0-primitive result survives

Across the four empirical probes (Notes 0353/0365 + 0389 + 0390/0391 + 0392
= ~615M trials), zero primitives were observed even at side-(3,1) shapes.
The 3-vector dependence at $\sim 8\%$ rate of no-full $S$ DOES enable
rank-deficient $u_\alpha$ at suitable coefficients, but the additional
constraints — same-$\alpha$ on $v$ side, rank-2 $(u, v)$, trivial dyadic
stabilizer, mixed parity in BOTH rows — apparently prune away the
remaining candidates.

The structural reason for this pruning is the next concrete algebraic
question.

---

## The actual structure of the 3-vector dependences

Most of the 896-count dependences involve the same $L_2$-arithmetic
"pencils":

* $(8, 10, 9)$, $(8, 10, 11)$ at 896 S each: these are the cases where
  $\mathrm{HT}(t^8), \mathrm{HT}(t^{10})$ already span a 2-dim subspace
  (or 1-dim at the 128 S of Note 0393), and $\mathrm{HT}(t^9)$ or
  $\mathrm{HT}(t^{11})$ falls in that span.
* The dependences are not "free 3-vector relations" — they piggyback on
  the Note 0393 structural pairs.

Equivalently: the 8 high-tail vectors $\{\mathrm{HT}(t^4), \ldots,
\mathrm{HT}(t^{15})\}$ in $\mathbb{F}_q^4$ have a very specific
pencil structure governed by the $\mathbb{Z}/16\mathbb{Z}$-action on the
quotient ring $\mathbb{F}_q[t] / g_S$.

The character-theoretic decomposition (Note 0394 sketch) should make
this pencil structure explicit.  This is the next concrete algebraic
artifact.

---

## Updated closure status

| Sub-class | Status | Note |
|---|---|---|
| All-alpha | CLOSED unconditional | 0388 |
| Half-turn stabilizer | CLOSED unconditional | 0345-0351 |
| One-residue lambda lift | CLOSED | 0356-0359 |
| Same-folded cancellation | trivial | 0360 |
| **4-supp at $L_2 = (16, 4)$, side (2,2)** | **CLOSED structurally + prime-uniform** | 0393 + 0394 (corrected) |
| 4-supp at $L_2 = (16, 4)$, side (3,1) or (1,3) | OPEN structurally; empirical 0 | 0392 + 0395 (this) |
| 5+/6+/7+ supp | OPEN structurally; empirical 0 | 0392 |
| 4-supp at $L_2 = (32, 8)$ | CLOSED empirically (5k sample) | 0394 |

---

## Next concrete artifact

To close the side-(3,1) and 5+ supp branches structurally, the next
artifact must:

1. Identify which 3-vector dependences DO survive the additional
   primitive-obstruction constraints (rank-2 $(u, v)$, mixed parity in
   BOTH rows, trivial stabilizer).  Empirically: 0 across 615M trials.
2. Provide the structural reason via the character-theoretic pencil
   structure of $\{\mathrm{HT}(t^r)\}$.
3. Or: a different reduction argument (e.g., via the Action-Orbit
   theorem in the multi-position case).

The pairwise Note 0393 lemma stands as the first hand-proof component
for Q2.  Note 0394's overstated extension is corrected here.  Empirical
case for the FULL Q2 closure remains overwhelming (615M trials, 0
primitives), but the unconditional algebraic closure for the side-(3,1)
and higher-supp branches requires fresh structural work.

---

## Lesson learned

The Q2 algebraic structure has more layers than the pairwise lemma
captures.  Each apparent simplification (pairwise → 3-vector) needs
empirical verification before claiming closure.  The HONEST sequence
of Notes 0393 → 0394 → 0395 documents both the real progress (Note 0393
lemma + its proper scope at side-(2,2)) and the failed extension (the
3-vector lemma).  This is healthy iteration.
