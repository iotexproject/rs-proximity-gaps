# Note 0255 — δ_k = (3/2) [z^k] U² structural identity

**Date:** 2026-04-29 night
**Status:** **CLEAN STRUCTURAL IDENTITY** for the δ_k correction in the
y0+y2 constraint chain. Replaces the conjectural "δ_k ∈ (x_1²)" pattern
in Note 0254 (which is FALSE for k ≥ 7).

## Statement

In the y0+y2 elimination chain (Note 0254), define the chain residuals:

```
u_c := x_c - W_c        (for c ≥ 1, with x_c via y0 chain)
U(z) := Σ_{c ≥ 1} u_c z^c
```

Then the constraint correction polynomial δ_k satisfies the **closed-form
identity**:

```
δ_k = (3/2) · [z^k] U(z)²
    = (3/2) · Σ_{a+b=k, a,b ≥ 1} u_a u_b.       (*)
```

This is an EXACT polynomial identity (no "mod I" needed) — it's a
consequence of how the y0+y2 chain combines.

## Derivation

Apply y0 c=k after substituting chain x_a (a < k):

```
4 y0_k = (x_k - W_k) + 3 V_k + 2 (X·W)_k - (W²)_k = 0
⟹ x_k = W_k - 3 V_k - 2 (X·W)_k + (W²)_k.
```

Apply y2 c=k after substituting chain x_a (a < k) — but BEFORE substituting x_k:

```
2 y2_k = 3 x_k - 3 W_k - 2 V_k + 2 cubic_k = 0
```

Combine: substitute the y0 expression for x_k into y2_k:

```
3 (W_k - 3 V_k - 2 (X·W)_k + (W²)_k) - 3 W_k - 2 V_k + 2 cubic_k = 0
⟹ -9 V_k - 6 (X·W)_k + 3 (W²)_k - 2 V_k + 2 cubic_k = 0
⟹ 2 cubic_k = 11 V_k + 6 (X·W)_k - 3 (W²)_k
⟹ cubic_k = (11 V_k + 6 (X·W)_k - 3 (W²)_k) / 2.       (C_k constraint W-form)
```

Hence:

```
δ_k = 7 V_k - cubic_k = 7 V_k - (11 V_k + 6 (X·W)_k - 3 (W²)_k) / 2
    = (14 V_k - 11 V_k - 6 (X·W)_k + 3 (W²)_k) / 2
    = (3 V_k - 6 (X·W)_k + 3 (W²)_k) / 2
    = (3/2) (V_k - 2 (X·W)_k + (W²)_k).
```

Recognize the inner quantity as a perfect-square expansion:

```
V_k - 2 (X·W)_k + (W²)_k = [z^k] X² - 2 [z^k] (X · W) + [z^k] W²
                         = [z^k] (X - W)² = [z^k] U².
```

(Where the convolutions V_c = [z^c] X², (X·W)_c = [z^c] (X · W),
(W²)_c = [z^c] W² are standard polynomial Cauchy products.)

Thus:

```
δ_k = (3/2) [z^k] U². ∎
```

## Implications

### (1) The "hidden symmetry" of the y0+y2 chain

The y0 chain expresses x_c via W_c — equivalently, u_c = x_c - W_c is the
"y0-residual". The constraint chain says:

  cubic_c (= [z^{2h+c}] X³) ≡ 7 V_c − δ_c   modulo I_stage2.

The correction δ_c is purely a function of the y0-residuals, with no
"new" content beyond U². This explains why the chain has no obstruction
beyond the y0/y2 layer — it's structurally bounded.

### (2) "δ_k ∈ (x_1²)" conjecture (Note 0254) is FALSE for k ≥ 7

Empirical computation (script `g3_delta_pattern.py` at K=10) shows:

| k | δ_k_in_W (factored)                                                            | x_1²? |
|---|--------------------------------------------------------------------------------|-------|
| 2 | 0                                                                              | trivial |
| 3 | 0                                                                              | trivial |
| 4 | 24 W_1⁴                                                                        | ✓ |
| 5 | -96 W_1³ (4 W_1² - W_2)                                                        | ✓ |
| 6 | 48 W_1² (108 W_1⁴ - 40 W_1² W_2 + 2 W_1 W_3 + 3 W_2²)                          | ✓ |
| 7 | -96 W_1 (704 W_1⁶ - 324 W_1⁴ W_2 + 20 W_1³ W_3 + ...)                          | ✗ (only x_1¹) |
| 8 | 24 (... + W_2⁴)                                                                | ✗ (no x_1 factor) |
| 9 | -96 (... + 20 W_1 W_2⁴ + ...)                                                  | ✗ |

**Reason:** δ_k = (3/2) [z^k] U² is a quadratic in U. For low k (k ≤ 6),
only u_1 (= 0) and u_2, u_3 (= W_1 polynomials) contribute, so x_1²
factor is automatic. For k ≥ 7, terms like u_4·u_3, u_5·u_2 etc. appear
where higher u_c can lack x_1 dependence.

Specifically, **the leading W_1-degree of δ_k drops linearly with k**:
- δ_4: W_1⁴ leading
- δ_5: W_1³ leading
- δ_6: W_1² leading
- δ_7: W_1¹ leading
- δ_8: W_1⁰ (no W_1 factor!) — has W_2⁴ as pure-x_2⁴ term.

### (3) The "endpoint constraint" form

For c ∈ {h-2, h-1}: cubic_c (genuine [z^{2h+c}] X³) = 0 by degree truncation.

So the C_c constraint reduces to:

```
0 = 7 V_c - δ_c        ⟹      14 V_c = 3 [z^c] U²       (mod I_stage2)
```

Equivalently:  **[z^c] (14 X² - 3 U²) ∈ I_stage2** for c ∈ {h-2, h-1}.

Expanding U = X - W: 14 X² - 3 (X - W)² = 14 X² - 3 X² + 6 X W - 3 W²
                                       = 11 X² + 6 X W - 3 W².

So: [z^c] (11 X² + 6 X W - 3 W²) ∈ I_stage2 for c = h-2, h-1.

These are 2 NEW polynomial relations in (x_1, ..., x_{h-1}).

(The "bulk" constraints c ∈ [1, h-3] are: cubic_c = (11 V_c + 6 (X·W)_c - 3 (W²)_c)/2, with cubic_c ≠ 0 and h-dependent.)

## Tighter closure path (h-uniform attempt)

The endpoint constraints, written compactly:

```
[z^{h-1}] (11 X² + 6 X W - 3 W²) ≡ 0 mod I       (E_1)
[z^{h-2}] (11 X² + 6 X W - 3 W²) ≡ 0 mod I       (E_2)
```

where W(z) = Σ_{a≥0} W_a z^a with W_a = [z^{h+a}] X² (the "wraparound" part of X²).

**Claim (TARGET, h-uniform):** Combined with the y0 + y2 chain and the
genuine-cubic constraints for c ∈ [1, h-3], (E_1) and (E_2) force
V(I_stage2) = {origin} for char(F) outside a small bad set.

This is the **structural attack target** for general-h closure.

## Verification

Script `g3_delta_pattern.py --K K`:
- Builds the y0+y2 elimination chain in W's symbolically.
- Computes δ_k_in_W for k = 2..K.
- Inverts chain to express δ_k_in_x.
- Verifies (3/2) [z^k] U² formula against direct cubic_constraint
  derivation.
- Tests x_1² divisibility (now known to fail for k ≥ 7).

Run at K = 10: confirms δ_k_in_W matches both formulations (direct
chain and U² formula) at k = 2..10.

## Connection to Note 0252 master identity

In the master identity αβ = (s⁸ - 1/16) + σX + δU + (X² - U²),
the U field IS the same U = X - W (with appropriate s-inclusion).
The fact that αβ contains the term −U² is structurally tied to the
δ_k = (3/2) [z^k] U² identity here.

This suggests the **Z/h-grading of αβ + the U-decomposition** is the
right framework for h-uniform closure.

## What's next

1. **(C_1) is automatically (E_2 with adjustment)** at small h, but at
   general h, (E_1) and (E_2) together with bulk constraints might force
   X = 0 directly via Bezout-type argument.

2. **U(z) is in the kernel of a specific projection**: u_c = x_c - W_c
   = x_c - [z^{h+c}] X². This is a "wraparound" relation, structurally
   tied to the Z/h-grading.

3. **The Z/h-action on (E_1, E_2) constraints**: under z → ζ z (ζ a
   primitive h-th root of unity), the constraints might decompose into
   h cleaner pieces, yielding a 1-eq-per-character system.

These are concrete next moves toward h-uniform structural closure.

## Files

- `notes/scripts/g3_delta_pattern.py` — chain + δ_k computation, K=10 verified.
- `notes/scripts/g3_stage2_master_identity.py` — αβ master identity (Note 0252).
- `notes/scripts/g3_stage2_normalized.py` — full Stage 2 GB sweep (Note 0251).
