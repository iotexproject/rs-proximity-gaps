# Note 0473 — Second virtual consult: Gong + Helleseth on closing GS m=2 (τ=71)

**Date:** 2026-05-04 PM (post Note 0471/0472)
**Status:** ACTIONABLE — both experts converge on **prove 3-valued distribution**.
**Branch:** `main`

---

## Setup of the new question

After Note 0471/0472 closed K_BW ≤ 2 at τ=80 structurally, the next open
problem is: prove K_GS_2 ≤ 2 at τ=71 (GS m=2 list-decoding threshold).

At τ=71, Lemma 2 (degree counting) gives bound $(k-1) + (n-71) = 31+57 = 88$,
which exceeds 71, so the simple argument fails.

Empirically K_GS_2 ≤ 2 across 24 cases. The path forward needs sharper
structural machinery.

## Both experts converge on: prove the 3-valued distribution

The empirical fact (Note 0469): for K=2 saturating cases, the agreement
multiset is exactly **3-valued** with levels $\{48, 56, 80\}$ at multiplicities
$(p-5, 2, 2)$. **No level falls in [57, 79].**

If we PROVE this, then K_GS_2 ≤ 2 at τ=71 is **immediate**: the only level
satisfying $\geq 71$ is 80 itself, with multiplicity 2.

## Gong's recommended path: Power Moments

Compute moments $M_k = \sum_\alpha \mathrm{agr}(g_\alpha, 0)^k$ as explicit
polynomials in the Fourier coefficients of $f_u, f_v$. The disjoint-support
condition ($r \bmod 4 \in \{0,1\}$ vs $\{2,3\}$) kills cross-terms.

The Pless power-moment identities then **uniquely determine the 3-valued
distribution** if and only if $M_1, M_2, M_3$ match.

References:
- Helleseth 1976, *Discrete Math*, "Some results about cross-correlation function..."
- Gong-Golomb 2002, *IEEE IT*, "Two-tuple-balance of non-binary sequences..."
- Calderbank-McGuire-Poonen-Rubinstein 1996, *Designs, Codes and Crypto*.
- Schmidt-White 2002, *FFA* (small-prime cyclotomy).

Estimated time: 6-8 weeks.

## Helleseth's recommended path: Niho 3-valued classification

Hollmann-Xiang 2001 "*A proof of the Welch and Niho conjectures*"
classifies when a Niho exponent gives a 3-valued cross-correlation.
Helleseth-Kholosha-Mesnager 2011 "*Niho type cross-correlation functions
and related equations*" Theorem 3 gives the explicit 3-valued distribution
for a pencil $f_u + \alpha f_v$ with disjoint Niho-type supports.

Our setup ($r \bmod 4 \in \{0,1\}$ vs $\{2,3\}$ on $[k_2, n_2)$) **fits the
HKM-2011 hypothesis almost verbatim**, modulo verifying the fold $w \mapsto w^4$
preserves the Niho splitting.

Companion: Stickelberger 2-adic congruence forces $K$ to be even
(cyclotomic fingerprint of the prime-uniform pattern).

## Synthesis (this note)

| Strategy | Pros | Cons |
|---|---|---|
| Gong's $M_2/M_3$ moment | Self-contained, $p$-uniform, no external citation | 6-8 weeks, $M_2$ is a 4th-order Fourier sum |
| Helleseth's HKM-2011 | Already proven in literature; just verify hypothesis | Requires verifying Niho splitting + small-prime adaptation |
| Combination | Gong's moments cross-checked against HKM | Most rigorous |

**Recommended:** Try Gong's path FIRST (compute $M_2$ explicitly), then
verify against HKM-2011 hypothesis.

## First moment computation (this note)

Define $\mathcal{F}(\alpha) = |\phi^{-1}(\alpha)|$ where
$\phi: L_2 \setminus T \to \mathbb{F}_p^*, \phi(z) = -f_u(z)/f_v(z)$.

**$M_1$** (already known from Lemma 1):
$$
M_1 = \sum_\alpha \mathrm{agr}(g_\alpha, 0) = 4 \cdot |Z_{L_0}(g_\alpha)| \text{ summed over } \alpha = 48 p + 80
$$
because for each w ∈ L_0 with $w^4 \in T$, EVERY $\alpha$ contributes (giving $48p$); for each w with $w^4 \notin T$, exactly ONE $\alpha$ contributes (giving 80).

Lemma 1 follows by subtracting baseline · $|\mathbb{F}_p^*|$:
$$
\sum_{\alpha \in \mathbb{F}_p^*}(\mathrm{agr}(g_\alpha, 0) - 48) = M_1 - 48 p - (\mathrm{agr}(g_0, 0) - 48) = 80.
$$

**$M_2$**:
$$
M_2 = \sum_\alpha \mathrm{agr}(g_\alpha, 0)^2 = 16 p |T|^2 + 32 |T|(n_2 - |T|) + 16 \sum_\alpha \mathcal{F}(\alpha)^2.
$$

(Derived from pair-counting: each (w, w') ∈ L_0^2 contributes either p (if both fibers in T), 1 (if exactly one in T), or [φ(z)=φ(z')] (if both outside T). Multiplied by 16 = 4^2 fiber pairs.)

For |T|=12, $n_2 = 32$: $M_2 = 2304 p + 7680 + 16 \cdot \sum \mathcal{F}^2$.

**Verification against 3-valued distribution (multiplicities $(p-4, 2, 2)$):**
$$
M_2 = 48^2 (p-4) + 56^2 \cdot 2 + 80^2 \cdot 2 = 2304(p-4) + 6272 + 12800 = 2304 p + 9856.
$$
Equating: $16 \sum \mathcal{F}^2 = 2176 \Rightarrow \sum \mathcal{F}^2 = 136 = 64+64+4+4$.

Empirical check (Note 0469 data, K=2 cases at |T|=12): multiplicities $(8, 8, 2, 2)$ over 4 distinct image values, sum of squares = 136. ✓

So **$M_2$ is determined by $\sum \mathcal{F}^2$**, and the latter is determined by the algebraic identity:
$$
\sum_\alpha \mathcal{F}(\alpha)^2 = |\{(z, z') \in (L_2 \setminus T)^2 : f_u(z) f_v(z') = f_u(z') f_v(z)\}|.
$$

## The structural rigidity question

For 3-valued distribution to hold, we need $\sum \mathcal{F}^2 = 136$ (specific value). This is NOT implied by stratum (B) cross-side $K=16$ alone — empirically:

| Case type | $\sum \mathcal{F}^2$ | Distribution |
|---|---|---|
| K=2, \|T\|=12 (saturating) | 136 | 3-valued $\{48, 56, 80\}$ |
| K_GS_2=1, \|T\|=12 | 52 | 4-valued $\{48, 52, 56, 72\}$ |
| K=0, \|T\|=8 | (varies) | 4-5-valued |

So $\sum \mathcal{F}^2$ is a **case-dependent quantity**, characterizing
the K=2 saturating subset of stratum (B).

## What this means for closing τ=71

The route via "prove 3-valued distribution universally" is **NOT a direct path** because the distribution depends on the algebraic structure of $(f_u, f_v)$ beyond stratum (B). We instead need to show:

**Refined claim**: For ANY stratum (B) cross-side $K=16$ pair at $|T| \leq 12$, the agreement levels at agreement $\geq 71$ count to at most 2.

Equivalently: at most one elevated level $\ell \geq 71$ exists, and it has multiplicity ≤ 2.

This is a different claim than 3-valued. It's weaker: doesn't require the WHOLE distribution to be 3-valued, just that the high tail has ≤ 2 α's.

A natural hypothesis: among all 4-valued cases at |T|=12 (K_GS_2 ∈ {0, 1}), the highest level is at most 76. Empirically:
- K_GS_2 = 1 cases: highest level = 72 (from p=641 case 3, p=769 case 2). Below 76.
- K_GS_2 = 0 cases: highest level = 68. Below 76.

So **empirically the gap [73, 79] is universally empty**. Combined with budget (Lemma 1) which gives K · 23 ≤ 80, K ≤ 3 at τ=71... but the structure forces K ≤ 2 because the highest non-saturating level is < 76.

To prove this gap [73, 79] is empty: this is again a 3-valued / quantization claim. Hard without Niho.

## Action items emerging

1. **Compute $\sum \mathcal{F}^2$ via Fourier** as a polynomial in
   $\hat f_u, \hat f_v$. The algebraic identity $f_u(z) f_v(z') = f_u(z') f_v(z)$
   has a nice Fourier expansion via Plancherel.

2. **Test the gap [73, 79] universality** across the 24 cases — done empirically, found gap is always empty. ✓

3. **Verify Niho splitting** under fold $w \mapsto w^4$:
   - L_0 = μ_128, L_2 = μ_32, fold factor = 4.
   - u-side $r \in [8, 32)$ with $r \bmod 4 \in \{0, 1\}$: lifted Fourier index $4r \bmod 128 \in \{32, 36, 48, 52, ...\} \subset \{j \in [0, 128) : j \equiv 0 \text{ or } 4 \pmod{16}\}$.
   - v-side similarly: lifted Fourier index $j \equiv 8 \text{ or } 12 \pmod{16}$.
   - These are disjoint cosets of $16 \mathbb{Z} / 128 \mathbb{Z}$ in $\mathbb{Z}/128$. Niho-style splitting confirmed.

4. **Real email to Gong/Helleseth** with the explicit problem and ask for
   the 3-valued / Niho theorem citation.

## Next session priority

Compute $\sum \mathcal{F}^2$ as a Fourier polynomial in $\hat f_u, \hat f_v$.
This is the next concrete computation.

## Files

- This note 0473.
- Gong subagent transcript: (in this note's source above)
- Helleseth subagent transcript: (in this note's source above)
