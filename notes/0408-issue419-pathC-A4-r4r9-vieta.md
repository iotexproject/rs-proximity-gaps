# Note 0408 -- Issue #419: Path C field-uniform proof for (r,r')=(4,9) at |A|=4

**Date:** 2026-05-02 (Tier 1c iteration 3 — first Vieta-on-kill-polynomial result)
**Branch:** `main`
**Status:** **Closed-form, FIELD-UNIFORM** proof for $(r, r') = (4, 9)$ at
$|A| = 4$, $L_2 = (16, 4)$.  Holds for **every** odd prime $q$ with $16 \mid q-1$;
no exceptional primes.

The argument is computer-assisted: a finite enumeration of the 5760 no-full
$|A|=4$ S, each yielding 3 constraints in $\mathbb{Z}[\omega_{16}]$ (Vieta on the
degree-5 kill polynomial).  We verify (i) all 3 constraints are nonzero in
$\mathbb{Z}[\omega_{16}]$ for every S, and (ii) for every prime $q$ with $16 \mid q-1$
that could potentially zero them all simultaneously (bounded by the Galois
norms), no such joint-vanishing occurs.

---

## 1.  The kill polynomial and Vieta

Recall (Note 0407 §2): for $(r, r') = (4, 9)$:
* $X = 1$, $\tilde Y_0(y) = y^2 + s_1 y + h_2$ where $s_1 = \zeta_1+\zeta_2$,
  $h_2 = \zeta_1^2 + \zeta_1\zeta_2 + \zeta_2^2 = s_1^2 - p$, $p = \zeta_1\zeta_2$.

The (II) consistency condition $\lambda_c = K$ for all 4 c becomes:
$$
g(u_c) := u_c^5 + s_1 u_c^3 + h_2 u_c \;=\; -1/K \;=:\; K' \qquad (c = 1, 2, 3, 4).
$$
So $u_1, u_2, u_3, u_4$ are 4 of the (up to 5) roots of $g(u) - K' = u^5 + s_1 u^3 + h_2 u - K'$.

Let $u_5$ be the 5th root.  By Vieta on this quintic:
* $\sigma_1(u_1, ..., u_5) = 0$ (coefficient of $u^4$): $E_1 + u_5 = 0$, where $E_k := e_k(u_1, ..., u_4)$.
* $\sigma_2 = s_1$: $E_2 + u_5 E_1 = s_1$, so $E_2 - E_1^2 = s_1$.
* $\sigma_3 = 0$: $E_3 + u_5 E_2 = 0$, so $E_3 - E_1 E_2 = 0$, i.e., $E_3 = E_1 E_2$.
* $\sigma_4 = h_2$: $E_4 + u_5 E_3 = h_2$, so $E_4 - E_1 E_3 = h_2$.
  Substituting $E_3 = E_1 E_2$: $E_4 - E_1^2 E_2 = h_2$.

The 3 Vieta constraints:
$$
\boxed{\;\;\;(C1)\; E_2 - E_1^2 - s_1 = 0, \qquad (C2)\; E_3 - E_1 E_2 = 0, \qquad (C3)\; E_4 - E_1^2 E_2 - h_2 = 0.\;\;\;}
$$

For (II)-consistency: ALL THREE must vanish in $\mathbb{F}_q$.

---

## 2.  Reduction to $\mathbb{Z}[\omega_{16}]$

For each no-full S at $|A|=4$, the LHS of (C1), (C2), (C3) is an element of
$\mathbb{Z}[\omega_{16}]$ (since $u_c, \zeta_i$ are 16th- or 8th-roots of unity).
$\mathbb{Z}[\omega_{16}]$ is the ring of integers of the cyclotomic field
$K = \mathbb{Q}(\omega_{16})$, with $[K : \mathbb{Q}] = \varphi(16) = 8$.

The (II) test fails in $\mathbb{F}_q$ if and only if AT LEAST ONE of (C1), (C2), (C3)
is a nonzero element of $\mathbb{Z}[\omega_{16}]/\mathfrak{p}$, where $\mathfrak{p}$
is a prime of $\mathbb{Z}[\omega_{16}]$ above $q$.  When $16 \mid q-1$, $q$ splits
completely in $K$, so $\mathbb{Z}[\omega_{16}]/\mathfrak{p} = \mathbb{F}_q$.

A nonzero element $\alpha \in \mathbb{Z}[\omega_{16}]$ vanishes modulo $\mathfrak{p}$ above $q$
**only if** $q \mid N_{K/\mathbb{Q}}(\alpha)$, the integer Galois norm.

---

## 3.  Computer-assisted finite check

Script: `issue419_pathC_4_9_vieta_Zomega.py` enumerates all 5760 no-full
$|A|=4$ S, computes (C1), (C2), (C3) ∈ $\mathbb{Z}[\omega_{16}]$, and verifies:

> **All 5760 S have all 3 constraints $\ne 0$ in $\mathbb{Z}[\omega_{16}]$.**

Script: `issue419_pathC_constraint_norms.py` computes integer norms
$N(C_i)$ for $i = 1, 2, 3$ across all 5760 S and reports:

| Constraint | $\min |N|$ over S | $\max |N|$ over S |
|---|---|---|
| $|N(C_1)|$ | 2 | 5184 |
| $|N(C_2)|$ | 4 | 2312 |
| $|N(C_3)|$ | 578 | 28,076,096 |

**Bound on bad primes.**  For $q > 5184$, $q \nmid N(C_1)$ for any S, so $C_1$
is nonzero in $\mathbb{F}_q$ for all S.  Hence (II)-test fails for all $q > 5184$.

**For $q \le 5184$ with $16 \mid q-1$**: there are 83 such primes
($q \in \{17, 97, 113, 193, 241, 257, 337, ..., 5153\}$).  For each, we
check if any S has all 3 of $(C_1, C_2, C_3)$ vanishing mod $q$:

> **Joint-vanishing scan: 0 hits across all 83 primes × 5760 S.**

So for every prime $q \equiv 1 \pmod{16}$, every $|A|=4$ no-full S, the
(II)-test for $(r, r') = (4, 9)$ fails.

---

## 4.  Theorem statement

> **Theorem (Path C, $|A|=4$, $(r, r') = (4, 9)$).**
> For every odd prime $q$ with $16 \mid q-1$, every choice of orbit
> reps $\{a_1, a_2\} \subset \mathbb{Z}/8$, every choice of singletons
> $\{b_1, b_2, b_3, b_4\} \subset \mathbb{Z}/16$ satisfying the no-full
> constraint, and every $K \in \mathbb{F}_q$, the four derived values
> $\lambda_c = -1/(u_c \tilde Y_0(u_c^2))$ for $\tilde Y_0(y) = y^2 + s_1 y + h_2$
> are not all equal to $K$.
>
> Hence the (II) compatibility test fails, and no opposite-parity
> proportionality $\mathrm{HT}(t^4) \propto \mathrm{HT}(t^9)$ exists at $|A|=4$.

The proof is computer-assisted: 5760 S × 3 constraints × 83 small-prime
checks + a 5184-bound reasoning for large primes.  Verifiable by re-running
the two companion scripts.

---

## 5.  Comparison with Note 0407

| Pair | Method | Field-uniform? | Effort |
|---|---|---|---|
| (4, 5) | $X = \tilde Y_0 = 1$ collapse | ✓ pure (Note 0405) | 1 evening |
| (4, 7) | poly-degree kill (deg 3 < 4) | ✓ pure (Note 0407) | 1 evening |
| (6, 5) | poly-degree kill (deg 2 < 4) | ✓ pure (Note 0407) | (combined) |
| **(4, 9)** | **Vieta + Z[ω_16] enum** | **✓ computer-assisted** | **1 evening (this)** |

The (4, 9) proof is the first to use the **Vieta + cyclotomic-norm**
template.  The same template will scale to the remaining easy pairs
(higher-degree kill polynomials → more Vieta constraints → still finite
check in $\mathbb{Z}[\omega_{16}]$).

**Cumulative Path C field-uniform: 4 / 36 pairs at $|A|=4$.**

---

## 6.  Next concrete artifact

Tier 1c iteration 4: extend Vieta+norm to $(r, r') = (8, 5)$.

For (8, 5): $\tilde Y_0 = 1$, $X(y) = y^2 + s_1 y + h_2$ (by the same calculation
as Note 0407 with $r$ and $r'$ roles swapped — actually by a different
calculation: $r/2 = 4$, deg X = 2).  The kill polynomial is
$h_8(u) = X(u^2) + K u = u^4 + s_1 u^2 + h_2 + K u$.  Quartic in $u$,
4 roots possible.

For 4 distinct $u_c \in \mu_{16}$ to all be roots:
* $E_1 = 0$ (coef $u^3$)
* $E_2 = s_1$
* $E_3 = -K$
* $E_4 = h_2$

So 3 free parameters $(K, s_1, h_2)$ + 4 unknowns $u_1, .., u_4$ + 4 constraints
$\Rightarrow$ 1-parameter family.  Need extra structure (e.g., $s_1, h_2$ in
specific 8th-root form, no-full).

Output target: Note 0409.
