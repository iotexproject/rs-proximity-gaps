# Q1 ↔ Number Theory Literature: Bridge Audit

**Date:** 2026-05-06
**Source paper:** `/Users/raullenstudio/work/EF1M/paper2.tex` §§1481–1612, 3499–3520
**Q1 (paper):** For every $d = 2^j$, $j \geq 2$, $R_d := -3 x_{d/2} + 2 V_{d/2} + 3 W_{d/2}$ does not vanish identically on $V_d^{\mathrm{prim}}$. Equivalently $\mathrm{Norm}_{K_d/\mathbb{Q}}(F_d(\alpha)) \neq 0$.

## Headline verdict

**No literature problem provides a clean 1-to-1 equivalence with Q1.** Q1 is a structurally novel non-vanishing question whose data ($V_d^{\mathrm{prim}}$, the chain ideal, the polynomial $R_d$) does not coincide with the inputs of any named conjecture I located. The closest matches are *literature-shape* analogues. I recommend paper2 should cite Q1 as a **standalone non-vanishing problem** with literature-flavor parallels in three named families, rather than claim equivalence.

## Three best candidates

### Candidate A — Greenberg's conjecture (cyclotomic $\mathbb{Z}_2$-extensions)

- **Statement:** For every totally real number field $F$ and prime $p$, the Iwasawa $\lambda$- and $\mu$-invariants of the cyclotomic $\mathbb{Z}_p$-extension vanish; equivalently, the projective limit class-group module $X_\infty$ is finite. The $p = 2$ case for real quadratic / abelian $F$ is the most-studied form.
- **Citation:** Greenberg, "On the Iwasawa invariants of totally real number fields," *Amer. J. Math.* 98 (1976); modern surveys: Mizusawa & Ozaki (Tohoku Math. J. 1997 onward), Fukuda–Komatsu, Itoh–Mizusawa (arXiv 2202.02844, 2310.03543).
- **Status:** Open in general; verified for $F = \mathbb{Q}(\sqrt{f})$, $0 < f < 10^4$ at $p=2$.
- **Verdict:** *Literature-shape only.* Both problems concern non-vanishing/finiteness phenomena along a 2-power tower with self-similar structure, and Q1 carries class-field-theoretic data ($\mathbb{Q}(\sqrt{-D})$, $h = 1{,}709{,}193$) that Iwasawa-theoretic invariants would also produce. **But Q1's $V_d^{\mathrm{prim}}$ is a finite zero-dimensional scheme cut out by a polynomial chain ideal (Newton-symmetric / Vieta-locator), not the inverse limit of class groups.** No precise reduction either direction.

### Candidate B — Kummer–Vandiver conjecture / Kummer's lemma family

- **Statement (Kummer–Vandiver):** $p \nmid h^+(\mathbb{Q}(\zeta_p))$, the class number of the maximal real subfield. Equivalent (Kurihara) to $K_{4n}(\mathbb{Z}) = 0$.
- **Citation:** Kummer (1849, letters to Kronecker); Vandiver (1920s); Kurihara, "Some remarks on conjectures about cyclotomic fields and K-groups of $\mathbb{Z}$," *Compositio Math.* 81 (1992); Stolin, "Vandiver's Conjecture via K-theory" (arXiv 2001.09702).
- **Status:** Open. Verified for $p < 1.6 \times 10^8$.
- **Verdict:** *Literature-shape only.* Both ask non-vanishing/non-divisibility of an arithmetic invariant attached to cyclotomic data. Both are computationally verifiable per-instance. **But Kummer–Vandiver is a divisibility (mod $p$) statement about a class number, while Q1 is the non-vanishing (over $\mathbb{Q}$) of a single resultant-type integer.** The shapes are parallel; the bridge is not algebraic.

### Candidate C — Stark non-vanishing of regulators (rank-one abelian Stark)

- **Statement:** For an abelian extension $K/k$ with appropriate $S$, the leading Taylor coefficient of $L_S(s, \chi)$ at $s=0$ equals (Stark unit regulator) $\times$ (algebraic constant); the regulator is conjecturally nonzero, equivalently the predicted Stark unit is a true unit.
- **Citation:** Stark, "L-functions at $s=1$. IV," *Adv. Math.* 35 (1980); Tate, *Les conjectures de Stark sur les fonctions L d'Artin en s=0*, Birkhäuser 1984; Dasgupta–Greenberg AWS 2011 notes; Dasgupta–Kakde–Ventullo, "On the Gross–Stark Conjecture," *Ann. Math.* 188 (2018).
- **Status:** Open in general; rank-one abelian case proven by Dasgupta–Kakde for the integral refinement (Brumer–Stark, 2020).
- **Verdict:** *Literature-shape only.* Stark's conjecture also predicts a specific algebraic non-vanishing inside a class-field-theoretic setup, and the "Hilbert class field of degree $\sim 3.4 \times 10^6$" mentioned in paper2 §3514 is exactly the kind of object Stark predicts units inside. **But paper2 explicitly notes (§3513–3515) that the naive Stark / Davenport–Hasse / Hecke L-value route is *infeasible* due to Hilbert class field degree.** This rules out Stark as a precise bridge — Q1's residue field $K_d$ is not a known Stark base field, and $F_d(\alpha)$ is not a known Stark unit.

### Honorable mentions (rejected)

- **Ferrero–Washington theorem ($\mu = 0$):** *Theorem*, not conjecture, and concerns $\mu$ not $\lambda$. No bridge.
- **Kolyvagin's conjecture (non-vanishing of derived Heegner classes):** Different category — modular-form / Selmer setting, not a polynomial resultant non-vanishing.
- **Lehmer's conjecture (Mahler measure):** Bound on a measure, not a non-vanishing of a specified expression. Wrong shape.
- **Cohen–Lenstra heuristics:** Probabilistic, not a precise non-vanishing.
- **Bombieri–Lang:** About rational point density on varieties of general type. Q1's $V_d^{\mathrm{prim}}$ is zero-dimensional, of *unrestricted* general type. Wrong category.

## Recommendation for paper2 §Open Q1

**Do not claim equivalence with any named conjecture.** Cite Greenberg (Cand. A) as the closest *family-shape* analogue and note explicitly:

> "Q1 has the shape of a Greenberg-style $\mathbb{Z}_2$-tower non-vanishing along a self-similar dyadic chain. Unlike Greenberg, Q1 lives on a finite zero-dimensional scheme $V_d^{\mathrm{prim}}$ with explicit chain ideal; we know of no precise reduction in either direction."

A secondary citation to Kummer–Vandiver (per-instance computational verification, no structural proof) would honestly characterize Q1's status.

## Bridge formula

**No clean bridge.** Best honest formulation:

> Q1 belongs to the family of "non-vanishing of explicit class-field-theoretic invariants along $\mathbb{Z}_2$-towers with self-similar structure," whose canonical exemplars are Greenberg's $\lambda = 0$ conjecture and the Kummer–Vandiver conjecture. Q1 is not known to be a special case, generalization, or consequence of either.

## What we'd need to prove a real bridge

1. **For Greenberg-equivalence:** Construct a tower of class groups $\{A_d\}$ along the chain $V_d^{\mathrm{prim}} \hookrightarrow V_{2d}^{\mathrm{prim}}$ such that $R_d = 0$ on $V_d^{\mathrm{prim}}$ corresponds to a non-trivial element of $\varprojlim A_d$. This requires interpreting $V_d^{\mathrm{prim}}$ as a Spec of a class field rather than as a Newton-symmetric variety — currently no such interpretation is known.
2. **For Stark-equivalence:** Show $\mathrm{Norm}_{K_d/\mathbb{Q}}(F_d(\alpha))$ equals a value (or leading coefficient) of an Artin / Hecke $L$-function attached to $K_d$. Paper2 §3513–3515 explicitly says the Hilbert class field has degree $\sim 3.4 \times 10^6$ which makes this **computationally infeasible** at $d = 4$ already; structurally, $F_d$ is a Vieta locator, not a known Stark expression.
3. **For Kummer–Vandiver-shape:** Show $\mathrm{Norm}(F_d(\alpha))$ is divisible by $p$ ⇔ specific class-group condition. No such bridge known.

The honest deliverable for paper2 is: **Q1 is a new non-vanishing question in the same neighborhood as Greenberg / Kummer–Vandiver, but neither subsumes it and neither is reducible to it.**
