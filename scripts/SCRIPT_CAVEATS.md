# Script Caveats

A second-pass audit (codex CLI, May 2026) flagged several scripts whose
docstrings or printed output overstated what the code actually computes.
The scripts themselves remain useful as **empirical spot checks** at small
parameters; the literal theorem statements they accompany are established
in the paper proofs, not in these scripts.  This file consolidates the
caveats so a public reader can calibrate.  Per-script docstrings were
also updated in-place to match.

## Distance-to-RS via planted codeword (upper bound, not nearest)

- `ca-bound/audit_critical_inequality.py` — sets `delta_f := err_weight/n`
  for a planted codeword `g + e`.  This is `Delta(f, g)`, an upper bound
  on `Delta(f, RS_k)`.  Verifying `delta_joint >= delta_f` implies the
  lemma's `delta_joint >= Delta(f, RS_k)` but does not exhibit the
  literal nearest-codeword witness.
- `ca-bound/audit_halved_threshold.py` — same proxy for `Delta(f, RS_k)`
  and an analogous proxy for the alpha-count (alphas with low Hamming
  weight against the folded planted codeword).

## Distance-to-RS via DFT truncation (upper bound, not nearest)

- `fri-coupling/audit_fri_coupling.py` — reports `Delta(f_even, RS_{k/2})`
  and `Delta(f_odd, RS_{k/2})` as the Hamming distance to the specific
  codewords `g_even` / `g_odd` obtained by Fourier truncation.  This is
  `Delta(., g_e)` for that specific `g_e`; it is an upper bound on the
  literal nearest-codeword distance.  At small parameters with sparse
  errors the two coincide, but a small brute-force counter-example
  exists already at `RS[4,2]/F_5`.

## Heuristic / partial coverage (not exhaustive)

- `fri-coupling/proximity_gap_derive.py` — `list_decoding_profile()`
  samples 200 codewords / 50 error patterns / 2000 centers; the
  hard-coded `M_data` line at the bottom is a sample lower bound on
  `M_max`, not an exhaustive search.  The `n=20` slot was previously a
  placeholder `0`; replaced with `'?'` to avoid implying coverage.
- `char2-circle/s3_char2.py` — caps `lam_range` at 100 elements; for
  `F_q` with `q > 100` (e.g. `F_{2^8}`, `F_{2^12}`, `F_{2^16}`) the
  reported `max_M` / `max_NOT` are sample maxima over the first 100
  lambdas, not the field-wide maximum.
- `paper2-deployment-l3/issue419_boundary_lift_universal.py` —
  hard-coded at `(p, n_2, k_2) = (257, 32, 8)`; samples 500 random
  configs and uses the first 50 per `K` parity.  Empirical spot check
  for `thm:boundary-lift-closure`; the universality (any no-full kernel)
  is established in the paper proof, not here.
- `paper2-deployment-l3/issue419_large_K_sweep.py` — currently focuses
  on `K=16` only; broader `K=12, 14, 16` coverage is split across
  `issue419_case3_BW_total_K.py` and `issue419_stratum_B_empirical_K.py`
  (see `paper2-deployment-l3/README.md`).

## What we are **not** caveating

- `ca-bound/ca_equal_threshold.py`, `ca-bound/ca_ratio_sweep.py`,
  `cs-construction/`, `list-size/`, `op1-barrier/`, `op2-obstruction/`,
  `archive/` — independently audited in the same pass and no
  comparable correctness flags were found.  See per-file docstrings
  for what each script computes.

## Source of these caveats

The May 2026 audit pass is reproducible: run `codex exec --sandbox
read-only` against the prompt logged at the top of this commit.
