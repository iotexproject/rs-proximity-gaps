# Note 0361 — Issue #404 finite-orbit open theorem

> **Note number history**: filed as Note 0314 on the `issue-404`
> branch; renumbered to 0361 on `main` to avoid collision with the
> existing `0314-rate-eighth-lift-consistency` /
> `0314-gap-B-multi-prime-branch-certification` content. Cross-references
> to "Notes 0312, 0313" inside the body refer to the issue-404 branch
> trail and were not separately absorbed; they are available at
> `origin/issue-404` for the full provenance chain.

**Branch:** `issue-404`
**Date:** 2026-05-01
**Status:** paper-safe finite certificate layer after Note 0313 (branch numbering).

## Executive summary

Notes 0312--0313 reduce the three-position sparse-branch problem at the first
proxy `(n,k,c)=(16,4,3)` to a finite support-orbit classification.  This note
records the theorem statement that is now supported by deterministic
certificates:

> Among the `1379` raw codimension-one support orbits in the `(16,4,3)` proxy,
> exactly `313` orbit-best branches are leading.  They are exactly the branches
> forcing eight distinct alpha values.  Every such branch has a nonempty
> Zariski-open subset with exact sparse endpoint supports, `joint=True`,
> `S*=10`, and finite `K`.

This is not the full Paper 2 sparse-worst conjecture.  It is the finite-orbit
open theorem needed to support the Paper 2 / Paper 3 codimension-composition
story without the false dense-exclusion route.

## Certificate files

The leading-orbit certificate table is:

```text
notes/data/issue404_forced8_leading_certificates.csv
```

It has one row for each of the `313` leading support orbits.  Each row records:

```text
orbit_left, orbit_right, left, right, H, left_coeffs, right_coeffs, K, Sstar, joint
```

The larger JSON audit files are:

```text
notes/data/issue404_forced_alpha_census_full.json
notes/data/issue404_orbit_best_exact_audit.json
```

The deterministic verifier is:

```bash
python3 notes/scripts/issue404_verify_forced_alpha_separation.py
```

It recomputes raw branches, forced alpha counts, `K`, `S*`, and `joint` for all
`1379` orbit-best records.  Current output:

```text
forced_alpha_separation=PASS
orbits=1379
separation={(0, False): 564, (1, False): 502, (8, True): 313}
```

A second verifier records the support geometry behind the separation:

```bash
python3 notes/scripts/issue404_support_geometry_audit.py
```

Output:

```text
support_geometry_audit=PASS
orbit_best_geometry:
forced_alpha=0: raw=8, |support_inter|=8, |support_union|=16, leading=False
forced_alpha=1: raw=8, |support_inter|=8, |support_union|=16, leading=False
forced_alpha=8: raw=8, |support_inter|=2, |support_union|=10, leading=True
all_raw_branch_geometry:
|support_inter|=8, |support_union|=16: 4538
|support_inter|=2, |support_union|=10: 2616
```

## Why each certificate row gives a Zariski-open branch

Fix a row in the certificate table.  The row specifies:

- ordered sparse supports `A,B`;
- a right-coefficient hyperplane `H`;
- one exact-support coefficient point over `F_193`;
- `K`, `S*`, and `joint` values at that point.

The following conditions are Zariski-open in the five-dimensional branch
parameter space `(a_0,a_1,a_2,b_0,b_1,b_2)\cap H`:

1. all six endpoint coefficients are nonzero;
2. the eight forced-incidence denominators are nonzero;
3. the eight forced alpha values are pairwise distinct;
4. no common support of size `w=9` exists (`joint=True`);
5. the joint support span has minimal size exactly `S*=10`;
6. no extra alpha beyond the finite checked set appears, when exact `K` is
   required.

The verifier point satisfies these open conditions over `F_193`.  Since
`193 ≡ 1 (mod 16)`, the primitive 16-th root specialization is valid.  A
nonzero value after this reduction certifies that the corresponding polynomial
inequality is not the zero polynomial over the cyclotomic coefficient ring.
Therefore each certificate row defines a nonempty Zariski-open branch in
characteristic zero and in all compatible characteristics outside the finite
bad-prime set.

## Compressed structure

The `313` leading rows use only seven right-hyperplane shapes:

```text
b0=b2                         110
b1=b2                          90
b0=b1                          69
b0-b1+b2=0                     25
b0-b1-9b2=0                     9
b0-b1-b2=0                      9
b0-9b1-b2=0                     1
```

Their exact `K` values are:

```text
K=8:   13
K=9:  250
K=10:  45
K=11:   5
```

Every leading orbit has `S*=10` and `joint=True`.

The non-leading orbit-best regimes are:

```text
forced_alpha=0: 564 orbits, all non-leading
forced_alpha=1: 502 orbits, all non-leading
```

Most non-leading records have `S*=12`; the rest have `S*=11`.  None has
`S*=10`.

The support-union audit gives the structural reason.  Branches with a
`10`-point support union are the only branches that can support the leading
`S*=10` component.  On a nonempty open subset of such branches, the eight raw
incidences have nonzero denominators and pairwise distinct alpha values.  A
special coefficient point on the same branch can still drop to fewer observed
forced alphas; that is a closed degeneracy, not a different branch geometry.

The non-eight branch geometry has eight raw supports whose union is the full
`16`-point domain, so those raw incidences do not by themselves define a
leading `S*=10` joint support span.

This is not just an orbit-best artifact.  Across all `7154` raw count-eight
branches, the support geometry has exactly two types:

```text
leading-capable geometry: |support_inter|=2, |support_union|=10  (2616 branches)
non-leading geometry:     |support_inter|=8, |support_union|=16  (4538 branches)
```

## The current theorem boundary

This note gives a finite-orbit, certificate-backed theorem at the first proxy.
The remaining gap for a handwritten proof is not another computation; it is the
structural explanation of the observed trichotomy:

\[
  \mathrm{forced\_alpha}\in\{0,1,8\}.
\]

A clean paper proof should show:

1. if the eight raw supports have full domain union, then the branch is
   generically non-leading (`S*>=11`);
2. if the eight raw supports have `10`-point union, then the eight incidence
   equations force distinct alpha values on a nonempty open subset; and
3. the `10`-point-union case is covered by the seven hyperplane templates
   above after support-orbit canonicalization.

Until that structural proof is written, the honest claim is:

> Issue #404 is finite-certificate closed at `(16,4,3)`, but not yet
> handwritten-unconditional for all three-position sparse supports.
