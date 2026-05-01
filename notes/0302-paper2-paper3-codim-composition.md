# Note 0302 — Issue #404: paper2 sparse-worst vs paper3 codim composition

**Branch:** `issue-404`  
**Date:** 2026-04-30  
**Status:** first checkpoint; direct composition target needs re-scoping.

## Question

Issue #404 proposes composing:

1. paper2 P3 / Conjecture `conj:sparse-worst`: the maximum of
   \(K(f_1,f_2;\delta)\) above Johnson is achieved by a three-position
   Fourier-sparse pair; and
2. paper3 Theorem `thm:main` / `thm:obstruction`: the high-multiplicity
   Berlekamp bad set \(V_{\rm bad}\subseteq F^{2D}\) has exact codimension
   \(2(c-1)\), with leading components \(V_S\times V_S\), \(|S|=w+1\).

The intended prize-grade payoff would be an unconditional theorem replacing
paper2's sparse-worst conjecture.

## Correct interface

Let \(s_i={\rm synd}(f_i)\). Then

\[
K(f_1,f_2;\delta)
= \#\{\alpha : s_1+\alpha s_2\in \bigcup_{|E|=w}V_E\}.
\]

This is exactly paper3's multiplicity function \(M(s_1,s_2)\), up to the
minor convention of whether \(\alpha=0\) is included. Thus paper3 is relevant:
it classifies the **high-\(K\) locus in syndrome-pair space**.

The important distinction is support:

- paper2 sparsity is **Fourier/monomial support** of \(f_i\) on the cyclic
  evaluation domain;
- paper3 leading components use **Vandermonde support**: \(s_i\in V_S\), where
  \(V_S\) is spanned by coordinate-error syndromes \({\rm ev}_v\).

These are dual-looking but not equivalent. A Fourier-sparse vector can have
large or no small Vandermonde support in syndrome space.

## Guardrail: direct equivalence is false as stated

The acceptance wording in #404 asks for something like:

> joint-support \(\le 3\) iff \(V_S\times V_S\) codim achieves
> \(2(c-1)\) tightly.

This cannot be used literally unless "joint support" is redefined. The two
support notions above are different.

Reproducible small-parameter sanity check:

```bash
python3 notes/scripts/issue404_sparse_vs_vsupport_probe.py
```

Current output:

```text
PARAM n=16 k=4 p=17 D=12 omega=3
  exponents=(4, 5, 6) syndrome_nonzero_coords=[10, 11] min_VS_support_le_6=None
  exponents=(4, 6, 9) syndrome_nonzero_coords=[7, 10] min_VS_support_le_6=None
  exponents=(13, 14, 15) syndrome_nonzero_coords=[1, 2, 3] min_VS_support_le_6=None

PARAM n=16 k=8 p=17 D=8 omega=3
  exponents=(8, 9, 10) syndrome_nonzero_coords=[6, 7] min_VS_support_le_6=None
  exponents=(8, 10, 13) syndrome_nonzero_coords=[3, 6] min_VS_support_le_6=(5, 2, [(2, 3, 4, 9, 12), (4, 8, 10, 14, 15)])
  exponents=(13, 14, 15) syndrome_nonzero_coords=[1, 2, 3] min_VS_support_le_6=(5, 2, [(1, 3, 8, 11, 12), (4, 5, 6, 12, 15)])
```

For \((n,k)=(16,4)\), several three-monomial above-codeword examples have no
representation in any \(V_S\) with \(|S|\le 6\). Hence three-monomial Fourier
sparsity does **not** imply membership in a small paper3 leading component.

## What paper3 still gives

Paper3 gives a valid structural statement for paper2's \(K\):

- If \(K(f_1,f_2)>T\), then \((s_1,s_2)\in V_{\rm bad}\).
- The Zariski-leading part of this high-\(K\) locus is the union of
  \(V_S\times V_S\), \(|S|=w+1\), with codimension \(2(c-1)\).
- Sub-leading strata have codimension at least \(2(c-1)\), and are strict in
  the intended paper3 stratification when \(|S^*|>w+1\).

This is a **high-multiplicity syndrome geometry theorem**, not by itself a
Fourier-sparse maximizer theorem.

## Corrected #404 target

The viable composition target should be rephrased as one of the following.

### Target A — high-K leading-component reduction

Prove that any maximizer of \(K\) over paper2's FRI-induced syndrome-pair family
must lie on a paper3 leading component \(V_S\times V_S\) with \(|S|=w+1\), not
on a sub-leading component.

This would not prove Fourier sparse-worst, but would reduce P3 to analyzing
FRI curves through leading \(V_S\times V_S\) components.

### Target B — Fourier-to-leading-component rigidity

For syndrome pairs arising from cyclic FRI folds, prove that high \(K\) plus
membership in a leading component forces the original fold to be equivalent,
under cyclic symmetries, to the known Crites--Stewart / BGHKS sparse patterns.

This is the closest route to proving `conj:sparse-worst`, but it requires a
new bridge from Vandermonde support to Fourier support. Paper3 alone does not
supply that bridge.

### Target C — dominance, not equivalence

Replace the equality-of-maximizers claim with a codim/dimension dominance
claim:

\[
\dim\{\text{dense FRI-induced pairs with }K\ge K_0\}
<
\dim\{\text{sparse FRI-induced pairs with }K\ge K_0\}
\]

for the relevant \(K_0\). This may support a deployment narrative, but it is
weaker than the current sparse-worst theorem target because worst-case maximum
is not determined by codimension alone.

## Next concrete step

Do not directly edit paper2's conditional theorem into an unconditional theorem.
The immediate high-ROI task is to build a small exact classifier that maps
paper2 pairs to paper3 strata:

1. compute \((s_1,s_2)\) for sparse and random dense pairs;
2. compute minimal joint Vandermonde support \(S^*(s_1,s_2)\);
3. compute \(K=M(s_1,s_2)\);
4. test whether high \(K\) correlates with \(|S^*|=w+1\) and whether the
   leading-component cases are exactly the known sparse patterns.

If that classifier shows high-\(K\) dense pairs sitting on leading components,
#404's direct route likely fails. If it shows leading high-\(K\) cases collapse
to known sparse patterns, Target B becomes a plausible theorem.
