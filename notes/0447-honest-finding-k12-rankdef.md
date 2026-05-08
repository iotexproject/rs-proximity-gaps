# Note 0447 -- HONEST FINDING: Side-Row Vanishing FAILS at $k=12$ at $L_2=(32, 8)$

**Date:** 2026-05-03 morning (Tier 3 deployment-scale rigor — caveat)
**Branch:** `main`
**Status:** Empirical scan reveals that the Side-Row Vanishing Lemma's
$k$-vec rank-$k$ claim FAILS at $k = 12$ (full same-side) at
$L_2 = (32, 8)$.  This is a real gap in the closure framework for
24-supp at this scale.

---

## 1.  Empirical finding

Script `issue419_uside_full_kvec_n32.py` and
`issue419_uvside_k12_check.py`:

For 500 sampled no-full S at $L_2 = (32, 8)$:
- u-side k=12 (full u-side, all 12 monomials): rank-def at **20/500 ≈ 4%** of S.
- v-side k=12: rank-def at **same 20/500 S** (joint).
- Cross-prime: same 20 S at $q \in \{97, 193, 257\}$ — **prime-uniform**.

For $k \in \{5, 6, 7, 8, 9, 10, 11\}$ same-side u-side: 0 rank-def
(empirical at all primes).  Side-Row Vanishing Lemma holds for these $k$.

For $k = 12$: **Lemma FAILS** at structural ~4% of no-full S.

---

## 2.  Implication for Note 0438 framework

Note 0438's Cases A-D for $k$-supp closure:
- Case D ($\min(u, v) \ge 3$): Side-Row Vanishing applied to smaller side
  → smaller-side row vanishes → reduces to side-pure (Case A).

For $k$-supp $\le 23$: $\min(u, v) \le 11$.  Side-Row Vanishing for $k \le 11$
holds → Case D closes.

For $k$-supp $= 24$: $u = v = 12$.  Side-Row Vanishing for $k = 12$ FAILS.
Case D **does NOT directly close**.

Hence the closure at $k = 24$ at $L_2 = (32, 8)$ has a real gap.

---

## 3.  What the 12-vec rank-def means

For 12-vec same-side rank-def at S: there exists nontrivial
$(c_8, c_9, c_{12}, c_{13}, c_{16}, c_{17}, c_{20}, c_{21}, c_{24}, c_{25}, c_{28}, c_{29})$
with $\sum c_r \mathrm{HT}(t^r) = 0$ in $\mathbb{F}_q^{|S|}$.

I.e., the polynomial $p(t) = \sum c_r t^r$ saturates: $p(\omega^s) = 0$ for
all $s \in S$.

Equivalently: there exists low-tail polynomial $q(t)$ of degree $< k_2 = 8$
such that $p(t) \equiv q(t) \pmod{g_S(t)}$.

This is a CODEWORD-style structure: $p$ (high-tail combo) equals $q$
(low-tail) mod $g_S$.

---

## 4.  Does this give a primitive rank-2 obstruction?

For paper2's K ≤ 10 to be challenged: need a primitive rank-2 W(α) with
joint saturation.

For 12-vec u-side saturation at S: $u_\alpha$ (with α-twist on q=1 odds)
saturates as some specific kernel vector.

For 12-vec v-side saturation at SAME S: $v_\alpha$ saturates similarly.

For $W(\alpha) = (u_\alpha, v_\alpha)$ to have rank 2 over $\mathbb{F}_q[\alpha]$:
need $u_\alpha, v_\alpha$ as polynomial-in-α 2-vectors to be linearly
independent.

**This is a separate question from the 12-vec rank-def.**  Need additional
empirical or structural analysis.

---

## 5.  Side-pure exclusion

paper2's `thm:no-full-base-closure` says every saturated no-full candidate
is either zero-row or side-pure (rank ≤ 1).

For our 12-vec u-side saturation: support entirely on u-side (q=0 + q=1).
So **side-pure**.

By paper2's exclusion: rank $W \le 1$.  **Not primitive rank 2**.

Hence the 12-vec u-side saturation does NOT give a primitive obstruction
on its own.

For the joint 24-supp case (u-side AND v-side both saturated): rank can
be 2.  Need to check if it's also subject to paper2's exclusions.

---

## 6.  Proposed closure for $k = 24$ at $L_2 = (32, 8)$

If 24-supp obstruction exists with both sides saturated and rank 2:
- Check action-orbit stabilization (paper2 Remark `rem:sparse-worst-action-orbit-nonstab`).
- Check dyadic stabilizer triviality.
- Check mixed parity in BOTH rows.

Empirically (paper2's 4.6M certs at deployment scale): no primitive
obstruction found.  So either:
(a) The 12-vec joint rank-def doesn't lift to primitive rank-2 (likely
    via action-orbit stabilization at these specific S).
(b) Or the empirical missed them.

For full rigor: need to compute the kernel vectors at the 20 S and verify
the action-orbit / stab criteria.

---

## 7.  Honest update to Note 0438

The Side-Row Vanishing Lemma should be stated as:
> **Lemma (Side-Row Vanishing, REVISED).**  For $k \in \{2, ..., 11\}$
> at $L_2 \in \{(16, 4), (32, 8)\}$ (and analogous bounds at higher
> scales): every $k$-vec same-side has rank $k$ at every no-full S.

For $k$ above the "Lemma threshold" (k = 12 at L_2=(32, 8); analogously
at higher scales): rank-def occurs at some specific S, requiring
additional analysis (action-orbit / paper2's existing exclusions).

---

## 8.  Updated rigor table

| Configuration | Status |
|---|---|
| Q2 LOCAL at $L_2 = (16, 4)$ all support | THEOREM (Notes 0438-0440) |
| Q2 LOCAL at $L_2 = (32, 8)$, supp ≤ 23 | THEOREM via Cases A-D + Lemma for k ≤ 11 |
| Q2 LOCAL at $L_2 = (32, 8)$, supp = 24 | **GAP**: needs action-orbit analysis at the 20 special S |
| Q2 LOCAL at $L_2 \ge (64, 16)$ | Narrow Lemma + empirical (Notes 0441, 0444) |

The "supp = 24" gap at $L_2 = (32, 8)$ corresponds to "joint full
saturation".  Likely closed by paper2's existing action-orbit
stabilization exclusion, but needs explicit verification.

---

## 9.  Files

* This Note: `0447-honest-finding-k12-rankdef.md`.
* Scripts: `issue419_uside_full_kvec_n32.py`, `issue419_uvside_k12_check.py`.

---

## 10.  Strategic implication

This is an HONEST CAVEAT to the morning's progress. The structural rigor
at L_2=(32, 8) is for support sizes up to 23; the corner case (24 = full)
needs additional analysis.

For paper2 v22: should mention this caveat and the proposed action-orbit
closure path.

For the prize claim: K ≤ 10 at L_2=(32, 8) for support ≤ 23 is now
structurally rigorous (this morning's contribution).  For support = 24,
inherit paper2's existing empirical position (4.6M certs, 0 counter-examples).

This morning's progress remains substantial despite the honest caveat.
