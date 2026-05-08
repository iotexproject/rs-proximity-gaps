# Note 0368 -- Issue #396: primitive projection sieve for the residual branch

> **Note number history**: filed as Note 0342 on the `issue-396`
> branch; renumbered to 0368 on `main` to avoid collision with already-
> absorbed content at slot 0342. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** proof-level necessary conditions, with one corrected one-residue
fiber caveat, for the remaining primitive no-full branch.

---

## Purpose

Notes 0340 and 0341 decomposed the first two bilateral base layers into
explicit charges:

```text
same-residue side cancellation,
order-2 parity stabilizer,
direct residual rank collapse.
```

This note records the general normal form behind those charges.  The point is
to separate primitive work from bookkeeping: before attacking the hard
defect-allocation obstruction in Note 0336, one can pass every fixed
`alpha1` row through an effective-support sieve on residues modulo `k`.

The output is not a full closure of #396.  It is a rigorous list of necessary
conditions any remaining primitive rank-2 no-full component must satisfy.

---

## Setup

Let the post-two-fold domain have order `4k`, and write residual rows after
fixing `alpha1` as

```text
u_alpha(x) = sum_a U_a(alpha1) x^a,
v_alpha(x) = sum_a V_a(alpha1) x^a,      0 <= a < k.
```

The coefficients `U_a,V_a` are obtained by quotienting exponents modulo `k`.
For example, on the `u` side:

```text
U_a(alpha1)
  = sum_{j == a mod k, j mod 4 = 0} c_j
    + alpha1 sum_{j == a mod k, j mod 4 = 1} c_j.
```

The `v` side is the same with quadrants `2,3`.  Define the effective residue
supports

```text
E_u(alpha1) = { a : U_a(alpha1) != 0 },
E_v(alpha1) = { a : V_a(alpha1) != 0 }.
```

These are the supports of the two actual residual directions in
`F[x]_<k`, not the nominal support count before residue aggregation.

---

## Lemma 0342.A -- zero effective side is never primitive

If `E_u(alpha1)=empty` or `E_v(alpha1)=empty`, then the residual row span has
rank at most one in the quotient residual layer.  Hence it is charged to the
rank-collapse branch and cannot be a primitive rank-2 no-full component.

In residue equations, `E_u(alpha1)=empty` means

```text
U_a(alpha1)=0       for every residue a.
```

For a two-term side, this can happen at nonzero `alpha1` only when the two
terms project to the same residue modulo `k`; this is the same-residue
cancellation of Notes 0340--0341.  For larger sides, the equations simply
state that every effective residue bucket cancels.  The conclusion is the
same: the row is rank-deficient and leaves the primitive branch.

---

## Lemma 0342.B -- literal singleton side is the all-scale tail case

If one actual residual direction is a literal singleton monomial, say

```text
u_alpha(x) = c x^e,        k <= e < 4k,
```

and a set `S` of size `2k` is saturated for the full row span, then in
particular `u_alpha|_S` lies in `RS_k(S)`.  This is exactly the singleton
residual-tail case handled by Notes 0335 and 0337: a monomial `x^e` with
`k <= e < 4k` restricts to degree `<k` on `S`.

Note 0335 proves that the only equality cases are the two parity halves, and
both contain full quarter blocks.  Therefore a no-full primitive component
cannot have a literal singleton residual side.

There is an important caveat.  A singleton **effective residue**

```text
E_u(alpha1) = {a}
```

does not necessarily mean a literal monomial.  It may be a whole quotient-`C4`
fiber

```text
x^a Q(x^k),        deg Q < 4,
```

with several nonzero `C4` Fourier components.  That one-residue fiber is not
closed by Note 0335 alone.  If it is parity-pure it is caught by Lemma
0342.C below; otherwise it remains a lower-dimensional C4-fiber subcase of
the defect-allocation problem.

Update after Note 0343: this caveat is partly closed by a value-level
root-budget argument.  A one-residue C4 fiber cannot support a saturated
`2k` set whose selected points meet exactly two scalar value levels.  The
remaining one-residue subcases are single active value levels of multiplicity
at least three, or selections meeting at least three scalar values.

---

## Lemma 0342.C -- parity-pure directions descend through order 2

Let `omega` generate the post-two-fold domain of order `4k`.  The order-2
substitution `x -> omega^{2k} x` acts on monomials by

```text
x^a -> (-1)^a x^a.
```

If each effective direction is parity-pure,

```text
E_u(alpha1) mod 2 = {epsilon_u},
E_v(alpha1) mod 2 = {epsilon_v},
```

then

```text
D_{omega^{2k}} u_alpha = (-1)^epsilon_u u_alpha,
D_{omega^{2k}} v_alpha = (-1)^epsilon_v v_alpha.
```

Thus `span(u_alpha,v_alpha)` is invariant under a nontrivial diagonal
substitution.  By Lemma 0310.A, this is a projective cyclic action on the
alpha2 pencil.  It belongs to the dyadic descendant/stabilizer branch, not to
the primitive trivial-stabilizer branch.

Consequently any remaining primitive trivial-stabilizer component must have
at least one direction whose effective support meets both parity classes.

---

## Primitive Projection Sieve

Combining Lemmas 0342.A--C with Notes 0335--0337 gives the following
necessary conditions.

Let `S` be a no-full saturated `2k`-component for a folded above-Johnson
rank-2 residual row span at a fixed nonzero `alpha1`.  If `S` is not charged
to rank collapse, literal singleton-tail parity halves, or dyadic stabilizer
descent, then:

1. both effective residual directions are nonzero;
2. neither actual residual direction is a literal singleton monomial;
3. not both effective directions are parity-pure;
4. the row span has trivial diagonal stabilizer under the order-2 dyadic
   action;
5. any effective one-residue side must be treated as a quotient-`C4`
   one-fiber subcase, not as a solved monomial tail;
6. otherwise the component must satisfy the full defect-allocation constraints
   of Note 0336 with genuinely mixed effective residues.

Equivalently, the only branch left for #396 is:

```text
rank 2,
no full quarter block,
no zero effective side,
no literal singleton residual direction,
trivial order-2 stabilizer,
not both effective directions parity-pure,
and no two-block / defect-root charge.
```

This is the clean primitive target.  It removes the three low-level
projection artifacts that accounted for all nonzero leftovers in the
four- and five-support base panels.

---

## Relation to the finite panels

For four-support `(2,2)` rows, each side has exactly two nominal terms.  A
zero side at nonzero `alpha1` is therefore exactly Lemma 0342.A in its
same-residue form.  The only rank-2 charged leftovers in the seven-prime
panel are Lemma 0342.C order-2 stabilizers.

For five-support `(2,3)/(3,2)` rows, the two-term side behaves the same way:
every zero-side rank collapse in the `q=193` panel is a same-residue
cancellation on that two-term side.  The stabilizer leftovers are precisely
Lemma 0342.C.  The remaining `rank1:nonzero-proportional` aliases are direct
rank collapses and are excluded before the primitive sieve.

Thus Notes 0340--0341 are no longer only empirical histograms.  They are
base-layer confirmations that, after the projection sieve and the one-residue
fiber caveat, no primitive trivial-stabilizer no-full component appears in
the first two bilateral layers.

---

## Remaining hard step

The sieve does not prove that the final branch is empty.  It identifies the
exact branch where the real proof must act:

> Prove that a no-full defect allocation from Note 0336 cannot exist when
> the row span has trivial dyadic stabilizer, no zero or literal singleton
> residual side, and no complete-block/two-block/defect-root charge is
> available; the one-residue C4-fiber subcase must be handled explicitly
> rather than silently folded into the monomial-tail lemma.

This is the structural core of #396.  Any future computation should target
this filtered primitive branch directly; any future paper proof should use
the sieve first, then prove the defect-allocation obstruction only on this
reduced branch.
