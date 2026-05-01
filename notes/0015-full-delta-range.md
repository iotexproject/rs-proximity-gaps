# Note 0015 — Full δ-Range Proximity Gap Theorem

**Date**: 2026-04-21  
**Status**: Theorem formulated; partial verification

## Main theorem

**Theorem 8** (Proximity Gap for Multiplicative Subgroups): Let $L \subset \FF_p^*$ be a multiplicative subgroup of order $n$, $\RS_k$ the RS code with $k = 2$, and $\delta = 1 - t/n$ the proximity parameter for integer $t \geq 3$.

For any word $w \in \FF_p^n$, the list size satisfies:

$$M_\delta(w) \leq \frac{n}{t} \cdot \mathbb{1}_{[t \mid n]} + \frac{n}{t-1} \cdot \mathbb{1}_{[(t-1) \mid n]} + O\!\left(\frac{\binom{n}{t}}{p^{t-2}}\right).$$

The three terms correspond to:
1. **Monomial term** ($e_1 = 0$, word $w = x^t$): subgroup-cosets of order $t$, count $n/t$.
2. **Binomial term** ($e_1 \neq 0$, word $w = x^t + \lambda x^{t-1}$): pivot-extracted cosets of order $t-1$, count $n/(t-1)$.
3. **Sporadic**: non-coset solutions, bounded by cyclotomic norms.

## Specializations

### Power-of-2 domains ($n = 2^k$)

For even $t$: $t - 1$ is odd, $\gcd(t-1, 2^k) = 1$. So $M = O(\binom{n}{t}/p^{t-2})$.

| $t$ | Sporadics $\binom{n}{t}/p^{t-2}$ at $n = 2^{20}$, $p = 2^{31}$ | $M$ |
|-----|----------------------------------------------------------------|-----|
| 4 | $\binom{2^{20}}{4}/2^{62} \approx 2^{18}$ | **Not O(1)!** |
| 6 | $\binom{2^{20}}{6}/2^{124} \approx 2^{-14}$ | $O(1)$ ✓ |
| 8 | $\binom{2^{20}}{8}/2^{186} \approx 2^{-46}$ | $O(1)$ ✓ |
| 10 | $\binom{2^{20}}{10}/2^{248} \approx 2^{-78}$ | $O(1)$ ✓ |

**Observation**: For $t = 4$ on BabyBear native field: sporadic term is $O(2^{18})$, NOT negligible! Need extension field ($p^4 \approx 2^{124}$) or larger native $p$ (Goldilocks).

For $t \geq 6$ on BabyBear: sporadic is negligible. $M = O(1)$.

### FRI proximity at standard parameters

FRI operates at $\delta \approx 1 - \rho$ where $\rho = k/n$ is the rate. The agreement threshold is $t \approx (1-\rho) n$.

For rate $\rho = 1/2^R$ (blow-up $R$):
- $t = (1 - 1/2^R) n = n(2^R - 1)/2^R$
- For $n = 2^K$: $t = 2^K(2^R - 1)/2^R = 2^{K-R}(2^R - 1)$
- $t - 1 = 2^{K-R}(2^R - 1) - 1$

For $R \geq 2$: $2^R - 1 \geq 3$ (odd), so $t = 2^{K-R} \cdot \text{odd}$. Then $t$ is even iff $K > R$, which is always true ($K \geq 16$, $R \leq 4$). So $t$ is even → $t - 1$ odd → $\gcd(t-1, n) = 1$ → $M = O(1)$.

**Result**: For ALL standard FRI parameters: $M = O(1)$ at the natural operating point.

## δ dependence: the "even/odd oscillation"

On power-of-2 domains, the list size oscillates:
- Even $t$ ($\delta$ slightly above certain values): $M = O(1)$
- Odd $t$: $M$ can be $O(n/2)$ (from $\gcd(t-1, n) \geq 2$)

This oscillation is a consequence of the power-of-2 structure and has no analogue for smooth-order domains.

**Practical implication**: FRI naturally operates at EVEN $t$ (since $t = (1-\rho)n$ and both $\rho n$ and $n$ are powers of 2, making $(1-\rho)n$ a multiple of 2). So FRI always hits the "good" even-$t$ case.

## Comparison with BCHKS

| Regime | BCHKS bound | Our bound (power-of-2) |
|--------|-------------|----------------------|
| Below Johnson ($t > \sqrt{2n}$) | $M \leq n/2$ with $O(n)$ exceptions | Same (our bound doesn't improve here) |
| At Johnson ($t = \sqrt{2n}$) | $M = O(n)$, $\Omega(n^{1.99})$ exceptions | Same (boundary case) |
| Above Johnson, even $t$ | **No bound** (vacuous) | **$M = O(1)$** ← NEW |
| Above Johnson, odd $t$ | **No bound** | $M \leq n/2 + O(\binom{n}{t}/p^{t-2})$ ← NEW |

## Open: can we remove the even/odd oscillation?

For odd $t$ on power-of-2 domains: $M$ could be $O(n)$ (from order-$2^{v_2(t-1)}$ cosets). Can we prove a UNIFORM bound $M = O(1)$ for ALL $t$ on power-of-2?

**Probably not**: the coset solutions genuinely exist when $\gcd(t-1, n) > 1$. The bound $M = n/\gcd(t-1,n)$ is TIGHT for the worst-case word.

But: FRI always uses even $t$ (see above), so the oscillation doesn't matter in practice.
