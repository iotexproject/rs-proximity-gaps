# Note 0344 -- Issue #419: Layer-3 global attachment drill

> **Note number history**: filed as Note 0340 on the
> `issue-419-l3-attachment` branch; renumbered to 0344 on `main` because
> Note 0340 on the trunk is the (renumbered) defect-allocation normal-form
> note. Cross-references to "Notes 0337", "Notes 0338--0339",
> "Note 0336", and "Note 0335" inside the body point to the branch
> numbering and correspond on `main` to Notes 0341, 0342--0343, 0340, and
> 0337 respectively. The "Notes 0321--0323" reference points to the
> quotient-`C4` complete-block machinery, which on `main` is consolidated
> at Note 0323 (`issue396-block-interpolant-normal-form`).

**Date:** 2026-05-01
**Branch:** `issue-419-l3-attachment`
**Status:** local path-(c) theorem imported and checked; global attachment
still reduces to one named defect-allocation descent theorem.

---

## Executive summary

Layer 3 is not blocked by the dyadic monomial tail anymore.

The current state is:

1. **Complete-block machinery:** Notes 0321--0323 give the quotient-`C4`
   local-interpolant normal form.  Two-block components and one-point
   defect-root families have explicit low-degree descriptions.
2. **Local no-full singleton branch:** Notes 0333--0335 prove the
   all-scale tail lemma.  If a no-full saturated `2k`-set would force a
   singleton monomial `x^e`, `k <= e < 4k`, into `RS_k(S)`, then `S` must be
   a parity half, hence contains complete quarter blocks.
3. **Strict 3-support attachment:** Note 0337 packages that local lemma into
   an all-scale strict 3-support theorem.  Side-pure rows are rank deficient;
   mixed rows have a singleton residual side and are killed by Note 0335.
4. **First bilateral layers:** Notes 0338--0339 show the first cases where the
   singleton argument no longer applies still collapse: `(2,2)` four-supports
   over seven primes and `(2,3)/(3,2)` five-supports at `q=193` have no
   primitive rank-2 no-full survivor.

Therefore the remaining 1M-blocker is not another tail lemma.  It is the
global attachment theorem turning these local charges into a proof for
general folded row spans.

---

## The remaining theorem

Use the notation of Note 0336.  Let `L` have order `4k`, quarter blocks
`C_0,...,C_3`, and let `W=span(u,v)` be the post-two-fold row span.  For a
saturated component `S`, put

```text
A_i = S cap C_i,        d_i = k - |A_i|,        sum_i d_i = 2k.
```

The component is already charged if it has:

- two full quarter blocks: two-block equality;
- a full two-block base plus one-point substitutions: defect-root family;
- a singleton residual direction: Note 0335 tail theorem;
- rank `<2`, full-code row, or nontrivial dyadic stabilizer: descent/charged
  degeneracy.

The remaining theorem should be stated exactly as:

> **Defect-allocation descent theorem.**  Suppose `W` arises from a legal
> strict above-Johnson folded row, `alpha1 != 0`, `rank(W)=2`, and `W` has
> trivial dyadic stabilizer.  If a saturated `2k`-component `S` is not charged
> to the complete-block/two-block/defect-root/singleton-tail families, then no
> such `S` exists.

Equivalently:

```text
no-full saturated S
  => alpha1 = 0
     or rank(W) < 2
     or W has nontrivial dyadic stabilizer
     or S descends to a charged smaller dyadic quotient.
```

This is the global attachment needed to promote path (c) from local rigorous
pieces to a proof-level Layer-3 closure.

---

## Why the local theorem is not enough

Note 0335 kills only singleton-tail residuals.  A general `f` can produce both
`alpha2` sides with at least two residual terms.  Then saturation of `S` does
not force a single monomial `x^e` into `RS_k(S)`; it forces two-dimensional
local representative maps to land in four vanishing spaces:

```text
D_i^S(W) subset Z_i(A_i),       dim Z_i(A_i)=d_i.
```

That is a rank/defect-allocation condition, not a root-count condition.
Continuing to prove stronger monomial-tail lemmas will not close the global
case.

---

## Concrete proof handle

The quotient-`C4` formula of Note 0323 gives, for `0 <= a < k`,

```text
[x^a] R_r(P) = sum_m p_{a+mk} zeta^{rm}.
```

Thus the four local representatives are a length-4 Fourier transform of the
coefficient vector in each residue class modulo `k`.

In the no-full bilateral case, all four defect spaces `Z_i(A_i)` are nonzero,
but none pins the common representative `rho_S`.  The right object is the
dual parity-check system from Note 0336:

```text
H_S (R_0(w)|_{A_0}, R_1(w)|_{A_1}, R_2(w)|_{A_2}, R_3(w)|_{A_3})^T = 0
```

for both `w=u,v`.

The proof should show that this system cannot hold for a primitive rank-2
folded row unless the support is stabilized by a lower dyadic quotient.  This
matches the empirical buckets: after removing `alpha1=0`, every tested
bilateral no-full survivor is rank deficient or stabilizer-controlled.

---

## Next drill target

Do not add a new reduction layer.  The next useful result is one of:

1. **Base symbolic identity:** extract from the seven-prime `(2,2)`
   certificates an explicit integer/rational identity proving
   `no-full + alpha1 != 0 + rank2 + trivial-stabilizer` is empty at
   `L2=(16,4)`.
2. **Stabilizer lemma:** prove that any bilateral no-full defect allocation
   satisfying the dual system forces equality under a nontrivial dyadic
   shift, hence descends.
3. **Counterexample search at higher support:** if the above theorem is false,
   the first likely counterexample is not support size 3 and probably not 4;
   it should appear as a primitive rank-2 no-full survivor at larger
   bilateral support.  A targeted search should stop on the first primitive
   row and record its defect allocation.

The highest-ROI next move is (2): prove the stabilizer lemma from the
quotient-`C4` local maps.  It is the direct global attachment from local
rigorous path-(c) to Layer 3.

---

## Verification performed in this session

After importing the relevant #396 notes and scripts into this branch:

```text
PYTHONPATH=notes/scripts python3 notes/scripts/issue396_block_interpolant_normal_form.py
PYTHONPATH=notes/scripts python3 notes/scripts/issue396_no_full_monomial_tail_obstruction.py
python3 notes/scripts/issue396_cyclotomic_tail_classification.py
```

The local-interpolant normal form verified at `(n,k,q)=(16,4,193)`,
`(32,8,193)`, and `(64,16,257)`.  The no-full monomial-tail checks reproduced
`first_bad=None` across the seven-prime panel.  The exact cyclotomic
classification again returned only the two parity halves for the feasible
tail exponents.
