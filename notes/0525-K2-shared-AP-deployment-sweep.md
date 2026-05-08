# Note 0525 — K_2 shared 3-pos AP sweep at deployment + Helleseth-school consult

**Date:** 2026-05-05 (post-Note 0524 compact, L3 deployment closure drill)
**Status:** Major empirical finding + expert-prediction mismatch.

## Setup

Tool: `notes/scripts/g3_K2_shared_AP_32_8.py` — focused shared-3-pos
AP-stratified K_2 sweep using NumPy-accelerated GS m=2 list-decoder
(`gs_sudan_m2_np.gs_decode_m2_np`) at $\tau = 15$ (strict above-J at
$(32, 8)$).

For each shared-3-pos support $S = \{s_1, s_1+d, s_1+2d\} \subset [k, n-1]$:
- Sample $N$ pencils $(c_1, c_2, c_3) \times (b_1, b_2, b_3) \in (\mathbb{F}_p^*)^6$.
- Compute $K_2(f_1, f_2) := \#\{\alpha \in \mathbb{F}_p^* : \exists\ c \in C \setminus \{0\},\ d_H(f_1 + \alpha f_2, c) \leq \tau\}$.
- Track max $K_2$, count cex with $K_2 > 7$.

Stratify by $\gcd(d, n)$: AP-step-divisor ($\gcd > 1$), AP-step-coprime
($\gcd = 1$).

## Small-scale finding at $(16, 4)/\mathbb{F}_{17}$, $\tau = 8$

**Conjecture $K_2 \leq 7$ massively violated** at small scale across
*both* AP-coprime and AP-divisor strata, in 10 random pencils per
support:

| Support $S$ | step $d$ | $\gcd(d, 16)$ | max $K_2$ | mechanism |
|---|---|---|---|---|
| $(8, 9, 10)$  | 1 | 1 | **16** (saturated all $\alpha$) | consecutive |
| $(9, 10, 11)$ | 1 | 1 | **16** (saturated) | consecutive |
| $(4, 7, 10)$  | 3 | 1 | 12 | matches Note 0518 |
| $(6, 10, 14)$ | 4 | 4 | **15** | AP-divisor punctured-coset |
| $(7, 11, 15)$ | 4 | 4 | **15** | AP-divisor punctured-coset |
| $(4, 8, 12)$  | 4 | 4 | 7 | AP-divisor saturating (boundary OK) |
| $(13, 14, 15)$ | 1 | 1 | 0 | consecutive (boundary, no saturation) |

Note: $\tau = 8$ here is exactly Johnson radius
$n - \lceil\sqrt{nk}\rceil = 16 - 8 = 8$. **Boundary regime**:
agreement $\geq 8 = J$, so the K_2 count includes Johnson-tight cases.

## Helleseth-school expert prediction (subagent consult, agentId
`a55a263821e92a08e`)

The expert diagnosed:

1. **Consecutive support (8,9,10) saturation = cyclotomic-degeneracy
   artifact**: support polynomial $f_S(x) = x^{s_1}(1 + x + x^2) =
   x^{s_1} \Phi_3(-x)$. Over $\mathbb{F}_{17}$, $\Phi_3$ is irreducible
   ($3 \nmid 16$), but $\hat e$ vanishes on a $\mathbb{F}_{17}$-rational
   conjugate-pair frequency ⟹ linearized polynomial rank-1 collapse ⟹
   saturation (Helleseth 1976 Lemma 4.3).

2. **AP-divisor (6,10,14) saturation = Niho-Welch exceptional stratum**:
   $S = \omega^6 \cdot \{1, \omega^4, \omega^8\}$ is a coset of order-4
   subgroup $\langle \omega^4 \rangle$ minus one point — a "punctured
   $H$-coset" (Niho 1972, Helleseth-Kumar-Martinsen 2001). The
   Crites-Stewart hyperelliptic correspondence's hypothesis (H4)
   action-non-stab assumes *full* coset stabilizers are excluded;
   punctured-coset produces a degree-1 (genus-0) curve component the
   Cyclotomic Descent Lemma cannot bound.

3. **Predictions at $(32, 8)/\mathbb{F}_{97}$**:
   - Consecutive (8,9,10) etc.: $\Phi_3 \mid x^{32} - 1$ over $\mathbb{F}_{97}$
     (since $3 \mid 96$), so $\Phi_3$ *splits* — saturation **even
     worse**, expect $K_2 = 96$ for consecutive supports.
   - AP-coprime non-consecutive (8,15,22): generic Niho, expect
     $K_2 \leq 7$ ✓.
   - AP-divisor punctured-coset (8,12,16) step 4: expect saturation
     $K_2 \gtrsim 24$.

4. **Refinement that saves the conjecture**: add hypotheses
   - (H5) $\gcd(\Phi_S(x), x^n - 1)$ trivial (no cyclotomic
     degeneracy);
   - (H6) $S$ is not a punctured $H$-coset for any subgroup $H \leq \mu_n$.
   Both are decidable in $O(|S|^2 \log n)$ per support. The
   615M-trial sweep missed both because **independent supp1, supp2**
   randomization concentrates on Sidon-generic supports
   ($\sim 1 - O(1/n)$ density), avoiding both bad strata.

## Empirical cross-check at $(32, 8)/\mathbb{F}_{97}$, $\tau = 15$

Quick sweep (20 random shared-3-pos supports, 5 pencils each):

| Support $S$ | step $d$ | $\gcd(d, 32)$ | class | max $K_2$ |
|---|---|---|---|---|
| $(14, 15, 16)$ | 1 | 1 | AP-coprime, **consecutive** | **0** ✗ contradicts expert |
| $(15, 16, 17)$ | 1 | 1 | AP-coprime, **consecutive** | **1** ✗ contradicts expert |
| $(10, 13, 16)$ | 3 | 1 | AP-coprime | 0 |
| $(13, 22, 31)$ | 9 | 1 | AP-coprime | 0 |
| $(21, 26, 31)$ | 5 | 1 | AP-coprime | 0 |
| $(13, 17, 21)$ | 4 | 4 | AP-divisor (potential punctured-coset) | **0** |
| $(19, 23, 27)$ | 4 | 4 | AP-divisor | 0 |
| $(23, 27, 31)$ | 4 | 4 | AP-divisor | 0 |
| $(8, 10, 12)$ | 2 | 2 | AP-divisor | 0 |
| $(15, 17, 19)$ | 2 | 2 | AP-divisor | 0 |
| $(11, 19, 27)$ | 8 | 8 | AP-divisor (subgroup-coset) | 1 |
| $(9, 17, 25)$ | 8 | 8 | AP-divisor (subgroup-coset) | 0 |

**Expert prediction WRONG**: consecutive supports at deployment $(32, 8)/\mathbb{F}_{97}$ give
$K_2 \in \{0, 1\}$, NOT saturation $K_2 = 96$.

## Diagnosis: the small-scale-vs-deployment gap is the **Johnson cliff**

At $(16, 4)$: $\tau_J = n - \lceil\sqrt{nk}\rceil = 16 - 8 = 8$. The
sweep used $\tau = 8 = \tau_J$ exactly — Johnson cliff regime.
Codewords of degree $< 4$ in $\mathbb{F}_{17}^{16}$ are dense at
agreement $= 8$ — saturation is a Johnson-cliff artifact, not a
structural cex.

Strict above-J at $(16, 4)$ means $\tau \leq 7$ (agreement $\geq 9$).
**The conjecture's K_2 ≤ 7 hypothesis (H3) Δ > 1 - √ρ requires this
strict regime.**

At $(32, 8)$: $\tau_J = 16$, $\tau$-sweep uses $\tau = 15 < \tau_J$ —
strictly below Johnson cliff. K_2 ≤ 1 observed.

**Re-test plan**: re-run $(16, 4)/\mathbb{F}_{17}$ at $\tau = 7$ (strict above-J).
Predicted: K_2 drops, conjecture saved at small scale too.

## Targeted (32, 8) verification needed

The 5-pencil quick-sweep is too small. Targeted sweep:

1. **Consecutive supports** at $(32, 8)/\mathbb{F}_{97}$: $(8,9,10)$,
   $(9,10,11)$, ..., $(28, 29, 30)$ — 23 supports × 50 pencils each.
   Test expert's $\Phi_3$-splitting prediction.

2. **Punctured-coset AP-divisor**: $(0, 8, 16)$ truncated, $(0, 4, 8)$
   step 4 (subset of $\langle \omega^4\rangle$), $(8, 12, 16)$ step 4,
   etc. — test expert's punctured-coset prediction.

3. **Sidon-generic AP-coprime**: 100 random supports satisfying both
   (H5) cyclotomic-non-degenerate and (H6) not-punctured-coset, 50
   pencils each.

If consecutive + punctured-coset at deployment ALL give $K_2 \leq 7$,
expert's prediction is fully refuted, conjecture stands at deployment.
If even ONE deployment cex emerges, conjecture needs (H5)/(H6)
refinement.

## Strategic implication

Expert's analysis of *small-scale mechanism* is correct ($\Phi_3$
factor, punctured-coset). But the *deployment-scale prediction*
extrapolates incorrectly across the Johnson-cliff transition.

The cleanest path to L3 deployment closure:
1. Verify $(8,9,10) + (16,17,18) + (8,12,16)$ at $(32, 8)/\mathbb{F}_{97}$
   give $K_2 \leq 7$ directly (50 pencils each).
2. If yes: paper2 row 3b' empirical statement strengthens, K_2 ≤ 7
   at deployment validated for ALL strata (not just AP-divisor non-punctured).
3. The structural rigorization (Theorem K2-hyperelliptic) covers
   AP-divisor non-punctured. Remaining open: (H5)/(H6) closure
   structural argument — research-level, but EMPIRICALLY closed at
   deployment.

## Files

- `notes/scripts/g3_K2_shared_AP_32_8.py` — sweep script (numpy GS m=2)
- `/tmp/sweep_quick.txt` — partial output at (32, 8)/F_97
- Helleseth subagent: `agentId a55a263821e92a08e`
- Cross-references: Notes 0518, 0519, 0522, 0523, 0524.

## Next steps (this drill iteration)

1. ✅ Quick sweep at (32, 8)/F_97 — preliminary result K_2 ≤ 1 across
   all classes including consecutive.
2. ⏳ Targeted (8,9,10), (8,12,16) at deployment with 50 pencils.
3. ⏳ Re-test (16, 4)/F_17 at strict above-J $\tau = 7$ to confirm
   small-scale saturation is Johnson-cliff artifact.
4. ⏳ If both confirm: update paper2 row 3b' to "K_2 ≤ 7 at
   deployment, all strata, strengthened empirical".
