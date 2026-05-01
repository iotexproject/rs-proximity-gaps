# Note 0338 -- Issue #429: scale-lift closure review

> **Note number history**: filed as Note 0336 on the `issue-429` branch;
> renumbered to 0338 on `main` to avoid collision with the existing Note
> 0336 (scale-lift CRT-reformulation) on the trunk.

## Purpose

Issue #429 asks for a paper-grade proof of the general dyadic tail lemma from
Note 0334:

```text
L cyclic of order 4k, |S|=2k, S no-full across quarter blocks
  => x^e|_S notin RS_k(S) for every k <= e < 4k.
```

This note audits Note 0337 against that target.  The conclusion is that the
local scale-lift lemma is closed by an unconditional root-count proof.  The
proof is stronger than requested: it does not use that `k` is a power of two,
only that the field has odd characteristic and contains a cyclic subgroup of
order `4k`.

## Audited theorem

Let `L` be cyclic of order `4k`, and let `S subset L` have `|S|=2k`.  Suppose
there exists `p` with `deg p < k` such that

```text
p(x) = x^e        for every x in S,
```

where `k <= e < 4k`.  Write `e=ak+r`, `a in {1,2,3}`, `0 <= r < k`.  Then
the only possibilities are:

```text
a=2, S={x in L: x^(2k)= 1}, p=x^r,
a=2, S={x in L: x^(2k)=-1}, p=-x^r.
```

Both parity halves contain full quarter blocks, so no no-full `S` can occur.

## Case audit

### `a=1`

Set `F=x^(k+r)-p`.  Since `deg p<k`, the leading term of `x^(k+r)` cannot
cancel.  Thus `F` is nonzero and `deg F=k+r<2k`.  It cannot vanish on the
`2k` distinct points of `S`.

### `a=3`

On `L`, `x^(4k)=1`.

If `r>0`, then `x^(3k+r)=x^(-(k-r))` on `L`, so interpolation implies

```text
H(x)=x^(k-r)p(x)-1
```

vanishes on `S`.  This polynomial is nonzero: all monomials in
`x^(k-r)p(x)` have positive degree, so the constant term `-1` cannot cancel.
Also

```text
deg H <= (k-r)+(k-1)=2k-r-1 < 2k.
```

This contradicts the `2k` roots in `S`.

If `r=0`, use `H=x^k p-1`.  Again `H` is nonzero, `deg H<=2k-1`, and it
cannot vanish on all of `S`.

This closes the hardest branch from the issue statement without needing the
suggested Galois descent through `Q(zeta_k) subset Q(zeta_{2k})`.

### `a=2`

Let

```text
E=S cap {x in L: x^(2k)= 1},
O=S cap {x in L: x^(2k)=-1}.
```

The conditions are

```text
p-x^r vanishes on E,
p+x^r vanishes on O.
```

Both polynomials have degree `<k`.  If both are nonzero, then
`|E|<=k-1` and `|O|<=k-1`, contradicting `|S|=2k`.  Hence one is identically
zero.

If `p=x^r`, then `p+x^r=2x^r` has no roots on `L` in odd characteristic, so
`O` is empty and `S` is the full even parity half.  The case `p=-x^r` gives
the full odd parity half.

## Edge conditions

- The proof uses only distinct roots, so the existence of a cyclic subgroup
  of order `4k` is enough.
- Odd characteristic is required only for `2x^r` to be nonzero in the `a=2`
  branch.
- The `r=0` cases are covered explicitly for `a=2` and `a=3`.
- The no-full conclusion follows because the even half is `C_0 union C_2`
  and the odd half is `C_1 union C_3`.

## Acceptance status

Issue #429 acceptance criterion (1) is satisfied:

```text
Theorem with rigorous proof of the general dyadic tail lemma at all
k=2^j, j>=2.
```

The local path-(c) scale-lift obstruction is therefore no longer the blocker.
The remaining work for the larger sparse-worst/P3 program is global: attach
this singleton-tail closure to the full dyadic component decomposition from
Notes 0318--0322, rather than proving another same-local-scale lemma.
