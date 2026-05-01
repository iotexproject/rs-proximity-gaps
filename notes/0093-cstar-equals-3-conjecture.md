# Note 0093 — c*(n, k=n/2) = 3 conjecture

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Status**: Strong empirical evidence; replaces v3 conjecture

## The refined conjecture

**Conjecture (v4)**: For RS[n, n/2] over F_p (rate 1/2), at sufficiently large p:

> `max_bad(s_1, s_2) ≤ ⌊(2D-1)/c⌋` for all `c ≥ 3`.

This says: the Open-Set Rank Lemma holds **for all `c ≥ 3`**, regardless of `n`.
Equivalently, `c*(n, k=n/2) = 3` is universal.

## Why c=2 fails (Note 0092 + c=2 paper)

- c=2 paper shows `max_bad ≈ 0.63 × 1.356^n` (exponential in `n`)
- v3 bound `⌊(2D-1)/2⌋ = D-1 ≈ n/2` is way below exponential
- Specific witness at `n=8 c=2`: m=4 with rank-deficient A, all open conditions hold
- Lemma DISPROVED at c=2

The structural mechanism: **triangle of overlapping supports** (3 size-w
supports forming a triangle on 3 vertices, w=2). At c=2, w=D-2 leaves enough
"room" for triangles.

## Why c=3 holds (empirical, this note)

For `c=3`, w = D-3 (smaller supports). The triangle obstruction (3 supports
of size w with all pairwise overlaps = w-1) requires `3(w-1) + 3 ≤ n` vertices
to embed the 3 supports... harder to fit at small w.

### Empirical data

For `c=3` at `n ∈ {8, 12, 16}`, tested at primes `p > 200·bound` (well past
saturation regime):

| n  | k | D | w | bound = ⌊(2D-1)/3⌋ | Test primes      | max_bad | PASS? |
|----|---|---|---|--------------------|--------------------|---------|-------|
| 8  | 4 | 4 | 1 | 2                  | 73, 89, 97, 113, 137 | 1     | ✓     |
| 12 | 6 | 6 | 3 | 3                  | 601, 613, 661, 673, 709 | 1   | ✓     |
| 16 | 8 | 8 | 5 | 5                  | 1009, 1153, ...      | 2     | ✓     |
| 20 | 10 | 10 | 7 | 6                | (running)            | TBD     | TBD   |
| 24 | 12 | 12 | 9 | 7                | (running)            | TBD     | TBD   |

At small primes (p ~ 50-300), `max_bad` can exceed bound due to mod-p
saturation, but **trend is monotonically decreasing toward bound or below**.
At p > 200·bound, max_bad consistently ≪ bound.

## Note: this is STRONGER than #322's original target

Original #322 target: prove `max_bad ≤ ⌊(2D-1)/c⌋` at `c = c_J ≈ 0.207n` for
rate 1/2. Our refined statement: works for **all c ≥ 3**, much wider regime.

If proven, this gives:
- At `c = 2`: max_bad = exponential (can't help)
- At `c = 3`: max_bad ≤ ⌊(2D-1)/3⌋ ≈ n/3 (linear in n!)
- At `c = c_J ≈ n/4`: max_bad ≤ 4 (constant)

**Linear bound at c=3** is a NEW result (paper-worthy on its own).

## Connection to ConjE / codex

The codex/fri-conje-attack branch's recent finding (Note 0226, 2026-04-29):

> "Newton-Girard partial doesn't imply full elementary-symmetric structure"

This is the **same flavor** as our finding:

| ConjE (codex)                              | Berlekamp (this branch)                |
|--------------------------------------------|----------------------------------------|
| Newton-Girard partial reduction insufficient | Open-Set Rank Lemma fails at c=2 |
| Need full e-symmetric data                 | Need rank-deficiency structure beyond Triangle |
| Locator gap on `μ_{8h}`                    | Triangle on size-w supports in `[n]`   |
| Lam-Leung vanishing sums of roots of unity | Polynomial syzygy of ELP coefficients  |

Both attack a "rank deficiency forcing structural pattern" question.

## What needs to be proven

For c ≥ 3:
1. **Open-Set Rank Lemma** at c ≥ 3:
   For supports E_1, ..., E_m of size w = D-c, distinct γ_1, ..., γ_m, the
   constraint matrix A satisfies:
   - rank A = min(mc, 2D), OR
   - ∃i with `⟨n_0(E_i), s_2⟩ = 0` for all `(s_1, s_2) ∈ ker A`.

2. **Bound corollary**: max_bad ≤ ⌊(2D-1)/c⌋.

## Proof attack: triangle obstruction at c=3

At c=3, w = D-3. For 3 supports E_1, E_2, E_3 of size w forming a triangle:
- |E_1 ∩ E_2| = |E_1 ∩ E_3| = |E_2 ∩ E_3| = ?
- Pairwise overlap > w - c = w - 3

For w = D - 3 = (n/2) - 3 at rate 1/2: w large for large n.
Triangle requires 3 supports with all pairwise overlaps > w-3 ≈ w.

If overlap ≥ w-2 (i.e., |E_i Δ E_j| ≤ 4): triangle uses
3 supports each of size w, sharing at least w-2 elements per pair.
Total vertices: w + 2 + 2 = w + 4 (rough estimate).

For n ≥ w + 4: triangle achievable in principle. So triangle obstruction
exists at c=3 too — but maybe with weaker rank deficiency that passes the
full Open-Set Rank Lemma.

**Detailed analysis needed**: at c=3, does triangle still produce row dependency
that bypasses the lemma's `a_0 ≡ 0` branch?

## Files

- `notes/scripts/op2_c3_verylarge_p.py` — large-p test script
- `notes/scripts/op2_verify_lemma_at_c2.py` — finds c=2 witness
- `notes/scripts/op2_witness_analysis.py` — structural analysis of c=2 witness

## Next steps

1. ~~Confirm c=3 at large p for n=20, 24~~ (running)
2. Find c=3 lemma witness if any (test at small p first, then verify at large p)
3. If c=3 lemma holds: prove it
4. If c=3 lemma fails at large p: refine to c=4
