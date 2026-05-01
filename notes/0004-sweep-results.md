# Note 0004 — Sweep Results: Conjecture 4 (Strict) Fails at n ≥ 36

*2026-04-20. Empirical results from `cs_sweep_fast.py`. Conjecture refined.*

## Raw results

| (n, m, s, r)   | p   | k | δ      | #bad λ | #wits | aligned | NOT aligned |
|----------------|-----|---|--------|--------|-------|---------|-------------|
| (12, 2, 6, 3)  | 13  | 2 | 0.500  | 1      | 2     | 2       | **0**       |
| (12, 2, 6, 4)  | 13  | 4 | 0.333  | 6      | 6     | 6       | **0**       |
| (12, 3, 4, 3)  | 13  | 3 | 0.250  | 0      | 0     | —       | —           |
| (24, 2, 12, 3) | 73  | 2 | 0.750  | 1      | 4     | 4       | **0**       |
| (30, 2, 15, 3) | 31  | 2 | 0.800  | 16     | 20    | 20      | **0**       |
| (30, 3, 10, 3) | 31  | 3 | 0.700  | 0      | 0     | —       | —           |
| **(36, 2, 18, 3)** | 37 | 2 | 0.833 | 37 | 60 | 24 | **36** |
| (36, 3, 12, 3) | 37  | 3 | 0.750  | 1      | 4     | 4       | **0**       |
| **(42, 2, 21, 3)** | 43 | 2 | 0.857 | 22 | 70 | 28 | **42** |
| (42, 3, 14, 3) | 43  | 3 | 0.786  | 0      | 0     | —       | —           |
| **(60, 2, 30, 3)** | 61 | 2 | 0.900 | 61 | 310 | 70 | **240** |

**Total: 476 witnesses, 158 aligned (33%), 318 NOT aligned (67%).**

## Key findings

### F1. Conjecture 4 (strict) is FALSE.

Starting at $n = 36$, witnesses that do **not** decompose as unions of cosets of any single subgroup of $L$ exist, and they outnumber the aligned ones for large $n$.

### F2. Alignment fraction decays with $n$.

For $m = 2, r = 3$ cases:
- $n \in \{12, 24, 30\}$: **100% aligned**
- $n = 36$: **40% aligned**  
- $n = 42$: **40% aligned**
- $n = 60$: **22% aligned**

The decay is consistent with: aligned solutions are a *fixed-count* structured family; total solutions grow combinatorially with $n$.

### F3. Larger $m$ kills the failure entirely.

For $m = 3, r = 3$ cases:
- All have either **0 witnesses** or **100% aligned**
- Reason: $m = 3$ imposes more Newton-conditions on the bad set (we need $p_j(S) = 0$ for more $j$'s — see Note 0002 §3); the algebraic variety has lower dimension; only structured solutions survive.

This is **important for FRI**: realistic FRI parameters have moderate-to-large $m$. The "alignment dominates" regime may match practice, even though strict Conjecture 4 fails in toy parameters.

### F4. Non-aligned witnesses have a recurring shape.

Three NON-aligned $S$'s for $(36, 2, 18, 3)$:
- $S_1 = \{8, 11, 12, 19, 20, 32\}$
- $S_2 = \{1, 2, 14, 26, 29, 30\}$
- $S_3 = \{9, 21, 24, 25, 32, 33\}$

Decomposition pattern (all three):
$$S = \underbrace{\{a, a+12, a+24\}}_{\text{coset of order-3 subgroup}} \;\cup\; \underbrace{\{b, b+1, b+8\}}_{\text{"shape"}}$$

The "shape" set $\{b, b+1, b+8\}$ in $\mathbb{Z}/36\mathbb{Z}$ is the **same** in every non-aligned witness (modulo translation). It is **not** a coset of any subgroup of $\mathbb{Z}/36\mathbb{Z}$.

For $(42, 2, 21, 3)$ and $(60, 2, 30, 3)$ a similar structure appears (residues to be classified — see Studio Task S1).

## Refined conjecture

**Conjecture 4′.** *Every bad agreement set in a CS-style proximity-gap failure decomposes as*
$$S \;=\; \underbrace{\bigsqcup_{i} c_i H_i}_{\text{subgroup-coset part}} \;\cup\; \underbrace{R}_{\text{residue}},$$
*where each $c_i H_i$ is a coset of some multiplicative subgroup $H_i \leq L$ (subgroups can vary), and $R$ is a "shape" set determined by the algebraic variety $\mathcal{V}$ cut out by the Newton-symmetric conditions $p_j(S) = 0$.*

Equivalently: **the bad agreement sets are the $\mathbb{F}_p$-points of an algebraic variety on $L^{rm}$**, and:
- Subgroup-coset structure provides "guaranteed" $\mathbb{F}_p$-points (always present).
- Generic algebraic-geometric points ("shape" residues) emerge as $|\mathbb{F}_p|$ grows.

## Interpretive picture

The proximity-gap-failure structure is governed by:
$$\mathcal{V}_{n, m, r} \;=\; \{S \subset L : |S| = rm,\ p_j(S) = 0 \text{ for } j \in J(m, r)\}$$
where $J(m, r) = \{1, 2, \ldots, 2m-1\} \setminus \{m\}$ (from Note 0002 §3).

This is an algebraic variety of expected dimension $rm - (2m - 2) = (r-2)m + 2$ over the ambient $L^{rm}$, embedded in $\mathbb{F}_p$-points.

The **size of this variety over $\mathbb{F}_p$** controls the proximity-gap-failure count. Bezout-style bounds give $|\mathcal{V}(\mathbb{F}_p)| \leq C \cdot p^{(r-2)m + 2}$ for some $C$ depending on $(n, m, r)$.

Currently observed: with $r = 3, m = 2$, $|\mathcal{V}(\mathbb{F}_p)| \sim p \cdot \text{(something growing in n)}$. Need bigger experiments to pin scaling.

## What this means for the prize

- Strict "subgroup-only" picture is too narrow. Good — refines our angle.
- The **algebraic-variety picture** is potentially even better: it says proximity-gap failure is governed by counting $\mathbb{F}_p$-points on an explicit variety, which is **exactly** the kind of question Weil / Lang-Weil / Deligne-style estimates address.
- This puts us in the **arithmetic-geometric** machinery shared by the sequence-school cross-correlation literature *and* mainstream algebraic geometry — broader than just "subgroup lattice".
- The 2m - 2 condition count is a sharp invariant — subgroup-cosets are the "guaranteed" rational solutions, but the variety has more.

## Action items (transferred to STUDIO_TODO.md)

- **S1**: Bigger $n$ (up to 200), with **proper** multiplicative subgroups (not full $\mathbb{F}_p^*$).
- **S2**: Classify the residue shapes $R$ — are they all algebraic perturbations of subgroup-cosets?
- **S3**: Char-2 experiments — does the same structure hold over $\mathbb{F}_{2^t}$?
- **S4**: Lang-Weil count: empirically estimate $|\mathcal{V}(\mathbb{F}_p)|$ growth and compare to expected dimension.
- **S5**: MCA extension: same setup but with a *family* of $u_\ell$'s, requiring common $D$.
