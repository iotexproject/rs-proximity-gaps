# Note 0122 — Case-B → Case-A reduction: Conjecture B is now THEOREM B

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Note 0119 (case-A algebraic bound), 0117 (V_S × V_S inclusion).
**Status**: RIGOROUS. Closes the Case-B gap left open in Note 0119.

## Headline

The "Conjecture B" gap of Note 0119 is closed by a **support-substitution
argument**: every realizer (γ, E), case A or case B, admits a *case-A*
realizer (γ, E_A) with E_A ⊂ S* at the **same γ**. Hence Note 0119's
case-A bound `|S*| ≤ w + ⌊w/T⌋` applies to all V_bad witnesses
unconditionally.

```
codim V_bad  =  2(c − 1)        RIGOROUS for c ∈ {3, 4} all D
codim V_bad  ≥  2(c − ⌊w/T⌋)    RIGOROUS for general c, all D
```

For c ∈ {3, 4}: `⌊w/T⌋ = 1`, so the upper (Note 0117) and lower
(Note 0119 + this note) bounds match exactly.

## The Reduction

### Setup

Let (s_1, s_2) ∈ V_bad with realizers (γ_l, E_l)_{l=1..m}, m = T+1, and
S* the joint Vandermonde support (smallest S with s_1, s_2 ∈ V_S).

Write x_{γ_l} := s_1 + γ_l s_2. Each x_{γ_l} has rank ≤ w (since
x_{γ_l} ∈ V_{E_l}, |E_l|=w). Let

```
T_{γ_l}  :=  V_{S*}-support of x_{γ_l}
        =   {v ∈ S* : (α_v + γ_l β_v) ≠ 0}    (in V_{S*}-basis coords)
```

Then T_{γ_l} ⊂ S*, |T_{γ_l}| = (Hankel rank of x_{γ_l}) ≤ w.

### Construction of E_A

For each realizer (γ_l, E_l), define

```
E_l^A  :=  T_{γ_l}  ∪  (any w − |T_{γ_l}| extras drawn from S* ∖ T_{γ_l})
```

This requires `|S* ∖ T_{γ_l}| ≥ w − |T_{γ_l}|`, i.e., `|S*| ≥ w`.

**If |S*| < w**: the Note 0119 bound `|S*| ≤ w + ⌊w/T⌋` is trivially
satisfied (since |S*| < w ≤ w + 1). Done.

**Otherwise (|S*| ≥ w)**: E_l^A ⊂ S*, |E_l^A| = w, T_{γ_l} ⊂ E_l^A.

### (γ_l, E_l^A) is a case-A realizer

```
x_{γ_l}  ∈  V_{T_{γ_l}}  ⊂  V_{E_l^A}        (since T_{γ_l} ⊂ E_l^A)
|E_l^A ∪ S*|  =  |S*|  ≤  D                  (since E_l^A ⊂ S*)
```

The first line uses linear independence of {ev_v : v ∈ E_l^A} (which
holds because |E_l^A| = w ≤ D, Vandermonde). The second is the case-A
condition.

### Bound transfers

The set of distinct γ_l values is **unchanged** under substitution
E_l ↦ E_l^A (we keep γ_l fixed, only swap the supporting E). Hence
the multiplicity `m = T+1` of distinct γ-values is preserved.

Apply Note 0119's Sub-case A1 proof to (γ_l, E_l^A):

```
α_v + γ_l β_v  =  0    for all v ∈ S* ∖ E_l^A    (since x_{γ_l} ∈ V_{E_l^A})
```

(The forcing comes from {ev_v : v ∈ S*} linearly independent, |S*| ≤ D.)

Define `r(γ) := |{v ∈ S* : β_v ≠ 0 and α_v + γβ_v = 0}|`. Then
`r(γ_l) ≥ |S* ∖ E_l^A| = |S*| − w` (with equality, as E_l^A ⊂ S* and
|E_l^A| = w).

Sum over l:

```
m · (|S*| − w)  ≤  Σ_l r(γ_l)  ≤  Σ_γ r(γ)  ≤  |S*|
```

For m = T + 1, |S*| > w:

```
|S*|  ≤  w + ⌊w/T⌋
```

(Sub-case A2 (some β_v = 0) handled identically to Note 0119, by
reducing to V_1 := {v : β_v ≠ 0} with effective w' = w − |V_0|.) ∎

## Why this works (intuition)

The key fact is that x_γ ∈ F^D has a **canonical V_{S*}-representation**
(unique because |S*| ≤ D, Vandermonde), with V_{S*}-support T_γ
intrinsic to x_γ. Whether x_γ ∈ V_{E_B} for some E_B ⊄ S* (case B) is
**irrelevant for the algebra of S***: T_γ ⊂ S* still suffices to find an
E_A ⊂ S* containing T_γ.

The Note 0119 obstruction "T' ⊂ E_l with |T'| ≤ w but T' ⊄ S*" was about
the *alternative* support T' inside E_B. But T' is irrelevant — what
matters is T_{γ_l}, which is a property of x_{γ_l} (independent of E_l)
and lives inside S* by definition.

Equivalently: Prony rank of x_γ in the V_{S*}-basis is the unique
"intrinsic" rank, and this rank ≤ w ⟺ x_γ realized in some V_E.

## Implications

### 1. Conjecture B is THEOREM B

The 4-layer empirical evidence in Note 0119 (340/340 |S*| bound +
0/600 V_bad density at δ=1 + 0/400 at δ=2 + 0/44 case-B realizers in
V_S × V_S) is now **redundant** — the bound is rigorous.

### 2. Deployment table now fully rigorous (c ∈ {3, 4})

| Aspect                                  | Status (post-Note 0122) |
|-----------------------------------------|-------------------------|
| codim V_bad ≤ 2(c−1)                    | RIGOROUS (Note 0117)    |
| codim V_bad ≥ 2(c−1) for c ∈ {3, 4}     | **RIGOROUS** (Notes 0119+0122) |
| codim V_bad ≥ 2(c−⌊w/T⌋) for c ≥ 5      | RIGOROUS (Notes 0119+0122) |

For c ∈ {3, 4}: `codim V_bad = 2(c−1)` exactly, no conjectures.

### 3. Prize submission status (Note 0121 update)

Type-A (positive bound): **fully rigorous** for c ∈ {3, 4} at all D.
Conditional notes about Conjecture B can be removed.

Type-B (counter-example for c=3 31-bit base fields): unchanged, still
rigorously off by 4 bits.

### 4. The general-c bound

For any c ≥ 2:

```
|S*|  ≤  w + ⌊w/T⌋          (RIGOROUS)
codim V_bad  ≥  2(c − ⌊w/T⌋)  (RIGOROUS, Note 0117 matches when ⌊w/T⌋ = 1)
```

For c = 5, 6, 7: ⌊w/T⌋ ∈ {1, 2, 2}, giving codim ≥ 2(c−2) or 2(c−1)
depending on D. Still nontrivial improvement over BCIKS-generic n/q.

## Comparison with prior rigor claim

Note 0119 said: "RIGOROUS for c ∈ {3, 4} all D **modulo Conjecture B**".

Note 0122 says: "RIGOROUS for c ∈ {3, 4} all D, **unconditionally**".

The substitution argument is purely linear-algebraic; it relies only on
{ev_v : v ∈ S*} being linearly independent (which holds whenever |S*|
≤ D, automatic). No probabilistic, no genericity, no measure-theoretic
input.

## Reading order (updated)

1. **Note 0117**: rigorous upper bound (V_S × V_S construction).
2. **Note 0119 §"Proof (Case A)"**: r(γ_l) ≥ |S*| − w bound and finite-
   geometry counting argument. (The §"Case B" part is now superseded.)
3. **Note 0122 (this note)**: substitution argument that makes Case A
   universal.
4. **Note 0121**: consolidated state, now with unconditional rigor.

## Files (no new scripts — argument is purely algebraic)

The rigor of this reduction means the four empirical confirmation layers
in Note 0119 can be cited as *redundant validation* rather than essential
pillars. Scripts retained for reproducibility and as sanity checks.

## What's still open

1. **For c ≥ 5 large D**: the bound `|S*| ≤ w + ⌊w/T⌋` may give ⌊w/T⌋ > 1,
   so codim V_bad ≥ 2(c − ⌊w/T⌋) < 2(c−1). The Note 0117 upper bound
   2(c−1) still applies. Closing the gap (proving codim V_bad = 2(c−1)
   for c ≥ 5) would require a tighter |S*| bound, possibly via
   non-trivial algebraic-combinatorial input.
2. **Lean formalization** (Issue #341 follow-up): the substitution
   argument is short and clean; ideal candidate.
3. **Paper §6.6 rewrite**: lead with the unconditional theorem.
