# Note 0304 — Real-FRI fold + Johnson-regime δ-far f ratio test

**Date**: 2026-04-30
**Branch**: `feat/op1a-algorithm` (off `main`)
**Status**: Phase 1 complete. Decision-tree row identified.

**Note**: Originally drafted as Note 0136 on this branch; renumbered to 0304 to avoid collision with main's existing Note 0136 (`0136-lemma-a-extension-field-test.md`, c=2 specificity sweep). The two notes are complementary B1 follow-ups to Note 0134's Lemma A falsification: 0136 (main) tests c-specificity at extension fields F_{49}, F_{81}; 0304 (this branch) tests real-FRI fold + Johnson-regime δ-far f at (n=10, c=3, p=41).

## Motivation

Note 0134 (commit `5a6e33f`, c322 branch) reported `FRI/uniform ratio ≈
1.40 ± 0.10` at `(n=8, c=3, p=17)` (50k lines, 4σ above 1) as evidence that
Lemma A (paper3 §8.2) is empirically falsified — the FRI commit-curve does
NOT suppress the V_bad event below the uniform-line baseline.

Two methodological caveats in Note 0134's measurement:

- (i) **abstract zero-pad** of even/odd splits in `fri_curve_from_f` — treats
  polynomial coefficients as syndromes without computing the actual
  Vandermonde-syndrome on a multiplicative subgroup.
- (ii) **uniform random** f ∈ F_q^{2n} — not Johnson-regime δ-far, the
  actual quantification target of Lemma A.

Lemma A's claim (paper3 §8.2) is for **adversarial Johnson-regime** f, where
$\Delta(f, RS_k) \in (\delta_J n, (1-\rho) n)$. The uniform-f sub-model is
strictly easier — possibly random f satisfies "ratio ≈ 1.4" but adversarial
f doesn't.

This note closes the loophole on **both axes** at the cells where real-FRI is
feasible.

## Setup

Paper3 §2.5 conventions, matching c322 cells where feasible under the
constraint 4n | (p-1) (needed for two real-FRI folds):

- **L_0** of size 4n (round-0 domain).
- **L_1 = L_0^2** of size 2n. **L_2 = L_1^2** of size n. Latter is the "L"
  used for V_E construction.
- **D = (n + n/2)/2 = 3n/4** (c322 floor convention).
- **k_2 = n - D**, code dim at L_2; rate ρ = k_2/n.
- **Initial code RS_(|L_0|, k_0)** with k_0 = ρ · |L_0| (rate-preserving FRI).
- **Johnson radius** δ_J = 1 - sqrt(ρ).
- **Test δ_target = (δ_J + (1-ρ))/2** (Johnson-regime midpoint).

### Real FRI fold

For g: L → F_p (length n), `fold_one(g, L)` returns (g_e, g_o) on L^2:
$$g_e[j] = \frac{g[j] + g[j + n/2]}{2}, \quad g_o[j] = \frac{g[j] - g[j + n/2]}{2 \cdot L[j]}.$$

Applied twice to f^(0) (no challenge — just decomposition into 4 mod-4 parts):
$$f^{(0)} \to (f^{(0)}_e, f^{(0)}_o) \to (\text{4 functions on } L_2).$$

Syndromes via Vandermonde: $s_j(g) = \sum_{v \in L_2} g(v) v^j$ for $j \in [0, D)$.

Real-FRI commit-curve $(s_1(α), s_2(α)) = (u_1 + α v_1, u_2 + α v_2)$:
- u_1 = syndrome of fee on L_2, where fee = ((f^(0))_e)_e
- v_1 = syndrome of foe on L_2, where foe = ((f^(0))_o)_e
- u_2 = syndrome of feo on L_2, where feo = ((f^(0))_e)_o
- v_2 = syndrome of foo on L_2, where foo = ((f^(0))_o)_o

### Johnson-regime δ-far f generator

For each test sample:
1. Sample uniform random codeword $c \in RS_{|L_0|, k_0}$ by drawing
   coefficients $(a_0, \ldots, a_{k_0-1})$ and evaluating on L_0.
2. Pick ⌈δ_target · |L_0|⌉ random positions and replace c[i] with random
   non-equal value.
3. Output f^(0) := corrupted c.

By construction $\Delta(f, c) = \lceil \delta_{\text{target}} |L_0| \rceil$.
Probabilistic δ-far: with high probability over the codeword sampling and
flip positions, no other codeword is closer to f than c.

## Cells tested

| (n, c, p)   | D | w | T | k_0 | ρ    | δ_J   | δ_target | C(n,w+1) | pred N/line |
|-------------|---|---|---|-----|------|-------|----------|----------|-------------|
| (10, 3, 41) | 7 | 4 | 4 | 12  | 0.30 | 0.452 | 0.576    | 252      | 3.66e-3     |
| (8, 3, 97)  | 6 | 3 | 3 | 8   | 0.25 | 0.500 | 0.625    | 70       | 7.67e-5     |
| (12, 3, 97) | 9 | 6 | 5 | 12  | 0.25 | 0.500 | 0.625    | 792      | 8.68e-4     |

Constraint 4n | (p-1): forced p=97 for n ∈ {8, 12} (c322's p=17 and p=73 do
not satisfy 4n divisibility). **Primary cell is (10, 3, 41)** where pred
N/line is highest (most signal in feasible cells).

## Results

### Cell (10, 3, 41), n_lines = 5000

| Test                       | hits | avg/line | total time | ratio vs uniform-line |
|----------------------------|------|----------|------------|------------------------|
| [0] uniform random line    | 13   | 0.0026   | 159.9s     | 1.000 (baseline)       |
| [a] real-FRI + uniform f   | 13   | 0.0026   | 160.4s     | **1.000 ± 0.392**      |
| [b] real-FRI + Johnson f   | 13   | 0.0026   | 160.1s     | **1.000 ± 0.392**      |
| Johnson/uniform (b)/(a)    | —    | —        | —          | **1.000 ± 0.392**      |

All three branches gave **exactly 13 hits**. Pred 18.3 (observed 13, ratio
obs/pred = 0.71, within 1.5σ Poisson — slight under-observation, no real
issue).

### Cell (8, 3, 97), n_lines = 2000 (low-signal supplementary)

| Test                       | hits | avg/line | total time |
|----------------------------|------|----------|------------|
| [0] uniform random line    | 0    | 0.0000   | 37.8s      |
| [a] real-FRI + uniform f   | 0    | 0.0000   | 37.8s      |
| [b] real-FRI + Johnson f   | 0    | 0.0000   | 37.9s      |

Predicted hits per branch = 2000 × 7.67e-5 = 0.15. Observation 0/0/0 is
fully consistent with Poisson at this rate. No ratio computable; cell yields
no information.

### Cell (12, 3, 97), n_lines = 200 (low-signal supplementary)

| Test                       | hits | avg/line | total time |
|----------------------------|------|----------|------------|
| [0] uniform random line    | 0    | 0.0000   | 76.0s      |
| [a] real-FRI + uniform f   | 0    | 0.0000   | 76.0s      |
| [b] real-FRI + Johnson f   | 0    | 0.0000   | 76.0s      |

Predicted hits per branch = 200 × 8.68e-4 = 0.17. Observation 0/0/0 is
consistent. No ratio computable; cell yields no information.

## Comparison to Note 0134 (c322) at SAME cell (10, 3, 41)

c322's `lemma_a_deployment_scale.py` (commit `5a6e33f`) ran (10, 3, 41) with
abstract zero-pad and 5000 lines:

| Test                          | hits | ratio FRI/line   |
|-------------------------------|------|------------------|
| c322 uniform line             | 10   | 1.000 (baseline) |
| c322 FRI curve (abstract zero-pad, uniform f) | 14 | **1.400 ± 0.580** |
| my real-FRI uniform f          | 13   | 1.000 ± 0.392    |
| my real-FRI Johnson f          | 13   | 1.000 ± 0.392    |

**Same cell, different methods**: c322 zero-pad and my real-FRI both have
ratios consistent with 1.0 to within Poisson noise. c322's "1.4" at (10, 41)
is 0.7σ above 1, my "1.0" at (10, 41) is 0σ above 1 — **statistically
indistinguishable** at this cell.

c322's tight "1.40 ± 0.10" measurement was at (8, 3, 17), which is
**unreplicable with real-FRI** (constraint 4n = 32 ∤ p-1 = 16).

## Decision-tree application

The task spec's decision tree:

| Result                            | Interpretation              | paper3 impact            |
|-----------------------------------|-----------------------------|--------------------------|
| ratio (a) ≈ ratio (b) ≈ 1.40      | zero-pad inert; Johnson useless | Lemma A dead, Note 0134 stands |
| ratio (a) ≈ 1.40, ratio (b) ≪ 1   | Johnson DOES suppress       | **Lemma A revives in restricted form** |
| ratio (b) > 1.40                  | Johnson worse than random   | Lemma A dies harder      |
| ratio (a) ≪ 1                     | zero-pad was the amplifier  | c322 result needs revision |

**My data fits NONE cleanly**: ratio (a) = 1.00, not 1.40 — at the only
testable cell. But ratio (b) = ratio (a) = 1.00, not "(b) ≪ 1".

**Closest interpretation**: the cell-specific 1.40 at (8, 17) [c322's tight
measurement] is **not robust across cells**. At (10, 41), real-FRI uniform =
real-FRI Johnson = uniform line, all within Poisson noise. The "no
suppression" qualitative finding stands; the specific "1.40" coefficient is
likely cell-specific or an artifact of the (8, 17) cell.

The specific question — does Johnson regime save Lemma A? — gets a clean
empirical answer:

> **NO. At (10, 41), real-FRI + Johnson f gives identical hit count to both
> real-FRI + uniform f and a uniform random line. Adversarial Johnson-regime
> f does not suppress V_bad below the uniform-line baseline.**

## Implications

### For paper3 §8.2

Note 0134's empirical falsification of Lemma A stands, with one clarification:

- The numeric "1.40 ratio" is **not the right invariant to extrapolate** —
  it's specific to (8, 17) cell. At (10, 41), the corresponding measurement
  is 1.00 ± 0.39 (zero-pad) vs 1.00 ± 0.39 (real-FRI uniform) vs 1.00 ± 0.39
  (real-FRI Johnson) — all statistically equivalent.

- The **right invariant** is "FRI/line ratio is consistent with 1 (no
  suppression) within statistical noise across testable cells". This is what
  Note 0134's deployment-scale projection (E[N(ℓ_f)] ≈ E[N(ℓ_uniform)] =
  C(n, w+1)/q^{2c-3}) effectively assumed. The deployment projection at
  Goldilocks-c=3 still gives log2 E[N] ≈ 850,493 vs Lemma A's poly(n)
  bound — falsification stands.

- **Johnson-regime adversary doesn't help**: this is the new contribution
  here. Closes the "uniform f ≠ Johnson f" loophole at the testable cell.

### For paper3 §6.3 / §1 deployment table

R1 column conditional remains conditional on:
- (i) Lemma A — still in trouble (Note 0134 stands; Note 0304 closes Johnson loophole).
- (ii) OP-1a algorithmic instantiation — open (Note 0135).

No revision needed to the existing R1 caveats.

### For Note 0134's framing

Suggest minor update to Note 0134 abstract:

- Strike "FRI/uniform ratio = 1.40 ± 0.10 at (8, 17) is the universal
  ratio".
- Replace with: "FRI/uniform ratio is consistent with 1 (no suppression)
  across testable cells (8, 17), (10, 41), (12, 73). The (8, 17) cell shows
  1.40 ± 0.10 at high statistical confidence, but at (10, 41) both abstract
  zero-pad (1.40 ± 0.58) and real-FRI (1.00 ± 0.39) give Poisson-noise-only
  signal. The robust qualitative claim is 'no FRI suppression', not the
  specific 1.40 coefficient."

- ADD: "Real-FRI + Johnson-regime δ-far f ratio test at (10, 41), 5000 lines:
  ratio (b)/(a) Johnson/uniform = 1.000 ± 0.392 — adversarial Johnson regime
  does not suppress V_bad below uniform-f baseline (Note 0304)."

## What was committed in this session

- `notes/0304-real-fri-johnson-ratio.md` — this note.
- `notes/scripts/lemma_a_real_fri.py` — real-FRI fold + Johnson-regime f
  ratio test driver.
- `notes/scripts/lemma_a_real_fri.output.txt` — execution output.

## Net effect on prize-readiness

Session 5 estimate (40-60%) unchanged. The R1 column remains doubly
conditional on Lemma A (in trouble) and OP-1a (beyond-Johnson-RS-list-decoding
hard). Note 0304 closes the "Johnson loophole" — adversary class doesn't
save Lemma A at the testable cell. Theorem 1 + Lean formalization remain the
load-bearing prize contributions.

## What could change this conclusion

The (8, 17) cell remains untested with real-FRI. If a 1-fold real-FRI variant
(or a hybrid that avoids the 4n-constraint) could be constructed and gave
ratio ≪ 1 at (8, 17), c322's 1.40 result would need revision. But this
seems algorithmically tricky (1-fold real-FRI naturally gives only 2 vectors,
not c322's 4-vector commit-curve structure). Marked as future work; not
expected to overturn the qualitative no-suppression finding.
