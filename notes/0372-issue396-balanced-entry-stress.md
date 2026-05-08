# Note 0372 -- Issue #396: balanced one-residue entry stress

> **Note number history**: filed as Note 0350 on the `issue-396`
> branch; renumbered to 0372 on `main` to avoid collision with already-
> absorbed content at slot 0350. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** targeted empirical check for the Note 0349 entry lemma.

Artifacts:

- `notes/scripts/issue396_one_residue_balanced_entry_search.py`
- `notes/scripts/issue396_one_residue_balanced_entry_search.n32_q193.output.txt`

---

## Purpose

After Note 0349, the remaining one-residue entry lemma is a moment-rank
statement: a primitive separating case would have

```text
rank M_a(S) <= 2
ker M_a(S) not contained in any equality hyperplane lambda_i=lambda_j.
```

The base and recursive quotient panels already showed that separating
lambda planes occur inside dyadic orbit-union families and then force deeper
stability.  This note stress-tests the complementary possibility: a balanced
support which is not visibly in the dyadic orbit-union family but still has a
separating rank-2 lambda plane.

---

## Search shape

The script samples balanced no-full supports at `(n,k)=(32,8)`:

```text
|S cap C_i| = 4        for i=0,1,2,3.
```

For each sampled support and every `0 <= a < 8`, it computes the Note 0349
dual-moment rank and confirms the result against the primal lambda-space
solver.  It records the forced equality partition of the lambda kernel and
whether the support is order-2 or order-4 stable.

This is intentionally not a broad support sweep.  It targets exactly the
balanced branch where a separating lambda plane could survive after the
one-active and exactly-two-active value-level cases have been charged.

---

## Output

```text
q=193, n=32, k=8, balanced_sets=20000, systems=160000

lambda_rank=1
forced_partition=((0, 1, 2, 3),)
order2_stable=False
order4_stable=False
count=159992

lambda_rank=1
forced_partition=((0, 1, 2, 3),)
order2_stable=True
order4_stable=False
count=8
```

No sampled balanced system had a nonconstant lambda projection.  In
particular, there were no rank-2 separating kernels outside the structured
dyadic panels of Notes 0345--0347.

The second line is also consistent with Note 0345: order-2 stable but not
order-4 stable balanced supports contribute only the constant-low branch, not
the separating branch.

---

## Consequence

The empirical picture for the one-residue entry lemma is now:

1. arbitrary one-active value level: rank collapse by Note 0348;
2. exactly two active value levels: impossible by Note 0343;
3. base quotient separating plane: order-2 stable by Note 0344;
4. order-`d`, `k/d=4` quotient separating plane: order-`2d` stable by Note
   0347;
5. random balanced high-scale supports outside the visible dyadic family:
   only constant-low lambda kernels in this stress panel.

This still does not prove the entry lemma, but it strongly suggests the next
paper proof should attack the Note 0349 moment minors directly: show that a
rank-2 separating kernel forces the deleted-point polynomial of `S` to be
even under a nontrivial dyadic substitution, hence `S` is an orbit union.
