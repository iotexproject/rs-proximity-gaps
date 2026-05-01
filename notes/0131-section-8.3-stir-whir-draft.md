# Note 0131 — §8.3 draft: STIR / WHIR extension via the Berlekamp realizer

**Date**: 2026-04-30
**Status**: draft for paper 3 §8.3, expanding the current "two routes"
hedged sketch into a concrete literature-grounded analysis.
**Builds on**: research subagent literature search (2026-04-30,
spanning BCIKS-2020, BCIKS-2025, STIR ACFY24a, WHIR ACFY24b,
secbit.io WHIR notes, gfenzi.io STIR summary).

---

## Key facts established by literature search

1. **All three protocols (FRI, STIR, WHIR) share the same per-round
   commit-side proximity-gap kernel `poly(n)/|F|`.** Improvements to
   the kernel (e.g., BCIKS-2025's `O(n/|F|)` over BCIKS-2020's
   `O(n²/|F|)`) flow into all three.

2. **STIR's `k` is the FRI folding parameter, not a batching factor.**
   No s-fold interleaved-codeword combination on the commit side —
   STIR's wins are on QUERY count via rate-improving quotients, not
   commit-side soundness sharpening.

3. **WHIR uses a strengthened *mutual correlated agreement* (MCA)
   assumption** (ACFY24b Conjecture 1): the same agreement set must
   work for every codeword in the linear combination. Proven up to
   the unique-decoding radius; conjectured up to capacity.

4. **BCIKS-2025 (eccc 2025/169, Thm 1.5)** sharpened the original
   BCIKS-2020 commit-side bound from `O((ηρ)^{-7} n²/|F|)` to
   `O_{η,ρ}(n/|F|)` via an improved Berlekamp-Welch / Guruswami-Sudan
   analysis: from `a = O(n²)` exceptional `z`'s to `a = O(n)`.

---

## Draft for paper 3 §8.3

**§8.3 Extension to STIR and WHIR**

Production STARK protocols increasingly use STIR~\cite{STIR}
(Arnon-Chiesa-Fenzi-Yogev 2024) and WHIR~\cite{WHIR}
(Arnon-Chiesa-Fenzi-Yogev 2024) as proximity tests in addition to or
in place of FRI. The two protocols share the same per-round
commit-side primitive as FRI — a single-round fold check on a
syndrome pair $(s_1, s_2)$ — and the codim equality
Theorem~\ref{thm:main} applies directly to that primitive. The
question is how the per-round bound composes with each protocol's
recursion / outer-reduction structure.

### STIR

STIR retains FRI's commit-side primitive without modification. Its
contribution is on the QUERY axis: each round shrinks the evaluation
domain by $|L_{i+1}| = |L_i|/2$ while folding by $k$, so the rate
$\rho_i = (2/k)^i \rho$ falls geometrically and per-round query
counts shrink. The commit-side bound per round is the same BCIKS-style
$\mathrm{poly}(n) \cdot |F|^{-1}$ as in FRI~\cite{BCIKS, BCHKS}; under
hybrid R2 framing (\S\ref{sec:R1R2}), this is the operative bound.

Under R1 framing (with explicit Welch-Berlekamp list-decoding at the
folded last layer, see \S\ref{sec:R1Berlekamp}), Theorem~\ref{thm:main}
applies to STIR's per-round commit-side primitive identically:
$\eps^{R1}_{commit, STIR} \leq \mathrm{poly}(n, c) \cdot |F|^{-2(c-1)}$,
conditional on Lemma~A. Composition over $R = \log_2 n$ rounds adds at
most $\log_2 R$ bits, sub-leading to the codim exponent at deployment
scale.

### WHIR

WHIR's per-round commit-side primitive is **not** identical to FRI:
each round runs (i) $k$ rounds of multilinear sumcheck on the weight
constraint of a Constrained Reed-Solomon code, (ii) a STIR-style
folded oracle on a halved domain $L^{(2)}$, and (iii) out-of-domain +
shift queries. The proximity-gap kernel is a generalised
$(1-\delta)^t + \mathrm{poly}(2^m, 1/\rho)/|F|$, with sumcheck
soundness composing additively at $O(km/|F|)$ — sub-leading to the
proximity-gap term.

WHIR additionally requires a **strengthened mutual correlated
agreement (MCA) assumption** (\cite{WHIR} Conjecture~1): the same
agreement set must work for every codeword in the linear combination.
Proven up to the unique-decoding radius; conjectured up to capacity.
Theorem~\ref{thm:main}'s codim bound on $V_{\mathrm{bad}}$ does not
directly imply MCA at arbitrary radius — MCA is a stronger statement
about the joint agreement structure of multiple codewords, not the
single-syndrome event $V_{\mathrm{bad}}$.

Under R1 framing, the codim improvement applies to the per-round
commit-side primitive of WHIR identically to FRI; the MCA assumption
remains independent. Whether the codim-based analysis here can sharpen
MCA (or, conversely, whether MCA implies a sharper codim than the
$2(c-1)$ proven in Theorem~\ref{thm:main}) is open.

### Numerical summary

The headline-row deployment impact of this paper, in the hybrid
R1+R2 framing, applies uniformly to FRI, STIR, and WHIR:

\begin{center}
\small
\begin{tabular}{lcccc}
\toprule
Protocol & R2 commit (BCIKS) & R1 commit (Berlekamp) & R1 improvement \\
\midrule
FRI~\cite{BCIKS, BCHKS} & $\mathrm{poly}(n)/|F|$ & $|F|^{-2(c-1)}$ & $|F|^{c-2}$ \\
STIR~\cite{STIR}        & same                   & same             & same \\
WHIR~\cite{WHIR}\textsuperscript{\dag} & same   & same             & same \\
\bottomrule
\end{tabular}
\end{center}

\textsuperscript{\dag} WHIR additionally requires its mutual
correlated agreement (Conjecture 1 of~\cite{WHIR}); the codim
improvement composes with MCA, but does not imply MCA at higher
radii.

### Two open follow-ups

1. **MCA + codim bridge.** Whether the codim-based analysis of
   $V_{\mathrm{bad}}$ here can establish MCA at radii beyond the
   unique-decoding bound, closing WHIR Conjecture 1.

2. **Sharper STIR / WHIR commit-side via BCIKS-2025.** The recent
   BCIKS-2025 sharpening~\cite{BCHKS} (Theorem 1.5: $O_{\eta, \rho}
   (n/|F|)$ vs the original $O(n^2/|F|)$) propagates to STIR and WHIR
   per-round bounds. A combined analysis using BCIKS-2025 for R2 and
   Theorem~\ref{thm:main} for R1 gives, in the hybrid framing, the
   tightest currently-known commit-side bound for each protocol.

---

## What this draft adds vs paper 3's current §8.3

Current §8.3 has a "two routes" sketch: per-round union bound (Route 1)
vs joint batched (Route 2), both honestly hedged. The draft above:

* Adds **specific algebraic structure facts** about each protocol
  (no s-fold for STIR; sumcheck + MCA for WHIR).

* Cites **theorem numbers and constants** (BCIKS-2020 Thm 7.2 vs
  BCIKS-2025 Thm 1.5; WHIR Conjecture 1; STIR's per-round bound).

* Identifies the **MCA + codim bridge** as a concrete open follow-up
  with potential prize-relevance (closing WHIR's Conjecture 1).

* Removes the "we conjecture" hedge in favor of the
  literature-grounded summary table.

---

## Open questions flagged for paper / companion repo

1. **Direct WebFetch failed** for STIR (eprint 2024/390) and WHIR
   (eprint 2024/1586) — IACR returned 403 to subagent. The exact
   theorem numbers in §8.3 should be cross-checked against locally-pulled
   PDFs before paper submission.

2. **STIR's "s-fold combination" question.** The CHECKPOINT spec asked
   whether STIR has an s-fold combination on the commit side that
   would amplify the prefactor. Subagent's reading of the literature:
   no — STIR's `k` is the FRI folding parameter, not a batching
   factor. If the spec had a different STIR variant in mind (e.g.,
   batched STIR), the analysis would change.

3. **MCA framework.** Whether Theorem 3.1 implies MCA at any
   non-trivial radius is a concrete open problem worth flagging for
   the WHIR authors (Arnon, Chiesa, Fenzi, Yogev — note that Fenzi
   is on the prize committee).

---

## Sources (verified by subagent)

- BCIKS-2020 PDF (full): Theorems 1.2, 1.4, 1.6, 1.7, 7.2 verified
  from math.toronto.edu mirror.
- BCIKS-2025 ECCC 169 PDF (full): Theorems 1.3, 1.5, 1.6, 1.9
  verified.
- Arnon-Boneh-Fenzi 2026/680 PDF (full, in `refs/`): proximity-gap /
  CA / MCA framework, Section 4.2 on MCA scaling.
- Xie-Guo "Note on WHIR" (secbit.io): WHIR Definitions 1 and 4.14,
  Claim 4.15, Conjecture 1, full one-iteration protocol diagram.
- gfenzi.io STIR blog post: STIR total-soundness formula,
  query-complexity comparison vs FRI.
- STIR/WHIR primary PDFs: HTTP 403 to subagent; user should pull
  locally for final cross-check.
