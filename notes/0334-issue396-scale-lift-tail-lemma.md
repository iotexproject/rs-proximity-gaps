# Note 0334 -- Issue #396: scale-lift target for the cyclotomic tail lemma

## Purpose

Note 0333 closes the primitive no-full branch in the legal base model
`L2=(16,4)`.  This note identifies the exact scale-lift lemma needed to move
from that base certificate toward the paper2/P3 general-f dyadic component
theorem.

The point is to avoid further same-scale enumeration.  The next useful hard
step is a block-interpolation theorem for general `n=4k`.

Update: Note 0337 proves the scale-lift lemma by a shorter root-count
classification.  The block-interpolation normal form below remains useful
diagnostic scaffolding, but the theorem no longer depends on further
enumeration or Groebner-basis checks.

## General dyadic tail lemma target

Let `L=<zeta>` be cyclic of order `n=4k`, and split it into the four quarter
blocks

```text
C_b = {x in L : x^k = i^b},     b=0,1,2,3.
```

Let `S subset L` have size `2k` and write `S_b=S cap C_b`, `s_b=|S_b|`.
Call `S` no-full if

```text
s_b < k for every b.
```

For `k <= e < 4k`, write

```text
e = a k + r,        0 <= r < k.
```

On block `C_b`,

```text
x^e = (x^k)^a x^r = i^{ab} x^r.
```

The scale-lift lemma needed by #396 is:

> If `S` is no-full, then `x^e|_S` is not the restriction of any degree-`<k`
> polynomial, for every `k <= e < 4k`.

Equivalently, `tail_S(x^e) != 0` for every no-full `S`.

The base case `k=4` is exactly Note 0332.  There the only 8-subsets where
`x^e` can restrict to degree `<4` are the two parity halves, and both contain
full quarter blocks.

## Block-interpolation normal form

Assume for contradiction that a degree-`<k` polynomial `p` agrees with `x^e`
on `S`.  Then for each block `b`,

```text
p(x) = i^{ab} x^r       for x in S_b.
```

Let

```text
G_b(x) = prod_{x in S_b} (x-x_i).
```

Since `deg p < k`, the block condition is equivalent to the divisibility
normal form

```text
p(x) = i^{ab} x^r + G_b(x) Q_b(x),
deg Q_b < k - s_b.
```

For two blocks `b,c`, subtracting gives the polynomial identity

```text
(i^{ab}-i^{ac}) x^r = G_c(x) Q_c(x) - G_b(x) Q_b(x).        (1)
```

This identity has degree `<k`.  It is the scale version of the exact
cyclotomic determinant test from Note 0332.  The no-full condition is exactly
that all four degree budgets `k-s_b` are positive while

```text
s_0+s_1+s_2+s_3 = 2k.
```

## Expected classification

The expected full classification is:

```text
if x^e|_S in RS_k(S) and |S|=2k,
then either S contains a full quarter block,
or e=2k+r and S is one of the two parity halves.
```

The parity halves have occupancies

```text
(k,0,k,0) and (0,k,0,k),
```

so they are not no-full.  Thus the classification implies the no-full
tail lemma.

For `k=4`, Note 0332 proves exactly this classification:

```text
e=4..7:    no feasible S
e=8..11:   exactly the two parity halves
e=12..15:  no feasible S
```

## Why naive exact search is not the route

A quick exact backtracking attempt for `k=8` (`n=32`) using the determinant
condition on every `k+1=9` subset pruned too slowly to be useful.  Random
sanity checks found no no-full singleton-tail counterexample at:

```text
n=32, k=8, q=97,  2000 random no-full S
n=64, k=16, q=193, 500 random no-full S
```

This is only sanity evidence.  The real route should be a classification
argument using the block-interpolation identity (1), not larger brute force.

## Impact on #396

If the general dyadic tail lemma is proved, then the Note 0333 primitive
no-full theorem lifts from the `L2=(16,4)` base model to arbitrary dyadic
block size in the singleton-side case:

```text
mixed support
  => singleton residual side c x^e
  => no-full saturated S would force tail_S(x^e)=0
  => impossible by the scale-lift lemma.
```

That would supply the missing local input for the broader dyadic component
theorem from Notes 0318--0322.  The remaining work would then be to show that
general-f non-full components reduce to this singleton-side primitive case,
two-block components, single-substitution defect roots, or dyadic descent.
