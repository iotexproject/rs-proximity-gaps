# Note 0308 — Issue #404: codimension-one sparse branch family

**Branch:** `issue-404`  
**Date:** 2026-04-30  
**Status:** finite-pattern target refined; the high-\(K\) mechanism is a
codimension-one family, not a full six-coefficient open set.

## Correction to Note 0307

Note 0307 proposed a generic coefficient open set for the support pattern

\[
  A=(9,11,12),\qquad B=(6,8,12).
\]

That is too strong.  Symbolic elimination of the three normal equations for
one of the observed complement families shows a linear coefficient constraint.
For example, for

\[
  C_x=\{2,4,6,10,12,14\}\cup\{x\},\qquad x\ {\rm odd},
\]

and

\[
  s_1=a_9S_9+a_{11}S_{11}+a_{12}S_{12},\qquad
  s_2=b_6S_6+b_8S_8+b_{12}S_{12},
\]

the \(3\times 2\) rank-one condition for the normal equations contains the
factor

\[
  b_6-b_8.
\]

Thus the observed high-\(K\) mechanism is not generic in all six coefficients.
It lives on a codimension-one sparse branch.

## Branch family

Let \(\omega\) be the primitive \(16\)-th root used for the domain.  For each
\(r\in\{0,\dots,7\}\), define

\[
  P_r=\{i\equiv r\pmod 2\},\qquad
  B_r=P_r\setminus\{r,r+8\},
\]

and let the moving point range over the opposite parity class

\[
  X_r=\{i\not\equiv r\pmod 2\}.
\]

The branch is

\[
  C_{r,x}=B_r\cup\{x\},\qquad x\in X_r,
\]

with coefficient constraint

\[
  b_8=\omega^{-2r}b_6.
\]

For generic coefficients on this hyperplane, the line
\(s_1+\alpha s_2\) meets every \(V_{[16]\setminus C_{r,x}}\) in a unique
challenge \(\alpha_{r,x}\).  Outside a proper exceptional locus these eight
challenges are distinct and nonzero.  Together with the \(\alpha=0\) branch,
this gives \(K\ge 9\).  Empirically, the generic value on these branches is
usually exactly \(K=9\), with occasional \(K=8,10\) on small exceptional
collisions or extra-incidence loci.

At \(p=193\), the eight concrete branches are:

```text
r=0: base=(2,4,6,10,12,14), ratio b8/b6=omega^0
r=1: base=(3,5,7,11,13,15), ratio b8/b6=omega^14
r=2: base=(0,4,6,8,12,14), ratio b8/b6=omega^12
r=3: base=(1,5,7,9,13,15), ratio b8/b6=omega^10
r=4: base=(0,2,6,8,10,14), ratio b8/b6=omega^8
r=5: base=(1,3,7,9,11,15), ratio b8/b6=omega^6
r=6: base=(0,2,4,8,10,12), ratio b8/b6=omega^4
r=7: base=(1,3,5,9,11,13), ratio b8/b6=omega^2
```

The Note 0307 witness is the \(r=0\) branch: \(b_6=b_8\).

## Verification

The branch-family checker verifies the eight forced incidences and samples the
remaining open conditions:

```bash
python3 notes/scripts/issue404_branch_family.py --p 193 --trials 20 --full-k-samples 20
```

Representative output:

```text
PARAM n=16 k=4 p=193 D=12 w=9 omega=64
family: base parity class minus {r,r+8}; movers are opposite parity; impose b8=omega^(-2r)b6
r=0 base=(2,4,6,10,12,14) ratio=omega^0=1 incidence=19/20 distinct=16/20 joint=20/20 fullK={9: 15, 8: 3, 10: 2}
r=1 base=(3,5,7,11,13,15) ratio=omega^14=9 incidence=19/20 distinct=17/20 joint=20/20 fullK={9: 17, 7: 1, 8: 2}
r=2 base=(0,4,6,8,12,14) ratio=omega^12=81 incidence=19/20 distinct=18/20 joint=20/20 fullK={9: 16, 7: 1, 10: 2, 8: 1}
r=3 base=(1,5,7,9,13,15) ratio=omega^10=150 incidence=19/20 distinct=17/20 joint=20/20 fullK={9: 16, 8: 2, 10: 1, 7: 1}
r=4 base=(0,2,6,8,10,14) ratio=omega^8=192 incidence=20/20 distinct=15/20 joint=20/20 fullK={8: 4, 9: 13, 10: 2, 7: 1}
r=5 base=(1,3,7,9,11,15) ratio=omega^6=184 incidence=20/20 distinct=18/20 joint=20/20 fullK={9: 16, 8: 2, 10: 2}
r=6 base=(0,2,4,8,10,12) ratio=omega^4=112 incidence=19/20 distinct=16/20 joint=20/20 fullK={9: 16, 10: 1, 7: 1, 8: 2}
r=7 base=(1,3,5,9,11,13) ratio=omega^2=43 incidence=20/20 distinct=15/20 joint=20/20 fullK={9: 15, 8: 4, 10: 1}
```

The failures are expected exceptional-locus events: denominator zero, alpha
collision, or extra support incidence.  The branch itself is stable.

## Proof route

The algebraic proof should use the complement polynomial.  If \(C=C_{r,x}\)
and \(E=[16]\setminus C\), then the normal space to \(V_E\subset F^{12}\) is
spanned by the coefficient vectors of

\[
  Q_E(z),\quad zQ_E(z),\quad z^2Q_E(z),
\]

where

\[
  Q_E(z)=\prod_{i\in E}(z-\omega^i).
\]

Write

\[
  \rho=\omega^r,\qquad \tau=\omega^x,\qquad \epsilon=\rho^8\in\{\pm1\}.
\]

Since \(x\) has the opposite parity, \(\tau^8=-\epsilon\).  The complement
polynomial is

\[
  \prod_{i\in C_{r,x}}(z-\omega^i)
  =
  {z^8-\epsilon\over z^2-\rho^2}\,(z-\tau),
\]

and therefore

\[
  Q_E(z)
  =
  {z^{16}-1\over \prod_{i\in C_{r,x}}(z-\omega^i)}
  =
  (z^2-\rho^2){z^8+\epsilon\over z-\tau}
  =
  (z^2-\rho^2)\sum_{j=0}^7 \tau^j z^{7-j}.
\]

Let \(q_d=[z^d]Q_E(z)\).  The relevant coefficients are

\[
  q_7=\tau^2-\rho^2,\quad q_6=\tau q_7,\quad q_5=\tau^2q_7,
  \quad q_4=\tau^3q_7,\quad q_3=\tau^4q_7,\quad q_2=\tau^5q_7,
\]

and

\[
  q_{10}=0,\qquad q_9=1,\qquad q_8=\tau.
\]

The three normal equations from \(Q_E,zQ_E,z^2Q_E\) evaluate on
\(s_1+\alpha s_2\) as

\[
  A_j+\alpha B_j=0,\qquad j=0,1,2.
\]

For the left endpoint,

\[
  A_j=\tau^j(\tau^2-\rho^2)
      (a_9+a_{11}\tau^2+a_{12}\tau^3).
\]

For the right endpoint, the constraint \(b_8=\rho^{-2}b_6\) gives

\[
  B_j=\tau^j\left(b_8\tau+b_{12}(\tau^2-\rho^2)\tau^3\right).
\]

Thus the three equations are scalar multiples of one equation, and the
challenge is

\[
  \alpha_{r,x}
  =
  -{(\tau^2-\rho^2)(a_9+a_{11}\tau^2+a_{12}\tau^3)
    \over b_8\tau+b_{12}(\tau^2-\rho^2)\tau^3},
\]

whenever the denominator is nonzero.  The remaining conditions
\(\alpha_{r,x}\ne 0\), \(\alpha_{r,x}\ne\alpha_{r,y}\), joint-admissibility,
and absence of unwanted extra incidences are explicit nonvanishing polynomial
conditions.  The \(p=193\) representatives above certify that this open set is
nonempty in the first rate-\(1/4\) proxy.

This is the current sharp finite-pattern theorem target for #404:

> For each \(r\), on a nonempty Zariski-open subset of
> \(b_8=\omega^{-2r}b_6\), the sparse branch above is joint-admissible and has
> \(K\ge 9\) at the \((16,4,c=3)\) proxy.

It is weaker than the original full-open claim but stronger and more accurate
than random evidence: it identifies the algebraic stratum that produces the
paper3 leading high-\(K\) sparse witnesses.
