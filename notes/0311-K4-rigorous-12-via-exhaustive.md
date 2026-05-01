# Note 0311 — Exhaustive (1, 2, 6, 7) sweep refutes K_4 ≤ 9 universal

**Date:** 2026-04-30 evening
**Status:** **#406 cannot close to K_4 ≤ 9 RIGOROUS** — exhaustive enumeration
at q = 1153 yields max $K_4 = 12$ for (1, 2, 6, 7), exhibiting the
Bezout-12 algebraic ceiling realizes in $\mathbb{F}_q$ for some primes.
The $K_4 \leq 9$ EMPIRICAL claim from Notes 0296/0298 was a sampling
artifact at q ≤ 449.

This affirms paper2's existing **K_4 ≤ 12 RIGOROUS** bound (Note 0295)
as the correct one. No improvement to K_4 ≤ 9 is possible.

## Result

| $q$ | (ρ_2, ρ_3) pairs enum'd | max $K_4$ | $K=12$ count | distribution |
|---|---|---|---|---|
| 97 | 9216 | 9 | 0 | $\{0: 6912, 1: 192, 4: 1152, 8: 576, 9: 384\}$ |
| 193 | 36864 | 9 | 0 | $\{0: 26880, 4: 6912, 5: 384, 8: 1920, 9: 768\}$ |
| 257 | 65536 | 9 | 0 | $\{0: 47616, 1: 512, 4: 14848, 8: 1536, 9: 1024\}$ |
| 449 | 200704 | 9 | 0 | $\{0: 144256, 1: 896, 4: 45696, 8: 8064, 9: 1792\}$ |
| **1153** | **1327104** | **12** | **2304** | $\{0: 997632, 1: 2304, 4: 276480, 8: 43776, 9: 4608, \mathbf{12: 2304}\}$ |

The transition from "max = 9" to "max = 12" between $q = 449$ and $q = 1153$
shows the Bezout-12 ceiling is realized in $\mathbb{F}_q$ for some primes,
even when smaller $q$'s show max = 9.

## K = 12 witnesses at q = 1153

```
(ρ_2, ρ_3) = (1, 440)
(ρ_2, ρ_3) = (1, 713)   [= 713 ≡ -440 mod 1153]
(ρ_2, ρ_3) = (2, 273)   [= ρ_3/ρ_2 ≡ 713 ≡ -440]
```

All 3 witnesses lie on the **2-element** locus $\rho_3/\rho_2 \in
\{440, -440\}$ (two ratios in $\mathbb{F}_{1153}$, i.e., a single
$\rho_3^2 = 1049 \rho_2^2$ relation since $440^2 = 1049 \mod 1153$).

This is a *characteristic-dependent* hypersurface in $(\rho_2, \rho_3)$-space:
- At $q = 97, 193, 257, 449$: the analog of "440" is empty (no $r$ with the right algebraic property)
- At $q = 1153$: $r = 440$ realizes, K = 12 happens at $\rho_3^2 = 1049 \rho_2^2$

## Why my earlier hypothesis was wrong

I hypothesized a Galois obstruction:
$$\chi(\beta_1)\chi(\beta_2)\chi(\beta_3) = \chi(\beta_1\beta_2\beta_3) = 1$$
prevents all 3 cubic β-roots from being 4-th powers simultaneously.

This is **incorrect**. The character relation only constrains the *product*,
not individual values. (1, 1, 1) is consistent with the product being 1.
At specific $(\rho_2, \rho_3)$ where the cubic splits AND each root happens
to be a 4-th power, K = 12 realizes — exactly what happens at q = 1153.

## Implication for paper2 / #406

**#406 should be closed with conclusion**: K_4 ≤ 12 RIGOROUS UNIVERSAL is the
correct bound for (1, 2, 6, 7) at base case (8, 2). The $\leq 9$ improvement
is **not achievable** — counterexample at q = 1153 demonstrates K = 12.

Existing paper2 statement (`thm:caseC-K10` proof + §11 P3″):
- K_4 ≤ 12 RIGOROUS UNIVERSAL ✓ (no change)
- K_4 ≤ 9 EMPIRICAL was based on q ≤ 449 sample bias; at q ≥ 1153 the
  Bezout-12 ceiling realizes
- Update: state K_4 ≤ 12 RIGOROUS (universal), drop the $\leq 9$ empirical
  claim (it's misleading given q = 1153 evidence)

## Possible follow-up

The K=12 witnesses lie on a 1-dim hypersurface $H_q \subset \mathbb{F}_q^2$.
Could this be characterized algebraically (independent of $q$)?

If $H_q$ is characteristic-dependent (e.g., requires a specific cyclotomic
condition on $q$), then **K_4 ≤ 9 holds at $q$ where $H_q = \emptyset$**.
This would be a conditional improvement, not universal.

For $q = 97, 193, 257, 449$: $H_q = \emptyset$ → K_4 ≤ 9 EMPIRICAL RIGOROUS
For $q = 1153$: $H_q = \{(\rho_2, \rho_3) : \rho_3^2 = 1049 \rho_2^2\}$ →
K_4 = 12 realizes

Algebraic characterization of $H_q$ as a function of $q$ is open. If it's
related to $q \mod N$ for some explicit $N$, paper2 could state K_4 conditionally
on the deployment field's residue class.

## Files

- `notes/scripts/g3_4mono_267_exhaust_q.py` — exhaustive enumeration script
- `notes/scripts/g3_4mono_267_symbolic_factor.sing` — symbolic Φ derivation
- `/tmp/267_exhaust_{97, 193, 257, 449, 1153}.out` — outputs

## Conclusion

paper2's K_4 ≤ 12 RIGOROUS is the **correct universal bound** for (1, 2, 6, 7).
The $\leq 9$ empirical pattern at q ≤ 449 was a sampling/structural coincidence,
broken at q = 1153.

The $K(f) \leq K_4 + 1 = 13$ for 4-pos sparse $\hat f$ stands, and remains
the best RIGOROUS UNIVERSAL bound for the 4-mono extension.

**#406 closes as wontfix** (improvement not possible).
