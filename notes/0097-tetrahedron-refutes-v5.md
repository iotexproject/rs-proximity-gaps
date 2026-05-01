# Note 0097 — Tetrahedron pattern REFUTES Conjecture v5

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Status**: Major correction to notes 0093–0096

## TL;DR

Conjecture v5 (`max_bad ≤ ⌊(2D-1)/c⌋` for c ≥ 3 at large p) is **REFUTED at all primes**. The "(w+1)-clique" (tetrahedron) configuration realizes m = w+1 distinct bad γ for any prime supporting the n-th roots of unity. Random empirical search misses these witnesses because they live on a **measure-zero subvariety** of (s_1, s_2)-space (density ≈ p^{-2D + ker dim} ≈ p^{-8} at n=12 c=3).

Phase 1's "max_bad ≤ bound at large p" evidence was probabilistic, not worst-case.

## What we computed

### Over Q (rationals), with generic L_j = 1, 2, ..., n

For tetrahedron at n=12 c=3 (V = {1,4,5,8}, supports = all 3-subsets of V):
- rank A = 8 < 12 = min(mc, 2D)
- ker A has dim 4 over Q
- Explicit (s_1, s_2) ∈ ker A produces 4 distinct realized γ values
- Open conditions ⟨n_0(E_i), s_2⟩ ≠ 0 hold for all i
- → **Open-Set Rank Lemma is FALSE over Q.** Not a Schwartz-Zippel artifact.

See `notes/scripts/op2_tetrahedron_over_Q.py` and `op2_tet_verify_witness.py`.

### At RS evaluation domain L = ω^j, large primes

At p ∈ {61, 109, 229, 601, 1009, 10009, 100003}:
- rank A = 8 (deficient by 4) for all
- ker A has dim 4 mod p
- Each kernel point gives a (s_1, s_2) yielding **4 distinct bad γ**
- → **Bound `m ≤ ⌊(2D-1)/c⌋ = 3` violated at every tested prime.**

See `notes/scripts/op2_tet_witness_at_largep.py`.

### At Johnson radius (the #322 reference cases)

Tetrahedron realizes at every n ∈ {16, 20, 24, 28, 32, 36, 40} with c = c_J:

| n  | c_J | w  | m=w+1 | bound | best realized | violation |
|----|-----|----|-------|-------|---------------|-----------|
| 16 | 4   | 4  | 5     | 3     | 5             | ⚠️         |
| 20 | 5   | 5  | 6     | 3     | 6             | ⚠️         |
| 24 | 5   | 7  | 8     | 4     | 8             | ⚠️         |
| 28 | 6   | 8  | 9     | 4     | 9             | ⚠️         |
| 32 | 7   | 9  | 10    | 4     | 10            | ⚠️         |
| 36 | 8   | 10 | 11    | 4     | 11            | ⚠️         |
| 40 | 9   | 11 | 12    | 4     | 12            | ⚠️         |

The #322 comments report "empirical max_bad ≤ 4" via random search — random search **misses the tetrahedron**. See `op2_tet_at_johnson.py`.

### Density of tetrahedron witnesses

50,000 random (s_1, s_2) at n=12 c=3 p=1009 with tetrahedron supports:
- 100% achieved 0 realized γ
- 0 out of 50,000 achieved any tetrahedron pattern
- Predicted density: p^{-(2D - ker dim)} = p^{-8} ≈ 10^{-25}

This explains why all prior empirical "Phase 1" evidence appeared to support v5 — it sampled in a region where witnesses are exponentially rare.

See `op2_tet_density.py`.

## What this means

### Worst-case bound is FALSE

For any (n, k) with c ≥ 3 and rate close to 1/2:
```
   max_{s_1, s_2} M(s_1, s_2) ≥ w + 1 = D - c + 1
```

This grows **linearly in n** for fixed c. For c = c_J at rate 1/2:
- w_J ≈ 0.293n, so worst-case max_bad ≥ 0.293n + 1
- Old conjectured bound was 4 (constant). FALSE.

### Generic / high-probability bound likely still holds

The tetrahedron witnesses live on a Zariski-closed proper subvariety. For "generic" (s_1, s_2) (i.e., outside a measure-zero set), the bound `M ≤ ⌊(2D-1)/c⌋` likely holds.

**Reformulated conjecture (v6)**: There exists a Zariski-closed proper subvariety
`V_bad ⊂ F_p^{2D}` such that for `(s_1, s_2) ∉ V_bad`:
```
   M(s_1, s_2) ≤ ⌊(2D-1)/c⌋
```
The exceptional set `V_bad` has codimension ≥ some `c'(n, c) > 0`, so density `p^{-c'}`.

### Implications for FRI / RS soundness (prize context)

For FRI 2-round soundness, the relevant question is the **measure** of bad (s_1, s_2), not the worst case. The tetrahedron's negligible density (p^{-8} at our test) means:
- Random verifier challenge (s_1, s_2) avoids tetrahedron with overwhelming probability
- Soundness theorems based on "average" or "high-probability" bounds remain plausible
- **The worst-case Berlekamp Overconstrained conjecture v3/v5 is dead.**

But the SOUNDNESS theorem we'd want is now "(s_1, s_2) outside Zariski-closed subset" — a more delicate statement that the prover cannot exploit (since the verifier's challenge is random).

## Connection to c=2 exponential

At c=2, max_bad ≈ 0.63 × 1.355^n (exponential, holds for "many" (s_1, s_2)).
At c=3, the worst-case is also linear/superlinear (tetrahedron witnesses), but on a **thin** set.

The c=2 vs c=3 distinction is now:
- **c=2**: exponentially many bad (s_1, s_2) achieve high M
- **c=3+**: only measure-zero bad (s_1, s_2) achieve M > ⌊(2D-1)/c⌋, but they DO exist

## What needs to be revised

1. ~~Note 0093~~ — c*(n) = 3 universal: refute, replace
2. ~~Note 0094~~ — proof strategy at c=3: refute (lemma is false over Q), pivot
3. ~~Note 0095~~ — Paper §6.6 draft: rewrite with generic / measure-theoretic statement
4. ~~Note 0096~~ — final summary: redo

## Updated next steps

1. **Density quantification**: for general (n, k, c), compute codimension of `V_bad`
2. **Reformulate as algebraic geometry**: the "max_bad" problem becomes counting points on a determinantal variety
3. **Paper section**: rewrite §6.6 as "generic worst-case" with explicit failure pattern (tetrahedron)
4. **FRI soundness implication**: re-examine whether the "measure-zero failure" matters for soundness

## Files (this update)

- `notes/scripts/op2_tetrahedron_over_Q.py` — over Q rank/kernel test
- `notes/scripts/op2_tet_verify_witness.py` — explicit witness construction
- `notes/scripts/op2_tet_witness_at_largep.py` — verification at p ≤ 100003
- `notes/scripts/op2_clique_scan.py` — (w+1)-clique violation scan
- `notes/scripts/op2_tet_at_johnson.py` — c_J reference cases (n=16..40)
- `notes/scripts/op2_tet_density.py` — measure-zero density confirmation
- `notes/0097-tetrahedron-refutes-v5.md` — this file
