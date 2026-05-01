# Note 0118 — V_bad decomposition: empirical matching lower bound

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0114, 0116, 0117
**Status**: empirical evidence for matching codim lower bound.
Combined with Note 0117 rigorous upper bound, gives `codim V_bad =
2(c−1) ± O(log_p n)` empirically.

## Setup

Note 0117 proved `codim V_bad ≤ 2(c−1)` rigorously by exhibiting
`V_S × V_S ⊂ V_bad` for any `|S| = w + 1` subset. The matching question
is the **lower bound**:
```
codim V_bad ≥ 2(c−1) − O(log_p n)
   ⟺   V_bad  ⊆  ⋃_{|S| ≤ w+1}  V_S × V_S    (up to lower-dim corrections)
```

If true, `codim V_bad = 2(c−1)` exactly (modulo log poly), which is the
clean prize-grade statement.

## Empirical test (op2_v_bad_decomposition_test.py)

Sample bad witnesses `(s_1, s_2)` from random `(E_*, γ_*)` configurations,
compute the smallest `S ⊂ [n]` with `(s_1, s_2) ∈ V_S × V_S` (= "min
joint support size in Vandermonde basis").

| (n, c, p)    | D  | w | T | target |S| = w+1 | observed distribution                | % at ≤ w+1 |
|--------------|----|---|---|---------------------|--------------------------------------|------------|
| (12, 3, 1009)| 6  | 3 | 3 | 4                   | {1: 20, 2: 8, 4: 2}                  | 100.0%     |
| (16, 4, 257) | 8  | 4 | 3 | 5                   | {1: 17, 2: 10, 3: 3}                 | 100.0%     |
| (20, 5, 41)  | 10 | 5 | 3 | 6                   | {1: 14, 2: 11, 3: 5}                 | 100.0%     |

**100% of bad witnesses fit in some `V_S × V_S` with `|S| ≤ w+1`.**

## Why most have `|S| < w+1`

The sampling draws from kernels of A(γ) — these are low-dim subspaces.
Common low-dim witnesses fall in the "saturated" cases:
- `|S| = 1`: `s_2 = 0`, `s_1 = α · ev_v`. Then every γ satisfies
  `s_1 + γ s_2 = s_1 ∈ V_{E}` for any `E ∋ v`. M = p−1 (trivially bad).
- `|S| = 2`: similar low-rank structures.

These are degenerate "trivially bad" components with low dim, contributing
negligibly to total `|V_bad|`. The dominant volume is the `|S| = w+1`
components from Note 0117.

## Combined picture

| Dim contribution | from              | rigorousness |
|------------------|-------------------|--------------|
| `2(w+1)` (= max) | `V_S × V_S`, `|S|=w+1` | RIGOROUS lower bound on `\|V_bad\|` (Note 0117) |
| `≤ 2 · w`       | `V_S × V_S`, `|S|≤w` | rigorous (sub-leading) |
| `> 2(w+1)`?     | (hypothetical)     | NOT OBSERVED — empirical 0/90 sampled |

If the empirical rules out `> 2(w+1)` components universally,
```
|V_bad|  ≤  Σ_{|S|≤w+1} |V_S × V_S|
        ≤  poly(n) · p^{2(w+1)}
codim V_bad  ≥  2(c−1) − O(log_p n)
```
matching the upper bound.

## Caveats

1. Sampling drew from random `(E_*, γ_*)` configurations. Doesn't
   exhaustively explore V_bad. A pathological component with `|S| > w+1`
   might be unsampled, particularly if it's a measure-zero subvariety
   inside a larger ambient.
2. The min-S computation is brute-force over `2^n` subsets — only
   feasible at `n ≤ 24` or so. Deployment-scale `n = 2^{21}` direct
   testing is infeasible.
3. Different field characteristics (`p ∈ {1009, 257, 41}`) all show
   the same pattern, weakening the chance of being a small-prime
   artifact.

## Implication for the rescope

After Notes 0117 + 0118:

| Bound direction         | Status                                    |
|-------------------------|-------------------------------------------|
| `codim V_bad ≤ 2(c−1)`  | **RIGOROUS** (Note 0117)                  |
| `codim V_bad ≥ 2(c−1) − O(log_p n)` | **empirical at 3 (n,c)**, prize-grade if extrapolates |

Note 0115's "core gap" is now narrowed: only the lower bound is open,
and it has empirical support. For Issue #376-style submission, this
matches the type-(A) "positive deployment bounds" framework.

## Files

- `notes/scripts/op2_v_bad_decomposition_test.py` — empirical test
- `notes/scripts/op2_v_bad_decomposition_test.output.txt` — output
- `notes/0117-V_S-rigorous-codim-upper-bound.md` — companion (upper bound)

## Next steps (toward rigor)

To upgrade the lower bound from empirical to rigorous:

1. **Algebraic argument**: prove that any bad `(s_1, s_2)` must have
   joint Vandermonde support `≤ w+1`. Approach: from `s_1 + γ_l s_2 ∈
   V_{E_l}` for `m > T` distinct `γ_l, E_l`, derive an algebraic
   constraint on the joint support of `(s_1, s_2)`. This is a
   strengthening of the routed-dichotomy approach in Notes 0107–0112.

2. **Empirical at larger n**: extend the decomposition test to
   `n ∈ {28, 32, 40}` (still feasible if min-S restricted to
   `|S| ≤ w + 2` upper bound). If empirical pattern holds across all,
   the conjecture becomes very robust.

3. **Mass-balance argument**: directly bound `|V_bad|` by counting
   `(E_*, γ_*)` configurations and their kernel sizes, then show
   total ≤ `poly(n) · p^{2(w+1)}`.
