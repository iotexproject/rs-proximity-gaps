# Note 0369 -- Issue #396: one-residue C4-fiber root budget

> **Note number history**: filed as Note 0343 on the `issue-396`
> branch; renumbered to 0369 on `main` to avoid collision with already-
> absorbed content at slot 0343. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** partial reduction of the one-residue caveat from Note 0342.

---

## Purpose

Note 0342 corrected an over-aggressive shortcut: a singleton effective
residue modulo `k` is not necessarily a literal monomial tail.  It can be a
full quotient-`C4` fiber

```text
P(x) = x^a Q(x^k),        deg Q < 4,
```

whose values on the four quarter blocks are scalar multiples of `x^a`.
This note isolates a root-budget obstruction for that caveat.

The result is not a full #396 closure.  It proves a two-active-value
obstruction: a no-full `2k` saturated set cannot draw points from exactly two
different scalar value levels of a one-residue fiber.  Thus the one-residue
caveat is narrowed to either a single high-multiplicity value level or at
least three active value levels.

---

## Setup

Let `L=<omega>` have order `4k`, and write

```text
C_i = { x in L : x^k = zeta^i },      i=0,1,2,3,
```

where `zeta=omega^k` has order four.  Let

```text
P(x)=x^a Q(x^k),        0 <= a < k,        deg Q < 4.
```

On block `C_i`,

```text
P(x) = lambda_i x^a,        lambda_i := Q(zeta^i).
```

Let `S subset L`, `|S|=2k`, and put

```text
A_i = S cap C_i.
```

Assume `P|_S` agrees with some degree-`<k` polynomial `p`.

---

## Lemma 0343.A -- value-level root budget

For each scalar value `lambda` attained by

```text
(lambda_0, lambda_1, lambda_2, lambda_3),
```

define the selected value level

```text
B_lambda = union_{i : lambda_i = lambda} A_i.
```

If `p != lambda x^a`, then

```text
|B_lambda| <= k-1.
```

If `p = lambda x^a`, then

```text
B_mu = empty        for every mu != lambda.
```

**Proof.**
On every point of `B_lambda`,

```text
p(x) = lambda x^a.
```

Thus `p-lambda x^a` is a degree-`<k` polynomial with roots `B_lambda`.  If it
is nonzero, it has at most `k-1` roots on the cyclic domain.  If it is zero,
then for any `mu != lambda`,

```text
p(x)-mu x^a = (lambda-mu)x^a,
```

which has no roots on `L`, so no selected point can lie in a `mu`-level. ∎

---

## Corollary 0343.B -- exactly two active value levels are impossible

Suppose the selected set `S` meets exactly two distinct value levels of
`P=x^a Q(x^k)`, say `lambda` and `mu`.  Lemma 0343.A gives

```text
|S| = |B_lambda| + |B_mu| <= (k-1)+(k-1)=2k-2,
```

unless `p` equals one of the two scalar multiples, in which case the other
level is empty.  This contradicts `|S|=2k`.

Therefore a saturated `2k` set for a one-residue C4 fiber cannot have exactly
two active scalar value levels.

The one-active-level case is different and must not be discarded.  If all of
`S` lies in blocks with the same value `lambda`, then `p=lambda x^a` works on
that row.  This cannot produce a no-full `2k` set when that value occurs in
only one or two quarter blocks, because then the no-full capacity is at most
`2k-2`.  But if the value occurs in three or four blocks, a no-full `2k`
subset can fit inside that single level for this row alone.  Such a component
would still have to be saturated for the second row direction.

---

## Consequence for the Note 0342 caveat

The one-residue caveat is now smaller:

```text
P=x^a Q(x^k) one-residue fiber
  + no-full |S|=2k saturation
  => active value levels are not exactly two.
```

In particular:

1. constant `Q` is a low-degree row and is not an above-Johnson residual
   obstruction;
2. a one- or two-block value level cannot alone host a no-full `2k` set;
3. exactly two active value levels are impossible by the root budget;
4. the remaining one-residue subcases are:
   - one active value level of multiplicity at least three, with the second
     row direction doing all remaining work; or
   - at least three active scalar values.

This is useful because the parity/stabilizer branch tends to create exactly
two active block-value patterns.  Those patterns are now excluded from the
one-residue caveat without appealing to a finite panel.

---

## Remaining subcase

The unresolved one-residue branch is therefore:

```text
P=x^a Q(x^k),
S either lies in one value level of multiplicity >=3
  or meets >=3 distinct value levels of Q on the C4 blocks,
and S is simultaneously saturated for the second row direction.
```

This is a much smaller problem than the original caveat.  It is a
four-level interpolation budget, not a general sparse-support question.  A
next proof step would combine Lemma 0343.A for two independent row directions:
their value-level partitions must admit a common degree-`<k` interpolant on
the same `2k` no-full set.  That is the remaining algebraic constraint for
one-residue fibers inside the Note 0336 defect-allocation theorem.

Update after Note 0344: the base quotient `L2=(16,4)` has now been classified
by the full linear lambda-space, not just by sampled scalar values.  The
`>=3`-active-value alternative exists at the base layer only on balanced
opposite-pair sets invariant under the order-2 dyadic action, so it is charged
to stabilizer/descent rather than to the primitive branch.  The remaining
one-residue work is therefore the all-scale lift of that stabilizer mechanism
plus the high-multiplicity one-active-value branch.

Update after Note 0348: the high-multiplicity one-active-value branch is also
rank collapse.  If `S` meets only one scalar value of `Q(x^k)`, then
`x^a Q(x^k)|_S` equals the low monomial `lambda x^a|_S`, so that residual
direction is already in `RS_k(S)`.  The remaining one-residue gap is the
entry lemma for the high-scale rank-2 separating branch.
