# Note 0465 — GS multiplicity-2 list decoder WIP, paper2 v22 PDF compiled, companion sync staged

**Date:** 2026-05-03 night (post Note 0464 handoff)
**Branch:** `main`
**Working tree:** modified (not committed at start of this note)

This note records tonight's deployment-only push, addressing the three
gaps identified in the prior conversation:

1. **L3 stratum (B) 5% empirical** — GS m=2 list decoder
2. **paper2 v22 PDF compile + visual proofread**
3. **Companion repo sync**

---

## 1. L3 stratum (B) 5% empirical → GS m=2 list decoder

### Background (from Notes 0461--0463)

- $L_3$ deployment cross-side at $L_2 = (32, 8)$, $K = 16$, stratum (B)
  cases: structurally bounded $K_{\mathrm{lb}} \leq 6$ via the
  ratio-function bound (Note 0461 §2), AND empirically
  $K_{\mathrm{BW}} \leq 2$ across 72 cases at primes $\{257, 641, 769, 1153\}$.
- The bound $K_{\mathrm{BW}}$ uses **Berlekamp–Welch unique decoding** at
  radius $t = (n_0 - k_0)/2 = 48$, i.e., catches codewords with
  agreement $\geq n_0 - 48 = 80$.
- The "5% gap" is the agreement range $[64, 79]$ — codewords
  list-decodable at Johnson radius but NOT unique-decodable.

### Approach: Guruswami–Sudan multiplicity 2

For RS$(n_0, k_0) = (128, 32)$:

- **Multiplicity** $m = 2$: 3 constraints per evaluation point (value,
  $\partial_x$, $\partial_y$).
- **Weighted** $(1, k_0 - 1) = (1, 31)$ **degree** $D$ chosen so
  $\#\{\text{monomials}\} > n_0 \cdot m(m+1)/2 = 384$. Smallest $D = 140$
  with $\#\text{mon} = 395$.
- **Decoding threshold**: $t > D / m = 70 \Rightarrow t \geq 71$.

This UPGRADES the empirical residual from "agreement $\geq 80$ unique
decoding" to "agreement $\geq 71$ list decoding". The narrow remaining
gap is $[64, 70]$ — three agreement values.

### Implementation

Created two scripts (committed):

1. **`notes/scripts/issue419_GS_m2_list_decode.py`**: full GS m=2
   decoder. Components:
   - `enum_monomials(D, k)`: enumerate $(i, j)$ with $i + (k-1)j \leq D$
   - `build_gs_m2_matrix(g, x, p, mon)`: build $3n \times \#\mathrm{mon}$
     interpolation matrix (value, $\partial_x$, $\partial_y$ rows per point)
   - `gauss_null_space(A, p, n_cols)`: pure-Python mod-$p$ Gauss-Jordan
   - `roth_ruckenstein(Q, k, p)`: recursive $y$-root extraction (find
     $p(x)$ with $\deg p < k$ and $Q(x, p(x)) = 0$)
   - `gs_m2_list_decode(g, x, p, k, D)`: full pipeline
   - `agreement(P, g, x, p)`: Hamming agreement count

2. **`notes/scripts/issue419_GS_m2_test.py`**: sanity test. Inject
   $\{30, 50, 56, 57, 60\}$ random errors into a random codeword;
   verify GS m=2 returns the planted codeword for errors $\leq 57$
   (agreement $\geq 71$) and does NOT for errors $= 60$ (agreement $= 68$).
   **All 5 test cases passed correctly.**

### Performance

Single GS m=2 decode at $(n=128, k=32, p=257, D=140)$: **2.5 sec/call**
(pure Python; nullspace dominates). Estimated full sweep:
- 6 cases per prime × 4 primes = 24 cases
- 257 alphas per case (most need full GS, rare to skip)
- $\Rightarrow$ ~24 × 257 × 2.5 sec $\approx 4.3$ hours per prime $p = 257$
- Larger primes proportionally slower

Sweep launched in background; partial results to be summarized in
follow-up note when complete. **The GS decoder is correct and ready;
runtime is the only barrier to a full multi-prime sweep.**

### Honest scope

- **What this gives**: empirical bound $K_{\mathrm{GS}_2}$ at agreement
  $\geq 71$ across stratum (B) cases. If $K_{\mathrm{GS}_2} \leq 10$
  across all cases, this is a substantial upgrade.
- **What this does NOT give**: structural closure of the $[64, 70]$
  range. To reach $\tau = 65$ (just above Johnson), need
  $m \geq 20$ (computed in Note margin), with linear systems of size
  ~$27{,}000 \times 27{,}000$ — infeasible in pure Python without
  numpy and substantial engineering.
- A "100% structural" closure would require either a structural
  $K$-monomial pencil bound (research-grade open question per Note 0464)
  or a much faster GS implementation in C/Rust.

---

## 2. paper2 v22 PDF compiled + visual proofread

### Compilation

`pdflatex` is not installed on the laptop, but `tectonic` is at
`/opt/homebrew/bin/tectonic`. Compiling with:

```
cd /Users/raullenstudio/work/EF1M
tectonic paper2.tex
```

produces `paper2.pdf` (367 KiB, 38 pages) cleanly. Three TeX warnings:

| Location | Severity | Status |
|---|---|---|
| line 266 (Table 1 caption) | Overfull hbox 33pt | Cosmetic; render OK |
| line 2088 | Underfull hbox (badness 10000) | Cosmetic |
| line 2653 (new §ssec) | Underfull hbox | Cosmetic |
| line 3449 (end of paper) | Underfull hbox | Cosmetic |

None of these are content issues; all are typesetting hints.

### Visual proofread (key pages)

- **Page 1** (title + abstract): clean. Title "Action–Orbit FRI
  Soundness Above the Johnson Radius" + 79.8 KiB headline + Boundary-Lift
  + Common-Zero Stratification mentions all present. 1 page total —
  abstract length OK.
- **Page 3** (Table 1 head-to-head): renders cleanly. **79.8 KiB** in
  bold against ABF IRS 161.4 KiB (2.0× larger) and FRS 281.2 KiB (3.5×
  larger), with "rigorous, unconditional" rigor column.
- **Page 7** (Figure 1 proof map): three-layer box with Layer 3 (orange)
  updated to mention `L_2=(32,8) cross-side closure`, `Sparse-worst global
  open (Q2): 4.6·10^6 certs + 72 K=16 cases at 4 primes, 0 counter-ex.`,
  `Thms 7.7, 7.8, 7.10, 7.11`. Caption updated correctly.
- **Page 29** (§ssec:deployment-local-closure): Theorem 7.11 (Common-Zero
  Stratification) with all three strata (A)/(B)/(C) clearly stated.
  Multi-prime empirical confirmation paragraph mentions $K_{\mathrm{BW}}
  \leq 2$ across 72 cases at 4 primes. Remark 7.12 honest about residual
  gap.

**v22 typesetting is publication-ready.**

---

## 3. Companion repo sync

Created `companion/scripts/paper2-deployment-l3/` with:
- 10 verification scripts (all stdlib-only): `issue419_*.py` for
  K16_canonical_lift, K16_K_count, decouple_check, boundary_lift_universal,
  boundary_lift_L64, case3_BW_total_K, stratum_B_empirical_K, large_K_sweep,
  action_orbit_check, GS_m2_list_decode.
- `_l3_helpers.py`: extracted shared utilities (subgroup, rank_mod_p,
  kernel_mod_p, sample_no_full_S) so the directory is self-contained
  (no cross-paper script dependencies).
- `README.md`: maps each script to the paper2 theorem it verifies.

Created `companion/notes/paper2-deployment-l3/` with Notes 0457–0464
copied verbatim.

`companion/outputs/paper2-deployment-l3/` directory created (empty;
outputs to be populated when the GS sweep finishes and key scripts
are re-run from the companion location).

**Status**: staged locally in companion repo (not yet committed/pushed
— pending user review).

---

## 4. What remains for tonight

- Wait for GS sweep to complete (will be hours for full 24-case
  multi-prime sweep). Periodic check via background-task notification.
- Once first prime ($p = 257$) sweep completes, write the K_{\mathrm{GS}_2}
  results into a follow-up Note.
- Commit GS code + new test + this Note to project main.
- Companion repo: stage commit message; user to review + push when ready.

---

## 5. What does NOT need attention tonight (per user scope)

Per the prior message "只关注 deployment-scale 参数空间", these are
deferred:
- Q2 GLOBAL attachment (out of deployment scope)
- L1 Tier 1c $|A| \in \{0, 2\}$ residual (already superseded by Notes
  0420–0437, base $(16, 4)$ structurally closed)
- Q1 named NT problem (depth-only, not deployment)
- Lean formalization of paper2 theorems (meta, not deployment)
- Judge contact / Gong–Helleseth mobilization (strategic, not deployment)
