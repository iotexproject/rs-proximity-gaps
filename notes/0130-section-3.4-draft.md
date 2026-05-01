# Note 0130 — §3.4 draft: Implementable Berlekamp decoder (SUPERSEDED)

**Date**: 2026-04-30
**Status**: **SUPERSEDED 2026-04-30 by feat/sec3-hybrid-framing
commit `c032e75`.** The Welch-Berlekamp framing in this draft is
based on a wrong premise: at the unique-decoding radius `w`, the
WB decoder returns at most one candidate codeword, so the
"list-size > T" rejection predicate this draft proposes is empty
(it never fires). The actual R1 event `{M > T}` counts realizers
across `γ ∈ F_q^*`, which is a different combinatorial object that
no Welch-Berlekamp instantiation directly tests.

**The correct §7.6** in paper 3 (after `c032e75`) frames R1 as a
*structural specification* (verifier rejects iff `M(s_1, s_2) > T`)
and explicitly flags the algorithmic gap: the simplest instantiation
(realizer enumeration) is `O(|F| · poly(n))` per fold round; no
sub-linear-in-`|F|` algorithm is known. See
[`notes/OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) OP-1a for the
algorithmic open problem in standalone form.

**Why this draft is preserved**: as a record of the WB-cost analysis
that motivated the algorithmic-gap recognition. The folded-last-layer
trade-off discussion below (and the cost numbers for `n_f ≤ 256`)
remain useful if the algorithmic gap is closed via a list-decoding-
like primitive at the last layer. Until then, the "deploy WB at
folded last layer" recommendation is moot.

**Critical correction from research subagent (2026-04-30)**: my
earlier estimate of "+10% verifier time" for full-domain Welch-Berlekamp
was wrong by ~3 orders of magnitude. The fix below restricts the
decoder to the **folded last layer**, where the cost is genuinely
small. (Note: even the corrected fix is moot per the
SUPERSEDED notice above.)

---

## Draft text for paper 3 §3.4

**§3.4 Implementable Berlekamp list-decoder**

The protocol modification proposed in §3.1 (R1 framing) augments
the FRI verifier with an explicit Welch-Berlekamp list-decoder
applied to the **folded last layer** of FRI's recursive folding
schedule. We argue this is engineering-tractable and Fiat-Shamir
sound.

### Cost analysis

FRI folds an initial codeword of length `n = 2^N` through `R = N -
N_0` rounds, leaving a final layer of length `n_f = 2^{N_0}` for
some configurable `N_0` (typically `N_0 ∈ [4, 8]`, so `n_f ∈ [16,
256]`). The proposed modification: at the final layer, instead of
verifying via direct evaluation against a low-degree witness, run
Welch-Berlekamp on the folded codeword to list-decode and check
list-size ≤ T.

**Decoder complexity** (textbook Welch-Berlekamp): `O(n_f^3)` field
operations. At `n_f = 256`: `~10^7` ops, ≈ 10 ms on a modern CPU at
`10^9` ops/s. At `n_f = 16`: `~4·10^3` ops, sub-microsecond.

**Verifier-side overhead**: a typical FRI verifier at `n = 2^{20}`
performs ~30 colinearity queries × ~20 Merkle path levels = ~600
hash compressions, plus a few thousand field multiplications.
Total verifier time ~10-20 ms (Plonky3 / SP1 numbers, c.f. ethSTARK
documentation).

**Ratio (folded last layer)**: Welch-Berlekamp at `n_f = 256` adds
~10 ms to ~15 ms verifier time = **~67% overhead on verifier**.
At `n_f = 64`: ~150K ops ≈ 0.15 ms = **~1% overhead**. At
`n_f = 16`: negligible.

**Recommended deployment**: use `n_f ∈ [16, 64]` to keep the
decoder overhead under 5%. This is the same range FRI deployments
already use for the final-layer threshold (per Plonky3 / SP1 / RISC
Zero defaults).

### Why fast variants don't help here

The literature has fast Welch-Berlekamp variants (Justesen 1976,
Gao 2002) running in `Õ(n)` field ops via additive FFT. These
matter for *full-codeword* decoding (n = 2^{20}) where O(n^3) is
prohibitive. At the **folded last layer** (n_f ≤ 256), the textbook
O(n^3) is already cheap, so the engineering complexity of the fast
variants isn't justified. Use the textbook decoder.

### Fiat-Shamir compatibility

The decoder runs on the folded codeword, which is fully
committed-to in the transcript by the time the verifier runs the
decoder. Decoder output is a deterministic function of the
transcript; the round-by-round soundness argument (Attema-Fehr-Klooß,
J. Cryptology 2023) is unaffected.

**Caveat**: if the decoder's output is fed into a subsequent
Fiat-Shamir challenge derivation, that derivation must hash the
decoder output into the transcript via an explicit absorb call.
Otherwise a state-restoration attack (Holmgren, eprint 2019/1261)
becomes possible. The fix is one extra `transcript.absorb(decoded)`
before the next squeeze.

### Library status

No production STARK prover (Plonky3, SP1, RISC Zero, Stwo,
Winterfell) currently ships a Welch-Berlekamp decoder; their RS
handling is encoder-only. The reference Rust crate
(`SohamJog/reed_solomon_rs`) is GF(256), education-grade, O(n^3) —
the GF(256) doesn't transfer to STARK fields (BabyBear, KoalaBear,
Goldilocks, Mersenne31). The decoder must be written from scratch
on top of Plonky3's NTT primitives. Estimated effort: 500-2000
lines of Rust depending on field generality. We list this as a
concrete engineering deliverable.

---

## Open engineering questions (post-§3.4)

1. **Wall-clock benchmark**: no published wall-clock for fast WB on
   a STARK field at any `n_f`. The above analysis is paper-bound.
   A concrete benchmark on KoalaBear at `n_f = 64` would close this
   gap.

2. **Per-prover integration cost**: each of Plonky3 / SP1 / RISC
   Zero / Stwo would need to add a decoder call. The integration
   surface area depends on each prover's verifier architecture.

3. **Trade-off with `n_f` choice**: smaller `n_f` (= 16) makes the
   decoder negligible but increases the recursion depth, costing
   verifier hashes. Larger `n_f` (= 256) shrinks recursion but
   makes the decoder dominant. The optimal `n_f` for the R1 + WB
   protocol is open.

---

## Sources for the draft

- Justesen, *On the complexity of decoding Reed-Solomon codes*
  (IEEE TIT 1976) — fast WB asymptotic
- Gao, *A New Algorithm for Decoding Reed-Solomon Codes* (2002) —
  modern fast WB
- Häböck, *A summary on the FRI low degree test*, eprint 2022/1216 —
  FRI verifier cost breakdown
- Ben-Sasson et al., *ethSTARK Documentation v1.2*, eprint 2021/582 —
  config: 30 queries, ρ=1/8, PoW=20
- Attema-Fehr-Klooß, *Fiat-Shamir Transformation of Multi-Round
  Interactive Proofs*, J. Cryptology 2023 — round-by-round soundness
- Holmgren, *On Round-by-Round Soundness and State Restoration
  Attacks*, eprint 2019/1261 — state-restoration caveat
- `SohamJog/reed_solomon_rs` — only Rust WB crate (GF(256), O(n^3))
- Plonky3 repo — encoder + FRI only, no decoder

---

## What this note is NOT

* **NOT a full RFC for the protocol modification.** A full RFC
  would include a precise pseudocode, transcript-binding spec, and
  composition with Fiat-Shamir. This note is paragraph-level
  guidance for §3.4 of paper 3.

* **NOT a benchmark.** The numbers above are operation counts
  derived from the literature; no wall-clock measurement was
  performed. Production deployment requires a benchmark on the
  target STARK field.
