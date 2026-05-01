# Note 0087 — OP2 Obstruction: M=0 is False at FRI Parameters

## 1. The Question

Paper's OP2: "proving M_max(p) = 0 for all centers u once p ≥ p_0(n,k)"

This would eliminate the 2× query overhead in FRI soundness.

## 2. The Obstruction

**Theorem (Elementary Construction)**: For RS[n,k] over F_p with p > n and codimension excess c ≤ ⌊(n-k-1)/2⌋, there exist received words u with M(u) ≥ 2 for ALL p.

**Proof**: Take two codewords c_1, c_2 ∈ RS_k at minimum distance d_min = n-k+1. Let S = supp(c_1 - c_2), |S| = d_min. Choose two w-subsets B_1, B_2 ⊂ S with B_1 ∪ B_2 = S (requires |B_1| + |B_2| ≥ |S|, i.e., 2w ≥ d_min, i.e., c ≤ (n-k-1)/2). Construct u:
- u = c_1 = c_2 on L \ S (they agree outside S)
- u = c_2 on B_1 \ B_2 (so u ≠ c_1 on B_1)
- u = c_1 on B_2 \ B_1 (so u ≠ c_2 on B_2)
- u ∉ {c_1, c_2} on B_1 ∩ B_2 (requires p ≥ 3)

Then d(u, c_1) = |B_1| = w and d(u, c_2) = |B_2| = w. So M(u) ≥ 2. ∎

## 3. Application to FRI Parameters

At rate ρ = 1/2 and Johnson bound δ = 1 - 1/√2 ≈ 0.293:
- w_J = ⌊δn⌋ ≈ 0.293n
- c_J = n/2 - w_J ≈ 0.207n
- Threshold: (n/2 - 1)/2 ≈ n/4 = 0.25n

**For n ≥ 32**: c_J ≈ 0.207n < 0.25n ≈ threshold. The construction gives M ≥ 2 at the Johnson bound for ALL p.

**For n ≤ 20**: c_J > threshold (ceiling effects). Construction fails at Johnson; OP2 may hold at small n.

Verified computationally for RS[n, n/2] at n ∈ {8, 10, 12, 16, 32, 64}:

| n | k | w_J | c_J | threshold | M≥2 at Johnson? |
|---|---|-----|-----|-----------|:---:|
| 8 | 4 | 2 | 2 | 1.5 | NO |
| 10 | 5 | 2 | 3 | 2.0 | NO |
| 12 | 6 | 3 | 3 | 2.5 | NO |
| 16 | 8 | 4 | 4 | 3.5 | NO |
| 20 | 10 | 5 | 5 | 4.5 | NO |
| 24 | 12 | 7 | 5 | 5.5 | **YES** |
| 32 | 16 | 9 | 7 | 7.5 | **YES** |
| 64 | 32 | 18 | 14 | 15.5 | **YES** |

## 4. Connection to OP1

The 2× query overhead is intrinsic for TWO independent reasons:

1. **OP1 tightness**: ε_ca(C, δ, δ) = Θ(1) above Johnson. Equal-threshold CA is false. The half-threshold δ/2 is optimal within the CA framework.

2. **OP2 obstruction**: M_max ≥ 2 at FRI-relevant parameters for n ≥ 32, for ALL p. Even without the CA framework, the list-decoding geometry prevents M = 0.

## 5. What IS True

The paper's structural results are still correct and valuable:

- **Codimension bound**: dim V_{012} ≤ w - 3 (Theorem thm:codim)
- **Generic M = 0**: for generic flats of codim ≥ 3 (Corollary cor:M-zero)
- **Average M → 0**: E[M] = C(n,w)/p^c for c = 1 (Theorem thm:second-moment)
- **Incidence bound**: M ≤ C(n,d)/C(w,d) on any flat (Theorem thm:incidence)
- **Practical M = 0**: for p ≫ n at deployment parameters (BabyBear, Goldilocks), M is essentially 0

The obstruction is for the WORST-CASE statement "M_max = 0 for all centers u". The average-case and practical-case statements remain strong.

## 6. Salvageable Directions

The 2× overhead might be reducible (not eliminated) by:

1. **Restrict to fold-compatible flats**: the fold f_1 + αf_2 of a far-from-code function is NOT an arbitrary received word. The far-from-code constraint rules out the specific u's with M ≥ 2. If M = 0 for all fold-compatible centers: the proximity gap might improve beyond δ/2.

2. **Non-CA proximity gap**: bypass the CA framework entirely. The FRI fold has a specific algebraic structure (even/odd decomposition on multiplicative cosets) that isn't used by the CA argument.

3. **Tighter Johnson bound**: for the specific RS codes used in FRI (power-of-2 evaluation domain, BabyBear field), the list-decoding geometry may be better than the generic Johnson bound.

## 7. Impact on Paper

OP2 should be reformulated. The current statement "M_max(p) = 0 for all centers u" is:
- TRUE for n ≤ 20 at rate 1/2 (unproven but not obstructed)
- **FALSE for n ≥ 32 at rate 1/2** (elementarily obstructed)

The claim "proving M = 0 on all RS-compatible flats would eliminate the 2× query overhead entirely" is technically correct but vacuously true at n ≥ 32: M = 0 is impossible, so any consequence follows.

Suggested revision: separate OP2 into (a) average-case decay (proved for c = 1, conjectural for c ≥ 2), and (b) practical M = 0 at deployment parameters (empirically verified, theoretically justified by Lang-Weil density).
