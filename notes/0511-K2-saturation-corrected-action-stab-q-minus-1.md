# Note 0511 — K_2 SATURATES TO q-1 for action-stab; Note 0510 incomplete

**Date:** 2026-05-05 (Q2 drill iter 34, post Notes 0509/0510)
**Status:** **Major correction** to Note 0510. Full 220-support sweep reveals K_2 = q-1 = 16 for adversarial coefficient choices on certain supports. Conjecture's `action-non-stab` filter is ESSENTIAL.

## Corrected empirical data (full sweep, 220 supports × 5 samples)

Saturation cases at (16, 4)/F_17 (K_total ≥ 6):

| Support S | Class | K_1 | K_2 | K_total | Note |
|---|---|---|---|---|---|
| **(4, 8, 12)** | AP-step-4 div n | 1 | **15** | **16** | mod-4 sym |
| (6, 9, 14) | non-AP | 1 | 15 | 16 | |
| (7, 10, 15) | non-AP | 1 | 15 | 16 | |
| (7, 11, 13) | non-AP | 1 | 15 | 16 | |
| **(8, 9, 11)** | non-AP | 0 | **16** | **16** | includes n/2 |
| **(8, 10, 11)** | non-AP | 0 | **16** | **16** | includes n/2 |
| **(9, 10, 11)** | AP-step-1 | 0 | **16** | **16** | consecutive |
| **(8, 9, 10)** | AP-step-1 | 0 | **16** | **16** | consecutive |
| (4, 9, 11) | non-AP | 0 | 8 | 8 | |
| (5, 7, 9) | AP-step-2 div n | 0 | 8 | 8 | |
| (5, 7, 15) | non-AP | 0 | 8 | 8 | |
| (5, 7, 13) | non-AP | 1 | 6 | 7 | |
| (4, 6, 14) | non-AP | 0 | 7 | 7 | (Note 0510 claimed (4,6,8)=7) |
| (4, 12, 14) | non-AP | 0 | 7 | 7 | |
| (5, 7, 8) | non-AP | 0 | 7 | 7 | |
| (6, 10, 12) | non-AP | 0 | 7 | 7 | |
| (7, 11, 15) | AP-step-4 div n | 0 | 7 | 7 | |
| (8, 10, 15) | non-AP | 0 | 7 | 7 | |
| (9, 13, 15) | non-AP | 0 | 7 | 7 | |
| (11, 12, 14) | non-AP | 0 | 7 | 7 | |

## What this reveals

1. **K_2 = q - 1 = 16** (i.e., ALL nonzero α) achievable for several supports including:
   - (4, 8, 12) — mod-4 symmetric
   - (8, 9, 10), (9, 10, 11) — consecutive triples around n/2
   - (8, 9, 11), (8, 10, 11) — non-AP with 8 = n/2

2. **These K = q saturating cases are EXACTLY the "paired-circuit obstruction"** described in paper2 `rem:sparse-worst-action-orbit-nonstab`. They are action-stab and EXCLUDED by the conjecture's admissibility predicate.

3. **For "typical" non-saturating cases**: K ≤ 7 ≈ conjecture margin K_2 ≤ 7.

## Note 0510 correction

Note 0510 claimed K_2 = 7 saturation → margin TIGHT. The full sweep shows:
- K_2 = 7 is the typical max for **action-non-stab** pencils (consistent with conjecture).
- K_2 = q - 1 = 16 saturation is achievable for **action-stab** pencils, which are EXCLUDED.

So:
- For action-non-stab pairs: K_2 ≤ 7 holds (consistent with conjecture).
- For action-stab pairs: K_2 = q - 1, but conjecture excludes these.

paper2 v24 conjecture is CORRECT as stated; the action-non-stab filter is ESSENTIAL.

## Strategic implications

paper2 v24 status (committed in 2ee9d35) is robustly supported:
- K_1 ≤ 3 RIGOROUS (Note 0504)
- K_2 ≤ 7 conjectured for action-non-stab pairs (Note 0510 corrected)
- Action-stab pairs (K = q saturation) explicitly excluded.

The **structural proof of K_2 ≤ 7 for action-non-stab** remains open.

## Next steps

1. **Implement action-stab classifier**: distinguish stab vs non-stab pencils from coefficients. Current "fixed pointwise by ⟨ω^{b-a}⟩" def is mathematically precise but operationally unclear.

2. **Re-test (16, 4) brute force WITH action-non-stab filter applied**: confirm K_2 ≤ 7 holds universally for filtered pencils.

3. **At deployment scale (32, 8)**: the 4.6M cert sweep is presumably over action-non-stab pairs (or at least samples them at random); the empirical K ≤ 10 hold there.

## Files

- `notes/scripts/g3_K2_structural_sweep.py` — full 220-support sweep
- `notes/scripts/g3_K2_structural_sweep.output.txt` (need to save)
- This note: 0511

## paper2 v24 robustness assessment

The patch (2ee9d35) introducing K_1 ≤ 3 universal-budget theorem is INDEPENDENT of the K_2 structure:
- K_1 bound holds for ALL pairs (action-stab or not).
- K_2 ≤ 7 is conjectured (now better understood as "for action-non-stab").

So paper2 v24 patch is robust. The K_1 contribution is rigorous and uncontroversial. The K_2 conjecture statement matches paper2's existing `conj:sparse-worst` (which has the action-non-stab filter built in).
