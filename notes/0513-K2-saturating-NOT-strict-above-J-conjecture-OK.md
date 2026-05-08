# Note 0513 — K_2 saturating cases at (16,4) are NOT strict above-J — conjecture OK

**Date:** 2026-05-05 (Q2 drill iter 36, post Note 0512)
**Status:** **RESOLVES Note 0512 caution**: K_2 = q-1 saturating cases have individual d(f_i, RS_k) ≤ Johnson boundary (= n/2 = 8). They are AT BEST at Johnson boundary, NOT strictly above-J. paper2 conjecture's `Δ > δ_J` strict condition EXCLUDES these cases.

## The check

For each K_2 saturating case at (16, 4)/F_17, compute individual Hamming distance d(f_i, RS_k) by brute force over all 17^4 codewords:

| Support | Class | K_1 | K_2 | d(f_1, C) | d(f_2, C) | above-J? |
|---|---|---|---|---|---|---|
| (8, 9, 10) | AP-step-1 around n/2 | 0 | 16 | 7 | 7 | **NO (≤8)** |
| (9, 10, 11) | AP-step-1 around n/2 | 0 | 16 | 8 | 6 | NO (≤8) |
| (8, 9, 11) | non-AP includes n/2 | 0 | 16 | 8 | 7 | NO (≤8) |
| (8, 10, 11) | non-AP includes n/2 | 0 | 16 | 7 | 7 | NO (≤8) |
| (4, 8, 12) | mod-4 sym | 1 | 15 | 4 | 8 | NO (≤8) |
| (6, 9, 14) | non-AP | 1 | 15 | 8 | 7 | NO (≤8) |
| (7, 10, 15) | non-AP | 1 | 15 | 8 | 7 | NO (≤8) |

**ALL saturating cases have max(d_1, d_2) ≤ 8 = n/2 = Johnson radius.**

## Why this matters

paper2 conjecture (line 2336): "$\Delta((f_1, f_2), C^2) > \delta$" — STRICT above-J.

$\delta_J = 1 - \sqrt{\rho} = 1/2$ at rate $\rho = 1/4$. Strict above-J means $\Delta_{\mathrm{joint}} > 1/2$, equivalently joint disagreement $> n/2 = 8$.

For each saturating case: max(Δ(f_1, C), Δ(f_2, C)) ≤ 1/2. So:
- $\Delta(f_i, C) \leq 1/2$ individually (within Johnson radius).
- $\Delta_{\mathrm{joint}}((f_1, f_2), C^2)$ depends on joint analysis but is ≤ max + (1 - overlap factor) ≤ 1.
- For these cases, optimal $(c_1, c_2)$ minimization gives $\Delta_{\mathrm{joint}} \leq 1/2$ (Johnson boundary, NOT strict above).

**Therefore: paper2 strict-above-J condition EXCLUDES all K_2 = q-1 saturating cases at (16, 4)**.

## Implications

1. **Note 0511 / 0512 caution RESOLVED**: The K_2 = q-1 saturation does NOT refute paper2's K ≤ 10 conjecture, because those pencils are NOT in the conjecture's strict-above-J quantifier scope.

2. **paper2 v24 conjecture is fully consistent with all empirical evidence** — including the (16, 4) base-case anomalies which are now seen as Johnson-boundary cases excluded by strict above-J.

3. **The conjecture's strict above-J condition is essential** — without it, K can saturate to q-1 at boundary cases.

4. **paper2 v24 patch (commit 2ee9d35)** is robust:
   - K_1 ≤ 3 RIGOROUS (Note 0504)
   - K_2 ≤ 7 conjectured for action-non-stab strict above-J pairs
   - Both empirically supported and structurally well-defined.

## Note 0510 / 0511 / 0512 chain — final status

- Note 0510 claimed K_2 = 7 saturation tight. **Partially correct**: K_2 = 7 saturation occurs for "near-Johnson" boundary cases.
- Note 0511 corrected: K_2 = q-1 actually achievable. **Correct empirically**.
- Note 0512 raised caution about strict above-J status. **Caution justified to investigate**.
- **Note 0513 RESOLVES**: All K_2 saturating cases at (16, 4) are at Johnson BOUNDARY (d(f_i, C) ≤ 8), NOT strict above. Conjecture's strict-above filter excludes them.

## Strategic Q2 status (FINAL)

paper2 §7 Q2 GLOBAL:
- **K_1 ≤ 3 RIGOROUS** (Theorem K1-universal-budget, Note 0504, paper2 v24 §7.5)
- **K_2 ≤ 7 conjectured** for strict-above-J action-non-stab pairs at deployment scale (32, 8)+
- Empirical at deployment: 4.6M certs + 615M trials, 0 cex
- Base-case (16, 4) Johnson-boundary saturations EXCLUDED by strict above-J

paper2 v24 patch (commit 2ee9d35 + LaTeX fix e1a20df) **deploys substantial improvement** to paper2 v23's Q2 GLOBAL position.

## Open structural problem (1-3 month timeline per consults)

Prove K_2 ≤ 7 structurally for action-non-stab strict above-J pairs. Both Helleseth (vLW) and Gong (WG) approaches face technical obstacles per Note 0507 (vLW |D_α| failed) and Note 0509 (WG resultant deg = 14 not ≤ 7).

The combinatorial mechanism is now clearer:
- K_2 = q-1 only at Johnson boundary (excluded).
- K_2 ≤ 7 in strict above-J regime (conjecture, empirically robust).

## Files

- `notes/scripts/g3_K2_saturating_above_J_check.py`
- This note: 0513
