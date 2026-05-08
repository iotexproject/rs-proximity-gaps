# Note 0362 — Issue #404 five complement-family reduction

> **Note number history**: filed as Note 0315 on the `issue-404`
> branch; renumbered to 0362 on `main` to avoid collision with
> existing `0315-gap-B-cycle3-parity-aligned-c4` content.
> Cross-references to "Note 0314" inside the body refer to the
> issue-404 branch trail and correspond on `main` to Note 0361
> (`issue404-finite-orbit-open-theorem`).

**Branch:** `issue-404`
**Date:** 2026-05-01
**Status:** structural compression after Notes 0313--0314 (branch numbering; Note 0314 = Note 0361 on `main`).

## Executive summary

The raw support-orbit count in Note 0312 looked too large:

```text
7154 raw count-eight branches
1379 support orbits
```

The right invariant is not the endpoint support pair.  It is the family of
eight weight-`w` complements attached to a raw codimension-one branch.  After
canonicalizing this eight-complement family by cyclic shifts, there are only
five family types.

This is the best current handwritten-proof entry point for Issue #404:

> classify five complement-family types, not 1379 endpoint-support orbits.

## Five-family census

Reproducible command:

```bash
python3 notes/scripts/issue404_complement_family_census.py \
  --json-out notes/data/issue404_complement_family_census.json
```

Result:

```text
complement_family_census=PASS
families=5
raw_count_eight_branches=7154
support_union_hist={10: 1, 16: 4}
family_branch_count_hist={408: 1, 560: 1, 1140: 1, 2430: 1, 2616: 1}
```

Deterministic verifier:

```bash
python3 notes/scripts/issue404_verify_complement_families.py
```

Output:

```text
complement_family_certificate=PASS
families=5 raw_count_eight_branches=7154
count=2616 |comp_inter|=6 |comp_union|=14 |support_inter|=2 |support_union|=10
count=408  |comp_inter|=0 |comp_union|=8  |support_inter|=8 |support_union|=16
count=560  |comp_inter|=0 |comp_union|=8  |support_inter|=8 |support_union|=16
count=1140 |comp_inter|=0 |comp_union|=8  |support_inter|=8 |support_union|=16
count=2430 |comp_inter|=0 |comp_union|=8  |support_inter|=8 |support_union|=16
```

The support geometry split by family is:

```text
four non-leading families:
  |comp_inter|=0, |comp_union|=8,
  |support_inter|=8, |support_union|=16

one leading-capable family:
  |comp_inter|=6, |comp_union|=14,
  |support_inter|=2, |support_union|=10
```

The unique leading-capable family accounts for all `2616` raw branches with
`10`-point support union.  The other four families account for all `4538` full
domain-union raw branches.

There is an even simpler normal form:

- the unique leading-capable family is `core + one mover`, where
  `core={0,2,4,8,10,12}` and the mover runs through the eight odd positions;
- each of the four non-leading families is `union - one deleted point` for an
  eight-point union.

Thus the geometric split is not accidental.  It is the difference between
adding one of eight movers to a fixed six-point complement core versus deleting
one point from an eight-point complement union.

## Canonical leading-capable family

One cyclic representative of the leading-capable complement family is:

```text
(0,1,2,4,8,10,12)
(0,2,3,4,8,10,12)
(0,2,4,5,8,10,12)
(0,2,4,7,8,10,12)
(0,2,4,8,9,10,12)
(0,2,4,8,10,11,12)
(0,2,4,8,10,12,13)
(0,2,4,8,10,12,15)
```

These complements have common core

```text
(0,2,4,8,10,12)
```

and the moving coordinate runs through the eight positions outside the
10-point support union.  Equivalently, the associated eight weight-`w` supports
share a 2-point intersection and lie in one 10-point union.

This is exactly the geometry needed for `S*=10`.

## Non-leading families

The four non-leading complement-family types all have:

```text
|comp_inter|=0, |comp_union|=8,
|support_inter|=8, |support_union|=16.
```

So their eight raw incidences sweep the whole domain rather than one leading
10-point support union.  In orbit-best exact audit they produce only:

```text
forced_alpha=0 or forced_alpha=1,
S*=11 or S*=12,
low K.
```

## Proof target after this reduction

The next proof should avoid endpoint-support enumeration entirely.  Prove:

1. every raw count-eight codimension-one branch has one of the five cyclic
   complement-family types above;
2. four types are full-union families and hence generically non-leading;
3. the remaining core-plus-eight-movers type gives the leading-capable
   `10`-union geometry; and
4. on a nonempty open subset of the leading-capable type, the eight alpha
   values are distinct and no extra bad incidence destroys finiteness.

This is now a realistic finite combinatorial proof.  It is still not the full
universal Paper 2 sparse-worst theorem, but it is much closer than the raw
1379-orbit formulation.

## Nonzero-syndrome support caveat

At `(n,k)=(16,4)` with the current syndrome convention, exponent `4` has zero
syndrome.  Thus the inclusive support pool `range(k,n)` contains one
codeword/zero-syndrome coordinate.  This is harmless for the finite atlas, but
it should not be hidden when translating the classification into a paper proof.

Running the same complement-family census on the strictly nonzero syndrome
exponents `5,...,15` gives:

```bash
python3 notes/scripts/issue404_complement_family_census.py \
  --min-exp 5 \
  --json-out notes/data/issue404_complement_family_census_nonzero.json
```

```text
support_pairs=27225
families=3
raw_count_eight_branches=2464
support_union_hist={10: 1, 16: 2}
family_branch_count_hist={204: 1, 928: 1, 1332: 1}
```

The unique leading-capable geometry survives unchanged:

```text
|support_inter|=2, |support_union|=10, |comp_inter|=6, |comp_union|=14
```

The two extra family types in the inclusive five-family census are therefore
non-leading artifacts of allowing exponent `4` in sparse supports.  A clean
handwritten theorem should either quotient out the codeword coordinate or state
the inclusive convention explicitly.
