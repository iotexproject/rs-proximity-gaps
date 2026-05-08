# Note 0387 -- Issue #419: all-alpha danger equals paired tail circuits

**Date:** 2026-05-01  
**Branch:** `issue-419-layer3-degeneracy-stratification`  
**Status:** structural refinement after Note 0386; this identifies the exact
shape of the all-alpha obstruction.

---

## Summary

Note 0386 split the saturated branch into

```text
V_all-alpha-saturated  union  V_finite-root-saturated.
```

The all-alpha stratum is now structurally clear in the folded
`L2=(16,4)` model:

> **All-alpha rank-2 danger = paired high-tail circuits.**  
> For a fixed no-full component `S`, an all-alpha rank-2 obstruction exists
> exactly when the same high-tail matrix has one nonzero kernel vector on a
> `u` quadrant and one nonzero kernel vector on a `v` quadrant.  Equivalently,
> the obstruction is a pair of minimal tail circuits placed on opposite
> `alpha2` sides.

This is the mechanism behind the Note 0362 / Issue #435 counterexample.

Script:

```text
notes/scripts/issue419_all_alpha_circuit_classifier.py
```

Output:

```text
notes/scripts/issue419_all_alpha_circuit_classifier.output.txt
```

---

## Linear algebra statement

For fixed support `A` and no-full `S`, write the residual row as

```text
u_alpha1 = u0 + alpha1 u1,
v_alpha1 = v0 + alpha1 v1.
```

All-alpha saturation is

```text
H_S u0 = H_S u1 = H_S v0 = H_S v1 = 0.
```

Because the quotient-`C4` monomials occupy separate quadrants, this matrix is
block diagonal by quadrant:

```text
q0 -> u0,    q1 -> u1,    q2 -> v0,    q3 -> v1.
```

Therefore a rank-2 all-alpha row span cannot be created by a mysterious
mixed equation. It must be assembled from independent quadrant kernels:

```text
one kernel on q0 or q1   plus   one kernel on q2 or q3.
```

At minimal support size, each such kernel is a three-column high-tail circuit
of the `4 x 3` block

```text
[ tail_S(x^e1)  tail_S(x^e2)  tail_S(x^e3) ].
```

This gives the corrected obstruction normal form:

```text
support =
  {4e1 + q_u, 4e2 + q_u, 4e3 + q_u}
  union
  {4f1 + q_v, 4f2 + q_v, 4f3 + q_v},

q_u in {0,1}, q_v in {2,3},
tail_S(e1,e2,e3) has rank 2,
tail_S(f1,f2,f3) has rank 2.
```

Choosing any nonzero kernel vector on each side gives a full `q x q`
bad-challenge grid, hence paper2 two-dimensional `K = q`.

---

## Exhaustive base-panel classification

The classifier enumerates no-full `S` and all minimal three-column high-tail
circuits over `F_193` in the `L2=(16,4)` base model.  It finds:

```text
no_full_with_three_circuit = 1840
family:other              = 1840
paired_rank2_templates    = 284800
```

Circuit-count histogram:

```text
circuit_count:1  = 32
circuit_count:2  = 128
circuit_count:4  = 1280
circuit_count:8  = 384
circuit_count:40 = 16
```

Two immediate consequences:

1. All minimal all-alpha circuit sources are in `family=other`; they are not
   parity-half, near-parity, or quarter-pair families.
2. The obstruction family is large as an arbitrary-coefficient object. It is
   not a single accidental example.

---

## Issue #435 obstruction as a circuit pair

For the target no-full component

```text
S = (0, 1, 2, 3, 4, 6, 8, 10),
occupancy(S) = (3,1,3,1),
family(S) = other,
```

the classifier finds four three-column circuits.  The Note 0362 support

```text
support = (32, 36, 40, 34, 38, 46)
```

is the pair

```text
q0 exponents: (8, 9, 10)
q2 exponents: (8, 9, 11).
```

The corresponding kernel vectors are

```text
left  kernel = (109, 182, 144)
right kernel = ( 74,  13, 144).
```

The explicit Note 0362 coefficients are exactly the same paired-circuit point
up to a common scalar `63`:

```text
(112, 79, 1) = 63 * (109, 182, 144) mod 193,
( 30, 47, 1) = 63 * ( 74,  13, 144) mod 193.
```

This explains why every `alpha1` row has a full `alpha2` fiber and why Issue
#435 measured

```text
K = |V_delta| / q = 193.
```

---

## Implication for #419 / #396

The arbitrary-coefficient primitive theorem is not salvageable in its old
form.  The corrected Layer-3 path is:

```text
all-alpha branch:
  classify as paired tail circuits and charge/exclude separately;

finite-root branch:
  continue with Note 0355 nonzero-alpha collapse after removing all-alpha
  kernels.
```

This note gives the precise replacement for the vague "legal coefficient
coupling" gap in Note 0386.  The remaining theorem-level question is now
not whether all-alpha danger exists; it does.  The question is whether paired
tail circuits are:

1. excluded by the actual general-`f` dyadic decomposition,
2. charged to a sparse representative with at least the same `K`, or
3. a genuine counterexample to the current statement of `conj:sparse-worst`.

Given Conjecture `sparse-worst` quantifies over all admissible adversaries,
option 1 cannot be assumed without a proof from the original unfurled
coefficient model.

---

## Next target

The next highest-ROI lemma is:

> **Paired-circuit charging lemma.**  Every all-alpha paired-tail-circuit
> component arising in the folded Layer-3 model is either not joint-admissible
> in the original paper2 metric, or is matched by a three-position sparse
> adversary with `K >= q`.

If this lemma fails, the current sparse-worst conjecture must be weakened or
rewritten as a stratified bound rather than a literal maximizer statement.
