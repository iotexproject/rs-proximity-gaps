# Note 0168 — q-scaling of |V_δ|/q² for the rank-3 sparse stratum

**Date:** 2026-04-28
**Goal:** Lock G3 work onto **#343 (positive OP1 via character sums)** and
**#344 (FRI 2× tightness)** — the two ROI-highest issues in roadmap #368.
This note delivers the empirical bedrock for that decision.

---

## Roadmap context (#368)

OP1 (zero-loss CA above Johnson) splits:

```
   POSITIVE                       NEGATIVE
   #343 character sums            #344 FRI 2× tight
   on L = ⟨ω⟩  ←——— our exclusive sequence-school asset
```

**#322 (Berlekamp overconstrained, P0+) is NOT our track** — handed off.
Our focus is locked on #343 + #344.

The reviewed-fri-2round-tightness branch already broke the strict 2q
intermediate inequality at rank-2 K=2 low-overlap (Note 0114, q=97). But
P_avg < 1−δ stayed safe there. So the live #344 question is: does there
exist a strict-above-J f for which **|V_δ|/q² stays bounded above poly(n)/q**
as q → ∞? If yes — prize-level negative for OP1.

---

## Experiment

`notes/scripts/g3_pacc_qscaling.py`. For each of the 24 count=9 supports
(rank-3, generic — the stratum the reviewed branch did NOT analyze) at
(n_0, k_0) = (32, 8), with deterministic seeded coefs, sweep across primes
q ∈ {97, 193, 257, 449, 577, 769, 1153}, all ≡ 1 mod 32. Per (sup, q):

- check above-J at L_0
- count_α₁ at L_1 (d_1 ≤ w_J(L_1) = 8)
- |V_δ| = #{(α_1, α_2) ∈ F_q² : d_2 ≤ w_J(L_2) = 4} via analytic Lagrange
  match δ_e + α_2 · δ_o = 0
- |V_δ|/q² = ε_ca-relevant ratio

Runtime: 287 lines, ~75s total local.

## Result

**Every one of 24 × 7 = 168 (support, q) cases is strict-above-J** with
count_α₁ = 9 (occasionally 8). |V_δ| splits cleanly into two flavors per
mod-4 class of L_0 support:

| mod-4 class | |V_δ| at q | |V_δ|/q² |
|---|---|---|
| ⊂ {0, 1} | **count_α₁ · q** = 9q exactly | 9/q |
| ⊂ {2, 3} | **count_α₁ · q + (q − count_α₁)** = 10q − 9 | 10/q − 9/q² |

Examples:

| q | mod4⊂{0,1} V_δ | mod4⊂{2,3} V_δ | max V_δ/q² |
|---|---|---|---|
| 97 | 873 = 9·97 | 961 = 10·97 − 9 | 0.1021 |
| 193 | 1737 = 9·193 | 1921 = 10·193 − 9 | 0.0516 |
| 257 | 2313 = 9·257 | 2561 = 10·257 − 9 | 0.0388 |
| 449 | 4041 = 9·449 | 4481 = 10·449 − 9 | 0.0222 |
| 577 | 5193 = 9·577 | 5761 = 10·577 − 9 | 0.0173 |
| 769 | 6921 = 9·769 | 7681 = 10·769 − 9 | 0.0130 |
| 1153 | 10377 = 9·1153 | 11521 = 10·1153 − 9 | 0.0087 |

**Universal bound**: |V_δ| ≤ 10·q − 9 for all 24 supports, all 7 primes.
Translating: |V_δ|/q² ≤ 10/q ⟶ 0 as q → ∞. **POLY DECAY. Zero-loss FRI
2-round upheld for this stratum.**

## Interpretation

### For #344 (negative)

**This stratum is NOT a counterexample.** |V_δ|/q² decays as 10/q. Combined
with reviewed-branch's rank-2 K=2 low-overlap data at q=97 (|V_δ|/q² ≈ 0.030
there), there's no observed strict-above-J f at FRI 2-round (32,8) with
|V_δ|/q² staying bounded as q grows. Empirical zero-loss holds. **#344
negative is not breakable via 3-pos sparse rank-3.**

To break #344 we'd need a denser / structurally different witness. Candidates
to test next:
- 4-pos / 5-pos sparse (rank up to 4)
- the reviewed branch's rank-2 K=2 low-overlap construction lifted to q=1153
- strict above-J at (64, 16) deployment-scale params

### For #343 (positive) — the structure to target

The empirical structure is clean enough to **state as a theorem to prove**:

**Conjecture #168.A** (count_α₁ + 1 bound). For every strict above-J f at
(n_0, k_0) and every R-round chain,
```
   |V_δ| ≤ (count_α₁(f) + 1) · q
```
where count_α₁(f) is the level-1 bad set size, **provided** rank ≤ 3 (3-pos
sparse stratum).

**Conjecture #168.B** (mod-4 dichotomy). The "+1" extra column appears iff
supp(f) mod 4 lies in the **anti-symmetric class** {2, 3} (forcing a single
universal α_2 = 0 column) and is absent for the symmetric class {0, 1}.

If #168.A holds, then since count_α₁ ≤ n_1 − s + 1 = 9 (BCIKS subdomain CA
trivial direction), we get
```
  |V_δ|/q² ≤ (n_1 − s + 1 + 1) · 1/q = (n_1 − s + 2)/q = poly(n)/q
```
i.e. **zero-loss CA up to Johnson at FRI 2-round, with explicit constant
n_1 − s + 2 = 10**. This is a **substantial improvement over the universal
[BCHKS25] O(n^5/q) bound**.

The proof strategy for #343:
1. **Level-1 bound** (BCIKS subdomain CA, established): count_α₁ ≤ n_1 − s + 1.
2. **Lift bound** (PR #373 affine-cover): for each level-1-bad α_1, the ENTIRE
   α_2 fiber {α_2 ∈ F_q : (α_1, α_2) ∈ V_δ} can saturate q. So the
   level-1-bad slice contributes count_α₁ · q.
3. **Residual bound** (NEW, this is the #343 character-sum target): for the
   level-1-good slice {α_1 : d_1(fold_{α_1}, RS) > w_J(L_1)}, the level-2-bad
   set {(α_1, α_2) : d_2 ≤ w_J(L_2)} has size ≤ q (= one full column).

Step 3 is the open lemma. The mod-4 dichotomy says: it's exactly the
"α_2 = 0 column" giving level-2 agreement when supp(f) mod 4 ⊂ {2, 3} (the
fold-2 inherits sign-flip symmetry from the mod-4 class). For mod-4 ⊂ {0, 1}
the residual is empty.

**This is character-sum-tractable**: the residual is the count of α_1 such
that fold_{α_1, 0} has high agreement with RS_{k_2}. fold_{α_1, 0} = even part
of fold_{α_1} on L_2. Setting α_2 = 0 makes the dependence on α_1 affine, and
the agreement count becomes a Niho-cross-correlation evaluated on L_2.

## Prior-art reality check (lock-in)

| Item | Status | Source |
|---|---|---|
| count_α₁ ≤ n_1 − s + 1 = 9 | **known** | [BCIKS20] subdomain CA trivial direction |
| ε_ca ≤ O(n^5/q) up to Johnson | **known** | [BCHKS25] εmca up to Johnson |
| **|V_δ| ≤ (count_α₁ + 1) · q for rank-3 sparse @ FRI 2-round** | **NEW** | this note (Conj #168.A) |
| **mod-4 anti-symmetric class adds +1 column** | **NEW** | this note (Conj #168.B) |
| character-sum proof of step 3 residual bound | **OPEN** | #343 |

The novelty is the **explicit constant** (n_1 − s + 2 = 10) and the
**character-sum-tractable form** (mod-4 dichotomy reduces step 3 to a
Niho-cross-correlation on L_2).

## What I will do next (#343/#344-priortized)

1. **Test Conjecture #168.A on (64, 16)** — does the same |V_δ| ≤
   (count_α₁ + 1) · q hold at deployment scale? Need to find above-J f at
   (64, 16) first.

2. **Test #344 negative on rank-2 K=2 low-overlap** — lift reviewed branch's
   q=97 counterexample to multiple q, see if |V_δ|/q stays at ~3 (their
   value) → another decaying ratio confirming zero-loss; or if it grows →
   #344 negative.

3. **Set up character-sum framework for step 3** — write the Niho
   cross-correlation expression for fold_{α_1, 0} agreement count on L_2.
   This is the entry to #343.

## Files

- `notes/scripts/g3_pacc_qscaling.py` — the experiment.
- `notes/scripts/g3_pacc_qscaling.output.txt` — full table (287 lines).

## Tasks affected

- [#165 in progress] #344-decisive q-scaling — DONE for rank-3 sparse, not
  a counterexample. Move to (64, 16) and rank-2 next.
- [#166 pending] #343 character-sum framework — kickoff with mod-4
  dichotomy + α_2 = 0 column analysis.
- [closed-as-task] #149 cyclotomic generalization, #142 K=2/dense cluster,
  #151 CS-comparison, #154 D' refinement, #153 Conjecture E. Marked for
  removal — not on #343/#344 critical path.
