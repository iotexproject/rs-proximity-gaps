# Note 0054 — Three Approaches: Deep Dive Results

## Approach 1: BGK + Li-Wan — BLOCKED

**Li-Wan decomposition**: $-1 + p\cdot\mathbb{1}[h_i=0] = \sum_{t=1}^{p-1}\psi(t\cdot h_i)$.

Substituting and swapping summation order: the sum over $\xi$ collapses by character orthogonality, giving $R_w = N_w - \text{main}$. **Circular** — it's just the definition.

**Why BGK doesn't help directly**: BGK bounds $|\sum_{x \in H} \psi(ax)|$ for multiplicative subgroups $H \subset \mathbb{F}_p^*$. But our sum is over $\xi \in \mathbb{F}_p^{n-k}$ (a VECTOR SPACE), not a multiplicative subgroup. The structural mismatch prevents direct application.

**Possible fix**: decompose $\xi$ into "radial" (multiplicative) and "angular" (directional) parts. But $\mathbb{F}_p^{n-k}$ has no natural multiplicative structure for $n-k > 1$.

**Verdict**: ❌ Dead end as stated. Needs a reformulation to bring the multiplicative structure into play.

---

## Approach 2: Katz l-adic cohomology — WRONG DIMENSION

**Setup**: Group the sum by zero count: $R_w = (1/p^{n-k})\sum_z S_w(z) \cdot \Phi(z,c)$.

$\Phi(z,c) = \sum_{\xi: |Z(\xi)|=z} \psi(-\langle\xi,c\rangle)$ is a character sum over the variety $V_z = \{\xi : q_\xi \text{ has exactly } z \text{ zeros on } L\}$.

**Deligne bound**: For variety of dimension $d$ and degree $D$: $|\sum_{x \in V} \psi(f(x))| \leq C(D) p^{d/2}$.

$V_z$ has dimension $\approx n-k-1$ (generic $z$). Deligne gives: $|\Phi(z,c)| \leq C \cdot p^{(n-k-1)/2}$.

**Result**: $|R_w| \leq C/\sqrt{p} \cdot \sum_z |S_w(z)|$. The sum $\sum |S_w(z)| \approx \binom{n}{w} p^{n-k-1}$.

So: $|R_w| \leq C \binom{n}{w} p^{n-k-3/2} / p^{n-k} = C\binom{n}{w}/p^{3/2}$.

For FRI: $\binom{n}{w} \approx 2^{10^6}$ and $p^{3/2} \approx 2^{46.5}$. **Astronomically far from $<1$.**

**Verdict**: ❌ The variety dimension $n-k-1$ is too large. Deligne saves only $\sqrt{p}$, but we need to save $\binom{n}{w}$.

---

## Approach 3: Gong's cross-correlation via MacWilliams — MOST PROMISING ✓

**The MacWilliams identity** for the coset weight distribution:

$$N_w = A_w(c + \text{RS}_k) = \frac{1}{p^k}\sum_{j=0}^n B_j(c) \cdot K_w(j; n, p)$$

where $K_w(j)$ = Krawtchouk polynomial and:

$$B_j(c) = \sum_{\substack{v \in \text{RS}[n,n-k] \\ \text{wt}(v) = j}} \psi(\langle v, c \rangle)$$

is the **twisted weight enumerator** of the dual code.

**Main term** ($j=0$): $B_0 = 1$, $K_w(0) = \binom{n}{w}(p-1)^w$. Gives $\binom{n}{w}(p-1)^w/p^k$.

**Error**: $R_w = (1/p^k)\sum_{j=k+1}^n B_j(c) K_w(j)$.

**Trivial bound**: $|B_j(c)| \leq A_j^\perp$ (number of weight-$j$ dual codewords). This gives $|R_w| \leq \sum_j A_j^\perp |K_w(j)| / p^k \approx \binom{n}{w}(p-1)^w$. **Way too large.**

### The key question: does $B_j(c)$ have CANCELLATION?

$B_j(c) = \sum_{v: \text{wt}=j} \psi(\langle v, c\rangle)$. The inner product $\langle v, c\rangle = \sum_{i} v(\omega^i) c_i$.

For dual RS codewords $v$: these are evaluations of polynomials of degree $< n-k$ on $L$. The sum $\langle v, c\rangle$ is an exponential sum involving the polynomial's evaluations — a **cross-correlation** between the dual codeword and the word $c$.

**In Gong's language**: $B_j(c)$ is the partial Walsh/Fourier transform of the dual code, restricted to weight-$j$ codewords, twisted by the phase from $c$.

### The conjecture

**Conjecture (Square-Root Cancellation)**:
$$|B_j(c)| \leq C \cdot \sqrt{A_j^\perp} \quad \text{for all } c, \text{ all } j \geq k+1$$

**Why plausible**: The phases $\psi(\langle v, c\rangle)$ for different dual codewords $v$ of fixed weight should be "pseudo-random" — equidistributed over $p$-th roots of unity. The $A_j^\perp$ terms in the sum have random-looking phases, so by heuristic CLT: $|B_j| \approx \sqrt{A_j^\perp}$.

**What it gives**: $|R_w| \leq (1/p^k) \sum_j \sqrt{A_j^\perp} |K_w(j)|$.

For MDS: $A_j^\perp \approx \binom{n}{j} p^{j-k}$. So $\sqrt{A_j^\perp} \approx \sqrt{\binom{n}{j}} p^{(j-k)/2}$.

The Krawtchouk polynomial: $|K_w(j)| \leq \binom{n}{w}(p-1)^w \cdot \text{(oscillation factor)}$. For $j$ near the roots of $K_w$: the oscillation factor is small.

### Connection to known results

1. **Golomb-Gong (Ch. 10)**: Cross-correlation of m-sequences and Gold/Kasami sequences is few-valued (3 or 5 values). For RS codes: the cross-correlation spectrum is richer but still structured by the algebraic nature of the codewords.

2. **Yu-Gong (2010)**: Refined Weil bounds for multiplicative character sums over $\mathbb{F}_q^*$. Could bound individual terms $\psi(\langle v, c\rangle)$ when $v$ and $c$ have specific structure.

3. **Bourgain-Glibichuk-Konyagin**: For subgroups $H > p^\epsilon$: $|\sum_{x \in H} \psi(ax)| = o(|H|)$. Applied to the subgroup $L$: exponential sums of polynomial evaluations on $L$ have nontrivial cancellation.

4. **Li-Wan (2018)**: Used sieving + character sums over the FULL field. Their error term $O(p^{k-1/2})$ comes from Weil bounds over $\mathbb{F}_p$, not over subgroups.

5. **Pless power moment identities**: $\sum_c |B_j(c)|^2 = A_j^\perp \cdot p^{n-k}$ (Parseval over syndromes). This gives AVERAGE $|B_j|^2 = A_j^\perp / p^{n-k} \cdot p^{n-k} = A_j^\perp$... wait, that's just the trivial bound for each $c$ individually.

Actually: $\sum_{c \in \mathbb{F}_p^{n-k}} |B_j(c)|^2 = \sum_{v_1, v_2: \text{wt}=j} \sum_c \psi(\langle v_1-v_2, c\rangle) = p^{n-k} A_j^\perp$ (only $v_1 = v_2$ survives). So $\mathbb{E}_c[|B_j(c)|^2] = A_j^\perp$. RMS of $|B_j|$ = $\sqrt{A_j^\perp}$.

**The RMS is exactly $\sqrt{A_j^\perp}$!** So the conjecture asks: is $|B_j(c)|$ close to its RMS for ALL $c$?

This is a **concentration** question: does $|B_j(c)|$ concentrate around $\sqrt{A_j^\perp}$?

By the fourth moment method: $\mathbb{E}[|B_j|^4] = \sum_{v_1,v_2,v_3,v_4: \text{wt}=j} \sum_c \psi(\langle v_1-v_2+v_3-v_4, c\rangle)$ = $p^{n-k} \cdot |\{(v_1,v_2,v_3,v_4): v_1-v_2+v_3-v_4=0, \text{all wt } j\}|$.

The count: $|\{(v_1,v_2,v_3,v_4) \in (C_j^\perp)^4 : v_1+v_3=v_2+v_4\}|$ where $C_j^\perp$ = weight-$j$ dual codewords. This is the **additive energy** of the weight-$j$ codewords!

For RS (MDS) codes: the additive energy of weight-$j$ codewords is controlled by the code's algebraic structure. If the energy is $O((A_j^\perp)^2)$ (Cauchy-Schwarz): $\mathbb{E}[|B_j|^4] = O(p^{n-k} (A_j^\perp)^2)$, giving $\max |B_j| \leq (p^{n-k} (A_j^\perp)^2)^{1/4} = (A_j^\perp)^{1/2} \cdot p^{(n-k)/4}$. Still too large.

For the energy to be $O((A_j^\perp)^{3/2})$ or less: need the weight-$j$ codewords to be "spread out" (low additive energy). This is a COMBINATORIAL property of MDS codes.

### Status: the reduction is clean, the bound is not

The MacWilliams identity cleanly reduces $N_w$ to the twisted weight enumerator $B_j(c)$. The RMS of $|B_j|$ is $\sqrt{A_j^\perp}$. But bounding the MAXIMUM of $|B_j(c)|$ over all $c$ requires:

1. **Cross-correlation equidistribution** of RS dual codewords (Gong's expertise)
2. **Additive energy bounds** for MDS codewords of fixed weight (combinatorial)
3. **Krawtchouk polynomial estimates** in the relevant regime

This is a well-posed mathematical problem with clear connections to the Gong-Golomb-Helleseth tradition.
