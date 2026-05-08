# Note 0505 — Virtual Consult Helleseth + Gong on K_2 closure

**Date:** 2026-05-05 (Q2 GLOBAL drill iter 2, post Note 0504)
**Status:** Synthesized advice from two subagent personas. Concrete next-step computation identified.

## Setup

Q2 GLOBAL conjecture: $K(f_1, f_2; \delta) \leq 10$ for action-non-stab strict above-J pairs at deployment scale.

Note 0504 closed $K_1 \leq 3$ (zero-codeword saturating part) universally via budget identity.

Open: $K_2 \leq 7$ where
$$K_2 := \#\{\alpha : \mathrm{agr}(g_\alpha, 0) < T_{\mathrm{thresh}}, \exists c_\alpha \neq 0 \in \mathrm{RS}_{k_0} \text{ with } \mathrm{agr}(g_\alpha, c_\alpha) \geq T_{\mathrm{thresh}}\}.$$

## Helleseth's verdict (via subagent persona)

**Ranking:** Roos / van Lint-Wilson (vLW) > Krawtchouk-LP > Niho > novel.

**Key reasoning:**
- Niho cross-correlation is fundamentally a 2D Walsh transform on $\mathbb{F}_{2^n}$; pencil $g_\alpha = f_1 + \alpha f_2$ is NOT Niho — pattern-matching will burn 3 months.
- Krawtchouk-LP gives $K_2 \leq C(\rho, \delta) \cdot n$ — useless, need absolute constant.
- vLW handles non-consecutive defining sets exactly the regime here.

**Concrete attack:**
$D_\alpha := \{j \in [k_0, n_0-1] : \hat{g}_\alpha(j) = 0\}$. Each $j$ in $D_\alpha$ kills one $\alpha$ (since $\hat{g}_\alpha(j) = \hat{f}_1(j) + \alpha \hat{f}_2(j) = 0$ has unique $\alpha$ root when $\hat{f}_2(j) \neq 0$).

**Lemma to prove:** for $g_\alpha$ to be at distance $\leq \delta n_0$ from non-zero RS codeword, $D_\alpha$ must contain $\geq r$ "useful" indices for vLW to bite.

If $r \geq 4$ at $(n_0, k_0) = (32, 8)$: $K_2 \leq (n_0 - k_0)/r = 24/4 = 6 \leq 7$. ✓

**First computation:** for $(32, 8)$, enumerate α over $\mathbb{F}_q$ for 50 random above-J pairs. For each α giving witness $c_\alpha$, log $|D_\alpha|$ histogram. **Test: is $|D_\alpha| \geq 4$ always when witness exists?**

**Concerns from Helleseth:**
- (a) Action-non-stab → need to translate to a Roos hypothesis on $\hat{f}_1/\hat{f}_2$.
- (b) Constant 7 might be artifact of small $n_0$ — test at $(128, 32)$, $(256, 64)$.
- (c) vLW for cyclic codes with random complement defining set: open territory; Schmidt-Willems tables stop at $n \leq 125$.

**Probability:** ~35% in 1 month, ~65% in 3 months.

## Gong's verdict (via subagent persona)

**Ranking:** Welch-Gong / 2-monomial pencil elimination > cyclotomic + partial Gauss sum > Weil bounds (vacuous, $O(\sqrt q)$ not constant).

**Key reasoning:**
- $K_2$ bound must come from **algebraic elimination** (polynomial identity in $\alpha$), not analytic estimate.
- Weil gives $|\sum \chi(f(x))| \leq (d-1)\sqrt q$ — vacuous for $n_0 \ll \sqrt q$ (BCIKS / Crites-Stewart already navigated this trap).

**Concrete attack:**

**Lemma A.** For action-non-stab $(f_1, f_2)$, the K_2-witness $\alpha$ is a root of explicit polynomial $\Phi(f_1, f_2; X) \in \mathbb{F}_q[X]$ of degree $\leq D(k_0)$, $q$-independent.

Construction: $g_\alpha = X^{k_0} h_\alpha(X)$ with $\deg h_\alpha \leq 3k_0 - 1$. Agreement condition forces $h_\alpha - X^{-k_0} c_\alpha$ to have $\geq 2k_0 + 1$ roots in $L_0$, but $\deg \leq 2k_0 - 1$. This is a Hankel-style rank-degeneracy condition on coefficients of $f_1, f_2$, linear in $\alpha$. Determinant gives $\Phi$.

Heuristic degree: $\Phi$ has degree $\leq 2k_0 + 1$ — too large.

**Lemma B (cyclotomic chop).** Mod-4 fold: $g_\alpha = a(X^4) + Xb(X^4) + X^2c(X^4) + X^3d(X^4)$. Agreement set $A_\alpha$ of size $> n_0/2$ hits ≥ 2 fold-classes with density > 1/2. Restricting rank-degeneracy to single class gives Hankel of size $\sim k_0/2$, plus cyclotomic class-sum identity.

**This is the WG transformation mechanism** (Helleseth-Gong-Kumar 2002) — constant 7 should fall out as small explicit cyclotomic count over $\mathbb{Z}/4\mathbb{Z}$.

**First computation:** for $(32, 8)$, compute $\Phi(f_1, f_2; X) \in \mathbb{F}_q[X]$ explicitly for 50 random pairs. Count $\mathbb{F}_q^*$-roots corresponding to genuine $K_2$ events.

**Concerns from Gong:**
- Action-non-stab side-condition bookkeeping might take longer than main argument (cf. CMPR 1996).
- Don't be seduced by $K_2 = 0$ empirics — that's *generic* case; conjecture allows up to 7.
- After 2 weeks if Lemma A clean, Lemma B almost there: optimistic. If $\deg \Phi$ won't drop below 15: pull in Helleseth.

**Probability:** 35-45% in 1 month.

## Synthesis: convergent attack

**Both experts agree on:**
1. ✗ Avoid Niho (Helleseth's own field) and character-sum LP / Weil — wrong toolkit.
2. ✓ Need algebraic / cyclic-code mechanism, not analytic.
3. ✓ The mod-4 fold structure is the ENABLER (vLW or WG both use it).
4. ✓ Check empirical structure first via $|D_\alpha|$ or $\deg \Phi$ histogram.

**Convergent attack** (combines both):
- Helleseth's $D_\alpha$ = vanishing positions of $\hat{g}_\alpha$ in support window $[k_0, n_0)$.
- Gong's $\Phi$ = elimination polynomial whose roots are $K_2$-witness $\alpha$'s.
- These are **DUAL views of the same object**: $\Phi$ has roots exactly where $D_\alpha$ is large enough to force vLW witness.

**The unified question:** what's the minimum $|D_\alpha|$ for a $K_2$-witness to exist? And does that minimum, summed over distinct $\alpha$'s, exceed $n_0 - k_0 = 24$ (forcing $K_2 \leq 6$)?

## Next concrete computation

`g3_K2_D_alpha_histogram.py`:
1. For $(n_0, k_0) = (32, 8)$ over $q = 193$:
2. Sample 100 random $(f_1, f_2)$ above-J non-sparse.
3. For each, find the $\alpha$'s with $K_2$-witness via Berlekamp-Welch (since $\delta_J n < \tau_{BW}$ at this scale; otherwise use Sudan).
4. For each witness $(\alpha, c_\alpha)$: compute $|D_\alpha|$ = count of $j \in [k_0, n_0-1]$ with $\hat{f}_1(j) + \alpha \hat{f}_2(j) = 0$.
5. Output: histogram of $|D_\alpha|$ across all witnesses.

**Pass criterion:** min $|D_\alpha| \geq 4$ across all witnesses. Then $K_2 \leq 24/4 = 6$.

If pass: write Lemma B' (vLW restriction lemma) and proof attempt.
If fail: investigate witnesses with $|D_\alpha| < 4$ — these are the structural exceptions.

## Literature pointers (combined)

1. **van Lint & Wilson, "On the minimum distance of cyclic codes," IEEE-IT 1986** — the shifting bound (Helleseth's #1 recommendation).
2. **Roos, "A new lower bound for the minimum distance of a cyclic code," IEEE-IT 1983** — predecessor; sanity check.
3. **Schmidt & Willems, "On the minimum distance of cyclic codes," Des. Codes Cryptogr. 2010+** — modern computational tables.
4. **Hollmann & Xiang, "A proof of the Welch and Niho conjectures...," FFA 2001** — read for *technique* (1-parameter family analysis), not Niho exponents.
5. **Calderbank, McGuire, Poonen, Rubinstein, IEEE-IT 1996** — algebraic-geometric closure of finite count via elimination + curve genus (Gong's pick).
6. **Helleseth, Discrete Math. 1976** — original 5-valued cross-correlation (cyclotomic action partition technique).
7. **Gong-Helleseth-Kumar, IEEE-IT 2002** — Welch-Gong transformation, 2-monomial pencil bounds independent of $q$.

## Status

K_1 closed (Note 0504). K_2 attack vector identified (Note 0505). Empirical histogram next.

If $|D_\alpha| \geq 4$ holds: Q2 GLOBAL closes within $\leq 1$ month with ~50% probability (combined estimate).

If $|D_\alpha| \geq 4$ fails: investigate exceptions; likely "novel approach" needed; pull in Tang/Ding cluster.
