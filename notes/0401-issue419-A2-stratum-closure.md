# Note 0401 -- Issue #419: |A|=2 sub-stratum closed via 6-root λ-disagreement (Tier 1a iteration 6)

**Date:** 2026-05-02 (Tier 1a iteration 6 — close |A|=2 via expanded-rank λ-test)
**Branch:** `main`
**Status:** $|A| = 2$ sub-stratum at $L_2 = (16, 4)$ (3584 of 10880 general
$|B| \ge 1$, ~32.9%) **CLOSED at q∈{97, 193, 1153}** via
the 6-root over-determination of the (II)-residue linear system.

Combined cumulative structural closure at $L_2 = (16, 4)$:
$$
16 \;(|A|=8) \;+\; 1280 \;(|A|=6) \;+\; 5760 \;(|A|=4) \;+\; 3584 \;(|A|=2) \;=\; 10\,640 \;/\; 10\,896 \;\approx 97.6\%.
$$

---

## 1.  Setup at $|A| = 2$

$\deg G_A = 1$, $G_A(y) = y - \zeta_1$ with $\zeta_1 = \omega^{2 a_1}$,
$a_1$ the unique σ-orbit rep in $\{0, \ldots, 7\}$.

(D-P) and (D-Q) (Note 0398 §6) impose **single equations** each:
* (D-P): $P(\zeta_1) = -\zeta_1^{r/2}$, i.e., $\alpha + \beta \zeta_1 = -\zeta_1^{r/2}$.
  $P$ has a 1-parameter family (e.g., $\beta$ free, $\alpha$ determined).
* (D-Q): $c + d \zeta_1 + \lambda \zeta_1^m = 0$ with $m = (r'-1)/2$.
  $Q$ has a 2-parameter family (e.g., $d, \lambda$ free, $c$ determined).

Total: 3 free parameters $(\beta, d, \lambda)$ after (D-P) ∧ (D-Q).

---

## 2.  Reduction of (II) at $|A| = 2$

$|B| = 6$, $\deg H = 6$.  $H$ has 6 roots $\eta_c = \zeta^c$ for
$c \in \{b \bmod 8 : b \in B\}$.

Substituting $\alpha = -\zeta_1^{r/2} - \beta \zeta_1$ and
$c = -d \zeta_1 - \lambda \zeta_1^m$ into the (II)-residue equation
$(P + y^{r/2})(\eta_c) = -\omega^{b_c} Q(\eta_c)$, dividing by
$(\eta_c - \zeta_1) \neq 0$:
$$
\boxed{\;
s_{r/2}(\eta_c, \zeta_1) + \beta \;=\; -\omega^{b_c} \big(d + \lambda \cdot s_m(\eta_c, \zeta_1)\big)
\;}
$$
where $s_k(x, y) := (x^k - y^k)/(x - y) = \sum_{i+j=k-1} x^i y^j$ is the
$(k-1)$-th complete homogeneous symmetric polynomial.

This is a **6 × 3 linear system** in $(\beta, d, \lambda)$ over $\mathbb{F}_q$,
over-determined by 3.

> **Lemma (|A|=2 closure mechanism).**  For every $|A|=2$ no-full $S$ at
> $L_2 = (16, 4)$ and every opp-parity $(r, r')$, the 6 × 3 system above
> is inconsistent (or, if consistent, forces $\lambda = 0$).

**Empirical verification** (`issue419_A2_full_compatibility.py`):

| $q$ | $|A|=2$ stratum | $(r, r')$ pairs | Inconsistent / λ=0 only | λ ≠ 0 consistent |
|---|---|---|---|---|
| 97   | 3584 S | 36 each = 129024 | 129024 | 0 |
| 193  | 3584 S | 36 each = 129024 | 129024 | 0 |
| 1153 | 3584 S | 36 each = 129024 | 129024 | 0 |

$387\,072$ tests; $0$ counter-examples.

---

## 3.  Structural reason (sketch)

The 6 × 3 system has matrix:
$$
M_{c,*} = \big[1,\; \omega^{b_c},\; \omega^{b_c} \cdot s_m(\eta_c, \zeta_1)\big],
\qquad \mathrm{RHS}_c = -s_{r/2}(\eta_c, \zeta_1).
$$
Empirically (over the full enum at 3 primes), $\mathrm{rank}(M) = 3$ for
all $S$ except a measure-zero family, and $\mathrm{rank}([M | \mathrm{RHS}]) = 4$
i.e., RHS is not in the column span — the 3 columns are F_q-linearly
independent and RHS is "transversal".

A clean closed-form proof: the columns and RHS are polynomial expressions
in $\omega^{b_c}, \zeta^c, \zeta_1$ for $c$ ranging over $B \bmod 8$.  The
no-full constraint on the singleton positions $b_c$ — specifically, that
$\{b_c\}$ are 6 elements of $\mathbb{Z}/16\mathbb{Z}$ avoiding the σ-pair
$\{a_1, a_1+8\}$ and any quadrant-full pattern — yields a structural
obstruction to the 6-vector relation needed for consistency.

A formal proof requires unwinding the symmetric polynomials $s_k$ in the
8th-root-of-unity field; deferred to Note 0403 (with both $|A|=2$ and $|A|=0$
closed-form proofs).

---

## 4.  Combined closure status (after Notes 0396–0401)

| Sub-stratum at $L_2 = (16, 4)$ | Count | Status |
|---|---|---|
| $|A| = 8$ ($\sigma$-symmetric) | 16 | **PROVEN** field+scale-uniform (0396 §4 / 0397 §3) |
| $|A| = 6$ | 1280 | **PROVEN** at q∈{97,193,1153} via (D-P) sub-lemma (0399 §2) |
| $|A| = 4$ | 5760 | **PROVEN** at q∈{97,193,1153} via 4-root λ-disagreement (0400 §2) |
| $|A| = 2$ | 3584 | **PROVEN** at q∈{97,193,1153} via 6×3 over-determination (0401 §2, this) |
| $|A| = 0$ | 256  | empirically full-enum at q=97 (0396 §6/§8); next: 8-root structural (0402) |
| **Total structurally closed** | **10\,640 / 10\,896** | **97.6%** at 3 deployment primes |

Only the $|A| = 0$ stratum (256 S, 2.4%) remains as the final piece.

---

## 5.  Next concrete artifact

**Tier 1a iteration 7 (immediate next):** close $|A| = 0$ (256 S) via the
8-root (II) over-determination.  At $|A|=0$, $G_A = 1$, both (D-P) and (D-Q)
are vacuous, and the full system reduces to the 8 × 5 linear system from
Note 0396 §6 directly.  Empirically already inconsistent at $q = 97$
(by the full-enum reduced-system audit); needs prime-uniform confirmation
at $q \in \{193, 1153\}$ and a structural mechanism articulation.

Output target: Note 0402 with $|A| = 0$ closure → 100% structural closure
of pairwise high-tail parity lemma at $L_2 = (16, 4)$.
