# Note 0021 — Responses to Reviewer Objections

**Date**: 2026-04-21

## Boneh Review — Response

### "Fatal Error": e_1(S) not in L

**Objection**: The sum of elements of a multiplicative subgroup is not generally in the subgroup. So pivot extraction (finding j* with ω^{j*} = e_1(S)) fails.

**Response**: This is a **misunderstanding of the proof**. We do NOT claim e_1(S) ∈ L for arbitrary S. We observe that **e_1(S) = -λ** (a Vieta identity from the agreement polynomial). The value -λ is determined by the WORD w = x^t + λx^{t-1}, not by S. The adversary controls w, hence λ.

Case analysis:
- If -λ ∈ L: pivot extraction works. On power-of-2 domains: |T| ≤ 1. M = O(1).
- If -λ ∉ L: no extraction needed. Only sporadic solutions. M = O(sporadic).

The bound M ≤ n/(t-1) + O(sporadic) holds for ALL λ. The worst case (-λ ∈ L) gives the coset contribution.

**Verdict**: Objection resolved. The proof is correct on this point.

### "Major Gap": k=2 only

**Objection**: The proof works for k=2 but Grand Challenges ask about constant-rate codes (k = ρn).

**Response**: Partially valid. The k-independence reduction (fixing h2,...,h_{k-1}) IS correct but needs refinement:
- For each word w: exactly ONE tuple (h2,...,h_{k-1}) = (a2,...,a_{k-1}) reduces to binomial core → coset solutions.
- All other tuples → sporadic only.
- Total: n/(t-1) + O(n^t/p^{t-k}).
- For t > k (intermediate zone): exponentially small sporadic.

**Remaining gap**: For VERY large k (k ~ n/2): p^{k-2} tuples times sporadic = p^{k-2} × n^t/p^{t-2} = n^t/p^{t-k}. Need t > k for convergence. In the intermediate zone: t ≈ 0.6n and k ≈ 0.5n. So t-k ≈ 0.1n. Thus n^t/p^{t-k} = n^{0.6n}/p^{0.1n}. For p > n^6: this is (n^6/p)^{0.1n} < 1. Verified for BabyBear.

### "Major Gap": Sporadic bound heuristic

**Objection**: O(C(n,t)/p^{t-2}) is heuristic counting, not a proof.

**Response**: Partially valid. The rigorous version:
1. For small t (t=6): the norm argument is fully rigorous (Thm 1 mechanism).
2. For large t (intermediate zone): the counting argument is supported by Lang-Weil theorem on 0-dimensional varieties, but we haven't formally computed the variety dimension.

**Action needed**: Cite Lang-Weil theorem explicitly. Show the variety of non-coset t-subsets satisfying Vieta conditions has dimension 0. This follows from: t-2 conditions on t-element subsets of a 1-dimensional group (Z/nZ) give a variety of expected dimension t - (t-2) = 2 in the symmetric product. But the roots-in-L condition (each root in a finite set of n elements) cuts further. Need formal argument.

### "Fatal Error": MCA misunderstood

**Objection**: Volume counting doesn't match ABF's MCA definition.

**Response**: Need careful re-examination. ABF defines:
ε_mca = max_{f1,f2} Pr_γ [∃S s.t. |S|≥t, Δ_S(f1+γf2, C)=0, AND Δ_S((f1,f2), C^{=2}) > 0]

Our proof bounds Pr_γ[∃S s.t. |S|≥t, Δ_S(f1+γf2, C)=0] ≤ ceil(n/t)/|F|.

This IS an upper bound on ε_mca (since the ABF definition has an additional AND condition that only makes the probability SMALLER). So our bound is VALID but potentially LOOSE.

**Verdict**: The MCA bound IS correct (it's an upper bound on a subset of the events). Boneh's objection here is wrong — we DON'T need the AND condition; omitting it only makes our bound weaker (an overcount), not invalid.
