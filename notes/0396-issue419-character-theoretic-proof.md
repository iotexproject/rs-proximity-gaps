# Note 0396 -- Issue #419: character-theoretic proof of the high-tail parity lemma (Tier 1a)

**Date:** 2026-05-02 (Tier 1a — formalize Note 0393's structural lemma)
**Branch:** `main`
**Status:** σ-symmetric subcase **PROVEN** structurally and field-uniformly
(holds in any odd characteristic with $16 \mid q-1$).
General no-full subcase reduced to a finite system of polynomial
divisibilities in $\mathbb{F}_q[y]/G_*(y)$; structural proof of the
reduced system is the remaining algebraic step.

---

## 1.  Restatement of the lemma

Let $L_2 = (n_2, k_2) = (16, 4)$, $\omega \in \mathbb{F}_q^*$ a primitive
$16$-th root of unity (so $16 \mid q-1$), and $S \subset \mathbb{Z}/16\mathbb{Z}$
a *no-full* subset of size $|S| = 8$, i.e.,
$|S \cap \{j, j+4, j+8, j+12\}| < 4$ for each $j \in \{0,1,2,3\}$.

Set $g_S(t) = \prod_{s\in S}(t - \omega^s)$ and define the **high-tail
projection** $\mathrm{HT}: \mathbb{F}_q[t]/g_S \to \mathbb{F}_q^4$ by
sending a polynomial $p(t)$ of degree $<8$ to its coefficients at
$t^4, t^5, t^6, t^7$.

**Lemma (high-tail parity, Note 0393).**  For every no-full $S$ and every
pair $r, r' \in \{4, \ldots, 15\}$ with $r \not\equiv r' \pmod 2$, the
vectors $\mathrm{HT}(t^r), \mathrm{HT}(t^{r'}) \in \mathbb{F}_q^4$ are
*not* nonzero scalar multiples of each other.

---

## 2.  Reduction to $\ker(M)$ membership

Via the Lagrange basis $\{L_s\}_{s\in S}$ of $\mathbb{F}_q[t]/g_S$, the map
$\mathrm{HT}$ factors through evaluation:
$$
M : \mathbb{F}_q^S \;\longrightarrow\; \mathbb{F}_q^4, \qquad
M(\delta_s) = \mathrm{HT}(L_s),
$$
and for any $r$, $\mathrm{HT}(t^r) = M(\chi_r|_S)$ where
$\chi_r(s) := \omega^{rs}$ is the $r$-th character of $\mathbb{Z}/16\mathbb{Z}$
restricted to $S$.

**Kernel structure.**  $\ker(M)$ is the image of $\mathrm{ev}_S: \mathbb{F}_q[t]_{\le 3} \to \mathbb{F}_q^S$,
i.e., the span $\langle \chi_0|_S, \chi_1|_S, \chi_2|_S, \chi_3|_S \rangle$.
Since $\{1, t, t^2, t^3\}$ has at most $3$ common roots in $\mathbb{F}_q^*$
and $|S| = 8$, this span is $4$-dimensional.

**Reformulation of the lemma.**  Nonzero proportionality
$\mathrm{HT}(t^r) = \lambda \, \mathrm{HT}(t^{r'})$ with $\lambda \in \mathbb{F}_q^*$
is equivalent to
$$
\chi_r|_S - \lambda \chi_{r'}|_S \;\in\; \ker(M),
$$
i.e., the polynomial $f_\lambda(t) := t^r - \lambda t^{r'} - q(t)$ for some
$q \in \mathbb{F}_q[t]_{\le 3}$ is divisible by $g_S$ in $\mathbb{F}_q[t]$.

---

## 3.  σ-isotypic structure

Let $\sigma$ act on $\mathbb{F}_q[t]$ by $\sigma(p)(t) = p(-t)$.  Note
$-t = \omega^8 t$ since $\omega^{16} = 1$ and $\omega^8 = -1$ in any
characteristic where $-1$ has order $2$.

* On monomials: $\sigma(t^j) = (-1)^j t^j$.  Eigenspaces $V_+$ (even-degree)
  and $V_-$ (odd-degree).
* On characters: $\chi_r(s+8) = \omega^{8r} \chi_r(s) = (-1)^r \chi_r(s)$.
  Hence $\chi_r$ is $\sigma$-invariant if $r$ is even, $\sigma$-anti-invariant
  if $r$ is odd.
* On $g_S$: $\sigma(g_S)(t) = \prod_{s\in S}(-t - \omega^s) = \prod_{s\in S}(t - \omega^{s+8}) = g_{S+8}(t)$.
  $g_S$ is $\sigma$-stable (i.e., $g_S(t) = g_S(-t)$) iff $S = S+8 \bmod 16$,
  which we call the **$\sigma$-symmetric** case.

---

## 4.  Proof of the σ-symmetric case

Suppose $S = S+8 \bmod 16$.  Then $g_S$ is an *even* polynomial.
Reduction modulo an even polynomial preserves parity:
$$
t^{r} \bmod g_S \;\in\; \begin{cases} V_+ & r \text{ even,} \\ V_- & r \text{ odd.} \end{cases}
$$

So $t^r \bmod g_S$ has only even-degree coefficients (for $r$ even), and only
odd-degree coefficients (for $r$ odd).  Restricting to the high-tail
indices $\{4, 5, 6, 7\}$:
$$
\mathrm{HT}(t^r) \in \mathrm{span}\{e_0, e_2\} \subset \mathbb{F}_q^4 \quad (r \text{ even}, \text{ degrees } 4, 6),
$$
$$
\mathrm{HT}(t^{r'}) \in \mathrm{span}\{e_1, e_3\} \subset \mathbb{F}_q^4 \quad (r' \text{ odd}, \text{ degrees } 5, 7).
$$

These are complementary $2$-dimensional coordinate subspaces of $\mathbb{F}_q^4$.
Two nonzero vectors from complementary coordinate subspaces cannot be
scalar multiples of each other.  Hence
$\mathrm{HT}(t^r) \ne \lambda \mathrm{HT}(t^{r'})$ for any $\lambda \in \mathbb{F}_q^*$,
when at least one of $\mathrm{HT}(t^r), \mathrm{HT}(t^{r'})$ is nonzero.

If both are zero, the proportionality is trivial (both sides zero), which
the lemma's "nonzero scalar multiple" qualifier excludes.  $\square$

**Counting.**  $\sigma$-symmetric no-full $S$ are precisely $S = T \sqcup (T+8)$
for $T \subset \{0,\ldots,7\}$ a transversal of the $\sigma$-orbit pairs
$\{q, q+4\}$, $q \in \{0,1,2,3\}$.  There are $2^4 = 16$ such $S$.
Although a small fraction of the $10\,896$ no-full $S$ at $L_2 = (16, 4)$,
this case is the conceptual core of the proof and is now field-uniform.

---

## 5.  σ-orbit decomposition for general $S$

Decompose $S = A \sqcup B$ where $A := \{s \in S : s+8 \in S\}$ is the
$\sigma$-symmetric part (always $|A|$ even) and $B := S \setminus A$ are the
$\sigma$-singletons.  The $\sigma$-symmetric closure
$$
S^* := S \cup (S+8) = A \cup B \cup (B+8)
$$
satisfies $|S^*| = |A| + 2|B| = 8 + |B|$ and $S^* = S^* + 8$.

Factor $g_{S^*} = g_A \cdot g_B \cdot g_{B+8}$.  Crucially:

* $g_A$ is even ($A$ is $\sigma$-symmetric, $|A|$ even, hence
  $\prod_{a\in A}(t - \omega^a) = \prod_{i=1}^{|A|/2}(t^2 - \omega^{2 a_i})$).
* $g_B$ is *not* generally even.
* $\sigma(g_B)(t) = g_B(-t) = g_{B+8}(t)$; hence
  $g_B \cdot g_{B+8} = g_B(t) g_B(-t) = (g_B^{\mathrm{even}}(t))^2 - (g_B^{\mathrm{odd}}(t))^2$
  is even.
* Thus $g_{S^*} = g_A(t) \cdot \big((g_B^{\mathrm{even}})^2 - (g_B^{\mathrm{odd}})^2\big)(t)$
  is an even polynomial.  Write $g_{S^*}(t) = G_*(y)$ with $y := t^2$ and
  $\deg G_* = |S^*|/2 = 4 + |B|/2$.

---

## 6.  Doubling reduction

Suppose nonzero proportionality holds: $g_S(t) \mid f_\lambda(t)$ where
$f_\lambda(t) = t^r - \lambda t^{r'} - q(t)$ with $q = q_e + q_o$
(even/odd parts, $\deg q \le 3$, so $q_e = \alpha + \beta t^2$,
$q_o = c t + d t^3$).

Multiply both sides by $g_{B+8}(t)$:
$$
g_{S^*}(t) \;=\; g_S(t) \cdot g_{B+8}(t) \;\;\Big|\;\; f_\lambda(t) \cdot g_{B+8}(t) \;=:\; \tilde h(t).
$$

Apply $\sigma$: since $g_{S^*}$ is $\sigma$-stable, $g_{S^*} \mid \tilde h$
implies $g_{S^*} \mid \sigma(\tilde h)$.  Compute
$$
\sigma(\tilde h)(t) \;=\; (t^r + \lambda t^{r'} - q(-t)) \cdot g_B(t),
$$
since $\sigma(g_{B+8}) = g_B$ and $r$ even, $r'$ odd.

Form the $\sigma$-eigenpieces $\tilde h_\pm := \tilde h \pm \sigma(\tilde h)$,
both divisible by $g_{S^*}$:
$$
\begin{aligned}
\tilde h_+(t) &= 2\,\Big[\, t^r g_B^{\mathrm{even}}(t) + \lambda t^{r'} g_B^{\mathrm{odd}}(t) - q_e(t) g_B^{\mathrm{even}}(t) + q_o(t) g_B^{\mathrm{odd}}(t)\,\Big],\\
\tilde h_-(t) &= -2\,\Big[\, t^r g_B^{\mathrm{odd}}(t) + \lambda t^{r'} g_B^{\mathrm{even}}(t) + q_o(t) g_B^{\mathrm{even}}(t) - q_e(t) g_B^{\mathrm{odd}}(t)\,\Big].
\end{aligned}
$$
$\tilde h_+$ is even, $\tilde h_-$ is odd; substituting $y = t^2$ and writing
$g_B^{\mathrm{even}}(t) = G_e(y)$, $g_B^{\mathrm{odd}}(t) = t \cdot G_o(y)$:
$$
\tilde h_+(t) = H_+(y), \qquad \tilde h_-(t) = t \cdot H_-(y),
$$
with
$$
\boxed{\;
\begin{aligned}
H_+(y) &= y^{r/2} G_e(y) + \lambda y^{(r'+1)/2} G_o(y) - (\alpha + \beta y) G_e(y) + (c y + d y^2) G_o(y),\\
H_-(y) &= y^{r/2} G_o(y) + \lambda y^{(r'-1)/2} G_e(y) + (c + d y) G_e(y) - (\alpha + \beta y) G_o(y).
\end{aligned}\;}
$$

Since $G_*(0) = \prod_{s\in S^*}(-\omega^s) \neq 0$, we have $\gcd(G_*(y), y) = 1$,
so $g_{S^*} \mid t \cdot H_-(y)$ ⇔ $G_*(y) \mid H_-(y)$.  Combined:

> **Reduced system.**  $\mathrm{HT}(t^r) = \lambda \mathrm{HT}(t^{r'})$ with $r$
> even, $r'$ odd, $\lambda \in \mathbb{F}_q^*$, implies the existence of
> $\alpha, \beta, c, d \in \mathbb{F}_q$ with
> $$
> G_*(y) \;\Big|\; H_+(y) \qquad \text{and} \qquad G_*(y) \;\Big|\; H_-(y) \quad \text{in } \mathbb{F}_q[y].
> $$

This is a system of $2 \deg G_* = |S^*| = 8 + |B|$ scalar equations in
$5$ unknowns $(\alpha, \beta, c, d, \lambda)$.  For $|B| \ge 1$ the
system is over-determined, and the lemma claims it admits no
$\lambda \ne 0$ solution.

---

## 7.  σ-symmetric subcase recovered

When $|B| = 0$ (i.e., $S = A$), $g_B = 1$, so $G_e = 1$ and $G_o = 0$:
$$
H_+(y) = y^{r/2} - (\alpha + \beta y), \qquad H_-(y) = \lambda y^{(r'-1)/2} + (c + d y).
$$
$\deg G_* = 4$ (since $|S^*| = 8$, $|B| = 0$).

For $r/2 \in \{2, 3\}$ (i.e., $r \in \{4, 6\}$) and $(r'-1)/2 \in \{2, 3\}$
(i.e., $r' \in \{5, 7\}$), $\deg H_\pm < \deg G_* = 4$, so divisibility forces
$H_\pm \equiv 0$.  This yields $r/2 \in \{0, 1\}$ for $H_+$, contradicting
$r \ge 4$.

For $r \in \{8, 10, 12, 14\}$ (so $r/2 \ge 4$), $G_*(y) \mid y^{r/2} - \alpha - \beta y$
becomes a divisibility relation of comparable degree; combined with
$G_*(y) \mid \lambda y^{(r'-1)/2} + c + d y$ for $r' \in \{9, 11, 13, 15\}$
the constraint reduces to: both $y^{r/2}$ and $y^{(r'-1)/2}$ reduce mod
$G_*(y)$ to degree-$\le 1$ polynomials.  But this is *exactly* the
σ-symmetric case from §4 in disguise — in $\mathbb{F}_q[y]/G_*(y)$ each $y^k$
either has degree $\le 1$ residue or it doesn't, independently of the
proportionality structure, so the §4 disjoint-coordinate argument applies.

---

## 8.  General case (1 ≤ |B| ≤ 8): the remaining algebraic step

For $|B| \ge 1$ both $G_e, G_o$ are nontrivial polynomials in $y$, and
$H_\pm$ are genuinely $5$-parameter pencils.  The **claim to prove**:

> **Conjecture (reduced character system).**  For every no-full $S$ at
> $L_2 = (16, 4)$ with $|B| \ge 1$, the linear system
> $$ G_*(y) \mid H_+(y), \qquad G_*(y) \mid H_-(y) $$
> on $(\alpha, \beta, c, d, \lambda)$ is *inconsistent* over $\mathbb{F}_q$,
> for any $r \in \{4, 6, 8, 10, 12, 14\}$ and $r' \in \{5, 7, 9, 11, 13, 15\}$.

(Inconsistency $\Rightarrow$ no $\lambda$ at all, so in particular no
$\lambda \ne 0$ — a stronger statement than the lemma needs.)

**Empirical confirmation of the reduction.**  Script
`issue419_reduced_system_rank_audit.py` builds the reduced linear system
explicitly per $(S, r, r')$ and checks whether
$\mathrm{rank}([M | \mathrm{LHS}]) = \mathrm{rank}(M)$:

```text
q=97, all 10896 no-full S:
  σ-symmetric S skipped:  16 (covered by §4)
  General S × opp-parity: 10880 × 72 = 783360 reduced systems
  Inconsistent (no soln): 783360   ← ALL
  Consistent (any soln):  0
Rank distribution (rank M, deg G_*, |B|):
  rank-5 systems: 718080  (91.7% — full column rank)
  rank-4 systems:  65280  (8.3%  — column dependence, but still inconsistent)
```

The reduction is therefore confirmed empirically at $q = 97$ across the
**full enumeration** of no-full $S$.  Since the reduction is equivalent
to the original opposite-parity test, this is a re-derivation of Note 0393's
empirical result via the $\sigma$-isotypic linear-algebra structure.

Two natural paths to prove it structurally:

**Path A (degree counting / linear-algebra invariants).**
The system is *linear* in $(\alpha, \beta, c, d, \lambda)$ with $8 + |B|$
equations and $5$ unknowns (over-determined by $3 + |B|$).  Inconsistency
is equivalent to the constant column $(\mathrm{LHS}_+, \mathrm{LHS}_-)$
not lying in the column span of $M(S, r, r')$.  Construct a *witness
covector* $w \in \mathbb{F}_q^{8+|B|}$ such that $w \cdot M = 0$ but
$w \cdot \mathrm{LHS} \ne 0$ — symbolically, in terms of $G_e, G_o$ —
for every $S$.  The $w$ should be a polynomial expression in the
coefficients of $g_S$ (or of $G_*$), with the no-full condition entering
as a non-vanishing of a specific minor.

**Path B (resultants over $\mathbb{Z}[\omega]$).**  $G_*(y) \mid H_+(y)$
and $G_*(y) \mid H_-(y)$ together imply $G_*(y) \mid \gcd(H_+, H_-)$.
Compute the resultant $\mathrm{Res}_y(H_+, H_-)$ as a polynomial in
$(\alpha, \beta, c, d, \lambda)$; the conjecture is equivalent to: the
variety $\{ \mathrm{Res} = 0 \} \cap \{\lambda \ne 0\}$ is empty over
$\mathbb{F}_q$ for every no-full $G_*$.

**Field uniformity.**  The system has integer coefficients (after clearing
$\omega$ via $G_*(y) \in \mathbb{Z}[\omega][y]$).  Verifying emptiness over
$\mathbb{Q}$ via Gröbner basis (with formal $\omega$ a primitive $16$-th
root) would upgrade the empirical $3$-prime confirmation to all
primes outside a finite exceptional set, computable from the Gröbner
basis denominators.

---

## 9.  Closure status update (after Note 0396)

| Subcase | Status | Note |
|---|---|---|
| $\sigma$-symmetric $S$ ($|A| = 8$, $|B| = 0$) | **PROVEN field-uniformly** (any odd char with $16 \mid q-1$) | 0396 §4 |
| Non-$\sigma$-symmetric $S$ ($|B| \ge 1$) | reduced to finite linear system; *all* $783\,360$ systems at $q=97$ inconsistent (full enum); cross-prime at $q \in \{193, 1153\}$ via Note 0393 | 0396 §6, §8 |
| Side-$(2,2)$ 4-supp closure | implied by pairwise lemma above | 0393, 0394, 0396 |
| Side-$(3,1)$ / $(1,3)$ 4-supp | open (3-vector lemma refuted in Note 0395) | 0395 |
| 5-supp / 6-supp / 7-supp | open structurally; $0$ over $\sim 615$M trials | 0392 |

---

## 10.  Next concrete artifact

**Tier 1a continuation.**  Complete the polynomial-system proof of §8 for
$|B| \ge 1$ via Path A (degree counting + case analysis on $|B|$ and
quadrant pattern of $B$) or Path B (resultant + Gröbner over $\mathbb{Z}[\omega]$).

**Tier 1b.**  Lift the proven lemma from $L_2 = (16, 4)$ to $L_2 = (n, n/4)$
at general dyadic depth.  The $\sigma$-symmetric argument (§4) generalizes
verbatim once the parity/$\sigma$-isotypic structure is identified for
$\mathbb{Z}/n\mathbb{Z}$ ($n = 2^d$); the doubling reduction (§§5–6) is
also dimension-agnostic.  Output target: Note 0397.

**Together with the pending Tier 1a polynomial-system proof, these would
give an unconditional, field-uniform, scale-uniform proof of the side-$(2,2)$
$4$-supp closure of the Q2 finite-root primitive theorem.**
