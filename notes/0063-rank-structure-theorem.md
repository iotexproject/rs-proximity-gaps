# Note 0063 — Rank Structure Theorem for List Decoding

## Main Theorem (Computational)

**Theorem (Rank Structure)**: For RS[n,k] on multiplicative subgroup $L = \langle\omega\rangle$
of order $n$ over $\mathbb{F}_p$, at the Johnson radius $w = \lceil(1-\sqrt\rho)n\rceil$:

The worst-case list of $M$ codewords $f_1, \ldots, f_M$ at distance $w$ from a center $c$
has error sets $B_1, \ldots, B_M$ (each $|B_i| = w$) whose combined Vandermonde
condition rank equals **exactly** $n - k - 1$.

Equivalently: the feasible syndrome space is **1-dimensional** (a line in $\mathbb{F}_p^{n-k}$).

### Verified cases

| n | k | w | conds/B | M | Combined rank | n-k | Free dim |
|---|---|---|---------|---|---------------|-----|----------|
| 6 | 3 | 2 | 1 | 3 | 2 | 3 | **1** |
| 8 | 4 | 3 | 1 | 7 | 3 | 4 | **1** |
| 10 | 5 | 3 | 2 | 3 | 4 | 5 | **1** |
| 12 | 6 | 4 | 2 | 6 | 5 | 6 | **1** |

### Key structural observations

1. **Pairwise rank is always full**: For the actual worst-case error sets, every pair
   $(B_i, B_j)$ has combined condition rank $= 2 \cdot \text{conds/B}$ (no pairwise redundancy).
   The rank deficiency is a **global** phenomenon.

2. **The null vector characterizes the list**: The 1D null space of the combined
   conditions (modulo $RS_k$) is a vector $v \in \mathbb{F}_p^n \setminus RS_k$. The list
   size $M$ equals the number of error sets $B$ whose Vandermonde conditions all
   vanish on $v$. This is:
   $$M = |\{f \in RS_k : d(v, f) \leq w\}|$$
   i.e., $v$ IS the center (up to a codeword shift).

3. **Cumulative rank grows to $k+1$ then stops**: Starting from the $RS_k$ basis
   (rank $k$), adding the first error set's conditions increases rank to $k+1$.
   All subsequent conditions are redundant.

## Algebraic Factorization Framework

For center $c$ with polynomial representation $c(x)$ (degree $< n$), and codeword
$f$ with polynomial $h(x)$ (degree $< k$):

The error polynomial $e(x) = c(x) - h(x)$ vanishes on the agreement set $S$:
$$e(x) = Q(x) \cdot P_S(x)$$

where:
- $P_S(x) = \prod_{i \in S}(x - \omega^i)$, degree $n-w$
- $Q(x)$ has degree $w-1$

The condition $\deg(h) < k$ gives:
$$[Q \cdot P_S]_j = c_j \quad \text{for } j = k, \ldots, n-1$$

This is $(n-k)$ linear equations in $w$ unknowns (coefficients of $Q$).

**Overdetermined by**: $(n-k) - w = n - k - w = \text{conds/B}$

### Compatibility condition

For the system $A \mathbf{q} = \mathbf{c}_{\text{high}}$ (where $A$ depends on $P_S$)
to be compatible:

- **conds/B = 1**: One determinant condition. det$([A | \mathbf{c}_{\text{high}}]) = 0$.
  The determinant is a polynomial of degree $\leq w$ in the elementary symmetric
  polynomials of the agreement points.

- **conds/B = $c$**: $c$ independent conditions, each polynomial in the
  elementary symmetric polynomials.

### Degree bound for conds/B = 1

The matrix $[A | \mathbf{c}_{\text{high}}]$ is $(w+1) \times (w+1)$ with Toeplitz-like
structure. Entry at row $r$, column $l$ ($l < w$):
$$[A]_{r,l} = P_S[k + r - l]$$

Since $P_S$ is monic of degree $n-w$:
- $P_S[n-w] = 1$ (leading coefficient)
- $P_S[m] = 0$ for $m > n-w$
- $P_S[m] = (-1)^{n-w-m} e_{n-w-m}$ for $m = 0, \ldots, n-w$

The matrix is **upper Hessenberg** (zero below the first subdiagonal).

The determinant has **degree $\leq w$** in the elementary symmetric polynomials.
Converting to degree in the roots: degree $\leq w \cdot (n-w)$ (very loose bound).

## Implications for M = O(1)

### What's needed for a proof

1. **Bound the number of roots** of the compatibility polynomial $D(e_1, \ldots, e_{n-w}) = 0$
   over the "lattice" of $(n-w)$-subsets of $L$.

2. This is a **restricted zero counting** problem: how many $(n-w)$-subsets of $L$
   satisfy $D = 0$, where $D$ is a specific polynomial of known degree in the
   elementary symmetric polynomials?

3. **For conds/B ≥ 2**: the conditions are MULTIPLE polynomial equations,
   forming a **variety**. The dimension of this variety bounds $M$.

### Connection to GM-MDS

The GM-MDS conjecture (proved by BGM 2023 for generic points) states that
for generic evaluation points, the list size is $O(1)$. Their proof shows
that the compatibility polynomial $D$ is nonzero for generic points.

For **multiplicative subgroups**: $D$ may vanish on specific subsets, but the
number of such subsets is bounded by the degree of $D$.

The key difference: multiplicative subgroups have specific algebraic relations
among the evaluation points ($\omega^i \cdot \omega^j = \omega^{i+j}$), which
can create more zeros of $D$ than for generic points.

## What this theorem does NOT give

- An explicit formula for $M$ (only rank = $n-k-1$, not what $M$ equals)
- A proof that $M = O(1)$ for all $n$ (only verified for $n \leq 12$)
- Connection to packing bounds (pairwise rank is full, so no packing argument)

## Parity Check Correction

**IMPORTANT**: The matrix $H[r][i] = L[i]^{k+r}$ is NOT a valid parity check for
$\text{RS}[n,k]$ on $L = \{1, \omega, \ldots, \omega^{n-1}\}$ when $n \leq 2k$.
Specifically, $H G^T \neq 0$ because exponents $k+r+j \equiv 0 \pmod{n}$ can occur
with $r \in \{0,\ldots,n-k-1\}$ and $j \in \{0,\ldots,k-1\}$.

This does NOT affect the condition-rank analysis (which uses the Vandermonde
left kernel directly, not $H$), but it invalidates any computation that used
$H$ for syndrome grouping. The CORRECT parity check uses exponents in
$\{1, 2, \ldots, n-k\}$ (avoiding collision with generating exponents $\{0,\ldots,k-1\}$).

All $M$ values verified by DIRECT codeword enumeration (brute force, no parity check).

## Verified worst-case configurations

- **n=6, k=3, p=7, w=2**: M=3, center=(1,3,0,0,0,0), B's = {01}, {25}, {34}
- **n=8, k=4, p=17, w=3**: M=7, center=(7,1,3,0,0,0,0,0), B's = all 7 confirmed
- **n=10, k=5, p=11, w=3**: M=3, center=(1,3,3,0,...,0), B's = {012}, {356}, {489}

## Next steps

1. **Compute the degree of $D$** explicitly for $(n, k, w)$ at Johnson
2. **Count zeros of $D$** over $(n-w)$-subsets of the $n$-th roots of unity
3. **Use Weil bounds or character sums** to bound the zero count
4. **Handle conds/B ≥ 2** via intersection theory on the compatibility variety
5. **Determine if free dim = 1 is PROVABLE** from the algebraic factorization
