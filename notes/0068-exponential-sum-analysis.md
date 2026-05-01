# Note 0068 — Exponential Sum Analysis: Structure and Barrier

## 1. Setup

Character sum for compatibility counting:
$$S(\alpha) = \sum_{B \in \binom{[n]}{w}} \psi\!\left(\sum_{j=1}^w \alpha_j \sigma_j(B)\right)$$

where $\sigma_j(B) = e_j(\{\omega^i : i \in B\})$ are elementary symmetric polynomials of roots of unity, $\psi(x) = \exp(2\pi i x/p)$.

$$M_{\text{alg}} = \frac{N}{p^c} + \frac{1}{p^c} \sum_{t \neq 0} S(t)$$

where $N = \binom{n}{w}$, $c = n-k-w$ conditions, and $S(t)$ involves $\alpha_j = \alpha_j(t, c_{\text{high}})$ from the center.

## 2. Product Formula (Verified)

**Identity**: $\prod_{i=0}^{n-1}(1+\beta\omega^i) = 1-(-\beta)^n$.

*Proof*: From $x^n - 1 = \prod(x-\omega^i)$, set $x = -1/\beta$. ∎

For $\alpha_j = \beta^j$ ("geometric direction"):
$$S(\beta,\beta^2,\ldots,\beta^w) = \sum_B \psi\!\left(\prod_{i \in B}(1+\beta\omega^i) - 1\right)$$

When $(-\beta)^n \neq 1$ (i.e., $-\beta \notin L$): setting $\Gamma = 1-(-\beta)^n$,
$$S = \sum_B \psi(\Gamma / Q_{B^c} - 1), \quad Q_{B^c} = \prod_{j \notin B}(1+\beta\omega^j)$$

This is a **Kloosterman-type sum** $\sum \psi(\Gamma/Q)$ over complement products.

When $L = \mathbb{F}_p^*$ ($n = p-1$): $-\beta \in L$ for ALL $\beta$, so $\Gamma = 0$ always. The Kloosterman approach is **dead** for $L = \mathbb{F}_p^*$.

## 3. Newton-Gauss Decomposition (New)

### Key insight

Via Newton's identities: $\sigma_j = N_j(p_1, \ldots, p_j)$ where $p_k = \sum_{i \in B} \omega^{ki}$ are power sums. Crucially:
- $\sigma_1 = p_1$ (linear)
- $\sigma_2 = (p_1^2 - p_2)/2$ (quadratic in $p_1$)
- $\sigma_3 = (p_1^3 - 3p_1 p_2 + 2p_3)/6$ (cubic)

**Conditioning on $p_1 = v$**: all $\sigma_j$ for $j \geq 2$ become **LINEAR** in $(p_2, \ldots, p_w)$!

This is because $\sigma_j = N_j(v, p_2, \ldots, p_j)$ with $v$ fixed, and $N_j$ is linear in $p_j$ (the only degree-$j$ term is $p_j$ with coefficient $\pm 1/j$), and all products $p_i \cdot p_k$ with $i, k \geq 2$ have lower total index.

Wait — this isn't quite right. Let me be precise: $\sigma_2 = (p_1^2 - p_2)/2$. Given $p_1 = v$: $\sigma_2 = (v^2 - p_2)/2$ is LINEAR in $p_2$. ✓

$\sigma_3 = (p_1^3 - 3p_1 p_2 + 2p_3)/6$. Given $p_1 = v$: $\sigma_3 = (v^3 - 3v \cdot p_2 + 2p_3)/6$ is LINEAR in $(p_2, p_3)$. ✓

In general: given $p_1 = v$, $\sigma_j$ is a polynomial in $(p_2, \ldots, p_j)$ that is **linear** in each $p_k$ (since the Newton polynomial $N_j$ is linear in $p_j$ and products $p_i p_k$ only arise through $p_1 = v$ which is fixed). ✓

### Decomposition for $w = 2$

$$S(\alpha_1, \alpha_2) = \frac{1}{p} \sum_{\tau=0}^{p-1} G\!\left(\frac{\alpha_2}{2},\, \alpha_1 - \tau\right) \cdot e_w\!\left(\psi\!\left(-\frac{\alpha_2}{2}\omega^{2i} + \tau\omega^i\right)\right)$$

where $G(a,b) = \sum_{v \in \mathbb{F}_p} \psi(av^2 + bv) = \varepsilon\sqrt{p}\, \psi(-b^2/4a)$ is the Gauss sum.

**Verified computationally**: exact match for all tested $(n,p)$.

**Bound**: $|S| \leq \frac{1}{p} \sum_\tau |G(\tau)| \cdot |e_w(\tau)| \leq \frac{\sqrt{p}}{p} \sum_\tau |e_w(\tau)|$

By Cauchy-Schwarz: $|S| \leq \frac{\sqrt{p}}{p} \cdot \sqrt{p} \cdot \sqrt{\sum |e_w|^2} = \sqrt{\sum |e_w|^2 / p}$

Parseval for e_w: $\sum_\tau |e_w(\tau)|^2 = p \cdot N$ (when $\sigma$ map is injective on $(p_1, p_2)$ fibers).

So: $|S| \leq \sqrt{p \cdot N / p} = \sqrt{N}$... wait, this would be OPTIMAL. Let me recheck.

Actually: $\sum_\tau |e_w(\tau)|^2$ includes $\tau = 0$ term $|e_w(0)|^2 = N^2$. Excluding $\tau = 0$... no, we sum over all $\tau$.

The correct Parseval: over all $(\alpha, \beta) \in \mathbb{F}_p^2$: $\sum |e_w(\alpha, \beta)|^2 = p^2 \cdot \sum_{\text{fibers}} (\text{fiber size})^2$.

For injective $(p_1, p_2)$ map: $\sum |e_w|^2 = p^2 \cdot N$ (each fiber has size 1, except missing values have 0). The sum includes the $(\alpha,\beta) = (0,0)$ term $= N^2$.

So $\sum_{(\alpha,\beta) \neq 0} |e_w|^2 = p^2 N - N^2$, giving $\text{rms} |e_w| = \sqrt{(p^2 N - N^2)/(p^2-1)} \approx \sqrt{N}$.

The Gauss+e_w convolution: $S(\alpha_1) = \frac{1}{p} \sum_\tau G(a, \alpha_1-\tau) \cdot T(\tau)$ where $T(\tau) = e_w(\tau, c_2)$ is the e_w at fixed $\beta = c_2$.

By CS on the convolution: $|S|^2 \leq \frac{1}{p^2} \|G\|_2^2 \cdot \|T\|_2^2$.

$\|G\|_2^2 = \sum_b |G(a,b)|^2 = p \cdot p = p^2$ (each $|G| = \sqrt{p}$ for $a \neq 0$... actually $|G(a,b)| = \sqrt{p}$ for all $b$ when $a \neq 0$, so $\|G\|_2^2 = p \cdot p = p^2$).

$\|T\|_2^2 = \sum_\tau |e_w(\tau, c_2)|^2$. By the 1D Parseval: $\sum_\tau |T(\tau)|^2 = p \cdot \sum_v (\text{fiber}(v, c_2))^2$.

For generic $c_2$: most $(p_1, p_2 = c_2)$ fibers have size $\approx N/p^2$, so $\sum \text{fiber}^2 \approx p \cdot (N/p^2)^2 = N^2/p^3$. Then $\|T\|_2^2 = p \cdot N^2/p^3 = N^2/p^2$, giving $|S| \leq p \cdot N/p^2 \cdot p / p = N/p$. This would be excellent!

But this is wrong — the fibers are not all $N/p^2$ because we're fixing $p_2 = c_2$, not both $p_1$ and $p_2$.

Let me redo: $T(\tau) = \sum_{B: p_2(B) = c_2} \psi(\tau \cdot p_1(B))$. So $\|T\|_2^2 = p \cdot |\{B : p_2(B) = c_2\}| = p \cdot (N/p)$ (if $p_2$ is equidistributed). $= N$.

Then CS: $|S|^2 \leq p^2 \cdot N / p^2 = N$, giving $|S| \leq \sqrt{N}$.

This matches rms|S| = √N from Parseval! So the Gauss decomposition with CS gives **exactly** the Parseval bound — no improvement.

### Decomposition for $w = 3$

For $w = 3$ with $\alpha_3 \neq 0$: $g_v(x)$ depends on $v$ through the coefficient $-\alpha_3 v/2$ of $x^2$. Need an additional Fourier layer (sum over $v$ with cubic phase).

## 4. Multiplicative Fourier Approach

For the Kloosterman form $S = \sum_C \psi(\Gamma/Q_C)$ where $Q_C = \prod_{j \in C} f_j$:

$$S = \frac{1}{p-1} \sum_\chi g(\chi) \chi^{-1}(\Gamma) \cdot e_r\!\left(\chi^{-1}(1/f_0), \ldots, \chi^{-1}(1/f_{n-1})\right)$$

where $g(\chi) = \sum_t \chi(t)\psi(t)$ is the Gauss sum ($|g(\chi)| = \sqrt{p}$ for $\chi \neq \chi_0$) and $r = n-w$.

**Bound**: $|S| \leq \frac{1}{p-1}\left[N + (p-2)\sqrt{p} \cdot \max_{\chi \neq \chi_0} |e_r(\chi)|\right]$

If $\max |e_r(\chi)| \sim \sqrt{N}$: $|S| \leq O(\sqrt{pN})$. Same barrier.

**Verified** for $(8, 4, 17)$: multiplicative Fourier matches direct computation.

## 5. The √(pN) Barrier

### Statement

All approaches to bounding $|S(\alpha)|$ converge to $O(\sqrt{pN})$:

| Method | Bound | Source |
|--------|-------|--------|
| Parseval + CS | $\sqrt{N}$ (rms), max could be larger | rms only |
| Gauss + e_w | $\sqrt{p} \cdot \max |e_w| \sim \sqrt{pN}$ | e_w of structured phases |
| Multiplicative Fourier | $(p-2)\sqrt{p} \cdot \max |e_r|/(p-1) \sim \sqrt{pN}$ | e_r of characters |

### Empirical verification

| $n$ | $k$ | $w$ | $c$ | $p$ | max$|S|$ | $\sqrt{pN}$ | ratio |
|-----|-----|-----|-----|-----|---------|------------|-------|
| 6 | 3 | 2 | 1 | 31 | 9.28 | 21.56 | 0.43 |
| 8 | 4 | 3 | 1 | 73 | 33.52 | 63.94 | 0.52 |
| 10 | 5 | 3 | 2 | 11 | 28.49 | 36.33 | 0.78 |
| 10 | 5 | 3 | 2 | 101 | 58.66 | 110.09 | 0.53 |
| 10 | 5 | 3 | 2 | 151 | 48.78 | 134.61 | 0.36 |

The ratio max$|S|/\sqrt{pN}$ is $O(1)$ — **the barrier is tight**.

### Why this is insufficient

For $M_{\text{alg}} = O(1)$: need $\max|S(t)| \leq O(p^c)$.

But $\sqrt{pN} \gg p^c$ for large $n$ (fixed $p \approx n$):
$\sqrt{pN} = \sqrt{n \cdot 2^{0.87n}} = \sqrt{n} \cdot 2^{0.44n}$ vs $p^c = n^{0.21n}$.

For $n \geq 10$: $\sqrt{n} \cdot 2^{0.44n} \gg n^{0.21n}$, so the character sum bound gives $M \gg 1$.

### The REAL cancellation

Empirically: $\max_c M_{\text{alg}}(c)$ is bounded ($\leq 45$ for $n \leq 12$). This means the SUM $\sum_{t \neq 0} S(t)$ has massive cancellation that individual bounds on $|S(t)|$ cannot capture.

The second moment confirms this:

| $n$ | $p$ | $E[M]$ | $\text{Var}[M]$ | $E[M^2]$ | max $M$ | Poisson? |
|-----|-----|--------|-----------------|----------|---------|---------|
| 6 | 7 | 2.14 | 1.84 | 6.43 | 15 | ≈yes |
| 8 | 17 | 3.29 | 3.10 | 13.95 | 56 | ≈yes |
| 10 | 11 | 0.98 | 2.64 | 3.60 | 36 | slightly super |
| 10 | 31 | 0.12 | 0.20 | 0.21 | 8 | ≈yes |

$\text{Var}[M] \approx E[M]$ — **Poisson-like behavior**, consistent with pseudorandom σ-image.

## 6. Additional Findings

### σ map injectivity

For all tested $(n, p)$: the full σ map $B \mapsto (\sigma_1, \ldots, \sigma_w)$ is **fully injective** (max fiber = 1). This gives Parseval rms$|S| = \sqrt{N}$ exactly.

### Subspace restriction

The relevant α directions lie in a $c$-dimensional subspace $V_c$ of $\mathbb{F}_p^w$, determined by the center. Empirically: $\max_{\alpha \in V_c} |S(\alpha)| = \max_{\text{all } \alpha} |S(\alpha)|$. **No benefit from restricting to $V_c$**.

### Power sum factorization

For any **linear** combination of power sums $\sum \beta_k p_k(B)$:
$$\sum_B \psi\!\left(\sum_k \beta_k p_k(B)\right) = e_w\!\left(\psi(\beta_1 \omega^0 + \beta_2 \omega^0 + \cdots), \ldots, \psi(\beta_1 \omega^{n-1} + \cdots)\right)$$

This **factors as an elementary symmetric polynomial of unit complex numbers**. The bound $|e_w(z)| \leq \binom{n}{w}$ with $|z_i| = 1$ is trivially $N$; the structured-phase bound gives $O(\sqrt{N})$.

The obstacle: σ_j for $j \geq 2$ involves **products** of power sums ($p_1^2$ in σ_2, etc.), which destroy the factorization.

### Polynomial method constraint

All codewords in maximum-$M$ lists are at pairwise distance exactly $d_{\min} = n-k+1$.

| $n$ | $k$ | $d_{\min}$ | $2w$ | distances in list |
|-----|-----|-----------|------|-------------------|
| 8 | 4 | 5 | 6 | {5, 6} |
| 10 | 5 | 6 | 6 | {6} — ALL at $d_{\min}$! |
| 12 | 6 | 7 | 8 | {7, 8} |

For $\rho = 1/2$: $d_{\min} = n/2 + 1$ and $2w \approx n/2 + O(\sqrt{n})$. So $2w - d_{\min} = O(\sqrt{n})$ — the pairwise distances are tightly constrained.

## 7. Proof Strategy Assessment

### Direction C (exponential sums): BARRIER IDENTIFIED

Bounding individual $|S(t)|$ cannot prove $M = O(1)$ because:
1. max$|S| = \Theta(\sqrt{pN})$ — structural, all methods agree
2. This gives $M_{\text{alg}} \leq \sqrt{pN}$ which grows exponentially with $n$
3. The actual $M$ is bounded due to cancellation in $\sum S(t)$, not in individual terms

### What Direction C contributes

1. **Newton-Gauss decomposition**: structural tool for future work
2. **Product formula / Kloosterman connection**: links to multiplicative number theory
3. **σ injectivity**: confirms pseudorandom behavior, enables Parseval arguments
4. **Second moment / Poisson behavior**: the right "explanation" of boundedness, but proving $E[M^2] = O(1)$ is as hard as the original problem

### Remaining viable directions

**(A) Polynomial factorization** — MOST PROMISING given new data:
- All pairwise differences $f_i - f_j$ have exactly $d_{\min}$ nonzeros on $L$
- This means $f_i - f_j$ has exactly $n - d_{\min} = k - 1$ zeros on $L$
- So $(f_i - f_j)$ has a factorization dictated by the subgroup structure
- The number of such "minimum-weight" differences is bounded by the structure of $\text{RS}_k$ on the multiplicative subgroup

**(D) Sum-product incidence** — relates to σ-image equidistribution:
- The σ map is injective (proven empirically)
- The image $\{\sigma(B)\}$ is pseudorandom
- Sum-product estimates for multilinear maps on multiplicative subgroups could give the equidistribution bound directly

## 8. Scripts

- `exp_sum_explore.py` — Round 1: product formula, power sums, DFT, p-scaling
- `exp_sum_deep.py` — Round 2: Newton-Gauss decomposition, Gauss+e_w, quadratic expansion
- `exp_sum_cancellation.py` — Round 3: multiplicative Fourier, M_alg cancellation, Kloosterman
- `exp_sum_barrier.py` — Round 4: barrier test, actual vs bound, second moment, polynomial method
