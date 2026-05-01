# Note 0049 — Proof: M = 0 for RS on Multiplicative Subgroups when p > threshold

## Theorem

For RS$[\mathbb{F}_p, L, k]$ with $L \subset \mathbb{F}_p^*$ multiplicative subgroup of order $n$, $p > n$, and agreement threshold $t = (1-\delta)n$ with $\delta > \delta_J(\rho)$:

If $p > \binom{n}{\lfloor\delta n\rfloor}^{1/\lfloor(1-\rho-\delta)n\rfloor}$, then $M_\delta(w) = 0$ for ALL words $w$.

In particular: for $\rho = 1/2$ and $\delta \in (0.3, 0.5)$: the threshold is $< 100$ for all $n$. Every prime $p > 100$ gives $M = 0$.

## Proof

### Step 1: Reformulation

$M_\delta(w)$ = number of codewords $h \in \text{RS}_k$ with $\text{wt}(w - h) \leq \delta n$.

Equivalently: number of error vectors $e = w - h$ with $\text{wt}(e) \leq \delta n$ and $He^T = c$ where $c = Hw^T$ is the syndrome.

For EXACT weight $w_e$: $N_{w_e} = \#\{e : \text{wt}(e) = w_e, He^T = c, \text{all nonzero on support}\}$.

$M = \sum_{w_e=1}^{\lfloor\delta n\rfloor} N_{w_e}$ (plus possibly 1 if $w \in \text{RS}_k$, but this is independent of the bound).

### Step 2: Upper bound on $N_{w_e}$

Fix $w_e = w$. We count pairs $(T, x)$ with $T \subset [n]$, $|T| = w$, $x \in (\mathbb{F}_p^*)^w$, $\sum_{i \in T} x_i H_{\cdot,i} = c$.

For a fixed $T$: the system $H_T \cdot x = c$ is a linear system over $\mathbb{F}_p$ with $n - k$ equations and $w$ unknowns. The matrix $H_T$ is a $(n-k) \times w$ Vandermonde submatrix.

**MDS property**: Any $n-k$ columns of $H$ are linearly independent (RS codes are MDS). So for $w \leq n-k$: the columns of $H_T$ are linearly independent, and the system has AT MOST one solution.

The system has a solution iff $c \in \text{Col}(H_T)$, the $w$-dimensional column span. Since the ambient space has dimension $n-k$: this is a codimension-$(n-k-w)$ condition.

### Step 3: Counting consistent supports

**Claim**: The number of $w$-subsets $T \subset [n]$ with $c \in \text{Col}(H_T)$ is at most $\binom{n}{w} / p^{n-k-w}$ (for $p$ large enough).

**Proof via character sums**:

$$N_w^* := \#\{T : |T| = w, c \in \text{Col}(H_T)\} = \frac{1}{p^{n-k-w}} \sum_{\eta \in \mathbb{F}_p^{n-k-w}} \sum_{|T|=w} \psi(\langle \eta, \pi_T(c) \rangle)$$

Actually, a cleaner approach: the condition $c \in \text{Col}(H_T)$ is equivalent to: $\xi^T c = 0$ for all $\xi \in \ker(H_T^T)$. Since $H_T$ has rank $w$: $\ker(H_T^T)$ has dimension $n-k-w$.

Choose a basis $\xi_1, \ldots, \xi_{n-k-w}$ of $\ker(H_T^T)$. The condition: $\xi_j^T c = 0$ for $j = 1, \ldots, n-k-w$.

Using characters:

$$\mathbb{1}[c \in \text{Col}(H_T)] = \frac{1}{p^{n-k-w}} \sum_{\lambda \in \mathbb{F}_p^{n-k-w}} \psi\left(\sum_{j=1}^{n-k-w} \lambda_j \xi_j^T c\right)$$

But the basis $\xi_j$ depends on $T$! This makes the formula messy.

### Step 3 (Alternative): Direct counting

For each $T$: the $w$ columns of $H$ indexed by $T$ span a $w$-dimensional subspace $V_T \subset \mathbb{F}_p^{n-k}$. We need $c \in V_T$.

The number of such $T$: $\#\{T : c \in V_T\}$.

**Upper bound**: Consider the "dual" question. For each $i \in [n]$: define $v_i = H_{\cdot,i} \in \mathbb{F}_p^{n-k}$ (the $i$-th column of $H$). These are $n$ vectors in $\mathbb{F}_p^{n-k}$.

$c \in V_T$ iff $c = \sum_{i \in T} x_i v_i$ for some $x \in \mathbb{F}_p^w$. Since the $v_i$ are in "general position" (MDS): for $|T| = w \leq n-k$, the span $V_T$ is a generic $w$-dimensional subspace.

**The number of $w$-subsets whose span contains $c$**: This is a combinatorial geometry question. For $c \neq 0$:

$c \in V_T$ iff the $(w+1)$-subset $T \cup \{*\}$ (where $*$ represents the "column" for $c$) is linearly dependent in $\mathbb{F}_p^{n-k}$. But $c$ is not a column of $H$.

Better approach: $c \in V_T$ iff the system $\sum_{i \in T} x_i v_i = c$ has a solution. With the $v_i$ in general position: this requires a specific alignment.

**The probabilistic argument**: If we choose $c$ uniformly at random from $\mathbb{F}_p^{n-k}$:

$$\mathbb{E}[\#\{T : c \in V_T\}] = \sum_T \Pr[c \in V_T] = \binom{n}{w} \cdot \frac{p^w}{p^{n-k}} = \frac{\binom{n}{w}}{p^{n-k-w}}$$

(Since $V_T$ has $p^w$ elements and the ambient space has $p^{n-k}$ elements.)

For $c$ NOT random but the syndrome of a specific $w$: the count could deviate. But for the Vandermonde structure of $H$: the deviation is bounded.

### Step 4: Bounding the deviation via Weil

**Claim**: For the RS parity check matrix $H$ (Vandermonde), and ANY $c \in \mathbb{F}_p^{n-k}$:

$$\#\{T : |T| = w, c \in V_T\} \leq \frac{\binom{n}{w}}{p^{n-k-w}} + E$$

where $E \leq \binom{n}{w} \cdot n \cdot p^{-1/2}$ (Weil-type error).

For $E < 1 - \text{main}$: $N_w^* < 1$, so $N_w^* = 0$ (integer).

This requires: $\binom{n}{w} / p^{n-k-w} + \binom{n}{w} \cdot n / \sqrt{p} < 1$.

The SECOND term dominates for small $p$. Need $\binom{n}{w} \cdot n / \sqrt{p} < 1$, i.e., $p > n^2 \binom{n}{w}^2$.

This is MUCH weaker than the heuristic! For $w = \delta n$: $p > n^2 \cdot 2^{2H(\delta)n}$. This is EXPONENTIAL in $n$.

**This approach fails for practical parameters.**

### Step 5: Better approach — exploit the overdetermined structure

The key: the system $H_T x = c$ has $n-k$ equations and $w < n-k$ unknowns. The last $n-k-w$ equations are "check equations" that $c$ must satisfy GIVEN the first $w$ equations determine $x$.

For the Vandermonde matrix: the first $w$ rows of $H_T$ determine $x$ uniquely (since $H_T$ has rank $w$). The remaining $n-k-w$ rows give POLYNOMIAL conditions on the entries of $T$.

Specifically: write $H_T = [v_{i_1}, \ldots, v_{i_w}]$ where $v_j = (\omega^{-kj}, \omega^{-(k+1)j}, \ldots, \omega^{-(n-1)j})^T$. The system $H_T x = c$ determines $x$ from the first $w$ rows (Vandermonde inversion). The remaining rows give:

$$\sum_{\ell=1}^w x_\ell \omega^{-(r+k)i_\ell} = c_r \quad \text{for } r = w, w+1, \ldots, n-k-1$$

With $x_\ell$ determined by the first $w$ equations: $x_\ell = L_\ell(c_0, \ldots, c_{w-1}; i_1, \ldots, i_w)$ (Lagrange interpolation formula, rational in the $\omega^{-i_\ell}$).

Substituting: the last $n-k-w$ equations become POLYNOMIAL conditions on $(i_1, \ldots, i_w)$ (with $i_j \in [n]$, i.e., discrete variables).

These are polynomial equations on the symmetric group / subset lattice. The number of solutions: bounded by the DEGREE of the polynomial system times $n^{w - \dim}$ (where dim is the dimension of the solution variety).

**For the Vandermonde system**: the polynomial conditions have specific degree bounds. Each "check equation" involves a rational function of degree $O(w)$ in the positions $\omega^{-i_\ell}$. After clearing denominators: polynomial of degree $O(w^2)$.

With $n-k-w$ such conditions: by Bezout, the number of solutions is at most $O(w^2)^{n-k-w}$ in the continuous setting, intersected with the discrete set $[n]^w$.

**By Schwartz-Zippel over the discrete set $[n]$**:

Each condition is a polynomial of degree $\leq D$ in $w$ variables, evaluated on $[n]^w$ (actually on $\binom{n}{w}$ subsets, but treat as $n^w$ with overcounting). By SZ: each condition is satisfied on $\leq D \cdot n^{w-1}$ tuples. With $n-k-w$ independent conditions:

$$\#\text{solutions} \leq D^{n-k-w} \cdot n^{w-(n-k-w)} = D^{n-k-w} \cdot n^{2w-n+k}$$

For this $< 1$: need $D^{n-k-w} \cdot n^{2w-n+k} < 1$.

With $D = O(w)$: $w^{n-k-w} \cdot n^{2w-n+k} < 1$.

For $\rho = 1/2$, $\delta = 0.35$, $w = 0.35n$, $k = 0.5n$:
- $n-k-w = 0.15n$
- $2w-n+k = 0.7n - n + 0.5n = 0.2n$
- Bound: $(0.35n)^{0.15n} \cdot n^{0.2n} = n^{0.15n\log(0.35n)/\log n + 0.2n}$

For large $n$: this is $\approx n^{0.35n}$ (very large). **Doesn't work.**

## Step 6: The CORRECT approach (finally)

The key insight I've been missing: **don't iterate SZ over the variables — use the INTEGRALITY of $N_w$.**

From the character-sum formula:

$$N_w = \frac{\binom{n}{w}(p-1)^w}{p^{n-k}} + R$$

where $R = \frac{1}{p^{n-k}} \sum_{\xi \neq 0} \psi(-\langle\xi,c\rangle) S(\xi)$.

$N_w$ is a non-negative integer. If $|R| < 1 - \text{main}$: then $N_w = 0$ (since main + R < 1 and $N_w \geq 0$).

For main $< 1/2$: need $|R| < 1/2$.

**Bounding $|R|$**: 

$$|R| \leq \frac{1}{p^{n-k}} \sum_{\xi \neq 0} |S(\xi)|$$

With $|S(\xi)| \leq \binom{n}{w} \cdot \max_{z \leq n-k-1} \left(\frac{p-1}{\binom{n-z}{w}/\binom{n}{w}}\right)^z$...

This is still hard. Let me try a VERY CRUDE bound: $|S(\xi)| \leq \binom{n}{w} (p-1)^{n-k-1}$ (using $z \leq n-k-1$ and each factor $(p-1)$).

Then: $|R| \leq (p^{n-k}-1) \binom{n}{w} (p-1)^{n-k-1} / p^{n-k} \leq \binom{n}{w} (p-1)^{n-k-1}/p \leq \binom{n}{w} p^{n-k-2}$.

This is HUGE. The crude bound is useless.

**The real bound**: most $\xi$ have $|Z(\xi)|$ much smaller than $n-k-1$. In fact, for "generic" $\xi$: $|Z(\xi)| = 0$ (the polynomial $q$ has no roots on $L$). 

The fraction of $\xi$ with $|Z(\xi)| \geq 1$: for each root $\omega^{-i}$, the condition $q(\omega^{-i}) = 0$ is one linear equation on $\xi$ (since $q(\omega^{-i}) = \sum_r \xi_r \omega^{-ri}$). The number of $\xi$ with this root: $p^{n-k-1}$. Total for any root: $\leq n \cdot p^{n-k-1}$.

So: $\#\{\xi : |Z(\xi)| \geq 1\} \leq n \cdot p^{n-k-1}$ (union bound).

For these $\xi$: $|S(\xi)| \leq \binom{n}{w}(p-1)$ (using $z = 1$, so one factor of $(p-1)$ and the rest are $(-1)$'s). Actually:

For $z = |Z| = 1$: $S(\xi) = (-1)^w [\binom{n-1}{w}(1-p) + \binom{n-1}{w-1}] = (-1)^w [\binom{n-1}{w} - (p-1)\binom{n-1}{w-1} + ...]$

Hmm, let me just compute $|S(\xi)|$ for $z = 1$:

$S = \binom{1}{0}\binom{n-1}{w}(-1)^w + \binom{1}{1}\binom{n-1}{w-1}(p-1)(-1)^{w-1}$
$= (-1)^w [\binom{n-1}{w} - (p-1)\binom{n-1}{w-1}]$
$|S| = |\binom{n-1}{w} - (p-1)\binom{n-1}{w-1}|$

For $p \gg n$: $\approx (p-1)\binom{n-1}{w-1} \approx p \binom{n}{w} w/n$.

So: for $z = 1$: $|S| \approx p \binom{n}{w}/n$.

The contribution to $|R|$ from $z \geq 1$:
$\leq \frac{1}{p^{n-k}} \cdot n p^{n-k-1} \cdot p \binom{n}{w}/n = \binom{n}{w}$

This is STILL ≥ 1 for $\binom{n}{w} \geq 1$. The bound doesn't help!

**The issue**: the $z = 1$ terms contribute $O(\binom{n}{w})$ to the error, which matches the main term. The cancellation between different $\xi$'s (via the phase $\psi(-\langle\xi,c\rangle)$) is essential.

Without exploiting the phase cancellation: the bound is $O(\binom{n}{w})$, which is useless.

**To exploit phase cancellation**: need the sum $\sum_\xi \psi(-\langle\xi,c\rangle) S(\xi)$ to cancel. This requires $S(\xi)$ to vary "randomly" with $\xi$, or more precisely, to be "uncorrelated" with $\psi(\langle\xi,c\rangle)$.

For the Vandermonde matrix $H$: $\langle\xi,c\rangle = \sum_r \xi_r c_r = \sum_r \xi_r \sum_i w_i \omega^{-(r+k)i} = \sum_i w_i \sum_r \xi_r \omega^{-(r+k)i} = \sum_i w_i h_i(\xi)$.

So: $\psi(-\langle\xi,c\rangle) = \prod_i \psi(-w_i h_i(\xi))$.

And $S(\xi) = \sum_{|T|=w} \prod_{i \in T} (-1+p\mathbb{1}[h_i(\xi)=0])$.

The product $\psi(-\langle\xi,c\rangle) \cdot S(\xi)$ involves both the phase and the indicator. The sum over $\xi$: this is a character sum of a product of functions of $h_i(\xi)$.

Since $h_i(\xi) = \xi^T v_i$ (a linear form in $\xi$): the sum over $\xi$ is a multi-dimensional character sum over $\mathbb{F}_p^{n-k}$, with the constraint that $h_i$ are linear forms evaluated at $\xi$.

This is getting deep into the character-sum territory. I think the RIGHT tool is:

**The exponential sum bound for polynomial phase functions over $\mathbb{F}_p^m$:**

$\left|\sum_{\xi \in \mathbb{F}_p^m} F(\xi)\right| \leq C \cdot p^{m/2}$ for "generic" $F$.

But $F$ here involves indicators ($\mathbb{1}[h_i = 0]$) and phases ($\psi$), making it non-smooth. The Weil bound doesn't directly apply.

## Conclusion (this note)

The character-sum approach to proving $M = 0$ requires bounding a MULTI-DIMENSIONAL character sum with indicator functions. This is beyond simple Weil bounds — it requires tools from additive combinatorics (Bourgain-Katz-Tao, sum-product) or the Katz-Laumon formalism for l-adic sheaves.

**This is exactly the kind of problem Gong works on.** The clean formulation:

> For the Vandermonde matrix $H$ of RS$[n, k]$ over $\mathbb{F}_p$: bound $\sum_{\xi \in \mathbb{F}_p^{n-k}} \psi(-\langle\xi,c\rangle) \cdot e_w(\phi_\xi(0), \ldots, \phi_\xi(n-1))$ where $\phi_\xi(i) = -1 + p \cdot \mathbb{1}[\xi^T v_i = 0]$.

This is a character-sum formulation of the RS list-decoding problem. A bound of $o(p^{n-k})$ on this sum would give $M = 0$ for $p$ above the threshold.
