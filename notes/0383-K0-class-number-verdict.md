# Note 0383: Three-school diagnostic on K_0 — class number verdict

**Date**: 2026-05-01

## Summary

Three-school sequence experts (Helleseth + Gong + Tang-Ding) recommended running
PARI/Sage diagnostic on the imaginary quadratic field K_0 = Q(√-D), where
D = 83860066393667 is the unique squarefree-part prime of the discriminant of
the min poly of F_4(α) (Note 0382).

Decision rule from three-school consensus:
- h(K_0) ≤ 10 + LMFDB hit → 6-9 mo prize-grade structural proof possible
- h(K_0) ≤ 10 + no LMFDB hit → 18-24 mo construct new Hecke character
- h(K_0) huge → retreat to framing (a): Q1 open as standalone NT problem

## Result

```
PARI/GP version (2, 17, 2)

K_0 = Q(sqrt(-83860066393667))
  D = 83860066393667
  fundamental disc = -83860066393667 ✓
  -D ≡ 1 mod 4   (so O_{K_0} = Z[(1 + √-D)/2])

h(K_0) = 1,709,193
class group structure = Z/1709193Z (cyclic, single component)
```

**Verdict: h is HUGE** (~1.7 million). Hilbert class field of K_0 has degree
2 · 1,709,193 = **3,418,386** over Q. Hecke L-value computation in such a class
field is infeasible.

## Splitting of small primes in O_{K_0}

| p  | -D mod p | Behavior  | Note |
|----|----------|-----------|------|
| 2  | 1        | inert     | |
| 3  | 1        | **split** | bad-char hit |
| 5  | 3        | inert     | |
| 7  | 3        | inert     | bad-char hit |
| 11 | 8        | inert     | |
| 13 | 8        | inert     | |
| 17 | 10       | inert     | |
| 19 | 3        | inert     | |
| 23 | 2        | split     | |
| 29 | 5        | split     | |
| 31 | 7        | split     | |
| 37 | 3        | split     | |
| 41 | 30       | inert     | (41 is in trace, splits in Z[i]) |

paper2 bad-char {2,3,7} maps to (inert, split, inert) in O_{K_0} — mixed
pattern, no clean Stickelberger-style explanation.

## Numerical confirmation

The 6 roots of the min poly of F_4(α):
- 4 real: -13.27, 5.22, -5.39, 4.00
- 2 complex conj: 2.667 ± 0.456i
- Product = 10962.767... = **88798417 / 8100** ✓

## Decision

**Retreat to framing (a)**: Q1@d=4 is an open NT problem about the non-vanishing
of a specific algebraic value in a degree-6 field with imaginary quadratic
Galois resolvent, where the resolvent has class number 1,709,193.

This is a NAMED problem of bounded scope (not abandonment), but the structural
CM-isogeny lift route requires class field machinery of size 3.4M, which
neither sequence school nor the three subagent prescriptions can effectively
exploit at the prize timescale.

## What's still alive

1. **msolve operational closure** — per-d rigorous Q1 verification at deployment
   d ≤ 2^19 IF msolve scales. Currently grinding d=16 for 7+ hr.
2. **Per-d structural pattern** — d=8 still being computed; if it shows
   different Hecke conductor / class number pattern, this might rule out
   uniform CM-tower entirely (further negative evidence).
3. **Refined L2 partial** — accept Q1 universal as open conjecture; prize
   submission emphasizes L1 (sparse-class) + L3 (general-f) closure with L2
   per-d up to deployment scale.

## Action items

1. Update `conj_4_1_handoff.md` with this verdict
2. Frame paper2 §6 around "Q1 is an explicit open NT non-vanishing problem"
3. Continue waiting on d=8 elimination (negative confirmation only)
4. Stop msolve d=16 if it doesn't finish soon (cost > value at this point)
