# Reed--Solomon Proximity Gaps — Companion Repository

Lean 4 formalization, Python verification scripts, and manuscript PDFs for
two papers by Raullen Chai and Xinxin Fan (IoTeX Network):

> **Paper 1 — FRI Soundness Above the Johnson Bound via Threshold Halving.**
> Cryptology ePrint Archive, Paper [2026/861](https://eprint.iacr.org/2026/861.pdf), 2026.
> PDF in [`paper1/`](paper1/).
>
> **Paper 2 — Action-Orbit FRI Soundness above Johnson:
> Universal $K$-Bounds at Ethereum-Deployed Reed--Solomon Parameters.**
> Cryptology ePrint Archive, Paper [2026/858](https://eprint.iacr.org/2026/858.pdf), 2026.
> PDF in [`paper2/`](paper2/).

The papers attack the open intermediate zone (Johnson radius $< \delta < $
list-decoding capacity) of the Reed--Solomon proximity-gap problem — the
deployment regime of every FRI-based STARK on Ethereum's roadmap.

[![CI](https://github.com/iotexproject/rs-proximity-gaps/actions/workflows/ci.yml/badge.svg)](https://github.com/iotexproject/rs-proximity-gaps/actions/workflows/ci.yml)

---

## Repository Layout

```
rs-proximity-gaps/
  paper1/paper.pdf        Paper 1 manuscript (PDF)
  paper2/paper.pdf        Paper 2 manuscript (PDF)
  lean/                   Lean 4 + Mathlib formalization (Paper 1 core)
  scripts/                Python verification scripts (Paper 1 + Paper 2 spot checks)
  outputs/                Saved script outputs
  REPRODUCING.md          Reproduction commands
  PROOF_CHAIN.md          Step-by-step trace of Paper 1's main theorem
  LICENSE                 Apache 2.0
```

---

## Lean 4 Formalization (Paper 1)

The `FRISoundness` namespace machine-checks the combinatorial core of
Paper 1: half-threshold CA, equal-threshold CA, FRI even/odd coupling,
batch CA, generalized (any-characteristic) coupling, and the rational
counting / PMF transcript bound. Built against Mathlib v4.30.0-rc2,
**zero `sorry`** in the namespace, with **one external axiom**:
`bciks_proximity_gap` (BCIKS, FOCS 2020, Theorem 1.2).

```bash
cd lean
lake exe cache get   # download Mathlib cache (~5 min)
lake build           # builds FRISoundness
```

The CI workflow runs `lake build` on every push and verifies the no-`sorry`
property.

---

## Python Verification Scripts

Stdlib-only Python scripts under `scripts/`:

| Subdir | Verifies |
|---|---|
| `ca-bound/` | Half- and equal-threshold CA |
| `fri-coupling/` | FRI even/odd coupling and proximity gap |
| `op1-barrier/` | Equal-threshold CA equals $\binom{n}{w}/|F|$ |
| `op2-obstruction/` | $M_{\max} \geq 2$ at FRI parameters |
| `list-size/` | List-size moments and pairwise / $k$-wise independence |
| `cs-construction/` | Crites--Stewart construction sweep |
| `char2-circle/` | Characteristic-2 / circle-FRI extensions |
| `paper2-deployment-l3/` | Paper 2 deployment-scale L3 spot checks |
| `archive/` | Earlier exploratory scripts |

Per-script docstrings document what each script computes. Methodology
limitations of audit-style scripts are consolidated in
[`scripts/SCRIPT_CAVEATS.md`](scripts/SCRIPT_CAVEATS.md).

Run any individual script:

```bash
python3 scripts/<subdir>/<script>.py
```

Saved outputs (where pre-computed) live under `outputs/`, mirroring
the `scripts/` layout.

---

## Citation

```bibtex
@misc{ChaiFan2026FRI,
  author = {Chai, Raullen and Fan, Xinxin},
  title  = {{FRI} Soundness Above the {J}ohnson Bound via Threshold Halving},
  year   = {2026},
  howpublished = {Cryptology ePrint Archive, Paper 2026/861},
  url    = {https://eprint.iacr.org/2026/861},
  note   = {Companion repository: \url{https://github.com/iotexproject/rs-proximity-gaps}}
}

@misc{ChaiFan2026ActionOrbit,
  author = {Chai, Raullen and Fan, Xinxin},
  title  = {Action-Orbit {FRI} Soundness above {J}ohnson:
            Universal $K$-Bounds at Ethereum-Deployed {R}eed--{S}olomon Parameters},
  year   = {2026},
  howpublished = {Cryptology ePrint Archive, Paper 2026/858},
  url    = {https://eprint.iacr.org/2026/858},
  note   = {Companion repository: \url{https://github.com/iotexproject/rs-proximity-gaps}}
}
```

---

## License

[Apache License 2.0](LICENSE).

---

## Use of AI assistants

Both manuscripts and this companion repository were prepared with
Claude (Anthropic, Opus 4.7, 1M-context) as a research assistant —
proof drafting, code generation for empirical verification, and prose
review. All theorem statements, proofs, and structural framing are
the authors'; AI-generated content was independently checked by hand
or by reproducible computation before being kept.
