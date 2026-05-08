/-
Copyright (c) 2026 Raullen Chai, Xinxin Fan. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

FRI Soundness Above the Johnson Bound via Threshold Halving — Core Definitions.
-/
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Finset.Card
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Tactic

open Finset Fintype

namespace FRISoundness

variable {L : Type*} [Fintype L] [DecidableEq L]
variable {F : Type*} [Field F] [DecidableEq F]

/-! ## Agreement and error sets -/

/-- The agreement set of two functions: {x ∈ L : f(x) = g(x)} -/
def agreeSet (f g : L → F) : Finset L :=
  Finset.univ.filter (fun x => f x = g x)

/-- The error set: {x ∈ L : f(x) ≠ g(x)} -/
def errorSet (f g : L → F) : Finset L :=
  Finset.univ.filter (fun x => f x ≠ g x)

/-- Joint agreement set: positions where both pairs agree -/
def jointAgreeSet (f₁ f₂ g₁ g₂ : L → F) : Finset L :=
  Finset.univ.filter (fun x => f₁ x = g₁ x ∧ f₂ x = g₂ x)

/-- The linear combination f₁ + γ · f₂ -/
def linComb (f₁ f₂ : L → F) (γ : F) : L → F :=
  fun x => f₁ x + γ * f₂ x

/-! ## Cardinality lemmas -/

/-- Inclusion-exclusion: |A ∩ B| + n ≥ |A| + |B| for subsets of a finite type -/
theorem card_inter_add_card_univ_ge {α : Type*} [Fintype α] [DecidableEq α]
    (A B : Finset α) :
    (A ∩ B).card + card α ≥ A.card + B.card := by
  have h := (card_union_add_card_inter A B).symm
  have hle : (A ∪ B).card ≤ card α := card_le_univ _
  omega

end FRISoundness
