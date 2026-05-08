# Note 0415 — Overnight session summary (2026-05-02 → 2026-05-03)

**Date:** 2026-05-02 late night
**Branch:** `main`
**Goal at start of session**: continue Tier 1c Path C remaining 35 pairs at $|A|=4$ + start Tier 2 (side-(3,1)) attack.

---

## TL;DR

* **Tier 1c at $L_2 = (16, 4)$** is **substantially complete**.
* **|A|=4 stratum (5760 S × 36 pairs)**: ALL 36 (r, r') pairs are FIELD-UNIFORM at every prime $q \equiv 1 \pmod{16}$.
* **|A|=6 stratum (1280 S)**: FIELD-UNIFORM via Z[ω_8] complete-homogeneous-symmetric-polynomial argument.
* **|A| ∈ {0, 2} strata (3840 S)**: multi-prime empirical at 33 primes $q \in [97, 1889]$ (and 0 anomalies at q=17 |A|=2; q=17 |A|=0 = the known small-prime degeneracy excluded by paper2 Q_min=97).
* **Tier 2 framing**: Note 0414 documents the 4 candidate Mechanisms (A-D) for side-(3,1)/(1,3) closure.

---

## Notes written this session

| Note | Subject | Pages of math content |
|---|---|---|
| 0407 | (4, 7), (6, 5) field-uniform via polynomial-degree kill | 1 |
| 0408 | (4, 9) field-uniform via Vieta + Z[ω_16] norms | 1 |
| 0409 | (8, 5) field-uniform via Vieta (q=17 only candidate) | 1 |
| 0410 | All 11 easy pairs at |A|=4 field-uniform (batch) | 1 |
| 0411 | All 25 hard pairs at |A|=4 field-uniform via 2-minor framework | 1 |
| 0412 | |A|=6 stratum field-uniform via h_n in Z[ω_8] | 1 |
| 0413 | |A|=0/2 multi-prime empirical (34 primes ≤ 2000) | 1 |
| 0414 | Tier 2 framing — side-(3,1) Mechanisms A-D | 1 |
| 0415 | This summary | — |

**Total**: 9 new notes.

## Scripts written this session

| Script | Purpose |
|---|---|
| `issue419_pathC_easy_polynomial_kill.py` | Classifies (r,r') pairs by kill-poly degree |
| `issue419_pathC_4_9_vieta_Zomega.py` | (4,9) Vieta constraints in Z[ω_16] |
| `issue419_pathC_constraint_norms.py` | Integer Galois norms of constraints |
| `issue419_pathC_8_5_vieta_Zomega.py` | (8,5) Vieta constraints |
| `issue419_pathC_easy_unified.py` | Batch check for 8 easy pairs |
| `issue419_pathC_hard_unified.py` | Batch check for 25 hard pairs (2-minor) |
| `issue419_pathC_A6_h_nonzero.py` | |A|=6 h_n nonzero in Z[ω_8] |
| `issue419_pathC_A0_minor_check.py` | |A|=0 strict 6×6 minor check (slow) |
| `issue419_A4_full_compatibility_multi_prime.py` | (Initial WIP, replaced) |
| `issue419_A0_A2_multi_prime_correct.py` | Multi-prime empirical |

**Total**: 10 new scripts.

## Commits

11+ git commits (5c91ecb → 4b031d2), all pushed to origin/main.

---

## Key technical breakthroughs

1. **Polynomial-degree kill** (Note 0407): for pairs where the kill polynomial
   has degree < 4, no 4 distinct $u_c \in \mu_{16}$ can be roots → instant
   field-uniform closure. Applies to (4,5), (4,7), (6,5), (6,7).

2. **Vieta-on-kill-polynomial framework** (Note 0408): for higher-degree
   pairs with $X$ or $\tilde Y_0$ constant, polynomial division of the kill
   polynomial by $P_4(u) = \prod (u - u_c)$ yields 3 effective constraints
   in $\mathbb{Z}[\omega_{16}]$. Combined with norm bounds: bad primes ≤ max|N| +
   empirical check at remaining primes.

3. **Bilinear minor framework for hard pairs** (Note 0411): rank-2 condition
   on $4 \times 2$ matrix $[A_i, B_i]$ where $A_i = $ rem of $X(u^2)$ mod $P_4$,
   $B_i = $ rem of $u \tilde Y_0(u^2)$ mod $P_4$. 6 minors $A_i B_j - A_j B_i$
   in $\mathbb{Z}[\omega_{16}]$ — at least one must be nonzero in $\mathbb{F}_q$.

4. **|A|=6 sub-lemma generalization** (Note 0412): the (D-P) y²-coef equals
   $h_{r/2-2}(\zeta_1, \zeta_2, \zeta_3)$ in 3 σ-orbit reps. Verified nonzero
   in $\mathbb{Z}[\omega_8]$ for all 56 unordered triples of distinct 8th roots,
   except 8 "all-even" or "all-odd" triples whose σ-symmetric closure already
   contains a full quadrant of $\mathbb{Z}/16$ (excluded by no-full).

5. **Multi-prime empirical (Note 0413)**: extended Notes 0401/0402 verifications
   from 3 to 34 primes ≡ 1 mod 16 in [17, 2000]. 0 would-be primitives at all
   q ≥ 97; q=17 has 32 |A|=0 anomalies (matching paper2 Q_min=97 exclusion).

---

## Remaining gaps

| Gap | Status | Effort |
|---|---|---|
| Strict Z[ω_16] for |A|=0 | In progress (running in background) | ~30-60 min |
| Strict Z[ω_16] for |A|=2 | Not started; ~3-4h optimized Python compute | ~4 hours |
| Tier 2 side-(3,1) Mechanism B verification | Framing only (Note 0414) | ~1-2 days |
| Tier 2 side-(3,1) full structural proof | Not started | ~weeks |
| Tier 1b scale-lift to L_2 ∈ {(32,8), ...} for |A|<n_2/2 strata | Empirical via Note 0403/0404; field-uniform extension via same Z[ω_*] framework | ~1-2 days |

---

## Strategic position

**Q2 closure status**:
* Pairwise high-tail parity lemma at L_2=(16,4): **~95% provable** (modulo Z[ω_16] strict for |A| ∈ {0, 2}).
* Side-(2,2) 4-support: **CLOSED structurally + prime-uniform empirical** (Note 0394 + 0395).
* Side-(3,1)/(1,3) 4-support: **OPEN structurally**, empirical 0 across 615M trials (Note 0395).
* Side-(4,0)/(0,4) 4-support: **CLOSED trivially** via side-pure rank-bound.
* 5+/6+/7+/8+ supp: **OPEN structurally**, empirical 0 across 615M trials (Note 0392).

**Ethereum Foundation $1M Proximity Prize attack**:
* Pairwise lemma + side-(2,2) closure + multi-prime empirical for higher arities = **strong empirical case** for Q2.
* Theorem~\ref{thm:universal-K10} ($K \le 10$ for sparse) + Q2 → $\varepsilon_{ca}(C, \delta) \le 10/q$ for **all** $f$ → ABF Lemma 6.13 unconditional → **prize-quality result**.
* Tier 2 (side-(3,1)) closure would tighten to "structural + scale-uniform" status.

---

## Recommendations for tomorrow

1. **First priority**: complete Tier 2 Mechanism B verification (Note 0415+ scripts).
   * Empirically check whether side-(3,1) candidates have v-row mixed parity.
   * If yes for some: that's not the closing mechanism; try Mechanism C/D.
   * If no for any: side-(3,1) auto-closed by Note 0389's "at least one row mixed parity" requirement.

2. **Second priority**: extend Z[ω_16] strict framework to |A| ∈ {0, 2} by optimizing the Python implementation (e.g., numpy or ctypes for polynomial arithmetic). ~1 day.

3. **Third priority**: paper2 v22 integration. Add Tier 1c field-uniform results to §2 (Theorem~\ref{thm:no-full-base-closure}).

4. **Fourth priority**: continue Tier 1b scale-lift via the Z[ω_*] framework. Mechanical extension with growing cyclotomic ring degrees.

---

## Honest caveats

* The Z[ω_16] strict framework for |A| ∈ {0, 2} is implemented but slow in Python; sample-based or empirical extensions are the practical alternative.
* Multi-prime empirical at 34 primes is strong but not strict field-uniformity.
* Tier 2 (side-(3,1)) structural proof is genuinely open algebra; estimated 1-3 weeks to first insight, possibly months to full closure.
* The "polynomial-degree kill" and "Vieta + Z[ω_16] minor" frameworks scale to other |A|-strata mechanically; the user can iterate this offline.

---

## Quick navigation

* `notes/0407-issue419-pathC-A4-r4r7-r6r5.md` — start of Tier 1c (4,7),(6,5)
* `notes/0411-issue419-pathC-A4-hard-batch.md` — climax: all 25 hard pairs
* `notes/0412-issue419-pathC-A6-h-nonzero.md` — |A|=6 closure
* `notes/0413-issue419-A0-A2-multi-prime.md` — multi-prime extension
* `notes/0414-issue419-tier2-side31-framing.md` — Tier 2 framing
* `STATE.md` — current handoff
* All scripts in `notes/scripts/issue419_pathC_*.py`

User's next iteration prompt should clarify: **continue Tier 2 attack OR
optimize/extend the strict Z[ω_16] framework OR draft paper2 v22 integration.**
