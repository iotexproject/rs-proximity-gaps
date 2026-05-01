# Note 0342 -- Issue #396: four-support no-full base certificate

> **Note number history**: filed as Note 0338 on the
> `issue-419-l3-attachment` branch; renumbered to 0342 on `main` to avoid
> collision with `0338-issue429-scale-lift-closure-review` already on the
> trunk. Cross-references to "Note 0336" / "Note 0337" / "Note 0335" inside
> the body point to the branch numbering and correspond on `main` to
> Notes 0340 / 0341 / 0337 respectively.

**Date:** 2026-05-01
**Branch:** `issue-396` (originated on `issue-419-l3-attachment`)
**Status:** finite multi-prime certificate for the first true multi-term
layer.

Artifacts:

- `notes/scripts/issue396_no_full_4support_cert.py`
- `notes/scripts/issue396_no_full_4support_cert.q97.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q193.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q257.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q449.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q577.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q769.output.txt`
- `notes/scripts/issue396_no_full_4support_cert.q1153.output.txt`

---

## Purpose

Note 0337 closes strict three-support rows because every mixed 3-support has
a singleton residual side.  The next genuine multi-term obstruction is a
four-support with two residual terms on each `alpha2` side:

```text
u-side count = 2,     v-side count = 2.
```

This note records a finite certificate for that first bilateral layer at the
base post-two-fold panel `L2=(16,4)`.

The result is not the full general-`f` proof.  Its value is that the first
place where Note 0337 no longer applies still shows the same collapse pattern
over seven primes.

---

## Certification method

For a fixed support and no-full `8`-subset `S subset L2`, saturation of both
residual row directions is linear in `alpha1`:

```text
C(S) + alpha1 M(S) = 0.
```

The script reuses the same no-full tail matrix as Notes 0327--0330, but
changes the support enumeration from `C(48,3)` to `C(48,4)`.

Only the real bilateral supports are tested for the new obstruction:

```text
support_side_counts = (2,2).
```

A candidate solution is accepted as dangerous only if:

1. `alpha1 != 0`;
2. the residual row span has rank `2`;
3. the row is not full-code; and
4. the row has no nontrivial cyclic stabilizer.

Thus all charged classes from Notes 0310--0312, 0335, and 0337 are excluded
before a counterexample is reported.

---

## Multi-prime panel

The scan was run over

```text
q in {97, 193, 257, 449, 577, 769, 1153}.
```

For every prime:

```text
support_window=[16,64)
supports=C(48,4)=194580
(2,2) supports=76176
first_counterexample=None
```

The summarized outcomes are:

```text
q=97:   alpha_zero=47463328, rank<2=336,   stabilizer=16
q=193:  alpha_zero=47463136, rank<2=160,   stabilizer=0
q=257:  alpha_zero=47463056, rank<2=96,    stabilizer=0
q=449:  alpha_zero=47463056, rank<2=48,    stabilizer=0
q=577:  alpha_zero=47463040, rank<2=32,    stabilizer=0
q=769:  alpha_zero=47463040, rank<2=10912, stabilizer=0
q=1153: alpha_zero=47463024, rank<2=16,    stabilizer=16
```

There are no all-`alpha1` no-full subsets in this panel:

```text
all_alpha_subsets=0
```

In particular, every no-full symbolic candidate for a bilateral 4-support is
charged to one of:

```text
alpha1=0 degeneration,
rank<2 collapse,
cyclic stabilizer.
```

No primitive rank-2 no-full component survives.

---

## Interpretation

This is the first check beyond the singleton-tail theorem.  The pattern says
that the Note 0336 defect-allocation obstruction is already active at the
smallest possible bilateral support size.

The important feature is not just that no counterexample appears.  The
candidate equations have many solutions before charging:

```text
candidate_subsets ~= 47.46M per prime.
```

Almost all are exactly the excluded `alpha1=0` zero-row family.  The
nonzero-`alpha1` survivors are rank deficient or stabilizer-controlled.  This
matches the desired proof shape:

```text
bilateral defect allocation
  => zero-row / rank-collapse / stabilizer
  => no primitive no-full component.
```

---

## Consequence for #396

After Notes 0335--0337 and this certificate, the remaining hard theorem is
not the strict 3-support branch and not the first `(2,2)` bilateral base
layer.

The next proof target is a scale/generalization of the observed collapse:

> For folded above-Johnson row spans with at least two residual terms on both
> `alpha2` sides, every no-full defect allocation from Note 0336 either
> forces `alpha1=0`, drops rank, has a nontrivial stabilizer/dyadic descent,
> or promotes to a complete-block/two-block/defect-root component.

Equivalently, the open part of #396 has moved from "does the first multi-term
case even behave?" to "prove the defect-allocation collapse uniformly for
higher bilateral supports and larger dyadic scales."
