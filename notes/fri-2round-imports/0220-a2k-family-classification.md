# Note 0220 — Classification of (a, 2k) family at deployment scale

**Date:** 2026-04-29
**Status:** Empirical classification at (n=8, k=2) and (n=16, k=4).
**Discovery:** NEW non-sign-paired family at a = 3k/2 with |B| ≤ 8.

## Setup

At deployment scale `n = 4k`, consider the 2-monomial pencil family
`h_ρ(z) = ρz^a + z^{2k}` for `a ∈ [1, 2k-1]`. Note 0219 covers `a = k`
RIGOROUSLY. This note classifies all other `a`.

## Empirical eliminator Φ(ρ) — last lex GB poly

| (n, k) | a | Φ(ρ) | |B| | type |
|---|---|---|---|---|
| (8, 2) | 1 | (no ρ-eq, p₃ free) | full F_q* | degenerate |
| (8, 2) | 2 | ρ⁵ + 4ρ = ρ(ρ⁴ + 4) | 4 | Note 0219 (k, 2k) |
| (8, 2) | 3 | ρ⁹ - 16ρ = ρ(ρ⁴-4)(ρ⁴+4) | 8 | **NEW (3k/2, 2k)** |
| (16, 4) | 1, 2, 3 | (no ρ-eq, p₇ free) | full F_q* | degenerate |
| (16, 4) | 4 | ρ⁵ + 4ρ | 4 | Note 0219 (k, 2k) |
| (16, 4) | 5 | ρ | ∅ | trivial |
| (16, 4) | 6 | ρ⁹ - 16ρ | 8 | **NEW (3k/2, 2k)** |
| (16, 4) | 7 | ρ | ∅ | trivial |

Brute-force verification at `q=17`:
- `(4, 8)`: `B = {3, 5, 12, 14}`, `ρ⁴ = 13 ≡ -4 (mod 17)`. ✓ Note 0219.
- `(6, 8)`: `B = {3, 5, 6, 7, 10, 11, 12, 14}`, `ρ⁴ ∈ {4, 13} ≡ {±4}`.
  ⟹ `|B|` is 8 = 2 sign-paired-like cosets.

## Discovery: (3k/2, 2k) is a 2nd non-sign-paired family

Beyond `(k, 2k)` of Note 0219, **`(3k/2, 2k)` at `n = 4k` (k even)** is
non-trivial with eliminator
$$
\Phi(\rho) = \rho \cdot (\rho^4 - 4)(\rho^4 + 4) = \rho(\rho^8 - 16).
$$

The `(ρ⁴ + 4)` factor is identical to the (k, 2k) Note 0219 family.
The `(ρ⁴ - 4)` factor is genuinely new.

**Empirically scale-uniform** at `(8, 2)`, `(16, 4)`, **and `(32, 8)`**:
- `(n=32, k=8, a=12, b=16)`: lex GB last poly = `ρ⁹ - 16ρ` ✓ (6.9s).
- Identical eliminator across three deployment scales.

## Why (3k/2, 2k)? Structural observation

The pencil factors as
$$
h_\rho(z) = \rho z^{3k/2} + z^{2k} = z^{3k/2} (\rho + z^{k/2}).
$$

Dist to `RS_k(L_n)` ≡ dist of `(ρ + z^{k/2})` to a SHIFTED code
`z^{-3k/2} · RS_k(L_n)`. The free function has 2-mon support `{0, k/2}`,
the shifted code occupies positions `{5k/2, …, 7k/2 - 1}` mod n = 4k.

The interaction of the shorter binomial period (k/2 vs k for Note 0219)
with the shifted code window produces the additional `ρ⁴ = 4` cosolution.

## Other (a, 2k) cases

**`a < k` (i.e., a ∈ [1, k-1])**: Last lex GB poly involves `p_{2k-1}`,
not ρ. The ideal allows ρ to be any value. These are **at-J degenerate**
pencils per Note 0185 dichotomy: `dist(h_ρ, RS_k) = J` exactly for all ρ,
yielding K = 2q saturation regime. Not the prize-relevant **above-J**
regime.

**`a > k, a ≠ 3k/2, a ≠ 2k-1` at n = 16**: e.g. `a = 5, 7` → Φ = ρ
(only ρ = 0). At deployment scale, **B = ∅**. These pencils have no
above-J bad ratios.

**`a = 2k - 1`** (e.g., a = 7 at n = 16): B = ∅. The (a = k+1, 2k) toy
case at (8, 2) gave Φ = ρ⁹ - 16ρ (= 8 bad ρ), but at (16, 4) the analog
a = 5 gives Φ = ρ. **Toy is anomalous**; deployment scale collapses
this family to empty.

## Implication for Conjecture E completeness

**At deployment scale `n = 4k`, k ≥ 4**:

| Family | a | b | Status |
|---|---|---|---|
| Sign-paired | any | a + 2k | **RIGOROUS** |B|≤4 (Note 0218) |
| (k, 2k) | k | 2k | **RIGOROUS** |B|≤4 (Note 0219) |
| (3k/2, 2k) | 3k/2 | 2k | **EMPIRICAL** |B|≤8 (this note) |
| Other (a, 2k) | else | 2k | **EMPIRICAL** |B|=∅ at n=16 |
| (a, b) non-shaped | various | various | open |

The (3k/2, 2k) family is the natural **next rigorization target**.

## Toy-vs-deployment lesson

At toy `(n=8, k=2)`, several pencils had non-trivial bad sets:
- (3, 4): |B| = 8

At `(n=16, k=4)` the analogous "near-(k, 2k)" pencils collapse:
- (5, 8): B = ∅
- (7, 8): B = ∅

**Toy bad-ρ counts overcount**. The deployment-scale `(a, 2k)` family
has only TWO non-empty cases: `(k, 2k)` and `(3k/2, 2k)`.

## Files

- `notes/scripts/g3_a2k_groebner.py` — toy GB sweep
- `notes/scripts/g3_a2k_family_sweep.py` — toy brute B sweep
- `/tmp/g3_a2k_n16_lex.py` — n=16 lex GB sweep
- `/tmp/g3_a2k_n32.py` — n=32 (12, 16) eliminator: `ρ⁹ - 16ρ`
- `/tmp/g3_n16_brute.py` — brute B verification at n=16, q=17

## Next

1. ✓ Verify `(3k/2, 2k)` at `(32, 8)` → confirmed `Φ = ρ⁹ - 16ρ`.
2. Develop rigorous proof for `(3k/2, 2k)` family.
   - `deg u_± = k/2 > 0` (no longer constants like Note 0219).
   - But `H_+ - H_- = -2` (constant) still holds.
   - `lc(u_±) = -ρ` from leading-term matching.
   - Need new structural argument; Note 0219 quadratic-in-σ_+ collapse
     does not apply directly.
3. Classify pencils by `gcd(a, b, n)` factorization. The (3k/2, 2k)
   pencil factors as `z^{3k/2}(ρ + z^{k/2})` — the binomial period k/2
   is half the (k, 2k) period. Investigate how the binomial period
   interacts with `n = 4k` to produce the additional `ρ⁴ = 4` solution.
