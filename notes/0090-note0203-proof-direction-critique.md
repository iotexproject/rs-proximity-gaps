# Note 0090 — Proof-direction critique of `fri-2round-tightness` Note 0203

**Date:** 2026-04-29
**Status:** Critical pre-submission concern. Forwardable to branch author.
**Context:** During autonomous Paper 2 cherry-picking, evaluated whether
`fri-2round-tightness` Note 0203 ("UNIVERSAL ANALYTIC PROOF: sign-paired
bad ρ ⊆ 4-th roots, all deployment scales") can be cherry-picked into Paper 2
§4 to upgrade Theorem 4.5 (`thm:groebner-toy`) from rigorous-at-toy to
rigorous-at-all-scales.

## Conclusion

**Note 0203's "universal" upper bound is NOT proved.** What is proved is the
existence direction (already known via codex Note 0192). The substitute-verify
technique used in Note 0203 (and extended in Notes 0204, 0207) only verifies
one half of an ideal equality. Note 0208 (ePrint draft outline) inherits the
same gap and would be rejected on review unless tightened.

Note 0199's full Groebner-basis closure at `(n, k) ∈ {(8, 2), (16, 4)}` is
genuinely rigorous (independently re-verified here, see §5).

## The error in Note 0203

Note 0203 sets up an ideal
```
   I = ⟨ p_i  (i ∉ {0, k}),  p_0 - ρ³,  p_k² - (ρ³ - ρ),
         p_k(ρ² + 1),  ρ⁴ - 1 ⟩
```
and the certificate-plus-divisor ideal `(cert + div)` from the locator
polynomial system. The substitute-verify procedure rewrites every `cert + div`
generator using the I-generators as substitution rules; each generator
reduces to 0. This proves
```
   cert + div ⊆ I.
```
By the standard ideal-variety duality
```
   J ⊆ I  ⟺  V(I) ⊆ V(J),
```
this gives `V(I) ⊆ V(cert + div)`. Note 0203 then writes:

> "Equivalently, V(cert + div) ⊆ V(I)."

This is the opposite inclusion. The actual conclusion is `V(I) ⊆
V(cert + div)`, i.e., `{(p, ρ) satisfying I} ⊆ bad witnesses`. Projecting to
the ρ-axis: `{±1, ±ι} ⊆ bad-ρ set`. This is the **existence** direction
(equivalently, codex Note 0192's elementary identity).

The **upper bound** would require `V(cert + div) ⊆ V(I)`, equivalently
`I ⊆ cert + div`. Note 0203's substitute-verify procedure does not establish
this direction.

## Confirmation from the script's own docstring

The verification script `notes/scripts/g3_substitute_verify.py` on
`fri-2round-tightness` is explicit:

```
"""
[...] then substituting these into each cert+div equation should give 0
[...] This verifies cert+div ⊆ I (where I is the proposed ideal).

It does NOT prove I ⊆ cert+div, but is one half. The other half is what
Sympy Groebner verifies; this gives us a sanity check that scales.
"""
```

Success message in the same script:
```
✓ Direction (cert+div ⊆ proposed-ideal) verified
```

So the script and its author are aware that only one direction is checked.
The leap to "universal upper bound" appears in Note 0203's prose and in
Note 0208's ePrint draft, not in the verified mathematics.

## Independent Groebner verification at toy

To confirm Note 0199's toy claim independently, ran SymPy `sp.groebner` on
`(cert + div)` directly:

```
=== (n=8, k=2, a=2, b=6) ===
GB(cert+div) lex order in 0.4s, 6 polynomials:
  p_1
  p_3
  p_2² - ρ³ + ρ
  p_2(ρ² + 1)
  p_0 - ρ³
  ρ⁴ - 1

=== (n=16, k=4, a=4, b=12) ===
GB(cert+div) grevlex in 76.9s
D1 PASS: all 10 G-generators reduce to 0 mod GB(cert+div)
D2 PASS: all 12 cert+div equations reduce to 0 mod GB(G)
```

So at `(8, 2)` and `(16, 4)`, the ideals (cert + div) and the Note-0199
proposed I are equal as ideals. This is genuine rigorous coset-rigidity at
toy scales.

At `(32, 8)`, SymPy `sp.groebner` did not complete in 60 minutes
(exponential blow-up; 18 G-generators + 24 cert+div equations in 17
variables). No independent Groebner verification at this scale.

## Why the substitute-verify cannot give the upper bound

Substitute-verify takes the I-generators as rewriting rules and checks they
reduce cert+div generators to 0. This is a **forward** check: I-rules are
used to simplify cert+div polynomials.

The reverse check needed for the upper bound would be:
> Express each I-generator (in particular `ρ⁴ - 1` and each `p_i` for
> `i ∉ {0, k}`) as an explicit polynomial combination of cert+div
> generators.

This is not a substitution; it is an ideal-membership test. At toy scales
this is what Note 0199's full Groebner basis computation provides. There is
no analogous scale-uniform analytic argument in Note 0203.

## Suggested fixes (in order of effort)

**A. Tighten the statement, preserve the result.**
Rewrite Note 0203 (and Note 0208 §4) as:
> *Theorem (Sign-paired existence — analytic, scale-uniform).*
> For sign-paired pencil at deployment scale `n = 4k`, the four ratios
> `{±1, ±ι}` are bad. The proof is by direct polynomial arithmetic and is
> valid at every deployment scale.

This is genuinely new (vs codex Note 0192's elementary identity, the proof
technique here is reusable for other families like (k, 2k)) and is what the
substitute-verify actually establishes.

The K-bound theorem then stays unconditionally rigorous for the
**existence** of sign-paired contributions but the **upper bound** is
conditional on a separate coset-rigidity step.

**B. Establish the reverse inclusion analytically.**
Prove `I ⊆ cert + div` directly by exhibiting each I-generator as a
polynomial combination of cert+div generators. The toy Groebner output
gives a concrete target: at `(8, 2)`, the lex GB output above is the exact
form. Find an explicit combination uniformly in `k`. This may be possible
via a structural argument — see option C.

**C. Use a dimension/symmetry argument for the upper bound.**
The cert+div system has `k` certificate equations (degrees `[k, 2k-1]`) and
`2k` divisor equations, giving `3k` equations in `2k+1` variables
`(p_0, ..., p_{2k-1}, ρ)`. The system is acted on by the cyclic group
`⟨ω⟩` of order `n = 4k` (Theorem 0187 action). A clean argument might:

1. Show `V(cert + div)` is closed under the cyclic action.
2. Show the action is free on `V(cert + div)` away from a small
   exceptional locus.
3. Conclude `|V(cert + div)| ≤ (small) · n`, projecting to ≤ 4 ρ-values.

The shift-symmetry observation in Note 0200 is in this direction but did
not close.

## Implication for Paper 2

Paper 2's Theorem 4.5 (`thm:groebner-toy`) currently states the upper
bound at `(8, 2)` and `(16, 4)` only, citing Note 0199. This is
independently verified here and remains the strongest rigorous claim. No
upgrade based on Note 0203 is warranted.

If Note 0203's gap is closed (via fix B or C above), Paper 2 §4 can
immediately upgrade to universal-rigorous; this is the highest-ROI
cherry-pick the project has.

## Verification scripts

- `/tmp/verify_groebner.py` (local): runs SymPy `sp.groebner` and checks
  D1 + D2 directly.
- `notes/scripts/g3_verify_basis_template.py` (on
  `fri-2round-tightness` 2a36714): attempts D1 + D2 but uses single-pass
  `sp.reduced` rather than full Groebner reduction, so both directions
  fail trivially due to the test, not the math. Should be replaced with
  Groebner-based reduction as in this note.

## References

- `fri-2round-tightness` Note 0199 (RIGOROUS coset-rigidity at toy via
  Groebner): genuinely correct.
- `fri-2round-tightness` Note 0203 (UNIVERSAL ANALYTIC PROOF): only one
  direction; existence not upper bound.
- `fri-2round-tightness` Note 0204, 0207 (analytic extensions): same
  one-direction issue.
- `fri-2round-tightness` Note 0208 (ePrint outline): inherits the gap.
- `codex/fri-conje-attack` Note 0192 (elementary existence identity):
  rigorous; this is what Note 0203's analytic argument actually
  re-establishes scale-uniformly.
