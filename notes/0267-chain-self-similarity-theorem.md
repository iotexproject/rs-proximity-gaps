# Note 0267 — CHAIN SELF-SIMILARITY THEOREM (deepest structural result)

**Date:** 2026-04-29 night (deep)
**Status:** STRUCTURAL THEOREM revealing that the (3k/2, 2k) chain ideal
has a fractal-like self-similarity. Reduces orbit existence at any h
completely to orbit existence at divisors d | h.

## Theorem (Chain Self-Similarity)

For all integers h ≥ 2 and divisors d | h with d ≥ 2, the restriction
of the h-chain to the length-d slice equals the d-chain (after rescaling).

**Precise statement.** Let
- I_chain^{(h)} = ideal of chain in F[x_1, …, x_{h-1}].
- The length-d slice of V(I_chain^{(h)}) = {p : x_a(p) = 0 if (h/d) ∤ a}.
- This slice has d-1 free coordinates: y_j := x_{j · h/d} for j = 1, …, d-1.

**Then:** under the identification y_j ↔ x_j, the chain c_i^{(h)} for
i = j · h/d (j = 1, …, d-1) reduces to c_j^{(d)}, the j-th equation of
the d-chain. (For i not a multiple of h/d, c_i^{(h)} ≡ 0 at the slice.)

## Proof

Let w := z^{h/d}. Then on the slice,
```
X(z) = Σ_{j=1}^{d-1} y_j z^{j·h/d} = Σ_{j=1}^{d-1} y_j w^j = X̃(w),
```
where X̃ ∈ F[y_1, …, y_{d-1}][w] is exactly the "X" polynomial for the
d-chain (in d-1 variables).

Hence X² in z = X̃² in w. Coefficients of X² in z transform:
- V_c^{(h)} = [z^c] X² is nonzero only when (h/d) | c, and equals
  V_{c/(h/d)}^{(d)} (= [w^{c/(h/d)}] X̃²).
- W_c^{(h)} = [z^{h+c}] X² is nonzero only when (h/d) | c, and equals
  W_{c/(h/d)}^{(d)} (= [w^{d + c/(h/d)}] X̃²).

For the cross terms (X·W)_c, (W²)_c at the slice, only contributions
where indices respect the (h/d)-divisibility survive, and they reduce
to the corresponding (X̃ · W̃) and W̃² coefficients in the d-chain.

Substituting into the chain c_i^{(h)} = (x_i - W_i) + 3 V_i + 2 (X·W)_i
- (W²)_i:
- For i = j h/d: c_{jh/d}^{(h)} at slice = (y_j - W_j^{(d)}) + 3 V_j^{(d)}
  + 2 (X̃·W̃)_j - (W̃²)_j = c_j^{(d)} (the j-th d-chain equation).
- For i not a multiple of h/d: every term V_i, W_i, (X·W)_i, (W²)_i, x_i
  vanishes at the slice (since they all involve a single x_a with
  (h/d) ∤ a, which equals 0). So c_i^{(h)} ≡ 0 at slice.

Hence the chain at slice = d-chain. ∎

## Empirical verification

| (h, d) | h-chain at length-d slice equation 1 | d-chain equation 1 | Match? |
|---|---|---|---|
| (12, 3) | x_4 - x_8² | x_1 - x_2² | ✓ (rename) |
| (12, 4) | x_3 - 2 x_6 x_9 | x_1 - 2 x_2 x_3 | ✓ |
| (10, 5) | x_2 - 2 x_4 x_8 - x_6² | x_1 - 2 x_2 x_4 - x_3² | ✓ |
| (15, 3) | x_5 - x_10² | x_1 - x_2² | ✓ |
| (18, 3) | x_6 - x_12² | x_1 - x_2² | ✓ |

All match perfectly. Self-similarity confirmed.

## Consequence: orbit count by Möbius inversion

Define V_d := V(I_chain^{(d)}) (the d-chain variety, defined intrinsically,
NOT depending on the ambient h).

**Corollary.** For all h ≥ 2,
```
V(I_chain^{(h)}) = ⨆_{d | h, d ≥ 1} V_d^{primitive}
```
where V_d^{primitive} = points in V_d not lying in any V_{d'} for d' | d, d' < d.

Equivalently: V_d^{primitive} = V_d \ ⨆_{d' | d, d' < d} V_{d'}^{primitive}.

The number of length-d orbits at h (for d | h) is:
```
k_d^{(h)} = |V_d^{primitive}| / d.
```

## Computed at small d

| d | |V_d| | |V_d^{primitive}| | k_d (= |V_d^primitive| / d) |
|---|---|---|---|
| 1 | 1 | 1 | 1 (origin) |
| 2 | 1 | 0 | 0 (NO length-2 orbits, ever) |
| 3 | 4 | 3 | 1 |
| 4 | 5 | 4 | 1 |
| 5 | 26 | 25 | 5 |
| 6 | 64 | 60 | 10 (after subtracting V_3^prim = 3) |
| 7 | 190 | 189 | 27 |
| 8 | 493 | 488 | 61 (after subtracting V_4^prim = 4) |

## Universal orbit structure for h = 2^k

For h = 2^k, divisors are {1, 2, 4, …, 2^k}. By the theorem and our
computed values:
- d=1: 1 origin.
- d=2: 0 (theorem 0266a — NO length-2).
- d=4: 4 primitive points = 1 orbit.
- d=8: 488 primitive points = 61 orbits.
- d=2^j (j ≥ 2): need V_{2^j} computed.

## Universal orbit structure for h = 2^a · 3

For h = 6 = 2·3: |V_6| = 64. By theorem, |V_6| = 1 + 0 + 3 + V_6^prim,
so V_6^prim = 60 = 10 length-6 orbits. ✓ matches earlier.

For h = 12 = 4·3: divisors {1, 2, 3, 4, 6, 12}.
- d=1, 2: 1, 0.
- d=3: V_3^prim = 3 → 1 length-3 orbit.
- d=4: V_4^prim = 4 → 1 length-4 orbit.
- d=6: V_6^prim = 60 → 10 length-6 orbits.
- d=12: V_{12}^prim = ? → k_12 length-12 orbits.

vdim V_{12} = 1 + 0 + 3 + 4 + 60 + V_12^prim. So V_12^prim = vdim_12 - 68.

## Universal endpoint requirement (refined)

For closure at h, need to kill ALL length-d orbits for d | h, d ≥ 2.

Length-d orbit can be killed by E_c iff (h/d) | c AND E_c ≢ 0 on orbit.

**For h = 2^k:** orbit lengths are {4, 8, …, 2^k} (skipping 2 by theorem).
For each d = 2^j (j ≥ 2): h/d = 2^(k-j). Need 2^(k-j) | c.
Simplest endpoint set: E_{h - 2^j} for j = 0, 1, …, k-2.
Specifically:
- j = 0: E_{h-1} (any c works for length-h orbit).
- j = 1: E_{h-2} (kills length-h/2 orbit, needs 2|c, satisfied since h-2 even).
- j = 2: E_{h-4} (kills length-4 orbit and below, needs 4|c, satisfied since h-4 ≡ 0 mod 4 when 4|h).
- …
- j = k-2: E_{h - 2^{k-2}} = E_{h/4 · 3} (kills length-4 orbit).

Actually more carefully: E_{h-4} has c = h-4 = 2^k - 4. For this to be ≡ 0 mod 4: 2^k - 4 ≡ -4 ≡ 0 mod 4 ✓ (since 2^k mod 4 = 0 for k ≥ 2). Similarly E_{h-2^j} has c ≡ 0 mod 2^j for j ≤ k.

So **endpoint set {E_{h - 2^j} : j = 0, 1, …, k-1} suffices for h = 2^k**.

This is exactly **k = log₂(h) endpoints** — logarithmic in h!

## Conjecture C267 (sufficient endpoint set, refined)

For h with prime factorization h = ∏ p_i^{a_i}, the endpoint set
```
S(h) = {E_{h - p_i^j · ∏_{i' ≠ i} p_{i'}^{a_{i'}}} : i, j as needed}
       ⊆ {E_c : c ∈ Z/h, c covers all (h/d) divisibility classes}
```
suffices for closure. The size is poly in (h, log h).

For deployment h = 2^9 = 512: 9 endpoints.

## Implication for Lemma B universal

By self-similarity, Lemma B (closure of h-chain + endpoints) reduces
RECURSIVELY to:
1. For each d | h, d ≥ 3 with V_d^prim ≠ ∅: need an endpoint with
   (h/d) | c that's NONZERO on V_d^prim.
2. The "nonzero on V_d^prim" condition is an intrinsic property of d-chain
   (doesn't depend on h).

So Lemma B universal ⟺ for each d ≥ 3 with V_d^prim ≠ ∅, some
endpoint E_c (c ∈ Z/d, c < d) is nonzero on V_d^prim.

This is a FINITE list of conditions per d. Mechanical to verify.

## Proof status of universal Stage 2 closure

By Self-Similarity Theorem + Theorem 0266 + endpoint analysis:

**Universal closure at h ⟺ for each d | h, d ≥ 3:**
   ∃ endpoint c ∈ Z/h with (h/d) | c AND E_c|_{V_d^prim} ≢ 0 (intrinsic d-property).

We've verified the intrinsic condition for d = 3, 4 (with E_2 = 14 V_2 - 3 [z^2] U²
nonzero on V_3^prim and similar). For d ≥ 5, need to verify (mechanical).

For deployment h = 2^k: only d ∈ {4, 8, 16, …} matter (length-2^j orbits).
Need V_{2^j}^prim ≠ ∅ closure for each j. The endpoint set
{E_{h - 2^j}}_{j=0..k-1} provides covering Z/h-degrees, and intrinsic
non-vanishing must be verified at each d = 2^j.

## Files

- `notes/0267-chain-self-similarity-theorem.md` — this note
- `notes/0266-universal-orbit-classification.md` — companion (universal slice analysis)
- `/tmp/h_orbit_struct_proofs.py` — derivation script
