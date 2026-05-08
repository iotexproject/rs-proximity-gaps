# Note 0375 -- Issue #419: catalog-wide shape certificate for nonzero-alpha branch

> **Note number history**: filed as Note 0360 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0375 on `main` to
> avoid collision with already-absorbed content at slot 0360.
> Cross-references inside the body to "Notes 0356--0360" use branch
> numbering. Branch-to-main mapping for the issue-419 trail (post Notes
> 0345--0355 / 0356 absorptions):
>   branch 0356           = main 0360 (nonzero-alpha-collapse-mechanisms),
>   branch 0357--0359     = main 0363--0365 (rank-2 plan / shape cert / shape catalog),
>   branch 0360           = main 0375 (catalog-wide shape certificate),
>   branch 0361           = main 0376 (support-shape-theorem-boundary),
>   branch 0362           = main 0377 (mixed-circuit obstruction --- this trail).
> Cross-references to Notes 0345--0352 match `main` numbering directly.

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** base-panel shape certificate upgraded from representatives to all
observed nonzero-alpha shapes; all-scale support-shape theorem remains.

---

## Purpose

Notes 0358--0359 left one avoidable weakness: the Groebner shape certificate
checked six representative shapes, while the complete base-panel catalogs
contained 39 unique nonzero-alpha shapes.

I updated

```text
notes/scripts/issue419_parity_implication_shape_cert.py
```

so it can ingest the catalog outputs directly:

```text
--from-catalog notes/scripts/issue419_nonzero_shape_catalog.q97.4support.output.txt
--from-catalog notes/scripts/issue419_nonzero_shape_catalog.q193.5support.output.txt
```

The saved output is:

```text
notes/scripts/issue419_parity_implication_shape_cert.catalog.output.txt
```

---

## Result

The catalog-wide certificate covers all `15 + 24 = 39` unique observed
nonzero-alpha shapes:

```text
rows=39
rank-collapse expected shapes=33
parity-split expected shapes=6
```

Every rank-collapse shape becomes empty after saturation by `alpha1 != 0` and
the rank-2 minors:

```text
rank<2 shapes: 33/33 have rank2_branch_empty=True
```

Every rank-2 surviving shape is already a half-turn parity split:

```text
parity-split shapes: 6/6 have rank2_branch_empty=False
parity_forbidden_factors=0 for all 6
```

No catalog shape violates the Note 0357 implication.

---

## Interpretation

This closes the finite base-panel shape question:

```text
q=97 four-support nonzero-alpha shape
or q=193 five-support nonzero-alpha shape
  => rank-collapse after rank2 saturation
     or half-turn parity split.
```

Combined with Notes 0347--0351, every rank-2 catalog survivor is charged by
the already closed half-turn weighted quotient branch.

This is stronger than the previous representative check because it is not
choosing examples by hand.  The script parses the complete shape catalog and
certifies one representative per unique shape key.

---

## Remaining theorem

This still does **not** close #419 globally.  The remaining step is exactly
the all-scale support-shape theorem:

> In the legal quotient-`C4` no-full saturated system, after saturating by
> `alpha1 != 0` and `rank(W)=2`, every support shape is half-turn parity split.

The catalog-wide certificate proves the theorem for every shape that actually
appears in the complete q=97/q=193 base panels.  It does not prove that no new
mixed-parity rank-2 shape can appear at larger dyadic scale.

---

## Next proof target

The next useful proof step is therefore not more random search.  It is to
derive the shape theorem from the quotient-`C4` dual parity equations:

1. same-folded cancellation factors are rank-collapse factors;
2. same-parity two-row branches are rank-collapse factors;
3. after inverting those rank-collapse factors, the affine system
   `C(S)+alpha1 M(S)=0` forces the two quotient rows into opposite parity
   eigenspaces.

If this implication is proved, the primitive nonzero-alpha branch of #419
collapses into the already closed half-turn branch.


---

## Additional q=1153 regression

I also ran the four-support catalog at `q=1153`, the other prime where the
old four-support panel had a stabilizer bucket:

```text
notes/scripts/issue419_nonzero_shape_catalog.q1153.4support.output.txt
notes/scripts/issue419_parity_implication_shape_cert.q1153.4support.output.txt
```

The q=1153 catalog has only two unique nonzero-alpha shapes:

```text
unique_shapes=2
same-folded-cancellation: 1 shape, rank2_branch_empty=True
half-turn-parity-split:  1 shape, rank2_branch_empty=False
```

Both have the same half-turn fiber profile `0^3,1^2,2^3`.  This is a useful
regression because it shows the q=97 four-support stabilizer shape is not a
small-field artifact; at a much larger prime the only rank-2 survivor is still
exactly the half-turn weighted quotient profile already closed by Notes
0347--0351.
