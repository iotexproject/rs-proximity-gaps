# Note 0306 — Issue #396: mixed mod-4 fiber scaling

**Date:** 2026-05-01
**Branch:** `issue-396`
**Status:** second #396 diagnostic done.  The mixed mod-4 rank-3 cases are
the genuine nontrivial L2-fiber regime, but the observed distributions are
still finite-pattern `cq+O(1)` laws rather than a direct Helleseth--Kumar
Niho-table lookup.

Script:

- `notes/scripts/issue396_mixed_fiber_scaling.py`
- output: `notes/scripts/issue396_mixed_fiber_scaling.output.txt`

Unlike older mixed-audit scripts, this one uses stable q-independent
coefficients, not Python's process-randomized `hash()`.

---

## Setup

Same deployment as Note 0305:

$$
(n_0,k_0)=(32,8),\qquad R=2,\qquad
q\in\{97,193,257,449,577,769,1153\}.
$$

For fixed `alpha_1`, the measured fiber is

$$
B_2(\alpha_1)=
\{\alpha_2\in\mathbb F_q:
\operatorname{fold}^2_{\alpha_1,\alpha_2}(f)
\text{ is within Johnson at }L_2\}.
$$

Note 0305 handled the separated supports
`supp mod 4 ⊂ {0,1}` and `supp mod 4 ⊂ {2,3}`.  This note uses the
16 mixed supports from Note 0171's audit panel.

---

## Main observation

Mixed supports do **not** collapse to the separated `{0,q}` / `{1,q}` fiber
histograms.  They show stable small fiber sizes on L1-good rows:

| support | mod 4 | max L1-good fiber | asymptotic pattern |
|---|---|---:|---|
| `(13,14,16)` | `(1,2,0)` | 9 | `V=9q` |
| `(9,19,27)` | `(1,3,3)` | 6 | `V=7q-6` |
| `(18,25,26)` | `(2,1,2)` | 5 | `V=5q-4` |
| `(21,29,30)` | `(1,1,2)` | 5 | `V=5q-4` |
| `(11,16,23)` | `(3,0,3)` | 1 | `V=2q-1` |
| `(23,25,31)` | `(3,1,3)` | 0 | `V=q` |
| `(8,21,26)` | `(0,1,2)` | 4 | `V=2q+O(1)` |
| `(8,14,23)` | `(0,2,3)` | 2 | `V=56=O(1)` |
| `(11,12,30)` | `(3,0,2)` | 4 | `V=68=O(1)` |
| `(15,21,24)` | `(3,1,0)` | 2 | `V=64=O(1)` |
| `(8,18,29)` | `(0,2,1)` | 4 | `V=60=O(1)` |
| `(22,24,29)` | `(2,0,1)` | 8 | `V=64=O(1)` |
| `(19,21,24)` | `(3,1,0)` | 4 | usually `V=32=O(1)`; one `q=257` resonance gives `4q-O(1)` |
| `(16,23,24)` | `(0,3,0)` | 0 | `V=0` |
| `(10,12,14)` | `(2,0,2)` | 0 | `V=0` |

The largest observed L1-good fiber is 9, achieved uniformly by
`(13,14,16)`:

$$
|B_2(\alpha_1)| = 9\quad\text{for every }\alpha_1,\qquad |B_1|=0,
$$

so

$$
|V_\delta|=9q.
$$

This is exactly the Note 0171 worst mixed sample, now verified across all
seven q values with stable coefficients.

---

## Interpretation

For rank-3 supports, the two-round fold is always

$$
A+\alpha_1B+\alpha_2C+\alpha_1\alpha_2D
$$

with at least one of the four components missing.  In the separated cases,
two adjacent components vanish and the L2 fibers are trivial.  In mixed
cases, only one component may vanish, so each fixed-alpha row is a genuine
affine L2 pencil in `alpha_2`.

The mixed audit shows that these pencils are still very rigid:

- many rows have a constant fiber size independent of q;
- the nonzero asymptotic slopes are small integers such as 1, 2, 5, 7, 9;
- some supports contribute only `O(1)` total pairs as q grows;
- isolated q-dependent resonances occur, e.g. `(19,21,24)` at `q=257`.

This is not the distribution of a classical m-sequence cross-correlation
amplitude.  It is a finite-field incidence count for sparse RS proximity
pencils on the subgroup `L2`.

---

## Consequence for #396

The off-the-shelf route

> identify Note 0168 with a Helleseth--Kumar Niho `(d,e)` table and cite it

is now very unlikely to close the problem as stated.

What remains viable is narrower and cleaner:

> Prove a mixed-fiber bound
> $$
> \max_{\alpha_1\notin B_1}|B_2(\alpha_1)|\le 9
> $$
> for rank-3 mixed supports at `(32,8)`, and then lift it to the deployment
> family by the existing 2-monomial / sparse-pigeonhole machinery.

Together with the separated Note 0305 formula, this would give

$$
|V_\delta|\le (|B_1|+9)q
$$

for all rank-3 supports at this base scale.  The empirical worst mixed case
has `|B_1|=0`, so the observed bound is exactly `9q`.

This is weaker than the Note 0288 three-position K-bound route, but it is the
right #396 sequence-school formulation: a subgroup incidence / sparse affine
pencil problem, not a direct Niho decimation table lookup.

**Update (Note 0307).**  The mixed rank-3 ceiling above is in fact explained
by the existing 3-monomial pencil theorem (Note 0291): every non-full
fixed-`alpha_1` row is an above-J `s <= 3` monomial pencil on `L2`, hence has
at most `K_3 <= 9` bad `alpha_2` values.  So the rank-3 mixed part is closed
without a new Niho citation; the open #396 work starts at `s >= 4` and
general/dense `f`.

---

## Current #396 state

Positive:

1. Note 0168's separated rank-3 data is fully explained by mod-4 fold
   degeneracy (Note 0305).
2. Mixed rank-3 data has stable `cq+O(1)` fiber laws and max observed
   L1-good fiber 9 across the q-panel.
3. No sampled mixed support shows growth worse than `9q`.

Negative / limitation:

1. This does **not** prove the general-f K-bound requested by paper2 P3.
2. Helleseth--Kumar 1991 style tables do not appear to apply as a black-box
   citation to the measured object.
3. A proof still needs either a bespoke sparse-pencils lemma or external
   sequence-school input phrased as the mixed-fiber bound above.
