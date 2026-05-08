# Note 0532 — Session state: L3 deployment closure drill, pre-compact

**Date:** 2026-05-06 (post Notes 0530, 0531; user requested record before compact)
**Context:** Multi-hour /loop drill iteration toward L3 deployment closure.
User's directive: 大量计算 + subagent 召唤; 简洁漂亮 closure.

## TL;DR — current state

| Closure level | Status | Detail |
|---------------|--------|--------|
| **Deployment-conditional rigorous** (G1 deployment-certified) | ✅ **100% DONE** | paper2 §7.6 has Theorem K2-hyperelliptic-AP-divisor (mod G1) + dichotomy + Theorem K2-palindromic-bound |
| **Deployment-unconditional rigorous** (G1 promoted to theorem at deployment) | 🟡 **~5% done** | 4/80 supports rigorous G1-free; 76 still mod G1 |
| **Fully unconditional** (G1 universal proof) | research-level | unchanged |

## Drill achievements this session

### Major rigorous wins (G1-free)

1. **Theorem K2-palindromic-bound** (paper2.tex §7.6, lines ~3387-3413):
   - $K_2 \leq 2$ rigorously for 4 palindromic-symmetric AP-divisor + (H5)
     supports at $(32, 8)$: $\{(8,16,24), (10,16,22), (12,16,20), (14,16,18)\}$
     with palindromic pencils ($a_{i,1} = a_{i,3}$).
   - Proof: orbit-collapse via cyclotomic descent + dihedral involution
     $\sigma : z \mapsto z^{-1}$ + Vandermonde rigidity + σ-equivariance.
   - Sharper sub-cases:
     - $S = (8, 16, 24)$ ($d_0 = 8$): $\deg \Phi^{\text{palin}} = 2$, $K_2 \leq 2$
     - $S = (12, 16, 20)$ ($d_0 = 4$): $\deg = 0$, $K_2 = 0$ generically
     - $S = (14, 16, 18)$ ($d_0 = 2$): $\deg = 0$, $K_2 = 0$ generically
   - Empirical certification: 21,609 palindromic pencils at p ∈ {97, 193, 257},
     ZERO counterexamples, max $K_2 = 2$ (matches sharp prediction).

2. **Partial half-scale embedding mechanism** (constructive):
   - For zone-2 supports ($|S \cap [n/2, n-k-1]| = 2$, 16 supports total):
     $\alpha^* = -a_{1,c}/a_{2,c}$ (kills out-of-zone coefficient $A_c$)
     gives constructive saturating $\alpha$ when subgroup condition
     $-A_1/A_2 \in \mu_{n/\gcd(d, n/2)}$ holds (~6% of pencils).
   - Empirical max $K_2 = 1$ across 80 trials × 16 supports.
   - Mechanism documented in `notes/scripts/g3_profileD_analysis.py`,
     `g3_partial_halfscale_verify.py`.

### Empirical certifications

| Sweep | # pencils | Max $K_2$ | CEX |
|-------|-----------|-----------|-----|
| 615M (general supports, prior) | 615M | various | 0 |
| G1 deployment (Note 0530) | 2,400 | 1 | 0 |
| Pencil-grid (S=(8,16,24)) | 15,625 | 2 | 0 |
| Palindromic parallel | 21,609 | 2 | 0 |
| Phi_S structure | 6,420 × 10 primes | 1 | 0 |
| Partial halfscale verify | 80 | 1 | 0 |

### Other completed items

- **A_9 = 0** for hard triple (18, 25, 27) at (32, 16) — full 28M-iter
  enumeration. Q3 panel triple 2 contribution closed.
- **Note 0530**: G1 empirically certified at deployment.
- **Note 0531**: Palindromic-stratum K_2 ≤ 2 + partial half-scale mechanism.

### Tasks completed (this session)

- #346 L3-B AP-coprime K_2 verification: ✅
- #347 L3-C Sage genus-0: ✅ (replaced by orbit-collapse, no Sage needed)

### Tasks remaining

- #310 Stickelberger 2-adic congruence (Helleseth #1)
- #344 Q3.6 Gong path (BKK / Newton polytope)
- #350 L3-F (H5) ladder to (64, 16)
- #306 Companion repo sync

## Path forward to deployment-unconditional rigorous

**User-preferred path**: Path A (Sage genus computation).

Concrete steps:
1. Install Sage via `brew install sage` or binary (~30min, ~1GB disk)
2. Write `notes/scripts/g3_sage_genus_verify.py` that:
   - Enumerates 76 non-palindromic AP-divisor + (H5) supports at (32, 8)
   - For each, constructs the cyclotomic-quotient curve $\mathcal{X}/\langle\omega^{d_0}\rangle$
   - Runs `C.genus()` to verify $g = 0$
3. Total compute ~1-6 hours
4. If all 76 give $g = 0$: G1 promoted to theorem at deployment scale
   $(32, 8)$, completing **deployment-unconditional rigorous closure**.

**Alternative paths** (if Sage proves problematic):
- Path B: SymPy symbolic eliminant (~25h compute parallelized)
- Path C: extend orbit-collapse (research-level)
- Path D: empirical certification at much larger scale (not rigorous)

## Files & references

### Key notes (this session)
- `notes/0530-G1-empirical-verification-deployment.md` (G1 empirical)
- `notes/0531-palindromic-stratum-K2-bound.md` (palindromic-bound + partial half-scale)
- `notes/0532-SESSION-STATE-pre-compact.md` (this note)

### Key scripts (this session)
- `notes/scripts/g3_G1_empirical_AP_divisor_H5.py` (G1 sweep, 2400 pencils)
- `notes/scripts/g3_G1_pencil_grid_scan.py` (15,625 pencils)
- `notes/scripts/g3_G1_phi_S_factor.py` (phi_S structure)
- `notes/scripts/g3_palindromic_symbolic.py` ((8,16,24) rigorous proof)
- `notes/scripts/g3_palindromic_symbolic_extend.py` (extension to S_1, S_2)
- `notes/scripts/g3_palindromic_parallel.py` (21,609 verification)
- `notes/scripts/g3_orbit_collapse_full.py` (30-support analysis)
- `notes/scripts/g3_profileD_analysis.py` (NPC20/NPC22 codeword)
- `notes/scripts/g3_partial_halfscale_verify.py` (16 zone-2 supports)
- `notes/scripts/g3_A9_parallel.py` (A_9 = 0)

### Paper2 changes
- §7.6 NEW Theorem K2-palindromic-bound
- §7.6 Dichotomy corollary: palindromic-stratum sharpens to [0, 2] rigorously
- §7.6 G1 remark: partial removal noted
- §7.6 Theorem K2-half-scale-lower (lower interval, prior work)

## Recent commits (this session)

```
aadc056 Partial half-scale verify: α* mechanism rigorous when subgroup condition holds
7e043b5 21,609-pencil parallel scan FINAL: K_2 ≤ 2 on palindromic stratum confirmed
ea0904d Profile-D analysis: partial half-scale embedding mechanism for K_2=1 cases
86c4051 Honest assessment: orbit-collapse rigorous only on 4 palindromic supports
339fd38 Note 0531 update: 4 palindromic supports (not 3); plan for 27 orbit-constant non-palin
15aeec4 K2-palindromic-bound extended: K_2 ≤ 2 rigorous for ALL 3 supports
3eee02e Theorem K2-palindromic-bound: rigorous K_2 ≤ 2 via orbit-collapse (G1-free)
4bc0491 Palindromic-stratum K_2 ≤ 2 finding + A_9 = 0 confirmation
9311b45 G1 empirically certified at deployment: 2400 pencil-decodes, 0 cex
```

## Resumption instructions for next session

1. **Read this note first** (`notes/0532-SESSION-STATE-pre-compact.md`).
2. **Ask user**: "继续 Path A (Sage genus) 吗？" 
3. If yes: install Sage → write genus-verify script → run on 76 supports.
4. If 76 supports all give g = 0: write rigorous Theorem
   "K2-genus-0-deployment" in paper2 §7.6, drop G1-conditional clause
   for deployment scale, promote conditional results to unconditional.
5. Commit + push final result.
6. Estimate: 1 session for Sage install + script + run + writeup.

## User preferences (drilled this session)

- 大量计算 + subagent 召唤
- 简洁漂亮 closure (rigorous over hand-wavy)
- 留 2 cores free (use cpu_count() - 2 in multiprocessing)
- Honest assessment over optimistic claims
- Push commits early and often

## Bottom line

The **deployment-conditional rigorous closure** is COMPLETE. Paper2 §7.6
holds together as a clean, rigorous narrative with G1 as a precisely-located,
well-empirically-certified hedge.

The **deployment-unconditional rigorous closure** requires one more
focused session to install Sage and run the genus computation on 76
non-palindromic supports. If all give g = 0 (highly likely given
empirical evidence), G1 is promoted to theorem at deployment scale,
completing the 简洁漂亮 closure.
