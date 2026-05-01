# Note 0053 — The BGK Approach to List Decoding

## The reformulated counting problem

$N_w$ = number of pairs $(T, \mathbf{t})$ with $|T| = w$, $\mathbf{t} \in (\mathbb{F}_p^*)^w$, such that:

$$\sigma_r(T, \mathbf{t}) := \sum_{i \in T} t_i \omega^{-(r+k)i} = c_r \quad \text{for } r = 0, \ldots, n-k-1$$

## Change of variables

For each $i \in T$: define $x_i = t_i \cdot \omega^{-ki} \in \mathbb{F}_p^*$. Then:

$$\sigma_r = \sum_{i \in T} t_i \omega^{-(r+k)i} = \sum_{i \in T} x_i \omega^{-ri}$$

The conditions become: $\sum_{i \in T} x_i \omega^{-ri} = c_r$ for $r = 0, \ldots, n-k-1$.

This is: the DFT of the "signed indicator" $e(j) = x_j \mathbb{1}[j \in T]$ at frequencies $0, 1, \ldots, n-k-1$ equals prescribed values.

Equivalently: define $e: \mathbb{Z}/n\mathbb{Z} \to \mathbb{F}_p$ by $e(j) = x_j$ if $j \in T$, $e(j) = 0$ otherwise. Then:

$$\hat{e}(r) = \sum_{j=0}^{n-1} e(j) \omega^{-rj} = c_r \quad \text{for } r = 0, \ldots, n-k-1$$

And: $\text{wt}(e) = |T| = w$, $e(j) \neq 0$ for $j \in T$.

## The key observation: this is a LINEAR SYSTEM

The conditions $\hat{e}(r) = c_r$ for $r = 0, \ldots, n-k-1$ are $n-k$ LINEAR equations in $n$ unknowns $e(0), \ldots, e(n-1)$.

With the constraint $\text{wt}(e) = w$ (exactly $w$ nonzero entries): this is a SPARSE solution to a linear system.

## Count via combinatorics + linear algebra

For a fixed support $T$ (size $w$): the system has $n-k$ equations in $w$ unknowns $\{e(j) : j \in T\}$. For MDS: the system has rank $\min(w, n-k)$.

For $w \leq n-k$: rank = $w$. The system is consistent iff $c \in \text{Col}(H_T)$ (codimension $n-k-w$). If consistent: unique solution. Need to check $e(j) \neq 0$ for all $j \in T$.

So: $N_w = |\{T : |T|=w, c \in \text{Col}(H_T), e_T^* \in (\mathbb{F}_p^*)^w\}|$

where $e_T^*$ is the unique solution.

## The approach: bound the "bad" T count

For MDS: $c \in \text{Col}(H_T)$ is $n-k-w$ conditions. "Expected" count: $\binom{n}{w} / p^{n-k-w}$.

Need to show: actual count $\leq \binom{n}{w}/p^{n-k-w} + \text{error}$ with error $< 1$.

## Using the SECOND MOMENT METHOD

Define $X_T = \mathbb{1}[c \in \text{Col}(H_T)]$ for $|T| = w$. Then $N_w^* = \sum_T X_T$.

$\mathbb{E}[N_w^*]$ (over random $c$) $= \binom{n}{w} / p^{n-k-w}$ = main.

$\text{Var}[N_w^*] = \sum_{T_1, T_2} (\mathbb{E}[X_{T_1} X_{T_2}] - \mathbb{E}[X_{T_1}]\mathbb{E}[X_{T_2}])$.

$\mathbb{E}[X_{T_1} X_{T_2}] = \Pr[c \in \text{Col}(H_{T_1}) \cap \text{Col}(H_{T_2})]$.

The intersection $\text{Col}(H_{T_1}) \cap \text{Col}(H_{T_2})$: has dimension $w_1 + w_2 - \text{rank}(H_{T_1 \cup T_2})$ where $w_1 = w_2 = w$.

For MDS: $\text{rank}(H_{T_1 \cup T_2}) = \min(|T_1 \cup T_2|, n-k)$.

$|T_1 \cup T_2| = 2w - |T_1 \cap T_2|$. For $|T_1 \cap T_2| = s$: rank $= \min(2w-s, n-k)$.

If $2w - s \leq n-k$: rank $= 2w-s$, intersection dim $= 2w - (2w-s) = s$.
If $2w - s > n-k$: rank $= n-k$, intersection dim $= 2w - (n-k)$.

For the intermediate zone ($w < n-k$): $2w < 2(n-k)$, so $2w - s \leq 2w < 2(n-k)$. For $s < 2w - (n-k)$: rank $= n-k$, intersection dim $= 2w - (n-k)$. For $s \geq 2w - (n-k)$: rank $= 2w-s$, intersection dim $= s$.

$\Pr[c \in \text{intersection}] = p^{-\text{codim(intersection)}} = p^{-(n-k-\text{dim})}$.

Case $s \geq 2w-(n-k)$: $\Pr = p^{-(n-k-s)}$.
Case $s < 2w-(n-k)$: $\Pr = p^{-(n-k-(2w-(n-k)))} = p^{-(2(n-k)-2w)}$.

The variance:

$$\text{Var} = \sum_{s=0}^{w} \binom{n}{w,s,w-s} \cdot (p^{-(n-k-s)} - p^{-2(n-k-w)})$$

where $\binom{n}{w,s,w-s}$ counts pairs $(T_1, T_2)$ with $|T_1 \cap T_2| = s$.

$\binom{n}{w,s,w-s} = \binom{n}{s}\binom{n-s}{w-s}\binom{n-w}{w-s}$ (choose intersection, then the rest of each).

For the DOMINANT term ($s = 0$): $\binom{n}{w}^2 \cdot (p^{-(n-k)} - p^{-2(n-k-w)})$.

For $n-k > 2(n-k-w)$ i.e. $w > (n-k)/2$: the first term dominates. $\text{Var} \approx \binom{n}{w}^2 p^{-(n-k)}$.

The ratio $\text{Var}/\mathbb{E}^2 \approx \binom{n}{w}^2 p^{-(n-k)} / (\binom{n}{w}/p^{n-k-w})^2 = p^{-(n-k)} \cdot p^{2(n-k-w)} = p^{n-k-2w}$.

For $w > (n-k)/2$: ratio $< 1$. Paley-Zygmund: $\Pr[N_w^* > 0] \geq \mathbb{E}^2 / \mathbb{E}[N_w^{*2}]$.

Hmm, the second moment gives: for RANDOM $c$, $N_w^*$ is concentrated around its mean. But we need a bound for the WORST $c$.

## For worst-case $c$: Markov's inequality on $N_w^*$

$\mathbb{E}_c[N_w^*] = \text{main}$. By Markov: $\Pr[N_w^* \geq m] \leq \text{main}/m$.

For $m = 1$: $\Pr[N_w^* \geq 1] \leq \text{main}$. If main $< 1$: most $c$'s have $N_w^* = 0$.

But this is for AVERAGE $c$, not worst case!

## The worst case: Singleton-type bound

From the MDS weight distribution: the maximum weight-$w$ count over all cosets:

$\max_c N_w(c) \leq A_w(\text{dual code}) + \text{correction}$?

No, this is not right. The coset weight distribution can exceed the code weight distribution.

## The key tool missing: a POINTWISE bound on $N_w(c)$ for ALL $c$

This is exactly the list-decoding problem. The second moment method gives an AVERAGE bound but not a pointwise bound.

For a POINTWISE bound: we need the character-sum estimate (which gives uniform control over $c$ via the exponential sum).

OR: we need an ALGEBRAIC argument that bounds $N_w(c)$ using the structure of MDS codes.

## Algebraic approach: the number of $w$-subsets of $L$ with $c \in \text{Col}(H_T)$

This is the number of $w$-planes (from Vandermonde columns) containing $c$.

For GENERIC $c$: this is $\binom{n}{w}/p^{n-k-w}$ (by counting).

For SPECIAL $c$ (e.g., $c = v_i$ for some $i$): this is $\binom{n-1}{w-1}/p^{n-k-w}$ (we must include column $i$).

The MAXIMUM over all $c$: bounded by the maximum "covering number" of Vandermonde planes.

## Conjecture (for Gong)

For RS$[\mathbb{F}_p, L, k]$ with $L$ multiplicative subgroup of order $n$ and $p > n^C$:

$$\max_c |\{T \subset L : |T| = w, c \in \text{Col}(H_T)\}| \leq \frac{\binom{n}{w}}{p^{n-k-w}} + O(1)$$

The $O(1)$ error would give $M = O(1)$ in the FRI regime.

This is a statement about the "regularity" of Vandermonde planes — that no point is covered by too many more planes than average. This is a **discrepancy** or **uniformity** statement for the Vandermonde configuration in $\mathbb{F}_p^{n-k}$.

For RANDOM vectors (not Vandermonde): the discrepancy is $O(\sqrt{\text{main}})$ (Chernoff bound). For Vandermonde: the discrepancy should be similar, by the "pseudorandomness" of Vandermonde vectors.

The BGK result (Bourgain-Glibichuk-Konyagin) is precisely a pseudorandomness statement for elements of multiplicative subgroups: exponential sums are small. The connection: the covering number of Vandermonde planes is an exponential sum (by the indicator-to-character decomposition).

**This IS the bridge between BGK and list-decoding.**
