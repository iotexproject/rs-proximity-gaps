# Note 0258 — h=5 closure via chain + 2 endpoints (template for general h)

**Date:** 2026-04-29 night
**Status:** Pen-and-paper proof at h=5 in char(F) ∉ {2, 7}. The argument
uses ONLY the y0 chain + endpoint constraints E_{h-2}, E_{h-1} (no bulk).
Lays out the template for the general-h structural attack.

## Setup at h=5

Variables x_1, ..., x_4. Polynomials:
- W_1 = 2 x_2 x_4 + x_3².  W_2 = 2 x_3 x_4.  W_3 = x_4².  W_4 = 0.
- u_c = x_c - W_c.  On V(I_y0): u_1 = 0; u_2 = -4 W_1²; u_3 = -8 W_1(W_2 - 4W_1²); u_4 (computed below).

## Chain (4 equations, on V(I_y0))

```
x_1 = W_1 = 2 x_2 x_4 + x_3².            (chain 1)
x_2 = W_2 - 4 W_1² = 2 x_3 x_4 - 4 W_1². (chain 2)
x_3 = W_3 - 8 W_1 W_2 + 32 W_1³.          (chain 3)
x_4 = -8 W_1 W_3 + 96 W_1² W_2 - 304 W_1⁴ - 4 W_2².   (chain 4)
```

(Chain 4 derived as in Note 0254. At h=5, W_4 = 0 so x_4 = u_4 directly.)

## Endpoint constraints (2 equations, on V(I_y0))

By Note 0257, with U = X − W and δ_k = (3/2) [z^k] U² (Note 0255):

**E_3 = 14 V_3 - 3 [z^3] U² ∈ I_stage2**:
- V_3 = 2 x_1 x_2.
- [z^3] U² = 2 u_1 u_2 = 0 on V(I_y0) (since u_1 = 0).
- So E_3 ≡ 14 · 2 x_1 x_2 mod V(I_y0).
- Substituting chain: x_1 x_2 = W_1 (W_2 - 4 W_1²) = W_1 W_2 - 4 W_1³.
- ⟹ **E_3 = 28 W_1 (W_2 - 4 W_1²) ∈ I.**  (★)

**E_4 = 14 V_4 - 3 [z^4] U² ∈ I_stage2**:
- V_4 = 2 x_1 x_3 + x_2² = 2 W_1 W_3 - 24 W_1² W_2 + 80 W_1⁴ + W_2² (after chain).
- [z^4] U² = 2 u_1 u_3 + u_2² = u_2² = (-4 W_1²)² = 16 W_1⁴ on V(I_y0).
- ⟹ **E_4 = 28 W_1 W_3 - 336 W_1² W_2 + 1072 W_1⁴ + 14 W_2² ∈ I.**  (★★)

## Closure proof

From (★) in char ≠ 2, 7: **W_1 = 0 OR W_2 = 4 W_1²**.

### Case A: W_1 = 0

Then x_1 = W_1 = 0.
(★★) gives 0 - 0 + 0 + 14 W_2² = 0, so **W_2 = 0** (char ≠ 2).
Chain 2: x_2 = W_2 - 4 W_1² = 0.
W_2 = 2 x_3 x_4 = 0 ⟹ x_3 x_4 = 0.
W_1 = 2 x_2 x_4 + x_3² = 0 + x_3² = 0 ⟹ **x_3 = 0**.
Then W_3 = x_4². Chain 3: x_3 = W_3 - 0 + 0 = x_4² ⟹ x_4² = 0 ⟹ **x_4 = 0**.
✓ All zero.

### Case B: W_2 = 4 W_1², W_1 ≠ 0

Chain 2: x_2 = W_2 - 4 W_1² = 0. So **x_2 = 0**.
W_1 = 2 x_2 x_4 + x_3² = 0 + x_3² = x_3². So **x_3² = W_1 ≠ 0**, hence x_3 ≠ 0.
W_2 = 2 x_3 x_4 = 4 W_1² = 4 x_3⁴ ⟹ x_4 = 2 x_3³ (in char ≠ 2).
W_3 = x_4² = 4 x_3⁶.

Substitute into (★★):
28 W_1 W_3 - 336 W_1² W_2 + 1072 W_1⁴ + 14 W_2²
= 28 x_3² · 4 x_3⁶ - 336 x_3⁴ · 4 x_3⁴ + 1072 x_3⁸ + 14 · 16 x_3⁸
= 112 x_3⁸ - 1344 x_3⁸ + 1072 x_3⁸ + 224 x_3⁸
= (112 - 1344 + 1072 + 224) x_3⁸ = 64 x_3⁸ = 0.

Since char ≠ 2: x_3⁸ = 0 ⟹ **x_3 = 0**, contradicting x_3 ≠ 0.

So Case B is empty. ∎

## Bad characteristic set: {2, 7}

The proof uses char ≠ 2 (from "x = 0 ⟹ x_3 = 0", etc.) and char ≠ 7
(from E_3 / 14 division).

## Template for general h

The h=5 closure follows this pattern:

1. **E_{h-1} (after chain on V(I_y0))** factors as W_1 · (something).
   - (Conjecture: E_{h-1} on V(I_y0) is divisible by W_1 — explains the
     "either W_1 = 0 OR …" dichotomy.)

2. **Case A: W_1 = 0** ⟹ chain forces all x_c = 0 trivially.

3. **Case B: the "something" = 0 with W_1 ≠ 0** ⟹ specific algebraic
   relation among W's. Combined with E_{h-2} on V(I_y0) and the
   POLYNOMIAL CONSTRAINT W_a = [z^{h+a}] X² (which expresses W_a in
   x's), get a contradiction via Resultant in char outside a small set.

The challenge: prove (1)-(3) for general h with explicit char-bound.

## Verification

`g3_chain_endpoint_only.py` verified closure at h ∈ {4, 5, 6, 7}. h=8
GB exceeds available time (chain alone has 212 GB elements at h=8).

## Files

- `notes/scripts/g3_chain_endpoint_only.py`: layer-by-layer closure test.
- `notes/scripts/g3_delta_pattern.py`: δ_k computation.
