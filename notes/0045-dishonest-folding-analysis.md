# Note 0045 — Dishonest Folding: Why Loss Kills the Query Phase

## BCHKS RBR Framework (from Block-Garreta-Tiwari-Zajac)

Total FRI soundness:
$$\varepsilon_{\text{FRI}} \leq d \cdot \frac{a}{|F|} + (1-\delta_{\text{eff}})^q$$

- $d$ = folding rounds = $\log_2(k)$
- $a$ = per-round proximity gap exceptions
- $\delta_{\text{eff}}$ = effective proximity at query phase
- $q$ = queries per round

## The compound-loss problem

| Round $i$ | BCHKS (zero loss) | Ours (loss δ/2) |
|-----------|-------------------|-----------------|
| δ_i | δ (constant) | δ/2^i (halving) |
| Commit error | O(n)/\|F\| | O(1)/\|F\| |
| Query catch prob | 1-(1-δ)^q | 1-(1-δ/2^i)^q |

At round $i = \log_2(q\delta) \approx 6$: query catch probability → 0 for us.

## Dishonest prover's optimal strategy

1. **Rounds 0 to ~6**: fold honestly (consistency check is strong)
2. **Round 7+**: switch to sending codewords (consistency check is weak)

Result: prover survives with probability ≈ $\prod_{i=7}^{R}(1-\delta/2^i)^q \approx 0.8$ for $q=128$.

## Quantitative comparison

For BabyBear ($|F|=2^{31}$, $n=2^{20}$, $R=20$, $q=128$, $δ=0.4$):

**BCHKS**: $\varepsilon = 20 \cdot 2^{20}/2^{31} + (0.6)^{128} = 2^{-7} + 2^{-95} \approx 2^{-7}$

**Ours (dishonest)**: $\varepsilon \approx 20/2^{31} + \prod_{i=0}^{19}(1-0.4/2^i)^{128}$
- Commit: $2^{-27}$ (good)
- Query: $\approx 0.8$ (terrible)
- Total: $\approx 0.8$ (WORSE than BCHKS)

**Ours (honest)**: $\varepsilon \leq R/|F| = 20/2^{31} \approx 2^{-27}$ (good, via SZ)

## Conclusion

The halved-threshold trick improves the commit phase but degrades the query phase. For dishonest folding: net effect is negative. For honest folding: the SZ argument bypasses the query phase entirely.

## Paths to fix dishonest folding

### Path 1: Zero-loss CA above Johnson
Would give $\delta_{\text{eff}} = \delta$ at all rounds. Blocked by borderline barrier.

### Path 2: New composition beyond RBR
Instead of tracking per-round doomed states, analyze the ENTIRE FRI transcript algebraically. The SZ argument for honest folding does this — can it be extended to dishonest?

### Path 3: Hybrid BCHKS + halved threshold
Use BCHKS (zero loss, O(n) exceptions) for the query phase, and our result for a DIFFERENT purpose (e.g., bounding the number of "plausible" dishonest folds).

### Path 4: Accept the cost, increase q
With $q = O(2^R/\delta)$: the query phase works. But $q \approx 2.5M$ — impractical.
