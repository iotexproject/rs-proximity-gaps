# Note 0318 — Cross-branch contribution to paper2: structural issue in Note 0315's F(0) closed-form reduction

**Branch:** `feat/op1a-algorithm-fixes` (paper3) — written here for handoff to `fri-2round-tightness` (paper2).
**Date:** 2026-05-01
**Status:** Finding flagged for paper2 owner. Verified symbolically at d=4. Bears on Issue #410 (Q1 universal).

## Headline

Note 0315 (`fri-2round-tightness`) claims:

> **(∗): a_1 ≠ 0 on every Galois-orbit of V_d^prim.** With (i)–(iii), Q1@d holds, where
> a_c := A_c(0) (constant-in-s coefficient of A_c ∈ F̄[s]/H_d(s)),
> and F(0) = (−1)^{d/2}·11·3^{d/2−2}·C_{d/2−1}·a_1^{d/2}.

**The closed-form reduction has a structural issue**: the chain c_1, after substituting x_a = t^a · A_a(s), s = t^d, FORCES a_1 = A_1(0) = 0. The "(∗): a_1 ≠ 0" condition is then vacuous — never satisfied — so the closed-form path doesn't actually reduce Q1 to anything new.

The geometric claim "x_1 ≠ 0 on V_d^prim" (rigorous at d=4 hand-proof, d=8 multi-prime Singular GB at commit `13fcdde`) **stands**. What fails is the further reduction Q1 ⟸ F(0) ≠ 0 ⟸ a_1 ≠ 0.

## Verification (symbolic, d=4)

Script: `notes/scripts/contrib_paper2/verify_note0315_a1_full.py`. Reproduces Note 0315's d=4 chain hand-proof, substitutes x_a = t^a · A_a(s), reduces t^4 → s, and extracts the s=0 coefficient.

Result:

```
[1] c_1 / t  =  4·s·A_1²·A_3 + 2·s·A_1·A_2² − 2·s·A_2·A_3 + A_1
[2] c_2 / t² =  −4·s²·A_2²·A_3² + 8·s·A_1·A_2·A_3 + 2·s·A_2³ − s·A_3² + 3·A_1² + A_2
[3] c_3 / t³ =  −4·s²·A_2·A_3³ + 6·s·A_1·A_3² + 6·s·A_2²·A_3 + 6·A_1·A_2 + A_3

Evaluate at s=0:
  c_1/t at s=0   →   a_1 = 0          (no other coeffs involved — not "empty sum" tautology)
  c_2/t² at s=0  →   3·a_1² + a_2 = 0   (Note 0315 recursion at c=2)
  c_3/t³ at s=0  →   6·a_1·a_2 + a_3 = 0  (Note 0315 recursion at c=3)
```

The c=1 case **does** appear in Lemma 0315.1's recursion `a_c = −3·∑_{a=1}^{c−1} a_a·a_{c−a}` for `c = 1, ..., d−1`. At c=1 the sum is empty, so `a_1 = 0` from the lemma itself. The Catalan corollary's "free parameter a_1" interpretation is inconsistent with this.

Substituting a_1 = 0 (forced by c_1) into the rest:
- a_2 = −3·0² = 0
- a_3 = −6·0·a_2 = 0
- ...
- a_{d/2} = (−3)^{d/2−1}·C_{d/2−1}·0^{d/2} = 0

Therefore F(0) = (−1)^{d/2}·11·3^{d/2−2}·C_{d/2−1}·a_1^{d/2} = 0 **always**, vacuous as a Q1 test.

(Numerical sanity check: `notes/scripts/contrib_paper2/verify_note0315_a1_d4.py` confirms the chain identity `A_1·(1 + 2·s·G_0) − s·G_1 ≡ 0 mod H_d(s)` holds with residual ~5×10⁻¹⁷ at one Newton-found length-4 orbit.)

## Why the empirical / Singular evidence still stands

Note 0315's table records `|x_1| min ≈ 5.7e-2` at d=8 over 16 orbits. This measures `|x_1|` at orbit POINTS, where x_1 = t · A_1(s) for the orbit's specific (t, s). |x_1| ≠ 0 means A_1 ≠ 0 in the field F̄[s]/H_d(s) — a statement about the FIELD ELEMENT, not its constant coefficient A_1(0).

The d=8 multi-prime Singular GB result (commit `13fcdde`) shows
`V(I_chain^{(8)} + ⟨x_1⟩) ⊆ V(⟨x_1, x_3, x_5, x_7⟩)` after saturation. This is a GEOMETRIC statement: every solution of the chain with x_1 = 0 has all odd x's vanishing, hence cannot be a length-8 orbit. Equivalent to "x_1 ≠ 0 on V_8^prim" (the field-element claim).

Both pieces of evidence support **the geometric (∗): "x_1 ≠ 0 on V_d^prim"**, NOT the constant-coefficient (∗): "A_1(0) ≠ 0".

## Why F(0) is forced to 0

Substituting x_a = t^a · A_a(s) and s = t^d into c_c gives
$$
c_c \;=\; t^c \cdot \big[\,A_c(s) \;+\; 3\,F_c(s) \;+\; \text{(terms with explicit } s \text{ factor)}\big] \pmod{H_d(s)},
$$
so c_c ≡ 0 mod H_d ⟹ A_c(s) + 3·F_c(s) + s·(…) = 0 mod H_d. At s=0:
$$
A_c(0) \;+\; 3\,F_c(0) \;=\; 0
\quad\Longleftrightarrow\quad
a_c \;=\; -3\sum_{a+b=c,\,a,b\ge 1} a_a\,a_b.
$$

For c=1, the RHS is empty, so a_1 = 0. **This is not an "empty sum" loophole** — the substituted c_1 polynomial in s genuinely has no constant-in-s term other than A_1 (because the V_1 term is empty and the other quadratic-W terms all carry an explicit factor of s through W_b = t^b · s · G_b for b ≥ 1, or W_0 = s · G_0).

So a_1 = 0 follows rigorously from the substitution, not as a tautology.

## What's actually being asked

The geometric statement is:
- **Q1@d**: F(s) ≢ 0 in F̄[s]/H_d(s) (equivalently, R_d ≢ 0 on V_d^prim).
- **(∗) geometric**: A_1(s) ≢ 0 in F̄[s]/H_d(s) (equivalently, x_1 ≢ 0 on V_d^prim).

Both speak about the FIELD F̄[s]/H_d(s). Neither reduces to a single F̄-valued coefficient.

The closed-form derivation tries to use the surjection F̄[s]/H_d(s) → F̄ via s ↦ 0 to test "F(0) ≠ 0 in F̄", which would imply F ≠ 0 in field. But F(0) = 0 always (by the cascade above), so that test is uninformative.

## What might fix the reduction

A few directions for the paper2 owner:

1. **Use a different specialization point.** s ↦ 0 is one of finitely many specializations of F̄[s]/H_d(s) → F̄. Other specializations (e.g., s ↦ ω where ω is a root of some other polynomial coprime to H_d) may give nonzero F(specialization). One specialization with F(specialization) ≠ 0 suffices to conclude F ≠ 0 in field.

2. **Use the s-adic valuation at s=0.** A_1 has positive s-adic valuation at s=0 (since A_1(0) = 0). Define `v_a := v_{s=0}(A_a) ∈ ℤ_{≥0}` (or ∞ if A_a = 0 in field). The chain identities give recursions for {v_a} and for the "leading s-adic coefficients" of A_a (the first nonzero Taylor coefficient). The right (∗) might be a leading-coefficient non-vanishing statement, not a constant-coefficient one.

3. **Direct geometric reduction.** Show "x_1 ≠ 0 on V_d^prim ⟹ R_d ≠ 0 on V_d^prim" without going through F(0). This would be a CHAIN-level argument: setting R_d = 0 + chain ⟹ x_1 = 0 (by manipulating chain identities and Galois action). The (Z/d)*-equivariance noted in 0315 §"Path to (∗)-proof" Obs 3 is the natural tool.

4. **Replace H_d with something more tractable.** H_d is the "irreducible orbit polynomial"; its degree depends on the orbit. If the right object is "the orbit-extension polynomial for ALL length-d orbits combined" (like the resultant of x_3 from my d=4 GB calculation), the analysis simplifies.

## Concrete handoff

For the paper2 owner working on Issue #410 (Q1 universal):

- The d=8 multi-prime Singular GB result (commit `13fcdde`) is **independently rigorous** — it proves "x_1 ≠ 0 on V_8^prim" without going through F(0). This is the geometric (∗) at d=8.
- The d=4 hand-proof in Note 0315 §"d=4 hand-proof of (∗)" likewise proves the geometric (∗) at d=4.
- These give **rigorous (∗)-geometric** at d ∈ {4, 8}, and empirical-geometric at d ∈ {16, 32, 64} (no Newton-orbit found with |x_1| < 1e-8).
- What still needs work: connecting (∗)-geometric to Q1@d. Note 0315's F(0) closed-form path doesn't do it; one of directions (1)–(4) above (or another) is needed.

Note 0315's empirical evidence and rigorous d=8 GB result are still high-value contributions; only the F(0) closed-form **reduction step** is the one with the issue.

## Files

- `notes/scripts/contrib_paper2/verify_note0315_a1_d4.py` — numerical chain-identity check (residual ~5e-17).
- `notes/scripts/contrib_paper2/verify_note0315_a1_full.py` — symbolic d=4 substitution, exposes a_1 = 0 forcing.
- `notes/scripts/contrib_paper2/verify_note0315_a1_d4_algebraic.py` — full GB enumeration of V(I_chain^4): 25 points (1 origin + 24 length-4 across 6 orbits).

## Cross-refs

- `notes/0315-Q1-F0-closed-form-breakthrough.md` (fri-2round-tightness branch, commit `01ee807` + update `13fcdde`)
- Issue #410 (Q1 universal proof)
- Issue #417 (Q1 cluster sweep)
- paper2 conj:Q1 (Note 0273 fri-2round-tightness)
