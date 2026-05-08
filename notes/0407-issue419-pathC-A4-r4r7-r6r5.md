# Note 0407 -- Issue #419: Path C field-uniform proofs for (r,r')=(4,7) and (6,5) at |A|=4

**Date:** 2026-05-02 (Tier 1c iteration 2 — first non-trivial Path C field-uniform proofs)
**Branch:** `main`
**Status:** **Closed-form, FIELD-UNIFORM** proof for two new pairs $(r, r') \in \{(4, 7), (6, 5)\}$
at $|A| = 4$, $L_2 = (16, 4)$.  Both proven by a clean **polynomial-degree
kill argument** that requires neither no-full constraints nor the 16th-root
structure beyond "$u_i$ are pairwise distinct".

Combined with Note 0405's $(4, 5)$: **3 of 36 pairs at $|A|=4$ now field-uniform**.

---

## 1.  Setup recap

For (II) consistency at the 4 roots $\eta_c = u_c^2$ of $H(y)$ (where $u_c := \omega^{b_c}$,
the 4 singletons of $B$), the 4 derived values
$$
\lambda_c \;=\; \frac{-X(\eta_c)}{u_c \cdot \tilde Y_0(\eta_c)} \;=\; \frac{-X(u_c^2)}{u_c \cdot \tilde Y_0(u_c^2)}
$$
must all be equal.  We show: for the 3 pairs $(4, 5), (4, 7), (6, 5)$,
the 4 derived $\lambda_c$ **cannot all be equal** for any 4 distinct $u_c$
in $\mathbb{F}_q$.  No no-full constraint, no specific prime, just $u_i \ne u_j$.

Note: $u_c = \omega^{b_c}$ with $b_c$ distinct in $\mathbb{Z}/16$ and $\omega$ of
order $16$, hence $u_c$ are 4 distinct elements of $\mathbb{F}_q^*$.

---

## 2.  The polynomial-degree kill

**Define the auxiliary polynomial.**

* For $r = 4$ (so $X = 1$, $\tilde Y_0$ is degree $m - 2$ where $m = (r' - 1)/2$):
  $$
  \lambda_c = K \;\Longleftrightarrow\; u_c \cdot \tilde Y_0(u_c^2) \;=\; -1/K \;=:\; K'.
  $$
  Define $g_{r'}(u) := u \cdot \tilde Y_0(u^2)$.  Note: $\tilde Y_0(u^2)$ is even in $u$,
  so $g_{r'}$ is **odd** in $u$, with $\deg g_{r'} = 2(m - 2) + 1 = 2m - 3 = r' - 4$.

* For $r' = 5$ (so $\tilde Y_0 = 1$, $X$ is degree $r/2 - 2$):
  $$
  \lambda_c = K \;\Longleftrightarrow\; X(u_c^2) \;=\; -K u_c.
  $$
  Define $h_r(u) := X(u^2) + K u$ (treating $K$ as a parameter).  $X(u^2)$ is even,
  $\deg X(u^2) = r - 4$.  $\deg h_r = \max(r - 4, 1)$.

**The kill.**  In either case, the 4 distinct $u_c$ must be roots of a single
univariate polynomial $g_{r'}(u) - K'$ or $h_r(u)$.  A nonzero polynomial of
degree $d$ has at most $d$ distinct roots.  So if $d < 4$, we cannot have 4
distinct roots, contradiction.

| Pair | $\deg X$ | $\deg \tilde Y_0$ | Kill polynomial degree | Verdict |
|---|---|---|---|---|
| $(4, 5)$ | 0 | 0 | $\deg(u - K') = 1$ (Note 0405) | $1 < 4$, **KILLED** |
| $(4, 7)$ | 0 | 1 | $\deg(u^3 + s_1 u - K') = 3$ | $3 < 4$, **KILLED** |
| $(6, 5)$ | 1 | 0 | $\deg(u^2 - K u + s_1) = 2$ | $2 < 4$, **KILLED** |
| $(4, 9)$ | 0 | 2 | $\deg(u^5 + s_1 u^3 + h_2 u - K') = 5$ | $5 \ge 4$, degree-kill insufficient |
| $(8, 5)$ | 2 | 0 | $\deg(u^4 + ... + K u + ...) = 4$ | $4 \ge 4$, degree-kill insufficient |
| $\ldots$ | | | | |

So **$(4, 5), (4, 7), (6, 5)$ are killed cleanly by polynomial degree alone**.
The kill is **field-uniform** (no exceptional primes), requires only that $\omega$
have order $\ge 16$ in $\mathbb{F}_q^*$ (so the $u_c$ are distinct elements
of $\mathbb{F}_q$), and uses no no-full constraint.

---

## 3.  The closed-form polynomials (verification)

### (4, 7): $X = 1$, $\tilde Y_0(y) = y + s_1$

**Derivation.** $m = 3$, so $Y_0(y) = y^3 - h_2 y + p s_1$ where
$h_n := \sum_{i+j=n} \zeta_1^i \zeta_2^j$, $s_1 = \zeta_1+\zeta_2$, $p = \zeta_1\zeta_2$.

Polynomial division by $G_A(y) = y^2 - s_1 y + p$:
$$
y^3 - h_2 y + p s_1 \;=\; (y + s_1)(y^2 - s_1 y + p) \;+\; (s_1^2 - h_2 - p) y \;=\; (y + s_1) G_A(y),
$$
since $h_2 = s_1^2 - p$, the remainder vanishes.  So $\tilde Y_0(y) = y + s_1$.

**Kill polynomial.**  $g_7(u) = u \tilde Y_0(u^2) = u(u^2 + s_1) = u^3 + s_1 u$.
For $\lambda_c = K$: $g_7(u_c) = -1/K =: K'$.  Equation $u^3 + s_1 u - K' = 0$
has degree 3, at most 3 distinct roots.  4 distinct $u_c$ cannot all be roots.

> **Theorem (Path C, $|A|=4$, $(r,r') = (4,7)$).**  For every odd characteristic
> with $16 \mid q-1$, every choice of $\zeta_1, \zeta_2 \in \mathbb{F}_q^*$, and every
> 4 distinct $u_1, u_2, u_3, u_4 \in \mathbb{F}_q^*$, the 4 derived values
> $\lambda_c = -1/(u_c (u_c^2 + s_1))$ cannot all be equal.  Hence the (II)
> compatibility test fails, and no opposite-parity proportionality
> $\mathrm{HT}(t^4) \propto \mathrm{HT}(t^7)$ exists.

### (6, 5): $X(y) = y + s_1$, $\tilde Y_0 = 1$

**Derivation.** $r/2 = 3$, $P + y^3 = G_A(y) X(y)$ with $\deg P < 2$.
$P(\zeta_i) = -\zeta_i^3$ gives $P(y) = -h_2 y + p s_1$ (linear interpolation).
Polynomial division:
$$
y^3 - h_2 y + p s_1 \;=\; (y + s_1)(y^2 - s_1 y + p),
$$
identical to (4,7)'s computation.  So $X(y) = y + s_1$.

**Kill polynomial.**  $\lambda_c = -X(u_c^2)/u_c = -(u_c^2 + s_1)/u_c$.

Setting $\lambda_c = K$: $u_c^2 + s_1 = -K u_c$, i.e., $u_c^2 + K u_c + s_1 = 0$.
Degree 2, at most 2 distinct roots.  4 distinct $u_c$ cannot all be roots.

> **Theorem (Path C, $|A|=4$, $(r,r') = (6,5)$).**  Same hypothesis as (4,7).
> The 4 derived values $\lambda_c = -(u_c^2 + s_1)/u_c$ cannot all be equal.

A direct alternative argument (without invoking polynomial degree):
$\lambda_i = \lambda_j$ gives $(u_i - u_j)(u_i u_j - s_1) = 0$, so $u_i u_j = s_1$
for the agreeing pair.  All 6 pairs agreeing forces $u_1 u_2 = u_1 u_3 \Rightarrow u_2 = u_3$, contradiction.

---

## 4.  Pair-wise stronger statement

Both (4, 7) and (6, 5) admit a sharper claim:

> **Lemma (pairwise $\lambda$-collapse → 1-parameter constraint).**
> For $(r, r') \in \{(4, 7), (6, 5)\}$, $\lambda_i = \lambda_j$ ($i \ne j$) is
> equivalent to:
> * $(4, 7)$: $u_i^2 + u_i u_j + u_j^2 + s_1 = 0$.
> * $(6, 5)$: $u_i u_j = s_1$.
>
> So pairwise collapse pins one polynomial expression in $(u_i, u_j, s_1)$
> to zero.  6 pairwise constraints with 4 unknowns $u_i$ + 1 unknown $s_1$
> give 6 conditions on 5 unknowns; over-determined modulo Vieta.

This stronger pairwise structure shows that the polynomial-degree
argument is *one specific way* to derive the contradiction.  An
equivalent direct elimination argument:

* $(6, 5)$: pairwise $u_i u_j = s_1$ + distinctness of $u$'s → contradiction (above).
* $(4, 7)$: pairwise $u_i^2 + u_i u_j + u_j^2 + s_1 = 0$.  From pairs $(1, 2)$ and $(1, 3)$:
  subtract → $(u_2 - u_3)(u_1 + u_2 + u_3) = 0$ → $u_1 + u_2 + u_3 = 0$.
  Similarly $u_1 + u_2 + u_4 = 0$, giving $u_3 = u_4$, contradiction.

Both arguments are field-uniform.

---

## 5.  Cumulative Path C status (after Notes 0405, 0407)

| Pair | Status | Method |
|---|---|---|
| $(4, 5)$ | ✓ FIELD-UNIFORM | $X = \tilde Y_0 = 1$ collapse, distinct $\omega^{-b_c}$ (Note 0405) |
| $(4, 7)$ | ✓ FIELD-UNIFORM | polynomial-degree kill (deg 3 < 4) (this) |
| $(6, 5)$ | ✓ FIELD-UNIFORM | polynomial-degree kill (deg 2 < 4) (this) |
| $(4, 9..15)$ | ⚙ degree $\ge 5$, needs extra structural argument | (next) |
| $(8..14, 5)$ | ⚙ degree $\ge 4$, needs extra structural argument | (next) |
| $(6..14, 7..15)$ | hard, both polynomials non-constant | Path B Sage / unified sub-lemma |

So **3 / 36 pairs at $|A|=4$ are now field-uniformly closed**, all by elementary
arguments (Vieta or polynomial-degree).  Remaining 8 easy pairs and 25 hard
pairs require additional algebra.

---

## 6.  Strategic observation

The clean polynomial-degree kill is a **sharp boundary** between trivially-easy
and structurally-rich pairs:

* **Polynomial degree $< 4$**: 3 pairs killed unconditionally.
* **Polynomial degree $\ge 4$**: kill polynomial admits 4 roots in principle;
  need to show that the **specific 4 roots being 16th-roots-of-unity** is
  obstructed.

For the 8 "easy but degree-insufficient" pairs (e.g., $(4, 9), (8, 5)$), the
next analytical tools are:
* **Vieta on the kill polynomial**: 4 of its roots are 16th roots; 5th root
  $u_5$ is forced to be $-(u_1+u_2+u_3+u_4)$, with constraints on
  $\sigma_3(u_1,...,u_5)$, $\sigma_4$, etc.  Need to show these are
  incompatible with $u_i$ being distinct 16th roots.
* **No-full constraint exploitation**: $b_i \ne b_j + 8$ means $u_i \ne -u_j$,
  i.e., $\{u_i\}$ and $\{-u_i\}$ are disjoint.  Plus mod-4 quadrant constraint.

These additional tools are likely sufficient for the next 8 pairs; each may
take 1-2 evenings of pen-and-paper.

---

## 7.  Next concrete artifact

Tier 1c iteration 3: tackle $(4, 9)$ via Vieta-on-kill-polynomial argument.

The kill polynomial is $u^5 + s_1 u^3 + h_2 u - K' = 0$.  If 4 distinct
16th-roots $u_1, ..., u_4$ are roots, then by Vieta (with 5th root $u_5$):
$E_1 = 0$, $E_2 - E_1^2 = s_1$, $E_3 = E_1 E_2 = 0$, $E_4 - E_1 E_3 = h_2$,
$E_5 = K'$.  So $E_1 + u_5 = 0$ → $u_5 = -E_1$.

Constraints:
* $E_1(u_1, ..., u_4) + u_5 = 0$ (sum of roots).
* $E_2(u_1,...,u_4) + u_5 E_1 = s_1$ (where $E$ are elementary on 4 vars).
  Substituting $u_5 = -E_1$: $E_2 - E_1^2 = s_1$.
* $E_3 + u_5 E_2 = 0$: $E_3 - E_1 E_2 = 0$, i.e., $E_3 = E_1 E_2$.

Show: under no-full ($u_i \ne -u_j$) plus $u_i$ distinct 16th roots, these
3 constraints + the requirement $s_1 = \zeta_1 + \zeta_2$ for some
$\zeta_1, \zeta_2 \in 8$th roots disjoint from $\{u_i^2\}$, are incompatible.

Output target: Note 0408.
