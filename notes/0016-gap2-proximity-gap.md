# Note 0016 — Gap 2: From List-Size to Proximity Gap

**Date**: 2026-04-21  
**Status**: Analysis of the gap; identifies exactly what's needed

## 1. The proximity gap definition (BCIKS)

For RS code $\mathcal{C} = \mathrm{RS}[F, L, k]$ and proximity parameter $\delta$:

An affine line $V = \{f + z \cdot g : z \in F\}$ (for fixed $f, g \in F^n$) satisfies the **proximity gap** at distance $\delta$ with $E$ exceptions if:

- Either $\Delta(f + zg, \mathcal{C}) \leq \delta$ for ALL $z \in F$
- Or $\Delta(f + zg, \mathcal{C}) \leq \delta$ for at most $E$ values of $z$

The **proximity gap theorem** says: $E = O(n)$ for $\delta < J(\rho)$ (Johnson radius).

## 2. Connection to FRI

FRI folding: $f(x) = f_{\text{even}}(x^2) + x \cdot f_{\text{odd}}(x^2)$. Folded word: $f'(y) = f_{\text{even}}(y) + \alpha \cdot f_{\text{odd}}(y)$ for random $\alpha$.

The affine line is $\{f_{\text{even}} + \alpha \cdot f_{\text{odd}} : \alpha \in F\}$.

FRI soundness per round = $\Pr_\alpha[f' \text{ is } \delta'\text{-close to RS}_{k/2}]$.

If the proximity gap holds with $E$ exceptions: soundness error $\leq E / |F|$.

## 3. What we have vs what's needed

### What we have (Thm 8/9)

For ANY single word $w$: $M_\delta(w) \leq n/(t-1) \cdot \mathbb{1}_{(t-1)|n} + O(\binom{n}{t}/p^{t-2})$.

For power-of-2 domains, even $t$: $M_\delta(w) = O(1)$.

### What the proximity gap needs

For an AFFINE LINE $\{f + zg : z \in F\}$: 

$$E = \#\{z \in F : M_\delta(f + zg) \geq 1\} \leq ???$$

### The gap

Our bound is **per-word**. The proximity gap is about **how many words on a line** are close to RS.

These are different questions! A per-word bound $M = O(1)$ says: each word has few nearby codewords. But it doesn't directly bound how many words on a line have ANY nearby codeword.

## 4. Can we bridge the gap?

### Approach A: BCIKS reduction

BCIKS reduce proximity gap to list-decoding. Their key tool: the **correlated agreement** theorem.

**Correlated Agreement** (informal): If many $z$-values have $f + zg$ close to RS, then there exist codewords $h_f, h_g$ such that $f$ is close to $h_f$ and $g$ is close to $h_g$, and the "nearby codewords" for $f + zg$ are of the form $h_f + z \cdot h_g$.

This means: the bad z's are "correlated" — they all arise from the SAME pair $(h_f, h_g)$.

If correlated agreement holds: $E \leq$ (number of z's where $h_f + z \cdot h_g$ is close to $f + zg$) + O(n).

For the "correlated" part: $\Delta(f + zg, h_f + zh_g) = \Delta(f - h_f, z(h_g - g))$. If $f \neq h_f$ or $g \neq h_g$: this is the distance of an affine function of $z$ from a fixed function, bounded by $\ldots$ (degree argument).

**Problem**: BCIKS prove correlated agreement up to Johnson. Above Johnson: the proof fails (Guruswami-Sudan doesn't give bounded list size).

### Approach B: Direct counting (our approach)

For each codeword $h \in \mathrm{RS}_k$: the set of $z$-values where $f + zg$ agrees with $h$ on $\geq t$ points is:

$$Z_h = \{z : |\{x \in L : f(x) + zg(x) = h(x)\}| \geq t\}$$

For fixed $x$: $f(x) + zg(x) = h(x)$ iff $z = (h(x) - f(x))/g(x) =: \phi_h(x)$ (when $g(x) \neq 0$).

The agreement set at $z$ with $h$ is $\{x \in L : \phi_h(x) = z\}$ (level set of $\phi_h$).

$|Z_h| = \#\{z : |\phi_h^{-1}(z)| \geq t\} \leq n/t$ (pigeonhole).

Over ALL codewords $h$: $E \leq \#\{z : \exists h, |\phi_h^{-1}(z)| \geq t\}$.

Different $h$'s can give the SAME $z$. So: $E \leq |\bigcup_h Z_h| \leq \sum_h |Z_h| \leq p^k \cdot n/t$. Way too loose.

### Approach C: Use our structure theorem

Our Thm 4/6 says: the agreement sets of $f + zg$ with codewords are COSETS (or sporadic). The coset structure means the agreements are highly structured.

For the affine line $f + zg$: as $z$ varies, the word changes linearly. The agreement polynomial for codeword $h$ at a specific point $x$ is linear in $z$: $f(x) + z \cdot g(x) - h(x)$. This is linear in $z$ for each $x$.

The $t$-rich $z$-values: where $\geq t$ of the $n$ linear functions (one per $x \in L$) vanish simultaneously.

**This is EXACTLY the same incidence problem we solved for per-word list size, but in the $z$-variable instead of the $h$-variable!**

For fixed $h$: the $n$ conditions $f(x) + z g(x) = h(x)$ are $n$ linear equations in $z$. Each gives $z = \phi_h(x)$. The agreement count at $z$ is the multiplicity of $z$ in the multiset $\{\phi_h(x) : x \in L\}$.

The max list size of $z$-values with multiplicity $\geq t$: same as our per-word problem but with the role of $(h_0, h_1)$ replaced by $z$ (a 1-dimensional parameter).

By the 1D version of our argument: the number of $t$-popular $z$-values for a FIXED $h$ is $\leq n/t$ (pigeonhole, since each $z$ uses $\geq t$ points of $L$).

Over all $h$: the question is how many DISTINCT $z$'s appear. If different $h$'s give different $z$'s: $E$ could be large. If they share: $E$ could be small.

### Approach D: Key observation — the problem IS 1-dimensional

For the proximity gap: the parameter $z$ is 1-dimensional (just a field element), while our list-size bound dealt with 2D parameter space $(h_0, h_1)$.

In 1D: the "coset extraction" argument becomes SIMPLER. The $t$-popular $z$-values for a fixed $h$ form level sets of $\phi_h: L \to F$. The number of such is $\leq n/t$.

**But the key constraint**: for $h + z' \cdot h'$ to be in RS (for the "correlated" part), $h$ and $h'$ are BOTH in RS. The affine line in codeword space $\{h + z \cdot h' : z \in F\}$ has at most $p^k$ elements (all of RS for varying $z$). Each gives a different $z$-value. So the "correlation" part contributes at most $\min(p^k, n/t)$ bad $z$'s.

For $p^k \gg n$: this is $n/t$. So: **$E \leq n/t + O(\text{sporadic})$.**

## 5. Conjecture

**Conjecture**: For RS on multiplicative subgroup $L$ of order $n$, the proximity gap at distance $\delta = 1 - t/n$ satisfies:

$$E \leq \frac{n}{t} \cdot \mathbb{1}_{[t|n]} + \frac{n}{t-1} \cdot \mathbb{1}_{[(t-1)|n]} + O\!\left(\frac{\binom{n}{t}}{p^{t-2}}\right)$$

Same bound as the per-word list size! The reason: the proximity gap problem in 1D ($z$-parameter) has the same algebraic structure as the list-size problem in 2D ($(h_0, h_1)$-parameter).

## 6. What's needed for proof

1. Formalize the reduction: proximity gap → per-$h$ level-set counting → coset extraction in the $\phi_h$ function.
2. Handle the "union over $h$" step: show that different $h$'s don't create too many new $z$-values.
3. Use the structure: $\phi_h(x) = (h(x) - f(x))/g(x)$ has degree $\leq n$ but restricted to $L$, its level-set structure is controlled by the multiplicative group.

**Estimated effort**: This is the hardest remaining gap. 2-4 weeks of serious work.
