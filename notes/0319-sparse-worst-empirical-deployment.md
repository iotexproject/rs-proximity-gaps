# Note 0319 — Empirical sparse-worst at deployment: Hamming-K vs Algebraic-K

**Branch:** `feat/op1a-algorithm-fixes` (paper3) — cross-branch contribution to paper2.
**Date:** 2026-05-01
**Status:** Working. Documents empirical findings from #421 GS list-decoder + K-sweep iterations.

## Headline

Empirical Hamming-K computation via Sudan GS list-decoder (m=1, m=2) at deployment-scale shows: **at random sampling, K_q = 0 across both sparse and dense configurations at (32, 8) p=257**. This isn't a refutation of `conj:sparse-worst` — it indicates the algebraic-K (paper2's Singular eliminator deg, q-independent) is the right object, and Hamming-K at finite q is an information-poor empirical proxy when eliminator roots typically lie in extension fields.

## What was built (#421)

| Commit | Component |
|--------|-----------|
| 328850c | Berlekamp-Welch unique decoder (RS over multiplicative subgroup) |
| 37a59b1 | K(f_1, f_2) Hamming-K via direct enumeration |
| 3e0b07c | Systematic s-sweep at base (8, 2) |
| a78c837 | Focused max-K sweep — **K_2 = 8 = paper2 universal exact at p=17** |
| 44dc018 | NumPy-vectorized enumeration at (16, 4) |
| c7aa5fa | Sudan GS m=1 + Roth-Ruckenstein (recovers from 7 errors at (16,4)) |
| bbb0798 | GS-based K-sweep at (8,2) (16,4) p=17 |
| b83bfa2 | **Sudan GS m=2 with Hasse derivatives — reaches Johnson at (16,4)** |
| 479b490 | K-sweep via Sudan(m=2) at (16,4) p=17/97 |
| 671104a | Crafted witness test (32,8) — K=0 simple configs |
| f5f9ad2 | NumPy GS, deployment K-sweep null at random |

## Empirical findings

### At base (8, 2) — small q sanity

| p   | δ ≤ 3 | δ ≤ 4 (Johnson) | δ ≤ 5 (Berlekamp) |
|-----|-------|------------------|---------------------|
| 17  | 0     | K_2=8, K_3=6, K_4=6, dense=6 | full saturation |
| 97  | 0     | K_2=7, K_3=5, K_4=2, dense=2 | ~45 (saturation) |

**K_2 = 8 at p=17 exactly matches paper2's universal K_2 ≤ 8 bound.** This validates Hamming-K as a meaningful empirical at small q.

At p=97, sparse 2-mono > dense by 3.5× at Johnson — consistent with sparse-worst direction.

### At intermediate (16, 4)

Sudan(m=1) τ=7 (below Johnson J=8):
- p=17 sparse 0-2, dense 0; pattern weak but sparse > dense
- p=97 ALL K=0

Sudan(m=2) τ=8 (= Johnson exact):
- p=17 sparse 4-6, dense 4
- p=97 K_2=2, K_5=1, K_6=1, K_3=K_4=K_dense=0; n_random=30

Pattern: at p=97 random Hamming-K gives mostly 0; only specific s-class configs reach K=1-2.

### At deployment (32, 8) — Sudan(m=2) τ=15 (J-1)

| Test | Result | Note |
|------|--------|------|
| Random n_random=2 | All K=0 | Per-trial 9s pure-Python |
| Random n_random=15 | All K=0 | Per-trial 5s numpy; 326s total |
| Crafted: adjacent 2-mono | K=0 | |
| Crafted: disjoint 3-mono | K=0 | |
| Crafted: same-supp 3-mono | K=0 | |

**Random and simple-crafted configurations all give K_q = 0 at deployment Hamming-K.** This is structurally consistent with: paper2's K_3 ≤ 10 bound is **algebraic** (over Q-bar); for specific F_257, the eliminator's 10 roots typically lie in extension fields F_{257^d} with d > 1, giving K_q < K_alg, often K_q = 0.

## Implication for `conj:sparse-worst` empirical at deployment

The Hamming-K random-sampling empirical at deployment is **information-poor**. For meaningful test:

1. **Algebraic-K via Singular eliminator**: q-independent, matches paper2 framework. Note 0313 already does this at base (8, 2): K_3=10, K_4=12, K_5≥15. Studio cluster running for above-J 5-mono cases.

2. **Crafted constructions with Galois-rational roots**: configurations where eliminator splits over F_q. Hard to construct without the eliminator structure.

3. **Larger primes**: at q≫deployment field, more eliminator roots fall in F_q. But deployment is q ∼ 2^31, a fixed scale.

For prize-grade empirical, **path 1 (algebraic via Singular)** is the principled approach. #421 GS implementation is correct for finite-field Hamming-K but not for paper2's algebraic-K.

## What's working from #421

- Sudan GS list-decoder (m=1, m=2) — reaches Johnson at (16,4), τ=15 at (32,8). This is a **standalone deliverable** independent of sparse-worst. Useful for any future plain-RS list-decoding empirical or for OP-1a algorithmic exploration (which paper3 §sec:berlekamp-howto reduces forward to).

- K_2 = 8 empirical at p=17 base matching paper2's universal — validates the framework of "max K over s-mono sparse" at small q.

- Sudan(m=2) at Johnson exact at (16,4) — shows that Hamming-K at intermediate scale and Johnson radius can differentiate sparse from dense even with random sampling (K_2=2 vs K_dense=0 at p=97).

## What's needed for definitive deployment empirical

1. **Algebraic-K via sympy resultant or Singular**:
   - For (16, 4) c=2: should reproduce paper2 K_3 ≤ 10, K_4 ≤ 12 numbers
   - For (32, 8) c=2: should give max K for s-mono families, comparable to dense

2. **Studio above-J 5-mono cases** (from Note 0314 handoff): if K_5 above-J > 10, conjecture **REFUTED**; if ≤ 10, supportive.

3. **Sudan(m=3) for Johnson exact at (32,8)**: 6n=192 constraints, d=48, τ=16=J. Implementation extension of Hasse-derivative interpolation to 6 constraints/point: H^{i,j} for (i,j) ∈ {(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)}.

## Files

- `notes/scripts/contrib_paper2/gs_sudan.py` — Sudan(m=1) implementation
- `notes/scripts/contrib_paper2/gs_sudan_m2.py` — Sudan(m=2) with Hasse derivatives
- `notes/scripts/contrib_paper2/gs_sudan_m2_np.py` — numpy speedup
- `notes/scripts/contrib_paper2/sparse_worst_K_sweep.py` — direct enumeration K-sweep
- `notes/scripts/contrib_paper2/sparse_worst_K_sweep_np.py` — numpy enumeration
- `notes/scripts/contrib_paper2/sparse_worst_K_gs.py` — GS-based K-sweep (m=1)
- `notes/scripts/contrib_paper2/sparse_worst_K_gs_m2.py` — GS K-sweep (m=2)
- `notes/scripts/contrib_paper2/sparse_worst_K_gs_m2_np.py` — numpy GS K-sweep (m=2)
- `notes/scripts/contrib_paper2/crafted_witness_test.py` — crafted witness null result

## Cross-refs

- Note 0313 — paper2 Studio s-mono cluster (algebraic K via Singular GB)
- Note 0314 — paper2 Conj 4.1 attack handoff (Q1 + sparse-worst as P0 gates)
- Note 0318 — Note 0315 a_1=A_1(0) issue
- paper2 thm:universal-K10 (K_2 ≤ 8, K_3 ≤ 10, K_4 ≤ 12 — algebraic bounds)
- paper2 conj:sparse-worst (Issue #419)
