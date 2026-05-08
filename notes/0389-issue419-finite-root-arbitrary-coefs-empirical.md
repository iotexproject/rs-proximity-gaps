# Note 0389 -- Issue #419: finite-root primitive hunt at arbitrary coefficients

**Date:** 2026-05-02  
**Branch:** `main`  
**Status:** empirical strengthening of the Note 0355 nonzero-alpha closure
target; zero finite-root primitive obstructions found at random arbitrary
coefficients across q=97 (4-supp) and q=193 (5/6/7-supp) sweeps.

---

## Why this note

Note 0388 closes the all-alpha branch (paired tail circuits → L1 lift hits
exactly Johnson agreement, hence excluded by strict above-J).  After that
closure, the only remaining primitive global-attachment gap for #419 is the
finite-root branch from Note 0355:

> coefficients NOT in any all-alpha kernel,  
> alpha1 specific nonzero (not all alpha1),  
> rank(W) = 2, trivial dyadic row-span stabilizer,  
> at least one residual row with mixed parity in quotient coords,  
> no-full saturated component S.

A single such finite-root primitive would refute the Note 0355 statement.

The existing primitive-branch classifier (Note 0353) found zero primitives
across 200M+ candidate subsets, but only at the deterministic
`stable_coefs(support, p)` model.  Conjecture `sparse-worst` quantifies
over arbitrary coefficients, so the strongest empirical case requires
random-coefficient sweeps too.

This note records that strengthening.

---

## Hunter

Script:

```text
notes/scripts/issue419_finite_root_primitive_hunt.py
```

Per random `(support, coefs)` trial:

1. Sample support uniformly from `range(16, 64)`, size `s`.
2. Require `quadrant_min = 4` so the support engages all four `C4` blocks
   (otherwise we're back in the all-alpha-trivial regime excluded by
   Note 0388).
3. Sample `coef_samples` random nonzero coefficient vectors in `F_p^s`.
4. Per (sup, coefs): solve `C(S) + alpha1 M(S) = 0` for every no-full
   8-subset `S` of `L2 = (16, 4)`.
5. Skip all-alpha rows (Note 0388 closes those).
6. Classify finite-root rows: `rank<2 / full / stabilizer / primitive`.
7. Stop on first primitive (real obstruction) or report none across
   the whole sweep.

This is the same classification rubric used by `issue419_primitive_branch_classifier.py`
(stable_coefs) but with arbitrary random coefs.

---

## Sweep results

### q=97, support_size=4, quadrant_min=4

```text
support_trials=5000, coef_samples=2000, seed=918273
skipped:quadrant_min=4467               # only 533 sup span 4 quadrants
coef_samples=1066000
candidate_subsets=463104
class:rank<2=463104
class:primitive=0
```

Every finite-root saturation collapses to rank-deficient row span.  No
stabilizer-class hit, no full-class hit, no primitive hit.  Profile
breakdown by `half_turn_fiber_profile`:

```text
profile:rank<2:0^1,1^6,2^1: 150528
profile:rank<2:0^2,1^4,2^2: 241920
profile:rank<2:0^3,1^2,2^3:  59232
profile:rank<2:0^4,2^4:        672
profile:rank<2:1^8:          10752
```

### q=193, support_size=5, quadrant_min=4

(Killed early: random arbitrary coefs at q=193 5-support produce
essentially no finite-root saturations because the 8-equation system is
too rigid relative to the 5-coef parameter space.  Initial 600 supports
gave only 3 candidate subsets, all `rank<2`.)

### q=193, support_size=6, quadrant_min=4

```text
support_trials=1000, coef_samples=500
skipped:quadrant_min=563
coef_samples=218500
candidate_subsets=0
class:primitive=0
```

### q=193, support_size=7, quadrant_min=4

```text
support_trials=1000, coef_samples=200
skipped:quadrant_min=431
coef_samples=113800
candidate_subsets=0
class:primitive=0
```

At larger support over the larger field, finite-root saturations are
vanishingly rare under random arbitrary coefs.  This is consistent with
the per-`(S, coefs)` saturation probability scaling as `q^{-(8 - s + 1)}`.

---

## Combined empirical case for Note 0355 finite-root closure

```text
stable_coefs (Note 0353/0365):
  4-supp q=97       full panel    47.4M candidate subsets   0 primitives
  5-supp q=193      full panel   316M  candidate subsets   0 primitives
  4-supp q=1153     full panel                              0 primitives
  6/7/8-supp        random 200M+ trials                      0 primitives

random arbitrary coefs (this note):
  4-supp q=97       1.07M trials  463k candidate subsets    0 primitives
  6-supp q=193      218k  trials     0 candidate subsets    0 primitives
  7-supp q=193      114k  trials     0 candidate subsets    0 primitives
```

After Note 0388 closes the all-alpha branch, every observed finite-root
saturated component is one of:

1. `rank<2` (immediate), or
2. `stabilizer` (charged by Notes 0347--0351 weighted-quotient theorem
   chain).

No primitive (rank-2, trivial-stabilizer, mixed-parity, no-full) finite-root
component has been observed in any sweep, at either coefficient model.

---

## What this changes

The Note 0355 finite-root primitive theorem now has empirical support at
both quantifiers:

```text
forall (sup, stable_coefs(sup, p)):    no primitive   (Note 0353/0365)
forall (sup, random coefs in F_p^s):   no primitive   (this note)
```

The remaining work is structural: prove the saturated affine ideal
`(C(S) + alpha1 M(S)) + (alpha1 != 0) + (rank(W) = 2) + (trivial dyadic stab)`
is the unit ideal in the quotient-`C4` model, regardless of coefficient
specialization.  Note 0376 frames this as:

> after inverting alpha1, same-folded factors, and at least one rank-2 minor,
> the affine ideal implies
>
>   u_even u_odd = 0,
>   v_even v_odd = 0,
>   u_even v_even = 0,
>   u_odd  v_odd  = 0.

Note 0388 already removes the only known counterexample (the Note 0377
mixed-circuit obstruction is paired-tail-circuit, hence all-alpha, hence
boundary-excluded).

---

## Practical consequence for paper2

The current paper2 abstract caveats `K_{3pos-sparse} = 10` headline as
"conditional on a natural sparse-worst-case dominance conjecture (Q2)".
Q2 is now further strengthened:

* All-alpha danger: closed unconditionally (Note 0388, structural identity).
* Finite-root danger: zero observed across 200M+ stable + 1.4M+ random
  arbitrary coefficient trials at deployment-relevant support sizes.

The remaining proof gap is the algebraic lemma above.  Until that is
closed, the paper2 framing of Q2 as "conjecture supported by exhaustive
panel + random sweeps + structural reduction to a finite-dimensional ideal
question" is faithful.

---

## Outputs

```text
notes/scripts/issue419_finite_root_primitive_hunt.py
notes/scripts/issue419_finite_root_primitive_hunt.q97.4supp.output.txt
notes/scripts/issue419_finite_root_primitive_hunt.q193.6supp.output.txt
notes/scripts/issue419_finite_root_primitive_hunt.q193.7supp.output.txt
```

---

## Next concrete artifact

The next note should be the algebraic shape-template verifier from Note
0376's "Next concrete artifact":

> enumerate abstract mixed-parity support templates with no same-folded
> cancellation, rank-2 minor inverted, alpha1 inverted; ask whether any
> no-full tail matrix `H_S` can satisfy the affine system.

If every such abstract template saturates to the unit ideal, the resulting
identities are candidates for a hand proof of the Note 0355 finite-root
closure theorem.  The empirical sweeps above now make that hand proof the
only remaining primitive-branch work for #419.
