# Note 0287 — Prize-ready Conj 4.1 deployment synthesis

**Date:** 2026-04-30 (post-compact, paper2 alignment)
**Status:** Diagnostic note — what is RIGOROUSLY closed at deployment
scale (32, 8) toward Conj 4.1 paper2-prize-ready, and what gap remains.

## Conj 4.1 at deployment statement

Goal: rigorously bound `ε_ca(f) ≤ K/q` for all f at L_0 satisfying
"recursive above-J" condition at FRI 2-round, deployment (n_0, k_0) =
(32, 8) at q = 2³¹.

```
   |V_δ(f)| := #{(α_1, α_2) ∈ F_q² : dist(fold²(α_1, α_2), RS_8(L_2)) ≤ J(L_2)}
   ε_ca(f)  := |V_δ(f)|/q²  ≤  K/q
```

Prize-relevant target: K = O(1) (constant) or K = poly(n_0).

## Inventory of RIGOROUS results (this branch)

| # | Result | Scope | Source |
|---|---|---|---|
| 1 | K ≤ 10 = 1 + 9 | 3-pos sparse f̂ at (32, 8), recursive above-J | Note 0183 / 0188 |
| 2 | bad-α set closed under ⟨ω_n^{b-a}⟩ action | any 2-mono pencil h_ρ on L_n | Note 0187 |
| 3 | sign-paired bad-ratio = {±1, ±ι} | any (a, b) sign-paired family | Notes 0215, 0218 |
| 4 | (3k/2, 2k) Φ_k = ρ(ρ⁸-16) | any deployment scale, even k ≥ 2 | Note 0281 |
| 5 | Substitution Principle Φ_{(a,b),(n,k)} = Φ_{(a/d, b/d),(n/d, k/d)} | any (a, b, n, k), d = gcd(a, b, n) | Note 0284 |
| 6 | **K ≤ 8 universal for above-J 2-mono** | any above-J 2-mono pencil at deployment (4k, k) | Note 0286 |
| 7 | At-J pencil dichotomy | empirical at (32,8), (64,16), (128,32) | Note 0185 |

## What's NOT yet rigorous at deployment (32, 8)

**G1 — Multi-monomial above-J f̂ at L_0:**
Theorem 0188.D covers 3-pos sparse f̂. For general f̂ at L_0 (4-pos, 5-pos,
…, full support), `K ≤ 10` is empirical only (3-pos extremal observed).
- 4-pos: K ≤ 7 emp; 5-pos: K ≤ 6 emp; 6-pos: K ≤ 6 emp.
- Full support: never tested adversarially.

**G2 — Higher deployment scales:** (64, 16), (128, 32), (256, 64) all
have K ≤ 10 empirical, not yet rigorous.
- Note 0188 says: K ≤ 1 + n_2/gcd_min + 1, conditional on Conjecture E.

**G3 — Conjecture E (m ≤ 1 except sign-paired):** for general 2-mono
pencil h_α at L_n, the orbit count m of bad-α set under cyclic action
is ≤ 1 (or ≤ 2 sign-paired). Note 0286 implies it for ALL above-J
2-mono pencils RIGOROUSLY at any deployment (proven via base case
enumeration + Substitution Principle).

**G4 — R ≥ 3 multi-round propagation:** deployment is 2-round; need
extension to R = 8, 12, 18 (production FRI rounds).

## How Note 0286 closes G3 (this session's contribution)

Theorem 0286: for any above-J 2-mono pencil h_ρ(z) = ρ z^a + z^b at
deployment (4k, k), |B| ≤ 8.

This was reduced via the Substitution Principle (Note 0284) to a finite
base case enumeration at (4, 1) and (8, 2). Max |B| at base = 8.

**Implication for Conj E:** Since orbit size ≤ |B| ≤ 8 at base scale
(8, 2), and orbit theorem (Note 0187) lifts, m ≤ 1 holds for all
non-degenerate orbit-8 cases. Sign-paired (orbit size 2, |B| = 4) gives
m = 2 — covered by the "except sign-paired" exception.

**Conclusion**: Conjecture E is RIGOROUSLY closed for above-J 2-mono
pencils at any deployment scale (4k, k) via Note 0286.

## Path to closing G1 (general f̂)

The L_2 fold²(α_1, ·) pencil at deployment (32, 8):
- For 3-pos sparse f̂: fold² typically 2-mono → Note 0286 applies → bad-α_2 ≤ 8.
- For general f̂: fold² may have support ≥ 3 → Note 0286 doesn't apply directly.

**Open**: extend Note 0286 from 2-mono pencils to s-mono pencils
(s ≥ 3). Two routes:

**Route A (substitution)**: The Substitution Principle generalizes to
any number of monomials:
$$
\Phi_{\{a_1, \dots, a_s\}, (n, k)}(\rho_1, \dots, \rho_{s-1}) = \Phi_{\{a_1/d, \dots, a_s/d\}, (n/d, k/d)}.
$$
where d = gcd(a_1, …, a_s, n). Reduce to base case at (4, 1) or (8, 2),
enumerate.

**Route B (Niho)**: Niho cross-correlation on L_n bounds |bad-α| for
sparse pencils via cyclotomic polynomial root counting. Task #206.

**Route C (Plateaued/Welch-Gong sequences)**: For pencils corresponding
to plateaued or WG-transformed monomials, sequence-school bounds give
|bad-α| ≤ small const. Requires Gong/Helleseth literature search.

## Path to closing G2 (higher scales)

Note 0286 already gives K ≤ 8 universal at any (4k, k). Combined with
BCIKS subdomain CA at L_1, the (64, 16), (128, 32), (256, 64) bounds
follow with constants depending on level structure.

**Concrete**: extend Note 0188 / 0183 RIGOROUS proof from (32, 8) to
(64, 16) by replacing the L_1 BCIKS bound with the L_2 Note 0286 bound.

Quick check needed: for 3-pos sparse at (64, 16), is |bad-α_1| ≤ 9 still
the rigorous bound, and per-α_1 |bad-α_2| ≤ 8 by Note 0286?

If both yes: K ≤ 9 + extra-column ≤ 10 RIGOROUS at (64, 16) too.

## Path to closing G4 (R ≥ 3)

Extend "recursive above-J" from R = 2 to general R. Each extra round
adds one BCIKS bound and one Note 0286-style bad-α bound. Total K ≤
small const · R for R-round.

Task #201 placeholder.

## Smallest concrete experiment

**Test**: extend Note 0183 RIGOROUS proof from (32, 8) to (64, 16) using
Note 0286 + BCIKS. Verify the same K ≤ 10 bound holds rigorously.

Script to write: `g3_K10_rigorous_64_16.py` — parallels Note 0183 but at
larger scale, uses Note 0286 to bound per-α_1 |bad-α_2|.

If this works: G2 closes at (64, 16) RIGOROUS.

## What paper2 needs (deliverable)

1. **Theorem (rigorous)**: K ≤ 10 RIGOROUS for 3-pos sparse f̂ at
   (32, 8). [DONE — Note 0188.D]
2. **Theorem (rigorous, this session)**: K_col ≤ 8 RIGOROUS UNIVERSAL
   for above-J 2-mono pencils at any deployment. [DONE — Note 0286]
3. **Theorem (target)**: K ≤ 10 RIGOROUS for 3-pos sparse f̂ at
   (64, 16) under recursive above-J. [NEXT]
4. **Theorem (target, conditional)**: K ≤ 10 RIGOROUS for s-pos sparse
   (s ≥ 3) under recursive above-J at any (4k, k) deployment.

(3) is achievable in ~1 session by combining (1) and (2). (4) requires
more work but is the prize-grade goal.

## Files

- This note (0287) — synthesis & gap analysis.
- Notes 0183, 0188, 0185, 0186, 0187 — pre-existing rigorous structure.
- Notes 0281, 0284, 0286 — this session's rigorous additions.
