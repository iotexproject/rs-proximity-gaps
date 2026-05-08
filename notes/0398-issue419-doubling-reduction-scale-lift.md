# Note 0398 -- Issue #419: doubling reduction at scale L₂=(n, n/4) (Tier 1b extension)

**Date:** 2026-05-02 (Tier 1b iteration 2 — extend Note 0396 §6 to n>16)
**Branch:** `main`
**Status:** §6 doubling reduction generalized to arbitrary $L_2 = (n, n/4)$
with $n = 2^d$, $d \ge 3$.  Reduced linear system has
$|S^*|$ equations in $(k_2 + 1)$ unknowns, over-determined by
$k_2 + |B| - 1 \ge k_2$.  Empirical confirmation at $L_2 = (32, 8)$
deferred to next iteration; structural shape established here.

---

## 1.  Setup at scale

At $L_2 = (n, n/4)$:
* $\omega \in \mathbb{F}_q^*$ primitive $n$-th root, $n = 2^d$, $d \ge 3$.
* $S \subset \mathbb{Z}/n\mathbb{Z}$, $|S| = n/2$, no-full ($|S \cap C_j| < k_2$
  for each coset $C_j$ of $\langle 4 \rangle$).
* $g_S(t)$ degree $n/2$.
* $\mathrm{HT}: \mathbb{F}_q[t]/g_S \to \mathbb{F}_q^{k_2}$ projects onto
  coefficients at degrees $\{k_2, k_2+1, \ldots, n/2 - 1\}$.

The "low" polynomial $q(t)$ orthogonal to $\mathrm{HT}$ has degree $< k_2 = n/4$,
i.e., $q \in \mathbb{F}_q[t]_{<n/4}$ has $k_2$ coefficients.
Decompose into even/odd parts:
$$
q(t) = q_e(t) + q_o(t), \quad q_e \in \mathrm{span}\{1, t^2, \ldots, t^{k_2-2}\}, \;
q_o \in \mathrm{span}\{t, t^3, \ldots, t^{k_2-1}\}.
$$
$q_e$ has $k_2/2$ coefficients $\alpha_0, \alpha_1, \ldots, \alpha_{k_2/2 - 1}$
(coefficient of $t^{2i}$).  Similarly $q_o$ has $k_2/2$ coefficients
$\gamma_0, \ldots, \gamma_{k_2/2 - 1}$ (coefficient of $t^{2i+1}$).

Total unknowns: $k_2 + 1$ (the $k_2$ coefficients of $q$ plus $\lambda$).

---

## 2.  Doubling reduction at scale

$S^* := S \cup (S + n/2)$ (σ-symmetric).  $g_{S^*}(t) = G_*(y)$ with
$y = t^2$, $\deg G_* = |S^*|/2 = n/4 + |B|/2$.

Setup as in Note 0396 §6:
$g_S(t) g_{B+n/2}(t) = g_{S^*}(t) \mid f_\lambda(t) g_{B+n/2}(t) =: \tilde h(t)$.

$\sigma$-eigenpieces $\tilde h_\pm$ are even/odd polynomials, each
divisible by $g_{S^*}$.  Substituting $y = t^2$:
$\tilde h_+(t) = H_+(y)$ and $\tilde h_-(t) = t \cdot H_-(y)$.

The polynomial decomposition $g_B(t) = g_B^{\mathrm{even}}(t) + t \cdot g_B^{\mathrm{odd}}(t)/t = G_e(y) + t \cdot G_o(y)$
(where $G_e$, $G_o$ are polynomials in $y$) extends verbatim.

Compute:
$$
H_+(y) = (y^{r/2} - q_e(y)) G_e(y) + (\lambda y^{(r'+1)/2} + y \cdot q_o^*(y)) G_o(y),
$$
$$
H_-(y) = y^{r/2} G_o(y) + \lambda y^{(r'-1)/2} G_e(y) + q_o^*(y) G_e(y) - q_e(y) G_o(y),
$$
where I have written $q_e(y) := \sum_i \alpha_i y^i$ (a polynomial in $y$ of
degree $\le k_2/2 - 1$) and $q_o^*(y) := \sum_i \gamma_i y^i$ (degree $\le k_2/2 - 1$),
so $q_o(t) = t \cdot q_o^*(t^2) = t \cdot q_o^*(y)$.

Both $H_+, H_-$ are linear in $\{\alpha_i, \gamma_i, \lambda\}$ with $k_2 + 1$
unknowns total.

The reduced system is:
$$
\boxed{\; G_*(y) \mid H_+(y) \quad \text{AND} \quad G_*(y) \mid H_-(y). \;}
$$

This is $2 \deg G_* = n/2 + |B|$ scalar linear equations in $k_2 + 1 = n/4 + 1$
unknowns over $\mathbb{F}_q$, over-determined by $n/4 + |B| - 1$.

---

## 3.  Comparison to L₂=(16,4)

| Quantity | $L_2=(16, 4)$ | $L_2=(n, n/4)$, general |
|---|---|---|
| $k_2$ | $4$ | $n/4 = 2^{d-2}$ |
| $q$ coefficients | $4$ ($\alpha, \beta, c, d$) | $k_2$ ($\alpha_i, \gamma_i$ each $k_2/2$ many) |
| Unknowns (incl. $\lambda$) | $5$ | $k_2 + 1$ |
| $\deg G_*$ | $4 + |B|/2$ | $n/4 + |B|/2$ |
| Equations | $8 + |B|$ | $n/2 + |B|$ |
| Over-determination | $3 + |B|$ | $n/4 + |B| - 1$ |

For $n = 32$, $k_2 = 8$: $9$ unknowns, $16 + |B|$ equations,
over-determined by $7 + |B|$.

---

## 4.  Inconsistency claim at scale

**Conjecture (reduced character system, scale-uniform).**  For every
$L_2 = (n, n/4)$ with $n = 2^d$, $d \ge 3$, every no-full $S$ with $|B| \ge 1$,
every $r \in \{k_2, k_2+2, \ldots, n-2\}$ even, and every $r' \in \{k_2+1,
k_2+3, \ldots, n-1\}$ odd, the linear system
$G_*(y) \mid H_+(y) \;\wedge\; G_*(y) \mid H_-(y)$ is inconsistent over $\mathbb{F}_q$.

**Empirical status:**
* $L_2 = (16, 4)$ at $q = 97$: full enumeration $783\,360 / 783\,360$ inconsistent
  (Note 0396 §8 + script verifier).
* $L_2 = (16, 4)$ at $q \in \{193, 1153\}$: prime-uniform via Note 0393 direct test.
* $L_2 = (32, 8)$: $\sigma$-symmetric subcase verified at $784\,512$ HT-prediction
  cases (Note 0397).  General $|B| \ge 1$ inconsistency: pending verifier
  extension (next iteration).

---

## 5.  What still needs the bookkeeping extension

The script `issue419_reduced_system_rank_audit.py` was hardcoded for
$L_2 = (16, 4)$ (5 unknowns, columns $\alpha, \beta, c, d, \lambda$).
To extend:

1. Generalize column construction: for each $i \in \{0, 1, \ldots, k_2/2 - 1\}$,
   columns $\alpha_i$: $(-y^i G_e \bmod G_*, -y^i G_o \bmod G_*)$.
   For each $i$, columns $\gamma_i$: $(y^{i+1} G_o \bmod G_*, y^i G_e \bmod G_*)$.
   Plus $\lambda$ column as before.
2. Build $(n/2 + |B|) \times (k_2 + 1)$ matrix per $(S, r, r')$.
3. Test rank consistency.

This is mechanical Python work, ~30 lines of generalization to the existing
script.  Empirical verification at $L_2 = (32, 8)$ would need sampling
(no-full enumeration is $O(\binom{32}{16}) \approx 6 \times 10^8$, too large).

---

## 6.  Remaining structural step (Tier 1a Path A continuation)

Setting $u_0 := (-G_e, -G_o)$ and $v_0 := (y G_o, G_e)$ as the two "basis
vectors" of $M$'s columns (re-derived from §6 by recognizing
$\mathrm{col}_{\alpha_i} = y^i u_0$, $\mathrm{col}_{\gamma_i} = y^i v_0$,
$\mathrm{col}_\lambda = y^{(r'-1)/2} v_0$, $\mathrm{LHS} = -y^{r/2} u_0$),
the consistency condition becomes:
$$
(P(y) + y^{r/2}) G_e(y) \equiv Q(y) y G_o(y) \pmod{G_*(y)}, \qquad \text{(I)}
$$
$$
(P(y) + y^{r/2}) G_o(y) \equiv Q(y) G_e(y) \pmod{G_*(y)}. \qquad \text{(II)}
$$
Here $P(y) = q_e(y)$ (degree $< k_2/2$, the even part of $q$ as a polynomial
in $y$), and $Q(y) = q_o^*(y) + \lambda y^{(r'-1)/2}$ (the odd part of $q$
restated in $y$, plus the $\lambda$ term).

**Key identity.**  $G_e(y)^2 - y G_o(y)^2 = g_B(t) \cdot g_B(-t) = g_B(t) \cdot g_{B+n/2}(t) = g_{S^*}(t)/g_A(t)$.
In $y$-form: $G_e^2 - y G_o^2 = G_*(y)/G_A(y)$, where $G_A(y)$ is the
$y$-form of $g_A(t)$ ($\deg G_A = |A|/2$).

**Two divisibility consequences.**  Multiplying (I) by $G_o$ and (II) by $G_e$,
subtracting gives $Q(y) (G_e^2 - y G_o^2) \equiv 0 \pmod{G_*}$, i.e.,
$Q \cdot G_*/G_A \equiv 0 \pmod{G_*}$, i.e.,
$$
G_A(y) \mid Q(y). \qquad \text{(D-Q)}
$$
Symmetrically, multiplying (I) by $G_e$ and (II) by $y G_o$, subtracting
gives $(P + y^{r/2})(G_e^2 - y G_o^2) \equiv 0 \pmod{G_*}$, i.e.,
$$
G_A(y) \mid (P(y) + y^{r/2}). \qquad \text{(D-P)}
$$

**Necessary, not sufficient.**  (D-P) ∧ (D-Q) is implied by (I) ∧ (II), but
the converse needs (I) or (II) directly.  However, (D-P) and (D-Q) are
*strong* constraints when $|A|/2 \ge k_2/2$:

* (D-P) says $y^{r/2} \bmod G_A(y) = -P(y)$, a polynomial of degree
  $< k_2/2$.  When $\deg G_A = |A|/2 \ge k_2/2$, the residue
  $y^{r/2} \bmod G_A$ generically has degree $|A|/2 - 1 \ge k_2/2 - 1$,
  *exceeding* the allowed $< k_2/2$ unless a structural coincidence holds.

* (D-Q) says $Q(y)$ vanishes at every root $\omega^{2 a_i}$ of $G_A$.
  $Q$ has at most $3$ free coefficients in the form $c + d y + \lambda y^m$
  for the $L_2 = (16, 4)$ case (or up to $k_2/2 + 1$ for larger $k_2$).
  When the $|A|/2$ vanishing equations exceed the free parameters, $Q = 0$
  is forced; combined with (II), this forces $(P + y^{r/2}) G_o \equiv 0
  \pmod{G_*}$, a strong constraint.

> **Reformulated lemma (clean Tier 1a target).**  For every no-full $S$
> at $L_2 = (n, n/4)$ and every $r \in \{k_2, k_2+2, \ldots, n-2\}$ even,
> $r' \in \{k_2+1, \ldots, n-1\}$ odd:
>
> Either (A) $y^{r/2} \bmod G_A(y)$ has degree $\ge k_2/2$ (so (D-P) fails
> for all admissible $P$), OR (B) the required $Q$-shape $c + d y + \lambda y^m$
> cannot vanish at all roots of $G_A$ (so (D-Q) fails).  In either case the
> system (I) ∧ (II) is inconsistent.

The cases split by $|A|$:
* $|A|/2 \ge k_2/2 + 1$ ($|A| \ge k_2 + 2$): (D-P) generically fails by
  degree count.
* $|A|/2 = k_2/2$ ($|A| = k_2$): (D-P) is generically satisfied (any
  $y^{r/2} \bmod G_A$ has degree $< k_2/2$); inconsistency must come from
  (D-Q) or the $(I) \Leftrightarrow (II)$ compatibility.
* $|A|/2 < k_2/2$ ($|A| < k_2$): both (D-P) and (D-Q) are non-trivial;
  full system (I) ∧ (II) carries the inconsistency.

For $L_2 = (16, 4)$, $k_2 = 4$, $k_2/2 = 2$:
* $|A| = 8$: $\sigma$-symmetric (already proven).
* $|A| = 6$: (D-P) gives $\deg(y^{r/2} \bmod G_A) \le 2 < |A|/2 = 3$;
  $r/2 \in \{2, ..., 7\}$ generically gives degree $|A|/2 - 1 = 2$;
  the $< k_2/2 = 2$ allowance forces degree $\le 1$ — borderline, needs case work.
* $|A| = 4$: $\deg G_A = 2$; $y^{r/2} \bmod G_A$ has degree $\le 1 < k_2/2 = 2$,
  vacuous, so (D-Q) carries the load.
* $|A| = 2$: $\deg G_A = 1$, vacuous on (D-P) and weak on (D-Q).
* $|A| = 0$: both vacuous; full (I) ∧ (II) needed.

---

## 7.  No-full constraint on $|A|$

$A$ is the σ-symmetric part of $S$.  Since each σ-orbit $\{s, s+n/2\}$ lies
within a single coset of $\langle 4 \rangle$ (because $n/2 \in \langle 4 \rangle$
for $d \ge 3$), the no-full bound $|S \cap C_j| < k_2$ implies
$|A \cap C_j| \le 2 \lfloor (k_2 - 1)/2 \rfloor = k_2 - 1$ if $k_2$ odd,
$k_2 - 2$ if $k_2$ even.  Summing over $4$ cosets:
$$
|A| \le 4 \cdot (k_2 - \mathrm{parity\ correction}) = O(4 k_2 - 4) = O(n - 4).
$$
For $L_2 = (16, 4)$, $k_2 = 4$ even: $|A| \le 4 \cdot 2 = 8$, attained
by σ-symmetric $S$ (16 such $S$, Note 0396 §4).
For $L_2 = (32, 8)$, $k_2 = 8$ even: $|A| \le 4 \cdot 6 = 24$.

So the σ-symmetric extreme $|A| = n/2$ is allowed only when each coset
intersection $|A \cap C_j|$ exactly equals $k_2$ — but this is the *full*
case, excluded by no-full.  Hence $|A| < n/2$ strictly for no-full $S$, and
$|A|/2 < k_2$.  In particular $\deg G_A < k_2$.

---

## 8.  Tier 1 status summary (after Notes 0396, 0397, 0398)

| Sub-claim | Status | Note |
|---|---|---|
| σ-symmetric, $L_2=(16,4)$ | PROVEN | 0396 §4 |
| σ-symmetric, $L_2=(n,n/4)$, $d\ge 3$ | PROVEN field+scale-uniform | 0397 §3 |
| General $|B|\ge 1$, $L_2=(16,4)$, reduction | EXPLICIT linear system | 0396 §6 |
| General $|B|\ge 1$, $L_2=(16,4)$, inconsistency | empirically full-enum at $q=97$, prime-uniform via Note 0393 | 0396 §8 |
| General $|B|\ge 1$, $L_2=(n,n/4)$, reduction | derived (this note §2) | 0398 §2 |
| **Two-divisibility decomposition** (this note §6) | reduces inconsistency to (D-P) ∧ (D-Q) ∧ system compatibility | 0398 §6 |

The clean-form lemma in §6 splits the inconsistency proof into two
divisibility statements (D-P) and (D-Q), each accessible:
* (D-P) is a polynomial-residue statement: $y^{r/2} \bmod G_A(y)$ has
  degree $\ge k_2/2$ — easily verified empirically and provable by
  $\sigma$-orbit structure of $A$.
* (D-Q) is a vanishing statement on $|A|/2$ values: $Q(y)$ of prescribed
  shape cannot vanish at all roots of $G_A$.

**Next concrete artifact (next iteration):** verify the (D-P) and (D-Q)
divisibility predictions empirically across the $|A|$-stratification, and
then assemble the structural proof case-by-case.  Output target: Note 0399.
