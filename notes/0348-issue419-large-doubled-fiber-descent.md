# Note 0348 -- Issue #419: large doubled-fiber weighted quotient descent

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** all-scale large-doubled theorem for the weighted half-turn branch;
the complementary small-doubled case is closed by Note 0351.

Artifacts:

- `notes/scripts/issue419_small_doubled_random_probe.py`
- `notes/scripts/issue419_small_doubled_random_probe.h4q193.output.txt`
- `notes/scripts/issue419_small_doubled_random_probe.h8q257.output.txt`

---

## Setup

This note continues Notes 0346--0347.

Let the post-fold domain have size

```text
|L| = 8h,        k = 2h,
```

and quotient by the half-turn:

```text
pi: x -> y=x^2,        pi(L)=mu_{4h}.
```

Write a degree-`<2h` representative as

```text
rho(x)=A(y)+xB(y),        deg A, deg B < h.
```

Consider a half-turn eigenrow.  After stripping its character monomial, the
high quotient part has the form

```text
H(y)=y^{2h} C(y),        deg C < h.
```

For an even eigenrow, full quotient fibers impose

```text
A(y)=H(y),        B(y)=0.
```

For an odd eigenrow, full quotient fibers impose

```text
A(y)=0,           B(y)=H(y).
```

Thus the two parity characters are symmetric.  It suffices to discuss the
even case.

Let `D` be the set of doubled quotient fibers, i.e. fibers where `S` contains
both antipodal lifts.  Let

```text
d = |D|.
```

---

## Lemma 0348.A -- doubled fibers decouple the representative

If `d >= h`, then every weighted quotient interpolation solution has

```text
B=0
```

in the even branch, and

```text
A=0
```

in the odd branch.

**Proof.**  In the even branch, every doubled fiber forces `B(y)=0` at the
corresponding quotient point.  Since `deg B<h`, vanishing at at least `h`
distinct quotient points gives `B=0`.  The odd branch is identical with
`A` and `B` exchanged. ∎

---

## Lemma 0348.B -- large-doubled classification

Assume `d >= h`.  Let

```text
T = pi(S) subset mu_{4h}
```

be the quotient support.  Put

```text
T_+ = T cap {y : y^{2h}=+1},
T_- = T cap {y : y^{2h}=-1}.
```

Then a nonzero even or odd high quotient direction exists only if one parity
side has fewer than `h` sampled quotient points:

```text
min(|T_+|, |T_-|) <= h-1.
```

More precisely, if `|T_s| >= h` and `|T_{-s}|=m<h`, then the kernel has
dimension at most

```text
h-m.
```

After choosing the side `s`, every high quotient direction is represented by

```text
(y^{2h}-s) C(y),
```

where `C` has degree `<h` and vanishes on `T_{-s}`.

**Proof.**  By Lemma 0348.A, the even branch reduces to ordinary quotient
interpolation

```text
A(y)=y^{2h}C(y)       on T.
```

On the parity side `y^{2h}=s`, this is

```text
A(y)=sC(y),
```

or equivalently `(A-sC)(y)=0` on `T_s`.  Both `A` and `C` have degree `<h`, so
`A-sC` has degree `<h`.  If `|T_s|>=h`, then `A=sC` as polynomials.

If both parity sides have at least `h` sampled points, the same argument gives
simultaneously

```text
A=C,        A=-C,
```

so `A=C=0` because the characteristic is odd.

Therefore a nonzero solution requires one side, say `T_{-s}`, to have
`m<h` points.  The side `T_s` with at least `h` points forces `A=sC`.
On the other side the interpolation equation becomes

```text
sC(y) = -sC(y),
```

so `C` must vanish on `T_{-s}`.  The space of degree-`<h` polynomials
vanishing on `m` distinct points has dimension `h-m`.  Multiplication by
`y^{2h}-s` gives the displayed high quotient directions. ∎

---

## Relation to the base five-root lemma

For the base `L2=(16,4)` half-turn quotient, `h=2`.  The stabilizer witnesses
have profile

```text
0^3, 1^2, 2^3,
```

so `d=3>=h` and `|T|=5`.  Lemma 0348.B says a nonzero high direction requires
a `(4,1)` split across the two parity sides.  This is exactly Note 0347:

```text
T = mu_8^s union {t},       t^4=-s,
kernel generator = (y^4-s)(y-t).
```

Thus Note 0347 is the smallest instance of the large-doubled theorem.

---

## What remains

Together with Note 0351, the all-scale half-turn stabilizer branch splits into
two closed cases:

1. **Large doubled-fiber case (`d>=h`)**: classified by Lemma 0348.B.  Any
   nonzero high direction is already a quotient parity-tail direction
   `(y^{2h}-s)C(y)`, hence belongs to the charged descent bucket.
2. **Small doubled-fiber case (`d<h`)**: closed by Note 0351.  Before that
   proof, the random probe found no no-full weighted high-row survivor:

   ```text
   h=4, q=193, trials_per_d=3000:
     hit_hist={}

   h=8, q=257, trials_per_d=1500:
     hit_hist={}
   ```

   Note 0351 gives the missing proof by a parity-side multiplicity argument:
   after squaring the singleton equations, one quotient parity side has enough
   roots counted with multiplicity to force the relevant polynomial identity;
   the opposite side then kills the remaining high quotient polynomial.

This closes the half-turn weighted stabilizer sub-branch of #419.  The
remaining #419 work is global attachment: prove that every primitive rank-2
no-full bilateral allocation either has such a row-span stabilizer or is
already charged by the local complete-block / defect-root / singleton-tail
families.
