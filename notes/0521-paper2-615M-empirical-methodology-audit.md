# Note 0521 — paper2 615M empirical methodology audit: information-set LOWER BOUND, not exact

**Date:** 2026-05-05 (post Note 0520, audit of 615M sampling code)
**Status:** **MAJOR METHODOLOGY ISSUE FOUND**. Read `g3_sparse_worst_deployment_empirical.py` source: the "615M empirical" is information-set sampling that produces K_lb (LOWER BOUND), NOT exact K_2 count. Per-word miss probability ~5% at default 5000 membership samples. The "0 cex / 615M" claim only validates K_lb ≤ 7, NOT K_2 ≤ 7 actual.

## Methodology audit

Source: `notes/scripts/g3_sparse_worst_deployment_empirical.py`

```python
"""
The sampler is one-sided:
  * FOUND means a concrete information set T interpolates a nearby codeword.
  * NOT FOUND is only high-confidence evidence, with miss probability reported.

So this script is empirical evidence, not a replacement for a GS/Wu list decoder.
It is designed to run safely at (32, 8, q >= 97) and to make the decoder
limitation explicit in the output.
"""
```

**The script ITSELF flags the limitation in its docstring**. paper2 v25 row 3b cites this script's output as "0 cex / ~615M empirical", but the methodology only produces K_lb, not K_2.

## Sample output verification (q=97, n=32, k=8 cell)

From `g3_sparse_worst_deployment_empirical.q97_n32_seeded.output.txt`:
```
=== issue #403 sparse-worst deployment empirical ===
cell: q=97, n=32, k=8, delta_n=17, agreement_target=15
membership_samples=5000
one-word miss probability at target agreement: 4.689e-02

--- sparse 3-pos samples: target accepted 6 ---
sparse done in 28.5s; accepted=6, attempts=7
K_sparse: min=0, max=2, mean=0.67
```

**6 sparse samples per cell**, NOT 615M. The 615M total is across many cells × many samples.

**Per-word miss probability = 4.69%**: each information set draw misses a real close codeword with 4.7% probability. K_lb undercounts by ~5% × #close_codewords on average.

## Implications

### 1. K_lb ≤ 7 does NOT imply K_2 ≤ 7

If actual K_2 = 12 (as in our (16, 4)/F_17 (4,7,10) anomaly):
- Probability that 5000 samples find ALL 12 close codewords: 1 - (1 - 0.95)^... — actually quite high if each find prob ~95%.
- BUT if information sets are CORRELATED (sampling from same word population), the miss can systematically bias.
- Especially: K_1 contamination (zero codeword) may dominate K_lb at strict above-J zone.

### 2. Sample size at (32, 8) per support is small

6 sparse samples per cell × ~3 cells (q ∈ {97, 193, 257}) = ~18 samples for sparse 3-pos. Then dense, 4-pos, 5-pos sums to maybe 100 samples per scale. Across many supports & primes: 615M is info-set draws, not pencil draws.

### 3. Random supp2 ≠ shared-support pencil

In the first run without `--same-support`:
- supp1 = (8, 16, 24), supp2 = (23, 27, 28) — DIFFERENT supports
- The pencil c_α = f_1 + α f_2 has joint DFT support = supp1 ∪ supp2 = 6 positions, NOT 3!

This is NOT testing the K_2 ≤ 7 conjecture which is for **SHARED 3-pos pencils**.

`--same-support` flag forces supp2=supp1 (shared 3-pos pencil). This is the correct test mode for our K_2 ≤ 7 verification. Initial run without it tested 6-pos joint, not 3-pos shared.

## Re-running with `--same-support` and AP-coprime supports

```bash
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
    --q 97 --n 32 --k 8 --support-search --same-support \
    --support-pool "8,11,14;8,13,18;8,15,22;10,15,20;8,12,16;8,16,24" \
    --coeff-trials 10 --membership-samples 10000
```

**Expected** (per Note 0519 three-expert prediction):
- AP-coprime supports (step 3, 5, 7) at (32, 8): K_2 ≈ 24 = n - k
- AP-divisor (step 4, 8): K_2 ≤ 7 to ≤ 13 (CS hyperelliptic bound 2|S|+1=7 may hold here)

**If observed K_lb < n - k for AP-coprime**: methodology under-counts. Per-word miss prob × K_2 ≈ 0.05 × 24 = 1.2 missed. K_lb ≈ 22-23, still ≫ 7.
**If observed K_lb > 7 for ANY AP-coprime sample**: paper2 row 3b empirical UNAMBIGUOUSLY broken at deployment scale.

## Three possible audit outcomes

| Scenario | K_lb at AP-coprime | Implication |
|---|---|---|
| **A** | All ≤ 7 | Deployment-scale field-specific protection. K_2 ≤ 7 holds at (32,8)/F_97 even though small-scale (16,4)/F_17 fails. publishable! |
| **B** | Mostly > 7 | paper2 row 3b unambiguously broken. Need conjecture revision. |
| **C** | Mixed (some > 7, some ≤ 7) | Conjecture holds with some structural predicate — investigate which AP-coprime samples failed. |

Currently waiting on shared-support audit run (background job `bq13t8gnu`).

## Strategic implication: paper2 v25 §1.4 row 3b language

Even before the audit completes, the methodology issue is alone enough to soften paper2's claim:

**Current** (paper2 v25 line 465):
> "general-$f$ global, $K_2$ component | $K_2 \leq 7$ | mod Q2 (empirical, $0$ cex / ${\sim}615$M + brute force)"

**Should be revised to**:
> "general-$f$ global, $K_2$ component | $K_2 \leq 7$ | mod Q2 (lower-bound empirical $K_{\mathrm{lb}} \leq 7$ over $\sim 615$M information-set samples; brute-force at (16, 4) only; deployment-scale exact verification OPEN)"

This honesty avoids over-claiming.

## Bottom line

paper2 v25 row 3b's 615M empirical evidence is a LOWER BOUND, not exact. The "0 cex" claim does NOT rule out K_2 > 7 actual; it only confirms K_lb ≤ 7. With per-word miss prob ~5%, this is significant under-counting for real K_2 ≈ 12-24 (per Note 0520 prediction).

Combined with Note 0520's 25/25 AP-coprime violations at (16, 4), paper2's K_2 ≤ 7 conjecture is on **very shaky empirical ground**. Critical: the in-progress shared-support AP-coprime audit at (32, 8)/F_97 will resolve which scenario (A/B/C) applies.

**Next**: wait for audit completion, write Note 0522 with the verdict.

## Files
- This note: 0521
- Audit script outputs:
  - `notes/scripts/g3_sparse_worst_AP_coprime_audit.output.txt` — initial run WITHOUT --same-support (joint 6-pos, not shared 3-pos; all K_lb ≤ 1, but irrelevant since wrong test)
  - `notes/scripts/g3_sparse_worst_AP_coprime_audit_shared.output.txt` — current shared-support audit (in progress)
- Existing 615M outputs:
  - `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_seeded.output.txt`
  - `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_dense50.output.txt`
  - `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_dense50_union.output.txt`
  - `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_medium.output.txt`
