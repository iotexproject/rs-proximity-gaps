# Note 0371 -- Issue #396: dual-moment normal form for one-residue entry

> **Note number history**: filed as Note 0349 on the `issue-396`
> branch; renumbered to 0371 on `main` to avoid collision with already-
> absorbed content at slot 0349. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** algebraic restatement of the remaining one-residue entry lemma.

Artifacts:

- `notes/scripts/issue396_one_residue_dual_moment.py`
- `notes/scripts/issue396_one_residue_dual_moment.n16_q193.output.txt`
- `notes/scripts/issue396_one_residue_dual_moment.n32_q193.sample.output.txt`

---

## Setup

Let `L=<omega>` have order `4k`, and let the quarter blocks be

```text
C_i = {x in L : x^k = zeta^i},        i=0,1,2,3.
```

Fix a no-full support `S subset L`, `|S|=2k`, and put

```text
A_i = S cap C_i.
```

For a one-residue row

```text
P(x)=x^a Q(x^k),        0 <= a < k,
```

write

```text
lambda_i = Q(zeta^i).
```

The lambda-space condition is that there exists `p in F[x]_<k` such that

```text
p(x) = lambda_i x^a,        x in A_i.
```

Notes 0344--0347 tested this condition by solving the primal interpolation
system.  The same condition has a sharper dual form.

---

## Lemma 0349.A -- the block moment matrix

Let

```text
S = {s_1,...,s_{2k}},
c_s = 1 / prod_{t in S, t != s} (s-t).
```

These are the usual GRS dual multipliers for evaluation on `S`.  A word
`y:S -> F` lies in `RS_k(S)` iff

```text
sum_{s in S} c_s s^t y(s) = 0,        0 <= t < k.
```

Apply this to

```text
y(s)=lambda_i s^a,        s in A_i.
```

Then the lambda vector is feasible iff it lies in the kernel of the `k x 4`
block-moment matrix

```text
M_a(S)_{t,i} = sum_{s in A_i} c_s s^{a+t},
0 <= t < k,  0 <= i < 4.
```

Therefore

```text
lambda_rank(S,a) = 4 - rank M_a(S).
```

**Proof.**  The dual parity-check equations for the length-`2k`,
dimension-`k` GRS code `RS_k(S)` are exactly the displayed moment equations.
Substituting the one-residue value `lambda_i s^a` groups the sum by quarter
block and gives `M_a(S) lambda = 0`.  This is precisely the condition that
the values are the restriction of a degree-`<k` polynomial on `S`. ∎

---

## What the remaining entry lemma becomes

After Note 0348, one-active value levels are rank collapse.  After Note 0343,
exactly two active value levels are impossible.  Thus a primitive
one-residue obstruction must have a lambda kernel which is not contained in
any equality hyperplane `lambda_i=lambda_j`.  In the dual form this means:

```text
rank M_a(S) <= 2,
ker M_a(S) is not contained in any lambda_i=lambda_j,
S is no-full and not already in a dyadic descendant.
```

The entry lemma is now the following explicit moment-rank statement:

> If the four block moment columns of `M_a(S)` span a plane whose kernel is
> separating, then `S` must acquire a nontrivial dyadic orbit structure.
> Iterating this descent should put the branch in the `k/d=4` quotient where
> Note 0347 applies.

This is more concrete than the earlier interpolation wording.  It says the
hard case is a rank condition on four length-`k` moment sequences attached to
the deleted-point polynomial of `S`.

---

## Verification

The verifier compares this dual moment rank with the primal linear solve used
in Note 0344.

Complete base quotient:

```text
q=193, n=16, k=4, checked_systems=43584
identity: lambda_rank = 4 - rank(M_a(S))
```

The first separating examples are exactly the Note 0344 opposite-pair cases:

```text
occupancy=(2,2,2,2)
forced_partition=((0,), (1,), (2,), (3,))
order2_stable=True
moment_rank=2
lambda_rank=2
```

The rank-2 non-stable examples in the same output have forced partition
`((0,1,2),(3,))`, i.e. the high-multiplicity one-active branch now charged to
rank collapse by Note 0348.

A sampled higher-scale check also matches the primal system:

```text
q=193, n=32, k=8, checked_systems=8000
identity: lambda_rank = 4 - rank(M_a(S))
```

In that sample, the displayed rank-2 non-stable cases again have forced
partition `((0,1,2),(3,))`, not a separating lambda plane.  This is not a
proof of the entry lemma, but it confirms that the dual moment matrix is the
right object to attack next.

Update after Note 0351: the matrix `M_a(S)` has an exact complement-polynomial
formula.  For `D_B(X)=prod_{b in L\S}(X-b)=sum d_r X^r`,

```text
M_a(S)_{t,i}
  = (1/4) * sum_{r+a+t+1 == 0 mod k} d_r eta_i^((r+a+t+1)/k).
```

Thus the remaining moment-rank lemma can be attacked through the folded
coefficient triples `(d_b,d_{b+k},d_{b+2k})` of `D_B`.
