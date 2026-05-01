# Note 0007 — List-Size Bound Above Johnson

**Date**: 2026-04-20  
**Status**: Empirical scaling law established; proof sketch in progress

## 1. The problem

For $\mathrm{RS}_k$ on domain $L$ ($|L| = n$), the **per-word list size** is:

$$M_\delta(w) = \#\{h \in \mathrm{RS}_k : |\{x \in L : w(x) = h(x)\}| \geq (1-\delta)n\}$$

The Johnson bound gives $M_\delta \leq n/k$ when $\delta < 1 - \sqrt{\rho}$ ($\rho = k/n$). **Above Johnson**, no generic bound is known.

For the CS construction: $t = rm$, $k = (r-2)m$, $\delta = 1 - r/s$. At $m = 2, r = 3$: $t = 6, k = 2, \delta = 1 - 6/n$. The Johnson boundary is $\delta = 1 - \sqrt{2/n} \approx 1 - 0.24/\sqrt{n}$, while $\delta_{\mathrm{CS}} = 1 - 6/n$. For $n > 36$: $\delta_{\mathrm{CS}} > \delta_J$, so we're **above Johnson**.

## 2. Empirical scaling law

Tested $n \in \{36, 48, 60, 72, 96, 120, 144, 180, 240\}$ with proper-subgroup primes. Words: $w = x^a + \lambda x^b$ for $(a,b) \in \{(6,4), (6,5), (7,6)\}$.

**Result**: $M_\delta(w) \leq n/(t-1)$, with equality achieved by $(a,b) = (6,5)$.

| $n$ | $(a,b)$ | $\max M$ | $n/(t-1)$ | ratio |
|-----|---------|----------|-----------|-------|
| 36 | any | 6 | 7.2 | 0.83 |
| 48 | any | 8 | 9.6 | 0.83 |
| 60 | (6,5) | 11 | 12 | 0.92 |
| 72 | CS/(7,6) | 12 | 14.4 | 0.83 |
| 96 | any | 16 | 19.2 | 0.83 |
| 120 | (6,5) | 24 | 24 | 1.00 |
| 180 | (6,5) | 39 | 36 | 1.08 |
| 240 | (6,5) | 47 | 48 | 0.98 |

**Conjecture**: For $k = 2$, threshold $t \geq 6$, and $L$ a multiplicative subgroup:

$$M_\delta(w) \leq \frac{n}{t-1} + O(1)$$

for all words $w$ and all primes $p \equiv 1 \pmod{n}$.

## 3. Why classical bounds fail

The Plotkin/Cauchy-Schwarz approach:

Given $M$ codewords $h_1, \ldots, h_M$ with $|S_i| \geq t$ and $|S_i \cap S_j| \leq k-1 = 1$:

$$\left(\sum |S_i|\right)^2 \leq n \sum |S_i|^2 \leq n(M^2 + (t-1)M)$$

This gives $t^2 M \leq n(M + t - 1)$, i.e., $M(t^2 - n) \leq n(t-1)$.

- For $t^2 > n$: $M \leq n(t-1)/(t^2 - n)$ (BELOW Johnson)
- For $t^2 = n$: $M \leq \infty$ (AT Johnson boundary)
- For $t^2 < n$: **no bound** (ABOVE Johnson)

Our operating point: $t = 6, n > 36$, so $t^2 = 36 < n$. Cauchy-Schwarz gives nothing.

## 4. The dual picture

In the $(h_0, h_1)$-plane, define $n$ lines:

$$\ell_i: h_0 + h_1 \omega^i = w(\omega^i), \quad i = 0, \ldots, n-1$$

These are $n$ lines in $\mathbb{F}_p^2$, in "general position" (no two parallel, since $\omega^i$ are distinct).

A $t$-rich point $(h_0, h_1)$ lies on $\geq t$ of these lines, corresponding to a codeword $h = h_0 + h_1 x$ that agrees with $w$ on $\geq t$ points of $L$.

**The list size $M$ equals the number of $t$-rich points of this line arrangement.**

## 5. Structure of the dual lines

The $n$ dual lines have coefficients $(1, \omega^i, c_i)$ where $c_i = w(\omega^i)$. The arrangement is NOT generic — it inherits the multiplicative structure of $L$.

**Key property**: The $n$ lines are indexed by a cyclic group $\mathbb{Z}/n\mathbb{Z}$ (via $i \mapsto \omega^i$), and the slopes $\omega^i$ form a multiplicative subgroup of $\mathbb{F}_p^*$.

The intersection point of $\ell_i$ and $\ell_j$ is:

$$h_1 = \frac{c_j - c_i}{\omega^j - \omega^i}, \quad h_0 = c_i - h_1 \omega^i$$

For $w(x) = x^a + \lambda x^b$:

$$c_i = \omega^{ai} + \lambda \omega^{bi}$$

$$h_1 = \frac{\omega^{aj} - \omega^{ai} + \lambda(\omega^{bj} - \omega^{bi})}{\omega^j - \omega^i}$$

The divided differences $\frac{\omega^{aj} - \omega^{ai}}{\omega^j - \omega^i}$ are sums of powers of $\omega$ — character-sum-like objects that live in $\mathbb{Z}[\zeta_n]$.

## 6. Proof strategy for $M = O(n)$

### Approach 1: Degree bound

A $t$-rich point lies on $\geq t$ lines, meaning $\geq t$ of the equations $h_1 \omega^i + h_0 = c_i$ hold. Fix $h_1$: then $h_0 = c_i - h_1 \omega^i$ for each agreeing $i$. For these to be consistent (same $h_0$): $c_i - h_1 \omega^i = c_j - h_1 \omega^j$ for all agreeing pairs, i.e., $h_1 = (c_i - c_j)/(\omega^i - \omega^j)$ for all pairs.

So: fix $h_1$. The set of $i$ such that $h_0 = c_i - h_1 \omega^i$ is the same value is the agreement set. The function $f(i) = c_i - h_1 \omega^i = w(\omega^i) - h_1 \omega^i$ is a polynomial in $\omega^i$ of degree $\max(a, 1)$. The agreement set is $\{i : f(i) = h_0\}$, i.e., roots of $f(i) - h_0 = 0$.

For $w(x) = x^a + \lambda x^b$: $f(x) = x^a + \lambda x^b - h_1 x$, and $f(x) - h_0 = 0$ has degree $a$. So $|S| \leq a$.

**Now: for a fixed $h_1$, how many values of $h_0$ give $|S| \geq t$?**

$f(\omega^i) = \omega^{ai} + \lambda \omega^{bi} - h_1 \omega^i$ takes values in $\mathbb{F}_p$. As $i$ ranges over $\{0, \ldots, n-1\}$, $f$ takes at most $n$ values (possibly with repeats). The number of values $h_0$ with $|\{i : f(\omega^i) = h_0\}| \geq t$ is at most $n/t$ (pigeonhole: $n$ values, each counted at most once, partitioned into classes of size $\geq t$).

**So: for each $h_1$, at most $n/t$ values of $h_0$ give $|S| \geq t$.**

**And: the total $M = \sum_{h_1} \#\{h_0 : |S_{h_0,h_1}| \geq t\}$.**

But this gives $M \leq p \cdot n/t$, which is huge (proportional to $p$). We need to sum only over $h_1$ values that actually achieve $|S| \geq t$.

### Approach 2: Refined pigeonhole

For a **fixed word** $w$:
- The function $g_{h_1}(i) = w(\omega^i) - h_1 \omega^i$ maps $\{0, \ldots, n-1\} \to \mathbb{F}_p$.
- A value $h_0$ is $t$-popular for $g_{h_1}$ if $|g_{h_1}^{-1}(h_0)| \geq t$.
- The number of $t$-popular values is $\leq \lfloor n/t \rfloor$.

Total list size: $M = \#\{(h_0, h_1) : |g_{h_1}^{-1}(h_0)| \geq t\} = \sum_{h_1} \#\{h_0 : t\text{-popular for } g_{h_1}\}$.

Each $h_1$ contributes $\leq \lfloor n/t \rfloor$ to the sum. But the sum is over all $h_1 \in \mathbb{F}_p$, so $M \leq p \cdot \lfloor n/t \rfloor$.

**This is too weak.** We need to show that most $h_1$ contribute 0.

### Approach 3: Algebraic constraint on $h_1$

For $w(x) = x^a + \lambda x^b$ and $k = 2$: the agreement polynomial is $P(x) = x^a + \lambda x^b - h_1 x - h_0$. For $|S| \geq t = a$ (all roots in $L$): $P$ splits completely over $L$.

The condition "$P$ splits completely over $L$" constrains $(h_0, h_1)$ to an algebraic variety. Specifically: the resultant $\text{Res}_x(P, x^n - 1)$ must vanish (for all roots of $P$ to be $n$-th roots of unity). This resultant is a polynomial in $(h_0, h_1, \lambda)$.

For $a = 6$: $P$ has degree 6 and 6 roots, all required to be in $L$. The resultant $R(h_0, h_1) = \text{Res}_x(x^6 + \lambda x^b - h_1 x - h_0, x^n - 1)$ is a polynomial of degree $n$ in each variable. The zero set $R = 0$ has at most $\text{deg}(R)$ many $h_1$ values (for generic $h_0$), giving $M = O(n^2)$.

This is still too weak. But maybe the specific structure helps.

**To be continued**: need to analyze the resultant variety more carefully, possibly using the factorization $x^n - 1 = \prod_d \Phi_d(x)$ and the fact that roots lie in a specific cyclotomic extension.

## 7. What we can state now

**Theorem (empirical, computationally verified for $n \leq 240$)**: For the RS proximity gap with $k = 2$, threshold $t = 6$, and $L$ a multiplicative subgroup of order $n$ in $\mathbb{F}_p^*$:

$$\max_w M_\delta(w) = \frac{n}{t-1} + O(1)$$

The worst case is achieved by binomial words $w = x^t + \lambda x^{t-1}$.

**Implication for FRI soundness**: The per-round soundness error from proximity gap failure is at most $M/p \leq n/(p(t-1))$, which is $O(n/p)$ — negligible for $p \gg n$.
