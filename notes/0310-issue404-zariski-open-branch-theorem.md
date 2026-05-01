# Note 0310 — Issue #404: Zariski-open branch theorem

**Branch:** `issue-404`  
**Date:** 2026-04-30  
**Status:** replacement theorem for the surviving #404 deliverable.

## Executive status

The original #404 formulation is not provable because it is false: Note 0304
gives a dense joint-admissible saturated witness at
\((n,k,q,c)=(16,4,17,3)\).  The corrected output of this branch is therefore
not a dense-exclusion theorem.  It is a structural composition theorem:

> At the first rate-\(1/4\) proxy \((n,k,c)=(16,4,3)\), Paper 3 leading
> codimension strata contain explicit three-monomial sparse codimension-one
> branches with \(K\ge 9\).  The branch is a nonempty Zariski-open subset of
> the hyperplane \(b_8=\omega^{-2r}b_6\).

This is the strongest paper-safe statement currently supported by the
mathematics and scripts on `issue-404`.

## The finite-pattern theorem

Let \(F\) be an algebraically closed field of characteristic not dividing
\(16\), containing a primitive \(16\)-th root \(\omega\).  Work at
\((n,k,c)=(16,4,3)\), so the syndrome length is \(D=12\) and the relevant
weight threshold is \(w=D-c=9\).

For \(r\in\{0,\ldots,7\}\), set

\[
  B_r=\{i\equiv r\pmod 2\}\setminus\{r,r+8\},
  \qquad X_r=\{i\not\equiv r\pmod 2\}.
\]

Consider the sparse syndrome line

\[
  s_1=a_9S_9+a_{11}S_{11}+a_{12}S_{12},\qquad
  s_2=b_6S_6+b_8S_8+b_{12}S_{12},
\]

restricted to the branch hyperplane

\[
  H_r:\qquad b_8=\omega^{-2r}b_6.
\]

Then there is a nonempty Zariski-open subset \(U_r\subset H_r\) such that every
point of \(U_r\) has:

1. exact three-monomial support in each endpoint;
2. no common support of size \(w\), i.e. the pair is joint-above-\(\delta\);
3. eight distinct nonzero challenges
   \(\{\alpha_{r,x}:x\in X_r\}\) for which
   \(s_1+\alpha_{r,x}s_2\) lies on the Paper 3 leading support
   \(C_{r,x}=B_r\cup\{x\}\);
4. consequently \(K(s_1,s_2)\ge 9\), including the endpoint challenge
   \(\alpha=0\).

Moreover, over \(F_{193}\) each of the eight branches has an explicit point
with \(K=9\) and \(S^\ast=10=w+1\), so the open subset above is not only
nonempty but hits the Paper 3 leading stratum exactly in the checked proxy.

## Proof of the eight forced incidences

Fix \(r\) and \(x\in X_r\), and write

\[
  \rho=\omega^r,\qquad \tau=\omega^x,\qquad E=[16]\setminus C_{r,x}.
\]

The complement polynomial is

\[
  Q_E(z)=\prod_{i\in E}(z-\omega^i)
       =(z^2-\rho^2)\sum_{j=0}^{7}\tau^jz^{7-j}.
\]

The normal space to the support span \(V_E\subset F^{12}\) is spanned by the
coefficient vectors of \(Q_E,zQ_E,z^2Q_E\).  Substituting
\(s_1+\alpha s_2\) into these three normal equations gives

\[
  A_j+\alpha B_j=0,\qquad j=0,1,2,
\]

with

\[
  A_j=\tau^j(\tau^2-\rho^2)(a_9+a_{11}\tau^2+a_{12}\tau^3)
\]

and, after imposing \(b_8=\rho^{-2}b_6\),

\[
  B_j=\tau^j\left(b_8\tau+b_{12}(\tau^2-\rho^2)\tau^3\right).
\]

Thus all three equations are scalar multiples of a single equation.  Whenever
the denominator is nonzero, the unique challenge is

\[
  \alpha_{r,x}
  =
  -{(\tau^2-\rho^2)(a_9+a_{11}\tau^2+a_{12}\tau^3)
    \over b_8\tau+b_{12}(\tau^2-\rho^2)\tau^3}.
\]

This proves the eight forced Paper 3 leading incidences on a principal open
subset of \(H_r\).

## Why the open subset is nonempty

The remaining conditions are all Zariski-open:

- exact sparse endpoint support is
  \(a_9a_{11}a_{12}b_6b_{12}\ne0\);
- denominator and nonzero-challenge conditions are finitely many inequalities
  in \((a_9,a_{11},a_{12},b_6,b_{12})\);
- pairwise distinctness is
  \(\alpha_{r,x}\ne\alpha_{r,y}\), equivalently
  \(N_{r,x}D_{r,y}-N_{r,y}D_{r,x}\ne0\);
- joint-above-\(\delta\) is the complement of the finite union of closed
  conditions saying that both endpoints lie in a common weight-\(w\) support
  span;
- exact \(K=9\), when desired, is the additional complement of finitely many
  closed extra-incidence conditions.

The script

```bash
python3 notes/scripts/issue404_branch_certificate.py --p 193 --max-trials 1000
```

finds a point on each \(H_r\) satisfying all of these conditions with
\(K=9\) and \(S^\ast=10\).  Since \(193\equiv1\pmod {16}\), the specialization
\(\omega\mapsto64\in F_{193}\) is a valid reduction of the cyclotomic
coefficient ring.  A nonzero value after this reduction certifies that the
corresponding defining inequality is not the zero polynomial over
\(\mathbb{Q}(\omega)\).  Therefore the same finite list of inequalities defines
a nonempty Zariski-open subset in characteristic zero, and in any sufficiently
large compatible characteristic avoiding the finitely many bad reductions.
For auditability, the discovered \(F_{193}\) points are also hard-coded in a
deterministic verifier:

```bash
python3 notes/scripts/issue404_verify_branch_certificates.py
```

This verifier performs no random search; it checks the branch equation, the
closed-form challenges, joint-above-\(\delta\), \(S^\ast=10\), and exact
\(K=9\) for all eight branches.

The closed-form incidence formula was independently audited against raw
normal-equation linear algebra by

```bash
python3 notes/scripts/issue404_branch_formula_check.py --p 193 --trials 40
python3 notes/scripts/issue404_branch_formula_check.py --p 97 --trials 40
```

with zero failures in \(5120\) sampled branch/mover/trial checks.

## What this does and does not prove

This closes the corrected finite-pattern theorem behind #404:

- It proves that the Paper 3 leading codimension mechanism is compatible with
  sparse three-monomial witnesses.
- It identifies the actual algebraic locus: codimension-one branches, not a
  full six-coefficient open set.
- It gives exact \(K=9,S^\ast=10\) certificates in the first rate-\(1/4\)
  proxy.

It does **not** prove the original #404 dense-exclusion criterion, because
that criterion is false.  It also does not prove the full Paper 2
Conjecture~4.2 sparse-worst statement.  Its role in the paper should be an
evidence/theorem block explaining how Paper 3 codimension strata are reached
by sparse witnesses, not a replacement for the global sparse-worst conjecture.
