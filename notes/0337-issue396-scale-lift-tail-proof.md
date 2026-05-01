# Note 0337 -- Issue #396: scale-lift proof for the dyadic tail lemma

> **Note number history**: filed as Note 0335 on the `issue-429` branch;
> renumbered to 0337 on `main` to avoid collision with the existing Note
> 0335 (codex-absorption-synthesis) on the trunk.

## Purpose

Note 0334 isolated the scale-lift gap behind the issue #396 no-full branch
and issue #429:
lift the exact `k=4` cyclotomic tail lemma from Note 0332 to arbitrary
block size `k=2^j`.  This note closes that gap by a root-count argument.

The proof is independent of the finite-field prime and does not require a new
same-scale sweep.  It works over any field of odd characteristic containing a
cyclic subgroup `L` of order `4k`; in particular it applies to the dyadic
`k=2^j` setting used in the FRI chain.

## Theorem

Let `L` be a cyclic subgroup of order `4k`, and let `S subset L` have
`|S|=2k`.  For `k <= e < 4k`, suppose there is a polynomial `p(x)` with
`deg p < k` such that

```text
p(x) = x^e        for every x in S.
```

Write `e = ak+r`, with `a in {1,2,3}` and `0 <= r < k`.  Then exactly one of
the following can occur:

1. `a=2`, `S` is the even parity half `{x in L : x^{2k}=1}`, and `p=x^r`.
2. `a=2`, `S` is the odd parity half `{x in L : x^{2k}=-1}`, and `p=-x^r`.

In particular, if `S` is no-full with respect to the four quarter blocks

```text
C_b = {x in L : x^k=i^b},        b=0,1,2,3,
```

then no such `p` exists.

## Proof

First take `a=1`, so `e=k+r`.  The polynomial

```text
F(x)=x^{k+r}-p(x)
```

has degree at most `2k-1`, and its leading term cannot be cancelled by `p`
because `deg p<k`.  If `F` vanished on `S`, it would have `2k` distinct roots
despite degree `<2k`, impossible.

Next take `a=3`, so `e=3k+r`.  On `L`, `x^{4k}=1`.

If `r>0`, then `x^{3k+r}=x^{-(k-r)}` on `L`.  Hence `p=x^e` on `S` implies

```text
x^{k-r}p(x)-1 = 0        for every x in S.
```

This polynomial is nonzero and has degree at most

```text
(k-r)+(k-1)=2k-r-1 < 2k,
```

so it cannot vanish on all `2k` points of `S`.

If `r=0`, the same argument uses

```text
x^k p(x)-1 = 0        for every x in S,
```

whose degree is at most `2k-1` and which is again nonzero.  Thus `a=3` is
impossible.

It remains to consider `a=2`, so `e=2k+r`.  On `L`,

```text
x^{2k} = +1    on the even parity half,
x^{2k} = -1    on the odd parity half.
```

Let

```text
E = S cap {x in L : x^{2k}=1},
O = S cap {x in L : x^{2k}=-1}.
```

The interpolation condition is exactly

```text
p(x)-x^r = 0        for x in E,
p(x)+x^r = 0        for x in O.
```

Both `p-x^r` and `p+x^r` have degree `<k`.  If both are nonzero, then

```text
|E| <= k-1,        |O| <= k-1,
```

so `|S|=|E|+|O| <= 2k-2`, contradiction.  Therefore one of these two
polynomials is identically zero.

If `p=x^r`, then `p+x^r=2x^r` has no roots on `L` in odd characteristic, so
`O` is empty and `S` is the full even parity half.  If `p=-x^r`, the symmetric
argument gives the full odd parity half.  This proves the classification.

Each parity half contains two full quarter blocks:

```text
even: C_0 union C_2,
odd:  C_1 union C_3.
```

Thus the no-full case is impossible.

## Consequence for #396 / #429

The scale-lift target from Note 0334 is now proved:

```text
no-full S, |S|=2k
  => x^e|_S is not in RS_k(S) for every k <= e < 4k.
```

Together with Note 0333, this removes the singleton residual side in the
primitive no-full branch at arbitrary dyadic scale.  A mixed strict-above-J
3-support cannot create a no-full saturated component through a monomial
tail; the only possible equality cases are the two parity halves, both of
which are full-block components and are handled by the two-block branch.

This is the rigorous scale-lift counterpart of the `k=4` exact cyclotomic
certificate from Note 0332.

Note 0336 records a targeted self-review against the issue #429 acceptance
criteria.
