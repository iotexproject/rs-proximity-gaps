# Note 0385 — Q1 recursion theorem (corrected post Note 0315 retraction)

**Date:** 2026-05-01
**Branch:** feat/op1a-algorithm-fixes
**Status:** Re-derives the *valid* per-$d$ recursion for Q1@$d$ (paper2
`conj:Q1`) using only Self-Similarity (Note 0267 / Lemma 0315.7) and
the orbit decomposition. Removes the dependency on the **retracted**
$(\ast)@d \Rightarrow$ Q1@$d$ implication (Note 0315 Theorem 0315.4,
RETRACTED at commit `332faac` on `fri-2round-tightness`).

## Motivation

Issue #428 frames Path A (structural induction) as

> "If Q1@$e$ holds for every $e \mid d$ with $e < d$, AND $(\ast)@d$
> holds, AND the vdim consistency formula recurses correctly, THEN
> Q1@$d$ holds."

paper2 main `rem:Q1-induction-framework` (commit `8ac87cc`) inherits
this framing and writes the conclusion as:

> "$\mathrm{vdim}(I_{\mathrm{chain}}^{(d)} + \langle R_d \rangle) = 1$
> follows by orbit decomposition $V(I_{\mathrm{chain}}^{(d)}) = \{0\}
> \sqcup \bigsqcup_{e \mid d, e \geq 4} V_e^{\mathrm{prim}}$"

after assuming (i) Q1@$e$ for $e < d$, (ii) $(\ast)@d$, (iii) chain
self-similarity.

**The implicit step (ii) $\Rightarrow$ "Q1@$d$ on $V_d^{\mathrm{prim}}$"
is the retracted Catalan F(0) reduction.** Without it, $(\ast)@d$ does
*not* imply $R_d \not\equiv 0$ on $V_d^{\mathrm{prim}}$.

This note states what *does* go through.

## The valid recursion

For $d = 2^k$, $k \geq 2$, write $V_d := V(I_{\mathrm{chain}}^{(d)})$
and $V_d^{\mathrm{prim}}$ for the intrinsic length-$d$ orbit stratum.
Let
\[
   R_d \;:=\; -3\,x_{d/2} + 2\,V_{d/2} + 3\,W_{d/2}
\]
(Note 0275 reduction).

### Lemma 1 (R_d at sub-strata equals R_e intrinsic)

For every $e \mid d$ with $4 \leq e < d$, the restriction
$R_d \big|_{V_e^{\mathrm{prim}}}$ equals
$R_e \big|_{V_e^{\mathrm{prim}}}$ (the intrinsic $e$-chain's $R_e$),
under the relabeling $x_a^{(d)} = x_{a/(d/e)}^{(e)}$ for $a$ a multiple
of $d/e$ (Note 0267 self-similarity).

**Proof.** Write $r := d/e$. Points of $V_e^{\mathrm{prim}}$ have
$x_a = 0$ for $r \nmid a$. So:
- $x_{d/2}|_{V_e^{\mathrm{prim}}}$: nonzero iff $r \mid d/2$, i.e.
  $r \mid r e/2$, i.e.\ $e$ is even (true for $e = 2^j, j \geq 2$);
  then $x_{d/2} = x_{e/2}^{(e)}$ in intrinsic coords.
- $V_{d/2}^{(d)} = \sum_{a + b = d/2,\ 1 \le a \le b \le d-1}
   c_{a,b}\, x_a x_b$ with $c_{a,b} = 2$ ($a \neq b$), $c_{a,a} = 1$.
  At $V_e^{\mathrm{prim}}$: only $a, b$ both multiples of $r$ survive.
  Writing $a = r a'$, $b = r b'$ with $a' + b' = e/2$, get
  $V_{d/2}|_{V_e^{\mathrm{prim}}} = V_{e/2}^{(e)}$ (intrinsic).
- Same calculation for $W_{d/2}$ with $a + b = 3d/2 = 3 r e/2$ giving
  $W_{d/2}|_{V_e^{\mathrm{prim}}} = W_{e/2}^{(e)}$.

Therefore $R_d|_{V_e^{\mathrm{prim}}} = -3 x_{e/2}^{(e)} +
2 V_{e/2}^{(e)} + 3 W_{e/2}^{(e)} = R_e$ (intrinsic $e$-chain). $\square$

### Definition (strong form of Q1@d)

$$\mathrm{Q1}@d \;:\;\; R_d(P) \neq 0 \;\;\text{for every}\;\;
P \in V_d^{\mathrm{prim}}.$$

Equivalently: $V_d^{\mathrm{prim}} \cap V(R_d) = \emptyset$. This is
*strictly stronger* than "$R_d$ does not vanish identically on
$V_d^{\mathrm{prim}}$" because $V_d^{\mathrm{prim}}$ is a finite union
of Galois orbits and $R_d$ could vanish on a proper subset of orbits.
The strong form is what the Norm computation (Note 0277) and the vdim
test (Note 0316) actually verify.

### Theorem 2 (Q1@d via per-d vdim test)

Assume Q1@$e$ (strong form) holds for every $e \mid d$ with $4 \le e < d$.
Then
\[
   \mathrm{Q1}@d \;\;\Longleftrightarrow\;\;
   \mathrm{vdim}\!\bigl(I_{\mathrm{chain}}^{(d)} + \langle R_d\rangle
   \bigr) = 1.
\]

**Proof.** Apply orbit decomposition (Note 0267):
\[
   V(I_{\mathrm{chain}}^{(d)} + \langle R_d \rangle)
   \;=\; \bigl(\{0\} \sqcup \bigsqcup_{4 \le e \mid d}
            V_e^{\mathrm{prim}}\bigr) \cap V(R_d).
\]
- $\{0\} \cap V(R_d) = \{0\}$ since $R_d(0) = 0$. Contributes $1$ to vdim.
- For each $e \mid d$, $4 \le e < d$: by Lemma 1, $R_d|_{V_e^{\mathrm{prim}}}
  = R_e$ (intrinsic). By the inductive hypothesis Q1@$e$ (strong),
  $R_e \neq 0$ at every point of $V_e^{\mathrm{prim}}$. Hence
  $V_e^{\mathrm{prim}} \cap V(R_d) = \emptyset$. Contributes $0$.
- For $e = d$: $V_d^{\mathrm{prim}} \cap V(R_d) = \emptyset$ iff Q1@$d$
  (strong form).

Hence $\mathrm{vdim} = 1 + |V_d^{\mathrm{prim}} \cap V(R_d)|$, which is
$1$ iff Q1@$d$ (strong form) holds. $\square$

**Remark.** This is exactly the equivalence stated in Note 0316
(commit `2191184` on `fri-2round-tightness`). The point of writing it
out here is that the *strong-form* convention is what makes the
equivalence go through. The weak-form ("$R_d \not\equiv 0$ on
$V_d^{\mathrm{prim}}$") is insufficient — strict-subset vanishing
could leave isolated $V_d^{\mathrm{prim}} \cap V(R_d)$ points in the
ideal, inflating vdim.

### Remark 3 (No structural shortcut)

Theorem 2 is **a per-$d$ test**, not a structural induction lifting per-$d$
results to all $d = 2^k$. The remaining open problem is exactly what the
RETRACTED Note 0315 Theorem 0315.4 attempted to solve: a *uniform-in-$d$*
proof that $R_d \not\equiv 0$ on $V_d^{\mathrm{prim}}$.

The Note 0315 attempt invoked the recursion $a_c = -3 \sum a_a a_{c-a}$
(Catalan), but this recursion came from (incorrectly) reading the
"constant-in-$s$" coefficient of $c_c$ as zero. The *valid* identity is
\[
   a_c + 3 F_c(0) \;=\; q_c(0) \cdot H_d(0)
\]
where $q_c$ is the chain quotient $c_c / H_d(s)$. Knowing $q_c(0)$
universally (or bounding the right side away from $0$) is exactly the
open structural problem.

### Remark 4 ($(\ast)@d$ is a separate conjecture, not implied by Galois)

$(\ast)@d$: $V_d^{\mathrm{prim}} \cap \{x_1 = 0\} = \emptyset$ (strong
form: $x_1 \neq 0$ at every point of $V_d^{\mathrm{prim}}$).

Galois $(\mathbb Z/d)^*$-equivariance (Note 0315 Obs 3) propagates "some
$P$ has $x_1(P) = 0$" to "for each odd $a$, some Galois-conjugate $P_a$
has $x_a(P_a) = 0$". This is a symmetry constraint, **not** a contradiction
with "length-$d$ orbits require some odd $x_a \neq 0$" (Obs 2): each
$P_a$ separately can have other odd $x_b$ ($b \neq a$) nonzero. So
$(\ast)@d$ is *not* automatic.

$(\ast)@d$ is rigorous at $d \in \{4, 8\}$ (Note 0315: Singular GB
multi-prime). At $d \ge 16$ it's an empirical conjecture in its own
right.

Even granting $(\ast)$ universal, the implication $(\ast)@d \Rightarrow
\mathrm{Q1}@d$ — which would unlock universal Q1 from a single linear
condition — was the goal of Note 0315 Theorem 0315.4 via Catalan F(0).
That theorem is **retracted** because the recursion $a_c = -3 \sum a_a
a_{c-a}$ (constant-in-$s$ reading) is invalid: $c_c \equiv 0
\pmod{H_d(s)}$ is not the same as $c_c \equiv 0$ as a polynomial in $s$.

Without the F(0) bridge, $(\ast)@d$ has no clear logical relationship
with Q1@$d$ (in either direction): each is a non-vanishing claim about a
*different* polynomial on $V_d^{\mathrm{prim}}$, and the retracted
Catalan identity was the only known link. Both remain open conjectures
at $d \ge 16$ in their own right; verifying one doesn't help the other.

## What this means for #428 and paper2

### For Issue #428

- **Path A (structural induction)** as written assumes Note 0315's
  retracted reduction. The actual valid recursion (Theorem 2 above) is
  a *per-$d$ test*, not a structural shortcut. So Path A's "single
  structural step: prove $(\ast)@d$ for general $d$" does NOT close
  Q1 universal.
- **Path B (deployment-pragmatic)** is the realistic route: per-$d$
  Singular vdim at $d = 2^k$ for $k \le K_{\mathrm{max}}$.

### For paper2 main `rem:Q1-induction-framework`

The remark currently states that $(\ast)@d$ + chain self-similarity +
Q1@$e$ ($e < d$) gives the vdim test result $= 1$. This is incorrect
post-retraction.

Suggested correction: either
1. **Drop $(\ast)@d$ as an ingredient.** State Theorem 2 above as the
   valid recursion: Q1@$d$ is verified per-$d$ via the vdim test, given
   Q1@$e$ for $e < d$. The "induction framework" reduces to a finite
   chain of per-$d$ Singular checks, not a single universal statement.
2. **Restore the closed-form bridge.** This requires either reviving the
   Note 0315 Catalan argument (would need a different proof — the
   "constant-in-$s$" reading is invalid) or finding a new structural
   identity linking $(\ast)@d$ to Q1@$d$.

Option 1 is honest about the current state. Option 2 is a research
problem.

## Operational notes (2026-05-01 session)

Direct Singular `std()` of $I_{\mathrm{chain}}^{(16)} + \langle R_{16} \rangle$
over $\FF_{1009}$ is heavy: parallel runs over $\FF_{1009}$ and $\FF_{31}$
on Studio (M3 Ultra, 256 GB RAM, single-thread Singular) exceeded 1 hour
each in `std()` with RAM at 4+ GB and growing slowly. Note 0316's
"$\sim 10$ min" estimate appears to have been the unmeasured "pending"
status guess, not a real measurement.

The right tool here is **msolve** (Berthomieu--Eder--Safey El Din,
v0.9.5 on Studio at `/opt/homebrew/Cellar/msolve/0.9.5_1/bin/msolve`),
which uses F4 + FGLM and parallelizes natively. msolve input format is
trivial (vars line, characteristic, polynomials), and the included
`scripts/contrib_paper2/gen_msolve_chain.py` produces it from a
symbolic chain expansion.

Coordination: codex launched `msolve -t 16` on this same input
($\FF_{1009}$, d=16) at 2026-05-01 14:29; result pending (40 min CPU,
12.9 GB RAM at 8 min wall when observed). Once that result lands
on `fri-2round-tightness`, integrate.

For $d = 32$ direct vdim: input file `d32_F1009.ms` (31 vars, 32 polys
including $R_{32}$) staged on Studio. Launch after $d = 16$ finishes
(don't compete for RAM/CPU).

## Lemma A' — algebraic rewrite of $R_d$ on the chain locus

**Lemma A' (polynomial identity).** For $d = 2^k$, $k \geq 2$, the following
holds in $\mathbb{Z}[x_1, \dots, x_{d-1}]$:
\[
  R_d \;-\; S_d \;=\; -3\, c_{d/2},
\]
where
\[
  R_d = -3 x_{d/2} + 2 V_{d/2} + 3 W_{d/2}, \qquad
  S_d = 11\, V_{d/2} + 6\, (XW)_{d/2} - 3\, (WW)_{d/2}.
\]

*Proof.* Direct expansion: $-3 c_{d/2} = -3(x_{d/2} - W_{d/2}) - 9 V_{d/2}
- 6 (XW)_{d/2} + 3 (WW)_{d/2}$, giving $R_d - S_d = -3 c_{d/2}$ termwise.
\qed

**Corollary.** $R_d \equiv S_d \pmod{c_{d/2}}$, hence $R_d|_{V_d^{\mathrm{prim}}}
= S_d|_{V_d^{\mathrm{prim}}}$. In particular, Q1@d is equivalent to
$S_d \neq 0$ on $V_d^{\mathrm{prim}}$.

**Verification.** sympy at $d \in \{4, 8, 16\}$ confirms the identity
exactly (no residue). Script: `scripts/contrib_paper2/verify_lemma_A_prime.py`.

**Status.** Algebraic rewrite, not a structural reduction: $S_d$ is degree
4 (vs.\ $R_d$ at degree 2), and still contains $x_{d/2}$ implicitly through
$W_b$ for $b < d/2$. It removes only the explicit linear $-3 x_{d/2}$ term
in favor of the higher-degree $V/XW/WW$ expansion. Whether the higher-degree
form is more amenable to factor / Newton-identity / structural arguments
remains to be tested.

**Followup attempt (Gröbner exploration at $d=8$).** sympy GB of
$I_{\mathrm{chain}}^{(8)}$ in grevlex over $\mathbb{Q}$ has 212 elements
(\texttt{notes/scripts/contrib\_paper2/grobner\_d8\_explore.py}, 4 min wall,
single-thread). The low-degree elements (\texttt{grobner\_d8\_low\_deg.py})
turn out to be standard reductions of the chain relations under each
other — e.g.\ the deg-2 element $-x_1 + 2(x_2 x_7 + x_3 x_6 + x_4 x_5)
= -c_1$, the deg-2 element $4 x_1^2 + x_2 - 2(x_3 x_7 + x_4 x_6) - x_5^2
\equiv c_2 \pmod{c_1}$, etc. $R_8$ and $S_8$ both reduce to themselves
(already in normal form modulo this GB; their monomials are not divisible
by any GB lead term). So GB exploration at $d=8$ does not reveal a new
structural identity beyond Lemma~A'.

## Followup attempt: $q_c(0) \cdot H_d(0)$ at $d=4$ (Note 0315 retraction analysis)

The retracted Note 0315 derived the Catalan recursion $a_c = -3 \sum_{a=1}^{c-1}
a_a a_{c-a}$ from "$c_c(s)$ has zero constant term as polynomial in $s$".
The corrected statement is $c_c(0) = q_c(0) \cdot H_d(0)$, where
$q_c(s) := (c_c/t^c) / H_d(s)$ is the chain quotient, and $H_d(0) \neq 0$
(origin not on orbit).

**Closed form at $d=4$ (gauge $A_3 = 1$).** Cascade elimination
(\texttt{explore\_qc\_Hd\_d4\_d8.py}) gives
\[
  H_d(s) = s^3 + \tfrac{1}{64}, \qquad
  A_1(s) = 4 s^2, \quad A_2(s) = 2 s, \quad A_3 = 1.
\]
Then $q_1(s) = 0$, $q_2(s) = 64 s$, $q_3(s) = 64$; constant terms
$q_1(0) = q_2(0) = 0$, $q_3(0) = 64$, and $H_d(0) = 1/64$.
Verified: $a_c + 3 F_c(0) = q_c(0) H_d(0)$ at all $c \in \{1, 2, 3\}$
(the identity reduces to $c_c(s) = q_c(s) H_d(s)$ evaluated at $s=0$,
so it holds tautologically given the chain divisibility).

**Where Lemma 0315.1 actually fails.** It would require $q_c(0) = 0$
for the recursion to hold (since $H_d(0) \neq 0$). In the gauge $A_{d-1}=1$,
$A_a(s)$ for $a < d-1$ has constant term 0 (verified at $d=4$), hence
$a_a = 0$ for $a < d-1$ and $a_{d-1} = 1$. Then $c_c(0) = a_c$ for
$c < d-1$ (since $F_c(0) = 0$), so $q_c(0) = 0 \iff a_c = 0 \iff c < d-1$.
At $c = d/2$ (the index used in Theorem 0315.3) this gives $q_{d/2}(0) = 0$
\emph{trivially}, but only because $a_{d/2} = 0$ in this gauge — both
sides of "$F(0) = -\frac{11}{3} a_{d/2}$" vanish, no useful information.

In other gauges (e.g.\ Note 0315's $a_1 = 1$ normalization), $a_{d/2}$ is
not zero, and $q_{d/2}(0)$ is genuinely nonzero — that's the case where
the retraction note caught the recursion failing.

**Q1@d as a gauge-invariant statement.** The orbit polynomial $H_d(s)$
is irreducible (over the appropriate field), and Q1@d holds iff
$F(s) := -3 A_{d/2}(s) + 2 F_{d/2}(s) + 3 s G_{d/2}(s)$ satisfies
$\gcd(F(s), H_d(s)) = 1$ in $\mathbb{F}[s]$. This is the gauge-invariant
form. At $d=4$: $F(s) = -6s + 32 s^4 + 3s = s(32 s^3 - 3) \equiv s \cdot
(32 \cdot (-1/64) - 3) = -7s/2 \pmod{H_d}$, hence $\gcd(F, H_d) = 1$
(since $-7s/2 \not\equiv 0$), confirming Q1@4 in this framework.

**Structural conclusion.** The corrected identity $c_c(s) = q_c(s) H_d(s)$
is a tautology of the chain construction; it does \emph{not} furnish a
shortcut from $(\ast)$ to Q1. Reviving the Catalan F(0) bridge would
require a gauge-invariant reason for $\gcd(F, H_d) = 1$ at all $d = 2^k$,
which is essentially Q1@d itself. The vdim/$\gcd$ formulation is
equivalent to Note 0316's direct $I_{\mathrm{chain}}^{(d)} + \langle R_d \rangle$
attack, just expressed in $s$-space (orbit space) rather than $x$-space.

**Attempted: $H_d(s)$ at $d=8$ via cascade resultant.** sympy resultant
explodes after $A_3$ elimination (28.5s for the first resultant, output
3442 terms; subsequent eliminations would multiply this further). Without
a fast multivariate polynomial backend (Singular / Sage / FLINT) locally,
this avenue is impractical. The d=4 closed form is informative; d=8
extraction would require Studio computation (currently busy with codex's
$d=16$ msolve job). Even with $H_d$ in hand, the structural conclusion
above (Q1@d $\iff \gcd(F, H_d) = 1$ being equivalent to vdim test) means
the explicit form would not yield a new shortcut — only confirm at one
more $d$ what's already implied by the framework.

## Lemma C — Catalan-V closed form for $R_d$ on chain locus (NEW, 2026-05-01)

### Setup and Derivation

Define the OGF of the chain: $C(z) := \sum_{c=1}^{d-1} c_c z^c$. Setting
$X(z) := \sum_{i=1}^{d-1} x_i z^i$, $V(z) := \sum_{c \geq 2} V_c z^c$,
$\widetilde{W}(z) := \sum_{c \geq 1} W_c z^c$, direct termwise summation gives

$$C(z) \equiv X + 3V - \widetilde{W} + 2 X \widetilde{W} - \widetilde{W}^2 \pmod{z^d}$$

(verified by sympy at $d \in \{4, 8\}$, script
\texttt{notes/scripts/contrib\_paper2/verify\_ogf\_chain.py}).

Setting $E := \widetilde{W} - X$ and using $V \equiv X^2 \pmod{z^d}$ identically,
the chain $C(z) \equiv 0$ becomes

$$\boxed{E^2 + E \equiv 4 X^2 \pmod{z^d, I_{\mathrm{chain}}^{(d)}}.}$$

Solving the quadratic in $E$ (branch with $E(0) = 0$):

$$E \equiv \frac{\sqrt{1 + 16 X^2} - 1}{2} = -\sum_{k \geq 1} (-4)^k C_{k-1} X^{2k}
\pmod{z^d, I_{\mathrm{chain}}}$$

where $C_n = \frac{1}{n+1}\binom{2n}{n}$ is the $n$-th Catalan number
(via the Catalan generating function $\sum_n C_n y^n = (1-\sqrt{1-4y})/(2y)$).

### Lemma C statement

For $d = 2^k$, $k \geq 2$, the obstruction $R_d := -3 x_{d/2} + 2 V_{d/2} + 3 W_{d/2}$
satisfies, modulo the chain ideal:

$$\boxed{R_d \;\equiv\; 14\, V_{d/2} \;-\; 3 \sum_{k=2}^{d/4} (-4)^k\, C_{k-1}\, [z^{d/2}] V(z)^k \pmod{I_{\mathrm{chain}}^{(d)}}}$$

equivalently $R_d \equiv [z^{d/2}](2 V + \tfrac{3}{2}(\sqrt{1+16V} - 1)) \pmod{I_{\mathrm{chain}}^{(d)}}$.

### Verification

\texttt{notes/scripts/contrib\_paper2/verify\_catalan\_V\_formula.py}:
- $d = 4$: $R_4 \equiv 14 V_2 = 14 x_1^2 \pmod{I_{\mathrm{chain}}^{(4)}}$ ✓
  (Gröbner reduction confirms; difference $-3(c_2 + c_1^2) \in I$.)
- $d = 8$: $R_8 \equiv 14 V_4 - 48 V_2^2 = 28 x_1 x_3 + 14 x_2^2 - 48 x_1^4
  \pmod{I_{\mathrm{chain}}^{(8)}}$ ✓
  (Gröbner reduction over the 212-element basis confirms zero residue.)

### Significance

1. **Uniform-in-$d$ closed form.** $R_d$ on the chain locus is a Catalan-weighted
   polynomial in $V_2, V_3, \dots, V_{d/2}$ alone, with formula valid for all
   $d = 2^k$.

2. **Variable elimination.** $V_a$ for $a \leq d/2$ depends only on
   $x_1, \dots, x_{d/2-1}$. The "second half" variables $x_{d/2}, \dots, x_{d-1}$
   do not appear in the Catalan-V form. At $d = 16$ this reduces from 15 vars
   to 7 vars in the obstruction analysis.

3. **Reconnects to $(\ast)$ at $d = 4$.** $V_2 = x_1^2$, so Q1@4 $\iff$
   $V_2 \neq 0$ on $V_4^{\mathrm{prim}}$ $\iff$ $x_1 \neq 0$ on
   $V_4^{\mathrm{prim}}$, which is exactly $(\ast)@4$. This is consistent with
   Note 0315's original intuition while avoiding the gauge-dependent
   recursion error: the formula is in $V_a$ (gauge-invariant
   coefficients of $X^2$), not in $a_c$ (gauge-dependent orbit invariants).

4. **Reformulation of Q1@d.**
   $$\mathrm{Q1@}d \iff \widetilde{P}_d(V_2, \dots, V_{d/2}) \neq 0
   \text{ on } V_d^{\mathrm{prim}}$$
   where $\widetilde{P}_d$ is the explicit Catalan-V polynomial.

### Why the retraction missed this

The retracted derivation worked at the *orbit level* with $a_c := A_c(0)$
(gauge-dependent constant terms of orbit-coordinate functions $A_c(s)$).
The "Catalan recursion" $a_c = -3 \sum a_a a_{c-a}$ failed because
$c_c(s) \equiv 0 \pmod{H_d(s)}$ does not give $c_c(0) = 0$.

The corrected formula avoids gauge entirely: it works in
$F[x_1, \dots, x_{d-1}]/I_{\mathrm{chain}}^{(d)}$ via the OGF identity
$E^2 + E = 4 X^2$ which is a polynomial identity (not gauge-dependent).

### Next step: prove $\widetilde{P}_d \neq 0$ on $V_d^{\mathrm{prim}}$

The polynomial $\widetilde{P}_d$ has explicit form:
\begin{align*}
\widetilde{P}_4 &= 14 V_2 \\
\widetilde{P}_8 &= 14 V_4 - 48 V_2^2 \\
\widetilde{P}_{16} &= 14 V_8 - 96 V_2 V_6 - 96 V_3 V_5 - 48 V_4^2 + 1152 V_2^2 V_4 + 1152 V_2 V_3^2 - 3840 V_2^4 \\
&\dots
\end{align*}
At $d=4$: trivially follows from $(\ast)@4$ (rigorous, Note 0277).
At $d=8$: $\widetilde{P}_8 = 14 V_4 - 48 V_2^2$. Need $V_4 / V_2^2 \neq 24/7$ on
$V_8^{\mathrm{prim}}$ (when $V_2 \neq 0$, by $(\ast)@8$ rigorous).
At general $d = 2^k$: open. Requires either (a) structural analysis of
$\widetilde{P}_d$'s zero locus in $V_2, \dots, V_{d/2}$ space, or
(b) an OGF argument from the algebraic relation $\sqrt{1+16V}$ has on
the orbit polynomial $H_d(s)$.

## Lemma D — Pell-conic parametrization of $R$ on chain locus

The chain identity $E^2 + E = 4 X^2 \pmod{z^d, I}$ (with $E := \widetilde W - X$)
defines a smooth conic $Y^2 = 1 + 16 X^2$ where $Y := 2E + 1$. Rationally
parametrize this conic by $u := Y - 4X$:
\[
  Y = \frac{u + u^{-1}}{2}, \qquad
  X = \frac{u^{-1} - u}{8}, \qquad
  u(0) = 1.
\]
Equivalently, set $\eta := (u - 1)/(u + 1) = 2X/(E + 1)$. Then:
\[
  X(z) = \frac{\eta(z)}{2 (1 - \eta(z)^2)}, \qquad
  \eta_1 = -2 x_1 \pmod{c_1}.
\]

**Closed form for $R$ in $\eta$:**
\[
  \boxed{R(z) \equiv \frac{\eta(z)^2 \, (7 - 6\, \eta(z)^2)}{2\, (1 - \eta(z)^2)^2}
    \;=\; \sum_{m \geq 1} \frac{m+6}{2}\, \eta(z)^{2m}
    \pmod{z^d, I_{\mathrm{chain}}^{(d)}}.}
\]

(Derivation: $R = 2V + 3E = 2X^2 + (3/2)(Y-1)$; substitute Pell-conic
parametrization and simplify.)

**Q1@d in $\eta$-form:**
$\widetilde{P}_d = [z^{d/2}] R(z) = \sum_{m=1}^{d/4} \frac{m+6}{2} [z^{d/2}] \eta(z)^{2m}$.

**Observations:**
1. $R(z) \equiv 0$ as power series iff $\eta(z) \equiv 0$ (the factor $7 - 6\eta^2$
   has nonzero constant term 7, hence is invertible).
2. $\eta(z) \equiv 0$ iff $\eta_1 = -2 x_1 = 0$ (and the recursion forces all higher
   $\eta_c = 0$ if $\eta_1 = 0$, by the Pell relation).
3. So $(\ast)@d$ ($x_1 \neq 0$ on $V_d^{\mathrm{prim}}$) is equivalent to
   "$R(z) \not\equiv 0$ as power series on $V_d^{\mathrm{prim}}$".

**Where Q1 differs from $(\ast)$.** Q1@d is a specific-coefficient condition:
$[z^{d/2}] R \neq 0$. This is strictly stronger than $R \not\equiv 0$ because
the latter only requires *some* z-coefficient to be nonzero, whereas Q1
requires the specific $z^{d/2}$ one. Cancellation between Catalan-weighted
contributions at different powers of $\eta$ could in principle make
$[z^{d/2}] R = 0$ even when $R \not\equiv 0$.

**Concrete reformulation for $d=8$:**
$\widetilde{P}_8 = (7/2)[z^4]\eta^2 + 4 [z^4]\eta^4 = (7/2)(2\eta_1\eta_3 + \eta_2^2) + 4 \eta_1^4$
$= 7 \eta_1 \eta_3 + (7/2) \eta_2^2 + 4 \eta_1^4$.
Q1@8 $\iff$ this combination is nonzero on $V_8^{\mathrm{prim}}$.

**Open structural question:** is there a pattern in the $\eta_c$ sequence on
$V_d^{\mathrm{prim}}$ (e.g., $\eta_c$ as polynomial in $\eta_1, \dots, \eta_{c-1}$
via the chain) that prevents accidental cancellation of $[z^{d/2}] R$ at all
$d = 2^k$? The Pell parametrization may admit a Lagrange-Bürmann residue
treatment yielding a uniform-in-d non-vanishing result.

## Lemma D — Algebraic relation $R^2 + (3 - 4V) R + 2V(2V - 21) = 0$

Combining Lemma C with the Pell parametrization yields the very clean
power-series identity:
\[
  \boxed{R(z) \;\equiv\; \frac{4 V(z) - 3 + 3 \sqrt{1 + 16\, V(z)}}{2}
  \pmod{z^d, I_{\mathrm{chain}}^{(d)}}.}
\]

(Verified by sympy at $d \in \{4, 8\}$ via Gröbner reduction; equivalent to the
Catalan-V form of Lemma C after substituting $\sqrt{1+16V}$'s Taylor series.)

Squaring and rearranging:
\[
  \boxed{R^2 + (3 - 4V)\, R + 2 V (2V - 21) \;\equiv\; 0
  \pmod{z^d, I_{\mathrm{chain}}^{(d)}}.}
\]

(Discriminant in $R$: $(3-4V)^2 - 8V(2V-21) = 9 + 144V = 9(1 + 16V)$, matching
the square root in the closed form.)

**Equivalent compact form** via Catalan generating function
$C(y) := (1 - \sqrt{1-4y})/(2y) = \sum_n C_n y^n$:
\[
  R(z) \equiv 2 V(z)\, \bigl(1 + 6\, C(-4 V(z))\bigr) \pmod{z^d, I_{\mathrm{chain}}^{(d)}}.
\]

### Significance

1. **$R$ is algebraically integral over $\mathbb{Z}[V_2, \dots, V_{d-1}]$**
   with explicit minimal polynomial of degree 2 over $V$.

2. **Uniform-in-$d$ algebraic structure.** The relation $R^2 + (3-4V)R + 2V(2V-21) = 0$
   holds in $F[x_1, \dots, x_{d-1}]/I_{\mathrm{chain}}^{(d)}$ for every $d = 2^k$
   simultaneously (it's an identity of formal power series in $z$).

3. **Q1@d in terms of $V$ alone.** The chain locus is identified with the
   conic $\{(R, V) : R^2 + (3-4V)R + 2V(2V-21) = 0\}$ inside the
   power-series ring (modulo $z^d$, $I_{\mathrm{chain}}$). Q1@d is the
   non-vanishing of $[z^{d/2}] R$ on $V_d^{\mathrm{prim}}$, where $R$ is the
   appropriate branch of this conic equation.

4. **Connection to retraction.** The retracted "Catalan F(0) = $-(11/3) a_{d/2}$"
   was an attempt to extract the "constant in $s$" of the orbit-level $F$
   without realizing the recursion failed because $H_d(0) \neq 0$. The
   correct universal identity is at the full power-series level, not at $s=0$:
   Lemma D is what the retracted "Catalan formula" should have been.

### Path forward

Q1@d ⟺ $[z^{d/2}] R \neq 0$ on $V_d^{\mathrm{prim}}$, where $R$ satisfies the
algebraic relation above. Possible attacks:

(i) **Resolvent/discriminant analysis.** $R^2 + (3-4V)R + 2V(2V-21) = 0$
implies $R(R + 3 - 4V) = -2V(2V - 21) = 2V(21 - 2V)$. So $R \cdot (R + 3 - 4V)
= 2V(21 - 2V)$. If we can show RHS has a non-vanishing $z^{d/2}$ component
forcing $R$'s $z^{d/2}$ component nonzero, we close.

(ii) **Reformulate via $\sqrt{1+16V}$.** The branch $R = (4V - 3 + 3\sqrt{1+16V})/2$
mod $H_d(s)$ on each orbit is a specific algebraic element. Q1@d is its
$[z^{d/2}]$ component being non-zero. Connection to L-functions of CM-curves
on the Pell conic $Y^2 = 1 + 16 V$?

(iii) **Recursion in $d$.** $\widetilde{P}_d = [z^{d/2}](2V(1 + 6C(-4V)))$ doubles
in $d$ via $V$'s low/high split. Possible inductive argument Q1@d ⟹ Q1@2d
via the linear-in-new-V structure of the doubling.

## Lemma E — Exact doubling formula

Splitting $V^{(2d)}(z) = V^{(d)}_{<d}(z) + z^d \widetilde V(z)$ where
$\widetilde V(z) = \sum_{c=d}^{2d-1} V^{(2d)}_c z^{c-d}$, Taylor expansion
of $R(V^{(2d)})$ around $V^{(d)}_{<d}$ gives EXACTLY (no higher-order terms
contribute to $[z^d]$):

\[
  \boxed{\widetilde P_{2d} \;=\; [z^d]\, R(V^{(d)}(z)) \;+\; 14\, V^{(2d)}_d.}
\]

(Verified by sympy at $(d, 2d) = (4, 8)$ and $(d, 2d) = (8, 16)$.)

The second term $14 V^{(2d)}_d = 14 \sum_{i+j=d, 1 \leq i, j} x_i x_j$ is the
"diagonal-pair" contribution at index $d$, involving only $x_1, \dots, x_{d-1}$.

The first term $[z^d] R(V^{(d)}(z))$ is a polynomial in $V^{(d)}_a$ for
$a \in [2, d-1]$, distinct from $\widetilde P_d = [z^{d/2}] R(V^{(d)})$
(different z-coefficient extraction).

**Status of doubling-induction.** This decomposition is clean but does not
immediately yield Q1@d ⟹ Q1@2d, because $[z^d] R(V^{(d)})$ involves
$V^{(d)}_a$ for $a > d/2$ which are not constrained by Q1@d (which only
controls the $a \leq d/2$ data). A genuine inductive lift requires
additional structural input — most likely from the chain relations
$c_c^{(2d)}$ for $c \in [d, 2d-1]$ that couple "first-half" and
"second-half" variables.

## Cross-refs

- Note 0267 (chain self-similarity, orbit decomposition)
- Note 0275 (R_d reduction)
- Note 0315 (RETRACTED Theorem 0315.4: $(\ast) \Rightarrow$ Q1)
- Note 0316 (post-retraction direct vdim attack)
- Note 0277 (Q1@d=4 rigorous over Q via primdec + Norm)
- Issue #428 (Path A structural induction sub-issue)
- Issue #410 (Q1 universal master)
- paper2 main `rem:Q1-induction-framework`
- `scripts/contrib_paper2/gen_msolve_chain.py` (this branch)
