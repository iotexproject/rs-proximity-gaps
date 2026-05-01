# Open problems left after Paper 3 (internal tracker)

This document collects the technical open problems that remain after
the publication of *Closing the FRI Commit-Side Soundness Gap via the
Berlekamp Realizer* (Paper 3, IoTeX/Chai-Fan, 2026). They are listed
in roughly decreasing order of importance for follow-up work.

> **Note.** This is the *internal* follow-up tracker for the Paper 3
> team. The principal open problem (OP-1, Lemma A) is also mirrored in
> standalone form at the repository-root file
> [`OPEN_PROBLEMS.md`](../OPEN_PROBLEMS.md), which is the version
> intended for circulation to the algebraic-geometry community. The
> root file is self-contained and tracks Lemma A only; this file
> tracks all open problems including paper-internal follow-ups
> (OP-1a through OP-7) that are out of scope for AG circulation.

---

## OP-1. Lemma A — curve-intersection degree of V_bad

**Status**: open. Empirical evidence consistent up to (n, c) = (16, 5).
Rules out the obvious uniform-measure approaches (Heintz Bezout,
Möbius inclusion-exclusion).

**Statement**. Let `n, c, k ∈ ℤ_{>0}` with `D = (n + k)/2`, `w = D - c`,
`T = ⌊(2D-1)/c⌋`, and `L ⊂ F_q^*` a multiplicative subgroup of size
`n`. Define

  V_S × V_S  :=  span{ev_v : v ∈ S} × span{ev_v : v ∈ S}  ⊂  F_q^{2D}
  V_bad      :=  ⋃_{|S| = w+1}  V_S × V_S                ⊂  F_q^{2D}

(i.e., V_bad is the union of `binom(n, w+1)` linear subspaces, each
of codim `2(c-1)`). For a generic affine line `L_α := {(s_1(α),
s_2(α)) : α ∈ F_q}` with `s_1, s_2: F_q → F_q^D` degree-1, prove
that

  |L_α ∩ V_bad|  =  n^{O(c)}                              (∗)

uniformly in q, n, c.

**What's known**.

* The naive Bezout bound `|L_α ∩ V_bad| ≤ deg V_bad = binom(n, w+1)`
  is loose (exponential).
* Möbius inclusion-exclusion on the lattice of Vandermonde supports
  gives leading coefficient `binom(n, w+1)` for the count of
  F_q-points of V_bad — **uniform measure cannot improve**.
* The IMPROVEMENT comes from passing to curve measure: a generic
  1-parameter family hits the leading components in only `O(n^c)`
  effective S^*-equivalence classes (per Note 0125 sketch).
* Empirical: `curve_max ≤ 4` at `n ≤ 12`, `curve_max = 0` at
  (n, c) ∈ {(16, 4), (16, 5)} with `|F| ≫ T`.

**Why this matters**. (∗) closes Paper 3 §8.1 modulo a single AG
input. Combined with Lang-Weil (Lemma B in §8.1), it gives
`ε^{R1}_{commit} ≤ poly(n, c) · |F|^{-2(c-1)}` rigorously, replacing
the conditional theorem currently stated.

**Suggested approach**.

1. (Combinatorial-AG) Direct proof via the alternating
   inclusion-exclusion sum on the lattice of size-`(w+1)` subsets
   of `[n]`, with a careful bookkeeping of which terms survive
   along a generic line.
2. (Algorithmic-AG transcription) Eisenbud-Schreyer "Geometry of
   Syzygies" Ch. 10 has degree formulas for unions of linear
   subspaces in special position. The Vandermonde generators of
   `V_S` are in a specific position; if a known formula applies,
   it could give `n^{O(c)}` directly.
3. (Stratified Bezout) Bertin-Vergne 1985 framework for stratified
   affine degree, applied to `V_bad`'s `S^*`-stratification.

**Relevant expertise**: Helleseth / Gong (sequence-school view of
Vandermonde supports), Sturmfels and students (algorithmic AG),
Eisenbud / Landsberg (degree formulas for special-position linear
subspace unions).

---

## OP-1a. Algorithmic instantiation of the `{M > T}` predicate (R1 deployability)

**Status**: open. Identified by feat/sec3-hybrid-framing self-review
(commit `c032e75`) after observing that Welch–Berlekamp at the
unique-decoding radius `w` returns at most one candidate, so the
naive "list-size > T" reading of R1 is empty; the actual R1 event
`{M > T}` counts realizers across `γ ∈ F_q^*`, which has no obvious
sub-linear-in-`|F|` test.

**Statement**. Find an algorithm that, given `(s_1, s_2) ∈ F_q^{2D}`,
decides `M(s_1, s_2) > T` in time `polylog(|F|) · poly(n)` (or any
sub-linear-in-`|F|` bound), with constant-or-better soundness.

**What's known**.

* Realizer enumeration: iterate `γ ∈ F_q^*`, for each test whether
  `s_1 + γ s_2 ∈ V_E` for some `|E| = w`. Per-`γ` cost is `poly(n)`
  (Vandermonde rank check). Total `O(|F| · poly(n))` per fold round.
  Operationally impractical at `|F| = 2^{31}, n = 2^{20}`.
* Welch–Berlekamp at radius `w`: returns `≤ 1` candidate; cannot
  distinguish `M = 1` from `M > T`. **The naive Berlekamp framing
  of R1 is empty.**
* Welch–Berlekamp at radius `> w` (list decoding): returns up to a
  list, but the list is over candidate codewords, not realizers
  across `γ`. Different object — does not directly answer the R1
  question.

**Why this matters**. Paper 3 §7.6 frames R1 as a *structural*
specification (Theorem 3.1 controls codim, soundness payoff is real).
Deploying R1 as an actual FRI modification requires this algorithmic
gap to close. Until then, R1 is a paper-bound proposal, not a
deployable protocol.

**Suggested approach**.

1. **Randomized Monte-Carlo estimate of M.** Sample `t` random
   `γ ∈ F_q^*`, test `s_1 + γ s_2 ∈ V_E` for some `|E| = w` per
   sample (each test is `poly(n)` via Berlekamp–Massey / Welch–
   Berlekamp). To distinguish `M ≤ T` from `M > T` with constant
   gap by Chernoff, `t = Θ(|F| / T)` is sufficient — sub-linear in
   `|F|` only when `T` is large. At small `T` (the deployment
   regime, `T ≈ poly(n)`) this remains `Θ(|F|/poly(n))` — closer
   to but not `polylog(|F|)`. **Open**: a `polylog(|F|) · poly(n)`
   randomized test with constant soundness gap.
2. **Snarkable verification.** Prover supplies a succinct
   certificate (sumcheck / inner-SNARK) that `M(s_1, s_2) ≤ T`,
   verified by the FRI verifier in `polylog(|F|) · poly(n)` time.
   The certificate's existence depends on `M ≤ T` being expressible
   as a low-degree-extension constraint — this is plausible but
   not yet proven. Compare WHIR's out-of-domain query mechanism for
   constrained Reed–Solomon codes.
3. **Vandermonde-structural test.** Exploit Theorem 3.1's
   `S^*`-stratification: a test that certifies `|S^*| ≤ w` (= R2
   regime) without enumerating realizers. The case-A counting bound
   (Paper 3 §5.1) gives `|S^*| ≤ w + ⌊w/T⌋`; making this
   computational rather than existential is the open content.
4. **Reformulate as polynomial system.** The condition
   `∀ γ : ∃ E, |E| = w, s_1 + γ s_2 ∈ V_E` is a
   quantifier-alternating statement; whether it admits an efficient
   decision procedure via Gröbner / cylindrical algebraic
   decomposition is unclear.

**Relevant expertise**: list-decoding algorithmics (Guruswami,
Sudan, Wu), Berlekamp / Welch decoders for Vandermonde codes,
randomized algebra (Schwartz–Zippel-style identity testing).

---

## OP-2. Codim of intermediate strata `{M = j}` for `2 ≤ j ≤ T`

**Status**: open. Note 0126 conjectures monotone interpolation
between `c-1` (j=1, BCIKS) and `2(c-1)` (j>T, V_bad).

**Statement**. For `(s_1, s_2) ∈ F_q^{2D}` with `M(s_1, s_2)` the
realizer count (Paper 3 §3), prove

  codim {M = j}  =  ?(c, j)                                (†)

The boundary cases are known:
* `?(c, 1) = c - 1` (BCIKS regime, codim of `{M ≥ 1}` minus higher
  strata; verified empirically in Note 0128).
* `?(c, T+1) = 2(c-1)` (the leading stratum of V_bad; Paper 3 Theorem 3.1).
* `?(c, j) > 2(c-1)` strictly for `j ≥ T + 2` (sub-leading strata of
  V_bad; Paper 3 Lemma 5.5).

The open question is the *intermediate* range `2 ≤ j ≤ T`: how does
the codim transition from `c-1` to `2(c-1)`?

**Why this matters**. Refines the threshold-mismatch picture
(Note 0126 / Paper 3 §8.1 R2 caveat). If `?(c, j)` grows
monotonically with j, the FRI commit-side error decomposition

  ε^{FRI}_{commit}  ≤  Σ_{j=1}^{T} Pr[M = j]  +  Pr[M > T]

has each term controlled by its stratum's codim, giving a refined
hybrid bound between BCIKS and Berlekamp regimes.

**What's known**: empirically, `Pr[M = 1]` follows codim `c-1` and
`Pr[M > T]` follows codim `2(c-1)` (Note 0128). The intermediate
strata have not been individually measured.

**Suggested approach**: extend the Note 0125 stratification analysis
to count, for each `j`, the codim of `{M = j}` in `F_q^{2D}` via
the `S^*`-decomposition.

---

## OP-3. Tighter R2 (BCIKS) prefactor

**Status**: not Paper 3's contribution; flagged for completeness.

The BCIKS bound `ε^{R2} ≤ poly_BCIKS(n) · |F|^{-(c-1)}` has a
specific `poly_BCIKS(n)` (typically poly-in-n of degree 1-3, see
Ben-Sasson et al. FOCS 2020). Whether this prefactor can be
improved further (e.g., to a constant in n) is an open problem in
the BCIKS / BCHKS / Goyal-Guruswami line, independent of Paper 3.

---

## OP-4. STIR / WHIR commit-side bounds via the Berlekamp realizer

**Status**: open follow-up.

**Statement**. STIR (Arnon-Chiesa-Fenzi-Yogev 2024/390) and WHIR
(2024/1586) modify FRI's per-round structure: STIR uses an `s`-fold
combination of folded codewords with shifted query domain; WHIR
wraps a multilinear-to-univariate sumcheck around the proximity
test. Per-round commit-side primitive is unchanged from FRI in
both protocols.

Two questions:

(a) **Mechanical.** Apply Theorem 3.1 (and the Lemma A reduction)
   per round and union-bound over `log_2 n` rounds. Verify the
   resulting STIR/WHIR commit-side bounds match the published
   per-round security claims of those protocols.

(b) **Joint.** STIR's `s`-fold combination simultaneously controls
   `s` syndrome pairs at correlated challenges. Does the codim
   bound improve under joint analysis (rather than per-round
   union)? WHIR's sumcheck wrapper raises a similar question for
   the multilinear extension.

**Why this matters**. STIR and WHIR are likely the next
production-deployment proximity tests after FRI; if Theorem 3.1
extends mechanically, the deployment table extends to STIR / WHIR
with no additional rigor.

---

## OP-5. Lean formalization of the ε translation

**Status**: partial. Companion repo `iotexproject/rs-proximity-gaps`
PR #3 has Theorem 3.1 (codim equality) formalized in Lean 4.

The remaining Lean work:

1. Lang-Weil application: from `codim V_bad = 2(c-1)` (formal) to
   `|V_bad(F_q)| ≤ poly(n) · |F|^{2D - 2(c-1)} + remainder`.
2. The Möbius / Boolean-lattice tightness argument from Note 0125.
3. Empirical companion: the count_M and curve-measure infrastructure
   (`op2_curve_measure_prefactor.py`) reflected as Lean computation.

Estimated effort: ~500-1000 lines of Lean for (1) and (2); (3) is
optional.

---

## OP-6. Production FRI implementation: which framing (R1 / R2)?

**Status**: open empirical question.

Paper 3 §3.1 (under the hybrid R1+R2 framing) treats production FRI
as R2 (BCIKS). This is *conjectured* based on the absence of
explicit Berlekamp list-decoding in deployed STARK provers
(Plonky3, SP1, RISC Zero, Stwo). A direct audit of the source
code of these provers would confirm or refute the conjecture.

If any of these provers actually implements an R1-style decoder
(perhaps as part of a different algorithmic component, e.g.,
zero-testing in the underlying IOP), Paper 3's bound applies more
directly than under R2.

**Audit checklist**:
- Plonky3: `commit/src/lib.rs` and `merkle-tree/src/`
- SP1: `core/src/stark/`
- RISC Zero: `circuit/keccak/src/`
- Stwo: `crates/prover/src/`

---

## OP-7. Paper 1 ↔ Paper 3 unified bound

Paper 1 (companion, `Paper1Companion`) gives a moment-bound proof
of the c = 2 case via E[M] = binom(n, w)/|F| and a sub-Poisson
tail. Paper 3 gives the codim-based proof for c ≥ 2.

A unified analysis covering all c ≥ 2 with a single argument
(bridging moment-bound and codim-based approaches) is open. The
`{M = j}` stratum codim conjecture (OP-2) is the natural bridge:
if the codim formula `?(c, j)` is known, the moment-bound
`E[M^k]` and the codim-based `Pr[M > T]` can be related directly.

---

## Provenance

- OP-1, OP-2, OP-7: identified in Notes 0125 + 0126 + 0127.
- OP-3: BCIKS / BCHKS / Goyal-Guruswami line, not Paper 3.
- OP-4: Paper 3 §8.3 "two routes" sketch.
- OP-5: companion repo Lean PR #3.
- OP-6: identified by Reviewer C#2/3/4 + Note 0126.
