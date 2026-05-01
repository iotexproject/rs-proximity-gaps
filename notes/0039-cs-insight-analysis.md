# Note 0039 — Crites-Stewart Insights for the Borderline Barrier

**Date**: 2026-04-21

## Key observations

### 1. ABF Thm 5.3 cannot be invoked above Johnson
Our loss 2δ_hd exceeds 1-ρ-1/n for all δ_hd > (1-ρ)/2 < δ_J. CONFIRMED: no route via ABF reductions.

### 2. Triangle inequality is already tight
The refined analysis (S_γ \ E vs S_γ ∩ E) gives the same 2δ bound. No slack to exploit.

### 3. φ = e1/e is adversary-controlled
e1 = f1 - u1 (arbitrary), e = f2 - g2 (arbitrary). No RS structure constrains the ratio on E. The adversary CAN make φ injective → V = δn.

### 4. FRI commitment doesn't help
The prover commits f (hence f1, f2) before seeing γ. Can pre-set borderline structure.

### 5. CS paper's Shamir connection
Their key move: Shamir secret sharing ↔ RS. The attack on threshold Schnorr exploits that the adversary controls the "error" in the sharing. Same structure as our φ = e1/e: the adversary controls the error ratio. The CS paper's contribution was showing this attack WORKS (disproof), not preventing it.

## Paths forward

### A. FRI recursive argument
FRI checks consistency across rounds. Even if one round has borderline MCA, the NEXT round's fold either exposes the cheat (consistency failure) or reduces to a smaller problem. Could the recursive structure make the borderline irrelevant?

**Problem**: BCHKS's existing analysis already accounts for this. Their O(n/|F|) per round IS the result of the recursive analysis. We'd need a TIGHTER recursive argument.

### B. New reduction (CA → list-size)
CS proved CA → list-decodability. Their reduction requires δ_nt ≤ 1-ρ. Can a DIFFERENT reduction work with δ_nt = 2δ?

**Idea**: instead of reducing to GS decoder (which needs δ < J), use our COSET EXTRACTION as the decoder. Coset extraction works for k=2 above Johnson. Could it replace GS in the BCHKS reduction?

### C. O(n/|F|) is optimal (prove it)
Show that Θ(n/|F|) is information-theoretically tight for zero-loss MCA above Johnson. This would be a NEGATIVE result but would resolve the open problem.

Our Prop 8.1 gives the LOWER BOUND: ε_mca ≥ Ω(n/|F|). BCHKS gives the UPPER BOUND: ε_mca ≤ O(n/|F|). Together: ε_mca = Θ(n/|F|) at the borderline. This is already proved!

**The zero-loss MCA above Johnson IS Θ(n/|F|).** Our paper proves this (Thm 3.1 upper + Prop 8.1 lower).

## Wait — is this itself a publishable result?

**Theorem**: For plain RS codes in the intermediate zone:
- With loss δ: ε_ca(C, δ, 2δ) = O(1)/|F| [Theorem 3.1]
- Without loss: ε_mca(C, δ) = Θ(n/|F|) [BCHKS upper + Prop 8.1 lower]

This COMPLETELY CHARACTERIZES the CA/MCA behavior above Johnson:
- You can get O(1) exceptions WITH loss δ
- You MUST accept Θ(n) exceptions WITHOUT loss
- The transition is sharp at loss = 0 vs loss > 0

THIS is a clean, complete result. It says: the proximity loss is the PRICE you pay for O(1) exceptions above Johnson. No free lunch.
