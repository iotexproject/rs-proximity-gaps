# Note 0326 -- Issue #396: symbolic-alpha primitive no-full certification

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** multi-prime and larger-panel evidence for the corrected primitive
rank-2 theorem.

Artifacts:

- `notes/scripts/issue396_no_full_symbolic_cert.py`
- output: `notes/scripts/issue396_no_full_symbolic_cert.multiprime.output.txt`
- output: `notes/scripts/issue396_no_full_symbolic_cert.support64.q193.output.txt`

---

## Upgrade over Note 0325

Note 0325 used brute-force `alpha1` enumeration to show that the
`(64,16)->L2=(16,4)` strict above-Johnson `C(48,3)` panel has no primitive
rank-2 no-full-block component over `F_193`.

This note replaces the enumeration with a symbolic-alpha certificate.

For a fixed 3-support and an 8-subset `S` of `L2`, write

```text
u_alpha = u0 + alpha1 u1,     v_alpha = v0 + alpha1 v1.
```

The condition that both residual basis vectors interpolate on `S` is

```text
tail_S(u0) + alpha1 tail_S(u1) = 0,
tail_S(v0) + alpha1 tail_S(v1) = 0.
```

Thus every no-full component candidate solves one vector linear equation

```text
C(S) + alpha1 M(S) = 0.
```

The script solves this equation directly for each no-full `S` and then
classifies the resulting row as:

- `rank<2`;
- `full`;
- `stabilizer` (rank 2 but nontrivial dyadic stabilizer);
- `primitive` (rank 2, non-full, trivial dyadic stabilizer).

Only the last class is a primitive obstruction to the corrected theorem.

---

## Multi-prime legal panel

Panel:

```text
L2=(16,4), support_window=[16,64), supports=C(48,3)=17296.
```

Primes:

```text
q in {97, 193, 257, 449, 577, 769, 1153}.
```

Result:

| q | supports | candidate no-full equations | rank<2 | stabilizer | primitive |
|---:|---:|---:|---:|---:|---:|
| 97 | 17296 | 22056250 | 22056250 | 0 | 0 |
| 193 | 17296 | 22055749 | 22055749 | 0 | 0 |
| 257 | 17296 | 22055799 | 22055799 | 0 | 0 |
| 449 | 17296 | 22055949 | 22055949 | 0 | 0 |
| 577 | 17296 | 22055630 | 22055630 | 0 | 0 |
| 769 | 17296 | 22055639 | 22055639 | 0 | 0 |
| 1153 | 17296 | 22055609 | 22055609 | 0 | 0 |

Across all seven primes, every no-full symbolic-alpha candidate in the legal
`C(48,3)` panel is rank `<2`.  There are no stabilized rank-2 candidates and
no primitive rank-2 candidates.

This is materially stronger than the previous `F_193` brute-force sweep:
the exclusion is prime-uniform on the tested set and the mechanism is not
"rank-2 but hidden"; it is pure rank collapse in this panel.

---

## Larger support-window stress test

To probe small-window artifacts, the same `L2=(16,4)` certifier was run on

```text
support_window=[16,80), supports=C(64,3)=41664, q=193.
```

Result:

```text
hist={
  all_alpha_subsets: 6101792,
  candidate_subsets: 105753397,
  class:full: 3138048,
  class:rank<2: 102607157,
  class:stabilizer: 8192,
  supports: 41664
}
first_counterexample=None
```

There are still no primitive rank-2 no-full components.  The enlarged window
does produce rank-2 no-full candidates, but every such rank-2 candidate has a
nontrivial dyadic stabilizer.

One representative is:

```text
support=(32,41,70), alpha1=13,
S=(0,1,2,4,6,8,9,10), occupancy=(3,2,3,0).
```

Audit:

```text
u = 142 x^8 + 73 x^10,
v = 108 x,
stabilizer_exponents = (0,8).
```

So `mu=-1` preserves the pencil: `u` is even and `v` is odd.  This is exactly
the recursive dyadic/stabilizer descent bucket from Note 0325, not a primitive
counterexample.

Interpretation caveat: `[16,80)` is a stress window on the same `L2=(16,4)`
folded model, not a literal `(64,16)` parent support set.  It is useful because
it intentionally probes folded aliasing beyond the legal `j<64` panel; the
only new behavior it finds is stabilized descent.

---

## Current theorem target

The empirical target is now sharper:

> In the legal strict above-Johnson 3-support panel, every no-full saturated
> component candidate forces rank collapse.  In larger folded stress panels,
> every rank-2 no-full candidate found so far has nontrivial dyadic stabilizer.

The proof target should therefore be:

> If a strict above-Johnson 3-support row admits a no-full saturated component,
> then the residual pencil either has rank `<2` or has nontrivial dyadic
> stabilizer.  Consequently, trivial-stabilizer rank-2 rows have no no-full
> saturated component.

This is a better hard target than the naive Note 0324 statement.  It also
matches the recursive proof stack:

1. `rank<2` is routed to the rank-1 lift/descent machinery.
2. nontrivial stabilizer is routed to dyadic quotient descent.
3. primitive rank-2 rows have no no-full components.
4. complete-block components are handled by Notes 0321--0323.

---

## Next algebraic route

The symbolic-alpha formulation gives the natural ideal for a proof or GB
check:

```text
C(S) + alpha M(S) = 0,
rank2 minors nonzero,
stabilizer minors nonzero,
no-full occupancy constraints.
```

The multi-prime table says this ideal should be empty on the legal
`C(48,3)` stratum after saturating away rank collapse.  For the larger stress
panel, the same ideal becomes empty only after also saturating away the
nontrivial stabilizer locus.
