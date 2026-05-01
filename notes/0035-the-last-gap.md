# Note 0035 — The Last Gap: f2-Close MCA Violation Count

**Date**: 2026-04-21

## The precise problem

Given: $f_1, f_2 \in F^n$ with $\Delta(f_2, C) \leq \delta$ (f2 close to RS). Let $g_2 \in C$ nearest to $f_2$, $e = f_2 - g_2$, $\mathrm{wt}(e) \leq \delta n$, $E = \mathrm{supp}(e) \subset L$.

For $\gamma \in F$: $w_\gamma = f_1 + \gamma f_2$. A $\gamma$ is "MCA-violating" if:
1. $\exists h_\gamma \in C, S_\gamma \subset L$ with $|S_\gamma| \geq t$ and $w_\gamma = h_\gamma$ on $S_\gamma$
2. $\nexists (g_1, g_2') \in C^{=2}$ with $f_1 = g_1$ AND $f_2 = g_2'$ on $S_\gamma$

Condition (2) fails (i.e., MCA is satisfied) iff $f_2|_{S_\gamma}$ is a degree-$< k$ polynomial on $S_\gamma$.

**Question**: $V = \#\{\gamma : \text{MCA-violating}\} = ?$

**What we need**: $V \leq O(1)$ (or at least $V \leq O(n)$).

## Setup for character-sum attack

Write $f_2 = g_2 + e$ on $L$. On $S_\gamma$: $f_2|_{S_\gamma}$ is degree $< k$ iff $e|_{S_\gamma}$ is degree $< k$.

$e$ is a sparse function: $\mathrm{wt}(e) \leq \delta n$, supported on $E$.

$e|_{S_\gamma}$ is degree $< k$ on $S_\gamma$ iff the unique polynomial interpolating $e$ on $S_\gamma$ (which exists since $|S_\gamma| \geq t > k$) equals $e$ on all of $S_\gamma$.

Equivalently: $e|_{S_\gamma}$ extends to a degree-$< k$ polynomial. Since $|S_\gamma| \geq t > k$: this means $e$ restricted to ANY $k$ points of $S_\gamma$ determines the interpolant, and $e$ agrees with this interpolant on ALL of $S_\gamma$.

A sparse function ($\leq \delta n$ nonzeros) being degree $< k$ on a set of size $\geq t$: this is possible only if the nonzero pattern of $e$ on $S_\gamma$ is "algebraically consistent."

## The character-sum formulation

The number of MCA-violating $\gamma$ is:

$$V = \#\{\gamma : \exists S_\gamma \text{ with } |S_\gamma| \geq t, w_\gamma = h_\gamma \text{ on } S_\gamma, \text{ AND } e|_{S_\gamma} \notin \mathrm{RS}_k|_{S_\gamma}\}$$

The condition "$e|_{S_\gamma} \notin \mathrm{RS}_k|_{S_\gamma}$" means: the "syndrome" of $e$ restricted to $S_\gamma$ is nonzero. In DFT terms:

$$\exists j \in [k, t-1]: \sum_{i \in S_\gamma} e(\omega^i) \omega^{-ij} \neq 0$$

This is a partial DFT condition on $e$ restricted to the indicator of $S_\gamma$.

## Key observation

$S_\gamma$ depends on $\gamma$ (it's the agreement set of $f_1 + \gamma f_2$ with $h_\gamma$). On $S_\gamma$:

$$f_1(\omega^i) + \gamma f_2(\omega^i) = h_\gamma(\omega^i) \quad \forall i \in S_\gamma$$

So: $f_1 + \gamma g_2 + \gamma e = h_\gamma$ on $S_\gamma$. Define $w' = f_1 + \gamma g_2$ (a shifted codeword direction). Then $h_\gamma = w' + \gamma e$ on $S_\gamma$.

Since $h_\gamma \in C$ (degree $< k$) and $w' = f_1 + \gamma g_2$:

$$h_\gamma - w' = \gamma e \text{ on } S_\gamma$$

$h_\gamma - w'$ has degree $< \max(\deg h_\gamma, \deg w') < n$. And $\gamma e$ is a sparse function (weight $\leq \delta n$).

The condition: a low-degree polynomial ($h_\gamma - w'$) equals a sparse function ($\gamma e$) on $S_\gamma$.

## Character-sum bound attempt

For a FIXED $\gamma$: how many large sets $S \subset L$ have a degree-$< k$ polynomial $h$ matching $w' + \gamma e$ on $S$?

This is the list-decoding count $M_\delta(w' + \gamma e) = M_\delta(f_1 + \gamma f_2)$.

For the MCA violation: additionally need $e|_S \notin \mathrm{RS}_k|_S$.

Counting via characters: the number of $(S, h)$ pairs with $|S| \geq t$, $w_\gamma = h$ on $S$, and $e|_S \notin \mathrm{RS}_k|_S$:

This can be expressed as:

$$V(\gamma) = M_\delta(w_\gamma) - M_\delta^{\text{interleaved}}(w_\gamma)$$

where $M^{\text{interleaved}}$ counts codewords $h_\gamma$ such that $e|_{S_\gamma} \in \mathrm{RS}_k|_{S_\gamma}$.

The total MCA violation: $V = \sum_\gamma \mathbb{1}[V(\gamma) > 0]$.

## The f2-close constraint via exponential sums

On $S_\gamma$: $\gamma e = h_\gamma - w'$. The DFT of $\gamma e \cdot \mathbb{1}_{S_\gamma}$ at frequency $j$:

$$\sum_{i \in S_\gamma} \gamma e(\omega^i) \omega^{-ij} = \sum_{i \in S_\gamma} (h_\gamma(\omega^i) - w'(\omega^i)) \omega^{-ij}$$

For $j \geq k$: $\hat{h}_\gamma(j) = 0$ (since $h_\gamma \in \mathrm{RS}_k$). So:

$$\gamma \sum_{i \in S_\gamma} e(\omega^i) \omega^{-ij} = -\sum_{i \in S_\gamma} w'(\omega^i) \omega^{-ij}$$

The LHS involves $e$ (sparse, known) restricted to $S_\gamma$ (unknown, depends on $\gamma$).
The RHS involves $w' = f_1 + \gamma g_2$ restricted to $S_\gamma$.

Since $g_2 \in C$: $\hat{g}_2(j) = 0$ for $j \geq k$. So:

$$\sum_{i \in S_\gamma} w'(\omega^i) \omega^{-ij} = \sum_{i \in S_\gamma} f_1(\omega^i) \omega^{-ij} + \gamma \sum_{i \in S_\gamma} g_2(\omega^i) \omega^{-ij}$$

For the FULL sum (over all $L$): $\sum_{i=0}^{n-1} g_2(\omega^i) \omega^{-ij} = n \hat{g}_2(j) = 0$ for $j \geq k$.

But the sum is over $S_\gamma$, not $L$! $\sum_{i \in S_\gamma} g_2(\omega^i) \omega^{-ij} = -\sum_{i \notin S_\gamma} g_2(\omega^i) \omega^{-ij}$ (since the full sum is 0).

$|L \setminus S_\gamma| \leq \delta n$. So: $|\sum_{i \in S_\gamma} g_2(\omega^i) \omega^{-ij}| = |\sum_{i \notin S_\gamma} g_2(\omega^i) \omega^{-ij}| \leq \delta n \cdot \max|g_2|$.

This is a partial exponential sum over the "error set" $L \setminus S_\gamma$.

## Where character sums enter

The key quantity: $\sum_{i \in E'} g_2(\omega^i) \omega^{-ij}$ where $E' = L \setminus S_\gamma$ has $|E'| \leq \delta n$.

This is an **incomplete exponential sum** — a sum of $\psi(g_2(\omega^i) \cdot \omega^{-ij})$ over a subset $E'$ of the multiplicative subgroup $L$.

Bounds from the sequence literature:
- **Weil bound**: $|\sum_{x \in L} \psi(f(x))| \leq (d-1)\sqrt{p}$ for $f$ of degree $d$ (COMPLETE sum over $L$).
- **Incomplete sums**: for $E' \subset L$ with $|E'| = m$: $|\sum_{x \in E'} \psi(f(x))| \leq m$ (trivially), or sharper via Vinogradov/Korobov methods.

The incomplete sum $\sum_{i \in E'} g_2(\omega^i) \omega^{-ij}$ has $|E'| \leq \delta n$ terms. Trivial bound: $\leq \delta n$. This is not useful (same order as $n$).

## The approach that might work

Instead of bounding individual sums, count the NUMBER of $\gamma$ where the cancellation works.

For MCA violation at $\gamma$: need $\gamma e|_{S_\gamma}$ to be NOT low-degree on $S_\gamma$. Equivalently: the syndrome of $\gamma e \cdot \mathbb{1}_{S_\gamma}$ is nonzero at some $j \geq k$.

The syndrome at $j$: $\gamma \sum_{i \in S_\gamma} e(\omega^i) \omega^{-ij} = -\sum_{i \in S_\gamma} f_1(\omega^i) \omega^{-ij}$ (from the relation above, with the $g_2$ term vanishing).

Wait: let me redo. We had $\gamma \sum_{i \in S_\gamma} e(\omega^i) \omega^{-ij} = -\sum_{i \in S_\gamma} w'(\omega^i) \omega^{-ij}$.

And $w' = f_1 + \gamma g_2$. So $\sum_{i \in S_\gamma} w' \omega^{-ij} = \sum_{i \in S_\gamma} f_1 \omega^{-ij} + \gamma \sum_{i \in S_\gamma} g_2 \omega^{-ij}$.

Combined: $\gamma \sum_{S_\gamma} e \omega^{-ij} + \sum_{S_\gamma} f_1 \omega^{-ij} + \gamma \sum_{S_\gamma} g_2 \omega^{-ij} = 0$ for $j \geq k$.

$\gamma (\sum_{S_\gamma} e \omega^{-ij} + \sum_{S_\gamma} g_2 \omega^{-ij}) = -\sum_{S_\gamma} f_1 \omega^{-ij}$

$\gamma \sum_{S_\gamma} f_2 \omega^{-ij} = -\sum_{S_\gamma} f_1 \omega^{-ij}$ (since $e + g_2 = f_2$)

This is just: $\sum_{S_\gamma} (f_1 + \gamma f_2) \omega^{-ij} = 0$ for $j \geq k$. Which is EXACTLY the condition that $f_1 + \gamma f_2$ restricted to $S_\gamma$ is degree $< k$. True by construction (since $h_\gamma \in C$ and $h_\gamma = f_1+\gamma f_2$ on $S_\gamma$).

So this is circular! The syndrome vanishes by definition.

The MCA violation condition is about $e|_{S_\gamma}$, not $(f_1+\gamma f_2)|_{S_\gamma}$. Let me reformulate.

$e|_{S_\gamma} \in \mathrm{RS}_k|_{S_\gamma}$ iff $\exists g \in \mathrm{RS}_k$ with $e = g$ on $S_\gamma$. I.e., $\sum_{i \in S_\gamma} (e(\omega^i) - g(\omega^i)) \omega^{-ij} = 0$ for all $j$ (trivially for $j < k$ by choosing $g$ appropriately; the constraint is for $j \geq k$).

For $j \geq k$: $\sum_{S_\gamma} e \omega^{-ij} = \sum_{S_\gamma} g \omega^{-ij} = -\sum_{L \setminus S_\gamma} g \omega^{-ij}$ (since $\hat{g}(j) = 0$ for $g \in C$).

So: $e \in \mathrm{RS}_k|_{S_\gamma}$ iff $\forall j \geq k: \sum_{S_\gamma} e \omega^{-ij} = -\sum_{L \setminus S_\gamma} g \omega^{-ij}$ for SOME $g \in C$.

The RHS involves $g$ restricted to $L \setminus S_\gamma$ (a small set of $\leq \delta n$ points). With $k$ free parameters in $g$: we can choose $g$ to match $k$ conditions. We have $n - k$ conditions ($j = k, ..., n-1$). For the system to be satisfiable: the $n-k$ equations must be consistent given $k$ free parameters. Generically: $n - k - k = n - 2k$ conditions are over-determined.

For $n - 2k > 0$ (i.e., $\rho < 1/2$): over-determined. Generally NO solution. So $e \notin \mathrm{RS}_k|_{S_\gamma}$ generically. MCA IS violated.

For $n - 2k = 0$ (i.e., $\rho = 1/2$): the system is square. May have a solution. MCA might NOT be violated.

This doesn't directly give a COUNT. But it shows: MCA violation is the GENERIC case (for $\rho < 1/2$). The question is: how many $\gamma$ avoid MCA violation?
