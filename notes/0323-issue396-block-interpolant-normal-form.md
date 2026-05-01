# Note 0323 -- Issue #396: cyclotomic block-interpolant normal form

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** proof-level algebraic normal form for the dyadic component
program.

Artifacts:

- `notes/scripts/issue396_block_interpolant_normal_form.py`
- output: `notes/scripts/issue396_block_interpolant_normal_form.output.txt`

---

## Setup

Let `L=<omega>` have size `n=4k`, and let

```text
C_r = {omega^{r+4t} : 0 <= t < k},  r=0,1,2,3.
```

Thus the `C_r` are the four post-two-fold cyclotomic blocks.  Put

```text
zeta = omega^k,
```

so `zeta` is a primitive fourth root of unity.  For a polynomial

```text
P(x)=sum_e p_e x^e
```

viewed modulo `x^n-1`, let `R_r(P)` be the unique degree-`<k` polynomial
agreeing with `P` on `C_r`.

---

## Lemma 0323.A -- local interpolation is quotient-`C4` Fourier transform

For `0 <= a < k`,

```text
[x^a] R_r(P) = sum_m p_{a+mk} zeta^{r m}.
```

Equivalently, for each residue class `a mod k`, the four local representatives
`R_0(P),...,R_3(P)` are the length-4 Fourier transform of the folded
coefficient vector

```text
(p_a, p_{a+k}, p_{a+2k}, p_{a+3k}).
```

**Proof.**  If `x in C_r`, then `x=omega^r beta` with `beta^k=1`.  Hence

```text
x^{a+mk} = x^a (omega^r beta)^{mk}
         = x^a omega^{r m k}
         = x^a zeta^{r m}.
```

Collecting all monomials with exponent congruent to `a mod k` gives the
formula.  The right side has degree `<k` and agrees with `P` on all of `C_r`,
so uniqueness of interpolation on the `k` distinct points of `C_r` proves the
claim. ∎

---

## Lemma 0323.B -- two-block equality in coefficients

For two blocks `C_r,C_s`,

```text
P|_{C_r union C_s} in RS_k(C_r union C_s)
```

if and only if

```text
R_r(P)=R_s(P).
```

By Lemma 0323.A this is the explicit coefficient system

```text
sum_m p_{a+mk} (zeta^{r m} - zeta^{s m}) = 0,  0 <= a < k.
```

For a row span `W=span(u,v)`, the quarter-pair component condition is just
this system for `u` and for `v`.

This gives the general version of Note 0321's affine-linearity observation:
for two-round folded sparse rows, each coefficient of `u` and `v` is affine in
`alpha1`; therefore every two-block incidence equation is affine in
`alpha1`, at every `k`, not just at `(16,4)`.

---

## Lemma 0323.C -- defect roots are local-representative differences

Assume `H=C_r union C_s` is a two-block component for `P`, and write

```text
R_H(P)=R_r(P)=R_s(P).
```

On any outside block `C_t`, the defect polynomial from Note 0321.B is

```text
D_{H,t}^P(x) = R_t(P)(x) - R_H(P)(x),      deg D_{H,t}^P < k.
```

Thus a point `b in C_t` is an intruder root exactly when

```text
D_{H,t}^u(b)=0 and D_{H,t}^v(b)=0.
```

Consequently, for a non-full row, each outside block contributes at most
`k-1` intruders unless the two local representatives coincide on that whole
outside block, which promotes the row to an additional two-block equality.

**Proof.**  On `C_t`, both `P` and `R_t(P)` agree.  The representative on `H`
is `R_H(P)`, so the pointwise defect is exactly `R_t(P)-R_H(P)`.  A nonzero
degree-`<k` polynomial has at most `k-1` roots on the `k`-point block.  If it
vanishes on all of `C_t`, then `R_t(P)=R_H(P)`. ∎

---

## What this buys for #396

The dyadic component program no longer depends on black-box interpolation.
Every object in Notes 0321--0322 has an explicit quotient-`C4` formula:

```text
local representatives       = length-4 Fourier transforms over exponent mod k
two-block components         = equality of two quotient-Fourier fibers
single-substitution roots    = common roots of two degree-<k difference polys
full-code rows               = all four local representatives equal for u,v
```

This is a real proof handle.  In particular:

1. Quarter-pair rows are governed by affine systems in `alpha1` for all `k`.
2. Near-coset intruders are ordinary common roots of explicit degree-`<k`
   local-difference polynomials.
3. The only remaining hard classification is now sharply stated:

> prove that a saturated `2k`-set for a folded above-Johnson row span must
> contain a dyadic two-block base, unless the row is full-code or belongs to a
> deeper dyadic refinement.

That is stronger and more concrete than the earlier Fourier-erasure statement:
it identifies the exact low-degree polynomials whose common roots must be
controlled.

---

## Verification

The script checks the formula against direct polynomial reduction modulo
`prod_{x in C_r}(X-x)` and checks the two-block and defect-root equivalences.

Saved output:

```text
Issue #396 block-interpolant normal form
verified n=16, k=4, q=193: local formula, two-block equality, defect roots
verified n=32, k=8, q=193: local formula, two-block equality, defect roots
verified n=64, k=16, q=257: local formula, two-block equality, defect roots
```

This is not a closure of #396 by itself, but it turns the hard part into a
specific cyclotomic local-representative classification problem.
