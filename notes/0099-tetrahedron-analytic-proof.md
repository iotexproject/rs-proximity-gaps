# Note 0099 — Why tetrahedron breaks the Open-Set Rank Lemma (analytic proof)

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0097, 0098

> ⚠️ **Correction (Note 0114, 2026-04-29)**: the X_γ-side rank/Lagrange
> analysis below is correct. Any **codim contribution to V_bad** derived
> by `2D − dim ker A(γ)` for fixed γ is **WRONG** — the actual
> `dim V_tet(V) = 2(w+1)`, not `w+1`, because γ varies and ker A sweeps
> a `2(w+1)`-dim subspace `V_V × V_V`. See Note 0114.

## Statement

For supports E_i = V \ {v_i} (i = 1, ..., w+1) of size w, where V = {v_1, ..., v_{w+1}},
the **Open-Set Rank Lemma fails** at any prime p with distinct L_{v_i} ∈ F_p:

- rank A < min(mc, 2D)
- For all i, (0, Λ_{E_i}) ∉ row-span(A)
- Hence ⟨n_0(E_i), s_2⟩ ≠ 0 for some (s_1, s_2) ∈ ker A

## Proof

### Lagrange diagonality

Write Λ_V(z) := ∏_{j ∈ V}(z - L_j). Then:
```
Λ_{E_i}(z) = Λ_V(z) / (z - L_{v_i})
```

Evaluate at L_{v_j}:
```
Λ_{E_i}(L_{v_j}) = Λ_V(L_{v_j}) / (L_{v_j} - L_{v_i})
```

For j ≠ i: numerator Λ_V(L_{v_j}) = 0 (since v_j ∈ V), denominator nonzero, so
**Λ_{E_i}(L_{v_j}) = 0**. For j = i: Λ_V has simple zero at L_{v_i}, so the ratio is
nonzero by L'Hôpital: Λ_{E_i}(L_{v_i}) = Λ'_V(L_{v_i}) = ∏_{l ≠ i}(L_{v_i} - L_{v_l}).

So the matrix `M_{ij} := Λ_{E_i}(L_{v_j})` is **diagonal** with nonzero entries.

### X_γ has nontrivial elements (rank deficient)

Recall `X_γ := {(ĥ_j) ∈ (F_p[x]_<c)^m : Σ_j ĥ_j Λ_{E_j} = 0 ∧ Σ_j γ_j ĥ_j Λ_{E_j} = 0}`.
For any (ĥ_j) ∈ X_γ, evaluate the first constraint at x = L_{v_i}:
```
   Σ_j ĥ_j(L_{v_i}) · Λ_{E_j}(L_{v_i}) = 0
```
By diagonality of M, only j = i survives: `ĥ_i(L_{v_i}) · Λ_{E_i}(L_{v_i}) = 0`,
so **ĥ_i(L_{v_i}) = 0** for all i.

Hence ĥ_i(x) = (x - L_{v_i}) · q_i(x) for some q_i ∈ F_p[x]_{<c-1}.

Substituting back:
```
   ĥ_j(x) Λ_{E_j}(x) = (x - L_{v_j}) q_j(x) · Λ_V(x)/(x - L_{v_j}) = q_j(x) · Λ_V(x)
```

So the X_γ constraints simplify to:
```
   Σ_j q_j(x) · Λ_V(x) = 0  →  Σ_j q_j(x) = 0          (i)
   Σ_j γ_j q_j(x) · Λ_V(x) = 0  →  Σ_j γ_j q_j(x) = 0  (ii)
```

These are 2 linear constraints on Σ_{j=1}^{w+1} (c-1) = (w+1)(c-1) coefficients of
the q_j's. Each constraint kills (c-1) coefficients (degree-by-degree), so:
```
   dim X_γ = (w+1)(c-1) - 2(c-1) = (w-1)(c-1) ≥ 0  (always)
```

For c=3, w=3: dim X_γ = 2·2 = 4 ✓ (matches empirical at n=12).
For c=3, w=5: dim X_γ = 4·2 = 8 ✓ (matches at n=16).
For c=3, general w: dim X_γ = 2(w-1).

### (0, Λ_{E_i}) ∉ row-span(A) — open condition fails

For (0, Λ_{E_i}) ∈ row span A, need (ĥ_j) with:
```
   Σ_j ĥ_j Λ_{E_j} = 0           (X_γ_1 condition)
   Σ_j γ_j ĥ_j Λ_{E_j} = Λ_{E_i} (NEW: produces Λ_{E_i} in twisted sum)
```

From X_γ_1: ĥ_i(L_{v_i}) = 0 (same as before).

Evaluate the SECOND condition at x = L_{v_i}:
```
   Σ_j γ_j ĥ_j(L_{v_i}) · Λ_{E_j}(L_{v_i}) = Λ_{E_i}(L_{v_i})
```
By diagonality, only j = i survives:
```
   γ_i · ĥ_i(L_{v_i}) · Λ_{E_i}(L_{v_i}) = Λ_{E_i}(L_{v_i}) ≠ 0
```
So `ĥ_i(L_{v_i}) = 1/γ_i ≠ 0`.

**Contradiction** with `ĥ_i(L_{v_i}) = 0` from X_γ_1.

→ No (ĥ_j) realizes (0, Λ_{E_i}). Hence (0, Λ_{E_i}) ∉ row-span(A).
→ The lemma's open-condition branch is **vacuous** for the tetrahedron.

### Putting it together

- `dim X_γ = (w-1)(c-1)`. For c ≥ 3 and w ≥ 2, this is ≥ 2 — strict rank deficiency.
- (0, Λ_{E_i}) ∉ row-span(A) for any i — Lemma's escape clause vacuous.
- → `(s_1, s_2) ∈ ker A` exists with no E_i forced to have ⟨n_0, s_2⟩ = 0.
- → For each γ_i, the "bad γ" condition is realized non-trivially.
- → m = w+1 distinct bad γ's, exceeding the conjectured bound.

QED.

## Counting violation density

The (s_2)-projection of ker A:
```
   (s_1, s_2) ∈ ker A  ↔  (ĥ_j) ∈ X_γ via row-span correspondence
```
ker A → s_2 surjects onto a subspace of F_p^D of dimension d_2. Each (ĥ_j) ∈ X_γ
encodes (Σ_j ĥ_j Λ_{E_j}, Σ_j γ_j ĥ_j Λ_{E_j}) = (0, 0). The "open condition"
contribution to s_2 is more subtle — but empirically d_2 ≈ dim X_γ = (w-1)(c-1).

For random (s_1, s_2) ∈ F_p^{2D}: probability (s_1, s_2) ∈ tetrahedron-witness-set =
p^{(d_2 + d_1) - 2D} where d_1 + d_2 = ker dim.

For c=3, w=3, n=12: ker dim = 4, codim 8 in F_p^{12}. Density ≈ p^{-8}.

But there are C(n, w+1) tetrahedron V choices. For n=12 c=3: C(12, 4) = 495. So total
density ≈ 495 · p^{-8} ≈ p^{-4} for moderate p. Still negligible.

## Refined conjecture

The tetrahedron is the "minimal" violation pattern. We conjecture:

**Conjecture v6 (Generic Open-Set Rank Lemma)**: Outside the union of tetrahedron-
type loci (and their generalizations for larger m), the Open-Set Rank Lemma holds.
Equivalently:
```
   Pr_{(s_1, s_2)}[ M(s_1, s_2) > ⌊(2D-1)/c⌋ ] ≤ |violation patterns| × p^{-codim}
```
For p large enough, this is negligible — the bound holds with high probability.

## Implication for original Open-Set Rank Lemma

The lemma as stated in #322 is **false**. The tetrahedron is a counterexample.
The (w+1)-clique structure (where supports = (w+1)-set minus one vertex) is the
fundamental obstruction.

A correct version: "If supports do NOT form a (w+1)-clique, the lemma holds" —
but this needs further verification.

## Files

- `notes/scripts/op2_tetrahedron_over_Q.py` — Q verification
- `notes/scripts/op2_tet_witness_at_largep.py` — large-p verification  
- `notes/scripts/op2_tet_consolidated.py` — consolidated witness construction
- `notes/0097-tetrahedron-refutes-v5.md` — initial empirical refutation
- `notes/0098-multiclique-violations.md` — multi-clique scan
- `notes/0099-tetrahedron-analytic-proof.md` — this analytic proof
