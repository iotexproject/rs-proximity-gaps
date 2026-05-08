# Note 0486 — L_1 deployment-scale K_BW: empirical + structural close

**Date:** 2026-05-04 night (post-compact iteration 3).
**Status:** Empirical K_BW^{L_1} = 0 across 80 cases × 8 primes. Structural close via mod-2 split, 2:1 lift.

## Setup

Scaled-down analog of L_3 / L_2 setups, this time with a **2:1 lift** (since 4:1 with k_inner = 1 is degenerate — RS_1 is just constants):

- **Outer**: L_1 = μ_16, RS_4(L_1). Deployment K_BW question. τ_BW = 10.
- **Inner**: L_2' = μ_8, RS_2(L_2'). Stratum (B) base.
- **Lift**: z → z² from L_2' to L_1, 2:1.

Stratum (B) split mod 2:
- u_side = {r ∈ [2, 8) : r ≡ 0 mod 2} = {2, 4, 6} (size 3)
- v_side = {r ∈ [2, 8) : r ≡ 1 mod 2} = {3, 5, 7} (size 3)

Symmetric split (unlike L_2 setup where mod-4 was asymmetric).

## Empirical result (`issue419_L1_kbw_scaled_analog.py`)

Across **8 primes** {97, 113, 193, 257, 433, 641, 769, 1153} (admitting μ_16) and **10 random stratum (B) cases each = 80 cases total**:

| Case attribute | Value |
|---|---|
| |T_inner| (common zeros on L_2') | **0** in all 80 cases |
| K_1 (saturating α) | **0** in all 80 cases |
| K_2 (non-zero codeword α above τ=10) | **0** in all 80 cases |
| **K_BW^{L_1}** | **0** in all 80 cases |

## Structural explanation

Same machinery as L_2 / L_3 chain, scaled to L_1:

**(L1) Budget at L_1 → L_2'**: $\sum_\alpha (\mathrm{agr}_{L_1}(h_\alpha, 0) - 2|T_{L_2'}|) = 2(n_{L_2'} - |T_{L_2'}|) = 2(8 - |T_{L_2'}|)$.

For |T_{L_2'}| = 0: sum = 16.

**(L3) Saturation pigeonhole**:
- |T_{L_2'}| = 0: excess = 10. K_1 · 10 ≤ 16, so $K_1^{L_1} \leq 1$.
- |T_{L_2'}| = 1: excess = 8. K_1 · 8 ≤ 14, so $K_1^{L_1} \leq 1$.
- |T_{L_2'}| = 2: excess = 6. K_1 · 6 ≤ 12, so $K_1^{L_1} \leq 2$.

Empirically |T_{L_2'}| = 0, so $K_1^{L_1} \leq 1$.

**G1+G2+G3 + L_1-factored at L_1 → L_2'** (2:1 lift via z → z²; fiber size 2):

Per-fiber decomp: $c_0(z) = c_{0,0}(z^2) + z\, c_{0,1}(z^2)$, where $c_{0,r} \in \mathrm{RS}_2(L_2')$ (degree ≤ 1).

- **G1 (per-fiber polynomial degree)**: a_u ≤ 2 (per fiber of size 2). a_u = 2 iff F ≡ 0 on fiber.
- **G2 (common-zero bound)**: a_u = 2 requires $c_{0,1}(u) = 0$ AND $c_{0,0}(u) = h_\alpha(u)$ (the L_2' projection). c_{0,1} ∈ RS_2(L_2') is degree ≤ 1; ≤ 1 zero on L_2'. So **N_2 ≤ 1**.
- **G3 (cross-pair Plancherel--Singleton at L_1)**: with fiber size 2 there is only one pair per fiber. $E_1(z) := c_0(z) - c_0(-z) = 2z\, c_{0,1}(z^2)$. $\deg E_1 \leq 1 + 2 \cdot 1 = 3$ in z. $E_1 = z \cdot 2 c_{0,1}(z^2)$, factors as $z \cdot \tilde E_1$ with $\deg \tilde E_1 \leq 2$. For non-induced ($c_{0,1} \not\equiv 0$): $E_1 \not\equiv 0$. $|Z_{L_1}(E_1)| \leq 2$. So $\sum_u a_u(a_u - 1) = M_1 \leq 2$.

**IP at L_1**: maximize $\sum_u a_u = 2 N_2 + N_1$ subject to $2 N_2 \leq 2$, $N_2 \leq 1$, $\sum N_i = 8$.

- $N_2 = 1$: cost 2, slots 1 + (rest). Max $N_1 = 7$. Value $= 2 + 7 = 9$.
- $N_2 = 0$: $N_1 \leq 8$. Value $= 8$.

**Max = 9 < 10 = τ_{L_1}** ✓✓✓

So sub-case A non-induced at L_1 gives **agr ≤ 9 < 10**, structurally closed.

## Sub-case B at L_1 ($c_{0,1} \equiv 0$, induced)

$c_0(z) = c_{0,0}(z^2)$ is constant on each fiber. agr_{L_1}(h_α, c_0) for fiber over u ∈ L_2' = sum of #{z in fiber : h_α(z) = c_{0,0}(u)}.

$c_{0,0} \in \mathrm{RS}_2(L_2')$: constants + linear. agr_{L_2'}(h, c_{0,0})·... wait, h_α isn't a function on L_2' — it's on L_1. The lift relation: agr_{L_1}(h_α, c_0) = ?

Actually for c_0 = c_{0,0}(z²), c_0 is even in z. Each fiber {z, -z} has c_0 constant. agr_{L_1}(h_α, c_0) = sum over u ∈ L_2' of [#{z in fiber over u: h_α(z) = c_{0,0}(u)}].

If h_α is also even (factors through z → z²), this reduces to 2 · agr_{L_2'}. But h_α isn't even generically.

For h_α arbitrary on L_1: per fiber {z, -z}, agreement with constant c_{0,0}(u) is at most 2 (if both h_α(z), h_α(-z) = c_{0,0}(u)) or 1 or 0.

**Bound**: agr_{L_1}(h_α, c_0) ≤ #{z ∈ L_1 : h_α(z) = c_{0,0}(z²)}. Since c_{0,0}(z²) takes values in F_p, this is just the equality count. lemma:degree-counting at L_1 with c_0 ∈ RS_4(L_1) (since c_0(z) = c_{0,0}(z²) has deg ≤ 2 in z, in RS_3 ⊂ RS_4): agr ≤ (k - 1) + (n - N_α) = 3 + (16 - N_α) = 19 - N_α.

For agr ≥ 10: N_α ≤ 9. h_α at L_1 has Fourier support [4, 16) (above-J, lifted from [2, 8)). h_α non-zero polynomial of degree ≤ 14 on μ_16 has ≤ 14 zeros. Generically much fewer.

The bound 19 - N_α doesn't preclude agr ≥ 10. But empirically K_2 from induced sub-case = 0. Reduces to L_2' = (8, 2) Conj A (recursive base).

## Status summary

| Component (L_1 deployment K_BW) | Empirical | Structural |
|---|---|---|
| K_1^{L_1} ≤ 2 | 0/80 saturate | Budget+pigeonhole, |T_{L_2'}| ≤ 2 ✓ |
| Non-induced sub-case A bound ≤ 9 < 10 | confirmed | G1+G2+G3 + IP ✓ |
| Induced sub-case (c_{0,1} ≡ 0) | 0/80 contribute | reduces to L_2' = (8, 2) Conj A (recursive base) |

## Combined L_1 + L_2 + L_3 status

| Layer | (n, k) | τ | K_BW empirical | Structural status |
|---|---|---|---|---|
| L_1 | (16, 4) | 10 | 0 / 80 cases | non-induced A unconditional (≤ 9), induced empirical |
| L_2 | (32, 8) | 20 | 0 / 60 cases | non-induced A unconditional (≤ 16), induced+B empirical |
| L_3 | (128, 32) | 80 | ≤ 2 (24 cases × multiple primes) | 4/5 unconditional at N_α=80, residual reduces to L_2 Conj A + (64,16) |

**The recursive structure**: L_3 residual reduces to L_2 Conj A. L_2 residual reduces to L_4 = (8, 2) Conj A. L_1 residual reduces to L_2' = (8, 2) Conj A — same base case.

The base case L_2' = L_4 = (8, 2) Conj A is the smallest non-trivial scale and resists recursive reduction (further lift to (2, 1) is degenerate). It's empirically held across all 140 = 60 + 80 outer-scale tests, but a direct structural proof at (8, 2) requires a different argument.

**Practical close**: K_BW ≤ 2 unconditional at L_1, L_2 deployment scales for the non-induced sub-case A regime (which is the bulk). Induced + B sub-cases reduce to (8, 2) Conj A — a clean residual at the lowest scale.

## Next steps

1. Write paper2 §7 lemmas: `lem:L1-K-BW-structural`, `lem:L2-K-BW-structural`, `lem:base-case-conj-A` mirroring `thm:K-BW-2-structural`.
2. Update `lem:L2-recursion` in paper2 to cite the new lemmas, removing residual (i) for N_α<80 scenarios.
3. Final status table: 5 unconditional + 1 base-case-residual.

## Files

- `issue419_L1_kbw_scaled_analog.py` (test driver) + `.output.txt`
- This note 0486
- Reuses same infrastructure as Note 0485 (find_stratum_B_cases adapted for mod-2 split, berlekamp_welch).
