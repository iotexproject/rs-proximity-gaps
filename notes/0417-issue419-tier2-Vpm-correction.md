# Note 0417 -- Issue #419: Correction to Note 0416 — V_± decomposition does NOT close side-(3,1) directly

**Date:** 2026-05-02 late night (Tier 2 framing iteration 3 — honest correction)
**Branch:** `main`
**Status:** **CORRECTION** to Note 0416's §3 closure claim.  The σ-isotypic
$V_\pm$ decomposition of $\mathbb{F}_q^{|S|}$ requires σ to act on $S$, i.e.,
$S = \sigma S$, which holds only for σ-symmetric S (|A| = 8).  For general
no-full S, σ does NOT preserve S, so $V_\pm$ is not well-defined on
$\mathbb{F}_q^{|S|}$.

Hence the §3 reduction of Note 0416 — claiming the saturation $\sum c_i HT(t^{r_i}) = 0$
splits as $V_+$-part + $V_-$-part independently — does not hold in general.

The closure statement of Note 0416 §6 must be retracted.

---

## 1.  The fundamental issue

For σ : t ↦ -t = $\omega^{n_2/2} \cdot t$, the σ-action on $\mathbb{F}_q^{|S|}$
sends position $s$ to $\sigma(s) = s + n_2/2 \bmod n_2$.  This permutes the
positions of $S$ iff $\sigma S = S$, i.e., S is σ-symmetric.

For general no-full S with $|A| < 8$ (where $A := S \cap \sigma S$): $\sigma S \neq S$,
so σ does NOT permute positions of S.  Hence $\mathbb{F}_q^{|S|}$ has no σ-action
and no $V_\pm$ decomposition.

**The high-tail vectors $\mathrm{HT}(t^r) \in \mathbb{F}_q^{|S|}$ for even/odd r
do NOT live in disjoint σ-eigenspaces** in general.

---

## 2.  What survives from Note 0416

**Partial $V_\pm$ on A-coords.**  Write $\mathbb{F}_q^{|S|} = \mathbb{F}_q^{|A|} \oplus \mathbb{F}_q^{|B|}$
(decompose by A vs B positions).  The A-coords $\mathbb{F}_q^{|A|}$ ARE σ-stable
(since A is σ-symmetric), so the A-restriction $HT(t^r)|_A$ decomposes by σ-eigenvalue:
* Even r: $HT(t^r)|_A \in V_+^{(A)}$
* Odd r:  $HT(t^r)|_A \in V_-^{(A)}$

For the B-coords: σ sends B → σB, which is disjoint from B, so σ doesn't act on
$\mathbb{F}_q^{|B|}$.  No decomposition.

The saturation on A-coords does decompose:
$\sum c_i HT(t^{r_i})|_A = 0 \Rightarrow$
$\sum_{r_i \text{ even}} c_i HT(t^{r_i})|_A = 0$ AND $\sum_{r_i \text{ odd}} c_i HT(t^{r_i})|_A = 0$.

But the saturation on B-coords does NOT decompose by parity.

So the "single vector V_- dependence forces $c = 0$" reasoning fails on B-coords.

---

## 3.  Why the empirical 0 result still holds

Despite the V_± argument failing for general S, the empirical fact remains:
**0 primitives across 615M trials at side-(3,1) configurations** (Notes 0353, 0389, 0392).

The structural reason is more subtle than the simple V_± parity-split argument.
It likely involves:
1. The interaction of A-coord σ-structure with B-coord arbitrariness.
2. The specific quadrant-pencil structure at the 896 S where rank-2 dependences exist.
3. Possibly a multi-step reduction via the doubling Note 0398 §5.

---

## 4.  Correct partial result (σ-symmetric S only)

The Note 0416 §3-§6 reasoning IS valid for σ-symmetric S (|A| = 8), which is
just 16 of 10896 no-full S.

> **Theorem (Tier 2 partial, σ-symmetric S only).**
> For σ-symmetric S (|A| = 8), no side-(3,1) primitive exists.

But |A|=8 is the σ-symmetric stratum already covered by Note 0397 (parity preservation).
So this partial result adds nothing new.

For the remaining 10880 S with |A| < 8: the V_± argument does not directly apply,
and side-(3,1) closure requires alternative structural analysis.

---

## 5.  Revised Tier 2 status

Tier 2 (side-(3,1)/(1,3) closure) is **STILL OPEN** structurally.
Note 0416's claim was overstated; this Note retracts it.

What we have empirically:
* 615M trials, 0 primitives (Notes 0353-0392).
* Multi-prime structural empirical (Notes 0413, 0413).
* Pairwise high-tail parity lemma at L_2=(16,4) field-uniform (Notes 0407-0413).
* Side-(2,2) at L_2=(16,4) closed structurally (Note 0394).

What we don't have structurally:
* Side-(3,1) primitive closure at L_2=(16,4).
* 5+/6+/7+/8+ supp closure at any L_2.

---

## 6.  Path forward (revised)

**Approach 1: Adapt V_± to S*.**
Use the doubling reduction g_{S*} = g_S · g_{B+8} (Note 0398 §5) to embed the
saturation on S into a saturation on S* := S ∪ σS.  S* is σ-symmetric, so V_±
decomposition applies.

The saturation on S extends to "saturation on S* with extra constraint".
The V_± decomposition on S* gives parity-separated dependencies.

The "extra constraint" from extending to S*: needs careful analysis.

**Approach 2: Direct character-pencil analysis.**
The 8 high-tail vectors {HT(t^r) : r ∈ [4, 15]} form a $\mathbb{Z}/16$-module
under the multiplicative action $t \mapsto \omega t$.  The pencil structure
determines all rank-2 dependences and hence all 4-vector dependences.
For side-(3,1), use the pencil to constrain the v-side vector relative to
the u-side rank-2 subspace.

**Approach 3: Cyclotomic resultant.**
Compute the resultant of the 4-vector dependence equations over $\mathbb{Z}[\omega_{16}]$.
If empty (no solution): side-(3,1) closed.

These all need significant work.  Estimated 1-3 weeks.

---

## 7.  Lesson learned

The V_± argument seemed too clean to be true — and indeed, it relied on σ
acting on the full $\mathbb{F}_q^{|S|}$, which holds only for σ-symmetric S.
For general no-full S, the σ-action is partial (A-coords only) and the
parity-split saturation argument doesn't go through.

This is healthy iteration: Note 0416 proposed a clean closure; Note 0417
honestly retracts the over-strong claim; the correct structural analysis
remains an open algebraic question.

The empirical 0-primitive result at 615M trials still strongly suggests
side-(3,1) closes — just not by the simple V_± parity argument.

---

## 8.  Updated Q2 closure status (revised after retraction)

| Sub-class | Status | Note(s) |
|---|---|---|
| All-alpha | CLOSED | 0388 |
| Half-turn stabilizer | CLOSED | 0345-0351 |
| One-residue lambda lift | CLOSED | 0356-0359 |
| Same-folded cancellation | trivial | 0360 |
| 4-supp side-(2,2) at L_2=(16,4) | CLOSED structurally + prime-uniform | 0393, 0394 |
| **4-supp side-(3,1)/(1,3) at L_2=(16,4)** | **OPEN (Note 0416 retracted)** | 0414, 0417 (this) |
| 4-supp side-(4,0)/(0,4) at L_2=(16,4) | CLOSED (side-pure rank ≤ 1) | 0394, paper2 §3 |
| 4-supp at L_2=(32,8) | empirically CLOSED (5k sample) | 0394 |
| Pairwise high-tail parity at L_2=(16,4) | FIELD-UNIFORM | 0407-0413 |
| 5+/6+/7+/8+ supp at any L_2 | OPEN structurally | 0392 |

Tier 2 (side-(3,1)) remains OPEN.  Empirical evidence: overwhelming (0 across
615M trials).  Structural proof: open problem.

---

## 9.  Strategic implication

* **Tier 1c at L_2=(16,4)** is essentially complete (Notes 0407-0413).
* **Tier 2 (side-(3,1))** remains genuinely open, with strong empirical
  evidence but no structural closure.

For the prize attack:
* Theorem~\ref{thm:universal-K10} ($K \le 10$ for sparse) requires Q2 for
  unconditional bound.
* Q2 closed for 3-support (paper2 §3), side-(2,2) (Notes 0393-0394), and
  side-(4,0)/(0,4) trivially.
* 4-supp side-(3,1)/(1,3) and 5+ supp remain structurally open but
  empirically 0 across 615M trials.
* Multi-prime empirical at 33+ primes provides strong evidence for
  field-uniform pairwise lemma.

For deployment-quality: empirical case is overwhelming; structural Tier 2
work continues.

---

## 10.  Next concrete artifact

Tier 2 iteration 3: pursue Approach 1 (V_± via S* doubling reduction).
This is the cleanest path: leverage Note 0398's doubling framework to apply
σ-decomposition on the doubled set S*.

Output target: Note 0418.

Or alternatively: continue Tier 1c by extending the Z[ω_16] minor framework
to |A| ∈ {0, 2} via optimized implementation.

Or: paper2 v22 integration draft with current Tier 1c results.
