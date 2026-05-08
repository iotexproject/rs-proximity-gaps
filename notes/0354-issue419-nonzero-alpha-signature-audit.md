# Note 0354 -- Issue #419: nonzero-alpha candidate signatures

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** structural audit of the remaining primitive branch.

---

## Purpose

Note 0353 showed that the primitive branch classifier finds no primitive
survivor on the 4-support and 5-support panels, and that random 6/7/8-support
stress mostly produces only `alpha1=0` candidates.  This note audits the
nonzero-alpha candidates that do exist in the full 5-support panel.

Artifact:

```text
notes/scripts/issue419_nonzero_alpha_signature_audit.py
```

Command:

```text
python3 notes/scripts/issue419_nonzero_alpha_signature_audit.py \
  --q 193 --support-size 5 --workers 20 --chunksize 32 --progress 500000
```

---

## Result

The scalar totals match the 5-support classifier:

```text
candidate_subsets = 316,422,821
alpha_zero        = 316,422,482
nonzero-alpha     = 339
```

All 339 nonzero-alpha candidates are already charged:

```text
rank<2     = 259
stabilizer = 80
primitive  = 0
```

The stabilizer bucket has exactly one row-shape type, up to cyclic shift:

```text
support side count:       (2,3) or (3,2)
folded support shape:     one doubled folded exponent + three singleton folded exponents
row shape:                |supp(u)|=|supp(v)|=2,
                          supp(u), supp(v) each separated by half-turn
row stabilizer:           (0,8)
half-turn profile:        0^3,1^2,2^3
```

This is exactly the half-turn branch closed by Notes 0347--0351.

The rank-collapse bucket has three profile types:

```text
0^3,1^2,2^3 : 224
0^2,1^4,2^2 : 32
0^4,2^4     : 3
```

These are harmless for #419 because `rank(W)<2` is already a charged
degeneracy in Note 0344's theorem statement.

---

## Interpretation

The nonzero-alpha locus is much smaller than the raw candidate count suggests.
At 5-support it is entirely explained by two elementary mechanisms:

1. one residual side vanishes or rows become dependent (`rank<2`);
2. both residual sides become half-turn eigenpairs (`stabilizer`).

No nonzero-alpha candidate with a genuinely primitive rank-2 row span appears.
This suggests the next possible theorem:

> **Nonzero-alpha collapse lemma.**  In the quotient-`C4` defect-allocation
> system, any no-full saturated component with `alpha1 != 0` either collapses
> row rank or forces a half-turn row-span stabilizer, unless it belongs to an
> already charged complete-block / defect-root / singleton-tail family.

This is stronger and cleaner than proving absence of primitive components by
support-size enumeration.  It would combine directly with Note 0351: if
nonzero-alpha forces a half-turn stabilizer, then the weighted quotient closure
charges that branch.

---

## Why this is not yet a proof

The audit is still finite-panel evidence.  It does not prove the collapse
lemma at arbitrary support size or dyadic scale.  However, it identifies the
right algebraic invariant to target: the symbolic-alpha saturation equations
should have no solutions with simultaneous conditions

```text
alpha1 != 0,
rank(W)=2,
trivial dyadic row-span stabilizer.
```

The next proof step is to express that claim as a determinant/rank statement
in the quotient-`C4` local representative maps from Note 0323 and the defect
spaces `Z_i(A_i)` from Note 0340.

---

## 4-support comparison over `F_97`

The same audit on the full 4-support panel gives the same structural shape:

```text
candidate_subsets = 47,463,680
alpha_zero        = 47,463,328
nonzero-alpha     = 352
rank<2            = 336
stabilizer        = 16
primitive         = 0
```

Every nonzero-alpha 4-support candidate has half-turn profile `0^3,1^2,2^3`.
The unique stabilizer row shape is again

```text
|supp(u)|=|supp(v)|=2,
supp(u), supp(v) each half-turn separated,
row_stabilizer=(0,8).
```

So the 4-support and 5-support panels agree on the relevant non-rank-collapse
mechanism: nonzero-alpha survivors are precisely the half-turn row-span
stabilizer bucket closed by Note 0351.
