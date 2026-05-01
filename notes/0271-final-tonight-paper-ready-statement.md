# Note 0271 — FINAL tonight: paper-ready theorem & status

**Date:** 2026-04-30 early AM (after laptop limits hit)
**Status:** Synthesis of all tonight's structural results into a
paper-ready statement for Paper 2 §4.6, with explicit limits and
remaining empirical verifications.

## What we ACTUALLY proved (rigorously)

### Theorem A (Self-Similarity, Note 0267) — UNIVERSAL

For all h, d with d | h, the h-chain restricted to the length-d slice
(parametrized by y_j = x_{j·h/d}, j = 1, …, d-1) equals the d-chain.

**Consequence:** V(I_chain^{(h)}) = ⨆_{d | h} V_d^primitive,
where V_d^primitive is intrinsic to d.

### Theorem B (No length-2 orbits, Note 0266a) — UNIVERSAL

V(I_chain^{(h)}) has no length-2 orbits at any h ≥ 2 even.
*Proof:* slice forces c_{h/2} = x_{h/2} = 0.

### Theorem C (Length-3 orbits, Note 0266b) — UNIVERSAL

V(I_chain^{(h)}) has exactly one length-3 orbit iff 3 | h, with 3
points satisfying x_{2h/3}³ = -1/4, x_{h/3} = x_{2h/3}².

### Theorem D (Length-4 orbits, Note 0266c) — UNIVERSAL

V(I_chain^{(h)}) has at least one length-4 orbit iff 4 | h, with 4
points satisfying a 3-variable polynomial system.

### Theorem E (E_1 ≡ 0 mod chain, Note 0269) — UNIVERSAL

For all d ≥ 2, the endpoint E_1 = 14 V_1 - 3 [z^1] U² satisfies
E_1 = 6 W_0 (x_1 - W_1) = 6 W_0 · c_1 ∈ I_chain.

### Theorem F (Z/h-orbit obstruction, Note 0265) — UNIVERSAL

For Z/h-homogeneous f of degree c: f|_{length-d orbit} ≡ 0 if (h/d) ∤ c.

## Endpoint criterion (corrected, Note 0269)

For h-chain + E_c to close, ALL must hold:
1. **Z/h-divisibility:** (h/d) | c for each d | h with V_d^prim ≠ ∅.
2. **Avoid E_1:** c ≠ h/d for each such d.
3. **Intrinsic non-vanishing:** E_{c·d/h} at d-chain ≠ 0 on V_d^prim.

(1) and (2) are immediate from the orbit theorem and E_1 identity.
(3) is the per-d empirical condition, intrinsic to d (not h).

## What we EMPIRICALLY verified

| Test | char | Result | Status |
|---|---|---|---|
| h=4 + E_2 (=h/2) | any | vdim = 1 | ✓ closes |
| h=8 + E_4 (=h/2) | 11 | vdim = 1 | ✓ closes |
| h=8 + E_2 (=h/4) | 11 | vdim = 5 | ✗ length-4 surv (E_1 trap) |
| h=12 + {E_6, E_8} | 3 | vdim = 1 | ✓ closes |
| h=12 + {E_8, E_9} | 3 | vdim = 73 | ✗ length-12 (6 orbits surv) |
| h=12 + {E_10, E_11} | 3 | vdim = 248 | ✗ multiple lengths surv |
| h=16 + E_8 | 5 | (laptop OOM at 4GB) | TBD via different machine |

## Single-endpoint conjecture at h = 2^k

**Conjecture C268' (refined).** For h = 2^k, h-chain + E_{h/2} closes
IF AND ONLY IF E_{2^(j-1)} at d=2^j chain is non-vanishing on V_{2^j}^prim
for each j = 2, 3, …, k.

**Empirical state:** Verified at j ∈ {2, 3} (d=4, d=8). Pending at j ≥ 4.

**For deployment** (h = 2^k, k = 9, …, 19): each j needs separate
verification. Direct GB infeasible at large k on laptop. **Strategic
alternative:** verify via:
- Modular GB on cluster.
- FGLM transformation (compute over grevlex, transform to lex).
- M2 / Sage / Macaulay2 (different GB engines).

## What this gives Paper 2 §4.6

**Theorem 4.x (paper-ready, conditional).** For h = 2^k, k ≥ 2, and
characteristic ≠ 7, the (3k/2, 2k) Stage 2 closure holds via the
single endpoint E_{h/2}, conditional on intrinsic non-vanishing
verifications at each d = 2^j up to d = h.

This is **a finite mechanical algorithm** for proving closure at any
specific h — not a universal proof, but a constructive algorithm.

For deployment: requires verification at k = 9, …, 19. Each is a
finite computation.

## Open structural questions (for future work)

**Q1:** Is intrinsic non-vanishing of E_{d/2} on V_d^prim always TRUE
for d = 2^k? If yes, single endpoint always works; we've verified k=2, 3.

**Q2:** What's the precise structure of V_d^prim that makes E_{d/2}
non-vanishing? Possible angle: V_d^prim is a SMOOTH 0-dim variety
where E_{d/2} is a "regular function" (no algebraic identity zeroing).

**Q3:** Generalize self-similarity to other "constraint chain" families
beyond (3k/2, 2k). E.g., do all (a, 2k) pencils have similar self-similarity?

## Strategic implications

For prize-readiness:
- Stage 2 closure for (3k/2, 2k) at deployment fields: STRUCTURALLY
  REDUCED to per-d empirical verifications.
- d ≤ 16 verified (using full Stage 2 endpoints, not single).
- d = 32, 64, ..., 2^19 require larger-machine verification.

For Paper 2 OP A1: PARTIALLY closed via this framework. The
"per-deployment-h" verification is a finite mechanical task.

## Files

- Notes 0265-0270: structural theorems and prior synthesis.
- Note 0271: this final synthesis.
- All scripts in `notes/scripts/g3_*.py`.

## Tonight's contributions summary (commit history)

- 0265: Z/h-orbit obstruction.
- 0266: orbit existence at small d (no length-2; length-3 iff 3|h; length-4 iff 4|h).
- 0267: Chain Self-Similarity.
- 0268: single-endpoint conjecture at h=2^k (later refined).
- 0269: E_1 ≡ 0 mod chain identity.
- 0270: synthesis with reduced empirical condition.
- 0271: this — paper-ready statement with explicit limits.

7 new notes, ~1500 lines, plus empirical scripts. The structural framework
is SUBSTANTIALLY MORE rigorous than at the start of tonight.
