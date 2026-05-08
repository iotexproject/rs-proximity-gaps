/-
Copyright (c) 2026 Raullen Chai, Xinxin Fan. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

Helper lemmas combining `ca_halved` with the FRI coupling building blocks.
-/
import FRISoundness.CA
import FRISoundness.RSCode

open Finset Fintype

namespace FRISoundness

/-! ## Half-threshold proximity-gap helper

A direct restatement of `ca_halved` over an arbitrary linear submodule
`C' ⊆ (L' → F)`. The paper's `thm:proximity-gap` (the round-1 ≤ 1 bad α
statement) adds one ingredient on top of this helper: the FRI coupling
step `Δ(f, RS_k) > δ ⟹ joint Δ((fE, fO), RS_{k/2}²) > δ`, formalized at
the abstract level as `RSCode.coupling_pointwise` and
`RSCode.coupling_counting`. Wiring those into a paper-faithful theorem
requires an instantiated `RSIsomorphismWitness` for the concrete
multiplicative-coset FRI domain, which is not yet in the library.

The BCIKS '20 Theorem 1.2 transcription (rounds ≥ 2) is *not* part of
this lemma; it enters only at the level of the full FRI soundness
theorem (`thm:fri-full`).

Until the concrete pairing instance is in place we expose the helper
below under the name `proximity_gap_core` so a reader does not mistake
it for the full paper-labelled theorem. -/

/--
**Half-threshold proximity-gap helper** (alias for `ca_halved` on a
folded linear code).

If the joint distance of `(fE, fO)` from `C' × C'` exceeds `2d`, then at
most one `α ∈ F` makes `fE + α · fO` agree with a codeword of `C'` on
`≥ |L'| - d` positions. -/
theorem proximity_gap_core
    {L' : Type*} [Fintype L'] [DecidableEq L']
    {F : Type*} [Field F] [DecidableEq F]
    (C' : Submodule F (L' → F))
    (fE fO : L' → F) (d : ℕ)
    (hprem : ∀ g₁ ∈ C', ∀ g₂ ∈ C',
      (jointAgreeSet fE fO g₁ g₂).card + 2 * d < card L')
    {α₁ α₂ : F} (hne : α₁ ≠ α₂)
    {c₁ c₂ : L' → F} (hc₁ : c₁ ∈ C') (hc₂ : c₂ ∈ C')
    (hA₁ : card L' ≤ (agreeSet (linComb fE fO α₁) c₁).card + d)
    (hA₂ : card L' ≤ (agreeSet (linComb fE fO α₂) c₂).card + d) :
    False :=
  ca_halved C' fE fO d hprem hne hc₁ hc₂ hA₁ hA₂

/-- Per-round union-bound numerator: the sum of round-1 (≤ 1) and rounds
2..R (≤ n each) is bounded by `nR`. -/
theorem bad_alpha_count (n R : ℕ) (hn : 0 < n) (hR : 0 < R) :
    1 + (R - 1) * n ≤ n * R := by
  obtain ⟨R', rfl⟩ : ∃ R', R = R' + 1 := ⟨R - 1, by omega⟩
  simp only [Nat.add_sub_cancel, Nat.mul_succ]
  rw [Nat.mul_comm R' n]
  omega

/-! ## Roadmap note: full paper-labelled FRI soundness theorem

The paper's full FRI-soundness theorem (`thm:fri-full`) bounds
`Pr[FRI accepts] ≤ nR/|F| + (1 - δ/2)^q`. The two combinatorial
components are:
- Round 1 contributes ≤ 1 bad scalar via `ca_halved`.
- Rounds 2..R contribute ≤ |L| bad scalars each, supplied externally by
  BCIKS '20 Theorem 1.2 (zero-loss proximity gap below the Johnson
  bound). A faithful transcription of that theorem against the FRI
  pairing data is not yet in this library.

The probabilistic step is a per-round union bound:
`Σᵢ |bad_i| / |F| ≤ (1 + (R-1)·n) / |F| ≤ nR / |F|`
(NOT a tuple count over `F^R`; see `bad_alpha_count`).

The rational form of the bound is proved in `Probability.lean`
(`fri_soundness_above_johnson_counting`,
`fri_soundness_above_johnson_rational_bound`); converting the rational
inequality to the paper-form probability statement requires a concrete
FRI transcript instantiation. STATUS.md lists this as the priority-1
roadmap item. -/

end FRISoundness
