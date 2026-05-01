# Note 0092 — Open-Set Rank Lemma fails at c=2 (concrete witness)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Status**: Computational discovery — fundamental structural insight for #322

## Statement of the lemma (#322 comment 4)

**Open-Set Rank Lemma (conjectured)**. Let `E_1, ..., E_m ⊂ [n]` be supports of size `w`,
let `γ_1, ..., γ_m ∈ F_p^*` be distinct, and let `A ∈ F_p^{m·c × 2D}` be the constraint
matrix with block rows `[N_{E_i} | γ_i N_{E_i}]`. Then either:

1. `rank A = min(m·c, 2D)`, OR
2. For every `(s_1, s_2) ∈ ker A`, there exists `i` with `⟨n_0(E_i), s_2⟩ = 0`.

**Empirical claim** (from #322): verified across 50000+ configs at `n ∈ {28, 32, 36, 40}`,
`m ∈ {5, 6}`, `c = c_J ≈ 0.207n`. Zero counterexamples.

## What we proved here: lemma FAILS at c=2

**Concrete counterexample** at `n=8, k=4, c=2, p=113`:

```
s_1 = [94, 77, 100, 104]
s_2 = [66, 86, 13, 43]
E_1 = (3, 6),  γ_1 = 22
E_2 = (5, 6),  γ_2 = 31
E_3 = (0, 1),  γ_3 = 60
E_4 = (3, 5),  γ_4 = 104
```

m = 4 distinct γ values, all 4 supports valid bad-γ realizations.

### Matrix A (8×8 over F_113)

```
[18, 29,  1,  0, 57, 73, 22,  0]
[ 0, 18, 29,  1,  0, 57, 73, 22]
[69,  3,  1,  0, 105, 93, 31,  0]
[ 0, 69,  3,  1,  0, 105, 93, 31]
[18, 94,  1,  0, 63, 103, 60,  0]
[ 0, 18, 94,  1,  0, 63, 103, 60]
[ 1, 62,  1,  0, 104,  7, 104,  0]
[ 0,  1, 62,  1,  0, 104,  7, 104]
```

**rank A = 7 < min(mc, 2D) = 8**. Branch (1) of lemma fails.

### Branch (2) check

`ker A` = 1-dim, spanned by `v = (60, 78, 47, 76, 83, 2, 66, 1)`.

For each support, `⟨n_0(E_i), s_2(v)⟩` evaluated on `s_2 = (83, 2, 66, 1)`:

| i | E_i | n_0(E_i) | ⟨n_0, s_2⟩ |
|---|-----|----------|------------|
| 1 | (3,6) | (18, 29, 1, 0) | 36 |
| 2 | (5,6) | (69, 3, 1, 0)  | 36 |
| 3 | (0,1) | (18, 94, 1, 0) | 53 |
| 4 | (3,5) | (1, 62, 1, 0)  | 47 |

**All nonzero** → branch (2) fails.

Both branches fail → **lemma DISPROVED at c=2**.

## Structural mechanism: triangle of overlapping supports

The row dependency of A (left null space) is:

```
w = (33, 96 | 26, 16 | 0, 0 | 98, 1)
```

Decomposing by support:

| i | E_i | row coeffs | participates? |
|---|-----|-----------|---------------|
| 1 | (3, 6) | (33, 96)  | YES |
| 2 | (5, 6) | (26, 16)  | YES |
| 3 | (0, 1) | (0, 0)    | **NO** |
| 4 | (3, 5) | (98, 1)   | YES |

The row dependency uses ONLY `E_1, E_2, E_4` — these form a **triangle** on
vertices `{3, 5, 6}`:

- `E_1 ∩ E_2 = {6}`
- `E_1 ∩ E_4 = {3}`
- `E_2 ∩ E_4 = {5}`

All three pairs share exactly one element, forming `K_3` on `{3, 5, 6}`.
This is the "triangle hypergraph".

The fourth support `E_3 = (0, 1)` is **disjoint** from the triangle and does
not participate in the row dependency.

## Why this matters

### For Phase 1 (find c*)
The lemma's failure at c=2 means the v3 bound `max_bad ≤ ⌊(2D-1)/c⌋` does NOT hold
at c=2. We have a concrete witness with `max_bad = 4 > 3 = ⌊7/2⌋`.

This matches Paper 1 §6.5 (c=2 work): max_bad grows exponentially (~1.356^n), so
the linear bound fails.

### For Phase 2 (proof at c=c_J)
The triangle obstruction is specific to **small c, large w**. For w = 2, three size-2
supports forming a triangle on 3 vertices fit easily.

For larger c (smaller w): triangles still possible but require more vertices. For
w supports of size w with all pairwise overlap exactly 1, need (3w-3) vertices.

For w small (c large): triangles use few vertices, available in any n.
For w large (c small): triangles use many vertices, may exceed n for small n.

But the DEEPER question: at what c does the row dependency mechanism break?

### Conjecture: lemma holds for c ≥ c*(n)

Empirically:
- `c*(8, 4) = 3` (sweep showed c=2 fails, c=3 passes tight)
- `c*(n, k=n/2)` = ? for larger n

Phase 1 sweep aims to determine the scaling of `c*(n, k=n/2)`.

## Implication for proof

Any proof of the v3 bound MUST exclude the "triangle" mechanism. Possible approaches:

1. **Pigeonhole on triangle edges**: at c ≥ c_*, no triangle of size-w supports can
   form a row dependency.
2. **Algebraic geometry**: the row dependency requires specific algebraic relations
   among ELP coefficients. Show these relations have measure zero for c ≥ c_*.
3. **Berlekamp-Welch-style**: at c=c_J, the "decoding radius" is at Johnson, and
   Johnson list size is O(1).

## Files

- `notes/scripts/op2_verify_lemma_at_c2.py` — finds the witness
- `notes/scripts/op2_witness_analysis.py` — detailed structural analysis
- `notes/scripts/op2_cstar_largep.py` — large-p Phase 1 sweep (running)

## Next steps

1. Wait for Phase 1 sweep results (c* for n ∈ {8, 12, 16, 20, 24})
2. Check whether triangle mechanism explains all failures (or other structures appear)
3. For Phase 2: prove lemma at c = c_J at rate 1/2, exclude triangle
