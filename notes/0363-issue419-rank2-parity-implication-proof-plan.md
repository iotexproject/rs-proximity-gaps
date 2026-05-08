# Note 0363 -- Issue #419: proof plan for rank-2 nonzero-alpha parity implication

> **Note number history**: filed as Note 0357 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0363 on `main` because
> Note 0357 on the trunk is `issue396-one-residue-stable-lift-probe`.
> Cross-references inside the body to "Note 0356" / "Notes 0356--0358" use
> branch numbering; on `main` they correspond to:
>   branch 0356 = main 0360 (nonzero-alpha-collapse-mechanisms),
>   branch 0357 = main 0363 (this note),
>   branch 0358 = main 0364 (shape-level-parity-cert).
> Cross-references to Notes 0345--0352 match `main` numbering directly.

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** proof-plan note; converts Note 0356 evidence into the next algebraic lemma.

---

## Target from Note 0356

The full q=97 four-support and q=193 five-support panels show:

```text
alpha1 != 0 + no-full saturated component + rank(W)=2
    => half-turn parity split.
```

Equivalently, the row span has half-turn stabilizer and is charged by Notes
0347--0351.  This is now the only primitive global-attachment gap in #419.

The remaining theorem should be stated as:

> **Rank-2 parity implication.**  Let `W=span(u_alpha,v_alpha)` be a legal
> strict above-J folded row span in the quotient-`C4` normal form.  Suppose a
> no-full saturated component `S` satisfies the dual system
> `C(S)+alpha1 M(S)=0` for some `alpha1 != 0`, and `rank(W)=2`.  Then `u_alpha`
> and `v_alpha` are supported on opposite parity eigenspaces of the half-turn
> operator.

---

## What the computation actually proved at base panels

The mechanism classifier is sharper than the old primitive classifier:

```text
q=97 four-support:
  rank<2 same-folded-cancellation   208
  rank<2 rank-or-parity-degenerate  128
  rank=2 half-turn-parity-split      16
  primitive/unclassified              0

q=193 five-support:
  rank<2 same-folded-cancellation   211
  rank<2 rank-or-parity-degenerate   48
  rank=2 half-turn-parity-split      80
  primitive/unclassified              0
```

Thus rank-collapse mechanisms do not need to be classified.  They are already
outside the theorem hypothesis.  The theorem only needs to rule out this
configuration:

```text
rank(W)=2,
alpha1 != 0,
no-full saturated,
at least one of u_alpha or v_alpha has both parities in quotient support.
```

---

## Algebraic reduction to prove

Use the dual parity system of Note 0340.  For each component `S`, high-tail
compatibility gives two affine vector equations:

```text
C_u(S)+alpha1 M_u(S)=0,
C_v(S)+alpha1 M_v(S)=0.
```

Let

```text
E = even quotient exponents,
O = odd quotient exponents.
```

Decompose the residual rows as

```text
u = u_E + u_O,
v = v_E + v_O.
```

The half-turn parity split is exactly:

```text
(u_E,u_O) has one zero side and (v_E,v_O) has the opposite zero side.
```

The forbidden rank-2 mixed-parity case is therefore:

```text
rank(W)=2 and at least one of
  u_E,u_O both nonzero,
  v_E,v_O both nonzero,
  u and v live on same single parity.
```

The q=97/q=193 classifiers show that every such case either makes `rank(W)<2`
or fails the affine no-full equations.

---

## Candidate proof route

### Step 1: factor the affine equations by parity

Because local representatives are quotient-`C4` Fourier transforms, the
half-turn action corresponds to the sign `(-1)^a` on quotient exponent `a`.
The dual equations can be projected to even and odd quotient exponent windows:

```text
Pi_E(C+alpha M)=0,
Pi_O(C+alpha M)=0.
```

A mixed-parity row contributes independently to both projections.  A
single-parity row contributes to only one.

The proof should show that, after quotienting rank-collapse branches, the two
projected systems cannot both have a nonzero solution on the same row.

### Step 2: isolate rank-collapse factors

The classifier found two rank-collapse buckets:

1. **same-folded cancellation:** a literal factor

```text
c_{4r} + alpha1 c_{4r+1}=0
```

or

```text
c_{4r+2} + alpha1 c_{4r+3}=0;
```

2. **rank-or-parity-degenerate:** both rows survive on the same parity and are
proportional there.

These are exactly the minors of the `2 x support` coefficient matrix for
`W`.  Therefore, saturating by `rank(W)=2` should remove both buckets.

### Step 3: prove the saturated parity projection has no mixed solution

After imposing `alpha1 != 0` and inverting all rank-2 minors needed to keep
`rank(W)=2`, the remaining affine ideal should imply

```text
u_E u_O = 0,
v_E v_O = 0,
```

and should exclude the same-parity case by the rank-2 minors plus no-full
occupancy.  The only surviving rank-2 possibility is opposite parity support.

This is a finite-dimensional linear-algebra statement over the quotient-`C4`
normal form.  It should not require another broad enumeration; the computation
already identifies the exact saturation factors.

---

## Concrete next script/proof artifact

The next script should be a small symbolic verifier for a *support-shape*, not
for a field panel:

```text
notes/scripts/issue419_parity_implication_shape_cert.py
```

Input shape examples:

```text
rank-collapse shape: ((10,), (8,), (10,), (8,))
stabilizer shape:    ((11,), (9,), (8,10), ())
stabilizer shape:    ((8,10), (8,), (11,), (9,))
```

The script should:

1. introduce symbolic coefficients for each support-shape slot;
2. build `u0,u1,v0,v1` and hence `u_alpha,v_alpha` symbolically modulo a large
   prime;
3. impose the affine no-full equations for the observed `S` shape;
4. saturate by `alpha1`, then by the rank-2 minors;
5. check that the mixed-parity minors vanish.

If this succeeds on the observed shapes, the resulting identities should be
readable enough to lift into a hand proof: rank-2 saturation kills all
non-parity-split branches.

---

## Current gap statement

#419 is now reduced to proving the rank-2 parity implication above.  The
half-turn branch itself is already closed by the weighted quotient theorem
chain:

```text
Note 0346 row-span/eigenspace descent
+ Note 0348 large-doubled quotient
+ Note 0351 small-doubled quotient
```

So a proof of this parity implication would close the primitive global
attachment branch left by Note 0352.
