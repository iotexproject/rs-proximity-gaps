# Note 0320 — Hamming-K = q-1 saturation at 3-pos supp {n/2, n/2+1, n/2+2}

**Branch:** `feat/op1a-algorithm-fixes` (paper3) — cross-branch contribution to paper2.
**Date:** 2026-05-01
**Status:** Algebraic identity verified at (16, 4) p=97, c=2. Generalizes Note 0315 cycle 3 parity-aligned mechanism.

## Headline

For RS(n, k) with n = 2k', any 3-pos sparse pencil with support {n/2, n/2+1, n/2+2} gives Hamming-K = q-1 (full saturation) at τ = Johnson, for ANY choice of pencil coefficients.

This is a **structural algebraic identity** driven by ω^{n/2} = -1, NOT a numerical artifact.

## The identity

Let n=16, k=4, ω = primitive 16th root of unity over F_q with 16 | q-1. Pencil:
- f_i[j] = c_i[0]·ω^{8j} + c_i[1]·ω^{9j} + c_i[2]·ω^{10j}, j = 0, ..., 15
- h_α[j] = f_1[j] + α·f_2[j] = (c_1[0] + α·c_2[0])·ω^{8j} + (c_1[1] + α·c_2[1])·ω^{9j} + (c_1[2] + α·c_2[2])·ω^{10j}

Define candidate codeword cw with message msg = (c_1 + α·c_2, 0) ∈ F_q^4 (i.e., msg[0:3] = c_1 + α·c_2 element-wise, msg[3] = 0):
- cw[j] = (c_1[0] + α·c_2[0]) + (c_1[1] + α·c_2[1])·ω^j + (c_1[2] + α·c_2[2])·ω^{2j}

Difference e[j] = h_α[j] - cw[j]:
- For each i ∈ {0, 1, 2}: contribution (c_1[i] + α·c_2[i]) · (ω^{(8+i)j} - ω^{ij})
- Factor: ω^{(8+i)j} - ω^{ij} = ω^{ij} · (ω^{8j} - 1)
- ω^{8j} - 1 = (-1)^j - 1 = 0 for j even, -2 for j odd

**Therefore e[j] = 0 for all even j.** Half the positions (j = 0, 2, 4, 6, 8, 10, 12, 14) — 8 positions — have e[j] = 0, regardless of (c_1, c_2, α).

Hamming weight of e ≤ 8 = Johnson radius J at (16, 4). Hence d_H(h_α, cw) ≤ J for **every** α ∈ F_q^*, giving K = q - 1.

## Empirical verification

Script: `notes/scripts/contrib_paper2/debug_K96.py`. Verified at (16, 4) p=97 with (c_1, c_2) = ([1,2,3], [1,3,5]):

```
Min-Hamming-distance distribution over α=1..96:
  1 α gives min-dist 6 (some odd-j entries cancel)
  13 α give min-dist 7
  82 α give min-dist 8 (= J, generic case)
  → all 96 α within Johnson, K = 96 = q-1
```

## Generalization to n/2 = 2^{k-1}

The mechanism requires ω^{n/2} = -1 (always true for n even, ω primitive n-th root in field with n | q-1). Generalizes to:

**Theorem (parity-aligned saturation at supp {n/2, n/2+1, ..., n/2+(k-1)}):**
For RS(n, k) with n even, the 3-pos (more generally, k-pos) pencil with support {n/2, n/2+1, ..., n/2+(k-1)} admits, for every α, a codeword msg = c_1 + α·c_2 (component-wise on first k positions, 0 elsewhere) at Hamming distance ≤ n/2 = J. Hence K = q-1.

For (16, 4): supp = {8, 9, 10, 11} 4-pos extension also saturates (confirms paper3 §sec:setup multi-position saturation).

## Connection to paper3 Note 0315 cycle 3

Note 0315 (paper3-side cycle 3) gave parity-aligned 3-pos sparse at (16, 4, c=4) with supp ⊆ odd positions {5, 7, 9, 11, 13, 15}, achieving M = q-1 saturation via Q_E = z^8 ± 1 factorization.

This Note 0320 is a different parity-aligned construction:
- Supp = {n/2, n/2+1, n/2+2} (one element from "shift origin" n/2, two adjacent)
- Works at c=2 (rate 1/4 deployment), not just c=4
- Mechanism: ω^{n/2} = -1 forces e to vanish on even j (8 of 16 positions)

Both are instances of paper3's general saturation theme but with different structural drivers.

## Implication for `conj:sparse-worst` empirical

paper2 thm:universal-K10 (algebraic K_3 ≤ 10) is for above-Johnson δ in the FRI 2-round commit-curve syndrome rank framework. My K = q-1 finding here is **Hamming-K** at τ = Johnson exact, a **different object**.

The conjecture is NOT refuted: this saturation construction lives at exactly J (the Johnson boundary), and the conjecture talks about strict above-J. For δ > J (strict above), Hamming-K can be much smaller; the saturation here is δ = J specifically.

What this finding clarifies:

1. **Hamming-K vs algebraic-K**: at τ = J exactly, certain structured pencils (parity-aligned, supp {n/2, n/2+1, ...}) achieve Hamming-K = q - 1. This is an algebraic identity, not random alignment.

2. **For above-J empirical**: must use τ > J (e.g., τ = J - 1 via Sudan(m=2) at (32, 8), giving τ = 15 < 16). At τ < J, Hamming-K is much smaller and matches paper2's framework better.

3. **The trivial saturation sub-locus** (paper3 Note 0316 cycle 4, |S*| ≤ w) and this Note 0320's parity-aligned saturation are **different mechanisms**:
   - Trivial sat (cycle 4): joint support ≤ w, saturation in M (realizer count)
   - Parity-aligned (Note 0315 cycle 3 + Note 0320): specific positional structure forcing Hamming-K = q-1 via algebraic vanishing

Both are paper3-internal saturation phenomena at τ = J boundary. paper2's K_3 ≤ 10 holds for δ > J strictly, where these saturations don't apply.

## Files

- `notes/scripts/contrib_paper2/debug_K96.py` — empirical verification at (16, 4) p=97
- `notes/scripts/contrib_paper2/verify_K96_trivial_saturation.py` — disproves trivial-sat hypothesis (other |S*| ≤ w cases give K=0)

## Cross-refs

- paper3 Note 0315 (cycle 3) — parity-aligned at (16, 4, c=4)
- paper3 Note 0316 (cycle 4) — trivial saturation sub-locus {|S*| ≤ w}
- paper3 §sec:setup — saturation regime
- paper2 thm:universal-K10 — algebraic K_3 ≤ 10 for δ > J strict
- paper2 conj:sparse-worst (Issue #419)
- This Note 0320 — Hamming-K saturation at τ = J via supp {n/2, n/2+1, n/2+2}
