# Note 0411 -- Issue #419: Path C field-uniform proofs for ALL 25 hard pairs at |A|=4

**Date:** 2026-05-02 (Tier 1c iteration 6 — batch closure of all hard pairs)
**Branch:** `main`
**Status:** **All 25 hard pairs at $|A|=4$, $L_2 = (16, 4)$ are FIELD-UNIFORM.**

Combined with Notes 0405, 0407–0410: **ALL 36 PAIRS AT $|A|=4$ ARE FIELD-UNIFORM.**

This essentially completes the **field-uniform Path C closure of the
$|A|=4$ stratum at $L_2 = (16, 4)$** — covering 5760 of 10896 no-full S.

---

## 1.  Hard-pair framework

For hard $(r, r')$ at $|A|=4$, both $X(y) = \sum_k h_k y^{r/2-2-k}$ and
$\tilde Y_0(y) = \sum_k h_k y^{m-2-k}$ ($m = (r'-1)/2$) are non-constant
polynomials.  The (II) test:
$$
\lambda_c = \frac{-X(u_c^2)}{u_c \tilde Y_0(u_c^2)} = K \;\Longleftrightarrow\;
X(u_c^2) + K \cdot u_c \tilde Y_0(u_c^2) = 0.
$$

Define the parametric kill polynomial $\Psi(u; K) := X(u^2) + K \cdot u \tilde Y_0(u^2)$,
of degree $d := \max(r-4, r'-4)$ in $u$.

For 4 distinct $u_c \in \mu_{16}$ to all satisfy $\Psi(u_c; K) = 0$:
divide by $P_4(u) = \prod_c (u - u_c)$.  The 4 remainder coefficients are
$$
r_i \;=\; A_i + K \cdot B_i \qquad (i = 0, 1, 2, 3),
$$
where $A_i$ is the $i$-th remainder coefficient of $X(u^2) \bmod P_4(u)$
and $B_i$ likewise for $u \tilde Y_0(u^2) \bmod P_4(u)$.

For all 4 $r_i = 0$ to admit a single $K$: the $4 \times 2$ matrix
$\begin{pmatrix} A_i & B_i \end{pmatrix}$ must have rank $\le 1$.  This holds
iff **all 6 two-by-two minors $A_i B_j - A_j B_i$ vanish** ($i < j$).

For (II)-test FAILURE (good): at least one minor is **nonzero** in $\mathbb{F}_q$.

---

## 2.  Polynomial-degree kill bonus: (6, 7)

Pair $(6, 7)$: $X(y) = y + s_1$, $\tilde Y_0(y) = y + s_1$.
$$\Psi(u; K) = (u^2 + s_1) + K u (u^2 + s_1) = (u^2 + s_1)(1 + K u),$$
degree $3$ in $u$.  4 distinct roots impossible.  **FIELD-UNIFORM by polynomial degree.**

---

## 3.  Batch verification

Script: `issue419_pathC_hard_unified.py`.  For each of the 24 remaining
hard pairs (excluding $(6, 7)$), enumerate 5760 no-full $|A|=4$ S, compute the
6 minors $A_i B_j - A_j B_i$ in $\mathbb{Z}[\omega_{16}]$, compute integer norms,
find candidate "bad" primes via the bound $q \le \min_k \max_S |N_k|$.

**Final summary:**

| Status | Count | Pairs |
|---|---|---|
| FIELD-UNIFORM automatic (degree-kill or norm bound) | **15** | $(6,7), (6,15), (8,9), (8,11), (8,13), (8,15), (10,9), (10,11), (10,15), (12,9), (12,13), (12,15), (14,7), (14,11), (14,15)$ |
| Needs only $q=17$ empirical check | **10** | $(6,9), (6,11), (6,13), (8,7), (10,7), (10,13), (12,7), (12,11), (14,9), (14,13)$ |
| Other (anomaly) | 0 | — |

For the 10 pairs needing $q=17$ empirical: the existing
`issue419_A4_full_compatibility.py --q 17` run (Note 0409 §4) tested ALL 36
opp-parity pairs at $q=17$ and found **0 consistent across 207360 tests**.

So all 10 pairs are empirically closed at $q=17$, AND no other prime
$q \equiv 1 \pmod{16}$ has joint norm-vanishing.  **All 25 hard pairs FIELD-UNIFORM.**

---

## 4.  Combined Path C status at $|A|=4$, $L_2 = (16, 4)$

| Pair count | Method | Notes |
|---|---|---|
| 1 trivial (4, 5) | Constant collapse | 0405 |
| 2 elementary-kill (4, 7), (6, 5) | Polynomial degree | 0407 |
| 8 easy Vieta-norm | Quintic+ Vieta in Z[ω_16] | 0408, 0409, 0410 |
| **25 hard Vieta-rank-2** | **Bilinear minor in Z[ω_16]** | **0411 (this)** |
| **TOTAL** | **36 / 36** | **FIELD-UNIFORM at every $q \equiv 1 \pmod{16}$** |

This **completes Tier 1c Path C field-uniform closure of the $|A|=4$ stratum**
at $L_2 = (16, 4)$.

---

## 5.  Cumulative Tier 1 status at $L_2 = (16, 4)$

| Stratum | Count | Tier 1a status (3 primes empirical) | Tier 1c status (field-uniform) |
|---|---|---|---|
| $|A| = 8$ (σ-symmetric) | 16 | ✓ Note 0396 | ✓ Note 0397 (scale-uniform too) |
| $|A| = 6$ | 1280 | ✓ Note 0399 | partial (8th-root sub-lemma is field-uniform for $r \in \{4, 6\}$) |
| **$|A| = 4$** | **5760** | ✓ Note 0400 | **✓ Notes 0405, 0407-0411 (THIS)** |
| $|A| = 2$ | 3584 | ✓ Note 0401 | (next) |
| $|A| = 0$ | 256 | ✓ Note 0402 | (next) |

The $|A|=4$ stratum (5760/10896 ≈ 52.9%) is now **field-uniform**.  Combined
with Note 0397's σ-symmetric ($|A|=8$, 16 S) and Note 0399's partial $|A|=6$
($r \in \{4, 6\}$, 12 of 36 pairs × 1280 S = 15360 sub-tests), the field-uniform
fraction is now substantial.

---

## 6.  Remaining work for full Tier 1c at $L_2 = (16, 4)$

**Path C extension to $|A| \in \{0, 2, 6\}$:**

* $|A|=6$: 1280 S × 36 pairs.  Note 0399 closed $r \in \{4, 6\}$ by 8th-root
  sub-lemma; need extension to $r \in \{8, 10, 12, 14\}$ (24 pairs).  Likely
  similar Vieta + Z[ω_16] norm framework, possibly easier (more constraints
  in (D-P)).
* $|A|=2$: 3584 S × 36 pairs.  Note 0401 closed empirically via 6×3
  over-determination.  Field-uniform via Z[ω_16]: extend Note 0411 framework
  to the (D-Q) constraint structure.
* $|A|=0$: 256 S × 36 pairs.  Smallest stratum.  Note 0402 closed
  empirically via 8×5 over-determination.

Estimated effort: **~1-2 days** to extend the Z[ω_16] framework to the other
strata, modulo similar technical refinements.

---

## 7.  Strategic implication

The Z[ω_16] norm-bound framework is now a **mature pipeline**:
1. Express the (II) test failure as a polynomial-rank condition in Z[ω_16].
2. Compute integer norms of the constraint polynomials per S.
3. Bad primes bounded by $\min_k \max_S |N_k|$.
4. Empirical check at the (typically very few) bad primes ≤ bound.

For **deployment-relevant primes** ($q \in \{97, 193, 1153\}$): Tier 1a
already covers everything empirically.  For **arbitrary primes**: the
framework reduces to a finite computation per stratum/pair.

**Field-uniformity at $L_2 = (16, 4)$ is essentially complete** modulo
extending the framework to the other 3 strata (mechanical).

---

## 8.  Next concrete artifact

Tier 1c iteration 7: extend Z[ω_16] framework to $|A|=6$ stratum.

For $|A|=6$: $G_A = (y - \zeta_1)(y - \zeta_2)(y - \zeta_3)$, degree 3.
The (D-P) condition $G_A | (P + y^{r/2})$ uniquely determines $P$ degree 2.
The 4-root λ-disagreement test now uses 3 roots of $H$ (deg $H = 6$, but
$|B|=2$, so only 2 roots in our test... wait need to re-derive).

Actually $|A|=6$ has $|B|=2$ (since $|S|=8 = |A| + |B|$).  Two singletons,
2 mod-8 residues distinct from $\{a_1, a_2, a_3\}$.  $H$ has degree
$2 |B| = 4$ in $y$ (4 roots).  Check the structure.

Output target: Note 0412.

Or alternatively: compress the 4 "easy + hard" |A|=4 closures into a single
publishable proof template and start drafting paper2 v22 § for Tier 1c
field-uniform closure.

User's compaction directive favors continuing math.  Let me proceed with
Note 0412 (extending to |A|=6).
