# Note 0129 — Lemma A: empirical R_lead and tension with conjecture

**Date**: 2026-04-30 (post Bezout-night, attacking Lemma A)
**Branch**: `feat/berlekamp-c322`
**Status**: empirical finding; refines understanding of Lemma A's
quantitative content. Suggests the conjecture's $n^{O(c)}$ bound on
$\#\{\alpha : \ell(\alpha) \in V_\mathrm{bad}\}$ requires $q$ to scale
polynomially with $n$ — it does **not** hold at fixed moderate $q$ as
$n$ grows. Independent of whether the conjecture survives this
refinement, it sharpens what needs to be proved.

## Setup: leading-stratum reduction

Lemma A (Paper 3 §8.2 / `OPEN_PROBLEMS.md`): for a generic affine line
$\ell(\alpha) = (u_1 + \alpha v_1, u_2 + \alpha v_2) \in \FF_q^{2D}$,

$$
N(\ell) := \#\{\alpha \in \FF_q : \ell(\alpha) \in V_\mathrm{bad}\}
\;\stackrel{?}{\leq}\; n^{O(c)}.
$$

By Paper 3 Theorem 4.1, $V_\mathrm{bad} \subseteq
\bigcup_{|S|=w+1} V_S \times V_S$ (leading stratum), so

$$
N(\ell) \;\leq\; R_\mathrm{lead}(\ell) :=
\#\{S \subset [n], |S| = w+1 : \exists\,\alpha,\;
    \ell(\alpha) \in V_S \times V_S\}.
$$

For a generic line not parallel to any $V_S \times V_S$, each $S$
contributes at most one $\alpha$, so $N(\ell) \approx
R_\mathrm{lead}(\ell)$ generically (different $S$ rarely share the
same $\alpha$).

The conjecture's "expected route" predicts $R_\mathrm{lead} \leq
O(n^{c-1})$ along a generic curve, with sub-leading strata
contributing strictly less.

## Direct measurement

Per $S$, "$\ell$ crosses $V_S \times V_S$" iff the $2(c-1)$ linear
constraints
$\langle X^k p_S, u_i + \alpha v_i\rangle = 0$,
$k \in \{0,\dots,c-2\}$, $i \in \{1,2\}$
admit a common $\alpha$. This reduces to a $(2c-3)$-codim algebraic
condition on the projection of $(u_1, v_1, u_2, v_2)$ onto $V_S^\perp$
(the dim-$(c-1)$ ideal of polynomials of degree $<D$ vanishing on
$L_S$).

Implementation: `notes/scripts/lemma_a_stratum_count.py` enumerates
all $S$, projects via $p_S, X p_S, \dots, X^{c-2} p_S$, checks
linear-dependence + simultaneous-vanishing.

## Findings

50 random lines per cell (20–30 at larger $n$). Output:
`notes/scripts/lemma_a_stratum_count.output.txt`. Selected rows:

| $(n, c, p)$    | $D$ | $w$ | $T$ | $\binom{n}{w+1}$ | $R_\mathrm{lead}$ avg | max | predicted $\binom{n}{w+1}/q^{2c-3}$ |
|----------------|-----|-----|-----|------------------|----------------------|-----|------------------------------------|
| $(8, 2, 257)$  |  6  |  4  |  5  |     56           |     0.26             |   2 |     0.22                           |
| $(10, 2, 251)$ |  7  |  5  |  6  |    210           |     1.06             |   4 |     0.84                           |
| $(12, 2, 241)$ |  9  |  7  |  8  |    495           |     2.20             |   7 |     2.05                           |
| $(14, 2, 281)$ | 10  |  8  |  9  |   2,002          |     7.12             |  12 |     7.13                           |
| $(16, 2, 257)$ | 12  | 10  | 11  |   4,368          |    17.87             |  25 |    17.0                            |
| $(20, 2, 241)$ | 15  | 13  | 14  |  38,760          |   159.35             | 173 |   161.0                            |
| $(8, 3, 257)$  |  6  |  3  |  3  |     70           |     0.00             |   0 |     4.1e-6                         |
| $(12, 3, 241)$ |  9  |  6  |  5  |    792           |     0.00             |   0 |     5.7e-5                         |
| $(16, 3, 257)$ | 12  |  9  |  7  |   8,008          |     0.00             |   0 |     4.7e-4                         |
| $(16, 4, 257)$ | 12  |  8  |  5  |  11,440          |     0.00             |   0 |     4.0e-7                         |

**Observation 1 — perfect match to probabilistic expectation.** For
all measured rows, $R_\mathrm{lead}$ matches the random-line
prediction $\binom{n}{w+1} \cdot q^{-(2c-3)}$ to within sampling
noise. This is the *uniform* random behavior: $R_\mathrm{lead}$ is a
sum of $\binom{n}{w+1}$ Bernoulli-ish indicators, each of which fires
with probability $q^{-(2c-3)}$ (the $2c-3$ codim of the consistency
variety in the line parameter space).

**Observation 2 — scaling at fixed $c$ matches $n^{w+1-O(1)}/q$, not
$n^{c-1}$.** Log-log slope of $R_\mathrm{lead}$ vs. $n$ at $c=2$ is
$\approx 6.79$, close to $w+1$ at the tested $D \approx 3n/4$, not the
expected route's $c-1 = 1$. At fixed $q$, $R_\mathrm{lead}$ grows
*exponentially* in $n$ (since $\binom{n}{w+1} \approx \binom{n}{n/2}
\sim 2^n / \sqrt{n}$ for $w+1 \sim n/2$).

**Observation 3 — $c \geq 3$ rows are uninformative.** At
$(n, c, q) = (16, 3, 257)$, predicted $R_\mathrm{lead}
\approx 4.7 \cdot 10^{-4}$, so observing 0 over 20 lines is consistent
both with the conjecture and with no-special-structure. The dataset
does not separate them at $c \geq 3$ unless we use $q \approx T$, in
which case $V_\mathrm{bad}$ saturates the space.

## Implication for Lemma A

Combining $N(\ell) \leq R_\mathrm{lead}(\ell)$ with the empirical
$R_\mathrm{lead} \approx \binom{n}{w+1} \cdot q^{-(2c-3)}$:

$$
N(\ell) \;\lesssim\; \binom{n}{w+1} \cdot q^{-(2c-3)}.
$$

For Lemma A's conjectured $N(\ell) \leq \mathrm{poly}(n, c)$ to hold,
we need $q^{2c-3} \geq \binom{n}{w+1} / \mathrm{poly}(n, c)$, i.e.,
$q$ must be *exponentially large in $n$* (since
$\binom{n}{w+1} \sim 2^n$ for the deployment regime $w+1 \sim n/2$).

For the deployment grid ($n \leq 2^{20}$, $q \in \{2^{31}, 2^{64},
2^{124}, 2^{186}\}$, $c \in \{3,4,6,9\}$), $q$ does **not** satisfy
this asymptotic requirement: $q^{2c-3}$ is at most $2^{1488}$
(KoalaBear-ext6, $c=9$) versus $\binom{2^{20}}{2^{19}} \approx
2^{2^{20} - 10}$, a gap of $\approx 2^{2^{20}}$ orders of magnitude.

So the conjecture as stated — $N(\ell) \leq n^{O(c)}$ at any
$q \gg T$ — is **inconsistent with $R_\mathrm{lead}$ matching uniform
expectation**. Either:

1. **The leading-stratum upper bound $N \leq R_\mathrm{lead}$ is
   loose by $\binom{n}{w+1}/\mathrm{poly}$.** Sub-stratum cancellation
   inside $V_\mathrm{bad} \subsetneq \bigcup V_S \times V_S$ removes
   most leading-stratum hits. This is the only way to reconcile
   Lemma A with Note 0128's uniform-tightness ($\Pr[M > T]$
   prefactor $= \binom{n}{w+1}$ exactly).

2. **The conjecture should be restated for FRI-specific curves**,
   not arbitrary affine lines. The FRI verifier challenge curve has
   structure (it traces commit-side states under the protocol's fold
   operation) that may give a polynomial bound where a generic line
   does not.

3. **The conjecture is false at deployment scale.** The
   uniform-prefactor $\binom{n}{w+1}$ transfers to curve measure too,
   and Paper 3's R1 framing cannot beat BCIKS R2 in the deployment
   regime.

Path (3) would force a pivot to BCIKS (R2) framing across the
deployment table, removing the $|F|^{c-1}$ codim improvement.
Path (1) is the conjecture's intended escape but requires explicit
algebraic content sharper than ambient codim arithmetic. Path (2) is
a re-scoping of Lemma A: the FRI commit-side curve is **not** generic
in the sense Lemma A's statement requires.

## Why path (1) is the load-bearing question

Note 0128's threshold-histogram sweep at $(n,c) = (8,3)$ measured
$\Pr[M > T] = (1.0 \pm 0.1) \cdot \binom{n}{w+1} \cdot q^{-2(c-1)}$.
This is the **uniform** measure: $(s_1, s_2)$ drawn uniformly from
$\FF_q^{2D}$. The prefactor $\binom{n}{w+1}$ is uniform-tight; no
cancellation between $V_S \times V_S$ components is observed in the
uniform measure (consistent with Note 0125's Möbius / Heintz
ruled-out-reductions).

For curve measure, $E_\ell[N(\ell)] = q \cdot \Pr[\ell(0) \in
V_\mathrm{bad}]$ (basepoint uniform $\to$ uniform marginal at any
$\alpha$), so $E[N] = \binom{n}{w+1} \cdot q^{-(2c-3)}$ inherits the
same exponential prefactor. The empirical $R_\mathrm{lead}$
measurement above confirms this transfer.

Path (1) — sub-stratum cancellation specifically for curve measure
that does **not** apply to uniform measure — is the only way to
combine "uniform-tight $\binom{n}{w+1}$" (Note 0128) with "polynomial
bound on $N(\ell)$" (Lemma A). Neither this note nor any earlier note
has produced empirical evidence for such cancellation; the existing
empirical evidence ($\mathrm{curve\_max}$ small at small $n, c$) is
also consistent with $E[N(\ell)] \cdot q$ already being $\ll 1$ at
those parameters, so it doesn't separate paths (1) and (3).

## Path (1) refuted: $N(\ell) \to R_\mathrm{lead}$ at large $q/T$

Sub-stratum cancellation test (script
`notes/scripts/lemma_a_substratum_check.py`, output
`.output.txt`): for each $S$-resonance at $\alpha_S$, compute
$M(\ell(\alpha_S))$ exactly (using all $|E|=w$ supports in $[n]$,
not just $E \subset S$) and tally $M$-histogram + ratio
$R_\mathrm{in\_Vbad} / R_\mathrm{lead}$.

| $(n, c, p)$ | $T$ | $q/T$ | $R_\mathrm{lead}$ | $R_\mathrm{in\_Vbad}$ | ratio | $M$-hist (at crossings) |
|-------------|-----|-------|-------------------|----------------------|-------|--------------------------|
| $(8, 3, 17)$  | 3 |  5.7 | 15 |  5 | 0.33 | 2:2, 3:8, 4:5         |
| $(10, 3, 31)$ | 4 |  7.8 | 10 |  5 | 0.50 | 3:1, 4:4, 5:4, 6:1     |
| $(12, 3, 37)$ | 5 |  7.4 | 13 | 12 | 0.92 | 5:1, 6:7, 7:5          |
| $(16, 3, 97)$ | 7 | 13.9 |  4 |  4 | 1.00 | 9:1, 11:2, 13:1        |

The ratio $R_\mathrm{in\_Vbad}/R_\mathrm{lead}$ tracks $q/T$
monotonically and reaches 1 by $q/T \approx 14$. Mechanism: at
moderate $q/T$, some leading-stratum crossings land on the
discriminant locus of $V_S \times V_S$ (where $M < w+1$ due to
$\gamma_u$-collisions per Paper 3 §4) and so escape $V_\mathrm{bad}$.
As $q$ grows, the discriminant locus has Zariski codim $\geq 1$
within $V_S \times V_S$ and its $F_q$-density vanishes as $1/q$, so
generic crossings land in the open subset $U_S$ where $M = w+1 > T$.

**Implication.** At deployment scale where $|F| \in \{2^{31}, \dots,
2^{186}\}$ and $T = O(n)$, $q/T$ is astronomically large, so
$N(\ell) = R_\mathrm{lead}(\ell)$ to within an additive lower-order
term. The path-(1) escape — that $V_\mathrm{bad} \subsetneq
\bigcup V_S \times V_S$ removes most leading-stratum crossings — is
**refuted** as a deployment-scale phenomenon. Sub-stratum cancellation
is an artifact of small $q/T$ and does not save Lemma A's
poly-prefactor claim.

The interesting $M$-histogram structure at $(16, 3, 97)$ — $M \in
\{9, 11, 13\}$, with $13 = 2(w+1) - 1$ — also indicates **multi-$S$
overlap** (one crossing in $V_S \times V_S \cap V_{S'} \times V_{S'}$
contributing $\gamma$-realizers from both $S$ and $S'$), confirming
that the leading-stratum union $\bigcup V_S \times V_S$ has nontrivial
intersection structure. Such multi-$S$ events strengthen, not weaken,
the connection between $R_\mathrm{lead}$ and $N$ — they
*increase* $M$ above $w+1$, putting points more deeply into
$V_\mathrm{bad}$ rather than removing them.

## Adversarial $N(\ell)$: bounds the worst case

The decisive test would be: choose $\ell$ adversarially to *maximize*
$N(\ell)$. The maximum tells us whether $\deg(V_\mathrm{bad})$ along
adversarial curves is poly-in-$n$ (Lemma A holds in worst case) or
matches $\binom{n}{w+1}$ (conjecture fails worst case).

Heuristic upper bound on adversarial $N(\ell)$: each $S$ contributing
to $N$ imposes $2c-3$ algebraic constraints on the line parameters
$(u_1, v_1, u_2, v_2) \in \FF_q^{4D}$. For $N = t$ contributions, we
need $t \cdot (2c-3) \leq 4D - 2$ (line gauge), giving $t \leq (4D -
2) / (2c-3) = O(n / c)$. Linear in $n$; matches conjecture's
$n^{O(c)}$ shape (specifically $O(n)$, weaker than the
"expected-route" $O(n^{c-1})$ but in the same family).

If the heuristic is tight (upper bound achievable), then
$\max_\ell N(\ell) = O(n)$, supporting Lemma A in the worst case
direction. If it's not tight (algebraic dependencies among the
constraints reduce effective codim), $\max N$ could be larger.

This is the test to run next. Script proposal: enumerate small
$\Sigma \subset \binom{[n]}{w+1}$ in increasing size, solve the
resulting linear system for $(u, v)$, check if a solution exists and
whether the resulting $\ell$ realizes $|\Sigma|$ resonances.

## Action items

1. **Path (2) is the remaining lifeline.** Lemma A as stated for
   "generic affine lines" is empirically inconsistent with $R_\mathrm{lead}
   \approx \binom{n}{w+1} q^{-(2c-3)}$ at deployment scale. The
   conjecture's $n^{O(c)}$ bound on $N(\ell)$ at fixed $q$ requires
   curve-measure-specific cancellation that empirically does not
   occur for arbitrary lines. The remaining option: identify the
   FRI verifier challenge curve specifically, and prove a polynomial
   bound that exploits its structural properties (e.g., the curve
   parameterization comes from the protocol's fold operation, which
   may impose algebraic relations on $(u_1, v_1, u_2, v_2)$ that
   generic lines don't satisfy).

2. **If FRI-curve specifics don't yield a polynomial bound**:
   conclude Lemma A is false, and pivot Paper 3's deployment claim
   to BCIKS R2 framing across the entire deployment table. The
   $|F|^{-2(c-1)}$ improvement becomes a Lemma-A-conditional
   *protocol-modification* suggestion only, with no claim about
   existing FRI's commit-side ε.

3. **Independently check the FRI-curve characterization.** The
   FRI commit curve is parameterized by $\alpha \in \FF_q$ as
   $(s_1(\alpha), s_2(\alpha)) = (f^{(i)}(\alpha), f^{(i+1)}(\alpha))$
   for the $i$-th and $(i{+}1)$-th fold-round commitments. Whether
   this curve admits the polynomial bound is a separate, more
   concrete question than the generic-line conjecture. Worth
   examining the BCIKS proof for the analogous $\{M \geq 1\}$
   bound — they get $\mathrm{poly}(n) \cdot |F|^{-(c-1)}$ for
   curve measure, suggesting the FRI curve has *some* polynomial
   prefactor structure that beats $\binom{n}{w}$. Recovering
   $|F|^{-2(c-1)}$ instead of $|F|^{-(c-1)}$ would require sharpening
   that structure to bound the higher-codim event.

## Method limitations

- $R_\mathrm{lead}$ counts only the leading stratum
  $|S^*| = w+1$. Sub-leading strata $|S^*| = w + j$, $j \geq 2$,
  contribute additional $V_\mathrm{bad}$-points. Paper 3 §5.3 gives
  these higher codim per-stratum, so they're a sub-leading correction
  in the uniform measure. For curve measure, the leading-stratum
  empirical match already saturates the union-bound prediction, so
  sub-leading isn't qualitatively different here.

- Sample sizes are limited (20–50 lines per cell). For $c \geq 3$,
  the predicted $R_\mathrm{lead}$ is so small that 0 observations is
  the expected outcome under both the conjecture and the
  uniform-expectation hypothesis. The dataset doesn't separate them.

- The fit $R_\mathrm{lead} \sim \binom{n}{w+1}/q^{2c-3}$ is at fixed
  $D \approx 3n/4$. The deployment regime is similar but not
  identical; extrapolation to $n = 2^{20}$ assumes the per-S
  probability $q^{-(2c-3)}$ continues to hold, which is the
  ambient-codim consequence and should be robust.

## Rigorous statement: regime-dependent obstruction

The empirical observations refine into a regime-dependent argument:

1. **(Marginal identity)** For uniformly random
   $\ell = (\mathbf{u}, \mathbf{v})$ over $\FF_q^{4D}$ and uniform
   $\alpha \in \FF_q$, the marginal of $\ell(\alpha) = (u_1 + \alpha
   v_1, u_2 + \alpha v_2)$ over $\FF_q^{2D}$ is uniform. Hence
   $$
   \E_\ell[N(\ell)] \;=\; q \cdot \eps^\mathrm{unif}_\mathrm{commit}.
   $$

2. **(Uniform-tightness, Note 0128, valid in Lang-Weil regime)**
   When $|F|$ is large enough that the additive component bound
   $\binom{n}{w+1} |F|^{-2(c-1)} < 1$ — i.e., $|F| \gg
   \binom{n}{w+1}^{1/(2c-2)}$ — the Lang-Weil asymptotic gives
   $\eps^\mathrm{unif}_\mathrm{commit} = \binom{n}{w+1} \cdot
   |F|^{-2(c-1)} \cdot (1 + O(|F|^{-1/2}))$ exactly. Note 0128
   verified this at $(n, c) = (8, 3)$ with $|F| \in \{17, \dots, 137\}$
   (where $\binom{8}{4} = 70 \ll |F|^4 \approx 10^4$ to $10^9$).

3. **(Pigeonhole, Lang-Weil regime)** Combining (1)–(2), in the
   Lang-Weil regime where $\binom{n}{w+1} < |F|^{2(c-1)}$:
   $$
   \E_\ell[N(\ell)] \;=\; \binom{n}{w+1} \cdot |F|^{-(2c-3)}.
   $$
   For Lemma~A's $N(\ell) \leq n^{O(c)}$ to hold on a Zariski-open
   $U$ with $\Pr[\ell \in U] = p$ (and $N(\ell) \leq q$ trivially on
   the complement),
   $$
   \binom{n}{w+1} \cdot |F|^{-(2c-3)}
   \;\leq\; p \cdot n^{O(c)} \;+\; (1 - p) \cdot q.
   $$
   In particular, when $\binom{n}{w+1} \cdot |F|^{-(2c-3)} \gg
   n^{O(c)}$ (i.e., $|F|^{2c-3} \cdot n^{O(c)} \ll
   \binom{n}{w+1}$), the non-generic mass satisfies
   $1 - p \gtrsim \binom{n}{w+1} \cdot |F|^{-2(c-1)}$ — the bound
   forces a non-zero (Lang-Weil-tight) fraction of lines to lie
   outside the conjecture's "generic" set.

4. **(What this rules out)** Lemma~A's $n^{O(c)}$ bound for
   arbitrary $\FF_q$-affine lines, with the Zariski-open subset $U$
   having $\FF_q$-density approaching 1, is **inconsistent with
   uniform-tightness in the Lang-Weil regime**. Specifically, at
   any $(n, c, q)$ where $\binom{n}{w+1} > q^{(2c-3) + \log_n(\text{poly})}$,
   the average $\E_\ell[N(\ell)]$ exceeds the conjectured per-line
   bound, so a positive-density fraction of lines must violate the
   bound.

5. **(What this does not rule out — deployment regime)** At
   deployment scale ($n = 2^{20}$, $|F| \in \{2^{31}, \dots,
   2^{186}\}$, $c \in \{3, \dots, 9\}$), $\binom{n}{w+1} \approx
   2^{n}/\sqrt{n} \gg |F|^{2(c-1)}$ for all rows. We are **deep
   below** the Lang-Weil regime: components of $V_\mathrm{bad}$ must
   overlap heavily, and the actual $\eps^\mathrm{unif}_\mathrm{commit}$
   need not match the additive-sum formula. Without a rigorous
   handle on $\eps^\mathrm{unif}_\mathrm{commit}$ in this saturated
   regime, the pigeonhole argument above cannot be substituted to
   conclude vacuity at deployment scale.

**What is robust.** In the Lang-Weil regime where uniform-tightness
holds, Lemma~A as stated is *false* (in the sense that no
positive-density Zariski-open subset achieves the polynomial bound;
the bound either holds on a measure-zero set or is loose).

**What is open.** Whether $V_\mathrm{bad}$'s component overlap in
the deployment regime suppresses
$\eps^\mathrm{unif}_\mathrm{commit}$ below $\binom{n}{w+1} |F|^{-2(c-1)}$
sufficiently to make Lemma~A's $n^{O(c)}$ bound consistent. This
overlap-saturation analysis is itself a substantive AG question
that, as far as we can tell, has not been addressed in the BCIKS
or paper-3 literature.

**Path forward.**
- Either (a) compute $\eps^\mathrm{unif}_\mathrm{commit}$ in a
  *saturated* regime (e.g., $n = 30$, $c = 3$, $q$ chosen so that
  $\binom{n}{w+1} \approx q^{2(c-1)}$, the transition point) and
  observe whether Pr saturates below the additive sum.
- Or (b) replace "generic affine line" with the FRI commit-curve
  (path 2 in earlier discussion); the marginal identity (step 1)
  breaks because FRI-curve's basepoint/direction are constrained
  by the prover's $f^{(0)}$, and the pigeonhole argument does not
  apply.

## Independent inconsistency: $\deg(V_\mathrm{bad})$ is a fixed
number, not "sharpenable"

Paper 3 §3 (line 593-599) claims:
$$
\eps_\mathrm{commit} \;\leq\; \deg(\Vbad) \cdot |F|^{-2(c-1)} +
                              O(|F|^{-2(c-1)-1/2})
$$
via Lang--Weil, then claims a "rigorous $\deg(\Vbad) \leq n^{O(c)}$
sharpening" reduces to Lemma~A. But:

- $\Vbad \subseteq \bigcup_{|S|=w+1} V_S \times V_S$ is a strict
  inclusion only on a measure-zero subset (the discriminant locus
  $V_S \times V_S \setminus U_S$ from Theorem~4.1). The Zariski
  closure $\overline{\Vbad}$ equals the union exactly.
- By Vandermonde linear independence, $V_S \neq V_{S'}$ for distinct
  $(w{+}1)$-subsets $S, S'$, so the union has $\binom{n}{w+1}$
  distinct irreducible linear components, each of degree $1$.
- Hence $\deg(\overline{\Vbad}) = \sum_S \deg(V_S \times V_S) =
  \binom{n}{w+1}$ exactly. This is the variety-theoretic $\deg$, not
  an estimate. There is no further "sharpening" available.

The statement "$\deg(\Vbad) \leq n^{O(c)}$" is therefore false as
written: $\deg(\Vbad) = \binom{n}{w+1}$, and $\binom{n}{w+1} >
n^{O(c)}$ for the deployment regime $w + 1 \approx n/2$. Lemma~A
cannot reduce $\deg(\Vbad)$ to a polynomial because $\deg(\Vbad)$
is a fixed, computed quantity exceeding any polynomial.

This is consistent with Note 0125's Möbius/Goresky--MacPherson
analysis (no inclusion-exclusion cancellation) and with Note 0128's
empirical uniform-tightness ($\Pr[V_\mathrm{bad}] = \binom{n}{w+1}
\cdot |F|^{-2(c-1)}$ exactly, ratio $\in [0.90, 1.18]$).

**What Lemma~A could legitimately mean.** Three candidates:

1. **A scheme-theoretic refinement.** $\deg$ of $\Vbad$ as a *scheme*
   defined by an explicit ideal might be smaller than the variety
   $\deg$ if the ideal has multiplicity $> 1$ on some components and
   the relevant Bezout bound uses the scheme structure. We have not
   found such a sharpening in the literature, and the
   irreducible-component-of-degree-1 argument above shows the
   reduced scheme has full $\binom{n}{w+1}$ degree.

2. **A curve-restricted sharpening, not a variety statement.** The
   $\bigcup_S V_S \times V_S$ has $\binom{n}{w+1}$ irreducible
   components, but a *generic affine line* meets only an
   $n^{O(c)}$-size fraction of them (because each component is
   codim $2(c-1) \geq 2$, so generic line misses it; only
   $\poly(n, c)$ "lucky" components are crossed). This is the
   "stratified Bezout" route. *This is what the paper §8.1 ought to
   formalize*, but as Note~0129 (this note) shows empirically, the
   leading-stratum sum $R_\mathrm{lead}$ matches the additive
   uniform expectation, so the per-line crossing count does *not*
   sharpen to $\poly(n, c)$ for arbitrary lines in the
   Lang--Weil regime.

3. **An FRI-curve-specific claim.** $V_\mathrm{bad}$ along the
   specific 1-parameter family arising from the FRI verifier
   challenge (under a $\delta$-far prover constraint) is hit by
   only $\poly(n, c)$ values of the challenge. This is a sharper
   claim than (2) — it leverages the algebraic structure of the
   FRI curve, which is *not* a uniform random affine line.

Interpretation (3) is the only one that survives the obstructions
above. Restating Lemma~A in form (3) is path-2 of the action
items, and it is the natural framing because the BCIKS bound
$\Pr[M \geq 1]$ is precisely an FRI-curve-specific result with a
$\poly(n)$ prefactor. Recovering the analogous bound for
$\Pr[M > T]$ (codim $2(c{-}1)$ instead of $c{-}1$) is what would
actually close §8.1's deployment claim.

## Bottom line

Two empirical results from this note:

1. $R_\mathrm{lead}(\ell) \approx \binom{n}{w+1} \cdot q^{-(2c-3)}$
   for generic line $\ell$ over $\FF_q$, matching probabilistic
   expectation. No algebraic suppression beyond ambient codim.
2. At $q \gg T$, $N(\ell) = R_\mathrm{lead}(\ell)$ deterministically
   (path-1 sub-stratum cancellation is a $1/q$ effect that vanishes).

Combined, $N(\ell)$ at deployment-scale $q$ is governed by the
exponential-in-$n$ uniform prefactor $\binom{n}{w+1}$, not by a
polynomial. **Lemma A's stated $n^{O(c)}$ bound for arbitrary
generic lines is empirically inconsistent with deployment-scale
parameters.**

The conjecture survives only if Lemma A is restated for the
**FRI-specific curve**, where the parameterization
$(s_1(\alpha), s_2(\alpha))$ is constrained by the protocol's fold
operation and may admit a polynomial bound that arbitrary lines do
not. This is path (2). It is now the only viable lifeline for
Paper 3's R1-conditional deployment claim.

If path (2) does not yield a polynomial bound, Paper 3's deployment
table must pivot fully to BCIKS R2 ($|F|^{-(c-1)}$), and the
$|F|^{-2(c-1)}$ improvement becomes a *protocol-modification
suggestion* only — applicable to a hypothetical Berlekamp-augmented
FRI, not to existing production deployments.
