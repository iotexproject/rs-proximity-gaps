/-
Copyright (c) 2026 Raullen Chai, Xinxin Fan. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.

Finite counting wrappers for the probability-level FRI soundness statement.
-/
import FRISoundness.Coupling

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

The remaining gap to the final theorem is packaging these counting lemmas in
Mathlib's probability monad and connecting the abstract FRI transcript event to
the combinatorial predicates in `Coupling.lean`.
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

end FRISoundness
