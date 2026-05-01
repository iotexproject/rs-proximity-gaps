# Note 0088 — Structural Results on Per-Word List Size

## Overview

These results were originally §8–§9 of the main paper. They are independent of the FRI soundness theorem (Theorem thm:fri-full) and were moved here to streamline the presentation. They provide finer structural information about the per-word list size M, originally aimed at showing M = 0 on all RS-compatible flats (Open Problem 2). Proposition prop:m2-obstruction (in the main paper) shows this is false at deployment-relevant code lengths (n ≥ 32, rate 1/2); the results below remain valid and independently valuable for understanding the list-size landscape.

The results below include:
- §A: Coset extraction on multiplicative subgroups (Golomb-Gong tradition)
- §B: Fiber bound and pinned-pair structure
- §C: Bézout bound for general codimension
- §D: Weighted homogeneity and structural identities
- §E: Irreducibility of the remainder hypersurface (Newton polygon + Gao)
- §F: Codimension bound via fiber dimension (dim V₀₁₂ ≤ w−3)
- §G: Incidence bound for list size (M ≤ C(n,d)/C(w,d))
- §H: Bivariate coprimality (conjectural, verified w ≤ 7)
- §I: Assembly of list-size bounds at FRI parameters

## Status

- All theorems and lemmas are proved (except Conjectures 1-2 in §H, which are computationally verified for w ≤ 7, n ≤ 30)
- Computational verification scripts are in notes/scripts/
- The Fisher bound (Thm list-size-k2) and Frankl-Wilson bound (Thm frankl-wilson) remain in the main paper as compressed remarks
- The second moment theorem (Thm second-moment) and error-locator normal identity (Lem locator-normal) remain in the main paper as §7 core

## LaTeX Source

The full LaTeX source of the removed sections is preserved below for future use (e.g., companion paper, appendix expansion).

---

[LaTeX content follows — this is the material from former §8 "Coset Extraction on Multiplicative Subgroups" and §9 "Fiber Bound and Pinned-Pair Structure" of paper.tex, removed in the restructuring of 2026-04-24.]
