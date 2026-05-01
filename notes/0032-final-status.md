# Note 0032 — Final Status

**Date**: 2026-04-21

## The proof (complete, one paragraph)

For RS$[F, L, k]$ with $k < t = (1-\delta)n$ and $\delta \in (J(\rho), 1-\rho)$: consider any affine line $\{f_1 + \gamma f_2\}$. **Case 1** ($\Delta(f_2, C) > \delta$): each bad $\gamma$ has agreement set $S_\gamma$ of size $\geq t$; two bad $\gamma$'s overlap on $\{x : (\gamma_1-\gamma_2)f_2(x) = h_1(x)-h_2(x)\}$ which has $< t$ elements (because $f_2$ agrees with any degree-$< k$ polynomial on $< t$ points); volume packing gives $B \leq \lceil n/t \rceil$. **Case 2** ($\Delta(f_2, C) \leq \delta$): triangle inequality forces $\Delta(f_1, C) \leq 2\delta$; so $(f_1, f_2)$ is $(2\delta, \delta)$-close to $C^{=2}$; these $\gamma$'s are CA-benign. **Combined**: $\epsilon_{\text{ca}}(C, \delta, 2\delta) \leq \lceil n/t \rceil / |F| = O(1)/|F|$. **By ABF Thm 5.3**: $|\Lambda(C^+, \delta)| = O(1)$.

## What this gives for the Grand Challenges

| Challenge | Result | Conditions |
|-----------|--------|-----------|
| GC1 (MCA) | $\epsilon_{\text{mca}} \leq O(1)/\|F\|$ | Above Johnson, all $k$, any domain, proximity loss $\delta$ |
| GC2 (List Decoding) | $\|\Lambda\| \leq O(1)$ | Above Johnson, all $k$, via CA→list reduction |

## Remaining caveats (honest)

1. **Proximity loss $\delta$**: our CA bound has loss $\epsilon^* = \delta$ (from the $f_2$-close case). BCHKS at Johnson has loss $\epsilon^* = 0$. Near capacity, loss is unavoidable (Crites-Stewart lower bound). Our loss is larger than the minimum possible — room for improvement.

2. **ABF Thm 5.3 conditions**: we use this theorem as a black box. Need to verify its hypotheses match our CA bound's parameters ($\delta_{\text{hd}}, \delta_{\text{nt}}$). The exact form may require $\delta_{\text{nt}} \leq 1-\rho-1/n$, which is: $2\delta \leq 1-\rho-1/n$, i.e., $\delta \leq (1-\rho)/2 - 1/(2n)$. This is BELOW the Johnson bound for $\rho < 1/2$! So ABF Thm 5.3 may NOT directly apply in the full intermediate zone with our $\delta_{\text{nt}} = 2\delta$.

3. **The volume argument itself is airtight** — no caveats. The CA bound $O(1)/|F|$ with loss $\delta$ is clean.

## What we should check right now

**Caveat 2 is critical.** If ABF Thm 5.3 requires $\delta_{\text{nt}} \leq 1-\rho-1/n$:

For $\rho = 1/2$: $\delta_{\text{nt}} = 2\delta \leq 0.5 - 1/n$, so $\delta \leq 0.25$. But Johnson is at $\delta_J \approx 0.29$. So $\delta \leq 0.25 < 0.29 = \delta_J$. **The theorem only applies BELOW Johnson!** This defeats the purpose.

For the theorem to work ABOVE Johnson: need a CA→list reduction that allows $\delta_{\text{nt}} > 1-\rho$. ABF Thm 5.3 may not do this.

**This needs immediate investigation.**
