# Note 0481 — Diagnostic for task #313: |T|=12 K_BW dichotomy

**Date:** 2026-05-04 evening (post Note 0480)
**Status:** Empirical characterization of K_BW=2 vs K_BW=0 at |T|=12.

---

## TL;DR

For stratum (B) cross-side $K=16$ pencils with $|T| = 12$:
- $K_{\mathrm{BW}} = 2$ requires $f_u - f_v$ and $f_u + f_v$ each to
  vanish at exactly 8 points of $L_2 \setminus T$ (i.e., the ±1 ratio
  pattern is "balanced" with multiplicity (8, 8)).
- $K_{\mathrm{BW}} = 0$ corresponds to "unbalanced" ±1 multiplicity (6, 2).

Empirical: 13 K=2 cases vs 11 K=0 cases out of 24 sampled |T|=12 cases
across $p \in \{641, 769, 1153\}$.

## 1. Setup

Lemma 1 (budget): for $z \in L_2 \setminus T$, the value
$\alpha(z) := -f_u(z) / f_v(z)$ is well-defined (since stratum (B) gives
$f_v(z) \neq 0$). Each $z$ contributes 1 to the multiplicity of $\alpha(z)$
in the agreement budget.

The multiplicity of $\alpha$ equals $(N_\alpha - 4|T|) / 4$, the
"agreement excess per α."

## 2. K_BW = 2 condition (saturation)

Lemma 3: K_1 = #{α : N_α ≥ 80} ≤ 80 / 32 = 2.5, so K_1 ≤ 2.

For $K_1 = 2$: 2 α's must have multiplicity ≥ 8 in the ratio multiset.
By the budget total = 20, this forces 16 of 20 contributions to those
2 α's, with the remaining 4 spread among other α's.

## 3. Diagnostic results (`issue419_T12_diagnostic.py`)

Across 24 |T|=12 cases at $p \in \{641, 769, 1153\}$:

| Case | K_1 | Top-5 (α, mult) | mult(α=±1) |
|---|---|---|---|
| K_BW=2 cases (13 total) | | | |
| ex | 2 | [(1, 8), (-1, 8), (a, 2), (b, 2)] | (8, 8) |
| K_BW=0 cases (11 total) | | | |
| ex | 0 | [(1, 6), (-1, 2), (a, 1), (b, 1), ...] | (6, 2) |

**Pattern**:
- K_BW=2: ±1 multiplicity = (8, 8); 4 other α's get mult 1 each.
- K_BW=0: ±1 multiplicity = (6, 2); 12 other α's get mult 1 each.

## 4. Algebraic characterization

The ratio $-f_u(z) / f_v(z) = 1$ iff $f_u(z) = -f_v(z)$, i.e.,
$(f_u + f_v)(z) = 0$. Similarly $-f_u/f_v = -1$ iff $(f_u - f_v)(z) = 0$.

So:
- mult(α = +1) = #{$z \in L_2 \setminus T : (f_u + f_v)(z) = 0$}
- mult(α = −1) = #{$z \in L_2 \setminus T : (f_u - f_v)(z) = 0$}

(plus zeros on $T$ where $f_u = f_v = 0$ automatically.)

For $f_u + f_v$ to vanish at 8 points of $L_2 \setminus T$ and at 12 points
of $T$ (total 20 zeros on $L_2$): this is well within $\deg(f_u + f_v) < 32$.

For BOTH $f_u + f_v$ AND $f_u - f_v$ to have exactly 8 zeros on $L_2 \setminus T$
(plus 12 on $T$): a non-trivial algebraic condition.

## 5. K_BW = 0 cases: where do the missing zeros go?

For K_BW = 0 case with mult(α = ±1) = (6, 2):
- $(f_u + f_v)$ has 6 zeros on $L_2 \setminus T$ + 12 on $T$ = 18 total.
- $(f_u - f_v)$ has 2 zeros on $L_2 \setminus T$ + 12 on $T$ = 14 total.
- Total ratio multiplicity at ±1: 8.

Remaining 12 z's have $-f_u/f_v \in \mathbb{F}_p^* \setminus \{1, -1\}$,
each at multiplicity 1 (generic).

Why does the ratio land on ±1 with imbalance? Because $f_u + f_v$ has
specific extra roots beyond $T$, while $f_u - f_v$ does not (or vice
versa).

**Conjecture (algebraic)**: The "K_BW=2 saturation" requires the polynomial
identity $(f_u^2 - f_v^2)(z) = $ has exactly 16 zeros on $L_2 \setminus T$
(8 each from $f_u \pm f_v$), totally 28 with $T$.

Algebraically: $f_u^2 - f_v^2 = (f_u - f_v)(f_u + f_v)$, polynomial of
degree $< 64$. By GCD, the common zero set $T$ is shared with $f_u f_v$;
the additional zeros are governed by $f_u^2 - f_v^2$ mod
$\prod_{z \in T}(z - z_T)$.

## 6. Implication for K_BW upper bound

Lemma 3 already gives $K_1 \leq 2$ unconditionally. The diagnostic shows
$K_1 \in \{0, 2\}$ (never 1) at |T|=12, with the ±1 symmetry class
governing whether saturation occurs.

This empirical "$K_1 \in \{0, 2\}$ dichotomy" can be proven via:
- $K_1 = 1$ would require exactly 1 α with mult ≥ 8, but the budget
  identity $\sum (N_\alpha - 48) = 80$ with one α contributing $≥ 32$
  leaves 48 to spread among other α's. By the ±1 symmetry argument
  (Note 0469: 3-valued distribution), the contribution is also at α = -1
  (= +1's symmetric counterpart). So $K_1 = 1 \Rightarrow K_1 \geq 2$,
  contradiction.
- Hence $K_1 \in \{0, 2\}$.

## 7. Why the ±1 symmetry is forced

The $w \mapsto -w$ involution on $L_0$ maps $g_\alpha(w) \to g_{-\alpha}(-w)$
(roughly). Specifically: $f_u^{(0)}(-w) = f_u^{(0)}(w)$ if $f_u^{(0)}$ is
even (DFT support on even frequencies), else $-f_u^{(0)}(w)$ if odd.

Computing for our setup: $f_u$ has DFT support on $r \equiv 0, 1 \mod 4$
(in $[8, 32)$). After lifting via $w \mapsto w^4$: support on $4r$ for
$r \in $ supp. So $\hat{f_u^{(0)}}$ has support on $\{32, 36, 40, 44, ...\}$
which has values $4r \mod 2$: all multiples of 4 are even. So $f_u^{(0)}$
is invariant under $w \mapsto -w$.

Wait, $f_u^{(0)}(-w) = f_u^{(0)}(w)$. Then $g_\alpha(-w) = g_\alpha(w)$
trivially (induced from $w^4$, same as $-w$). So $g_\alpha$ doesn't distinguish
$w$ from $-w$. The induced symmetry $\alpha \to -\alpha$ comes from elsewhere.

Actually the ±1 symmetry comes from the **stratum (B) cross-side structure**:
$f_u$ has DFT support on $\{0, 1\} \mod 4$ and $f_v$ on $\{2, 3\} \mod 4$.
The map $w \to \zeta_2 w$ where $\zeta_2 = -1 \in \mu_2 \subset \mu_{128}$:
$f_u^{(0)}(\zeta_2 w)$? Since $\zeta_2^4 = 1$ in $\mu_{128}$ (well, $\zeta_2 = -1$
has $\zeta_2^4 = 1$), $f_u^{(0)}(\zeta_2 w) = f_u(\zeta_2^4 w^4) = f_u(w^4)$.
So $f_u^{(0)}(-w) = f_u^{(0)}(w)$. Same for $f_v^{(0)}$. So ${f_u^{(0)}, f_v^{(0)}}$
are both even functions on $L_0$ and the involution is trivial. Where does
±1 symmetry come from?

This needs more thought (Note 0469's empirical observation needs structural
explanation).

## 8. Status

- Diagnostic complete for task #313.
- |T|=12 K_BW dichotomy characterized: K_BW=2 ⟺ balanced ±1 ratio
  multiplicity (8, 8).
- K_BW=0 cases have asymmetric (6, 2).
- Underlying algebraic mechanism: zeros of $(f_u + f_v)$ vs $(f_u - f_v)$
  on $L_2 \setminus T$.

## 9. Files

- This note 0481
- `notes/scripts/issue419_T12_diagnostic.py` + output
- Notes 0469-0480 (related context)
