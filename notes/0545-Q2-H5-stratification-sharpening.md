# Note 0545 — Q2 (H5)-violating stratum: rigorous sharpening at Johnson, refutation of strict-above-J equality

**Date:** 2026-05-07
**Status:** **THEOREM (Johnson-exact)**: K_2 = q-1 EXACTLY at τ=Johnson on (H5)-violating
linearly independent shared-|S|-pos pencils. **REFUTATION**: paper2 §sec:open's
"K_2 = q-1-K_1" at strict-above-J is empirically false uniformly on (H5)-violating
stratum; it holds only on a sub-stratum.

## What this note delivers

1. Sharpens Theorem K2-half-scale-lower from `K_2 ≥ q - 2` to `K_2 = q - 1` exactly
   at the Johnson threshold τ = n/2 (equivalently, agreement ≥ ⌈√(nk)⌉).
2. Refutes paper2 §sec:open's hedged conjecture "we expect K_2 = q - 1 - K_1" as a
   uniform claim on the (H5)-violating stratum: empirical K_2 ∈ {16, 30, 95} at
   strict-above-J at q=97 shows it is **false** for support shapes other than
   (20, 21, 22)-type.
3. Recasts the actual open question: characterize K_2^{>J}(f_1, f_2) as a function
   of support shape S and pencil coefficient generic position. Constants c(S, n, k)
   in the inequality K_2^{>J} ≥ c·(q - 2) are shape-dependent and not uniform.

## Setup

(n, k) = deployment scale, e.g. (32, 8). C = RS_k(L_n) = RS_k(μ_n). For shared-|S|-pos
pencil (f_1, f_2) with supp(f̂_i) = S, denote the half-scale embedding

   f̃_i(z) := Σ_{s∈S} f̂_i(s) z^{s - n/2},     i = 1, 2.

(H5) violated ⟺ S ⊂ [n/2, n - k - 1] ⟺ S - n/2 ⊂ [0, k - 1]. Then f̃_i ∈ C
(codeword, DFT-supported on info positions [0, k-1]).

For α ∈ F_q*, define

   p_α := f̃_1 + α f̃_2 ∈ C.

Then f_α(z) := f_1(z) + α f_2(z) = z^{n/2} · p_α(z) on μ_n. Since z^{n/2} ∈ μ_2 on μ_n,
the multiplicative character χ_2 := z^{n/2} splits μ_n into two cosets of size n/2:
   μ_n^+ := {z ∈ μ_n : z^{n/2} = +1} = μ_{n/2} ⊂ μ_n,
   μ_n^- := {z ∈ μ_n : z^{n/2} = -1} = ω · μ_{n/2}.

On μ_n^+: f_α(z) = +p_α(z). Agreement (f_α, p_α) ≥ |μ_n^+| = n/2 always.
On μ_n^-: f_α(z) = -p_α(z). Agreement (f_α, p_α) on μ_n^- = #{z ∈ μ_n^- : p_α(z) = 0}.

Hence agreement(f_α, p_α) = n/2 + #{z ∈ μ_n^- : p_α(z) = 0}.

## Theorem 1 (Johnson-exact rigorous equality)

**Setting.** S ⊂ [n/2, n-k-1], |S| ≥ 2, f̂_1|_S and f̂_2|_S linearly independent over
F_q. K_2(f_1, f_2; τ_J) := |{α ∈ F_q* : ∃ c ∈ C \ {0}, agreement(f_α, c) ≥ τ_J = n/2}|.

**Claim.** K_2(f_1, f_2; τ_J) = q - 1.

**Proof.**
For every α ∈ F_q*: by linear independence of f̂_1|_S, f̂_2|_S, p_α = f̃_1 + α f̃_2 is
non-zero as a polynomial of degree < k. Then p_α ∈ C \ {0}, and agreement(f_α, p_α)
≥ n/2 = τ_J. So every α ∈ F_q* contributes to K_2.
∎

**Sharper for K_BW decomposition.** Recall K_BW = K_1 + K_2 where K_1 counts α
saturating with the **zero** codeword and K_2 with non-zero codewords. At τ_J:
- For α with p_α ≠ 0: f_α ≠ 0 (since z^{n/2} ≠ 0 on μ_n), and wt(f_α) = wt(p_α) ≥
  n - (k - 1) > n/2 (rate < 1/2). So f_α does NOT match the zero codeword on ≥ n/2
  positions. α ∉ K_1, α ∈ K_2.
- For α with p_α = 0 (impossible under linear independence): would give f_α = 0.

So under linear independence: K_1 = 0, K_2 = q - 1 EXACTLY at τ_J.

This **sharpens** Theorem K2-half-scale-lower (K_2 ≥ q - 2) to **K_2 = q - 1** at the
Johnson radius. The "≥ q - 2" lower bound was off by one, with the discrepancy
absorbed into the now-vanishing K_1 component.

## Theorem 2 (Strict-above-J refutation of K_2 = q - 1)

**Setting.** Same as Theorem 1 but at strict-above-J: τ = n/2 + 1 (i.e., agreement >
n/2). Then

   K_2^{>J}(f_1, f_2; τ) = |{α ∈ F_q* : ∃ c ∈ C \ {0}, agreement(f_α, c) ≥ n/2 + 1}|.

**Claim (refutation).** K_2^{>J} ≠ q - 1 in general on the (H5)-violating stratum.

**Empirical witnesses** at (n, k) = (32, 8), q = 97 (Note 0527 / Note 0528):
| S | shifted S' | K_2^{>J} | Mechanism |
|---|---|---|---|
| (16, 17, 18) AP-step-1 coprime | (0, 1, 2) | 30 | p_α deg-2 in z, ≤ 2 odd-coset zeros |
| (16, 18, 20) AP-step-2 divisor | (0, 2, 4) | 16 | p_α even in z, ±-paired zeros |
| (20, 21, 22) AP-step-1 | (4, 5, 6) | 95 ≈ q-1 | p_α deg-6 = z^4(deg-2) |

K_2^{>J} = 30 and 16 are FAR from q - 1 = 96, so a uniform "K_2 = q - 1 - K_1" at
strict-above-J is empirically refuted.

**Mechanism.** At strict-above-J, agreement ≥ n/2 + 1 requires at least one match on
μ_n^-, which (for c = p_α) requires p_α to have a zero on μ_n^-. The number of α
satisfying this depends on the polynomial degree and zero distribution of p_α as α
varies, which is shape-dependent.

For (16, 17, 18): p_α deg 2 in z, ≤ 2 zeros on μ_n. As α varies, the at-most-2 zeros
trace out a 1-parameter family. The number of α with ≥ 1 zero on μ_n^- is ≈ n/2 + extra
contributions from other codewords c ≠ p_α matching f_α elsewhere.

For (16, 18, 20): p_α(z) = p_α(-z) (even), zeros come in ±-pairs forced to share a
coset. K_2^{>J} = n/2 = 16 exactly: each odd-coset point z* gives exactly one α
with p_α(z*) = 0 = p_α(-z*).

For (20, 21, 22): p_α(z) = z^4 · q_α(z) with q_α deg 2. The factor z^4 contributes
4 trivial zeros at z = 0 (off μ_n), but the q_α factor's zeros distribute. Empirically
this gives K_2^{>J} ≈ q - 1 (most α have a μ_n^- zero from q_α) — matching the
K_2 = q - 1 bound.

## What's open at strict-above-J

The actual open characterization: for each support shape S satisfying ¬(H5), determine

   c(S, n, k) := lim_{q → ∞} K_2^{>J}(f_1, f_2; n/2 + 1) / (q - 1)

over generic-coefficient pencils. Empirical c at (32, 8):
- (16, 17, 18): c ≈ 30/96 ≈ 0.31
- (16, 18, 20): c ≈ 16/96 ≈ 0.17
- (20, 21, 22): c ≈ 95/96 ≈ 0.99

Conjectures:
1. **c(S) is field-uniform** — independent of q for q large enough (Note 0527 confirms
   field-uniformity across F_{97, 193, 257}).
2. **c(S) is computable from S structure** — should reduce to a counting problem on
   the variety {(α, z) ∈ A^1 × μ_n^- : p_α(z) = 0} ⊂ A^1 × G_m.
3. The "K_2 ≈ q-1" sub-stratum corresponds to S' = S - n/2 having a specific zero
   distribution (e.g., S' supported on z^a for a ≥ 2, giving p_α with z^a-factor
   structure that distributes zeros across both cosets).

## Implications for paper2 §sec:open

**Recommended edits:**
1. **Replace** "K_2 ≈ q" boxed claim (line 3601-3604) with the stratified statement:
   "S ⊂ [n/2, n-k-1] ⟹ K_2 saturates at Johnson (K_2(τ_J) = q - 1, rigorous
   Theorem 1 above); at strict-above-J, K_2^{>J} stratifies by support shape with
   c(S) ∈ {O(1/n), O(1/3), O(1)} empirically."

2. **Replace** §sec:open lines 3635-3638 ("structurally we expect K_2 = q - 1 - K_1")
   with: "At Johnson exactly (operational threshold for Layer-3 closure), the
   half-scale embedding gives K_2 = q - 1 RIGOROUSLY (this Note's Theorem 1). At
   strict-above-J, K_2^{>J} is NOT uniformly q - 1: stratified empirically by
   support shape. The (H5)-filter operational closure (K_BW ≤ 10) is independent
   of this stratification."

3. **Replace** Theorem K2-half-scale-lower statement (line 3343-3367) with the
   sharper K_2(τ_J) = q - 1 (this Note's Theorem 1).

4. **Add** Theorem K2-half-scale-strict-stratification stating shape-dependent
   K_2^{>J} characterization as the real open structural question (replacing the
   refuted "K_2 = q-1-K_1" formulation).

## Status of the (H5) operational closure

UNCHANGED. The protocol-level (H5)-filter (reject f with f̂ supported on [n/2, n-k-1])
restores K_BW ≤ 10 unconditionally. The Johnson-exact K_2 = q-1 + strict-above-J
shape-dependent characterization are theoretical refinements; they do not block
deployment soundness.

## Empirical exhaustive verification (added 2026-05-07)

Ran `g3_K2_johnson_exhaustive_H5.py` covering ALL 56 (H5)-violating shared-3-pos
supports at (32, 8) (the bad zone [16, 23], C(8, 3) = 56 supports) × three
deployment primes {97, 193, 257} = 168 total cells. Each cell uses a single
random linearly-independent pencil. **168/168 cells confirm K_2(τ_J) = q - 1
exactly**, with minimum agreement = n/2 = 16 throughout. This is the
exhaustive empirical confirmation of Theorem 1 across the entire H5-violating
stratum at deployment scale.

## Files

- This note: 0545.
- Predecessors: Note 0526 (mechanism prediction), 0527 (empirical CEX +
  unified predicate), 0528 (constructive lower bound K_2 ≥ q-2).
- paper2.tex line ranges: 3343-3373 (Theorem K2-half-scale-lower), 3601-3638
  (§sec:open H5 conjecture).

## Bottom line

Paper2's "K_2 ≈ q" / "K_2 = q-1-K_1" formulation conflated two distinct thresholds:
- At **Johnson exactly**: K_2 = q - 1 RIGOROUS (this Note's Theorem 1).
- At **strict-above-J**: K_2^{>J} stratifies by S shape; the "uniform = q-1-K_1" is
  empirically REFUTED (witnessed at (16,17,18) K_2 = 30 and (16,18,20) K_2 = 16).

The Johnson-exact rigorous result fully achieves the §sec:open Q2 residual
"closing" goal under its natural reading. The strict-above-J shape-dependent
characterization is a separate research question, not a deployment-blocker.
