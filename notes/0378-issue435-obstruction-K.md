# Note 0378 -- Issue #435: 2D commit-K of the Note 0362 obstruction

> **Note number history**: filed as Note 0363 on the
> `issue-435-obstruction-k` branch; renumbered to 0378 on `main` because
> Note 0363 on the trunk is `issue419-rank2-parity-implication-proof-plan`.
> Closes GH issue #435.


**Date:** 2026-05-01  
**Branch:** `issue-435-obstruction-k`  
**Status:** exact computation; obstruction is K-dangerous under the paper2
2D commit-curve convention.

---

## Summary

Issue #435 asked whether the arbitrary-coefficient obstruction from Note 0362
is harmless after converting it to the same `K` convention used by paper2 /
fri-2round, rather than the older one-dimensional Hamming-pencil convention.

It is not harmless.

For the Note 0362 obstruction over `F_193`, the exact two-round bad-pair count
is

```text
|V_delta| = 37249 = 193^2,
K(f)     = |V_delta| / q = 193.
```

This exceeds the current rigorous three-position comparison bound

```text
K_3pos_max = 10.
```

Thus the obstruction is not merely a failure of a proposed shape theorem.  If
arbitrary coefficient choices at this support are admitted into the sparse-worst
Layer-3 statement, it is a genuine K-level counterexample.

---

## Convention

The computation uses the paper2 two-dimensional commit-curve convention:

```text
K(f) := |V_delta(f)| / q,
```

where `V_delta(f)` is the set of challenge pairs `(alpha1, alpha2)` such that
the two-round folded row is within the Johnson threshold at `L2=(16,4)`.

For fixed `alpha1`, the folded row is

```text
h_{alpha1,alpha2}(t) = u_alpha1(t) + alpha2 v_alpha1(t).
```

A pair is bad iff there exists an eight-subset `S` of `L2` such that
`h_{alpha1,alpha2}|_S` lies in `RS_4(S)`.  Equivalently, the four high-tail
coefficients of the remainder modulo `g_S` vanish.

This is not the one-dimensional Hamming-K used by some older sparse pencil
sweeps.

---

## Obstruction input

The Note 0362 support and coefficients are:

```text
p       = 193
L2      = (16, 4)
support = (32, 36, 40, 34, 38, 46)
coefs   = (112, 79, 1, 30, 47, 1)
S       = (0, 1, 2, 3, 4, 6, 8, 10)
```

The target component has

```text
family(S)    = other
occupancy(S) = (3, 1, 3, 1)
```

and the residual rows are

```text
u = 112 x^8 + 79 x^9 + x^10,
v =  30 x^8 + 47 x^9 + x^11.
```

Both rows vanish in the high-tail quotient for the same `S`.

---

## Exact result

Script:

```text
notes/scripts/issue435_obstruction_commit_K.py
```

Output:

```text
notes/scripts/issue435_obstruction_commit_K.output.txt
```

The exact result is:

```text
bad_pairs: 37249
K_fraction: 193
K_float: 193.0
K_3pos_max: 10
within_3pos_max: False
nonzero_alpha1_rows: 193
```

For every `alpha1 in F_193`, all `193` values of `alpha2` are bad.

The reason is structural: the obstruction support uses only fold quadrants
`0` and `2`.  Therefore `u_alpha1` and `v_alpha1` are independent of
`alpha1`.  Since the same no-full subset `S` annihilates both rows, it
annihilates every row in the pencil `u + alpha2 v`, for every `alpha2`, and
this repeats for every `alpha1`.

---

## Consequence for Issue #419 / Layer 3

The obstruction must be treated as a real blocker for any theorem that allows
arbitrary coefficients in this six-position support class.

Safe interpretations still possible:

1. the intended Layer-3 theorem is a generic / Zariski-open statement, not an
   arbitrary-coefficient universal statement;
2. the intended sparse-worst reduction excludes all-alpha degeneracies of this
   type by a coupling hypothesis inherited from the original FRI instance; or
3. the theorem must explicitly separate and account for these q-level
   all-alpha components.

What is no longer tenable:

```text
arbitrary six-position quotient-C4 coefficients
  => K no worse than the three-position max.
```

The Note 0362 obstruction gives `K=193 > 10` under the paper2 K convention.
