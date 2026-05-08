# Note 0458 -- K=16 canonical lift is STRICTLY ABOVE Johnson (boundary argument FAILS)

**Date:** 2026-05-03 post-compact (continuing from Note 0457 Option A)
**Branch:** `main`
**Status:** **REVISED.** §3's hypothesis "agreement at L_0 = 64 = exactly
Johnson" was empirically refuted by `issue419_K16_canonical_lift.py`: the
kernel polynomial $f$ has MORE zeros on $L_2$ than just $|S|=16$ (typically
20-24 zeros), so $f^{(0)}(w) := f(w^4)$ at $L_0$ has 72-80 zeros, agreement
72-80 STRICTLY ABOVE the Johnson threshold 64.

So the K=14, 16 residual is NOT excluded by Johnson-boundary admissibility.
It MAY be in scope of `conj:sparse-worst` after all.

The remaining exclusion mechanism is action-orbit non-stabilization (paper2
exclusion (i)), which has not yet been checked.

The empirical numbers from the run (5 K=16 cases at p=257):

| Case | rs | L_2 zeros (incl S) | L_0 lift zeros | Above-J? |
|---|---|---|---|---|
| 1 | [8,9,10,11,12,13,14,15,21,22,24,25,27,28,30,31] | 20 | 80 | YES (agreement 80 > 64) |
| 2 | [8,9,10,12,14,15,16,17,19,23,24,26,28,29,30,31] | 20 | 80 | YES |
| 3 | [10,12,13,14,16,18,19,20,22,23,24,25,26,28,29,30] | 18 | 72 | YES |
| 4 | [8,9,10,12,13,14,15,18,19,21,22,25,26,28,29,31] | 20 | 80 | YES |
| 5 | [8,9,10,14,15,16,17,19,22,24,25,26,28,29,30,31] | 20 | 80 | YES |

**Implication**: cannot simply invoke paper2 exclusion (ii) on these cases.
Need to either:
(A) Check action-orbit (non-)stabilization for each case (paper2 (i)).
(B) Compute actual $K(f_1, f_2; \delta)$ at $L_0$ to see if it exceeds 10.

---

## 1.  The observation

My K=12, 14, 16 cross-side rank-def cases at $L_2 = (32, 8)$ are all from
`sample_no_full_S(n2=32, k2=8, ...)`, which samples $S \subset L_2$ with
$|S| = n_2/2 = 16$.

Johnson agreement at $L_2 = (32, 8)$:
$$
\sqrt{n_2 \, k_2} = \sqrt{32 \cdot 8} = 16.
$$

Disagreement count at $L_2$ for the canonical zero-codeword pairing:
$|S| = 16 = n_2 - 16 = $ **exactly Johnson disagreement**.

So: **my K=16 cases sit at the $L_2$ Johnson boundary, NOT strictly above.**

---

## 2.  Lifting to $L_0$ keeps boundary

Given kernel polynomial $f \in \FF_q[z]$ on $L_2$ vanishing on $|S| = 16$,
the canonical lift $f^{(0)}(w) := f(w^4)$ on $L_0 = \mu_{128}$ satisfies:

* $f^{(0)}(w) = 0 \iff w^4 \in S$.
* Each $z \in L_2$ has 4 preimages in $L_0$, so $f^{(0)}$ vanishes at
  $4 |S| = 64$ positions of $L_0$.
* Disagreement of $f^{(0)}$ with the zero codeword: $128 - 64 = 64
  = \sqrt{n_0 k_0} = $ **exactly Johnson at $L_0$.**

By paper2's `rem:sparse-worst-action-orbit-nonstab` exclusion (ii):

> Independently, an all-$\alpha_2$ saturating component on $L_2$ lifts to the
> level-1 fold with agreement \emph{exactly} $\sqrt{n_1 k_1}$ -- on the
> Johnson threshold, not strictly above it.

The same counting argument applies to my K=16 cases: $L_2$ saturation at
$|S| = n_2/2$ lifts to $L_1, L_0$ at the corresponding Johnson thresholds.

**Therefore: my K=14, 16 residual cases are NOT strictly above-J at $L_0$,
and are excluded from the `conj:sparse-worst` admissibility predicate.**

---

## 3.  Subtlety: distance to nearest codeword

Strictly speaking, $\Delta(f^{(0)}, C_0)$ is the distance to the *nearest*
$C_0$-codeword, not just to $0$. Since $f^{(0)}$ has support
$\{4r : r \in \text{supp}(f)\} \subseteq \{32, \ldots, 124\}$, its
projection to $C_0 = \{p : \deg p < k_0 = 32\}$ along monomials is $0$,
so $\Delta(f^{(0)}, 0) = 64$. But there could be a non-zero $p \in C_0$
with $\Delta(f^{(0)}, p) < 64$.

In a degree-uniform setting (random coefficients), $\Delta(f^{(0)}, C_0)$
is exactly $64$ at the Johnson boundary with high probability, and can
only DECREASE on structured low-$K$ examples. So it stays $\leq 64$, not
strictly above.

Strictly-above-J requires $\Delta(f^{(0)}, C_0) > 64$. The zero-codeword
witness gives $\Delta(f^{(0)}, 0) = 64$, so $\Delta(f^{(0)}, C_0) \leq 64$
\emph{always}. NEVER strictly above-J. **Excluded.**

---

## 4.  Status of the residual after empirical check

Combining Note 0457 + Note 0458 (revised):

* My K=14, 16 (and K=12) random no-full $S$ rank-def cases at $L_2 = (32, 8)$:
* Are NOT in scope of `thm:no-full-base-closure` (base $(16, 4)$ + 3-support).
* Are NOT in scope of `thm:universal-K10` (3-position-sparse $\hat f$).
* Lift via canonical $f^{(0)}(w) := f(w^4)$ to $L_0 = (128, 32)$ with agreement
  $4 \cdot |\{z \in L_2 : f(z) = 0\}|$. Empirically this is 72-80, **strictly
  above** the Johnson threshold 64.
* So they are NOT excluded by admissibility (ii). Either admissibility (i)
  excludes them (action-orbit stabilization) or they are genuine candidates
  for refutation of `conj:sparse-worst` (still open in paper2).

**Conclusion**: the residual is NOT cleanly excluded. Need to check
admissibility (i) explicitly per case, or directly measure $K(f_1, f_2; \delta)$
at $L_0$ to determine bearing on the conjecture.

---

## 5.  Revised L3 status (provisional, after empirical refutation of §3)

* Q-Class Decomposition (Note 0453) + (1±t^{n_2/2}) Extension (Note 0454):
  STRUCTURAL closure of cross-side cases at concentrated $S$ and
  +n_2/2-paired kernels. ~90% of cases at non-boundary $|S|$.
* K=14, 16 random-S cases at $|S| = n_2/2$: STRICTLY ABOVE-J at $L_0$
  (canonical lift), so NOT excluded by Johnson-boundary admissibility.
  Need to check action-orbit (non-)stabilization (paper2 (i)) and
  measure $K(f_1, f_2; \delta)$ at $L_0$.

**L3 deployment-scale extension is NOT yet structurally complete; the
residual remains research-grade open until (i) action-orbit and/or
(ii) actual K-count are measured.**

---

## 6.  Empirical verification plan (B-lite)

The argument in §3 hinges on the canonical lift $f(w^4)$ giving
$\Delta(f^{(0)}, 0) = 64$ exactly. To confirm: run an explicit script
that takes one of the 23 K=16 cases, lifts via $f^{(0)}(w) := f(w^4)$,
and measures $\Delta(f^{(0)}, C_0)$ at $L_0 = (128, 32)$ over $\FF_{97}$.

Expected: $\Delta = 64$ exactly. To be coded as
`issue419_K16_canonical_lift.py`.

---

## 7.  Strategic position (provisional, after empirical check)

* paper2 stated theorems: **all intact**.
* paper2 K ≤ 10 headline (3-pos sparse): **unaffected** — different scope.
* paper2 `conj:sparse-worst`: **still open** in general (paper2 admits this).
  My K=16 residual MIGHT bear on it; canonical lift IS strictly above-J
  at $L_0$. Action-orbit stabilization (admissibility (i)) NOT yet checked.
* Q-Class Decomposition framework: **complete** for the in-scope (concentrated
  $S$, +n_2/2-paired) regime at $L_2 = (32, 8)$.
* L3 deployment-scale extension: **research-grade open** for K=14, 16
  random-S residual; need (i) action-orbit check + (ii) actual K-count
  measurement.

Next concrete step (Note 0459): code action-orbit checker for the 5 K=16
cases. If all are action-stabilised: residual fully excluded. If some are
non-stabilised: measure $K(f_1, f_2; \delta)$ to test refutation potential.

---

## 8.  Files

* This note: `0458-K16-residual-is-Johnson-boundary.md`
* Companion: `0457-Option-A-paper2-scope-resolves-K16-residual.md`
* Script (TODO): `notes/scripts/issue419_K16_canonical_lift.py`
