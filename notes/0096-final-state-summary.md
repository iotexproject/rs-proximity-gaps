# Note 0096 — Final State Summary, Berlekamp #322 Branch

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322` (pushed)
**Issue**: https://github.com/raullenchai/ef1m/issues/322

## TL;DR

The original v3 conjecture `max_bad ≤ ⌊(2D-1)/c⌋ for any c, n` is **disproved at c=2**
by the c=2 paper (exponential growth `0.63 × 1.355^n`). We refined to:

> **Conjecture v5**: For RS[n, n/2] at sufficiently large p, `max_bad ≤ ⌊(2D-1)/c⌋`
> holds for `c ≥ 3`.

This is the **PHASE TRANSITION at c=3**: c=2 is exponential, c≥3 is linear.

## Key Findings

### Established (rigorous or strong empirical)

1. **Open-Set Rank Lemma fails at c=2** with concrete witness (Note 0092).
   Triangle obstruction: 3 supports forming K_3 on a 3-vertex set.

2. **Open-Set Rank Lemma fails at c=3 small p** with concrete witness (Note 0094).
   Tetrahedron obstruction: 4 supports = all size-3 subsets of a 4-vertex set.

3. **Conjecture v5 holds empirically at large p** for n ∈ {8, 12, 16}.
   At p > 100·bound, max_bad ≤ bound consistently.

4. **At c=c_J (rate 1/2, n ≥ 28)**: empirical bound = 4 (matches #322 comments).

### Open

1. **Rigorous proof of conjecture v5**: prove the Open-Set Rank Lemma at c ≥ 3
   over Q (or "for sufficiently large p"). The proof is hard but conceptually clear:
   construct a Cramer-style determinant identity over Z, show it's non-zero, conclude
   for p > largest-prime-divisor that the lemma holds.

2. **Tight bound at intermediate c**: for 3 ≤ c ≤ c_J - 1, the bound `⌊(2D-1)/c⌋ = O(n/c)`.
   Empirically max_bad is much smaller (often constant). Tight asymptotics open.

## Files Created (this session)

- `STUDIO_TODO.md` — task tracking
- `notes/0091-berlekamp-c322-state.md` — initial state
- `notes/0092-open-set-rank-lemma-failure.md` — c=2 witness analysis
- `notes/0093-cstar-equals-3-conjecture.md` — c*=3 conjecture
- `notes/0094-proof-strategy-c3.md` — proof strategy + tetrahedron witness
- `notes/0095-paper-section-draft.md` — Paper 1 §6.6 draft
- `notes/0096-final-state-summary.md` — this file
- `notes/scripts/op2_max_bad_phase_diagram.py` — main sweep
- `notes/scripts/op2_cstar_largep.py` — large-p sweep
- `notes/scripts/op2_c3_verylarge_p.py` — c=3 large-p verification
- `notes/scripts/op2_verify_lemma_at_c2.py` — c=2 lemma counterexample finder
- `notes/scripts/op2_witness_analysis.py` — witness structural analysis
- `notes/scripts/op2_find_witness_general.py` — general c witness finder
- `notes/scripts/op2_tetrahedron_at_largep.py` — tetrahedron achievability

## Phase Diagram (for paper)

```
c=1  : max_bad = C(n, w) — exponential — saturation regime
c=2  : max_bad ≈ 0.63·1.355^n — exponential — Möbius regime (Paper 1 §6.5)
c=3+ : max_bad ≤ ⌊(2D-1)/c⌋ at large p — LINEAR in n — overconstrained regime (this section)
```

**Transition between exponential and polynomial**: at c=3 (this branch's discovery).

## Connection to Other Threads

- **Paper 1 §6.5 (c=2 exponential)**: companion result, branch `feat/c2-exponential-growth`
- **ConjE / FRI 2-round**: codex 0226 noted "Newton-Girard partial insufficient" — same flavor
- **#347 PR**: pairwise-compatible bound `⌊D/(c-1)⌋` — provides the SUFFICIENT condition
- **#368 ROI map**: this branch addresses "OP2 c=2 quadratic formula proof" line item (P1)

## Next Steps (for follow-up session)

1. **Algebraic proof of v5 conjecture** via determinant construction
2. **Refine bound at intermediate c** (might be sub-linear actually)
3. **Lift to general rate** (currently focused on rate 1/2)
4. **Integrate Paper 1 §6.6** with §6.5 (c=2 exponential)

## Branch State

- 6 commits on `feat/berlekamp-c322`
- Pushed to remote: https://github.com/raullenchai/ef1m/tree/feat/berlekamp-c322
- Notes 0091-0096 cover full investigation
- Scripts cover Phase 1 (empirical) + Phase 2 (proof strategy)
- Paper section draft (§6.6) ready in note 0095
