# Note 0276 -- h=16 univariate certificate pivot

**Date:** 2026-04-30  
**Branch:** `codex/issue-387-h2k-cluster-verification`  
**Status:** The direct closure computation remains the live checkpoint, but
the best next route is now the primitive univariate certificate.

## Why pivot

The direct h=16 certificate

```text
I_chain^(16) + <E_8> = <x_1, ..., x_15>
```

has now hit the local workstation limit through three independent engines:

- Singular `std`;
- Singular `slimgb`;
- bounded streaming `msolve`.

The h=16 p17 msolve probe reached about 35.8 GiB peak RSS and still timed
out.  Repeating larger local brute force is therefore low ROI unless it tests a
strictly smaller certificate.

The upstream `fri-2round-tightness` branch added the decisive structural clue:
for `h = 2^k`, the odd `h-1` projection implies

```text
G_h(s) = H_h(s),
```

because every lower-length orbit has `x_{h-1}=0`.  Thus the h=16 primitive
piece can be studied through the chain-only eliminant

```text
f_h(t) = t * G_h(t^h),    t = x_{h-1}.
```

Once `G_16` is available modulo good primes, the endpoint non-vanishing check
can be converted from a 15-variable closure GB into a one-dimensional gcd or
remainder certificate on the primitive factor.

## New tooling

`notes/scripts/g3_h2k_univariate_probe.py` emits and optionally runs a modular
Singular LEX job for the chain-only eliminant.  It then parses `f_h(t)`,
converts it to `G_h(s)`, factors `G_h mod p`, and reports the same
multi-prime sub-product obstruction used in upstream Note 0272 for `G_8`.
With `--reduce-endpoint`, the same job also reduces `E_{h/2}` by the chain
GB, parses

```text
E_{h/2} mod I_chain = t^a Q(t^h),
```

and checks `gcd(G_h(s), Q(s)) = 1` over `F_p[s]`.

It deliberately excludes characteristics `{2,3,7}`.

The first h=16 six-prime univariate + endpoint-remainder sweep jobs are
pre-emitted:

```text
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p13.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p17.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p19.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p23.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p29.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p31.sing
```

A second six-prime sweep is also pre-emitted with a `grevlex -> FGLM -> lex`
strategy:

```text
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p13_grevlex_fglm.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p17_grevlex_fglm.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p19_grevlex_fglm.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p23_grevlex_fglm.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p29_grevlex_fglm.sing
notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p31_grevlex_fglm.sing
```

This does not change the certificate.  It only changes the extraction engine:
compute a `dp` standard basis first, then use Singular's built-in
`fglm(source_ring, G)` to move to `lp` before extracting `f_h(t)` and reducing
the endpoint.  The h=4 endpoint certificate calibrates this strategy at p=13.

Cluster command template:

```text
Singular -q \
  notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p13.sing \
  > notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p13.cluster.out 2>&1
```

Local command template, only with explicit timeout:

```text
python3 notes/scripts/g3_h2k_univariate_probe.py \
  --k 4 --primes 13 --timeout 3600 --reduce-endpoint
```

## Calibration caveat

The endpoint-gcd parser is calibrated at h=4.  The command

```text
python3 notes/scripts/g3_h2k_univariate_probe.py \
  --k 2 --primes 11,13 --timeout 120 --reduce-endpoint
```

returns, for both p=11 and p=13,

```text
deg=1 factors=(1,) endpoint_shift=2 endpoint_q_degree=0 endpoint_gcd_degree=0
```

with transcripts in
`notes/scripts/g3_h2k_upoly_h4_endpoint_calibration.output.txt` and
`notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k2_h4_p{11,13}.output.txt`.
Concretely, the Singular reductions give `E_2 mod I_chain = 2*x3^2` over
F_11 and `E_2 mod I_chain = 3*x3^2` over F_13, so the endpoint remainder is
coprime to the primitive factor `G_4(s)`.

A local h=8 LEX extraction probe was stopped after it became another GB-bound
computation rather than a quick calibration.  This is not a mathematical
failure.  It means the h=8/h=16 univariate route still needs either:

1. a cluster run for the emitted LEX jobs; or
2. a smaller extraction method that avoids full LEX GB.

A later h=8 `grevlex -> FGLM` extraction at p=13 finished quickly and
confirmed that the FGLM leg itself is operational:

```text
python3 notes/scripts/g3_h2k_univariate_probe.py \
  --k 3 --primes 13 --strategy grevlex-fglm --timeout 600 \
  --heartbeat-seconds 60 --max-rss-mb 80000 --reduce-endpoint
```

It produced `vdim = 493`, `deg_f = 489`, and a univariate eliminant in
`x7 = t`, but the endpoint normal form still contained `x6^2`:

```text
RENDPOINT_BEGIN
3*x6^2 + Q(x7)
RENDPOINT_END
```

The endpoint-gcd parser now handles this case by using the second lex-basis
relation:

```text
G[2] = x6*x7 - P(x7)
```

On the primitive branch `x7 != 0`, the endpoint vanishing test is equivalent
to a univariate gcd after clearing the denominator:

```text
gcd(f_h(x7)/x7, 3*P(x7)^2 + x7^2*Q(x7)) = 1.
```

The calibrated command

```text
nice -n 10 python3 notes/scripts/g3_h2k_univariate_probe.py \
  --k 3 --primes 11,13 --strategy grevlex-fglm --timeout 120 \
  --heartbeat-seconds 30 --max-rss-mb 20000 --reduce-endpoint \
  | tee notes/scripts/g3_h2k_upoly_h8_relation_endpoint_calibration.output.txt
```

reports `endpoint_gcd_degree=0` at both good primes:

```text
k=3 h=8 p=11: PASS deg=61 ... endpoint_gcd_degree=0
k=3 h=8 p=13: PASS deg=61 ... endpoint_gcd_degree=0
```

This removes the h=8 endpoint-parser blocker.  For h=16 the remaining local
blocker is earlier: the good-prime grevlex/FGLM jobs have not yet reached
`std_done`, so there is still no h=16 `FPOL`/`RENDPOINT` transcript to feed
this relation-clearing endpoint test.

The existing upstream Note 0272 already calibrates the same mathematical
certificate at h=8: `G_8(s)` has degree 61 and is irreducible over Q by
multi-prime sub-product exclusion.

## Next proof target

The concrete next certificate is:

1. Extract `G_16(s) mod p` for several good primes.
2. Use factor patterns to either find a single irreducibility witness or run
   the multi-prime sub-product exclusion.
3. Extract the endpoint restriction/remainder
   `E_8 mod I_chain = t^a R_8(t^16)` along `t = x_15`.
4. Prove

```text
gcd(G_16(s), R_8(s)) = 1
```

over at least one good prime.

By the `G_h = H_h` observation at powers of two, this gcd certificate is the
same intrinsic non-vanishing condition needed by Notes 0268--0271.

## Operational rule

Do not launch more unbounded local GB jobs for h=16.  Use emitted jobs on a
high-memory machine, or attack a smaller remainder/elimination certificate.

## Preferred cluster handoff

The direct closure jobs in Note 0275 remain valid but should now be treated as
fallbacks.  The preferred h=16 handoff is the six-prime univariate +
endpoint-remainder sweep below:

```text
for p in 13 17 19 23 29 31; do
  Singular -q \
    notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p${p}.sing \
    > notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p${p}.cluster.out 2>&1
done
```

Alternative FGLM handoff:

```text
for p in 13 17 19 23 29 31; do
  Singular -q \
    notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p${p}_grevlex_fglm.sing \
    > notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p${p}_grevlex_fglm.cluster.out 2>&1
done
```

The machine-readable manifest for both sweeps is:

```text
notes/data/h16_upoly_job_manifest.jsonl
```

Each JSONL row records `h`, `k`, `prime`, `strategy`, the `.sing` job, the
expected `.cluster.out`, and the exact shell command.

List or select manifest rows with:

```text
python3 notes/scripts/g3_h2k_upoly_manifest.py
python3 notes/scripts/g3_h2k_upoly_manifest.py --prime 13 --strategy grevlex-fglm
python3 notes/scripts/g3_h2k_upoly_manifest.py --strategy grevlex-fglm --commands-only
python3 notes/scripts/g3_h2k_upoly_manifest.py --outputs-only
```

Cluster-array jobs can use `--index $TASK_ID --run` to execute exactly one
manifest row.

Collect completed outputs with:

```text
python3 notes/scripts/g3_h2k_upoly_collect.py \
  --require-endpoint --markdown \
  notes/scripts/g3_h2k_upoly_jobs/g3_h2k_upoly_k4_h16_p*.cluster.out
```

The closure row is:

```text
k = 4, h = 16, p notin {2,3,7}, status = PASS, gcd = 0.
```

A transcript missing `RENDPOINT` is not enough for issue #387.  It can still
feed the multi-prime irreducibility/sub-product analysis for `G_16`, but the
single-endpoint checkpoint needs the endpoint remainder gcd.
