# Note 0104 — FRI 2-round soundness from Conjecture v6 v2

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0099, 0103

## Setup

FRI (Fast Reed-Solomon IOP of Proximity) protocol over RS[F_p, L, k] with
|L| = n, rate ρ = k/n. The 2-round soundness analysis bounds the probability
that a malicious prover passes the verifier's checks given a starting word
that's δ-far from RS[F_p, L, k].

The relevant **proximity gap parameter** is:
```
   ε_{ca}(n, k, δ) := Pr_{γ ∈ F_p^*}[Δ(f_1 + γ f_2, RS_k) ≤ δ]
```
where f_1, f_2 are arbitrary words and Δ is normalized Hamming distance.

For the OP2 setup (after reduction to syndromes), this becomes:
```
   ε_{ca} = Pr_{(s_1, s_2) ∈ F_p^{2D}}[ ∃ γ s.t. line(s_1, s_2; γ) hits Im(V_E)
                                          for some E ∈ C(L, w) ]
```

The relevant quantity for FRI soundness is **max_bad/p** — the fraction of γ's
that are "bad" for a worst-case (s_1, s_2).

## Connection: from v6 v2 to soundness

For ANY (s_1, s_2): max_bad(s_1, s_2) := |{γ : ∃ E s.t. (s_1, s_2, γ, E) bad}|.

**Conjecture v6 v2 says**:
```
   Pr_{(s_1, s_2)}[max_bad(s_1, s_2) > T] ≤ ε_{v6}
```
where T = ⌊(2D-1)/c⌋ and ε_{v6} ≤ poly(n) · p^{-(D + c - 2)}.

**For the FRI verifier**: the verifier picks (s_1, s_2) "at random" via the
challenge mechanism. The probability of selecting a bad (s_1, s_2) is ε_{v6}.

If verifier selects a non-bad (s_1, s_2): max_bad ≤ T, so the prover can fool
the verifier on at most T "bad" γ values out of p choices → soundness gap
T/p per round.

If verifier selects a bad (s_1, s_2): worst case max_bad ≤ #(realized supports),
which is bounded by tetrahedron scaling: ≤ w + 1 + extras (≈ w + O(n) for
large n).

## The soundness theorem (conditional on v6 v2)

**Theorem (conditional)**: For RS[n, k] over F_p with c = n - k - w ≥ 3 and
D = n - k, and any starting words f_1, f_2:
```
   Pr_{γ ∈ F_p^*}[Δ(f_1 + γ f_2, RS_k) ≤ w/n] ≤ T/p + ε_{v6}
                                                 ≤ ⌊(2D-1)/c⌋/p + poly(n) · p^{-(D + c - 2)}
                                                 ≤ (2D + 1)/(c · p) + (negligible)
```

**Soundness amplification**: After q FRI rounds with independent γ's:
```
   ε_{FRI} ≤ ((2D + 1)/(c · p))^q + q · ε_{v6}
            ≤ poly(n) · ε_{v6}        for q · log(p) sufficient
```

For BabyBear at FRI parameters (n, k) = (40, 20), c = c_J = 12:
- (2D+1)/(cp) = 41/(12 · 2^31) ≈ 2^{-29}
- ε_{v6} = poly(40) · 2^{-1054}
- After 4 rounds: ε_{FRI} ≤ 2^{-116} from main + 4 · 2^{-1024} ≈ 2^{-116}.

This matches FRI's known soundness (1/(c·p) per round).

## What's NEW from this branch

1. **Refutation of "uncondition for any (c, n)" version of #322**: tetrahedron
   provides explicit lower bound ≥ w+1, beating the conjectured upper bound at
   every (n, c_J) for n ≥ 12 (Note 0099).

2. **Identification of bad-set structure**: V_bad has multiple components beyond
   tetrahedron. Codim grows linearly in n at fixed c (Note 0103, formula
   2D - T - 2).

3. **Empirical FRI soundness numbers**: poly(n) · 2^{-465} to 2^{-1054} at FRI
   parameters n ∈ {20, 40} c=c_J BabyBear (Note 0104).

## What's needed for prize-ready

1. **Prove Conjecture v6 v2** at general (n, c). Strategy:
   - Catalog all "structural" bad patterns (tet + 4 non-tet sub-patterns observed)
   - Bound codim of each pattern
   - Sum codim bounds for total density

2. **Connect to existing FRI soundness theorems** (BCIKS, Crites-Stewart, BBHR):
   - Identify the regime where v6 v2 gives improvement
   - Specifically: at intermediate c (not Johnson radius), where existing
     bounds are loose

3. **Paper writeup**: Paper 1 §6.6 with corrected Phase Diagram + soundness
   corollary.

## Comparison to existing prize-relevant bounds

| Bound source           | Statement                                  | Status |
|------------------------|--------------------------------------------|--------|
| BCIKS                  | ε_{ca} via algebraic geometry              | Proved |
| Crites-Stewart         | ε_{ca} for c=1 covering radius             | Proved |
| PR #347 (this repo)    | max_bad ≤ ⌊D/(c-1)⌋ under conditions       | Proved |
| Author's #322 v3       | max_bad ≤ ⌊(2D-1)/c⌋ unconditional         | REFUTED |
| **This branch v6 v2**  | Pr[max_bad > T] ≤ poly(n)·p^{-(D+c-2)}     | Conjectured |

## Branch state

- 12 commits on `feat/berlekamp-c322`, all pushed
- 14 notes (0091–0104) covering full investigation
- 30 scripts in `notes/scripts/op2_*`
- ~3500 lines total

## Files

- `notes/0099-tetrahedron-analytic-proof.md` — rigorous Theorem 1
- `notes/0103-revised-v6.md` — Conjecture v6 v2 with non-tet patterns
- `notes/0104-fri-soundness-application.md` — this file
- `notes/scripts/op2_bound_comparison.py` — comparison table

## Distance to prize submission

Per Note 0102 estimates:
- Tighten v6 v2 codim bound: 1-2 weeks
- Prove v6 v2 (full): 3-5 weeks
- Write up FRI soundness theorem: 1 week
- Paper integration: 1-2 weeks
- **Total**: 5-9 weeks for a complete prize-ready submission.
