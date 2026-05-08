# Note 0351 -- Issue #419: small-doubled branch closes by parity-side multiplicity

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** proof of the remaining small-doubled weighted quotient rank lemma from Notes 0349--0350.

---

## Purpose

Notes 0349--0350 reduced the remaining half-turn stabilizer branch to the
small-doubled regime

```text
|D| = d < h,
```

where `D` is the set of doubled quotient fibers under `x -> y=x^2` on
`mu_{8h}`.  Note 0350 formulated a product-gap Toeplitz rank lemma as the
remaining blocker.  This note gives a simpler proof: split the quotient
`mu_{4h}` into the two parity sides `y^{2h}=+1` and `y^{2h}=-1`, then use
multiplicity after squaring the singleton equations.

The proof closes the small-doubled weighted quotient lemma directly.  The
product-gap full-column-rank statement follows as a corollary because its
kernel is exactly the same weighted quotient kernel.

---

## Setup

Work over a field of odd characteristic containing the required `8h`-th roots
of unity.  Use the notation of Note 0349.  A degree-`<2h` representative is
written as

```text
rho(x)=A(y)+xB(y),        y=x^2,        deg A, deg B < h.
```

For an even high half-turn eigenrow, write

```text
H(y)=y^{2h} C(y),         deg C < h.
```

Let the quotient fibers be partitioned as

```text
D = doubled fibers,
E = empty fibers,
G = singleton fibers.
```

Since `|S|=4h` and the quotient has `4h` fibers,

```text
|D| = |E| = d,            |G| = 4h - 2d.
```

The even-branch equations are

```text
A(g)-g^{2h}C(g)=0,        B(g)=0,                  g in D,
A(g)+xi_g B(g)-g^{2h}C(g)=0,                       g in G,
```

where `xi_g^2=g` is the selected singleton lift.

For `s in {+1,-1}` define the quotient parity side

```text
Y_s = { y in mu_{4h} : y^{2h}=s }.
```

Write

```text
D_s = D cap Y_s,      E_s = E cap Y_s,      G_s = G cap Y_s.
```

Each side has `2h` quotient fibers, so

```text
|D_s| + |E_s| + |G_s| = 2h.                         (1)
```

---

## Theorem 0351.A -- small-doubled weighted quotient rank lemma

Assume `d<h`.  Then every even-branch solution of the weighted quotient
system above has

```text
A=B=C=0.
```

Consequently the high quotient direction is zero.  The odd branch has the
same conclusion by the explicit parity-swapped argument below, so the
small-doubled half-turn stabilizer branch is closed.

### Proof

For each parity side `Y_s`, put

```text
U_s(y) = A(y) - s C(y).
```

On that side the equations say:

- if `g in D_s`, then `U_s(g)=0` and `B(g)=0`;
- if `g in G_s`, then `U_s(g)=-xi_g B(g)`.

Squaring the singleton equations gives

```text
U_s(g)^2 = g B(g)^2,       g in G_s.
```

Define

```text
Z_s(y) = U_s(y)^2 - y B(y)^2.
```

Since `deg U_s, deg B < h`,

```text
deg Z_s <= 2h - 1.                                      (2)
```

The polynomial `Z_s` vanishes at every singleton point in `G_s`.  At every
doubled point in `D_s`, both `U_s` and `B` vanish.  Hence `Z_s` has a double
root there: indeed

```text
Z_s'(y) = 2U_s(y)U_s'(y) - B(y)^2 - 2yB(y)B'(y),
```

which is also zero whenever `U_s(y)=B(y)=0`.

Thus `Z_s` has at least

```text
|G_s| + 2|D_s| = 2h + |D_s| - |E_s|                  (3)
```

roots counted with multiplicity, using (1).

Because `|D|=|E|`, the two quantities `|D_s|-|E_s|` sum to zero over
`s=+1,-1`.  Therefore at least one side, call it `Y_s`, satisfies

```text
|D_s| >= |E_s|.
```

For this side, (3) gives at least `2h` roots counted with multiplicity.  By
(2), this forces

```text
Z_s(y) identically 0.
```

So

```text
U_s(y)^2 = y B(y)^2                                      (4)
```

as an identity in the polynomial ring.  Since the characteristic is odd and
`y` is not a square in `F[y]`, (4) implies

```text
U_s=0,        B=0.
```

Equivalently,

```text
B=0,          A=sC.                                      (5)
```

Now look at the opposite parity side `Y_{-s}`.  With `B=0`, every non-empty
fiber on that side imposes

```text
A(y)+sC(y)=0,
```

because `y^{2h}=-s`.  Using (5), this becomes

```text
2s C(y)=0
```

on every point of `D_{-s} union G_{-s}`.  The number of such non-empty fibers is

```text
|D_{-s}| + |G_{-s}| = 2h - |E_{-s}| >= 2h - d > h,
```

because `|E_{-s}| <= |E| = d < h`.  Since `deg C<h` and the characteristic is
odd, this forces `C=0`.  Then (5) gives `A=0`, and already `B=0`.

This proves the even branch.

For the odd branch the high row is `x y^{2h}C(y)`.  On side `Y_s`, set

```text
V_s(y)=B(y)-sC(y).
```

The doubled equations give `A(g)=V_s(g)=0`, and each singleton equation gives

```text
A(g)+xi_g V_s(g)=0.
```

Squaring gives

```text
A(g)^2 = g V_s(g)^2       on G_s.
```

Now use

```text
Z_s^{odd}(y)=A(y)^2-yV_s(y)^2.
```

It has degree at most `2h-1`, vanishes on `G_s`, and has double roots on
`D_s`.  The same side with `|D_s|>=|E_s|` therefore forces
`Z_s^{odd}=0`, hence `A=V_s=0` by the same nonsquare argument.  Thus
`A=0` and `B=sC`.  On the opposite side every non-empty fiber imposes
`B+sC=0`, so `2sC=0` at at least `2h-d>h` distinct points.  Hence `C=0`,
and then `A=B=0`. ∎

---

## Corollary 0351.B -- product-gap full-column-rank lemma

Let `S subset mu_{8h}` have size `4h` and fewer than `h` antipodal pairs.  Let

```text
Q_S(x)=prod_{s in S}(x-s)
```

and let

```text
T_S : F[x]_{<=2h-2} -> F^{3h-1}
```

be the joint forbidden-window map from Note 0350:

```text
M |-> (
  [x^{2h}]Q_SM, ..., [x^{4h-1}]Q_SM;
  [x^{4h+1}]Q_SM, [x^{4h+3}]Q_SM, ..., [x^{6h-3}]Q_SM
).
```

Then `T_S` has full column rank `2h-1`.

### Proof

A kernel vector `M` gives a polynomial

```text
P(x)=Q_S(x)M(x)
```

with support contained in

```text
{0,1,...,2h-1} union {4h,4h+2,...,6h-2}.
```

Writing

```text
P(x)=A(x^2)+xB(x^2)-x^{4h}C(x^2)
```

recovers exactly the even-branch weighted quotient system above.  Theorem
0351.A gives `A=B=C=0`, hence `P=0`.  Since `F[x]` is an integral domain and
`Q_S` is nonzero, `M=0`. ∎

---

## Consequence for #419 stabilizer branch

Combining this note with the previous reductions gives the half-turn
stabilizer closure chain:

1. Note 0345: descent must be formulated for row spans, not setwise supports.
2. Note 0346: row-span half-turn descent reduces to weighted quotient fibers.
3. Note 0347: the `h=2` large-doubled base witness is the five-root quotient
   lemma.
4. Note 0348: all-scale large-doubled case `d>=h` is classified and descends to
   a charged parity-tail bucket.
5. This note: all-scale small-doubled case `d<h` has no high quotient direction.

Thus the half-turn weighted stabilizer sub-branch of the defect-allocation
descent theorem is closed.  What remains for the full #419 master theorem is
checking that every primitive rank-2 no-full bilateral allocation either enters
this row-span stabilizer branch or one of the already charged local families
from Notes 0340--0344.

---

## Exhaustive regression at `h=4`

Although the proof above is field-uniform in odd characteristic, I also added
an exhaustive regression checker for the exact product-gap matrix:

```text
notes/scripts/issue419_product_gap_exhaustive.py
```

Over `F_193`, every `h=4` small-doubled configuration passes:

```text
d=0:      65,536 cases, rank 7 throughout
d=1:   3,932,160 cases, rank 7 throughout
d=2:  44,728,320 cases, rank 7 throughout
d=3: 164,003,840 cases, rank 7 throughout
```

This is not needed for the theorem, but it is useful regression coverage for
future edits of the product-gap formulation.
