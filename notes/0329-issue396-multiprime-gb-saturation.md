# Note 0329 -- Issue #396: multi-prime GB saturation panel

## Purpose

Note 0328 gave the direct Singular saturation certificate over `F_193`.
This note repeats the same certificate across the seven-prime panel from
Note 0326:

```text
q in {97, 193, 257, 449, 577, 769, 1153}.
```

The check is stronger than the rank-class audit: after quotienting
`alpha1=0`, it explicitly computes

```text
sat(sat(sat(I, <alpha1>), U), V)
```

and requires the result to be `<1>` for every remaining no-full branch.

## Command

```bash
for q in 97 193 257 449 577 769 1153; do
  python3 notes/scripts/issue396_no_full_saturation_cert.py \
    --q "$q" --support-count 48 --chunk-size 256
done
```

The full transcript is saved at
`notes/scripts/issue396_no_full_saturation_cert.multiprime.output.txt`.

## Results

| q | candidate subsets | alpha-zero skipped | all-alpha cases | saturation cases | good | bad |
|---:|---:|---:|---:|---:|---:|---:|
| 97 | 22,056,250 | 22,053,568 | 16 | 2,698 | 2,698 | 0 |
| 193 | 22,055,749 | 22,053,568 | 0 | 2,181 | 2,181 | 0 |
| 257 | 22,055,799 | 22,053,568 | 0 | 2,231 | 2,231 | 0 |
| 449 | 22,055,949 | 22,053,536 | 0 | 2,413 | 2,413 | 0 |
| 577 | 22,055,630 | 22,053,504 | 0 | 2,126 | 2,126 | 0 |
| 769 | 22,055,639 | 22,053,520 | 0 | 2,119 | 2,119 | 0 |
| 1153 | 22,055,609 | 22,053,504 | 0 | 2,105 | 2,105 | 0 |

The `q=97` panel has 16 all-alpha no-full equations.  These are not
counterexamples: they are included as `I=<0>` cases, then quotiented by
`alpha1=0` and saturated by `U` and `V`; Singular still returns `<1>`.

## Consequence

Across all seven primes, the legal no-full symbolic-alpha branch has no point
remaining after the zero-alpha quotient and the two one-sided saturations.
Thus the rank-collapse pattern from Notes 0326--0328 is prime-stable at the
level of ideal-theoretic saturation, not only at the level of row
classification.

For paper deployment this is still computational evidence, not a closed-form
proof.  The proof target is now very narrow:

```text
legal strict above-J 3-support no-full equations
  => alpha1=0 or u_alpha=0 or v_alpha=0.
```

The remaining hard step is to replace the seven-prime unit-ideal transcript by
a prime-uniform symbolic identity or a finite bucket proof that explains why
the same saturation is unit.
