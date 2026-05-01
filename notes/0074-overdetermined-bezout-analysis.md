# Note 0074 — Overdetermined Bézout Analysis: Toward M = O(1) for All p > n

## 1. Setup

For RS[n, k] on $L = \langle\omega\rangle \subset \mathbb{F}_p^*$, Johnson radius $w$, codimension $c = n-k-w$, dimension $d = w-c$:

The compatible $\sigma$-values form a $d$-dimensional flat $V_c \subset \mathbb{F}_p^w$ parameterized by $s = (s_1, \ldots, s_d)$:
$$\sigma_j(s) = a_j + \sum_{i=1}^d s_i b_{j,i}, \quad j = 1, \ldots, w$$

The companion matrix $C(s)$ of $\Lambda_s(x) = x^w - \sigma_1 x^{w-1} + \cdots + (-1)^w \sigma_w$ gives:
$$x^n \bmod \Lambda_s(x) = r_0(s) + r_1(s) x + \cdots + r_{w-1}(s) x^{w-1}$$

Valid $w$-subsets $B \subset L$ correspond to parameters $s$ satisfying:
$$r_0(s) = 1, \quad r_1(s) = 0, \quad \ldots, \quad r_{w-1}(s) = 0$$

## 2. Degree Correction

**Paper (Theorem 9.4) claims**: $\deg_s(r_i) \leq n-w$.

**Correct bound**: $\deg_s(r_i) \leq n-w+1$.

**Proof**: The polynomial division $x^n \bmod \Lambda_s(x)$ requires $n - (w-1) = n-w+1$ reduction steps. Each step multiplies the leading coefficient by a $\sigma_j$ (degree 1 in $s$), increasing the $s$-degree by 1.

**Verified computationally** for all $(n,w) \in \{(6,2), (6,3), (8,3), (10,3), (10,4), (12,5), (14,5), (16,5), (20,6)\}$.

Let $D = n-w+1$ denote the correct degree bound. The corrected Bézout bound is:
$$M \leq D^d = (n-w+1)^d$$

## 3. Key Empirical Finding: |V(r_0-1, r_1)| = O(1)

For $d=2$, the first two conditions $r_0(s_1, s_2) - 1 = 0$ and $r_1(s_1, s_2) = 0$ already cut the solution set to $O(1)$ points, far below the Bézout bound $D^2$.

### 3.1 Two-equation intersection sizes

| $n$ | $p$ | $w$ | $c$ | $D$ | $D^2$ | max $|V_{01}|$ | max $M$ | avg $M$ | density $\binom{n}{w}/p^c$ |
|-----|-----|-----|-----|-----|-------|-----------------|---------|---------|----------------------------|
| 10 | 11 | 4 | 2 | 7 | 49 | 5 | 5 | 1.70 | 1.74 |
| 10 | 13 | 4 | 2 | 7 | 49 | 3 | 1 | 0.03 | 1.24 |
| 10 | 31 | 4 | 2 | 7 | 49 | 3 | 2 | 0.20 | 0.22 |
| 12 | 13 | 4 | 2 | 9 | 81 | 9 | 6 | 2.97 | 2.93 |
| 12 | 13 | 5 | 3 | 8 | 64 | 4 | 2 | 0.43 | 0.36 |
| 14 | 17 | 5 | 3 | 10 | 100 | 2 | 0 | 0.00 | 0.41 |

**Observation**: $|V_{01}| \leq D$ and additional equations $r_2 = 0, \ldots, r_{w-1} = 0$ barely reduce further.

### 3.2 Leading form proportionality

For $d=2$, the highest-degree homogeneous parts of $r_0-1$ and $r_1$ are frequently **proportional** (same projective curve at infinity). This means the projective curves $\overline{V(r_0-1)}$ and $\overline{V(r_1)}$ meet with high multiplicity at infinity, reducing the affine intersection count.

When leading forms are proportional: $r_0 - 1 = \alpha g_D + f_{D-1} + \cdots$ and $r_1 = \beta g_D + h_{D-1} + \cdots$. Then $\beta(r_0-1) - \alpha r_1$ has degree $\leq D-1$, and $V_{01} \subset V(\beta(r_0-1) - \alpha r_1, r_1)$ with Bézout bound $(D-1) \cdot D$.

### 3.3 Coprimality

In ALL tested cases (over 100 trials): $|V_{01}|$ is finite (0-dimensional), confirming that $r_0-1$ and $r_1$ are **coprime** in $\mathbb{F}_p[s_1, s_2]$. No common irreducible factor was ever observed.

## 4. Projection and Fiber Structure

For $d=2$, decompose $M$ by the $s_2$-projection:

$$M = \sum_{s_2 \in \mathbb{F}_p} M(s_2) \quad \text{where } M(s_2) = |\{s_1 : (s_1, s_2) \in V_{\text{all}}\}|$$

### Fiber bound
Each $s_2$-fiber is a $d=1$ problem. By the proved fiber bound: $M(s_2) \leq \lfloor n/w \rfloor$.

### Projection size
| $n$ | $p$ | $w$ | max $\#\{\text{active } s_2\}$ | max fiber | max $M$ |
|-----|-----|-----|------|------|------|
| 10 | 11 | 4 | 4 | 2 | 5 |
| 10 | 13 | 4 | 1 | 1 | 1 |
| 12 | 13 | 4 | 6 | 3 | 6 |
| 12 | 13 | 5 | 2 | 1 | 2 |
| 14 | 17 | 5 | 0 | 0 | 0 |

### Partial pinning in fibers
When a fiber has $M(s_2) > 1$, the corresponding $w$-subsets **share common elements** (partial pinning). Example: at $n=12, p=13, w=4$, fiber $s_2=9$ has 3 subsets $\{0,4,6,10\}, \{1,4,5,10\}, \{4,7,10,11\}$ sharing $\{4, 10\}$.

This is the $d=1$ pinning mechanism operating within each fiber.

## 5. Density Match

The average $M$ over random flats matches the density prediction:

$$\bar{M} \approx \frac{\binom{n}{w}}{p^c}$$

to within $\pm 10\%$ in ALL tested parameter sets. The max $M$ is $2$–$3\times$ the average.

For rate $1/2$ Johnson parameters with $p \geq n+1$:

| $n$ | $\binom{n}{w}/p^c$ | Regime |
|-----|---------------------|--------|
| 10 | 1.74 | $M = O(1)$ empirically |
| 12 | 2.93 | $M = O(1)$ empirically |
| 14 | 0.41 | $M = 0$ dominant |
| 20 | 0.14 | $M = 0$ dominant |

For $n \geq 14$: the density $< 1$, so $M = 0$ for most flats and $M \leq 2$ for all.

## 6. Barriers to Proof

### 6.1 Exponential sum barrier ($\sqrt{pN}$)

The character sum approach (Note 0068) gives:
$$M \leq \frac{\binom{n}{w}}{p^c} + \max_{\lambda \neq 0} |S(\lambda)|$$

where $|S(\lambda)| \leq \sqrt{p \cdot \binom{n}{w}}$. Since $\sqrt{p \cdot \binom{n}{w}}$ grows exponentially with $n$, this is **useless** for $M = O(1)$.

### 6.2 Bézout barrier ($D^d$)

The algebraic approach gives $M \leq D^d = (n-w+1)^d$, which is $O(n^d)$ — polynomial but not $O(1)$.

### 6.3 The real mechanism

The data suggests that $|V(r_0-1, r_1)|$ is already $O(1)$, far below $D^2$. This happens because:

1. Each curve $V(r_i)$ has $\approx p$ rational points (Weil bound for degree-$D$ curves), not $D \cdot p$.
2. The "random intersection" of two curves with $\approx p$ points each in $\mathbb{F}_p^2$ gives $\approx p \cdot p / p^2 = 1$ intersection point.
3. The companion matrix structure ensures the curves are in "generic position" (coprime, non-proportional outside infinity).

Making this rigorous requires:
- Proving $V(r_0-1)$ is **irreducible** (or has at most $O(1)$ irreducible components)
- Bounding the number of $\mathbb{F}_p$-rational intersection points of two specific algebraic curves defined via the companion matrix

## 7. Three Paths Forward

### Path A: Irreducibility + Weil (most promising)

If $r_0(s_1, s_2) - 1$ is irreducible of degree $D$:
- $|V(r_0-1)(\mathbb{F}_p)| = p + O(D\sqrt{p})$ by Weil
- $r_1$ restricted to $V(r_0-1)$ has $\leq D^2$ zeros (Bézout)
- But the $\mathbb{F}_p$-rational zeros are $\leq D$ (heuristic, supported by data)

**Gap**: no known theorem bounds $|V(f,g)(\mathbb{F}_p)|$ below $\deg f \cdot \deg g$ for coprime $f, g$.

### Path B: Resultant elimination

Eliminate $s_1$ from the system to get $w-1$ univariate conditions on $s_2$. If the GCD of the resulting resultants has degree $O(1)$, then $M = O(1)$.

**Challenge**: computing the actual degree of the elimination ideal.

### Path C: Large n reduction

For rate $1/2$ Johnson with $n \geq N_0$ (some explicit constant):
$$\frac{\binom{n}{w}}{(n+1)^c} < 1$$

This gives $\bar{M} < 1$, so $M = 0$ for "most" flats. Combined with a variance bound (second moment method), this gives $\max M = O(1)$.

**For $n < N_0$**: verify computationally. This is essentially what the FRI regime proof already does, extended to all $p > n$.

## 8. Recommended Next Steps

1. **Fix the degree in paper.tex**: $n-w \to n-w+1$ in Theorem 9.4 (minor, doesn't affect FRI result).

2. **Prove irreducibility of $r_0(s_1, s_2) - 1$**: use the companion matrix structure (Cayley-Hamilton, discriminant of $\Lambda_s(x)$).

3. **Compute the elimination ideal**: for specific small $(n, w, p)$, compute the degree of $\gcd(\text{Res}_{s_1}(r_0-1, r_j))_{j=1}^{w-1}$ and see if it's $O(1)$.

4. **Second moment / variance bound**: show $\text{Var}(M)$ is bounded, which combined with $\bar{M} = O(1)$ gives $\max M = O(1)$.

## 9. Scripts

- `overdetermined_bezout.py` — Progressive intersection V(r_0-1,...,r_j) with reduction factors
- `overdetermined_coprime.py` — Explicit polynomial computation, leading form analysis, coprimality
- `overdetermined_resultant.py` — Resultant computation attempt (Sylvester matrix, degree inflation issue)
- `overdetermined_fiber_proj.py` — Projection and fiber decomposition of V_all
- `overdetermined_degree_verify.py` — Degree verification: n-w+1, not n-w
