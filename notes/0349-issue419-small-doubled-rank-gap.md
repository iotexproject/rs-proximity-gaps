# Note 0349 -- Issue #419: small-doubled weighted quotient rank gap

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** precise remaining gap after Notes 0346--0348.

---

## Current closure status of the stabilizer branch

The row-span stabilizer branch has been reduced as follows:

1. **Row-span, not setwise, descent** (Note 0345): `tau W=W` need not imply
   `tau S=S`.
2. **Weighted quotient descent** (Note 0346): after half-turn eigenspace
   decomposition, `S` becomes a weighted quotient support with fiber weights
   `0,1,2`.
3. **Base five-root lemma** (Note 0347): the `L2=(16,4)` stabilizer bucket is
   hand-proved; it is exactly a `(4,1)` quotient split.
4. **Large doubled-fiber theorem** (Note 0348): at arbitrary dyadic scale,
   if at least `h` quotient fibers are doubled, the weighted system decouples
   and is classified by a root-count argument.

Therefore the only remaining part of the stabilizer branch is:

```text
small doubled-fiber regime: d < h.
```

---

## Exact algebraic form

Let the half-turn quotient have size `4h`, and let the original post-fold
domain have size `8h`.  A degree-`<2h` representative decomposes as

```text
rho(x)=A(y)+xB(y),        y=x^2,        deg A,deg B<h.
```

For an even high eigenrow, write

```text
H(y)=y^{2h}C(y),          deg C<h.
```

Let:

- `D` be the doubled quotient fibers, `|D|=d`;
- `G` be the singleton quotient fibers, `|G|=4h-2d`;
- for each `g in G`, let `xi_g` be the selected lift, so `xi_g^2=g`.

The weighted interpolation equations are:

```text
A(g)-g^{2h}C(g)=0,        B(g)=0,                  g in D,
A(g)+xi_g B(g)-g^{2h}C(g)=0,                       g in G.
```

The odd branch is identical after exchanging `A` and `B`.

The goal is to prove:

> **Small-doubled rank lemma.**  If `d<h`, every solution of the above system
> has `C=0`.

Equivalently, the high quotient direction has zero image in the quotient by
ordinary representatives.  This would close the half-turn stabilizer branch
at all dyadic scales.

---

## Why the naive projection argument is insufficient

If we forget singleton signs and keep only the projection support

```text
T = D union G subset mu_{4h},
```

then the statement is false at larger `h`.  For example, at `h=4`, the
projection-only space

```text
span{1,...,y^{h-1}, y^{2h},...,y^{3h-1}}
```

has nonzero kernel on many `|T|>=2h` supports whenever one parity side is
under-sampled.

So the proof must use the signed singleton equations

```text
A(g)+xi_g B(g)-g^{2h}C(g)=0,
```

not just the projection set `T`.

---

## Evidence

The random probe in Note 0348 sampled the entire small-doubled range:

```text
h=4, q=193, d=0,1,2,3:
  sampled_nofull_by_d={0:3000, 1:3000, 2:3000, 3:3000}
  hit_hist={}

h=8, q=257, d=0,...,7:
  sampled_nofull_by_d={0:1500, ..., 7:1500}
  hit_hist={}
```

A second random test without the no-full filter also found no small-doubled
survivor at `h=2,3,4`.  This suggests the small-doubled lemma may be true
without no-full assumptions.

---

## Promising proof route

Define

```text
F(y)=A(y)-y^{2h}C(y).
```

The equations become

```text
F=0 and B=0 on D,
F(g) = -xi_g B(g) on G.
```

Here:

```text
F in span{1,...,y^{h-1}, y^{2h},...,y^{3h-1}},
B in span{1,...,y^{h-1}}.
```

Since `d<h`, the singleton set has size

```text
|G|=4h-2d > 2h.
```

The signed equations should force the graph of the rational function

```text
F/B
```

to equal `-xi_g` on too many square-root choices.  Squaring gives

```text
F(g)^2 = g B(g)^2          on G.
```

The obstacle is that the resulting polynomial has degree too large for an
immediate root-count proof after reduction modulo `y^{4h}-1`.  A successful
proof likely needs to exploit the gap in `F`'s spectrum:

```text
F has only low band [0,h-1] and high band [2h,3h-1].
```

This is now the exact mathematical blocker.

---

## Current stopping condition

I do not have a complete proof of the small-doubled rank lemma yet.  The
problem is now substantially narrower than the original #419 stabilizer
lemma:

```text
prove C=0 in one signed weighted quotient linear system when d<h.
```

No counterexample has been found.  The next high-ROI move is to attack the
spectral-gap rank statement directly, either by:

1. deriving a left-kernel certificate for the signed singleton matrix; or
2. proving a Chebotarev/Vandermonde-style rank lower bound for the two-band
   space `F` coupled to the low-band space `B`.

---

## Exact h=2 verification

As a finite base check, the script

```text
notes/scripts/issue419_small_doubled_exact_h2.py
```

enumerates every weighted half-turn configuration with `d<h` at `h=2`
over `F_193`.  This is the same quotient size used by the `L2=(16,4)`
base stabilizer bucket.

Output:

```text
Issue #419 exact h=2 small-doubled weighted quotient verification
q=193, h=2, total=3840
hist={(0, 0, 0): 256, (1, 0, 0): 3584}
bad={}
```

The tuple key is

```text
(doubled_count, even_high_dim, odd_high_dim).
```

Thus the small-doubled branch is fully closed at `h=2`: neither `d=0` nor
`d=1` permits a nonzero high quotient direction.

This complements Note 0347:

- `d>=h` at `h=2` is classified by the five-root quotient lemma;
- `d<h` at `h=2` is exactly verified by the rank computation above.

The remaining proof work is therefore only the all-scale `h>=4` signed
two-band rank statement.

---

## Stronger rank form observed

Further matrix inspection suggests a stronger statement than "the high
projection is zero."  In sampled small-doubled configurations, the full
weighted equation matrix has rank exactly `3h`, while its representative-only
submatrix has rank exactly `2h`.

For the even branch, the full matrix columns are

```text
A_0,...,A_{h-1}, B_0,...,B_{h-1}, C_0,...,C_{h-1}.
```

Each selected point contributes the row

```text
(1,y,...,y^{h-1}; x,xy,...,xy^{h-1}; -y^{2h},..., -y^{3h-1}).
```

The stronger conjectural lemma is:

> **Small-doubled full-rank lemma.**  If `d<h`, then this `4h x 3h`
> weighted matrix has column rank `3h`.

This immediately implies `C=0` modulo representatives, because the
representative submatrix has full column rank `2h` and the extra high columns
add exactly `h` new dimensions.

The sampled ranks were:

```text
h=4:  (d, rank_full, rank_rep, rank_full-rank_rep)
      (0,12,8,4), (1,12,8,4), (2,12,8,4), (3,12,8,4)

h=8:  (0,24,16,8), ..., (7,24,16,8)
```

This points to a clean Vandermonde/Chebyshev proof: no nonzero two-band
polynomial `A(y)-y^{2h}C(y)` can agree with `-xB(y)` on more than `2h`
unpaired square-root choices unless all three low polynomials vanish.

The reproducible probe is:

```text
notes/scripts/issue419_small_doubled_rank_probe.py
```

Outputs:

```text
h=4, q=193, trials_per_d=1000:
  every even/odd sample has (rank_full, rank_rep, difference)=(12,8,4)
  first_bad=None

h=8, q=257, trials_per_d=1000:
  every even/odd sample has (rank_full, rank_rep, difference)=(24,16,8)
  first_bad=None
```
