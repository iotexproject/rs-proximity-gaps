# Note 0386 -- Issue #419: all-alpha degeneracy stratification after #435

**Date:** 2026-05-01  
**Branch:** `issue-419-layer3-degeneracy-stratification`  
**Status:** corrected Layer-3 target; arbitrary-coefficient sparse-worst needs a
separate all-alpha stratum.

---

## Summary

Issue #435 shows that the Note 0362 mixed-circuit obstruction has

```text
K(f) = |V_delta(f)| / q = 193
```

under the paper2 two-dimensional commit-curve convention.  This is larger than
the current three-position comparison bound `K <= 10`.

Therefore the #419 / #396 path cannot keep the statement

```text
arbitrary quotient-C4 coefficients
  => no worse than 3-position sparse.
```

The correct next move is to split the saturated branch into an explicit
all-alpha degeneracy stratum plus the remaining finite-root stratum.

---

## All-alpha linear locus

For a support `A` and an eight-subset `S` of `L2=(16,4)`, write

```text
u_alpha1 = u0 + alpha1 u1,
v_alpha1 = v0 + alpha1 v1.
```

The condition that `S` is saturated for every `alpha1` and every `alpha2` is
the linear system

```text
H_S u0 = H_S u1 = H_S v0 = H_S v1 = 0.
```

For fixed `(A,S)`, this defines a linear subspace of coefficient space.  If
the coefficient vector lies in this kernel, then `S` contributes a full
`q x q` grid of bad challenge pairs whenever the resulting row span is rank 2.

This is exactly the mechanism behind the Note 0362 obstruction.

Script:

```text
notes/scripts/issue419_all_alpha_locus_audit.py
```

Output:

```text
notes/scripts/issue419_all_alpha_locus_audit.output.txt
```

---

## Note 0362 support audit

Use the Note 0362 support

```text
support = (32, 36, 40, 34, 38, 46).
```

For no-full eight-subsets `S`, the audit finds:

```text
positive_nullity_no_full_subsets = 896
nullity:2                       = 896
family:other                    = 896
```

So this support has many proper all-alpha loci.  They are not automatic
counterexamples for generic coefficients; they are proper linear subspaces.

For the explicit Note 0362 coefficients

```text
coefs = (112, 79, 1, 30, 47, 1),
```

the audit finds:

```text
coefs_in_locus_no_full_subsets = 16.
```

The target subset

```text
S = (0, 1, 2, 3, 4, 6, 8, 10)
```

has

```text
family(S)    = other
occupancy(S) = (3, 1, 3, 1)
rank         = 4
nullity      = 2
side_ranks   = ((0,3,2), (1,0,0), (2,3,2), (3,0,0)).
```

The side-rank signature exposes the mechanism: the `q0` and `q2` sides are two
independent three-column tail circuits.  Choosing one kernel vector on each
side produces a rank-2 row span annihilated by the same no-full component `S`.

For the same support with deterministic `stable_coefs`, the audit finds:

```text
coefs_in_locus_no_full_subsets = 0.
```

This matches Note 0362's observation: the obstruction is a special coefficient
locus, not a generic/stable-coefficient phenomenon.

---

## Corrected theorem target

The #419 sparse-worst route should now be stated as a stratified theorem:

```text
V_delta =
  V_action
  union V_all-alpha-saturated
  union V_finite-root-saturated
  union V_nonaction-nonsaturated.
```

The old primitive-branch target tried to absorb
`V_all-alpha-saturated` into the finite-root saturated analysis.  #435 shows
that is impossible for arbitrary coefficients.

The viable target is:

1. **All-alpha stratum.**  Prove that coefficient vectors entering these
   kernels are either excluded by the legal coefficient-coupling hypothesis,
   contained in a proper Zariski-closed exceptional set, or separately charged
   in the final sparse-worst bound.
2. **Finite-root saturated stratum.**  Outside the all-alpha kernels, retain
   the Note 0355 nonzero-alpha collapse theorem: every no-full finite-root
   saturated component is rank-deficient, stabilizer-charged, or belongs to an
   already charged local family.
3. **Generic/Zariski-open version.**  Since the all-alpha loci are finite
   unions of proper linear subspaces for fixed support, a generic theorem can
   safely exclude them.  The remaining proof must then handle only finite
   alpha roots.

---

## Immediate next work

The highest-ROI next lemma is now:

> **All-alpha legal-coupling lemma.**  For coefficient vectors arising from the
> actual paper2 Layer-3 sparse-worst reduction, a rank-2 no-full all-alpha
> saturated component either cannot occur generically, or it is an explicitly
> charged exceptional stratum.

This is narrower and more defensible than the false arbitrary-coefficient
claim.  It also preserves the existing Note 0355 finite-root collapse route,
because that route should be applied only after removing all-alpha kernels.
