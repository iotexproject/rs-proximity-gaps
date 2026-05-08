# Note 0498 — (32, 8) has no α-only 9-tuples in natural candidates: K_2 = 0 likely

**Date:** 2026-05-05 iteration 19-20
**Status:** Surprising structural finding: the parity-class machinery that
made (8, 2) Conj A admit cex (K_2 = 1) does NOT apply at (32, 8). All
candidate 9-tuples have full rank 9 — no α-only minors. Likely consequence:
**(32, 8) Conj A holds with K_2 = 0 unconditional**, i.e., paper2's named
"Conjecture A" might be unconditional after all.

## Iteration 19 finding

For each candidate 9-subset $J \subset \{0, ..., 31\}$, computed the rank
of the 9×20 matrix
$[1, \omega^j, \omega^{2j}, \ldots, \omega^{7j},
  \omega^{8j}, \omega^{9j}, \omega^{12j}, \ldots, \omega^{29j}]_{j \in J}$
where the last 12 columns are the u-side monomials.

α-only condition: rank ≤ 8 (so each u-side column is in span of low-degree).

| Candidate | # 9-tuples | rank dist | α-only count |
|---|---|---|---|
| All-even $\{0, 2, ..., 30\}$ | $\binom{16}{9} = 11440$ | $\{9: 11440\}$ | **0** |
| All-odd $\{1, 3, ..., 31\}$ | 11440 | $\{9: 11440\}$ | **0** |
| $j \mod 8 \in \{0,1,2,3\}$ | 11440 | $\{9: 11440\}$ | **0** |
| $j \mod 8 \in \{0,1,4,5\}$ | 11440 | $\{9: 11440\}$ | **0** |
| $j \mod 4 \in \{0,1\}$ | 11440 | $\{9: 11440\}$ | **0** |

**No α-only 9-tuples found** in any of these natural subgroup-coset
candidates.

## Why is (32, 8) different from (8, 2)?

At (8, 2):
- u-side $= \{4, 5\}$, only 2 monomials
- 3-tuple α-only condition: $z^4 = $ const + linear, $z^5 = $ const + linear
- All-even/all-odd 3-tuples satisfy both (z^4 → ±1, z^5 → ±z) → **8 α-only triples**

At (32, 8):
- u-side $= \{8, 9, 12, 13, 16, 17, 20, 21, 24, 25, 28, 29\}$, **12 monomials**
- 9-tuple α-only condition requires ALL 12 columns $\omega^{rj}$ to be in span of
  $[1, \omega^j, \omega^{2j}, \ldots, \omega^{7j}]$ at the chosen 9 points.
- For all-even $j \in \{2k\}$ where $\tau = \omega^2$ is primitive 16-th root:
  $\omega^{rj} = \tau^{rk}$. For $r = 8$: $\tau^{8k} = (-1)^k$, NOT in span
  of $[1, \tau^k, \ldots, \tau^{7k}]$ on 9 distinct points (since
  $z^8 - p_7(z)$ has at most 8 zeros if non-zero).
- Hence the rank at all-even 9-tuples is full (9), confirming the empirical.

The (8, 2)-style "low-degree-on-coset" trick fails because at (32, 8) the
u-side monomials reach $z^{29}$, far beyond degree 7.

## Strategic implication

If NO α-only 9-tuples exist at (32, 8), the failure-variety structure that
Path A exploited at (8, 2) **does NOT exist at (32, 8)**. Consequences:

1. **Direct path: K_2 = 0 unconditional at (32, 8)**: Without α-only minors,
   every minor condition pins α to a value depending on c (via $\alpha = -B/A$).
   For the system to be consistent across multiple minors → many polynomial
   constraints on c, generically over-determined, **likely no F_p solution**.
   This matches the empirical Note 0491 (56K alphas, 0 cex at (32, 8)).

2. **paper2 §7 implication**: If (32, 8) Conj A is K_2 = 0 unconditional, then
   $K_{BW} \leq 2$ at L_3 = (128, 32) becomes **fully unconditional**, removing
   the "modulo Conj A" qualifier from `thm:K-BW-2-structural`. The paper's
   main bound stands as advertised.

3. **The (8, 2) result becomes "small-scale curiosity"**: K_2 ≤ 1 at (8, 2)
   doesn't propagate to higher scales because the (8, 2) admit-pair structure
   is destroyed by the additional degree-7 polynomial space at (32, 8).
   (8, 2) Conj A in K_2 = 0 form remains false (per Note 0496), but at
   higher scales the analog DOES hold in K_2 = 0 form.

## Validation needed

**(a) Confirm via more candidate searches**: are there α-only 9-tuples in
*non-natural* candidate sets? E.g., tuples mixed with elements from different
mod-classes. Need broader search, but C(32, 9) = 28M is probably too many.

**(b) Confirm via direct empirical**: re-run (32, 8) Conj A test with broader
kernel sampling (current script `issue419_path_A_32_8_full_kernel_exhaustive.py`
uses 200 seeds × ~all (S, c) pairs; if it gives 0 cex, supports K_2 = 0).

**(c) Mathematical proof of "no α-only 9-tuple"**: if we can show that NO
9-tuple has the rank-≤8 property (regardless of natural-subset choice),
this is a structural proof that (32, 8) Conj A is K_2 = 0 unconditional.
Maybe via a counting / Vandermonde argument.

## Connection to "paperwork vs new math"

Per the user's question:
- (8, 2) Conj A: **strictly proven** (K_2 ≤ 1 in $\mathbb{Z}[\zeta_8]$).
- (32, 8) Conj A: **likely K_2 = 0 unconditional**, but the proof structure
  is different from (8, 2). Not pure paperwork — needs verification of
  "no α-only 9-tuple" more rigorously.
- (16, 4) Conj A and (64, 16) intermediate: TBD; likely same as (32, 8).
- (128, 32) Conj A (paper2's named Conj): **likely unconditional** if (32, 8)
  closes via this argument.

If the "no α-only 9-tuple" structural argument can be made rigorous, paper2
§7 K_BW ≤ 2 is unconditional with **no further math needed beyond paperwork
to write the lemma cleanly**.

## Files

- `issue419_path_A_alpha_only_at_32_8.py` (NEW, iter 19) — α-only candidate
  search at (32, 8), 0 found
- `issue419_path_A_32_8_full_kernel_exhaustive.py` (NEW, iter 20, running) —
  empirical confirm via larger kernel sample at p=97

## Confidence update

- **(8, 2) K_2 ≤ 1 unconditional**: PROVEN
- **(32, 8) K_2 = 0 unconditional**: 70% (pending iter 20 empirical + iter 21+ rigorous "no α-only" argument)
- **paper2 §7 K_BW ≤ 2 unconditional via (32, 8) automatic close**: 60%
  within 2 weeks
- **Full unconditional rewrite of paper2 §7**: 50% within 4 weeks
