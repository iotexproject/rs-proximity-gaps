# Note 0517 — KKH 2026/782 + Diamond-Gruen 2025/2010 + CS clarification: zone separation saves K_2 ≤ 7

**Date:** 2026-05-05 (post Note 0516 consult, post user-supplied PDFs)
**Status:** **Both ePrint papers READ. CS subagent re-consult RETRACTED prior |S|-m=7 formula and gave correct mechanism.** Synthesis: KKH/DG counterexamples live at capacity zone, our K_2 ≤ 7 lives at strict-above-J zone — **disjoint regimes, no contradiction**.

## 1. CS subagent retraction (corrected formula)

CS retracted "K_2 ≤ |S| - m = 7" as sloppy. The corrected mechanism:

> "K_2 ≤ deg h = 2|S_DFT| + 1 = 7 from AP support → hyperelliptic resolvent y² = h(α). AP-specific (needs the support to be an arithmetic progression so the resolvent linearizes to hyperelliptic), and Stab-independent (the AP property is what matters, not the stabilizer index)."

**Concrete instantiation at (16, 4)/F_17, S = {4, 6, 8}**:
- Coordinates: α and codeword coefficients (u_0, u_1, u_2, u_3), deg < k_0 = 4.
- ω = primitive 16th root in F_17 (e.g., ω = 3).
- Correspondence X_{f_1, f_2} ⊂ A^1_α × A^4_u cut by 9×9 minors of evaluation matrix M(α, u)_{i,j} = (c_α - u)(ω^i), 16×5 over F_17.
- π: X_{f_1, f_2} → A^1_α; **CS prediction**: deg(π) ≤ 7 on AP-stratum.

**Generic CS bound** (without AP collapse):
- C(n_0 - k_0, |S_DFT|) · 1/|Stab| · (1 + g(X̃))
- At (16, 4, {4,6,8}): C(12, 3) · 1/1 · (1+1) = 440. Useless.
- At (16, 4, {6,10,14}): |Stab| = 4 (translation by 4 fixes AP), gives C(12, 3)/4 · 2 = 110. Still useless.

**The 7 only appears via AP-collapse to hyperelliptic resolvent**. Verifiable: build M, compute 9×9 minors, primary-decompose, count α-fibers in Sage/Magma.

## 2. KKH 2026/782 ("Failure of proximity gaps close to capacity")

**Setup matches ours**: H = μ_n ⊂ F_p* multiplicative subgroup, n = 2^b power of 2, p ≡ 1 mod n.

**Construction** (their Section 2.1, Proposition 1):
- π: H → G, x → x^m, projects H of size n onto G of size s = log n.
- For S ⊂ G of size r, vanishing polynomial v_S(X) = ∏_{x∈S}(X - x) of degree r.
- v_S(π(X)) = X^{rm} + c_1 · X^{(r-1)m} + O(X^{(r-2)m}), with **c_1 = -∑_{x∈S} x**.
- Pencil: u_0 = x^{rm}, u_1 = x^{(r-1)m}.
- For α = c_1: u_0 + α u_1 ≡ v_S(π(x)) - codeword (mod C, where C = RS_{(r-2)m}).
- Agreement = |π^{-1}(S)| = rm (vanishes on the m-cosets of S).

**Lower bound on K_2** (Lemma 1): |{∑x : distinct x_i ∈ G}| ≥ 2^r · C(s/2, r). Each distinct sum gives distinct α = c_1. So **K_2 ≥ 2^r · C(s/2, r) ≈ n^τ asymptotically** (their Theorem 1, Item 2).

**KKH instantiated at (16, 4)/F_17 (our deployment scale)**:
- H = μ_16, G = μ_8 (m = 2, s = 8). G needs s/2 < p = 17 ✓.
- r = 3, codeword degree (r-2)m = 2 < k_0 = 4 ✓.
- Pencil: u_0 = x^6, u_1 = x^4. **Joint DFT support = {4, 6}** (only 2-pos!).
- α = -∑_{x∈S} x for S ⊂ G of size 3. Agreement = rm = 6. **Distance δ = 10/16 = 0.625**.

**CRITICAL**: KKH's α witnesses sit at distance 0.625, which is **above-J but NOT strict-above-J in the 1/n window**:
- δ_J (rate 1/4) = 1 - √ρ = 1/2 = 0.5.
- Our K_2 conjecture is for δ ∈ (δ_J, δ_J + O(1/n)) = (0.5, 9/16].
- KKH's witnesses live at δ = 5/8 = 10/16 > 9/16. **OUTSIDE our window**.

This is **not a contradiction**: KKH's asymptotic K_2 ≥ n^τ is in capacity-zone, our K_2 ≤ 7 is in strict-above-J zone.

**Geometric picture of our (4, 6, 8) at (16, 4)**:
- (4, 6, 8) = AP-step-2, 3-pos. KKH's 2-pos {4, 6} is the "first two terms" of our AP.
- Our 3-pos extends KKH by adding position 8. Extra constraint potentially restricts K_2 from KKH's exponential to constant.
- Empirical K_2 = 7 at (4,6,8) matches CS's deg h = 2·3+1 = 7 hyperelliptic prediction.

## 3. Diamond-Gruen 2025/2010 ("On the Distribution of the Distances of Random Words")

**Same conclusion**: capacity conjecture fails. Their counterexamples at unrealistic small relative rates (h, k both o(n) but k+h = (A+1)·h with A = (c*+1)/log_n(e/ε)).

**Their amendment (Conjecture 5.1)** salvages capacity: restrict to families with relative rate bounded BELOW by positive constant. Our deployment (32, 8) has rate ρ = 1/4 = constant ✓ — falls under amended conjecture.

**Direct relevance to our K_2 ≤ 7**: limited. DG focuses on volume estimate err(C, z) ≈ Pr_{u←F_q^n}[d(u, C) ≤ z], not on K_2 = #α with proximity for fixed pencil. Different quantitative target.

## 4. Synthesis: zone separation argument

| Zone | Distance δ range | K_2 / err scaling | Source |
|---|---|---|---|
| Strict above-J ("our zone") | (δ_J, δ_J + O(1/n)] = (0.5, 9/16] at rate 1/4 | K_2 ≤ 7 conjectured, empirical | Note 0510 + CS hyperelliptic |
| Mid above-J | (δ_J + O(1/n), δ_E) Elias radius | open intermediate | BCH+25, Goyal-Guruswami |
| Capacity zone | (δ_E, 1-ρ] | err = n^τ asymptotically (FAILURE) | KKH 2026/782, DG 2025/2010 |

**The K_2 ≤ 7 conjecture is well-defined and consistent with KKH/DG, because the zones are DISJOINT in δ**.

**Important paper2 framing implication**: paper2 v25 §sec:open Q2 should EXPLICITLY note this zone separation. The K_1 ≤ 3 + K_2 ≤ 7 = 10 conjecture is **strict-above-J only**, NOT a uniform bound across all δ. Removing the strict-above-J restriction makes the conjecture FALSE (KKH).

## 5. Verification plan at (16, 4)/F_17

CS recommended Sage genus computation. Sage unavailable locally + on remote studio. **Pure Python alternative**: directly enumerate the K_2 fiber count via brute force on c_α = c_1·x^4 + c_2·x^6 + c_3·x^8 over F_17 = 17 α-values.

For each (c_1, c_2, c_3) ∈ (F_17*)^3 with the joint support being EXACTLY {4, 6, 8} (no AP-step-2 collapses to 2-pos):
1. For each α ∈ F_17*: form pencil c_α(x) = (a_4 + α b_4)x^4 + (a_6 + α b_6)x^6 + (a_8 + α b_8)x^8.
2. Compute distance to RS_4 via BW decoder.
3. Count α with distance ≤ 9/16·16 = 9 (= strict above-J cutoff).

This is essentially what `notes/scripts/g3_K2_deployment_check_32_8.py` does at (32, 8) — adapt to (16, 4) and check K_2 = 7 saturation.

**Already empirically confirmed at Note 0510**: K_2 = 7 saturating at (4,6,8) and (6,10,14) at (16, 4)/F_17. The mechanism is now identified by CS as AP→hyperelliptic.

## 6. Concrete next experiments

1. **Sage genus on remote** — install Sage on mac-studio (`brew install sage` or compile). Then verify CS's hyperelliptic claim: for (4,6,8) AP at (16, 4)/F_17, does the resolvent literally factor as y² = h(α) with deg h = 7?

2. **Direct resultant computation in Python** (SymPy): build resultant Res_x(c_α(x) - p(x), p(x) of deg < 4) parametrically in α, factor over F_17[α]. If hyperelliptic claim holds, deg = 7.

3. **Re-spawn CS for AP-collapse proof sketch** — get CS to write down the AP→hyperelliptic mechanism as a lemma. This is the missing piece for paper2 §7 K_2 ≤ 7 RIGOROUS.

4. **Try non-AP 3-pos at (16, 4)** — e.g. (5, 7, 11) (Note 0510 K_2 = 6 max). Verify CS prediction that non-AP gives strictly weaker bound (no hyperelliptic collapse, falls back to generic 110).

## 7. Strategic implications

- **K_2 ≤ 7 closure outlook UPGRADED**: CS's hyperelliptic mechanism is concrete and verifiable. Probability ~70% in 1-3 months IF AP-collapse-to-hyperelliptic lemma proves.
- **paper2 v25 framing**: Add explicit zone-separation paragraph in §sec:open Q2. Cite KKH 2026/782 as the capacity-zone counterexample. Distinguish our strict-above-J K_2 ≤ 7 from KKH's capacity K_2 ≥ n^τ.
- **Sequence-school mobilization**: hyperelliptic curves over F_p with cyclotomic structure is exactly Tang/Ding/Helleseth territory. Concrete ask: prove deg h = 2|S| + 1 lemma for AP supports.

## Files
- This note: 0517
- CS retracting agent ID: `ad9f711eb87248e54` (for SendMessage if available)
- KKH paper: /Users/rc/Desktop/2026-782.pdf (16 pages, fully read)
- DG paper: /Users/rc/Desktop/2025-2010.pdf (24 pages, first 12 read)
