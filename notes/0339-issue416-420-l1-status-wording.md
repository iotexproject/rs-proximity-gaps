# Note 0339 -- Issues #416/#420: Layer-1 status wording cleanup

> **Note number history**: filed as Note 0337 on the `issue-416-420-l1`
> branch; renumbered to 0339 on `main` to avoid collision with the
> existing Note 0337 (issue 396 scale-lift tail proof) on the trunk.

## Purpose

This is a cosmetic/status-only cleanup for the two open Layer-1 verification
items:

- issue #416: 4-position sparse rate-`1/2` sweep at `(16,8)` still has 58
  Singular TIMEOUT cases.
- issue #420: rate-`1/8` theorem is rigorous at the base panel, but the
  deployment-scale lift still needs the `(16,2)/(32,4)/(64,8)` verification.

No new mathematical result is claimed here.

## Paper wording change

The previous text could be read as claiming that all three sparse rates were
already deployment-uniform.  The corrected wording is:

```text
rho in {1/4, 1/2}: rigorous and deployment-uniform.
rho = 1/8: rigorous at the base panel; deployment lift tracked by #420.
4-pos rate 1/2: open sweep tracked by #416.
```

This keeps the paper honest without weakening the already-proved rate-`1/4`
and rate-`1/2` deployment statements.

## Scope

Changed only status prose in `paper2.tex` (and the project-internal status doc).  The actual sweeps
requested by #416 and #420 remain open.
