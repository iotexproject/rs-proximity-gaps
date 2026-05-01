# Note 0332 -- Issue #396: exact cyclotomic proof certificate for the tail lemma

## Purpose

Note 0331 reduced the mixed-support obstruction to a finite monomial-tail
claim on the 16-th roots:

```text
no-full S, |S|=8  =>  tail_S(x^e) != 0 for every 4 <= e < 16.
```

This note removes the finite-field dependence.  The new certificate works
exactly over

```text
Z[zeta_16] = Z[t] / (t^8 + 1).
```

## Determinantal reduction

Let `S` be an 8-subset of the 16-th roots.  If `x^e` restricts to a polynomial
of degree `<4` on `S`, then for every five-subset `T={x_1,...,x_5} subset S`
the five columns with exponents `{0,1,2,3,e}` are linearly dependent:

```text
det(x_i^a)_{a in {0,1,2,3,e}, i=1..5} = 0.
```

For distinct roots this determinant factors as

```text
Vandermonde(T) * h_{e-4}(T),
```

where `h_m` is the complete homogeneous symmetric polynomial of degree `m`.
Since `Vandermonde(T) != 0`, the necessary condition is exactly

```text
h_{e-4}(T) = 0 for every five-subset T subset S.
```

Conversely, if all five-subsets have determinant zero, the evaluation matrix
on `S` has rank at most four, so `x^e` lies in the span of
`1,x,x^2,x^3` on `S`.  Thus this condition is equivalent.

## Exact classification

The script

```text
notes/scripts/issue396_cyclotomic_tail_classification.py
```

enumerates the above condition in `Z[zeta_16]`.  The transcript is saved at

```text
notes/scripts/issue396_cyclotomic_tail_classification.output.txt
```

Result:

| e | h degree | feasible 8-subsets | no-full feasible |
|---:|---:|---:|---:|
| 4 | 0 | 0 | 0 |
| 5 | 1 | 0 | 0 |
| 6 | 2 | 0 | 0 |
| 7 | 3 | 0 | 0 |
| 8 | 4 | 2 | 0 |
| 9 | 5 | 2 | 0 |
| 10 | 6 | 2 | 0 |
| 11 | 7 | 2 | 0 |
| 12 | 8 | 0 | 0 |
| 13 | 9 | 0 | 0 |
| 14 | 10 | 0 | 0 |
| 15 | 11 | 0 | 0 |

For `e=8,9,10,11`, the two feasible subsets are exactly the parity halves:

```text
{0,2,4,6,8,10,12,14}
{1,3,5,7,9,11,13,15}
```

Each contains two full quarter blocks, with occupancies `(4,0,4,0)` and
`(0,4,0,4)`.  Therefore no no-full 8-subset is feasible.

## Lemma for paper use

Let `L=<zeta_16>` and let `S subset L` have size `8`.  Suppose `S` contains
no full coset of `<zeta_16^4>`.  Then for every `4 <= e < 16`, the restriction
of `x^e` to `S` is not the restriction of any polynomial of degree `<4`.

Equivalently, if `g_S(x)=prod_{s in S}(x-s)`, then the remainder of `x^e`
modulo `g_S` has a nonzero coefficient in degrees `4,5,6,7`.

The only 8-subsets on which this can fail are the even and odd parity halves,
and both contain full quarter blocks.

## Issue #396 consequence

For a mixed strict-above-J 3-support, one alpha2-side is a singleton residual
monomial `c x^e` with `4 <= e < 16`.  A no-full saturated component would force
`tail_S(x^e)=0`, contradicting the lemma above.

Hence every no-full branch after the `alpha1=0` quotient is side-pure.  A
side-pure branch has one residual row identically zero, so it is a rank-one
branch and cannot be the primitive rank-2 obstruction sought in #396.
