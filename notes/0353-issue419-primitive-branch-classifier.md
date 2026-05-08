# Note 0353 -- Issue #419: primitive branch classifier after stabilizer closure

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** tooling checkpoint for the remaining primitive global attachment theorem.

---

## Purpose

Note 0352 separates the now-closed nontrivial half-turn stabilizer branch from
the still-open primitive global attachment branch.  This note adds a dedicated
classifier for that branch:

```text
notes/scripts/issue419_primitive_branch_classifier.py
```

It wraps the existing symbolic-alpha saturation system and reports every
candidate in one of the exact #419 buckets:

```text
alpha_zero,
rank<2,
full,
stabilizer,
primitive.
```

After Note 0351, `stabilizer` is no longer a suspicious bucket: it is charged
by row-span/eigenspace descent plus weighted quotient closure.  Therefore the
first `primitive` hit is the first real obstruction to the remaining global
attachment theorem.

---

## 4-support regression over `F_97`

Command:

```text
python3 notes/scripts/issue419_primitive_branch_classifier.py \
  --q 97 --support-size 4 --workers 12 --progress 0
```

Output summary:

```text
candidate_subsets = 47,463,680
alpha_zero        = 47,463,328
rank<2            = 336
stabilizer        = 16
first_primitive   = None
```

The histogram matches the earlier witness extractor exactly.  All nonzero
non-rank-collapse survivors are half-turn row-span stabilizer cases with
profile `0^3,1^2,2^3`, hence covered by Notes 0347--0351.

---

## 5-support regression over `F_193`

Command:

```text
python3 notes/scripts/issue419_primitive_branch_classifier.py \
  --q 193 --support-size 5 --workers 20 --chunksize 32 \
  --max-examples 2 --progress 250000
```

Output summary:

```text
candidate_subsets = 316,422,821
alpha_zero        = 316,422,482
rank<2            = 259
stabilizer        = 80
first_primitive   = None
```

The rank-collapse bucket has several half-turn fiber profiles:

```text
rank<2 profile 0^2,1^4,2^2 : 32
rank<2 profile 0^3,1^2,2^3 : 224
rank<2 profile 0^4,2^4     : 3
```

But the stabilizer bucket remains clean:

```text
stabilizer profile 0^3,1^2,2^3 : 80
```

Thus the branch closed by Notes 0347--0351 is exactly the only non-rank,
non-alpha-zero survivor seen in both 4-support and 5-support panels.

---

## Consequence

The current empirical implication is:

```text
no-full saturated candidate in tested bilateral panels
  => alpha1 = 0
     or rank(W) < 2
     or W has half-turn row-span stabilizer.
```

Since the half-turn stabilizer branch is now theorem-level closed, the tested
panels contain no uncharged primitive global-attachment survivor.

This is still not a proof of the full primitive theorem.  The next mathematical
step is to extract the structural reason that the classifier never reaches
`primitive`: a rank identity for the quotient-`C4` defect-allocation system
after removing the alpha-zero, rank-collapse, and stabilizer loci.

---

## Random larger-support stress

I added `--random-trials` to the classifier to probe larger support sizes
without committing to full `C(48,s)` enumeration.

Commands:

```text
for s in 6 7 8; do
  python3 notes/scripts/issue419_primitive_branch_classifier.py \
    --q 193 --support-size $s --random-trials 2000 \
    --workers 12 --chunksize 16 --max-examples 2 --progress 0 \
    --seed $((41953+s))
done
```

Outputs:

```text
s=6: candidate_subsets=196,128, alpha_zero=196,128, first_primitive=None
s=7: candidate_subsets=185,232, alpha_zero=185,232, first_primitive=None
s=8: candidate_subsets= 87,184, alpha_zero= 87,184, first_primitive=None
```

In this random larger-support stress, every saturated no-full candidate found
is already in the `alpha1=0` degeneration.  No rank-collapse or stabilizer
charging was even needed on these samples.

This suggests a sharper possible route for the primitive theorem: after
excluding the explicit small bilateral layers, the symbolic-alpha equations may
force `alpha1=0` generically.  If true, the primitive global attachment theorem
could be reduced to proving that the affine saturation equations have no
nonzero-alpha solution outside the known low-support stabilizer/rank-collapse
exceptions.

Additional `s=6` stress with 20,000 random supports over `F_193` also found only
`alpha1=0` candidates:

```text
s=6 random20000: candidate_subsets=1,983,104, alpha_zero=1,983,104,
                 first_primitive=None
```

This makes the nonzero-alpha locus look concentrated in the first two
bilateral layers (`s=4,5`), where it collapses to rank/stabilizer buckets.
