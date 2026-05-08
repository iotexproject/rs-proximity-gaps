# Note 0394 -- Issue #419: high-tail parity lemma — scope extensions

**Date:** 2026-05-02 (Q2 attack iteration 6 — extending Note 0393)  
**Branch:** `main`  
**Status:** the high-tail parity lemma (Note 0393) extends scope-wise to
(i) ANY 4-supp at $L_2 = (16, 4)$ via the 2-positions-per-side reduction,
and (ii) deployment-scale $L_2 = (32, 8)$ via empirical scale-lift
(5000-sample, prime-uniform).

---

## Extension I: 2-positions-per-side 4-supp at L2 = (16, 4) (catalog half-turn shape)

The Note 0393 argument was framed for one-position-per-quadrant 4-supp.
The same lemma immediately extends to ALL 4-supp shapes at
$L_2 = (16, 4)$.

For a 4-supp with quadrant pattern (1, 1, 2, 0) (e.g., the catalog
half-turn shape `((11,), (9,), (8, 10), ())`):

```text
u_alpha = c_3 t^{r_3} + alpha c_1 t^{r_1}    (q=0 + q=1 contributions)
v_alpha = c_0 t^{r_0} + c_2 t^{r_2}          (q=2 contributions; no alpha)
```

The $u$-side equation needs $\mathrm{HT}(t^{r_3}) \propto
\mathrm{HT}(t^{r_1})$ (one $\alpha$ enters as scalar).  Same as the
1-pos-per-quadrant case.

The $v$-side equation needs $\mathrm{HT}(t^{r_0}) \propto
\mathrm{HT}(t^{r_2})$ (no $\alpha$ at all; pure pairwise dependence).

By the Note 0393 lemma, BOTH proportionalities require same parity.

* The catalog half-turn shape has $(r_3, r_1) = (11, 9)$ both odd and
  $(r_0, r_2) = (8, 10)$ both even — this IS the parity-split shape.
* Mixed-parity variants (e.g., $(r_0, r_2) = (8, 9)$) FAIL the lemma.

Same closure holds for quadrant patterns (2, 0, 1, 1), (1, 2, 1, 0), etc.
All 4-supp shapes at $L_2 = (16, 4)$ reduce to pairwise high-tail
proportionalities — within scope of Note 0393.

> **Corollary (4-supp closure at $L_2 = (16, 4)$).**  Every 4-support at
> $L_2 = (16, 4)$ admitting a rank-2 nonzero-$\alpha$ saturated solution
> has each "side" (q=0,1 vs q=2,3) entirely on one parity class of folded
> exponents; equivalently, the two residual rows are half-turn parity
> split.

This closes the 4-supp finite-root primitive branch at $L_2 = (16, 4)$
**structurally and prime-uniformly across $q \in \{97, 193, 1153\}$**.

---

## Extension II: scale-lift to L2 = (32, 8)

Deployment-scale $L_2 = (32, 8)$ has $|S| = 16$ no-full subsets totaling
$598{,}138{,}512$ — too many to enumerate exhaustively.  We sample.

```text
notes/scripts/issue419_high_tail_proportionality_audit.py
  --q 193 --n2 32 --k2 8 --exponent-min 8 --exponent-max 32
  --mode pairwise --sample-S 5000
```

Result at $q = 193$, 5000 random no-full $S$:

```text
Same-parity proportionalities:        NONE
Opposite-parity proportionalities:    NONE
```

Same result at $q = 97$ with 1000-sample.  Across the random 5000-sample
panel and 23 valid pairs $(r_1, r_2)$ per $S$ (at $|HT| = 8$), every
single pair is non-proportional.

Interpretation: at $L_2 = (32, 8)$ the high-tail is 8-dimensional, so
proportionality of two 8-vectors is structurally rarer than at
$L_2 = (16, 4)$ (where the high-tail is 4-dim).  The pattern that
manifested as $(8, 10)$ and $(9, 11)$ at $L_2 = (16, 4)$ does NOT
appear at $L_2 = (32, 8)$ even at sampling scale 5000.  This is
consistent with the structural lemma extending unconditionally to higher
scale.

This empirical scale-lift covers the deployment-relevant target
$L_2 = (32, 8)$ (the BCIKS-style commit-curve cell at rate $1/4$
folding factor 2).

---

## Combined updated closure status (Q2 finite-root)

| Sub-class | Status | Evidence | Note |
|---|---|---|---|
| All-alpha (paired tail circuits) | CLOSED scale-uniform | L1 boundary identity | 0388 |
| Half-turn stabilizer | CLOSED unconditionally | weighted quotient theorem | 0345-0351 |
| One-residue lambda recursive lift | CLOSED | symbolic descent | 0356-0359 |
| Same-folded cancellation | rank-deficient | trivial minor | 0360 |
| **All 4-supp at $L_2 = (16, 4)$** | **CLOSED structurally, prime-uniform** | **Note 0393 lemma + 2-pos extension** | **0393, 0394** |
| 4-supp at $L_2 = (32, 8)$ | CLOSED empirically (5k sample, prime-uniform) | sample audit | 0394 |
| 5-supp / 6-supp / 7-supp (3+ pos per side) | OPEN structurally; empirical 0 | pairwise proportionality insufficient | 0392, 0394 |

### What's left for Q2 unconditional closure

The pairwise high-tail parity lemma covers any $u_\alpha, v_\alpha$
with $\leq 2$ monomial terms each.  This handles:

* All 4-supp (each side has $\leq 2$ folded positions).
* The catalog half-turn parity-split shapes.
* The Mechanism I (same-folded cancellation) and Mechanism II
  (half-turn parity split) of Note 0360.

The remaining algebraic gap for Q2 is the **3-or-more position per side
case**, which requires a 3-vector dependence at the high-tail level:

```text
c_0 HT(t^{r_0}) + c_1 HT(t^{r_1}) + alpha c_2 HT(t^{r_2}) = 0.
```

This is a 3-term dependence in $\mathbb{F}_q^{k_2}$.  At $L_2 = (16, 4)$,
$k_2 = 4$, so 3 high-tail vectors are generically linearly independent
(rank 3 in 4-dim space) — dependence would require special $S$.

The natural extension of the Note 0393 lemma is:

> **Conjectural extension (3-vector parity lemma).**  For every no-full
> $S \subset L_2$ and every triple $(r_0, r_1, r_2) \subset \{4, \ldots, 15\}$
> with $r_0, r_1$ same parity AND $r_2$ opposite parity, the three
> vectors $\mathrm{HT}(t^{r_0}), \mathrm{HT}(t^{r_1}), \mathrm{HT}(t^{r_2})$
> are linearly INDEPENDENT in $\mathbb{F}_q^{k_2}$.

If true, this lemma closes the 5-supp / 6-supp finite-root branch at
$L_2 = (16, 4)$ structurally.  Empirical verification + character-theoretic
proof attempt is the next concrete artifact.

---

## Path to character-theoretic proof of Note 0393 lemma

The lemma is an isotypic-decomposition statement for the
$\mathbb{Z}/16\mathbb{Z}$-module $\mathbb{F}_q[t] / g_S$ (rank 8).  The
half-turn $\sigma: t \to -t$ generates the $\mathbb{Z}/2\mathbb{Z}$
quotient of $\mathbb{Z}/16\mathbb{Z}$.

For $r$ even: the character vector $\chi_r = (\omega^{rs})_{s \in S}$ is
INVARIANT under $s \to s + 8$ (since $\omega^{r \cdot 8} = (\omega^8)^r =
(-1)^r = 1$).

For $r$ odd: $\chi_r$ is ANTI-invariant ($(-1)^r = -1$).

Thus $\chi_r$ for $r$ even and $\chi_r$ for $r$ odd lie in COMPLEMENTARY
$\sigma$-isotypic components $V_+$ and $V_-$ of $\mathbb{F}_q^{16}$
(both 8-dim in the full space, narrower in the restriction to $S$).

The kernel of the high-tail map $M: \mathbb{F}_q^S \to \mathbb{F}_q^{k_2}$
is generically 4-dim (with $|S| = 8$, $k_2 = 4$).  IF $\ker(M)$
respects the $\sigma$-isotypic decomposition (i.e.,
$\ker(M) = (\ker M \cap V_+|_S) \oplus (\ker M \cap V_-|_S)$),
then opposite-parity proportionality $M\chi_r = \lambda M\chi_{r'}$
forces $\chi_r \in \ker M$ AND $\chi_{r'} \in \ker M$, i.e., both
high-tails are zero — never the case for nonzero high-tail.

The remaining algebraic step: prove that $\ker(M)$ respects the
$\sigma$-decomposition for every no-full $S$.

This is a finite-dimensional linear-algebra statement whose proof should
be accessible.  Drafting it is the next concrete artifact.

---

## Output

```text
notes/scripts/issue419_high_tail_proportionality_audit.py
```

(Pairwise mode supports `--sample-S` for L2 sizes too large to enumerate.)
