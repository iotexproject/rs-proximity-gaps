# Note 0350 -- Issue #419: product-gap form of the small-doubled rank lemma

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** algebraic reformulation of the remaining small-doubled blocker;
closed by the parity-side multiplicity proof in Note 0351.

---

## Purpose

Note 0349 isolates the remaining half-turn stabilizer gap as a signed
two-band rank statement.  This note rewrites that rank statement as a
polynomial product-gap theorem.  This is a better target for hand proof or
exact symbolic certification because it removes the interpolation
representative variables.

---

## From matrix kernel to product divisibility

Use the notation of Notes 0348--0349.  In the even branch, the weighted
matrix kernel is equivalent to a nonzero polynomial

```text
P(x) = A(x^2) + x B(x^2) - x^{4h} C(x^2)
```

with

```text
deg A, deg B, deg C < h
```

vanishing on the selected `4h`-set `S`.

The exponent support of `P` lies in

```text
E = {0,1,...,2h-1} union {4h,4h+2,...,6h-2}.
```

Let

```text
Q_S(x)=prod_{s in S}(x-s).
```

Since `deg P <= 6h-2` and `deg Q_S=4h`, vanishing on `S` is equivalent to

```text
P(x)=Q_S(x) M(x),        deg M <= 2h-2.
```

Thus the small-doubled rank lemma is equivalent to:

> **Product-gap lemma.**  If `S` has size `4h` and fewer than `h` antipodal
> pairs, then no nonzero `M` of degree `<=2h-2` can make `Q_S M` supported in
> `E`.

The forbidden coefficient windows are:

```text
[2h, 4h-1]                         length 2h,
odd exponents in [4h+1, 6h-3].      length h-1.
```

The first window alone gives `2h` linear equations on the `2h-1`
coefficients of `M`, but it is **not** sufficient at larger `h`: random
checks at `h=4,8` find middle-window rank drops.  The correct map must include
both forbidden windows.

---

## Why small doubled matters in `Q_S`

Write the half-turn quotient fibers as:

```text
D = doubled fibers,       |D|=d<h,
G = singleton fibers,     |G|=4h-2d.
```

Then

```text
Q_S(x)
  = prod_{y in D} (x^2-y)
    prod_{g in G} (x-x_g),
```

where `x_g` is the selected square root over `g`.

The condition `d<h` means that the singleton product has degree

```text
|G| = 4h-2d > 2h.
```

This is exactly the regime where the middle coefficients of `Q_S M` should be
too constrained to allow a gap of length `2h`.

---

## Exact proof target

Let

```text
T_S : F[x]_{<=2h-2} -> F^{3h-1}
```

be the joint coefficient-gap map

```text
M |-> (
  [x^{2h}]Q_SM, ..., [x^{4h-1}]Q_SM;
  [x^{4h+1}]Q_SM, [x^{4h+3}]Q_SM, ..., [x^{6h-3}]Q_SM
).
```

The product-gap lemma follows from:

> **Joint-gap full-column-rank lemma.**  If `S` has fewer than `h` antipodal
> pairs, then `T_S` has rank `2h-1`.

This statement is stronger than needed but matches the observed full-rank
matrix behavior in Note 0349.  It is also independent of the even/odd branch:
the odd branch has the same `Q_S` and the same middle gap after shifting by
one exponent.

---

## Current obstacle

This obstacle was open when this note was written.  It is now closed by Note
0351, which proves the equivalent weighted quotient statement by a
parity-side multiplicity argument.  The determinant target below remains the
right regression object:

```text
the (3h-1) x (2h-1) Toeplitz submatrix selecting
exponents [2h,4h-1] and odd exponents [4h+1,6h-3]
```

where `Q_S(x)=sum_i q_i x^i`.

Equivalently, a counterexample would be a nonzero polynomial `M` of degree
`<=2h-2` such that the product `Q_S M` has a long internal coefficient gap.
The small-doubled hypothesis should rule this out because `Q_S` has more than
`2h` unpaired linear factors.

This is now the most compact form of the remaining #419 stabilizer blocker.

Random checks of this exact joint map found full column rank in all sampled
small-doubled cases:

```text
h=2, q=193: rank 3 = 2h-1
h=4, q=193: rank 7 = 2h-1
h=8, q=257: rank 15 = 2h-1
```

The middle window without the high odd window is not enough, so any proof must
use both parts of the coefficient gap.
