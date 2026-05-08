# Note 0356 -- Issue #396: base one-residue lambda-space classification

> **Note number history**: filed as Note 0344 on the `issue-396` branch;
> renumbered to 0356 on `main` to avoid collision with `0344-issue419-l3-global-attachment-drill`. Cross-references to "Notes 0343, 0344, 0345, 0346, 0347" inside the body refer to the
> branch numbering and correspond on `main` to Notes 0343 (unchanged),
> 0356, 0357, 0358, 0359 respectively for the issue-396 sequence.

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** base-layer classification of the remaining one-residue C4-fiber
caveat from Note 0343.

Artifacts:

- `notes/scripts/issue396_one_residue_lambda_space.py`
- `notes/scripts/issue396_one_residue_lambda_space.q193.output.txt`

---

## Purpose

Note 0343 reduced the one-residue caveat to two cases:

```text
P=x^a Q(x^k),  deg Q<4,
S either lies in one high-multiplicity value level
  or meets at least three scalar value levels.
```

The second alternative could still be a genuine primitive obstruction.  This
note checks the base quotient `L2=(16,4)` without fixing the scalar values of
`Q`.  The point is to classify the whole lambda-space

```text
lambda_i = Q(zeta^i),       i=0,1,2,3,
```

rather than test a few sample values.

---

## Linear lambda-space test

For fixed `a` and a no-full `8`-set `S subset L2`, solve the homogeneous
linear system

```text
p(x) = lambda_i x^a,        x in S cap C_i,        deg p < 4,
```

in the variables

```text
(p_0,p_1,p_2,p_3, lambda_0,lambda_1,lambda_2,lambda_3).
```

Project the solution space to the four `lambda` coordinates.  The forced
equality partition of that projection tells which block-value patterns can
occur:

- `((0,1,2,3),)` means only constant `Q` survives, hence the row is low and
  is not an above-Johnson residual obstruction.
- `((i,), (j,k,l))` means a three-equal/one-distinct `Q` can occur, but the
  no-full set uses no point in the exceptional block, so the active selected
  value level is the high-multiplicity one.
- `((0,), (1,), (2,), (3,))` means no pair of lambda coordinates is forced
  equal.  In the base run this projection has rank `2`, not rank `4`; it is a
  separating lambda plane, not the whole four-dimensional lambda space.  Since
  a two-dimensional subspace over `F_193` is not covered by the six equality
  hyperplanes unless it is contained in one of them, generic vectors on this
  plane still have at least three active value levels.

The script performs this exact linear classification over `F_193`.  Since the
system is linear and the support points are the fixed `16`th roots, this is a
base quotient certificate, not a random value sample.

---

## Output summary

The run enumerates all no-full `8`-subsets of `L2=(16,4)` and all
`a=0,1,2,3`:

```text
q=193, n=16, k=4
nonzero_lambda_cases=43584
by_a={0: 10896, 1: 10896, 2: 10896, 3: 10896}
```

After discarding the constant-low partition `((0,1,2,3),)`, every nonconstant
case is one of the following two mechanisms.

### Mechanism 1: high-multiplicity single active value

The forced partition is one singleton exceptional block plus the other three
blocks equal:

```text
((0,), (1,2,3)),  ((0,1,2), (3)),
((0,1,3), (2)),  ((0,2,3), (1)).
```

In every such row, the occupancy has zero in the exceptional block and
occupancy `(2,3,3)` in the equal-value blocks, up to permutation.  Thus the
selected set meets only the high-multiplicity value level.  This is exactly
the first remaining case from Note 0343, not the `>=3`-active-value case.

### Mechanism 2: order-2 stabilized separating lambda plane

The only partition with no forced lambda equalities is

```text
((0,), (1,), (2,), (3,))
```

and the complete output line is:

```text
occupancy=(2,2,2,2)
lambda_rank=2
forced_partition=((0,), (1,), (2,), (3,))
order2_stabilized=True
count=64
example=(0,1,2,3,8,9,10,11)
```

The count `64` is `4` choices of `a` times `16` selected sets.  Each selected
set is invariant under the order-2 action `x -> -x`, equivalently index
translation by `8` in `L2`.  For example,

```text
(0,1,2,3,8,9,10,11)
```

is a union of four opposite pairs.  The other fifteen examples choose one
opposite pair in each quarter block.  Therefore the only base-layer
`>=3`-active-value one-residue possibility is not primitive: it is charged to
the dyadic stabilizer/descent branch of Notes 0310 and 0342.

---

## Consequence for the one-residue caveat

At the base quotient `L2=(16,4)`, the one-residue C4-fiber caveat has no
primitive `>=3`-active-value survivor.  Nonconstant one-residue saturated
no-full sets are exactly:

```text
three-equal/one-empty-block high-multiplicity value level,
or
order-2 stabilized balanced opposite-pair sets.
```

Thus the remaining all-scale proof target is sharper than Note 0343:

> Prove that the all-scale lift of the separating-lambda-plane case forces the
> same order-2 dyadic stabilizer whenever the lambda projection is not
> contained in a two-value equality pattern, and then handle only the
> high-multiplicity one-active-value branch against the second row direction.

This is a real narrowing of the hard branch.  It eliminates the vague
`>=3 active value levels` caveat at the base layer and identifies its expected
scale-lift mechanism.

Update after Note 0345: the first lift check at `L=(32,8)` supports this
mechanism.  Within the balanced order-2-stable family, the only nonconstant
separating lambda planes are already stable under the deeper order-4 dyadic
action.  Thus the likely all-scale proof is recursive stabilizer descent, not
a new value-level incidence family.
