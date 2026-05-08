# Note 0414 -- Issue #419: Tier 2 framing — side-(3,1)/(1,3) primitive obstruction

**Date:** 2026-05-02 (overnight, post-Tier-1c-substantial-completion)
**Branch:** `main`
**Status:** Framing note for Tier 2 attack on the side-(3,1) / (1,3) sub-class
of 4-support primitives at $L_2 = (16, 4)$.  Note 0395 documented the obstacle;
this Note formalizes the target and structure of the lemma to be proven.

---

## 1.  The target

After Notes 0407–0413 (Tier 1c at $L_2 = (16, 4)$), the remaining open
algebraic gap for **Q2 (sparse-worst-case dominance) closure** is the
4-support **side-(3,1) / (1,3)** primitive sub-class.

**Setup.**  $L_2 = (16, 4)$, $|S| = 8$, no-full.  4-support
$\mathrm{supp} = \{r_1, r_2, r_3, r_4\}$ with positions distributed
across the 4 quadrants of $\mathbb{Z}/16$ ($j \bmod 4 \in \{0, 1, 2, 3\}$).

**Side-(3, 1)** quadrant pattern: 3 of the 4 positions have $j \bmod 4 \in \{0, 1\}$
(u-side), 1 position has $j \bmod 4 \in \{2, 3\}$ (v-side).

For such a 4-support, the residual matrix:
$$
W(\alpha_1)_{[u, v]} =
\begin{pmatrix}
c_{u_1} t^{r_{u_1}} + c_{u_2} t^{r_{u_2}} + c_{u_3} t^{r_{u_3}} + \alpha_1(\text{u-twist}) \\
c_v t^{r_v}
\end{pmatrix}
$$
has u-side row with 3 monomials + α-perturbation, v-side row with 1 monomial.

**Primitive obstruction**: $\mathrm{rank}\, W(\alpha_1) = 2$ saturated on $S$
(meaning $W(\alpha_1)|_S = 0$ for some α_1), with all the additional
side conditions (Note 0389):
1. Coefficients NOT in any all-α kernel (excludes Note 0388's all-α branch).
2. $α_1$ specific nonzero (not vacuously α-uniform).
3. $\mathrm{rank}\, W = 2$ (not rank ≤ 1).
4. Trivial dyadic row-span stabilizer (no σ-symmetry trick).
5. At least one residual row with mixed parity in quotient coords.

**Empirical**: across 615M trials at random arbitrary coefs (Notes 0353/0365/0389
plus follow-ups), $0$ side-(3,1) primitives at any tested $q \ge 97$.

**Structural gap**: the pairwise high-tail parity lemma (Note 0393) closes
side-(2, 2) exhaustively but does NOT directly cover side-(3, 1) — Note 0395
documented 3-vector dependences (e.g., $(8, 10, 9)$ rank 2 at exactly $896 / 10896$ S)
that pose a potential obstruction.

---

## 2.  The 3-vector dependences in detail

From Note 0395 §1, at $L_2 = (16, 4)$:

| Triple $(r_a, r_b, r_c)$ | Rank-2 S count | Prime-uniform? |
|---|---|---|
| $(8, 10, 9)$ | 896 / 10896 | ✓ same at $q \in \{97, 193\}$ |
| $(8, 10, 11)$ | 896 / 10896 | ✓ |
| $(9, 11, 8)$ | 896 / 10896 | ✓ |
| $(9, 11, 10)$ | 896 / 10896 | ✓ |
| (other triples) | smaller buckets | varied |

The 4 main triples are exactly the **mixed-parity 3-supports** containing
the Note 0393 pairs $(8, 10)$ and $(9, 11)$:
* $(8, 10)$ same-parity (both even) — gives 128 S where $\mathrm{HT}(t^8) \propto \mathrm{HT}(t^{10})$.
* When you append a third position $r_c$ of opposite parity ($9$ or $11$):
  the rank-2 dependence on $\{8, 10, r_c\}$ persists (rank 2 = rank already from $(8, 10)$).
* So the 896 S = $128 \times 7$ where 7 is some structural multiplier — likely
  the number of distinct mod-8 "lift" choices, but the precise factorization
  needs further analysis.

**Crucial observation.**  At those 896 S, the rank-2 dependence is on
$\mathrm{HT}(t^8), \mathrm{HT}(t^{10}), \mathrm{HT}(t^9)$ in $\mathbb{F}_q^4$
(or analogous triples).  This is necessary but NOT sufficient for a side-(3,1)
primitive.  The additional constraints (rank-2 (u, v) joint, trivial dyadic
stab, etc.) still need to be checked.

The empirical 0-primitive result across 615M trials suggests these additional
constraints **always fail** for the 896 S × triples.  The structural reason
is the open Tier 2 question.

---

## 3.  Plausible structural mechanisms

Several candidate mechanisms could explain the empirical 0-primitive result:

**Mechanism A: V-side singleton constraint.**
The v-side has 1 position $r_v$.  $v_α = c_v t^{r_v}$ is a single monomial.
For $v_α|_S = 0$: $\mathrm{HT}(t^{r_v}) = 0$ in $\mathbb{F}_q^{k_2}$, equivalently
$g_S | t^{r_v}$.  This requires $S$ to contain all roots of $t^{r_v}$ on $L_2$,
i.e., to contain $\{0\}$... wait this isn't quite right.  $\mathrm{HT}(t^{r_v})$
is the "high-tail" projection, not the full polynomial.  Need to rederive.

Actually: $u_α|_S = 0$ AND $v_α|_S = 0$ is the saturation condition.  Each
gives $|S|$ equations.  For nontrivial $α_1$ kernel, the rank reduction must
align with the saturation constraint.

**Mechanism B: Mixed-parity twin constraint.**
Note 0395 mentions "mixed parity in BOTH rows" as a primitive constraint.
For side-(3,1), the v-row has 1 position with single parity — vacuously NOT
mixed.  So if "mixed parity" is required for primitive, side-(3,1) is
**automatically excluded** from primitive class.  This would close side-(3,1)
trivially!

But this contradicts Note 0395's claim that mixed-parity 3-vector dependences
(8, 10, 9) etc. enable potential primitives.  Need to clarify the "mixed
parity" requirement.

**Mechanism C: DFT character pencil structure.**
The 8 high-tail vectors $\{\mathrm{HT}(t^r) : r \in [4, 15]\}$ form a
$\mathbb{Z}/16\mathbb{Z}$-module via $g_S$-quotient action.  The rank
structure of any 3-subset is determined by the $\mathbb{Z}/16$-character
decomposition.  A unified structural argument might show: for side-(3,1)
support, the rank-2 dependences (when they exist) have the wrong character
for any nonzero $α_1$ kernel.

This is the Note 0395 "DFT pencil structure" approach.  Requires deep
character-theoretic analysis.

**Mechanism D: Dyadic stabilizer obstruction.**
Side-(3,1) supports might have nontrivial dyadic row-span stabilizer for ALL
no-full S — failing Note 0389's "trivial stabilizer" constraint for primitives.

---

## 4.  Concrete next steps

**Step 1**: Verify Mechanism B (mixed-parity exclusion).  Empirically check
whether any side-(3,1) candidate has v-row with "mixed parity" (which
shouldn't happen with 1 monomial).

**Step 2**: If Mechanism B holds: side-(3,1) is structurally closed by the
combined lemma (Note 0393 pairwise + Note 0389 mixed-parity requirement).

**Step 3**: If not: pursue Mechanism C/D — character pencil or dyadic
stabilizer analysis.

**Step 4**: Document conclusion in Notes 0415+.

**Step 5**: Extend to side-(1, 3) (symmetric case).  Then 4-support fully
closed.

---

## 5.  Side-(4, 0) and (0, 4) considerations

Side-(4, 0) = all 4 positions on u-side (j mod 4 ∈ {0, 1}).
Side-(0, 4) = all 4 positions on v-side.

These are **side-pure** 4-supports.  By Note 0395 §3 paper2 §3 reasoning
(side-pure 3-support → rank ≤ 1 by zero residual row), the side-pure
4-support also has rank ≤ 1 in the residual row that's missing.  So
$\mathrm{rank}\, W(\alpha_1) \le 1$ → not primitive (rank-2 required).

So side-(4, 0) and (0, 4) close trivially via side-pure rank-bound.

**Remaining 4-support open class: side-(3, 1) and (1, 3) only.**

---

## 6.  Strategic position update

Tier 1c at $L_2 = (16, 4)$: 7056/10896 (64.8%) strict field-uniform via
Z[ω_*] frameworks; 3840/10896 (35.2%) multi-prime empirical at $q \ge 97$.
Combined: the pairwise high-tail parity lemma is essentially proven
(modulo Z[ω_16] extension to |A| ∈ {0, 2}).

**Tier 2 (side-(3,1)/(1,3))**: open algebraic gap with empirical 0 across 615M trials.
Mechanism B (mixed-parity-row exclusion) is the most likely quick close.
Estimated 1-3 days for first mechanism to hold up; possibly weeks for full
structural proof.

After Tier 2 closes: 4-support fully proven at $L_2 = (16, 4)$ → Q2 closure
COMPLETE at base scale.  Scale-lift via Note 0397 framework extends to
deployment scales.  **Q2 conjecture proven**, and ABF Lemma 6.13 + Q2 →
**Theorem~\ref{thm:universal-K10} unconditional** at deployment scale →
**Ethereum Foundation $1M Proximity Prize attack vector solidified**.

---

## 7.  Next concrete artifact

Tier 2 iteration 1: write `issue419_side31_mixed_parity_check.py` to
empirically verify Mechanism B on the 896 S × 4 triples × all coef configurations.

Output target: Note 0415 (Mechanism B verification).
