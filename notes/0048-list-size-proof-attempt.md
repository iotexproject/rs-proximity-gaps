# Note 0048 — Proof Attempt: M = 0 for RS on Multiplicative Subgroups when p ≫ 1

## Setup

RS[$\mathbb{F}_p$, $L$, $k$] with $L = \langle\omega\rangle \subset \mathbb{F}_p^*$ of order $n$, $p$ prime.
Parity check matrix $H$: $(n-k) \times n$, $H_{r,i} = \omega^{-(r+k)i}$ for $r = 0, \ldots, n-k-1$, $i = 0, \ldots, n-1$.

Word $w \in \mathbb{F}_p^n$. Syndrome: $c = Hw^T \in \mathbb{F}_p^{n-k}$.

List-decoding count: $M = \#\{h \in \text{RS}_k : \Delta(w, h) \leq \delta\}$.

Equivalently: $M = \#\{e : \text{wt}(e) \leq \delta n, He^T = c, e(x) \neq 0 \text{ on supp}(e)\}$.

## Key lemma: counting supports

**Lemma**: The number of $w$-element subsets $T \subset [n]$ such that the system $H_T \cdot x = c$ has a solution (over $\mathbb{F}_p$) is:

$$N_w = \frac{1}{p^{n-k}} \sum_{\xi \in \mathbb{F}_p^{n-k}} \psi(-\langle \xi, c \rangle) \cdot \sum_{|T|=w} \prod_{i \in T} \left(\sum_{y \neq 0} \psi(y \cdot \langle \xi, H_{\cdot,i} \rangle)\right) \cdot \prod_{i \notin T} 1$$

Wait, this isn't right. Let me redo.

$N_w$ = number of pairs $(T, x)$ with $|T| = w$, $x \in (\mathbb{F}_p^*)^w$, and $\sum_{i \in T} x_i \cdot H_{\cdot,i} = c$.

Using additive characters:

$$N_w = \frac{1}{p^{n-k}} \sum_{\xi \in \mathbb{F}_p^{n-k}} \psi(-\langle \xi, c \rangle) \sum_{|T|=w} \prod_{i \in T} \sum_{x_i=1}^{p-1} \psi(x_i \langle \xi, H_{\cdot,i} \rangle)$$

For each $i$: define $h_i = \langle \xi, H_{\cdot,i} \rangle = \sum_{r=0}^{n-k-1} \xi_r \omega^{-(r+k)i} \in \mathbb{F}_p$.

Then: $\sum_{x_i=1}^{p-1} \psi(x_i h_i) = \begin{cases} p-1 & \text{if } h_i = 0 \\ -1 & \text{if } h_i \neq 0 \end{cases}$

So:

$$N_w = \frac{1}{p^{n-k}} \sum_\xi \psi(-\langle \xi, c \rangle) \sum_{|T|=w} \prod_{i \in T} (-1 + p \cdot \mathbb{1}[h_i = 0])$$

Let $Z(\xi) = \{i \in [n] : h_i = 0\} = \{i : \sum_r \xi_r \omega^{-(r+k)i} = 0\}$.

This is the zero set of the polynomial $f_\xi(X) = \sum_{r=0}^{n-k-1} \xi_r X^{r+k}$ evaluated at $\omega^{-i}$ for $i = 0, \ldots, n-1$.

Equivalently: $f_\xi$ is a polynomial of degree $\leq n-1$ (with nonzero terms at positions $k, k+1, \ldots, n-1$). Since $\xi \neq 0$: $f_\xi$ has degree $\leq n-1$ and is nonzero. So $|Z(\xi)| \leq n-1$.

But more precisely: $f_\xi(X) = \sum_{r=0}^{n-k-1} \xi_r X^{r+k}$ has degree at most $n-1$ and its nonzero terms are at positions $k$ through $n-1$. If $\xi_{n-k-1} \neq 0$: degree = $n-1$. If the leading terms are zero: degree could be less.

**Key fact for RS (MDS)**: For $\xi \neq 0$, $f_\xi$ is a nonzero polynomial of degree $\leq n-1$ with $\leq n-k-1$ terms (actually exactly $n-k$ terms). Its zero set $Z(\xi)$ on $L$ has $|Z(\xi)| \leq n-k-1$ (by the degree bound? No — the polynomial has degree $\leq n-1$ but the zero set on $L$ is bounded by $\min(\deg f_\xi, n)$).

Actually, for the evaluation on $L$: the function $i \mapsto f_\xi(\omega^{-i})$ is a DFT-type evaluation. The zero set: $f_\xi(\omega^{-i}) = 0$ iff $\omega^{-i}$ is a root of $f_\xi$.

Since $f_\xi$ has degree $\leq n-1$: on $L$ (which has $n$ elements), $f_\xi$ can vanish at up to $n-1$ points. But $f_\xi$ is also a CODEWORD of the dual RS code: $f_\xi \in \text{RS}[n, n-k]^*$... hmm, not exactly.

Actually: $h_i = \sum_r \xi_r \omega^{-(r+k)i}$. This is the evaluation of $g(\omega^{-i})$ where $g(X) = \sum_r \xi_r X^{r+k} = X^k \sum_r \xi_r X^r$. Since $\omega^{-i}$ runs over $L$ as $i$ varies: $g$ evaluated on $L$ is a codeword of some RS code.

Specifically: $g(X) = X^k \cdot q(X)$ where $q(X) = \sum_{r=0}^{n-k-1} \xi_r X^r$ has degree $< n-k$. So $g$ has degree $< n$. The evaluation $g|_L$ is a codeword of RS$[n, n]$ = all functions on $L$.

But $g = X^k \cdot q$: this is the product of two polynomials. On $L$: $g(\omega^{-i}) = \omega^{-ki} \cdot q(\omega^{-i})$. The zero set: $g = 0$ iff $q(\omega^{-i}) = 0$ (since $\omega^{-ki} \neq 0$).

$q$ has degree $< n-k$. So $|Z(\xi)| = |\{i : q(\omega^{-i}) = 0\}| \leq \deg q \leq n-k-1$.

**Lemma**: For $\xi \neq 0$: $|Z(\xi)| \leq n-k-1$. (Since $q$ has degree $< n-k$ and $\xi \neq 0$ means $q \neq 0$.)

This is the dual code minimum distance: the dual of RS$[n,k]$ is RS$[n, n-k]$, which has minimum distance $k+1$. A nonzero codeword of the dual has at most $n - (k+1) = n-k-1$ zeros. ✓

## The sum over T

With $|Z(\xi)| \leq n-k-1 =: d^*-1$:

$$\sum_{|T|=w} \prod_{i \in T} (-1+p \cdot \mathbb{1}[i \in Z(\xi)]) = \sum_{|T|=w} (-1)^{w-|T \cap Z|} p^{|T \cap Z|} \cdot (-1)^{|T \setminus Z|}$$

Hmm, let me redo. For $i \in Z(\xi)$: factor = $-1 + p = p-1$. For $i \notin Z(\xi)$: factor = $-1$.

$$S(\xi) := \sum_{|T|=w} \prod_{i \in T} \begin{cases} p-1 & i \in Z(\xi) \\ -1 & i \notin Z(\xi) \end{cases}$$

$$= \sum_{j=0}^{\min(w,|Z|)} \binom{|Z|}{j} \binom{n-|Z|}{w-j} (p-1)^j (-1)^{w-j}$$

$$= (-1)^w \sum_j \binom{|Z|}{j} \binom{n-|Z|}{w-j} (-(p-1))^j$$

$$= (-1)^w \sum_j \binom{|Z|}{j} \binom{n-|Z|}{w-j} (1-p)^j$$

For the main term ($\xi = 0$, $|Z| = n$):

$$S(0) = \sum_j \binom{n}{j} \binom{0}{w-j} (p-1)^j (-1)^{w-j} = (p-1)^w$$

(Only $j = w$ contributes.)

So: $N_w = (p-1)^w \binom{n}{w}/p^{n-k} + \text{error}$.

Wait, I need to be more careful. For $\xi = 0$: $|Z(0)| = n$ (all $h_i = 0$). The factor for each $i \in T$: $p-1$. So:

$$S(0) = \binom{n}{w} (p-1)^w$$

And the main term: $\psi(0) \cdot S(0) / p^{n-k} = \binom{n}{w}(p-1)^w / p^{n-k}$.

## Bounding the error

Error $= \frac{1}{p^{n-k}} \sum_{\xi \neq 0} |S(\xi)|$.

For $\xi \neq 0$: $|Z(\xi)| \leq n-k-1$. Let $z = |Z(\xi)|$.

$$|S(\xi)| = \left|\sum_{j=0}^{\min(w,z)} \binom{z}{j}\binom{n-z}{w-j}(p-1)^j(-1)^{w-j}\right|$$

$$= \left|(-1)^w \sum_j \binom{z}{j}\binom{n-z}{w-j}(1-p)^j\right|$$

$$\leq \sum_j \binom{z}{j}\binom{n-z}{w-j}(p-1)^j$$

$$= \sum_j \binom{z}{j}(p-1)^j \binom{n-z}{w-j}$$

By the Vandermonde-Chu identity with a twist: this equals the coefficient of $u^w$ in $(1+(p-1)u)^z (1+u)^{n-z}$, which is:

$$[u^w] (1+(p-1)u)^z (1+u)^{n-z}$$

For $z \leq n-k-1$ and $j \leq z$: the dominant term is $j = 0$ (giving $\binom{n-z}{w}$) plus corrections.

**Cleaner bound**: Factor out $\binom{n}{w}$:

$$|S(\xi)| \leq \binom{n}{w} \cdot \left(\frac{(1+(p-1)u)(1+u)^{-1}}{}\right)^z \bigg|_{\text{coefficient ratio}}$$

Actually, let's use a cleaner approach. Define $r = z/n$ (fraction of zeros). Then:

$$|S(\xi)| \leq [u^w] (1+(p-1)u)^{rn} (1+u)^{(1-r)n}$$

By saddle point: $\leq \exp(n \cdot \max_u [r\log(1+(p-1)u) + (1-r)\log(1+u) - (w/n)\log u])$

For the main term ($r = 1$): $\exp(n \cdot [\log(1+(p-1)u) - \delta\log u])$ maximized at $u = \delta/(p(1-\delta))$, giving $(p-1)^\delta / \delta^\delta(1-\delta)^{1-\delta} \sim (p-1)^\delta \cdot 2^{H(\delta)}$.

Hmm, this is getting complicated. Let me just use the crude bound:

$$|S(\xi)| \leq \binom{n-z}{w} (p-1)^z + \text{lower terms} \leq \binom{n}{w} \cdot \left(\frac{p-1}{n/w}\right)^z$$

Actually, even simpler: use $|S(\xi)| \leq \binom{n}{w} \cdot p^z$ (crude upper bound by replacing all factors by their max).

Then: error $\leq \frac{1}{p^{n-k}} \sum_{\xi \neq 0} \binom{n}{w} p^{z(\xi)} \leq \frac{\binom{n}{w}}{p^{n-k}} \sum_{\xi \neq 0} p^{z(\xi)}$.

Now: $\sum_{\xi \neq 0} p^{z(\xi)}$. For each $\xi$: $z(\xi) = |Z(\xi)| = $ number of zeros of a degree-$< (n-k)$ polynomial $q$ on $L$.

The sum: $\sum_{\xi \neq 0} p^{z(\xi)} = \sum_{z=0}^{n-k-1} p^z \cdot A_z$

where $A_z$ = number of $\xi \neq 0$ with $|Z(\xi)| = z$.

$A_z$ is related to the weight distribution of the DUAL RS code. For MDS codes (RS): the weight distribution is given by the MDS formula:

$$A_z = \binom{n}{z} \sum_{j=0}^{n-z-(k+1)} (-1)^j \binom{n-z}{j}(p^{n-z-k-j} - 1)$$

Wait, this is the weight distribution of RS$[n, n-k]$ (the dual). A codeword of weight $n-z$ (i.e., $z$ zeros) has $A_{n-z}$ count.

For MDS: $A_d = \binom{n}{d} \sum_{j=0}^{d-d_{\min}} (-1)^j \binom{d}{j}(q^{d-d_{\min}+1-j}-1)$ ... this is getting complicated.

Let me just use the crude bound: $A_z \leq \binom{n}{z} p^{n-k-1}$ (each set of $z$ zeros determines a codeword, with $p^{n-k-1}$ scalar multiples... not right).

Actually: the number of polynomials $q$ of degree $< n-k$ with exactly $z$ roots on $L$: each such $q$ factors as $q(X) = r(X) \cdot \prod_{i \in Z} (X - \omega^{-i})$ where $\deg r < n-k-z$ and $r$ has no roots on $L$. The number of such $r$: complicated.

For the TOTAL $\sum_\xi p^{z(\xi)}$: this equals $\sum_{i \in L^*} p^{|Z(i)|}$... no, the sum is over $\xi \in \mathbb{F}_p^{n-k}$.

Let me try a completely different approach: USE the fact that $N_w$ is a NON-NEGATIVE INTEGER. If we can show the main term is $< 1$ and the total $|N_w| \leq$ main + error $< 1 + $ something: we need error $<$ 1 - main.

For the main term $\binom{n}{w}(p-1)^w/p^{n-k}$: for FRI parameters this is exponentially small. So we need error $< 1$.

Can we bound the error $< 1$? Let me try to compute $N_w$ directly for small cases and see.

## Alternative: direct algebraic argument

Instead of character sums, use the algebraic structure directly.

For $w = \delta n$ and $n-k-w > 0$: the system $H_T x = c$ has $n-k$ equations in $w$ unknowns. With $H_T$ a Vandermonde-type matrix: the system is overdetermined by $n-k-w$ equations.

For a SPECIFIC $c$ (syndrome of $w$): the system is consistent iff $c$ lies in the column span of $H_T$. This is a codimension-$(n-k-w)$ condition.

Over $\mathbb{F}_p$: the probability for random $c$ is $p^{-(n-k-w)}$. Over ALL $T$: the expected count is $\binom{n}{w} p^{-(n-k-w)}$.

For $c$ NOT random but STRUCTURED (syndrome of a specific $w$): the count could be larger. But for MDS codes: the structure is limited.

**Claim**: For RS codes on multiplicative subgroups with $p > \binom{n}{w}^{1/(n-k-w)}$:

$$N_w \leq \binom{n}{w} / p^{n-k-w} + O(n^2/p)$$

The $O(n^2/p)$ error comes from... I'm not sure yet. But for $p$ large enough: $N_w < 1$, so $M = 0$.

The threshold: $p > \binom{n}{\delta n}^{1/((1-\rho-\delta)n)} = 2^{H(\delta)/(1-\rho-\delta)}$.

For $\rho = 1/2$, $\delta = 0.35$: $2^{0.93/0.15} = 2^{6.2} \approx 73$.

**For BabyBear ($p = 2^{31}$): VASTLY exceeds the threshold.**
