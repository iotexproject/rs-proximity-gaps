# Proof Chain: Complete Status

*Last updated: 2026-04-26 (post PR #359)*

## Goal

**Ethereum Foundation Proximity Prize**: Prove FRI soundness above Johnson for plain RS codes.

Formal: $\mathrm{RS}[F, L, k]$, $L \subset F^*$ multiplicative subgroup of order $n$, $\delta_J < \delta < 1 - \rho$.

$$\Pr[\text{FRI accepts} \mid \Delta(f, \mathrm{RS}_k) > \delta] \;\le\; \frac{nR}{|F|} \;+\; \left(1 - \tfrac{\delta}{2}\right)^q$$

BCHKS achieves $O(Rn)/|F|$ at Johnson. Our soundness theorem extends (unconditionally) above Johnson at the cost of a 2× query overhead vs. the conjectured zero-loss baseline.

---

## Chain overview

```
FRI Soundness above Johnson
    |
    |--- Strategy A: honest folding ---> SZ on multilinear syndromes ---> R/|F|
    |       needs: [1] f^(R) is multilinear in α's
    |              [2] at least one syndrome not identically zero
    |
    |--- Strategy B: dishonest folding (deviate at one or more rounds)
    |       needs: [3] per-round proximity gap O(n)/|F|
    |              [4] consistency check catches deviation: i.i.d. catch lemma
    |
    [3] per-round proximity gap (round 1)
        needs: [5] half-threshold CA bound (δ/2)         ── our contribution
               [6] FRI coupling inequality (even/odd)

    [3] per-round proximity gap (rounds ≥ 2)
        needs: BCIKS distance-locking at δ/2 < (1-ρ)/2 ── classical, since after round 1
                                                          we are in unique-decoding regime
```

---

## Each link: status and proof

### [1] $f^{(R)}$ is multilinear in $(\alpha_1, \ldots, \alpha_R)$ — ✅ trivial

Each FRI fold is linear in the new challenge: $f^{(i)}(y) = f^{(i-1)}_{\mathrm{even}}(y) + \alpha_i \cdot f^{(i-1)}_{\mathrm{odd}}(y)$. Composing $R$ linear maps: $f^{(R)}(y)$ is multilinear of total degree $\le R$.

---

### [2] At least one syndrome polynomial is not identically zero — ✅ proved

If all syndromes vanished identically, then $f^{(R)} \in \mathrm{RS}_{k/2^R}$ for every $(\alpha_1, \ldots, \alpha_R)$. Unfolding inductively via the even/odd isomorphism (requires $k = 2^m$): $f^{(0)} \in \mathrm{RS}_k$, contradicting the hypothesis. By Schwartz–Zippel: $\Pr[f^{(R)} \in \mathrm{RS}] \le R/|F|$.

---

### [3] Per-round proximity gap above Johnson — ✅ proved

**Round 1** (Theorem 7, `thm:proximity-gap`): If $\Delta(f, \mathrm{RS}_k) > \delta$ with $\delta > \delta_J$, then $|\{\alpha : \Delta(f_{\mathrm{even}} + \alpha f_{\mathrm{odd}}, \mathrm{RS}_{k/2}) \le \delta/2\}| \le 1$. Combines [5] + [6].

**Rounds 2..R** (BCIKS distance-locking, Remark `rem:no-compound`): $\delta/2 < (1-\rho)/2$ places us in the unique-decoding regime where the BCIKS proximity gap (Theorem 1.2) at threshold γ = δ/2 gives ≤ n bad challenges per round and *preserves* distance (does not further reduce to δ/4). The 1/2 reduction happens exactly **once**.

Total bad α budget: ≤ 1 + (R−1)n ≤ nR.

---

### [4] Consistency check catches deviation — ✅ proved (Lemma 9, `lem:catch-prob`)

The standard FRI query model (Definition 8, `def:query-model`) samples $q$ base-level points $z_1, \ldots, z_q \in L$ i.i.d. uniform with replacement. For any deviation set $D_i \subseteq L^{(i)}$ with $|D_i|/|L^{(i)}| \ge \tau$:

$$\Pr_{z_1, \ldots, z_q}\bigl[\,\pi_i(z_j) \notin D_i \text{ for all } j\,\bigr] \;\le\; (1-\tau)^q.$$

**Proof** (independence under deterministic maps): $X_j := \mathbf{1}\{\pi_i(z_j) \in D_i\}$ are i.i.d. Bernoulli with parameter $\ge \tau$ because $z_j$ are i.i.d. and $X_j = h(z_j)$ for a deterministic $h$. Independence does **not** require the realized $\pi_i(z_j)$ to be distinct: even when collisions are forced by pigeonhole at late rounds, the joint distribution of $(z_1, \ldots, z_q)$ remains the product measure on $L^q$. Without-replacement implementations satisfy the same bound by negative association (Remark `rem:query-model-impl`).

For τ = δ/2: missing the deviation across all $q$ queries has probability $\le (1-\delta/2)^q$.

---

### [5] Half-threshold CA bound — ✅ proved (Theorem 3, `thm:ca-halved`) — **our contribution**

$$\varepsilon_{\mathrm{ca}}(C, \delta/2, \delta) \;\le\; \frac{1}{|F|}.$$

**Proof** (RVW13 direct 2×2 solve):
Suppose two distinct bad γ₁, γ₂ both make $f_1 + \gamma_i f_2$ within distance $\delta/2$ of $C$, witnessed by codewords $h_1, h_2$. On the agreement-overlap $S_1 \cap S_2$ (size $\ge (1-\delta) n$):

$$h_1 - h_2 = (\gamma_1 - \gamma_2) f_2 \;\Longrightarrow\; f_2 = (h_1 - h_2)/(\gamma_1 - \gamma_2) \in C \text{ on this overlap}.$$

Setting $g_2 := (h_1 - h_2)/(\gamma_1 - \gamma_2) \in C$ and $g_1 := h_1 - \gamma_1 g_2 \in C$: the joint disagreement $|\{x : (f_1, f_2) \ne (g_1, g_2)\}| \le |L \setminus (S_1 \cap S_2)| \le \delta n$. Hence $\Delta_{\mathrm{joint}} \le \delta$, contradicting the CA hypothesis $\Delta_{\mathrm{joint}} > \delta$. So ≤ 1 bad γ.

**Why ratio 1:2 is optimal** (Remark `rem:barrier`): the structural ceiling is $2 \delta_{\mathrm{hd}} \le \delta$ (the 2×2 solve picks up a factor 2 from the union of two agreement complements), giving $\delta_{\mathrm{hd}} = \delta/2$. The older BKS18 Case-1/Case-2 split achieves a 1:3 ratio with zero loss; our direct 2×2 solve trades zero loss for the better 1:2 ratio.

**Equal-threshold** (Theorem 4, `thm:eq-threshold-upper`): $\varepsilon_{\mathrm{ca}}(C, \delta, \delta) \le \binom{n}{w}/|F|$, tight up to lower-order terms (Prop. 5, Cor. 6). Vacuous at FRI scale ($\binom{n}{w} \gg |F|$). This is the formal statement behind the OP1-within-CA-framework framing.

---

### [6] FRI coupling inequality — ✅ proved (Lemma 6, `lem:fri-coupling`)

$$\Delta(f, \mathrm{RS}_k) \;\le\; \Delta_{\mathrm{joint}}\bigl((f_{\mathrm{even}}, f_{\mathrm{odd}}), \mathrm{RS}_{k/2}^{=2}\bigr).$$

**Proof**: For each $y \in L'$, the fibre $\{\sqrt{y}, -\sqrt{y}\}$ contributes $c_y \in \{0,1,2\}$ errors. If $f_{\mathrm{even}}(y) = g_{\mathrm{even}}(y)$ and $f_{\mathrm{odd}}(y) = g_{\mathrm{odd}}(y)$, then $f(\pm\sqrt{y}) = g(\pm\sqrt{y})$, so $c_y \ge 1 \Rightarrow$ joint error at $y$. Sum: $\Delta(f,g) \le 2E/n = E/|L'| = \Delta_{\mathrm{joint}}$.

Requires char(F) ≠ 2 and $k$ even (for the ±√y decomposition). The k = 2^m hypothesis is what makes "k even" hold at every fold.

---

### [7] Char-2 additive isomorphism — ✅ proved (Appendix B)

For char(F) = 2, $L$ an $\mathbb{F}_2$-linear subspace, $\beta \in L \setminus \{0\}$: the subspace polynomial $s(x) = x^2 + \beta x$ is $\mathbb{F}_2$-linear with $\ker(s|_L) = \{0, \beta\}$. Image $L' = s(L)$ has $|L'| = n/2$. Decomposition: $f(x) = f_0(s(x)) + x \cdot f_1(s(x))$.

For $k$ even: $g \mapsto (g_0, g_1)$ is an isomorphism $\mathrm{RS}_k(L) \to \mathrm{RS}_{k/2}(L')^{=2}$.

---

### [8] Char-2 FRI coupling — ✅ proved (Appendix B)

$$\Delta(f, \mathrm{RS}_k) \le \Delta_{\mathrm{joint}}\bigl((f_0, f_1), \mathrm{RS}_{k/2}^{=2}\bigr).$$

**Proof**: identical structure to [6]. Each $y \in L'$ has fibre $\{x, x + \beta\}$. Joint agreement at $y$ implies $f = g$ on both preimages. Same bound, char-independent.

---

## Combining: the full FRI theorem (Theorem 10, `thm:fri-full`)

$$\Pr[\text{FRI accepts}] \;\le\; \frac{nR}{|F|} \;+\; \left(1 - \tfrac{\delta}{2}\right)^q.$$

**Strategy A** (honest folding): by [1] + [2], $\Pr[f^{(R)} \in \mathrm{RS}] \le R/|F|$.

**Strategy B** (single deviation at round $i$): the honest fold is $> (\delta/2)$-far for all but ≤ 1 (round 1) or ≤ n (rounds 2..R) values of $\alpha_i$. By [4] with τ = δ/2: $\Pr[\text{not caught}] \le (1-\delta/2)^q$. Over R rounds: $\le nR/|F| + (1-\delta/2)^q$.

**Strategy B-multi** (multiple deviations): two cases. (a) All deviations are at "unlucky" α: each contributes a $(\delta/2)$-far discrepancy on $L$; the union is at least as large as a single one, so $\Pr[\text{all miss}] \le (1-\delta/2)^q$. (b) Some deviation is at "lucky" α: the error propagates through subsequent honest folds; by [1] + [2] applied to the error, $\Pr[f^{(R)} \in \mathrm{RS}] \le R/|F|$.

**Total**: $\max(A, B) \le nR/|F| + (1-\delta/2)^q$.

---

## STIR and WHIR (Section 8)

**STIR** (Theorem 11, `thm:stir-full`):

$$\Pr[\text{STIR accepts}] \;\le\; \frac{(k+2) R}{|F|} \;+\; \left(1 - \tfrac{\delta}{2}\right)^q.$$

The $k$-factor is the OOD shift-query degeneracy, intrinsic to STIR's quotient structure (negligible on extension fields, ~7 bits on the base field — comparable to BCHKS).

**WHIR** (Theorem 13, `thm:whir-full`), assuming the prover-committed initial oracle satisfies $\Delta(f^{(0)}, C^{(0)}) > \delta$:

$$\Pr[\text{WHIR accepts}] \;\le\; \frac{Mk + (n+2)R}{|F|} \;+\; \left(1 - \tfrac{\delta}{2}\right)^q.$$

Proof structure: Case (a) ambient distance $\Delta(f^{(0)}, \mathrm{RS}_k) > \delta$ → handled by half-threshold CA at iteration 1's first fold (the only invocation of half-threshold CA in the WHIR proof); subsequent folds use BCIKS at $\delta/2 < \delta_J$. Case (b) ambient close but constraint-violating → handled by black-box reduction to WHIR Theorems 5.4–5.5 (sumcheck/OOD soundness, MCA-independent). Merkle binding ensures the case split is determined at commit time.

---

## What requires NO further work

| Link | Status | Difficulty |
|------|--------|-----------|
| [1] Multilinearity | ✅ | Trivial |
| [2] Nonzero syndrome | ✅ | Unfold isomorphism + SZ |
| [3] Per-round proximity gap | ✅ | Combines [5] + [6] (round 1); BCIKS classical (rounds ≥ 2) |
| [4] Catch lemma | ✅ | i.i.d. independence under deterministic maps |
| [5] Half-threshold CA (1/F) | ✅ | RVW13 direct 2×2 solve |
| [6] FRI coupling | ✅ | Three lines + contrapositive |
| [7] Char-2 additive fold | ✅ | Subspace polynomial isomorphism |
| [8] Char-2 coupling | ✅ | Identical to [6], additive variant |
| **Full FRI theorem (any char)** | **✅** | **Combines all above** |
| **STIR + WHIR theorems** | **✅** | **Half-threshold CA is drop-in for STIR; WHIR uses Case (a)/(b) + WHIR Thm 5.4–5.5 black box** |

---

## What remains OPEN (interesting but not on the critical path)

| Question | Status | Needed for FRI/STIR/WHIR theorems? |
|----------|--------|----------------|
| Non-CA proof of zero-loss CA above Johnson | ❓ Hard (the equal-threshold CA bound binom(n,w)/|F| is vacuous at FRI scale; any non-CA route is open) | **No** |
| Tight worst-case M_max bounds for general k | ❓ Needs algebraic structure | **No** |
| M = 0 on all RS-compatible flats | ❌ Refuted at FRI scale (Prop. `prop:m2-obstruction`) | **No** |
| Capacity-level proximity gap | ❌ Disproven (Crites–Stewart, Kambiré, Diamond–Gruen) | **No** |

---

## Summary: one sentence

We prove FRI/STIR/WHIR soundness above Johnson for plain Reed–Solomon codes over **any finite field** via a half-threshold CA bound (ε ≤ 1/|F| at threshold δ/2, ratio 1:2 optimal at deployment scale), an FRI coupling inequality (multiplicative or additive), and the BCIKS distance-locking observation that δ/2 sits below the unique-decoding radius — preventing the threshold reduction from compounding across rounds. The 2× query overhead vs. the conjectured zero-loss baseline is intrinsic within the CA framework.
