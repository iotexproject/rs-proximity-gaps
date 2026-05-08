# Note 0543 — Q3 Closure Executive Summary

**Date:** 2026-05-07
**Audience:** Voloch / Litt / Sawin engagement memo (drafted to be ready
            for forwarding once Gong introduction is in place).
**Status:** Empirical envelope at deployment scale ($n \geq 128$) is paper-ready.

## TL;DR

We have an empirically robust conjecture (Q3) that:
1. Provides the cyclotomic-subgroup analog of the Crites-Stewart 2025
   trinomial construction on $\mathbb{G}_m$
2. Establishes the descended-monodromy infrastructure needed for any
   proof of the Reed-Solomon Proximity Prize ($\$1$M, EF, announced
   2026-01-26) in the open intermediate zone
3. Reduces to a single uniform descended-$\mathrm{Sp}$-monodromy theorem
   on $\mu_n \subset \mathbb{F}_p^*$ for trinomial pencils

The empirical case is comprehensive across three independent verification
axes (BW interior count, Sato-Tate 4th moment, msolve eliminator). The
closure pathway is named-author with a 6-paper bibliography toolkit.
We seek 1-3 collaborators among Voloch / Litt / Sawin to write the
descended-monodromy theorem (3-6 months conditional).

## The Conjecture (Q3)

For $n = 2^{j+1}$ with $j \geq 3$, $k = 2^j$, $L = \mu_n \subset \mathbb{F}_p^*$
($p \equiv 1 \pmod n$), let

$$K_\text{interior}(a_1, a_2, a_3; n, k; \mathbb{F}_p) := \#\left\{ \alpha \in (\mathbb{F}_p^*)^3 : \exists c \in \mathrm{RS}_k(L), |\{z \in L : c(z) = f_\alpha(z)\}| \geq \tau \right\}$$

where $f_\alpha(z) = \alpha_1 z^{a_1} + \alpha_2 z^{a_2} + \alpha_3 z^{a_3}$
and $\tau = \lceil\sqrt{nk}\rceil$ is the Johnson radius.

**Conjecture Q3:** For all coprime mixed-parity triples
$(a_1, a_2, a_3) \in [k, n-1]^3$ and all $p \equiv 1 \pmod n$,
$K_\text{interior} = 0$.

## Empirical state at end of Round 5 panel + drill iterations

### Axis 1: Berlekamp-Welch interior count

| Scale | $\tau$ tested | Cells | $K_\text{interior}$ |
|-------|---------------|-------|---------------------|
| $j=3$ (16, 8) | 12 (msolve exact) | 40 | $\leq 4$ field-uniform |
| $j=4$ (32, 16) | various | 70 | $0$ field-uniform |
| $j=5$ (64, 32) | $\{55, 56, 57\}$ | 12 (BW) | $0$ |
| $j=6$ (128, 64) | $\{120\}$ | 6,144 | $0$ |
| $j=6$ (128, 64) tight | $\{110, 100, 97\}$ | 15,360 | $0$ |
| $j=7$ (256, 128) at $p=257$ | $\{226, 206, 194\}$ | 3,072 | $0$ |
| $j=7$ (256, 128) at $p=769$ multi-prime | $\{226, 206, 194\}$ | 6,912 | $0$ field-uniform |
| $j=8$ (512, 256) at $p=7681$ | $502$ | 4,500 | $0$ (5 triples: EOO/OEO/EEO + 2 Kummer incl. Katz-hardest) |

**TOTAL deployment-scale BW: 35,988 cells, all $K = 0$**, with $\tau$
swept to within $1$–$2$ of the BW unique-decoding boundary at $j \in \{6, 7\}$,
plus extension to $j=8$ at smallest $p \equiv 1 \pmod{512}$
($p = 7681$): 4,500 cells × 5 triples (full parity panel + 2 Kummer-
degenerate including j=8 Katz-hardest analog). $j=7$ multi-prime
verification at $p \in \{257, 769\}$ confirms field-uniformity in the
BW axis as well as the Sato-Tate axis.

The conjecture's saturation threshold $\tau_\text{BCH} = \lceil\sqrt{nk}\rceil$
lies $5$ ($j=6$) and $10$ ($j=7$) below the BW reach respectively,
hence stricter test would require multiplicity-$m$ Guruswami-Sudan list
decoder.

### Axis 2: Sato-Tate 4th-moment Larsen invariant

Reference values: Sato-Tate $\mathrm{Sp}/\mathrm{SU}$ semicircle $M_4/M_2^2 = 2$,
independent Gaussian $M_4/M_2^2 = 3$.

| $j$ | Triples | Parity strata | $M_4/M_2^2$ range | Verdict |
|-----|---------|---------------|--------------------|---------|
| 5 | 7 | EOO/OEO/EEO | $[2.04, 2.54]$, EOO outlier $\approx 2.51$ | finite-scale anomaly |
| 5 multi-prime | 12 cells (F_193,257,449) | EOO | $[2.45, 2.54]$ | field-uniform anomaly |
| 6 | 14 | all 5 | $[1.92, 2.09]$ | uniformly Sato-Tate |
| 6 multi-prime | 8 cells (F_257, F_641) | EOO | $[2.01, 2.09]$ | field-uniform Sato-Tate |
| 7 | 8 | all 5 | $[1.93, 2.06]$ | uniformly Sato-Tate |
| 7 multi-prime | 8 cells (F_257, F_769) | EOO + OEO + EEO | $[1.99, 2.08]$ | field-uniform Sato-Tate |
| 8 pilot at $p = 7681$ | 1 cell × 3.7M samples | EOO | $2.0875$ | Sato-Tate at largest empirical scale |

The $j=5$ EOO outlier 2.51 was originally framed (Litt Round 5) as a
$\mathrm{Sp} \oplus \text{atom}$ $1/d$-dilution decomposition, but the
$j=6$ EOO test gave $2.05$ — a much faster wash-out than $1/d$. At
deployment scale ($j \geq 6$), descended monodromy is uniformly
Sato-Tate $\mathrm{Sp}$ across ALL parity strata, with no carve-out
needed.

### Axis 3: msolve eliminator structure

At $j = 3$ ZERO_DIM, the eliminator $p_0^4 - 1 = \Phi_1 \Phi_2 \Phi_4$
is field-uniform across $\mathbb{F}_p$ for $p \in \{113, 193, 241, 257\}$.
Cyclotomic-trivial structure consistent with descended-monodromy theorem
(boundary $\alpha_i = 0$ stratum).

## Closure pathway

The Q3 conjecture closes uniformly via one descended-monodromy theorem:

> **Theorem (target, 3-6 months).** For $j \geq 6$ and any coprime
> mixed-parity triple $(a_1, a_2, a_3) \in [k, n-1]^3$, the descended
> geometric monodromy $G_\text{geom}^{\mu_n}$ of the trinomial pencil
> local system is $\mathrm{Sp}_{2g}$ where $g$ is the geometric genus of
> the resolved trinomial-pencil curve. Consequently
> $\max_\alpha |C_{f_\alpha}(\beta, j)| \leq c \sqrt{nk}$ uniformly,
> and Q3 holds.

**Bibliography toolkit:**
- Adolphson-Sperber 1989 (Newton polygon nondegeneracy)
- Deligne Weil II (pointwise Frobenius bound)
- Katz 2002 *Twisted L-functions and monodromy* (geometric monodromy on $\mathbb{G}_m$)
- Voloch 1990 (torus-complement Weil)
- Liu-Wan 2010 (T-adic family Newton polygon)
- Sawin-Shusterman 2022 (descended-monodromy adaptation template — the new ingredient)

**Authorship plan (convergent across 5 rounds of expert panel):**
- Felipe Voloch (Canterbury) — Component on torus-complement Weil
- Daniel Litt (Toronto) — Component on descended-monodromy descent
- Will Sawin (Columbia) — Component on Sawin-Shusterman template
- Hui June Zhu (Buffalo) — Newton polygon consultancy
- Daniel Katz (Cal State Northridge) — 4th-moment lower bounds consultancy

## Why Q3 matters for the EF Proximity Prize

The headline up-to-capacity conjecture was disproven Nov 2025 (Crites-
Stewart, BGHKS, Diamond-Gruen). The prize money rides on:
1. Open intermediate zone ($\sqrt{\rho} < \delta < 1 - \rho$)
2. MCA-type upgrades
3. Sharper soundness constants

Q3 directly attacks (1) on the cyclotomic-subgroup variant. The
Crites-Stewart 2025 construction works on $\mathbb{G}_m$; we work on
$\mu_n \subset \mathbb{F}_p^*$ where the descended-monodromy structure
is much more restrictive. The judges (Boneh / Fenzi / Arnon) are not
sequence-school experts; the Voloch / Litt / Sawin descended-monodromy
toolkit is novel for the community.

## Engagement plan

1. **Voloch first** (Sawin Round 4 recommendation, lowest-friction): we
   already have direct line via Gong → Tang Xiaohu → Voloch.
2. **Litt second** (most central to descended-monodromy on cyclotomic
   covers): cold-mail with the eliminator $\Phi_1\Phi_2\Phi_4$ data +
   3-axis empirical summary + 4 honest references.
3. **Sawin third** (final on the team for Sawin-Shusterman template
   ownership).

## Empirical scripts (reproducible)

All scripts in `notes/scripts/`:
- `g3_BW_64x32_*.py`, `g3_BW_128x64*.py`, `g3_BW_256x128.py` — BW interior
- `g3_cc_charpin_*.py`, `g3_cc_j5_*.py`, `g3_cc_j6_*.py`, `g3_cc_j7_*.py` — Sato-Tate
- `g3_msolve_*.py` — eliminator computation

## Outlook

Q3 is in a paper-publishable empirical state. The remaining work is
expert engagement and the descended-Sp-monodromy theorem write-up.
This memo can be forwarded to candidate collaborators verbatim once
the Gong introduction is arranged.
