# Note 0123 — codim V_bad = 2(c−1) universal: closes the c ≥ 5 gap

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0117 (upper), 0119 (case-A bound), 0122 (case-B → A reduction).
**Status**: RIGOROUS UNIVERSAL. No conjectures. Closes the |S*| ≤ w+⌊w/T⌋
"loose" bound to a TIGHT codim 2(c−1) for all c ≥ 2.

## Headline

```
codim V_bad  =  2(c − 1)        RIGOROUSLY for ALL c ≥ 2, ALL D (w ≥ 1, T ≥ 1)
```

The Note 0119 bound `|S*| ≤ w + ⌊w/T⌋` (which can give codim > 2(c−1) for
c ≥ 5 when ⌊w/T⌋ ≥ 2) is loose at the dim/codim level. A sub-leading
stratum analysis tightens it: every component of V_bad with |S*| > w+1
has dim STRICTLY LESS than the leading 2(w+1).

## The dim/codim analysis

Let (s_1, s_2) ∈ V_bad with realizers (γ_l, E_l)_{l=1..m}, m ≥ T+1.
By Note 0122, replace each E_l with E_l^A ⊂ S* (case A). Set δ' := |S*|−w.

**Stratification**: V_bad = ⋃_{δ' ≥ 0} V_bad^{(δ')} where
V_bad^{(δ')} := {(s_1, s_2) : |S*(s_1, s_2)| = w + δ', M > T}.

**Leading (δ' = 1)**: V_S × V_S ⊂ V_bad for |S| = w+1 (Note 0117).
dim = 2(w+1). codim = 2(c−1) in F^{2D}.

**Sub-leading (δ' ≥ 2)**: must show dim < 2(w+1).

### Sub-leading codim count

For (s_1, s_2) ∈ V_bad^{(δ')} with δ' ≥ 2:

1. (Note 0122) m = T+1 distinct γ_l, each a case-A realizer with
   E_l^A ⊂ S*, |E_l^A| = w.

2. (Note 0119) Each γ_l satisfies r(γ_l) := |f^{−1}(γ_l) ∩ V_1| ≥ δ',
   where f(v) = −α_v/β_v, V_1 = {v ∈ S* : β_v ≠ 0}.

3. The γ_l being distinct means the preimages f^{−1}(γ_l) are
   **disjoint** subsets of V_1. We have T+1 disjoint preimages,
   each of size ≥ δ'. They consume ≥ (T+1)δ' elements of V_1, which
   fits since (T+1)δ' ≤ |V_1| ≤ |S*| = w+δ' iff δ' ≤ w/T (Note 0119).

4. **Codim per preimage**: a preimage of size r in coords (α, β) on
   V_1 ⊂ F^{2|V_1|} is the set {(α, β) : −α_{v_1}/β_{v_1} = ··· =
   −α_{v_r}/β_{v_r}}. Equivalent to r−1 cross-ratio equations
   α_{v_i}β_{v_{i+1}} = α_{v_{i+1}}β_{v_i}. **codim = r − 1 ≥ δ' − 1**.

5. **Independence**: different preimages involve disjoint variable sets,
   so the codim conditions are independent. Total
   codim within V_{S*}² (sub-case A1, all β_v ≠ 0):
   ```
   codim_in_V*²  ≥  Σ_l (r(γ_l) − 1)  ≥  (T+1)(δ' − 1)
   ```

   Sub-case A2 (some β_v = 0) only ADDS codim: |V_0| more linear
   constraints β_v = 0 for v ∈ V_0, on top of the V_1 analysis.

6. **V_{S*}² codim in F^{2D}**: 2(c − δ').

7. **Total codim of V_bad^{(δ')} in F^{2D}**:
   ```
   codim_total  ≥  2(c − δ')  +  (T+1)(δ' − 1)
                =  2c − δ' − T − 1 + δ'·T
                =  2(c − 1)  +  (δ' − 1)(T − 1)
   ```

8. For δ' ≥ 2 and T ≥ 1:
   ```
   (δ' − 1)(T − 1)  ≥  0
   ```
   with **strict inequality iff T ≥ 2 AND δ' ≥ 2**.

### Conclusion

```
dim V_bad^{(δ')}  ≤  2D − codim_total
                  =  2(w+1) − (δ' − 1)(T − 1)
                  ≤  2(w+1)
```

with equality iff δ' = 1 (leading) or T = 1 (degenerate).

For non-degenerate deployment (T ≥ 2, equivalently w ≥ T ≥ 2):
sub-leading components have dim **strictly less** than 2(w+1).

Hence dim V_bad = 2(w+1), codim V_bad = 2(c−1). ∎

## Edge cases

**T = 1**: requires `2D − 1 < 2c`, i.e., `D ≤ c`, i.e., `w ≤ 0`. Trivial
decoder, ignore.

**T = 0**: `m = T+1 = 1` is "any single realizer is bad". Then V_bad =
all (s_1, s_2) with M ≥ 1, codim = 2c − 1 (Hankel rank ≤ w variety).
Not the deployment regime.

**δ' = 0**: |S*| = w. Then E_l^A = S* for all l (only one case-A
choice). V_{S*}² has codim 2c in F^{2D}, all γ realize, M = q − 1 > T,
so V_{S*}² ⊂ V_bad. dim 2w < 2(w+1) ✓ (sub-leading by 2).

## Implications

### 1. Universal closure

| c   | Old (Notes 0119+0122) | Note 0123 (this note) |
|-----|------------------------|------------------------|
| 3   | codim = 2(c−1) = 4    | codim = 4 (same)       |
| 4   | codim = 2(c−1) = 6    | codim = 6 (same)       |
| 5   | codim ≥ 2(c−2) = 6    | **codim = 8**          |
| 6   | codim ≥ 2(c−2) = 8    | **codim = 10**         |
| 7   | codim ≥ 2(c−3) = 8    | **codim = 12**         |
| ≥ 8 | codim ≥ 2(c−⌊w/T⌋)    | **codim = 2(c−1)**     |

For c ∈ {3, 4} the result was already known. For c ≥ 5 this **closes
the gap** that Note 0119 left between the loose bound 2(c−⌊w/T⌋) and
the matching upper bound 2(c−1) from Note 0117.

### 2. Deployment table impact

The 90.6% pass rate at codim 2(c−1) (Note 0116) was already RIGOROUS
for c ∈ {3, 4} (the dominant deployment rows). Note 0123 extends rigor
uniformly to c ∈ {6, 9} rows — these were also passing under the
optimistic 2(c−1) assumption, now justified.

| c | Status pre-Note 0123      | Status post-Note 0123 |
|---|---------------------------|------------------------|
| 3 | RIGOROUS UNCONDITIONAL    | unchanged              |
| 4 | RIGOROUS UNCONDITIONAL    | unchanged              |
| 6 | rigorous codim ≥ 8        | **RIGOROUS codim = 10** |
| 9 | rigorous codim ≥ 10       | **RIGOROUS codim = 16** |

### 3. Prize-grade soundness

For ABF §6.3 KoalaBear-ext6 and similar deployment rows: ε_round ≤
poly(n)·q^{-2(c−1)} now RIGOROUS for all c. The "modulo Conjecture B"
qualifiers are removed entirely (Note 0122 closed Conjecture B for
c ∈ {3, 4} by reduction; Note 0123 closes the residual c ≥ 5 gap).

## Why the Note 0119 bound was loose

Note 0119 derived `m·(|S*|−w) ≤ |S*|` from r(γ_l) ≥ δ' summed over l ≤
T+1. This gave |S*| ≤ w·m/(m−1) = w + w/T, i.e., δ' ≤ ⌊w/T⌋.

The bound is sharp **at the |S*|-level**: there exist (s_1, s_2) with
|S*| = w + ⌊w/T⌋ in V_bad (the "extremal" case where all r(γ_l) = δ'
exactly).

But these extremal witnesses live in a CODIM-(T+1)(δ'−1) subvariety of
V_{S*}², not in the entire V_{S*}². So they're sub-leading at the
codim/dim level.

Note 0123 captures this codim correction — the sub-leading components
exist (the |S*| bound is sharp) but have lower dimension than leading,
so they don't affect dim V_bad or codim V_bad.

## Reading order (final, post-Note 0123)

1. **Note 0117**: codim V_bad ≤ 2(c−1) (V_S × V_S construction).
2. **Note 0119 §"Proof (Case A)"**: r(γ_l) ≥ |S*| − w bound.
3. **Note 0122**: case-B → case-A substitution (no Conjecture B).
4. **Note 0123**: dim/codim closes sub-leading strata for c ≥ 5.
5. **Note 0121**: consolidated state (now to be updated).

## Files (no new scripts — argument is purely algebraic)

The result builds entirely on existing structure (Notes 0117 + 0119 +
0122). No new computation needed. The empirical layers in Note 0119
(340/340 etc.) remain as redundant validation for the |S*| ≤ w+⌊w/T⌋
sharp bound; Note 0123 says the remaining "extremal" witnesses with
|S*| > w+1 are codim-suppressed and don't affect the headline.

## What's still open

After Note 0123, the **only** remaining question is the **prefactor**:
codim V_bad = 2(c−1) means Pr[bad] ≲ poly(n) · q^{-2(c−1)}. The poly(n)
factor (number of |S|=w+1 components, ≤ C(n, w+1)) determines the exact
deployment ε bound. The prefactor analysis is deployment-context-
specific (FRI commit-side vs query-side) and lives in Note 0120 + the
Paper §6.6 writeup, not in the codim theorem itself.
