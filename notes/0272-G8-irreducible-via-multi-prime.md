# Note 0272 — Lemma A for h=8: G_8 is IRREDUCIBLE over Q

**Date:** 2026-04-30 ~03:00
**Status:** Lemma A confirmed at h=8 via multi-prime sub-product analysis.
G_8(s) of degree 61 has no Q-factor of degree d for any 1 ≤ d ≤ 30,
hence is irreducible.

## Method

1. Extract G_8(s) mod p for several primes p via Singular LEX GB at h=8.
2. Factor G_8 mod p; record cycle pattern.
3. For each candidate split (a, 61-a) over Q, the Q-factor mod p must
   be a SUB-PRODUCT of the mod-p factors. Hence subset of mod-p factor
   degrees must sum to a.
4. Any (a, 61-a) ruled out by failing this for SOME prime → cannot be
   the Q-factorization.

## Mod-p factor patterns

| p | factor degrees | sub-product sums |
|---|---|---|
| 11 | (1, 2, 4, 7, 14, 33) | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, ..., 61 |
| 13 | (2, 2, 13, 44) | 0, 2, 4, 13, 15, 17, 44, 46, 48, 57, 59, 61 |
| 17 | (2, 6, 53) | 0, 2, 6, 8, 53, 55, 59, 61 |
| 19 | (1, 1, 6, 13, 40) | 0, 1, 2, 6, 7, 8, 13, 14, 15, 19, 20, 21, 40, ..., 61 |
| 23 | (1, 1, 2, 3, 5, 9, 12, 13, 15) | many sums |
| 29 | (1, 5, 6, 10, 10, 29) | 0, 1, 5, 6, 10, 11, 15, 16, 20, 21, 25, 29, 30, 31, 35, 39, 40, 45, 50, 51, 55, 60, 61 |

## Compatibility analysis

For each candidate Q-factor degree a ∈ {1, …, 30}, check if subset
sum a is achievable in EVERY mod-p factorization above:

- **a = 1:** mod 13 has no degree-1 sub-product (smallest is 2). RULED OUT.
- **a = 2:** mod 29 has no degree-2 sub-product (only one degree-1 factor; no two 1's). RULED OUT.
- **a = 3, 4, 5, 6, 7, 8:** mod 13 has no sub-product of these degrees. RULED OUT.
- **a = 9:** mod 13 has no 9. RULED OUT.
- **a = 10:** mod 13 has no 10. RULED OUT.
- **a = 11:** mod 13 has no 11. RULED OUT.
- **a = 12, 13:** mod 17 / 13 fail. RULED OUT.
- **a = 14, 15:** mod 17 fails (no 15). RULED OUT.
- ... (all a from 1 to 30 ruled out by SOME prime).

By symmetry (a, 61-a), all splits eliminated. Only (61) — irreducible —
remains compatible.

## Theorem 0272

**Theorem.** G_8(s) is irreducible over Q.

**Proof.** By the multi-prime sub-product argument above, no degree-a
Q-factor with 1 ≤ a ≤ 30 is compatible with the mod-p factorizations
at p ∈ {11, 13, 17, 19, 23, 29}. By symmetry, no a ∈ {31, …, 60} either.
Hence G_8 has no proper Q-factor, i.e., is irreducible. ∎

## Important: G_h vs H_h structure

**Observation.** For h = 2^k, h - 1 is odd. The Z/h-orbit theorem (Note 0265)
implies length-d orbits with d < h have x_{h-1} = 0 (since (h/d) is a
power of 2 ≥ 2, hence even, hence cannot divide odd h-1).

So at h = 2^k, all length-d orbits for d < h project to t = x_{h-1} = 0.
Only V_h^primitive contributes nonzero t-values to G_h(s).

**Consequence:** G_h(s) at h = 2^k equals H_h(s) (the intrinsic V_h^prim
factor), with no need to factor through smaller divisors.

So my proof "G_8 irreducible over Q" is EQUIVALENT to "H_8 irreducible
over Q" — the intrinsic length-8 orbit polynomial.

By Self-Similarity (Note 0267), H_h is intrinsic to h. So:
- H_h irreducible over Q ⟺ V_h^prim is a single Galois orbit over Q.
- Verified at h=4 (trivial), h=5, 6, 7 (mod-p witness), h=8 (multi-prime).

For deployment h = 2^k, k ≥ 9: same multi-prime exclusion technique
applicable (per-h mechanical algorithm).

## Updated Lemma A status

| h | Witness | Status |
|---|---|---|
| 4 | trivial (deg 1) | irreducible ✓ |
| 5 | mod 17 irreducible | irreducible ✓ |
| 6 | mod 11 irreducible | irreducible ✓ |
| 7 | mod 23 irreducible | irreducible ✓ |
| **8** | **multi-prime exclusion (no single mod-p irreducibility witness yet)** | **irreducible ✓** |

For h=8, no single prime has G_8 mod p irreducible (in primes ≤ 29
tested). But the EXCLUSION argument suffices.

This refines the universal Lemma A approach: when no irreducibility
witness is found at small primes, multi-prime sub-product compatibility
analysis can still establish irreducibility.

## For deployment h ≥ 16

This multi-prime technique scales: for h=16, even if G_16 has no small
prime irreducibility witness, multi-prime exclusion can still establish
irreducibility (assuming no proper Q-factor exists).

Combined with Note 0267 (Self-Similarity) and tonight's structural
framework, this gives:

**Universal Lemma A (Stage 2 closure for h=2^k):** G_{h}(s) component
H_h corresponding to V_h^primitive is irreducible over Q for h ∈ {4, 5,
6, 7, 8} verified. h ≥ 16 conjectured by Chebotarev density (Galois
group generic in S_{D_h}).

## Files

- `notes/0272-G8-irreducible-via-multi-prime.md` — this note
- `/tmp/g8_multi_prime.py`, `/tmp/g8_more_primes.py` — extraction scripts
- Empirical data preserved in `/tmp/g8_*_out.txt`
