# Note 0303 — Issue #403 deployment sparse-worst empirical harness

**Date:** 2026-04-30
**Status:** First deployment-scale harness for `conj:sparse-worst`.  The
`(n,k)=(32,8)` sparse side is now exact at `q in {97,193,257}` for the same
3-position pencil with `K=6`; the dense side remains sampled evidence rather
than an exact maximization.

## What changed

Issue #403 asks for an above-Johnson deployment-scale sparse-vs-dense sweep:

$$
K(f_1,f_2;\delta)=
|\{\alpha\in\mathbb F_q:\Delta(f_1+\alpha f_2,\mathrm{RS}_k(L))\leq\delta n\}|.
$$

The toy Note 0302 script enumerates all `q^k` codewords and therefore stops at
`(16,4,17)`.  The new script

```
notes/scripts/g3_sparse_worst_deployment_empirical.py
```

uses information-set interpolation instead.  For a sampled `k`-set `T`, it
interpolates `f_1|T` and `f_2|T`; then, for every outside coordinate, agreement
of the pencil

$$
f_1+\alpha f_2
$$

with the interpolated codeword is one linear equation in `alpha`.  Hence one
information set gives candidate bad `alpha` values for the whole pencil at
once.  This is much faster than testing all `alpha` independently.

Implementation update: the interpolants and alpha-equation aggregation are now
evaluated in NumPy batches, using the same barycentric structure as
`mds_decoder.batched_extras`.  This changes the `(32,8,97)` seeded pilot from
roughly 40 seconds at 5000 information sets to about 0.6 seconds on this
machine for the same scale.  The script also streams exact information-set
enumeration by batch, instead of materializing every `k`-subset in memory.

The method is still empirical:

- If it finds an information set with at least `n-delta_n` agreements, the
  bad `alpha` is certified.
- If it does not find one, the result is a lower bound on `K`, not a proof that
  the alpha is good.
- The script reports both the one-word miss probability for a fixed agreement
  set and a capped union-bound diagnostic over all tested alpha values.

## Pilot result at `(32,8,97)`

Command:

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --q 97 --n 32 --k 8 \
  --membership-samples 5000 \
  --n-sparse 6 --n-dense 3 \
  --batch 1000 --progress 1 \
  --same-support \
  --seed-support 15,18,19 \
  --seed-support 1,3,5 \
  --seed-support 11,14,15 \
  --seed 403
```

Coverage row:

| q | n | k | delta_n | membership_samples | one-word miss | n_sparse | sparse_attempts | K_sparse_lb_max | n_dense | dense_attempts | K_dense_lb_max | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 17 | 5000 | 4.689e-02 | 6 | 7 | 2 | 3 | 3 | 0 | 42.6 |

Top sparse lower-bound witness from the pilot:

```
K_lb=2, best_agree_seen=16,
support=(15,21,31), same-support pencil
```

The seeded `15,18,19` sparse support also gives a nonzero lower bound:

```
K_lb=1, best_agree_seen=17,
support=(15,18,19), same-support pencil
```

Dense random samples had `K_dense_lb_max=0`.

Interpretation: this is a positive first deployment-scale signal
(`dense <= sparse` in the lower-bound comparison), and the harness now sees
nonzero sparse bad-alpha structure at `(32,8,97)`.  It does **not** close
Issue #403 yet, because `K_sparse` and `K_dense` are both lower bounds and the
sample size is small.

## Medium `(32,8,q)` rows

After batch-vectorizing the pencil/interpolant loop, the same harness can run a
medium table at 20k information-set samples with one-word miss probability
`4.835e-06` for a fixed target agreement set.  Each row below uses same-support
3-sparse pencils with the seeded supports `15,18,19`, `1,3,5`, and `11,14,15`,
plus random same-support sparse pencils.

| q | n | k | delta_n | samples | one-word miss | n_sparse | sparse_attempts | K_sparse_lb_max | n_dense | dense_attempts | K_dense_lb_max | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 17 | 20000 | 4.835e-06 | 5 | 6 | 2 | 3 | 3 | 0 | 4.0 |
| 193 | 32 | 8 | 17 | 20000 | 4.835e-06 | 5 | 6 | 2 | 3 | 3 | 0 | 4.0 |
| 257 | 32 | 8 | 17 | 20000 | 4.835e-06 | 5 | 6 | 1 | 3 | 3 | 0 | 4.1 |

All three medium rows remain consistent with the sparse-worst prediction in the
one-sided sense measured by this script: sampled dense pencils do not exceed
the sparse lower-bound maxima, while sparse pencils repeatedly produce nonzero
bad-alpha witnesses.

The top repeated sparse support is `15,21,31` at `q=97,193`, where the harness
finds `K_lb=2`.  The seeded `15,18,19` support remains a stable nonzero witness
across all three primes.

## Support-focused sparse search

The random sparse-vs-dense sweep is useful as a sanity check, but the sparse
worst case is support-structured.  The script now has a support-search mode:

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --support-search --q 97 --n 32 --k 8 \
  --membership-samples 5000 \
  --support-limit 50 --coeff-trials 2 \
  --same-support --seed 404
```

This samples a pool of 3-position supports and multiple coefficient pairs per
support.  In a 50-support pilot it found a stronger sparse support:

| q | n | k | samples | supports | coeff_trials | attempts | accepted | top support | top_K_sparse_lb | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 5000 | 50 | 2 | 100 | 96 | `9,21,25` | 3 | 11.6 |

The support `9,21,25` was then rechecked at 50k information-set samples:

| q | n | k | samples | one-word miss | support | coeff_trials | top_K_sparse_lb | runtime_s |
|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 50000 | 5.141e-14 | `9,21,25` | 8 | 3 | 9.7 |
| 193 | 32 | 8 | 50000 | 5.141e-14 | `9,21,25` | 4 | 2 | 5.0 |
| 257 | 32 | 8 | 50000 | 5.141e-14 | `9,21,25` | 4 | 3 | 5.0 |

This is the strongest evidence in this note: `9,21,25` is not an isolated
coefficient accident at `q=97`; it persists across three valid prime fields.
The measurement is still a lower bound, but the miss probability for each
fixed target agreement set is negligible at 50k samples.

For the top `q=97` coefficient witness, exact information-set enumeration is
now feasible.  The command

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --support-search --q 97 --n 32 --k 8 \
  --membership-samples 0 --batch 50000 \
  --support-pool '9,21,25' \
  --fixed-coeffs1 88,11,92 \
  --fixed-coeffs2 54,34,86 \
  --same-support --no-filter-generators \
  --info-progress-every 1000000
```

enumerates all `C(32,8)=10,518,300` information sets and returns:

| q | n | k | support | coeffs1 | coeffs2 | membership | exact K | best agreement | runtime_s |
|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `9,21,25` | `88,11,92` | `54,34,86` | exact | 3 | 16 | 57.7 |

So `K=3` for this fixed sparse pencil is not a sampling artifact.

The same fixed pencil now also has an exact generator-side check.  The command

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --support-search --generator-only --q 97 --n 32 --k 8 \
  --membership-samples 0 --batch 50000 \
  --support-pool '9,21,25' \
  --fixed-coeffs1 88,11,92 \
  --fixed-coeffs2 54,34,86 \
  --same-support
```

again enumerates all `C(32,8)=10,518,300` information sets, but only for the
two fixed generators.  It returns:

| q | n | k | support | coeffs1 | coeffs2 | close1 | best agreement 1 | close2 | best agreement 2 | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `9,21,25` | `88,11,92` | `54,34,86` | false | 11 | false | 12 | 53.2 |

Thus the exact `K=3` pencil is not relying on close-to-RS generators: both
generators are exactly certified above the requested radius by exhaustive
information-set enumeration.

## Larger support search and exact `K=6` witness

A wider same-support sparse search at `(32,8,97)` used 200 supports, three
coefficient pairs per support, and 10k information-set samples per decision:

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --support-search --q 97 --n 32 --k 8 \
  --membership-samples 10000 --batch 1000 \
  --support-limit 200 --coeff-trials 3 \
  --same-support --progress 25 --top 20 --seed 406
```

It found a stronger repeated support:

| q | n | k | samples | supports | coeff trials | accepted | top support | top `K_sparse_lb` | runtime_s |
|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 10000 | 200 | 3 | 583 | `14,22,30` | 6 | 140.5 |

The top coefficient pair was then exact-checked at `q=97`:

```
python3 notes/scripts/g3_sparse_worst_deployment_empirical.py \
  --support-search --q 97 --n 32 --k 8 \
  --membership-samples 0 --batch 50000 \
  --support-pool '14,22,30' \
  --fixed-coeffs1 52,84,20 \
  --fixed-coeffs2 47,84,30 \
  --same-support --no-filter-generators \
  --info-progress-every 1000000 --top 3
```

This enumerated all `C(32,8)=10,518,300` information sets and returned exact
`K=6` with best agreement 16 in 57.1 seconds.  Repeating the exact enumeration
at `q=193` and `q=257` gives the same value:

| q | n | k | support | coeffs1 | coeffs2 | membership | exact K | best agreement | runtime_s |
|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | exact | 6 | 16 | 57.1 |
| 193 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | exact | 6 | 16 | 62.0 |
| 257 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | exact | 6 | 16 | 61.6 |

A generator-only exact check on the same fixed pair returned:

| q | n | k | support | coeffs1 | coeffs2 | exact K | close1 | best agreement 1 | close2 | best agreement 2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | 6 | false | 11 | false | 12 |
| 193 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | 6 | false | 11 | false | 11 |
| 257 | 32 | 8 | `14,22,30` | `52,84,20` | `47,84,30` | 6 | false | 11 | false | 11 |

So the current strongest sparse-worst witness on this branch is exact in both
ways that matter for the empirical claim across all three tested `(32,8,q)`
prime-field cells: the pencil has six bad alphas, and both generators are
exactly above the requested radius.

## Dense-side lower-bound search at `(32,8,q)`

To strengthen the sparse-vs-dense comparison, the harness now supports
dense-only runs (`--n-sparse 0`).  With 50 dense above-J random pencils per
prime and 50k information-set samples per pencil, all three tested primes had
zero observed bad alphas:

| q | n | k | samples per pencil | dense pencils | one-word miss | all-tested-pencils union bound | `K_dense_lb_max` | dense best agreement seen | runtime_s |
|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 50000 | 50 | 5.141e-14 | 2.493e-10 | 0 | 14 | 59.1 |
| 193 | 32 | 8 | 50000 | 50 | 5.141e-14 | 4.961e-10 | 0 | 14 | 60.9 |
| 257 | 32 | 8 | 50000 | 50 | 5.141e-14 | 6.606e-10 | 0 | 13 | 61.2 |

This is still lower-bound evidence for dense pencils, not an exact dense
maximization.  Combined with the exact sparse `K=6` witness, the measured
`(32,8,q)` comparison is now:

| q | `K_sparse` evidence | `K_dense` evidence |
|---|---|---|
| 97 | exact `K=6` | 50 sampled dense pencils, max lower bound 0 |
| 193 | exact `K=6` | 50 sampled dense pencils, max lower bound 0 |
| 257 | exact `K=6` | 50 sampled dense pencils, max lower bound 0 |

## Four-support adversarial check at `(32,8,q)`

The conjecture says the worst case should be achieved by joint support at most
three.  A natural nearest-neighbor falsification attempt is therefore to search
same-support 4-position pencils.  The harness now accepts
`--support-size 4`, so the same information-set path can test this adversarial
family without changing the membership oracle.

I ran same-support 4-position searches with 50k information sets per pencil.
The top lower bound stayed well below the exact 3-support `K=6` witness:

| q | n | k | support size | supports | coeff trials | accepted pencils | one-word miss | all-tested-pencils union bound | top `K_lb` | top support | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 4 | 120 | 2 | 240 | 5.141e-14 | 1.197e-09 | 2 | `15,18,22,31` | 286.4 |
| 193 | 32 | 8 | 4 | 80 | 2 | 160 | 5.141e-14 | 1.588e-09 | 2 | `15,18,22,31` | 192.0 |
| 257 | 32 | 8 | 4 | 80 | 2 | 160 | 5.141e-14 | 2.114e-09 | 2 | `15,18,22,31` | 195.8 |

For the top 4-support pencil in each prime, I also enumerated all
`C(32,8)=10,518,300` information sets:

| q | n | k | support | coeffs1 | coeffs2 | membership | exact K | best agreement | generator best agreements | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `15,18,22,31` | `68,86,77,31` | `17,80,46,38` | exact | 2 | 16 | `(12,12)` | 112.9 |
| 193 | 32 | 8 | `15,18,22,31` | `20,78,163,76` | `97,73,56,155` | exact | 2 | 17 | `(11,11)` | 107.2 |
| 257 | 32 | 8 | `15,18,22,31` | `234,33,34,188` | `219,212,98,133` | exact | 2 | 16 | `(11,11)` | 116.8 |

So the strongest 4-support candidates found so far are not sampling artifacts,
and none threaten the exact 3-support `K=6` witness.  This does not prove the
sparse-worst conjecture, but it meaningfully reduces the most obvious
structured counterexample risk beyond the stated 3-support boundary.

As an extra stress test, I also sampled same-support 5-position pencils at
`(32,8,97)`.  Again the top candidate stayed at `K=2`:

| q | n | k | support size | supports | coeff trials | accepted pencils | one-word miss | all-tested-pencils union bound | top `K_lb` | top support | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | 5 | 60 | 2 | 120 | 5.141e-14 | 5.984e-10 | 2 | `10,16,18,22,26` | 142.2 |

Exact enumeration of the top 5-support pencil gives the same value:

| q | n | k | support | coeffs1 | coeffs2 | membership | exact K | best agreement | generator best agreements | runtime_s |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 32 | 8 | `10,16,18,22,26` | `71,77,2,38,70` | `95,91,14,65,35` | exact | 2 | 18 | `(12,12)` | 110.3 |

This further supports the empirical picture that the current high-`K`
structure is concentrated in the 3-support family, not in immediate larger
same-support perturbations.

## Cell validity caveat

For a prime-field multiplicative subgroup of size `n`, we need `n | q-1`.
Therefore two cells listed in Issue #403 are invalid as prime-field cells:

| requested cell | status |
|---|---|
| `(64,16,97)` | invalid over prime field: `64 ∤ 96` |
| `(128,32,97)` | invalid over prime field: `128 ∤ 96` |

The script now exits cleanly on such cells, e.g.

```
ERROR: no multiplicative subgroup of size n=64 in prime field F_97:
n must divide q-1=96
```

To test those rows, use either extension-field domains or replace `q` by a
prime with `n | q-1`.

A smoke row confirms that the script can run the next valid prime-field cell,
but also shows why light sampling is not meaningful at this size:

| q | n | k | delta_n | samples | one-word miss | n_sparse | K_sparse_lb_max | n_dense | K_dense_lb_max |
|---|---|---|---|---|---|---|---|---|---|
| 193 | 64 | 16 | 33 | 2000 | 9.988e-01 | 1 | 0 | 1 | 0 |

So for `(64,16)` and beyond, #403 needs either a much stronger decoder or a
targeted sparse-support search; a small random information-set sample is
essentially blind.

A targeted `(64,16,193)` same-support search reinforces the same caveat.  With
100 random supports, one coefficient pair per support, and 20k information-set
samples, the script found a candidate at support `33,37,41` with sampled
`K_lb=3`.  However, a 100k generator-only recheck finds the first generator is
already close to RS:

| q | n | k | samples | support | coeffs1 | coeffs2 | close1 | best agreement 1 | close2 | best agreement 2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 193 | 64 | 16 | 100000 | `33,37,41` | `46,55,107` | `79,55,167` | true | 36 | false | 20 |

If the generator filter is disabled, the same pair shows `K_lb=13` at 100k
samples, but it is not an above-J sparse-worst witness because `f_1` is inside
the requested radius.  This is a useful negative control: at `(64,16)`, light
information-set sampling can accept false above-J generators and therefore must
not be used as a closure oracle.

## Current assessment

This branch establishes the reproducible empirical infrastructure for #403 and
now gives a strong `(32,8,q)` coverage table: exact sparse `K=6` witnesses at
all three tested primes, sampled dense rows whose all-tested-alpha miss union
bounds are below `7e-10` per row, and a 4-support adversarial family that does
not beat the 3-support exact witness.  The most important remaining work is
still not wrapper code; it is a stronger membership/list-decoding oracle or a
deterministic dense maximization.  Information-set enumeration makes the fixed
`(32,8)` sparse witnesses exact, but the `(64,16)` smoke row shows that the same
approach does not scale by just increasing samples modestly.

I also checked whether the repository or local environment already contains a
drop-in above-Johnson list decoder.  The existing `mds_decoder.py` is the
information-set oracle used here.  `general_k_syndrome.py` enumerates error
supports, which is infeasible at the #403 `(32,8)` radius because it would need
support sizes near 17.  The `galois` Python package installed locally exposes
standard Reed-Solomon decoding but not GS/Wu list decoding, and Sage is not
installed in this environment.  Thus the remaining blocker is genuine algorithm
work, not an uncalled existing tool.

## Next experiments

1. Add a GS/Wu decoder or a deterministic above-J decision path for dense
   pencils, so the dense table reports exact `K`, not only sampled lower
   bounds.
2. Search whether any `(32,8,q)` sparse 3-position support beats exact `K=6`;
   the current best exact support is `14,22,30`.
3. For `(64,16)` and `(128,32)`, avoid light random information-set sampling;
   use a targeted sparse-support search or a real list decoder.
4. Replace invalid prime-field cells by valid primes:
   - `(64,16,q)` needs `q ≡ 1 mod 64`.
   - `(128,32,q)` needs `q ≡ 1 mod 128`.
5. If extension fields are the intended deployment model, add an `F_{p^m}`
   backend instead of the current prime-field-only arithmetic.

## Files

- `notes/scripts/g3_sparse_worst_deployment_empirical.py`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_medium.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_medium.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_medium.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n64_smoke.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n64_support_search_100x1.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n64_support_33_37_41_confirm100k.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n64_support_33_37_41_generators100k.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n64_support_33_37_41_nofilter100k.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_search.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_9_21_25_confirm.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_9_21_25_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_9_21_25_generators_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_search_200x3.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_14_22_30_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_support_14_22_30_generators_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_support_14_22_30_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_support_14_22_30_generators_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_support_14_22_30_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_support_14_22_30_generators_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_support_14_22_30_confirm.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_support_14_22_30_confirm.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_dense50_union.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_dense50_union.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_dense50_union.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_4support_search120x2.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_4support_search80x2.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_4support_search80x2.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_4support_top_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_4support_top_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_4support_top_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_5support_search60x2.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_5support_top_exact.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_dense50.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_dense50.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_dense50.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q193_n32_support_9_21_25_confirm.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q257_n32_support_9_21_25_confirm.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_seeded.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.q97_n32_pilot.output.txt`
- `notes/scripts/g3_sparse_worst_deployment_empirical.invalid_n64_q97.output.txt`
