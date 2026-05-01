# Note 0091 — Berlekamp #322 State (entering branch)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Issue**: https://github.com/raullenchai/ef1m/issues/322

## What #322 has tried (history)

The issue has gone through five versions of the conjectured bound. Each version
was sharpened/falsified by counterexamples, leading to the current target.

### Version timeline

| version | statement | status | note |
|---------|-----------|--------|------|
| original | `max_bad ≤ C(n,w)/p^{m-1}` with `m = n−k−w` | partial | tight only at `m=1` (paper §4); `m≥2` gives expectation, not worst-case |
| v0 (strong) | `max_bad ≤ ⌊D/(c-1)⌋` at `c=c_J` | DISPROVED | counterexamples at `n ∈ {28, 32}`: 4 supports, all-pair overlap=3, give `max_bad = 4 > 2 = ⌊D/(c-1)⌋` |
| v1 (refined) | `max_bad ≤ ⌊2D/c⌋` at `c=c_J` | empirical | verified `n ∈ {28,32,36,40}` at rate 1/2 → `max_bad ≤ 4` universally |
| v2 (slightly sharper) | `max_bad ≤ ⌊(2D-1)/c⌋` for any `c, n` | DISPROVED at `c=1` | Paper 1 §4 RS[6,3] gives `max_bad = 15`, bound says `5`; RS[8,4] gives `56`, bound says `7` |
| **v3 (today's reframing)** | `max_bad ≤ ⌊(2D-1)/c⌋` for `c ≥ c*(n, k)` | needs `c*` defined | empirical scan not done yet |

The v2 falsification (Paper 1 §4) is **definitive**: at `c=1`, the bound is exponentially wrong.
The v3 reframing introduces a threshold `c*(n, k)` such that the bound holds for `c ≥ c*`.

## Reductions already done (PR #347 + comments)

The lemma needed for the bound has been **fully reduced to a clean polynomial-syzygy question**:

### Open-Set Rank Lemma (conjectured; empirically verified 50000+ configs)

Given supports `E_1, ..., E_m` of size `w`, distinct nonzero `γ_1, ..., γ_m`,
constraint matrix `A ∈ F_p^{m·c × 2D}` with row `i` = `[N_{E_i} | γ_i N_{E_i}]`.
Then either:

1. `rank A = min(m·c, 2D)`, OR
2. `∃ i: ⟨n_0(E_i), s_2⟩ = 0` for all `(s_1, s_2) ∈ ker A`.

### Stronger empirical observation

`dim image(ℓ) ≤ d := min(m·c, 2D) − rank A`, where `ℓ : ker A → F_p^m` sends
`(s_1, s_2) ↦ (⟨Λ_{E_i}, s_2⟩)_i`.

### Polynomial reformulation (twisted syzygy)

Define the **twisted syzygy module**
```
X_γ := { (ĥ_j) ∈ (F_p[x]_<c)^m :
         Σ ĥ_j Λ_{E_j} = 0  ∧  Σ γ_j ĥ_j Λ_{E_j} = 0 }
```

Need to show: for any non-zero `(ĥ_j) ∈ X_γ`, the polynomial
`Σ (γ_j − γ_i) ĥ_j Λ_{E_j}` (which is `0` by `X_γ` conditions composed)
realizes `Λ_{E_i}` for some `i`, given the `γ_j` are distinct.

This is a **standard polynomial-algebra question** — likely tractable via
γ-twisted Cramer / determinant identity. Phase 3.

## What today's c=2 work gives us (Paper 1 §6.5)

On `feat/c2-exponential-growth`:

- `max_bad ≈ 0.63 × 1.356^n` at `c=2` (rate 1/2), exponential in `n`
- Möbius theorem: `γ_C(L_x) = (AL_x+B)/(CL_x+D)` for all `w`
- Birthday bound conjecture: `max_bad ≤ O(√C(n,w))`

This **is the boundary** for v3. The transition `c*(n,k)` separates:
- `c < c*`: exponential in `n` (e.g., c=1 saturates `C(n,w)`, c=2 grows as `1.356^n`)
- `c ≥ c*`: bound `⌊(2D-1)/c⌋`, finite (constant 4 at rate 1/2)

## The central question for this branch

**What is `c*(n, k)`?**

Three candidate scalings, with very different paper implications:

| scaling | implication for paper |
|---------|----------------------|
| `c* = O(log n)` | Almost-everywhere polynomial; `c=2` (the exponential case) is essentially the only obstruction |
| `c* = O(√n)` | Mid-range — interesting phase diagram |
| `c* = Θ(n)` | Only the Johnson regime works; bound is "rate-asymptotic" |

The c=2 work shows `c=2` is exponential. We don't know yet if `c=3`, `c=4`, ... are still exponential or polynomial.

**Phase 1 task**: empirical sweep to determine `c*(n,k)`.

## Reference data points

### From #322 comments (rate 1/2, c = c_J)

| n | k | c_J | D | actual max_bad | ⌊(2D-1)/c⌋ |
|---|---|-----|---|----------------|------------|
| 28 | 14 | 6 | 14 | 4 | 4 |
| 32 | 16 | 7 | 16 | 4 | 4 |
| 36 | 18 | 8 | 18 | 4 | 4 |
| 40 | 20 | 9 | 20 | 4 | 4 |

Bound is **tight** in Johnson regime at rate 1/2.

### From Paper 1 §4 (c = 1, covering radius)

| n | k | c | max_bad |
|---|---|---|---------|
| 6 | 3 | 1 | C(6,2) = 15 |
| 8 | 4 | 1 | C(8,3) = 56 |

Saturation: `max_bad = C(n, w)` (exponential).

### From `feat/c2-exponential-growth` (c = 2)

| n | k | c | max_bad |
|---|---|---|---------|
| 8 | 4 | 2 | 7 |
| 16 | 8 | 2 | 79 |
| 24 | 12 | 2 | 986 |

Fit: `max_bad ≈ 0.63 × 1.356^n`. Exponential.

## Plan for this branch

1. **Phase 1** (empirical, this week): find `c*(n, k)` via sweep
2. **Phase 2** (small-scale proof): rate 1/2, `c = c_J`
3. **Phase 3** (general proof): `c ≥ c*`, all rates
4. **Paper 1 §6.6**: write up the theorem + phase diagram

See `STUDIO_TODO.md` for detailed task breakdown.

## Files this branch will produce

- `STUDIO_TODO.md` — top-level task tracking
- `notes/0091-berlekamp-c322-state.md` — this file
- `notes/0092-berlekamp-phase-diagram.md` — Phase 1 deliverable
- `notes/0093-rate-half-c-johnson.md` — Phase 2 deliverable
- `notes/0094-twisted-syzygy-proof.md` — Phase 3 deliverable
- `notes/scripts/op2_max_bad_phase_diagram.py` — Phase 1 main script
- `notes/scripts/op2_open_set_rank_extended.py` — Phase 2 verification
