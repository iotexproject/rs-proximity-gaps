# Computational Companion: FRI Soundness Above the Johnson Bound

This repository contains all computational verification scripts and formal proofs accompanying the paper:

> **FRI Soundness Above the Johnson Bound via Threshold Reduction**
> Raullen Chai, Xinxin Fan (IoTeX Network), 2026

## Repository Structure

```
rs-proximity-gaps/
  lean/                     Lean 4 + Mathlib formalization
    FRISoundness/
      Defs.lean             Core definitions (agree/error sets, linear combination)
      CA.lean               Theorem ca-halved: FULLY PROVED (0 sorry)
      RSCode.lean           RS code definition, FRI fold, coupling lemma
      Coupling.lean         Proximity gap, bad-alpha count
      Probability.lean      Counting wrapper for probability-level soundness
      BatchCA.lean          Batch CA for STIR/WHIR
      Char2.lean            Characteristic-2 generalization
    lakefile.toml           Build configuration (Mathlib dependency)
    lean-toolchain          Lean 4 v4.30.0-rc2

  scripts/
    ca-bound/               Correlated agreement bound verification
    list-size/              List-size landscape (moments, obstruction, pairwise independence)
    fri-coupling/           FRI folding and coupling lemma verification
    op1-barrier/            OP1: equal-threshold CA bound eps_ca = C(n,w)/|F|
    op2-obstruction/        OP2: M_max >= 2 at FRI parameters
    char2-circle/           Characteristic-2 and circle FRI extensions
    cs-construction/        Crites-Stewart construction sweep

  outputs/                  Saved script outputs for reproducibility
```

## Lean 4 Formalization

The core correlated agreement bound (Theorem 3.1 in the paper) is **fully machine-checked** in Lean 4 with Mathlib, with zero `sorry` statements. This is the first formal verification of any FRI soundness result.

### What is proved (0 sorry)

| Theorem | Description | File |
|---------|-------------|------|
| `ca_halved` | Half-threshold CA: at most 1 bad gamma | `CA.lean` |
| `coupling_pointwise` | FRI fold preserves agreement pointwise | `RSCode.lean` |
| `coupling_counting` | 2 * \|jointAgree\| <= \|agree\| | `RSCode.lean` |
| `commit_phase_count_bound` | Commit bad-challenge numerator <= nR | `Probability.lean` |
| `query_phase_miss_count_bound` | Query miss numerator <= (n-d)^q | `Probability.lean` |
| `fri_soundness_above_johnson_counting` | Counting skeleton for the nR/|F| + query term bound | `Probability.lean` |
| `batch_ca_per_coord` | Per-coordinate batch CA (for STIR/WHIR) | `BatchCA.lean` |
| `gen_coupling_pointwise` | Char-2 coupling (no NeZero(2:F) needed) | `Char2.lean` |

### Remaining formalization gap

The probability-level theorem is now represented by finite counting numerators
that build under Lean.  The remaining work is to package these counts in
Mathlib's probability monad and connect the abstract transcript acceptance event
to `fri_soundness_above_johnson_counting`.  The RS isomorphism axioms also need
an algebraic FRI-pairing interface relating `α (fst y)`, `α (snd y)`, and
`α' y`; the current abstract `FRIPairing` only stores the pairing and separation
factor, which is not enough to prove degree preservation.

### Axioms (4, all standard)

| Axiom | Source | Status |
|-------|--------|--------|
| `rs_iso_forward` | RS even/odd decomposition | Standard polynomial degree bound |
| `rs_iso_surj` | RS isomorphism surjectivity | Standard polynomial degree bound |
| `schwartz_zippel_fri` | Root count <= degree | In Mathlib (`Polynomial.card_roots_le_degree`) |
| `bciks_proximity_gap` | BCIKS Theorem 1.2 (FOCS 2020) | External published result |

### Building

```bash
cd lean
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y
lake update
lake exe cache get
lake build
```

## Python Verification Scripts

All scripts use Python 3 standard library only (no external dependencies). Each script is self-contained and can be run independently.

### Correlated Agreement Bound (`scripts/ca-bound/`)

| Script | Verifies |
|--------|----------|
| `ca_equal_threshold.py` | Equal-threshold CA bound eps_ca(C, delta, delta) |
| `ca_equal_fast.py` | Fast version of equal-threshold test |
| `audit_halved_threshold.py` | Halved-threshold proximity gap (Theorem 4.2) |
| `audit_critical_inequality.py` | Delta_joint >= Delta(f, RS_k) coupling inequality |
| `ca_ratio_sweep.py` | Sweep over CA threshold ratios |

### List-Size Landscape (`scripts/list-size/`)

| Script | Verifies |
|--------|----------|
| `verify_M_true_pdep.py` | p-dependence of M_true and Q-rank characterization |
| `verify_kwise_independence.py` | k-wise independence of error-locator normals |
| `verify_c2_pairwise_independence.py` | Pairwise independence at c >= 2 (Theorem pairwise-c) |
| `verify_E_Mtrue.py` | E[M_true] = C(n,w)(1-1/p)^w / p^c (Corollary moments-c) |
| `compute_exact_variance.py` | Exact second moment of Berlekamp count |
| `c2_moment_bound.py` | c >= 2 moment bound verification |
| `M_errorpattern.py` | Exact M via error-pattern enumeration |
| `large_n_verify.py` | Verification on power-of-2 domains (n=32,64) |
| `M_intermediate_zone.py` | List-size in the intermediate zone (Johnson < delta < capacity) |

### OP1: CA Barrier (`scripts/op1-barrier/`)

Verifies Remark `rem:barrier`: the equal-threshold CA bound is eps_ca = C(n,w)/|F|, not Theta(1).

| Script | Parameters |
|--------|------------|
| `op1_scaling.py` | RS[6,3] over F_q, q = 7..163 |
| `op1_scaling_n8.py` | RS[8,4] over F_q, q = 17..281 |
| `op1_cs_construction.py` | Crites-Stewart explicit construction |
| `op1_sweep_large_n.py` | Extension to n = 16, 32 |

### OP2: List-Size Obstruction (`scripts/op2-obstruction/`)

Verifies Proposition `m2-obstruction`: M_max >= 2 at FRI parameters for all p.

### FRI Coupling (`scripts/fri-coupling/`)

Direct verification of the FRI folding coupling lemma and proximity gap.

### Characteristic 2 (`scripts/char2-circle/`)

Verifies that the CA bound and coupling lemma extend to characteristic 2 (additive fold s(x) = x^2 + beta*x).

## Reproduction

Every saved output in `outputs/` can be reproduced:

```bash
# Example: verify OP1 scaling for RS[6,3]
python3 scripts/op1-barrier/op1_scaling.py

# Example: verify c>=2 moment bound
python3 scripts/list-size/c2_moment_bound.py

# Example: build Lean formalization
cd lean && lake build
```

## Citation

If you use this code, please cite:

```bibtex
@misc{chai2026fri,
  author = {Chai, Raullen and Fan, Xinxin},
  title = {FRI Soundness Above the Johnson Bound via Threshold Reduction},
  year = {2026},
  note = {Computational companion: \url{https://github.com/iotexproject/rs-proximity-gaps}}
}
```

## License

Apache 2.0
