# Note 0365 -- Issue #419: complete nonzero-alpha shape catalog at base panels

> **Note number history**: filed as Note 0359 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0365 on `main` because
> Note 0359 on the trunk is `issue396-one-residue-quotient-lift-lemma`.
> Cross-references inside the body to "Notes 0356--0358" use branch
> numbering; on `main` they correspond to Notes 0360 / 0363 / 0364
> respectively.

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** complete base-panel shape catalog; no primitive/unclassified shape.

---

## Purpose

Notes 0356--0358 narrowed #419 to a rank-2 parity implication.  The missing
piece was whether the shape-level certificates were only checking a few chosen
examples or all nonzero-alpha support shapes seen in the base panels.

This note records the complete shape catalog for the q=97 four-support and
q=193 five-support panels.

Script:

```text
notes/scripts/issue419_nonzero_shape_catalog.py
```

Outputs:

```text
notes/scripts/issue419_nonzero_shape_catalog.q97.4support.output.txt
notes/scripts/issue419_nonzero_shape_catalog.q193.5support.output.txt
```

---

## q=97 four-support catalog

Full panel:

```text
supports=194580
candidate_subsets=47463680
alpha_zero=47463328
class:rank<2=336
class:stabilizer=16
unique_shapes=15
first_obstruction=None
```

Shape mechanism split:

```text
rank-or-parity-degenerate: 1 shape, 128 candidates
same-folded-cancellation: 13 shapes, 208 candidates
half-turn-parity-split:   1 shape,  16 candidates
```

The single rank-2 shape is the half-turn parity-split template:

```text
((11,), (9,), (8,10), ())
```

with `u` supported on odd quotient exponents and `v` supported on even
quotient exponents.

---

## q=193 five-support catalog

Full panel:

```text
supports=1712304
candidate_subsets=316422821
alpha_zero=316422482
class:rank<2=259
class:stabilizer=80
unique_shapes=24
first_obstruction=None
```

Shape mechanism split:

```text
rank-or-parity-degenerate: 3 shapes,  48 candidates
same-folded-cancellation: 16 shapes, 211 candidates
half-turn-parity-split:   5 shapes,  80 candidates
```

All five rank-2 shapes are half-turn parity-split templates.  The examples in
the output have one row on even quotient exponents and the other row on odd
quotient exponents, with row stabilizer `(0,8)`.

---

## Consequence for the proof target

The base-panel search is now shape-complete, not just example-complete:

```text
nonzero-alpha candidate
  => one of 15 q=97 shapes or 24 q=193 shapes,
  => rank<2 or half-turn parity split,
  => no primitive/unclassified rank-2 shape.
```

Combined with Note 0358, the q=97/q=193 base panels have a symbolic coefficient
certificate for the rank-collapse templates and a direct parity-split form for
all rank-2 templates.

The remaining all-scale theorem is therefore a support-shape classification:
prove from the quotient-`C4` dual parity equations that every nonzero-alpha
rank-2 shape is one of the half-turn parity-split templates.

---

## Next theorem statement

A useful final statement for #419 is:

> **Nonzero-alpha support-shape theorem.**  In the legal quotient-`C4`
> no-full saturated system, after saturating by `alpha1 != 0` and
> `rank(W)=2`, every support shape is half-turn parity split.

The computation now supplies the exact base templates and verifies that no
other shape occurs in the deployment-scale panels.  The remaining proof should
be a structural argument excluding mixed-parity rank-2 shapes before any field
specialization.

---

## ⚠️ UPDATE 2026-05-01 (post-absorption): the universal form above is refuted

The "Nonzero-alpha support-shape theorem" stated immediately above is
**false at arbitrary coefficients**.  See Note 0377
(`issue419-mixed-circuit-obstruction`) for an explicit counterexample over
`F_193` at `L_2 = (16, 4)` with 6-position support
`(32, 36, 40, 34, 38, 46)`, coefs `(112, 79, 1, 30, 47, 1)`, `alpha1 = 1`,
yielding a no-full saturated `S = (0,1,2,3,4,6,8,10)` with `rank(W) = 2`,
trivial dyadic stabilizer, and mixed-parity row support
(`u_parity = (0,1)`, `v_parity = (0,1)`).

The shape-complete catalog at q=97 / q=193 / q=1153 (this note +
Note 0375) remains valid for the **stable-coefficient** model used in the
sparse-worst scans: every observed nonzero-alpha shape is rank-collapse or
half-turn parity split, and the obstruction does not appear because its
special coefficients are not realized by `stable_coefs(support, p)`.

Per Note 0377, the correct statement now requires a **coefficient-quantifier
clarification** for paper2 Layer 3 / `conj:sparse-worst`:

* **Generic / Zariski-open form** (consistent with empirical scans):
  the mixed-circuit locus is a proper closed subset of coefficient space;
  outside it, every nonzero-alpha rank-2 no-full component is half-turn
  parity-split.
* **Worst-case all-coefficient form** (consistent with the `\max` quantifier
  in `conj:sparse-worst`): the mixed-circuit family must be charged by an
  additional local family not covered by `family ∈ {parity-half, near-parity,
  quarter-pair}`.

The unconditional arbitrary-coefficient support-shape theorem should not be
claimed.  The base-panel catalog of this note is still useful as the
finite-shape inventory for the stable-coefficient sparse-worst panels and
for the Note 0376 boundary statement.
