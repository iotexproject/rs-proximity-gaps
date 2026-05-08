# Note 0390 -- Issue #419: abstract shape-template Groebner verifier

**Date:** 2026-05-02  
**Branch:** `main`  
**Status:** Note 0376 / 0389 "next concrete artifact"; abstract shape-level
symbolic certificate.  Random-sample pass: 20k (shape, S) Groebner runs,
**0 primitive candidates** under the corrected no-full filter.

---

## Why this note

Notes 0353 / 0365 (stable_coefs) and Note 0389 (random arbitrary coefs at
the panel level) provide overwhelming empirical evidence that the
finite-root primitive branch of #419 is empty.  Note 0376's "next
artifact" calls for an abstract shape-level Groebner certificate that
checks ALL coefficient choices simultaneously, per (sup, S) shape.

The existing `issue419_parity_implication_shape_cert.py` does this for the
39 unique (sup, S) shapes that appear under stable_coefs at the q=97 /
q=193 / q=1153 base panels.  This note builds the abstract extension:
enumerate ALL 4-supp shape representatives at L2 = (16, 4) (not just
those that appear at stable_coefs) and run the symbolic certificate per
(shape, no-full S) pair.

---

## Hunter

Script:

```text
notes/scripts/issue419_abstract_shape_template_verifier.py
```

For each (sup, S):

1. Build symbolic c_i (one per support position) and symbolic alpha.
2. Form u, v from quadrant decomposition (paper2 §2 substitution principle).
3. Compute high-tail equations `tails[e] @ u_alpha = 0` and
   `tails[e] @ v_alpha = 0` for tails of polynomial reduction modulo
   `g_S = prod_{s in S}(x - L2[s])`.
4. Saturate by `alpha != 0` and by all rank-2 minors of (u, v).
5. Classify the surviving Groebner ideal:
   - `rank<2`: ideal is unit; no rank-2 nonzero-alpha solution exists.
   - `parity-split`: ideal non-unit but parity_forbidden_factors == 0
     (u and v already on opposite parities by support structure), OR
     adding parity_forbidden_factors makes it unit.
   - `PRIMITIVE-CANDIDATE`: ideal non-unit AND mixed-parity branch
     survives.

A `PRIMITIVE-CANDIDATE` would be a real obstruction to Note 0355.

---

## Critical bug surfaced and fixed

The first version of the script used CONTIGUOUS-quadrant indexing for
the no-full filter ({0,1,2,3}, {4,5,6,7}, ...) instead of the standard
RESIDUE-MOD-4 cosets ({0,4,8,12}, {1,5,9,13}, ...).  The `occupancy(S)`
function (used everywhere else in the codebase) buckets by `i % 4`.  The
two conventions give the same COUNT of no-full subsets (10896 at L2 16,4)
but DIFFERENT subsets, by symmetry.

The buggy filter falsely admitted

```text
S = (0, 2, 3, 4, 6, 8, 10, 12)    # has 4 elements in coset i%4 == 0
```

as no-full.  The script then flagged this as a `PRIMITIVE-CANDIDATE` at

```text
support = (32, 37, 38, 43),
coefs   = (70, 1, 70, 1),
alpha1  = 1.
```

Inspection confirmed this S is FULL by the standard convention (4
elements in residue class 0 mod 4); excluded from the proper no-full
universe.  K(f) computation at this (sup, coefs) gave `K = 9409 / 97 = 97`,
which is the all-alpha ceiling — not a finite-root primitive at all.
The actual all-alpha witnesses are

```text
S_1 = (0, 2, 4, 6, 8, 10, 12, 14)    # all even indices, 8th roots of unity
S_2 = (1, 3, 5, 7, 9, 11, 13, 15)    # all odd indices, shifted 8th roots
```

both saturated for ALL alpha at the same coefs.  These are paired-tail
all-alpha (Note 0388) and excluded by the L1 lift Johnson-boundary
identity.

Bug fixed: the script now uses the standard `i % 4` coset convention.

---

## Sweep result (corrected filter)

```text
q=97, L2=(16,4), support_window=[16,64), 4-supp any quadrant pattern
unique 4-supp shapes (any quadrant pattern): 173328
shape representatives sampled: 200
S subsets per shape (random sample): 100
Total (shape, S) Groebner runs: 20,000

branch totals = {'rank<2': 20000}
primitive_candidates = 0
```

Every (shape, S) pair has the rank-2 nonzero-alpha branch EMPTY after
saturating by `alpha != 0` and rank-2 minors.  Stronger than parity-split:
even before requiring parity separation, no rank-2 nonzero-alpha solution
exists at all.

Random sampling missed the unique 4-supp parity-split catalog shape
(`((11,), (9,), (8,10), ())`, occurring at coverage ~5/173328) but the
verifier correctly classifies it on direct test:

```text
support=(34, 37, 42, 44), S=(1, 3, 5, 6, 7, 9, 11, 14)
=> branch=parity-split, parity_forbidden_factors=0
```

---

## Outputs

```text
notes/scripts/issue419_abstract_shape_template_verifier.py
notes/scripts/issue419_abstract_shape_template_verifier.q97.4supp.output.txt
```

---

## Combined empirical case after Note 0390

| Source | Trials | Primitives |
|---|---|---|
| Stable_coefs full panels (Notes 0353 / 0365) | 47.4M (q=97 4-supp) + 316M (q=193 5-supp) + 200M+ random 6/7/8-supp | 0 |
| Random arbitrary coefs (Note 0389) | 1.07M q=97 4-supp + 218k q=193 6-supp + 114k q=193 7-supp | 0 |
| Symbolic Groebner (this note) | 20k abstract (shape, S) at q=97 4-supp | 0 |

Three orthogonal probes — fixed-coefs panel scans, random-coefs panel
scans, and symbolic abstract shape Groebner — all return 0 primitives.
The empirical case for the Note 0355 finite-root primitive theorem is now
strong across all three quantifiers.

---

## What remains for a hand proof

The symbolic Groebner verifier is now ready for catalog extension:

1. Run the verifier in EXHAUSTIVE mode on all `~173k` unique 4-supp shapes
   at L2 = (16, 4); per shape, all 10896 no-full S.  Estimated runtime
   on the studio: ~1 day at 8 workers (rough at 10ms / Groebner).
2. Repeat at q=193 5-supp, q=1153 4-supp panels.
3. If 0 primitives across exhaustive enumeration, the structural identity
   "rank-2 + nonzero-alpha + no-full saturated => rank-collapse" is
   confirmed at the panel level.
4. Lift to a hand proof via the rank-of-tail-block argument from Note
   0376: rank-2 saturation factors out same-folded cancellation +
   rank-collapse minors, leaving only parity-separated solutions.

The bug surfaced in this note (no-full convention mismatch) is a useful
guard-rail against the related K-level danger from Note 0388 paired
tail circuits: any apparent "finite-root primitive" should be
cross-checked against the all-alpha kernel at every adjacent S to rule
out boundary phenomena.
