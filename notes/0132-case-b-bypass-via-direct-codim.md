# Note 0132 — Case-B BYPASS via direct codim count (Session 2 breakthrough)

**Date**: 2026-04-30
**Branch**: main
**Builds on**: Notes 0117 (V_S²-inclusion), 0119 (case-A f-image bound), 0131 (MDS-syzygy + Session 1 diagnosis).
**Status**: **PROOF SKETCH** of unconditional codim V_bad ≥ 2(c-1). No reliance on Note 0122's flawed reduction. Empirical validation pending sessions 3-5.

## Headline

**The case-B reduction (Note 0122) is UNNECESSARY.** A direct codim count, summing case-A and case-B contributions per-realizer, gives codim V_bad ≥ 2(c-1) unconditionally. The proof works because case-B realizers contribute MORE codim per realizer (c) than case-A (d ≤ c at deployment), so any mix yields at least the all-case-A bound.

## The lemma

**Lemma 3 (Direct codim bound).** Let $(s_1, s_2) \in V_{\text{bad}}$ with joint Vandermonde support $S^*$, $|S^*| = w + 1 + d$ ($d \geq 0$). For each of the $T+1$ realizers $(\gamma_l, E_l)$, classify as case A ($E_l \subseteq S^*$ or more precisely $|E_l \cup S^*| \leq D$) or case B otherwise. Let $M_A, M_B$ be the counts ($M_A + M_B = T+1$). Then within $V_{S^*}^2$,
$$
\codim_{V_{S^*}^2}\bigl(V_{\text{bad}} \cap V_{S^*}^2\bigr) \;\geq\; M_A \cdot d + M_B \cdot c.
$$

For $d \leq c$ (deployment regime): $M_A \cdot d + M_B \cdot c \geq (M_A + M_B) \cdot d = (T+1) d$.

Combined with $\codim_{F^{2D}}(V_{S^*}^2) = 2(c-1-d)$:
$$
\codim_{F^{2D}}\bigl(V_{\text{bad}} \cap V_{S^*}^2\bigr) \;\geq\; 2(c-1-d) + (T+1)d \;=\; 2(c-1) + (T-1)d.
$$

For $T \geq 1, d \geq 0$: $\geq 2(c-1)$, with strict inequality for $d \geq 1, T \geq 2$ (sub-leading is strictly higher codim than leading).

## Proof

### Case-A contribution

For case-A realizer $(\gamma_l, E_l)$ with $E_l \subseteq S^*$ (well, $|E_l \cup S^*| \leq D$ which forces same V-intersection): the constraint $x_{\gamma_l} \in V_{E_l}$ implies $\alpha_v + \gamma_l \beta_v = 0$ for $v \in S^* \setminus E_l$, $|S^* \setminus E_l| \geq |S^*| - w = d + 1$.

Equivalently: $f(v) := -\alpha_v / \beta_v$ takes the value $\gamma_l$ at $\geq d + 1$ points $v$. So $f^{-1}(\gamma_l) \supseteq T_l$ with $|T_l| \geq d + 1$.

The condition "$f(v_i) = f(v_j)$ for all $v_i, v_j \in T_l$" is $|T_l| - 1 \geq d$ ratio equations $\alpha_{v_i}\beta_{v_j} = \alpha_{v_j}\beta_{v_i}$. Codim $\geq d$ on the $(α_v, β_v)$ for $v \in T_l$.

For T+1 case-A realizers with distinct $\gamma_l$: preimages $T_l$ are disjoint (since $\gamma_l$ distinct), involving disjoint variable sets. Total codim $\geq M_A \cdot d$ (sum over independent variables).

### Case-B contribution

For case-B realizer $(\gamma_l, E_l)$ with $E_l \not\subseteq S^*$ (more precisely $|E_l \cup S^*| > D$): the intersection $V_{E_l} \cap V_{S^*}$ has dim $|E_l| + |S^*| - D = w + |S^*| - D$ (Vandermonde rank-D ambient). Codim of $V_{E_l} \cap V_{S^*}$ in $V_{S^*}$ is $|S^*| - (w + |S^*| - D) = D - w = c$.

The constraint $x_{\gamma_l} = \alpha + \gamma_l \beta \in V_{E_l} \cap V_{S^*}$ is therefore $c$ linear equations on $(\alpha, \beta) \in V_{S^*}^2$. Codim $c$ per realizer.

For $M_B$ case-B realizers with generic distinct $(\gamma_l, E_l)$: total codim $\geq M_B \cdot c$ (independence of distinct $W_l = V_{E_l} \cap V_{S^*}$ generically).

### Independence of case-A vs case-B contributions

Case-A constraint involves ratios $\alpha_{v_i} / \beta_{v_i}$ on the disjoint preimage subsets $T_l \subseteq V_1 \subseteq S^*$.
Case-B constraint involves linear projections of $(\alpha + \gamma\beta)$ onto $V_{S^*} / (V_E \cap V_{S^*})$, involving the full $(α, β) \in V_{S^*}^2$.

These are different polynomial conditions; generically the joint variety has codim equal to the sum.

### Combining

Total codim of $V_{\text{bad}} \cap V_{S^*}^2$ in $V_{S^*}^2$: $\geq M_A \cdot d + M_B \cdot c$.

Bound by $(T+1) \cdot d$ for $d \leq c$ (using $c \geq d$ to absorb the case-B excess):
$$
M_A d + M_B c \geq M_A d + M_B d = (M_A + M_B) d = (T+1) d.
$$

(Equality when all realizers are case-A and $d = c$; strict when any case-B and/or $d < c$.)

### Final codim

$$
\codim_{F^{2D}} V_{\text{bad}} \cap V_{S^*}^2 \geq 2(c-1-d) + (T+1)d = 2(c-1) + (T-1)d.
$$

For $d = 0$ (leading): $= 2(c-1)$, achieved by $V_S^2$ inclusion (Note 0117).
For $d \geq 1$ (sub-leading): $> 2(c-1)$ (strict).

Stratifying $V_{\text{bad}} = \bigsqcup_d V_{\text{bad}}^{(d)}$ over joint VS sizes:
$$
\codim V_{\text{bad}} = \min_d \codim V_{\text{bad}}^{(d)} = 2(c-1).
$$

Achieved at $d = 0$. $\blacksquare$

## Why this works (where Note 0122 failed)

**Note 0122's strategy**: replace each case-B realizer with a case-A one inside $S^*$, then apply Note 0119's case-A bound. **Failure**: the replacement requires $|T_\gamma| \leq w$, which can fail in case B (alt-support).

**Note 0132's strategy**: don't try to convert case-B to case-A. Just sum codim contributions per-realizer directly. The case-A and case-B codim contributions are different ($d$ vs $c$), but BOTH are at least $\min(d, c) = d$ for $d \leq c$. So the sum is at least $(T+1)d$, regardless of how realizers split.

**Key insight**: case-B realizers have MORE per-realizer codim ($c \geq d$), not less. So they don't weaken the bound.

## Comparison with prior approaches

| Note | Strategy | Status |
|------|----------|--------|
| 0117 | $V_S \times V_S$ inclusion | ✅ Upper bound rigorous |
| 0119 case A | f-image collapse | ✅ Rigorous when all case-A |
| 0119 case B | Conjecture B (later 0122) | ⚠️ Note 0122 reduction has gap |
| 0122 | reduction to case-A | ❌ Gap (assumes \|T_γ\|≤w) |
| 0123 | sub-leading codim via 0122 | ⚠️ Inherits 0122 gap |
| **0132 (this)** | direct per-realizer codim sum | **✅ Bypasses 0122 entirely** |

## Empirical predictions to verify (sessions 3-5)

For sub-leading $|S^*| = w + 1 + d$ (d ≥ 1), the codim of $V_{\text{bad}} \cap V_{S^*}^2$ within $V_{S^*}^2$ should be $\geq (T+1) d$.

For c=3, d=1: codim $\geq T+1$. At empirical (n=10, c=3, p=41): T+1 = 5, $\dim V_{S^*}^2$ = 12, codim should be $\geq 5$, dim $\leq 7$. 

To verify: sample $(s_1, s_2) \in V_{S^*}^2$ with $|S^*| = w+2$ (sub-leading), measure how often M > T. Expected: $\sim p^{-5}$ frequency under uniform sample of $V_{S^*}^2$.

## Caveats / what to check

1. **Independence of constraints**: assumed generically. For non-generic V_bad witnesses (multiple realizers with same $W_l$), codim could be less. **Need to verify these special components don't drop codim below 2(c-1)**.

2. **Definition of "case B"**: I used $|E \cup S^*| > D$. The analysis assumes $\dim(V_E \cap V_{S^*}) = w + |S^*| - D$ in case B, which holds when the ambient $\dim V_{S^*} + \dim V_E - \dim$ both non-degenerate. Pathological alignments could exceed this dim.

3. **$d \leq c$ regime**: my bound used this. For $d > c$ (very wide sub-leading), need separate argument (case-B contributes c per realizer, less than d). But $d \leq c$ corresponds to $|S^*| \leq w + 1 + c = D + 1$, which is automatic since $|S^*| \leq D$. So $d \leq c - 1$ always. ✓

4. **Note 0119's empirical 340/340 |S^*| ≤ w + ⌊w/T⌋ bound** is independent of this proof and remains valuable as orthogonal evidence.

## Implication for paper3

If Note 0132 holds (sessions 3-5 verify):
- Theorem 3.1 (codim V_bad = 2(c-1)) becomes **fully unconditional for all c ≥ 2**.
- Path (b) [absorb to sub-leading] is REALIZED via the direct codim count.
- Lemma `lem:reduction` (paper3 §5.3) can be REMOVED entirely, replaced by Lemma 3 (direct codim count).
- Conjecture B / Note 0122 can be cited as a parallel-development backup that's now unnecessary.

This is the **best-case outcome of the 5-session attack**: case-B closed without needing to prove the original Note 0122 claim.

## Files this session

- `notes/scripts/case_b_per_witness_count.py` — per-witness $M_B$ counter (89 witnesses, 0 violations of Lemma 2 + Note 0119 bound)
- `notes/0132-case-b-bypass-via-direct-codim.md` — this note (Session 2 breakthrough)

## Status going into Session 3

**Need to verify** (sessions 3-5):
1. Empirical: sub-leading V_bad density matches $\sim p^{-(T+1)d}$ within $V_{S^*}^2$ (codim prediction).
2. Independence: special V_bad components don't drop codim below 2(c-1).
3. Edge cases: $d > c$, all-case-B configurations, $|S^*| = D$.

**If verified**: rewrite paper3 §5.3 with Lemma 3 (direct codim), drop case-B reduction, claim Theorem 3.1 unconditional. Push for ePrint readiness with case-B fully closed. (Lemma A still pending c322 separately.)
