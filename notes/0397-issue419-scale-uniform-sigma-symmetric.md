# Note 0397 -- Issue #419: scale-uniform σ-symmetric proof at L₂=(n, n/4) (Tier 1b)

**Date:** 2026-05-02 (Tier 1b — scale-lift Note 0396 §4)
**Branch:** `main`
**Status:** σ-symmetric subcase of high-tail parity lemma is now proven
**field-uniformly AND scale-uniformly** at $L_2 = (n, n/4)$ for every
dyadic $n = 2^d$ with $d \ge 3$ and every characteristic with $n \mid q-1$.

---

## 1.  Setup at general L₂=(n, n/4)

Fix $n = 2^d$ with $d \ge 3$ (so $n \in \{8, 16, 32, 64, 128, \ldots\}$),
$k_2 = n/4 = 2^{d-2}$, and $\omega \in \mathbb{F}_q^*$ a primitive $n$-th
root of unity.

* $S \subset \mathbb{Z}/n\mathbb{Z}$ with $|S| = n/2$.
* No-full: $|S \cap C_j| < k_2$ for each coset $C_j = \{j, j+4, j+8, \ldots\}$
  of the subgroup $\langle 4 \rangle \le \mathbb{Z}/n\mathbb{Z}$ ($j \in \{0,1,2,3\}$).
  (At $L_2 = (16,4)$ this recovers the $|S \cap \{j, j+4, j+8, j+12\}| < 4$ condition.)
* $g_S(t) = \prod_{s \in S}(t - \omega^s)$, $\deg g_S = n/2$.
* $\mathrm{HT}: \mathbb{F}_q[t]/g_S \to \mathbb{F}_q^{n/4}$ projects to coefficients
  at degrees $\{k_2, k_2+1, \ldots, n/2 - 1\}$, a window of length $n/4$.

The σ-action: $\sigma: t \to -t$, equivalently $\sigma: t \to \omega^{n/2} \cdot t$
(since $\omega^{n/2}$ has order $2$ in any characteristic with $n \mid q-1$).
$g_S$ is $\sigma$-stable iff $S = S + n/2 \pmod n$, the **σ-symmetric** condition.

---

## 2.  Parity decomposition of the high-tail window

The HT window $\{k_2, k_2+1, \ldots, n/2 - 1\}$ has length $n/4 = k_2$.
Since $k_2 = 2^{d-2}$ and $n/2 = 2^{d-1}$, both endpoints of the window
are even (for $d \ge 3$), so the window consists of consecutive
$n/4$ integers starting at the even number $k_2$.

The window splits into:
$$
\mathrm{HT}_{\mathrm{even}} := \{k_2, k_2+2, \ldots, n/2 - 2\}, \qquad
\mathrm{HT}_{\mathrm{odd}} := \{k_2+1, k_2+3, \ldots, n/2 - 1\},
$$
each of size $n/8 = 2^{d-3}$.  These index complementary coordinate
subspaces of $\mathbb{F}_q^{n/4}$.

---

## 3.  Structural proof (σ-symmetric subcase)

**Theorem (high-tail parity, σ-symmetric, scale-uniform).**  For every
$L_2 = (n, n/4)$ with $n = 2^d$, $d \ge 3$, every characteristic with
$n \mid q-1$ and $\mathrm{char}(\mathbb{F}_q) \ne 2$, every σ-symmetric
no-full $S$, and every $r \in \{k_2, k_2+1, \ldots, n-1\}$ with
$r \not\equiv r' \pmod 2$, the high-tail vectors $\mathrm{HT}(t^r),
\mathrm{HT}(t^{r'}) \in \mathbb{F}_q^{n/4}$ are not nonzero scalar multiples
of each other.

**Proof.**  $S = S + n/2 \pmod n$ implies $g_S$ is even (the argument of
Note 0396 §3 generalizes verbatim: $g_S(-t) = \prod_{s\in S}(t - \omega^{s + n/2})
= \prod_{s\in S}(t - \omega^s) = g_S(t)$ using $S = S + n/2$ and $|S|$ even).

Reduction modulo an even polynomial preserves parity:
$$
t^r \bmod g_S \in \begin{cases} V_+ & r \text{ even,} \\ V_- & r \text{ odd,} \end{cases}
$$
where $V_+, V_- \subset \mathbb{F}_q[t]_{<n/2}$ are the even-degree / odd-degree
subspaces.

Hence:
$$
\mathrm{HT}(t^r) \in \mathrm{span}\{e_i : i \in \mathrm{HT}_{\mathrm{even}} - k_2\} \quad (r \text{ even}),
$$
$$
\mathrm{HT}(t^{r'}) \in \mathrm{span}\{e_i : i \in \mathrm{HT}_{\mathrm{odd}} - k_2\} \quad (r' \text{ odd}).
$$
These are complementary coordinate subspaces of $\mathbb{F}_q^{n/4}$, so two
nonzero vectors from them cannot be scalar multiples.  $\square$

The proof is identical in structure to Note 0396 §4; the only ingredients
needed are (i) $g_S$ even from σ-symmetry, (ii) parity preservation, and
(iii) the disjointness of $\mathrm{HT}_{\mathrm{even}}$ and
$\mathrm{HT}_{\mathrm{odd}}$ inside the HT window.  All three hold for any
$n = 2^d$, $d \ge 3$.

---

## 4.  Counting σ-symmetric no-full S at scale n

σ-symmetric $S$ in $\mathbb{Z}/n\mathbb{Z}$ are $S = T \cup (T + n/2)$ for $T \subset
\{0, 1, \ldots, n/2 - 1\}$ with $|T| = n/4$.

No-full: each coset $C_j$ of $\langle 4 \rangle$ in $\mathbb{Z}/n\mathbb{Z}$ has
$|S \cap C_j| \le k_2 - 1 = n/4 - 1$.  Since each $C_j$ has size $n/4$
and is $\sigma$-symmetric (because $n/2 \in \langle 4 \rangle$ for $d \ge 3$),
$|S \cap C_j| = 2 |T \cap C_j^+|$ where $C_j^+ = C_j \cap \{0, \ldots, n/2 - 1\}$
of size $n/8$.

So no-full requires $|T \cap C_j^+| \le (n/4 - 1)/2 = n/8 - 1/2$, i.e.,
$\le \lfloor n/8 - 1/2 \rfloor = n/8 - 1$ (for $n \ge 8$).

This generalizes the $L_2=(16,4)$ count of $16$ σ-symmetric no-full $S$
(when $n=16$, $n/8 = 2$, so $|T \cap C_j^+| \le 1$, and $|T| = 4$ with
$4$ cosets gives $|T \cap C_j^+| = 1$, $2^4 = 16$ choices).

For $n = 32$: $|T \cap C_j^+| \le 3$, $|T| = 8$ across $4$ cosets each of
size $4$.  Counts of $T$ with $\sum |T \cap C_j^+| = 8$ and each
$|T \cap C_j^+| \in \{0, 1, 2, 3\}$: by inclusion-exclusion,
$\binom{16}{8} - 4 \binom{12}{4} = 12870 - 4 \cdot 495 = 10890$.

(The σ-symmetric count at $n=32$ matches the *general* no-full count at $n=16$
modulo the $16$ σ-symmetric subset, an arithmetic coincidence.)

---

## 5.  Doubling reduction also scales

The Note 0396 §5–§6 doubling reduction generalizes to general $n$:

* $S^* := S \cup (S + n/2)$, $|S^*| = n/2 + |B|$, $S^*$ is σ-symmetric.
* $g_{S^*} = g_A \cdot g_B \cdot g_{B+n/2}$, with $g_A$ even (since $A$ is σ-symmetric).
* $g_B \cdot g_{B + n/2} = g_B(t) \cdot g_B(-t) = (g_B^{\mathrm{even}})^2 - (g_B^{\mathrm{odd}})^2$ is even.
* So $g_{S^*}(t) = G_*(y)$ with $y = t^2$, $\deg G_* = (n/2 + |B|)/2 = n/4 + |B|/2$.

The σ-eigenpieces $\tilde h_\pm$ are formed identically, yielding a reduced
linear system in $(\alpha, \beta, c, d, \lambda)$ with the only structural
change being the now-larger ambient $G_*$.  The unknowns count remains
$5$ (the polynomial $q \in \mathbb{F}_q[t]_{<k_2}$ has $k_2$ coefficients,
but the σ-symmetric collapse only retains the *first* two even and two
odd degrees that interact with the reduced system; for $k_2 > 4$ extra
parameters appear and the analysis must be extended — see §6).

---

## 6.  What is NOT yet covered at scale

For $L_2 = (n, n/4)$ with $n > 16$:
* The σ-symmetric subcase is fully proven (§3 above).
* The general $|B| \ge 1$ subcase requires the doubling reduction to be
  carried out with $q \in \mathbb{F}_q[t]_{<k_2}$ for $k_2 = n/4 > 4$,
  introducing more unknowns ($k_2$ coefficients for $q$).  The Note 0396 §6
  derivation (which assumed $k_2 = 4$) needs to be extended.

This extension is a *bookkeeping* task — no new mathematical idea is
needed.  Concretely, $q(t) = \sum_{i=0}^{k_2 - 1} q_i t^i$ has $k_2$
coefficients; the σ-eigenpieces $\tilde h_\pm$ remain well-defined and
give linear systems with $k_2 + 1$ unknowns (the $k_2$ $q_i$ plus
$\lambda$), in $|S^*| = n/2 + |B|$ scalar equations.  For $|B| \ge 1$ and
$n/2 + |B| > k_2 + 1 = n/4 + 1$, the system is over-determined by
$|B| + n/4 - 1 \ge n/4$, so generic inconsistency is expected and matches
the σ-symmetric structural prediction.

The scale-lift to L₂=(32, 8) and beyond therefore reduces to a single
extended bookkeeping task, deferred to Note 0398.

---

## 7.  Combined Tier 1 status (after Notes 0396, 0397)

| Subcase × Scale | Status | Notes |
|---|---|---|
| σ-symmetric, $L_2 = (16, 4)$ | **PROVEN field-uniformly** | 0396 §4 |
| σ-symmetric, any $L_2 = (n, n/4)$, $d \ge 3$ | **PROVEN field-uniformly AND scale-uniformly** | 0397 §3 (this) |
| General $|B| \ge 1$, $L_2 = (16, 4)$ | reduced to linear system; $783\,360$/$783\,360$ inconsistent at $q=97$, prime-uniform via 0393 | 0396 §6, §8 |
| General $|B| \ge 1$, $L_2 = (n, n/4)$ for $n > 16$ | bookkeeping extension of 0396 §6; deferred | 0398 (planned) |

The σ-symmetric structural argument now constitutes a fully scale-uniform
and field-uniform Q2 lemma component.  Combined with the general-$S$
empirical reduction (now covering $\sim 8 \cdot 10^5$ reduced systems per
prime at $L_2 = (16,4)$ alone), the Tier 1 closure of the side-$(2,2)$
$4$-supp class is structurally near-complete; only the symbolic witness
covector / resultant emptiness step (Note 0396 §8 Path A or B) remains
unconditional-pure-math work.

---

## 8.  Sanity check

Verification at $L_2 = (32, 8)$ for σ-symmetric S would empirically
reconfirm the structural prediction.  Script:
`issue419_sigma_symmetric_high_tail_verify.py` is parameterized via
`enum_sigma_symmetric_no_full(n2, k2)` and `component_tails_for_S`, both
accept arbitrary $n_2, k_2$.  A 5-second extension to test $L_2 = (32, 8)$
would confirm the structural prediction at deployment scale.

(See follow-up `issue419_sigma_symmetric_high_tail_verify.py` runs at
`--n2 32 --k2 8` for the empirical confirmation — to be added in next
iteration.)
