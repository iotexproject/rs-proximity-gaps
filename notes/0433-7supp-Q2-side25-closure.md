# Note 0433 -- Issue #419: 7-supp Q2 partial closure via side-(2,5)/(5,2) reduction

**Date:** 2026-05-03 early morning (Tier 3 7-supp partial)
**Branch:** `main`
**Status:** Side-(2,5) and side-(5,2) configurations of 7-supp at L_2=(16,4)
are STRUCTURALLY CLOSED via Note 0393 reduction. Side-(3,4)/(4,3) requires
3-vec rank analysis on q-restricted HT triples.

---

## 1.  Side-(2, 5) reduction

For 7-supp side-(2, 5): u-row 2 monomials, v-row 5 monomials.

**u-row saturation analysis** by parity of u-monomials:

### Case A: Both u-monomials q=0 (both even)

Pair from {4, 8, 12} (q=0 evens at L_2=(16, 4)).

Possible pairs: (4, 8), (4, 12), (8, 12).

By **Note 0393's pairwise high-tail parity lemma** (FIELD-UNIFORM via Notes 0407-0413):
the only same-parity (even-even) proportional pair at L_2=(16, 4) is $\{8, 10\}$.

The pair (8, 10) requires $10 \in q=2$, **NOT $q=0$**.

So pairs from q=0 evens are NEVER proportional at no-full S.

⇒ For u-row saturation: $c_e1 \mathrm{HT}(t^{r_{e1}}) + c_e2 \mathrm{HT}(t^{r_{e2}}) = 0$
forces $c_{e1} = c_{e2} = 0$. u-row vanishes → 7-supp degenerates to 5-supp on v-side.

**5-supp closed by Tier 3 (Notes 0425-0428).**

### Case B: Both u-monomials q=1 (both odd)

Pair from {5, 9, 13}. The only odd-pair proportional is (9, 11), which requires
$11 \in q=3$, NOT q=1.

⇒ Same argument as Case A: c_u = 0 → 5-supp closed.

### Case C: 1 even q=0 + 1 odd q=1 (mixed parity)

u_α = $c_e t^{r_e} + α c_o t^{r_o}$ (α multiplies q=1 contribution).

For u_α saturated on S: $c_e \omega^{r_e s} + α c_o \omega^{r_o s} = 0$ for $s \in S$.

Equivalent: $α c_o = -c_e \omega^{(r_e - r_o) s}$ for each $s \in S$.

For α specific nonzero, $α c_o$ is a fixed F_q-element. The RHS $\omega^{(r_e - r_o) s}$
must be constant across $s \in S$.

But $\omega^{(r_e - r_o) s}$ constant across s ∈ S requires $(r_e - r_o)(s - s') \equiv 0 \pmod{16}$
for all $s, s' \in S$.

Since $r_e$ even and $r_o$ odd, $r_e - r_o$ is **odd**. For $r_e - r_o \in \{\pm 1, \pm 3, ..., \pm 11\}$:
$\gcd(r_e - r_o, 16) = 1$ (odd vs power of 2).

Hence $16 | (s - s')$ for all $s, s' \in S$. With $|S| \ge 2$ and $s, s' \in \mathbb{Z}/16$
distinct: $|s - s'| \le 15$, never divisible by 16.

**Contradiction.** So mixed-parity u-row cannot be α-saturated for nontrivial α.

If $c_e = c_o = 0$: u-row vanishes → 5-supp closed.

⇒ Mixed-parity Case C also reduces to 5-supp.

### Conclusion for side-(2, 5)

In all cases (A, B, C), u-row saturation forces $c_u = 0$ (or trivial) →
7-supp degenerates to 5-supp closed by Tier 3.

**Side-(2, 5) parity-(any) at any no-full S is structurally CLOSED.**

---

## 2.  Side-(5, 2) reduction — symmetric

By symmetric argument (u/v swap): side-(5, 2) closes via v-row 2-monomial
forced to vanish.

**Side-(5, 2) at any no-full S is CLOSED.**

---

## 3.  Side-(3, 4) and (4, 3) — need further analysis

For 7-supp side-(3, 4)/(4, 3): one row has 3 monomials.

**For 3-monomial u-row saturation**:
- All same parity (3 q=0 evens or 3 q=1 odds): 3-vec dep requires generalized
  Vandermonde det = 0. For specific (r_1, r_2, r_3) and S: empirical check needed.
  - For 3 q=0 evens (4, 8, 12): not in Note 0395's main rank-2 list; likely independent.
  - For 3 q=1 odds (5, 9, 13): same expectation.
- Mixed parity (e.g., 2 evens + 1 odd, or 1 even + 2 odds): α-twist analysis,
  similar to Case C.

If 3-monomial side has rank 3 (no dep): forces c = 0 → 4-supp closed.

If 3-monomial side has rank ≤ 2: nontrivial dep, but the kernel direction
may not align with the larger-side saturation constraints.

A clean structural closure for side-(3, 4)/(4, 3) requires either:
* Generalized Note 0393 to 3-vec independence at q-restricted HT triples.
* Or empirical verification at multiple primes.

---

## 4.  Updated 7-supp Q2 status

| Side classification | Status |
|---|---|
| Side-(7, 0)/(0, 7) | side-pure rank ≤ 1, NOT primitive → CLOSED |
| Side-(6, 1)/(1, 6) | single v/u-monomial → c=0 → 6-supp closed |
| **Side-(5, 2)/(2, 5)** | **CLOSED via Note 0393 reduction (this Note)** |
| Side-(4, 3)/(3, 4) | partial analysis; same-parity 3-row likely closes |

For paritya analysis (similar to 6-supp Note 0432): rank-def at parity
(3, 4)/(4, 3) needs k-vec scan stratification at k=7. Already done in
Note 0427 k=7 scan.

---

## 5.  Combined Q2 status (post-0433)

| Sub-class | Status |
|---|---|
| 3-supp | CLOSED (paper2 §3) |
| 4-supp | CLOSED (Tier 2) |
| 5-supp | CLOSED (Tier 3, Note 0426) |
| 6-supp | CLOSED (Tier 3, Note 0432) |
| **7-supp side-(7,0)/(6,1)/(5,2)/(2,5)/(1,6)/(0,7)** | **CLOSED (this Note)** |
| 7-supp side-(4,3)/(3,4) | partial; needs 3-vec analysis on q-restricted HTs |
| 8+ supp | empirical only |

**For 7-supp: ~70% structurally closed via this Note's side reductions.**

---

## 6.  Strategic position

* Q2 closed for support ≤ 6.
* Q2 ~70% structural for support 7.
* For prize: K ≤ 10 unconditional for support ≤ 6 and side-(2,5)/(5,2)
  configurations of 7-supp.

---

## 7.  Next concrete artifact

* Note 0434: side-(3, 4)/(4, 3) closure via 3-vec analysis on q-restricted HTs.
* Or: paper2 v22 update to reflect the 6-supp + partial 7-supp closure.
