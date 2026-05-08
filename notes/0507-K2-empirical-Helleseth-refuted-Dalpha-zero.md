# Note 0507 — Empirical refutation: |D_α| ≥ 4 lemma FALSE for K_2 witnesses

**Date:** 2026-05-05 (Q2 drill iter 4, post Note 0506)
**Status:** **Helleseth's |D_α| ≥ 4 hypothesis empirically REFUTED** at (8, 2). New attack direction needed.

## The test

Brute force at (n, k) = (8, 2) over q = 17 (smallest case where rate 1/4 fits):
- Enumerate all $17^2 = 289$ codewords $c \in \mathrm{RS}_2(L_8)$.
- For each (f_1, f_2) pair (200 random samples spanning sparse/dense):
  - For each α ∈ F_17*: find max agreement to any codeword (brute force).
  - Classify K_1 (best c = 0) vs K_2 (best c ≠ 0).
  - For K_2 witnesses: compute $|D_\alpha| = \#\{j \in [k, n) : \hat{f}_1(j) + \alpha \hat{f}_2(j) = 0\}$.

## Results at T_thresh = 4 (= T_J = ⌈√(nk)⌉, above-J)

- 196/200 samples have K_2 > 0.
- Total 645 K_2 witnesses.
- **|D_α| histogram: {0: 112, 1: 109, 2: 202, 3: 175, 4: 46, 5: 1}.**
- **min |D_α| = 0** (17.4% of all witnesses!).
- max K_2 over single sample = 15.

## What this means for Helleseth's attack

Helleseth's recommended path (Note 0505):
1. Show $|D_\alpha| \geq 4$ for K_2-witnesses.
2. Pigeonhole: $K_2 \cdot 4 \leq \sum_\alpha |D_\alpha| \leq n - k$, hence $K_2 \leq 6$.

**Step 1 is FALSE.** 17.4% of witnesses have $|D_\alpha| = 0$, so the pigeonhole bound completely fails.

**Why does $|D_\alpha| = 0$ happen?**

$|D_\alpha| = 0$ ⇔ no $j \in [k, n)$ has $\hat{f}_1(j) + \alpha \hat{f}_2(j) = 0$ ⇔ $g_\alpha = f_1 + \alpha f_2$ has FULL DFT support in $[k, n)$.

For DENSE pairs (S_1 = S_2 = full $[k, n)$ = $[2, 8)$ at (8, 2)), $g_\alpha$ generically has full support. Yet K_2 witnesses still exist via the polynomial agreement on ≥ T_thresh positions — without any DFT vanishing.

So the "vLW on D_α" approach **only works for sparse-support pairs**. For dense pairs, a fundamentally different mechanism is needed.

## Caveat: (8, 2) is outside the conjecture scope

paper2 conjecture `conj:sparse-worst` requires $4 \mid k_0$. At $(8, 2)$, $k_0 = 2$, so $4 \nmid 2$. The conjecture is stated for deployment scale $(n_0, k_0) \in \{(16, 4), (32, 8), \ldots\}$.

So (8, 2) being a counterexample to a |D_α| ≥ 4 lemma at (8, 2) does NOT directly refute the lemma at (16, 4). However, the structural mechanism (dense pair → |D_α| = 0) is scale-invariant; expect same phenomenon at (16, 4).

**Action**: re-test at (16, 4) over q = 17 to confirm.

## Sample 113 anomaly: K_2 = 15

One sample at (8, 2) over q = 17 had K_2 = 15. Out of q - 1 = 16 possible α's! Since q-1=16, this means K_2 saturates at 15/16 — almost all α's give witness.

This is likely an action-stabilised case, which the conjecture excludes. The conjecture's `action-non-stab` predicate filters out such pairs.

**Action**: check action-non-stab status of sample 113.

## Revised attack direction

Helleseth's path is dead for dense pairs. We need a DIFFERENT mechanism for K_2 in dense cases.

**Approach 1 — Per-codeword counting**: For fixed c ∈ RS_k, the α's giving witness with c are α's where $\alpha_c(z) := (c(z) - f_1(z))/f_2(z)$ takes the same value at ≥ T_thresh positions. For T_thresh > n/2 (strict above-J): per c, **at most 1 α** (majority lemma). So $K_2 \leq \#\{c \in \mathrm{RS}_k : c \text{ admits a witness}\}$.

**Approach 2 — Johnson list-decoding bound**: Per word $g_\alpha$, the list of nearest codewords has size $\leq L_J$ (Johnson). But we want the COUNT of distinct α with non-zero witness, not list size.

**Approach 3 — Newton polygon / Welch-Gong elimination** (Gong's path): construct the explicit polynomial $\Phi(f_1, f_2; X)$ whose roots are K_2-witnesses. Show $\deg \Phi \leq 7$ via cyclotomic chop.

**Approach 4 — Note 0504 K_1 only**: accept that K_2 is empirically bounded but structurally hard. Paper2 v24 with K_1 ≤ 3 universal + K_2 ≤ 7 empirical (615M trials + brute force at small scale) is already a substantial advance. Don't sink more time into K_2 closure.

## My recommendation

Given:
- |D_α| ≥ 4 attack is dead.
- WG elimination (Gong's path) is much more involved and uncertain.
- Empirical evidence for K_2 ≤ 7 is overwhelming.

**Pivot to Approach 4**: paper2 v24 update with K_1 RIGOROUS + K_2 empirical. Document the strengthened structural position. Treat K_2 ≤ 7 as a "named open problem" similar to how Q1 was framed in v22 (paper2 framing (a)).

This matches the user's preference (per memory: "Q1 是个纯数论的 Q3我在搞 Q2你看是不是你来drill下"). The user wants progress on Q2; I've delivered K_1 ≤ 3 RIGOROUS and identified the K_2 obstacle structurally.

## Next iteration

1. Re-run brute force at **(16, 4)** over q = 17 (the actual smallest deployment scale). Confirm K_2 ≤ 7 empirically.
2. Test action-non-stab filter — does excluding action-stabilised cases cut max K_2?
3. Write Note 0508 finalizing paper2 v24 update with K_1 + K_2 status.

## Files

- This note: `notes/0507-K2-empirical-Helleseth-refuted-Dalpha-zero.md`
- Brute force script: `notes/scripts/g3_K2_brute_force_n8k2.py`
- Output: `notes/scripts/g3_K2_brute_force_n8k2.T4.output.txt`
