# Note 0275 -- h=16 odd-prime cluster campaign

**Date:** 2026-04-30  
**Branch:** `codex/issue-387-h2k-cluster-verification`  
**Status:** Operational plan for closing the first live h=2^k checkpoint after
local `std`, `slimgb`, and bounded `msolve` probes all hit workstation limits.

## Target

Close the h=16 single-endpoint checkpoint:

```text
I_chain^(16) + <E_8> = <x_1,...,x_15>
```

over at least one good odd prime.  Good means `p not in {2,3,7}` and the
endpoint row is not degenerate modulo `p`.

## Calibrated tools

Singular runner:

```text
python3 notes/scripts/g3_h2k_cluster_verify.py \
  --k-list 4 --prime 13 --order grevlex --emitter formula --gb slimgb \
  --timeout 21600 \
  --out notes/scripts/g3_h2k_cluster_formula_h16_p13_slimgb_6h.output.txt
```

msolve runner:

```text
python3 notes/scripts/g3_h2k_msolve_run.py \
  --k-list 4 --prime 13 --timeout 21600 --threads 8 \
  --transcript notes/scripts/g3_h2k_msolve_h16_p13_6h.output.txt
```

Both runners emit reproducible inputs before execution.  The msolve runner
streams logs to `*.msolve.log`, records peak RSS, and kills the process group on
timeout.  Use explicit timeouts; do not run raw `msolve` without a wrapper.

## Prime sweep

The first cluster sweep should try:

```text
p in {13, 17, 19, 23, 29, 31}
```

Rationale:

- `p=5`: local Singular/`slimgb` already timed out.
- `p=11`: h=8 msolve calibration degenerates because the endpoint row becomes
  zero modulo 11, so skip it for msolve.
- `p=13`: h=8 calibrates cleanly for both Singular and msolve.
- `p=17`: h=16 bounded msolve also times out locally, but remains a valid
  cluster prime.  The 8-thread, 900s local run peaked at about 35 GiB RSS and
  still timed out, so longer p=17 jobs should be cluster jobs rather than
  workstation background experiments.

The branch pre-emits both msolve and Singular inputs/transcripts for the full
six-prime sweep:

```text
notes/scripts/g3_h2k_k4_h16_p{13,17,19,23,29,31}.msolve.in
notes/scripts/g3_h2k_msolve_h16_p{13,17,19,23,29,31}_emit.output.txt
notes/scripts/g3_h2k_singular_jobs/g3_h2k_k4_h16_p{13,17,19,23,29,31}_grevlex_formula_slimgb.sing
notes/scripts/g3_h2k_cluster_h16_p{13,17,19,23,29,31}_slimgb_emit.output.txt
```

Cluster-side msolve command template:

```text
msolve -f notes/scripts/g3_h2k_k4_h16_p13.msolve.in \
  -o notes/scripts/g3_h2k_k4_h16_p13.cluster.msolve.out \
  -v 1 -t 8
```

Cluster-side Singular command template:

```text
Singular -q \
  notes/scripts/g3_h2k_singular_jobs/g3_h2k_k4_h16_p13_grevlex_formula_slimgb.sing \
  > notes/scripts/g3_h2k_k4_h16_p13.cluster.singular.out 2>&1
```

## Success criterion

For Singular:

```text
status = PASS, vdim = 1, all_x_reduce_to_0 = True
```

For msolve:

```text
status = PASS, degree of ideal = 1
```

Either one is enough to close the h=16 finite certificate over a good prime.

For timeout diagnostics, compare `peak_rss_mb` across primes and engines before
increasing thread count.  A 10s local `p=17` smoke reached about 810 MiB RSS;
an 8-thread, 120s local `p=13` run reached about 5.4 GiB RSS; an 8-thread,
900s local `p=17` run reached about 35.8 GiB RSS and still timed out.  Large
thread counts should be reserved for a high-memory machine, and a h=16 PASS may
require either a much larger cluster job or a smaller certificate.

## If the sweep stalls

If all cluster jobs timeout, or if memory growth looks like the 900s p17 run,
stop treating this as an engine-selection issue.  The next proof target is a
lighter certificate for the same ideal, likely one of:

1. a small elimination/radical membership certificate for `x_i in sqrt(I)`;
2. a reduced univariate restriction using the self-similarity/orbit framework;
3. a normalized-coordinate transfer from the Stage 2 `lambda` system.

Do not add more workstation brute force unless it tests one of these smaller
certificates.
