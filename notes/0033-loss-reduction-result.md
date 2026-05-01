# Note 0033 — Proximity Loss Reduction: Partial Success

## Attempt: eliminate proximity loss δ from CA bound

### What we tried
Reduce ε_ca(C, δ, 2δ) to ε_ca(C, δ, δ) (zero loss).

### What we found

**Sub-case: f2 close, f1 close** (Δ(f1,C) ≤ δ, Δ(f2,C) ≤ δ):
- (f1,f2) is (δ,δ)-close to C^{=2}. All bad γ are CA-benign at threshold δ.
- **Zero loss in this sub-case. ✓**

**Sub-case: f2 close, f1 far** (Δ(f1,C) > δ, Δ(f2,C) ≤ δ):
- Write f1+γf2 = (f1+γg2) + γe where g2 nearest codeword to f2, e = f2-g2.
- For correlated γ (h_γ = u1+γg2 form): need wt(e1+γe2) ≤ δn.
- Since wt(e1) = Δ(f1,u1)·n > δn and wt(e2) ≤ δn: generic wt(e1+γe2) > δn.
- Cancellation requires aligned error patterns: ≤ O(1) γ values.
- **BUT proving O(1) rigorously requires bounding level-set sizes of φ(x) = -e1(x)/e2(x), which we haven't done.**

### Honest status

| Claim | Status |
|-------|--------|
| ε_ca(C, δ, 2δ) ≤ O(1)/\|F\| | **PROVED** (volume bound for f2-far; triangle for f2-close) |
| ε_ca(C, δ, δ) ≤ O(1)/\|F\| | **NOT PROVED** (f2-close, f1-far sub-case unresolved) |
| ε_mca(C, δ) ≤ O(1)/\|F\| | **PROVED for f2-far; BELIEVED for f2-close** |

### Why option 2 is hard

The fundamental obstacle: when f2 ≈ g2 ∈ RS, the affine line {f1+γf2} ≈ {f1+γg2} is PARALLEL to the code. Distance to RS is approximately CONSTANT along this line. The error γe perturbs this, but bounding the perturbation's effect on list-size requires understanding the error geometry — which is exactly what makes the proximity gap hard in general.

### What IS achievable without new ideas

The loss-δ version ε_ca(C, δ, 2δ) = O(1)/|F| is clean and rigorous. It says:

> If f1+γf2 is δ-close to RS for more than O(1) values of γ, then (f1,f2) is 2δ-close to the interleaved code C^{=2}.

This is a NOVEL proximity gap above Johnson with explicit (though non-zero) proximity loss.
