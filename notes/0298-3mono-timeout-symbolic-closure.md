# Note 0298 — 3-mono self-reflective timeout cases closed symbolically

**Date:** 2026-04-30
**Status:** RIGOROUS symbolic closure of the two Note 0291 self-reflective
3-monomial base cases at `(n,k)=(8,2)`.

## Target

Note 0291 proves the universal 3-monomial pencil bound `K_3 <= 9` by
reducing to irreducible base cases at `(4,1)` and `(8,2)`.  All but the
self-reflective pair

```text
(2,3,6), (2,5,6)
```

were discharged by SymPy GB or reflection.  Note 0291 used a `q=97`
numerical enumeration for this pair.  That was strong evidence, but not a
characteristic-zero eliminator certificate.

This note replaces the numerical patch with a direct Singular elimination
certificate over `QQ`.

## Method

For each pencil

```text
h_alpha(z) = z^a + rho z^b + alpha z^c
```

at `(n,k)=(8,2)`, set

```text
sigma(z) = z^4 + p3 z^3 + p2 z^2 + p1 z + p0.
```

Use the same cert+div ideal as `g3_3mono_base_cases.py`:

1. `sigma | h_alpha` in the high-degree coefficient range `d in {2,3}`.
2. `sigma | z^8 - 1`.
3. Eliminate `p0,p1,p2,p3` from the ideal in
   `QQ[p0,p1,p2,p3,alpha,rho]`.

Script:

```text
python3 notes/scripts/g3_3mono_singular_timeout_82.py --run --timeout 300
```

Output:

```text
notes/scripts/g3_3mono_singular_timeout_82.output.txt
```

## Certificate for `(2,3,6)`

The eliminator contains:

```text
11186563934477352960*alpha^4
 + 10654571229625*rho^40
 + 26732830634912127224*rho^32
 + 3207807790819288573200*rho^24
 - 57734795005565773722880*rho^16
 - 6940446899265672986624*rho^8
 - 11186563934477352960
```

For any fixed `rho`, this gives an `alpha`-polynomial of degree at most `4`.
Therefore the bad-alpha fiber has size at most `4`, counted with
multipity, outside the harmless specialization where the polynomial becomes
identically zero.  The eliminator also contains lower-degree mixed
relations, so the generic fiber is in fact finite; the degree-4 row is enough
for the `K_3 <= 9` ceiling.

## Certificate for `(2,5,6)`

The eliminator contains:

```text
6273*alpha^4
 - 4096*alpha^2*rho^24
 - 557056*alpha^2*rho^16
 - 65536*alpha^2*rho^8
 + 4096*rho^24
 + 557056*rho^16
 + 65536*rho^8
 - 6273
```

Again, for fixed `rho`, this is an `alpha`-polynomial of degree at most `4`;
the remaining eliminator rows include degree-2 and degree-3 mixed
constraints.

## Consequence

The two self-reflective timeout cases have symbolic `deg_alpha <= 4`
certificates over characteristic zero.  Thus Note 0291 no longer depends on
finite-field numerical enumeration for the last base cases:

```text
K_3 <= 9
```

is rigorous for all irreducible 3-monomial base cases at `(8,2)`, hence
universal by the 3-mono Substitution Principle.

## Files

- `notes/scripts/g3_3mono_singular_timeout_82.py`
- `notes/scripts/g3_3mono_singular_timeout_82.sing`
- `notes/scripts/g3_3mono_singular_timeout_82.output.txt`
