# Note 0330 -- Issue #396: side-purity mechanism behind the no-full branch

## Purpose

Notes 0328--0329 certify by GB saturation that the legal no-full branch has no
rank-2 survivor after quotienting `alpha1=0`.  This note audits the structural
reason for that certificate.

The key question is whether a no-full symbolic-alpha survivor can have mixed
support across the two `alpha2` sides:

```text
u-side: j mod 4 in {0,1},
v-side: j mod 4 in {2,3}.
```

If a 3-support lies entirely on the u-side, then `v_alpha` is identically
zero.  If it lies entirely on the v-side, then `u_alpha` is identically zero.
Either case is rank-one before any GB saturation.  A genuine rank-2 no-full
obstruction would therefore need mixed side support.

## Run

Command:

```bash
python3 notes/scripts/issue396_no_full_side_purity_audit.py --top 12 \
  > notes/scripts/issue396_no_full_side_purity_audit.multiprime.output.txt
```

The script reuses the symbolic-alpha equations but does not call Singular.  It
keeps exactly the branches that remain after the `alpha1=0` quotient, including
all-alpha rows when present, and records whether their supports are side-pure.

## Results

| q | cases after alpha-zero quotient | u-side only `(3,0)` | v-side only `(0,3)` | first mixed |
|---:|---:|---:|---:|---|
| 97 | 2,698 | 1,243 | 1,455 | none |
| 193 | 2,181 | 1,088 | 1,093 | none |
| 257 | 2,231 | 1,063 | 1,168 | none |
| 449 | 2,413 | 1,346 | 1,067 | none |
| 577 | 2,126 | 1,049 | 1,077 | none |
| 769 | 2,119 | 1,060 | 1,059 | none |
| 1153 | 2,105 | 1,047 | 1,058 | none |

Across all seven primes, every remaining no-full symbolic-alpha branch is
side-pure.  No mixed-support branch survives the no-full equations.

## Consequence

This explains the GB saturation certificate:

```text
no-full equations + alpha1 != 0
  => support is side-pure
  => u_alpha = 0 or v_alpha = 0
  => no rank-2 no-full branch.
```

Thus the paper-level proof target is now more combinatorial and much narrower:

```text
legal strict above-J 3-support with mixed alpha2-side support
  cannot satisfy the no-full symbolic-alpha equations.
```

The saturated-unit computations in Notes 0328--0329 are now best viewed as
certificates of this side-purity obstruction.  The remaining hard step is to
prove the mixed-side impossibility directly from the RS4 tail equations, likely
by a finite occupancy/quadrant argument rather than by another prime sweep.
