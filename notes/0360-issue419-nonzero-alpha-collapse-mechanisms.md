# Note 0360 -- Issue #419: nonzero-alpha collapse mechanisms

> **Note number history**: filed as Note 0356 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0360 on `main`
> because Note 0356 on the trunk is the (renumbered)
> `issue-396-one-residue-base-classification`. Cross-references to
> "Note 0355" (next-target charter) match `main` numbering directly.

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** structural audit; next theorem target refined from Note 0355.

---

## Purpose

Note 0355 identified the remaining #419 target as a Nonzero-alpha collapse
statement for quotient-`C4` defect allocation.  The previous classifier showed
that every tested `alpha1 != 0` no-full saturated candidate is either
rank-deficient or half-turn-stabilizer controlled, but it did not expose the
local algebraic reason.

This note records the first structural refinement from the affine system

```text
C(S) + alpha1 M(S) = 0.
```

New audit script:

```text
notes/scripts/issue419_affine_collapse_audit.py
```

Saved outputs:

```text
notes/scripts/issue419_affine_collapse_audit.q97.examples.output.txt
notes/scripts/issue419_affine_collapse_audit.q193.examples.output.txt
notes/scripts/issue419_affine_collapse_audit.q97.prefix200.output.txt
```

---

## What the affine audit checks

For a fixed support and component `S`, the script computes the high-tail
vectors `C(S), M(S)` for both residual basis rows.  For each nonzero solution
`alpha1`, it records:

1. the common scalar relation `C=-alpha1 M`;
2. whether the resulting row span has rank `<2`;
3. whether the row span has half-turn stabilizer;
4. the support split by folded exponent and fold quadrant;
5. same-folded cancellations of the form

```text
u_r = c_{4r} + alpha1 c_{4r+1} = 0,
```

or

```text
v_r = c_{4r+2} + alpha1 c_{4r+3} = 0;
```

6. parity of the surviving `u` and `v` quotient exponents.

This is deliberately a mechanism audit, not another broad enumeration.

---

## Observed two-mechanism dichotomy

On the q=97 four-support representatives and q=193 five-support
representatives, every nonzero-alpha survivor falls into exactly one of two
mechanisms.

### Mechanism I: same-folded cancellation

Example q=97:

```text
support=(24,25,34,43), alpha1=46,
split_support=((6,), (6,), (8,), (10,)).
```

The two `u` monomials have the same folded exponent `6` but occupy fold
quadrants `0` and `1`, so at the special nonzero `alpha1`,

```text
c_{24} + alpha1 c_{25} = 0.
```

The audit records

```text
same_folded_cancellations=(('u', 6, 0, 1),)
u_terms=()
v_terms=((8,*),(10,*))
```

hence the row span loses rank immediately.  The q=193 rank-collapse example is
the same pattern:

```text
support=(16,17,38,39,46), alpha1=161,
split_support=((4,), (4,), (9,11), (9)),
same_folded_cancellations=(('u', 4, 0, 1),).
```

### Mechanism II: half-turn parity split

Example q=97:

```text
support=(34,37,42,44), alpha1=50,
split_support=((11,), (9,), (8,10), ()).
```

There is no same-folded cancellation.  Instead the surviving quotient supports
split by parity:

```text
u_terms=((9,*),(11,*))   -- odd quotient exponents
v_terms=((8,*),(10,*))   -- even quotient exponents
row_stabs=(0,8).
```

The q=193 stabilizer example is identical up to parity reversal:

```text
support=(32,33,39,40,46), alpha1=45,
split_support=((8,10),(8,),(11,),(9)),
u_terms=((8,*),(10,*))   -- even quotient exponents
v_terms=((9,*),(11,*))   -- odd quotient exponents
row_stabs=(0,8).
```

Thus the nonzero-alpha non-rank-collapse branch is not primitive: it is exactly
the half-turn row-span stabilizer branch already closed by Notes 0347--0351.

---

## Refined theorem target

The Note 0355 Nonzero-alpha collapse theorem should now be attacked as the
following sharper dichotomy.

> **Dichotomy target.**  In the quotient-`C4` defect-allocation system for a
> legal strict above-J folded row span, suppose a no-full saturated component
> has a nonzero solution of `C(S)+alpha1 M(S)=0`.  Then either:
>
> 1. some same-folded pair cancels at this `alpha1`, forcing rank `<2`; or
> 2. after removing such cancellations, the two residual basis rows have
>    opposite parity support in the quotient coordinate, hence the row span is
>    invariant under the half-turn action.

This target is materially stronger than the previous classifier statement and
is closer to a proof.  It also matches the already-proved closure status:

```text
same-folded cancellation -> rank collapse,
half-turn parity split   -> Notes 0347--0351 weighted quotient closure.
```

---

## Algebraic interpretation

The quotient-`C4` local representative formula from Note 0323 writes every
residual coefficient as an affine form in `alpha1`.  A nonzero solution can only
occur when a block of high-tail equations makes `C` and `M` proportional.

The observed proportionality is not arbitrary:

- In Mechanism I the proportionality scalar is exactly the scalar that cancels
  a same-folded pair inside one basis row.
- In Mechanism II no folded pair cancels; instead the surviving row supports
  lie in the two eigenspaces of the half-turn operator on the quotient circle.

So the remaining proof should not try to classify all components `S` directly.
It should prove that proportionality `rank(C,M)=1` in the no-full saturated
system forces one of these two quotient-support configurations.

---

## Immediate next work

1. Express same-folded cancellation as explicit linear factors in the affine
   row coefficients.
2. For the quotient after those factors are inverted, prove that `rank(C,M)=1`
   forces quotient parity separation of the surviving `u` and `v` supports.
3. Invoke Notes 0347--0351 to discharge the parity-separated branch.

This is now the concrete remaining proof gap for the primitive global
attachment branch of #419.
