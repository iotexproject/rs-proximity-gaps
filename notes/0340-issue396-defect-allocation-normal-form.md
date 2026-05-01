# Note 0340 -- Issue #396: defect-allocation normal form for the multi-term gap

> **Note number history**: filed as Note 0336 on the
> `issue-419-l3-attachment` branch; renumbered to 0340 on `main` to avoid
> collision with `0336-scale-lift-CRT-reformulation` already on the trunk.
> Cross-references in the body to "Note 0335" refer to the singleton-tail
> proof, which lives at Note 0337 on `main`. Cross-references to
> "Notes 0321--0323" point to the quotient-`C4` complete-block machinery,
> which on `main` is consolidated into Note 0323
> (`issue396-block-interpolant-normal-form`).

**Date:** 2026-05-01
**Branch:** `issue-396` (originated on `issue-419-l3-attachment`)
**Status:** proof-level reduction of the remaining general-`f` component gap.

---

## Purpose

Note 0335 closed the singleton monomial tail obstruction at every dyadic
scale.  The remaining #396 gap is therefore not a local tail lemma.  It is the
multi-term question:

> when can a folded rank-2 row span have a saturated Johnson component that is
> not already charged to a two-block component, a defect-root substitution, or
> a deeper dyadic descendant?

This note rewrites that question as a finite-dimensional defect-allocation
problem on the four cyclotomic blocks.  The point is to remove the last
informal phrase "unstructured component" from the proof target.

---

## Setup

Let `L` be cyclic of order `4k`, with quarter blocks

```text
C_0, C_1, C_2, C_3,     |C_i|=k.
```

Let `W=span(u,v)` be a folded row span.  For a word `w`, let `R_i(w)` be the
unique degree-`<k` polynomial agreeing with `w` on `C_i`.

Let `S subset L`, `|S|=2k`, and put

```text
A_i = S cap C_i,        a_i=|A_i|,
d_i = k-a_i.
```

The vector

```text
d(S)=(d_0,d_1,d_2,d_3)
```

is the **block defect allocation**.  Since `|S|=2k`,

```text
d_0+d_1+d_2+d_3 = 2k.
```

For a subset `A_i subset C_i`, define

```text
Z_i(A_i) = { Q in F[x]_<k : Q|_{A_i}=0 }.
```

Then

```text
dim Z_i(A_i) = d_i.
```

---

## Lemma 0336.A -- saturated components are defect allocations

`S` is saturated for `W` iff there is a unique linear map

```text
rho_S : W -> RS_k(L)
```

such that, for every `w in W` and every block `C_i`,

```text
D_i^S(w) := R_i(w) - rho_S(w)   lies in   Z_i(A_i).
```

Equivalently, saturation is the existence of four block-defect maps

```text
D_i^S : W -> Z_i(A_i)
```

whose sum with the common low representative `rho_S` recovers the local
representatives:

```text
R_i(w) = rho_S(w) + D_i^S(w).
```

**Proof.**
If `S` is saturated, then for each `w in W` there exists a degree-`<k`
polynomial `rho_S(w)` agreeing with `w` on `S`.  It is unique because
`|S|=2k>k`.  Linearity in `w` follows from uniqueness.  On each block `C_i`,
both `w` and `R_i(w)` agree on `C_i`, while `rho_S(w)` agrees with `w` on
`A_i`; hence `R_i(w)-rho_S(w)` vanishes on `A_i`, so it lies in `Z_i(A_i)`.

Conversely, if such a `rho_S` exists, then on `A_i` the defect
`R_i(w)-rho_S(w)` vanishes.  Since `R_i(w)` agrees with `w` on `C_i`,
`rho_S(w)` agrees with `w` on every point of `A_i`.  The union of the `A_i` is
`S`, so `W|_S subset RS_k(S)`. ∎

---

## Immediate structural consequences

The normal form isolates exactly where known components enter.

### Dual linear system

Let

```text
E_i : F[x]_<k -> F^{A_i}
```

be evaluation on `A_i`, and let

```text
E_S : F[x]_<k -> F^S
```

be evaluation on all of `S`.  Since `|S|=2k>k` and the points are distinct,
`E_S` has rank `k`.  For each `w in W`, saturation is equivalent to the
compatibility of the overdetermined system

```text
E_i rho = E_i R_i(w),       i=0,1,2,3.
```

Equivalently, if `H_S` is any `k x 2k` parity-check matrix for the image of
`E_S`, then

```text
H_S ( R_0(w)|_{A_0}, R_1(w)|_{A_1}, R_2(w)|_{A_2}, R_3(w)|_{A_3} )^T = 0
```

for both basis vectors of `W`.

This is the dual version of Lemma 0336.A.  It shows that every remaining
component is cut out by two copies of the same `k` parity equations, with the
row-span dependence entering only through the four local representative maps
`R_i`.

### Full-block and two-block cases

If `d_i=0`, then `A_i=C_i`, so `Z_i(A_i)=0` and

```text
R_i(w)=rho_S(w)        for every w in W.
```

If `d_i=d_j=0`, then

```text
R_i(w)=R_j(w)          for every w in W,
```

so `C_i union C_j` is a two-block component by Notes 0321 and 0323.  Thus any
component with two full quarter blocks is already charged.

### Single-substitution cases

If `S=(H\{a}) union {b}` where `H=C_i union C_j`, then the allocation has

```text
d_i+d_j=1,       d_t+d_l=2k-1
```

with the missing point inside `H` and the intruder in the outside half.  Lemma
0321.B says the whole family is controlled by the common roots of the two
defect polynomials on the outside block.  In this normal form, this is exactly
the case where one block defect space in the base half has dimension one and
all deleted-point choices share the same low representative.

### Singleton tail cases

If one row direction has only one residual monomial beyond `RS_k`, then the
condition `D_i^S(w) in Z_i(A_i)` forces `x^e|_S in RS_k(S)` for some
`k<=e<4k`.  Note 0335 proves that the only `|S|=2k` equality cases are the
two parity halves, and both contain full quarter blocks.  Hence singleton
tails do not contribute to the no-full multi-term branch.

---

## The remaining theorem in normal-form language

After the known charges, a genuinely new component would have to satisfy all
of the following:

1. `d_i>0` for at least three blocks, and no two `d_i` are zero.
2. The common representative map `rho_S` is nonzero on a rank-2 row span.
3. For every block, the image

   ```text
   im(D_i^S) subset Z_i(A_i)
   ```

   has dimension at most `min(2,d_i)`.
4. The four local representative maps `R_i:W->RS_k` come from the folded
   above-Johnson support pattern, so their differences are constrained by the
   quotient-`C4` Fourier formula of Note 0323.

This is now the precise hard subclaim:

> **Defect-allocation obstruction.**  For folded above-Johnson row spans, any
> rank-2 solution of the four inclusions `D_i^S(W) subset Z_i(A_i)` is either
> a two-block component, a single-substitution defect-root family, a
> singleton-tail equality case from Note 0335, a full-code row, or it descends
> to the same statement on a smaller dyadic quotient.

The useful feature is that the unknown set `S` only appears through the four
vanishing spaces `Z_i(A_i)` and their dimensions `d_i`.  This is the right
shape for either:

- a Grassmannian/rank proof: show the four quotient-`C4` local maps cannot
  land in such low-dimensional vanishing spaces unless one of the charged
  cases occurs; or
- a dyadic descent proof: if all `Z_i(A_i)` are nonzero but none gives a
  charged component, the common zero sets define a saturated component after
  quotienting by a lower 2-power subgroup.

---

## Why this advances #396

The previous statement "prove no unstructured components" mixed three
different objects: the set `S`, its four occupancies, and the row-span local
representatives.  Lemma 0336.A separates them.

The issue #396 proof target can now be attacked by proving one explicit rank
obstruction for the maps

```text
R_i - rho_S : W -> F[x]_<k / Z_i(A_i),
```

instead of enumerating saturated subsets.  Notes 0321, 0323, and 0335 already
remove all cases where this obstruction degenerates to a full block, a
two-block equality, a one-point defect-root family, or a singleton monomial
tail.

Update after Note 0338: the smallest true bilateral case after the
singleton-tail branch, namely four-supports with side counts `(2,2)` in the
`L2=(16,4)` support window, has been certified over seven primes with no
primitive rank-2 no-full survivor.  This is empirical/finite rather than the
general proof, but it confirms that the obstruction in this note is already
visible at the first multi-term layer: nonzero-`alpha1` candidates collapse in
rank or enter the stabilizer bucket.

Update after Note 0339: the same collapse persists at the next support layer.
For five-supports at `q=193`, the full `L2=(16,4)` support window has no
primitive rank-2 no-full survivor across the `(2,3)/(3,2)` bilateral cases.
This strengthens the evidence that the required proof should be a structural
rank/stabilizer identity for quotient-`C4` local maps, not more monomial-tail
casework.
