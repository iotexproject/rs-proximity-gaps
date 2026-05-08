# Note 0449 -- Single-Monomial Side Closure: scale-uniform structural lemma

**Date:** 2026-05-03 afternoon (continuation, post k=12 closure)
**Branch:** `main`
**Status:** New scale-uniform structural lemma closing all same-side $k$-vec
configurations with parity $(k-1, 1)$ or $(1, k-1)$ at $L_2 = (n_2, n_2/4)$
for any $n_2 \ge 16$.

---

## 1.  Statement

**Lemma (Single-Monomial Side).**  At $L_2 = (n_2, n_2/4)$ with $16 \mid n_2$
and $32 \mid q - 1$, for every $k \ge 2$ and every same-side $k$-vec
configuration with parity $(k-1, 1)$ (or symmetrically $(1, k-1)$): every
no-full $S$ has rank $k$.

I.e., no nontrivial linear dependence exists among the $k$ rows
$\mathrm{HT}(t^r)|_S$ when one parity-class contributes exactly one monomial.

---

## 2.  Proof

WLOG consider u-side parity $(k-1, 1)$: $k-1$ monomials from q=0 evens
$\{n_2/4, n_2/4 + 4, \ldots, n_2 - 4\}$ and 1 monomial from q=1 odds
$\{n_2/4 + 1, n_2/4 + 5, \ldots, n_2 - 3\}$.

Factor $p(t) = t^{n_2/4} [A(t^4) + t \cdot B(t^4)]$ where:
- $A(u) \in \mathbb{F}_q[u]$ has $k-1$ nonzero coefficients, degree $\le n_2/4 - 1$.
- $B(u) = c \cdot u^d$ is a single monomial ($c \ne 0$, $d \in \{0, \ldots, n_2/4 - 1\}$).

Set $\nu := \omega^4$, a primitive $(n_2/4)$-th root of unity in $\mathbb{F}_q$.

For $p(\omega^s) = 0$ at $s \in S$: dividing by $\omega^{(n_2/4) s} \ne 0$,
$$
A(\nu^{s \bmod n_2/4}) + \omega^s \cdot B(\nu^{s \bmod n_2/4}) = 0.
$$

For each class $c \in \{0, 1, \ldots, n_2/4 - 1\}$ (mod $n_2/4$):
- $B(\nu^c) = c \cdot \nu^{cd} \ne 0$ (both $c$ and $\nu^{cd}$ nonzero).
- So $\omega^s = -A(\nu^c) / B(\nu^c)$, a **single specific value** in $\mathbb{F}_q^*$.

Within class $c$, the elements $s \in \{c, c + n_2/4, c + n_2/2, c + 3 n_2/4\}$
give 4 **distinct** $\omega^s$ values (since $\omega$ has order $n_2$).

Hence at most **1** element of $S$ lies in class $c$.

Total: $|S| \le n_2/4$ (one per class).

But by assumption $|S| = n_2/2 > n_2/4$.  **Contradiction.**

Therefore no such linear dependence exists.  $\square$

---

## 3.  Symmetric cases

By the same argument:
- **u-side parity $(1, k-1)$**: A is single monomial nonzero on $\mu_{n_2/4}$,
  B is $(k-1)$-monomial.  Per class $c$: $A(\nu^c) \ne 0$, so equation
  $A + \omega^s B = 0$ requires $B(\nu^c) \ne 0$ (else $A = 0$ contradiction)
  and forces $\omega^s$ to a single value.  Same conclusion.
- **v-side parities $(k-1, 1)$ and $(1, k-1)$**: identical argument with
  q=2 evens and q=3 odds.

---

## 4.  Empirical confirmation (script `issue419_k4_parity31_uside_n32.py`)

At $L_2 = (32, 8)$, $k = 4$:

| Parity | Configs | Trials/prime | Primes | Total trials | Rank-def |
|---|---|---|---|---|---|
| (3, 1) u-side | 120 | 12000 | $\{97, 193, 257\}$ | 36000 | **0** |
| (1, 3) u-side | 120 | 12000 | $\{97, 193, 257\}$ | 36000 | **0** |

Total: 72,000 trials, 0 rank-def.  Confirms the lemma.

---

## 5.  Coverage extension

This Lemma immediately closes:

| $k$ | Parity | $L_2$ scales |
|---|---|---|
| 2 | (1, 1) | all dyadic $\ge (16, 4)$ |
| 3 | (2, 1), (1, 2) | all dyadic |
| 4 | **(3, 1), (1, 3)** | **all dyadic (NEW for $L_2 \ge (32, 8)$)** |
| 5 | **(4, 1), (1, 4)** | **all dyadic (NEW)** |
| 6 | **(5, 1), (1, 5)** | **all dyadic (NEW)** |
| 7 | **(6, 1), (1, 6)** | **all dyadic (NEW)** |
| ... | ... | ... |

For $k = 4, 5, 6, 7, \ldots$ at $L_2 = (32, 8)$: parity $(k-1, 1)$ and
$(1, k-1)$ are the "near-balanced edge" cases that previously needed
empirical scans.  Now structurally closed.

---

## 6.  Updated rigor table at $L_2 = (32, 8)$ (replaces Note 0445 §4)

| $k$ | parity $(n_e, n_o)$ | Status |
|---|---|---|
| 3 | (3, 0) / (0, 3) | THEOREM (Note 0442) |
| 3 | (2, 1) / (1, 2) | THEOREM (Note 0449, this Note) |
| 4 | (4, 0) / (0, 4) | THEOREM (Note 0442) |
| 4 | (2, 2) | THEOREM (Note 0442 §3a-bis) |
| 4 | (3, 1) / (1, 3) | **THEOREM (Note 0449, this Note)** |
| 5 | (5, 0) / (0, 5) | THEOREM (Note 0442 ext.) |
| 5 | (3, 2) / (2, 3) | THEOREM (Note 0446) |
| 5 | (4, 1) / (1, 4) | **THEOREM (Note 0449, this Note)** |
| 6 | (6, 0) / (0, 6) | empirical (Note 0442 ext. needed) |
| 6 | (5, 1) / (1, 5) | **THEOREM (Note 0449, this Note)** |
| 6 | (4, 2) / (2, 4) | empirical |
| 6 | (3, 3) | empirical |
| 7-12 | varied | partial structural + empirical |
| 12 (full side) | (6, 6) | (1+ct²) extension via Note 0448 |

**Significant new structural coverage at $L_2 = (32, 8)$.**

Remaining structural gaps at $L_2 = (32, 8)$:
- $k = 6, 7, 8$ parities $(n_e, n_o)$ with $\min \ge 2$.
- Same-q-class for $k \ge 4$ (Note 0442 partial; $k = 4$ done, $k = 5+$
  needs extension).

---

## 7.  Strategic implication

Combined with previous structural closures (Notes 0438-0448):

**Q2 LOCAL closure at $L_2 = (32, 8)$ is now structurally complete for:**
- All $k \le 5$ same-side configurations.
- All $k$ same-side configurations with parity $\min(n_e, n_o) \le 1$.
- $k = 24$ full-high-tail saturation (Note 0448).

The intermediate parity gaps ($k \ge 6$ with $\min \ge 2$) remain empirical
but are covered by paper2's 4.6M deployment-scale certs.

For $L_2 \ge (64, 16)$: this Lemma applies identically, giving closure for
parity-edge cases at all higher dyadic depths.

---

## 8.  Files

* This Note: `0449-single-monomial-side-closure.md`.
* Script: `issue419_k4_parity31_uside_n32.py`.

---

## 9.  Why this works structurally

The key observation is that a **single monomial** $B(u) = c u^d$ has NO
roots in $\mu_{n_2/4}^*$ (since $c \ne 0$ and $\nu$ is a primitive root).
This means EVERY mod-$(n_2/4)$ class is "restricted" — not "free" — and
therefore admits at most 1 element of $S$.

The crucial constraint is $|S| = n_2/2 > n_2/4 = $ # classes, which makes
the "all classes restricted" scenario infeasible.

This argument is purely combinatorial and dimension-counting; no resultant
bounds, no irrationality arguments, no per-prime case analysis.  It is the
**cleanest structural closure** in the deployment-scale framework.
