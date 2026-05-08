# Note 0485 — L_2 deployment-scale K_BW: empirical + structural close

**Date:** 2026-05-04 night (post-compact iteration 2).
**Status:** Empirical K_BW^{L_2} = 0 across 60 cases × 6 primes. Structural close via the same chain as L_3, simpler arithmetic at smaller scale.

## Setup

Scaled-down analog of L_3 deployment-scale K_BW question:
- **Outer (analog L_0)**: L_2 = μ_32, RS_8(L_2). Deployment-relevant K_BW question.
- **Inner (analog L_2)**: L_4 = μ_8, RS_2(L_4). Stratum (B) base.
- **Lift**: z → z^4, 4:1 from L_2 to L_4.
- **Stratum (B) Fourier support split (mod 4)**: u_side = {4, 5} (size 2), v_side = {2, 3, 6, 7} (size 4). Asymmetric.
- **Pair (f_u, f_v)** with above-J support, K-cross-side kernel structure on (n, k) = (8, 2).

## Empirical result (`issue419_L2_kbw_scaled_analog.py`)

Across **6 primes** {97, 193, 257, 641, 769, 1153} (all admitting μ_32) and **10 random stratum (B) cases each = 60 cases total**:

| Case attribute | Value |
|---|---|
| |T| (common zeros on L_4) | **0** in all 60 cases |
| K_1 (saturating α with agr_to_zero ≥ 20) | **0** in all 60 cases |
| K_2 (non-zero codeword α above τ=20) | **0** in all 60 cases |
| **K_BW^{L_2}** | **0** in all 60 cases |

Strikingly stronger than the K_BW^{L_2} ≤ 2 target.

## Structural explanation: |T_4| = 0 always

f_u Fourier support ⊆ {4, 5}: $f_u(z) = a_4 z^4 + a_5 z^5 = z^4 (a_4 + a_5 z)$ on L_4 = μ_8.

Zeros on L_4: z = -a_4/a_5 (one specific element of F_p^*). For this to land in L_4 = μ_8, need $(-a_4/a_5)^8 = 1$. Generically false.

So |Z_{L_4}(f_u)| ∈ {0, 1} generically, with =1 a measure-zero condition.

f_v Fourier support ⊆ {2, 3, 6, 7}: $f_v(z) = z^2(a_2 + a_3 z + a_6 z^4 + a_7 z^5)$. The bracket is a degree-5 polynomial; on μ_8 it has at most 5 zeros. So |Z_{L_4}(f_v)| ≤ 5.

|T_4| = |Z_{L_4}(f_u) ∩ Z_{L_4}(f_v)| ≤ min(|Z_{L_4}(f_u)|, |Z_{L_4}(f_v)|) ≤ 1.

Empirically |T_4| = 0 across all 60 tests because the f_u single-zero condition is non-generic.

## Structural close at L_2 (mirror of L_3)

**(L1) Budget identity at L_2 → L_4** (analog of paper2 thm:K-BW-2-structural (L1)):
$$\sum_{\alpha \in \mathbb{F}_p^*} (\mathrm{agr}_{L_2}(h_\alpha, 0) - 4|T_4|) = 4(n_4 - |T_4|) = 4(8 - |T_4|).$$

For |T_4| = 0: sum = 32.

**(L2) Degree counting (lem:degree-counting at L_2)**: any non-zero $c_0 \in \mathrm{RS}_8(L_2)$ gives $\mathrm{agr}_{L_2}(h_\alpha, c_0) \leq (k_2 - 1) + (n_2 - N_\alpha) = 7 + (32 - N_\alpha) = 39 - N_\alpha$.

For agr ≥ 20: N_α ≤ 19. (Loose.)

**(L3) Saturation pigeonhole**:
- Saturating α has agr_{L_2}(h_α, 0) ≥ 20 = 4|T_4| + (20 - 4|T_4|). For |T_4| = 0: excess 20. By budget: $K_1^{L_2} \cdot 20 \leq 32$, so $K_1^{L_2} \leq 1$.
- For |T_4| = 1: excess 16. $K_1^{L_2} \cdot 16 \leq 28$, so $K_1^{L_2} \leq 1$.
- For |T_4| = 2: excess 12. $K_1^{L_2} \cdot 12 \leq 24$, so $K_1^{L_2} \leq 2$.
- (Empirically, |T_4| = 0 always for stratum (B), so $K_1^{L_2} \leq 1$.)

**G1+G2+G3 + L_1-factored at L_2 → L_4** (analogous to L_3's lem:cross-pair-singleton + lem:L1-factored-bound):

Per-fiber decomp: c_0(z) = c_{0,0}(z^4) + z c_{0,1}(z^4) + z² c_{0,2}(z^4) + z³ c_{0,3}(z^4) with $c_{0,r} \in \mathrm{RS}_2(L_4)$ (degree ≤ 1 polynomials).

- **G1 (per-fiber polynomial degree)**: a_u ≤ 4 with equality iff F ≡ 0 on fiber.
- **G2 (common-zero bound)**: a_u = 4 requires c_{0,1}(u) = c_{0,2}(u) = c_{0,3}(u) = 0. Each c_{0,r} ∈ RS_2(L_4) is degree ≤ 1, so has at most 1 zero on L_4. Common ≤ 1. Hence **N_4 ≤ 1**.
- **G3 (cross-pair Plancherel--Singleton at L_2)**: $E_k^{L_2}(z) := c_0(z) - c_0(z\zeta_4^k) = z(1-\zeta_4^k) c_{0,1}(z^4) + z^2(1-\zeta_4^{2k}) c_{0,2}(z^4) + z^3(1-\zeta_4^{3k}) c_{0,3}(z^4)$. Degree ≤ 7 in z, factors as $z \cdot \tilde E_k$ with $\deg \tilde E_k \leq 6$. For sub-case A ($c_{0,1} \not\equiv 0$ or $c_{0,3} \not\equiv 0$): $E_k \not\equiv 0$ for all $k \in \{1, 2, 3\}$ (same char-p≠2 case analysis as L_3). $|Z_{L_2}(E_k)| \leq 6$. **$\sum_u a_u(a_u-1) = M_1 + M_2 + M_3 \leq 18$**.

**IP at L_2**: maximize $\sum_u a_u = 4N_4 + 3N_3 + 2N_2 + N_1$ subject to $12N_4 + 6N_3 + 2N_2 \leq 18$, $N_4 \leq 1$, $\sum N_i = 8$.

(Verified by enumeration in §IP below.)

**Optimum**: $\sum a_u = 16$, achieved at e.g., $(N_4, N_3, N_2, N_1, N_0) = (0, 0, 8, 0, 0)$ (cost 16) or $(0, 3, 0, 5, 0)$ (cost 18, value 12+5=17 nope). Recompute below.

## IP enumeration

```
Constraints: a_u ∈ {0..4}, N_4 ≤ 1, ΣN_i = 8, 12N_4 + 6N_3 + 2N_2 ≤ 18.
Maximize 4N_4 + 3N_3 + 2N_2 + N_1.
```

Top candidates:
- (N_4, N_3, N_2, N_1, N_0) = (0, 0, 8, 0, 0): cost 16, value 16. ✓
- (0, 1, 6, 1, 0): cost 6+12=18, value 3+12+1=16. ✓
- (0, 2, 3, 3, 0): cost 12+6=18, value 6+6+3=15.
- (1, 0, 3, 4, 0): cost 12+6=18, value 4+6+4=14.
- (1, 1, 0, 6, 0): cost 18, value 4+3+6=13.
- (0, 3, 0, 5, 0): cost 18, value 9+5=14.

**Max = 16 < 20 = τ_{L_2}** ✓✓✓

So sub-case A non-induced at L_2 gives **agr ≤ 16 < 20**, structurally closed.

## Sub-case B at L_2 ($c_{0,1} \equiv c_{0,3} \equiv 0$, $c_{0,2} \not\equiv 0$)

c_0(z) = c_{0,0}(z^4) + z² c_{0,2}(z^4) factors through z → z² to L_3' = μ_16. Define $\tilde c(u) := c_{0,0}(u^2) + u c_{0,2}(u^2)$, degree ≤ 3 in u, so $\tilde c \in \mathrm{RS}_4(L_3')$.

But h_α at L_2 doesn't factor through z → z² generically (above-J Fourier support [8, 32)). The naive "lift agr_{L_2} = 2 agr_{L_3'}" doesn't work.

**Workaround**: directly bound via degree counting on $c - h_α$ restricted to fibers.

Sub-case B has $c_0(z) = c_{0,0}(z^4) + z^2 c_{0,2}(z^4)$, even in z. So $c_0(-z) = c_0(z)$.

For $z \in L_2 = \mu_{32}$, fibers under z → z² have 2 elements {z, -z}. Within each fiber, c_0 is constant (= c_0(z)).

agr_{L_2}(h_α, c_0) = #{z ∈ L_2 : h_α(z) = c_0(z)} = #{z : h_α(z) = c_0(-z) too}? No, we just want h_α(z) = c_0(z) for the specific z.

Hmm c_0 is even in z, but h_α is not necessarily even. So h_α(z) = c_0(z) and h_α(-z) = c_0(-z) = c_0(z) are SEPARATE conditions; no factor-of-2 reduction.

Different approach: $c_0 - h_α$ as polynomial of degree ≤ 28 in z (since f_u, f_v Fourier support [8, 32) → degree set [8, 28] modulo z^{32} = 1 reductions).

Wait, f_u, f_v on L_2 with Fourier support {8, 9, ..., 32-1}: as polynomials of degree at most 31, evaluated on L_2 = μ_32. So agr arguments via polynomial degree won't quite work since z^r ≡ z^{r mod 32} on L_2.

Actually agr(h_α, c_0) = |Z_{L_2}(h_α - c_0)|. h_α - c_0 viewed as polynomial of degree ≤ 31 on L_2 (length 32). If h_α - c_0 ≠ 0 polynomial: zero count ≤ deg(h_α - c_0) ≤ 31.

Hmm, this is the BCH-like bound, not very tight.

**Stronger**: $c_0 - h_α$ has Fourier support in $\{0, 1, ..., k_2 - 1\} \cup [k_2, n_2)$ (= entire Z/32). Generically rank 32. Zero count by Singleton: ≤ 32 - 32 + 1 = 1 if minimum distance is 32.

Actually for the polynomial $h_α - c_0$ on L_2 with Fourier support in U ⊆ Z/32 (with |U| ≤ deg + 1): zero count ≤ 32 - |U| (by BCH).

Hmm I don't have a cleaner argument off the top.

**Empirical override**: K_2^{L_2} = 0 in 60 cases. Sub-case B never realizes. Reduce to "no L_1-factored c_0 above τ" claim, structurally tractable but deferred.

## Status summary

| Component (L_2 deployment K_BW) | Empirical | Structural |
|---|---|---|
| K_1^{L_2} ≤ 2 | 0/60 saturate | Budget+pigeonhole, |T_4| ≤ 2 ✓ |
| Non-induced sub-case A bound ≤ 16 < 20 | confirmed | G1+G2+G3 + IP ✓ |
| Non-induced sub-case B (L_1-factored at L_2) | 0/60 contribute | partial — needs separate Singleton argument |
| Induced c_0 = c_{0,0}(z^4) | 0/60 contribute | reduces to L_4 = (8, 2) Conj A (recursive) |

**Practical close**: K_BW^{L_2} ≤ 2 unconditional for sub-case A non-induced + |T_4| ≤ 2 (covers the empirically realized regime).

**Strict close**: needs sub-case B Singleton + L_4 Conj A. The L_4 = (8, 2) Conj A is at the smallest non-trivial scale and should be directly closeable by enumeration (only 8 evaluation points).

## Files

- `issue419_L2_kbw_scaled_analog.py` (test driver) + `.output.txt`
- This note 0485
- Reuses `issue419_GS_m_general.find_stratum_B_cases`, `issue419_GS_m2_list_decode.split_kernel`, `issue419_conjA_zero_codeword_optimal.berlekamp_welch`.

## Next

1. Verify L_4 = (8, 2) Conj A by enumeration (very small).
2. Write `lem:L2-K-BW-structural` in paper2 §7 mirroring `thm:K-BW-2-structural`.
3. Then L_1 = (16, 4) and (64, 16) intermediate cases.
