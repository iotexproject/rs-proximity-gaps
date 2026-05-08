# Note 0515 — paper2 v23 → v25 final deliverable summary for user

**Date:** 2026-05-05 (drill iter 43, post v25 PDF compile-verification)
**Status:** **paper2 v25 ship-ready**. All v24 + v25 patches committed, paper2.pdf compiles cleanly (52 pages, 470 KiB, 0 undefined refs).

## Branch state

- **27 commits ahead of upstream f76eb28** (paper2 v23 baseline at iter starting point)
- All commits on `main` branch local
- Not yet pushed to GitHub

## Headline contributions: paper2 v23 → v25

| Section | v23 status | v25 status | Driver |
|---|---|---|---|
| §7 Q2 GLOBAL | "K ≤ 10 fully conditional" | $K_1 \leq 3$ RIGOROUS + $K_2 \leq 7$ conjectured | NEW thm:K1-universal-budget (Note 0504) |
| §3.3 Q4 4-pos sparse | "open" | $K_4 \leq 13$ RIGOROUS at rate 1/4 | NEW thm:caseD-K12 (Notes 0294/0295/0297 sync) |
| §1.4 Layer status table | 6 rows | 8 rows (added 1a' for K_4, 3a' for K_1) | new theorems |
| §1.4 Contributions Layer 1 table | 3 columns (rate × K_2-mono × K_3-pos) | 4 columns (added K_4-pos) | new theorem |
| §sec:open Q4 | "open, natural Q4 task" | "CLOSED at rate 1/4; open at rate 1/2 / 1/8" | thm:caseD-K12 |
| §sec:open Q2 | "open conjecture" | "$K = K_1 + K_2$, $K_1$ rigorous, $K_2$ conjectured" | rem:K1-K2-decomposition |
| Remark line 1991 (4-pos extension) | "open at every rate" | "rate 1/4 closed, rates 1/2 / 1/8 open" | consistency |
| paper2.pdf | 32 pages, 417 KiB | 52 pages, 470 KiB | new theorems + remarks |

## Commits index (v23 → v25)

```
9438c37 STATE.md: paper2 v25 PDF compiles clean
4371d44 paper2 v25 fix: K_1 → $K_1$ math mode (compile error)
b9aab96 paper2 v25: §1.4 Contributions Layer 1 table — K_4-pos column
79b3308 paper2 v25 fix: remark line 1991 4-pos rate 1/4 CLOSED
eec8df8 paper2 v25 follow-up: Layer 1a' row added for 4-pos sparse
0dcb074 STATE.md: paper2 v25 Q4 CLOSED via thm:caseD-K12
c0954de paper2 v25: §3.3 Theorem caseD-K12 + §sec:open Q4 CLOSED  ← KEY commit (Q4)
... (Q2 drill iter 35-41 commits Notes 0511-0514)
e1a20df paper2 v24 LaTeX fix: relative joint distance notation
... (Q2 drill iter 31-34 commits Notes 0506-0510)
2ee9d35 paper2 v24: §7.5 K_1 ≤ 3 universal-budget theorem  ← KEY commit (Q2)
... (Q2 drill iter 28-30 commits Notes 0504-0505)
```

## Notes index (12 new notes 0504-0515)

- 0504: K_1 ≤ 3 universal budget (RIGOROUS THEOREM)
- 0505: K_2 attack via Helleseth + Gong subagent consults
- 0506: paper2 v24 update proposal
- 0507: Helleseth |D_α| ≥ 4 EMPIRICALLY REFUTED
- 0508: K_2 ≤ 7 verified at (16,4) brute force
- 0509: Gong resultant deg = 14 (not ≤ 7); rat.map.deg insight
- 0510: K_2 = 7 saturation found (margin tight at strict above-J)
- 0511: K_2 = q-1 correction (action-stab cases)
- 0512: Δ_joint(0) = 1.0 caution
- 0513: RESOLVED — saturating cases at Johnson boundary, excluded by strict above-J
- 0514: Q2 GLOBAL drill final synthesis
- 0515: This note (final user-facing summary)

## Open problems remaining in paper2 §sec:open

| Q# | Problem | Status |
|---|---|---|
| Q1 | $R_d$ non-vanishing on $V_d^{\mathrm{prim}}$, $d = 2^k$ | NT problem, settled $d = 4, 8$; user's domain |
| Q2 | Sparse-worst dominance: K_2 ≤ 7 | $K_1 \leq 3$ RIGOROUS NEW; $K_2 \leq 7$ conjectured w/ overwhelming empirical |
| Q3 | Rate-$1/2$ universal-$k$ Substitution Principle lift | User's domain |
| Q4 | $4$-pos sparse coverage | **CLOSED at rate 1/4 NEW**; rates 1/2 / 1/8 open |
| Q5 | Char-uniform Stage-2 closure at $h \geq 5$ | Reduces to Q1 essentially (single-endpoint at $h = 2^k$) |
| Q6 | Sign-paired upper bound at $k = 2^j$, $j \geq 3$ | Conjectural (2-primary tower) |
| Rate-1/8 lifts | various | Future work |
| Hasse-Weil bound for arbitrary primes | Q2-related | Future work |

## Recommended user actions

1. **Review paper2.pdf** — newly compiled, 52 pages. Visually verify the new content renders correctly:
   - §1.4 Contributions Layer 1 table (page ~6, with K_4-pos column)
   - §1.4 Layer status table (page ~6, with 1a' and 3a' rows)
   - §3.3 Theorem caseD-K12 (page ~30, after thm:caseC-K10)
   - §7.5 ssec:K1-universal-budget Theorem K1-universal-budget (page ~46)
   - §sec:open Q4 paragraph (page ~50, now CLOSED)
   - §sec:open Q2 paragraph (page ~50, with K_1+K_2 reduction)

2. **Decide on push/PR strategy**:
   - Option A: `git push origin main` — direct to upstream
   - Option B: create branch `paper2-v25-K1-K4-closures` + PR for codex review
   - Option C: keep local for further refinement

3. **Decide K_2 ≤ 7 attack priority**:
   - Open GitHub Issue #441 with full attack plan from Note 0505
   - Estimated 1-3 month timeline
   - Tag for sequence-school cluster (Tang/Ding) mobilization

4. **Optional enhancements**:
   - paper2 abstract could mention K_4 ≤ 13 + K_1 ≤ 3 as new contributions (currently only mentions 3-pos K ≤ 10 + Q2 + Q1)
   - paper2 §1.5 Organization could mention §3.3 Case D and §7.5 K_1 universal-budget

## Strategic Q2/Q4 progression

```
v23 baseline: Q2 fully open, Q4 fully open
  ↓
v24: Q2 K_1 ≤ 3 RIGOROUS in §7.5 (Notes 0504-0508 + 0513-0514)
  ↓
v25: Q4 K_4 ≤ 13 RIGOROUS in §3.3 (Notes 0294-0297 sync)
  ↓
[next] K_2 ≤ 7 structural proof — open structural (1-3 mo)
[next] Q5 reduces to Q1 (already framed)
[next] Q3 user's domain
```

## Bottom line

**Two paper2 open problems CLOSED back-to-back via systematic "已证 in notes 但 paper 没 sync" pattern**:
- Q2 K_1 component (NEW theorem from Note 0504)
- Q4 4-pos rate-1/4 (legacy theorem from Notes 0294/0295/0297, now incorporated)

paper2 v25 is the **largest substantive update since paper2 v22 deployment closure** (Note 0464, iter 26 Note 0502 conjA killed).

Ready for user disposition.
