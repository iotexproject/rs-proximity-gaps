# Note 0483 — Q3 Expert Consultation: Gong + Helleseth

**Date:** 2026-05-05
**Purpose:** Two senior sequence-school experts consulted on the residual
Q3 closure: prove a priori $K \leq 28$ at any 3-mono coprime triple at
$(2^{j+1}, 2^j)$ for $j \geq 4$ without finite GB sweep.

## Gong (Waterloo) recommendation: BKK / Newton polytope mixed-volume

**Key insight**: Note 0294's $z = u^d$ substitution = $d$-fold dilation in
Newton polytope coordinates. Mixed volume is **invariant** under uniform
scaling (after normalization). Hence the eliminator-polynomial Newton
polytope mixed volume at base $(8, 4)$ propagates uniformly to every
$(2^{j+1}, 2^j)$ in the dyadic tower.

**Concrete plan**:
1. Compute Newton polytope $P_{\text{base}}$ of cert+div equations at
   $(8, 4)$ saturating triples. Verify $\text{mixed\_vol}(P_{\text{base}},
   P_{\text{base}}) = 28 = \binom{8}{6}$.
2. This converts $28 = \binom{8}{6}$ from "combinatorial coincidence" to
   **geometric invariant**.
3. Note 0294 substitution = mixed-volume preserving: gives uniform bound
   $K \leq 28$ at every dyadic scale, no GB recomputation needed.

**Why other paths are weaker** (per Gong):
- van Lint–Wilson / Vandermonde: bounds $\text{dist} \geq$ (lower bound),
  wrong direction for $K \leq$ (upper bound).
- Schönhage-Strassen finite-step verification: clean but cycle-by-cycle,
  not uniform.
- Decimation diagnostics: useful for orbit classification, not as
  upper-bound proof.

**First step**: compute $P_{\text{base}}$ via polymake/Sage NewtonPolytope
on the 6 saturating triples. Verify mixed volume = 28.

## Helleseth (Bergen) recommendation: HT + Roos bound

**Key insight**: 3-mono pencil has linear complexity exactly 3. The
Hartmann-Tzeng bound (Hartmann-Tzeng 1972) on cyclic codes with
consecutive defining sets, augmented by the Roos bound (Roos 1983) on
non-consecutive zero patterns, gives a uniform-in-$j$ K-bound.

**Caveat**: Helleseth's specific formula
"$K \leq \binom{n/2}{n/2-1}|_{n=8} = 28$" appears to have a typo:
$\binom{4}{3} = 4 \neq 28$. The intended formula is likely
$\binom{n}{n-2}|_{n=8} = 28$, but the correct statement of the bound
requires the original paper.

**Recommended references**:
- Hartmann-Tzeng, *Inform. Control* 1972.
- Roos, *IEEE Trans. Inform. Theory* 1983 (Thm 2).
- Lahtonen-McGuire-Ward 2007 (cited in subagent response, possibly in
  *Adv. Math. Comm.* not FFA — to verify).
- Helleseth-Lahtonen-Rosendahl 2007 (Niho cross-correlation, FFA 13).

**Concrete plan**:
1. Write up the HT + Roos argument explicitly for our cyclic-group setting.
2. Apply to our cyclic code $C^{\text{aug}} = \mathrm{RS}_k(L_n) \oplus
   \langle z^{a_1}, z^{a_2}, z^{a_3} \rangle$ with defining set
   $[k, n-1] \setminus \{a_1, a_2, a_3\}$.
3. Bound min dist of $C^{\text{aug}}$ uniformly via HT ≥ structure.
4. Translate to $K$-bound via list-decoding considerations.

**Other Helleseth recommendations**:
- Niho exponent decomposition (Dobbertin FFA 1999) for mixed-parity:
  splits pencil into single-even + 2-mono-odd, applies shortened-RS bound
  giving $K_{\text{mixed}} \leq n - k = n/2$. Combined with our orbit-size
  Lemma collapses to $K \leq 4$ as observed at (16, 8).
- Linear-complexity-3 + HT ≥ $n - k - 2$ uniformly (Hartmann-Tzeng).
- Decimation diagnosis to classify orbits (not as proof).

## Comparison of paths

| Path | Tractability | Result | Dependencies |
|------|--------------|--------|--------------|
| Gong (BKK / mixed-vol) | Medium (polymake/Sage compute) | $K \leq 28$ uniform in $j$ | Note 0294 substitution invariance + base mixed-volume verification |
| Helleseth (HT + Roos) | Hard (paper-level proof) | Likely $K \leq O(n)$ generically; saturating $K = 28$ at structured triples | HT + Roos bounds + Niho decomposition for mixed-parity |
| Direct Sudan/GS list decoder | Computational, expensive | Empirical at (32, 16) | $m \geq 31$ multiplicity, $\sim 6$ hours for 16-triple sample |

## Recommendation for paper2 push

Given that both research-level paths require substantial follow-up work,
the pragmatic choice is to KEEP the current "rigorous mod Q3
(twist-tower + mixed-parity sub-saturation)" wording for paper2 ePrint v2.

The structural Lemmas already in paper2 §3 (Lemma~`lem:twist1-substitution`,
Lemma~`lem:mixed-parity-orbit`) reduce Q3 to a single, sharp residual:
"prove $K \leq 28$ a priori at $(32, 16)$ and beyond". Future work can
attack via either path.

## Files

- This note (0483)
- Notes 0480–0482: Q3 closure framework
- Subagent transcripts in conversation log
