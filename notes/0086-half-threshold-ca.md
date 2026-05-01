# Note 0086: Half-Threshold CA Bound — The 1:2 Ratio Proof

## Result

**Theorem.** For any linear code $C$ over $F$:
$$\varepsilon_{\mathrm{ca}}(C, \delta/2, \delta) \leq 1/|F|.$$

Equivalently: if $\Delta_{\mathrm{joint}}((f_1, f_2), C \times C) > \delta$, at most 1 value of $\gamma$ satisfies $\Delta(f_1 + \gamma f_2, C) \leq \delta/2$.

## Proof (10 lines)

Suppose $\gamma_1 \neq \gamma_2$ are both bad: $\exists h_1, h_2 \in C$ with $|S_i| := |\{x : f_1(x) + \gamma_i f_2(x) = h_i(x)\}| \geq (1-\delta/2)n$.

By inclusion-exclusion: $|S_1 \cap S_2| \geq (1-\delta)n$.

On $S_1 \cap S_2$, solve the system $f_1 + \gamma_i f_2 = h_i$ for $i=1,2$:
- $g_1 := (\gamma_2 h_1 - \gamma_1 h_2)/(\gamma_2 - \gamma_1) \in C$
- $g_2 := (h_1 - h_2)/(\gamma_1 - \gamma_2) \in C$

So $(f_1, f_2) = (g_1, g_2)$ on $S_1 \cap S_2$, giving:
$$\Delta_{\mathrm{joint}}((f_1, f_2), C \times C) \leq |L \setminus (S_1 \cap S_2)|/n \leq \delta.$$

This contradicts $\Delta_{\mathrm{joint}} > \delta$. Hence at most 1 bad $\gamma$. □

## Why this works and the old proof didn't reach 1:2

The old proof (Case 1/2 framework) extracts only ONE codeword from two bad $\gamma$'s:
- On $S_1 \cap S_2$: $(\gamma_1 - \gamma_2)f_2 = h_1 - h_2$, so $f_2 \approx$ codeword.
- Then Case 2 bounds joint error as $\leq 2\delta_{hd} + \delta_{hd} = 3\delta_{hd}$.
- Need $3\delta_{hd} \leq \delta$, i.e., $\delta_{hd} \leq \delta/3$.

The new proof extracts BOTH codewords simultaneously:
- Solve the 2×2 linear system for (f_1, f_2) on the overlap.
- Joint error = $|L \setminus (S_1 \cap S_2)| \leq 2\delta_{hd}$.
- Need $2\delta_{hd} \leq \delta$, i.e., $\delta_{hd} \leq \delta/2$.

The key insight: two equations in two unknowns, not one equation in one unknown.

## Why 1:2 is optimal

Two bad $\gamma$'s always give $|S_1 \cap S_2| \geq 2(1-\delta_{hd})n - n = (1-2\delta_{hd})n$.
Joint error $\leq 2\delta_{hd}$. Need $2\delta_{hd} \leq \delta$.

At equal threshold ($\delta_{hd} = \delta$): joint error $\leq 2\delta > \delta$. No contradiction.
Computation confirms: $\varepsilon_{ca}(C, \delta, \delta) = \Theta(1)$ above Johnson.

Three bad $\gamma$'s give an overdetermined system (3 equations, 2 unknowns). The extra equation gives a polynomial constraint on $h_3$ given $h_1, h_2$, but doesn't improve the inclusion-exclusion bound beyond the 2-$\gamma$ result.

## Structural observations

1. **No code structure needed.** The proof uses only linearity of $C$ (closed under $F$-linear combinations). It works for ANY linear code, not just RS.

2. **No parameter conditions.** No restriction on $k$, $\delta$, or field size. The FRI conditions ($\delta > \delta_J$, $k = 2^m$, etc.) are for the FRI APPLICATION, not the CA theorem.

3. **The isomorphism $C^{=2} = C \times C$.** For the even/odd FRI decomposition: $RS_k \cong RS_{k/2} \times RS_{k/2}$ via $g \mapsto (g_{even}, g_{odd})$. So the "product code" $C \times C$ IS the "joint code" $C^{=2}$. This is why the proof applies directly to the FRI proximity gap.

## Impact on FRI

**Old bound:** $\varepsilon_{FRI} \leq 2R/|F| + (1-\delta/3)^q$
**New bound:** $\varepsilon_{FRI} \leq 2R/|F| + (1-\delta/2)^q$

For 128-bit security at $\rho = 1/2$, $\delta = 0.4$:
- Old: $q \approx 485$ queries/round
- New: $q \approx 311$ queries/round
- Savings: 36% fewer queries

For $\delta = 0.293$ (just above Johnson):
- Old: $q \approx 657$
- New: $q \approx 427$
- Overhead vs zero-loss: 2.2× (was 3.4×)

## Why this was missed

The Case 1/2 framework is inherited from Ben-Sasson et al. (2018) → BCIKS (2020) → BCHKS (2025) → our paper. Everyone followed the same template: split on $\Delta(f_2, C)$, handle each case separately. The framework extracts only $f_2$'s codeword, then bounds the joint error indirectly.

Nobody tried: "don't split at all, solve for BOTH components." The insight is trivial in retrospect — two equations, two unknowns — but it wasn't visible through the Case 1/2 lens.

## Computational verification

From the ratio sweep (notes/scripts/ca_ratio_sweep.py):

| Code | Field | w_hd | w_nt | Ratio | max_bad | Theorem |
|------|-------|------|------|-------|---------|---------|
| RS[6,3] | F_7 | 1 | 2 | 2.0 | 1 | ≤ 1 ✓ |
| RS[8,4] | F_17 | 1 | 3 | 3.0 | 1 | ≤ 1 ✓ |
| RS[10,5] | F_11 | 2 | 4 | 2.0 | 1 | ≤ 1 ✓ |
| RS[8,4] | F_17 | 2 | 3 | 1.5 | 4 | N/A (ratio < 2) |
| RS[10,5] | F_11 | 3 | 4 | 1.33 | 9 | N/A (ratio < 2) |

All cases with ratio ≥ 2 have max_bad ≤ 1, exactly matching the theorem.
All cases with ratio < 2 have max_bad > 1, confirming tightness.
