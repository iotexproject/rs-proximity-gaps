# Note 0355 -- Issue #419: next proof target after nonzero-alpha audit

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** proof-target checkpoint; stop adding enumeration unless it tests this target.

---

## Current theorem-level progress

The branch now has one real theorem closure:

> **Half-turn row-span stabilizer closure.**  A nontrivial half-turn row-span
> stabilizer descends to a weighted quotient system.  The large-doubled quotient
> case is charged by a parity-tail quotient direction (Note 0348), and the
> small-doubled quotient case has no nonzero high direction (Note 0351).

This closes a genuine sub-branch of the defect-allocation descent theorem.

The classifier/audit evidence then shows that, in the tested 4- and 5-support
base panels, every `alpha1 != 0` no-full saturated candidate is either:

```text
rank(W) < 2,
```

or exactly the half-turn stabilizer branch above.

Random 6/7/8-support stress found no `alpha1 != 0` candidates at all.

---

## Do not continue blind enumeration

Further support-size enumeration has diminishing value.  The next result must
attack the structural reason that the symbolic-alpha equations collapse.

The useful target is:

> **Nonzero-alpha collapse theorem.**  In the quotient-`C4` defect-allocation
> system for a legal strict above-J folded row span, every no-full saturated
> component with `alpha1 != 0` is either rank-deficient, has nontrivial dyadic
> row-span stabilizer, or belongs to the already charged local families.

A proof of this theorem, together with Note 0351, would close the primitive
attachment branch left by Note 0352 and therefore close the path-(c) route of
#419.

---

## Concrete algebraic handle

Use Note 0323's local representative formula.  For every residue `a mod k`, the
four block representatives are the `C4` Fourier transform of

```text
(p_a, p_{a+k}, p_{a+2k}, p_{a+3k}).
```

For a legal folded row span, the coefficients are affine in `alpha1`.  For a
fixed no-full component `S`, saturation is the dual parity system from Note
0340:

```text
H_S (R_0(w)|_{A_0}, R_1(w)|_{A_1}, R_2(w)|_{A_2}, R_3(w)|_{A_3})^T = 0
```

for both basis rows `w`.  Since each row is affine in `alpha1`, every component
imposes

```text
C(S) + alpha1 M(S) = 0.
```

The audits suggest the following stronger finite-dimensional statement:

> If `C(S)+alpha1 M(S)=0` has a solution with `alpha1 != 0`, then the two row
> directions produced by the legal folded support either lose rank or have a
> half-turn eigenbasis.

Equivalently, after excluding rank deficiency, the nonzero-alpha equations
should force the row supports to split into two half-turn-separated pairs:

```text
supp(u) = {r, r+2h},       supp(v) = {s, s+2h}
```

in the descended quotient coordinate.  That is exactly the stabilizer bucket
closed by Notes 0347--0351.

---

## Suggested next implementation

Build a symbolic extractor for the linear system matrices `C(S), M(S)` that:

1. takes one no-full component `S` and one abstract support pattern;
2. computes the affine equations over `Z` or a large prime;
3. saturates by `alpha1 != 0` and rank-2 minors;
4. checks whether the ideal implies the half-turn stabilizer minors.

This should start with the observed 4-support stabilizer/rank-collapse shapes,
not arbitrary support.  The goal is a template identity that can then be lifted
from the finite panel to the general quotient-`C4` normal form.
