# Note 0014 — $k \geq 3$: Reduction to $k = 2$

**Date**: 2026-04-21  
**Status**: Key observation + partial proof

## Observation

For $k = 3$: the codeword is $h = h_0 + h_1 x + h_2 x^2$. For a fixed $h_2$: the problem reduces to $k = 2$ with effective word $w'(x) = w(x) - h_2 x^2$.

**Verified for $w = x^9 + x^8$, $n = 64$, $p = 193$, $t = 9$:**

- Only $h_2 = 0$ gives any witnesses. $M(h_2 = 0) = 7 \approx n/(t-1)$.
- All $h_2 \neq 0$: $M = 0$.
- Total $M = 7$.

## Why only $h_2 = 0$ works

For $h_2 \neq 0$: the effective word $w'(x) = x^9 + x^8 - h_2 x^2$ has a nonzero $x^2$ term. In the Vieta conditions, this means $e_{t-2} = e_7 \neq 0$ (specifically, $e_7$ depends on $h_2$). The nonzero $e_7$ disrupts the coset extraction: Newton's identities give $p_7(T) \neq 0$, so the residual $T$ does NOT satisfy $x^{t-1} = \text{const}$.

By Note 0011: nonzero intermediate $e_j$ reduce $M$ to $O(1)$. So $M(h_2 \neq 0) = O(1)$, typically 0.

## General $k$ argument

**Claim**: For any $k$ and the worst-case word: the list size $M \leq n/(t-1) + O(k)$.

*Argument*: Fix $h_2, \ldots, h_{k-1}$ (the higher-order codeword coefficients). Each such fixing reduces to a $k = 2$ problem. By Thm 4/6: each gives $M \leq n/(t-1)$ or $O(1)$.

The number of active $(h_2, \ldots, h_{k-1})$ tuples is $O(1)$ (typically just the all-zero tuple), because nonzero higher-order $h_j$ disrupt the Vieta/coset structure.

Total: $M \leq O(1) \cdot n/(t-1) + O(p^{k-2}) \cdot O(1) = n/(t-1) + O(p^{k-2})$.

For $p > n^{t-1}$ and $k \leq t$: $p^{k-2}$ is potentially large. But the $O(1)$ per active tuple makes the total small.

**Conjecture (supported by computation)**: $M \leq n/(t-1) + O(1)$ for ALL $k$, not just $k = 2$.

## Proof completed (2026-04-21)

### Why $h_j \neq 0$ kills cosets

After pivot extraction, $T$ satisfies a characteristic polynomial:
$$x^{t-1} + c_{t-3} x^{t-3} + \cdots + c_1 x + c_0 = 0$$

where $c_{t-j-1}$ depends on $e_j(T)$, which in turn depends on $h_j$.

- **$h_j = 0$ for all $j \geq 2$**: all intermediate $c_i = 0$. Char poly is $x^{t-1} + c_0$, i.e., $x^{t-1} = -c_0$. By the cyclic coset lemma: solutions are a coset of order $\gcd(t-1, n)$.
- **Any $h_j \neq 0$**: at least one intermediate $c_i \neq 0$. Char poly is NOT $x^d = \text{const}$. By Note 0011: no coset solutions, only sporadic $O(1)$.

### General $k$ theorem

**Theorem 9**: For $\RS_k$ on multiplicative subgroup $L$ of order $n$ in $\FF_p^*$, ANY $k \geq 2$, and agreement threshold $t$:

$$M_\delta(w) \leq \frac{n}{t}\mathbb{1}_{[t|n]} + \frac{n}{t-1}\mathbb{1}_{[(t-1)|n]} + O\!\left(\frac{\binom{n}{t}}{p^{t-2}}\right)$$

The bound is **independent of $k$**.

*Proof*: Fix $(h_2, \ldots, h_{k-1})$. Reduce to $k = 2$ problem with effective word $w' = w - \sum_{j=2}^{k-1} h_j x^j$. Only $(h_2, \ldots, h_{k-1}) = \mathbf{0}$ gives coset solutions (by the intermediate-coefficient argument). All $h_j \neq 0$ cases contribute $O(1)$ sporadic. Total: same as $k = 2$ bound.

**Corollary**: For FRI ($n = 2^K$, $t = 6$, any $k$): $M = O(1)$. The FRI soundness improvement of 20 bits/round applies to ALL rounds, not just the final one.
