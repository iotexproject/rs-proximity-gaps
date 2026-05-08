# Note 0366 -- Issue #396: four-support charged-mechanism audit

> **Note number history**: filed as Note 0340 on the `issue-396`
> branch; renumbered to 0366 on `main` to avoid collision with already-
> absorbed content at slot 0340. Cross-references inside the body
> use branch numbering. Branch-to-main mapping for the issue-396 trail
> after Notes 0327--0334 (already absorbed earlier as 0327--0334 / 0337
> on main):
>   branch 0338, 0339           = absorbed earlier (codex synthesis 0335 / l1 wording 0339 on main differ),
>   branch 0340--0343           = main 0366--0369,
>   branch 0344--0347           = main 0356--0359 (one-residue base / lift / quotient lemma),
>   branch 0348--0352           = main 0370--0374 (this trail).

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** structural audit of the Note 0338 four-support certificate.

Artifacts:

- `notes/scripts/issue396_no_full_4support_cert.py`
- `notes/scripts/issue396_4support_mechanism.q97.output.txt`
- `notes/scripts/issue396_4support_mechanism.q193.output.txt`
- `notes/scripts/issue396_4support_mechanism.q257.output.txt`
- `notes/scripts/issue396_4support_mechanism.q449.output.txt`
- `notes/scripts/issue396_4support_mechanism.q577.output.txt`
- `notes/scripts/issue396_4support_mechanism.q769.output.txt`
- `notes/scripts/issue396_4support_mechanism.q1153.output.txt`

---

## Purpose

Note 0338 showed that the first bilateral multi-term layer, support size `4`
with side counts `(2,2)`, has no primitive rank-2 no-full survivor over seven
primes.  This note asks a sharper question:

> after excluding `alpha1=0`, what are the actual mechanisms charging the
> remaining symbolic no-full solutions?

The certifier now records a mechanism histogram for every nonzero charged
candidate.  This does not change the primitive-counterexample test; it only
classifies the already-excluded rows.

---

## Mechanisms

For a four-support row, each residual side has exactly two terms.  The audit
uses three explicit mechanisms.

### Same-residue side cancellation

If the two terms on one residual side have the same `L2` exponent and lie in
the two `alpha1` quadrants of that side, then there is at most one `alpha1`
for which that whole side vanishes:

```text
c0 t^r + alpha1 c1 t^r = 0.
```

At that alpha, the residual row span has rank at most one, so it cannot be a
primitive rank-2 component.  In the mechanism histogram this appears as

```text
rank1:u-zero:same-residue:(0, 1)
rank1:v-zero:same-residue:(2, 3)
```

This is the local rank-collapse version of the zero-row family from the
earlier notes.

### Order-2 parity stabilizer

If the nonzero `u` residues lie in one parity class of `L2` and the nonzero
`v` residues lie in one parity class, then multiplication by `omega2^8` acts
by scalars on the two residual directions.  For example, when `u` is even and
`v` is odd,

```text
D_{omega2^8} u = u,       D_{omega2^8} v = -v.
```

Thus the projective residual span is preserved by a nontrivial order-2 cyclic
action.  This is a dyadic-descendant/stabilizer charge, not a primitive
no-full component.  In the mechanism histogram this appears as

```text
order2:parity-split:u(0,):v(1,)
order2:parity-split:u(1,):v(0,)
```

### Residual rank alias

Two primes also show pure rank aliases:

```text
rank1:nonzero-proportional
rank0:both-zero
```

These are field-specific coefficient coincidences in the fixed deterministic
coefficient panel.  They are still rank-collapse charges and therefore do not
enter the primitive rank-2 branch.

---

## Seven-prime mechanism panel

All runs use the Note 0338 panel:

```text
L2=(16,4)
support_window=[16,64)
support size = 4
side_min = 2
```

The complete mechanism summaries are:

```text
q=97:
  rank<2 = 336
    rank1:nonzero-proportional                 128
    rank1:u-zero:same-residue:(0,1)            128
    rank1:v-zero:same-residue:(2,3)             80
  stabilizer = 16
    order2:parity-split:u(1,):v(0,)             16

q=193:
  rank<2 = 160
    rank1:u-zero:same-residue:(0,1)            112
    rank1:v-zero:same-residue:(2,3)             48

q=257:
  rank<2 = 96
    rank1:u-zero:same-residue:(0,1)             64
    rank1:v-zero:same-residue:(2,3)             32

q=449:
  rank<2 = 48
    rank1:u-zero:same-residue:(0,1)             16
    rank1:v-zero:same-residue:(2,3)             32

q=577:
  rank<2 = 32
    rank1:u-zero:same-residue:(0,1)             16
    rank1:v-zero:same-residue:(2,3)             16

q=769:
  rank<2 = 10912
    rank0:both-zero                          10896
    rank1:v-zero:same-residue:(2,3)             16

q=1153:
  rank<2 = 16
    rank1:u-zero:same-residue:(0,1)             16
  stabilizer = 16
    order2:parity-split:u(0,):v(1,)             16
```

Every nonzero no-full symbolic candidate in the seven-prime four-support
panel is therefore charged to:

```text
same-residue side cancellation,
order-2 dyadic stabilizer,
or direct residual rank collapse.
```

There are still no primitive rank-2 no-full survivors.

---

## Consequence for the remaining proof

This audit strengthens Note 0338 in the useful direction.  The four-support
base layer is not merely counterexample-free; the entire nonzero leftover set
already decomposes into named local mechanisms.

The next proof target for #396 can now be stated more concretely:

> In the quotient-`C4` local-map normal form of Note 0336, any bilateral
> no-full defect allocation whose support projection creates a same-residue
> side cancellation drops rank, while any parity-separated projection descends
> through the order-2 dyadic stabilizer.  The genuinely primitive branch must
> avoid both mechanisms, and the four-support panel shows that no such branch
> exists at the first bilateral layer.

This does not close the higher-support/higher-scale theorem.  It identifies
the two algebraic charges that the general defect-allocation proof should
force before reaching the primitive rank-2 case.
