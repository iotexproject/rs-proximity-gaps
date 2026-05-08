# Reproducing the Paper Artifacts

Lightweight reproduction commands, organized per paper.  Run from the
repository root.

## Environment

- Python 3.10+ (standard library only) for `paper1/scripts/` and
  `paper2/scripts/`
- Lean 4 / Lake for `paper1/lean/`

## Manuscripts

Pre-rendered PDFs only — LaTeX sources are not included in this repository.

```text
paper1/paper.pdf   Paper 1 — FRI Soundness Above the Johnson Bound
paper2/paper.pdf   Paper 2 — Action-Orbit FRI Soundness above Johnson
```

Authoritative versions:
- Paper 1: <https://eprint.iacr.org/2026/861>
- Paper 2: <https://eprint.iacr.org/2026/858>

---

## Paper 1

### Lean formalization

```bash
cd paper1/lean
lake build
```

Builds the `FRISoundness` namespace.  CI on every push enforces zero
`sorry`; see `.github/workflows/ci.yml`.

### Deployment parameter table

```bash
python3 paper1/scripts/deployment_params.py
python3 paper1/scripts/deployment_params.py --latex
python3 paper1/scripts/deployment_params.py --per-round-max
```

Implements `eps <= nR/|F| + (1 - delta/2)^q` (interactive) and the BCS /
Fiat-Shamir compilation `eps <= Q * eps_int + 3(Q^2 + 1)/2^kappa`.
Defaults: `n=2^20`, `R=20`, `delta=0.4`, `q=128`, `Q=2^64`, `kappa=256`.

### Proximity-gap figure

```bash
python3 paper1/scripts/proximity_gap_diagram.py
```

Outputs `proximity_gap_diagram.{png,pdf}` next to the script.

### Verification scripts

Per-subdir docstrings document what each script computes; methodology
caveats are consolidated in `paper1/scripts/CAVEATS.md`.  Sample run:

```bash
python3 paper1/scripts/op1-barrier/op1_scaling.py
python3 paper1/scripts/ca-bound/audit_halved_threshold.py
```

To refresh a saved output, redirect stdout, e.g.:

```bash
python3 paper1/scripts/op1-barrier/op1_scaling.py \
  > paper1/outputs/op1-barrier/op1_scaling.output.txt
```

---

## Paper 2

### Deployment-scale L3 spot checks

```bash
python3 paper2/scripts/deployment-l3/issue419_action_orbit_check.py
python3 paper2/scripts/deployment-l3/issue419_K16_K_count.py
```

Caveats and what each script actually verifies are in
`paper2/scripts/CAVEATS.md` and `paper2/scripts/deployment-l3/README.md`.
