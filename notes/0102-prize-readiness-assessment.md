# Note 0102 — Prize-Readiness Assessment for Berlekamp #322 thread

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322`
**Cumulative work**: Notes 0091–0101

## Executive summary

| Component                                    | Status                  |
|----------------------------------------------|-------------------------|
| Refute strong unconditional bound            | ✅ DONE (Note 0099)     |
| Worst-case lower bound max_bad ≥ w+1         | ✅ PROVEN (Note 0099)   |
| Codim formula for V_tet(V)                   | ✅ PROVEN (Note 0099)   |
| Conjecture v6 (V_bad ⊂ ∪_V V_tet)            | ⚠️ EMPIRICAL (Note 0101) |
| Density bound poly(n)·p^{-(w+2c-1)}          | ⚠️ Modulo v6            |
| FRI 2-round soundness application            | ❌ Not done             |
| Paper §6.6 rewrite                           | ❌ Not done             |

**Estimated remaining work for full prize-ready**: 3-5 weeks focused effort.

## What's RIGOROUSLY proven

### Theorem 1 (Tetrahedron lower bound — Note 0099)

For RS[n, k] over F_p with c = n - k - w ≥ 3 and w ≥ 2, distinct L_1, ..., L_n ∈ F_p,
and V = {v_1, ..., v_{w+1}} ⊂ [n], the supports E_v := V \ {v} satisfy:
```
   max_{(s_1, s_2) ∈ F_p^{2D}} M(s_1, s_2) ≥ w + 1
```

**Proof**: Lagrange diagonality. The (w+1) × (w+1) matrix M_{ij} = Λ_{E_i}(L_{v_j})
is diagonal, forcing rank A = 2c + w - 1 < min(mc, 2D) = (w+1)c. The kernel ker A
in F_p^{2D} has dim w+1, and explicit construction shows (0, Λ_{E_i}) ∉ row-span(A)
for any i. → Open-Set Rank Lemma's escape clause vacuous → all m γ's realize. □

### Corollary (refutation of #322 strong conjecture)

The conjectured bound `max_bad ≤ ⌊(2D-1)/c⌋` for any (c, n) is FALSE whenever
w + 1 > ⌊(2D-1)/c⌋, which holds for all RS[n, n/2] with n ≥ 12, c ≥ 3.

This complements the issue author's c=1 counterexample (Paper 1 Theorem 4.1).

### Theorem 2 (Codim formula — Note 0099)

For each V ⊂ [n] with |V| = w+1, the tetrahedron-witness variety V_tet(V) ⊂ F_p^{2D}
is a (w+1)-dimensional algebraic subvariety (parameterized by the kernel of A_V),
giving codimension 2D - (w+1) = w + 2c - 1 in the ambient (s_1, s_2)-space.

(Proof: dim X_γ_tet = (w-1)(c-1) verified analytically and across 19 (n, c) cases.)

## What's CONJECTURED with strong evidence

### Conjecture v6 (Bad-set characterization — Note 0101)

```
   V_bad := {(s_1, s_2) : M(s_1, s_2) > T} = ⋃_{V ⊂ [n], |V|=w+1} V_tet(V)
```

**Empirical support** (3 angles):
1. Tet-witnesses give exactly M = w+1, no spillover (op2_witness_full_M.py)
2. V_tet(V_1) ∩ V_tet(V_2) is empty for V_1 ≠ V_2 (op2_intersection_tets.py)
3. Non-tet rank-deficient configs give M ≤ 2 (op2_nontet_witnesses.py)
4. 50K random (s_1, s_2) at n=12 c=3 p=1009: 0 bound violations (op2_tet_density.py)

**Status**: not proven analytically. The (⇒) direction is the gap.

### Density theorem (modulo v6)

```
   Pr_{(s_1, s_2) ∈ F_p^{2D}}[M(s_1, s_2) > T] ≤ C(n, w+1) · p^{-(w + 2c - 1)}
```

For prize-relevant fields:

| Field   | n  | c | Pr bound                | Comment              |
|---------|----|---|-------------------------|----------------------|
| BabyBear| 12 | 3 | 495 · 2^{-248}          | < 2^{-240}           |
| BabyBear| 28 | 6 | 30M · 2^{-682}          | < 2^{-650}           |
| BabyBear| 40 | 9 | 5G · 2^{-868}           | < 2^{-830}           |

All trivially soundness-tight. ε << 2^{-128}.

## What's NEEDED for "prize-ready"

### (A) Prove Conjecture v6 (3-4 weeks focused)

The (⇒) direction: if (s_1, s_2) realizes m > T distinct γ's, then ∃V s.t.
the realized supports include the tetrahedron(V). 

**Strategy**:
- Use the κ-distribution analysis (op2_pointwise_evaluation.py)
- For (ĥ_j) ∈ X_γ with all ĥ_j ≠ 0 (necessary for m γ's realized), derive
  combinatorial conditions on supports
- Show: only tetrahedron sub-pattern admits all-active syzygies

### (B) FRI 2-round soundness application (1-2 weeks)

Given the density bound, derive ε_ca for FRI 2-round:
- Verifier picks random (s_1, s_2) (or equivalent challenge)
- Prove: probability of hitting V_bad is ≤ poly(n) · p^{-(w+2c-1)}
- Translate to ε_FRI using standard FRI soundness reduction

### (C) Comparison to existing bounds (BCIKS, Crites-Stewart) (1 week)

- Identify the regime (n, k, p, δ) where this gives improvement
- Especially: at the Johnson-radius regime where #322 was conjectured

### (D) Paper integration (1-2 weeks)

- Rewrite Paper 1 §6.6 with the corrected Phase Diagram
- Add §6.7: "Generic vs worst-case max_bad" with v6 statement
- Expand on the c=2 vs c≥3 transition (companion to §6.5)

## Branch state

- 9 commits on `feat/berlekamp-c322`, all pushed
- 12 notes (0091–0102) covering the full investigation
- ~25 scripts in `notes/scripts/op2_*` for empirical verification
- Total: ~3000 lines of notes + scripts

## Recommended next session entry point

Read in this order:
1. `notes/0100-final-state-v2.md` — overview after refutation
2. `notes/0099-tetrahedron-analytic-proof.md` — the rigorous theorem
3. `notes/0101-prize-ready-conjecture.md` — Conjecture v6 + density
4. `notes/0102-prize-readiness-assessment.md` — this file

Pick up at: attempt analytic proof of (⇒) direction of v6 via κ-pattern argument.

## Distance to "fully resolves #322"

- **Issue closure** (negative answer): ~0 days. Post comment with refutation.
- **Prize-relevant statement** (Conjecture v6 proved): 3-5 weeks.
- **Full FRI soundness with this angle**: 6-8 weeks total.

## Distance to actual prize $1M

The Berlekamp #322 thread is one of multiple angles. Even with v6 proven and
FRI soundness application, this contributes to but does NOT alone win the
prize. The judges expect either:
- A new universal lower bound on FRI soundness in the open zone, OR
- A new algorithmic / coding-theoretic insight applicable across protocols

Our angle: c ≥ 3 bound + sequence-school techniques.
This branch's contribution would be cited in a broader prize submission.
