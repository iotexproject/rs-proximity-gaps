# Note 0095 — Paper 1 §6.6 Draft (Berlekamp Overconstrained, c ≥ 3)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Target**: paper.tex §6.6 (between §6.5 c=2 exponential and §7 Open Problems)

---

## Section 6.6: Worst-case bound at codimension excess c ≥ 3

### Setup and statement

Let `RS_k = RS[F_p, L, k]` with `|L| = n`. Define the codimension excess
`c := n - k - w`, so weight-`w` errors live in a codim-`c` subspace of the syndrome
space `F_p^D` (where `D := n - k`).

Define the worst-case list size on a syndrome line:

```
M(s_1, s_2) := |{γ ∈ F_p* : line s_1 + γs_2 hits Im(V_E) for some E ∈ C(L, w)}|
M_max(n, k, p, c) := max_{(s_1, s_2) ≠ (0, 0)} M(s_1, s_2)
```

### Theorem 6.6.1 (Phase Diagram)

**For `c = 1` (covering radius):** `M_max = min(p, C(n, w))`. At `p ≥ C(n, w)`,
`M_max = C(n, w)` (Paper 1 Theorem 4.1, tight).

**For `c = 2`:** `M_max ~ 1.355^n` (exponential in `n`; companion paper, branch
`feat/c2-exponential-growth`, n ≤ 24 verified).

**For `c ≥ 3` at sufficiently large `p`:** `M_max ≤ ⌊(2D-1)/c⌋` (this section, proof
sketch via Open-Set Rank Lemma).

**At Johnson radius (`c = c_J(n, k)`):** Combining the above,
```
   M_max(n, k, p, c_J) ≤ ⌊(2D - 1)/c_J⌋
```
For rate `1/2`: `c_J ≈ n(√2-1)/2 ≈ 0.207n`, so the bound `≈ 4` (constant in `n`).

### Theorem 6.6.2 (Open-Set Rank Lemma at c ≥ 3, conjectured)

For supports `E_1, ..., E_m ⊂ [n]` of size `w = D - c` (with `c ≥ 3`), distinct
`γ_1, ..., γ_m ∈ F_p^*`, and `A ∈ F_p^{m·c × 2D}` the constraint matrix with row
blocks `[N_{E_i} | γ_i N_{E_i}]`, **for all sufficiently large `p`**:

> Either `rank A = min(m·c, 2D)`, OR ∃`i` with `⟨n_0(E_i), s_2⟩ = 0` for all
> `(s_1, s_2) ∈ ker A`.

**Corollary (the bound)**: For any `(s_1, s_2)` with `M(s_1, s_2) = m`, we have
`m ≤ ⌊(2D-1)/c⌋`.

### Empirical evidence

**Verified via heavy-random search at large primes:**

| `n`  | `k`  | `D` | `c` | `w` | `bound` | observed `M_max` | passes? |
|------|------|-----|-----|-----|---------|-------------------|---------|
| 8    | 4    | 4   | 3   | 1   | 2       | 1                 | ✓       |
| 12   | 6    | 6   | 3   | 3   | 3       | 1 (p=601-709)     | ✓       |
| 16   | 8    | 8   | 3   | 5   | 5       | 2 (p=1009-1249)   | ✓       |
| 20   | 10   | 10  | 5   | 5   | 3       | ≤ 2 (PR #347 emp) | ✓       |
| 24   | 12   | 12  | 5   | 7   | 4       | ≤ 2               | ✓       |
| 28   | 14   | 14  | 6   | 8   | 4       | ≤ 4               | ✓       |
| 32   | 16   | 16  | 7   | 9   | 4       | ≤ 4               | ✓       |
| 36   | 18   | 18  | 8   | 10  | 4       | ≤ 4               | ✓       |
| 40   | 20   | 20  | 9   | 11  | 4       | ≤ 4               | ✓       |

(Last 5 rows from #322 comments, ≤ 14000 random configs each.)

### Counterexample structures at small primes (Schwartz-Zippel exceptions)

The lemma can FAIL at small primes due to mod-`p` algebraic coincidences:

**c = 2 (n = 8): Triangle obstruction.** At `p = 113`, the supports
`E_1 = (3,6), E_2 = (5,6), E_4 = (3,5)` form a `K_3` on vertices `{3,5,6}`, plus
disjoint `E_3 = (0,1)`. Witness gives `M = 4 > 3 = bound`. Row dependency uses
only triangle supports; `E_3` provides the +1.

**c = 3 (n = 12): Tetrahedron obstruction.** At `p = 61`, the supports
`(1,4,5), (1,4,8), (4,5,8), (1,5,8)` are all 4 size-3 subsets of `{1,4,5,8}`,
forming `K_4` (tetrahedron). Witness gives `M = 4 > 3 = bound`.

**General pattern**: at `c` with `w = D - c`, the "(`w+1`)-clique" (= all size-`w`
subsets of `(w+1)`-set) gives `m = w+1 > ⌊(2D-1)/c⌋ = O(D/c)` supports.
Realizable at small primes only.

### Proof outline (sketch, for c ≥ 3)

The lemma holds as an algebraic identity over `Q` (or any infinite field).
Lifting to `F_p` for sufficiently large `p` follows from Schwartz-Zippel.

Key ingredients:
1. **Polynomial reformulation**. Row span A consists of pairs
   `(Σ ĥ_j Λ_{E_j}, Σ γ_j ĥ_j Λ_{E_j})` for `ĥ_j ∈ F_p[x]_<c`.
   `(0, Λ_{E_i}) ∈ row span` corresponds to a specific syzygy.
2. **Twisted syzygy module**.
   `X_γ := {(ĥ_j) : Σ ĥ_j Λ_{E_j} = 0 ∧ Σ γ_j ĥ_j Λ_{E_j} = 0}`.
   `dim X_γ = mc - rank A`.
3. **Vandermonde-Cramer construction**. For `(ĥ_j) ∈ X_γ \ {0}`, define
   `P(t, x) := Σ_j ĥ_j Λ_{E_j} ∏_{l≠j}(t - γ_l)`. By X_γ conditions,
   `deg_t P ≤ m - 3`.
4. **Rank argument** (key step, c ≥ 3 specific). At `c ≥ 3`, the polynomial
   `P(t, x)` carries enough degree-of-freedom to extract `Λ_{E_i}` for some `i`.
   At `c = 2`, the analogous polynomial has degree `≤ m - 3 = m - 3`, which
   fails to capture `Λ_{E_i}`.

**[Detailed proof in companion note 0094.]**

### Connection to Reed-Solomon code structure

The supports `E_i` correspond to error patterns at distance `w` from the
codeword. The matrix `A` encodes the linear constraint
"line `s_1 + γs_2` hits the affine subspace of error-`w` codewords with support `E_i`".

The lemma says: rank-deficiency of `A` forces the `s_2`-component of any
realizing `(s_1, s_2)` to be orthogonal to one of the support's "leading
syndrome vectors" `n_0(E_i)`.

This generalizes the **Berlekamp key equation overconstraint** mechanism:
once `m·c > 2D`, the system is overdetermined and has no nontrivial solution.

---

## Connection to Companion Paper §6.5 (c = 2 exponential)

The c = 2 case is fundamentally different. Both the Berlekamp bound `O(D/c) ≈ n/2`
and the Open-Set Rank Lemma fail. List size grows exponentially as
`M_max ≈ 0.63 × 1.355^n` (companion branch `feat/c2-exponential-growth`,
verified through `n = 24` with peak `M = 986`).

The c = 3 transition (this section) marks the boundary: at `c = 2`, the
"triangle/tetrahedron" support obstructions create exponentially many bad γ's;
at `c ≥ 3`, these obstructions vanish at sufficiently large `p` and `M_max`
becomes polynomial (linear) in `n`.

---

## Open Problem (unchanged)

**Tighter bound at intermediate `c`**. For `3 ≤ c ≤ c_J - 1`, the bound
`⌊(2D-1)/c⌋` is `O(n/c)` (linear in `n`). Empirically, observed `M_max` is
much smaller (constant or near-constant). Determining the **tight** asymptotic
behavior across this regime is open.
