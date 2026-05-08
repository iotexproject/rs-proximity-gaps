# Note 0364 -- Issue #419: shape-level certificate for rank-2 parity implication

> **Note number history**: filed as Note 0358 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0364 on `main` because
> Note 0358 on the trunk is `issue396-recursive-one-residue-lift`.
> Cross-references inside the body to "Note 0357" use branch numbering;
> on `main` Note 0357 = Note 0363 (rank2-parity-implication-proof-plan).

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** finite-field shape certificate for the Note 0357 proof plan.

---

## Purpose

Note 0357 reduced the remaining primitive global-attachment gap to:

```text
C(S)+alpha1 M(S)=0, alpha1 != 0, rank(W)=2
    => parity_support(u) and parity_support(v) are singletons and distinct.
```

This note adds a shape-level algebraic certificate for the observed nonzero
alpha support shapes.  It is not another support-panel enumerator.  It treats
coefficients as symbolic variables for a fixed support/component shape and uses
finite-field Groebner saturation to check whether a rank-2 mixed-parity branch
survives.

Script:

```text
notes/scripts/issue419_parity_implication_shape_cert.py
```

Output:

```text
notes/scripts/issue419_parity_implication_shape_cert.all.output.txt
```

---

## Certificate method

For each shape, the script:

1. introduces symbolic coefficient variables `c_i` and symbolic nonzero
   `alpha1=a`;
2. builds `u_alpha,v_alpha` from the quotient-`C4` folded support positions;
3. forms the high-tail no-full equations for the observed component `S`;
4. saturates by `a` and by the rank-2 minors of `W=span(u,v)`;
5. checks whether the saturated ideal is the unit ideal.

For parity-split shapes there are no mixed-parity forbidden factors because the
symbolic support shape already lives in opposite parity eigenspaces.  For
rank-collapse shapes, saturation by rank-2 minors returns the unit ideal.

---

## Results

The six representative shapes from the q=97 four-support and q=193
five-support full-panel audits all behave as predicted.

### Rank-collapse shapes

```text
q97-rank-collapse-same-folded:
  equations=5, rank2_minors=2, rank2_branch_empty=True

q97-rank-collapse-same-parity:
  equations=8, rank2_minors=1, rank2_branch_empty=True

q193-rank-collapse-same-folded:
  equations=4, rank2_minors=2, rank2_branch_empty=True

q193-rank-collapse-same-parity:
  equations=8, rank2_minors=1, rank2_branch_empty=True
```

Interpretation: these nonzero-alpha shapes have solutions, but all such
solutions vanish after saturating by `rank(W)=2`.  They are purely rank-collapse
branches.

### Rank-2 parity-split shapes

```text
q97-half-turn-parity-split:
  equations=7, rank2_minors=4, rank2_branch_empty=False,
  parity_forbidden_factors=0

q193-half-turn-parity-split:
  equations=8, rank2_minors=4, rank2_branch_empty=False,
  parity_forbidden_factors=0
```

Interpretation: the only surviving rank-2 shapes are already parity-separated,
hence have the half-turn row-span stabilizer closed by Notes 0347--0351.

---

## What this proves and what remains

This certificate proves the rank-2 parity implication for the observed
nonzero-alpha support-shapes in the base panels, with symbolic coefficients.
It is stronger than enumerating stable random coefficients: rank-collapse is
removed by actual rank-minor saturation.

It does **not** yet prove the all-shape theorem.  The remaining mathematical
step is to show that the no-full affine equations admit no additional
rank-2 mixed-parity support shapes beyond the certified templates.

The proof path is now precise:

```text
full-panel mechanism classifier
  -> observed nonzero-alpha shapes only
  -> shape-level symbolic rank saturation
  -> rank-2 survivors are parity-split
  -> half-turn branch closed by Notes 0347--0351.
```

To close #419 completely, the next note should replace "observed shapes only"
with a structural support-shape lemma from the quotient-`C4` dual parity system.
