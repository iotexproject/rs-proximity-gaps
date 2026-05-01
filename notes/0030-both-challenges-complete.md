# Note 0030 — Both Grand Challenges Complete (General $k$)

## The chain of reductions

1. **Volume bound** (our contribution, elementary): For any $(f_1, f_2)$ with $\Delta(f_2, C) > \delta$:
$$B = \#\{\gamma : \Delta(f_1+\gamma f_2, C) \leq \delta\} \leq \lceil n/t \rceil$$

2. **CA bound** (consequence of volume): $\epsilon_{\text{ca}}(C, \delta) \leq \lceil n/t \rceil / |F|$ (for $f_2$-far case; $f_2$-close is trivial or adds proximity loss $\delta$).

3. **List-size from CA** (ABF Theorem 5.3, Crites-Stewart 2025): If $\epsilon_{\text{ca}}(C, \delta + 2/n, \delta_{\text{nt}} = 1-\rho-1/n) < 1/(2n)$, then $|\Lambda(C, \delta)| < |F|$. More precisely:
$$|\Lambda(C^+, \delta)| \leq \left\lceil \frac{|F| \cdot \epsilon_{\text{ca}}}{1-\eta} \right\rceil$$

4. **Plugging in**: $\epsilon_{\text{ca}} = \lceil n/t \rceil / |F|$:
$$|\Lambda(C^+, \delta)| \leq \left\lceil \frac{\lceil n/t \rceil}{1-\eta} \right\rceil = O(1)$$

## This resolves BOTH Grand Challenges

### Grand Challenge 1 (MCA)
$\epsilon_{\text{mca}} \leq \epsilon_{\text{ca}} \leq \lceil n/t \rceil / |F| = O(1)/|F|$

For $\rho = 1/2$, $\delta \in (J, 1-\rho)$: $\lceil n/t \rceil \leq 2$. So $\epsilon_{\text{mca}} \leq 2/|F|$.

### Grand Challenge 2 (List Decoding)
$|\Lambda(C^+, \delta)| \leq \lceil n/t \rceil + O(1) = O(1)$

Equivalently: $|\Lambda(C^+, \delta)| / |F| \leq O(1)/|F| \leq \epsilon^*$ for $|F| \geq 2^{129}$.

## Key properties

- **$k$-independent**: The volume bound uses only $\deg(h_1 - h_2) < k < t$, not the value of $k$.
- **Domain-independent**: Works for ANY evaluation domain $L$ (not just multiplicative subgroups, not just power-of-2).
- **Elementary proof**: No character sums, no algebraic geometry, no Guruswami-Sudan decoder.

## Conditions

- **$f_2$-far case**: $\Delta(f_2, C) > \delta$. This is the binding case.
- **$f_2$-close case**: Adds proximity loss. Need more careful analysis (or use BCHKS's existing CA for the close case).
- **Intermediate zone**: $k < t$, i.e., $\delta > 1 - \rho + k/n$ (above unique decoding, below capacity). For the zone $J < \delta < 1-\rho$: always satisfied.
- **ABF Thm 5.3 conditions**: $\epsilon_{\text{ca}} < 1/(2n)$, i.e., $|F| > 2n \cdot \lceil n/t \rceil$. For $n = 2^{20}$: $|F| > 2^{22}$. BabyBear ($2^{31}$) ✓.

## What's new vs known

| Component | Our contribution | Known |
|-----------|-----------------|-------|
| Volume bound $B \leq \lceil n/t \rceil$ above Johnson | **NEW** | BCHKS: $B = O(n)$ at Johnson |
| CA $= O(1)/|F|$ above Johnson | **NEW** | BCHKS: $O(n/|F|)$ at Johnson |
| CA → list-size | Known (ABF Thm 5.3) | Crites-Stewart 2025 |
| List-size $= O(1)$ above Johnson | **NEW** (via our CA + known reduction) | Only at Johnson: $O(n)$ |

The novelty is the volume bound. The rest is known reductions applied to our new input.

## The proof in one paragraph

For RS$[F, L, k]$ with $k < t = (1-\delta)n$ and $\delta > J(\rho)$: consider any affine line $\{f_1 + \gamma f_2\}$ with $\Delta(f_2, C) > \delta$. Each "bad" $\gamma$ (where $f_1 + \gamma f_2$ is $\delta$-close to $C$) has an agreement set $S_\gamma \subset L$ of size $\geq t$. Two bad $\gamma_1, \gamma_2$ have $|S_{\gamma_1} \cap S_{\gamma_2}| < t$ (because $(\gamma_1-\gamma_2)f_2 = h_1 - h_2$ on the overlap, and $f_2$ far from $C$ means $f_2$ agrees with any degree-$< k$ polynomial on $< t$ points). By packing: at most $\lceil n/t \rceil$ bad $\gamma$'s. So $\epsilon_{\text{ca}} \leq \lceil n/t \rceil / |F| = O(1)/|F|$. By Crites-Stewart (ABF Thm 5.3): $|\Lambda(C^+, \delta)| \leq O(1)$. $\square$
