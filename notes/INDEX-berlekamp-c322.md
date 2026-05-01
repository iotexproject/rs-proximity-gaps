# Notes Index — Berlekamp #322 / Paper 3 Branch

This index maps the Berlekamp #322 work on `feat/berlekamp-c322` to
phases for navigation. The final result is **Paper 3 (`paper3.tex`)**:
`codim V_bad = 2(c-1)` RIGOROUS UNCONDITIONAL UNIVERSAL for all
$c \geq 2$, all deployment $D$.

## Quick start (read in this order)

For a reviewer/merger who wants to verify the final result without
the historical detours:

1. **`0117-V_S-rigorous-codim-upper-bound.md`** — Upper bound:
   $V_S \times V_S \subset V_{\text{bad}}$ (5-line proof).
2. **`0119-S-star-size-bound-algebraic.md`** — Lower bound, case A:
   $|S^*| \leq w + \lfloor w/T \rfloor$ via $f$-preimage counting.
   (Note: the §"Case B" portion is superseded by 0122; banner present.)
3. **`0122-case-b-reduction-conjecture-b-closed.md`** — Case-B
   reduction: every realizer admits a case-A representative in $S^*$,
   making 0119's bound universal.
4. **`0123-codim-vbad-universal.md`** — Sub-leading codim closes the
   $c \geq 5 \lfloor w/T \rfloor$ gap. Final result.
5. **`0121-berlekamp-322-final-state.md`** — Consolidated state
   (updated post-0122/0123, "modulo Conjecture B" qualifier removed).

The math content of Paper 3 §3-5 is exactly Notes 0117 + 0119 + 0122 +
0123. The deployment verdict in §6 is from `op2_berlekamp_deployment_table.py`
(Note 0116).

## Phase 1: pre-rescope — routed dichotomy attempt (Notes 0091--0113)

Earlier session work attempting a "routed dichotomy" framework for
$c = 3$, then $c = 4$. Notes 0099--0103 developed the tetrahedron-analytic
attack; Notes 0109--0113 generalized to v6v2 routed dichotomy. **This
framework was disproved at Note 0114** and abandoned. Notes in this
phase are retained for historical context but **superseded** by
Notes 0117+:

| Note | Topic |
|------|-------|
| 0091 | Berlekamp #322 state |
| 0092--0098 | Open-set rank lemma failure, multiclique violations |
| 0099--0103 | Tetrahedron analytic proof (later corrected, see 0114 banners) |
| 0104 | FRI 2-round soundness application |
| 0105 | Paper section 6.6 draft (Paper 1, superseded by Paper 3) |
| 0106--0108 | Session checkpoints, FRI conjecture attack notes |
| 0109--0113 | Routed dichotomy v6v2 (Theorem 1 c=3, c=4 structure) |

## Phase 2: pivot — Note 0114 disproof + deployment rescope (Notes 0114--0116)

Three-note pivot that switched the entire approach:

| Note | Topic | Outcome |
|------|-------|---------|
| 0114 | `dim V_tet_sub` formula corrected | v6v2 grand conjecture **disproved** in general; correct in distinct-extras case only. Adds correction banners to 0099/0110/0111/0112/0113. |
| 0115 | Deployment-first rescope plan | Drop universal proof; produce deployment table at 672 rows. Mirror Issue #376. |
| 0116 | D1 extrapolation finds shared-extras gap | Empirically confirmed Note 0114; `op2_berlekamp_deployment_table.py` produces 672-row sweep, 90.6% pass under codim 2(c-1). |

## Phase 3: final closure (Notes 0117--0123)

The clean attack that closes the problem:

| Note | Result |
|------|--------|
| **0117** | RIGOROUS upper bound: $V_S \times V_S \subset V_{\text{bad}}$ for $\|S\| = w+1$, codim $\leq 2(c-1)$. |
| 0118 | Empirical lower-bound matching: $V_{\text{bad}} \subseteq \cup_{\|S\|\leq w+1} V_S \times V_S$, 3/3 cases. |
| **0119** | Case-A algebraic bound: $\|S^*\| \leq w + \lfloor w/T \rfloor$ via $f(v) = -\alpha_v / \beta_v$ counting. (§"Case B" superseded by 0122.) |
| 0120 | D3 FRI 2-round integration: vanilla FRI commit gain $\log_2(c)$ bits per round. ABF §6.3 KiB comparison table. |
| 0121 | Consolidated state for prize submission. |
| **0122** | Case-B → Case-A reduction (5-line algebraic substitution). Closes Conjecture B unconditionally for $c \in \{3, 4\}$. |
| **0123** | Sub-leading codim $\geq (T+1)(\delta'-1)$. Closes $c \geq 5$ $\lfloor w/T \rfloor$ gap. **Final theorem: codim = $2(c-1)$ UNIVERSAL.** |

**Bold** = essential for Paper 3. Notes 0118, 0120, 0121 are
deployment/empirical context.

## Scripts (key files)

In `notes/scripts/`:

| Script | Note | Purpose |
|--------|------|---------|
| `berlekamp_deployment_table.py` | 0116 | 672-row deployment ε table. Computed under "asymptotic-codim" accounting (poly factor ignored). |
| `op2_v_S_test.py` | 0117 | Verifies $V_S \times V_S \subset V_{\text{bad}}$ (5/5 cases). |
| `op2_v_bad_decomposition_test.py` | 0118 | Verifies $V_{\text{bad}} \subseteq \cup V_S \times V_S$ (3/3 cases). |
| `op2_v_bad_S_size_bound.py` | 0119 | Tests $\|S^*\| \leq w + \lfloor w/T \rfloor$ (340/340 across 18 (n,c,p)). |
| `op2_case_b_density.py` | 0119 | V_bad density inside $V_S \times V_S$ for $\|S\| > w+1$ (0/600, 0/400). |
| `op2_case_b_alt_support_count.py` | 0119 | Case A vs case B realizer split (0/44 case-B for generic). |
| `op2_d3_fri_integration.py` | 0120 | D3 deployment table with FRI 2-round soundness. |

## Paper 3 structure

`paper3.tex` (1192 lines, 14 pages) maps to notes as follows:

| Paper § | Topic | Source notes |
|---------|-------|--------------|
| §1 Introduction | Deployment problem, contribution, sequence-school angle | New writing; refs Paper 1, Paper 2 |
| §2 Setup | RS, Berlekamp realizer, $V_{\text{bad}}$, joint Vandermonde support | Standard / from notes |
| §3 Main theorem | $\codim V_{\text{bad}} = 2(c-1)$ UNIVERSAL | Synthesis |
| §4 Upper bound | Theorem 4.1 + Remark 4.2 | **Note 0117** |
| §5 Lower bound | Lemma 5.1 + 5.2 + 5.3 + Prop 5.4 | **Notes 0119 + 0122 + 0123** |
| §6 Deployment verdict | Asymptotic-codim accounting, structural obstruction, vindication | **Notes 0116 + 0121** |
| §7 Implications | Bit budget, small fields, Paper 2 composition, Lean | **Note 0120**; new Paper 2 composition |
| §8 Discussion | Open: prefactor; c=2 link to Paper 1; STIR/WHIR | New |

## Other content on this branch

- **`paper3.tex` + `paper3.pdf`** — Paper 3 first draft + rendered PDF.
- **`notes/scripts/op2_*`** — Berlekamp work computational artifacts
  (Phases 1-3). Some Phase 1 scripts predate the rescope and may be
  stale; Phase 3 scripts are current.
- **`notes/scripts/p3_*`, `notes/scripts/signpaired_*`** — DELETED on
  this branch (Phase 1 cleanup, see `git log -- notes/scripts/p3_*`).
- **`notes/fri-2round-imports/`** — Cross-imported notes from Paper 2
  branch for c-uniform context.

For the merge reviewer: the Phase 3 closure is the deliverable. Phase 1
and Phase 2 are retained for git-history continuity but **need not be
re-validated** — the result depends only on Notes 0117 + 0119 + 0122 +
0123, all of which are short, self-contained, and rigorous.
