# Note 0457 -- Option A: paper2 scope resolves the K=16 residual (NOT a counter-example)

**Date:** 2026-05-03 (post-compact, continuing handoff Note 0456)
**Branch:** `main`
**Status:** Resolves the K=14, 16 random-S "residual" of Note 0455 by reading
paper2's exact theorem scope.  **Result:** the residual is NOT a counter-example
to anything paper2 claims; it lives outside the stated scopes.

---

## 1.  What I did

Per Note 0456 §9 ("**Start with Option A** -- read paper2's primitive
definition"), I read the actual theorem statements in `paper2.tex`:

* `thm:no-full-base-closure` (line 2406)
* `thm:universal-K10` (line 1416)
* `thm:caseC-K10` (line 1571)
* `thm:dyadic-tail-scale-lift` (line 2424)
* `conj:sparse-worst` (line 2121)
* `rem:sparse-worst-action-orbit-nonstab` (line 2195)

---

## 2.  paper2's exact scopes (as written)

### 2.1  `thm:no-full-base-closure` (the LOCAL closure I had been extending)

> Fix the folded model $L_2 = \mu_{16}$ (cyclic of order 16, four quarter
> blocks).  Let $S \subset L_2$ have $|S| = 8$ and call $S$ \emph{no-full}.
> Let $(a_1, a_2, a_3) \subset [k_2, n_{\max})$ be a strict above-Johnson
> **3-support** in the legal $C(48, 3)$ window with $n_{\max} = 64$.
> Then no $\alpha \in \overline{\mathbb{Q}}^3$ produces a primitive rank-2
> saturated component...

**Two scope restrictions**:
1. **Base panel only**: $L_2 = (16, 4)$, NOT deployment $L_2 = (32, 8)$.
2. **3-support pencils only**: $(a_1, a_2, a_3)$, NOT K-support for K ≥ 4.

### 2.2  `thm:universal-K10` (the headline)

> Let $f \in \FF_q^{n_0}$ be **three-position sparse** and above the Johnson
> radius on $L_0$ at rate $\rho = 1/4$.  Then $K(f) \leq 10$ unconditionally
> at every deployment scale up to $(2^{19}, 2^{17})$.

Scope: $\hat f$ has exactly 3 nonzero positions.  By sparse-propagation
(`lem:sparse-propagation`), the post-fold-2 pencil on $L_2$ has support
size ≤ 3.

### 2.3  `thm:dyadic-tail-scale-lift`

Scale-lifts only the **single-monomial tail-vanishing** ($\mathrm{tail}_S(x^e) \neq 0$),
NOT the full primitive rank-2 closure for K ≥ 4.

### 2.4  `conj:sparse-worst` (open Q2, the only conditional gap)

For ARBITRARY $(f_1, f_2)$, the max $K(f_1, f_2; \delta)$ equals the
3-position-sparse max, **provided** $(f_1, f_2)$ is:
- Strictly above Johnson, AND
- **Action-non-stabilised**: support not pointwise-fixed by
  $\langle \omega^{b-a} \rangle$ for any fold pair $(a, b)$.

The known $K = q$ paired-circuit obstruction at $L_2 = (16, 4)$ is excluded
by EITHER of:
- (i) Action-orbit stabilisation (support sits in fold quadrants $\{0, 2\}$).
- (ii) Johnson-boundary (agreement = $\sqrt{n_1 k_1}$ exactly, not strict).

---

## 3.  Where my "residual" actually lives

The K=14, 16 random-S rank-def cases at $L_2 = (32, 8)$ that Note 0455
flagged as "potentially primitive rank-2 K=16 > 10" sit at:
- $L_2 = (32, 8)$ deployment scale (NOT base $(16, 4)$).
- Joint support size K = 16 (NOT 3).
- Coefficient vector $c \in \FF_p^{16}$ (NOT 3-coef pencils).

**Therefore**:

| paper2 statement | In scope? | Conclusion |
|---|---|---|
| `thm:no-full-base-closure` | NO -- base only, K=3 only | not a counter-example |
| `thm:universal-K10` | NO -- assumes 3-pos sparse $\hat f$ | not a counter-example |
| `thm:dyadic-tail-scale-lift` | NO -- single-monomial tail | not a counter-example |
| `conj:sparse-worst` | MAYBE -- arbitrary $f$ allowed | requires further verification |

Note 0455 was wrong to label these cases "PRIMITIVE rank-2 K=16 > 10" as if
they refute paper2.  paper2's K ≤ 10 quantifier is over ($\hat f$ 3-pos sparse,
strict above-J), and my K=16 pencils don't enter that quantifier at all.

---

## 4.  Could they refute `conj:sparse-worst`?

To be a counter-example to the sparse-worst conjecture, my K=16 (8,8)
cross-side pencils would need to:

(A) Lift to an actual $(f_1, f_2)$ pair with $\hat f_i$ having $\geq 16$
    nonzero positions (so they're not 3-position-sparse).
(B) Be **strictly above Johnson** (not boundary).
(C) Be **action-non-stabilised** (cyclotomic-action mixing on support).
(D) Achieve $K(f_1, f_2; \delta) > 10$.

My investigation establishes only (A) trivially and the rank-deficiency of
$M_S$.  It does NOT measure $K(f_1, f_2; \delta)$ for the lifted $(f_1, f_2)$,
nor verify (B), (C).

**Most likely outcome**: my K=16 rank-def cases produce $K(f_1, f_2; \delta) =
O(1)$ (small, probably 1-2 per kernel dimension), well within the conjectured
bound.  The "rank-deficient $M_S$" structure is generically MUCH weaker than
"$K = q$ saturating obstruction".

The `rem:sparse-worst-action-orbit-nonstab` exclusions (action-orbit + Johnson
boundary) are precisely the mechanisms that historically produced large-K
obstructions; they were already filtered out of the conjecture.  No new
deployment-scale K-blowup is predicted by my finding alone.

---

## 5.  Revised L3 status (replacing Note 0455's claim)

**OLD (Note 0455, overcorrected)**: "~90% structural + ~10% K=14, 16 PRIMITIVE
rank-2 residual; potentially refutes paper2 K ≤ 10."

**NEW (correct)**: paper2's `thm:no-full-base-closure` is at base $L_2 = (16, 4)$
for 3-support pencils.  The "L3 100% structural" framing was MY extension,
not paper2's claim.  My Q-Class Decomposition + (1±t^{n_2/2}) Extension
framework (Notes 0453--0454) IS a genuine extension to deployment scale, and
the ~90% coverage is real.

The residual ~10% (K=14, 16 random no-full S rank-def cases) is honest open
work for the SCALE-UPLIFTED no-full-primitive closure at deployment scale --
an EXTENSION of paper2 that isn't required by paper2's stated theorems but
would strengthen them.

paper2's stated theorems are unaffected.  paper2's open conjecture
(`conj:sparse-worst`) remains open; my residual cases COULD be relevant but
require additional analysis (lift to $(f_1, f_2)$, measure actual $K$, check
exclusion conditions) before any claim of refutation can be made.

---

## 6.  What this resolves and what remains

**Resolves**:
- Note 0455's worry that K=16 cases refute paper2 K ≤ 10.  They don't, by scope.
- The handoff Note 0456 §1 worry "~10% honest residual".  It's still ~10%
  open as deployment-scale extension work, but not a paper2 hole.

**Remains open** (research-grade, not paper2 critical):
- Does the Q-Class Decomposition + (1±t^{n_2/2}) Extension framework
  generalize to ALL no-full $S$ at $L_2 = (n_2, n_2/4)$ with K up to
  $n_2/2$?  Currently ~90% covered structurally.
- For the residual K=14, 16 random-S cases: do they produce
  action-non-stabilised, strictly-above-J $(f_1, f_2)$ pairs with
  $K(f_1, f_2; \delta) > 10$?  Empirically unlikely; would need direct
  measurement.

---

## 7.  Recommended next steps

Two cheap follow-ups (each 0.5--1 day):

**(B-lite)** For the 23 K=16 (8,8) random-S rank-def cases: lift each to a
    candidate $(f_1, f_2)$ and measure $K(f_1, f_2; \delta)$ at the
    appropriate $\delta$.  If $K \leq 10$ for all 23: the residual is
    confirmed non-threatening.  If any $K > 10$: investigate further.

**(C)** Run 5x larger random-S sample (~7500 instead of 1500) at K=16 to
    verify the 1.5% rate is stable.  If it drops sharply: artifact.

I recommend starting with (B-lite): it's the direct test of whether the
residual matters at all.

---

## 8.  Files touched

* This note: `0457-Option-A-paper2-scope-resolves-K16-residual.md`
* To-be-updated: `0455-FINAL-honest-unified-theorem-status.md` (correction note)
* MEMORY index update.

---

## 9.  Strategic position after Option A

* paper2 stated theorems: **all intact**.
* paper2 K ≤ 10 headline: **unaffected** by my K=16 deployment-scale findings.
* paper2 sparse-worst conjecture: **still open**, possibly probable from
  my K=16 cases but only via additional measurement.
* Q-Class Decomposition + (1±t^{n_2/2}) Extension: **genuine deployment-scale
  extension** of the LOCAL closure framework, ~90% coverage at $L_2 = (32, 8)$.
* Residual K=14, 16 cases: **research-grade open**, not paper2-blocking.

Net: the morning's "L3 100% structural" framing was over-stated, but the
"residual is a paper2 counter-example" framing was ALSO over-stated.  The
honest position is: ~90% deployment-scale extension complete, ~10% open as
extension work (not a paper2 hole).
