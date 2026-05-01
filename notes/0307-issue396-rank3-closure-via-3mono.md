# Note 0307 — Issue #396: rank-3 closure via the 3-monomial pencil theorem

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** rank-3 version of #396 is closed.  The mixed-fiber phenomenon in
Note 0306 is exactly bounded by Note 0291's rigorous `K_3 <= 9` theorem.
This does not close general-f P3, but it removes rank-3 mixed supports from
the list of places where external Niho machinery is needed.

---

## Theorem

Let `fhat` be 3-position sparse at the FRI two-round deployment

$$
(n_0,k_0)=(32,8),\qquad (n_1,k_1)=(16,4),\qquad (n_2,k_2)=(8,2),
$$

and assume the usual recursive above-Johnson hypotheses:

1. `f` is above Johnson at `L0`;
2. some first fold is above Johnson at `L1`;
3. some second fold is above Johnson at `L2`.

Then

$$
|V_\delta(f)|
=
\#\{(\alpha_1,\alpha_2):
\operatorname{fold}^2_{\alpha_1,\alpha_2}(f)
\text{ is Johnson-bad on }L_2\}
\le 18q.
$$

In the separated mod-4 classes of Note 0305, the sharper bound is

$$
|V_\delta(f)|\le 10q.
$$

For the mixed panel of Note 0306, the observed worst case is exactly `9q`.

---

## Proof

Write the two-round fold on `L2` as

$$
\operatorname{fold}^2_{\alpha_1,\alpha_2}(f)
=A+\alpha_1B+\alpha_2C+\alpha_1\alpha_2D.
$$

For a 3-position sparse `fhat`, at least one of `A,B,C,D` is identically zero.
Therefore, for every fixed `alpha_1`, the row pencil

$$
\alpha_2\mapsto A+\alpha_1B+\alpha_2(C+\alpha_1D)
$$

is an `s`-monomial pencil on `L2` with `s <= 3`.

Partition the `alpha_1` rows into two types.

### Full rows

A row is full if every `alpha_2` is Johnson-bad on `L2`.

If `fold^1_{alpha_1}(f)` were above Johnson on `L1`, then the one-round
BCIKS/PR-373 proximity gap applied to the second fold would give at most

$$
M_{\max}(L_1)=n_1-\sqrt{k_1n_1}+1=16-8+1=9
$$

bad `alpha_2` values, not `q`.  Hence every full row must come from an
L1-bad first fold.

The first-fold map

$$
\alpha_1\mapsto \operatorname{fold}^1_{\alpha_1}(f)
$$

is itself an `s <= 3` monomial pencil on `L1`.  Since the recursive
hypothesis gives at least one above-J first fold, Note 0291 applies to this
first-fold pencil and gives

$$
\#\{\text{full rows}\}\le |B_1|\le 9.
$$

These rows contribute at most `9q`.

### Non-full rows

For a non-full row, there exists at least one `alpha_2` for which the L2 word
is above Johnson.  Thus this fixed-row `s <= 3` monomial pencil is above-J.
By Note 0291:

$$
\#\{\alpha_2:
\operatorname{fold}^2_{\alpha_1,\alpha_2}(f)
\text{ is Johnson-bad on }L_2\}
\le K_3\le 9.
$$

There are at most `q` such rows, so they contribute at most `9q`.

Combining:

$$
|V_\delta(f)|\le 9q+9q=18q.
$$

This proves the claimed rank-3 #396 bound.

---

## Relation to Notes 0305 and 0306

Note 0305 gives exact formulas for separated supports:

$$
|V_\delta|=|B_1|q
\quad\text{or}\quad
|V_\delta|=|B_1|q+(q-|B_1|),
$$

so the separated rank-3 classes satisfy `<=10q`.

Note 0306 measured the mixed supports and found stable `cq+O(1)` laws, with
max L1-good fiber 9.  The proof above explains the ceiling: every non-full
mixed row is a 3-monomial above-J pencil on `L2`, so Note 0291 forces the
fiber size to be at most 9.

The empirical `9q` support `(13,14,16)` is therefore not a Niho-table
exception; it is the extremal `K_3=9` monomial-pencil case appearing row by
row.

---

## Consequence for #396

The rank-3 branch of #396 is now closed without external sequence-school
machinery:

| stratum | bound | status |
|---|---:|---|
| separated rank-3 | `10q` | exact structural formula, Note 0305 |
| mixed rank-3 | `18q` rigorous, `9q` observed in panel | follows from Note 0291 |

This narrows #396 substantially.  The remaining open problem is no longer
the Note 0168 rank-3 distribution.  It is:

> Extend the row-pencil argument from `s <= 3` to `s >= 4` and ultimately
> dense/general `f`.

For `s=4`, Note 0295/0304 already gives a rigorous base-pencil ceiling
`K_4 <= 12` and shows `K_4 <= 9` is false over `q=1153`.  Thus any
general-f #396 theorem should be formulated with `K_s`/moment bounds, not
with a direct Helleseth--Kumar table match.

**Update (Note 0308 / Phase 1 correction).**  The forward route for that
`s >= 4` / general-f theorem should be Bluher-style orbit counting, not a
Niho table lookup.  Niho explains fixed-fiber value distributions; Bluher
2004 is the closer precedent for empty/singleton/pair/saturated orbit-count
classification.
