# Note 0325 -- Issue #396: no-full-block counterexample is deeper dyadic rank-1

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** falsifies the naive no-full-block exclusion and replaces it with a
recursive dyadic target.

Artifacts:

- `notes/scripts/issue396_no_full_counterexample_search.py`
- output: `notes/scripts/issue396_no_full_counterexample_search.output.txt`
- output: `notes/scripts/issue396_no_full_counterexample_search.skip-rank1.output.txt`

---

## Result

The naive Note 0324 no-full-block exclusion is false.

Searching all strict above-Johnson 3-position supports at `(64,16)->L2=(16,4)`
over `F_193` found:

```text
support=(16,25,56), alpha1=84
S=(0,2,3,5,8,10,11,13), occupancy=(2,2,2,2)
```

This `S` is saturated and has no complete quarter block.

However, the row is rank-1:

```text
u = 64 x^4 + 135 x^6 + 66 x^14
v = 0
```

So this is not a new primitive rank-2 `alpha2`-pencil family.  It is a
degenerate row that must be routed to the existing rank-1 / recursive dyadic
machinery.

---

## Polynomial audit

For the no-full component

```text
S=(0,2,3,5,8,10,11,13),
```

the generator polynomial is

```text
g_S(x)=x^8 + 132 x^6 + 27 x^4 + 114 x^2 + 112.
```

It has only even powers because `S` is a union of antipodal pairs:

```text
(0,8), (2,10), (3,11), (5,13).
```

Reduction gives

```text
u mod g_S = 50 + 22 x^2,
```

so `u|_S` agrees with a degree-`<4` polynomial.

This is exactly a quotient phenomenon.  Since `u` is even, write `y=x^2`.
Then

```text
u(x)=P(y),       P(y)=64 y^2 + 135 y^3 + 66 y^7.
```

The antipodal-pair set `S` projects to four points in the quotient domain of
size `8`, and `P(y)` agrees with the line

```text
50 + 22 y
```

on those four quotient points.  In other words, the no-full component at
`(16,4)` is a full Johnson-sized component after one more dyadic quotient:

```text
(16,4), s=8
  no-full antipodal-pair component
    -> quotient (8,2), s=4 rank-1 component.
```

---

## Consequence

The correct theorem cannot be:

> every non-full saturated component contains a full quarter block.

The correct theorem must be recursive:

> every non-full saturated component is charged either to a complete block at
> the current dyadic level, or to a stabilizer/rank drop that descends to a
> deeper dyadic quotient.

This is consistent with Note 0321's caveat about "bounded-depth iteration",
but the new search shows the caveat is necessary, not optional.

---

## Updated proof stack for #396

1. **Rank-1 rows.**  Route through the existing rank-1 lift machinery
   (Note 0111) or through an explicit quotient recursion.  No-full components
   can occur here and should not be counted as primitive rank-2 obstructions.
2. **Rank-2 rows with nontrivial stabilizer.**  Descend along the stabilizer
   quotient and repeat the component analysis at the smaller dyadic level.
3. **Primitive rank-2 rows.**  Prove the no-full-block exclusion only after
   excluding rank drop and stabilizer quotient cases.
4. **Complete-block rows.**  Use Notes 0321--0323: quarter-pair affine
   equations plus defect-root intruders.
5. **Full-code rows.**  Charge using Notes 0310--0312.

This is sharper than Note 0324.  The hard primitive theorem is smaller, but
the full #396 proof must explicitly include recursive dyadic descent.

---

## Saved search output

```text
Issue #396 no-full-block counterexample search
q=193, L2=(16,4), supports=C(48,3)=17296, workers=12
Scanning all alpha1; full-code rows are skipped.

hist={'counterexample_supports': 1, 'full_rows': 0, 'supports': 347}
first_counterexample={'support': (16, 25, 56), 'alpha1': 84,
 'examples': [((0, 2, 3, 5, 8, 10, 11, 13), (2, 2, 2, 2))],
 'full_rows': 0}
```

The search stopped at the first counterexample by design.

---

## Primitive rank-2 follow-up

The same search was rerun with

```text
ISSUE396_SKIP_RANK1=1
```

so every rank-0/rank-1 row was ignored.  This scans the corrected primitive
rank-2 version of the no-full-block claim.

Saved output:

```text
Issue #396 no-full-block counterexample search
q=193, L2=(16,4), supports=C(48,3)=17296, workers=12
Scanning all alpha1; full-code rows are skipped; skip_rank1=True.
...
hist={'full_rows': 0, 'skipped_rank1': 799504, 'supports': 17296}
first_counterexample=None
```

Thus, across all strict above-Johnson 3-position supports at this scale, every
no-full-block counterexample found by the unrestricted search lies in rank
`<2`.  No primitive rank-2 no-full component appears.

This is the strongest current evidence for the corrected theorem:

> primitive rank-2 rows have no no-full-block saturated components; all
> no-full components are explained by rank/stabilizer descent.
