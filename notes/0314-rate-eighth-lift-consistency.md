# Note 0311 — Rate 1/8 Substitution Principle lift, partial sample at (16, 2)

**Date:** 2026-05-01 early morning
**Status:** PARTIAL POSITIVE — 2/2 reliable coprime triples at $(n, k) = (16, 2)$
rate 1/8 give $K = 56$, matching Note 0308 base case (8, 1). Substitution
Principle lift to deployment scale **consistent**. Full sweep deferred (some
Singular subprocesses failed silently — sequential rerun needed).

## Sample at (16, 2)

`g3_3pos_rate_eighth_lift_16x2.py` ran 10 representative triples:

### Coprime (gcd = 1)
| Triple | vdim | Time |
|---|---|---|
| (3, 5, 7) | **56** | 10.6s ✓ |
| (11, 13, 15) | **56** | 12.5s ✓ |
| (3, 7, 13) | (timeout 48s) | TBD |
| (5, 11, 13), (7, 11, 13), (9, 11, 13) | -1 (subprocess race) | bogus |

### Reducible (gcd = 2, expect lift to base K)
| Triple | Reduces to | Expected K (base) | vdim observed |
|---|---|---|---|
| (4, 6, 8) | (2, 3, 4) at (8, 1) | 37 | -1 (bogus) |
| (4, 8, 14) | (2, 4, 7) at (8, 1) | 32 | -1 (bogus) |
| (6, 10, 14) | (3, 5, 7) at (8, 1) | 56 | -1 (bogus) |
| (8, 12, 14) | (4, 6, 7) at (8, 1) | 32 | -1 (bogus) |

## Conclusions

1. **Coprime triples at (16, 2)**: 2/2 reliable cases give $K = 56$, matching
   the base case max. Empirically consistent with K ≤ 56 RIGOROUS UNIVERSAL
   at rate 1/8 deployment scale.

2. **Reducible cases**: Singular subprocess returned 0.0s elapsed with no
   vdim output — likely a race condition or RAM pressure from previously-
   running Singular instances on the same machine. Manual rerun of (4, 6, 8)
   was running 4+ min separately, confirming the actual computation IS slow,
   not instantaneous. Sequential rerun on a clean machine should resolve.

3. **No counterexample to universal K ≤ 56**: across all reliable data, max
   $K$ at rate 1/8 deployment is 56, matching base.

## Status of #408 / #410 rate-1/8 portion

Note 0308 closed rate 1/8 K bound at base (8, 1). This note adds:
- 2 coprime witnesses at deployment scale (16, 2) consistent with K = 56
- Reducible verification deferred to follow-up (subprocess rerun on clean machine)

paper2 PR #415 already has thm:rate-eighth-K56 stating the base-case bound;
the deployment lift is "by Substitution Principle (Note 0284) by analogy with
rate 1/2 verified at (16, 8) in Note 0307". This note provides initial
empirical support for that lift.

## Files

- `notes/scripts/g3_3pos_rate_eighth_lift_16x2.py` — sample script
- `notes/scripts/g3_3pos_rate_eighth_lift_16x2.output.txt` — partial output

## Cross-refs

- Note 0307 (rate 1/2 K=28 deployment lift verify, all 56 triples)
- Note 0308 (rate 1/8 K bounds at base)
- Issue #410 (Q1 universal proof) — relates structurally
- paper2 PR #415 (rate-extension theorems)
