# Note 0135 — OP-1a: status report and corrected analysis

**Date**: 2026-04-30
**Branch**: `feat/op1a-algorithm` (off `main`)
**Status**: **bug found, scope revised**. Original "BM + minpoly L-rooted" route
is provably incorrect in the deployment regime $w \to D$. OP-1a as stated in
paper3 §7.6 is harder than initially apparent and connects to
*beyond-Johnson-radius list decoding* — a hard open problem in coding theory.
This note documents the bug, corrects the framework, and identifies what is
genuinely solvable vs. open.

## Problem (paper3 §7.6, recall)

$M(s_1, s_2) = \#\{\gamma \in \FF_q^* : \exists\, E \subset [n], |E|=w,
s_1 + \gamma s_2 \in V_E\}$, where $V_E = \mathrm{span}\{\mathrm{ev}_v : v \in E\}$
and $\mathrm{ev}_v = (1, L_v, \dots, L_v^{D-1})$ with $L \subset \FF_q^*$ a
multiplicative subgroup of order $n$ ($\prod_{v \in L}(X - L_v) = X^n - 1$).

Threshold $T = \lfloor (2D-1)/c \rfloor$, $c = D-w \geq 2$, $D = n-k$.

OP-1a wishlist: a $\mathrm{polylog}(|F|) \cdot \mathrm{poly}(n)$ algorithm
deciding $M > T$. Brute force is $\Theta(|F| \cdot \binom{n}{w})$ via realizer
enumeration; even per-$\gamma$ Berlekamp-Welch is $\Theta(|F| \cdot \mathrm{poly}(n))$
— linear in $|F|$.

## Original framing (and where it fails)

The first version of this note (commit `de716fb`) proposed:

> Lemma 1: $x \in \bigcup_{|E|=w} V_E \Leftrightarrow \mathrm{rank}\, H_w(x) \leq w$
> AND $\mathrm{minpoly}(x) \mid X^n - 1$, where $\mathrm{minpoly}(x)$ is the
> unique monic min-degree generator of $\mathrm{Ann}_w(x) \subset \FF_q[X]_{\leq w}$.

The intended algorithmic payoff was: parametrize $x_\gamma$ symbolically, get
$\mathrm{minpoly}(x_\gamma) \in \FF_q(\gamma)[X]$ via SNF on the Hankel pencil
$A + \gamma B$, root-find at SNF rank-drop loci.

**This is incorrect.** Concrete counterexample at $(n, c, p) = (10, 3, 41)$:

- $s_1 = (36, 34, 13, 7, 39, 17, 35)$, $s_2 = (36, 13, 36, 18, 36, 17, 35)$,
  $\gamma = 8$, so $x = (37, 15, 14, 28, 40, 30, 28)$.
- Brute-force support enum: $x \in V_E$ for $E = \{0, 3, 4, 8\}$,
  $L_E = \{1, 4, 18, 37\}$, so $x \in \bigcup_{|E|=4} V_E$.
- The Hankel matrix $H_w(x)$ ($5 \times 3$) has rank $3$ (verified by a $3 \times 3$
  minor det $= 10 \neq 0 \pmod{41}$). So $\dim \mathrm{Ann}_4(x) = 5 - 3 = 2$.
- A basis of $\mathrm{Ann}_4(x)$ via row reduction:
  $v_1 = X(X^2 + 2X + 40)$ (degree $3$, root at $X = 0 \notin L$),
  $v_2 = X^4 + 40 X^2 + 39 X + 40$ (degree $4$).
- The expected $L$-rooted annihilator $Q = (X-1)(X-4)(X-18)(X-37) =
  X^4 + 22 X^3 + 2 X^2 + 17 X + 40$ is verified to annihilate $x$ at the
  three Hankel shifts $j = 0, 1, 2$ — so $Q \in \mathrm{Ann}_4(x)$.
- $Q$ is **not** in $\mathrm{span}(v_1, X v_1)$: $Q$'s constant term is $40 \neq 0$,
  while $v_1$ and $X v_1$ both have constant term $0$.
- $X \cdot v_1$ tested directly: it satisfies $j=0,1$ shifts but **fails at
  $j=2$** (residue $7 \pmod{41}$). So $X v_1 \notin \mathrm{Ann}_4(x)$,
  contradicting the claim that $\mathrm{Ann}_4 = (v_1) \cap \FF_q[X]_{\leq w}$.

**Root cause** (Prop 1.2 was wrong): I conflated two notions of "$Q$
annihilates $x$":

- **Strict**: $\sum_i Q_i x_{j+i} = 0$ for all $j \in [0, D - 1 - \deg Q]$.
- **Hankel-$w$**: $\sum_i Q_i x_{j+i} = 0$ for $j \in [0, D - 1 - w]$.

For $\deg Q = m < w$, "Hankel-$w$ annihilation" is **weaker** than "strict
annihilation": Hankel-$w$ checks fewer shifts ($D - w$ shifts vs. $D - m$
shifts). When $D < 2w + 1$ (the "short-data" regime, which is exactly the
deployment regime $c \ll w$), the two notions diverge, and $\mathrm{Ann}_w$ is
**not** a principal ideal.

In the example: $v_1$ satisfies Hankel-$w$ ($w = 4$, so 3 shifts), but $X v_1$
requires 4 shifts which is one more than Hankel-$w$ — so $X v_1$ is not
forced to be in $\mathrm{Ann}_w$.

**Empirical witness**: `notes/scripts/op1a_algorithm.py` cross-checks
"BM + L-rooted-minpoly" against the brute-force support enum from
`op2_curve_measure_prefactor.py`. At $(n, c, p) = (10, 3, 41)$, 9/10 trials
agree, 1 trial mismatches (the example above).

## Corrected Lemma 1

$x \in \bigcup_{|E|=w} V_E$ if and only if
$$\exists\, Q \in \mathrm{Ann}_w(x), \;\; Q \text{ monic deg } w, \;\; Q \mid X^n - 1.$$

(Here $\mathrm{Ann}_w(x) := \{Q \in \FF_q[X]_{\leq w} : H_w(x) \cdot \mathbf{q} = 0\}$
— the Hankel-$w$-annihilator subspace, of dimension $(w+1) - \mathrm{rank}\, H_w(x)$.)

This is *not* equivalent to "minpoly is $L$-rooted" — it's an **existence
question** over the entire affine-linear subspace $\mathrm{Ann}_w(x)$,
intersected with the discrete variety of $\binom{n}{w}$ degree-$w$ monic
$L$-rooted polynomials.

The proof of $\Leftarrow$ goes through (degree-$w$ $L$-rooted annihilator
gives the desired decomposition via Vandermonde). The proof of $\Rightarrow$
is just: the natural error locator $\Pi_E := \prod_{v \in E}(X - L_v)$ is
degree $w$, monic, $L$-rooted, and lies in $\mathrm{Ann}_w(x)$.

## Where this leads: Reed-Solomon list decoding

The corrected question per $\gamma$ is: does $x_\gamma$ admit a
weight-$\leq w$ syndrome decomposition over $L$?

In coding-theory language, this is **syndrome-side list-decoding** of the
Reed-Solomon code $\mathrm{RS}(n, n-D)$ at decoder weight $w$.

- For $w \leq \lfloor D/2 \rfloor$: Berlekamp-Massey/Welch-Berlekamp solves
  it uniquely in $\mathrm{poly}(n)$ time, $|F|$-independent.

- For $\lfloor D/2 \rfloor < w \leq J$ where $J = n - \sqrt{n(n - D - 1)}$ is
  the **Johnson radius**: Guruswami-Sudan list-decoding solves the existence
  question in $\mathrm{poly}(n)$ time, $|F|$-independent.

- For $w > J$: **open**. No general $\mathrm{poly}(n)$ algorithm is known for
  Reed-Solomon list-decoding beyond the Johnson bound (Guruswami-Sudan-Vardy,
  Wu, Koetter-Vardy provide partial extensions for specific code families,
  but not generic $\mathrm{RS}$).

**Where does paper3's deployment land?** With $D \approx n/2$ and $c \in \{3,
4, 6, 9\}$ (so $w \approx D$, decoder ratio $w/D \approx 1$), and Johnson
ratio $J/n \approx 1 - \sqrt{1/2} \approx 0.293$, we have $w/n \approx 0.5
\gg J/n$. **Deployment is firmly in the "beyond Johnson" regime**, where even
the per-$\gamma$ existence test does not have a known $\mathrm{poly}(n)$
algorithm.

## Algorithmic status (honest)

Three regimes for a per-$\gamma$ existence test:

| Regime         | Per-$\gamma$ cost            | Total cost over $\gamma$    | OP-1a? |
|----------------|------------------------------|------------------------------|--------|
| $w \leq D/2$   | $\mathrm{poly}(n)$ (BW/BM)   | $|F| \cdot \mathrm{poly}(n)$ | NO (still linear in $|F|$) |
| $D/2 < w \leq J$ | $\mathrm{poly}(n)$ (GS)    | $|F| \cdot \mathrm{poly}(n)$ | NO (still linear in $|F|$) |
| $w > J$        | **OPEN**                     | OPEN                         | OPEN   |

So even at small $w$, the per-$\gamma$ approach does not strictly satisfy
OP-1a's "$\mathrm{polylog}(|F|)$" criterion. Beating $|F|$ requires a
parametric construction that exploits how the existence-test structure varies
with $\gamma$ — and this is exactly the question that OP-1a poses.

## Parametric paths considered

### Path 1: SNF on Hankel pencil

The Hankel pencil $H_\gamma = A + \gamma B$ has SNF over $\FF_q[\gamma]$ with
invariant factors $d_1 \mid \dots \mid d_c$ (size $(w+1) \times c$, generic
rank $c$). The rank-drop locus $\{\gamma : d_c(\gamma) = 0\}$ has size
$\leq c = O(1)$.

**But** rank-drop is *not* the relevant filter — at deployment, $\dim
\mathrm{Ann}_w(\gamma) \geq w + 1 - c$ is **always huge** (not just at
rank-drop $\gamma$'s). So rank-drop tells us about exceptional $\gamma$'s
where the kernel is *one* dimension larger; it does not isolate the $\gamma$'s
where the kernel contains an $L$-rooted degree-$w$ element.

### Path 2: Parametric Berlekamp-Welch system

For each $\gamma$, BW solves a $O(D) \times O(D)$ linear system $M(\gamma) \cdot
v = 0$ encoding the existence of $(\Lambda, \Omega)$ with $\Lambda$ monic
deg-$w$, $\Lambda \cdot S(\gamma) \equiv \Omega \pmod{X^D}$. Pencil
$M(\gamma) = M_0 + \gamma M_1$, rank-drop locus $\{\det M(\gamma) = 0\}$
of size $\leq O(D)$.

**This works in the unique-decoding regime** ($w \leq D/2$): BW system has
unique solution at non-rank-drop $\gamma$'s, so rank-drop $\gamma$ is the
candidate set. Total cost: $\mathrm{poly}(n) \cdot \mathrm{polylog}(|F|)$ — but
this is the **easy** regime, not deployment.

**For $w > J$**: BW system itself is not known to characterize existence,
so this path doesn't extend.

### Path 3: Direct intersection enumeration

$M(s_1, s_2)$ counts intersections of the affine line $\{s_1 + \gamma s_2\}$
with $U := \bigcup_{|E|=w} V_E$. $U$ has $\binom{n}{w}$ irreducible
components, each of dim $w$, codim $c$ in $\FF_q^D$. Bezout-style bound:
$|line \cap U| \leq \deg U = \binom{n}{w}$ — way too large.

**Sharper bound** would require sharpening $\deg U$ in a measure-aware way
(curve measure, FRI commit-curve, etc.) — exactly the territory of
**Lemma A** (Note 0134), which is itself in trouble.

## Implications for paper3

The §7.6 "operational gap" is genuine and harder than initially apparent:

- **Within Johnson radius**: per-$\gamma$ poly($n$) tests exist (BW/GS), so a
  randomized OP-1a algorithm via uniform $\gamma$-sampling can give a
  high-probability decision in $\mathrm{polylog}(|F|) \cdot \mathrm{poly}(n)$
  expected time, *provided $T/|F|$ is bounded away from $0$*.
  
- **Beyond Johnson** (deployment): per-$\gamma$ test is itself open, and the
  parametric reductions in paths 1-3 don't extend.

**Recommendation for paper3 §7.6**: rather than replace the "open
algorithmic question" with an "Algorithm 1", strengthen the framing of *why*
it's open:

1. State the corrected Lemma 1 (existence-based, not minpoly-based).
2. Identify OP-1a's connection to Reed-Solomon list-decoding **beyond the
   Johnson bound** — a longstanding hard open problem.
3. Position OP-1a alongside Lemma A as the two remaining R1 conditionals,
   with clear context on what's known vs. open.

This is more *honest* than the original §7.6 framing and useful for prize
judges (Boneh, Fenzi, Arnon — succinct-proof / IOP community, may not be
familiar with the beyond-Johnson list-decoding gap).

## What was committed in this session

- `notes/0135-op1a-algorithm.md` — this note (corrected version).
- `notes/scripts/op1a_algorithm.py` — per-$\gamma$ BM-based oracle, agrees
  with brute-force support enum 29/30 trials at $(8,3,17), (10,3,41), (12,3,73)$.
  The 1 mismatch is the witness above.
- `notes/scripts/debug_op1a.py` — reproduces and isolates the
  Lemma-1-as-originally-stated counterexample.

## Net effect on prize-readiness

Original session 6 plan: "close OP-1a, R1 needs only Lemma A". Revised: OP-1a
is a longstanding open problem (beyond-Johnson RS list-decoding) wearing a
new hat. The R1 column in paper3 §6.3 deployment table remains conditional on
both (i) Lemma A and (ii) OP-1a, with (ii) now visible as more substantial
than the original §7.6 "gap" framing suggested.

This is consistent with the broader paper3 picture:
- **R2 column** (BCIKS, production model, codim $c-1$): unconditional.
- **R1 column** (Berlekamp list-decoding, codim $2(c-1)$): conditional on
  Lemma A AND OP-1a, both substantial open problems.
- **Theorem 1** ($\codim V_{\mathrm{bad}} = 2(c-1)$): unconditional structural
  result, the central contribution.

Prize-readiness assessment from session 5 stands: 40-60%, with Theorem 1 +
formalization being the load-bearing contribution; conditionals on R1 are
honest open-problem callouts, not undelivered claims.
