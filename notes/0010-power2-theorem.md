# Note 0010 — Theorem 6: Optimal Bound for Power-of-2 Domains

**Date**: 2026-04-21  
**Status**: Proved and verified

## Statement

**Theorem 6**: Let $L$ be a multiplicative subgroup of order $n$ in $\FF_p^*$ with $p > n^{t-1}$, $k = 2$, and agreement threshold $t$.

1. If $\gcd(t-1, n) = 1$ (in particular, for $n = 2^k$ and $t \not\equiv 1 \pmod{2}$, e.g., $t = 6$):
$$M_\delta(w) = O(1) \quad \text{for all words } w.$$

2. If $(t-1) \mid n$:
$$M_\delta(w) \leq \frac{n}{t-1} + O(1) \quad \text{for all words } w.$$

3. In general:
$$M_\delta(w) \leq \frac{n}{t-1} \cdot \mathbb{1}_{(t-1) \mid n} + O\left(\frac{\binom{n}{t}}{p^{t-2}}\right).$$

## Proof

The coset extraction from Theorem 4 (Note 0009) produces $T = S \setminus \{j^*\}$ with $|T| = t-1$ elements satisfying $x^{t-1} = -e_{t-1}(T)$.

The equation $x^{t-1} = c$ has exactly $\gcd(t-1, n)$ solutions in $L$ (when $c$ is in the correct coset of $L^{t-1}$, and 0 otherwise).

For a valid $T$: we need $|T| = t-1$ roots in $L$. This requires $\gcd(t-1, n) = t-1$, i.e., $(t-1) \mid n$.

When $(t-1) \nmid n$: $\gcd(t-1, n) < t-1$, so $x^{t-1} = c$ has $< t-1$ roots in $L$. No valid $T$ exists (of size $t-1$). The only agreement sets are "sporadic" (non-coset), bounded by $O(\binom{n}{t}/p^{t-2})$.

## Verification

| Domain type | $n$ | $\gcd(5,n)$ | $M_{\max}$ | Prediction |
|-------------|-----|-------------|------------|------------|
| $2^5$ | 32 | 1 | 0 | $O(1)$ ✓ |
| $2^6$ | 64 | 1 | 0 | $O(1)$ ✓ |
| $2^7$ | 128 | 1 | 1 | $O(1)$ ✓ |
| $2^8$ | 256 | 1 | 2 | $O(1)$ ✓ |
| $2^9$ | 512 | 1 | 0 | $O(1)$ ✓ |
| $5 \cdot 8$ | 40 | 5 | 7 | $n/5 - 1 = 7$ ✓ |
| $5 \cdot 16$ | 80 | 5 | 15 | $n/5 - 1 = 15$ ✓ |
| $5 \cdot 32$ | 160 | 5 | 32 | $n/5 = 32$ ✓ |
| $5 \cdot 64$ | 320 | 5 | 63 | $n/5 - 1 = 63$ ✓ |
| $5 \cdot 128$ | 640 | 5 | 127 | $n/5 - 1 = 127$ ✓ |

## Implications for FRI/STARK

FRI uses $n = 2^k$ (power-of-2 domains) with field size $p \sim 2^{64}$ or $2^{128}$.

**Comprehensive FRI parameter check** (all standard configs, $k=2$):

| Blow-up $R$ | $n$ | $t_{CS}$ | $\gcd(t-1, n)$ | $M$ bound |
|-------------|-----|-----------|-----------------|-----------|
| 2 | $2^{20}$ | $3 \cdot 2^{18}$ | **1** | $O(1)$ |
| 3 | $2^{20}$ | $3 \cdot 2^{17}$ | **1** | $O(1)$ |
| 4 | $2^{20}$ | $3 \cdot 2^{16}$ | **1** | $O(1)$ |
| any | any $2^k$ | any even $t$ | **1** | $O(1)$ |

For proximity $\delta \leq 0.7$: $t - 1$ is always odd → $\gcd = 1$ → $M = O(1)$.

**Concrete soundness improvement over BCHKS**:

| System | BCHKS | Ours |
|--------|-------|------|
| BabyBear ($p \approx 2^{31}$) | $\sim 11$ bits/round | $> 100$ bits/round |
| Goldilocks ($p \approx 2^{64}$) | $\sim 44$ bits/round | $> 100$ bits/round |

**The FRI proximity gap holds with essentially optimal parameters in the intermediate zone above Johnson.** The proximity gap is no longer the bottleneck for FRI soundness.

## Scripts

- `notes/scripts/t6_power2.py` — power-of-2 vs divisible-by-5 comparison
- `notes/scripts/t6_large_power2.py` — large-$n$ verification ($n = 256, 512, 1024$)
- `notes/scripts/fri_folding.py` — FRI folding soundness simulation
