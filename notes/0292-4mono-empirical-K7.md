# Note 0292 — 4-monomial pencil K_4 ≤ 7 empirical (q=97 sweep)

**Date:** 2026-04-30 (post Note 0291)
**Status:** EMPIRICAL K_4 ≤ 7 at base case (8, 2). SymPy GB hits 4-var
elimination wall (45s timeout on all 35 cases). Rigorous closure
requires cluster GB or structural argument.

## Empirical result

35 irreducible 4-mono cases at (n, k) = (8, 2), q = 97, 30 random
(ρ_1, ρ_2, ρ_3) ∈ F_q^3 per case:

**Max |B(α)| = 7**, achieved at $(a_1, a_2, a_3, a_4) = (1, 2, 4, 6)$.

| Top cases | max |B(α)| |
|---|---|
| (1, 2, 4, 6) | **7** |
| (1, 3, 5, 7) | 6 |
| (1, 2, 4, 5) | 5 |
| (1, 2, 3, 4), (1, 2, 3, 5), (1, 2, 3, 6) (after α=0) | 4 each |
| Others | ≤ 4 |

Most cases give |B(α)| ≤ 4.

## Comparison to s = 2, 3

| s (pencil arity) | K_s (universal RIGOROUS) | base case |
|---|---|---|
| 2 | 8 (Note 0286) | (8, 2) (2, 5), (3, 4), (5, 6) |
| 3 | 9 (Note 0291) | (8, 2) (1, 4, 7), (1, 5, 6) |
| 4 | **≤ 7 EMPIRICAL** | (8, 2) (1, 2, 4, 6) |

K decreases as s increases for s ≥ 3 — matching Note 0188's empirical
trend at (32, 8) (s=4: K ≤ 7, s=5: K ≤ 6, s=6: K ≤ 6).

## Status of rigorous extension to s ≥ 4

**Open:** SymPy GB at (8, 2) for 4-var elimination (3 ρ + 1 α) times out
in 45s for all 35 cases. Need:
- Cluster GB (Singular / M2 / Macaulay2) for rigor
- Or structural argument: via 4-mono Substitution Principle (untested)

**Conservative bound** for paper2: empirical K_4 ≤ 7, applied
universally via the conjectured 4-mono Substitution Principle (gcd
reduction analogous to Note 0284, also requires verification).

## Implication for paper2 prize claim

If empirical K_s ≤ 10 for all s ≥ 3 (which the trend strongly suggests),
then the full **s-pos sparse class** at deployment satisfies
$\varepsilon_{ca} \leq 10/q$ universally.

For paper2, this would extend the current 3-pos sparse class (RIGOROUS
via Theorem 0288 + Theorem 0291) to ALL sparse f̂.

For full f̂ (no sparsity assumption), a separate reduction (paper2 P3
op:reduction) is needed.

## Files

- `notes/scripts/g3_4mono_base_cases.py` — SymPy GB attempt (all TIMEOUT)
- `notes/scripts/g3_4mono_numerical.py` — q=97 numerical sweep
- `notes/scripts/g3_4mono_numerical.output.txt` — full output

## Next steps

- Cluster GB for 4-var elimination at (8, 2) (Singular / M2)
- Numerical verification at q ∈ {193, 257, 449} to filter q=97 artifacts
- Structural argument extending 3-mono Substitution to 4-mono
- 5-mono, 6-mono enumerations (continuing the K_s trend)
