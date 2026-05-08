# Note 0388 -- Issue #419: all-alpha paired circuits are level-1 boundary artifacts

**Date:** 2026-05-01  
**Branch:** `issue-419-layer3-degeneracy-stratification`  
**Status:** closes the folded all-alpha danger for the recursive above-J FRI
commit-curve formulation.

---

## Summary

Note 0387 identifies the all-alpha obstruction as paired high-tail circuits.
This note explains why that obstruction should not be counted as a strict
above-J FRI Layer-3 counterexample:

> **All-alpha boundary exclusion.**  
> If a level-2 component `S` is saturated for both residual rows `u` and `v`,
> then the level-1 fold agrees with an `RS_{k1}` codeword on the full two-point
> lift of `S`.  At rate `1/4`, this lifted set has exactly Johnson-threshold
> size.  Hence the level-1 fold is not strictly above Johnson.

So the Issue #435 obstruction is dangerous in the raw folded `K` count, but
it lies on the recursive-admissibility boundary.  It is not a strict
above-J admissible point for the paper2 two-round commit-curve theorem.

Script:

```text
notes/scripts/issue419_all_alpha_lift_admissibility.py
```

Output:

```text
notes/scripts/issue419_all_alpha_lift_admissibility.output.txt
```

---

## Proof mechanism

Let the first fold live on `L1` with parameters

```text
(n1,k1) = (32,8),
```

and the second fold live on `L2` with

```text
(n2,k2) = (16,4).
```

For a fixed first challenge `alpha1`, write the level-2 row as

```text
h_{alpha1,alpha2}(t) = u_{alpha1}(t) + alpha2 v_{alpha1}(t).
```

If `S subset L2`, `|S|=8`, is saturated for both rows, then there exist
polynomials

```text
p_u(t), p_v(t),    deg p_u, deg p_v < k2 = 4,
```

such that

```text
u_{alpha1}|_S = p_u|_S,
v_{alpha1}|_S = p_v|_S.
```

Lift `S` to the two square roots in `L1`:

```text
tilde S = { y in L1 : y^2 in S }.
```

Then `|tilde S| = 2|S| = 16`.  On this lifted set, the first fold agrees with

```text
P(y) = p_u(y^2) + y p_v(y^2).
```

Since

```text
deg P <= max(2(k2-1), 1+2(k2-1)) = 2k2 - 1 = k1 - 1,
```

we have `P in RS_{k1}(L1)`.  Therefore the level-1 fold has agreement at least

```text
|tilde S| = 16 = sqrt(n1 k1),
```

which is exactly the Johnson agreement threshold.  Strict above-J requires
agreement `< 16`; hence such an all-alpha component is excluded.

The same argument is scale-uniform at rate `1/4`: if `n2=4k2`,
`n1=2n2`, and `k1=2k2`, then a saturated level-2 Johnson component
`|S| = sqrt(n2 k2) = 2k2` lifts to

```text
2|S| = 4k2 = sqrt(n1 k1),
```

again exactly the level-1 Johnson boundary.

---

## Verification on the Issue #435 obstruction

For the Note 0362 / Issue #435 support

```text
support = (32, 36, 40, 34, 38, 46)
coefs   = (112, 79, 1, 30, 47, 1)
S       = (0, 1, 2, 3, 4, 6, 8, 10)
```

the script verifies every `alpha1 in F_193`:

```text
all_alpha1_checked = 193
min_lift_agreement = 16
max_lift_agreement = 16
failures = []
```

The interpolants are independent of `alpha1` in this example:

```text
p_u = 112 + 79 t + t^2,
p_v =  30 + 47 t + t^3.
```

Thus every first-level fold is exactly Johnson-boundary close to `RS_8(L1)`.

---

## Consequence for the #419 proof split

The stratified proof target from Note 0386 should be sharpened to:

```text
V_delta =
  V_action
  union V_all-alpha-boundary
  union V_finite-root-saturated
  union V_nonaction-nonsaturated.
```

The all-alpha branch is not a finite-root collapse problem.  It is a boundary
admissibility problem:

```text
all-alpha saturated at level 2
  => level-1 fold has Johnson-threshold agreement
  => excluded by strict recursive above-J.
```

Therefore the remaining primitive work for #419 is the finite-root branch
only: outside all-alpha kernels, prove the Note 0355 nonzero-alpha collapse
theorem.

One caveat remains for the literal level-0 Conjecture `sparse-worst`: its
statement is phrased in terms of the one-dimensional `K(f1,f2;delta)` and
joint level-0 admissibility.  This note closes the obstruction for the
paper2 recursive FRI commit-curve formulation.  The bridge from the literal
level-0 conjecture to the recursive two-round formulation should explicitly
invoke this boundary exclusion.
