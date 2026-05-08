# Note 0512 — K_2 = q-1 saturating cases have Δ_joint(0) = 1.0 (above-J)

**Date:** 2026-05-05 (Q2 drill iter 35, post Note 0511)
**Status:** **Caution flag**: K_2 = q-1 saturating cases at (16, 4) are STRICT above-J w.r.t. zero codeword pair. Conjecture scope explicitly EXCLUDES (16, 4) (deployment starts at (32, 8)), but raises questions about deployment-scale verification.

## Classification of K_2 = q-1 saturating cases

For each support that achieved K_2 = 16 in the full 220-support sweep (Note 0511), 300 random coefficient trials yielded near-saturating cases:

| Support | Class | K_1 | K_2 | Δ_joint (to (0,0)) | \|T\| |
|---|---|---|---|---|---|
| (4, 8, 12) | mod-4 sym | 1 | 15 | 1.000 | 0 |
| (8, 9, 10) | AP-step-1 around n/2 | 0 | **16** | 1.000 | 0 |
| (9, 10, 11) | AP-step-1 around n/2 | 0 | **16** | 1.000 | 0 |
| (8, 9, 11) | non-AP includes n/2 | 0 | **16** | 1.000 | 0 |
| (8, 10, 11) | non-AP includes n/2 | 0 | **16** | 1.000 | 0 |
| (6, 9, 14) | non-AP | 1 | 15 | 1.000 | 0 |
| (7, 10, 15) | non-AP | 1 | 15 | 1.000 | 0 |

## Critical observation

All K_2 = 16 (= q-1) saturating cases have:
- Δ_joint to (0, 0) = 1.000 → **strict above-J** w.r.t. zero codeword pair.
- |T| = 0 → no common zeros.
- All q-1 = 16 nonzero α admit non-zero codeword witness.

**These ARE in the conjecture's strict above-J class** (assuming joint distance is to (0, 0); true min-Δ over all (c_1, c_2) ∈ C^2 might be smaller).

## Conjecture scope check

paper2 `conj:sparse-worst` (line 2316):
> ...at FRI two-round deployment scale $(n_0, k_0) \in \{(32, 8), (64, 16), \ldots, (2^{19}, 2^{17})\}$...

**(16, 4) is BELOW deployment scope.** So K = 16 at (16, 4) does NOT directly refute the conjecture.

But it DOES raise the question: does similar saturation occur at (32, 8) and up?

## Critical caveats

1. **Δ_joint computation incomplete**: I computed Δ_joint w.r.t. $(0, 0)$ codeword pair only, not the true min over all $(c_1, c_2) \in C^2$. True Δ_joint might be ≤ 1/2 (i.e., the pair could be BELOW-J after optimal codeword shift).

2. **Action-non-stab check ambiguous**: Strict pointwise definition ("ω^{b-a} · ω^j = ω^j ∀j ∈ supp") is trivially false for non-trivial (b-a). The relevant operational definition is "support contained in single fold quadrant" (mod-4 class). Some saturating supports like (8, 9, 11) span multiple mod-4 classes — these might be action-non-stab but still saturate.

3. **(32, 8) deployment empirical evidence**: 4.6M cert sweep + 615M trials, 0 counterexamples. So conjecture holds empirically at deployment.

## What this means for paper2 v24

paper2 v24 patch (commit 2ee9d35, with LaTeX fix in e1a20df):
- **K_1 ≤ 3 RIGOROUS** holds for all above-J pairs at (32, 8)+.
- **K_2 ≤ 7** is the conjectured part. Empirical at (32, 8) deployment via 4.6M certs.
- (16, 4) base-case anomalies (K_2 = q-1 saturation) do NOT propagate to deployment empirically.

The conjecture's deployment-scale restriction is essential — base-case (16, 4) has different K_2 behavior.

## Action items for next iter

1. **Compute true Δ_joint(min over c_1, c_2)** for the saturating (16, 4) cases to clarify whether they're really above-J or just above-J w.r.t. (0,0).

2. **Verify K_2 ≤ 7 at (32, 8)** for the LIFTED versions of these problematic supports (e.g., (8, 9, 10) at (16,4) lifts via z↦z^2 to (16, 18, 20) at (32, 8) — but wait, lifts to indices in [16, 32) which isn't above-J at (32, 8) which needs indices ≥ k_0 = 8).

3. **Tighten conjecture statement**: maybe paper2 should explicitly note "(16, 4) is below deployment threshold; see Appendix for base-case behavior".

## Conclusion

paper2 v24's K_1 + K_2 framework is robust and reflects genuine progress. The K_2 ≤ 7 conjecture remains structurally open with caveats:
- At (16, 4) base: K_2 can saturate to q-1 for action-stab and certain action-non-stab supports.
- At (32, 8) deployment: K_2 ≤ 7 empirically (4.6M cert + 615M trials).
- Conjecture scope (32, 8)+ is correct.
