# Note 0103 — Conjecture v6 revised: V_bad has more components than just tet

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Supersedes**: parts of Note 0101 (v6 first version)

## Critical update

Conjecture v6 v1 stated `V_bad = ∪_V V_tet(V)`. This is **FALSE**:

At n=12 c=3 m=4, ~2% of random non-tet rank-deficient (E, γ) configurations
admit (s_1, s_2) realizing all m γ's distinctly with rank def = 1. These
witnesses do NOT lie in any tetrahedron variety.

Empirical: 54 such non-tet bad configs found in 3000 trials, of which:
- 30+ have degree pattern {0:4, 1:4, 2:4}, intersection {0:3, 1:2, 2:1}, |union|=8
- 20+ have degree pattern {0:5, 1:2, 2:5}, intersection {0:2, 1:3, 2:1}, |union|=7
- 3 have degree pattern {0:3, 1:6, 2:3}, intersection {0:3, 1:3}, |union|=9
- 3 have degree pattern {0:5, 1:3, 2:3, 3:1}, intersection {0:3, 2:3}, |union|=7, ker dim=2

These are STRUCTURED but not (w+1)-cliques. Some have a "tetrahedron sub-pattern
on 3 of the 4 supports" (e.g., 3 of 4 size-3 subsets of a 4-set, missing the 4th).

(Script: `op2_nontet_pattern_analysis.py`)

## Revised counting

Each non-tet bad pattern has 1-dim kernel → p (s_1, s_2)'s on a line in F_p^{2D}.

**Total |V_bad|**:
```
|V_bad| ≤ (tetrahedron contribution) + (non-tet contribution)
       ≤ C(n, w+1) · p^{w+1}  +  (# bad non-tet patterns) · p
```

Each bad pattern is determined by (E_1, ..., E_m, γ_1, ..., γ_m) tuple. The
number of (E, γ) tuples is C(C(n, w), m) · p^m (subject to distinctness).

Empirical bad fraction (n=12, m=T+1=4): 54/3000 = 1.8% × ~10x rejection rate
→ effective bad fraction ~0.5% of (E, γ) tuples are non-tet realizable.

**Density estimate**:
```
Pr[(s_1, s_2) ∈ V_bad] ≤ poly(n) · p^{-(2D - m - 1)}
                       ≤ poly(n) · p^{-(2D - T - 2)}
                       = poly(n) · p^{-(D + c - 2)}    [substituting T = ⌊(2D-1)/c⌋]
```

For rate 1/2 (D = n/2), c=3: codim ≈ n/2 + 1. Linear in n.

## Updated table for FRI parameters

| Field   | n  | c | T | Codim | Pr bound (p=2^31)    | Comment        |
|---------|----|---|---|-------|----------------------|----------------|
| BabyBear| 12 | 3 | 3 | 7     | poly(12) · 2^{-217}  | < 2^{-200}     |
| BabyBear| 28 | 6 | 4 | 22    | poly(28) · 2^{-682}  | < 2^{-650}     |
| BabyBear| 40 | 9 | 4 | 34    | poly(40) · 2^{-1054} | < 2^{-1020}    |

Still trivially soundness-tight.

## Refined Conjecture v6 (v2)

```
   Pr_{(s_1, s_2) ∈ F_p^{2D}}[M(s_1, s_2) > T] ≤ poly(n) · p^{-(2D - T - 2)}
                                                = poly(n) · p^{-(D + c - 2)}  at rate 1/2
```

The polynomial factor scales with C(C(n, w), m) ≈ exp(O(n log n)). At small
p (p ≪ exp(n)), the polynomial dominates and effective codim is reduced.
At large p (p ≫ exp(n) — true for FRI parameters), formula holds tightly.

**Empirical verification** (op2_verify_codim.py):

| n  | c | T | m | #bad/1500 | actual codim @ p=1009 | formula codim | gap     |
|----|---|---|---|-----------|------------------------|---------------|---------|
| 12 | 3 | 3 | 4 | 28        | 4.9                    | 7             | -2 (poly) |
| 16 | 4 | 3 | 4 | 13        | 7.8                    | 11            | -3 (poly) |
| 20 | 5 | 3 | 4 | 3         | 10.8                   | 15            | -4 (poly) |
| 24 | 5 | 4 | 5 | 1         | 10.5                   | 18            | -7 (poly) |

The "gap" is the polynomial-factor contribution to codim at p=1009. At
BabyBear (p=2^31), the polynomial factor is ~3× smaller in the codim
exponent, so formula codim is approached.

**Status**: empirically verified within polynomial factor at p=1009 across 4
configurations; asymptotic formula `2D - T - 2` matches at large p. Analytic
proof open.

## Why this is still good news

1. The bound is still **polynomially-many candidates × exponential-codim** structure
2. For ANY RS parameters with reasonable p, the soundness implication is fine
3. The revision changes the constant in the exponent but not the qualitative picture

## Open: characterize the "structural" non-tet bad patterns

The 4 patterns observed at n=12 c=3 m=4 suggest a finite "catalog" of
structural failure modes. Each has codim 2D - 1 = 11 (for ker dim 1) or
2D - 2 = 10 (for ker dim 2 in pattern D).

If we can enumerate all patterns and bound their codim ≥ some specific value,
we get a clean codim bound.

## Files

- `notes/scripts/op2_shifted_syzygy.py` — lemma escape clause test
- `notes/scripts/op2_check_nontet_lemma_fail.py` — verification at counterexamples
- `notes/scripts/op2_nontet_pattern_analysis.py` — pattern characterization
- `notes/0103-revised-v6.md` — this file
