# Note 0409 -- Issue #419: Path C field-uniform proof for (r,r')=(8,5) at |A|=4

**Date:** 2026-05-02 (Tier 1c iteration 4 — second Vieta+norm closed-form)
**Branch:** `main`
**Status:** **Closed-form, FIELD-UNIFORM** proof for $(r, r') = (8, 5)$ at $|A| = 4$,
$L_2 = (16, 4)$.  Holds at every prime $q$ with $16 \mid q-1$, no exceptions.

The argument: Vieta on the quartic kill polynomial gives 3 constraints in $\mathbb{Z}[\omega_{16}]$;
the smallest of their max-norms ($\max |N(C_1)| = 196$) bounds bad primes to
$q \le 196$ in any embedding; only 4 such primes exist ($q \in \{17, 97, 113, 193\}$),
each empirically verified.

---

## 1.  Setup

For $(r, r') = (8, 5)$: $r/2 = 4$, $\deg X = 2$; $m = 2$, $\deg \tilde Y_0 = 0$.
Computing $X(y) = (P(y) + y^4)/G_A(y)$ via polynomial division (analogous to Note 0407):
$$
X(y) = y^2 + s_1 y + h_2, \qquad \tilde Y_0 = 1.
$$
This is the **same polynomial** as $\tilde Y_0$ for $(r, r') = (4, 9)$ — a transposition
symmetry between $X_{(r=8, r'=5)}$ and $\tilde Y_0_{(r=4, r'=9)}$.

The derived $\lambda_c$:
$$
\lambda_c = -X(u_c^2)/u_c = -(u_c^4 + s_1 u_c^2 + h_2)/u_c.
$$

Setting $\lambda_c = K$ for all 4 c:
$$
u_c^4 + s_1 u_c^2 + K u_c + h_2 = 0 \qquad (c = 1, 2, 3, 4).
$$

This is a **quartic** in $u_c$.  4 distinct $u_c$ being roots saturates the degree:
the polynomial must factor as $\prod (u - u_c)$.  Vieta gives:

| Symmetric function | Value |
|---|---|
| $E_1 = u_1 + u_2 + u_3 + u_4$ | $0$ (coefficient of $u^3$ in kill polynomial) |
| $E_2 = \sum_{i<j} u_i u_j$ | $s_1$ (coefficient of $u^2$) |
| $E_3 = \sum_{i<j<k} u_i u_j u_k$ | $-K$ (coefficient of $u$, defines $K$) |
| $E_4 = u_1 u_2 u_3 u_4$ | $h_2$ (constant term) |

Yielding 3 constraints on the no-full S (since $E_3$ defines $K$):
$$
\boxed{\;\;\;(C1)\; E_1 = 0, \qquad (C2)\; E_2 = s_1, \qquad (C3)\; E_4 = h_2.\;\;\;}
$$

---

## 2.  Computer-assisted verification in $\mathbb{Z}[\omega_{16}]$

Script: `issue419_pathC_8_5_vieta_Zomega.py`.  Enumerate all 5760 no-full $|A|=4$ S
and compute (C1), (C2), (C3) as elements of $\mathbb{Z}[\omega_{16}]$.

**Result.**  Pattern of which constraints are zero in $\mathbb{Z}[\omega_{16}]$:

| (C1=0?, C2=0?, C3=0?) | Count |
|---|---|
| (False, False, False) | 5696 |
| (False, False, True) | 64 |

So **at least 2 of (C1), (C2) are nonzero in $\mathbb{Z}[\omega_{16}]$ for every S**.
(64 S have $E_4 = h_2$ identically — the singletons' product matches the
σ-orbit reps' "second power-sum-like" — a structural coincidence — but
$E_1 \ne 0$ AND $E_2 - s_1 \ne 0$ for those S still.)

**Norm statistics (over all 5760 S):**

| Constraint | $\min |N|$ | $\max |N|$ |
|---|---|---|
| $|N(C_1)|$ | 4 | **196** |
| $|N(C_2)|$ | 16 | 5184 |
| $|N(C_3)|$ | 0 (for 64 S) | 324 |

The crucial bound: $\max |N(C_1)| = 196$.

---

## 3.  Bad-prime analysis

A prime $q$ with $16 \mid q-1$ admits joint vanishing of $(C_1, C_2, C_3)$ in
**some** embedding $\omega \mapsto \tilde\omega \in \mathbb{F}_q^*$ only if
$q \mid N(C_i)$ for all $i$.  In particular, $q \mid N(C_1)$ requires $q \le 196$.

**Primes $q \le 196$ with $16 \mid q-1$:** $q \in \{17, 97, 113, 193\}$ (only 4!).

For each, scan: how many S have all 3 norms $|N(C_i)|$ divisible by $q$?
* $q = 17$: 640 S
* $q = 97$: 0 S
* $q = 113$: 0 S
* $q = 193$: 0 S

**For $q > 196$**: $C_1$ has nonzero norm, so $C_1 \not\equiv 0 \pmod{q}$ in any
embedding.  Hence the (II)-test fails identically.  No further check needed.

**For $q \in \{97, 113, 193\}$**: 0 norm-coincidences, so (II)-test fails by
norm argument alone.

**For $q = 17$**: 640 S have norm-coincidences (necessary condition met) and
require direct empirical verification in the actual $\mathbb{F}_{17}$ embedding.

---

## 4.  Empirical verification at $q \in \{17, 97, 113, 193\}$

Script: `issue419_A4_full_compatibility.py --q <q>`.  Tests all 5760 S × 36 (r, r')
pairs (including (8, 5)) for (II) consistency.

| $q$ | Total tests | Consistent (II) | Status |
|---|---|---|---|
| 17 | 207,360 | **0** | ✓ all (II)-tests fail |
| 97 | 207,360 | 0 | ✓ Note 0400 |
| 113 | 207,360 | **0** | ✓ this Note |
| 193 | 207,360 | 0 | ✓ Note 0400 |

So **for the 4 candidate "bad" primes** ($q \le 196$), the actual embedding-specific
(II)-test fails for every S × every (r, r') pair, including (8, 5).

---

## 5.  Theorem statement

> **Theorem (Path C, $|A|=4$, $(r, r') = (8, 5)$).**
> For every odd prime $q$ with $16 \mid q-1$, every $|A|=4$ no-full S at
> $L_2 = (16, 4)$, and every $K \in \mathbb{F}_q$, the four derived values
> $\lambda_c = -(u_c^4 + s_1 u_c^2 + h_2)/u_c$ are not all equal to $K$.
>
> Hence the (II)-test fails, and no opposite-parity proportionality
> $\mathrm{HT}(t^8) \propto \mathrm{HT}(t^5)$ exists at $|A|=4$.

The proof combines:
* Vieta + norm bound: $C_1$ has max norm 196, so $q > 196$ kills (II) automatically.
* Empirical verification at the 4 candidate primes $q \in \{17, 97, 113, 193\}$:
  all 207,360 (S, r, r')-tests inconsistent at each prime.

**Cumulative Path C field-uniform: 5 / 36 pairs at $|A|=4$.**

---

## 6.  Pattern: norm bound + 4 small-prime scan

The combined $(4, 9)$ + $(8, 5)$ pattern suggests a general approach for
remaining easy pairs:

1. Compute kill polynomial degree $d$.  Vieta gives $d - 1$ structural
   constraints (since one Vieta constraint just defines $K$).
2. Compute each constraint as element of $\mathbb{Z}[\omega_{16}]$ for all 5760 S.
3. Compute integer norms; find $\min_i \max_S |N(C_i)|$ — this bounds
   "potentially bad" primes.
4. Empirical verification at the surviving small primes.

For the 4 "problem primes" $q \in \{17, 97, 113, 193\}$ (the only
ones $\le 196$), one full empirical run at each suffices to clear all
remaining easy pairs.

---

## 7.  Next concrete artifact

Tier 1c iteration 5: extend the Vieta+norm template to the remaining 6
easy pairs: $(4, 11), (4, 13), (4, 15), (10, 5), (12, 5), (14, 5)$.

Each uses the same script template; expected per-pair effort: ~30 min.

For the harder ones (e.g., $(4, 15)$ where kill polynomial has degree 11
in $u$, giving 10 Vieta constraints), the norm computation may be slower
but still mechanical.

After all 11 easy pairs: **11 / 36 pairs at $|A|=4$ field-uniform**, leaving
25 hard pairs (both polynomials non-constant).  Hard pairs require either
ratio-form analysis or unified $|A|=4$ sub-lemma.

Output target: Note 0410+.
