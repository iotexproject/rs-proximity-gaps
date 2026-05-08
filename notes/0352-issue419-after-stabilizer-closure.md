# Note 0352 -- Issue #419: status after half-turn stabilizer closure

**Date:** 2026-05-01
**Branch:** `issue-419-stabilizer-lemma`
**Status:** checkpoint after Note 0351; identifies the remaining global attachment gap.

---

## What is now closed

Notes 0345--0351 close the nontrivial half-turn row-span stabilizer sub-branch
of the defect-allocation descent program.

The exact closed chain is:

1. **Row span, not setwise support** (Note 0345): a dyadic stabilizer preserves
   the folded row span `W`; it need not preserve the saturated component `S`.
2. **Eigenspace descent** (Note 0346): since the dyadic action is semisimple in
   odd characteristic, `W` admits a character eigenbasis.  The quotient image
   of `S` is a weighted fiber configuration.
3. **Base five-root quotient** (Note 0347): the `h=2` large-doubled profile is
   the `(4,1)` parity-side split and has an explicit kernel generator.
4. **Large doubled fibers** (Note 0348): if at least `h` half-turn quotient
   fibers are doubled, the representative decouples and any high direction is
   a charged parity-tail quotient direction.
5. **Small doubled fibers** (Note 0351): if fewer than `h` quotient fibers are
   doubled, the weighted system has no nonzero high direction.  The proof uses
   parity-side multiplicity after squaring the singleton equations.

Therefore:

> Any saturated component whose obstruction is controlled by a nontrivial
> half-turn row-span stabilizer is either charged to a lower dyadic quotient or
> has zero high quotient direction.

This is a theorem-level closure of the half-turn stabilizer branch.  It is not
just empirical: the only finite computation left in the chain is regression
coverage, not part of the proof.

---

## What this does *not* close

This does **not** yet prove the full #419 master theorem.  Note 0344's global
attachment theorem still has a primitive branch:

```text
alpha1 != 0,
rank(W)=2,
W has trivial dyadic row-span stabilizer,
S is no-full and saturated,
S is not charged by complete-block / defect-root / singleton-tail families.
```

The stabilizer work proves that the third line is a meaningful branch cut and
that the complementary nontrivial-stabilizer branch is safe.  It does not prove
that the trivial-stabilizer primitive branch is empty.

Thus the remaining theorem should now be stated without ambiguity:

> **Primitive global attachment theorem.**  Let `W` be a legal strict
> above-Johnson folded rank-2 row span with `alpha1 != 0` and trivial dyadic
> row-span stabilizer.  Then no no-full saturated `2k`-component outside the
> already charged complete-block / two-block / defect-root / singleton-tail
> families exists.

Equivalently, every no-full saturated component satisfies at least one of:

```text
alpha1 = 0,
rank(W) < 2,
nontrivial dyadic row-span stabilizer,
charged local family.
```

The first three branches are degeneracies/descent.  The last branch is local
path-(c) already handled by the imported Notes 0340--0344 machinery.

---

## Updated proof plan

The next work should not attack weighted quotients again.  That branch is now
closed.  The remaining task is to prove or falsify the primitive theorem above.

Recommended immediate targets:

1. **Formal branch classifier.**  Turn the current empirical buckets into a
   script that classifies every candidate as `alpha1=0`, `rank<2`,
   `stabilizer`, or `charged-local`; assert there is no unclassified primitive
   survivor on the existing multiprime panels.
2. **Primitive obstruction equations.**  Extract the exact linear conditions
   defining the unclassified branch from the quotient-`C4` local maps of Note
   0340.  The goal is a finite-dimensional rank statement with the stabilizer
   branch removed.
3. **Search for first survivor.**  If the primitive theorem is false, the first
   survivor should appear as a rank-2, trivial-stabilizer, no-full saturated
   component at larger bilateral support.  The classifier should stop and dump
   the defect allocation and row-span invariants.

A successful proof of the primitive theorem closes the global attachment step
of path (c), hence closes the Layer-3 sparse-worst gate tracked by #419.  A
counterexample would force a revision of the current sparse-worst strategy.
