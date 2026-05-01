# Note 0309 — Issue #404 status: what is solved, what remains

**Branch:** `issue-404`  
**Date:** 2026-04-30  
**Status:** #404 original acceptance is refuted as stated; a replacement
finite-pattern theorem is now explicit and partially proved.

## Current status

The original #404 acceptance target was:

> joint Fourier support \(\le 3\) iff the Paper 3 leading
> \(V_S\times V_S\) codimension \(2(c-1)\) is tight, hence dense pairs do not
> saturate.

This is false as an ambient statement.  Note 0304 gives a dense
joint-admissible saturated witness at the tiny exact proxy
\((n,k,q,c)=(16,4,17,3)\).  Thus Paper 3 codimension alone cannot prove
sparse-worst by dense exclusion.

The viable replacement target is narrower:

> identify the Paper 3 high-multiplicity strata, then prove that the
> deployment/Fourier-relevant top strata have sparse representatives with the
> same or larger \(K\).

This target is now concrete at the first rate-\(1/4\) proxy.

## Solved sub-result

For \((n,k,c)=(16,4,3)\), write

\[
  s_1=a_9S_9+a_{11}S_{11}+a_{12}S_{12},\qquad
  s_2=b_6S_6+b_8S_8+b_{12}S_{12}.
\]

For each \(r\in\{0,\dots,7\}\), set

\[
  B_r=\{i\equiv r\pmod 2\}\setminus\{r,r+8\},
  \qquad X_r=\{i\not\equiv r\pmod 2\}.
\]

On the codimension-one branch

\[
  b_8=\omega^{-2r}b_6,
\]

the complement family

\[
  C_{r,x}=B_r\cup\{x\},\qquad x\in X_r,
\]

gives eight explicit Paper 3 leading incidences.  The challenge value is

\[
  \alpha_{r,x}
  =
  -{(\tau^2-\rho^2)(a_9+a_{11}\tau^2+a_{12}\tau^3)
    \over b_8\tau+b_{12}(\tau^2-\rho^2)\tau^3},
  \qquad
  \rho=\omega^r,\quad \tau=\omega^x,
\]

when the denominator is nonzero.  This formula was derived from the complement
factorization

\[
  Q_E(z)=
  (z^2-\rho^2)\sum_{j=0}^7 \tau^j z^{7-j},
  \qquad E=[16]\setminus C_{r,x}.
\]

The formula is checked against raw normal-equation linear algebra by:

```bash
python3 notes/scripts/issue404_branch_formula_check.py --p 193 --trials 40
python3 notes/scripts/issue404_branch_formula_check.py --p 97 --trials 40
```

Both pass:

```text
p=193: checked=2560, failures=0
p=97:  checked=2560, failures=0
```

Together with the \(\alpha=0\) branch, this gives \(K\ge 9\) on the open
sub-locus where the eight denominators are nonzero, the eight \(\alpha\)'s are
distinct and nonzero, and the pair remains joint-admissible.

## What remains for a paper-grade finite theorem

The remaining proof obligations are now explicit nonvanishing statements:

1. **Distinctness:** prove
   \(\alpha_{r,x}\ne\alpha_{r,y}\) for \(x\ne y\) outside a proper
   coefficient hypersurface.
2. **Nonzero challenges:** prove \(\alpha_{r,x}\ne0\) outside a proper
   hypersurface.
3. **Joint admissibility:** prove no common support of size \(w=9\) occurs
   outside a proper hypersurface.
4. **No unwanted generic incidences:** if the goal is exact \(K=9\), show all
   other weight-9 supports occur only on proper hypersurfaces.  For #404's
   sparse-representative direction, exactness is not necessary; \(K\ge9\) is
   the relevant lower-bound mechanism.

The existing \(p=97,193\) representatives certify the open set is nonempty at
the first proxy.  For a fully field-uniform statement, the next step is to
write these nonvanishing conditions as explicit polynomials in
\((a_9,a_{11},a_{12},b_6,b_{12})\) and exhibit one symbolic specialization that
keeps them nonzero over \(\mathbb{Z}[\omega]\).

The finite-field nonemptiness certificate is now automated:

```bash
python3 notes/scripts/issue404_branch_certificate.py --p 193 --max-trials 1000
```

It finds one fixed specialization on each of the eight branches with

```text
K=9, S*=10=w+1,
```

and with the eight closed-form challenges defined, nonzero, and distinct.  A
typical run certifies all eight branches immediately:

```text
r=0 ... trial=0 K=9 Sstar=10
r=1 ... trial=0 K=9 Sstar=10
r=2 ... trial=0 K=9 Sstar=10
r=3 ... trial=1 K=9 Sstar=10
r=4 ... trial=0 K=9 Sstar=10
r=5 ... trial=0 K=9 Sstar=10
r=6 ... trial=0 K=9 Sstar=10
r=7 ... trial=1 K=9 Sstar=10
branch_certificate=PASS
```

## Issue-level conclusion

#404 should not be closed as originally stated.  Its original acceptance
criterion is false.  But the branch has produced a usable paper2/paper3
composition lemma:

> Paper 3 leading strata are hit by explicit three-monomial sparse codimension
> one branches with \(K\ge9\) at the first rate-\(1/4\) proxy.

This is a meaningful structural explanation of the sparse high-\(K\) witnesses
and a better theorem target than ambient sparse-vs-dense codimension
separation.
