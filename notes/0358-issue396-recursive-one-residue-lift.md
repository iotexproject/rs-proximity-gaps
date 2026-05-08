# Note 0358 -- Issue #396: recursive one-residue dyadic lift evidence

> **Note number history**: filed as Note 0346 on the `issue-396` branch;
> renumbered to 0358 on `main` to avoid collision with
> `0346-issue419-eigenspace-descent-and-weighted-quotient`.
> Cross-references to "Notes 0344--0345" inside the body refer to
> branch numbering and correspond on `main` to Notes 0356--0357.

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** targeted recursive lift evidence for the one-residue
separating-lambda-plane branch from Notes 0344--0345 (= 0356--0357 on `main`).

Artifacts:

- `notes/scripts/issue396_one_residue_recursive_lift.py`
- `notes/scripts/issue396_one_residue_recursive_lift.n64_q193.output.txt`
- `notes/scripts/issue396_one_residue_recursive_lift.n128_q257.output.txt`

---

## Purpose

Note 0345 showed that at `k=8`, the one-residue separating lambda-plane
survivors inside the balanced order-2-stable family are already stable under
the next dyadic action, order 4.

This note tests whether that is a one-step accident.  The recursive lift
probe assumes the current dyadic stabilizer order `d`, enumerates the balanced
order-`d` family in each quarter block, solves the same lambda-space system

```text
p(x) = lambda_i x^a,        x in S cap C_i,        deg p < k,
```

and checks whether every nonconstant separating lambda plane falls into the
order-`2d` subfamily.

The enumeration stays small because the recursive family has four
order-`d` orbits in each quarter block and chooses two of them:

```text
binom(4,2)^4 = 1296 sets.
```

---

## Results

### Reproduction of Note 0345

For `q=193`, `n=32`, `k=8`, `d=2`, the new recursive script reproduces Note
0345:

```text
balanced_assumed_stable_sets=1296
lambda_rank=1, forced_partition=((0,1,2,3),), order4_stable=False
lambda_rank=2, forced_partition=((0,), (1,), (2,), (3,)), order4_stable=True
```

The rank-1 branch is constant-low `Q` and is not an above-Johnson residual
row.  The rank-2 branch is the separating lambda plane, and every such row is
stable under the next dyadic action.

### Second lift: `k=16`

For `q=193`, `n=64`, `k=16`, `d=4`, the same pattern persists:

```text
balanced_assumed_stable_sets=1296
a_mod_8=0..7:
  lambda_rank=1, forced_partition=((0,1,2,3),), order8_stable=False
  lambda_rank=2, forced_partition=((0,), (1,), (2,), (3,)), order8_stable=True
```

For every `a mod 8`, there are `32` rank-2 separating-plane cases, and every
one is order-8 stable.

### Third lift: `k=32`

For `q=257`, `n=128`, `k=32`, `d=8`, the pattern persists again:

```text
balanced_assumed_stable_sets=1296
a_mod_16=0..15:
  lambda_rank=1, forced_partition=((0,1,2,3),), order16_stable=False
  lambda_rank=2, forced_partition=((0,), (1,), (2,), (3,)), order16_stable=True
```

For every `a mod 16`, there are again `32` rank-2 separating-plane cases, and
every one is order-16 stable.

---

## Interpretation

The one-residue `>=3`-active-value caveat is now experimentally confined to a
recursive dyadic descendant:

```text
k=4:   separating plane => order-2 stable
k=8:   order-2 stable separating plane => order-4 stable
k=16:  order-4 stable separating plane => order-8 stable
k=32:  order-8 stable separating plane => order-16 stable
```

The constant-low branch can fail to be next-stable, but it has
`lambda_rank=1` and corresponds to low `Q`; it is not an above-Johnson
residual obstruction.  The only nonconstant no-forced-equality branch observed
at every tested scale is the rank-2 separating plane, and that branch always
descends one more dyadic level.

This gives a sharper all-scale proof target:

> In the one-residue C4-fiber branch, if the lambda projection is a rank-2
> separating plane and the selected set is balanced and stable under the
> current dyadic order `d`, then the interpolation equations force stability
> under order `2d`.

Combined with Note 0344's base step, this recursive lemma would close the
`>=3`-active-value one-residue caveat by infinite descent to a dyadic
descendant, not a primitive no-full component.

The remaining paper-grade work is to replace the finite panels above by a
symbolic orbit/interpolation proof.  The panels are deliberately shaped to the
candidate lemma rather than broad enumeration.

Update after Note 0347: the panel mechanism has a symbolic quotient proof
whenever the support is already an order-`d` orbit union with `k/d=4`.  The
orbit character split reduces the equation exactly to the Note 0344 base
lambda-space on the quotient `L/H_d`, and the base opposite-pair conclusion
lifts to order-`2d` stability.
