# Note 0336 — Scale-lift cyclotomic tail lemma: CRT reformulation

**Date:** 2026-05-01 evening
**Branch:** fri-2round-tightness (Conj 4.1 L3 attack)
**Status:** Reformulation of codex Note 0334 target via Chinese Remainder
Theorem on the four block ideals. Reduces to a clean linear-algebra
condition: "top-k coefficients of CRT output vanish ⟺ S contains a full
quarter block".

## Setup (per Note 0334)

- L = ⟨ζ⟩ cyclic of order n = 4k
- Quarter blocks C_b = {x ∈ L : x^k = i^b}, b = 0, 1, 2, 3
- S ⊂ L with |S| = 2k, S_b = S ∩ C_b, s_b = |S_b|
- No-full: s_b < k for every b
- For k ≤ e < 4k, write e = ak + r with 0 ≤ r < k

**Target lemma**: tail_S(x^e) ≠ 0 for every no-full S, equivalently,
x^e |_S is NOT the restriction of any degree < k polynomial.

## Block-interpolation identities (codex Note 0334 + my unfolding)

If degree < k polynomial p satisfies p|_{S_b} = (x^e)|_{S_b} = i^{ab} x^r |_{S_b},
then p = i^{ab} x^r + G_b(x) Q_b(x) where G_b = ∏_{x ∈ S_b}(x − x_i),
deg Q_b < k − s_b.

Define A_b := G_b · Q_b. Then:
- p − i^{ab} x^r = A_b for each b ∈ {0, 1, 2, 3}
- Subtracting any two: A_c − A_b = (i^{ab} − i^{ac}) x^r

So all A_c are determined by A_0 + (constant) · x^r:
- A_c = A_0 + (1 − i^{ac}) x^r for c = 1, 2, 3 (taking b = 0 reference)

## CRT system

Each A_b must be divisible by G_b. So:
- A_0 ≡ 0 (mod G_0)  [A_0 = G_0 Q_0, deg Q_0 < k − s_0]
- A_0 ≡ (i^{ac} − 1) x^r (mod G_c) for c = 1, 2, 3

**By CRT**: since gcd(G_b, G_c) = 1 for b ≠ c (different blocks ⟹ different
roots), these 4 conditions determine A_0 uniquely modulo
$\prod_{b=0}^{3} G_b$, which has degree $\sum s_b = 2k$.

Let CRT(S, a, r) denote this unique polynomial of degree < 2k.

**Constraint from A_0 = G_0 Q_0**: A_0 has degree ≤ s_0 + (k − s_0 − 1) =
k − 1 < k.

## Reformulated lemma

> **Theorem 0336.A (proposed)**: For no-full S (all s_b < k) and any (a, r)
> with 1 ≤ a ≤ 3 and 0 ≤ r < k, deg(CRT(S, a, r)) ≥ k. Equivalently, the top
> k coefficients of CRT(S, a, r) are NOT all zero.

This is the scale-lift cyclotomic tail lemma reformulated.

## Why this is tractable

CRT(S, a, r) is a specific polynomial determined by (S, a, r). Its top k
coefficients are LINEAR functions of certain CRT projection matrices.

For a fixed (a, r), the condition "top-k coefficients of CRT output = 0" is a
SYSTEM of k LINEAR equations in S (encoded via the G_b polynomials). Showing
this system has no no-full solution = paper-grade structural argument.

## Base case k=4 (Note 0332)

Codex's Note 0332 proves this by direct enumeration over Z[ζ_16] (= F[s]/H_d
for d = 16): for every no-full 8-subset S of L_2 = (16, 4) and every
e ∈ [4, 16), tail_S(x^e) ≠ 0.

There are C(16, 8) = 12870 8-subsets, of which 70 contain a full block
(occupancy contains 4). The other 12800 are no-full and tail_S(x^e) ≠ 0 for
e ∈ [4, 16) checked individually.

## Concrete attack at k = 8 (next scale)

n = 32, |S| = 16, blocks of size 8, no-full ⟺ all s_b < 8.

Number of no-full S: C(32, 16) − Σ (full-block configurations) = ~15M, far
too many for individual enumeration.

CRT formulation reduces this to a SYMBOLIC question: for the CRT output
polynomial CRT(S, a, r) of degree < 16, when does it have degree < 8?

**Suggested attack path**:

1. Express CRT(S, a, r) in the dual basis of L = ⟨ζ_{32}⟩ characters.
2. Use the cyclotomic structure of i^{ac} (4-th roots of unity) to factor.
3. Show the top-8 coefficients form a specific Vandermonde-like system.
4. Solve this system: solutions correspond to S being a parity half (which
   is full, contradiction).

## Mod-p sanity verification

Implement CRT(S, a, r) computation in numpy/sympy. Sample 10K random no-full
S at (k, n) ∈ {(8, 32), (16, 64), (32, 128)}, check deg(CRT) ≥ k for each.

If all sampled S satisfy the bound: empirical confirmation. Then prove
structurally.

## Files

- Note 0334 (codex, base statement and identities)
- Note 0332 (codex, k = 4 base case)
- This note (0336): CRT reformulation + attack sketch

## Cross-refs

- Issue #419 master (path c)
- Issue #396 (sub-attack)
- Note 0335 (synthesis + Conj 4.1 progress)

## TODO

1. Implement CRT(S, a, r) symbolic computation
2. Sample-test at k = 8, 16, 32 for no-full S
3. If empirical bound holds: structural proof attempt via Vandermonde
4. Publish in #419 thread once empirical validated
