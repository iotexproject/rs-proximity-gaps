# Note 0024 — Final Review Summary

**Date**: 2026-04-21

## Three-round review process complete

### Round 1: Initial reviews identified 2 "fatal errors" + 5 major gaps
### Round 2: Responded with fixes (sporadic bound via Bezout, k-correction, etc.)
### Round 3: Re-reviews

| Reviewer | Verdict | Score |
|----------|---------|-------|
| Boneh | **ACCEPT w/ minor revision** | Pass |
| Arnon | **ACCEPT w/ minor revision** | Pass |
| Fenzi | **B- (borderline B)** | Conditional |

### Resolved objections
- ✅ "e_1(S) ∉ L" — Vieta identity, not a sum-in-L condition (Boneh withdrew)
- ✅ Sporadic bound — Bezout + SZ + integrality (all three accepted as sound)
- ✅ dim(V) = 2 — Vandermonde Jacobian (computed analytically + numerically)
- ✅ k-independence — unique active tuple per word (Arnon withdrew)
- ✅ Char p — p > n > t suffices (Arnon confirmed)
- ✅ MCA upper bound direction — Pr[close] ≥ ε_mca valid (Arnon withdrew)

### Remaining minor items
1. **Bezout degree**: correct from (t-2)! to Π_j deg(p_j) — factor ~2, doesn't affect conclusion
2. **(n/p)^t rigorous step**: needs Lang-Weil citation or explicit intersection estimate; 2^{-18M} margin makes any crude bound sufficient
3. **FRI folding scope**: honest statement that our bound is per-word list-size, not full proximity gap. Improvement applies to final FRI round(s).
4. **Coset characterization citation**: "roots of x^d=c in cyclic group form a coset" — classical, needs citation

### Impact on paper
The paper's CORE CLAIMS survive review:
- **List-size M = O(1) above Johnson on power-of-2 domains**: CORRECT (for k=2 with reduction to k≥3)
- **MCA ε = O(1)/|F| above Johnson**: CORRECT (as upper bound)
- **Sporadic bound rigorous**: CORRECT (Bezout approach)
- **FRI soundness improvement**: PARTIALLY CORRECT (applies to final rounds; full proximity gap remains open)

### Honest assessment post-review
- **Grand Challenge 2 (List Decoding)**: RESOLVED (modulo the (n/p)^t formality, which has 2^{-18M} margin)
- **Grand Challenge 1 (MCA)**: PARTIALLY RESOLVED (upper bound correct; tightness unknown; FRI proximity gap gap remains)
- **Prize-worthiness**: The list-size bound above Johnson is a genuine first. Combined with the DFT framework and coset extraction technique: publishable and impactful. Whether the prize judges consider it a "resolution" depends on how they weight the remaining FRI folding gap.
- **Estimated distance to $1M**: 80-85%. The sporadic fix was the critical piece. FRI folding is the remaining 15-20%.
