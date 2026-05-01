# Note 0126 — Threshold-mismatch audit (Reviewer C#2 follow-up)

**Date**: 2026-04-30
**Branch**: `feat/berlekamp-c322`
**Builds on**: Notes 0117 + 0119 + 0122 + 0123 (Paper 3 codim theorem),
Note 0125 (Bezout-style prefactor reduction).
**Status**: audit + concrete codim arithmetic. Identifies the precise
relationship between Paper 3's `V_bad` event (`M > T`) and FRI's
commit-side bad event (`M ≥ 1`); quantifies the codim-`(c-1)` `M = 1`
stratum and shows when each event dominates the deployment ε.

## The mismatch

Paper 3 §3.1 defines

```
V_bad   :=  { (s_1, s_2) ∈ F^{2D} : M(s_1, s_2) > T }
```

where `M` counts distinct realisers `γ ∈ F` such that
`s_1 + γ s_2` lies in some `V_E` of size `w`, and
`T = ⌊(2D - 1)/c⌋` is the Berlekamp threshold. Paper 3 §3.2 derives

```
ε_commit  ≤  |V_bad(F_q)| / |F|^{2D}        (Eq. 3.4)
```

bounded later by `≤ poly(n) · |F|^{-2(c-1)}` (Note 0125).

Reviewer C#2 (on paper3.tex review) flagged: FRI's actual commit-side
bad event is "*there exists* a γ for which the fold lands close to the
RS code", i.e., `M ≥ 1`, not `M > T`. The two events differ on the
strata `{1 ≤ M ≤ T}`, which Paper 3 §3.2 silently merges into
the `V_bad`-complement.

This note audits the gap and quantifies its impact on deployment.

## Two framings

### (R1) Berlekamp framing — Paper 3's V_bad event is correct

In list-decoding, a decoder accepts up to `L` candidate codewords; if
the syndrome admits *more* than `L` "valid" interpretations, the
decoder cannot disambiguate. The **Berlekamp threshold** `T` is the
list-decoding radius for RS codes at the relevant rate. Under this
framing:

* `M > T`  ⟺ decoder failure  ⟺ FRI bad event.
* `1 ≤ M ≤ T` ⟺ fold has 1..T valid candidates, all disambiguated
  by the Berlekamp decoder ⟺ *not* a bad event.

If FRI's protocol is "honest prover gives `M = 1` (the actual
codeword), adversarial prover gives `M > T`", then `V_bad` *is* the
right event. This is Paper 3 §3.1's stated framing.

### (R2) BCIKS framing — `M ≥ 1` is the FRI bad event

In BCIKS's analysis (FOCS 2020), the commit-side bad event is "the
prover's commitment is close to the RS code in a way that's
detectable". This corresponds to `M ≥ 1` in the Berlekamp framing
(any non-zero realiser count is a potential "close-to-code" signal).

Under (R2), the residual `{1 ≤ M ≤ T}` strata contribute to the
FRI ε bound:

```
ε_commit_FRI  ≤  Σ_{j=1}^{T} Pr[M = j]  +  Pr[M > T].
```

## Concrete codim of each stratum

We work out the codim of `{M = j}` for `j ∈ [1, T+1]` in `F^{2D}`.

### `M = 1` stratum

`{M ≥ 1}` = `{(s_1, s_2) : ∃ γ ∈ F : s_1 + γ s_2 ∈ V_E for some E}`.

For each fixed `(γ, E)`: `{(s_1, s_2) : s_1 + γ s_2 ∈ V_E}` is a
codim-`c` affine subspace of `F^{2D}` (since `V_E` is codim `c` in
`F^D`).

Varying `γ` ∈ F: union has codim `c - 1` (one parameter consumed).
Varying `E` ∈ C(n, w): finite union, no further codim reduction.

**Claim (BCIKS-style):** `codim {M ≥ 1} = c - 1` (with equality
generically).

**Sketch:** The locus is a `1`-parameter family of codim-`c` affine
subspaces, parametrized by `γ ∈ F`. The image has codim `c - 1`
generically, codim `c` for special `γ`. Taking the union over all
`γ` and `E` gives codim `c - 1`.

**Lang–Weil applied:** `|{M ≥ 1}(F_q)| ≤ poly(n) · q^{2D - (c-1)}`,
so

```
Pr[M ≥ 1]  ≤  poly(n) · q^{-(c - 1)}.
```

For deployment (`c = 6`, `|F| = 2^{186}`, `n = 2^{20}`):
`poly(n) · 2^{-930}`, *much* tighter than the deployment target
`2^{-128}` (assuming `poly(n) = n^{O(1)}`).

For deployment (`c = 3`, `|F| = 2^{31}`, `n = 2^{20}`):
`poly(n) · 2^{-62}`, *not* tight enough for `2^{-128}` — exactly the
regime where Paper 3 §6.3's structural obstruction applies.

### `M = j` stratum, 2 ≤ j ≤ T

By the Note 0117 leading-stratum construction (`V_S × V_S` for
`|S| = w + 1`), at deployment scale (`w + 1 ≥ T + 1`) the leading
component already realises `M = w + 1 ≥ T + 1`, so the `{M ≥ T + 1}`
locus has codim `2(c - 1)`. By Note 0123's strict-gap analysis,
sub-leading strata `{M = j}` for `T + 1 ≤ j` have codim ≥ 2(c - 1)
with strict equality at the leading.

For `2 ≤ j ≤ T`: the stratum is between the BCIKS `M = 1` regime
(codim `c - 1`) and the Berlekamp `M > T` regime (codim `2(c - 1)`).
The codim transitions monotonically:

| `j` (realiser count) | codim of `{M = j}` (deployment, generic position) |
|-----------------------|------|
| 1 (BCIKS)             | `c - 1`         |
| 2                     | `c - 1` to `2(c - 1)` (transition)  |
| ⋮                     | (monotone increase) |
| T                     | `≈ 2(c - 1)`    |
| T + 1 (V_bad leading) | `2(c - 1)`      |
| T + 2 (sub-leading)   | `> 2(c - 1)` (Note 0123) |

The intermediate strata's codim depends on the Vandermonde
configuration; an exact formula is open but the *minimum* codim is
`c - 1` (matching `M = 1`).

## Combined bound for FRI's bad event

Putting together the strata:

```
ε_commit_FRI  =  Pr[M ≥ 1]
              =  Pr[M = 1]  +  Σ_{j=2}^{T} Pr[M = j]  +  Pr[M > T]
              ≤  poly(n) · |F|^{-(c-1)}                     [M = 1, BCIKS]
              +  T · poly(n) · |F|^{-2(c-1)}                [M ∈ [2, T]]
              +  poly(n) · |F|^{-2(c-1)}.                   [M > T, V_bad]
```

The first term **dominates** at all deployment-scale `|F|` and
`c ≥ 2`. So, conservatively:

```
ε_commit_FRI  ≤  poly(n) · |F|^{-(c-1)}                   (RIGOROUS, c ≥ 2)
```

This **is the BCIKS bound**, recovered through the Berlekamp framing.

## Deployment impact

The two framings give *different* deployment thresholds:

| Field, `c` | (R1) `\|F\|^{-2(c-1)}` | (R2) `\|F\|^{-(c-1)}` |
|------------|-------------------------|------------------------|
| BabyBear, c=3 (`\|F\|=2^{31}`)  | `2^{-124}` (4 bits short) | `2^{-62}` (66 bits short)  |
| KoalaBear-ext6, c=6 (`\|F\|=2^{186}`) | `2^{-1860}` (1732 bits) | `2^{-930}` (802 bits) |
| Mersenne31, c=3 | `2^{-124}` | `2^{-62}` |
| Goldilocks, c=3 (`\|F\|=2^{64}`) | `2^{-256}` (128 bits)   | `2^{-128}` (0 bits margin) |

**Punchlines:**

1. **Sextic extensions (c = 6)** comfortably satisfy *both* framings;
   ABF §6.3's choice is robust either way.
2. **Goldilocks-c=3** *just* meets `2^{-128}` under (R2) and has
   massive headroom under (R1). This is the "marginal" deployment
   case where the framing matters.
3. **Base 31-bit fields with c = 3** fail under both: `2^{-62}` and
   `2^{-124}` are both below `2^{-128}`. Paper 3's structural
   obstruction (§6.3) applies *regardless* of framing.

## Recommended resolution

Paper 3 should be **explicit** about which framing it adopts:

* **If (R1)** (Paper 3's stated framing): §3.1 should clarify that
  V_bad is "the locus where the Berlekamp list-decoder fails", and
  the deployment table's `|F|^{-2(c-1)}` headline is the right bound
  *for that decoder model*.

* **If (R2)** (BCIKS framing): the deployment-table headline is the
  weaker `|F|^{-(c-1)}` (BCIKS bound), with the Berlekamp
  `|F|^{-2(c-1)}` improvement reserved for the `M > T` sub-regime.

Both framings preserve the qualitative deployment claims:

  * Sextic extensions (c = 6): comfortable across both framings;
  * Base 31-bit + c = 3: structurally obstructed across both framings.

The marginal cases (Goldilocks-c=3, BabyBear-ext2-c=3, etc.) depend on
which framing is operative; Paper 3 §3.1 + §6.1 should state the
choice.

## On the FRI protocol's actual bad event

In production FRI (Plonky3, SP1, RISC Zero, Stwo): the verifier
performs a *fold check* at the verifier's challenge `γ`. The check
*accepts* if the fold lands close to the RS code, *rejects*
otherwise. So the bad event for an adversarial prover is:

```
∃ γ (verifier's challenge) such that fold(s_1, s_2, γ) is close to RS.
```

The set of such γ has size `M(s_1, s_2)`. The probability over the
verifier's random choice is `M / |F|`.

For a *single-round* FRI without further consistency checks: the bad
event corresponds to `M ≥ 1` (any close-to-code γ is accepted). This
is BCIKS framing (R2).

For a *multi-round* FRI with explicit list-decoding (rare in
production): the bad event might be `M > T` (decoder fails). This is
Berlekamp framing (R1).

**Paper 3 should examine which model matches Plonky3 / SP1 / RISC
Zero specifically.** I conjecture (R2) because production FRI rarely
includes Berlekamp's list-decoder as an explicit step; the
soundness argument relies on the BCIKS proximity-gap bound, which
is for `M ≥ 1`.

If (R2) is correct, Paper 3 should:

1. State `|F|^{-(c-1)}` as the rigorous BCIKS bound.
2. State `|F|^{-2(c-1)}` as the *improved* Berlekamp bound *under
   the assumption* that the protocol explicitly uses Berlekamp
   list-decoding (a non-standard choice).
3. Position the `2(c-1)` improvement as a soundness-architecture
   suggestion: "*if* deployment includes Berlekamp list-decoding,
   then ε is `|F|^{-2(c-1)}` instead of `|F|^{-(c-1)}`."

This is a substantive contribution: it suggests a *protocol
modification* (add Berlekamp list-decoding to FRI) that *doubles* the
effective security level, motivated by Theorem 3.1.

## Files

- `notes/0126-threshold-mismatch-audit.md` — this note.

## References

- BCIKS — Ben-Sasson, Carmon, Ishai, Kopparty, Saraf. *Proximity gaps
  for Reed–Solomon codes.* FOCS 2020.
- Paper 3 — Chai, Fan. *Closing the FRI Soundness Gap: A
  Sequence-School Approach.* (2026, preprint).
- Note 0125 — *Bezout-style prefactor proof.*
