# Note 0439 -- Closed-form proof: q-restricted same-parity 3-vec rank 3

**Date:** 2026-05-03 morning (Tier 3 rigor pass)
**Branch:** `main`
**Status:** Structural proof (no empirical residue) of the rank-3 claim
for the four q-restricted same-parity triples
$\{(4,8,12), (5,9,13), (6,10,14), (7,11,15)\}$ at $L_2 = (16, 4)$.
This closes a key empirical "atom" used in Notes 0434-0438.

---

## 1.  Statement

> **Theorem.**  Let $L_2 = (16, 4)$, $\mathbb{F}_q$ odd char with
> $16 \mid q-1$, $\omega \in \mathbb{F}_q^*$ primitive 16th root, $S$
> no-full.  For each q-restricted same-parity triple
> $\mathcal{T} \in \{(4,8,12), (5,9,13), (6,10,14), (7,11,15)\}$:
> $$\mathrm{rank}\, [\mathrm{HT}(t^r)]_{r \in \mathcal{T}} = 3.$$

---

## 2.  Proof (one of four cases; others identical)

We treat $\mathcal{T} = (4, 8, 12)$ (the q=0 evens).

**Setup.**  Suppose 3-vec dep:
$$\sum_{r \in \mathcal{T}} c_r \mathrm{HT}(t^r) = 0 \quad \text{in } \mathbb{F}_q^{|S|},$$
i.e., $p(\omega^s) = 0$ for all $s \in S$ where
$$p(t) := c_4 t^4 + c_8 t^8 + c_{12} t^{12}.$$

WTS: $(c_4, c_8, c_{12}) = 0$.

**Reduction.**  Factor:
$$p(t) = t^4 \cdot (c_4 + c_8 t^4 + c_{12} t^8) = t^4 \cdot q(t^4)$$
where $q(u) := c_4 + c_8 u + c_{12} u^2 \in \mathbb{F}_q[u]$.

For $\omega^s \neq 0$ (always true): $p(\omega^s) = 0 \iff q(\omega^{4s}) = 0$.

Let $\nu := \omega^4$.  Since $\omega$ has order 16, $\nu$ has order
$16/\gcd(4, 16) = 4$.  So $\nu$ is a primitive 4th root of unity in
$\mathbb{F}_q$, and $\{\nu^s : s \in \mathbb{Z}/16\mathbb{Z}\} = \mu_4 = \{1, \nu, \nu^2, \nu^3\}$
with $\nu^s$ depending only on $s \bmod 4$.

**Key observation.**  $q(u)$ is a polynomial of degree $\le 2$ in $u$, so
has at most 2 roots in $\mathbb{F}_q$ (in particular, at most 2 roots in
$\mu_4$).

**Case (a): $(c_4, c_8, c_{12}) \neq 0$ but $q$ identically zero.**  Then
$c_4 = c_8 = c_{12} = 0$, contradiction.

**Case (b): $(c_4, c_8, c_{12}) \neq 0$ and $q$ has at most 2 roots in
$\mu_4$.**  Let $R \subseteq \mu_4$ be the set of roots of $q$ in
$\mu_4$, $|R| \le 2$.

Then $q(\omega^{4s}) = 0 \iff \nu^s \in R \iff s \bmod 4 \in R'$
where $R' := \{c \in \{0, 1, 2, 3\} : \nu^c \in R\}$, $|R'| = |R| \le 2$.

So $p(\omega^s) = 0 \iff s \bmod 4 \in R'$.

For $p(\omega^s) = 0$ for ALL $s \in S$: need $S \subseteq \{s : s \bmod 4 \in R'\}$.

**No-full constraint application.**  $S$ has $|S| = 8$ elements.  The set
$\{s : s \bmod 4 \in R'\}$ has $|R'| \cdot 4$ elements ($|R'|$ q-classes,
each with 4 elements in $\mathbb{Z}/16\mathbb{Z}$).

For $|R'| \le 2$: $|\{s \bmod 4 \in R'\}| \le 8$.

If $|R'| = 0$: no s satisfies, so $S = \emptyset$, contradicting $|S|=8$.

If $|R'| = 1$: $|\{s \bmod 4 \in R'\}| = 4 < 8 = |S|$, contradiction.

If $|R'| = 2$: $|\{s \bmod 4 \in R'\}| = 8 = |S|$.  So $S$ equals exactly
two q-classes, each with 4 elements.  But this means $|S \cap q\text{-class}_c| = 4$
for both $c \in R'$, **violating no-full** (which requires
$|S \cap q\text{-class}_c| \le 3$ for all $c$).

In all cases, contradiction.  Hence $(c_4, c_8, c_{12}) = 0$.  $\square$

---

## 3.  Other three triples

The same argument applies to $\mathcal{T} = (5, 9, 13)$, $(6, 10, 14)$,
$(7, 11, 15)$:

* $(5, 9, 13)$: factor $p(t) = t^5 (c_5 + c_9 t^4 + c_{13} t^8) = t^5 q(t^4)$.  Same $q(u)$ analysis.
* $(6, 10, 14)$: factor $p(t) = t^6 q(t^4)$.
* $(7, 11, 15)$: factor $p(t) = t^7 q(t^4)$.

All four cases reduce to the identical $q(u) = $ degree-$\le$-2 polynomial
in $u = t^4$, with the same $|R'| \le 2$ conclusion forced by no-full.

---

## 4.  Strategic significance

This Note **promotes** the four (4,8,12), (5,9,13), (6,10,14), (7,11,15)
rank-3 statements from "5-prime empirical" to "structural theorem
(field-uniform, scale-base-uniform)".

**Combined with Notes 0421-0423** (HT Pencil Rigidity, scale-uniform) and
**Note 0393** (pairwise high-tail parity lemma, FIELD-UNIFORM at L_2=(16,4)):

* The Side-Row Vanishing Lemma's $k = 3$ base case (Note 0438 §3.2) is
  **fully structurally rigorous**.
* The reductions for $k \in \{4, 5, 6\}$ in Note 0438 §3.3 still rely on
  a multi-element span statement ("strengthened HT rigidity"), which is
  empirical at 5 primes × 4.8M tests.

---

## 5.  Next rigor target

Promote the $k = 4, 5, 6$ same-side rank-$k$ statements from "5-prime
empirical" to "structural theorem".  The polynomial-factorization
approach used here may extend:

* For $k = 4$ parity (2,2): exponents $\{e_1, e_2, o_1, o_2\}$ with
  $e_i$ even ∈ {4,8,12} or u-side q=0, etc.  Factoring out $t^{\min}$
  gives a polynomial in $u = t^4$ AND $t$ (mixed degrees).  Need
  bivariate analysis.

* For $k = 5, 6$: similar, with more terms.

Output target: Note 0440 with $k = 4$ closed-form (if achievable).

---

## 6.  Final per-support rigor table (POST-Note 0439)

| support $k$ | Closure | Rigor level |
|---|---|---|
| 3 | paper2 §3 | Theorem (rigorous) |
| 4 | Tier 2 (Notes 0394, 0420-0423) | Theorem (rigorous) |
| 5 | Cases A-D (Note 0438) | Theorem; $k=3$ atom RIGOROUS (this Note); $k=4, 5$ empirical at 5 primes |
| 6 | Cases A-D | Same |
| 7 | Cases A-D | Same |
| 8 | Cases A-D | Same |
| 9-12 | Case D ($\min \ge 3$) | Theorem; the $k=3$ side row uses RIGOROUS k=3 atom |

So at $\min(u, v) = 3$ (the most common case for $k = 9..12$), the closure is now FULLY RIGOROUS.

For $\min(u, v) \in \{4, 5, 6\}$ (which arises for $k = 8, 10, 11, 12$): empirical at 5 primes, awaiting closed-form (next Note).

---

## 7.  Files

* This Note: `0439-q-restricted-3vec-closed-form.md`.
* Verification (no longer needed for rigor; empirical historical):
  - `issue419_q0_evens_3vec.py`.
