# Note 0335 — Synthesis after absorbing codex Notes 0327-0334 (issue-396 → fri-2round-tightness)

**Date:** 2026-05-01 evening
**Status:** SUMMARY of cross-branch absorption + revised Conj 4.1 progress estimate.

## What was absorbed

Cherry-picked 8 codex commits from `origin/issue-396` → fri-2round-tightness:

| Commit | Note | Content |
|---|---|---|
| 74383ec | 0327 | rank-collapse pattern audit (q=193): 22M candidates split into zero-row (22M) + one-sided (2245) |
| 32faf37 | 0328 | GB saturation cert at q=193: sat(I, α₁, U, V) = ⟨1⟩ (RIGOROUS ideal-theoretic) |
| 5056e52 | 0329 | Multi-prime GB saturation at 7 primes: ⟨1⟩ uniformly across all 7 primes |
| 714b55b | 0330 | Side-purity mechanism: mixed-support no-full forces u=0 or v=0 |
| 2b5bfea | 0331 | Monomial tail obstruction: x^e tail on no-full S |
| dcccdef | 0332 | **Cyclotomic tail lemma** over Z[ζ_16]: tail_S(x^e) ≠ 0 for k ≤ e < 4k, base k=4 RIGOROUS |
| b6ead09 | 0333 | **Synthesis: Theorem 0333.A** — legal C(48,3) panel no primitive no-full (RIGOROUS) |
| eaa849e | 0334 | Scale-lift target: general dyadic tail lemma at k=2^j (OPEN) |

## Path (c) status after absorption

**RIGOROUS** at base scale (L_2 = (16,4), k=4):

> Theorem 0333.A: In the legal `(64,16) → L_2=(16,4)` strict-above-Johnson C(48,3) panel, no primitive rank-2 no-full saturated component exists. Equivalently: any no-full saturated candidate has α₁=0 (zero-row) or is one-sided (u=0 or v=0).

Mechanism (per Notes 0330-0332):
1. **Side-purity**: mixed-support no-full forces one quarter-block side to be empty residually.
2. **Singleton residual**: the empty side leaves a single x^e residual monomial.
3. **Cyclotomic tail**: for k ≤ e < 4k and no-full 8-subset S in L_2, tail_S(x^e) ≠ 0 (proven over Z[ζ_16]).

Hence the singleton residual cannot lie in RS_4(S), so no saturated no-full primitive component.

**OPEN** at scale-lift (Note 0334):

> General dyadic tail lemma: for n = 4k cyclic group, no-full 2k-subset S, and k ≤ e < 4k:
> $\text{tail}_S(x^e) \neq 0$.

Base case k=4 = Note 0332 (RIGOROUS via finite enumeration over Z[ζ_16]). General k = 2^j: needs block-interpolation normal form proof (Note 0334 sets up the algebraic identity).

## My #419 contribution (today)

**Multi-prime, multi-panel empirical certification** (notes 0317, 0318):

| Panel | × Primes (≥ 97) | Combinations | primitive |
|---|---|---|---|
| C(48,3) | 7 (codex) | 121,072 | 0 |
| C(64,3) | 12 | 499,968 | 0 |
| C(80,3) | 8 | 657,280 | 0 |
| C(96,3) | 8 | 1,143,040 | 0 |
| C(112,3) | 8 | 1,823,360 | 0 |
| **TOTAL** | | **4,244,720** | **0** |

This empirical strength PRECEDED codex's GB saturation cert (0328-0329) and is consistent with it — confirmed at much larger panels.

Plus q=17 unique bad prime: 64 primitive CEs (q-1 = 16 = |μ_16| collapse).

## Layer 3 progress (revised after absorption)

Before absorption: **L3 ≈ 60%** (empirical strong, structural open).

After absorption: **L3 ≈ 80%** (base panel closed RIGOROUSLY by codex; scale-lift open).

Remaining for L3:
- ~15%: prove general dyadic tail lemma at k = 2^j (Note 0334 target). Paper-grade, weeks.
- ~5%: deployment-scale empirical extension if needed.

## Layer 2 (Q1 universal) — still bottleneck

Still ~38%:
- ✅ d=4, 8, 12 RIGOROUS
- 🟡 d=16 Singular GB pending (160+ min)
- 🟡 d ∈ {16-64} empirical via Newton sampler
- ⚠️ d ≥ 512 sampler basin shrinks (Note 0310)
- Universal structural proof: paper-grade, weeks-months

## Combined Conj 4.1 closure

L1 = 95%, L2 = 38%, L3 = 80%

**min(L1, L2, L3) = 38%** — L2 still bottleneck

**Weighted (Bayesian): 0.1×95% + 0.45×38% + 0.45×80% = 62.6%**

## Move-the-needle priorities (revised)

1. **Q1@d=16 RIGOROUS via Singular** — pending; if completes, L2 → ~50%.
2. **Q1 universal structural proof** — paper-grade, needs sequence-school expert (Gong/Helleseth/Tang). L2 → 100% if closed.
3. **Note 0334 scale-lift proof** — paper-grade structural; L3 → 100% if closed.
4. **Studio above-J 5-mono cases** (#212 cluster, 17+ hours) — clarifies sparse-worst direction.

L2 + L3 universal proofs are SYMMETRIC paper-grade obstacles. Either alone moves the needle a lot; both together = solo prize-grade.

## Files referenced

- Notes 0327-0334 (codex, absorbed via cherry-pick)
- Notes 0317, 0318 (my empirical)
- Note 0315 (Q1 F(0) RETRACTED — Theorem 0315.4 invalid)
- Note 0316 (Q1 direct vdim attack pivot)
- Issue #419 master, #410 (Q1 universal)
