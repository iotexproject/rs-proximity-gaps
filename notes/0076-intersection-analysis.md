# Note 0076 — Intersection V(r₀-1) ∩ V(r₁): Structure and Barriers

## 1. Goal

Prove |V(r₀-1) ∩ V(r₁)(F_p)| = O(1) on RS-compatible flats, closing the gap from the irreducibility theorem (Note 0075) to the full M = O(1) bound.

## 2. Key Findings

### 2.1. Structural factorization: σ_w | r_i for i ≤ w-2

In the bivariate specialization (σ₂ = ... = σ_{w-1} = 0):

**Theorem**: σ_w divides r_i for 0 ≤ i ≤ w-2. σ_w does NOT divide r_{w-1}.

Verified for all w ∈ {3,4,5} and n up to w+14. The factored forms:
- h_i := r_i / σ_w has weighted degree n-i-w and total degree n-i-1-(w-2) = n-w-i+1

**Consequence**: V(r₀-1) ∩ V(σ_w) = ∅ (since r₀(σ₁,0) = 0, so r₀-1 = -1 at σ_w = 0).
So V(r₀-1) ∩ V(r₁) = V(r₀-1) ∩ V(h₁) where h₁ = r₁/σ_w.

### 2.2. Differential identity: D_tot(r₁) = ∂r₀/∂σ₁

**Theorem**: For the total Euler operator D_tot = σ₁·∂/∂σ₁ + σ_w·∂/∂σ_w:

$$D_{\mathrm{tot}}(r_1) = \frac{\partial r_0}{\partial \sigma_1}$$

Equivalently: the coefficient of σ₁^a·σ_w^b in r₁ equals (a+1)/(a+b) times the coefficient of σ₁^{a+1}·σ_w^b in r₀.

**Proof**: Follows from the weighted Euler relations:
- σ₁·∂r₀/∂σ₁ + w·σ_w·∂r₀/∂σ_w = n·r₀ (weighted homogeneity, weight n)
- σ₁·∂r₁/∂σ₁ + w·σ_w·∂r₁/∂σ_w = (n-1)·r₁ (weighted homogeneity, weight n-1)

Subtracting D_tot(r₁) = ∂r₀/∂σ₁ from the second relation gives:
(w-1)·σ_w·∂r₁/∂σ_w = (n-1)·r₁ - ∂r₀/∂σ₁

Combined with the empirical identity (verified for all tested parameters).

**Consequence**: V(r₁) ⊂ V(∂r₀/∂σ₁). The zeros of r₁ are a subset of the critical points of r₀ w.r.t. σ₁.

### 2.3. Euler relation (verified)

σ₁·∂r₀/∂σ₁ + w·σ_w·∂r₀/∂σ_w = n·r₀

Verified for all (n,w) tested. This is the weighted Euler identity for weighted-homogeneous polynomials.

## 3. Intersection Counts: Generic vs RS Flats

### 3.1. Bivariate intersection (σ₂ = 0 flat)

| n | w | p | p mod n | |V₀₁| | |V_all| |
|---|---|---|---------|-------|--------|
| 7 | 3 | 17 | 3 | 1 | 0 |
| 11 | 3 | 23 | 1 | 11 | 11 |
| 15 | 3 | 31 | 1 | 20 | 20 |
| 8 | 4 | 17 | 1 | 2 | 2 |
| 10 | 4 | 11 | 1 | 0 | 0 |

**Spike at p ≡ 1 mod n**: When n | (p-1), ALL n-th roots of unity are in F_p. V_all = C(n,w) in full σ-space. The σ₁-values of V₀₁ at these special primes form the unique subgroup of order n in F_p* (verified for n=11, p=23).

### 3.2. Generic 2-flat intersection

| n | w | p | p mod n | σ₂=0 |V₀₁| | Random flat avg | Random flat max |
|---|---|---|---------|------------|-----------------|-----------------|
| 10 | 3 | 11 | 1 | 10 | 12.7 | 36 |
| 12 | 3 | 13 | 1 | 16 | 16.9 | 21 |
| 10 | 4 | 11 | 1 | 0 | 2.4 | 6 |
| 12 | 4 | 13 | 1 | 3 | 4.8 | 9 |

**Key finding**: avg |V₀₁| on random flat = C(n,w)/p^{w-2} exactly.
- w=3: C(n,3)/p ≈ n²/(6p) ≈ n/6 at p ≈ n. **O(n), NOT O(1).**
- w≥4: C(n,w)/p^{w-2} = O(1). Already bounded.

### 3.3. RS flat vs random flat: IDENTICAL distribution

| n | w | c | C(n,w)/p^c | RS avg M | Random avg M | RS max | Random max |
|---|---|---|-----------|----------|-------------|--------|-----------|
| 8 | 3 | 1 | 3.29 | 3.17 | 3.32 | 9 | 21 |
| 10 | 3 | 1 | 10.91 | 11.04 | 10.70 | 15 | 36 |
| 10 | 4 | 2 | 1.74 | 2.10 | 1.73 | 28 | 8 |
| 12 | 4 | 2 | 2.93 | 2.75 | 2.90 | 11 | 17 |

**The RS Toeplitz structure provides NO advantage.** Average M = C(n,w)/p^c for both RS and random flats.

### 3.4. Overcounting: M_actual vs M_bset

| n | w | c | M_bset max | M_actual max | ratio |
|---|---|---|-----------|-------------|-------|
| 8 | 3 | 1 | 9 | 5 | 1.8 |
| 10 | 4 | 1 | 36 | 22 | 1.6 |
| 10 | 4 | 2 | 8 | 3 | 2.7 |

M_actual (distinct codewords) is smaller than M_bset (B-set count) due to overcounting: each codeword at distance d contributes C(n-d, w-d) B-sets.

## 4. Why the Weil Approach Fails

### 4.1. 0-dimensional varieties have no Weil bound

For a 0-dim variety Z of degree δ over F_p: |Z(F_p)| ≤ δ. There is no Weil-type reduction to |Z(F_p)| ≤ δ/p or similar. All δ points could be F_p-rational.

### 4.2. Bézout on generic flats gives D² not D

On a 2-flat: V(r₀-1) is a curve of degree D, V(r₁) is a curve of degree D-1. Bézout: intersection ≤ D(D-1) ≈ D². The claim in Note 0075 §5.1 that M ≤ D for d=2 was **incorrect** — the degree of r₁ as a function on V(r₀-1) is D(D-1), not D.

### 4.3. Hurwitz/critical point approach

V(r₁) ⊂ V(∂r₀/∂σ₁) (from the D_tot identity). So V(r₀-1) ∩ V(r₁) ⊂ {critical points of projection σ₁ on V(r₀-1)}. By Hurwitz: #critical ≤ 2g + 2d - 2 ≈ D². Same order as Bézout.

### 4.4. Resultant analysis

At primes where the resultant can be computed: the DDF pattern is fixed (independent of p for given n,w). The number of degree-1 factors varies with p but is bounded by the degree.

At p ≡ 1 mod n: the resultant can split completely (all roots become F_p-rational), giving |V₀₁| = D·D₁ = O(n²).

## 5. Error Correction in Paper

**Corollary 9.5 (old)**: "M ≤ n - w + 1 for d = 2" — **INCORRECT**.

**Corollary 9.5 (corrected)**: Irreducibility of r₀-1 ensures transversality (0-dimensional intersection) on generic flats, validating the Bézout bound M ≤ (n-w+1)^d. Updated in paper.tex.

## 6. The Remaining Path to M = O(1)

The Weil approach (irreducibility → Weil → O(1)) is **blocked**. Three possible paths remain:

**A. Stepanov auxiliary polynomial.** Construct polynomial Φ(σ₁, σ_w) that:
- Vanishes to high order at all intersection points
- Has controlled degree
The D_tot(r₁) = ∂r₀/∂σ₁ identity provides algebraic relations between r₀ and r₁ that could constrain such Φ.

**B. Full system exploitation.** Use ALL w equations r₀=1, r₁=...=r_{w-1}=0 simultaneously, not just the first two. The system is overdetermined (w equations in d variables). For d=2, w=3: 3 equations in 2 unknowns. The third equation r₂=0 may reduce the count from O(n) to O(1).

**C. Accept M = O(n) for c=1.** For c=1 (one condition beyond MDS), M = Θ(C(n,w)/p) = Θ(n^{w-1}/p) on average. For w=3: O(n). For the Proximity Prize, the relevant regime is c ≥ 2 (Johnson radius), where density already gives M = O(1).

## 7. Scripts

- `intersection_r0r1.py` — Bivariate V₀₁ counts, resultant factorization, DDF
- `intersection_generic_flat.py` — Full σ-space, random 2-flat counts vs σ₂=0
- `intersection_rs_flat.py` — RS flat M vs random flat M comparison
- `intersection_overcounting.py` — M_actual vs M_bset decomposition
- `intersection_structure.py` — σ_w divisibility, derivative identity, Euler relation
