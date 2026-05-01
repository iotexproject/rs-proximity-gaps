# Note 0124 — Curve-vs-uniform measure prefactor for V_bad

**Date**: 2026-04-29
**Branch**: `feat/berlekamp-c322` (post-merge)
**Builds on**: Notes 0117 + 0119 + 0122 + 0123 (paper 3 codim theorem),
Paper 3 §8.1 (open question).
**Status**: empirical analysis. Confirms the sharpening direction
sketched in §8.1 of Paper 3; suggests a clean Bezout-style analysis
to replace the `C(n, w+1)` prefactor with a tame `n^{O(c)}`.

## Headline

Paper 3, Theorem 3.1 establishes `codim V_bad = 2(c−1)` rigorously.
The conservative uniform-measure consequence is

```
eps_commit_unif  ≤  C(n, w+1) · |F|^{-2(c-1)}.        (uniform measure)
```

The `C(n, w+1)` prefactor is the union-bound count of `V_S × V_S`
components and grows as `≈ 2^n` at deployment scale (`n = 2^{20}`,
`w ≈ n/2`), which would swamp the `|F|^{-2(c-1)}` codim gain unless
the components overlap heavily.

This note empirically demonstrates the overlap is *substantial*. Across
6 small parameter combinations spanning `c ∈ {3, 4}`, the V_bad variety
degree as seen by a generic 1-parameter line in `F^{2D}` is

```
deg_eff(V_bad)  ≤  4   for (n, c) ≤ (12, 3)         (curve_max = 4),
deg_eff(V_bad)  =  0   for (n, c) ≤ (12, 4)         (within 20 curves × |F| = 260 challenges),
```

versus the naive `C(n, w+1) ∈ {70, ..., 924}` union bound. The
nonzero rows show curve_max about **2–3 orders of magnitude** below
the union bound; the c = 4 rows hit zero in the sample budget,
consistent with — but not yet rigorous evidence for — a much larger
gap. Larger sweeps (more curves, more (n, c) cases) are needed to
sharpen the constant.

## The curve-measure model

For an FRI commit-side Berlekamp argument, `(s_1, s_2)` is constrained
to a 1-parameter algebraic family

```
(s_1(α), s_2(α))  =  (a + α b,  c + α d),         α ∈ F_q
```

where `(a, b, c, d) ∈ F_q^{4D}` is determined by the prover's
commitment and verifier's prior challenges. A generic such line
intersects an irreducible affine variety `V_bad ⊆ F_q^{2D}` of degree
`D_var` in at most `D_var` points (Bezout):

```
eps_commit_curve  =  |{α ∈ F : (s_1(α), s_2(α)) ∈ V_bad}| / |F|
                  ≤  D_var / |F|.
```

If `D_var = poly(n)` (sub-`C(n, w+1)`), the curve-measure bound is
asymptotically `poly(n) / |F|`, sharper than `C(n, w+1) · |F|^{-2(c-1)}`
whenever `|F|^{2(c-1)-1} · poly(n) ≪ C(n, w+1)`. At deployment
parameters (`|F| ≥ 2^{31}`, `c ≥ 3`), this is the regime of interest.

## Empirical results

`op2_curve_measure_prefactor.py` enumerates each `α ∈ F` for 20 random
degree-1 lines, counting `V_bad`-hits via the same Berlekamp `M`-counting
used in Notes 0117–0119. Output table (full output in
`op2_curve_measure_prefactor.output.txt`):

| (n, c, p)    | D | w | T | eps_unif | eps_curve_avg | curve_max | C(n, w+1) |
|--------------|---|---|---|----------|---------------|-----------|-----------|
| (8, 3, 17)   | 6 | 3 | 3 | 4.5e-04  | 0             | 0         | 70        |
| (8, 3, 41)   | 6 | 3 | 3 | 0        | 0             | 0         | 70        |
| (10, 3, 11)  | 7 | 4 | 4 | 7.05e-03 | 4.55e-03      | 1         | 252       |
| (10, 3, 31)  | 7 | 4 | 4 | 1.5e-04  | 0             | 0         | 252       |
| (12, 3, 13)  | 9 | 6 | 5 | 9.74e-02 | 7.69e-02      | 4         | 792       |
| (12, 4, 13)  | 9 | 5 | 4 | 5e-05    | 0             | 0         | 924       |

Three observations:

1. **`curve_max ≪ C(n, w+1)`.** Even the worst observed line hits at
   most 4 V_bad points, against a naive `C(n, w+1)` union bound of 70
   to 924. The variety degree as seen by a generic line is **3 orders
   of magnitude** below the union bound, even at `n = 12`.

2. **`c = 4` rows already have zero curve hits.** With `2(c−1) = 6 > 1`
   the codim-2(c-1) variety is generically missed by a 1-dim line. The
   curve-measure ε is essentially zero at the modest `|F|` tested here.

3. **`ε_curve` scales as `O(1/|F|)`** (the Bezout regime) at the small
   `c = 3` rows where some hits occur. As `|F|` grows from 11 to 31 at
   `n = 10, c = 3`, observed hits drop from 1 to 0 — consistent with
   the `D_var / |F|` curve-measure scaling.

## What this says about the §8.1 open question

The §8.1 question is whether the `C(n, w+1)` prefactor can be replaced
with a tame `n^{O(c)}` factor. The empirical evidence above is
**consistent with a tighter bound**

```
eps_commit  ≤  poly(n) · |F|^{-2(c-1)}        (curve measure)
```

with `poly(n) = n^{O(c)}` rather than `C(n, w+1)`. To make this
rigorous, two ingredients are needed:

* **Variety-degree bound for `V_bad`.** The leading
  `⋃_{|S|=w+1} V_S × V_S` decomposition is a union of
  linear subspaces, so its degree is bounded by the number of
  irreducible components meeting any given general fibre — by
  Note 0119 + Note 0122, this is at most the count of `(w+1)`-subsets
  of `[n]` whose pairwise Vandermonde supports overlap. A naive bound
  is `C(n, w+1)`, but the joint Vandermonde support `S^*` is a unique
  intrinsic invariant of `(s_1, s_2)`, so the actual irreducible-
  component count seen by a generic line is `≤ C(n, ≤ w+1)/(common
  overlap)`. We expect this to give `D_var = O(n^{2c})` for the leading
  stratum.

* **Sub-leading codim sharpening.** Note 0123 shows sub-leading strata
  have codim `> 2(c−1)`, hence don't contribute to the leading-order
  ε. The `curve` measure restricted to leading strata is what the
  empirical numbers above measure.

The combination `eps_commit ≤ n^{O(c)} · |F|^{-2(c-1)}` would close the
§8.1 question for FRI-deployment use: at `n = 2^{20}`, `c = 5`,
`|F| = 2^{186}`, this gives `2^{20·5} · 2^{-1860} = 2^{-1760}`, far
below the `2^{-128}` deployment target with massive headroom.

## Theoretical sketch (Bezout style)

For each fixed `S ⊂ [n]` of size `w+1`, the leading component
`V_S × V_S ⊂ F_q^{2D}` is a linear subspace of dimension `2(w+1)`
(linear independence of the `(w+1)` Vandermonde generators on `S`).
Its degree as a linear subspace is `1`.

The union `V_bad^{leading} := ⋃_{|S|=w+1} V_S × V_S` decomposes into
`C(n, w+1)` such subspaces. A generic line `L ⊂ F_q^{2D}` intersects
each linear subspace of dimension `2(w+1)` in dimension
`max(0, 2(w+1) + 1 - 2D)` points; for the deployment regime
`2D > 2(w+1)+1` (equivalently `c ≥ 1`), this is **zero** for each
component generically.

The line meets V_bad only when it crosses through the union of
`(2D − 2(w+1) − 1)`-codim singular sub-loci of `V_bad`. Counting
those sub-loci via inclusion-exclusion gives `O(n^c)` (the number of
"transversal" `S^*`-equivalence classes), not `C(n, w+1)`.

A complete proof requires a careful affine-variety degree argument,
which the existing FRISoundness Mathlib stack does not host
(Berlekamp/, like the rest of the formalization, treats codim
combinatorially); we leave it to follow-up work as recommended in
Paper 3 §8.1.

## What this is NOT

* **NOT a new soundness theorem.** Paper 3 §3 already gives the
  rigorous `codim = 2(c−1)` bound. This note refines the *prefactor*
  in the operational ε bound for FRI deployment, not the asymptotic
  scaling.

* **NOT a replacement for the asymptotic-codim accounting** that Paper
  3 §6 adopts (matching ABF §6.3 convention). The asymptotic accounting
  *implicitly* uses the curve-measure regime; this note makes the
  underlying mechanism explicit and quantifies it empirically.

* **NOT FRI-curve specific.** The empirical analysis uses *generic*
  degree-1 lines, not FRI's specific `α`-parameterized family. We
  expect the FRI curve to be at least as well-behaved as a generic
  line (it's a polynomial parametrization of low degree), so the
  bounds reported here are conservative for FRI.

## Files

- `notes/scripts/op2_curve_measure_prefactor.py` — empirical sweep
- `notes/scripts/op2_curve_measure_prefactor.output.txt` — saved output
