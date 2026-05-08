# Note 0495 — Pell-c-identity rigorously proven for both admitting S

**Date:** 2026-05-05 iteration 14-15
**Status:** **STRUCTURAL MILESTONE.** The polynomial identity
$B^2 + 2AB - A^2 \equiv 0$ in $\mathbb{Z}[\zeta_8]$ verified for both admitting
S, modulo the kernel + α-only constraints. Hence α satisfies the Pell equation
$\alpha^2 - 2\alpha - 1 = 0$ unconditionally for these (S, M).

## The proven identity

Setup (recap from Note 0494):
- $S \subset \mathbb{Z}/8$ with $|S|=4$, $S \mod 4 = \{0,1,2,3\}$ (admissible)
- $(c_2, ..., c_7) \in $ kernel of $M_S = (\omega^{rs})_{r \in [2,8), s \in S}$
- $h_\alpha(z) = c_4 z^4 + c_5 z^5 + \alpha (c_2 z^2 + c_3 z^3 + c_6 z^6 + c_7 z^7)$
- $M = \{0, 2, 4, 5, 7\}$, the 5-subset for collinearity test
- α-only minor (rows 0, 2, 4 of augmented 5×3 matrix at M):
  $A_0(c, \omega) := (c_2 + c_6) + \omega^2 (c_3 + c_7)$
- Non-degenerate minor (0, 2, 5):
  $A(c, \omega), B(c, \omega)$ explicit in Note 0494 §"The α formula"

**Theorem (rigorous polynomial identity)**:
For $S \in \{[0,1,2,3], [1,2,3,4]\}$ and the 5 linear constraints (4 kernel +
1 α-only), substituting the unique solution $c_2 = \ldots = c_6 = (\text{linear
in } c_7)$ into $A, B$:

$$\boxed{\quad B(c)^2 + 2 A(c) B(c) - A(c)^2 \;\equiv\; 0 \quad \text{in}
\quad \mathbb{Z}[\omega]/(\omega^4 + 1) \;=\; \mathbb{Z}[\zeta_8].\quad}$$

**Proof**: `issue419_path_A_pell_identity_clean.py` runs the symbolic computation
in sympy. After substituting the kernel + A_0 solution into $B^2 + 2AB - A^2$
and reducing $\omega^k$ for $k \geq 4$ via $\omega^4 + 1 = 0$, the result is
a polynomial in $c_7$ (the free parameter on the 1-dim line). Each coefficient
in $c_7^k$ for $k = 0, 1, 2$ is shown to be a rational function $\text{num}/
\text{denom}$ in $\omega$ with $\text{num} \equiv 0$ in $\mathbb{Z}[\omega]/(\omega^4+1)$.

Output (verbatim):
```
S = [0, 1, 2, 3]
  c_7^2: numerator = 0,   denom = ω·(169ω² - 239ω + 169)
  c_7^1: numerator = 0,   denom = 1
  c_7^0: numerator = 0,   denom = 1

S = [1, 2, 3, 4]
  c_7^2: numerator = 0,   denom = ω·(169ω² - 239ω + 169)
  c_7^1: numerator = 0,   denom = 1
  c_7^0: numerator = 0,   denom = 1
```

The denominator $\omega \cdot (169\omega^2 - 239\omega + 169) \neq 0$ in
$\mathbb{Z}[\zeta_8]$ (verified: $\omega$ is a unit, and the quadratic in $\omega$
factors as a non-zero element since its norm is non-zero in $\mathbb{Z}[\zeta_8]$).
Hence the rational function $B^2 + 2AB - A^2$ has all numerators zero, so the
function is identically zero. ∎

## What the identity means

Substituting α = -B/A into the Pell equation $\alpha^2 - 2\alpha - 1 = 0$:
$$\frac{B^2}{A^2} + \frac{2B}{A} - 1 = 0
\iff B^2 + 2AB - A^2 = 0 \;\;(\text{multiplying by } A^2 \neq 0).$$

The proven identity says: at the unique projective $c$-direction determined by
kernel + $A_0 = 0$, the $\alpha = -B(c)/A(c)$ AUTOMATICALLY satisfies the Pell
equation $\alpha^2 = 2\alpha + 1$.

Mod $p$ with $p \equiv 1 \pmod 8$, the Pell equation has 2 roots in
$\mathbb{F}_p^*$: $\alpha = 1 \pm \sqrt 2$. The reduction sends our $\alpha$ to
**one specific root** (depending on the choice of $\sqrt 2 = \omega + \omega^{-1}$
versus $-(\omega + \omega^{-1})$ in $\mathbb{F}_p$). Empirically (Note 0494): at
the cex direction $c = (23, 9, 17, 30, 1, 2)$ at $p=41$, $\alpha = 25 = 1 + \sqrt 2$.

## Structural consequence: K_2 ≤ 1 per (f_u, f_v)

For any $(f_u, f_v)$ with admissible $S$, kernel direction $c$:
- If $c$ does NOT satisfy kernel + $A_0 = 0$: by the system being consistent,
  no α gives 5-collinearity on M → no cex on M.
- If $c$ DOES satisfy kernel + $A_0 = 0$: $c$ is on the unique 1-dim line, so
  $c$ is a scalar multiple of the canonical $v_0(\omega, S)$. Then $\alpha =
  -B/A$ is fixed (scaling-invariant) and satisfies the Pell equation. Hence
  exactly **one** α admits cex on M.

**Per fixed projective direction**: $K_2$(on $M = \{0,2,4,5,7\}$) $\leq 1$.

## Open extensions (next iterations)

1. **Other M's**: M={0,2,4,5,7} is one of $\binom{8}{5} = 56$ subsets. For
   different M, the α-only minor is different, giving a different $A_0$, hence
   a different "failure direction". For each such M, the analogous Pell
   identity may or may not hold. Need to enumerate.
   - Conjecture: only certain M's (those admitting an α-only minor) have a
     Pell-style structure; the others have $K_2 = 0$.

2. **Universal K_2 ≤ 1 across M**: per fixed (f_u, f_v), how many M's give
   simultaneous failure? Empirically: at $S=[0,1,2,3]$, $c=(23,9,17,30,1,2)$,
   $\alpha=25$, the matching set is exactly $M=\{0,2,4,5,7\}$ — a **single**
   5-subset of $\mu_8$. Different α (e.g., $\alpha = 18 = 1 - \sqrt 2$) at the
   same $c$ may match a **different** 5-subset. So per direction, both Pell
   roots could give cex on different M's, leading to $K_2 = 2$ per direction.
   - The full $K_2$ count requires checking all 56 M's per direction, which
     is the running script `issue419_path_A_K2_per_direction.py`.

3. **Lift to (32, 8) base scale**: replicate the elimination + identity proof
   at scale (32, 8), where ω is a primitive 32-nd root of unity. Expect a
   higher-degree Pell-analog (over $\mathbb{Q}(\zeta_{32})$ or some real
   subfield).

## Files

- `issue419_path_A_pell_identity_proof.py` (iteration 14, has false-negative
  in simplify but Poly coefficient = 0)
- `issue419_path_A_pell_identity_clean.py` (iteration 15, this note —
  rigorous proof, both admitting S verified)
- `issue419_path_A_pell_identity_clean.output.txt` — verification output
- `issue419_path_A_identify_admitting_S.py` (iteration 15) — identifies
  admitting S = {[0,1,2,3], [1,2,3,4]}
- `issue419_path_A_K2_per_direction.py` (running) — exhaustive K_2 per
  (S, c-direction) across primes; will determine if $K_2 \leq 1$ universal

## Confidence update

- **K_2 ≤ 1 at S ∈ {[0,1,2,3], [1,2,3,4]}, M={0,2,4,5,7}**: PROVEN (rigorous
  polynomial identity in $\mathbb{Z}[\zeta_8]$).
- **K_2 ≤ 1 at any (S, c-affine) at base (8,2) for ANY M**: 80% confidence
  within 1 week (need to enumerate the 56 M's symbolically).
- **K_2 ≤ 1 at (32, 8) inner Conj A**: 50% within 4 weeks (replicate machinery
  at scale 32).
- **paper2 §7 unconditional rewrite "K_BW ≤ 3"**: 40% within 6 weeks
  (depends on (32, 8) close).

## Honest assessment

This iteration is the first rigorous structural progress on the (8, 2) Conj A
problem. The polynomial identity is **not a conjecture** — it's a verified
algebraic equation in $\mathbb{Z}[\zeta_8]$. The Pell root structure of the
failing α is no longer empirical pattern matching; it follows from explicit
computation in the cyclotomic ring.

What remains is to extend the result across all (S, M) pairs and lift to
(32, 8) — both routine algebra computations, not new mathematical insight.

This is the kind of progress that turns "modulo Conjecture A" into "lemma
(K_2 ≤ 1, base scale)".
