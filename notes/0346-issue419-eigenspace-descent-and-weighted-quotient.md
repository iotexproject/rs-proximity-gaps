# Note 0346 -- Issue #419: eigenspace descent gives a weighted quotient, not setwise descent

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** proof sharpening for the row-span stabilizer branch; the
half-turn weighted quotient charging gap identified here is closed by Notes
0347--0351.

Artifacts:

- `notes/scripts/issue419_defect_allocation_witnesses.py`
- `notes/scripts/issue419_defect_allocation_witnesses.q97.4support.output.txt`
- `notes/scripts/issue419_defect_allocation_witnesses.q1153.4support.output.txt`
- `notes/scripts/issue419_weighted_quotient_audit.py`
- `notes/scripts/issue419_weighted_quotient_classifier.py`
- `notes/scripts/issue419_weighted_quotient_classifier.q97.output.txt`
- `notes/scripts/issue419_weighted_quotient_classifier.q193.output.txt`
- `notes/scripts/issue419_weighted_quotient_classifier.q1153.output.txt`

---

## Result of this drill

Note 0345 corrected the stabilizer bucket: it stabilizes the folded row span
`W`, not necessarily the saturated set `S`.

This note makes the next step precise.  A nontrivial dyadic row-span
stabilizer gives an honest eigenspace descent of the row polynomials, but for a
non-invariant `S` the quotient object is **weighted**:

```text
half-turn fibers over y=x^2 carry weights 0, 1, or 2,
```

depending on whether `S` contains zero, one, or both points in the fiber.  The
right descent target is therefore a weighted lower-dyadic interpolation system,
not an ordinary lower-level subset.

This is enough to keep Note 0344's stabilizer branch usable without falsely
requiring `S+shift=S`.

---

## Algebraic eigenspace lemma

Let `F` have odd characteristic.  Let `tau` be a diagonal dyadic operator on
the folded coordinate ring, for example the half-turn action

```text
tau(P)(x) = P(-x).
```

More generally, if `mu` has 2-power order `h`, then

```text
tau(P)(x) = P(mu x).
```

If `W` is a two-dimensional row span and `tau W = W`, then `W` has a basis of
`tau`-eigenvectors.

Proof: the minimal polynomial of `tau|_W` divides `T^h-1`.  Since
`char(F)` is odd, `T^h-1` has no repeated roots.  Hence `tau|_W` is
semisimple.  If `P` is an eigenvector with character `lambda=mu^a`, then every
nonzero coefficient of `P` has exponent congruent to `a mod h`.  Thus

```text
P(x) = x^a Q(x^h)
```

after reducing the exponent class.  For the half-turn `h=2`, this is simply

```text
P_even(x)=Q_0(x^2),        P_odd(x)=x Q_1(x^2).
```

So the row span descends to a lower dyadic variable after stripping character
monomials.

---

## Why the quotient is weighted

Let `pi: x -> y=x^2`, and let a half-turn fiber be `{x,-x}`.  Decompose any
low representative `rho in RS_k` as

```text
rho(x)=rho_0(y)+x rho_1(y),
```

with the usual degree bounds on `rho_0,rho_1`.

For an even row `P(x)=Q(y)`, the constraints imposed by `S` on a fiber are:

```text
weight 0:  no equation;
weight 1:  rho_0(y) +/- x rho_1(y) = Q(y);
weight 2:  rho_0(y)=Q(y) and rho_1(y)=0.
```

For an odd row `P(x)=xQ(y)`, the constraints are:

```text
weight 0:  no equation;
weight 1:  rho_0(y) +/- x rho_1(y) = +/- x Q(y);
weight 2:  rho_0(y)=0 and rho_1(y)=Q(y).
```

Thus a non-invariant `S` still descends, but it descends to a weighted quotient
interpolation problem.  Full fibers impose two quotient equations; singleton
fibers impose one signed mixed equation; empty fibers impose none.

This is the exact place where a setwise-descent proof would be wrong.

---

## Empirical shape of the stabilizer bucket

After adding `half_turn_fiber_profile` to the witness extractor, the existing
base panels show a stable quotient profile in the nontrivial half-turn bucket.

For the q=97 and q=1153 four-support scans, every printed stabilizer/rank
degeneracy example has profile histogram

```text
three fibers of weight 2,
two fibers of weight 1,
three fibers of weight 0.
```

Equivalently, the half-turn quotient sees:

```text
|pi(S)| = 5,      total weight = 8,
```

with exactly three doubled fibers and two singleton fibers.

This explains the earlier paradox:

```text
row_stabs=(0,8),        S_shift_stabs=(0,)
```

The row span descends through parity eigenspaces, while `S` descends only as a
weighted fiber configuration.

---

## Corrected stabilizer branch for Note 0344

The nontrivial-stabilizer branch should be phrased as:

> If `tau W=W` for a nontrivial dyadic `tau`, replace `W` by a character
> eigenbasis and push the saturation equations through the quotient map.  The
> image of `S` is a weighted quotient configuration.  The branch is charged if
> the resulting weighted quotient system is one of the lower-dyadic charged
> systems.

This avoids the false implication:

```text
tau W = W   does not imply   tau S = S.
```

and replaces it with the true implication:

```text
tau W = W   implies   W has quotient eigenrows;
S contributes only fiber weights/signs to the quotient equations.
```

---

## Remaining blocker

This was the remaining blocker when the note was written.  It is now closed
for the half-turn branch by:

- Note 0347: base five-root quotient lemma;
- Note 0348: all-scale large-doubled quotient classification;
- Note 0351: all-scale small-doubled parity-side multiplicity proof.

The original narrowed target was:

> **Weighted quotient charging lemma.**  For the weighted lower-dyadic systems
> produced above, every no-full saturated configuration is charged by the
> complete-block / defect-root / singleton-tail families after quotienting,
> or descends again.

For the current base-panel stabilizer witnesses, this lemma only needs to
handle the `3 full + 2 singleton + 3 empty` half-turn fiber profile.  A general
proof should allow deeper dyadic stabilizers by replacing fiber weights
`0,1,2` with weights on `h`-point fibers and using the corresponding character
decomposition.

This is a real reduction in difficulty: the unknown set `S` no longer appears
as an arbitrary `2k`-subset.  It appears as a bounded-weight quotient
interpolation instance coupled to explicit character eigenrows.

---

## Base-panel weighted quotient classifier

The new classifier enumerates every no-full `8`-subset in `L2=(16,4)` and
tests the weighted quotient interpolation problem directly.

For a half-turn eigenrow, the only possible high quotient direction is

```text
even:  y^4(c_0+c_1 y),
odd:   x y^4(c_0+c_1 y).
```

The script asks whether a nonzero pair `(c_0,c_1)` can be absorbed by an
`RS_4` representative on `S`.  It does this by forming the weighted quotient
matrix for

```text
rho(x)=a_0+a_1 y + x(b_0+b_1 y)
```

and computing the allowed two-dimensional high-row direction modulo the
column span of the representative matrix.

The result is field-independent across the three audit primes:

```text
q=97:
  nofull_subsets=10896
  nonzero_weighted_quotient_subsets=128
  profile_hist={(((0, 3), (1, 2), (2, 3)), 1, 1): 128}

q=193:
  nofull_subsets=10896
  nonzero_weighted_quotient_subsets=128
  profile_hist={(((0, 3), (1, 2), (2, 3)), 1, 1): 128}

q=1153:
  nofull_subsets=10896
  nonzero_weighted_quotient_subsets=128
  profile_hist={(((0, 3), (1, 2), (2, 3)), 1, 1): 128}
```

So among all no-full sets, the weighted half-turn quotient permits any
nonzero high eigenrow only in the same profile already seen in the stabilizer
witnesses:

```text
0^3, 1^2, 2^3.
```

Moreover, the even and odd high-row directions always coincide.  For example:

```text
q=193:
  ratio_hist={
    ('-9','-9'):16, ('-1','-1'):16, ('43','43'):16, ('9','9'):16,
    ('-43','-43'):16, ('-81','-81'):16, ('1','1'):16, ('81','81'):16
  }
```

The ratios are exactly the eight values `-t^{-1}`, where `t` is the singleton
quotient root on the opposite parity coset.  Thus the base stabilizer branch is
not arbitrary: once a nonzero high quotient row exists, both parity characters
are forced into the same one-dimensional direction.

This gives the next paper-grade lemma target:

> **Weighted half-turn base lemma.**  In `L2=(16,4)`, a no-full weighted
> half-turn quotient set supports a nonzero even or odd high eigenrow iff its
> fiber profile is `0^3,1^2,2^3` and its high direction is one of the eight
> root directions `c_1/c_0=-y_i`.  The even and odd allowed directions are the
> same.

The statement is now finite-dimensional and independent of the original
folded support.  Proving this lemma symbolically would close the base
stabilizer branch; lifting it dyadically is the remaining all-scale step.

---

## Cleaner proof reduction for the base lemma

The classifier also reveals why the even and odd directions are identical.
Let the half-turn quotient support be

```text
T = pi(S) subset mu_8.
```

In the `0^3,1^2,2^3` profile, `|T|=5`: three doubled fibers and two singleton
fibers.  For an even high eigenrow

```text
E(y)=y^4(c_0+c_1 y),
```

the full fibers force the odd part `b_0+b_1y` of the representative to vanish
at three quotient points, hence vanish identically.  The singleton fibers then
impose the same equation as the full fibers:

```text
a_0+a_1y = E(y)        on T.
```

Thus a nonzero even high direction exists iff a nonzero polynomial in

```text
V = span{1, y, y^4, y^5}
```

vanishes on the five-point quotient support `T`.

For an odd high eigenrow the roles of `a_0+a_1y` and `b_0+b_1y` swap, and the
same condition on `V` is obtained.  This proves the equality of even and odd
allowed directions once the five-root classification in `V` is known.

So the base weighted lemma reduces to the following finite cyclotomic
statement:

> **Five-root quotient lemma.**  For `T subset mu_8`, `|T|=5`, the evaluation
> map `V -> F^T` has a kernel iff `T` is one of the eight projection supports
> detected by the classifier, namely a full parity coset plus one point `t` in
> the opposite parity coset.  In that case the kernel is one-dimensional and
> its high direction has `c_1/c_0=-t^{-1}`.

This is now the exact symbolic proof target.  The singleton signs are no
longer part of the algebra: once the projection support `T` is allowed, the
two singleton fibers can choose their signs independently, giving the observed
factor `4` per projection support and `16` per root direction.
