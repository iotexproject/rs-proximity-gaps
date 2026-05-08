/-
Copyright (c) 2026 Raullen Chai, Xinxin Fan. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

Finite counting wrappers for the probability-level FRI soundness statement.
-/
import FRISoundness.Coupling
import Mathlib.Data.Rat.Cast.Defs

namespace FRISoundness

/-!
The paper states the FRI soundness bound as

  Pr[accept] ≤ nR / |F| + (1 - δ/2)^q.

This file records the elementary finite-counting numerators behind that
probability statement.  Dividing these numerators by the corresponding uniform
sample spaces gives the probability form used in the paper:

* commit phase: at most `n * R` bad random challenges;
* query phase: if at least `d` of `n` positions catch the deviation, then at
  most `(n - d)^q` length-`q` query strings miss all catching positions.

The remaining gap to the final paper-form theorem is connecting the abstract
event predicate of `UniformTranscriptModel` to the concrete FRI verifier
acceptance predicate; we expose rational uniform-probability wrappers below
so that step is purely a transcript-encoding exercise.
-/

/-- Commit-phase numerator: the bad challenge count is bounded by `n * R`. -/
theorem commit_phase_count_bound (n R badChallenges : ℕ)
    (hbad : badChallenges ≤ 1 + (R - 1) * n)
    (hn : 0 < n) (hR : 0 < R) :
    badChallenges ≤ n * R := by
  exact hbad.trans (bad_alpha_count n R hn hR)

/--
Query-phase numerator: if `catching + missing = n`, and at least `d` positions
catch a bad word, then the number of all-missing `q`-query strings is bounded
by `(n - d)^q`.
-/
theorem query_phase_miss_count_bound
    (n d q missing catching : ℕ)
    (hpartition : missing + catching = n)
    (hcatch : d ≤ catching) :
    missing ^ q ≤ (n - d) ^ q := by
  have hsum : missing + d ≤ n := by
    calc
      missing + d ≤ missing + catching := Nat.add_le_add_left hcatch missing
      _ = n := hpartition
  have hmissing : missing ≤ n - d := Nat.le_sub_of_add_le hsum
  exact Nat.pow_le_pow_left hmissing q

/--
Counting-form FRI soundness skeleton.  This is the numerator-level analogue of
`nR/|F| + (1 - δ/2)^q`: the commit numerator contributes `nR`, and the query
miss numerator contributes `(n-d)^q`.
-/
theorem fri_soundness_above_johnson_counting
    (n R q d badChallenges missing catching : ℕ)
    (hbad : badChallenges ≤ 1 + (R - 1) * n)
    (hn : 0 < n) (hR : 0 < R)
    (hpartition : missing + catching = n)
    (hcatch : d ≤ catching) :
    badChallenges + missing ^ q ≤ n * R + (n - d) ^ q := by
  exact Nat.add_le_add
    (commit_phase_count_bound n R badChallenges hbad hn hR)
    (query_phase_miss_count_bound n d q missing catching hpartition hcatch)

/-! ## Uniform-transcript event model and rational probability wrappers -/

/--
A finite transcript space carrying a decidable event predicate.

The verifier is modelled as sampling a transcript uniformly from `Ω`; the
event-probability bound is given as a rational `eventCount / |Ω|` in
`eventProb` below. We deliberately stay at the rational-counting level
rather than wiring this into `Mathlib.Probability.PMF`, because the
remaining gap to a paper-form theorem is the protocol-event encoding,
not the probability monad. -/
structure UniformTranscriptModel (Ω : Type*) [Fintype Ω] [Nonempty Ω] where
  /-- The transcript event whose probability is being bounded. -/
  event : Ω → Prop
  decEvent : DecidablePred event

attribute [instance] UniformTranscriptModel.decEvent

/-- Number of accepting/bad transcripts in a finite uniform transcript model. -/
def UniformTranscriptModel.eventCount
    {Ω : Type*} [Fintype Ω] [Nonempty Ω]
    (T : UniformTranscriptModel Ω) : ℕ :=
  (Finset.univ.filter T.event).card

/-- Size of the transcript sample space. -/
def UniformTranscriptModel.spaceSize
    (Ω : Type*) [Fintype Ω] : ℕ :=
  Fintype.card Ω

/-- Rational probability of an event in a finite uniform transcript model. -/
def UniformTranscriptModel.eventProb
    {Ω : Type*} [Fintype Ω] [Nonempty Ω]
    (T : UniformTranscriptModel Ω) : ℚ :=
  (T.eventCount : ℚ) / (UniformTranscriptModel.spaceSize Ω : ℚ)

/--
Uniform-probability monotonicity: if at most `bound` outcomes are bad among
`total` equally likely outcomes, then the rational bad-event probability is at
most `bound / total`.
-/
theorem uniform_probability_bound (hits bound total : ℕ)
    (h : hits ≤ bound) (htotal : 0 < total) :
    (hits : ℚ) / (total : ℚ) ≤ (bound : ℚ) / (total : ℚ) := by
  exact div_le_div_of_nonneg_right
    (Nat.cast_le.mpr h)
    (le_of_lt (Nat.cast_pos.mpr htotal))

/--
Rational-probability form of the FRI soundness skeleton.  This divides the
commit and query numerators by their uniform sample-space sizes and combines
the two bounds by a union-bound-style addition.

This is deliberately still transcript-agnostic: `badChallenges` and
`missing ^ q` are the counted bad outcomes supplied by the combinatorial layer.
The remaining formalization step is to instantiate the abstract transcript event
with the concrete interactive/non-interactive FRI transcript acceptance
predicate.
-/
theorem fri_soundness_above_johnson_rational_bound
    (fieldCard n R q d badChallenges missing catching : ℕ)
    (hbad : badChallenges ≤ 1 + (R - 1) * n)
    (hfield : 0 < fieldCard) (hn : 0 < n) (hR : 0 < R)
    (hpartition : missing + catching = n)
    (hcatch : d ≤ catching) :
    (badChallenges : ℚ) / (fieldCard : ℚ) +
        ((missing ^ q : ℕ) : ℚ) / ((n ^ q : ℕ) : ℚ) ≤
      (((n * R : ℕ) : ℚ) / (fieldCard : ℚ)) +
        ((((n - d) ^ q : ℕ) : ℚ) / ((n ^ q : ℕ) : ℚ)) := by
  exact add_le_add
    (uniform_probability_bound badChallenges (n * R) fieldCard
      (commit_phase_count_bound n R badChallenges hbad hn hR) hfield)
    (uniform_probability_bound (missing ^ q) ((n - d) ^ q) (n ^ q)
      (query_phase_miss_count_bound n d q missing catching hpartition hcatch)
      (show 0 < n ^ q from Nat.pow_pos hn))

end FRISoundness
