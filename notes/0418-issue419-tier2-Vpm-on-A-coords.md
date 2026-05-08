# Note 0418 -- Issue #419: Tier 2 — V_± on A-coords (refined claim)

**Date:** 2026-05-02 late night (Tier 2 framing iteration 4 — refined position)
**Branch:** `main`
**Status:** **Refinement** of Notes 0416 (over-strong) and 0417 (over-cautious).
The V_±-decomposition argument is VALID **on A-coords only**, which suffices
to close side-(3,1) primitives for **all S with |A| ≥ 2** (= 10640 / 10896 S).
For |A| = 0 (256 S), the argument doesn't apply and requires separate analysis.

---

## 1.  Refined V_± setup

For S = A ⊔ B with A σ-symmetric and B singletons, we have natural decomposition:
$$\mathbb{F}_q^{|S|} = \mathbb{F}_q^{|A|} \oplus \mathbb{F}_q^{|B|}.$$

The σ-action permutes positions of A (since σA = A), so it acts on $\mathbb{F}_q^{|A|}$,
splitting:
$$\mathbb{F}_q^{|A|} = V_+^{(A)} \oplus V_-^{(A)}, \quad \dim V_\pm^{(A)} = |A|/2.$$

σ does NOT act on $\mathbb{F}_q^{|B|}$ (since σB ∩ B = ∅), so no decomposition there.

The saturation $f|_S = 0$ decomposes as $f|_A = 0$ AND $f|_B = 0$.

The first factor $f|_A = 0$ decomposes by σ-action into:
* $f|_A^{V_+}$ part: even-r coefficient saturation on $V_+^{(A)}$
* $f|_A^{V_-}$ part: odd-r coefficient saturation on $V_-^{(A)}$

Specifically, for each σ-orbit $\{a, a+n_2/2\} \subset A$ (one representative $a$):
$$f(a) + f(-a) = 2 \sum_{r_i \text{ even}} c_i \omega^{r_i a} = 0 \quad (V_+^{(A)})$$
$$f(a) - f(-a) = 2 \sum_{r_i \text{ odd}} c_i \omega^{r_i a} = 0 \quad (V_-^{(A)})$$

These are $|A|/2$ equations each.

---

## 2.  Side-(3,1) primitive closure for |A| ≥ 2

For side-(3,1) primitive with parity split (k_+, k_-) where k_+ + k_- = 4:

**Case (3, 1)** — 3 even, 1 odd. The $V_-^{(A)}$ saturation involves only the
odd column $r_v$:
$$c_v \cdot \omega^{r_v a} = 0 \quad \text{for each } a \in A/\sigma.$$
Since $\omega^{r_v a} \ne 0$ (unit) and $|A|/\sigma = |A|/2 \ge 1$ (i.e., $|A| \ge 2$):
$c_v = 0$.

**Case (1, 3)** — 1 even, 3 odd. Symmetric: $V_+^{(A)}$ forces the unique even
coefficient to zero.

**Case (4, 0)** — all 4 even. $V_-^{(A)}$ part is empty (no odd cols), so no
constraint.  $V_+^{(A)}$ has 4 cols, |A|/2 equations, may be solvable.
But (4, 0) parity split with side-(3, 1) quadrant pattern (3 in u, 1 in v):
* u-side has positions in q={0, 1}; r mod 4 ∈ {0, 1}; r mod 2 ∈ {0, 1}.
* For all 4 r even: positions in q=0 (even mod 4) AND q=2 (even mod 4).
* But q=2 is v-side. So 4 even positions = (3, 1) in u-v with u in q=0 and v in q=2.
* This forces q-distribution (3, 0, 1, 0).
* On (3, 0, 1, 0), v-row: $v_α = c_v t^{r_v}$ (single monomial, no α). Saturation
  on B-coords: $c_v \omega^{r_v b} = 0$ for each $b \in B$.  Forces $c_v = 0$.
* So either way, $c_v = 0$ → 3-support → closed.

**Case (0, 4)** — all 4 odd.  Same reasoning, $c_v = 0$.

**Case (2, 2)** — 2 even, 2 odd. Both $V_\pm^{(A)}$ parts have 2 cols. May have
non-trivial saturation. Need further analysis (next §).

---

## 3.  Side-(3,1) parity (2, 2) case

The parity-(2, 2) sub-case is the surviving structurally non-trivial one.

For side-(3,1) with parity (2, 2):
* u-side has 2 even + 1 odd OR 1 even + 2 odd (3 positions).
* v-side has 1 even OR 1 odd (1 position).

Combinations:
* u(2 even + 1 odd), v(1 odd): parity (2, 2) → quadrants (2, 1, 0, 1).
* u(2 even + 1 odd), v(1 even): parity (3, 1) → already closed.
* u(1 even + 2 odd), v(1 even): parity (2, 2) → quadrants (1, 2, 1, 0).
* u(1 even + 2 odd), v(1 odd): parity (1, 3) → already closed.

So the only side-(3,1) parity-(2,2) configurations are:
* $(k_0, k_1, k_2, k_3) = (2, 1, 0, 1)$: 2 in q=0, 1 in q=1, 0 in q=2, 1 in q=3.
* $(k_0, k_1, k_2, k_3) = (1, 2, 1, 0)$: 1 in q=0, 2 in q=1, 1 in q=2, 0 in q=3.

For these:
* V_+ saturation: 2 even cols (one from u, one from v) must be proportional.
* V_- saturation: 2 odd cols (one from u, one from v) must be proportional.

By the **pairwise high-tail parity lemma** (Note 0393, now FIELD-UNIFORM via
Notes 0407-0413): same-parity proportionalities at L_2=(16,4) only occur at
$(r_a, r_b) = (8, 10)$ for evens or $(9, 11)$ for odds, each at exactly 128 S.

For both V_+ and V_- to satisfy proportionality SIMULTANEOUSLY:
* Even pair = {8, 10}, odd pair = {9, 11}.
* So 4-support = {8, 9, 10, 11}.

But quadrants: 8 ∈ q=0, 9 ∈ q=1, 10 ∈ q=2, 11 ∈ q=3.
Quadrant pattern: (1, 1, 1, 1) = side-(2, 2), NOT side-(3, 1).

**Hence the parity-(2,2) side-(3,1) class is empty.**

---

## 4.  Combined conclusion

> **Theorem (Tier 2, side-(3,1)/(1,3) at L_2=(16,4), |A| ≥ 2).**
> For every odd characteristic with $16 \mid q-1$, every no-full S with $|A| \ge 2$,
> and every 4-support with side-(3,1) or (1,3) quadrant pattern: no primitive
> rank-2 saturated obstruction exists.
>
> **Proof.**  Decompose F_q^|S| = F_q^|A| ⊕ F_q^|B|.  The A-coords admit σ-isotypic
> decomposition into V_±^{(A)}.  For 4-support primitive saturation:
> * Parity split ≠ (2, 2): V_+^{(A)} or V_-^{(A)} forces a singleton-parity coef to 0,
>   reducing to 3-support → closed by paper2 §3.
> * Parity split (2, 2): would require {8, 9, 10, 11} support (Note 0393), which has
>   quadrant pattern (1,1,1,1) = side-(2,2), not side-(3,1).
>
> Hence side-(3,1) class is empty for |A| ≥ 2.  Symmetric for (1, 3).  $\square$

This covers **10640 / 10896 = 97.7%** of no-full S.

---

## 5.  |A| = 0 stratum (256 S)

For |A| = 0: A is empty, B = S, |B| = 8.

The A-coord decomposition is degenerate (no σ-orbits), so V_±^{(A)} reasoning
doesn't apply.  Side-(3,1) primitive analysis on |A|=0 requires direct
computation on the 8 B-coords.

**Empirical** (Notes 0353, 0389, 0392, 0413, multi-prime): 0 primitives at
|A|=0 across 33+ primes ≡ 1 mod 16, q ≥ 97.  Plus 615M random-coef trials
across all strata.

So |A|=0 side-(3,1) is **empirically closed** but lacks structural proof.
This matches the more general |A|=0 |gap| in Tier 1c (Note 0413).

---

## 6.  Updated Q2 closure status (post-correction)

| Sub-class | Status | Note |
|---|---|---|
| All-alpha | CLOSED | 0388 |
| Half-turn stabilizer | CLOSED | 0345-0351 |
| One-residue lambda lift | CLOSED | 0356-0359 |
| Same-folded cancellation | trivial | 0360 |
| 4-supp side-(2,2) at L_2=(16,4) | CLOSED structurally + prime-uniform | 0393, 0394 |
| **4-supp side-(3,1)/(1,3) at L_2=(16,4), |A| ≥ 2** | **CLOSED via V_±^{(A)} (this Note)** | **0418** |
| 4-supp side-(3,1)/(1,3) at L_2=(16,4), |A| = 0 | empirical (33 primes) | 0413 |
| 4-supp side-(4,0)/(0,4) at L_2=(16,4) | CLOSED via side-pure rank ≤ 1 | 0394, paper2 §3 |
| 4-supp at L_2=(32,8) | empirically CLOSED | 0394 |
| Pairwise high-tail parity at L_2=(16,4) | FIELD-UNIFORM | 0407-0413 |
| 5+/6+/7+/8+ supp at any L_2 | OPEN structurally | 0392 |

**4-support is now FIELD-UNIFORM CLOSED at L_2=(16,4) for ~98% of no-full S
structurally.**

---

## 7.  Verification status

The argument in §2 hinges on:
1. σ acts on $\mathbb{F}_q^{|A|}$ (correct for σ-symmetric A — which holds by definition).
2. The σ-eigenspace decomposition $V_\pm^{(A)}$ has dim = |A|/2 each.
3. For odd $r_v$, the V_- vector $\omega^{r_v a}$ is nonzero unit at each $a \in A/σ$.
4. Hence $c_v \cdot v_- = 0$ in the $V_-^{(A)}$ subspace forces $c_v = 0$ when |A| ≥ 2.

All four are standard. The argument is correct (in contrast to Note 0416's
original formulation which incorrectly assumed σ on full $\mathbb{F}_q^{|S|}$).

The §3 parity-(2,2) reduction relies on the pairwise high-tail parity lemma
(Note 0393, FIELD-UNIFORM via Notes 0407-0413). Combined with the {8,9,10,11}
quadrant-(1,1,1,1) observation: no side-(3,1) configuration in this class.

---

## 8.  Strategic implication

* **Q2 4-support closure is now FIELD-UNIFORM at L_2=(16,4) for |A| ≥ 2** (~97.7% of S).
* Combined with Tier 1c (Notes 0407-0413): the pairwise lemma is FIELD-UNIFORM
  too.
* Side-(3,1) for |A|=0 (256 S, ~2.4%) is empirical only.
* 5+ supp remains open structurally.

For the prize attack: the 4-support primitive obstruction is now structurally
closed for ALL but a tiny stratum (|A|=0, 256 S out of 10896), with empirical
backing for that residual. **This is a major Tier 2 result, opening the path
to unconditional Theorem~\ref{thm:universal-K10} at deployment scale.**

---

## 9.  Next concrete artifact

Tier 2 iteration 5: extend §2 reasoning to |A|=0 stratum.
* For |A|=0, the V_±^{(A)} argument is degenerate.
* Alternative: direct character-pencil analysis on the |A|=0 stratum (256 S,
  finite check).
* Or: Z[ω_16] complete-resultant approach.

Output target: Note 0419 (|A|=0 side-(3,1) extension).

Or: paper2 v22 integration draft with Tier 1c + Tier 2 (|A| ≥ 2) results.

---

## 10.  Lesson learned

The clean closure proof of Note 0416 was OVER-strong (claimed for all S);
Note 0417 OVER-corrected (claimed for σ-symmetric S only); this Note 0418 finds
the right level of generality (|A| ≥ 2, ~98% coverage).

Three iterations to land the right statement.  Honest documentation of the
arc (over-claim → over-retract → refined position) helps future readers
understand the actual structural content.
