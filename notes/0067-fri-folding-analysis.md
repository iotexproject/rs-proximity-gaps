# Note 0067 — FRI Folding and List Size Reduction

## 1. Setup

For RS[n, k] on $L = \langle\omega\rangle \subset \mathbb{F}_p^*$ with $n$ even, rate $\rho = k/n$.

**FRI folding**: Decompose $f(x) = f_{\text{even}}(x^2) + x \cdot f_{\text{odd}}(x^2)$. For $\alpha \in \mathbb{F}_p^*$:

$$g_\alpha(y) = f_{\text{even}}(y) + \alpha \cdot f_{\text{odd}}(y), \quad y \in L' = L^2 = \langle\omega^2\rangle$$

**Important**: $g_\alpha \in \text{RS}_{\lceil k/2 \rceil}$ on $L'$ (NOT $\text{RS}_{\lfloor k/2 \rfloor}$).

For even $k$: both parts have $k/2$ coefficients — no issue.
For odd $k$: $f_{\text{even}}$ has $\lceil k/2 \rceil$ coefficients (indices $0, 2, \ldots, k-1$),
$f_{\text{odd}}$ has $\lfloor k/2 \rfloor$ coefficients (indices $1, 3, \ldots, k-2$).

## 2. Error Image Under Squaring

For codeword $c$ at distance $d$ from $f$: error set $E = \{i : f(\omega^i) \neq c(\omega^i)\}$, $|E| = d$.

The squaring map $\pi: \mathbb{Z}/n\mathbb{Z} \to \mathbb{Z}/(n/2)\mathbb{Z}$, $i \mapsto i \bmod n/2$
sends each pair $\{i, i + n/2\}$ to the same point.

**Error image**: $E' = \pi(E) \subseteq [n/2]$.
- $|E'| = d - t$ where $t = |\{i \in E : i + n/2 \in E\}|/2$ (number of complete pairs).
- $\lceil d/2 \rceil \leq |E'| \leq d$.
- $t \leq \lfloor d/2 \rfloor$.

## 3. Folded Error Analysis

For position $y = \omega^{2j} \in L'$ with preimages $x_1 = \omega^j$ and $x_2 = \omega^{j+n/2}$:

$$e_E(y) = \frac{e(x_1) + e(x_2)}{2}, \quad e_O(y) = \frac{e(x_1) - e(x_2)}{2\omega^j}$$

Folded error: $e_{\text{fold}}(y) = e_E(y) + \alpha \cdot e_O(y)$.

**Case analysis at position $y$**:
1. Neither $x_1$ nor $x_2$ in $E$: $e_E = e_O = 0$, no error.
2. Only $x_1 \in E$ (unpaired): $e_E = e/2$, $e_O = e/(2\omega^j)$.
   Cancels at $\alpha = -\omega^j$. (One specific $\alpha$.)
3. Both $x_1, x_2 \in E$ (paired), $e(x_1) = e(x_2)$: $e_O = 0$, always error.
4. Both paired, $e(x_1) \neq e(x_2)$: $e_O \neq 0$, cancels at $\alpha = -e_E/e_O$.

**Folded distance**: $d_{\text{fold}}(\alpha) = |E'| - |\{y \in E' : \text{cancel at } \alpha\}|$.

For random $\alpha$: expected cancellations $\approx |E'|/(p-1)$. So $d_{\text{fold}} \approx |E'|$ for $p \gg 1$.

## 4. Survival Condition

Johnson radius for folded code RS[$n/2, \lceil k/2 \rceil$]:
$$w' = \lfloor n/2 - \sqrt{(n/2)(\lceil k/2 \rceil - 1)} \rfloor$$

Codeword $c$ survives folding at $\alpha$ iff $d_{\text{fold}}(\alpha) \leq w'$.

Need at least $r = |E'| - w'$ cancellations. Each cancellation happens at one specific $\alpha$.

**Survival probability**: $P[\text{survive}] \approx \binom{|E'|}{r} / (p-1)^r$ for random $\alpha$.

- $r = 0$ (fully paired, $|E'| \leq w'$): survives for ALL $\alpha$.
- $r = 1$: survives for $\sim |E'|/(p-1)$ fraction.
- $r \geq 2$: survives for $\sim O(p^{-r})$ fraction (negligible).

## 5. Empirical Results

| $n$ | $k$ | $p$ | $w$ | $M$ | $k'$ | $w'$ | max $M'$ | typical chain |
|-----|-----|-----|-----|-----|-------|------|-----------|---------------|
| 12  | 6   | 13  | 4   | 5   | 3     | 2    | 2         | [5,≤2,≤2]     |
| 14  | 7   | 29  | 5   | 7   | 4     | 2    | 1         | [7,0]         |
| 16  | 8   | 17  | 5   | 3   | 4     | 3    | 1         | [3,≤1,≤1,0]  |

**Error pairing data (n=14, M=7)**:
- cw0: $|E'|=5$, need 3 cancellations → survive 0/28
- cw1–cw6: $|E'|=4$, need 2 cancellations → survive 0–1/28
- Only 1 out of 28 alphas has ANY surviving codeword

**Folded list vs original list**: Independent computation confirms $M_{\text{fold}}(g_\alpha) = |\text{survivors}|$. No "new" codewords appear in the folded list that weren't in the original list.

## 6. Theoretical Analysis

### What folding proves

For a random $\alpha \in \mathbb{F}_p \setminus L$:
1. The folding map $\varphi_\alpha: \text{RS}_k \to \text{RS}_{k'}$ is injective on the list (probability $\geq 1 - M^2 k / p$).
2. Surviving codewords map injectively to the folded list.
3. $|\text{survivors}| \leq M(\text{RS}_{k'}, g_\alpha, w')$.

### What folding does NOT prove

The total list size $M$ is NOT bounded by folding alone:
$$M = |\text{survivors}| + |\text{non-survivors}|$$
Folding bounds $|\text{survivors}| \leq M'$, but $|\text{non-survivors}|$ is unconstrained.

### The lifting argument (attempted)

Each codeword $h$ in the folded list lifts to a coset of $\ker(\varphi_\alpha)$ in $\text{RS}_k$.

$\ker(\varphi_\alpha) = \{(x - \alpha) q(x^2) : q \in \text{RS}_{\lfloor k/2 \rfloor}\}$

This is a $\lfloor k/2 \rfloor$-dimensional code with minimum distance $\geq n - k + 2$ (for $\alpha \notin L$).

The number of lifts of $h$ close to $f$ (list-decoding $\ker(\varphi_\alpha)$ at radius $w$) is bounded by the packing argument:

$$M_{\text{lift}} \leq \frac{d_C - w}{(n-w)^2/n - (n - d_C)} \approx \frac{n}{4}$$

This gives $M \leq M' \times M_{\text{lift}} = O(1) \times O(n) = O(n)$. **Not useful.**

### Why the packing bound degenerates (again)

For $d_C = n - k + 2$ and $w \approx (1-\sqrt\rho)n$ at rate $\rho = 1/2$:

$(n-w)^2/n - (n - d_C) = 0.5n - (n/2 - 2) = 2$

The denominator is a constant (≈2), making the bound O(n). This is the same packing degeneracy as in Note 0066 §5.

## 7. Structural Discovery: Error Pairing Constraint

The most important finding: **FRI folding imposes a STRUCTURAL constraint on error sets**.

For a codeword to survive $R$ rounds of folding, its error set $E$ must be closed under the subgroup $\langle n/2^R \rangle$ of $\mathbb{Z}/n\mathbb{Z}$. After $\log_2 n$ rounds: $E = \emptyset$ or $E = \mathbb{Z}/n\mathbb{Z}$, forcing $M = 0$.

This means: the error sets of all codewords in the list are "unstable" under folding — they're destroyed by the squaring map. This structural instability is a property of the MULTIPLICATIVE SUBGROUP evaluation domain $L$ (it wouldn't hold for random evaluation points).

**Conjecture**: The instability of error sets under squaring is the key mechanism that keeps $M = O(1)$ for RS on multiplicative subgroups.

## 8. What's Needed

The FRI folding approach identifies the RIGHT structural constraint but can't close the proof. The gap:

1. Folding bounds survivors: $|\text{survivors}| \leq M' = O(1)$ (by induction).
2. Non-survivors have "unstable" errors: $|E'| > w'$ (too many positions in $L'$).
3. **Missing**: a direct bound on the number of codewords with "unstable" error sets.

This "missing" bound requires understanding how the algebraic constraints of RS codes interact with the pairing structure of $L$. Specifically: how many degree-$< k$ polynomials can have exactly $d$ non-zero evaluations on $L$, with those evaluations concentrated on "unpaired" positions?

## Scripts

- `fri_folding_v3.py` — n=8,10 (too small for interesting M)
- `fri_folding_n12v2.py` — n=12, correct w=4, M=5
- `fri_folding_final.py` — n=12,14,16 (bug: used k//2 instead of ceil(k/2) for odd k)
- `fri_folding_fixed.py` — FIXED version with ceil(k/2)
- `fri_debug.py` — debug script verifying folding at n=14
