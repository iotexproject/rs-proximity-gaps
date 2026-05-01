# Note 0029 — P1 Result: MCA Proof Audit

## The $f_2$-close case is NOT trivial

When $\Delta(f_2, C) \leq \delta$: $f_2$ agrees with some $g_2 \in \text{RS}$ on $T \subset L$ with $|T| \geq t$.

For bad $\gamma$: $f_1 + \gamma f_2$ agrees with $h_\gamma$ on $S_\gamma$ with $|S_\gamma| \geq t$.

The overlap $|S_\gamma \cap T| \geq 2t - n = (1-2\delta)n$.

**Problem**: $2t - n < t$ for all $\delta > 0$. So the "interleaved structure" is verified on a set SMALLER than the MCA threshold $t$.

## But the MCA upper bound IS still valid

Our bound: $\Pr_\gamma[\Delta(f_1+\gamma f_2, C) \leq \delta] \leq \lceil n/t \rceil / |F|$.

This is a valid upper bound on $\epsilon_{\text{mca}}$ because:

$$\epsilon_{\text{mca}} = \Pr[\text{close AND not-interleaved}] \leq \Pr[\text{close}] \leq \lceil n/t \rceil / |F|$$

The first inequality is $\Pr[A \cap B] \leq \Pr[A]$. Trivial but correct.

## What's proven vs what's not

| Statement | Status |
|-----------|--------|
| $\Pr_\gamma[\Delta(f_1+\gamma f_2, C) \leq \delta] \leq \lceil n/t \rceil/\|F\|$ | **PROVED** (volume bound, $k$-independent) |
| $\epsilon_{\text{mca}} \leq \lceil n/t \rceil / \|F\|$ | **PROVED** (trivial upper bound from above) |
| When $f_2$ close: MCA trivially satisfied | **NOT PROVED** (overlap $< t$) |
| When $f_2$ close: the bad $\gamma$'s are "benign" | **NOT PROVED** |

## The volume bound proof (recap, airtight version)

For arbitrary $f_1, f_2 \in F^n$ and threshold $t$ with $k < t$:

**Step 1**: Define $B = \#\{\gamma \in F : \exists h_\gamma \in C, |S_\gamma| \geq t \text{ with } w_\gamma|_{S_\gamma} = h_\gamma|_{S_\gamma}\}$.

**Step 2**: For two bad $\gamma_1 \neq \gamma_2$: on $S_{\gamma_1} \cap S_{\gamma_2}$:
$$(\gamma_1 - \gamma_2) f_2(x) = h_{\gamma_1}(x) - h_{\gamma_2}(x)$$
The RHS is a polynomial of degree $< k$.

**Sub-case 2a**: $\Delta(f_2, C) > \delta$, i.e., $f_2$ agrees with any codeword on $< t$ points. Then the equation $(\gamma_1-\gamma_2)f_2(x) = (\text{deg-}< k)$ has $< t$ solutions in $L$ (since $f_2$ restricted to the solution set equals a degree-$< k$ polynomial, so the solution set has size $< t$ by the far-from-RS condition).

Volume: $B_{\text{far}} \leq \lceil n/t \rceil$.

**Sub-case 2b**: $\Delta(f_2, C) \leq \delta$. Then $f_2$ has a nearby codeword $g_2$. The equation becomes $(γ_1 - γ_2)g_2(x) + (\gamma_1-\gamma_2)(f_2(x)-g_2(x)) = h_{\gamma_1}(x) - h_{\gamma_2}(x)$ on $S_{\gamma_1} \cap S_{\gamma_2}$.

The "noise" term $(f_2 - g_2)$ has weight $\leq \delta n$. On $S_{\gamma_1} \cap S_{\gamma_2}$: some of these noise points may lie in the overlap.

**The overlap can be large** (up to $t$). The volume argument doesn't bound $B$ in this case.

**But**: the TOTAL $B = B_{\text{far}} + B_{\text{close}}$. For $f_2$ with $\Delta(f_2, C) > \delta$: $B = B_{\text{far}} \leq \lceil n/t \rceil$. For $f_2$ with $\Delta(f_2, C) \leq \delta$: $B$ is unconstrained by our volume argument.

**Step 3**: $B \leq \lceil n/t \rceil$ ONLY when $f_2$ is far from RS.

When $f_2$ is close: $B$ could be up to $|F|$? No — consider: if $f_2 = g_2 \in C$ exactly, then $f_1 + \gamma g_2$ has $\Delta(f_1+\gamma g_2, C) = \Delta(f_1, C)$ for all $\gamma$ (linear code). So either ALL $\gamma$ are close (if $f_1$ close) or NONE (if $f_1$ far). $B \in \{0, |F|\}$.

If $f_2 \approx g_2$ (close but not exact): $B$ is either $\approx 0$ or $\approx |F|$, with proximity loss $\delta$.

**Step 4**: Combine.
$$\epsilon_{\text{mca}} \leq \Pr[\text{close}] = B/|F| \leq \begin{cases} \lceil n/t \rceil / |F| & \text{if } f_2 \text{ far} \\ 1 & \text{if } f_2 \text{ close (trivial)} \end{cases}$$

Taking the max: $\epsilon_{\text{mca}} \leq \lceil n/t \rceil / |F|$ when $f_2$ is far (the binding case). When $f_2$ is close: $B$ is large but most bad $\gamma$'s are "benign" (interleaved)... which we haven't proved.

## ACTUALLY: reconsidering the ABF definition

ABF defines:
$$\epsilon_{\text{mca}} = \max_{f_1, f_2} \Pr_\gamma[\text{close AND not-interleaved}]$$

The max is over ALL $(f_1, f_2)$. When $f_2$ is close to RS: Pr[close] is large, but Pr[not-interleaved] might be small. The PRODUCT Pr[close AND not-interleaved] is what matters.

Our bound: $\Pr[\text{close AND not-interleaved}] \leq \Pr[\text{close}]$. This is valid but loose when most close $\gamma$'s are interleaved.

**The volume bound gives**: for $f_2$ far from RS: $\Pr[\text{close}] \leq \lceil n/t \rceil / |F|$. Since "close AND not-interleaved" ⊆ "close": $\epsilon_{\text{mca}} \leq \lceil n/t \rceil / |F|$ for $f_2$-far pairs.

For $f_2$-close pairs: $\Pr[\text{close}]$ is large but $\Pr[\text{not-interleaved}]$ should be small. We can't prove the latter rigorously, but the product is bounded by:

$\Pr[\text{close AND not-interleaved}] \leq \Pr[\text{not-interleaved}] \leq ???$

The "not-interleaved" probability requires a separate bound that we DON'T have.

## Final honest assessment

**What IS proved**: $\epsilon_{\text{mca}} \leq \lceil n/t \rceil / |F|$ for all $(f_1, f_2)$ where $f_2$ is $\delta$-far from RS.

**What is NOT proved**: the same bound when $f_2$ is $\delta$-close to RS.

**For the prize**: the bound $\epsilon_{\text{mca}} = O(1)/|F|$ is proved for the "hard" case ($f_2$ far). The "easy" case ($f_2$ close) likely gives an even SMALLER $\epsilon_{\text{mca}}$ (because interleaved structure kicks in) but we haven't proved this.

**The overall MCA bound**: $\epsilon_{\text{mca}} \leq \max(\lceil n/t \rceil / |F|, \epsilon_{\text{close}})$ where $\epsilon_{\text{close}}$ is the MCA error for $f_2$-close pairs. If $\epsilon_{\text{close}} \leq \lceil n/t \rceil / |F|$: we're done. If not: the $f_2$-close case is the bottleneck.

**Conjecture**: $\epsilon_{\text{close}} = O(1)/|F|$ (because when $f_2$ is close, the interleaved structure almost forces MCA). But this is a conjecture, not a theorem.
