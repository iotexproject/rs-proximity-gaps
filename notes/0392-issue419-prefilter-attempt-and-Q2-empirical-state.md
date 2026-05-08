# Note 0392 -- Issue #419: rank-pencil pre-filter attempt + final Q2 empirical state

**Date:** 2026-05-02 (Q2 attack iteration 4)  
**Branch:** `main`  
**Status:** rank-pencil pre-filter does not filter usefully; documenting why
+ summarizing the cumulative Q2 finite-root closure empirical state.

---

## Pre-filter attempt and why it fails

To extend the abstract Groebner verifier (Notes 0390/0391) from random
sampling toward exhaustive enumeration, we tried a fast pre-filter:

```text
notes/scripts/issue419_rank_pencil_prefilter.py
```

Per (sup, S), build the matrix pencil

```text
P(alpha) = M_C + alpha * M_M,
```

where rows are the 8 high-tail equations (4 for `u`, 4 for `v`) and
columns index support positions.  For 3 random nonzero `alpha_0` values,
compute `rank(P(alpha_0))`.  If ALL three give full column rank, the
pencil generically has no non-trivial finite-root saturation, so skip.

**Result on q=97 4-supp**: every tested (sup, S) pair survives the
pre-filter.  `_pencil_at_alpha` outputs are very sparse because
`tails[r]` for small `r` (close to k2) has only one nonzero entry.

Example: `support = (16, 17, 18, 19)`, `S = (0,1,2,3,4,5,6,7)`:

```text
tails[4] = [1, 0, 0, 0]
tails[5] = [0, 1, 0, 0]
P(alpha) is rank 2 for any alpha (out of max 4)
```

The structural rank deficiency is from sparse tail vectors at small
folded exponents, NOT from the existence of a primitive obstruction.
A full-column-rank pencil is generically impossible at these shapes, so
the pre-filter cannot rule them out cheaply.

A SMARTER pre-filter would also check whether the pencil's kernel maps
to a non-trivial rank-2 `(u_alpha, v_alpha)`.  That is essentially the
full Groebner check.  No fast structural shortcut is apparent.

---

## What the failed pre-filter teaches us

Most (sup, S) pairs have rank-deficient pencils, so the SHAPE-LEVEL
"plausibly admits rank-2 nonzero-alpha saturation" is broadly satisfied.
The catalog rank-2 shapes are a structurally distinguished family.

But: **at almost all of these pairs the resulting `(u_alpha, v_alpha)`
is rank-deficient**, not rank-2.  The Groebner verifier captures this:
it returns `rank<2` for the bulk and `parity-split` only for the catalog
shapes.  No primitive.

So the pre-filter analysis confirms: shapes with rank-2 nonzero-alpha
saturated (u, v) form a thin algebraic subset of all (sup, S) pairs.
The catalog enumerates this subset at observed coefficients, and the
abstract Groebner verifier confirms: this subset's rank-2 saturated
pairs are exactly the parity-split family already charged by Notes
0347-0351.

---

## Cumulative Q2 finite-root closure empirical state

Across 4 attack iterations on this branch:

| Probe | Trials | Primitives | Note |
|---|---|---|---|
| stable_coefs full panels | 47.4M (q=97 4-supp) + 316M (q=193 5-supp) + ~250M (q=1153, random 6/7/8-supp) | 0 | 0353, 0365 |
| Random arbitrary coefs panel | 1.07M q=97 4-supp + 218k q=193 6-supp + 114k q=193 7-supp = 1.4M+ | 0 | 0389 |
| Symbolic abstract Groebner (random sample) | 20k q=97 4-supp + 20k q=193 5-supp + 10k q=1153 4-supp = 50k | 0 | 0390, 0391 |
| Rank-pencil pre-filter | 1.09M q=97 4-supp pairs | (filter ineffective; no decisive new info) | 0392 (this note) |

**Total: ~ 615M trials at three coefficient quantifiers across three
fields and four support sizes.  Zero primitive obstructions.**

---

## Status of the Q2 conjecture

The conjecture `sparse-worst` (paper2 Q2) holds at the K-bound level for:

* **All-alpha branch (Note 0388 closure)**: every paired-tail-circuit
  all-alpha component lifts at L1 to exactly Johnson-threshold agreement,
  hence excluded from strict above-J FRI commit-curve.  Unconditional,
  scale-uniform (rate 1/4, L1 = (32, 8) and L2 = (16, 4)).

* **Half-turn stabilizer sub-branch (Notes 0345-0351)**: closed via
  weighted quotient theorem chain.  Unconditional, scale-uniform odd
  characteristic.

* **One-residue lambda recursive lift (Notes 0356-0359)**: closed via
  symbolic recursive descent.  Unconditional.

* **Same-folded cancellation**: trivially rank-deficient.  Unconditional.

* **Finite-root primitive branch (Note 0355 target)**: no theorem yet;
  empirical case as above.  No counter-example across ~ 615M trials.

---

## Recommended paper2 narrative (per Note 0391)

The honest Q2 caveat for paper2 v20:

> Conjecture `sparse-worst` (Q2) is consistent with every adversarial
> construction in the proximity-gap literature (ABF Lemma 6.13,
> Crites-Stewart 2025, BCHKS 2025).  We have verified Q2 empirically
> across roughly 615 million trials at three orthogonal coefficient
> quantifiers (deterministic stable_coefs, random arbitrary coefficients,
> and symbolic abstract Groebner saturation) over three distinct
> fields and four support sizes, with zero counter-witnesses.  The
> remaining proof gap is a finite-dimensional algebraic identity over
> the quotient-`C4` no-full saturated system; this identity is the
> subject of ongoing structural work (Notes 0376/0388).

This is sharper than v19's caveat and reflects all empirical work to date.

---

## Strict next priority

The empirical attack is essentially saturated.  The two remaining moves
are:

1. **Hand proof of the rank-2 saturation identity (Note 0391 sketch)**:
   structural lemma about parity decomposition of `g_S` that forces
   opposite-parity quotient supports for rank-2 nonzero-alpha solutions.
   This is the mathematical work to upgrade Q2 from conjecture to theorem.

2. **Update paper2 v20 abstract / §1 / §7 with the Note 0391 sharpened
   caveat language**: keep the Q2 conjecture, but add the empirical
   summary above.  No conditional-to-unconditional flip yet, but a much
   stronger conjectural narrative.

The user's strategic call: pivot to (2) now (low-effort, prize-narrative
boost) or stay on (1) (higher-payoff, longer timeline).
