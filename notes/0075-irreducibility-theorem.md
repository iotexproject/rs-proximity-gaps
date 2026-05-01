# Note 0075 — Irreducibility of r₀(σ) − 1: Newton Polygon Proof

## 1. Statement

**Theorem (Absolute Irreducibility)**. For all $n > w \geq 2$ and all primes $p > n$ with $p \nmid c_{\lfloor n/w \rfloor}(n,w)$, the polynomial
$$r_0(\sigma_1, \ldots, \sigma_w) - 1 \in \mathbb{F}_p[\sigma_1, \ldots, \sigma_w]$$
is absolutely irreducible (irreducible over $\overline{\mathbb{F}}_p$).

Here $r_0(\sigma)$ is the constant coefficient of $x^n \bmod \Lambda_\sigma(x)$, where $\Lambda_\sigma(x) = x^w - \sigma_1 x^{w-1} + \sigma_2 x^{w-2} - \cdots + (-1)^w \sigma_w$.

The integer $c_q(n,w)$ is the coefficient of $\sigma_1^{n-qw}\sigma_w^q$ in $r_0(\sigma_1, 0, \ldots, 0, \sigma_w)$, with $q = \lfloor n/w \rfloor$. When $w \mid n$: $c_q = (-1)^{q(w+1)} = \pm 1$, so the condition $p \nmid c_q$ is automatic.

## 2. Key Structural Properties

### 2.1. Weighted homogeneity

$r_0(\sigma_1, \ldots, \sigma_w)$ is **weighted-homogeneous of weight $n$** with $\mathrm{wt}(\sigma_j) = j$.

*Proof*: The companion matrix recurrence preserves weighted degree. Each step multiplies by $c_j = (-1)^{w-j+1}\sigma_{w-j}$ which has weight $w-j$, contributing weight 1 to the polynomial degree per step. After $n$ steps: total weight $n$. ∎

### 2.2. The bivariate specialization

Set $\sigma_2 = \cdots = \sigma_{w-1} = 0$. Then $\Lambda(x) = x^w - \sigma_1 x^{w-1} + (-1)^w \sigma_w$, and the companion matrix recurrence has only two nonzero coefficients: $c_0 = (-1)^{w+1}\sigma_w$ and $c_{w-1} = \sigma_1$.

The resulting bivariate polynomial $f(\sigma_1, \sigma_w) := r_0(\sigma_1, 0, \ldots, 0, \sigma_w) - 1$ has **support**:
$$\mathrm{supp}(f) = \{(0, 0)\} \cup \{(n - jw,\ j) : j = 1, \ldots, q\}, \quad q = \lfloor n/w \rfloor$$

with coefficients:
- $(0, 0)$: coefficient $-1$
- $(n-w, 1)$: coefficient $(-1)^{w+1}$
- $(n-qw, q)$: coefficient $c_q(n,w)$
- Intermediate $(n-jw, j)$: coefficients are specific integers $c_j(n,w)$, independent of $p$

### 2.3. Collinearity of support points

**Claim**: All points $(n-jw, j)$ for $j = 1, \ldots, q$ are **collinear**.

*Proof*: The line through $(n-w, 1)$ and $(n-qw, q)$ at parameter $t = (j-1)/(q-1)$ gives first coordinate:
$$(n-w) - \frac{j-1}{q-1} \cdot (q-1)w = n - w - (j-1)w = n - jw \quad \checkmark$$

### 2.4. The Newton polygon is a triangle

For $q \geq 2$ (i.e., $n \geq 2w$): the convex hull of $\mathrm{supp}(f)$ is a **triangle** with vertices:
$$V_1 = (0, 0), \quad V_2 = (n-w, 1), \quad V_3 = (n - qw,\ q)$$

All intermediate support points $(n-jw, j)$ for $1 < j < q$ lie on the edge $V_2 V_3$.

For $q = 1$ (i.e., $w < n < 2w$): $\mathrm{supp}(f) = \{(0,0), (n-w, 1)\}$, a line segment.

## 3. Proof of Irreducibility

### Step 1: The Newton polygon is integrally indecomposable

**Theorem (classical)**: Every simplex in $\mathbb{R}^d$ is Minkowski-indecomposable.

*Proof for $d=2$ (triangle)*: If $P = P_1 + P_2$ with $\dim P_1, \dim P_2 \geq 1$:
- If $\dim P_1 = \dim P_2 = 1$: $P_1 + P_2$ is a parallelogram (4 edges) or a segment (if parallel). A triangle has 3 edges. Contradiction.
- If $\dim P_1 = 2, \dim P_2 = 1$: the Minkowski sum has $\geq 4$ edges (since a triangle contributes 3 normal directions, a segment contributes $\leq 2$, and the sum has $\geq \max(3,2)+1 = 4$ edges). A triangle has 3 edges. Contradiction.
- Similarly for $\dim P_1 = 1, \dim P_2 = 2$. ∎

For $q = 1$: the Newton polygon is a line segment in direction $(n-w, 1)$ with $\gcd(n-w, 1) = 1$ (primitive). A primitive segment is indecomposable.

### Step 2: Gao's theorem

**Theorem (Gao 2001)**: If $f \in k[x, y]$ has integrally indecomposable Newton polygon and all vertex coefficients are nonzero, then $f$ is absolutely irreducible.

Our vertex coefficients:
- $V_1 = (0,0)$: coeff $= -1 \neq 0$ ✓
- $V_2 = (n-w, 1)$: coeff $= (-1)^{w+1} \neq 0$ ✓
- $V_3 = (n-qw, q)$: coeff $= c_q(n,w) \neq 0 \pmod{p}$ (by hypothesis) ✓

**Conclusion**: $f(\sigma_1, \sigma_w) = r_0(\sigma_1, 0, \ldots, 0, \sigma_w) - 1$ is absolutely irreducible. ∎

### Step 3: Lifting to full σ-space

**Claim**: The absolute irreducibility of the bivariate specialization implies absolute irreducibility of $r_0(\sigma_1, \ldots, \sigma_w) - 1$.

*Proof*: Suppose $r_0(\sigma) - 1 = f(\sigma) \cdot g(\sigma)$ in $\overline{\mathbb{F}}_p[\sigma_1, \ldots, \sigma_w]$ with $\deg(f) = d \geq 1$, $\deg(g) = D - d$, where $D = n - w + 1 = \deg(r_0 - 1)$.

Restrict to $\sigma_2 = \cdots = \sigma_{w-1} = 0$:
$$f(\sigma_1, 0, \ldots, 0, \sigma_w) \cdot g(\sigma_1, 0, \ldots, 0, \sigma_w) = r_0(\sigma_1, 0, \ldots, 0, \sigma_w) - 1$$

The right side is absolutely irreducible (Step 2). Therefore one factor restricts to a nonzero constant. WLOG $f(\sigma_1, 0, \ldots, 0, \sigma_w) = c \in \overline{\mathbb{F}}_p^*$.

Then $g(\sigma_1, 0, \ldots, 0, \sigma_w) = \frac{1}{c}(r_0(\sigma_1, 0, \ldots, 0, \sigma_w) - 1)$, which has total degree $D$ (the leading term is $\frac{(-1)^{w+1}}{c} \sigma_1^{n-w}\sigma_w$ of total degree $(n-w)+1 = D$).

But $\deg(g) = D - d \leq D - 1$, so $\deg(g|_{\mathrm{plane}}) \leq D - 1 < D$. This contradicts $\deg(g|_{\mathrm{plane}}) = D$. ∎

## 4. Verification

### 4.1. Vertex coefficient $c_q$

| $n$ | $w$ | $q$ | $c_q$ | $|c_q| < n$? |
|-----|-----|-----|--------|-------------|
| 5 | 3 | 1 | 1 | ✓ |
| 7 | 3 | 2 | 2 | ✓ |
| 9 | 3 | 3 | 1 | ✓ |
| 11 | 3 | 3 | 6 | ✓ |
| 13 | 3 | 4 | 4 | ✓ |
| 6 | 4 | 1 | −1 | ✓ |
| 8 | 4 | 2 | 1 | ✓ |
| 10 | 4 | 2 | 3 | ✓ |
| 12 | 4 | 3 | −1 | ✓ |
| 14 | 4 | 3 | −6 | ✓ |
| 7 | 5 | 1 | 1 | ✓ |
| 9 | 5 | 1 | 1 | ✓ |
| 11 | 5 | 2 | 2 | ✓ |
| 13 | 5 | 2 | 4 | ✓ |
| 15 | 5 | 3 | 1 | ✓ |

When $w \mid n$: $c_q = (-1)^{q(w+1)} = \pm 1$. Always nonzero.

Conjecture: $|c_q(n,w)| \leq \binom{q}{1} \cdot w^{q-1}$ for all $n, w$. Verified for $n \leq 20$.

### 4.2. Computational verification of irreducibility

Tested via Hilbert specialization criterion (both $\sigma_1$ and $\sigma_2$ directions) over random flats:

| $n$ | $p$ | $w$ | $c$ | trials | abs. irred. | s2-only | neither |
|-----|-----|-----|-----|--------|-------------|---------|---------|
| 10 | 11 | 4 | 2 | 30 | 60% | 23% | 17% |
| 10 | 13 | 4 | 2 | 30 | 80% | 10% | 10% |
| 10 | 17 | 4 | 2 | 30 | 97% | 3% | 0% |
| 10 | 23 | 4 | 2 | 30 | 100% | 0% | 0% |
| 10 | 29 | 4 | 2 | 30 | 100% | 0% | 0% |
| 12 | 13 | 4 | 2 | 30 | 53% | 20% | 27% |
| 12 | 23 | 4 | 2 | 30 | 100% | 0% | 0% |

The "neither" cases at small $p$ are NOT counterexamples — the Hilbert test fails because $p$ is too small relative to degree $D$. For $p \geq 23$: 100% proven irreducible.

### 4.3. Point counts match Weil/Lang-Weil

| $n$ | $p$ | $w$ | avg $|V(r_0-1)|$ | $p^{w-1}$ | ratio |
|-----|-----|-----|-------------------|-----------|-------|
| 6 | 7 | 3 | 50 | 49 | 1.02 |
| 8 | 11 | 3 | 112 | 121 | 0.93 |
| 10 | 13 | 3 | 184 | 169 | 1.09 |
| 8 | 11 | 4 | 1210 | 1331 | 0.91 |
| 10 | 13 | 4 | 2045 | 2197 | 0.93 |

Ratio $\approx 1$ in all cases, consistent with a single irreducible component (Lang-Weil: $|V(F_p)| = p^{w-1} + O(p^{w-3/2})$).

## 5. Consequence for List Size

### 5.1. Improved bound

Combined with the Pinned Flat Uniqueness Theorem (Note 0072):

**Corollary**: For RS$[n, k]$ on $L = \langle\omega\rangle \subset \mathbb{F}_p^*$ at Johnson radius $w$, codimension $c = n-k-w$, dimension $d = w-c$:

On each $d$-dimensional flat $V_c$ of compatible $\sigma$-values:

$$M_{\mathrm{actual}} \leq D^{d-1} = (n-w+1)^{d-1}$$

*Proof*: The first condition $r_0 = 1$ defines an irreducible hypersurface on the flat (Bertini + this theorem). Intersecting with $r_1 = 0$ gives $\leq D$ points on this curve. Each additional condition $r_j = 0$ can only reduce. So $M \leq D^{d-1}$.

For $d = 2$: $M \leq D = n - w + 1$. Improves previous $M \leq D^2 = (n-w+1)^2$ (Bézout).

### 5.2. Remaining gap to M = O(1)

The bound $M \leq D$ is $O(n)$, not $O(1)$. The empirical data shows $M = O(1)$ with $|V_{01}| \leq D$ in all tests. The gap is:
- Bézout gives $M \leq D^2$ over $\overline{\mathbb{F}}_p$
- Irreducibility + Bézout gives $M \leq D$ rational points
- Data shows $M \leq 7$ for all tested $(n, w, p)$

Closing this gap requires bounding the $\mathbb{F}_p$-rational points of $V(r_0-1) \cap V(r_1)$, not just the algebraic intersection. This is related to the **Weil bound for 0-dimensional varieties** or the **Lang-Weil heuristic** for intersection point distribution.

## 6. The polynomial r₀(σ₁, 0, …, 0, σ_w) − 1 over ℤ

The polynomial is defined over $\mathbb{Z}$, independent of $p$:

**$w = 3$:**
$$r_0 - 1 = \sum_{j=1}^{q} c_j \cdot \sigma_1^{n-3j} \cdot \sigma_3^j - 1$$

| $n$ | polynomial |
|-----|-----------|
| 5 | $\sigma_1^2\sigma_3 - 1$ |
| 7 | $\sigma_1^4\sigma_3 + 2\sigma_1\sigma_3^2 - 1$ |
| 9 | $\sigma_1^6\sigma_3 + 4\sigma_1^3\sigma_3^2 + \sigma_3^3 - 1$ |
| 11 | $\sigma_1^8\sigma_3 + 6\sigma_1^5\sigma_3^2 + 6\sigma_1^2\sigma_3^3 - 1$ |

**$w = 4$:**
| $n$ | polynomial |
|-----|-----------|
| 6 | $-\sigma_1^2\sigma_4 - 1$ |
| 8 | $-\sigma_1^4\sigma_4 + \sigma_4^2 - 1$ |
| 10 | $-\sigma_1^6\sigma_4 + 3\sigma_1^2\sigma_4^2 - 1$ |
| 12 | $-\sigma_1^8\sigma_4 + 5\sigma_1^4\sigma_4^2 - \sigma_4^3 - 1$ |

**$w = 5$:**
| $n$ | polynomial |
|-----|-----------|
| 7 | $\sigma_1^2\sigma_5 - 1$ |
| 9 | $\sigma_1^4\sigma_5 - 1$ |
| 11 | $\sigma_1^6\sigma_5 + 2\sigma_1\sigma_5^2 - 1$ |
| 13 | $\sigma_1^8\sigma_5 + 4\sigma_1^3\sigma_5^2 - 1$ |

## 7. Scripts

- `irreducibility_r0.py` — Initial Hilbert specialization tests + point counts
- `irreducibility_deep.py` — Statistics over many random flats, factorization patterns
- `irreducibility_sigma_space.py` — Full σ-space computation, Lang-Weil verification
- `irreducibility_explicit.py` — Explicit polynomial + p-independence test
- `irreducibility_newton.py` — Newton polygon analysis + proof chain
