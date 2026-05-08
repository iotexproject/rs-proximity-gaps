# Note 0357 -- Issue #396: one-residue separating-plane lift probe

> **Note number history**: filed as Note 0345 on the `issue-396` branch;
> renumbered to 0357 on `main` to avoid collision with
> `0345-issue419-row-span-stabilizer-descent`. Cross-references to
> "Note 0344" inside the body refer to the branch's predecessor,
> which is now Note 0356 on `main` (one-residue base classification).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** targeted scale-lift evidence for the Note 0344 (= Note 0356 on `main`) separating
lambda-plane mechanism.

Artifacts:

- `notes/scripts/issue396_one_residue_stable_lift.py`
- `notes/scripts/issue396_one_residue_stable_lift.n32_q193.output.txt`

---

## Purpose

Note 0344 found that the base `L2=(16,4)` one-residue
`>=3`-active-value caveat is not primitive: every nonconstant no-forced-
equality lambda plane is supported on balanced opposite-pair sets, hence is
invariant under the order-2 dyadic action.

This note asks whether that is a one-scale artifact.  Rather than scanning all
no-full `16`-sets of `L=(32,8)`, we test the exact family predicted by Note
0344:

```text
balanced occupancy:      |S cap C_i| = k/2 = 4,
order-2 stability:       x in S  <=>  -x in S.
```

Inside each quarter block, this means choosing `k/4=2` opposite pairs.  There
are

```text
binom(4,2)^4 = 1296
```

such balanced order-2-stable sets at `n=32`.

---

## Result

For every such set and every `a<8`, solve the same lambda-space system

```text
p(x) = lambda_i x^a,        x in S cap C_i,        deg p < 8.
```

The output has only two mechanisms:

```text
lambda_rank=1, forced_partition=((0,1,2,3),)
lambda_rank=2, forced_partition=((0,), (1,), (2,), (3,))
```

The first mechanism is constant-low `Q` and is not an above-Johnson residual
row.  The second mechanism is the lifted separating lambda plane.  Crucially,
every separating-plane case is not only order-2 stable but also stable under
the next dyadic action:

```text
index translation by n/4 = 8.
```

The representative output line is:

```text
a_mod_4=0
lambda_rank=2
forced_partition=((0,), (1,), (2,), (3,))
order2_stable=True
order4_stable=True
count=32
example=(0,1,2,3,8,9,10,11,16,17,18,19,24,25,26,27)
```

The same count appears for `a mod 4 = 0,1,2,3`.

---

## Interpretation

At `k=8`, order-2 stability alone is not enough to create a nonconstant
separating lambda plane.  Among the `1296` balanced order-2-stable sets, the
separating-plane survivors are exactly the deeper dyadic-aligned subfamily in
this probe: they are also invariant under `x -> omega^{8} x`, i.e. the
order-4 action on `L`.

This points to a recursive descent mechanism:

```text
one-residue separating lambda plane
  => order-2 stable at k=4,
  => order-4 stable at k=8,
  => expected higher dyadic stability at larger k,
  => dyadic descendant, not primitive.
```

The statement is not yet a proof for all `k`; it is a sharper proof target.
The old residual caveat said "`>=3` active scalar values may remain."  After
Notes 0344--0345 the target is:

> If a one-residue C4 fiber has a lambda projection not contained in any
> two-value equality pattern, then the selected set must acquire a nontrivial
> dyadic stabilizer.  At `k=4` that stabilizer is order `2`; at `k=8` the
> separating-plane lift already lies in the order-`4` subfamily.

This is the scale-lift analogue of the stabilizer charge already used in
Notes 0310, 0340, and 0341.
