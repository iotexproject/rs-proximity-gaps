# Note 0484 — Q3 BKK Tight Bound at Base (8, 4)

**Date:** 2026-05-05
**Status:** Mixed volume V(P_2, P_3) = 24 EXACTLY at saturating triple
(4, 5, 6) base; matches empirical # interior solutions.

## Result

For the lex Gröbner basis of the rate-1/2 saturating system at base
$(n, k) = (8, 4)$, triple $(a_1, a_2, a_3) = (4, 5, 6)$, after
α_3 = 1 normalization, the GB has 3 generators with Newton polytopes:

- P_1: triangle with vertices (0, 0), (4, 0), (0, 24); area 48.
- P_2: triangle with vertices (0, 3), (0, 19), (1, 1); area 8.
- P_3: vertical segment from (0, 1) to (0, 25); area 0.

BKK mixed volumes (Bernstein normalization V(P, P) = n! Vol(P)):

| Pair | V_BKK |
|------|-------|
| (P_1, P_2) | 72 |
| (P_1, P_3) | 96 |
| **(P_2, P_3)** | **24** |

Per Bernstein's theorem, for any zero-dimensional system with $f_i$ having
support in $P_i$, the # of isolated zeros in $(\mathbb F^*)^2$ is at most
$\min_{i \neq j} V(P_i, P_j)$ (over independent pairs).

**Empirical** (g3_3mono_base_8x4.output.txt): vdim = 28 = 24 interior +
4 boundary (α_2 = 0, α_1 ∈ 4-th roots of unity at the pencil singular
locus).

The bound V(P_2, P_3) = 24 is **TIGHT** for the interior count. This is
the key BKK identity for the Gong path.

## Structural interpretation

P_3 is univariate in α_2 (a polynomial of degree 25 with 24 nonzero
roots, since α_2 = 0 is a root). For each nonzero root β of P_3, P_2
becomes a linear equation in α_1:
$$
P_2(\alpha_1, \beta) = 19584 \beta \alpha_1 + R(\beta) = 0
\implies \alpha_1 = -R(\beta) / (19584 \beta).
$$
This gives 24 isolated points $(\alpha_1, \alpha_2)$ in $(\mathbb F^*)^2$
forming the bad-α torus orbit. Plus the 4 boundary points at α_2 = 0
gives the full vdim = 28.

## Lift invariance under SP substitution

The standard SP substitution $z = u^d$ at $(n, k) \to (dn, dk)$ gives a
canonical bijection between bad-α sets at the two scales. Hence the
eliminator polynomial in $(\alpha_1, \alpha_2)$ is **identical** at both
scales (same monomials, same coefficients).

**Consequence**: NP and BKK V(P_2, P_3) = 24 propagate uniformly to
every saturating triple at $(2^{j+1}, 2^j)$ in the dyadic tower. No
GB recomputation needed for saturating triples.

This gives a CLEAN structural derivation of $K = 28$ at saturating
triples for all $j \geq 3$.

## Limitation: this BKK identity is for SATURATING triples only

The mixed-parity coprime sub-saturation conjecture (paper2 §3 Lemma
mixed-parity-orbit + Remark mixed-parity-subsat) requires bounding
$K$ for mixed-parity triples. At (8, 4), all 4 above-J coprime triples
are SATURATING (3 give vdim = 28, one gives vdim = 24 + boundary 4 = 28
total). At (16, 8), only 6 of 52 coprime triples are saturating; the
other 46 give vdim ≤ 4 (mixed-parity sub-saturation observed
empirically).

For the mixed-parity case, the eliminator polynomial is **DIFFERENT**
at higher scales — its NP and BKK V need fresh analysis. Per Helleseth's
Niho decomposition framework, mixed-parity 3-mono pencil splits into
single-even + 2-mono-odd, giving a shortened-RS structure with
$K_{\text{mixed}} \leq n - k$.

## Q3 closure status update

| Component | Status (after this note) |
|-----------|---------------------------|
| Saturating $K = 28$ at base via BKK | ✅ V(P_2, P_3) = 24 + 4 boundary = 28 |
| Saturating $K = 28$ at all $j$ via SP invariance | ✅ Eliminator NP preserved under z = u^d |
| Mixed-parity sub-saturation at $j \geq 4$ | 🔄 6/8 verified at (32, 16) F_257; 2 in F_97 retry |
| Universal-k a priori K ≤ 28 mixed-parity | ❌ Open; pursue Helleseth Niho path |

## Files

- `notes/scripts/g3_BKK_8x4.py` — corrected to BKK normalization; runs in <1s.
- This note (0484).

## Reference

- Bernstein, "The number of roots of a system of equations"
  (Funct. Anal. Appl. 9, 1975).
- Cox-Little-O'Shea, *Using Algebraic Geometry*, Ch. 7 (BKK theorem).
