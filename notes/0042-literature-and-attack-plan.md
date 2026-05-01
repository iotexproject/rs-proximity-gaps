# Note 0042 — Literature Synthesis & Attack Plan

## Critical literature findings

### 1. BCHKS equivalence (the master reduction)
**CA above Johnson ⟺ list decoding above Johnson for RS.**
If we prove list-size M = O(1) for RS on multiplicative subgroups above Johnson, CA follows via Gao-Cai-Xu-Kan (ePrint 2025/870).

### 2. Folded RS is SOLVED up to capacity
Goyal-Guruswami (2025/2054) + Jeronimo-Liu-Rajpal (arXiv 2601.10047): "curve-decodability" + "line stitching" give optimal proximity gaps for folded RS. Key: they exploit **subspace-design** property, NOT just small list size.

### 3. Nobody uses multiplicative structure
Confirmed across all papers. Everyone treats L generically. Our angle (character sums, cyclic group structure) is unexplored.

### 4. Okamoto (ePrint 2025/1712) claims complete resolution
"Syndrome-space lens" — change of basis to syndrome space. Single author, NOT cited by BCHKS/ABF/anyone. **Must investigate.**

### 5. Key negative: BCHKS Ω(n^{1.99}) lower bound at Johnson
At exactly δ_J: proximity gaps need ≥ Ω(n^{1.99}) exceptions. This is for GENERAL RS (any domain). On multiplicative subgroups: might be different!

## The three most promising attack vectors

### Attack A: Character-sum counting for list decoding

The number of t-subsets I ⊂ Z/nZ with prescribed DFT:

$$N = \frac{1}{p^{n-k}} \sum_{\boldsymbol{\xi}} \prod_j \psi(-\xi_j c_j) \cdot e_t(\phi_{\boldsymbol{\xi}}(0), \ldots, \phi_{\boldsymbol{\xi}}(n-1))$$

where $\phi_{\boldsymbol{\xi}}(i) = \psi(\sum_j \xi_j \omega^{ij})$.

**Main term** (ξ=0): $\binom{n}{t}/p^{n-k}$. For FRI params: exponentially small → M=0 expected.

**Error term**: need $\max_{\xi \neq 0} |e_t(\phi_\xi)| \ll \binom{n}{t}/p^{n-k}$.

**Technical target**: Prove square-root cancellation in $e_t$ of character values on cyclic groups. This is a problem in the Gong-Helleseth tradition (cross-correlation of m-sequences).

### Attack B: Adapt "line stitching" from folded RS

Goyal-Guruswami key idea: replace "small list size" (which fails above Johnson) with "cluster structure" (which works up to capacity). For folded RS: clusters come from Frobenius structure.

**Question**: Can we use the **multiplicative coset structure** of L = ⟨ω⟩ as a substitute for subspace-design?

Key property of L that folded RS lacks: the Galois action Gal(Q(ζ_n)/Q) acts on L. Cosets of subgroups give a hierarchical decomposition. FRI exploits this recursively.

**Concrete idea**: Define "coset-decodability" for RS on multiplicative subgroups. An agreement set S of size t must interact with the coset decomposition in a constrained way (by our coset extraction theorem). This constraint could replace the small-list requirement in the BCIKS reduction.

### Attack C: Investigate Okamoto's syndrome-space lens

ePrint 2025/1712. If correct: game over. If wrong: the failure mode reveals structure.

**Priority**: Read and verify before investing in A or B.

## Decision: execution order

1. **Immediately**: Fetch and analyze Okamoto 2025/1712
2. **If Okamoto fails**: Attack A (character-sum counting) — directly addresses the technical barrier
3. **In parallel**: Attack B (line-stitching adaptation) — the structural approach

## The precise technical problem (for Attack A)

**Conjecture (Character-Sum List-Decoding Bound):**

For RS[F_p, L, k] with L ⊂ F_p* multiplicative subgroup of order n, and t = (1-δ)n with δ_J < δ < 1-ρ:

$$M_\delta(w) \leq \frac{\binom{n}{t}}{p^{n-k}} + O(1)$$

For FRI parameters (p ≥ 2^{31}, n ≤ 2^{24}, ρ ≤ 1/2): the first term is exponentially small, giving M = O(1).

**What's needed to prove**: Bound |e_t(φ_ξ)| for non-trivial ξ. This reduces to a problem about symmetric functions of character values on cyclic groups — a generalization of the power-sum bounds in the Golomb-Gong tradition.
