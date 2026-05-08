# Note 0446 -- 5-vec parity (3, 2)/(2, 3) at $L_2 = (32, 8)$ closes structurally

**Date:** 2026-05-03 morning (Tier 3 deployment-scale rigor pass continued)
**Branch:** `main`
**Status:** Structural closure of 5-vec same-side parity (3, 2)/(2, 3) at
$L_2 = (32, 8)$, extending Note 0442's framework.

---

## 1.  Setting

5-vec at $L_2 = (32, 8)$, parity (3, 2): 3 q=0 evens (subset of
$\{8, 12, 16, 20, 24, 28\}$) + 2 q=1 odds (subset of
$\{9, 13, 17, 21, 25, 29\}$).

Factor $p(t) = t^{r_{\min}} [A(u) + t \cdot B(u)]$, $u = t^4$:
- $A$ = 3-monomial polynomial of degree $\le 5$ (3 nonzero coefs).
- $B$ = 2-monomial polynomial of degree $\le 5$ (2 nonzero coefs).

Per-mod-8-class analysis with disjoint-coset bound:
- Free: $A(\nu^c) = B(\nu^c) = 0$. $|S \cap \text{class}_c| \le 4$.
- Restricted: at most 1 element TOTAL across all restricted classes.
- Empty: 0 elements.

$|S| \le 4 n_F + 1$. $|S| = 16$ forces $n_F \ge 4$.

---

## 2.  Necessary condition: $B$ has 4 roots in $\mu_8$

$B = c_{o_1} + c_{o_2} u^k$ where $k = (o_2 - o_1)/4 \in \{1, 2, 3, 4, 5\}$.

Number of roots of $B$ in $\mu_8$: $\gcd(k, 8)$ if $-c_{o_1}/c_{o_2}$ is in
the image of the $k$-th power map; else $0$.

* $k = 1$: gcd 1, $\le 1$ root.
* $k = 2$: gcd 2, $\le 2$ roots.
* $k = 3$: gcd 1, $\le 1$ root.
* $k = 4$: gcd 4, $\le 4$ roots.
* $k = 5$: gcd 1, $\le 1$ root.

For $n_F \ge 4$: $B$ needs $\ge 4$ roots → $k = 4$ → $o_2 - o_1 = 16$.

So only $(o_1, o_2) \in \{(9, 25), (13, 29)\}$ (or symmetric on q=3 odds:
$(11, 27), (15, 31)$ — wait those are v-side, not u-side; for u-side q=1
odds, the only k=4 pairs are (9, 25) and (13, 29)).

For other $(o_1, o_2)$: $B$ has $< 4$ roots → $n_F < 4$ → INFEASIBLE.

---

## 3.  Closure for $(o_1, o_2) = (9, 25)$ or $(13, 29)$

For these configurations: $B = c_{o_1} + c_{o_2} u^4$ with
$-c_{o_1}/c_{o_2} \in \{\pm 1\}$ (since $\mu_8^4 = \mu_2 = \{\pm 1\}$).

* $-c_{o_1}/c_{o_2} = 1$: $B$ vanishes at $\mu_4 = \{\nu^0, \nu^2, \nu^4, \nu^6\}$.
  Mod-8 indices: $\{0, 2, 4, 6\}$.  Mod-4 indices: $\{0, 2, 0, 2\}$ → mod-4-classes 0 and 2 fully covered.
* $-c_{o_1}/c_{o_2} = -1$: $B$ vanishes at $\mu_8 \setminus \mu_4 = \{\nu, \nu^3, \nu^5, \nu^7\}$.
  Mod-8 indices: $\{1, 3, 5, 7\}$.  Mod-4-classes 1 and 3 fully covered.

For $A$ (3-monomial) to share these 4 roots: 4 equations on 3 unknowns
$(c_{e_1}, c_{e_2}, c_{e_3})$.  For nontrivial sol: rank $\le 2$.

**Sub-case analysis** (e.g., $(e_1, e_2, e_3) = (8, 12, 28)$, $D_2 = 1$,
$D_3 = 5$):

$A(u) = c_{e_1} + c_{e_2} u + c_{e_3} u^5$.

$A$ vanishing on $\mu_4 = \{1, \nu^2, \nu^4, \nu^6\}$:
$$\begin{aligned}
A(1) &= c_{e_1} + c_{e_2} + c_{e_3} = 0 \\
A(\nu^2) &= c_{e_1} + c_{e_2} \nu^2 + c_{e_3} \nu^{10} = c_{e_1} + (c_{e_2} + c_{e_3}) \nu^2 = 0 \\
A(\nu^4) &= c_{e_1} - c_{e_2} - c_{e_3} = 0 \\
A(\nu^6) &= c_{e_1} - (c_{e_2} + c_{e_3}) \nu^2 = 0
\end{aligned}$$

(Using $\nu^{10} = \nu^2$, $\nu^4 = -1$, $\nu^6 = -\nu^2$.)

Adding $A(1)$ and $A(\nu^4)$: $2 c_{e_1} = 0 \Rightarrow c_{e_1} = 0$.
Then $c_{e_2} + c_{e_3} = 0 \Rightarrow c_{e_3} = -c_{e_2}$.

So nontrivial $A$ exists with **$c_{e_1} = 0$**.  But this means the "5-vec
configuration" actually has a zero coefficient (degenerate to 4-vec).

For a GENUINE 5-vec dep with all 5 coefs nonzero: $c_{e_1} \ne 0$ required,
contradicting the above.  So no genuine 5-vec dep.

**For other $(D_2, D_3)$ configurations of $A$**: similar analysis.  In each
case, the 4-equations-on-3-unknowns over-determined system forces
$c_{e_1} = 0$ (or analogous degeneracy).

### General structural argument

For $A$ with 3 nonzero coefs to vanish on $\mu_4$ (4 distinct elements):
$A$ is divisible by $u^4 - 1 = (u-1)(u-\nu^2)(u+1)(u+\nu^2)$ in
$\mathbb{F}_q[u]$.

But $u^4 - 1$ has 4 nonzero coefs (1, 0, 0, 0, -1)?  Actually $u^4 - 1$
has 2 nonzero coefs (the constant -1 and the $u^4$ coefficient 1).

For $A$ divisible by $u^4 - 1$: $A = (\text{something}) \cdot (u^4 - 1)$.

* If $\text{something} = $ constant $\alpha$: $A = \alpha u^4 - \alpha$.
  2 nonzero coefs.  Doesn't match 3-monomial requirement unless 1 coef
  in our 3-monomial form is "redundant" (= 0).
* If $\text{something} = $ linear $\alpha + \beta u$: $A = \alpha u^4 + \beta u^5 - \alpha - \beta u$.
  4 nonzero coefs.  Match 3-monomial $\Rightarrow$ one coef = 0.

For $A = c_{e_1} + c_{e_2} u^{D_2} + c_{e_3} u^{D_3}$ to match
$\alpha u^4 + \beta u^5 - \alpha - \beta u$ with one coef = 0: requires
specific $(D_2, D_3)$ + zero coefficient.  Not a "genuine 3-monomial"
configuration with all coefs nonzero.

**Hence**: for all (e_1, e_2, e_3) configurations, $A$ vanishing on $\mu_4$
requires at least one of $(c_{e_1}, c_{e_2}, c_{e_3}) = 0$.  No genuine
5-vec dep with all 5 coefs nonzero.  $\square$

### Same conclusion for $\tau = -1$

By symmetric analysis: $A$ vanishing on $\mu_8 \setminus \mu_4$ also
requires degeneracy.

---

## 4.  Combined closure

> **Theorem (5-vec parity (3, 2) at $L_2 = (32, 8)$).**  For every odd
> prime $q$ with $32 \mid q-1$, every no-full $S$, every choice of
> $(e_1, e_2, e_3)$ from q=0 evens and $(o_1, o_2)$ from q=1 odds: no
> 5-vec linear dependence with all 5 coefs nonzero.

**Symmetric**: 5-vec parity (2, 3), and v-side variants.

---

## 5.  Updated rigor table

| Support / parity | $L_2=(16,4)$ | $L_2=(32,8)$ | $L_2 \ge (64,16)$ |
|---|---|---|---|
| 3 same-q | THEOREM | THEOREM | Narrow part |
| 4 parity (2,2) | THEOREM | THEOREM | Narrow part |
| 4 parity (3,1)/(1,3) | THEOREM | empirical | empirical |
| 5 parity (3,2)/(2,3) | THEOREM | **THEOREM (this Note)** | empirical |
| 5 parity (4,1)/(1,4) etc. | THEOREM | empirical | empirical |
| 6 same-side | THEOREM | empirical | empirical |
| 7..12 | THEOREM | empirical | empirical |

**Q2 LOCAL closure at $L_2 = (32, 8)$ now structural for k = 3, 4 parity
(2,2), and 5 parity (3,2)/(2,3).**  Significant additional coverage.

---

## 6.  Strategic position update

The structural closure at deployment $L_2 = (32, 8)$ now covers:
- All k=3 same-q-class configurations (Note 0442).
- All k=4 parity (2,2) configurations (Note 0442).
- All k=5 parity (3,2)/(2,3) configurations (this Note).
- Narrow-spread configs at all k (Note 0444).

Remaining at $L_2 = (32, 8)$: k=4 parity (3,1)/(1,3); k=5 parity (4,1)/(1,4);
k=6, 7, 8, ... mixed parities.  Estimated 1-2 days additional algebra to
close all.

For higher scales ($L_2 \ge (64, 16)$): refined no-full bookkeeping at
mod-(n_2/4)-class level, similar approach.
