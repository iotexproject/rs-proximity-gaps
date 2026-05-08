# Note 0384 — L2 prior-art survey + reduction options

**Date**: 2026-05-01

After K_0 verdict (Note 0383), surveyed prior art and reduction options for
Q1 universal (= L2). Honest synthesis below.

## What's dead (naive forms)

- **Davenport-Hasse / Jacobi sum** (Helleseth): R_4 ∉ Z[ζ_8] (Note 0382)
- **Hecke L-value over Hilbert class field of K_0** (3-school refined):
  h(K_0) = 1,709,193 — class field has degree 3.4M over Q, infeasible
- **Self-Similarity descent** (Tang-Ding alive line): already attempted in
  Note 0278 Attempt 1 — the slice gives R_{2d}|slice = R_d on V_d^prim ⊂
  V(I_chain^{2d}), but this doesn't tell us about V_{2d}^prim. Descent fails.
- **Lawrence-Venkatesh effective Mordell**: V_d^prim is dim 0 (finite point
  set), not curve/surface of general type. Wrong framework.

## What's been computed (rigorous, per-d only)

| Method | d=4 | d=8 | d=12 | d=16 |
|---|---|---|---|---|
| msolve vdim test (Q1) | ✓ 0.03s | ✓ 0.03s | n/a (3\|d) | grinding 7+ hr |
| Norm of F_d ≠ 0 (Q) | ✓ 88798417/8100 | computing | n/a | infeasible |
| Mahler M(F_d min poly) | ✓ M=88798417 | TBD | n/a | infeasible |
| p-adic v_p(Norm) | ✓ {2,3,5} only | TBD | n/a | infeasible |

All d=2^k tested: Q1 holds. **No counterexample found.**

## Prior art (sequence school)

Most relevant existing results, none directly applicable:

1. **Helleseth-Klove 1997**: cyclic codes / Welch-Gong sequence non-vanishing.
   General framework but specific theorems don't cover R_d's polynomial form.

2. **Niho cross-correlation 1972 + descendants**: 3-valued / 4-valued
   cross-correlation classifications. Closest cousin to "polynomial doesn't
   vanish on cyclotomic variety". But these are specific enumerations, not
   general theorems.

3. **Stickelberger 1890 (Gauss sum prime factorization)**: gives v_p of Gauss
   sums in Z[ζ_p]. Doesn't apply to R_d (not a Gauss sum).

4. **Bluher 2004 trinomial Galois orbit count**: used in our paper2 K-bound
   proofs. Doesn't bound R_d ≠ 0.

5. **Coulter-Matthews 1997 permutation polynomials**: specific PP families.
   No universal nonvanishing theorem.

6. **Carlet-Charpin-Zinoviev 1998 APN functions**: characterizations only.

7. **Smyth 1971 / Dobrowolski 1979 Mahler measure**: gives lower bound for
   M(F_d(α)) > 1 + ε. Confirms F_d non-cyclotomic but no per-d uniformity.

8. **Bombieri-Pila / Heath-Brown rational points**: bounds # rational points
   on a transcendental variety. Can't conclude {R_d=0} ∩ V_d^prim = ∅.

## Reductions to known problems

The **honest** reduction of Q1 universal:

```
Q1 universal  ⟺  ∀d=2^k, Norm_{K_d/Q}(R_d) ≠ 0
              ⟺  ∀d=2^k, F_d(s) ∉ (H_d) ⊂ Q[s]
```

Where K_d = residue field of V_d^prim, H_d = Galois orbit polynomial.

Equivalent formulations (none is "known solved"):

- **(a) Schinzel-style polynomial non-vanishing**: "for explicit poly P(d), is
  P(d) ≠ 0 for all d in arithmetic progression?" — open in general, no
  effective bounds for our P.

- **(b) Hilbert irreducibility for parametric system**: chain ideal
  parameterized by d; ask if specialization preserves non-vanishing —
  HIT applies generically but not effectively for specific d.

- **(c) Z/d-equivariant cohomology non-triviality**: V_d^prim has Z/d-action;
  R_d represents a class in H*_Z/d(V_d^prim). Open.

- **(d) Heights of algebraic numbers in towers**: F_d(α) lives in tower of
  deg-D_d extensions; ask uniform height lower bound. No general theorem.

None are "known NP problems" — all are open research questions. **Reducing
Q1 universal to any of these is reducing to another open problem.**

## What's realistically actionable

### Path B (operational, what's been working)

For each d ∈ {2^k : k = 2, ..., 19} (deployment range):
1. Generate chain + R_d ideal
2. Run msolve to verify vdim(I_chain^d + R_d) = 1 (i.e., only origin)
3. If yes: Q1@d RIGOROUSLY proven
4. Store certificate

**Cost**: msolve scales d=4 (0.03s) → d=8 (0.03s) → d=16 (7+ hr, 187 GB).
At d=16 we're at the practical edge for single-machine. d=32, 64, 128 require
GPU/cluster compute or algorithmic improvement.

### Path A++ (open research, with Schmidt outreach)

Frame Q1 universal as: "non-vanishing of an explicit algebraic value
F_d(α) ∈ K_d / Q across all d=2^k". Hand to Bernhard Schmidt (NTU) with:
- Note 0277 (d=4 rigorous decomp)
- Note 0382 (cyclotomic Stickelberger structure at d=4)
- Note 0383 (K_0 verdict — h=1.7M)
- This note (prior art survey)

Cost: 6+ months expert time, no guaranteed result.

## Decision (this session)

1. Continue d=8 over Q msolve (PID 31195) for Norm computation
2. Continue d=16 grinding (PID 88491) for vdim closure
3. Update task list (DONE)
4. Frame paper2 §6 as Tang-Ding (a) — Q1 as named open problem of bounded
   scope, with K_0 = Q[√-83860066393667] discriminant footprint as
   characterization
5. Schmidt outreach package (when d=8 data lands)

**This is not abandonment**: per-d rigorous closure at deployment scale is
sufficient for prize submission, IF we can get msolve to scale (or move
to GPU FGLM).

## Files referenced

- `notes/0277-Q1-rigorous-d4-explicit-decomposition.md` — d=4 rigorous
- `notes/0278-universal-Q1-attack-status.md` — 8 attempted attacks, all open
- `notes/0382-Q1-cyclotomic-Stickelberger-d4.md` — cyclotomic
- `notes/0383-K0-class-number-verdict.md` — K_0 h=1.7M verdict
- `notes/scripts/g3_stickelberger_vp_R4.py` — v_p computation
- `notes/scripts/g3_lehmer_mahler_R4.py` — Mahler measure
- `notes/scripts/g3_K0_class_group_diagnostic.py` — PARI K_0 diagnostic
