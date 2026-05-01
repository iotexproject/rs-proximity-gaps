# Note 0037 — The Final Truth

## The adversarial construction that defeats O(1)/|F| MCA

Choose: $g_2 \in C$, $e$ sparse with $|E| = \delta n$, $f_2 = g_2 + e$.
Choose: $u_1 \in C$, $e_1$ with $\text{supp}(e_1) \supset E$, $|\text{supp}(e_1) \setminus E| = 1$, and $\phi = e_1/e$ injective on $E$.
Set: $f_1 = u_1 + e_1$. Then $\Delta(f_1, C) = \delta + 1/n$ (borderline).

For each $\gamma \in \text{range}(\phi)$ ($\approx \delta n$ values):
- Agreement set $S_\gamma$ has size exactly $t$ (barely sufficient)
- On $S_\gamma$: $(f_1, f_2)$ is NOT interleaved (one point of disagreement forced)
- MCA IS violated

Result: $V = \delta n$ violations. $\epsilon_{\text{mca}} = \delta n / |F| = O(n/|F|)$.

**This matches BCHKS. Our approach does NOT beat the O(n/|F|) bound for worst-case MCA.**

## What our approach DOES give (still novel)

1. **f2-far case**: $\epsilon_{\text{ca}} \leq O(1)/|F|$ with zero loss. Novel, all $k$, any domain.
2. **f2-close, f1-far (> 2δ)**: $V = 0$. Novel.
3. **f2-close, f1-close (≤ δ)**: $V = 0$. Novel.
4. **k=2 list-size** $= O(1)$ above Johnson. Novel.
5. **Structural theory**: coset extraction, norm mechanism, power-of-2 optimality.
6. **DFT framework** connecting proximity gaps to sequence theory.

## What we CANNOT give

- **Worst-case MCA** $= O(1)/|F|$: IMPOSSIBLE by the borderline construction.
- **General-k list-size** $= O(1)$: SZ fails for dim $= k$.
- **Zero-loss CA above Johnson**: same barrier.

## Revised honest assessment

The puzzle's Grand Challenges are NOT fully solvable by volume packing + coset extraction alone. The borderline adversary ($\Delta(f_1,C) = \delta + \epsilon$) creates $O(\delta/\epsilon)$ MCA violations, which is UNBOUNDED.

**To beat O(n/|F|)**: need a fundamentally different technique that handles the borderline case. This is where character sums / Weil bounds on rational function level-sets COULD help — but only if the level-set distribution of the error ratio $e_1/e$ can be bounded by something sharper than pigeonhole.

**The specific technical question for Gong/Helleseth**: 

> For $e_1, e: L \to F_p$ with $\text{wt}(e) \leq \delta n$ and $\text{wt}(e_1) \leq (\delta+\epsilon)n$, and $\phi = e_1/e$ on $E = \text{supp}(e)$: is $\max_\gamma |\phi^{-1}(\gamma)| = O(1)$?

Answer: NO (the adversary can make $\phi$ arbitrary on $E$, including constant or injective). The level-set structure is adversary-controlled.

## What IS publishable

A paper with:
1. Theorem: $\epsilon_{\text{ca}}(C, \delta, 2\delta) \leq O(1)/|F|$ above Johnson, all $k$ (loss $\delta$)
2. Theorem: $M = O(1)$ for $k = 2$ above Johnson (SZ + coset extraction)  
3. Theorem: $M = O(1)$ for power-of-2 domains, $k = 2$, even $t$ ($\gcd$ argument)
4. The DFT framework + coset extraction technique
5. Computational evidence for scaling laws

This is genuinely novel — first results above Johnson for plain RS — and publishable in top venues. But it does not fully resolve the Grand Challenges.

## Distance to $1M (final, honest)

**50-60%.** We have novel partial results. The full resolution requires beating the O(n/|F|) MCA barrier, which our tools cannot do. The borderline adversary is a FUNDAMENTAL OBSTRUCTION, not a proof artifact.
