# Note 0096 — Sign-paired 2-primary descent: rigorous invariant case

**Date:** 2026-04-29  
**Branch:** `paper2-deployment-p0`  
**Status:** Partial closure of #382.  The descent step is rigorous for
antipodal-invariant witnesses; the remaining gap is forced antipodality.

## Setup

Let `k=2^s`, `n=4k`, and

\[
  h_\rho(z)=\rho z^{k+c}+z^{3k+c}=z^a(\rho+z^{2k}),
  \qquad a=k+c,\quad 0\le c<k.
\]

A half-set witness is `(S,r)` with `S subset mu_{4k}`, `|S|=2k`,
`deg r < k`, and `r(z)=h_rho(z)` on `S`.

Write the sign half-cosets as

\[
  L^+ = \{z:z^{2k}=1\},\qquad L^- = \{z:z^{2k}=-1\}.
\]

## Lemma 0096.A — antipodal witness descends

Assume `k` is even and `S=-S`.  Then the witness descends under `y=z^2` to a
sign-paired half-set witness at `k' = k/2`, with the same `rho`.

More explicitly, let `e = a mod 2` and write

\[
  a' = \frac{a-e}{2}=\frac{k}{2}+\left\lfloor\frac c2\right\rfloor.
\]

Then there exists a polynomial `R(y)` with `deg R < k/2` and a half-set
`T subset mu_{2k}` of size `k` such that

\[
  R(y) = y^{a'}(\rho+y^k) \qquad (y\in T).
\]

Since `mu_{2k}=mu_{4(k/2)}` and the exponent gap is `k=2(k/2)`, this is
exactly the sign-paired witness equation at the smaller parameter `k/2`.

### Proof

Because `S=-S`, for every `z in S` we also have `-z in S`.  The sign-paired
pencil satisfies

\[
  h_\rho(-z)=(-1)^a h_\rho(z),
\]

since the two monomial exponents differ by the even number `2k`.  Therefore

\[
  r(-z)-(-1)^a r(z)=0 \qquad (z\in S).
\]

The left side has degree `<k` and vanishes on `|S|=2k` distinct points, hence
it is identically zero.  Thus `r` has parity `a mod 2`, so

\[
  r(z)=z^e R(z^2)
\]

for some `R` with `deg R < k/2`.

Let `T={z^2:z in S}`.  Since `S=-S`, the squaring map is exactly two-to-one on
`S`, so `|T|=k`.  For `y=z^2`, divide the witness equation by `z^e`:

\[
  R(y)=y^{(a-e)/2}(\rho+z^{2k})=y^{a'}(\rho+y^k).
\]

This is the claimed smaller sign-paired witness. □

## Corollary 0096.B — invariant counterexamples reduce to the base case

If `k=2^s` and a non-fourth-root witness exists with `S=-S` at every descent
level, then iterating Lemma 0096.A gives a non-fourth-root witness at `k=1`.
But direct enumeration at `k=1` gives exactly `rho^4=1`.

Therefore no antipodal-invariant non-fourth-root counterexample exists at any
power-of-two `k`.

The same conclusion holds if the descent only becomes antipodal after finitely
many levels: start the iteration at the first invariant level.

## What remains for #382

The binding gap is now precise:

> **Forced antipodality lemma.**  For `k=2^s`, if a sign-paired witness with
> `rho^4 != 1` exists, then there is a sign-paired witness with the same `rho`
> whose support is antipodal-invariant.

Equivalently, among all witnesses for a fixed non-fourth-root `rho`, one can
choose a witness `S` with `S=-S`.

This is the missing bridge from the rigorous descent lemma to full #382
closure.

## Why the k=3 counterexample is not a contradiction

The Note 0094 counterexample is already antipodal and therefore descends once:

\[
  \mu_{12}\xrightarrow{z\mapsto z^2}\mu_6.
\]

The descent lands in a domain whose half parameter is `k'=3/2`, not in the
integer sign-paired tower `n'=4k'`.  Equivalently, the original `k=3` has an
odd factor and exits the `2`-primary chain.  This is exactly why the new target
must assume `k=2^s`.

## Next proof attempt

Work with the parity-defect polynomial

\[
  D(z)=r(-z)-(-1)^a r(z),\qquad \deg D<k.
\]

If `S` contains at least `k` antipodal-paired points, then `D` vanishes on at
least `k` points and hence `D=0`, making the witness antipodal and closing by
Lemma 0096.A.  Thus a minimal counterexample must have fewer than `k`
antipodal-paired points and more than `k` unpaired points.

The next target is a replacement/symmetrization lemma showing that such a
minimal unpaired witness can be modified, without changing `rho`, to increase
`|S cap (-S)|`.  Iterating would prove forced antipodality.
