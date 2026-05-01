# Note 0215 — Universal upper bound CONDITIONAL on sparse support

**Date:** 2026-04-29
**Status:** Conditional analytic proof — given sparse support
`{0, k, 2k}`, the upper bound `B ⊆ {ρ : ρ⁴ = 1}` follows by direct,
k-uniform polynomial arithmetic. This is a genuine reverse-direction
proof.

## Statement

**Theorem (Universal sign-paired upper bound, conditional)**.
For deployment scale `n = 4k`, sign-paired pencil `h_ρ(z) = ρ z^a +
z^{a+n/2}`, suppose every half-set witness σ_S has support ⊆ `{0, k, 2k}`,
i.e., `σ_S(z) = z^{2k} + p_k z^k + p_0`. Then the bad-ratio set
satisfies:
$$
B \subseteq \{\rho \in F_q^* : \rho^4 = 1\} = \{1, -1, \iota, -\iota\}.
$$

The proof is k-uniform (no k-dependent computation).

## Proof

Set `σ_S = z^{2k} + p_k z^k + p_0` (sparse support assumption).
Reduce powers of z mod σ_S:

`z^{2k} ≡ -p_k z^k - p_0`.

For `a ∈ [k, 2k-1]` (the deployment-shape range, where cert eqs apply
at degrees `[k, 2k-1]`), and `b = a + 2k`:

`z^b = z^a · z^{2k} ≡ -p_k z^{a+k} - p_0 z^a`.

`z^{a+k}` with `a+k ∈ [2k, 3k-1]` needs further reduction:
`z^{a+k} = z^{a-k} · z^{2k} ≡ -p_k z^a - p_0 z^{a-k}`.

Substituting:
$$
z^b \equiv (p_k^2 - p_0) z^a + p_k p_0 z^{a-k} \pmod{\sigma_S}.
$$

### Cert equations

At degrees `j ∈ [k, 2k-1]`:
- `j = a`: `ρ + (p_k² - p_0) = 0`, hence `p_0 = p_k² + ρ`.
- `j ∈ [k, 2k-1] \ {a}`: 0 = 0 (no contribution since `a-k ∈ [0, k-1]`
  doesn't intersect `[k, 2k-1]`).

So cert eqs collapse to one identity: **(C) `p_0 = p_k² + ρ`**.

### Divisor equations

`x^n = x^{4k} = (x^{2k})^2 ≡ (-p_k z^k - p_0)² (mod σ_S)`
= `p_k² z^{2k} + 2 p_k p_0 z^k + p_0²`.

Reduce `z^{2k}`:
= `p_k²(-p_k z^k - p_0) + 2 p_k p_0 z^k + p_0²`
= `(-p_k³ + 2 p_k p_0) z^k + (p_0² - p_k² p_0)`
= `p_k(2 p_0 - p_k²) z^k + p_0(p_0 - p_k²)`.

For `x^n ≡ 1`:
- Coefficient of `z^k`: **(D1) `p_k(2 p_0 - p_k²) = 0`**.
- Constant: **(D2) `p_0(p_0 - p_k²) = 1`**.

Other coefficients automatically zero (sparse support of `x^n` mod σ_S).

### Combining

Substitute (C) `p_0 = p_k² + ρ` into (D1) and (D2):

**(D1)**: `p_k(2(p_k² + ρ) - p_k²) = p_k(p_k² + 2ρ) = 0`.
Either `p_k = 0` or `p_k² = -2ρ`.

**(D2)**: `(p_k² + ρ)((p_k² + ρ) - p_k²) = (p_k² + ρ) · ρ = ρ p_k² + ρ² = 1`.
So `ρ p_k² = 1 - ρ²`.

### Case A: `p_k = 0`

(D2) becomes `0 + ρ² = 1`, so `ρ² = 1`, `ρ ∈ {1, -1}`.

### Case B: `p_k² = -2ρ`

(D2) becomes `ρ · (-2ρ) + ρ² = -2ρ² + ρ² = -ρ² = 1`, so `ρ² = -1`,
`ρ ∈ {ι, -ι}`.

### Conclusion

In both cases, `ρ⁴ = 1`. So **`B ⊆ {ρ : ρ⁴ = 1}`** at every deployment scale.

Combined with codex Note 0192's existence direction (4 ratios are bad),
**`B = {ρ : ρ⁴ = 1}`** at every deployment scale. **□**

## What this gives us

| Statement | Status |
|---|---|
| Universal sign-paired upper bound, given sparse support | **RIGOROUS** (this note) |
| Universal sign-paired upper bound, unconditional | Reduced to: **prove sparse support** |
| Sparse support `{0, k, 2k}` | Empirically true at (8,2)+(16,4); structural sketch in Note 0214; rigor pending |

This reduces the universal upper bound problem to a single structural
claim: **every half-set witness for sign-paired pencil has σ_S support
⊆ {0, k, 2k}**.

## Why sparse support is plausible

**Negation invariance**: For sign-paired `b = a + n/2`, the substitution
`z ↦ -z` maps witnesses to witnesses (via `(S, ρ, r(z)) ↦ (-S, ρ,
(-1)^a r(-z))`).

If S is fixed by negation: `S = S' ⊔ (-S')`, σ_S has even-power support
⊆ `{0, 2, ..., 2k}`.

If S is not fixed by negation: `(S, -S)` is a pair of distinct witnesses.
By the orbit structure, can choose a representative with finer invariance.

**Rotation invariance** (heuristic): the cyclic action `z ↦ ω^{n/k} z`
(primitive k-th root) on σ_S maps cert+div_(a,b) to cert+div_(a+n/k,
b+n/k). For consistency with bad-ratio set being shifted by ω^{n/k · (a-b)}
= ω^{n/k · (-n/2)} = ω^{-n²/(2k)} ... at sign-paired this evaluates to a
specific 4-th root. The "self-conjugacy" of the orbit forces the
representative to be invariant.

This is heuristic; the rigorous version is the next note.

## Compare to substitute-verify

The substitute-verify (Note 0203) proves **existence**: substituting the
proposed solution into cert+div makes them vanish.

This Note 0215 proves **upper bound**: starting from cert+div (assuming
sparse support) and reducing, the only solutions are `ρ⁴ = 1`.

The two directions together (with sparse support proven) give
`cert + div = ⟨I⟩` as ideals at deployment scale.

## Next steps

1. **Prove sparse support theorem**: this is now the only remaining gap.
2. **Generalize to non-sign-paired**: the same reduction technique should
   give Φ_(a,b)(ρ) for general (a, b), conditional on the appropriate
   sparse support pattern. (Existence side is in Notes 0204/0207.)

## Files

- `notes/0215-conditional-upper-bound-given-sparse-support.md` (this).
- `notes/0214-empirical-path-CD-scale-invariant-GB.md` — empirical
  scale-invariant GB.
- `notes/0203` (existence side, scale-uniform).
