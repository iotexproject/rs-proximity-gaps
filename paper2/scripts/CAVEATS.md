# Script Caveats — Paper 2

A second-pass audit (codex CLI, May 2026) flagged the following
deployment-scale L3 scripts as **empirical spot checks** rather than
universal verifications.  The literal theorem statements they
accompany are established in the paper proof; these scripts confirm
the bounds at fixed parameters.

- `deployment-l3/issue419_boundary_lift_universal.py` — hard-coded
  at `(p, n_2, k_2) = (257, 32, 8)`; samples 500 random configurations
  and uses the first 50 per `K` parity.  Empirical spot check for
  `thm:boundary-lift-closure`; the "ANY no-full kernel" universality
  is established in the paper proof, not in this script.
- `deployment-l3/issue419_large_K_sweep.py` — currently focuses on
  `K=16` only; broader `K=12, 14, 16` coverage is split across
  `issue419_case3_BW_total_K.py` and `issue419_stratum_B_empirical_K.py`
  (see `deployment-l3/README.md`).

Companion Paper 1 caveats:
[`../../paper1/scripts/CAVEATS.md`](../../paper1/scripts/CAVEATS.md).
