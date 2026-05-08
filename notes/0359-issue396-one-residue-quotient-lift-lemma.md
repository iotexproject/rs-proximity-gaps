# Note 0359 -- Issue #396: quotient proof for the recursive one-residue lift

> **Note number history**: filed as Note 0347 on the `issue-396` branch;
> renumbered to 0359 on `main` to avoid collision with
> `0347-issue419-five-root-quotient-lemma`. Cross-references to
> "Note 0346" / "Note 0344" inside the body refer to branch numbering
> and correspond on `main` to Notes 0358 / 0356 respectively.

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** symbolic proof of the Note 0346 (= Note 0358 on `main`) recursive panel mechanism.

---

## Setup

Let `L=<omega>` have order `4k`, and let the quarter blocks be the fibers of
`x^k`.  Suppose `d | k` and `S` is a union of orbits under

```text
H_d = <omega^(4k/d)>.
```

This subgroup has order `d` and lies inside each quarter block because
`h^k=1` for every `h in H_d`.

The one-residue lambda-space equation is

```text
p(x) = lambda_i x^a,        x in S cap C_i,        deg p < k.
```

Write `a=a_0+td`, with `0 <= a_0 < d`.

---

## Character split on each orbit

Decompose the low polynomial by exponent class modulo `d`:

```text
p(x) = sum_{r=0}^{d-1} x^r R_r(x^d),
deg R_r < k/d.
```

For a selected orbit representative `x`, the equation must hold for every
`h in H_d`:

```text
sum_r h^r x^r R_r(x^d)
  = lambda_i h^a x^a
  = h^{a_0} lambda_i x^{a_0} (x^d)^t.
```

Since the `d` characters `h -> h^r` are distinct over the field, equality for
all `h in H_d` implies

```text
x^r R_r(x^d) = 0                         for r != a_0,
R_{a_0}(x^d) = lambda_i (x^d)^t.
```

Thus the full order-`d` orbit equations reduce exactly to a quotient
lambda-space equation on `L/H_d`:

```text
R(z) = lambda_i z^t,        z = x^d,        deg R < k/d.
```

The four quarter blocks are preserved because `(x^d)^(k/d)=x^k`.

---

## The `k/d=4` quotient

In the recursive panels of Note 0346, `k/d=4`.  Therefore the quotient has
order

```text
4(k/d) = 16
```

and block size `4`.  The quotient equation is precisely the Note 0344 base
classification with exponent `t in {0,1,2,3}`:

```text
R(z) = lambda_i z^t,        deg R < 4.
```

Note 0344 then gives the complete nonconstant alternatives:

1. a high-multiplicity one-active-value branch, or
2. a rank-2 separating lambda plane supported on a balanced opposite-pair set
   in the quotient.

The second alternative is invariant under the quotient order-2 action.  Lifting
through `x -> x^d`, that quotient order-2 action is exactly the original
order-`2d` dyadic action.  Hence:

> If `k/d=4`, `S` is balanced and order-`d` stable, and the one-residue
> quotient has a rank-2 separating lambda plane, then `S` is order-`2d`
> stable.

This is the symbolic reason behind the Note 0346 observations:

```text
k=8,  d=2:  quotient (16,4) => order4 lift
k=16, d=4:  quotient (16,4) => order8 lift
k=32, d=8:  quotient (16,4) => order16 lift
```

---

## Scope

This lemma does not by itself prove that an arbitrary high-scale one-residue
separating branch first acquires an order-`d` stabilizer.  What it does prove
is the recursive lift mechanism once the branch has entered the dyadic
descendant family.  Together with Note 0344's base classification, the
remaining missing step is now isolated:

```text
primitive one-residue separating branch
  => enters an order-d orbit-union quotient with k/d=4
  => Note 0347 forces one more dyadic descent.
```

The high-multiplicity one-active-value branch remains separate and must still
be checked against the second row direction.
