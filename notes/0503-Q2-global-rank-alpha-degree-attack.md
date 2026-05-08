# Note 0503 — Q2 GLOBAL Attack via Rank-α Degree Bound

**Date:** 2026-05-05 (after paper2 v23+, post Note 0502)
**Status:** Initial attack plan / drill scaffolding.

## Setup recap

paper2 §7 `conj:sparse-worst` (Q2 GLOBAL): for action-non-stabilised
strict-above-J $(f_1, f_2)$ pairs at deployment scale,
$$\max K(f_1, f_2; \delta) = \max_{\text{3-pos sparse}} K(f_1, f_2; \delta) = 10.$$

Q2 LOCAL (cross-side stratified $K=16$ pencils) is closed via Boundary-Lift
+ Common-Zero Stratification + rank-$\alpha$ certificate (Notes 0460-0463,
0498-0502).

Q2 GLOBAL (the universal-quantifier version over all $(f_1, f_2)$) is open.

## Key observation (from Note 0498-0502 rank-α certificate)

For the kernel-direction setting, $V_M$-emptiness ⇔
$\mathrm{rank}([U + \alpha V \mid RS_M]) = \dim(\ker) + k$ ∀α.

The matrix $M_\alpha := [U + \alpha V \mid RS_M]$ has:
- First $\mathrm{kdim}$ columns linear in $\alpha$.
- Last $k$ columns constant in $\alpha$.

Determinant of any $(\mathrm{kdim}+k) \times (\mathrm{kdim}+k)$ square submatrix:
**polynomial in $\alpha$ of degree $\leq \mathrm{kdim}$.**

Hence: the rank-deficient $\alpha$'s for FIXED $M_{\mathrm{set}}$ are
roots of a degree-$\leq \mathrm{kdim}$ polynomial in $\alpha$.

## Bound on K via rank-α degree

For a fixed support pair $(\mathrm{supp}(\hat f_1), \mathrm{supp}(\hat f_2))$
and a fixed agreement set $M$:
$$\#\{\alpha : (f_1 + \alpha f_2) \text{ agrees with some } c \in C \text{ on } M\}
\leq \mathrm{kdim}(M, \mathrm{supp}).$$

For Q2 GLOBAL $K$ count at strict above-$J$:
- Agreement $\geq (1 - \delta_J) n_0 = \sqrt{n_0 k_0}$.
- At $(32, 8)$: $|M| \geq \sqrt{32 \cdot 8} = 16$.
- Generic agreement set size ≈ $n_0 - \delta n_0$.

For each $\alpha$ in the $K$ set, there exists SOME $M_\alpha$ with agreement.
The naive union bound over $M_\alpha$ choices is exponential.

**Refined attack**: instead of summing over $M$'s, use the algebraic
constraint that $K$ rank-deficient $\alpha$'s share STRUCTURE.

## Concrete attack plan

### Phase 1: Empirical pattern (next iteration)
Sweep $(f_1, f_2)$ at $(32, 8)$ over varied supports:
- Support sizes: $|S_1 \cup S_2| \in \{3, 4, 5, \ldots, 24\}$.
- For each, compute $K$ and the rank-α matrix degree.
- Plot: $K_{\max}$ vs support size and vs $\mathrm{kdim}_{\min}$.

Hypothesis to falsify or verify:
- $K(f_1, f_2; \delta) \leq \min_M \mathrm{kdim}(M, \mathrm{supp})$.

### Phase 2: If hypothesis holds — structural proof
- Define $\mathrm{kdim}^{\star}(\mathrm{supp}) := \min_{|M| \geq (1-\delta)n_0} \mathrm{kdim}(M, \mathrm{supp})$.
- Show $\mathrm{kdim}^{\star}(\mathrm{supp}) \leq 10$ for action-non-stab supports.
- This would give Q2 GLOBAL.

### Phase 3: If hypothesis fails — refine
- Identify the gap: K can exceed $\mathrm{kdim}^{\star}$ when?
- Likely: action-stabilised case (K = q, excluded by conjecture).
- Quantify the action-non-stab restriction precisely.

## Deliverables

1. Script `g3_q2_global_rank_alpha_sweep.py`:
   - For each support $S$ of size $s \in \{3, ..., 24\}$ at $(32, 8)$:
     - Sample random coefficient pairs.
     - Compute K (via direct distance enumeration over RS).
     - Compute kdim for the implicit rank-α matrix.
   - Output: histogram of $K$ vs $s$ and vs $\mathrm{kdim}$.

2. If pattern emerges: Note 0504 with structural lemma + proof attempt.

3. Update STATE.md when concrete result lands.

## Why this might work

1. The rank-α certificate just closed Conj A at deployment scale (Note 0502).
   Its mechanism is exactly degree-bounded matrix determinant.

2. Existing K10 proof for sparse case uses degree-≤9 eliminator polynomial.
   For general $f$, the natural generalization is rank-α matrix degree.

3. Empirical: K ≤ 2 universally for non-sparse — much smaller than the
   naive $\mathrm{kdim}$ bound, suggesting room for tightening.

## Why it might fail

1. The agreement set $M$ varies with $\alpha$; FIXED-$M$ rank-α only counts
   one stratum. Total $K$ might exceed any single fixed-$M$ bound.

2. Action-non-stab admissibility might not be enough; might need stronger
   "Fourier-spread" condition.

3. The 3-pos sparse maximum K=10 might be a different mechanism (mod-4
   pigeonhole) not captured by rank-α at all.

## Files this note generates

- `notes/scripts/g3_q2_global_rank_alpha_sweep.py` (TODO).
