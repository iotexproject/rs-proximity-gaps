# Note 0333 -- Issue #396: no-full primitive branch closed at the legal L2 base

## Purpose

This note stitches Notes 0326--0332 into a single theorem statement.  The
legal `(64,16)->L2=(16,4)` strict-above-Johnson 3-support panel has no
primitive rank-2 no-full saturated component.  The remaining #396 work is no
longer this base branch; it is the scale/general-f dyadic component theorem.

Update: Note 0337 proves the scale-lift of the monomial-tail obstruction for
arbitrary block size `k`, so the singleton residual side is now closed beyond
the `L2=(16,4)` base panel.

## Setup

After two folds, the base model is

```text
L2=(16,4),      |S|=8,      support window j in [16,64).
```

The four residue classes modulo `4` are the quarter blocks.  A component
`S` is no-full if it does not contain an entire quarter block.

For a fixed 3-support and fixed coefficients, the residual row pencil is

```text
W(alpha1)=span(u_alpha, v_alpha).
```

A saturated component is an 8-subset `S` such that

```text
u_alpha|_S in RS_4(S),     v_alpha|_S in RS_4(S).
```

Equivalently, both degree-`4..7` tails after reduction modulo
`g_S(x)=prod_{s in S}(x-s)` vanish.

## Theorem 0333.A -- legal no-full candidates are one-sided

In the legal support window, after removing the `alpha1=0` zero-row family, a
no-full saturated component candidate forces the support to be side-pure:

```text
support subset {j: j mod 4 in {0,1}}     or
support subset {j: j mod 4 in {2,3}}.
```

Consequently either `v_alpha=0` or `u_alpha=0`; the row span has rank at most
one.  In particular, no no-full component can be a primitive rank-2
obstruction.

### Proof

Split the four folded quadrants into the two `alpha2` sides:

```text
u-side: j mod 4 in {0,1},
v-side: j mod 4 in {2,3}.
```

If the 3-support is side-pure, one residual row is identically zero, so the
rank is at most one.

It remains to exclude mixed support.  A mixed 3-support has one side with a
single residual monomial.  Since we have quotient by `alpha1=0`, that singleton
coefficient is nonzero.  The folded exponent of that singleton is

```text
e=floor(j/4),     4 <= e < 16.
```

If a no-full `S` were saturated, the singleton row would have to lie in
`RS_4(S)`, i.e.

```text
tail_S(x^e)=0.
```

Note 0332 proves the exact cyclotomic tail lemma over
`Z[zeta_16]=Z[t]/(t^8+1)`: for every no-full 8-subset `S` and every
`4 <= e < 16`, `tail_S(x^e) != 0`.

Therefore no mixed support survives the no-full equations.  All surviving
no-full candidates are side-pure, hence rank at most one. ∎

## Certificate trail

The theorem is supported by the following independent checks and reductions.

1. Note 0326: symbolic-alpha certification over seven primes found zero
   primitive rank-2 no-full candidates in the legal `C(48,3)` panel.
2. Note 0327: every legal no-full candidate collapses by one-sided rank loss,
   not by hidden proportionality.
3. Notes 0328--0329: Singular saturation after quotienting `alpha1=0` and
   saturating away `u=0`, `v=0` gives the unit ideal over all seven primes.
4. Note 0330: the nonzero-alpha survivors are empirically all side-pure.
5. Note 0331: mixed support reduces to the monomial-tail obstruction
   `tail_S(x^e)=0`.
6. Note 0332: exact cyclotomic classification proves the monomial-tail
   obstruction without finite-field dependence.
7. Note 0337: the same monomial-tail obstruction scale-lifts to arbitrary
   `n=4k` by root counting, with only parity-half equality cases.

The strongest new mathematical input is Note 0332, which classifies all
8-subsets on which `x^e` can restrict to degree `<4`:

```text
e=4..7:    none
e=8..11:   only the even and odd parity halves
e=12..15:  none
```

The two parity halves contain full quarter blocks, so they are irrelevant for
the no-full branch.

## What this closes

Closed:

```text
legal strict-above-J 3-support
  + no-full saturated component
  + alpha1 != 0
  => rank(W(alpha1)) <= 1.
```

Together with the `alpha1=0` zero-row family, this eliminates primitive
rank-2 no-full obstructions in the legal `L2=(16,4)` base model.

## What remains for paper2/P3

This does **not** by itself close the full paper2 P3 general-f K-bound.  The
remaining theorem is the scale/general-f dyadic component statement from
Notes 0318--0322:

```text
Every non-full saturated component in the folded general-f row span is charged
to a two-block component, a single-substitution defect-root family, or a
bounded-depth dyadic descent.
```

Note 0337 lifts the singleton-side part from the legal 3-support/L2 model to
arbitrary dyadic block size.  The next hard step is no longer the local
scale-lift; it is to attach that local theorem to the full general-f dyadic
decomposition from Notes 0318--0322.
