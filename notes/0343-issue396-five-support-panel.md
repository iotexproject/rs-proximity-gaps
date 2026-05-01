# Note 0343 -- Issue #396: five-support bilateral panel at q=193

> **Note number history**: filed as Note 0339 on the
> `issue-419-l3-attachment` branch; renumbered to 0343 on `main` to avoid
> collision with `0339-issue416-420-l1-status-wording` already on the trunk.
> Cross-references to "Note 0338" / "Note 0336" point to the branch
> numbering and correspond on `main` to Notes 0342 / 0340 respectively.

**Date:** 2026-05-01
**Branch:** `issue-396` (originated on `issue-419-l3-attachment`)
**Status:** larger-support finite panel after Note 0342 (formerly 0338).

Artifacts:

- `notes/scripts/issue396_no_full_4support_cert.py`
- `notes/scripts/issue396_no_full_5support_cert.q193.output.txt`

---

## Purpose

Note 0338 certified the first true bilateral layer: four-supports with side
counts `(2,2)` in the base `L2=(16,4)` panel.  The natural next question is
whether this collapse is a tiny-support artifact.

This note records the next panel:

```text
support size = 5,
side_min = 2,
allowed side counts = (2,3) and (3,2).
```

The certifier is the same symbolic-alpha no-full system

```text
C(S) + alpha1 M(S) = 0,
```

followed by the same charging filters:

```text
alpha1=0, rank<2, full-code, cyclic stabilizer.
```

---

## q=193 full support-window scan

Parameters:

```text
q=193
L2=(16,4)
support_window=[16,64)
supports=C(48,5)=1712304
side_min=2
workers=20
```

Support-side distribution:

```text
side:(0,5) = 42504
side:(1,4) = 255024
side:(2,3) = 558624
side:(3,2) = 558624
side:(4,1) = 255024
side:(5,0) = 42504
```

Thus the true bilateral multi-term support count tested is

```text
558624 + 558624 = 1117248.
```

Outcome:

```text
candidate_subsets = 316422821
alpha_zero        = 316422482
rank<2            = 259
stabilizer        = 80
all_alpha_subsets = 0
first_counterexample = None
```

No primitive rank-2 no-full component survives.

---

## Interpretation

This is substantially larger than the Note 0338 four-support panel:

```text
4-support candidates at q=193:   47.46M
5-support candidates at q=193:  316.42M
```

The same charging pattern persists:

```text
no-full symbolic solutions
  -> alpha1=0 degeneration
  -> rank collapse
  -> stabilizer bucket
```

There is no evidence that adding one more residual term creates an
unstructured no-full component at the base scale.

---

## Consequence for #396

The remaining defect-allocation theorem from Note 0336 is now supported by
two consecutive bilateral layers:

```text
4-support (2,2): seven-prime panel, no primitive survivor.
5-support (2,3)/(3,2): q=193 full-window panel, no primitive survivor.
```

This still is not a proof of the general-`f` theorem, but it rules out the
most immediate small-support escape hatch.  The next mathematical target is
to turn the observed collapse into a rank identity for the quotient-`C4`
local maps, rather than continuing support-size enumeration indefinitely.
