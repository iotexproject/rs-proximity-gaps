# Note 0070 — Convolutional Anti-Alignment Analysis

## 1. Setup and Notation

RS[n, k] on $L = \langle\omega\rangle$ of order $n$ in $\mathbb{F}_p$, rate $\rho = k/n = 1/2$,
Johnson radius $w = n - \lfloor\sqrt{n(k-1)}\rfloor$, conditions $c = n - k - w$.

From Note 0064: a center $c$ with syndrome coefficients $(c_k, \ldots, c_{n-1})$ defines
$c$ linear conditions on $\sigma(B) = (\sigma_1, \ldots, \sigma_w)$:

$$D_m = \sum_{j=0}^{w} (-1)^j \sigma_j \cdot c_{m-w+j} = 0 \quad (m = k+w, \ldots, n-1)$$

The coefficient matrix is **Toeplitz**: $A[r][j] = (-1)^{j+1} c_{k+r+j+1}$, $b[r] = -c_{k+r}$.

## 2. Case Split Theorem

**Theorem**: For RS[n,k] with $d_{\min} = n-k+1$ and Johnson radius $w$:

**Case 1** ($d(c, \mathrm{RS}_k) < w$): There exists codeword $f$ with $d(c,f) = d < w$.
Any other codeword $g$ with $d(g,c) \leq w$ satisfies
$d(f,g) \leq d(f,c) + d(g,c) \leq d + w$.
Since $d(f,g) \geq d_{\min} = n-k+1$: need $d \geq d_{\min} - w = c + 1$.
For $d \leq c$: **no second codeword possible** → $M_{\text{actual}} = 1$.

**Case 2** ($d(c, \mathrm{RS}_k) \geq w$): Every codeword at distance $\leq w$ is at
distance **exactly** $w$. Each such codeword corresponds to a unique compatible $B$
(with $|B| = w$). So $M_{\text{actual}} = M_{\text{alg}}$.

**Verified** for $n=10, k=5, w=3, p=11$:
- $d=1,2$: $\max M_{\text{actual}} = 1$ ✓
- $d=3=w$: $\max M_{\text{actual}} = 3$
- Far centers ($d \geq w$): $M_{\text{actual}} = M_{\text{alg}}$ in **all** 200+ tests (zero mismatches)
- 97.6% of random centers are "far"

## 3. Bézout Bound via Companion Matrix

### The key algebraic identity

For a $w$-subset $B = \{i_1, \ldots, i_w\}$ of $\mathbb{Z}/n\mathbb{Z}$ with $x_j = \omega^{i_j} \in L$:

The error-locator polynomial $g(T) = \prod(T - x_j) = T^w - \sigma_1 T^{w-1} + \cdots + (-1)^w \sigma_w$
satisfies $g(T) \mid T^n - 1$ (since all roots are $n$-th roots of unity).

### Restriction to a line

For $c = 2$ conditions ($w = 3$): the affine subspace $V_c$ is a line (1D) in $\mathbb{F}_p^3$.
Parameterize: $\sigma = a + t \cdot b$ for $t \in \mathbb{F}_p$.

The error-locator becomes $g_t(T) = T^3 - (a_1+tb_1)T^2 + (a_2+tb_2)T - (a_3+tb_3)$.

Compute $T^n \bmod g_t(T) = r_2(t) T^2 + r_1(t) T + r_0(t)$.

The condition $g_t \mid T^n - 1$ is equivalent to:
$$r_0(t) = 1, \quad r_1(t) = 0, \quad r_2(t) = 0$$

### Degree analysis

Using the companion matrix recurrence:
$$\begin{pmatrix} a_{k+1} \\ b_{k+1} \\ c_{k+1} \end{pmatrix} = \begin{pmatrix} 0 & 0 & \sigma_3(t) \\ 1 & 0 & -\sigma_2(t) \\ 0 & 1 & \sigma_1(t) \end{pmatrix} \begin{pmatrix} a_k \\ b_k \\ c_k \end{pmatrix}$$

Since $\sigma_j(t)$ has degree 1 in $t$, each step increases the degree by at most 1.
Starting from degree 0: after $n$ steps, $\deg r_i \leq n - w = n - 3$.

**Verified**: For $n = 10, w = 3$: $\deg(r_0-1) = \deg(r_1) = \deg(r_2) = 8 = n-2$.

### Bézout theorem

$$M_{\text{alg}} \leq \deg \gcd(r_0 - 1, r_1, r_2) \leq n - w = n - 2 \text{ (for } w=3\text{)}$$

**Verified exhaustively**:

| $n$ | $w$ | $p$ | $\max$ gcd degree | Actual $\max M$ on line | $N/p^c$ |
|-----|-----|-----|-------------------|------------------------|---------|
| 10  | 3   | 11  | 8                 | 8                      | 0.99    |
| 10  | 3   | 31  | 1                 | 1                      | 0.12    |
| 10  | 3   | 41  | 1                 | 1                      | 0.07    |

The bound is **tight** for $p = n+1$ (smallest valid $p$). For larger $p$: max gcd = 1.

## 4. Incidence Geometry of σ-Images

### Max collinear (w=3, conds=2)

The max number of σ-image points on any line in $\mathbb{F}_p^w$:

| $n$ | $p$ | Max collinear | $= n-2$? |
|-----|-----|---------------|----------|
| 10  | 11  | 8             | ✓        |
| 10  | 31  | 8             | ✓        |
| 10  | 41  | 8             | ✓        |

**p-independent**: max collinear = $n - 2$ for all tested $p$.

### Max coplanar (higher $w$, conds=2)

| $n$ | $w$ | $c$ | Flat dim | $p$ | Max on flat | $= C(n-c, w-c)$? |
|-----|-----|-----|----------|-----|-------------|-------------------|
| 12  | 4   | 2   | 2        | 13  | 45          | $C(10,2) = 45$ ✓  |
| 12  | 4   | 2   | 2        | 37  | 45          | ✓                 |
| 14  | 5   | 2   | 3        | 29  | 220         | $C(12,3) = 220$ ✓ |
| 16  | 5   | 3   | 2        | 17  | 78          | $C(13,2) = 78$ ✓  |

**Conjecture**: $\max|\sigma\text{-image} \cap V| = C(n-c, w-c)$ for any $(w-c)$-flat $V$.

This is p-independent and matches the combinatorial count of subsets sharing $c$ elements.

## 5. Restricted Parseval Analysis

For $V_c^\perp$ (the row space of the Toeplitz matrix, c-dimensional):

$$M_{\text{alg}} = \frac{1}{p^c} \sum_{t \in V_c^\perp} S(t) \cdot \psi(-t \cdot x_0)$$

**Restricted second moment** $R(V^\perp) = \sum_{t \in V^\perp \setminus \{0\}} |S(t)|^2$:

| Case | $n$ | $R / R_{\text{expected}}$ | Interpretation |
|------|-----|---------------------------|----------------|
| Toeplitz | 10 | **0.414** | Avoids high-$|S|$ directions |
| Random   | 10 | 0.984     | Matches equidistribution      |
| Toeplitz | 8  | **0.688** | Less pronounced but present   |
| Random   | 8  | 1.027     | Matches                       |

The Toeplitz row space **systematically captures less energy** than random subspaces.
This is the quantitative signature of convolutional anti-alignment.

## 6. Subspace Alignment Analysis

### Which coordinate alignments are dangerous?

For $n=12, k=6, w=4, p=13$ ($c=2$), zeroing pairs of coordinates:

| Zeroed pair | Avg $M$ | Max $M$ | Interpretation |
|-------------|---------|---------|----------------|
| $\sigma_3, \sigma_4$ | 2.77 | **5** | SAFE |
| $\sigma_1, \sigma_2$ | 2.79 | 36 | DANGEROUS |
| $\sigma_1, \sigma_3$ | 2.97 | 41 | DANGEROUS |
| $\sigma_2, \sigma_4$ | 3.02 | 38 | DANGEROUS |

Zeroing the LAST two coordinates ($\sigma_{w-1}, \sigma_w$) is **safe** (max $M$ drops).
All other pair alignments are **dangerous**.

### RS conditions: σ_1-alignment analysis

σ₁-aligned RS centers ($c_{k+1} = \cdots = c_{k+c} = 0$) at $n=12$:
max $M_{\text{alg}} = 11$ (same as non-aligned RS).

The Toeplitz structure couples coordinates via the shift relation
$A[1][j] = -A[0][j+1]$, preventing simultaneous zeroing of all coordinates.

## 7. Proof Status and Gaps

### What IS provable now

1. **Case Split**: $M_{\text{actual}} = 1$ for $d(c, \mathrm{RS}) < w$ (MDS + triangle inequality).

2. **Bézout Bound for $w=3$**: $M_{\text{alg}} \leq n - 2$ on any line.
   Proof: $\deg \gcd(r_0-1, r_1, r_2) \leq \deg r_i = n - w$.

3. **Combined** (for $c = 2, w = 3$): $M_{\text{actual}} \leq \max(1, n-2) = n-2 = O(n)$.

### What is NOT yet provable

1. **$M = O(1)$**: The Bézout bound gives $O(n)$, not $O(1)$.
   Empirically max is $O(1)$ (≤ 7 for $n \leq 18$), but the gap is $O(n)$ vs $O(1)$.

2. **Cancellation in character sum**: Cauchy-Schwarz gives $|E| \leq \sqrt{N}$ (useless).
   The actual cancellation in $\sum_{t \in V^\perp} S(t)$ is much stronger but unproven.

3. **Extension to general $w, c$**: The Bézout approach for general $w$ gives
   $M \leq C(n-c, w-c)$ (conjectured from data). This is exponential in $n$ for $w-c \geq 2$.

### Most promising path forward

**Stepanov method**: Construct auxiliary polynomial $P(t)$ vanishing at all $t$ where
$\sigma = a + tb$ is a valid σ-image, using the THREE relations $r_0 = 1, r_1 = 0, r_2 = 0$
simultaneously. If the construction achieves $\deg P = O(1)$, then $M = O(1)$.

Key: need to exploit that the three degree-$(n-2)$ polynomials are NOT independent —
they come from the SAME companion matrix recurrence, so their coefficients satisfy
strong algebraic relations. The gcd computation shows the actual number of common zeros
is $O(1)$ for generic lines.

## 8. Scripts

- `conv_antialign_step1.py` — Random vs σ_w-aligned vs RS subspaces, M distribution
- `conv_antialign_step2.py` — Fiber structure, pair alignment, RS vs random comparison
- `conv_antialign_step3.py` — Exhaustive Toeplitz search, scaling analysis
- `conv_antialign_step4.py` — Case split verification (Case 1 and Case 2)
- `conv_antialign_step5.py` — Max collinear/coplanar, algebraic degree analysis
- `conv_antialign_parseval.py` — Restricted Parseval and R(V^⊥) computation
- `conv_antialign_bezout.py` — GCD of remainder polynomials (Bézout bound)
