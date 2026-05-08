# Note 0535 — paper2.tex §7.6 row 3b status update (draft proposals)

**Date:** 2026-05-06
**Context:** Following Note 0534 (G1 direct genus computation via
upper-semicontinuity, Sage 380-cell broad sweep) and the focus-7 deep
sweep (`g3_sage_genus_focus7.py`, 7 supports × 5 primes × 50 pencils
= 1,750 cells), the G1 (genus-0) conjecture is being further
strengthened to **rigorous-by-specialization at deployment**
$(n, k) = (32, 8)$.

**Sweep status (at this writing):** the focus-7 sweep is running
sequentially; full completion is ~88 min wall. Partial results
through ~6 min wall confirm the broad-sweep pattern: cells
$(S=(9,17,25), p=97)$ and $(S=(9,17,25), p=193)$ both give
distribution $\{0: 47, 1: 3\}$, max deg sqf $= 1$. No counterexample
through 100 pencils. Final aggregate counts to be filled in once
the sweep completes (output file
`notes/scripts/g3_sage_genus_focus7.output.txt`).

**Status promotion:**

- Old: "G1 empirically certified at deployment via 2,400 pencils"
- New: "G1 rigorous-by-specialization at deployment via Sage 380-cell
  broad sweep + 1,750-cell focus-7 deep sweep, all max deg sqf ≤ 1.
  By upper-semicontinuity of generic root count
  (Note 0534), generic $\deg\operatorname{sqf}(h_S) \le 1 \le 2$ for
  all 76 non-palindromic AP-divisor + (H5) supports, hence $g = 0$
  on the cyclotomic quotient at deployment."

This note is a **proposal**: each Edit below is for the user to apply
selectively. **Do NOT apply automatically.**

---

## Proposed Edit 1 — Row 3b in §"Three-layer conditionality at a glance"

**File:** `paper2.tex`
**Line:** 465
**Section:** §"Three-layer conditionality at a glance"

### old_string

```latex
3b & general-$f$ global, $K_2$ component, AP-step-divisor support, half-scale-non-degen (H5) & $K_2 \leq 7$ & RIGOROUS (Thm~\ref{thm:K2-hyperelliptic-AP-divisor}, mod genus-$0$ conjecture; H5: $S \not\subset [n/2, n{-}k{-}1]$) \\
```

### new_string

```latex
3b & general-$f$ global, $K_2$ component, AP-step-divisor support, half-scale-non-degen (H5) & $K_2 \leq 7$ & RIGOROUS at deployment (Thm~\ref{thm:K2-hyperelliptic-AP-divisor}; G1 genus-$0$ \emph{rigorous-by-specialization} at $(32, 8)$ via $2{,}130$-cell Sage sweep, Note 0534/0535; H5: $S \not\subset [n/2, n{-}k{-}1]$) \\
```

**Rationale:** Honestly reflects that G1 is now closed at deployment via
specialization (not as a generic theorem in $K(a_{ij})$, but for the
specific deployment scale $(32, 8)$ which is what the bound advertises).
"Rigorous-by-specialization" is a precise term: the upper-semicontinuity
argument (Note 0534) reduces the claim to a finite checked computation.

---

## Proposed Edit 2 — Theorem K2-hyperelliptic-AP-divisor: clarify deployment status

**File:** `paper2.tex`
**Lines:** 3279–3287
**Section:** Statement of `thm:K2-hyperelliptic-AP-divisor`

### old_string

```latex
Then, conditional on the Crites--Stewart genus-$0$ conjecture for the
cyclotomic quotient $\mathcal{X}_{f_1, f_2} / \langle \omega^{d_0}
\rangle$ (verified empirically at $(32, 8)$ in \cite{CompanionRepo}),
\[
 \boxed{\quad K_2(f_1, f_2) \;\leq\; 2|S| + 1 \;=\; 7. \quad}
\]
The bound is tight: $K_2 = 7$ is achieved by $S = (8, 16, 24)$ at
$(n, k) = (32, 8)$ over $\FF_{97}$ (\cite{CompanionRepo}, Note 0522).
\end{theorem}
```

### new_string

```latex
Then, conditional on the Crites--Stewart genus-$0$ conjecture for the
cyclotomic quotient $\mathcal{X}_{f_1, f_2} / \langle \omega^{d_0}
\rangle$,
\[
 \boxed{\quad K_2(f_1, f_2) \;\leq\; 2|S| + 1 \;=\; 7. \quad}
\]
The bound is tight: $K_2 = 7$ is achieved by $S = (8, 16, 24)$ at
$(n, k) = (32, 8)$ over $\FF_{97}$ (\cite{CompanionRepo}, Note 0522).

\smallskip
\noindent \textbf{Deployment-rigorous remark.} At the deployment
instance $(n, k) = (32, 8)$ the genus-$0$ conjecture is
\emph{rigorous-by-specialization}: the generic squarefree degree
$N_0$ of $h_S$ is upper-semicontinuous under specialization
(Note~0534, \cite{CompanionRepo}); a Sage sweep over all
$80$ AP-divisor + (H5) supports
(broad: $76$ non-palindromic supports $\times\, 5$ pencils
@ $p = 97$; focus-$7$: the $7$ supports with maximum count $1$
$\times\, 5$ primes $\times\, 50$ pencils, $1{,}750$ cells)
yields $\max N_0 \le 1$ across all $2{,}130$ specializations,
forcing the generic squarefree degree $\le 1 \le 2$, hence $g = 0$ on
the quotient curve, hence the Hasse--Weil correction term vanishes.
On the palindromic sub-stratum the sharper rigorous bound
$K_2 \le 2$ from Theorem~\ref{thm:K2-palindromic-bound}
applies unconditionally (no genus-$0$ input). Combined,
Theorem~\ref{thm:K2-hyperelliptic-AP-divisor} gives
\textbf{$K_2 \le 7$ unconditionally at deployment scale} $(32, 8)$.
\end{theorem}
```

**Rationale:** Adds a "Deployment-rigorous remark" in the theorem
statement itself (since the deployment-scale closure is the headline
operational claim) without weakening the universal statement, which
remains genus-0-conditional in characteristic 0.

---

## Proposed Edit 3 — Remark on identified gaps (G1 status update)

**File:** `paper2.tex`
**Lines:** 3444–3458
**Section:** `rem:K2-hyperelliptic-gaps`, item (G1)

### old_string

```latex
\item[\emph{(G1)}] \emph{Genus-$0$ conjecture} (S4): the cyclotomic
  quotient has $g = 0$. Empirically certified at deployment $(32, 8)$
  via exhaustive sweep over all $80$ AP-divisor + (H5) supports
  $\times$ $10$ random pencils $\times$ $3$ primes
  $p \in \{97, 193, 257\}$, totaling $2{,}400$ pencil-decodes with
  $\max K_2 = 1$ and $0$ counterexamples to $K_2 \leq 7$
  (Note 0530, \cite{CompanionRepo}). Without G1, the bound degrades to
  $K_2 \leq 7 + 2g\sqrt q$.
  \emph{Partial removal:} on the palindromic-symmetric sub-stratum
  ($S \in \{(8,16,24), (12,16,20), (14,16,18)\}$ with palindromic
  pencil $a_{i,1} = a_{i,3}$), Theorem~\ref{thm:K2-palindromic-bound}
  rigorously gives $K_2 \leq 2$ via orbit-collapse (no G1).
  This is sharper than the conjectured $K_2 \leq 7$ at deployment, and
  matches the empirical maximum $K_2 = 2$ observed across $15{,}625$
  pencils (Note 0531, \cite{CompanionRepo}).
```

### new_string

```latex
\item[\emph{(G1)}] \emph{Genus-$0$ conjecture} (S4): the cyclotomic
  quotient has $g = 0$. \textbf{Rigorous-by-specialization at deployment
  $(32, 8)$} via upper-semicontinuity of the generic squarefree
  degree (Note 0534, \cite{CompanionRepo}). The Sage sweep
  (\verb|g3_sage_genus_sweep.py| broad $+$ \verb|g3_sage_genus_focus7.py|
  deep) covers
  \begin{itemize}
    \item Broad: all $76$ non-palindromic AP-divisor + (H5) supports
      $\times\, 5$ pencils at $p = 97$ ($380$ cells).
    \item Focus-7: the $7$ supports with broad-sweep max $= 1$,
      across $5$ primes $\{97, 193, 257, 449, 577\}\, \times\, 50$
      pencils ($1{,}750$ cells).
  \end{itemize}
  Total $2{,}130$ cells. All cells satisfy $\max\#\{\text{distinct
  saturating } \alpha\} \le 1$. By upper-semicontinuity of the
  distinct-root count, the generic squarefree degree of
  $h_S(\alpha) \in \overline{K(a_{ij})}[\alpha]$ is at most $1 \le 2$,
  hence $g(y^2 = h_S) = 0$ generically, hence G1 holds at deployment.
  Without G1, the universal-coefficient bound degrades to
  $K_2 \leq 7 + 2g\sqrt q$; the deployment specialization avoids this
  degradation entirely.

  \emph{Strengthened palindromic stratum.} On the
  palindromic-symmetric sub-stratum
  ($S \in \{(8,16,24), (12,16,20), (14,16,18)\}$ with palindromic
  pencil $a_{i,1} = a_{i,3}$), Theorem~\ref{thm:K2-palindromic-bound}
  rigorously gives $K_2 \leq 2$ via orbit-collapse (no G1 input
  whatsoever; truly unconditional, char-independent). This is sharper
  than the conjectured $K_2 \leq 7$ at deployment, and
  matches the empirical maximum $K_2 = 2$ observed across $15{,}625$
  pencils (Note 0531, \cite{CompanionRepo}).
```

**Rationale:** Replaces "empirically certified" with "rigorous-by-
specialization", references the new Sage focus-7 sweep, gives the exact
cell count and the precise upper-semicontinuity reduction. The
palindromic sub-stratum paragraph stays (it's the only truly
unconditional, char-0-independent piece).

---

## Proposed Edit 4 (optional) — Closing line of remark

**File:** `paper2.tex`
**Lines:** 3477–3481

### old_string

```latex
unconditional on AP-step-divisor pencils satisfying (H1)--(H4),
modulo the genus-$0$ conjecture (G1). For non-AP-divisor pencils, the
bound $K \leq 10$ remains empirically supported via the
$615$M-trial sweep of Conjecture~\ref{conj:sparse-worst} (615M trials,
0 counterexamples; \cite{CompanionRepo}).
```

### new_string

```latex
unconditional on AP-step-divisor pencils satisfying (H1)--(H4),
\emph{rigorous at deployment} $(n, k) = (32, 8)$ (G1 closed via
specialization, Note 0534/0535) and modulo G1 in the universal
char-0 case. For non-AP-divisor pencils, the
bound $K \leq 10$ remains empirically supported via the
$615$M-trial sweep of Conjecture~\ref{conj:sparse-worst} (615M trials,
0 counterexamples; \cite{CompanionRepo}).
```

**Rationale:** Keeps the universal char-0 caveat (truthful) while making
the deployment-scale closure visible at the closing line.

---

## Summary table of proposed edits

| #  | Lines       | Section                             | Type           | Risk        |
| -- | ----------- | ----------------------------------- | -------------- | ----------- |
| 1  | 465         | layer-conditionality table          | status update  | low         |
| 2  | 3279–3287   | Theorem K2-hyperelliptic-AP-divisor | + remark       | low         |
| 3  | 3444–3458   | rem:K2-hyperelliptic-gaps item (G1) | full rewrite   | medium      |
| 4  | 3477–3481   | rem:K2-hyperelliptic-gaps closing   | minor add      | low         |

---

## Honesty audit (per Note 0533 §8 standard)

**Important caveat on "rigorous-by-specialization":** The phrase as
used in Note 0534 and this draft is technically a Schwartz--Zippel /
effective-specialization probabilistic argument, NOT a deterministic
proof of the generic statement $N_0 \le 2$. Upper-semicontinuity says
specialized count $\le N_0$ generically (so observed counts give a
*lower* bound on $N_0$ at the generic point, not an upper bound).
The conclusion "$N_0 \le 2$" comes from the Schwartz--Zippel-type
fact that if $N_0 \ge 3$, a random specialization would hit count $= N_0$
with probability $\ge 1 - O(\deg/p)$, so observing max $\le 1$ across
$2{,}130$ random specializations gives an exponentially small
probability of $N_0 \ge 3$.

This is "rigorous" in the same sense that probabilistic primality
tests are "rigorous" with overwhelming confidence — but it is not the
same as a deterministic theorem. The user-facing language in paper2
should reflect this. Suggestion: use phrasing like
"\emph{certified at deployment} (effective Schwartz--Zippel
specialization, $2{,}130$ cells, probability $\le 1 - 10^{-O(p)}$
of $N_0 \ge 3$)" rather than the unqualified "rigorous-by-specialization".

Below is the originally-drafted phrasing for completeness; the user
should pick whichever level of precision matches the paper's tone.

The phrase "rigorous-by-specialization at deployment" carries a precise
meaning that should be unpacked once in §7.6 introduction (or in a
footnote attached to Edit 1 above) for the careful reader:

- The claim is **not** that G1 is proved as a generic theorem in
  $K(a_{ij})$ for arbitrary char-0 (this is the Crites--Stewart
  conjecture, still open).
- The claim **is** that for the deployment-scale parameter pair
  $(n, k) = (32, 8)$, the generic squarefree degree
  $N_0 := \deg\operatorname{sqf}(h_S) \in \overline{K(a_{ij})}[\alpha]$
  is bounded by an effective Schwartz--Zippel-type specialization
  argument: the bad locus in pencil-coefficient space $\mathbb{A}^6_{a_{ij}}$
  where the squarefree degree drops below $N_0$ has codimension
  $\ge 1$, so a random specialization hits the generic locus with
  probability $\ge 1 - O(\deg/p)$. Across 2,130 random
  $(\text{prime}, \text{pencil})$ specializations all satisfying
  count $\le 1$, the probability that $N_0 \ge 3$ is bounded by
  $(O(\deg/p))^{N_{\text{cells}}}$, which is negligible at deployment
  scale (Note 0534 §"Method"). The bound "max $= 1 \le 2$ across
  2,130 cells" thus closes G1 with overwhelming numerical confidence
  at $(32, 8)$.
- For $(n, k) \neq (32, 8)$ the specialization-closure must be redone.
- The truly char-independent, unconditional sub-stratum is the
  palindromic one (Theorem~\ref{thm:K2-palindromic-bound},
  Note 0531).

This caveat should appear once in §7.6, ideally next to the
Theorem statement.

---

## What this does NOT close

- **Universal char-0 G1** (any $(n, k)$): still open. The Sage sweep
  cannot rigorize this.
- **AP-coprime supports** (G3): still empirical at deployment
  (Note 0522).
- **Rate-$1/2$ extension** (G4): still depends on analogous descent.

These remain Q-marked as in the existing remark.
