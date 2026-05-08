# Note 0345 -- Issue #419: stabilizer descent must be row-span descent

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** correction and sharpening of the Note 0344 stabilizer/descent target.

Artifacts:

- `notes/scripts/issue419_defect_allocation_witnesses.py`
- `notes/scripts/issue419_defect_allocation_witnesses.q97.4support.output.txt`
- `notes/scripts/issue419_defect_allocation_witnesses.q1153.4support.output.txt`

---

## Purpose

Note 0344 names the remaining Layer-3 blocker as a stabilizer/descent theorem:
primitive rank-2 no-full bilateral defect allocations should not survive after
excluding rank collapse and nontrivial dyadic stabilizer.

The first thing to check is what the stabilizer bucket actually stabilizes.  A
naive version would ask the saturated set `S` itself to be invariant under a
nontrivial dyadic shift.  That version is false in the certified base panels.
The correct descent is a **row-span/eigenspace descent**, not setwise descent of
`S`.

---

## Witness extraction

The new extractor reuses the symbolic-alpha system from Notes 0342--0343 but
prints examples from the non-primitive buckets.  It records:

```text
support, alpha1, S, occupancy(S), row_stabilizers, set_shift_stabilizers(S),
u_terms, v_terms.
```

Running the 4-support certifier at the two primes that have nonzero stabilizer
buckets gives exactly the old aggregate counts and exposes their structure.

For `q=97`:

```text
candidate_subsets = 47463680
alpha_zero        = 47463328
rank<2            = 336
stabilizer        = 16
primitive         = 0
```

A representative stabilizer witness is:

```text
support=(34,37,42,44), alpha1=50
S=(1,3,5,6,7,9,11,14), occupancy=(0,3,2,3)
row_stabs=(0,8), S_shift_stabs=(0,)
u_terms=((9,57),(11,7))
v_terms=((8,21),(10,23))
```

For `q=1153`:

```text
candidate_subsets = 47463056
alpha_zero        = 47463024
rank<2            = 16
stabilizer        = 16
primitive         = 0
```

A representative stabilizer witness is:

```text
support=(32,38,40,47), alpha1=917
S=(0,2,4,6,7,8,10,15), occupancy=(3,0,3,2)
row_stabs=(0,8), S_shift_stabs=(0,)
u_terms=((8,626),(10,900))
v_terms=((9,536),(11,207))
```

Thus the row span is preserved by the half-turn `x -> -x`, but the saturated
component is not a union of antipodal pairs.  Any theorem requiring
`S+8=S` would incorrectly reject known charged witnesses.

---

## Correct stabilizer lemma shape

Let `L` have size `4k`, and let `tau` be a nontrivial dyadic diagonal action
on coefficient space, equivalently `P(x) -> P(mu x)` for a nontrivial
2-power root `mu`.  Suppose

```text
tau W = W,      dim W = 2.
```

Since the characteristic is odd and `tau` has 2-power order, the action on `W`
is semisimple.  Therefore either:

1. `tau` acts by a scalar on `W`; then every row direction lies in a single
   dyadic character class after subtracting lower-code terms, so the row is a
   quotient/descent row; or
2. `W` has an eigenbasis `P_chi, P_psi`, where the monomial supports of each
   eigenvector lie in one exponent residue class modulo the dyadic quotient.

For the half-turn witnesses above this is visible directly:

```text
q=97:    u has odd exponents {9,11}, v has even exponents {8,10}
q=1153:  u has even exponents {8,10}, v has odd exponents {9,11}
```

So the stabilizer bucket is already a lower-dyadic quotient pencil after
separating parity characters, even though `S` itself is not shift-invariant.

The corrected lemma should therefore be stated as:

> **Row-span stabilizer descent.**  If a rank-2 folded row span `W` has a
> nontrivial dyadic stabilizer, then after choosing a stabilizer eigenbasis and
> stripping the corresponding character monomials, the no-full saturation
> equations factor through a smaller dyadic quotient.  The component `S` may be
> non-invariant; it is charged through the descended row span, not through
> setwise invariance of `S`.

This is the descent bucket needed by Note 0344.  The primitive theorem should
only exclude rows with **trivial row-span stabilizer**.

---

## Immediate proof target

The next proof step should not be another support-size cert.  It is the
following linear-algebra lemma.

> **Eigenspace-descent lemma.**  Let `W=span(P,Q)` be a folded above-Johnson
> rank-2 row span over a field of odd characteristic.  If a nontrivial dyadic
> diagonal operator `tau` preserves `W`, then there is a basis of `W` in which
> each basis vector is supported on one residue class modulo the order of
> `tau`.  After dividing by the corresponding character monomial, the two
> basis vectors are polynomials in `x^2` (or in the appropriate deeper quotient
> variable).  Consequently all defect-allocation equations from Note 0340 are
> inherited from a lower dyadic level.

The semisimple eigenbasis part is immediate.  The remaining mathematical work
is the last sentence: show that the Note 0340 dual parity system is preserved
under this quotient reinterpretation without requiring `S` itself to be a
fiber union.

This is now the precise binding subclaim for #419:

```text
row-span stabilizer
  => eigenbasis by dyadic characters
  => quotient-row defect allocation
  => charged descent bucket.
```

The q=97 and q=1153 witnesses show why the middle arrow must use row-span
characters rather than setwise component invariance.

---

## Consequence for Note 0344

The Note 0344 theorem statement remains right if "`S` descends" is interpreted
as row-span/eigenspace descent.  It should not be read as `S` having nontrivial
cyclic stabilizer.

A safer theorem formulation is:

```text
no-full saturated S
  => alpha1 = 0
     or rank(W) < 2
     or W has nontrivial dyadic row-span stabilizer
     or W is primitive and S belongs to a charged complete-block / defect-root /
        singleton-tail family.
```

Then a separate descent lemma handles the nontrivial-stabilizer branch by
passing to the stabilizer eigenspaces and the smaller dyadic quotient.
