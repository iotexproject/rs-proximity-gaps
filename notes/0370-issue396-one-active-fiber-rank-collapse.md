# Note 0370 -- Issue #396: one-active one-residue fibers are rank collapse

> **Note number history**: filed as Note 0348 on the `issue-396`
> branch; renumbered to 0370 on `main` to avoid collision with already-
> absorbed content at slot 0348. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** structural closure of the high-multiplicity one-active branch from
Notes 0343--0344.

---

## Statement

Let `L=<omega>` have order `4k`, with quarter blocks `C_i` cut out by `x^k`.
Suppose one actual residual direction has the one-residue form

```text
P(x) = x^a Q(x^k),        0 <= a < k,        deg Q < 4.
```

Let `S subset L`, `|S|=2k`, be a candidate saturated component.  If the
selected points of `S` meet only one scalar value level of `Q(x^k)`, say

```text
Q(x^k) = lambda        for every x in S,
```

then

```text
P|_S = (lambda x^a)|_S,
```

and `lambda x^a` has degree `< k`.  Hence this row direction is already in
`RS_k(S)`.

Consequently the quotient residual span on `S` has dimension at most one.  In
the primitive projection sieve of Note 0342, this is exactly a rank-collapse
case, not a remaining primitive rank-2 no-full branch.

---

## Why the high-multiplicity cases are covered

Note 0343 left open the case where a one-residue C4 fiber supports `S` on a
single high-multiplicity value level.  In the base quotient classification of
Note 0344 this appears as

```text
three equal block values, one exceptional block value,
S avoids the exceptional block.
```

The same argument is not specific to the base quotient.  It only uses the
fact that the chosen support points see one scalar value of `Q(x^k)`.  The
multiplicity of that value can be three blocks, four blocks, or a larger
coalesced value level after specialization; in all cases the restriction of
`P` to `S` is the restriction of the low monomial `lambda x^a`.

Thus the phrase "check the high-multiplicity one-active branch against the
second row direction" should be read as follows:

```text
one-active row in RS_k(S)
  => remove that row in the quotient by RS_k(S)
  => the remaining saturation condition has residual rank <= 1.
```

The second row may still be non-low globally, but it is then a rank-one
saturation problem after quotienting by the low row on `S`.  It cannot be the
primitive rank-2 obstruction isolated in Note 0342.

---

## Consequence for the one-residue caveat

Combining Notes 0343, 0344, 0347, and this note gives the current split:

1. exactly two active scalar value levels are impossible by the root budget of
   Note 0343;
2. one active scalar value level is rank collapse by the lemma above;
3. the base quotient `>=3` active branch is the rank-2 separating lambda plane
   of Note 0344;
4. once that separating branch is in an order-`d` orbit-union quotient with
   `k/d=4`, Note 0347 forces one more dyadic stabilizer descent.

So the only one-residue work still outside the existing charges is the
**entry lemma**:

```text
arbitrary high-scale rank-2 separating one-residue branch
  => enters an order-d orbit-union quotient, eventually with k/d=4.
```

This is a sharper target than the earlier "one-active or separating" caveat.
The one-active alternative is no longer an independent obstruction.
