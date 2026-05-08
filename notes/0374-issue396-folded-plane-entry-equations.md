# Note 0374 -- Issue #396: folded-plane equations for the one-residue entry

> **Note number history**: filed as Note 0352 on the `issue-396`
> branch; renumbered to 0374 on `main` to avoid collision with already-
> absorbed content at slot 0352. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** explicit coefficient equations for the remaining moment-rank
entry lemma.

---

## Setup

Continue with Note 0351.  Let

```text
D_B(X)=prod_{b in L\S}(X-b)=sum_{r=0}^{2k} d_r X^r
```

be the complement polynomial, with `d_{2k}=1` and `d_r=0` outside
`0<=r<=2k`.

For the one-residue row `x^a Q(x^k)`, `0<=a<k`, Note 0351 gives

```text
M_a(S)_{t,i}
  = (1/4) * sum_{r+a+t+1 == 0 mod k} d_r eta_i^((r+a+t+1)/k).
```

Since `a+t+1` runs through `a+1,...,a+k`, every residue class modulo `k`
appears exactly once.  The only extra datum is whether the phase exponent is
`1` or `2`.

---

## Lemma 0352.A -- the shifted folded rows

For `0<=b<k`, define the folded triples

```text
u_b = (d_b, d_{b+k}, d_{b+2k}).
```

For fixed `a`, the row space of `M_a(S)` is the C4-evaluation of the following
three-coordinate vectors in the Fourier basis `(T,T^2,T^3)`:

```text
v_b^(a) = (d_b, d_{b+k}, d_{b+2k})       if 0 <= b < k-a,
v_b^(a) = (0,   d_b,     d_{b+k})        if k-a <= b < k.
```

Here the second line is the wraparound case

```text
T^2(d_b+d_{b+k}T+d_{b+2k}T^2)
  = d_{b+2k} + d_b T^2 + d_{b+k}T^3,
```

and `d_{b+2k}=0` for `b>0`, so the constant term vanishes in the actual
wraparound range.

The C4 evaluation map on the span of `(T,T^2,T^3)` is injective.  Therefore

```text
rank M_a(S) = rank span{v_b^(a) : 0<=b<k}.
```

---

## Corollary 0352.B -- rank-two is a plane equation

The rank-two entry condition is equivalent to the existence of a nonzero
linear form `(A,B,C)` such that

```text
A d_b + B d_{b+k} + C d_{b+2k} = 0,      0 <= b < k-a,
B d_b + C d_{b+k} = 0,                  k-a <= b < k.
```

The only place where the monic top coefficient `d_{2k}=1` enters is the
`b=0` equation in the first range:

```text
A d_0 + B d_k + C = 0.
```

For `b>0`, `d_{b+2k}=0`, so the first range also reduces to a two-term
relation between the low and middle coefficient blocks:

```text
A d_b + B d_{b+k} = 0,                  1 <= b < k-a.
```

Thus a rank-two one-residue branch forces the middle coefficient block
`(d_k,...,d_{2k-1})` to be piecewise proportional to the low coefficient
block `(d_0,...,d_{k-1})`, with exactly one boundary equation absorbing the
monic coefficient.

---

## Why this matters

The remaining Note 0349 entry lemma can now be attacked as:

```text
D_B has roots L\S blockwise inside X^k-eta_i,
the folded-plane equations above hold for some a,
the resulting lambda kernel is separating,
S is not already a dyadic descendant
  => contradiction.
```

This is substantially more rigid than the original moment formulation.  A
generic complement polynomial will not have its first two `k`-coefficient
blocks piecewise proportional across a cyclic cut.  The expected structural
proof is now to show that such a proportionality can persist under the
blockwise root constraints only when `D_B` is even after a dyadic substitution,
which is exactly the orbit-union descent branch handled by Note 0347.

The unbalanced empty-block cases seen in the verifier satisfy these plane
equations but have equality-pattern lambda kernels; they are already rank
collapse by Note 0348.  The primitive branch must therefore satisfy the same
plane equations while avoiding those equality patterns.

Sanity check: the shifted-triple rank equality was verified against the
original `M_a(S)` rank on all 43,584 base systems `(16,4,193)` and on 3,984
valid sampled no-full systems from `(32,8,193)`.
