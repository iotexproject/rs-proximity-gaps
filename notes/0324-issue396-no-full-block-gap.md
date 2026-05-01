# Note 0324 -- Issue #396: the remaining gap is no-full-block exclusion

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** superseded by Note 0325.  This note correctly isolated the
no-full-block gap, but the naive exclusion stated below is false in rank-1 /
deeper-dyadic cases.

Artifacts:

- `notes/scripts/issue396_block_occupancy_gap.py`
- output: `notes/scripts/issue396_block_occupancy_gap.output.txt`

---

## Summary

Notes 0319--0323 explain every saturated component that contains a complete
cyclotomic block `C_r`:

- two complete blocks give a quarter-pair component;
- one complete block plus `k` extra roots is controlled by defect polynomials;
- full-code rows are charged separately.

Therefore the real remaining theorem is not vague.  The first candidate was:

> **No-full-block exclusion.**  For non-full two-round folded row spans coming
> from above-Johnson `f`, there should be no saturated `2k`-component `S`
> with `|S cap C_r| < k` for every `r=0,1,2,3`, except possibly through a
> deeper dyadic refinement that can be charged recursively.

At `(n,k)=(16,4)`, the current panels have no such component.  Note 0325 then
found a no-full-block counterexample outside the panel:
`support=(16,25,56), alpha1=84`.  It is rank-1 and descends to the antipodal
quotient, so the corrected target is recursive dyadic descent rather than
absolute no-full-block exclusion.

---

## Linear-algebra formulation

Let `A_r = S cap C_r` and `t_r=|A_r|`, so

```text
t_0+t_1+t_2+t_3 = 2k.
```

For a polynomial `P`, let `R_r(P)` be the local degree-`<k` representative on
`C_r` from Note 0323.  The condition

```text
P|_S in RS_k(S)
```

is equivalent to the existence of a single `R in RS_k(L)` such that

```text
R(x)=R_r(P)(x)  for all x in A_r,  r=0,1,2,3.
```

Equivalently,

```text
R in intersection_r ( R_r(P) + I(A_r) ),
```

where

```text
I(A_r) = { Q in F_q[x]_{<k} : Q vanishes on A_r }.
```

`I(A_r)` has dimension `k-t_r`.  Thus each saturated component asks that four
affine subspaces of the same `k`-dimensional polynomial space intersect.

For a row span `W=span(u,v)`, the same intersection condition must hold for
both `u` and `v`.

---

## Why complete blocks are easy

If `t_r=k`, then `A_r=C_r` and `I(A_r)=0`.  The global interpolant is forced:

```text
R = R_r(P).
```

All other conditions become pointwise roots of

```text
R_s(P)-R_r(P)
```

on the other blocks.  This is exactly the Note 0323 defect-root model.  The
two-block case is the subcase where some other `t_s=k`.

So complete-block components are no longer hard.

---

## Why no-full-block components are the hard case

If every `t_r<k`, then none of the four affine constraints pins down `R`.
The component condition is an intersection-of-affine-subspaces problem rather
than a root-count problem from one fixed base block.

The expected proof has to show that, for two-round folded above-Johnson row
spans, this affine intersection cannot happen at total size `2k` unless the
sets `A_r` themselves have dyadic structure.  In more concrete terms:

```text
R_r(P) - R_s(P)
```

is given by the quotient-`C4` coefficient equations from Note 0323.  A
no-full-block component would force these local-difference polynomials to
vanish on a distributed pattern of roots across all four blocks.  This is the
right place for a cyclic uncertainty / sparse Fourier support theorem, but
now the theorem has a precise finite-dimensional form.

---

## Empirical audit at `(16,4)`

The occupancy audit counts every non-full saturated component in the current
#396 panels by the tuple

```text
(|S cap C_0|, |S cap C_1|, |S cap C_2|, |S cap C_3|).
```

Saved output gives:

```text
grand_rows={empty-row:2495, full-row:8, nonfull-nonempty:1164}
no_full_component_examples=[]
```

The observed non-full occupancies are only:

- quarter-pairs, e.g. `(4,0,4,0)` and `(0,4,0,4)`;
- one-substitution near-cosets, e.g. `(4,1,3,0)` and `(0,3,1,4)`;
- isolated finite quarter-pairs such as `(4,4,0,0)`.

Every non-full component contains at least one complete block.

---

## Updated #396 proof target

With Notes 0321--0324, #396 has been reduced to the following theorem stack:

1. **Block normal form:** proved in Note 0323.
2. **Complete-block closure:** proved by Note 0323 plus the defect-root lemma
   from Note 0321.B.
3. **Full-code rows:** charge by the projective/orbit mechanism of
   Notes 0310--0312.
4. **No-full-block exclusion:** still open; this is now the single hard
   mathematical bone.

This is the point at which brute-force enumeration has stopped being the
right primary tool.  The next useful attack should prove or disprove the
no-full-block exclusion in the affine-subspace formulation above.
