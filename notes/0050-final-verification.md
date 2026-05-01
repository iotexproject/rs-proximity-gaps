# Note 0050 — Final Verification: k-parity fix and completeness check

## The k-parity bug and fix

**Bug**: For k odd, $x^k \notin \text{RS}_k$ but $f^{(1)} \in \text{RS}_{\lceil k/2 \rceil}$ for ALL $\alpha$. FRI accepts with prob 1.

**Root cause**: $\text{RS}_{\lceil k/2 \rceil}^{=2}$ has dim $k+1 > k = \dim(\text{RS}_k)$ for odd $k$. The even/odd map is NOT surjective → "fake pairs" exist.

**Fix**: Require k even at each round. For k even: $\text{RS}_{k/2}^{=2} \cong \text{RS}_k$ via even/odd (dimensions both = k). Coupling is exact.

**FRI standard**: $k = 2^m$, halves each round: $2^m, 2^{m-1}, \ldots, 2, 1$. All even except last round ($k=1$, handled by direct check). ✅

## Verification of each step for k = 2^m

### [5] Halved-threshold CA

Claim: $\varepsilon_{\text{ca}}(C, \delta/2, \delta) \leq \lceil n/t' \rceil / |F|$.

- Case 1 (f₂ far): packing on overlaps. Uses only: codeword differences have degree < k < t'. ✅
- Case 2 (f₂ close): error support identity on $S_\gamma$. Uses only: algebra of $e_1 = -\gamma e_2$. ✅
- Joint distance: $\leq |E_2| + |L \setminus S_\gamma| \leq \delta n$. Uses only: sizes. ✅

**No dependence on k-parity.** This theorem holds for ALL k. ✅

### [6] FRI coupling (k even)

Claim: $\Delta(f, \text{RS}_k) \leq \Delta_{\text{joint}}((f_{\text{even}}, f_{\text{odd}}), \text{RS}_{k/2}^{=2})$.

For k even: the map $g \mapsto (g_{\text{even}}, g_{\text{odd}})$ is an isomorphism $\text{RS}_k \to \text{RS}_{k/2}^{=2}$.

Proof of isomorphism: $g = \sum_{j=0}^{k-1} a_j x^j$ maps to $(g_{\text{even}}, g_{\text{odd}})$ where $g_{\text{even}} = \sum_{m=0}^{k/2-1} a_{2m} y^m$ and $g_{\text{odd}} = \sum_{m=0}^{k/2-1} a_{2m+1} y^m$. Both have degree $< k/2$. The map sends $(a_0, \ldots, a_{k-1})$ to $((a_0, a_2, \ldots), (a_1, a_3, \ldots))$. This is a permutation of coordinates → bijection. ✅

With the isomorphism: every $(g_1, g_2) \in \text{RS}_{k/2}^{=2}$ corresponds to a unique $g \in \text{RS}_k$. The coset counting argument: $c_y \geq 1 \implies$ joint error. So $\Delta(f,g) \leq \Delta_{\text{joint}}$. Taking min: ✅

### [3] Per-round proximity gap

Combines [5] and [6]: $\Delta_{\text{joint}} \geq \Delta(f) > \delta > \delta/2$. All $(\delta/2)$-close $\alpha$ are CA violations. Count $\leq 3$. ✅

### [2] SZ for honest folding (k = 2^m)

Claim: $\Pr[f^{(R)} \in \text{RS}_{k/2^R}] \leq R/|F|$.

Proof by induction: for k even, $f \notin \text{RS}_k \implies f_{\text{even}} \notin \text{RS}_{k/2}$ or $f_{\text{odd}} \notin \text{RS}_{k/2}$ (by isomorphism). So the syndrome of $f^{(1)} = f_{\text{even}} + \alpha_1 f_{\text{odd}}$ is a degree-$\leq 1$ nonzero polynomial in $\alpha_1$. Continuing inductively: $f^{(R)}$ has syndrome of degree $\leq R$ in $(\alpha_1, \ldots, \alpha_R)$, nonzero. SZ: $\leq R/|F|$. ✅

### [4] Consistency check

Standard probability. No dependence on k-parity. ✅

### Composition

Case A (honest): $R/|F|$ by [2].
Case B (dishonest at one round): $3R/|F| + (1-\delta/2)^q$ by [3] + [4].
Total: $\leq 3R/|F| + (1-\delta/2)^q$. ✅

## FINAL THEOREM

For $\text{RS}[\mathbb{F}_p, L, k]$ with $k = 2^m$, $L$ closed under negation, $|L| = n$, $\delta_J < \delta < 1-\rho$:

$$\Pr[\text{FRI accepts} \mid \Delta(f^{(0)}, \text{RS}_k) > \delta] \leq \frac{3R}{|F|} + (1-\delta/2)^q$$

where $R = m = \log_2 k$ rounds, $q$ queries per round.

For BabyBear ($|F| = 2^{31}$, $R = 20$, $q = 128$, $\delta = 0.35$):

$$\varepsilon \leq \frac{60}{2^{31}} + (0.825)^{128} \approx 2^{-26} + 2^{-35} \approx 2^{-26}$$

**26 bits of security.** BCHKS at Johnson: $20 \cdot 2^{20} / 2^{31} \approx 2^{-7}$ (7 bits). **Improvement: 19 bits.**
