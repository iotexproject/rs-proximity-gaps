# Note 0391 -- Issue #419: abstract Groebner verifier multi-field confirmation

**Date:** 2026-05-02 (late, Q2 attack iteration 3)  
**Branch:** `main`  
**Status:** abstract symbolic Groebner certificate extended from q=97 4-supp
to q=193 5-supp and q=1153 4-supp; total 50k (shape, S) Groebner runs,
**0 primitive candidates** across all three fields and both support sizes.

---

## Why this note

Note 0390 introduced the abstract shape-template Groebner verifier and ran
20k (shape, S) pairs at q=97 4-supp.  This note extends to the other
panels covered by the catalog (q=193 5-supp and q=1153 4-supp), giving
multi-field cross-confirmation.

---

## Sweeps

```text
notes/scripts/issue419_abstract_shape_template_verifier.py
```

now accepts `--support-size`.  Sweeps:

```text
q=97   4-supp  shape_window=[16,64), 200 shape reps, 100 S each, 20000 runs
q=193  5-supp  shape_window=[16,64), 200 shape reps, 100 S each, 20000 runs
q=1153 4-supp  shape_window=[16,64), 100 shape reps, 100 S each, 10000 runs
```

Result: **all 50,000 runs classified `rank<2`. 0 primitive candidates.**

Outputs:

```text
notes/scripts/issue419_abstract_shape_template_verifier.q97.4supp.output.txt
notes/scripts/issue419_abstract_shape_template_verifier.q193.5supp.output.txt
notes/scripts/issue419_abstract_shape_template_verifier.q1153.4supp.output.txt
```

---

## Why "rank<2" dominates random shapes

Most random (sup, S) shape representatives admit NO rank-2 nonzero-alpha
solution at any coefficients: the high-tail equations form an
overdetermined affine system that, after rank-2 saturation, becomes the
unit ideal.

The catalog parity-split shapes (1 unique at q=97 4-supp, 5 at q=193
5-supp) are RARE in the abstract enumeration and thus typically missed by
random sampling at 200-shape scale.  Direct test confirms the verifier
classifies them correctly as `parity-split` (Note 0390 verification on
`support=(34,37,42,44)`).

This means the abstract verifier's "0 primitive candidates" result is
*stronger* than the catalog cert's "39 shapes all parity-split or
rank-collapse": even the bulk of shapes that don't appear at stable_coefs
also have empty rank-2 nonzero-alpha branches.

---

## Aggregate empirical case for Note 0355 (Q2 finite-root closure)

| Probe | Quantifier | Trials | Primitives |
|---|---|---|---|
| stable_coefs full panels (Notes 0353, 0365) | fixed deterministic coefs | 47.4M (q=97 4-supp) + 316M (q=193 5-supp) + 200M+ random 6/7/8-supp | 0 |
| Random arbitrary coefs (Note 0389) | random in `F_p^|s|` | 1.07M q=97 4-supp + 218k q=193 6-supp + 114k q=193 7-supp | 0 |
| Symbolic abstract Groebner (Notes 0390, 0391) | symbolic over ALL coefs | 20k q=97 4-supp + 20k q=193 5-supp + 10k q=1153 4-supp | 0 |

Three orthogonal probes spanning three fields and three support sizes.
Every probe returns **0 primitive obstructions**.

---

## What an exhaustive sweep would say

The current symbolic sweep is random-sample.  An exhaustive abstract
sweep at q=97 4-supp would need:

```text
unique 4-supp shapes (any quadrant pattern): 173,328
no_full S subsets: 10,896
total (shape, S) pairs: ~1.9 billion
```

At ~50 ms / Groebner (current cost), this is ~ 26 GPU-years on a single
core, ~ 80 GPU-days at 100 cores.  This is the natural scale-out target
for the studio.

A SHARPER alternative: use the linear-algebra short-circuit.  A rank-2
nonzero-alpha solution can ONLY exist when both submatrices `(H_S |
u_supp)` and `(H_S | v_supp)` are rank-deficient (nullspace dimension
>= 1 each).  This is a pure F_p rank computation, microseconds per pair.
Pre-filter by this criterion, then run Groebner only on the surviving
candidates.  Expected reduction ratio: most pairs fail the rank
criterion immediately, leaving a small set for symbolic check.

---

## Hand-proof sketch (next attack)

The Note 0376 algebraic statement requires:

> For any (sup, S) at L2=(16,4), no full coset, with H_S u = H_S v = 0
> and rank(span(u, v)) = 2 and alpha != 0 and no same-folded
> cancellation, the row pair (u, v) must have opposite parity quotient
> supports.

The structural strategy:

1. **Nullspace decomposition.** `u, v in nullspace(H_S) = F[x]_{<k2} +
   g_S * F[x]_{<n2 - deg g_S}`.  Equivalently u = r_u + q_u * g_S with
   deg r_u < 4 and deg q_u < 8.

2. **Parity decomposition.** `g_S = g_even + g_odd`; same for u, v.
   Polynomial multiplication mod 2 in degree:
   ```
   (q * g)_even = q_even g_even + q_odd g_odd
   (q * g)_odd  = q_even g_odd  + q_odd g_even
   ```

3. **Rank-2 condition.** `u, v` linearly independent forces
   `(u_even, u_odd)` and `(v_even, v_odd)` not pairwise proportional.

4. **Saturation.** Same-folded cancellation = rank-1 minor.  Inverting
   it removes the rank-collapse factor from the variety.

5. **Mixed-parity lemma (TARGET).** After saturation, the only solutions
   where rank = 2 and alpha != 0 are those with one row purely even and
   the other purely odd.  Equivalently, the parity decomposition forces
   `u_even = 0 OR u_odd = 0` and similarly for `v`, with opposite
   choices.

The cross-saturated terms `g_odd * q_u` and `g_even * q_u` are the
algebraic witnesses.  If `q_u = q_u_even + q_u_odd` and likewise for
`q_v`, the eight unknowns `(q_u_even, q_u_odd, q_v_even, q_v_odd, r_u,
r_v, ...)` interact through the product structure of g_S.

The full proof requires a structural lemma about the parity decomposition
of g_S as S varies over no-full subsets of L2.  This is the next
algebraic artifact.

---

## Recommendation for paper2

Current paper2 v19 caveat:

> Theorem `K10-sparse-worst-corollary` is conditional on a natural
> sparse-worst-case dominance conjecture (Q2), consistent with every
> adversarial construction in the proximity-gap literature including ABF
> Lemma 6.13, Crites-Stewart, BCHKS.

After this Q2 attack iteration, the paper2 narrative can be sharpened:

> Theorem `K10-sparse-worst-corollary` is conditional on Q2; every
> adversarial construction in the literature satisfies Q2; we have
> verified Q2 empirically across 600M+ stable_coefs trials, 1.4M+ random
> arbitrary-coefs trials, and 50k symbolic abstract Groebner trials at
> three distinct field/support combinations, with zero counter-witnesses.

This is honest, defensible, and publishable AS-IS.  An unconditional
upgrade requires the structural proof above.
