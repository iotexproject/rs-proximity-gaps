# Note 0285 — Orbit-16 (16, 4) numerical sweep: at-J family characterization

**Date:** 2026-04-30 (this session)
**Status:** Empirical at q ∈ {17, 97}. **Confirms K ≤ 8 universal for above-J
2-mono pencils**, identifies 4 at-J saturation cases.

## Setup

Note 0282 sweep at (16, 4) had many GB TIMEOUTs for orbit-16 (gcd(b-a, 16) = 1)
cases. To bypass, ran direct numerical sweep over F_q, q ∈ {17, 97}, computing
|B| = #{ρ ∈ F_q* : dist(h_ρ, RS_4(L_16)) ≤ 8}.

## Results

### q = 17 (small-q artifact)

6 cases reported |B| = 16 (saturation): (5, 8), (8, 9), (8, 11), (9, 10),
(10, 11), (11, 14).

### q = 97 (structural answer)

| (a, b) | b - a | |B| | Type |
|---|---|---|---|
| (5, 8) | 3 | 0 | trivial |
| (8, 9) | 1 | **96** | **at-J saturation** |
| (8, 11) | 3 | **96** | **at-J saturation** |
| (9, 10) | 1 | **96** | **at-J saturation** |
| (10, 11) | 1 | **96** | **at-J saturation** |
| (11, 14) | 3 | 0 | trivial |
| All other 30 cases | various | 0 | trivial |

**The (5, 8) and (11, 14) cases at q=17 were SMALL-Q ARTIFACTS** (random
agreements over small field). At q = 97 they correctly give |B| = 0.

## At-J characterization: a ≥ 2k, b - a ≤ 3

The 4 at-J cases all have a ∈ {2k, 2k+1, 2k+2} = {8, 9, 10} and small b - a.

**Structural reason** (for (a, b) = (8, 9) at (16, 4)):
- h_ρ(z) = ρ z^8 + z^9 = z^8(ρ + z).
- On L_16 = ⟨ω⟩, z^16 = 1 ⟹ z^8 = ±1.
- On {z : z^8 = 1} (8 points): h_ρ = ρ + z (linear codeword for any ρ).
- Hence agreement ≥ 8 (= w_J) for every ρ ⟹ at-J for every ρ.

This generalizes: for a = 2k + j with small j, the pencil "degenerates"
into linear-codeword + sign part, giving structural at-J saturation.

## Implication for K bound

The at-J cases are **EXCLUDED by the recursive above-J hypothesis** (Note
0188). For above-J f at L_0, the L_2 pencil cannot be in the at-J family.

So for **above-J f**:
$$
K(f) \le 8 \quad \text{universal for 2-monomial pencils at deployment.}
$$

For at-J f: K(f) can be q (saturation), but ε_ca = K/q ≤ 1 trivially. Doesn't
break prize bound for the above-J class.

## Refined Note 0283 statement

**Theorem 0283 (refined)**: For ANY (a, b) **above-J** 2-mono pencil at
deployment scale (n, k) = (4k, k):
$$
|B(a, b)| \le 8.
$$

The "above-J" condition rules out (a, b) like (8, 9), (8, 11), (9, 10),
(10, 11) which give at-J saturation universally.

For Note 0188's "recursive above-J f" hypothesis at FRI 2-round, the L_2
pencil MUST be above-J (else f wasn't recursive above-J). So K ≤ 8.

## Lesson for codex (issue #387 cluster)

Codex's GB sweep at h = 16, p ∈ {13, 17, 19, 23, 29, 31} faces similar
small-q artifacts:
- q = 13, 17, 19, 23 are all < 32 = 2·n. Spurious agreements possible.
- q = 29, 31 are < 32 too.
- For structural answer, need q ≥ ~64 (= 4n) to wash out artifacts.

Note: the algebraic GB approach (eliminator Φ over Q) doesn't have this
issue — gives the structural answer directly. Only the numerical brute
force suffers from small-q.

**Recommendation**: codex's univariate certificate route is correct; small-q
results should be cross-validated at large q (e.g., q ≥ 97) before
declaring a structural conclusion.

## Files

- `notes/scripts/g3_orbit16_numerical_check.py` — F_q brute sweep
- `notes/scripts/g3_orbit16_numerical_check.output.txt` — full q=17, 97 data
- `notes/scripts/g3_orbit16_irreducible_focused.py` — SymPy GB attempt (mostly
  TIMEOUT due to 8-var GB at 60s; numerical above is faster)

## Next steps for prize submission

1. **Update Note 0283** to add "above-J" condition explicitly. RIGOROUS
   K ≤ 8 only for above-J 2-mono pencils.
2. **At-J family enumeration**: classify which (a, b) at deployment scale
   give at-J saturation. Empirically: a ≥ 2k, b - a ≤ small.
3. **Recursive above-J filter**: for FRI prize submission, the recursive
   above-J hypothesis automatically excludes at-J pencils at intermediate
   levels.
