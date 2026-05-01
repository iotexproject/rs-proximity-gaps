# Note 0331 -- Issue #396: monomial-tail obstruction for mixed supports

## Purpose

Note 0330 found that every no-full symbolic-alpha branch surviving the
`alpha1=0` quotient is side-pure.  This note isolates the simpler obstruction
behind that observation.

For a mixed 3-support, one `alpha2` side has exactly one monomial and the
other side has two.  Therefore a mixed no-full branch can exist only if the
singleton monomial lies in `RS_4(S)` on the no-full component `S`.

For `L2=(16,4)` and the legal strict above-Johnson support window
`j in [16,64)`, the folded exponents are

```text
e = floor(j/4) in {4,...,15}.
```

So the required singleton condition is exactly

```text
tail_S(x^e) = 0
```

for some no-full `S` and some `e in {4,...,15}`.

## Result

The script

```text
notes/scripts/issue396_no_full_monomial_tail_obstruction.py
```

checks all no-full `8`-subsets `S` of `L2` and all exponents `4 <= e < 16`.
Across the seven-prime panel, no bad pair appears:

| q | no-full subsets | full-block subsets | first bad |
|---:|---:|---:|---|
| 97 | 10,896 | 1,974 | none |
| 193 | 10,896 | 1,974 | none |
| 257 | 10,896 | 1,974 | none |
| 449 | 10,896 | 1,974 | none |
| 577 | 10,896 | 1,974 | none |
| 769 | 10,896 | 1,974 | none |
| 1153 | 10,896 | 1,974 | none |

The transcript is saved at
`notes/scripts/issue396_no_full_monomial_tail_obstruction.multiprime.output.txt`.

## Consequence

This gives a coefficient-free explanation of the mixed-support exclusion:

```text
mixed 3-support
  => one residual side is a singleton monomial c x^e, 4 <= e < 16
  => no-full S would require tail_S(x^e)=0
  => impossible on every no-full S in the seven-prime panel.
```

Thus every no-full branch after the `alpha1=0` quotient must be side-pure.
Then one residual side is identically zero, so the branch is rank-one and
cannot be a primitive rank-2 obstruction.

## Proof target

The remaining paper-level step is now a clean finite lemma:

```text
Let L be a cyclic group of order 16 and S subset L have size 8 with no full
quarter block.  For every 4 <= e < 16, x^e restricted to S is not the
restriction of any polynomial of degree < 4.
```

Equivalently, if `g_S(x)=prod_{s in S}(x-s)`, then for no-full `S`,
`g_S` never divides `x^e - p_3(x)` with `deg p_3 < 4` and `4 <= e < 16`.

This is a plausible direct combinatorial/cyclotomic lemma and is much smaller
than the original Niho/Bluher-scale question.
