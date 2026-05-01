# Note 0046 — List Size for General k: Empirical Results

## Data Summary

### Rate 1/2, δ=0.35 (just above Johnson δ_J≈0.293)

| n | k | p | p/n | M_max | Expected (main term) |
|---|---|---|-----|-------|---------------------|
| 8 | 4 | 17 | 2.1 | 5 | ~1 |
| 12 | 6 | 13 | 1.1 | **51** | ~2 |
| 16 | 8 | 17 | 1.1 | **29** | ~0.3 |
| 20 | 10 | 41 | 2.1 | 2 | ~10^{-4} |

### Rate 1/4, δ=0.55 (above Johnson δ_J=0.5)

| n | k | p | p/n | M_max |
|---|---|---|-----|-------|
| 8 | 2 | 17 | 2.1 | 5 |
| 12 | 3 | 13 | 1.1 | 5 |
| 16 | 4 | 17 | 1.1 | 3 |

### Rate 1/2, δ=0.45 (deep in intermediate zone, near capacity 0.5)

| n | k | p | p/n | M_max |
|---|---|---|-----|-------|
| 8 | 4 | 17 | 2.1 | **66** |
| 12 | 6 | 13 | 1.1 | **654** |
| 16 | 8 | 17 | 1.1 | **8394+** |

## Key observation: M depends critically on p/n

For **small p/n** (p ≈ n): M can be hundreds or thousands. Error term in character sum dominates.

For **large p/n** (p ≫ n): M → 0. Main term exponentially small.

### Heuristic formula

$$M \approx \sum_{w=1}^{\delta n} \frac{\binom{n}{w}(p-1)^w}{p^{n-k}} \approx \frac{\binom{n}{\delta n} p^{\delta n}}{p^{n-k}} = \frac{\binom{n}{\delta n}}{p^{(1-\rho-\delta)n}}$$

For FRI: $p = 2^{31}$, $n = 2^{20}$, $\rho = 1/2$, $\delta = 0.35$:
$$M \approx 2^{0.97 \cdot 2^{20}} / 2^{31 \cdot 0.15 \cdot 2^{20}} = 2^{-3.68 \cdot 2^{20}} \approx 0$$

**For ALL practical FRI parameters: M = 0.** The list is empty.

## Implication

The list-decoding problem above Johnson for RS on multiplicative subgroups is TRIVIALLY solved when p ≫ n (the FRI regime). The "hard" regime is p ≈ n, which is NOT relevant for STARKs.

This means: the proximity gap question for FRI is NOT about list-decoding at all — it's about the CA/MCA framework and how loss compounds.

## What this changes

1. **The character-sum counting approach IS the right path** — but the goal is a RIGOROUS bound, not just heuristics.
2. **The bound must be uniform in w** (or at least handle all p and n).
3. **For the prize**: a rigorous proof that M = O(1) for p > n^C (some explicit constant C depending on ρ, δ) would be new and valuable.
