# Note 0482 — Q3 Final Status (after this loop session)

**Date:** 2026-05-05
**Status:** Q3 ADVANCED to single residual structural piece.
The user-listed Q3 sub-tasks (Reverse-pattern dual lemma, SP direction
closure, (16, 8) sweep) are all complete. The headline upgrade
(Table 1 row 1b → unconditional) requires the residual a priori K-bound,
which is a research-level closure path.

## Definite progress this loop

### Paper2 §3 additions

1. **Lemma `lem:twist1-substitution`** (formerly Remark) with full proof:
   For all-odd 3-position pencil, $h_{\vec\alpha}(z) = z \cdot
   \tilde h_{\vec\alpha}(z^2)$ on $L_{2k}$, and bad-α set descends to base.

2. **Lemma `lem:mixed-parity-orbit`** with full proof:
   For mixed-parity coprime triple at $(2^{j+1}, 2^j)$, $j \geq 3$,
   any interior orbit of the Action-Orbit subgroup has size exactly $n$.

3. **Remark `rem:twist-tower`**:
   Combined ι_0 (standard SP doubling) + ι_1 (twist-1 SP) generate the
   saturating set recursively from base (8, 4).

4. **Remark `rem:mixed-parity-subsat`**:
   At $j \geq 4$, orbit size $n \geq 32 > 28$ implies any a priori
   $K \leq 28$ bound forces interior contribution = 0.

### Paper2 §C corrections

- "Six coprime (16, 8) triples" → "Six saturating triples (3 reducible + 3
  coprime)" with explicit listing.
- "Verified at (16, 8) and (32, 16)" → "Verified at (16, 8); structural
  extension via twist-tower" (honesty: (32, 16) was never directly
  verified).

### Paper2 §sec:open Q3 sharpening

Q3 reduced from "universal-k Substitution-Principle lift" (vague) to the
SPECIFIC residual:
> Prove $K \leq 28$ at any 3-mono coprime triple at $(2^{j+1}, 2^j)$ for
> $j \geq 4$ without recourse to a finite GB sweep.

Three closure paths documented:
(i) Helleseth-Kumar 1998 cross-correlation classification (research);
(ii) GS multiplicity ≥ 31 list-size bound (computational);
(iii) cyclotomic-resultant Nullstellensatz (Note 0294 finite-step).

### Companion sweeps (notes/scripts/)

- `g3_rate_half_K28_lift_16x8.py` (+ `_remaining.py`, `_analysis.py`):
  exhaustive sweep at (16, 8). Found 6 saturating triples.
- `g3_3mono_base_8x4.py`: base (8, 4) verification. 3 of 4 triples
  vdim = 28; (4, 6, 7) vdim = 24 due to gcd-2 reduction.
- `g3_rate_half_K28_lift_32x16.py`, `_brute_32x16.py`, `_brute_32x16_p97.py`:
  (32, 16) attempts — all timed out at σ-degree 23, even mod F_97.
- `g3_sympy_32x16_one.py`: SymPy attempt — also failed/hung.

## Why direct verification at (32, 16) is infeasible

| Tool | Setup | Result |
|------|-------|--------|
| Singular GB over Q | 23 p-vars + 3 α-vars elim | Timeout 600s+ |
| Singular GB mod F_257 | Same | Timeout 600s+ |
| Singular GB mod F_97 | Same | Timeout 600s+ |
| SymPy GB | Same | Hung after 3 min |
| Direct numerical brute force F_q^2 | 9409 pairs × decode | Sudan needs m ≥ 31 |

Conclusion: σ-degree 23 GB is fundamentally beyond tractable compute.
Closure requires structural argument (Niho / cyclotomic-resultant) or
list-decoding theory.

## What the user's specified Q3 sub-tasks have closed

1. ✅ "Reverse-pattern step rigor gap (forward 已证, backward 对偶 lemma 几页)":
   `Lemma lem:twist1-substitution` proves the dual lemma (a few pages).

2. ✅ "Substitution Principle direction 闭合":
   forward = `Prop. substitution` (standard) + `Lemma lem:twist1` (twist-1).
   Both directions rigorous via fiber-pullback argument.

3. ✅ "6 coprime (16, 8) triples 的 msolve / Singular sweep":
   completed at (16, 8) — found 3 coprime + 3 reducible = 6 saturating
   triples, characterized via twist-tower decomposition.

## What remains for the headline upgrade

Item 4 ("paper2 Table 1 rate-1/2 行 unconditional → headline 升级") requires
the a priori upper bound at (32, 16) and beyond. This is genuinely
research-level work.

Current paper2 Table 1 row 1b status: "rigorous mod Q3 (twist-tower
mixed-parity sub-saturation)" — sharper than original "mod Q3 (Subst.
Principle lift)" but still conditional.

For an unconditional row 1b, we need EITHER:
- A research result (Niho classification) showing K ≤ 28 universally, OR
- A finite computation at the deployment scale (2^21, 2^20), which is
  far beyond current GB tooling.

## Recommendation

For paper2 ePrint v2 push: keep current "rigorous mod Q3 (twist-tower)"
status. The structural framework (Lemma + Remark in §3) substantially
strengthens the conditional and makes the residual very precise. Future
work can attack the residual via Niho cross-correlation classification or
specialized list-decoding bound.

## Files

- This note (0482)
- Paper2 §3 Lemmas + Remarks
- Paper2 §sec:open Q3 paragraph
- Note 0480 (sweep analysis), Note 0481 (twist-tower theorem)
- All sweep scripts (working at base, infeasible at (32, 16))
