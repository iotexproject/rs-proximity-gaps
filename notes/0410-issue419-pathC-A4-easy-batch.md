# Note 0410 -- Issue #419: Path C field-uniform proofs for ALL 11 easy pairs at |A|=4

**Date:** 2026-05-02 (Tier 1c iteration 5 — batch closure of all easy pairs)
**Branch:** `main`
**Status:** **All 11 easy pairs at $|A|=4$, $L_2 = (16, 4)$ are FIELD-UNIFORM.**

Combining Notes 0405, 0407–0409 with this Note's batch verification:
| Method | Pairs | Status |
|---|---|---|
| Constant-collapse (Note 0405) | $(4, 5)$ | ✓ pure-elementary |
| Polynomial-degree kill (Note 0407) | $(4, 7), (6, 5)$ | ✓ pure-elementary |
| Vieta + norm (Notes 0408, 0409) | $(4, 9), (8, 5)$ | ✓ computer-assisted |
| Vieta + norm batch (this) | $(4, 11), (4, 13), (4, 15), (10, 5), (12, 5), (14, 5)$ | ✓ this Note |

**Cumulative Path C field-uniform: 11 / 36 pairs at $|A|=4$.**

---

## 1.  Unified framework

For every easy pair $(r, r')$ at $|A|=4$ (where one of $X$, $\tilde Y_0$ is constant),
the kill polynomial $g(u)$ has the form (after eliminating the parameter $K$):

* $(r=4, r')$: $g(u) - K' = u \tilde Y_0(u^2) - K'$, degree $r' - 4$ in $u$.
* $(r, r'=5)$: $g(u) + K u = X(u^2) + K u$, degree $\max(r-4, 1)$ in $u$.

Closed form for the polynomials:
$$
\tilde Y_0_{(4, r')}(y) = \sum_{k=0}^{m-2} h_k \, y^{m-2-k}, \quad m = (r'-1)/2,
\qquad
X_{(r, 5)}(y) = \sum_{k=0}^{r/2-2} h_k \, y^{r/2-2-k},
$$
where $h_k(\zeta_1, \zeta_2) = \sum_{i+j=k} \zeta_1^i \zeta_2^j$ are complete homogeneous
symmetric polynomials in the σ-orbit reps.

For 4 distinct $u_c \in \mu_{16}$ to all satisfy $g(u_c) = K$: the polynomial
$P_4(u) := \prod_c (u - u_c)$ must divide $g(u) - K$.

**Polynomial division** of $g(u) - K$ by $P_4(u)$ yields a remainder of degree $\le 3$
(4 coefficients).  One coefficient (linear in $K$) determines $K$; the other 3 are
**pure constraints** on $(u_c, \zeta_i) \in \mu_{16}^4 \times \mu_8^2$.

These 3 constraints live in $\mathbb{Z}[\omega_{16}]$.  Field-uniformity asks: for every
no-full S, at least one of the 3 constraints is nonzero in $\mathbb{F}_q$ for every prime
$q$ with $16 \mid q-1$.

---

## 2.  Batch verification

Script: `issue419_pathC_easy_unified.py`.  For each of the 8 remaining easy pairs
(after Note 0405's $(4,5)$, Note 0407's $(4,7), (6,5)$), enumerate 5760 no-full
$|A|=4$ S, compute the 3 constraint values in $\mathbb{Z}[\omega_{16}]$, compute integer
norms, and find candidate "bad primes" (those $q \equiv 1 \pmod {16}$ for which
some S has all 3 norms divisible by $q$).

**Result table:**

| Pair | $\max |N(C_i)|$ over $i, S$ | Min-max norm | Candidate bad primes ($q \le$ min-max, $q \equiv 1 \pmod {16}$) |
|---|---|---|---|
| $(4, 9)$ | $C_0$ max 5184 | 5184 | $\{17\}$ (256 S) |
| $(4, 11)$ | $C_0$ max 72386 | 38416 | $\{17\}$ (128 S) |
| $(4, 13)$ | $C_0$ max 43169 | 5184 | $\{17\}$ (256 S) |
| $(4, 15)$ | $C_2$ max 1 | 1 | NONE (q ≤ 1: empty list) ✓ |
| $(8, 5)$ | $C_1$ max 5184 | 196 | $\{17\}$ (640 S) |
| $(10, 5)$ | $C_2$ max 40000 | 25616 | $\{17\}$ (640 S) |
| $(12, 5)$ | $C_2$ max 40000 | 40000 | $\{17\}$ (256 S) |
| $(14, 5)$ | $C_2$ max 196 | 196 | NONE (no joint vanishing in $\{17, 97, 113, 193\}$) ✓ |

**Two pairs auto-close** without empirical work:
* $(4, 15)$: $\min |N| = 1$ — constraint $C_2$ is always a unit in $\mathbb{Z}[\omega_{16}]$,
  hence nonzero modulo any prime.  Field-uniform automatic.
* $(14, 5)$: no joint norm-vanishing for $q \in \{17, 97, 113, 193\}$ (the only primes
  in the bound).  Field-uniform automatic.

**Six pairs need empirical verification at $q = 17$**: $(4, 9), (4, 11), (4, 13),
(8, 5), (10, 5), (12, 5)$.  All 5760 S × these pairs = 6 × 5760 = 34560 tests
at $q=17$.

---

## 3.  Empirical verification at $q=17$

Script: `issue419_A4_full_compatibility.py --q 17`.  Verifies all 5760 S × 36 (r, r')
opp-parity pairs (= 207360 tests) for (II) consistency.

Result (already run in Note 0409 §4):
* **Inconsistent: 207360**
* **Consistent: 0**

Since this covers all 36 pairs, including the 6 pairs needing verification, those
6 pairs are empirically closed at $q=17$.

Combined with the norm bound (no other $q \equiv 1 \pmod{16}$ has joint norm-vanishing),
**all 6 pairs are FIELD-UNIFORM** at every $q \equiv 1 \pmod{16}$.

---

## 4.  Updated cumulative status (after Notes 0405, 0407–0410)

| Pair | Method | Status |
|---|---|---|
| $(4, 5)$ | Constant-collapse | ✓ FIELD-UNIFORM (Note 0405) |
| $(4, 7), (6, 5)$ | Polynomial-degree kill | ✓ FIELD-UNIFORM (Note 0407) |
| $(4, 9)$ | Vieta + norm + q=17 | ✓ FIELD-UNIFORM (Note 0408) |
| $(8, 5)$ | Vieta + norm + q=17 | ✓ FIELD-UNIFORM (Note 0409) |
| $(4, 11), (4, 13), (10, 5), (12, 5)$ | Vieta + norm + q=17 | ✓ FIELD-UNIFORM (this Note) |
| $(4, 15)$ | Vieta, $C_2$ unit | ✓ FIELD-UNIFORM (this Note, automatic) |
| $(14, 5)$ | Vieta, no q≤bound joint-vanish | ✓ FIELD-UNIFORM (this Note, automatic) |
| **TOTAL EASY** | | **11 / 11 closed** |
| 25 hard pairs | (next) | open |

**$11 / 36 \approx 30.6\%$ of $|A|=4$ pairs are now FIELD-UNIFORM at every prime $q \equiv 1 \pmod{16}$.**

The remaining 25 hard pairs $(r, r') \in \{(6..14)\} \times \{(7..15)\}$ have
both $X$ and $\tilde Y_0$ non-constant; the kill-polynomial reformulation gives
a **rational function** $\lambda_c = -X(u_c^2)/(u_c \tilde Y_0(u_c^2))$ rather than
a polynomial-only equation, so the Vieta-on-kill-polynomial framework needs
extension.

---

## 5.  Extension framework for hard pairs

For hard $(r, r')$: $\lambda_c = -X(u_c^2)/(u_c \tilde Y_0(u_c^2)) = K$ becomes
$X(u_c^2) + K u_c \tilde Y_0(u_c^2) = 0$, a polynomial equation in $u_c$ of degree
$\max(r - 4, r' - 4)$ — but with $K$ now coupled to BOTH $X$ and $\tilde Y_0$
coefficients via $\tilde Y_0(u_c^2)$ multiplied by $K$.

The 4 distinct $u_c$ being roots of this combined polynomial: divide by $P_4(u)$,
get 4 remainder coefficients (3 effective constraints + $K$ absorbing one).  The
constraints now involve $K$ multiplied by $\tilde Y_0$-coefficients, so they're
**polynomial in K** (degree 1).

Analytic next step: project out $K$ to get a single polynomial constraint per
"two pair" comparison, then proceed with norm bounds.

Output target: Note 0411+ for first hard pair (e.g., $(6, 7)$), then unified
hard-pair check.

---

## 6.  Strategic position update

**Tier 1c at $L_2 = (16, 4)$, $|A| = 4$ stratum:**
* Easy: **11 / 11 done, FIELD-UNIFORM at every prime $q \equiv 1 \pmod {16}$**.
* Hard: 0 / 25 done.

**Estimated effort for remaining 25 hard pairs:**
* Per-pair Vieta-on-rational-form analysis: ~1 hour each, ~25 hours total.
* OR unified $|A|=4$ sub-lemma: ~3-7 days for structural insight.

**Strategic:** the unified Z[ω_16] framework is now a mature pipeline.  Hard
pairs are mechanical extension; once the rational-form Vieta is set up, can
batch-verify all 25.  Estimated 3-5 days to complete.

After: extend Path C ladder to other strata $|A| \in \{0, 2, 6, 8\}$.

For tonight: continue with hard-pair attack (Note 0411+) and Tier 2 framing
(Note 0420+/Note 0407 → Tier 2 chain).
