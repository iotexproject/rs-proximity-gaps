# Note 0518 — CS hyperelliptic K_2 ≤ 7 prediction: empirical test reveals threshold dependency

**Date:** 2026-05-05 (post Note 0517, after running cs_hyperelliptic_verify_16_4.py)
**Status:** **Brute-force test at (16, 4)/F_17 reveals K_2 count is HIGHLY THRESHOLD-DEPENDENT**. CS's predicted K_2 ≤ 7 may need precise threshold spec to hold. One pencil ((4,7,10) sample 1, strict above-J) gave K_2 = 12 at threshold d ≤ 9, **APPARENTLY EXCEEDING** the K_2 ≤ 7 prediction.

## Test setup

Script: `notes/scripts/cs_hyperelliptic_verify_16_4.py`
- (n, k, q) = (16, 4, 17)
- Brute-force min-distance: enumerate all 17^4 = 83521 codewords per α, find min d over each.
- For each support S (size 3, in syndrome window [4, 16)): 2 random samples of (c_1, c_2) coefficients.
- Threshold: d ≤ 9 (= 1 above J = δ_J·n + 1).

## Raw results

```
support_class     S             sample  K_2(d≤9)   distances histogram
AP-step-2 sat     (4, 6, 8)          0     11    {8:3, 9:8, 10:5}
AP-step-2 sat     (4, 6, 8)          1      8    {8:4, 9:4, 10:8}
AP-step-4 sat     (6, 10, 14)        0      7    {4:1, 8:1, 9:5, 10:9}
AP-step-4 sat     (6, 10, 14)        1      7    {8:5, 9:2, 10:9}
AP-step-1 ctrl    (4, 5, 6)          0      0    {10:15, 11:1}
AP-step-1 ctrl    (4, 5, 6)          1      0    {10:15, 11:1}
non-AP ctrl       (5, 7, 11)         0      9    {8:7, 9:2, 10:7}
non-AP ctrl       (5, 7, 11)         1      8    {8:4, 9:4, 10:8}
AP-step-3 ctrl    (4, 7, 10)         0     13    {8:1, 9:12, 10:3}
AP-step-3 ctrl    (4, 7, 10)         1     12    {9:12, 10:4}
```

## Critical observations

### 1. Strict above-J samples (Δ_joint = min d > δ_J·n = 8)

Only 3 of 10 samples are STRICT above-J:
- **(4, 5, 6) sample 0**: min d = 10. K_2(d≤9) = 0. ✓ Compatible with K_2 ≤ 7.
- **(4, 5, 6) sample 1**: min d = 10. K_2(d≤9) = 0. ✓ Compatible with K_2 ≤ 7.
- **(4, 7, 10) sample 1**: min d = 9. K_2(d≤9) = 12. ✗ **VIOLATES K_2 ≤ 7**.

### 2. Borderline / at-J samples (min d = 8 = δ_J·n exactly)

Most samples are at-J, not strict above-J. These are EXCLUDED from the conjecture's domain.

### 3. K_2 = 7 saturating cases (Note 0510 confirmed)

(6, 10, 14) gave K_2 = 7 in both samples. Compatible with K_2 ≤ 7 prediction.

But (6, 10, 14) sample 0 had min d = 4, which is BELOW J (BW unique-decodable). So this pencil is NOT in the conjecture domain (Δ_joint > δ_J). Its K_2 = 7 is a count under permissive threshold.

### 4. (4, 6, 8) supposed saturating

Sample 0 gave K_2 = 11, NOT 7. Sample 0 has min d = 8 (at-J), so exclusion-from-domain may apply.

## Critical issue: K_2 definition ambiguity

The brute-force K_2 = 12 at (4, 7, 10) sample 1 (strict above-J) APPEARS to violate K_2 ≤ 7. Possible interpretations:

### Interpretation A: K_2 in paper2 is at BW threshold (d ≤ τ_BW = 6)

Then K_2 = 0 for ALL strict above-J pencils trivially (since min d > 8 > 6). K_2 ≤ 7 prediction is vacuous for above-J domain.

This matches Note 0508/0510's K_BW = 0 readings.

### Interpretation B: K_2 in paper2 is at d ≤ 9 = δ_J·n + 1

Then the (4, 7, 10) sample 1 K_2 = 12 is a genuine VIOLATION. CS's K_2 ≤ 7 prediction wrong, OR the exclusion predicate (action-non-stab + strict-above-J) needs refinement.

For (4, 7, 10): differences {3, 6}. ⟨ω^3⟩ has order 16/gcd(3,16) = 16. So no non-trivial pointwise stabilizer. Action-non-stab ✓.

So (4, 7, 10) sample 1 is a STRICT above-J + action-non-stab pencil with K_2 = 12.

### Interpretation C: K_2 separated from K_1 (zero codeword)

The brute-force K_2 = 12 may include K_1 (cases where closest codeword is zero). For shared 3-pos pencil at (4,7,10), c_α has at most 12 nonzero positions (deg ≤ 10), so weight ≥ 4. d(c_α, 0) = wt(c_α) ∈ [4, 16].

If 12 α give K_2 (incl. K_1), and K_1 ≤ 3 (Note 0504), then K_2 (non-zero codeword) ≥ 9. **Still violates ≤ 7.**

This refutes interpretation C as savior.

## Diagnostic: which interpretation applies?

To decide, need to:

1. **Re-read paper2 §7** for the precise K_2 threshold.
2. **Augment script** to distinguish closest-zero vs closest-non-zero.
3. **Re-spawn CS subagent** with this anomaly to get sharper formula.

## Hypothesis: K_2 ≤ 7 is at threshold δ_J·n (= 8), not δ_J·n + 1 (= 9)

For threshold d ≤ 8:
- Strict above-J pencils have min d > 8, so K_2(d ≤ 8) = 0. ✗ Trivial.
- If we count d ≤ 8 INCLUDING d = 8 (at-J), then for (4,7,10) sample 0: K_2 = 1 (only d=8). For (4,6,8) sample 0: K_2 = 3 (d=8 thrice). Etc.

This is more compatible with K_2 ≤ 7 historically. But then the "strict above-J" condition makes K_2 vacuously 0.

## Realistic conclusion: K_2 ≤ 7 conjecture is at d ≤ δ_J·n (= 8) NOT strict-above-J

The conjecture's natural threshold is the JOHNSON RADIUS itself (d ≤ ⌊δ_J·n⌋ = 8). Strict above-J pencils trivially satisfy K_2 = 0 at this threshold.

The "interesting" K_2 counts at slightly larger threshold (d ≤ δ_J·n + ε) — this is the LIST-DECODING regime, where K_2 can grow significantly (per KKH 2026/782, asymptotically as n^τ).

**For deployment scale (32, 8) and (16, 4) at threshold d = δ_J·n + 1 = 9 or 17**: K_2 may exceed 7 for some pencils, even at strict above-J.

## Action items

1. **Update Note 0517 zone-separation table**: K_2 ≤ 7 may apply ONLY at threshold d = δ_J·n exactly (uninteresting in above-J domain) or at δ_J·n + ε for tiny ε that excludes 1/n increments.

2. **Re-test (4, 7, 10) sample 1**: confirm K_2 = 12 reproducible. Examine WHICH 12 α give d=9 — are they structured (e.g. lying on a curve in F_17)?

3. **Re-spawn CS for refinement**: present (4, 7, 10) anomaly, ask whether (a) action-non-stab predicate excludes this case, or (b) the threshold needs tightening, or (c) K_2 ≤ 7 conjecture needs revision to K_2 ≤ 12 or similar.

4. **Re-read paper2 §7 K_2 definition carefully**: precise threshold is needed before further empirical analysis.

## Strategic implication

The K_2 ≤ 7 conjecture needs PRECISE threshold definition. Without it, the conjecture is either trivial (K_2 ≤ 7 at d ≤ τ_BW automatically by Singleton) or potentially false (K_2 ≤ 7 at d ≤ δ_J·n + 1 violated by (4, 7, 10)).

This is a CRITICAL diagnostic for paper2 §sec:open Q2. Before further work, paper2 §7 K_2 definition needs unambiguous threshold spec.

## paper2 §7 K_2 ≤ 7 conjecture — actual context (post-paper2 grep)

paper2.tex §1.4 row 3b states K_2 ≤ 7 "mod Q2 (empirical, 0 cex / ~615M + brute force)".
paper2.tex line 2037-38 specifies threshold δ ∈ (δ_J(ρ), 1-ρ) for rate ρ.

**For deployment (32, 8), ρ = 1/4**: δ_J = 1/2, threshold δ ∈ (1/2, 3/4), i.e. d ∈ (16, 24].
**For (16, 4), ρ = 1/4**: δ ∈ (1/2, 3/4), d ∈ (8, 12].

Our test threshold d ≤ 9 falls within (8, 12] ✓ — so we ARE testing the conjecture at (16, 4) within the conjecture's range.

**The 615M empirical campaign in paper2 row 3b is at deployment (32, 8), NOT (16, 4)**. So the (16, 4) violation candidate is OUTSIDE the empirical evidence scope. Two possibilities:
1. K_2 ≤ 7 fails at small scale (16, 4) but holds at deployment (32, 8).
2. K_2 ≤ 7 fails at both, but 615M sampling at (32, 8) missed cex pencils.

To resolve: implement **Sudan list-decoder** for (32, 8) and re-test (8, 14, 20) (= AP-step-3 analog of (4,7,10) at (16,4)) for K_2 at d ∈ (16, 24].

Brute-force at (32, 8) is infeasible (q^k = 97^8 ≈ 7.8·10^15 codewords). Sudan list-decoder over F_q[x] runs in O(n^O(1)) and gives exact list size — ideal for K_2 enumeration.

## Revised next action items

1. **Implement Sudan list-decoder for (32, 8)/F_97 with multiplicity r=1** — bivariate interpolation P(x, y) of bidegree (a, b), (a+1)(b+1) > n, factor for y - p(x). Test on (8, 14, 20) AP-step-3 pencil at random samples.

2. **If K_2 ≤ 7 holds at (32, 8) for AP-step-3**: scale-specific phenomenon. Note 0518 (16, 4) anomaly is just small-scale noise, deployment conjecture intact.

3. **If K_2 > 7 found at (32, 8)**: paper2 conjecture FAILS. Major finding. Re-examine 615M empirical sampling protocol to see how it missed.

## Files
- This note: 0518
- Script: `notes/scripts/cs_hyperelliptic_verify_16_4.py`
- Empirical violation candidate: (4, 7, 10) sample 1 at (16, 4)/F_17, K_2(d≤9) = 12 vs CS predicted ≤ 7. Within conjecture's range (δ ∈ (8/16, 12/16]).
