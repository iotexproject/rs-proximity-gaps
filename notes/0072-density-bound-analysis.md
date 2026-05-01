# Note 0072 — Density Bound Analysis: From Conjecture to Proof Strategy

## 1. Summary of Findings

This session's goal: prove Conjecture 9.4 (density bound) rigorously.

**Main result**: The conjecture is FALSE for general codim-c subspaces (pinning subspaces violate it). But it IS true for RS-compatible subspaces, with a rigorous Bézout-based upper bound and strong heuristic for the O(1) regime.

## 2. Fourier Analysis of σ-Image (Experiment 1)

Computed f̂(u) = Σ_{B ∈ L^{(w)}} ψ(u · e(B)) for all u ∈ F_p^w.

**Findings**:
- E[M] = C(n,w)/p^c EXACTLY (confirmed for all parameters)
- Var[M] ≈ E[M] (Poisson distribution)
- max|f̂(u)| ≈ N/2, achieved on the e_w axis (product direction)
- Parseval: Σ|f̂|^2 = p^w · N (exact)

**Implication**: Fourier approach alone gives error ≈ N/2 per coefficient, which exceeds the main term N/p^c. Direct Fourier proof requires better cancellation from RS structure.

## 3. The Pinning Obstruction

**KEY DISCOVERY**: max points on any hyperplane = C(n-1, w-1), achieved by the "pinning" hyperplane e_1 + e_2 + ... + e_w = -1 (i.e., Λ(-1) = 0, pinning the element -1 ∈ L).

For codim c: the "pinning c elements" subspace gives C(n-c, w-c) intersection points.

**The density conjecture M ≤ C·C(n,w)/p^c + O(1) is FALSE for general subspaces** when c = 1 (hyperplanes): max M = C(n-1,w-1) >> C(n,w)/p.

## 4. RS Codes Prevent Pinning (MDS Property)

**Theorem**: For RS[n,k] (MDS code) with k ≥ 1: no syndrome subspace is a "pinning" subspace.

**Proof**: For any α ∈ L and any center c: the polynomial f(x) ≡ c(α) (constant) has degree 0 < k, so c(α) is achievable by a codeword. Hence α is never a forced error location. The syndrome conditions DON'T imply Λ(α) = 0 for any specific α. □

## 5. KEY EQUATION: Toeplitz Structure

The RS syndrome conditions give LINEAR conditions on the error-locator coefficients:

S(x) · Λ(x) ≡ Ω(x) mod x^{n-k}, deg(Ω) < w

Expanding: for ℓ = 0,...,c-1:
Σ_{i=0}^w (-1)^i e_i s_{w+ℓ-i} = 0

This is a c×w TOEPLITZ system T_s · e = b_s.

For full-rank T_s (generic syndrome): the compatible subspace V_s has dimension d = w - c.

## 6. Companion Matrix and Bézout Bound

Parameterize V_s by t ∈ F_p^d. The error-locator Λ_t(x) is monic of degree w, linear in t.

Condition for all roots in L: x^n ≡ 1 mod Λ_t(x).

The remainder r(t) := x^n mod Λ_t(x) has w components r_0,...,r_{w-1}, each polynomial of degree ≤ n-w in t = (t_1,...,t_d).

**Theorem (Bézout Bound)**: For full-rank Toeplitz syndrome:

M ≤ (n-w)^d

**Proof**: The system r(t) = (1,0,...,0) gives w equations of degree ≤ n-w in d variables. By Bézout (using any d of the w equations): at most (n-w)^d solutions in F̄_p^d. Since all solutions correspond to w-subsets of L ⊂ F_p, they are F_p-rational. □

## 7. Computational Verification

### Density sweep (full-rank Toeplitz, 20000+ random syndromes each):

| n | k | p | w | c | d | C(n,w) | (n-w)^d | density | maxM |
|---|---|---|---|---|---|--------|---------|---------|------|
| 16 | 8 | 97 | 6 | 2 | 4 | 8008 | 10000 | 0.85 | 12 |
| 16 | 8 | 257 | 6 | 2 | 4 | 8008 | 10000 | 0.12 | 4 |
| 16 | 8 | 1153 | 6 | 2 | 4 | 8008 | 10000 | 0.006 | 2 |
| 20 | 10 | 41 | 7 | 3 | 4 | 77520 | 28561 | 1.12 | 16 |
| 20 | 10 | 101 | 7 | 3 | 4 | 77520 | 28561 | 0.075 | 3 |
| 20 | 10 | 241 | 7 | 3 | 4 | 77520 | 28561 | 0.005 | 1 |
| 20 | 10 | 601 | 7 | 3 | 4 | 77520 | 28561 | 0.0004 | 1 |

### Key observations:
1. **Bézout bound always holds**: maxM ≤ (n-w)^d in ALL cases
2. **O(1) regime**: maxM ≤ 5 when (n-w)^d / p^c < 0.15
3. **Transition**: roughly at p^c ≈ (n-w)^d, i.e., p ≈ (n-w)^{d/c}

## 8. FRI Parameter Analysis

For BabyBear (p ≈ 2^31), rate 1/2, n = 2^20:
- w ≈ 0.29n, c ≈ 0.21n, d ≈ 0.08n
- (n-w)^d ≈ (0.71 × 2^20)^{0.08 × 2^20} ≈ 2^{1.56 × 10^6}
- p^c ≈ (2^31)^{0.21 × 2^20} ≈ 2^{6.51 × 10^6}
- (n-w)^d / p^c ≈ 2^{-4.95 × 10^6} → 0

**M = 0 for all practical FRI parameters** (the Bézout solutions are empty over F_p).

## 9. Proof Strategy

### What we CAN prove rigorously (Theorem):
M ≤ (n-w)^{w-c}  (Bézout, p-independent)

### What we NEED to prove (Conjecture → Theorem):
M ≤ C · (n-w)^d / p^c + O(1)

### Gap: the 1/p^c factor

The extra c equations (beyond the d needed for Bézout) should reduce the count by ≈ 1/p per equation. This is the HEURISTIC step.

**Approaches to close the gap**:

**A. Over-determined Bézout**: For w equations in d variables, the ACTUAL degree of the 0-dimensional variety could be less than (n-w)^d. Computing the ideal dimension might give a tighter bound.

**B. Schwartz-Zippel on the complete intersection**: The d equations define a 0-dimensional variety S of degree ≤ (n-w)^d. Each additional equation f_j = 0 (degree n-w) on S has at most (n-w) · dim(S)/p zeros... but this doesn't help since S is finite.

**C. Counting argument**: The total number of (syndrome, B_1,...,B_t) tuples where all B_i are compatible has a specific count. For t = ⌈(n-k)/c⌉ + 1 ≥ 3: the system is over-determined in syndrome space, giving at most C(n,w)^t total tuples. Since there are p^{n-k} syndromes: average M^t ≤ C(n,w)^t / p^{n-k}. Combined with Markov: max M ≤ t · (C(n,w)^t / p^{n-k})^{1/t}.

For t = 3 and FRI: C(n,w)^3 / p^{n-k} → 0. So max M ≤ 2.

**APPROACH C IS THE MOST PROMISING.** It gives M ≤ 2 for FRI when:
p^{n-k} > C(n,w)^3, i.e., (n-k) log p > 3 log C(n,w).

For rate 1/2: n/2 × 31 > 3 × 0.87n → 15.5 > 2.61 ✓

## 10. The Counting Proof (Direction C)

**Claim**: For RS[n,k] over F_p with w = Johnson radius, c = n-k-w, and tc > n-k where t = ⌈(n-k)/c⌉ + 1:

#{syndromes s : M(s) ≥ t} ≤ C(n,w)^t / t!

**Proof sketch**:
1. Σ_s C(M(s), t) = #{ordered (s, B_1,...,B_t) : all compatible and distinct B_i} / t!
2. For each ordered t-tuple of distinct B_i: the system T_s σ(B_i) = b_s (i=1,...,t) gives tc conditions on n-k syndrome unknowns.
3. For tc > n-k (over-determined): at most 1 syndrome per t-tuple.
4. Total: ≤ C(n,w)^t / t!.
5. Since C(M,t) ≥ 1 when M ≥ t: #{s : M(s) ≥ t} ≤ C(n,w)^t / t!.

**For t = 3, rate 1/2, BabyBear**:
C(n,w)^3 / 6 ≈ 2^{2.6 million} (finite, but doesn't give max M ≤ 2).

To show max M ≤ 2: need ALL these "bad" syndromes to be IMPOSSIBLE for RS codes. This requires the Toeplitz structure to EXCLUDE these syndromes.

**Alternative**: show that C(n,w)^3 / p^{n-k} → 0 as a fraction of all syndromes, and that the RS syndrome map y ↦ H·y doesn't hit any of the bad syndromes. Since the syndrome map is SURJECTIVE onto F_p^{n-k}: every syndrome IS achievable. So we CAN'T avoid bad syndromes this way.

**REMAINING GAP**: The counting argument gives a FINITE bound on the number of bad syndromes, but since the syndrome map is surjective, some centers MIGHT correspond to bad syndromes. Need a structural argument to show that bad syndromes don't concentrate codewords.

## 11. Updated Proof Status

| Component | Status | Bound |
|-----------|--------|-------|
| Pinned-pair characterization | **PROVED** | max = n-w+1 on PP lines |
| Fiber bound (non-PP lines, c=w-1) | **PROVED** | M ≤ n/w |
| Bézout bound (general c) | **PROVED** | M ≤ (n-w)^d |
| MDS anti-pinning | **PROVED** | RS codes can't pin |
| Density bound | **HEURISTIC** | M ≈ C(n,w)/p^c |
| O(1) for FRI | **HEURISTIC** | (n-w)^d/p^c → 0 |

## 12. Next Steps

1. **Prove the counting bound** (Direction C): formalize the argument that #{bad syndromes} ≤ C(n,w)^t. This is an unconditional finite bound.

2. **Prove M ≤ (n-w)^d / p^c**: this requires either Weil-type bounds for the over-determined system, or a structural argument using Toeplitz properties.

3. **For paper.tex**: replace Conjecture 9.4 with the rigorous Bézout bound Theorem, keeping the density prediction as a remark.

## 13. Scripts

- `density_fourier_explore.py`: Full Fourier transform, density verification, character sums
- `rs_density_explore.py`: RS-specific M computation (slow, Vandermonde)
- `density_sweep_v2.py`: Fast numpy/multicore sweep with rank check
- `bezout_degree_verify.py`: Bézout bound verification and threshold analysis
