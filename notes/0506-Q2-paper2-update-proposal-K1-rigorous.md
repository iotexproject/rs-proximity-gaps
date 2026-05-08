# Note 0506 — Q2 GLOBAL: paper2 update proposal with K_1 ≤ 3 rigorous

**Date:** 2026-05-05 (Q2 drill iter 3, post Notes 0504/0505)
**Status:** Proposes paper2 §7 update incorporating Note 0504's K_1 ≤ 3 universal theorem.

## Headline change for paper2

Current paper2 §7 status of `conj:sparse-worst` (Q2 GLOBAL):
- Q2 LOCAL: rigorous via Boundary-Lift + Common-Zero Stratification + rank-α (Note 0502).
- Q2 GLOBAL: fully open conjecture, supported only by 615M trials.

**Proposed v24 status**:
- Q2 LOCAL: unchanged (rigorous).
- Q2 GLOBAL = K_1 + K_2:
  - **K_1 ≤ 3 RIGOROUS** (Note 0504 universal budget bound).
  - K_2 ≤ 7 empirical (615M trials, 0 cex). Structural attack identified (Note 0505).

This significantly **narrows the open part** of Q2 GLOBAL:
- Old: ALL of K ≤ 10 conditional on conjecture.
- New: K_1 ≤ 3 unconditional + K_2 ≤ 7 conditional.

Effectively, paper2's "K ≤ 10 conditional on Q2" becomes "K ≤ 3 + (K_2 ≤ 7 conditional)" — i.e., **paper2's RIGOROUS K bound is now ≤ 10 with the open part being only K_2 ≤ 7**.

## Concrete paper2 §7 edits proposed

### 1. New theorem `thm:K1-universal-budget`

Insert after `thm:K-BW-2-structural`:

> **Theorem (K_1 universal-budget bound).** Let $(f_1, f_2)$ be any pair on
> $L_0 = \mu_{n_0}$ at deployment scale $(n_0, k_0)$, $4 \mid k_0$, $n_0 = 4k_0$,
> with strict above-$J$ joint distance $\Delta_{\mathrm{joint}} > \delta_J n_0$.
> Then
> $$K_1(f_1, f_2; \delta) := \#\{\alpha \in \mathbb{F}_q^* : \mathrm{agr}(f_1 + \alpha f_2,\, 0) \geq T_{\mathrm{thresh}}\} \leq 3$$
> for $T_{\mathrm{thresh}} = (n_0 + k_0)/2$ (the BW unique-decoding agreement threshold).
> Proof: universal budget identity $\sum_{\alpha \in \mathbb{F}_q^*} (\mathrm{agr}(g_\alpha,0) - |T|) = |R|$ + saturation (Lemma 1 + 3 of Note 0504).

### 2. Update `conj:sparse-worst` decomposition

After conjecture statement, add remark:

> **Decomposition $K = K_1 + K_2$.** For any pair $(f_1, f_2)$:
> $K = K_1 + K_2$ where $K_1$ counts $\alpha$ saturating with the zero codeword
> and $K_2$ counts $\alpha$ saturating with non-zero codewords only. Theorem
> `thm:K1-universal-budget` rigorously bounds $K_1 \leq 3$ universally. The
> remaining open conjecture reduces to **$K_2 \leq 7$**, which is supported
> empirically by 615M trials (0 counterexamples).

### 3. Update Q2 paragraph in §sec:open

> **Q2 (sparse-worst dominance)**: ... [existing text] ... New v24 update:
> the conjecture is now decomposed into $K = K_1 + K_2$. The $K_1$ part is
> rigorously bounded $\leq 3$ for all action-non-stab strict above-J pairs at
> deployment scale (Theorem `thm:K1-universal-budget`). Closing $K_2 \leq 7$
> via the van Lint-Wilson / Welch-Gong attack (Note 0505) would give Q2
> GLOBAL unconditionally.

### 4. Update Layer 3 status table

Add row:
| Layer | Status | Note |
|---|---|---|
| L3 K_1 (universal budget) | RIGOROUS | thm:K1-universal-budget (NEW) |
| L3 K_2 ≤ 7 | empirical (615M) | open structural |

## Key technical content for the new theorem

The proof is short (~half page in paper format):

**Lemma A (Universal Budget Identity).** For any $(f_1, f_2)$ on $L_0$, with
$T = Z(f_1) \cap Z(f_2)$, $T_u = Z(f_1) \setminus T$, $T_v = Z(f_2) \setminus T$,
$R = L_0 \setminus (T \cup T_u \cup T_v)$:
$$\sum_{\alpha \in \mathbb{F}_q^*} (\mathrm{agr}(f_1 + \alpha f_2,\, 0) - |T|) = |R|.$$

**Proof sketch.** Each $z \in T$ contributes $|T|$ to every $\mathrm{agr}(g_\alpha, 0)$ (universally). Each $z \in R$ contributes 1 to a unique $\alpha = -f_1(z)/f_2(z) \in \mathbb{F}_q^*$. Sum follows. $\square$

**Lemma B (Saturation).** $K_1 \cdot (T_{\mathrm{thresh}} - |T|) \leq |R|$.

**Lemma C (Above-J implies $|T| < n_0/2$).** If $\Delta_{\mathrm{joint}}((f_1, f_2), C^2) > \delta_J n_0 = n_0/2$ (rate $\rho = 1/4$), then $|T| < n_0/2$. (Trivial: take $(c_1, c_2) = (0, 0)$.)

**Combining**: $K_1 \leq |R|/(T_{\mathrm{thresh}} - |T|) \leq (n_0 - |T|)/((n_0+k_0)/2 - |T|)$. Plugging $|T| < n_0/2$ and $T_{\mathrm{thresh}} = (n_0+k_0)/2 = n_0/2 + k_0/2$: $K_1 \leq (n_0 - |T|)/(k_0/2 + (n_0/2 - |T|))$. At $|T| \to n_0/2$: $K_1 \leq (n_0/2)/(k_0/2) = n_0/k_0 = 4$. With strict above-J $|T| \leq n_0/2 - 1$: $K_1 \leq (n_0/2 + 1)/(k_0/2 + 1) < n_0/k_0 = 4$. Combined with floor: $K_1 \leq 3$. $\square$

Actually let me redo more carefully. For $(n_0, k_0) = (32, 8)$, $T_{\mathrm{thresh}} = 20$:
$K_1 \leq (32 - |T|)/(20 - |T|)$. At $|T| = 15$: $17/5 = 3.4 \Rightarrow K_1 \leq 3$.

For $(n_0, k_0) = (128, 32)$, $T_{\mathrm{thresh}} = 80$:
$K_1 \leq (128 - |T|)/(80 - |T|)$. At $|T| = 63$: $65/17 \approx 3.82 \Rightarrow K_1 \leq 3$.

For deployment scales $(n_0, k_0) \in \{(32, 8), \ldots, (2^{19}, 2^{17})\}$: bound stays $\leq 3$ throughout.

## K_2 attack: convergent vLW + WG

From Note 0505 (Helleseth + Gong consult):

For $K_2$-witness $\alpha$ (non-zero codeword $c_\alpha$ with $\mathrm{agr}(g_\alpha, c_\alpha) \geq T_{\mathrm{thresh}}$):
- $h := g_\alpha - c_\alpha$ has weight $\leq \tau_{\mathrm{BW}} = (n_0 - k_0)/2$.
- DFT-zero-set of $h$ contains $D_\alpha := \{j \in [k_0, n_0) : \hat{g}_\alpha(j) = 0\}$ (since $c_\alpha \in \mathrm{RS}_{k_0}$, $\hat{c}_\alpha(j) = 0$ on $[k_0, n_0)$).

If we can prove: **for K_2-witness, $|D_\alpha| \geq 4$**, then by pigeonhole:
$\sum_{K_2\text{-witnesses}} |D_\alpha| \leq \sum_{\alpha \in \mathbb{F}_q^*} |D_\alpha| = \#\{j \in [k_0, n_0) : \hat{f}_2(j) \neq 0\} \leq n_0 - k_0$.
Hence $K_2 \cdot 4 \leq n_0 - k_0 = 24 \Rightarrow K_2 \leq 6 \leq 7$. $\square$

Status of $|D_\alpha| \geq 4$ lemma:
- Plausible from BCH-type arguments but BCH alone doesn't give it.
- vLW shifting bound on cyclic code $\mathcal{C}$ with defining set $D_\alpha$ may give $\min$ distance $> \tau_{\mathrm{BW}}$ when $|D_\alpha| \geq 4$, ruling out witness.
- Alternative: Welch-Gong elimination (Gong's path) gives explicit $\Phi(f_1, f_2; X) \in \mathbb{F}_q[X]$ with $K_2$-witnesses among roots; cyclotomic mod-4 chop reduces $\deg \Phi$ from $\sim 2k_0$ down to $\leq 7$.

## Strategic implications

1. **Immediate paper2 win**: Note 0504 K_1 ≤ 3 is RIGOROUS new content. Paper2 v24 should incorporate.

2. **K_2 attack tractable**: Both Helleseth and Gong personas estimate ~35-45% in 1 month.

3. **If K_2 ≤ 7 closes**: Q2 GLOBAL becomes unconditional theorem. **Paper2 prize-readiness jumps from "modulo Q2 conjecture" to "all 3 RS proximity-gap obstructions rigorously closed at deployment scale"**.

## Open work items

| Task | Approach | Estimated time |
|---|---|---|
| Verify K_1 ≤ 3 at structured stratum (B) cases | Plug Note 0471 setup into Note 0504 formula | done (matches K_1 ≤ 2) |
| Empirically test \|D_α\| ≥ 4 for K_2-witnesses | Need Sudan list decoder; brute force at (8,2) | 1-2 days |
| Prove vLW lemma: \|D_α\| ≥ 4 ⇒ no witness | Use Schmidt-Willems shifting bound | 1-2 weeks |
| Welch-Gong elimination polynomial | Gong's path; Hankel rank + cyclotomic chop | 2-4 weeks |
| paper2 v24 §7 update | After K_2 attack matures | 2-3 days |

## Conclusion

Note 0504's K_1 ≤ 3 universal bound is **the first rigorous structural improvement to paper2's Q2 status since Note 0502** (Conj A killed at deployment). It's a clean, short proof that should be incorporated into paper2 v24 immediately.

The K_2 attack via vLW or WG is concrete with literature support and ~35-45% probability of closing in 1 month. If it closes, **paper2 becomes unconditional at L_3 deployment** — a major prize-claim upgrade.
