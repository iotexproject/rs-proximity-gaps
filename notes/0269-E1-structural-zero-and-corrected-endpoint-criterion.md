# Note 0269 — E_1 ≡ 0 mod chain (universal): corrected endpoint criterion

**Date:** 2026-04-29 night (corrected)
**Status:** STRUCTURAL THEOREM proving E_1 at any d-chain is identically
zero modulo I_chain. This corrects the over-naive single-endpoint
conjecture in Note 0268 and gives the SHARP universal endpoint criterion.

## Theorem 0269 (E_1 ≡ 0 mod chain)

**Theorem.** For all d ≥ 2, the endpoint E_1 := 14 V_1 - 3 [z^1] U² at
the d-chain is identically zero modulo the chain ideal I_chain^{(d)}.

**Proof.** At any d ≥ 2:
- V_1 = [z^1] X² = 0 (since X = Σ_{i=1}^{d-1} x_i z^i starts at z^1, so X²
  starts at z^2).
- U(z) = X(z) - W(z) where W(z) = Σ_{c=0}^{d-1} W_c z^c.
- U² = W_0² + 2(-W_0)(x_1 - W_1) z + …
- [z^1] U² = -2 W_0 (x_1 - W_1).

Hence E_1 = 14·0 - 3·(-2 W_0 (x_1 - W_1)) = 6 W_0 (x_1 - W_1).

Now the chain c_1 at d-chain: c_1 = (x_1 - W_1) + 3 V_1 + 2 (X·W)_1 - (W²)_1.
- V_1 = 0.
- (X·W)_1 = Σ_a x_a W_{1-a} with 1 ≤ 1-a < d. For a=1: 1-a=0, excluded.
  For a > 1: 1-a < 0, invalid. So (X·W)_1 = 0.
- (W²)_1 = Σ_a W_a W_{1-a} with a, 1-a ∈ [1, d-1]. Empty range. So (W²)_1 = 0.

Therefore c_1 = x_1 - W_1.

So E_1 = 6 W_0 · c_1 ≡ 0 mod (c_1) ⊆ I_chain. ∎

## Empirical verification

At h=8 + E_2: vdim = 5 (length-4 orbit survives, 4 + origin = 5).
By Self-Similarity (Note 0267): E_2 at h=8 → E_{2·4/8} = E_1 at d=4 chain.
E_1 ≡ 0 mod chain ⟹ E_2 vanishes on V_4^primitive at h=8.

This explains the empirical h=8 + E_2 = vdim 5.

## Corrected single-endpoint criterion

For closure of h-chain via single endpoint E_c, ALL of these are required:
1. **Z/h-divisibility:** for each divisor d > 1 with V_d^prim ≠ ∅: (h/d) | c.
2. **Avoid E_1 reduction:** c·d/h ≠ 1 for each such d, i.e., c ≠ h/d for each
   divisor d ≥ 2 with V_d^prim ≠ ∅.
3. **Intrinsic non-vanishing:** for each such d, E_{c·d/h} at d-chain is
   non-vanishing on V_d^prim.

## For h = 2^k

V_d^prim ≠ ∅ for d ∈ {4, 8, 16, …, 2^k}. Restrictions on c:
1. Divisibility: 2^(k-j) | c for j ∈ {2, 3, …, k}.
2. Avoid E_1: c ≠ 2^(k-j) for j ∈ {2, …, k}, i.e., c ∉ {1, 2, 4, …, 2^(k-2)}.
3. Intrinsic non-vanishing at each d=2^j.

Candidate c values: must satisfy (1) lcm condition and (2) avoid {1, 2, …, 2^(k-2)}.

The smallest c satisfying (1) and (2) is **c = 2^(k-1) = h/2**.

(In particular, c = 2^(k-2) does NOT work — it's in the avoid set, since
c = 2^(k-2) corresponds to j = 2 obstruction.)

## Verified at small h

| h = 2^k | k | c = 2^(k-1) | empirical | matches prediction? |
|---|---|---|---|---|
| 4 | 2 | 2 | h=4 + E_2 verified close (single-endpoint study earlier) | ✓ |
| 8 | 3 | 4 | h=8 + E_4 = vdim 1 | ✓ |
| 16 | 4 | 8 | h=16 + E_8: pending | predict close |
| 32 | 5 | 16 | h=32 + E_16: pending | predict close |

And the FAILED cases (small c violating criterion):

| h | bad c | reason | empirical |
|---|---|---|---|
| 8 | E_2 | c = 2 = 2^1 = 2^(k-2), reduces to E_1 at d=4 | vdim 5 (length-4 survives) ✓ |

## Implications for h = 12 (composite, multiple prime divisors)

V_d^prim at h=12: d ∈ {3, 4, 6, 12} (with k_d as derived).

Required for single endpoint c at h=12:
1. Divisibility: 4 | c (length-3, h/d=4), 3 | c (length-4, h/d=3),
   2 | c (length-6, h/d=2), any (length-12).
   lcm(4, 3, 2) = 12 → c = 12 only (out of range [2, 11]).
2. Avoid c = h/d = {12/3, 12/4, 12/6, 12/12} = {4, 3, 2, 1}.

(1) + (2): no c in [2, 11] works. **Single endpoint INSUFFICIENT at h=12.**

For 2-endpoint sets {c_1, c_2}: c_1 covers some orbit lengths, c_2 covers
others, and avoidance must hold pairwise.

Closing 2-endpoint sets at h=12:
- Length-3 needs c with 4|c and c ≠ 4 → c = 8 (only option).
- Length-4 needs c with 3|c and c ≠ 3 → c ∈ {6, 9}.
- Length-6 needs c with 2|c and c ≠ 2 → c ∈ {4, 6, 8, 10}.

Minimal closing 2-endpoint sets:
- **{E_8, E_6}**: c=8 kills length-3, length-6; c=6 kills length-4, length-6.
- **{E_8, E_9}**: c=8 kills length-3, length-6; c=9 kills length-4.

(Length-12 killed by any c ≥ 2, c ≠ 1.)

## Generalized universal endpoint criterion

**Conjecture C269.** For h with prime factorization h = ∏ p_i^{a_i},
the minimal endpoint set has size = number of distinct primes p_i with
V_{h/p_i}^prim ≠ ∅, with explicit constructions:
- For each such p_i, choose c = (h/p_i) · (p_i - 1) (this satisfies
  divisibility for all length-d orbits with d = h/p_i^j, and avoids E_1).

For h = 2^k (single prime 2): 1 endpoint, c = (h/2) · 1 = h/2 = 2^(k-1).
For h = 2 · 3 = 6: 2 endpoints, c_1 = 3·1 = 3, c_2 = 2·2 = 4.
For h = 4 · 3 = 12: 2 endpoints, c_1 = 4·2 = 8, c_2 = 3·2 = 6.
For h = 2^a · 3 (general): 2 endpoints, c_1 = 2^(a-1)·1·3, c_2 = 2^a · 2.

This gives **endpoint set of size ω(h) = number of distinct prime factors of h**.

For deployment fields h = 2^k: ω = 1, so **single endpoint suffices**.

## Files

- Note 0269: this note (corrected criterion).
- Note 0268: superseded — single-endpoint claim refined.
- Note 0267: foundation (chain self-similarity).
- Note 0266: orbit existence at small d.
- Note 0265: Z/h-orbit obstruction theorem.
