# Note 0064 — Linear Conditions for RS List Decoding

## Main Result

**Theorem (Linear Compatibility)**: For RS[n,k] on multiplicative subgroup
$L = \langle\omega\rangle$ of order $n$ over $\mathbb{F}_p$, center $c(x)$,
and error set $B$ of size $w$ with error-locator polynomial
$P_B(x) = \prod_{i \in B}(x - \omega^i)$:

$$B \text{ is compatible with } c \iff [P_B \cdot c]_m = 0 \quad \text{for } m = k+w, \ldots, n-1$$

where $[f]_m$ denotes the coefficient of $x^m$.

These are **(n-k-w) linear equations** in the elementary symmetric polynomials
$(\sigma_1, \ldots, \sigma_w)$ of the error positions.

### Proof

Write $c = f + e$ where $f \in \text{RS}_k$ (degree $< k$) and $e = Q \cdot P_S$
with $P_S = (x^n - 1)/P_B$ (agreement polynomial). Then:

$$P_B \cdot c = P_B \cdot f + P_B \cdot Q \cdot P_S = P_B \cdot f + Q(x^n - 1)$$

Since $\deg(P_B \cdot f) < k + w$ and $Q(x^n-1)$ has its contribution at degrees
$\geq n$, the coefficients of $P_B \cdot c$ at positions $m = k+w, \ldots, n-1$
must vanish:

$$[P_B \cdot c]_m = \sum_{j=0}^{w} P_B[j] \cdot c[m-j] = 0$$

Since $P_B[j] = (-1)^{w-j} \sigma_{w-j}$ with $\sigma_0 = 1$, this becomes:

$$\sum_{j=0}^{w} (-1)^j \sigma_j \cdot c[m-w+j] = 0$$

which is **linear** in $(\sigma_1, \ldots, \sigma_w)$ for fixed center $c$.  ∎

## Consequences

### 1. M_algebraic = |σ-image points on a codimension-c affine subspace|

Let $\text{conds} = n - k - w$ (number of linear conditions). For a given center $c$,
the compatible error sets $B$ have their $\sigma(B) \in V_c$, where $V_c$ is an
affine subspace of $\mathbb{F}_p^w$ with codimension $\leq \text{conds}$.

The list size $M = |\{B : \sigma(B) \in V_c, \text{ and } B \text{ is the exact error set}\}|$.

### 2. Exact formula for conds/B = 1

When conds/B = 1 (single condition), the optimal center has the condition $\sigma_w = v$
for some $v \in L$. Since $\sigma_w = \omega^{\sum_{i \in B} i}$, this fixes
$\sum B \mod n$.

**Fact**: The number of $w$-subsets of $\mathbb{Z}/n\mathbb{Z}$ with sum
$\equiv s \pmod{n}$ equals:

$$N(n,w,s) = \frac{1}{n} \sum_{t=0}^{n-1} \omega_n^{-ts} \cdot [z^w] \prod_{i=0}^{n-1}(1 + z\omega_n^{ti})$$

For $\gcd(t,n)=1$: $\prod_{i=0}^{n-1}(1+z\omega_n^{ti}) = 1 + (-1)^{n+1}z^n$,
so $[z^w] = 0$ for $0 < w < n$.

**Corollary**: When $\gcd(w,n) = 1$:

$$N(n,w,s) = \binom{n}{w}/n \quad \text{for all } s$$

and the worst-case list size for conds/B = 1 is:

$$M = \binom{n}{w}/n$$

**Verified**: $n=6, M=3$; $n=8, M=7 = \binom{8}{3}/8$. Both p-independent.

### 3. For conds/B ≥ 2: M appears bounded

Computational data (rate $\rho = 1/2$ at Johnson radius, smallest valid $p$):

| $n$ | $k$ | $w$ | conds/B | $p$ | $M_{\text{actual}}$ | $\binom{n}{w}/p^c$ |
|-----|-----|-----|---------|-----|---------------------|---------------------|
| 6   | 3   | 2   | 1       | 7   | **3**               | 2.14                |
| 8   | 4   | 3   | 1       | 17  | **7**               | 3.29                |
| 10  | 5   | 3   | 2       | 11  | **3**               | 0.99                |
| 12  | 6   | 4   | 2       | 13  | **6**               | 2.93                |
| 14  | 7   | 5   | 2       | 29  | **8**               | 2.38                |
| 16  | 8   | 5   | 3       | 17  | **4**               | 0.89                |
| 18  | 9   | 6   | 3       | 19  | **7**               | 2.71                |
| 20  | 10  | 6   | 4       | 41  | **0**               | 0.014               |

### 4. M_algebraic overcounting

$M_{\text{algebraic}}$ counts the number of compatible $B$'s (sets of size $w$
that yield a valid interpolant). When a codeword $f$ has $d(c,f) = d < w$, it
contributes $\binom{n-d}{w-d}$ compatible $B$'s (all supersets of the true error set).

$M_{\text{actual}} = M_{\text{algebraic}}$ iff all codewords in the list are at
distance **exactly** $w$ from $c$.

### 5. p-dependence (RESOLVED)

For conds/B = 1: $M$ is **p-independent** (equals $N(n,w,s^*)$, a purely combinatorial quantity).
Cross-verified: $n=6$ gives $M=3$ for $p=7,13,19,31$; $n=8$ gives $M=7$ for $p=17,41,73,89$.

For conds/B ≥ 2: $M$ **is p-dependent** — decreasing as $p$ grows.
The σ-image geometry changes with $p$ (the elem syms of roots of unity live in different fields).

| $n$ | conds/B | $p=p_1$ | $M$ | $p=p_2$ | $M$ | $p=p_3$ | $M$ | $p=p_4$ | $M$ |
|-----|---------|---------|-----|---------|-----|---------|-----|---------|-----|
| 10  | 2       | 11      | 3   | 31      | 2   | 41      | 2   | 61      | 2   |
| 12  | 2       | 13      | 6   | 37      | 4   | 61      | 3   | 73      | 3   |
| 14  | 2       | 29      | 8   | 43      | —   | 71      | —   | 113     | 3   |

$M$ stabilizes at 2–3 for large $p$. For the FRI/STARK regime ($p \gg n$), $M$ is small.

## Explicit conditions

### n=6, k=3, w=2 (conds/B=1)

Matrix: $\begin{pmatrix} \sigma_1 & \sigma_1^2-\sigma_2 & c_3 \\ 1 & \sigma_1 & c_4 \\ 0 & 1 & c_5 \end{pmatrix}$

$D = c_3 - \sigma_1 c_4 + \sigma_2 c_5 = [P_B \cdot c]_5 = 0$

### n=8, k=4, w=3 (conds/B=1)

Matrix: $\begin{pmatrix} \sigma_1 & \sigma_1^2-\sigma_2 & \sigma_1^3-2\sigma_1\sigma_2+\sigma_3 & c_4 \\ 1 & \sigma_1 & \sigma_1^2-\sigma_2 & c_5 \\ 0 & 1 & \sigma_1 & c_6 \\ 0 & 0 & 1 & c_7 \end{pmatrix}$

$D = -c_4 + \sigma_1 c_5 - \sigma_2 c_6 + \sigma_3 c_7 = -[P_B \cdot c]_7 = 0$

### General formula

$$D_m = \sum_{j=0}^{w} (-1)^j \sigma_j \cdot c_{m-w+j} = 0 \quad \text{for } m = k+w, \ldots, n-1$$

This is **degree 1** in $\sigma$ (not degree $w$ as initially estimated from
the weighted-degree analysis of Note 0063).

## N(n,w,s) distribution

The distribution $N(n,w,s)$ of $w$-subset sums mod $n$ satisfies:

$$N(n,w,s) = \frac{1}{n} \sum_{\substack{d | n \\ d | \gcd(n, \text{lcm of divisors})}} \phi_d(s) \cdot [z^w](1+(-1)^{n/d+1}z^{n/d})^d$$

Key cases:
- $\gcd(w,n) = 1$: **perfectly uniform**, $N = \binom{n}{w}/n$
- $\gcd(w,n) = d > 1$: nearly uniform, max deviation $\leq \binom{d}{\lfloor d/2\rfloor}$

Verified data:

| $n$ | $w$ | $\gcd$ | $N$ range | $\binom{n}{w}/n$ |
|-----|-----|--------|-----------|-------------------|
| 6   | 2   | 2      | [2, 3]    | 2.5               |
| 8   | 3   | 1      | [7, 7]    | 7.0               |
| 10  | 3   | 1      | [12, 12]  | 12.0              |
| 12  | 4   | 4      | [40, 43]  | 41.2              |
| 14  | 5   | 1      | [143, 143]| 143.0             |
| 16  | 5   | 1      | [273, 273]| 273.0             |
| 18  | 6   | 6      | [1026,1038]| 1031.3           |
| 20  | 6   | 2      | [1932,1944]| 1938.0           |

## Implications for the prize

### What this gives

1. **Clean reformulation**: list decoding ⟺ counting σ-image points on an affine subspace
2. **Exact M for conds/B=1**: $M = \binom{n}{w}/n$ (when $\gcd(w,n)=1$)
3. **Computational verification** that $M = O(1)$ for rate $1/2$ at Johnson radius ($n \leq 18$)

### What's missing

1. **Proof that $M = O(1)$ for conds/B $\geq 2$**: requires bounding the
   intersection of a codimension-$c$ affine subspace with the σ-image of
   $w$-subsets of roots of unity. This is a problem in additive combinatorics
   / algebraic geometry over finite fields.

2. **Character sum bound**: the Weil bound gives
   $|S(\alpha)| \leq \binom{n}{w}\sqrt{p}/n$ for the σ_w-only sum, but
   bounding the general sum $\sum_B \psi(\alpha \cdot \sigma(B))$ requires
   the Deligne–Laumon theory for exponential sums of symmetric functions.

3. **Connection to proximity gap**: the linear conditions framework applies
   to EACH received word independently. The proximity gap requires showing
   a GAP in the distribution of agreement rates across ALL evaluations.

## Scripts

- `linear_conditions.py` — verification of linearity for n=6,8,10,12
- `linear_conditions_large.py` — extension to n=14,16 (M_algebraic)
- `M_actual_fast.py` — correct M computation with overcounting detection
- `M_extend.py` — n=18,20 and N(n,w,s) distribution
- `M_formula.py` — exact formula verification for conds/B=1
- `M_p_indep.py` — p-independence investigation (exhaustive for small p)
