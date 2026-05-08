# Note 0373 -- Issue #396: deleted-polynomial fold for one-residue moments

> **Note number history**: filed as Note 0351 on the `issue-396`
> branch; renumbered to 0373 on `main` to avoid collision with already-
> absorbed content at slot 0351. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** structural reduction of the Note 0349 moment-rank entry lemma.

Artifacts:

- `notes/scripts/issue396_deleted_poly_moment_fold.py`
- `notes/scripts/issue396_deleted_poly_moment_fold.n16_q193.output.txt`
- `notes/scripts/issue396_deleted_poly_moment_fold.n32_q193.sample.output.txt`

---

## Purpose

Note 0349 rewrote the remaining one-residue entry lemma as a rank condition
on the `k x 4` moment matrix

```text
M_a(S)_{t,i} = sum_{s in S cap C_i} c_s s^{a+t}.
```

The weights `c_s` looked support-dependent and barycentric.  They are in fact
controlled by the deleted-point polynomial of the complement `B=L\S`.  This
note records the exact fold formula.

---

## Lemma 0351.A -- deleted-polynomial weights

Let `L` have order `4k`, let `S subset L` have size `2k`, and put

```text
F_S(X) = prod_{s in S} (X-s),
D_B(X) = prod_{b in L\S} (X-b).
```

Then

```text
F_S(X) D_B(X) = X^{4k} - 1.
```

For `s in S`, differentiating at `s` gives

```text
F'_S(s) D_B(s) = 4k s^{4k-1} = 4k s^{-1}.
```

Therefore the GRS dual multiplier from Note 0349 is

```text
c_s = 1/F'_S(s) = s D_B(s)/(4k).
```

This removes the interpolation weights from the problem.

---

## Lemma 0351.B -- folded coefficient formula

Write

```text
D_B(X) = sum_r d_r X^r,        deg D_B = 2k,
eta_i = zeta^i,                C_i = {x : x^k = eta_i}.
```

For `h=a+t+1`, the moment row is

```text
M_a(S)_{t,i}
  = (1/4) * sum_{r+h == 0 mod k} d_r eta_i^((r+h)/k).
```

Indeed,

```text
M_a(S)_{t,i}
 = (1/(4k)) sum_{s in S cap C_i} D_B(s) s^{a+t+1}
 = (1/(4k)) sum_{s in C_i} D_B(s) s^h,
```

because `D_B` vanishes on deleted points.  Expanding `D_B`, the root sum over
`C_i` is zero unless `r+h` is divisible by `k`; in the divisible case it is
`k eta_i^((r+h)/k)`.

Equivalently, split the deleted polynomial into its three `k`-blocks:

```text
D_B(X)
 = sum_{b=0}^{k-1} X^b (d_b + d_{b+k} X^k + d_{b+2k} X^{2k}),
```

with missing coefficients treated as zero.  Each moment row is a C4 evaluation
of one of these folded coefficient triples, up to the predictable phase
`eta_i^m`.

---

## Consequence for the entry lemma

The primitive separating branch from Note 0349 is no longer an arbitrary
rank condition on `2k` barycentric weights.  It is a condition on the folded
coefficient triples of the complement polynomial:

```text
(d_b, d_{b+k}, d_{b+2k}),        0 <= b < k.
```

Thus a separating rank-2 kernel means that these C4-evaluated folded triples
fail to span the generic three-dimensional moment space.  The next paper
lemma should prove that this rank loss forces a dyadic symmetry of `D_B`, or
equivalently a nontrivial orbit structure for `S`, unless the kernel is one
of the already charged equality-pattern branches.

This is a stronger target than the Note 0349 wording because the deleted
polynomial has roots constrained blockwise by `X^k-eta_i`.  The rank loss is
now visible as a coefficient relation between adjacent `k`-blocks of
`D_B(X)`, not as a black-box interpolation accident.

---

## Verification

The verifier checks the folded formula against the original barycentric
moment matrix exactly.

Complete base quotient:

```text
q=193, n=16, k=4, checked_systems=43584
identity: barycentric M_a(S) equals folded D_{L\S}(X) formula
moment_rank_hist={2: 4672, 3: 38912}
```

A sampled higher-scale run:

```text
q=193, n=32, k=8, checked_systems=16000
identity: barycentric M_a(S) equals folded D_{L\S}(X) formula
moment_rank_hist={2: 112, 3: 15888}
```

The displayed rank-2 samples include both mechanisms already known from
Notes 0344 and 0348:

- balanced order-2 stable separating planes;
- unbalanced empty-block / high-multiplicity one-active cases, which are rank
  collapse after Note 0348.

So Note 0351 does not close #396 by itself.  It gives the missing entry lemma
the right algebraic object: the complement polynomial's folded coefficient
profile.
