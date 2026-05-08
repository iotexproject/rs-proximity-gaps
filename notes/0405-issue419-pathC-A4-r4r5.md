# Note 0405 -- Issue #419: Path C field-uniform proof for (r=4, r'=5) at |A|=4

**Date:** 2026-05-02 (Tier 1c — first concrete Path C closed-form result)
**Branch:** `main`
**Status:** **Closed-form, FIELD-UNIFORM** proof of the |A|=4 closure mechanism
for the specific exponent pair $(r, r') = (4, 5)$, valid in any odd
characteristic with $16 \mid q-1$.  No exceptional primes.

---

## 1.  The closed-form simplification

For $|A| = 4$ at $L_2 = (16, 4)$, the (II) compatibility test (Note 0400 §2)
gives 4 derived values $\lambda_c$ at the 4 roots $\eta_c = \zeta^c$ of $H$:
$$
\lambda_c = \frac{-X(\eta_c)}{\omega^{b_c} \cdot \tilde Y_0(\eta_c)}.
$$
Inconsistency requires the 4 values to *not* all be equal.

For the specific case $(r, r') = (4, 5)$:
* $r/2 = 2$, $\deg X = r/2 - 2 = 0$, so $X(y) \equiv X_0$ is constant.
  Computing: $y^2 \bmod G_A(y) = -L(y)$, $X(y) = (y^2 - L(y))/G_A(y)$.
  Since $G_A$ is monic of degree 2 and $y^2$ is monic of degree 2,
  the quotient $X(y) = 1$ (constant).
* $m = (r' - 1)/2 = 2$, $\deg \tilde Y_0 = m - 2 = 0$, so $\tilde Y_0(y) \equiv \tilde Y_{0,0}$ is constant.
  Computing $Y_0(y) = y^2 - s_1 y + (\zeta_1 s_1 - \zeta_1^2) = y^2 - (\zeta_1+\zeta_2) y + \zeta_1 \zeta_2 = G_A(y)$,
  so $\tilde Y_0(y) = 1$.

Hence:
$$
\lambda_c = \frac{-1}{\omega^{b_c}} = -\omega^{-b_c}, \qquad c \in \{b \bmod 8 : b \in B\}.
$$

The 4 derived $\lambda$ values are exactly $\{-\omega^{-b_1}, -\omega^{-b_2}, -\omega^{-b_3}, -\omega^{-b_4}\}$.

---

## 2.  Why all 4 must differ

The 4 elements $b_1, b_2, b_3, b_4 \in \mathbb{Z}/16\mathbb{Z}$ are the singletons
of $S$ (set $B$).  No two are σ-related (i.e., $b_i \ne b_j + 8$ for $i \ne j$),
nor σ-related to themselves in $S$.  So all 4 are *distinct in $\mathbb{Z}/16\mathbb{Z}$*.

$\omega$ has order $16$ in $\mathbb{F}_q^*$ (since $16 \mid q-1$).  Therefore
the map $b \mapsto \omega^{-b}$ is *injective* on $\mathbb{Z}/16\mathbb{Z}$, and
$\omega^{-b_1}, \ldots, \omega^{-b_4}$ are 4 distinct elements of $\mathbb{F}_q^*$.

Multiplying by $-1$ preserves distinctness.  So $\lambda_1, \ldots, \lambda_4$
are 4 distinct values.

> **Theorem (Path C, |A|=4, (r,r')=(4,5)).**  For every no-full $S$ at
> $L_2 = (16, 4)$ with $|A| = 4$, every odd characteristic with $16 \mid q-1$,
> and every choice of σ-orbit reps $\{a_1, a_2\}$ and singletons $\{b_1, ..., b_4\}$
> consistent with no-full, the 4 values $\lambda_c = -\omega^{-b_c}$ are
> pairwise distinct.  Hence the (II) compatibility test fails, and no
> opposite-parity proportionality $\mathrm{HT}(t^4) \propto \mathrm{HT}(t^5)$
> exists.

This is a **field-uniform, no-exceptional-prime** result.  The proof uses
only:
* $\omega$ has order $16$ (i.e., $16 \mid q-1$).
* $\mathrm{char}(\mathbb{F}_q) \ne 2$ (so $-1 \ne 0$, distinguishing $\omega^k$ from $-\omega^k$).
* Distinctness of $b_i \bmod 16$ from no-full constraint on $B$.

No use of cyclotomic identities or the 8th-root sub-lemma (Note 0399 §2).

---

## 3.  Coverage and significance

The case $(r, r') = (4, 5)$ is one of $6 \times 6 = 36$ opp-parity exponent
pairs at $L_2 = (16, 4)$.  Coverage: $5760$ S × $1$ pair = $5760$ tests
at every prime, now field-uniformly closed.

Combined with σ-symmetric ($|A|=8$, all 36 pairs) and the existing 3-prime
empirical for the rest, the field-uniform structural closure now covers:

| Sub-stratum | Pairs covered field-uniformly |
|---|---|
| $|A| = 8$ | 36 (all) — Note 0396 §4 |
| $|A| = 6$, $r \in \{4, 6\}$ | 12 (out of 36) — Note 0399 §2 |
| $|A| = 4$, $(r, r') = (4, 5)$ | 1 (out of 36) — this Note |

**Field-uniform tests count:** $16 \cdot 36 + 1280 \cdot 12 + 5760 \cdot 1 = 22\,656$
out of $10\,896 \cdot 36 = 392\,256$ pair-tests — still only ~5.8% are
fully field-uniform, but the *structural mechanism* generalizes cleanly.

---

## 4.  Path forward for full field-uniformity

The pattern from §1: when $r/2 - 2 \le 0$ AND $m - 2 \le 0$, both $X$
and $\tilde Y_0$ are constants, and the closure is trivial (4 distinct
$\omega^{-b_c}$).  This applies precisely to $(r, r') = (4, 5)$.

For higher $(r, r')$:
* $X(\eta_c)$ becomes a polynomial expression in $(\eta_c, \zeta_1, \zeta_2)$.
* $\tilde Y_0(\eta_c)$ similarly.
* $\lambda_c = -X(\eta_c) / (\omega^{b_c} \tilde Y_0(\eta_c))$ depends on
  $(\eta_c, b_c, \zeta_1, \zeta_2)$ in a more complex way.

To prove $\lambda_{c_i} \ne \lambda_{c_j}$ for any 2 distinct $c$'s:
$$
X(\eta_{c_i}) \omega^{b_{c_j}} \tilde Y_0(\eta_{c_j}) \ne X(\eta_{c_j}) \omega^{b_{c_i}} \tilde Y_0(\eta_{c_i}).
$$
This is a polynomial identity in $(\zeta_1, \zeta_2, \eta_{c_i}, \eta_{c_j}, \omega^{b_{c_i}}, \omega^{b_{c_j}})$
that needs to be shown nonzero under no-full constraints.

Each $(r, r')$ pair gives one such identity.  The 36 pairs at $L_2 = (16, 4)$
correspond to 36 separate Path C sub-lemmas; closed-form verification is
mechanical but takes time.

---

## 5.  Combined Tier 1 status update

| Component | Status |
|---|---|
| Tier 1a @ L₂=(16,4) | ✓ structural closure + 3-prime empirical (Notes 0396–0402) |
| Tier 1b σ-sym @ any L₂ | ✓ field+scale-uniform (Note 0397) |
| Tier 1b general |B|≥1 @ L₂=(32,8) | ✓ 432K systems × 3 primes (Note 0403) |
| Tier 1b general |B|≥1 @ L₂=(64,16) | ✓ 57.6K systems × 2 primes (Note 0404) |
| **Path C field-uniform: (r,r')=(4,5) @ |A|=4** | **✓ this note** |
| Path C remaining 35 pairs @ |A|=4 | mechanical, ~1 day each |
| Path C analogous coverage @ |A|∈{0,2,6} | mechanical, similar effort |

Estimated effort to fully field-uniformize Tier 1a at L₂=(16,4):
~5-10 days of similar closed-form work.  Each pair is a finite polynomial
identity in cyclotomic algebra, no new mathematical idea.

---

## 6.  Next concrete artifact

Continue the Path C ladder.  Two natural next pairs:
* $(r, r') = (4, 7)$: $r/2 = 2$ (X constant), $m = 3$ ($\tilde Y_0$ degree 1) — first non-trivial $\tilde Y_0$.
* $(r, r') = (6, 5)$: $r/2 = 3$ (X linear), $m = 2$ ($\tilde Y_0$ constant) — first non-trivial $X$.

Each is a one-page closed-form computation.  Output target: Note 0406.
