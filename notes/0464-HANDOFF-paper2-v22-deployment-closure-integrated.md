# Note 0464 -- HANDOFF after paper2 v22 deployment-closure integration

**Date:** 2026-05-03 late evening (before user-requested compact)
**Branch:** `main`
**Latest commit:** `96a03e9` (v22 review-pass updates), all pushed to origin.
**Working tree:** CLEAN.

This note is the AUTHORITATIVE handoff state. Read this FIRST when continuing.

---

## 1.  Where we are (one sentence)

paper2 v22 is **integrated and pushed**: the L3 deployment-scale local closure
work (Notes 0460-0463) has been added to `paper2.tex` as a new subsection
§ssec:deployment-local-closure plus 7 cross-reference updates (abstract,
§1.4 Contributions, §1.4 Three-layer status, §1.5 Organization, Figure 1
box + caption, §sec:sparse-worst intro, §rem:sparse-worst-empirical
"Deployment-scale upgrade" paragraph, Q2 paragraph in §sec:open).

---

## 2.  Today's complete note chain (READ IN THIS ORDER)

**Morning + early afternoon (per Note 0456 handoff)**: Notes 0438-0455
already integrated. See Note 0456 for that handoff.

**Post-compact iterations (this session, post Note 0456)**:

1. **0457** — Option A: paper2 scope analysis. paper2's `thm:no-full-base-closure`
   is at base $L_2 = (16, 4)$ for 3-support pencils ONLY; my K=16 deployment
   cases are out of scope. Note 0455's "K=16 refutes K≤10" claim corrected.

2. **0458** — Canonical lift check. Verified $f^{(0)}(w) = f(w^4)$ has
   $\geq n_0/2$ zeros at $L_0$ (4-to-1 lift counting). My initial §3
   "boundary-only" claim was empirically refuted (cases have 72-80 zeros, not
   exactly 64); revised note documents the actual structure.

3. **0459** — RESOLVED via direct K-count. 4/5 K=16 cases at exact joint
   distance boundary (excluded by paper2 admissibility (ii)); 1/5 admissible
   with $K_{\text{lb}} = 1$ via 0 codeword.

4. **0460** — UNIFIED L3 Theorem (Boundary-Lift Closure):
   $|\mathrm{Zeros}_{L_0}(f^{(0)})| \geq n_0/2 = \sqrt{n_0 k_0}$.
   1-line counting proof, scale-uniform. Verified empirically across 38 cases.

5. **0461** — Common-Zero Stratification: cross-side kernels split into
   (A) $|T| \geq n_2/2$ excluded by paper2 (ii) STRUCTURAL,
   (B) $|T| < n_2/2$ ratio-function $K_{\text{lb}} \leq 6$ STRUCTURAL,
   (C) $Z(f_u) \neq Z(f_v)$ joint-boundary STRUCTURAL.

6. **0462** — Empirical K-count survey: 43 cases initial sweep, K_BW $\leq 2$.
   Strata (A)/(C) structurally excluded; (B) structurally bounded + empirical.

7. **0463** — FINAL multi-prime confirmation: 72 K=16 stratum (B) cases at
   4 primes {257, 641, 769, 1153}, K_BW $\leq 2$ universally.

8. **0464** — THIS NOTE (handoff post-paper2-v22-integration).

---

## 3.  paper2.tex v22 changes (committed, pushed)

| Commit | Content |
|---|---|
| `877458d` | New §ssec:deployment-local-closure (165 lines): Theorem boundary-lift-closure (1-line proof), Theorem common-zero-stratification (case analysis), empirical paragraph, status remark |
| `f190d83` | Updates to abstract, §1.4 Contributions item (4), §1.5 Organization, §rem:sparse-worst-empirical "Deployment-scale upgrade" paragraph |
| `96a03e9` | Review-pass: §1.4 Three-layer Layer 3 bullet, Figure 1 box + caption updated to mention new theorems |

**paper2.tex stats**: 3452 lines (was 3255 in v21, +197 = +6%).

**Two new theorems** (with labels):
- `thm:boundary-lift-closure` (line 2541)
- `thm:common-zero-stratification` (line 2585)

**No deletions**: all v21 theorems remain valid (different scope: base panel for v21, deployment for v22).

---

## 4.  Verification status (PDF NOT compiled — see §5)

**Self-review pass complete:**
- All envs balanced (theorem/remark/proof/abstract/enumerate/itemize/minipage/figure all = 0)
- All 4 new labels defined exactly once
- All cross-references resolve (8+ \ref locations across abstract, contributions, organization, figure, body sections)
- Logical flow consistent across abstract → contributions → §1.4 status → §1.5 organization → §sec:sparse-worst body

**Cannot compile PDF locally**: pdflatex not installed on the laptop (verified
via `find / -name pdflatex`). User needs to rebuild on the studio:
```
cd /Users/raullenstudio/work/EF1M
pdflatex paper2 && bibtex paper2 && pdflatex paper2 && pdflatex paper2
```

---

## 5.  Critical context: ~95% structural + 5% empirical

The honest L3 status is:

* **Boundary-Lift Theorem (Note 0460)**: RIGOROUS, scale-uniform, q-uniform.
* **Common-Zero Stratification (Note 0461)**:
  - Strata (A), (C): RIGOROUSLY excluded via paper2 admissibility (ii).
  - Stratum (B): $K_{\text{lb}} \leq 6$ STRUCTURAL via ratio-function bound.
* **Stratum (B) total-K**: structurally bounded $K_{\text{lb}} \leq 6$ +
  empirically $K_{\text{BW}} \leq 2$ across 72 cases at 4 primes.

**The 5% structural gap**: total-K bound for stratum (B) including
list-decoding contributions in agreement range $[\sqrt{n_0 k_0}, n_0 - t_{\mathrm{BW}}) = [64, 80)$.
To close: implement Guruswami-Sudan list-decoder for RS(128, 32) at Johnson
radius (~1-2 days focused work) OR find new theoretical insight for K-monomial
pencil bound (~2-4 weeks, possibly with Helleseth/Gong collaboration).

---

## 6.  Failed angles for 100% structural (don't repeat)

Attempted and shown not to close the gap:
- **Action-orbit (i)**: 0/10 K=16 cases action-stabilized → admissibility (i) doesn't exclude.
- **Bezout degree bound**: too loose ($\leq 124$, need $\leq 64$).
- **Donoho-Stark uncertainty**: weak for $n_0 = 128$ (not prime).
- **Mod-4 pigeonhole**: doesn't apply (K=16 hits all 4 classes).
- **Per-p ratio function**: doesn't aggregate to total-K bound.
- **Direct paper2 K10 generalization**: Gröbner enumeration cost grows
  exponentially in K (Note 0286 for K=2 enumerates 12 base cases at (4,1)/(8,2);
  K=16 base case enumeration infeasible).
- **Sudan D_y=1 implementation**: my code only reaches agreement $\geq 80$
  (= unique decoding region), NOT Johnson radius 64. Need GS multiplicity $m \geq 2$
  for proper Johnson-radius decoding.

---

## 7.  Strategic position for paper2 v22 submission

**Headline numbers preserved from v21**:
- 80KB proof at 128-bit security (vs SOTA 160KB)
- $K \leq 10$ rigorous for 3-pos-sparse $\hat f$ at every deployment scale

**v22 new contributions** (substantial advance over v21):
- Boundary-Lift Closure Theorem (NEW, 1-line proof)
- Common-Zero Stratification Theorem (NEW, case analysis)
- Multi-prime empirical confirmation (72 K=16 cases at 4 primes)

**Q2 status updated**: deployment-scale local closure narrows the path to
unconditional K ≤ 10. Open: (i) GLOBAL Q2 attachment, (ii) tight stratum (B)
total-K via list-decoding.

---

## 8.  Recommended next steps (in order of payoff)

### Option A (1 day): User compiles PDF, reviews v22 typesetting.
Verify the new content displays correctly, especially:
- Figure 1 Layer 3 box (added 2 theorem refs, may need width adjustment)
- §ssec:deployment-local-closure flow with surrounding remarks
- Abstract paragraph length (added ~5 lines)

### Option B (1-2 days): Implement Guruswami-Sudan list-decoder.
Bring 5% empirical → "verified at full Johnson radius" via proper GS algorithm
at $L_0 = (128, 32)$. Still empirical in nature but much more thorough.
Files to create: `notes/scripts/issue419_GS_multiplicity_2.py`.

### Option C (collaboration, 1-3 months): Pull Gong / Helleseth.
Per the user's stated mobilization plan ("once we have a real lead, pull in
Gong + Helleseth"), the K-monomial structural bound is exactly the kind of
problem where sequence-school cross-correlation tools could give insight.

### Option D (alternative): Switch focus.
- Q1 (named NT problem) — still open, deepest mathematical question.
- L1+L2 work (Tier 1c |A|∈{0,2}, Tier 2 side-(3,1)/(1,3)) per Note 0456.
- Paper 3 follow-up work.

---

## 9.  Repo state (verified)

- Branch: `main`
- Latest commit: `96a03e9` "paper2 v22: review-pass updates"
- Pushed: yes (`origin/main` up to date)
- Working tree: CLEAN (verified `git status`)
- All notes 0457-0464 + scripts pushed
- All paper2.tex changes pushed

---

## 10.  Files index for v22 work

**Notes** (all in `notes/`):
- `0457-Option-A-paper2-scope-resolves-K16-residual.md`
- `0458-K16-residual-is-Johnson-boundary.md`
- `0459-K16-residual-RESOLVED-via-K-count.md`
- `0460-UNIFIED-L3-Theorem.md`
- `0461-Common-Zero-Stratification-structurally-closes-admissible.md`
- `0462-FINAL-L3-status-after-empirical-K-survey.md`
- `0463-FINAL-multi-prime-empirical-confirmation.md`
- `0464-HANDOFF-paper2-v22-deployment-closure-integrated.md` (THIS)

**Scripts** (all in `notes/scripts/`):
- `issue419_K16_canonical_lift.py` — canonical lift verification
- `issue419_K16_K_count.py` — K-count via 0 codeword
- `issue419_decouple_check.py` — Z(f_u) = Z(f_v) check
- `issue419_boundary_lift_universal.py` — Theorem 0460 multi-K verification
- `issue419_boundary_lift_L64.py` — scale-uniform at L_2=(64,16)
- `issue419_case3_BW_total_K.py` — Berlekamp-Welch decoder
- `issue419_stratum_B_empirical_K.py` — stratum (B) empirical sweep (initial)
- `issue419_large_K_sweep.py` — multi-prime sweep (4 primes)
- `issue419_action_orbit_check.py` — action-orbit stabilization check (0/10)
- `issue419_sudan_list_decode.py` — WIP Sudan implementation (D_y=1, buggy)

**paper2.tex changes**: 3 commits (`877458d`, `f190d83`, `96a03e9`).

---

## 11.  My recommendation for next session

1. **First**: User compiles paper2.pdf, verifies v22 typesetting OK.
2. **If typesetting issues**: fix specific problems (most likely Figure 1 box width).
3. **Then either**:
   - **(B)** GS list-decoder implementation if pushing toward 100% structural.
   - **(D)** Switch to L1/L2 work or Q1 if v22 is deemed sufficient for paper2 prize submission.

The v22 paper as committed is **submission-ready** in content; only PDF
compilation + visual proofreading needed.

The L3 deployment closure (95% structural + 72/72 empirical) is honest and
substantial. paper2 v22 with this addition is a genuine step beyond v21.
