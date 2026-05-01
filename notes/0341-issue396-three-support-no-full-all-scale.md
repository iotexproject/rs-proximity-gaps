# Note 0341 -- Issue #396: all-scale no-full theorem for strict 3-support rows

> **Note number history**: filed as Note 0337 on the
> `issue-419-l3-attachment` branch; renumbered to 0341 on `main` to avoid
> collision with `0337-issue396-scale-lift-tail-proof` already on the trunk.
> Cross-references to "Note 0336" refer to the defect-allocation note, now
> Note 0340 on `main`. Cross-references to "Note 0335" (the singleton-tail
> proof) refer to Note 0337 on `main`.

**Date:** 2026-05-01
**Branch:** `issue-396` (originated on `issue-419-l3-attachment`)
**Status:** rigorous consequence of Notes 0333 and 0337 (formerly Note 0335).

---

## Statement

Let the post-two-fold domain have size `4k` and code dimension `k`.  Consider
a legal strict-above-J three-monomial support after two folds, with the usual
`alpha2` split

```text
u-side: j mod 4 in {0,1},
v-side: j mod 4 in {2,3}.
```

After excluding `alpha1=0` zero-row degeneracies, there is no rank-2 saturated
`2k`-component `S` with no full quarter block.

Equivalently, the primitive rank-2 no-full branch for strict 3-supports is
closed at every dyadic scale.

---

## Proof

There are only two side-distribution types for a three-monomial support.

### 1. Side-pure support

If all three monomials are on the `u` side, then `v=0`.  If all three are on
the `v` side, then `u=0`.  In either case the row span has rank at most one,
so it is not a rank-2 primitive obstruction.

### 2. Mixed support

If the support is mixed, the side counts are `(1,2)` or `(2,1)`.  Therefore
one row-basis direction is a single folded monomial

```text
c x^e
```

with `c != 0` after the `alpha1=0` zero-row quotient.  For a legal
strict-above-J support, the folded exponent of this singleton residual lies
in the tail interval

```text
k <= e < 4k.
```

If `S` were saturated for the rank-2 row span, this singleton row direction
would restrict to `RS_k(S)`.  Since `c` is nonzero, this is exactly the
condition

```text
x^e|_S in RS_k(S).
```

Note 0335 classifies all such `|S|=2k` equalities: the only possible cases are
the two parity halves for exponents `e=2k+r`, and both parity halves contain
two complete quarter blocks.  Hence no saturated `S` with no full quarter
block can occur.

Thus the mixed side is impossible, and the side-pure side is rank-deficient.
This proves the claim. ∎

---

## Relation to the finite certificates

Notes 0328--0330 observed over seven primes that every no-full symbolic-alpha
survivor after quotienting `alpha1=0` is side-pure, hence rank deficient.  The
argument above explains that pattern without a prime-specific computation:

```text
mixed strict 3-support
  => singleton residual side
  => Note 0335 tail classification
  => parity half only
  => full quarter blocks
  => no no-full component.
```

The previous GB saturation certificates remain useful as finite checks of the
base equations, but they are no longer needed as the conceptual proof for the
strict 3-support no-full branch.

---

## What remains for #396

This note does not close arbitrary general-`f` rows.  It closes the complete
strict 3-support primitive no-full branch at all dyadic scales.

The remaining general-`f` issue is exactly the multi-term defect-allocation
problem of Note 0336: when both sides contain at least two residual terms, the
singleton-tail argument no longer applies, and one must prove the rank/defect
obstruction for the four quotient-`C4` local representative maps.
