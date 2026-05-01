# Note 0131 — Case-B attack: Session 1 (diagnosis + MDS-syzygy lemma)

**Date**: 2026-04-30
**Branch**: main
**Goal**: Crack case-B over 3-5 sessions to enable fully-unconditional Theorem 3.1 of paper 3.
**Status**: Session 1 of 5. MDS-syzygy lemma proved + empirically verified. Cognitive reset on "leading auto case-A". Attack vectors for sessions 2-5 documented.

## The gap (precise restatement)

Paper 3 §5.3 (`lem:reduction`) builds case-A realizer $E^A_l := T_{γ_l} \cup \{w - |T_{γ_l}|\}$ extras, requires $|T_{γ_l}| \leq w$. This holds in case A by Vandermonde-LI of $E \cup S^*$. **In case B it can fail**: empirical (this note) shows $|T_γ| > w$ at deployment params.

Note 0119's identification (line 117-122):
> An alternative support $T' \subset E_l$ with $|T'| \leq w$ but $T' \not\subset S^*$ might exist — the structural dependencies among $\{ev_v : v \in L\}$ ... provide exactly the room.

Note 0122 silently assumed `|T_γ| = Hankel rank ≤ w`, but that equation only holds when $|T_γ| \leq D/2$ (uniqueness regime).

## Lemma 1 (MDS-syzygy) — RIGOROUS

**Statement**: Let $(γ, E)$ be a realizer of $x_γ$ with $|E| = w$. Suppose the intrinsic representation $T_γ \subseteq S^*$ differs from $E$ as supports of $x_γ$. Then
$$
|T_γ \cup E| \;\geq\; D + 1.
$$

**Proof**: Two representations of $x_γ$:
$$
x_γ = \sum_{v \in T_γ} c_v \mathrm{ev}_v = \sum_{u \in E} \xi_u \mathrm{ev}_u
$$
with all $c_v, \xi_u \neq 0$. Subtracting yields a non-trivial Vandermonde syzygy
$$
\sum_v a_v \mathrm{ev}_v = 0, \quad a_v = c_v \mathbf{1}_{v \in T_γ} - \xi_v \mathbf{1}_{v \in E}.
$$
Support contains $T_γ \triangle E$ (where $a_v$ is $\pm c_v$ or $\pm \xi_v$, both nonzero). By the MDS property of Vandermonde matrices over $\FF_q$ (any $D$ rows of the matrix $[\mathrm{ev}_v]_{v \in [n]}$ are linearly independent), every non-trivial syzygy has support of size $\geq D + 1$. Hence $|T_γ \cup E| \geq |\text{supp}| \geq D + 1$. ∎

**Corollary 1.1**: $|T_γ \setminus E| \geq D + 1 - w = c + 1$. So $|T_γ| \geq c + 1$ in any case-B-alt realizer.

**Corollary 1.2**: $T_γ \subseteq S^*$ ⟹ $|S^*| \geq c + 1$. (Auto at deployment $|S^*| \geq w+1 \geq c+1$, not new.)

## Empirical validation (script: `notes/scripts/case_b_mds_probe.py`)

Sweep over $(n, c, p) \in \{(8, 3, 17), (10, 3, 41), (12, 3, 41)\}$, $D = 2c+1$, $w = c+1$, $T = (2D-1)/c$.

| $(n, c, p)$ | case-B realizers seen | with alt-support ($\|T_γ\| > w$) | $\|T_γ\|$ obs | MDS violations |
|-------------|-----------------------|------------------------------------|-----------------|----------------|
| (8, 3, 17)  | 0                     | 0                                  | —               | 0              |
| (10, 3, 41) | 4                     | 4                                  | 5 = w+1         | **0**          |
| (12, 3, 41) | 4                     | 4                                  | 5 = w+1         | **0**          |

**Conclusion**: case-B alt-support is real (8 cases observed); MDS-syzygy lemma holds in all of them.

## Cognitive correction: "leading auto case-A" was wrong

Earlier session reasoning: "$|S^*| = w+1$ and $|E| = w$ ⟹ $|E \cup S^*| \leq 2w+1 \leq D$ (unique decoding)".

**Error**: $w \leq (D-1)/2$ would imply $2w+1 \leq D$, but at deployment-scale paper3, $M > T$ event itself forces non-unique decoding (multiple realizers per $γ$). The empirical test setup at $D = 2c+1, w = c+1$ already has $w > (D-1)/2 = c$, thus case-B can occur in leading stratum.

**Implication**: Path (c) "c ∈ {3, 4} is unconditional via auto-case-A in leading" **fails**. Case-B affects all $c$. Hence:
- **path (c) revised**: all $c$ are conditional on case-B (with 340/340 + 8/8 empirical).
- **path (b) "absorb to sub-leading" also fails** (since case-B is in leading too).
- **Cracking case-B remains the only path** to fully-unconditional Theorem 3.1.

This actually **strengthens the case for the 3-5 session attack**: the prize is bigger.

## Attack vectors for sessions 2-5

### V1. Multi-realizer joint MDS chain (sessions 2-3 priority)

For T+1 realizers $(γ_l, E_l)_{l=1}^{T+1}$ with case-B alt-supports, each contributes a syzygy of support $\geq D + 1$. The T+1 syzygies share the $T_{γ_l}$'s, all $\subseteq S^*$. 

**Key combinatorial constraint**: $\bigcap_l f^{-1}(γ_l) = \emptyset$ (γ_l distinct), so $\bigcup_l T_{γ_l} = S^*$. Each $T_{γ_l} = S^* \setminus f^{-1}(γ_l)$.

For $|T_{γ_l}| > w$: $|f^{-1}(γ_l)| < |S^*| - w = δ'$. In leading $δ' = 1$: $r(γ_l) = 0$, all γ_l avoid f-image.

**Subclaim** (to prove): for T+1 case-B alt realizers in leading (all r=0), the $E_l \setminus S^*$ pieces interact in a way that forces high codim.

Each E_l has $|E_l \setminus S^*| \geq c$ (from MDS Corollary 1.1: $|T_{γ_l} \setminus E_l| \geq c+1$, so $|E_l \setminus T_{γ_l}| = |E_l| - |E_l \cap T_{γ_l}| \geq w - (w+1) + \dots$, hmm let me redo).

Actually wait, we have $|T_γ \cup E| \geq D+1$ ⟹ $|T_γ| + |E| - |T_γ \cap E| \geq D+1$ ⟹ $|T_γ \cap E| \leq |T_γ| + w - D - 1$. With $|T_γ| = w+1$ (leading case-B alt): $|T_γ \cap E| \leq 2w - D = -2(c - w) + ... $ hmm let me just compute.

For unique-decoding-regime test $(n=10, c=3, p=41, D=7, w=4)$: $|T_γ \cap E| \leq |T_γ| + 4 - 8 = |T_γ| - 4$. With $|T_γ| = 5$: $|T_γ \cap E| \leq 1$.

So in our empirical case-B alt cases: $|T_γ \cap E| \leq 1$. Most of $E$ is outside $S^*$.

This is a **strong structural constraint** to exploit in session 2.

### V2. Hankel-rank determinantal Bezout (session 3 backup)

For each γ, $x_γ$ has Hankel rank $\leq w$ (algebraic, not combinatorial-on-[n]) — given by vanishing of $(w+1) \times (w+1)$ Hankel minor. As poly in γ: degree $w+1$.

For T+1 distinct γ's vanishing: if $T+1 > w+1$ (i.e., $T > w$, low D): identical zero in γ. But at deployment $T < w$, so generic.

The CONSTRAINT is "min algebraic support of $x_γ$ lies in $[n]$". This is what introduces the $|F|^{-(c-1)}$ factor in BCIKS. Lifting to $|F|^{-2(c-1)}$ for T+1 distinct γ's: this is exactly what we need.

**Subclaim**: relate case-B alt-support to Hankel-rank loci structure on the line $\{x_γ : γ\}$.

### V3. Sequence-school: Niho/Welch cross-correlation (session 3 backup)

The ratio function $f: V_1 \to \FF_q$, $f(v) = -α_v/β_v$, is the central object. Its image distribution governs M.

For "all T+1 realizers case-B alt" (extreme): $\{γ_l\} \cap f\text{-image} = \emptyset$. This is a constraint on $f$.

Niho-style cross-correlation between $f$ and a constant sequence might give cardinality bounds via character sums (à la Helleseth 1976 thesis). This is the Gong/Helleseth wheelhouse.

### V4. Pivot to direct AG codim count (session 5 fallback)

If V1-V3 fail to close:
- Skip the case-B reduction entirely
- Compute codim of $\{(s_1, s_2) : \text{at least one case-B alt realizer in M-tuple}\}$ directly
- Show this stratum has codim $\geq 2(c-1) + \epsilon$

This gives the lower bound without needing $|T_γ| \leq w$. Not "satisfying" structurally but suffices for paper3.

## Files this session

- `notes/scripts/case_b_mds_probe.py` — empirical MDS check (this note's table)
- `notes/0131-case-b-attack-session1.md` — this note

## Status going into session 2

- Lemma 1 (MDS-syzygy): rigorous + empirical-validated
- Cognitive reset: case-B affects all c, path (c) needs path (b) backup
- Vector V1 (multi-realizer joint MDS) is the primary attack
- Subclaim to prove session 2: T+1 case-B alt realizers in leading + MDS chain → high codim contradiction or |S*|-bound

## What this note is NOT

- Not yet a proof of Conjecture B
- Not yet a paper3 patch (waiting for session 4)
- Doesn't address Lemma A (separate branch)
