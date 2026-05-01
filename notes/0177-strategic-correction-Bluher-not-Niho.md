# Note 0177 — Strategic correction: Bluher 2004 Galois technique, not Niho/Welch-Gong cardinality

**Date:** 2026-04-28 (loop iter 10)
**Status:** Course correction from user. Pivoting from "Gong/Helleseth Niho framework" to "Bluher 2004 Galois trinomial technique" for the orbit count K bound.

## What was wrong with the previous direction

Notes 0175 / 0176 framed the Pattern A mechanism as "Niho/Welch-Gong cross-correlation" because the saturating-column condition reduces to:
```
   #{z ∈ L_2 : c·z^{p*} = a + bz}  ≥  n_2 − w_J(L_2)
```
which is a value-distribution / cardinality question on a multiplicative subgroup.

The user clarified:
- **Niho/Welch-Gong literature** (Hollmann-Xiang, Helleseth-Lahtonen, Helleseth-Kholosha) bounds value distribution and cardinality. **This is in the same category as Crites-Stewart's |B_t| bound.** Necessary but NOT sufficient for the orbit count K problem.
- **No published machinery** transfers Gauss-sum bound → orbit count K. The "diagonal cyclotomic action" lemma in Codex / G3 is the multi-character generalization but the technique to bound K is missing.
- The **right precedent is Bluher 2004**, not the Niho line.

## Bluher 2004 — the seed result ★★★

**Bluher, A. W. (2004)**: *On x^{q+1} + ax + b*. Finite Fields and Their Applications.

**Theorem (Bluher 2004)**: For the trinomial `T(x) = x^{q+1} + ax + b ∈ F_{q²}[x]`, the number of F_{q²}-rational roots `N(a, b) ∈ {0, 1, 2, q+1}` and the parameter set with each value count is bounded explicitly.

**Why this matters for us**:
- `x^{q+1} = N_{F_{q²}/F_q}(x)`, so the trinomial has hidden norm structure → Galois F_{q²}/F_q action constrains roots into orbits.
- The (q+1)-roots case = "saturated case" = exactly our **V_δ saturating column** (when ALL of some coset is bad).
- The (a, b) parameter space bound = exactly our **V_δ size bound**.

**The technique** (Galois trinomial argument):
- Roots of T(x) come in Galois orbits under Frob_q.
- Hidden norm structure x^{q+1} = N(x) makes the orbit structure highly constrained.
- "Most" (a, b) give 0 or 1 root; few give 2; an explicit set gives q+1.

## Translation to our V_δ problem

Our setup (32, 8) at FRI 2-round:
- L_2 = ⟨ω^4⟩ ⊂ F_q* with q ≡ 1 mod 32. Order n_2 = 8.
- fold²(α_1, α_2) on L_2 is bilinear in (α_1, α_2):
```
   fold²(α_1, α_2)  =  (f_e)_e  +  α_1·(f_o)_e  +  α_2·(f_e)_o  +  α_1·α_2·(f_o)_o
```
- V_δ = {(α_1, α_2) : ∃ (a, b) with fold²(α_1, α_2)(z) = a + bz on ≥ 4 z ∈ L_2}.

This is a **4-parameter** problem (α_1, α_2, a, b) ∈ F_q⁴, with a `≥ 4 zeros in L_2` condition on the trinomial-like polynomial:
```
   P(z; α_1, α_2, a, b)  :=  fold²(α_1, α_2)(z)  −  a  −  b·z
```

**Bluher analog**: bound the orbit count K under the diagonal cyclotomic action on this parameter space.

## The 5 key references (per user)

1. **Bluher 2004** — `x^{q+1}+ax+b`, the seed result ★★★ — Finite Fields Appl.
2. **Helleseth-Kholosha 2008/2010** — generalization to `(q^k+1)/(q+1)`-trinomials.
3. **Hollmann-Xiang 2001** — Welch/Niho conjecture proof, partial Gauss sum technique.
4. **Helleseth-Lahtonen 2006** — Niho via Kloosterman/Dickson.
5. **arXiv:2407.16072 (2024)** — cross-correlation review confirming field still focused on value distribution.

The KEY ones for us: Bluher 2004 + Helleseth-Kholosha (path: trinomial → multinomial-on-subgroup is known). The OTHER three are about value-distribution (already covered by my Niho work, and by Crites-Stewart's argument).

## Strategy: don't engage Gong/Helleseth, read Bluher

User: "之前我说 '找 Gong / Helleseth' — 但他们是老人家做不快, 而且这条线缺的工具不是 Niho 的, 是 Bluher 的 Galois 技巧。"

Concrete plan:
1. **Read Bluher 2004 abstract / extract Galois argument** (next iteration).
2. **Read Helleseth-Kholosha extension** to see the multinomial generalization.
3. **Translate to our V_δ trinomial-on-μ_d setup**: identify the diagonal cyclotomic action, bound the orbit count K under it.
4. **Combine with my Niho dichotomy** (note 0176): the Niho gives the FIBER bound (per α_2*-line), while Bluher's K bound gives the BASE bound (over the parameter space (α_1, α_2)).

## What I keep from notes 0175/0176

- **Theorem 0175.B** (Pattern B all-odd, rigorous): scalar invariance argument is independent of the Bluher question. KEEP.
- **Niho dichotomy** (note 0176): the q-universal `c·z^{p*} bad ⟺ p* mod (n_2/2) ∈ {0..k_2-1}` IS a value-distribution result and is correct on its own. It's the FIBER condition: given α_2* makes fold² single-monomial, when is that monomial bad on L_2. KEEP.
- **What I overclaimed**: "Niho cross-correlation closes Pattern A". WRONG — Niho only closes the fiber question; the orbit/base question requires Bluher.

## Open: the correct framing for #343 prize claim

The Conjecture 174 ceiling `|V_δ| ≤ (n_1 − s + 2)·q` requires:
1. **Pattern A1/A2 saturating column** → 1·q from one column (the (a, b) "saturated" case in Bluher language) — **this is the Bluher (q+1)-root case**.
2. **Generic α_2 contribution** → ≤ (q-1)·M for M = M_max(L_2-line) — **this is the per-line BCIKS subdomain CA** (already known, not Niho).

So the full theorem decomposes as:
```
   |V_δ|  =  (saturating col, count ≤ small) · q  +  (generic col, count = q − small) · M
```
where M ≤ n_1 - s + 1 is the per-line BCIKS bound (NOT a Niho consequence).

The Niho dichotomy is helpful for predicting WHICH supports trigger saturating-col (those with `j ∈ [16, 23]` in supp at (32,8)). But the COUNT of saturating cols per (α_1, α_2)-family is the Bluher question.

## Next steps

1. **WebSearch for Bluher 2004** to find paper / abstract / key technique.
2. **Read Helleseth-Kholosha 2008** for the multinomial generalization on subgroup μ_d.
3. **Re-examine V_δ counting**: identify the "diagonal cyclotomic action" group on (α_1, α_2, a, b), compute orbit count K.
4. **Connect to existing Codex Note 0158** (count=q witness at q=1153) — that was the empirical evidence for the K bound.
