# Note 0406 -- Issue #419: Path C (r, r') pair classification at |A|=4

**Date:** 2026-05-02 (Tier 1c continuation — systematize Path C work)
**Branch:** `main`
**Status:** Classified all 36 opp-parity (r, r') pairs at $L_2 = (16, 4)$,
$|A| = 4$ stratum, by the polynomial degree of $X$ and $\tilde Y_0$ in
the $\lambda_c$-disagreement test.  Identifies 11 "easy" pairs (one of
$X, \tilde Y_0$ constant) vs. 25 "hard" pairs (both non-constant).

---

## 1.  Classification

Recall the $\lambda_c$ formula at root $\eta_c = \zeta^c$ of $H$:
$$
\lambda_c = \frac{-X(\eta_c)}{\omega^{b_c} \tilde Y_0(\eta_c)},
$$
with $\deg X = \max(0, r/2 - 2)$ and $\deg \tilde Y_0 = \max(0, m - 2)$
where $m = (r' - 1)/2$.

| Pair $(r, r')$ | $\deg X$ | $\deg \tilde Y_0$ | Class |
|---|---|---|---|
| (4, 5) | 0 | 0 | **Trivial** (Note 0405 closed) |
| (4, 7) | 0 | 1 | $X$-const, $\tilde Y_0$-linear |
| (4, 9) | 0 | 2 | $X$-const, $\tilde Y_0$-quadratic |
| ... | ... | ... | ... |
| (4, 15) | 0 | 5 | $X$-const, $\tilde Y_0$-quintic |
| (6, 5) | 1 | 0 | $X$-linear, $\tilde Y_0$-const |
| (8, 5) | 2 | 0 | $X$-quadratic, $\tilde Y_0$-const |
| (10, 5) | 3 | 0 | $X$-cubic, $\tilde Y_0$-const |
| (12, 5) | 4 | 0 | $X$-quartic, $\tilde Y_0$-const |
| (14, 5) | 5 | 0 | $X$-quintic, $\tilde Y_0$-const |
| (6, 7), (6, 9), ..., (14, 15) | $\ge 1$ | $\ge 1$ | **Hard** (both non-constant) |

* Trivial: 1 pair (4, 5)
* Easy ($X$-const or $\tilde Y_0$-const): 10 pairs
* Hard (both polynomial): 25 pairs

Script: `issue419_pathC_lambda_collapse.py` for full enumeration.

---

## 2.  Easy-pair sub-mechanism

**Easy case A: $X = X_0$ constant ($r = 4$).**
$$\lambda_c = \frac{-X_0}{\omega^{b_c} \tilde Y_0(\eta_c)}.$$
Distinctness of $\lambda_c$ values is equivalent to distinctness of
$\omega^{b_c} \tilde Y_0(\eta_c)$.  For $\tilde Y_0$ of degree $d_y \le 5$,
$\tilde Y_0(\eta_c)$ is a polynomial in $\eta_c$ taking 4 specific values
across the 4 distinct $\eta_c$.

**Easy case B: $\tilde Y_0 = Y_0$ constant ($r' = 5$).**
$$\lambda_c = \frac{-X(\eta_c)}{\omega^{b_c} Y_0}.$$
Distinctness equivalent to $X(\eta_c) \omega^{-b_c}$ distinct.

For both easy cases, the question reduces to: *does the polynomial-of-η
expression collide for some $(c_i, c_j)$ pair via a 16th-root-of-unity
factor coming from $\omega^{b_i - b_j}$?*

---

## 3.  Closed-form proof template for easy cases

For each easy case, the proof template is:

1. Compute $X$ or $\tilde Y_0$ as an explicit polynomial in $(y, \zeta_1, \zeta_2)$.
2. Evaluate at each $\eta_c = \zeta^c$ to get 4 values in $\mathbb{F}_q$.
3. Multiply by $\omega^{\pm b_c}$ for the $\omega$-twist.
4. Show that the 4 resulting values cannot all be equal under no-full
   constraints on $(\zeta_1, \zeta_2, b_1, b_2, b_3, b_4)$.

The "no-full constraint" includes:
* $b_i \in \mathbb{Z}/16\mathbb{Z}$, all 4 distinct.
* $b_i \ne b_j + 8$ (no σ-pairs in $B$).
* $\{b_i \bmod 8\} \cap \{a_1, a_2\} = \emptyset$ (A and B disjoint mod 8).
* The $b_i$ distribution across quadrants $\{j \bmod 4\}$ has $\le 3$
  per quadrant (no-full).

Each easy case is a *finite* polynomial identity in cyclotomic algebra;
mechanical verification.  Estimated 1 evening per case.

---

## 4.  Hard-pair sub-mechanism

For (r, r') with $r \ge 6$ AND $r' \ge 7$: both $X$ and $\tilde Y_0$
non-constant.  $\lambda_c$ becomes a ratio of two polynomial-in-$\eta$
expressions.  Distinctness needs ratio analysis.

These 25 pairs likely require a unified approach (e.g., resultant
emptiness over $\mathbb{Z}[\omega_{16}]$ — Path B) rather than pair-by-pair
closed forms.

---

## 5.  Cumulative Path C status

| Pair count | Pairs | Status |
|---|---|---|
| 1 (Trivial) | (4, 5) | ✓ Field-uniform proved (Note 0405) |
| 10 (Easy) | (4, 7..15), (6..14, 5) | template proof, ~10 evenings |
| 25 (Hard) | (6..14, 7..15) | resultant/symbolic algebra needed |
| **Total** | **36** | $11/36 \approx 31\%$ in reach |

For full Tier 1a field-uniformity at $L_2 = (16, 4)$: 25 hard pairs require
either (a) Path B resultant-emptiness computation in Sage/Macaulay2 (~1 week
total), or (b) a unified structural argument (e.g., a "no-full sub-lemma"
covering the entire $|A| = 4$ stratum).

The cleaner direction is (b): find a universal obstruction that doesn't
depend on $(r, r')$ specifics.

---

## 6.  Strategic assessment

Path C closed-form is more involved than initially estimated (Note 0405
"~5-10 days" assumed each pair is 1-page; actually only 11 pairs are clean,
the other 25 need Path B-style algebra).

**Revised effort estimate for Tier 1a field-uniformity:**
* 1 trivial pair: done (Note 0405).
* 10 easy pairs: ~5-7 days for template verification.
* 25 hard pairs: ~1-2 weeks via Path B (Sage resultants over $\mathbb{Z}[\omega_{16}]$).

Total: ~2-3 weeks for full L₂=(16,4) field-uniformity at all $|A|$ strata.

Given that the user asked for a tiered approach (Tier 1 → Tier 2 → Tier 3),
and the empirical 3-prime closure is already established (Notes 0396–0402),
**field-uniformity is "nice to have" but not a blocker** for prize-quality
paper integration.  Paper2 v21 with "verified at deployment primes
$\{97, 193, 1153\}$" is publishable; field-uniformity can follow as
follow-up.

---

## 7.  Next concrete artifact

Two parallel tracks:

**Track 1 (paper integration, ~2 days):** open paper2.tex, update
§rem:sparse-worst-empirical with Tier 1a/1b empirical-near-structural Q2
closure.  v21 ready for ePrint revision.

**Track 2 (Path C/B continuation, ~2-3 weeks):**
- Note 0407: closed-form for (4, 7), (6, 5) as template proof exemplars.
- Note 0408+: Sage-based Path B for hard pairs.

User's next-iteration prompt should clarify priority: integration vs.
algebraic completeness.  Both keep within Tier 1 "pure execution time".
