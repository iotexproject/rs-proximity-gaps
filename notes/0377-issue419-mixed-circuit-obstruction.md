# Note 0377 -- Issue #419: mixed-circuit obstruction to the naive support-shape theorem

> **Note number history**: filed as Note 0362 on the
> `issue-419-stabilizer-lemma` branch; renumbered to 0377 on `main` to
> avoid collision with already-absorbed content at slot 0362.
> Cross-references inside the body to "Notes 0356--0360" use branch
> numbering. Branch-to-main mapping for the issue-419 trail (post Notes
> 0345--0355 / 0356 absorptions):
>   branch 0356           = main 0360 (nonzero-alpha-collapse-mechanisms),
>   branch 0357--0359     = main 0363--0365 (rank-2 plan / shape cert / shape catalog),
>   branch 0360           = main 0375 (catalog-wide shape certificate),
>   branch 0361           = main 0376 (support-shape-theorem-boundary),
>   branch 0362           = main 0377 (mixed-circuit obstruction --- this trail).
> Cross-references to Notes 0345--0352 match `main` numbering directly.

**Date:** 2026-05-01  
**Branch:** `issue-419-stabilizer-lemma`  
**Status:** obstruction found; the naive arbitrary-coefficient
nonzero-alpha shape theorem is false.

---

## Summary

Note 0361 stated the remaining desired theorem in a deliberately strong form:

```text
alpha1 != 0 + rank(W)=2 + no-full saturated
  => half-turn parity split.
```

That statement is false if the folded row coefficients are allowed to be
arbitrary.

The obstruction is not visible in the stable-coefficient catalog scans because
it lives in a special coefficient locus.  It is nevertheless a valid
arbitrary-coefficient folded row span in the quotient-`C4` model.

Script:

```text
notes/scripts/issue419_mixed_circuit_counterexample.py
```

Output:

```text
notes/scripts/issue419_mixed_circuit_counterexample.output.txt
```

---

## Explicit obstruction over F_193

Use `L2=(16,4)`, field `F_193`, support

```text
support = (32, 36, 40, 34, 38, 46)
```

with coefficients

```text
coefs = (112, 79, 1, 30, 47, 1)
```

and `alpha1=1`.  The no-full saturated component is

```text
S = (0, 1, 2, 3, 4, 6, 8, 10).
```

The script verifies:

```text
occupancy(S) = (3,1,3,1)       # no full quarter block
family(S)    = other           # not parity half / near parity / quarter pair
```

The residual rows are:

```text
u = 112 x^8 + 79 x^9 + x^10,
v =  30 x^8 + 47 x^9 + x^11.
```

Both have zero high tail modulo `g_S`, so `S` is saturated for the row span.
But:

```text
alpha1 != 0,
rank(W)=2,
row_stabilizers=(0,),          # trivial dyadic row-span stabilizer
same_folded_cancellations=(),
u_parity=(0,1),
v_parity=(0,1).
```

Thus this is a mixed-parity, rank-2, trivial-stabilizer no-full saturated
component.

---

## Interpretation

The tail-matroid audit explains the mechanism.  After removing same-folded
duplicates and forgetting legal coefficient coupling, sparse three-column
circuits of the high-tail matrix exist.  Two independent mixed-parity
three-circuits can form a rank-2 trivial-stabilizer row span.

Therefore the all-scale proof cannot be:

```text
arbitrary quotient-C4 coefficients
  => nonzero-alpha rank2 branch is half-turn.
```

That theorem is simply false.

---

## Why this does not immediately refute the stable-coefficient scans

The existing #419 classifiers use the deterministic `stable_coefs(support,p)`
coefficient model inherited from the sparse-worst scans.  For the same support
above, those coefficients do **not** satisfy the saturation equations:

```text
unique alpha candidates = 0
all-alpha candidates    = 0
target S has nonzero constant tail and zero slope tail.
```

So the obstruction is a special coefficient-locus phenomenon, not a
counterexample to the exact stable-coefficient catalogs in Notes 0353--0360.

---

## Consequence for the proof strategy

#419 must now be formulated with the correct coefficient quantifiers.

Two possible paths remain:

1. **Generic/Zariski-open theorem.**  Prove that the mixed-circuit locus is a
   proper closed subset of coefficient space, while stable/generic folded
   rows avoid it.  This matches the current empirical scans and would support
   a generic sparse-worst statement.
2. **Worst-case arbitrary-coefficient theorem with extra charging.**  If the
   final conjecture quantifies over all coefficient choices, then the
   mixed-circuit family must be shown to be charged by another local family
   not covered by the current labels.  As written, the example is
   `family=other`, no-full, rank-2, and trivial-stabilizer.

Until that quantifier is clarified, the unconditional arbitrary-coefficient
support-shape theorem should not be claimed.

---

## Next actionable target

The highest-ROI next step is to characterize the legal coefficient locus for
path (c):

```text
Which coefficient choices are actually quantified by paper2 Layer 3 /
conj:sparse-worst, and are special mixed-circuit coefficients allowed?
```

If only Zariski-generic coefficients matter, then the next theorem should be:

> The bad mixed-circuit locus is contained in a proper algebraic subset;
> outside it, nonzero-alpha rank-2 no-full components are half-turn.

If all coefficients matter, then Note 0362 is a real obstruction to the current
primitive global-attachment theorem and the theorem statement must be revised.

---

## ⚠️ UPDATE 2026-05-01 (post-#435 K computation): obstruction is K-DANGEROUS, not just shape-theorem-only

Issue #435 (Note 0378 on `main`, branch `issue-435-obstruction-k`) computed
the **paper2 2D commit-curve K** for this obstruction and the result is far
worse than initially feared:

```text
bad_pairs   = 193^2 = 37249    (every (alpha1, alpha2) pair is bad)
K(f_1,f_2)  = |V_delta| / q = 193  (= q, full saturation)
K_3pos_max  = 10
verdict     : NOT harmless; obstruction is K-dangerous.
```

**Structural reason** (Note 0378): the obstruction support
`(32, 36, 40, 34, 38, 46)` lies entirely in fold quadrants `0` and `2`,
so `u_alpha1` and `v_alpha1` are **independent of `alpha1`**. The same
no-full `S` annihilates the pencil `u + alpha2 v` for every `alpha2`, and
this repeats for every `alpha1`. The 2-round folding therefore collapses to
effectively one round on this support — the round-1 challenge `alpha1`
does no mixing.

**Implication for `conj:sparse-worst` (paper2)**:

The conjecture as written
> $\max_{(f_1, f_2)} K(f_1, f_2; \delta) = \max_{3\text{-pos sparse}} K(\cdots)$

is **refuted in worst-case form** at this 6-position arbitrary-coefficient
input.  The conjecture must be amended to one of:

1. **Generic / Zariski-open**: max over a Zariski-open subset of
   $(f_1, f_2)$ achieves on 3-pos sparse; mixed-circuit / stabilized-support
   degeneracies live in a proper closed locus.
2. **Coefficient-coupling hypothesis**: only "legal" coefficients (those
   inherited from a real FRI-protocol instance) are admitted; the
   obstruction's `(112, 79, 1, 30, 47, 1)` violates the legal coupling.
3. **Action-orbit non-stabilization hypothesis**: support patterns whose
   $\langle \omega^{b-a} \rangle$-orbit on $L_n$ is stabilized (i.e., the
   round-1 fold action is trivial) are excluded explicitly. This matches
   paper2's own Action-Orbit Theorem framework.

Of these, **option 3 is structurally cleanest** and consistent with paper2's
existing Action-Orbit framework.  The obstruction's all-`alpha`-degenerate
nature is exactly the stabilizer phenomenon that the Action-Orbit Theorem
identifies (\cite{Paper2Companion}, `thm:action-orbit`); the sparse-worst
conjecture should therefore restrict to **support patterns with non-trivial
$\alpha_1$-action**.

This is the right amendment to ship before paper2 ePrint.

