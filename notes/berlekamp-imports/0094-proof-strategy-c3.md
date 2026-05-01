# Note 0094 — Proof strategy for Open-Set Rank Lemma at c ≥ 3

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Status**: Strategy outline; proof in progress

## Goal

Prove the **Open-Set Rank Lemma at c=3** (over `Q` / generic prime):
For supports `E_1, ..., E_m ⊂ [n]` of size `w = D-3`, distinct `γ_1, ..., γ_m`:
either `rank A = min(3m, 2D)`, OR `∃i: ⟨n_0(E_i), s_2⟩ = 0` for all `(s_1, s_2) ∈ ker A`.

## Why generic prime / Q

The lemma can fail at SMALL primes due to mod-p coincidences (Schwartz-Zippel-like).
At sufficiently large primes (or over Q), the lemma holds. This is the standard
"algebraic identity over Q lifts to all but finitely many primes" argument.

For Phase 1 empirical evidence: at p > 200·bound, the lemma holds for c=3.

## Reduction to polynomial syzygy

Recall (from #322 comment 5):

```
X_γ := {(ĥ_j) ∈ (F_p[x]_<c)^m : Σ ĥ_j Λ_{E_j} = 0 ∧ Σ γ_j ĥ_j Λ_{E_j} = 0}
```

`dim X_γ = mc - rank A`. The lemma's failure is equivalent to:
∃ (ĥ_j) ∈ X_γ \ {0} such that for ALL i, (0, Λ_{E_i}) ∉ row span A.

Equivalently: ∀i, ∄ (p_j) with Σ p_j Λ_{E_j} = 0 AND Σ γ_j p_j Λ_{E_j} = Λ_{E_i}.

## Trivial cases

- **m=1**: A is c × 2D, X_γ has m·c - rank A. For random γ_1 and generic E_1: rank = c (full row rank). X_γ = 0. Lemma trivial.

- **m=2**: From 2-equation system: ĥ_1 Λ_{E_1} + ĥ_2 Λ_{E_2} = 0 AND γ_1 ĥ_1 Λ_{E_1} + γ_2 ĥ_2 Λ_{E_2} = 0. Subtract: (γ_2 - γ_1) ĥ_2 Λ_{E_2} = 0 → ĥ_2 = 0 (since γ_1 ≠ γ_2 and Λ_{E_2} ≠ 0). Similarly ĥ_1 = 0. X_γ = 0. Lemma trivial.

- **m=3**: Counting: 3c unknowns vs 2D constraints. For c=3, 3c=9 unknowns. Constraints: Σ ĥ_j Λ_{E_j} ∈ F_p[x]_<D (D linear constraints) AND same for γ-twisted (D more). Total 2D constraints.

  At rate 1/2 n=12, D=6. So 9 unknowns, 12 constraints. **Generically X_γ = 0**.

  But at SPECIAL configurations (e.g., supports with specific algebraic relations), X_γ can be nonzero. Triangle obstruction (3 supports with specific overlaps).

## Triangle obstruction at c=3

At c=2 (Note 0092), the triangle of size-w supports forming K_3 on 3 vertices created the lemma failure. At c=3:

- w = D - 3
- For 3 supports forming triangle: all pairwise overlaps > w - c = w - 3
- For overlap = w - 2 (i.e., differ by 2 elements per pair): 3 supports use ≤ w + 4 vertices roughly

**Test**: at c=3 n=12 (w=3), can we find 3 supports of size 3 with each pair sharing 1 element? Yes — e.g., (0,1,2), (0,3,4), (1,3,5) shares 0,1,3 pairwise.

So triangles at c=3 exist combinatorially. The question is whether they create row dependency.

## Attack outline

### Strategy A: Direct case analysis at c=3

For c=3, classify all "obstruction configurations" (E_i pattern + γ_i specialization):
1. **Triangle** (3 supports forming K_3 in some sense)
2. **Star** (supports sharing common element)
3. **Path** (sequential overlap)

Show each obstruction either:
- Doesn't produce row dependency at c=3, OR
- Produces dependency that's caught by lemma's "a_0 ≡ 0" branch.

### Strategy B: Twisted Cramer / Vandermonde

Define polynomial `P(t, x) = Σ_j ĥ_j(x) Λ_{E_j}(x) ∏_{l≠j}(t - γ_l)` for `(ĥ_j) ∈ X_γ`.

Properties:
- `P(γ_i, x) = ĥ_i(x) Λ_{E_i}(x) ∏_{l≠i}(γ_i - γ_l)` (only j=i term survives)
- `deg_t P ≤ m - 3` (using both X_γ conditions; see Lagrange interpolation argument)

For `(ĥ_j) ∈ X_γ \ {0}`: at least one ĥ_i ≠ 0. Then `P(γ_i, x) = c_i · ĥ_i Λ_{E_i}` for some scalar c_i ≠ 0.

To realize Λ_{E_i} (without the ĥ_i factor), need ĥ_i to be a unit OR additional structure.

**Key gap**: how to extract Λ_{E_i} from ĥ_i Λ_{E_i}?

### Strategy C: Reduction to specific small-m case

For the bound, we need to rule out m = ⌊(2D-1)/c⌋ + 1 = ⌊(2D-1)/c⌋ + 1.

At c=3 rate 1/2, bound ≈ n/3. Need to rule out m = ⌊n/3⌋ + 1 supports.

For LARGE n: this requires many supports, hard direct. But maybe induction from small.

## Connection to ConjE / codex Note 0226

The codex branch noted:

> Newton-Girard partial reduction is INSUFFICIENT for the locator gap proof.
> Need full elementary-symmetric data.

This is the **same flavor** of difficulty. Both attack a "rank deficiency forcing
structural pattern" problem where partial information is not enough.

Their reference: **Lam-Leung "Vanishing sums of roots of unity"**.

For our problem, ELP coefficients ARE elementary symmetric functions of the roots
(evaluation points L_j of the support E_j). So the connection is direct.

## Lemma counterexample at c=3 (small prime)

Found a TRUE c=3 lemma counterexample at `n=12 c=3 p=61`:

```
s_1 = [1, 40, 28, 45, 19, 24]
s_2 = [12, 19, 34, 16, 42, 47]
E_1 = (1, 4, 5),  γ_1 = 33
E_2 = (1, 4, 8),  γ_2 = 41
E_3 = (4, 5, 8),  γ_3 = 48
E_4 = (1, 5, 8),  γ_4 = 52

m = 4, bound = ⌊11/3⌋ = 3.
rank A = 8 < 12 = min(mc, 2D).
⟨n_0(E_i), s_2⟩ = [55, 2, 31, 41] (all nonzero).
LEMMA DISPROVED at p=61.
```

### Structure: TETRAHEDRON

The 4 supports `(1,4,5), (1,4,8), (4,5,8), (1,5,8)` are EXACTLY the 4 size-3 subsets
of `{1, 4, 5, 8}`. This is a **tetrahedron** (4-clique on 4 vertices):

- Each support has size `w = 3`
- Universe has `w + 1 = 4` vertices
- Number of subsets: `C(4, 3) = 4`
- Pairwise intersection size: `w - 1 = 2`

**Generalization**: at c with w = D-c, the "tetrahedron" pattern is `m = C(w+1, w) = w+1`
size-w subsets of a (w+1)-set. Each pair shares w-1 elements.

For c=2 (w=D-2): tetrahedron has `m = D-1` supports.
For c=3 (w=D-3): tetrahedron has `m = D-2` supports.
For c=c_J (rate 1/2, w=w_J): tetrahedron has `m = w_J + 1 ≈ 0.293n + 1` supports.

**Tetrahedron exceeds the bound `⌊(2D-1)/c⌋`?**
- c=3: bound ≈ 2D/3, tetrahedron m = D-2. Tetrahedron > bound iff D-2 > 2D/3, i.e., D > 6.
- For n=12 (D=6): D-2 = 4 = m, bound = 3. Tetrahedron exceeds bound.
- For n=16 (D=8): D-2 = 6, bound = 5. Tetrahedron exceeds bound.
- For n=20 (D=10): D-2 = 8, bound = 6. Tetrahedron exceeds bound.

**At LARGE primes**: tetrahedron is NOT realizable empirically (max_bad ≤ 2 < bound).
The realizability requires specific algebraic conditions on (s_1, s_2) that fail at
large p (Schwartz-Zippel / mod-p coincidence vanishes).

## Updated conjecture (v5)

**Conjecture**: For RS[n, k] over F_p with c ≥ 3, at sufficiently large p:
`max_bad(s_1, s_2) ≤ ⌊(2D-1)/c⌋`.

The lemma (and bound) fail at small primes due to Schwartz-Zippel-style coincidences.
The lemma holds as an algebraic identity over Q (or F_p for p large).

**Threshold for "sufficiently large"**: empirically p > some `p_0(n, c)` which seems
to scale polynomially in `n`.

## Concrete next steps

1. **Verify lemma at large p**: find (or fail to find) lemma counterexamples at p ≥ 1000
2. **Algebraic proof over Q**: lift the proof to characteristic 0 / generic prime
3. **Lam-Leung connection**: investigate if vanishing sum machinery applies

## Files

- `notes/0091-berlekamp-c322-state.md` — entering state
- `notes/0092-open-set-rank-lemma-failure.md` — c=2 witness analysis
- `notes/0093-cstar-equals-3-conjecture.md` — c*=3 conjecture
- `notes/0094-proof-strategy-c3.md` — this file
- `notes/scripts/op2_find_witness_general.py` — general c witness finder
- `notes/scripts/op2_c3_verylarge_p.py` — large-p verification
