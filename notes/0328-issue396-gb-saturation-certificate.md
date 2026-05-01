# Note 0328 -- Issue #396: GB saturation certificate for the no-full branch

## Purpose

Note 0327 reduced the legal strict above-Johnson no-full branch to a sharper
algebraic emptiness statement.  For each fixed 3-support and no-full component
candidate `S`, the symbolic-alpha equations have the form

```text
C(S) + alpha1 M(S) = 0.
```

The desired rank-collapse certificate is that no point remains after removing
the two one-sided loci:

```text
u_alpha = 0,     v_alpha = 0.
```

This note runs that check directly in Singular over `F_193`.

## Singular formulation

For every nonzero-alpha symbolic no-full candidate in the legal panel, the
driver forms ideals

```text
I = <C(S) + alpha1 M(S)>,
U = <coefficients of u_alpha>,
V = <coefficients of v_alpha>.
```

It then asks Singular to compute

```text
sat(sat(sat(I, <alpha1>), U), V).
```

The first saturation quotients the `alpha1=0` branch; the second and third
saturations remove the two one-sided rank-collapse loci.  The branch is empty
exactly when the resulting ideal is `<1>`, equivalently `dim = -1`.

The alpha-zero family is quotiented out before the GB pass.  This matches the
next-step prescription in Note 0327 and prevents the 22M zero-row candidates
from being sent to Singular.

## Run

Command:

```bash
python3 notes/scripts/issue396_no_full_saturation_cert.py \
  --q 193 --support-count 48 --chunk-size 256 \
  > notes/scripts/issue396_no_full_saturation_cert.q193.output.txt
```

Panel:

```text
q=193, L2=(16,4), support_window=[16,64), skip_alpha_zero=True
supports=17296
candidate_subsets=22055749
skipped_alpha_zero=22053568
saturation_cases=2181
all_alpha_subsets=0
```

The 2181 saturation cases are the nonzero-alpha remainder after quotienting
away `alpha1=0`.  The difference from the 2245 one-sided rows in Note 0327 is
that 64 one-sided rows also lie on `alpha1=0`, so they are removed by the same
quotient step.

Singular transcript:

```text
chunk 1: cases=256, returncode=0, good=256, bad=0
chunk 2: cases=256, returncode=0, good=256, bad=0
chunk 3: cases=256, returncode=0, good=256, bad=0
chunk 4: cases=256, returncode=0, good=256, bad=0
chunk 5: cases=256, returncode=0, good=256, bad=0
chunk 6: cases=256, returncode=0, good=256, bad=0
chunk 7: cases=256, returncode=0, good=256, bad=0
chunk 8: cases=256, returncode=0, good=256, bad=0
chunk 9: cases=133, returncode=0, good=133, bad=0

total_good=2181
total_bad=0
```

## Consequence

Over `F_193`, the legal `C(48,3)` no-full branch has the following certified
decomposition:

1. `alpha1=0` quotient removes 22,053,568 candidate rows.
2. The remaining 2181 nonzero-alpha no-full candidates have
   `sat(sat(I,U),V)=<1>`.
3. Therefore no residual point survives with both `u_alpha != 0` and
   `v_alpha != 0`.

This is the requested direct GB check for the q=193 legal panel.  Combined
with Notes 0326--0327, it upgrades the computational statement from "all
observed candidates are rank<2" to an explicit ideal-theoretic emptiness
certificate after quotienting the zero-row branch and saturating away the
one-sided rank-collapse loci.

## Remaining proof work

This does not yet close the paper-level theorem by itself.  The remaining
tasks are:

1. Repeat the same saturation transcript across the multi-prime panel
   `{97,193,257,449,577,769,1153}`.  This is completed in Note 0329.
2. Extract a prime-uniform symbolic reason for the unit ideal across the
   finite support/occupancy buckets, or cite the finite GB certificate only as
   machine evidence.
3. Route the one-sided loci through the dyadic descent lemma from Note 0325.
