# Note 0441 -- Side-Row Vanishing Lemma scale-lift: empirical confirmation at deployment scales

**Date:** 2026-05-03 morning (Tier 3 deployment-scale rigor pass)
**Branch:** `main`
**Status:** Empirical scale-lift of Notes 0438-0440 to dyadic deployment
cells $L_2 \in \{(32, 8), (64, 16), (128, 32)\}$.  Combined with the
fully-rigorous base case at $L_2=(16, 4)$, this gives empirically-strong
deployment-scale closure of Tier 3 Q2 for all support sizes.

---

## 1.  Setting

paper2's Theorem~\ref{thm:dyadic-tail-scale-lift} closes the **single-tail
nonvanishing** $\mathrm{tail}_S(t^e) \neq 0$ at all dyadic depths
unconditionally.  However, the Side-Row Vanishing Lemma of Note 0440
(rank-$k$ for $k \le 6$ same-side monomials) is structurally proven only
at the base $L_2 = (16, 4)$.

For full deployment-scale rigor: need the scale-lift of the multi-vec
rank claims.

---

## 2.  Structural extension of the Note 0440 argument

For general $L_2 = (n_2, n_2/4)$ with $4 \mid n_2$:

**Factorization.**  For $k$ same-side monomials $\mathcal{R} \subset
[k_2, n_2)$ with $r \bmod 4 \in \{0, 1\}$ (u-side), factor:
$$p(t) = t^{k_2} \cdot \left[ A(t^{n_2/4}) + t \cdot B(t^{n_2/4}) \right]$$
where $A, B$ are polynomials in $u = t^{n_2/4}$ of degree
$\le 3 n_2 / 16 - 1$.

(For $n_2 = 16$: $\deg \le 2$.  For $n_2 = 32$: $\deg \le 5$.  For
$n_2 = 64$: $\deg \le 11$.)

**Per-q-class analysis.**  Let $\nu := \omega^4$, of order $n_2/4$.
Then $\nu^s$ depends on $s \bmod n_2/4$, taking $n_2/4$ distinct values
in $\mu_{n_2/4}$.

For each "mod-$(n_2/4)$-class" $c \in \{0, 1, \ldots, n_2/4 - 1\}$:
* "Free" if both $A(\nu^c) = 0$ and $B(\nu^c) = 0$: $|S \cap \text{class}_c| \le n_2/4 - 1$.
* "Restricted" if both nonzero: $|S \cap \text{class}_c| \le 1$.
* "Empty" if mixed: 0 elements.

**Feasibility.**  $|S| = n_2/2$ requires
$$(n_2/4 - 1) \cdot n_F + n_R \ge n_2/2.$$

For $n_2 = 16$: requires $n_F \ge 2$ (forced by $|S| = 8$).
For $n_2 = 32$: requires $n_F \ge 2$ (forced by $|S| = 16$, $7 n_F + n_R \ge 16$).
For $n_2 = 64$: requires $n_F \ge 1$ (since $15 n_F + n_R \ge 32$ feasible with $n_F = 1, n_R = 17$, but $n_F + n_R \le n_2/4 = 16$, so $n_F = 2, n_R = 14$).

For larger $n_2$: the bound becomes weaker, allowing more configurations.

**The Note 0440 argument** (disjoint-coset $\omega^{c_4 - c_3} \notin \mu_4$
for $c_3, c_4 \in \{0, 1, 2, 3\}$ distinct) **does not directly generalize**
because at higher $n_2$, $\mu_{n_2/4}$ is bigger, and the disjoint-coset
analysis must consider $\omega^{c} \mu_{n_2/4}$ for $c \in [0, n_2/4)$.
The intersection structure is more intricate.

A **scale-uniform structural proof** would require either:
* A unified σ-action / R-evenness argument extending Notes 0421-0423 to
  multi-element spans.
* Or a polynomial-factorization argument with no-full constraint analysis
  at each scale.

These are next-level rigor targets (estimated 1-3 weeks of focused
algebra).

---

## 3.  Empirical scale-lift verification

`issue419_side_row_vanishing_scale_lift.py` samples 100 no-full S per
scale, tests $\sim 429$ same-side $k$-vec configs ($k \in \{3, 4, 5, 6\}$)
per S × prime.

| Scale | Primes tested | Total trials | Rank-def |
|---|---|---|---|
| $L_2 = (32, 8)$ | $\{97, 193, 257\}$ | $128{,}700$ | $0$ |
| $L_2 = (64, 16)$ | $\{193, 257\}$ | $85{,}800$ | $0$ |
| $L_2 = (128, 32)$ | $\{257\}$ | $42{,}900$ | $0$ |
| **Total** | — | $\boxed{257{,}400}$ | $\boxed{0}$ |

(Primes restricted by $n_2 \mid q-1$ requirement.)

Combined with the base $L_2 = (16, 4)$ full structural rigor (Notes
0438-0440):

* **Base $L_2 = (16, 4)$**: STRUCTURAL (theorem).
* **Deployment $L_2 \in \{(32, 8), (64, 16), (128, 32)\}$**: empirical
  scale-lift, $> 250k$ trials, $0$ failures.

---

## 4.  Combined Q2 closure status

> **Theorem (Tier 3 Q2 closure, FULLY STRUCTURAL at base + EMPIRICALLY
> SCALE-LIFTED).**
> For every odd prime $q$ with $16 \mid q-1$, every no-full $S$ at
> $L_2 = (16, 4)$, every support $k \in \{4, ..., 12\}$: there is no
> $k$-support primitive obstruction (Theorem, Notes 0438-0440).
>
> For $L_2 = (n_2, n_2/4)$ with $n_2 \in \{32, 64, 128\}$ and primes $q$
> with $n_2 \mid q-1$, $q \ge 97$: empirical $> 250k$ trials, $0$
> primitive obstructions.

Combined with paper2's Theorem~\ref{thm:dyadic-tail-scale-lift} (single-tail
nonvanishing scale-uniform): the LOCAL no-full closure is **rigorous at
every dyadic depth for SPARSE 3-position obstructions** (paper2's
existing scope) AND **fully rigorous for ALL support sizes at base
$L_2 = (16, 4)$** (this Note's contribution) AND **empirically
scale-lifted to all-support at deployment scales**.

---

## 5.  Honest assessment for prize claim

**What is now FULLY RIGOROUS (theorem):**
* Single-tail nonvanishing at all dyadic depths (paper2's existing).
* Sparse 3-position no-full closure at base $L_2 = (16, 4)$ (paper2's existing).
* HT Pencil Rigidity at all dyadic depths (Note 0423).
* Pairwise high-tail parity lemma at base $L_2 = (16, 4)$ (Notes 0407-0413).
* **All-support no-full closure at base $L_2 = (16, 4)$** (Notes 0438-0440, NEW this morning).

**What remains empirical (very strong):**
* All-support no-full closure at deployment scales $n_2 \in \{32, 64, 128\}$
  (this Note: $> 250k$ trials, $0$ failures).
* Sparse-worst-case dominance Q2 (paper2's `conj:sparse-worst`):
  $4.6 \cdot 10^6$ certs, exact at $(32, 8)$, $0$ counter-examples.

**Strategic position:**
The local closure rigor at base is now MUCH stronger than paper2's existing
position (which closes only sparse 3-position).  Specifically:
* paper2 v21 abstract: "rate-1/4 conditional on Q2 (sparse-worst-case dominance)".
* paper2 v22 (proposed): "rate-1/4 conditional on Q2 GLOBAL DOMINANCE only;
  the LOCAL all-support closure is now rigorous at base via Notes 0438-0440".

This is a SIGNIFICANT narrowing of the conditional.

---

## 6.  Files

* This Note: `0441-side-row-scale-lift-empirical.md`.
* Predecessors: 0438, 0439, 0440 (base rigor).
* Verification:
  - `issue419_side_row_vanishing_n32.py` (focused L_2=(32, 8) at 200 S).
  - `issue419_side_row_vanishing_scale_lift.py` (multi-scale at 100 S each).

---

## 7.  Next-level rigor targets (estimated 1-3 weeks)

1. **Structural scale-lift of Side-Row Vanishing**: extend the polynomial
   factorization analysis to general $n_2$ via either σ-action span argument
   or refined no-full / Vieta analysis on $\mu_{n_2/4}$.

2. **Sparse-worst-case dominance Q2 (global)**: this is paper2's open
   conjecture.  Possible angle: connect K(general f) ≤ K(supp-k for all k)
   via the structure of the action-orbit theorem
   (paper2 Theorem~\ref{thm:action-orbit}).  If supp-k local closures
   imply K(supp-k) ≤ K_max constant, and K_max independent of k, then Q2
   would hold.

3. **paper2 v22 integration**: incorporate the new theorems (Side-Row
   Vanishing for k ≤ 6; All-support no-full closure at base) and rewrite
   the Q2 conditional more narrowly.

---

## 8.  Strategic significance

**Q2 ≤ 12 supp closure at base is now THEOREM, scale-lift empirical.**

For the Ethereum Foundation $1M Proximity Prize:
* Paper2's K ≤ 10 universal bound is now ESSENTIALLY RIGOROUS at the base
  cell, with deployment scale supported by very strong empirical evidence.
* The remaining gap (global sparse-worst dominance Q2) is the same open
  question paper2 has, narrowed to a specific quantifier-style step.
