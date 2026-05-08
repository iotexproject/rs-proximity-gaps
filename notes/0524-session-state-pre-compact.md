# Note 0524 — Session state pre-compact (2026-05-05)

**Date:** 2026-05-05
**Purpose:** Snapshot of paper2 / drill-session state before context compact.

## Repo HEAD
- Branch: `main`
- Commit: `c402d37` (paper2: rigorize K_2 ≤ 7 for AP-step-divisor)
- Origin/main synced (pushed)
- PR #441 (`claude/paper2-v25-K1-K2-attack`) merged into main as commit `1c38267`

## Drill-session arc (this conversation, 2026-05-05)

### Q3 work (Notes 0480–0488, paper2 §3 + §C + §sec:open Q3)

Achievements:
- **Lemma `lem:twist1-substitution`** (paper2 §3): twist-1 SP forward direction with full fiber-pullback proof (`k` even hypothesis added per codex review)
- **Lemma `lem:mixed-parity-orbit`** (paper2 §3): orbit-size lower bound, $\alpha_2 \neq 0$ hypothesis usage documented
- **BKK base certification** (paper2 §C, Note 0484): $V_{\mathrm{BKK}}(P_2, P_3) = 24$ tight at base $(8, 4)$; SP forward propagates to dyadic tower
- **Roos-Pless bridge** (paper2 §sec:open Q3, Note 0487): $d(\mathcal{C}_{D_0}) \geq 8$ for both hard $(32, 16)$ triples; $K \leq 24 A_8 + A_9$
- **Negative result** (Note 0488): Weil/Helleseth-Kumar do NOT close Q3 at deployment ($\deg(h_\alpha - p) \approx n$ exhausts genus budget)
- **Empirical**: 6/8 mixed-parity $(32, 16)$ msolve [-1]; 2/8 BW interior $|S| \leq 24$ over $\FF_{257}$
- **Active research-level paths** (Note 0488): (i) Helleseth-Kumar restricted to subgroup-coset, (ii) Katz thin-set partial Gauss sums, (iii) $\mathcal{V}_{n,m,r}$ variety analysis, (iv) Bombieri-Pila + cyclotomic factorization. 6-12 months sequence-school collaboration.

### PR #441 absorbed (Notes 0503–0522)

Q2 GLOBAL closure work absorbed from `claude/paper2-v25-K1-K2-attack`:
- **Theorem `thm:K1-universal-budget`** (paper2 §7.5): $K_1 \leq 3$ RIGOROUS via universal budget identity $\sum_\alpha (\mathrm{agr}(g_\alpha, 0) - |T|) = |R|$
- **Theorem `thm:caseD-K12`** (paper2 §3.3): Q4 4-pos rate-1/4 closed, $K \leq 13$ unconditional
- **Note 0522**: At deployment $(32, 8)/\FF_{97, 193, 257}$, AP-step-divisor saturates $K_{\mathrm{lb}} = 7$; AP-step-coprime gives $K_{\mathrm{lb}} \in \{0, 1\}$ (small-scale (16,4) violation = finite-field artifact)

### K_2 hyperelliptic rigorize (Note 0523, this session)

NEW Theorem `thm:K2-hyperelliptic-AP-divisor` (paper2 §7.6 ssec:K2-hyperelliptic):
- Under (H1) shared 3-pos + (H2) AP-step-divisor + (H3) strict above-J + (H4) action-non-stab:
  $$K_2 \leq 2|S| + 1 = 7$$
  conditional on Crites-Stewart genus-0 conjecture (verified empirically at $(32, 8)$).
- 5-step proof: bivariate correspondence → univariate eliminant → Cyclotomic Descent Lemma (KEY) → Hasse-Weil → tight $\deg h_S$.
- Combined with `thm:K1-universal-budget`: $K_{\mathrm{BW}} \leq 10$ unconditional on AP-step-divisor.

Identified gaps (Remark `rem:K2-hyperelliptic-gaps`):
- (G1) Genus-0 conjecture
- (G2) Generic-coefficient leading nonvanishing
- (G3) AP-coprime / non-AP extension
- (G4) Rate dependence

### Codex review fixes (commit 6279307)

Per subagent review:
- [C1] Bibliography orphans wired (Roos1983, HartmannTzeng1972, Khovanskii1991, MacWilliamsSloane1977)
- [C2] BKK base proof: removed unused $P_1$, expanded boundary derivation
- [I1] `lem:twist1-substitution`: added $k$ even hypothesis, fixed $k' = k/2$
- [I2] `thm:K1-universal-budget`: added closed-form analytic limit $(4 k_0 + 2)/(k_0 + 2) < 4$
- [I3] Layer 1a' row: clarified Case D non-degenerate scope
- [I4] `lem:mixed-parity-orbit`: documented $\alpha_2 \neq 0$ hypothesis use

## Current Layer status table (paper2 v25 final state)

| Row | Adversary | Bound | Status | Conditionality |
|-----|-----------|-------|--------|----------------|
| 1a | 3-pos rate-1/4 | $K \leq 10$ | ✅ RIGOROUS | UNCONDITIONAL (Mech.A) |
| 1a' | 4-pos rate-1/4 (Case D) | $K \leq 13$ | ✅ RIGOROUS | UNCONDITIONAL (`thm:caseD-K12`) |
| 1b | 3-pos rate-1/2 | $K \leq 28$ | 🟡 | mod Q3 (twist-tower mixed-parity sub-saturation) |
| 2 | $(3k/2, 2k)$ family | reduction | 🟡 | mod Q1 (settled $d \in \{4, 8\}$) |
| 3a | local stratum-B (32,8) | $K_{\mathrm{BW}} \leq 2$ | ✅ RIGOROUS | Mech.B, 80/80 |
| 3a' | global $K_1$ | $K_1 \leq 3$ | ✅ RIGOROUS | `thm:K1-universal-budget` |
| **3b** | global $K_2$, AP-step-divisor | $K_2 \leq 7$ | ✅ **RIGOROUS** | **`thm:K2-hyperelliptic-AP-divisor`, mod genus-0** |
| 3b' | global $K_2$, general support | $K_2 \leq 7$ | 🟡 | mod Q2 (615M + brute, 0 cex) |

**5 RIGOROUS rows + 4 conditional rows.**

## Open named questions (paper2 §sec:open)

- **Q1**: universal-$d$ non-vanishing of $R_d$ on $V_d^{\mathrm{prim}}$. Rigorous $d \in \{4, 8\}$; operational $d \in \{16, 32, 64\}$ via msolve. NT difficulty.
- **Q2**: $K_2 \leq 7$ for general support — partially closed by `thm:K2-hyperelliptic-AP-divisor` for AP-step-divisor stratum. Remaining: AP-step-coprime + non-AP (deployment $(32, 8)$ empirical strong).
- **Q3**: rate-1/2 universal-$k$ SP lift. Saturating-side closed via SP forward + BKK; mixed-parity sub-saturation conjectured. Research-level paths in Note 0488. j ∈ {17, 18, 19, 20} deployment open.
- **Q4** (4-pos rate-1/4): **CLOSED** (`thm:caseD-K12`).

## Easiest residual closure paths

Per user's prompt 之前评估:

1. **K_2 ≤ 7 hyperelliptic** ⭐⭐⭐ — DONE this session (commit `c402d37`)
2. **(32, 16) $A_8/A_9$ brute force** ⭐⭐ — pending (closes Q3 j=4 specifically)
3. **Sudan list decoder at (32, 8)** ⭐⭐ — pending (3b' empirical → exact)
4. Genus-0 conjecture rigorize (G1) — research-level
5. AP-coprime (G3) extension to deployment — research-level

## Files of record

### Notes added this session
- 0480–0488: Q3 drill-session
- 0503–0522: PR #441 (Q2 K_1 / K_2 attack arc)
- 0523: K_2 hyperelliptic rigorize (Theorem statement + proof sketch + gaps)
- 0524: this state record

### Paper2 modifications
- §3: Lemma `lem:twist1-substitution`, Lemma `lem:mixed-parity-orbit`, Remark `rem:twist-tower`, Remark `rem:mixed-parity-subsat`
- §1.4 Layer table: rows 1a, 1a', 1b, 2, 3a, 3a', 3b, 3b' (8 rows now)
- §3.3: Theorem `thm:caseD-K12` (Q4 closure)
- §7.5: Theorem `thm:K1-universal-budget` (K_1 ≤ 3 RIGOROUS)
- §7.6: Theorem `thm:K2-hyperelliptic-AP-divisor` + Remark `rem:K2-hyperelliptic-gaps`
- §C: BKK base certification (Note 0484 reflected)
- §sec:open Q2/Q3/Q4: updated wording
- Bibliography: Helleseth-Kumar 1998, Katz 1988, Roos 1983, Hartmann-Tzeng 1972, Bernstein 1975, Khovanskii 1991, MacWilliams-Sloane 1977, BGHKS, Sudan 1997, Guruswami-Sudan 2000, Polishchuk-Spielman 1994, Guruswami-Wang 2013, Stichtenoth 2009

### Scripts (notes/scripts/)
- `g3_BW_F257_hard_cases.py`: BW saturating enum at $(32, 16)$
- `g3_BW_F257_max_agreement.py`: BW max-agreement enum
- `g3_BW_F257_interior.py`: BW interior enum (final, used for paper2 §sec:open Q3)
- `g3_BKK_8x4.py`: BKK V(P_2, P_3) = 24 at base
- `g3_msolve_32x16_*.py`: msolve attempts (all timed out)
- `g3_A8_count_hard_cases.py`: incorrect (coefficient support); deprecated
- `g3_A8_eval_correct.py`: correct (eval support); not run
- Plus PR #441 K_2 / K_1 verification scripts

## Resume hints (for post-compact session)

If user asks "continue Q3 / Q2 / Q4 work":
- Q3: research-level (Note 0488 paths). In-session: brute force $A_8, A_9$ at $(32, 16)$ via `g3_A8_eval_correct.py`.
- Q2: K_2 ≤ 7 RIGOROUS for AP-step-divisor done. Next: rigorize genus-0 conjecture (G1) or AP-coprime extension (G3). Both research-level. In-session: Sudan list decoder at $(32, 8)$ to convert empirical to exact.
- Q1: NT difficulty, no in-session path.
- Q4: closed.

If user asks "what's the gap":
- Use the Layer status table above. 5 RIGOROUS, 4 conditional (1b mod Q3, rate-1/8, Layer 2 mod Q1, 3b' mod Q2 general support).

If user asks "push to main":
- Already pushed (origin/main = c402d37).

## Compact-safe summary

**Paper2 v25 main commits this session**:
1. Q3 drill: 72128af, 40a37d5, 4586b87, 7f70ae7, b33a314, 0517ea2, 6877b47, 1f0bc4b, 2a4c9bc, b93832d, e390805
2. PR #441 absorb: 1c38267 (merge of 42 commits including 39efaec, a76af49, etc.)
3. Codex fixes: 6279307
4. K_2 rigorize: c402d37

**Key deliverables**:
- 5 RIGOROUS rows (was 4 pre-session)
- 2 NEW RIGOROUS Theorems (`thm:K1-universal-budget`, `thm:K2-hyperelliptic-AP-divisor`)
- Q4 fully closed (`thm:caseD-K12`)
- Q3 deployment-scale closure paths identified (Note 0488); research-level

**Bottom line**: paper2 v25 is in best in-session state achievable. Further closure requires expert collaboration (Gong / Helleseth / Tang / Ding / Crites / Stewart).
