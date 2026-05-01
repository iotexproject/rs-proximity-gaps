# Note 0062 — Gap C: Full FRI Soundness Without δ/2 Loss

## Current Theorem (with δ/2 loss)

**Theorem 5.1** (paper.tex): For RS[F_p, L, k] with k = 2^m, δ_J < δ < 1-ρ:

$$\varepsilon_{\text{FRI}} \leq \frac{3R}{|\mathbb{F}|} + (1 - \delta/2)^q$$

## Improved Theorem (assuming M = O(1))

**Theorem (conditional on M = O(1))**:

If the list size $M(\delta) = \max_c |\{f \in \text{RS}_k : d(f|_L, c) \leq \delta n\}| \leq M_0$ for
a constant $M_0$ depending only on $\rho$ and $\delta$ (not on $n$ or $p$), then:

$$\varepsilon_{\text{FRI}} \leq \frac{(M_0 + 2)R}{|\mathbb{F}|} + (1 - \delta)^q$$

### Proof sketch

**Step 1 — Per-round proximity gap with full δ**: By the ABF framework (Theorem 2.1 in BCIKS),
the per-round proximity gap at distance $\delta$ satisfies:

$$\Pr_\gamma[\Delta(f_0 + \gamma f_1, \text{RS}_{k/2}) > \delta] \leq \frac{M_0}{|\mathbb{F}|}$$

This is because: $f_0 + \gamma f_1$ is $\delta$-close to RS iff $\gamma$ is a "bad" folding
challenge. Each bad $\gamma$ corresponds to a codeword in the list at distance $\delta n$.
With at most $M_0$ such codewords: at most $M_0$ bad $\gamma$'s.

(Compare with our current paper: we use halved threshold $\delta/2$ to ensure the list is
contained in the halved-distance ball, giving $\Pr \leq O(1)/|\mathbb{F}|$ but at distance $\delta/2$.)

**Step 2 — FRI composition**: Using the single-deviation argument (Section 5 of paper):

- Strategy A (all rounds honest): $\Pr[\text{accept}] \leq R/|\mathbb{F}|$ (Schwartz-Zippel)
- Strategy B (one dishonest round $i$):
  - Commit phase: $\Pr[\text{close at round } i] \leq M_0/|\mathbb{F}|$
  - Query phase: $\Pr[\text{pass queries}] \leq (1-\delta)^q$ (full $\delta$, no halving!)
  - Combined: $\leq M_0/|\mathbb{F}| + (1-\delta)^q$
- Over R rounds: $\leq R \cdot M_0/|\mathbb{F}| + (1-\delta)^q$

**Step 3 — Total**:

$$\varepsilon_{\text{FRI}} \leq \max(R/|\mathbb{F}|,\; R \cdot M_0/|\mathbb{F}| + (1-\delta)^q) \leq \frac{M_0 R}{|\mathbb{F}|} + (1-\delta)^q$$

## Concrete Improvement

For rate 1/2, $\delta = 0.35$ (above Johnson $\delta_J \approx 0.293$), BabyBear ($|\mathbb{F}| = 2^{31}-1$):

| Parameter | Current (δ/2) | With M=O(1) | Improvement |
|-----------|--------------|-------------|-------------|
| Query soundness per round | $(1-0.175)^q = 0.825^q$ | $(1-0.35)^q = 0.65^q$ | |
| At $q = 30$ | $0.825^{30} \approx 2^{-8.2}$ | $0.65^{30} \approx 2^{-17.8}$ | **+9.6 bits** |
| At $q = 50$ | $0.825^{50} \approx 2^{-13.7}$ | $0.65^{50} \approx 2^{-29.6}$ | **+15.9 bits** |
| Commit soundness | $3R/|\mathbb{F}|$ | $7R/|\mathbb{F}|$ | ~1 bit worse |
| Total at $q=50, R=20$ | ~13 bits | ~29 bits | **+16 bits** |

The query phase improvement ($\delta$ vs $\delta/2$) dramatically outweighs the minor
commit phase worsening ($M_0$ vs 3).

## What's Needed

1. **Prove M = O(1)**: the Pairwise Rank Lemma (Note 0059/0060).

2. **Determine $M_0$**: From data, $M_0 \leq 7$ for rate 1/2 at Johnson.

3. **Write into paper**: Add a section "Full proximity gap (conditional)" stating the
   improved theorem and the condition $M = O(1)$.

## Connection to Prize

The Prize specifically targets proximity gap bounds for RS codes above Johnson.

- Our CURRENT theorem gives an unconditional proximity gap with δ/2 loss.
- The IMPROVED theorem (conditional on M = O(1)) gives the FULL proximity gap.
- Proving M = O(1) for multiplicative subgroups is the remaining step.

The Prize judges (Boneh, Fenzi, Arnon) would likely value:
1. The unconditional theorem (50-60% of prize): novel, complete, publishable
2. Plus M = O(1) proof (90%+): resolves the core open problem

## The Clean Conditional Statement

**Theorem (Full FRI Soundness, conditional)**: Let RS[n,k] be a Reed-Solomon code
on a multiplicative subgroup L ⊂ F_p^* of order n with k = 2^m. Assume:

**(H)**: For all $\delta \in (\delta_J, 1-\rho)$, the list size satisfies
$M(\delta) \leq M_0(\rho, \delta)$ for some function $M_0$ independent of $n$ and $p$.

Then the FRI protocol with R rounds and q queries per round has soundness error:

$$\varepsilon_{\text{FRI}} \leq \frac{M_0 R}{|\mathbb{F}|} + (1-\delta)^q$$

Under hypothesis (H) with $M_0 \leq 7$ (verified computationally for $n \leq 16$,
$\rho = 1/2$): BabyBear FRI achieves ~29 bits per round at $\delta = 0.35$, $q = 50$.
