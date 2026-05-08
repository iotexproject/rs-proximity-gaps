# Computational Companion: Reed--Solomon Proximity Gaps Series

Lean 4 formalization, Python verification scripts, and research notes
accompanying three papers by Raullen Chai and Xinxin Fan (IoTeX Network):

> **Paper 1 — FRI Soundness Above the Johnson Bound via Threshold Halving.**
> Cryptology ePrint Archive, Paper [2026/861](https://eprint.iacr.org/2026/861.pdf), 2026.
> Manuscript in [`paper1/`](paper1/).
>
> **Paper 2 — Action-Orbit FRI Soundness above Johnson:
> Universal $K$-Bounds at Ethereum-Deployed Reed--Solomon Parameters.**
> Cryptology ePrint Archive, Paper [2026/858](https://eprint.iacr.org/2026/858.pdf), 2026.
> Manuscript in [`paper2/`](paper2/).
>
> **Paper 3 — Codim-$2(c{-}1)$ Reed--Solomon Proximity Bounds via the
> Berlekamp Realizer.**
> Cryptology ePrint Archive, 2026 (link to be added).

The three papers together attack the open intermediate zone
(Johnson radius $< \delta < $ list-decoding capacity) of the Reed--Solomon
proximity-gap problem, the deployment regime of every FRI-based STARK on
Ethereum's roadmap (SP1, RISC Zero, Plonky3, Stwo, the ~30 zkVMs on
EthProofs, the post-quantum signature aggregation layer).

This repository provides:

1. **Lean 4 formalization** of the core combinatorial bounds for Paper 1
   (`lean/`).  All named theorems in the `FRISoundness` namespace
   (≥ 18, including the half-threshold CA, equal-threshold CA, FRI
   coupling, RS isomorphism under the explicit `RSIsomorphismWitness`
   interface, batch CA, the PMF transcript model, and a
   characteristic-agnostic generalized coupling) are machine-checked
   with **zero `sorry`**.  Only one external result
   (`bciks_proximity_gap`, BCIKS FOCS 2020) remains as an axiom.
2. **Python verification scripts** for every numerical claim in
   Paper 1 (`scripts/`), with saved outputs in `outputs/`.
3. **Research notes** for Paper 2 and Paper 3 (`notes/`), including
   numbered notes 0001--0344 and the supporting Singular Gröbner /
   sweep / multiprime certificate scripts under `notes/scripts/`.
   Paper 2 and Paper 3 cross-reference these notes directly by
   number (e.g., `Note 0320`, `Note 0337`).

[![CI](https://github.com/iotexproject/rs-proximity-gaps/actions/workflows/ci.yml/badge.svg)](https://github.com/iotexproject/rs-proximity-gaps/actions/workflows/ci.yml)

---

## Repository Layout

```
rs-proximity-gaps/
  lean/                Lean 4 + Mathlib formalization (Paper 1)
    FRISoundness/
      Defs.lean              Agreement / error sets, linear comb     (fully proved)
      CA.lean                Theorem 5: half-threshold CA            (fully proved)
      EqualThresholdCA.lean  Theorem 7: equal-threshold CA bound     (fully proved)
      RSCode.lean            RS code, FRI pairing, RSIsomorphismWitness (fully proved)
      Coupling.lean          Theorem 14: proximity gap composition   (proved + 1 axiom)
      Probability.lean       Counting + PMF transcript model         (fully proved)
      BatchCA.lean           Batch CA for STIR/WHIR                  (fully proved)
      Char2.lean             Generalized coupling, all chars         (fully proved)
    lakefile.toml      Build (Mathlib v4.30.0-rc2)
    lean-toolchain     Lean 4 v4.30.0-rc2

  scripts/             Python verification scripts for Paper 1 (stdlib only)
    ca-bound/          Half- and equal-threshold CA
    list-size/         List-size moment / pairwise-independence / k-wise tests
    fri-coupling/      FRI even/odd coupling and proximity gap
    op1-barrier/       Equal-threshold CA = C(n,w)/|F|
    op2-obstruction/   M_max ≥ 2 at FRI parameters
    char2-circle/      Char-2 / circle-FRI extensions
    cs-construction/   Crites--Stewart construction sweep
    archive/           Earlier exploratory scripts (see archive/README.md)

  outputs/             Saved script outputs for Paper 1 (mirrors scripts/)
    archive/           Outputs of earlier exploratory phases

  notes/               Research notes for Paper 2 and Paper 3
    0001 – 0344        Numbered research notes (Markdown)
    scripts/           Singular Gröbner / sweep / multiprime certificate scripts
                       referenced by Paper 2 and Paper 3 by name

  REPRODUCING.md       One-shot reproduction instructions for Paper 1
  PROOF_CHAIN.md       Mechanization-ready proof skeleton for Paper 1
  .github/workflows/   CI (lake build + sample Python runs)
  LICENSE              Apache 2.0
```

---

## Paper 1 → Code Map

Every formal claim in Paper 1 that has a code witness is listed here.
**Lean** = machine-checked theorem name (`namespace.theorem`).
**Script** = Python verifier (under `scripts/`).
**Output** = saved output (under `outputs/`).

### Mainline (sections 3–5)

| Paper                               | Lean                                       | Script                                                | Output                                            |
|-------------------------------------|--------------------------------------------|--------------------------------------------------------|---------------------------------------------------|
| Theorem 5 (half-threshold CA)       | `FRISoundness.ca_halved`                   | `ca-bound/audit_halved_threshold.py`                  | (run script)                                      |
| Lemma fri-coupling                  | `FRISoundness.coupling_pointwise`,<br>`coupling_counting` | `fri-coupling/audit_fri_coupling.py`     | `fri-coupling/audit_fri_coupling.output.txt`      |
| Theorem 14 (proximity gap)          | `FRISoundness.proximity_gap`               | `fri-coupling/proximity_gap_derive.py`                | (run script)                                      |
| Theorem 18 (FRI soundness)          | (combinatorial: `proximity_gap` + axioms `bciks_proximity_gap`, `schwartz_zippel_fri`) | (composition; reproduced numerically by `fri-coupling/fri_folding.py`) | (run script) |

### Equal-threshold CA / OP1 (section 4)

| Paper                                           | Lean        | Script                                | Output                                          |
|-------------------------------------------------|-------------|---------------------------------------|-------------------------------------------------|
| Theorem 7  (equal-threshold CA upper bound)     | `FRISoundness.ca_equal_threshold` | `ca-bound/ca_equal_threshold.py`      | (run script)                                    |
| Proposition 9  (equal-threshold tightness)      | (paper proof) | `op1-barrier/op1_scaling.py`,<br>`op1-barrier/op1_scaling_n8.py` | `op1-barrier/op1_scaling.output.txt`,<br>`op1-barrier/op1_scaling_n8.output.txt` |
| Remark 12  (vacuous at FRI scale)               | (paper note) | `ca-bound/audit_vacuity_check.py`     | (run script)                                    |
| Crites–Stewart construction (cited as ref. 3)   | -           | `cs-construction/cs_sweep_fast.py`,<br>`op1-barrier/op1_cs_construction.py` | `cs-construction/cs_sweep_fast.output.txt`,<br>`op1-barrier/op1_cs_construction.output.txt` |
| OP1 sweep at large n                            | -           | `op1-barrier/op1_sweep_large_n.py`    | `op1-barrier/op1_sweep_large_n.output.txt`     |

### List-size landscape (section 6)

| Paper                                              | Lean | Script                                                   | Output                                       |
|----------------------------------------------------|------|----------------------------------------------------------|----------------------------------------------|
| Theorem second-moment  (E[M] = C(n,w)/p, Var[M])   | -    | `list-size/compute_exact_variance.py`                    | (run script)                                 |
| Corollary moments-c  (E[M] = C(n,w)/p^c)           | -    | `list-size/verify_E_Mtrue.py`                            | (run script)                                 |
| Theorem pairwise-c  (pairwise indep at c ≥ 2)      | -    | `list-size/verify_c2_pairwise_independence.py`,<br>`list-size/c2_moment_bound.py` | (run scripts) |
| k-wise indep refutation at c ≥ 2 (Note 0092)       | -    | `list-size/verify_kwise_independence.py`                 | (run script)                                 |
| M_true depends on p                                | -    | `list-size/verify_M_true_pdep.py`                        | (run script)                                 |
| M_max growth (intermediate zone)                   | -    | `list-size/M_errorpattern.py`,<br>`list-size/large_n_verify.py`,<br>`list-size/verify_true_M.py` | `list-size/M_errorpattern_output.txt`,<br>`list-size/large_n_verify.output.txt` |
| Proposition m2-obstruction  (M_max ≥ 2)            | -    | `op2-obstruction/op2_feasibility.py`                     | (run script)                                 |

### Batch CA / STIR / WHIR (appendix A)

| Paper                                       | Lean                                                     | Script | Output |
|---------------------------------------------|----------------------------------------------------------|--------|--------|
| Theorem batch-ca  (per-coordinate batch CA) | `FRISoundness.batch_ca_per_coord`,<br>`batch_ca_at_most_one`,<br>`batch_ca_per_coord_bad_card`,<br>`batch_ca_bad_count`,<br>`batch_ca_aggregate` | (no separate verifier) | -     |

### Characteristic 2 / Circle FRI (appendices B, C)

| Paper                                       | Lean                                            | Script                              | Output                              |
|---------------------------------------------|-------------------------------------------------|-------------------------------------|-------------------------------------|
| Generalized coupling (any characteristic)   | `FRISoundness.gen_coupling_pointwise`,<br>`gen_coupling_counting` | `char2-circle/s3_char2.py`          | `char2-circle/s3_char2.output.txt` |
| Theorem fri-char2  (FRI in char 2)          | (composition; via `gen_coupling_*` + `bciks_proximity_gap` axiom) | (covered by `s3_char2.py`)          | -                                   |
| Theorem fri-circle  (Stwo / Mersenne31)     | (paper proof; not in Lean)                      | -                                   | -                                   |

---

## Paper 2 / Paper 3 → Notes Map

Paper 2 and Paper 3 do not have a separate Lean formalization at this
revision; the verification artifacts are Singular Gröbner certificates,
multiprime sweep outputs, and the numbered research notes that document
their structural arguments.

Notes referenced directly by Paper 2 or Paper 3 (representative; see
each note's header for branch/date provenance):

- `notes/0286-K8-rigorous-deployment-2mono.md` — base-case 2-monomial
  bound for `thm:universal-K10` (Paper 2)
- `notes/0288-…`, `notes/0294-…`, `notes/0297-…` — Substitution
  Principle scale-uniform lift (Paper 2)
- `notes/0320-K_q-1-saturation-supp-n2.md` — `lem:q17-mu16-saturation`
  (Paper 2)
- `notes/0333-issue396-no-full-primitive-theorem.md` — local path-(c)
  no-full primitive theorem (Paper 2 Layer 3)
- `notes/0334-issue396-scale-lift-tail-lemma.md`,
  `notes/0337-issue396-scale-lift-tail-proof.md` — scale-lift to
  arbitrary `n = 4k` (Paper 2 `thm:dyadic-tail-scale-lift`)
- `notes/0340-issue396-defect-allocation-normal-form.md`,
  `notes/0344-issue419-l3-global-attachment-drill.md` — Layer 3
  defect-allocation reduction (Paper 2)
- `notes/scripts/issue396_no_full_4support_cert.q*.output.txt`,
  `notes/scripts/issue396_no_full_5support_cert.q*.output.txt` —
  multiprime no-full certificates supporting `rem:sparse-worst-empirical`
  (Paper 2)

The `notes/scripts/` directory contains the Python and Singular
verification scripts referenced by these notes.  Outputs are committed
alongside their scripts as `<script>.output.txt`.

---

## Lean 4 Formalization (Paper 1)

### Status summary

| Component                              | Status               | File              |
|----------------------------------------|----------------------|-------------------|
| `ca_halved`                            | **proved** (0 sorry) | `CA.lean`         |
| `coupling_pointwise`, `coupling_counting` | **proved** (0 sorry) | `RSCode.lean`     |
| `proximity_gap`                        | **proved** (chains `ca_halved`) | `Coupling.lean` |
| `bad_alpha_count`                      | **proved** (0 sorry) | `Coupling.lean`   |
| `batch_ca_*` (3 theorems)              | **proved** (0 sorry) | `BatchCA.lean`    |
| `gen_coupling_pointwise`, `gen_coupling_counting` | **proved** (0 sorry) | `Char2.lean`      |
| `ca_equal_threshold`                   | **proved** (0 sorry) | `EqualThresholdCA.lean` |

### Named theorems (descriptions)

| Theorem | Description | File |
|---------|-------------|------|
| `ca_halved` | Half-threshold CA: at most 1 bad γ | `CA.lean` |
| `ca_equal_threshold` | Equal-threshold CA: at most C(n,w) bad γ | `EqualThresholdCA.lean` |
| `coupling_pointwise`, `coupling_counting` | FRI fold preserves agreement; 2·\|jointAgree\| ≤ \|agree\| | `RSCode.lean` |
| `RSIsomorphismWitness` | Explicit algebraic interface for the concrete RS even/odd isomorphism | `RSCode.lean` |
| `rs_iso_forward` | RS even/odd decomposition theorem under `RSIsomorphismWitness` | `RSCode.lean` |
| `rs_iso_surj` | RS isomorphism surjectivity theorem under `RSIsomorphismWitness` | `RSCode.lean` |
| `proximity_gap` | Round-1 proximity gap, ≤ 1 bad α | `Coupling.lean` |
| `schwartz_zippel_fri` | Nonzero univariate polynomial has ≤ natDegree distinct roots (now proved) | `Coupling.lean` |
| `commit_phase_count_bound` | Commit bad-challenge numerator ≤ nR | `Probability.lean` |
| `query_phase_miss_count_bound` | Query-miss numerator ≤ (n−d)^q | `Probability.lean` |
| `fri_soundness_above_johnson_counting` | Counting skeleton for nR/\|F\| + (1−δ/2)^q | `Probability.lean` |
| `UniformTranscriptModel` | Finite PMF transcript-event model with uniform sampling | `Probability.lean` |
| `uniform_transcript_pmf_apply` | Point mass for the uniform transcript PMF | `Probability.lean` |
| `uniform_transcript_event_probability_bound` | PMF transcript event bound via finite rational counting | `Probability.lean` |
| `uniform_probability_bound` | Uniform finite probability monotonicity over rational quotients | `Probability.lean` |
| `fri_soundness_above_johnson_probability` | Rational-probability wrapper for the FRI counting skeleton | `Probability.lean` |
| `batch_ca_per_coord`, `batch_ca_aggregate` | Batch CA per coordinate + union-bound aggregate | `BatchCA.lean` |
| `gen_coupling_pointwise`, `gen_coupling_counting` | Generalized coupling, all characteristics | `Char2.lean` |

Zero `sorry` in the entire `FRISoundness` namespace.

### Remaining formalization gap

The combinatorial counting numerators, rational uniform-probability quotients,
and a finite PMF transcript-event model in `Probability.lean` compose with the
proximity-gap chain to give the paper's `nR/|F| + (1−δ/2)^q` bound at the
counting level. The remaining probability work is to instantiate the abstract
transcript event with the concrete interactive / non-interactive FRI
acceptance predicate.

The RS isomorphism statements are no longer global axioms — they are Lean
theorems under `RSIsomorphismWitness`, an explicit algebraic interface for the
concrete domain identities relating `α (fst y)`, `α (snd y)`, `sep y`, and
`α' y`. The remaining RS work is to instantiate that witness for the concrete
multiplicative FRI domain.

### Axioms (1, external)

| Axiom | Source / Justification | Defined in |
|-------|------------------------|------------|
| `bciks_proximity_gap` | BCIKS (FOCS 2020), Theorem 1.2 — external published result | `Coupling.lean` |

The earlier `schwartz_zippel_fri`, `rs_iso_forward`, and `rs_iso_surj` axioms
have all been **discharged** as proved theorems (the latter two parametrized
by `RSIsomorphismWitness`).

### Building

Requires [`elan`](https://github.com/leanprover/elan) (the Lean version
manager). The pinned toolchain is recorded in `lean/lean-toolchain`.

```bash
cd lean
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
lake update
lake exe cache get        # download Mathlib cache (~5 minutes; required to avoid recompiling Mathlib)
lake build                # build FRISoundness
```

The CI workflow (`.github/workflows/ci.yml`) runs `lake build` on every push
and verifies that no `sorry` appears in the `FRISoundness/` source.

---

## Python Verification Scripts

Pure Python 3 stdlib (no NumPy / SciPy / Sage / GPU requirements) for the
canonical Paper 1 scripts; one or two archived scripts use NumPy.  The
Paper 2 / Paper 3 scripts under `notes/scripts/` use `sympy` for finite
field arithmetic and shell out to `Singular` for Gröbner-basis vdim
computations where stated.

Run any Paper 1 script directly:

```bash
python3 scripts/op1-barrier/op1_scaling.py | tee outputs/op1-barrier/op1_scaling.output.txt
```

The CI workflow (`.github/workflows/ci.yml`) runs three smoke-test scripts
on every push as a sanity check; for the full reproduction set, see the
per-topic mapping in the **Paper 1 → Code Map** section above. Each saved
output in `outputs/<topic>/` corresponds to the same-named script in
`scripts/<topic>/` and can be regenerated by re-running it.

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

@misc{ChaiFan2026Codim,
  author = {Chai, Raullen and Fan, Xinxin},
  title  = {Codim-$2(c{-}1)$ {R}eed--{S}olomon Proximity Bounds via the Berlekamp Realizer},
  year   = {2026},
  howpublished = {Cryptology ePrint Archive, Paper 2026/XXXX},
  note   = {Companion repository: \url{https://github.com/iotexproject/rs-proximity-gaps}}
}
```

(Paper 3 ePrint number to be assigned.)

---

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
