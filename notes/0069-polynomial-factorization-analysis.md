# Note 0069 — Direction A (Polynomial Factorization) + Direction D (Sum-Product) Analysis

## 1. Direction A: Polynomial Factorization — EQUIVALENCE THEOREM

### Setup

For RS[n, k] on $L = \langle\omega\rangle$ of order $n$ over $\mathbb{F}_p$,
center $c$ with polynomial representation $P_c(x)$ (degree $< n$), Johnson radius $w$,
conditions $c_{\text{cond}} = n - k - w$.

### Key Identity

For each list member $f_i \in \mathrm{RS}_k$ with $d(f_i, c) \leq w$:

$$P_c(x) = R_i(x) \cdot Q_i(x) + f_i(x)$$

where:
- $R_i(x) = \prod_{j \in A_i} (x - \omega^j)$ (agreement polynomial, degree $n - w_i \geq n - w$)
- $Q_i(x)$ has degree $w_i - 1 \leq w - 1$ (quotient polynomial)
- $A_i = \{j : f_i(\omega^j) = c_j\}$ is the agreement set

### Structural Properties of $Q_i$

**Verified empirically** for all tested $(n, p)$:

1. **Shared leading coefficient**: All $Q_i$ have the same leading coefficient
   $= [\text{leading coeff of } P_c]$ (since $R_i$ is monic).

2. **$Q_i$ is determined by $B_i$**: Given the error set $B_i$, $Q_i$ is uniquely determined
   by the requirement $\deg(P_c - R_i \cdot Q_i) < k$.

3. **For $n = 10, p = 11$**: $Q_i$ coefficients $(b_i, c_i)$ lie on a LINE in $\mathbb{F}_p^2$.
   For $n = 8, p = 17$: $(b_i, c_i)$ do NOT lie on a line (but on a higher-degree curve).

### The Key Identity for Differences

For any two list members $f_i, f_j$:

$$(f_i - f_j) \cdot S_i \cdot S_j = (x^n - 1) \cdot N_{ij}$$

where $S_i(x) = \prod_{l \in B_i}(x - \omega^l)$ (error locator) and
$N_{ij} = Q_j \cdot S_i - Q_i \cdot S_j$.

**Degree of $N_{ij}$**: $\deg N_{ij} \leq k - 1 + 2w - n$ (leading terms cancel).

| $n$ | $k$ | $w$ | $\deg N_{ij}$ bound | Observed |
|-----|-----|-----|---------------------|----------|
| 6   | 3   | 2   | 0 (constant)        | constant ✓ |
| 8   | 4   | 3   | 1 (linear)          | degree 1 ✓ |
| 10  | 5   | 3   | 0 (constant)        | constant ✓ |
| 12  | 6   | 4   | 1 (linear)          | degree 1 ✓ |

**CRITICAL**: This identity is **tautological on $L$**: both sides vanish at every
$\omega^l \in L$ (LHS from $S_i \cdot S_j$ factors, RHS from $x^n - 1$). So the
$N_{ij}$ polynomial's roots at elements of $L$ are unconstrained. The identity
gives non-trivial information only at points OUTSIDE $L$.

### EQUIVALENCE THEOREM

**Theorem**: The polynomial factorization approach (Direction A) is **equivalent**
to bounding σ-image concentration (the core problem from Notes 0064-0066).
It does not provide additional algebraic constraints.

**Proof sketch**:
1. The pairwise $d_{\min}$ constraint on differences $f_i - f_j$ is AUTOMATIC
   (MDS property of RS codes). It doesn't add new information.
2. The $Q_i$ polynomial is determined by $B_i$ through the $R_i \cdot Q_i \equiv P_c \pmod{high}$
   matching, which IS the compatibility conditions rewritten.
3. The $N_{ij}$ identity is tautological on $L$.
4. The clique in the "pairwise $d_{\min}$" graph has size $p - 1$ (trivially: same
   zero set, different scalars). The CENTER constraint, not pairwise distance, limits $M$.

### What Direction A DID provide

- Clean $Q$-polynomial parameterization of the list
- Confirmed $Q_i$ coefficients are polynomial functions of σ(B_i)
- $N_{ij}$ degree bound is a new structural identity (though tautological on $L$)
- Clarified that the problem is PURELY about σ-image equidistribution

---

## 2. Pairwise Distance Clique Analysis

### Max clique sizes in the "all pairwise $d_{\min}$" graph

| $n$ | $p$ | Max clique | $M_{\text{actual}}$ | Ratio |
|-----|-----|-----------|---------------------|-------|
| 6   | 7   | 6         | 3                   | 2.0×  |
| 8   | 17  | 16 (= $p-1$) | 7               | 2.3×  |
| 10  | 11  | 8         | 3                   | 2.7×  |

The max clique at $n = 8$ is $p - 1 = 16$: all 16 scalar multiples of a single monic
polynomial (same zero set $Z = \{0,1,2\}$). Their pairwise differences are scalar
multiples of the same polynomial, hence also minimum weight.

**Conclusion**: The clique problem (pairwise $d_{\min}$) is NOT the bottleneck.
The CENTER constraint is what limits $M_{\text{actual}}$.

---

## 3. Direction D: Sum-Product Structure

### σ-image Structure

**σ₁ (additive) distribution**: Nearly uniform over $\mathbb{F}_p$.
Max/avg ratio ≈ 1.0–1.4.

**σ_w (multiplicative) distribution**: DEGENERATE.
- $n = 8, p = 17$: only 8 distinct values (= $n / \gcd(w, n) = 8$), each exactly 7 times
- $n = 10, p = 11$: 10 distinct values, each exactly 12 times
- Explanation: $\sigma_w(B) = \omega^{\sum_{i \in B} i}$, so $\sigma_w$ depends only
  on $\sum_{i \in B} i \pmod{n}$, giving $n$ values each appearing $\binom{n}{w}/n$ times.

Wait, that's $\sigma_w = (-1)^w \cdot \prod_{i \in B} \omega^i = (-1)^w \omega^{\sum i}$.
So $|\text{image}(\sigma_w)| = |\{\omega^s : s \text{ achievable}\}|$.
For $w = 3$, $n = 8$: sums mod 8 from $\{a+b+c : 0 \leq a < b < c \leq 7\}$ cover all residues.
So $|\text{image}| = n$ and each appears $\binom{n}{w}/n$ times. ✓

**Joint (σ₁, σ_w)**: max fiber = 1 for small $(n,p)$ (σ-map fully injective).

### Additive and Multiplicative Energy

| $n$ | $p$ | $E^+(\sigma_1)/\text{random}$ | $E^\times(\sigma_w)/\text{random}$ |
|-----|-----|------------------------------|-----------------------------------|
| 6   | 7   | 15.0×                        | 17.5×                             |
| 8   | 17  | 56.0×                        | 119.0×                            |
| 10  | 11  | 120.0×                       | 132.0×                            |

**Both** additive and multiplicative energies are $\Theta(N)$ times the random baseline.
This reflects the GROUP STRUCTURE of $L$ (the projections are structured, not pseudorandom).

BUT: the **JOINT** image has low energy (max fiber = 1), confirming σ-map injectivity.

### KEY FINDING: Fiber Alignment

For $n = 10, p = 11$, fixing $\sigma_w = v$:

| $\sigma_w$ | Fiber size | Max $M$ after 1 more random condition |
|-----------|------------|--------------------------------------|
| 1–4, 6–7, 9–10 | 12 | 4 |
| **5**     | 12         | **12** (all on a LINE!)              |
| **8**     | 12         | **12** (all on a LINE!)              |

For $\sigma_w \in \{5, 8\}$: ALL 12 subsets have their $(\sigma_1, \sigma_2)$ values
lying on a **single line** in $\mathbb{F}_{11}^2$. A random codimension-1 condition
on $(\sigma_1, \sigma_2)$ can capture all 12.

**But RS $M_{\text{actual}} = 2$** — the RS compatibility conditions AVOID this fiber alignment.

### RS vs Random Subspace Comparison

| $n$ | $p$ | $c$ | RS max $M_{\text{alg}}$ | RS max $M_{\text{actual}}$ | Random max $M$ |
|-----|-----|-----|------------------------|---------------------------|---------------|
| 6   | 7   | 1   | 5                      | 3                         | 5             |
| 8   | 17  | 1   | 21                     | 5                         | 9             |
| 10  | 11  | 2   | 36                     | 2                         | 14            |

RS $M_{\text{alg}}$ has heavier tails than random (due to overcounting from close codewords),
but RS $M_{\text{actual}}$ is **SMALLER** than random max $M$!

**The RS compatibility conditions are BETTER behaved than random affine subspaces.**

---

## 4. Proof Strategy: Convolutional Anti-Alignment

### The KEY observation

RS compatibility conditions have **CONVOLUTIONAL STRUCTURE**:

$$D_m(\sigma(B)) = \sum_j c_{m-j} \cdot \sigma_j(B) = 0$$

where $c_j$ are the center's high-frequency coefficients. The matrix defining the
codimension-$c$ subspace is a **Toeplitz/convolution matrix**.

### Why convolution prevents alignment

A Toeplitz matrix $[c_{m-j}]$ with "generic" entries mixes all coordinates $\sigma_j$
uniformly. The fiber alignment of $\sigma_w$ (where all $(σ_1,...,σ_{w-1})$ lie on a
subspace) requires the conditions to be INDEPENDENT of $\sigma_w$. But a Toeplitz
condition of the form $c_0 \sigma_w + c_1 \sigma_{w-1} + \cdots = 0$ always involves
$\sigma_w$ (when $c_0 \neq 0$), preventing alignment with $\sigma_w$-fibers.

### Formalization needed

To prove $M = O(1)$ via this approach:

1. Show that the σ-image is "pseudorandom" with respect to GENERIC affine subspaces
   (non-aligned with fibers) — this requires sum-product type estimates.

2. Show that RS compatibility conditions are ALWAYS generic (never aligned with fibers) —
   this uses the Toeplitz/convolution structure of the syndrome matrix.

3. Combine: $M_{\text{actual}} \leq M_{\text{alg}}|_{\text{generic}} \leq O(1)$.

---

## 5. What was Ruled Out

- **Direction A (polynomial factorization)**: EQUIVALENT to σ-image concentration.
  Does not provide genuinely new algebraic constraints. The pairwise $d_{\min}$
  constraint is automatic (MDS property), and the $N_{ij}$ identity is tautological on $L$.

- **Pairwise distance clique approach**: Max clique = $p - 1$ (trivial). Not the bottleneck.

## 6. What Remains Promising

- **Convolutional anti-alignment**: The RS conditions have Toeplitz structure that
  prevents alignment with the degenerate fibers of the σ-image. This might be
  provable using character sum analysis of the convolution matrix.

- **Combined FRI + anti-alignment**: FRI folding reduces the problem to smaller $n$,
  and the anti-alignment prevents degenerate cases at each step.

- **Stepanov method**: Construct a polynomial vanishing on all compatible σ-images
  in a given subspace. The degree bound would give $M = O(1)$.

---

## 7. Scripts

- `poly_factor_explore.py` — Round 1: min-weight enumeration, transitivity, cyclotomic
- `poly_factor_clique.py` — Round 2: clique analysis in pairwise-$d_{\min}$ graph
- `poly_factor_center.py` — Round 3: center-constrained analysis, $Q_i$ polynomials
- `poly_factor_Q_structure.py` — Round 4: $Q_i$ parametric structure, $N_{ij}$ identity
- `sum_product_explore.py` — Direction D Round 1: σ-image distributions, energies
- `sum_product_alignment.py` — Direction D Round 2: RS vs random alignment test
