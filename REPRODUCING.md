# Reproducing the Paper Artifacts

Lightweight reproduction commands for **Paper 1** (manuscript PDF in
`paper1/paper.pdf`, ePrint [2026/861](https://eprint.iacr.org/2026/861.pdf)).
Run from the repository root.

## Environment

- Python 3.10+ (standard library only) for `scripts/`
- Lean 4 / Lake for `lean/`

## Manuscripts

Pre-rendered PDFs only — LaTeX sources are not included in this repository.

```text
paper1/paper.pdf   Paper 1 — FRI Soundness Above the Johnson Bound
paper2/paper.pdf   Paper 2 — Action-Orbit FRI Soundness above Johnson
```

Authoritative versions:
- Paper 1: <https://eprint.iacr.org/2026/861>
- Paper 2: <https://eprint.iacr.org/2026/858>

## Deployment Parameter Tables

```bash
python3 scripts/deployment_params.py
python3 scripts/deployment_params.py --latex
python3 scripts/deployment_params.py --per-round-max
```

Implements the bound `eps <= nR/|F| + (1 - delta/2)^q` (interactive) and
the BCS / Fiat-Shamir compilation `eps <= Q * eps_int + 3(Q^2 + 1)/2^kappa`.
Defaults: `n=2^20`, `R=20`, `delta=0.4`, `q=128`, `Q=2^64`, `kappa=256`.

## Proximity-Gap Figure

```bash
python3 scripts/proximity_gap_diagram.py
```

Outputs `proximity_gap_diagram.{png,pdf}` next to the script.

## Lean Formalization

```bash
cd lean
lake build
```

Builds the `FRISoundness` namespace. CI on every push enforces zero `sorry`
in the namespace; see `.github/workflows/ci.yml`.

## Verification scripts

Per-subdir docstrings document what each script computes; methodology
caveats are consolidated in `scripts/SCRIPT_CAVEATS.md`. To refresh a
saved output, redirect stdout, e.g.:

```bash
python3 scripts/op1-barrier/op1_scaling.py > outputs/op1-barrier/op1_scaling.output.txt
```
