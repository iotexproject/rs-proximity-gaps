# Note 0327 -- Issue #396: no-full candidates collapse by one-sided rank loss

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** proof-target refinement after Note 0326.

Artifacts:

- `notes/scripts/issue396_no_full_pattern_audit.py`
- output: `notes/scripts/issue396_no_full_pattern_audit.q193.output.txt`

---

## Purpose

Note 0326 certified that the legal `(64,16)->L2=(16,4)` strict
above-Johnson `C(48,3)` panel has no primitive rank-2 no-full saturated
component across seven primes.  The remaining question is whether this is a
large unstructured finite fact or whether the rank collapse has a small
mechanism.

This note audits the symbolic-alpha candidates by support quadrant, residual
exponent multiplicity, no-full occupancy, and rank-collapse mechanism.

---

## Legal-panel result over `F_193`

Panel:

```text
q=193, L2=(16,4), support_window=[16,64), supports=C(48,3)=17296.
```

The symbolic no-full equation again produces exactly:

```text
candidate no-full equations = 22055749
primitive rank-2 candidates = 0
stabilized rank-2 candidates = 0
rank<2 candidates = 22055749
```

The new information is the rank-collapse split:

| mechanism | count |
|---|---:|
| zero-row | 22053504 |
| u=0 / v has 2 residual terms | 1056 |
| v=0 / u has 2 residual terms | 1024 |
| u=0 / v has 3 residual terms | 101 |
| v=0 / u has 3 residual terms | 64 |

There are no `dependent-same-support` rank-1 cases and no
`dependent-different-supports` cases.  In the legal panel, every no-full
candidate collapses because one side of the `u + alpha2 v` pencil is zero,
with the overwhelming majority being the trivial `alpha1=0` zero-row case.

Representative nontrivial one-sided examples:

```text
v=0/u3: support=(16,25,56), alpha1=84,
        S=(0,2,3,5,8,10,11,13), occupancy=(2,2,2,2).

u=0/v3: support=(19,34,59), alpha1=18,
        S=(1,4,6,7,9,12,14,15), occupancy=(2,2,2,2).

v=0/u2: support=(32,33,40), alpha1=11,
        S=(0,1,2,4,6,8,9,10), occupancy=(3,2,3,0).

u=0/v2: support=(34,35,42), alpha1=107,
        S=(0,1,2,4,6,8,9,10), occupancy=(3,2,3,0).
```

The first example is the Note 0325 deeper-dyadic counterexample; this audit
shows it is not exceptional.  It is one member of a small one-sided rank-loss
bucket.

---

## Support-signature concentration

The dominant support signatures are all in quadrants `1` and `3`:

```text
((1,1,1), exp_hist=(1,1,1), uv_counts=(3,0)): 2397120
((1,1,3), exp_hist=(1,1,1), uv_counts=(2,1)): 2397120
((1,3,1), exp_hist=(1,1,1), uv_counts=(2,1)): 2397120
((1,3,3), exp_hist=(1,1,1), uv_counts=(1,2)): 2397120
((3,1,1), exp_hist=(1,1,1), uv_counts=(2,1)): 2397120
((3,1,3), exp_hist=(1,1,1), uv_counts=(1,2)): 2397120
((3,3,1), exp_hist=(1,1,1), uv_counts=(1,2)): 2397120
((3,3,3), exp_hist=(1,1,1), uv_counts=(0,3)): 2397120
```

These are exactly the `alpha1=0` zero-row families: every monomial carries an
`alpha1` factor after the first fold, so the residual row vanishes at
`alpha1=0`.

The nontrivial one-sided families are much smaller and have signatures where
the nonzero side has two or three same-parity fold-quadrant terms after the
other side cancels.

---

## Proof target after the audit

The primitive rank-2/no-full theorem can now be attacked through a sharper
alternative:

> Let `S` be a no-full 8-subset of `L2=(16,4)` and let
> `C(S)+alpha1 M(S)=0` be the symbolic no-full condition for a legal strict
> above-Johnson 3-support row.  If the condition is solvable, then either
> `u_alpha=0` or `v_alpha=0`.

For the legal panel, this stronger one-sided statement implies rank `<2`
directly and removes the need to reason about general rank-1 proportionality.

The larger folded stress panel from Note 0326 still needs the stabilizer
escape hatch: there, rank-2 no-full candidates exist but all observed cases
have a nontrivial dyadic stabilizer.  Therefore the combined theorem remains:

```text
legal support window:
  no-full candidate => u=0 or v=0.

larger folded window:
  no-full candidate => rank<2 or nontrivial dyadic stabilizer.
```

---

## Next algebraic check

The immediate hard proof step is no longer an all-purpose saturated-component
classification.  It is an emptiness statement after saturating away the two
one-sided loci:

```text
C(S)+alpha M(S)=0,
u != 0,
v != 0.
```

For each no-full occupancy type and support quadrant signature, a GB check can
ask whether the above ideal has a point.  The audit says this ideal is empty
on the legal `C(48,3)` stratum over `F_193`; Note 0326 says the same
rank-collapse conclusion is prime-stable across
`{97,193,257,449,577,769,1153}`.

This is the concrete finite-case bridge from computation to proof:

1. quotient by the `alpha1=0` zero-row family;
2. saturate away `u=0` and `v=0`;
3. show the no-full symbolic-alpha equations have no remaining legal
   3-support solution.
