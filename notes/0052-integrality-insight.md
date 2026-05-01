# Note 0052 — The Integrality Insight

## Discovery

$N_w$ is a non-negative integer. $N_w = \text{main} + R_w$ where main $= \binom{n}{w}(p-1)^w/p^{n-k}$.

So $R_w = N_w - \text{main}$, and $|R_w| = |N_w - \text{main}|$.

**Empirical**: $|R_w|$ takes only FINITELY MANY discrete values, corresponding to $N_w \in \{0, 1, 2, \ldots\}$.

## What this gives immediately

If main $< 1$: $N_w \in \{0, 1\}$ (since $N_w \geq 0$ integer and $N_w = \text{main} + R_w$ with $|R_w| < $ something).

Actually: we need to BOUND $N_w$, not just $|R_w|$. The integrality gives:
- $N_w = 0 \implies |R_w| = \text{main}$
- $N_w = 1 \implies |R_w| = 1 - \text{main}$
- $N_w = m \implies |R_w| = m - \text{main}$

Without any bound on $|R_w|$: $N_w$ can be anything. The character sum IS needed to bound $|R_w|$ and hence $N_w$.

## But the character sum might be MUCH easier than expected

What we need: $|R_w| < 2$ (to get $N_w \leq 1$, giving $M \leq \delta n$).

Or: $|R_w| < 1$ (to get $N_w = 0$ when main $< 1/2$, or $N_w \leq 1$ when main $< 1$).

For $|R_w| < C$: need $|\sum_{\xi \neq 0} \psi(-\langle\xi,c\rangle) S_w(z(\xi))| < C \cdot p^{n-k}$.

The trivial bound: $\leq \sum |S_w(z)| \cdot |\{\xi: |Z|=z\}|$ which is $p^{n-k} \cdot O(\binom{n}{w} p^{n-k-1})$ — way too large.

But the PHASE $\psi(-\langle\xi,c\rangle)$ provides cancellation. The data shows: for p=17, n=8, ALL syndromes give $|R_w| < 1$. This means: the cancellation is PERFECT (or nearly so).

## The key structure: R_w depends on c only through the COSET

$N_w$ = number of weight-$w$ vectors in coset $c + \text{RS}_k$. Different $c$ in the SAME coset give the same $N_w$.

For MDS codes: there are $p^{n-k}$ cosets. The number of cosets with $N_w \geq m$: bounded by $\binom{n}{w}(p-1)^w / m$ (the total weight-$w$ vectors in all cosets is $\binom{n}{w}(p-1)^w$, each with $N_w \geq m$ contributes $\geq m$).

The fraction of cosets with $N_w \geq 1$: $\leq \binom{n}{w}(p-1)^w / p^{n-k} = \text{main}$.

For main $< 1$: the fraction is $< 1$, so MOST cosets have $N_w = 0$. But some cosets can have $N_w \geq 1$.

## What the character sum ACTUALLY computes

$N_w(c) = \text{main} + R_w(c)$ where $R_w(c)$ oscillates as $c$ varies. The AVERAGE of $N_w$ over all $c$: $\text{main}$ (by definition). The oscillation is controlled by the character sum.

For the list-decoding problem: we need $N_w(c) = O(1)$ for ALL $c$ (not just average).

The worst-case $c$: the one that maximizes $N_w(c)$. From the data (p=17, n=8): max $N_w = 1$. From (p=7, n=6): max $N_w = 3$.

## Connection to deep holes of RS codes

A "deep hole" of a code is a word at maximum distance from the code. A coset with many low-weight vectors is the OPPOSITE: it's a coset that's unusually CLOSE to many codewords.

The study of deep holes and coset weight distributions of RS codes is a classical topic in coding theory. Key reference: Cheng-Wan (2007) "On Deep Holes of RS Codes."

The coset weight distribution of MDS codes IS known (via MacWilliams identity). The question: is the MAXIMUM $N_w$ over all cosets bounded by $O(1)$?

For MDS: the average is main $= \binom{n}{w}(p-1)^w / p^{n-k}$. The max could be much larger.

For RS codes SPECIFICALLY (not just any MDS): the max might be O(1) due to the Vandermonde structure. This is related to the "list-decodability" of RS codes — exactly our problem!

## Status

The integrality observation simplifies the problem but doesn't solve it. We still need either:
1. A bound on $\max_c N_w(c)$ (the maximum coset weight), or
2. A bound on $|R_w(c)|$ for all $c$ (the character sum bound).

Both are equivalent. The character sum approach might be easier because it gives quantitative bounds.

For the FRI paper: we don't need this. The FRI theorem is complete. This is an open problem for the list-decoding question.
