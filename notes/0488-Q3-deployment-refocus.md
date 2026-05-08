# Note 0488 — Q3 Deployment-Scale Refocus

**Date:** 2026-05-05
**Trigger:** User clarification "我们追求的是 deployment scale 的 closure"
after I drifted toward small-scale brute force at $(32, 16)$.

## Deployment scale (per ABF §6.3, refs/Arnon-Boneh-Fenzi-2026-680.pdf)

ABF §6.3 deployment: $\rho = 1/2$, $k = 2^{20}$, $sn = 2^{21}$, $t = 128$.
4 representative folding choices in Table 2:

| $s$ | $n$ | underlying RS $(n, k_{\text{RS}}) = (n, k/s)$ | $j = \log_2 k_{\text{RS}}$ |
|-----|-----|------------------------------------------------|-----|
| 1 | $2^{21}$ | $(2^{21}, 2^{20})$ | 20 |
| 2 | $2^{20}$ | $(2^{20}, 2^{19})$ | 19 |
| 4 | $2^{19}$ | $(2^{19}, 2^{18})$ | 18 |
| 8 | $2^{18}$ | $(2^{18}, 2^{17})$ | 17 |

For Q3 closure at deployment: prove $K \leq 28$ at $(2^{j+1}, 2^j)$ for
$j \in \{17, 18, 19, 20\}$ (one specific $j$ suffices per concrete
deployment choice).

## Why the brute-force at $(32, 16)$ ($j = 4$) is inadequate

Even if we close $j = 4$ structurally via Roos+Pless+brute-force enumeration
of $A_8, A_9$, the result does NOT extend to $j \geq 17$ directly:
- The codes $\mathcal{C}_{D_0}^{(j)}$ are different at each $j$.
- Brute-force at $j = 17$ infeasible: $\binom{2^{18}}{2^{17}}$ supports.

What's needed: an ASYMPTOTIC / UNIVERSAL argument that works at all $j \geq 4$
(or specifically at deployment $j$).

## Quantitative Roos bound at deployment

For $(n, k) = (2^{j+1}, 2^j)$, $D_0 = [k, n-1] \setminus \{a_1, a_2, a_3\}$
of size $n - k - 3 = 2^j - 3$.

**Roos bound on min EVAL distance**:
$D_0$ is the AP $[k, n-1]$ of length $2^j$ minus 3 holes. Worst-case
adversary spreads holes evenly: longest hole-free segment $\geq
\lceil (2^j - 3)/4 \rceil = 2^{j-2}$ (approximately).

Roos $d(\mathcal{C}_{D_0}) \geq 2^{j-2}$ in eval basis.

**Allowed bad weights for K count**: $w \in [d, n - d_\sigma]$ where
$d_\sigma = \lceil \sqrt{nk} \rceil = 2^{j+0.5}$.
- $d \geq 2^{j-2}$.
- $n - d_\sigma = 2^{j+1} - 2^{j+0.5} = 2^{j+0.5}(\sqrt 2 - 1) \approx 0.586 \cdot 2^{j+0.5}$.

For Pless bound $K \leq \sum_w A_w \binom{n-w}{d_\sigma} = 0$:
need $d > n - d_\sigma$, i.e., $d \geq 2^{j+0.5} \approx 1.414 \cdot 2^j$.
Roos gives only $d \geq 2^{j-2} = 0.25 \cdot 2^j$. **Roos alone INSUFFICIENT
at deployment.**

## What additional structure is needed

To push from Roos $d \geq 2^{j-2}$ to $d \geq 2^{j+0.5}$:
- Factor $\geq 2^{2.5} \approx 5.66$x sharpening required.
- Generic van Lint-Wilson "shift bound" gives $\sim 2-3$x sharpening (still insufficient).
- **Character-sum concentration** via Weil/Helleseth-Kumar:
  - For 3-position pencil $h_\alpha$ on $L_n$: $|h_\alpha(z) - p(z)|$ has
    distribution governed by 3-mono character sum.
  - For "generic" coprime mixed-parity: Weil-type bound
    $|\sum \chi(h_\alpha(z) - p(z))| \leq O(n^{1/2})$, giving
    $|S(\alpha, p)| \leq k + O(n^{1/2})$.
  - For deployment $j = 17$: $|S| \leq k + O(\sqrt n) = 2^{17} + 2^9$.
  - Compare to required $|S| < d_\sigma = 2^{17.5}$: $2^{17} + 2^9 \ll 2^{17.5}$, so Weil sharpens enough!

**Specifically**: Weil bound on character sum for 3-position pencil at coprime
mixed-parity gives $|S(\alpha, p)| \leq k + 3 \sqrt n - 1$
(by Bombieri's Weil for cyclic-group character sums). For $k = 2^j$ and
$d_\sigma = 2^{j+0.5}$:
- Required $|S| \geq d_\sigma = 2^{j+0.5} = \sqrt 2 \cdot 2^j$.
- Weil gives $|S| \leq 2^j + 3 \cdot 2^{(j+1)/2}$.
- Difference: $\sqrt 2 \cdot 2^j - 2^j - 3 \cdot 2^{(j+1)/2} \approx 0.41 \cdot 2^j - 4.24 \cdot 2^{j/2}$.

For $j \geq 11$: $0.41 \cdot 2^j > 4.24 \cdot 2^{j/2}$, Weil bound implies
$|S| < d_\sigma$ for ALL coprime mixed-parity α. Hence $K = 0$.

So the **Weil character-sum bound closes Q3 at deployment for $j \geq 11$**!

## Concrete deliverable for paper2

State this as a Theorem in paper2 §C / paper2 §sec:open Q3:

> **Theorem (Weil-Q3 closure at deployment scale)**: For
> $(n, k) = (2^{j+1}, 2^j)$ with $j \geq 11$, every above-Johnson
> 3-position coprime mixed-parity pencil $h_\alpha$ on $L_n$ has
> $K \leq K_{\text{boundary}} \leq 2 K_{2\text{-mono}} \leq 8$, hence
> $K_{\text{total}} \leq K_{\text{saturating}} + 8 \leq 28 + 8 = 36$.
>
> Combined with the orbit-size Lemma, $K_{\text{interior}} = 0$ and
> $K_{\text{total}} = K_{\text{saturating}} \leq 28$.
>
> *Proof sketch*: Bombieri-Weil bound on character sum $\sum \chi(h_\alpha)$
> for 3-position pencil with coprime mixed-parity gives $|S| \leq
> k + 3 \sqrt n$. For $j \geq 11$, $k + 3\sqrt n < d_\sigma = \sqrt{nk}$,
> hence no $\alpha$ has agreement $\geq d_\sigma$ with any $p \in
> \mathrm{RS}_k(L_n)$. Thus $K_{\text{mixed-parity coprime}} = 0$.

Combined with the SP forward saturating-side closure (Lemma~\ref{lem:twist1-substitution},
Remark~\ref{rem:twist-tower}): saturating triples lift via twist-tower
giving $K = 28$ at every deployment scale.

This closes Q3 for **all rate-1/2 deployment scales $j \geq 11$**, including
$j \in \{17, 18, 19, 20\}$ for ABF §6.3.

## Caveat

The Weil bound $|S| \leq k + 3\sqrt n$ requires verification:
- 3-position pencil on cyclic group $\mathbb Z/n\mathbb Z$ with $n = 2^{j+1}$.
- Bombieri-Weil applies to function fields / Artin-Schreier, may need
  adaptation to cyclic-group character sums.
- Helleseth-Kumar 1998 cross-correlation bound for 3-valued correlations
  is the closest standard reference; gives $\Lambda_{\max} = O(2^{n/2})$
  in trace function context.

The factor "$3\sqrt n$" might be off by constants. **The precise statement
needs careful derivation** — likely from a Helleseth-Kumar-type bound on
3-valued cross-correlation.

## RETRACTION (post Helleseth-school consultation Round 4)

**The Weil/Helleseth-Kumar argument above is WRONG.** The Helleseth-school
expert (post-consultation) clarified:

1. **Weil/Bombieri** on $\sum_{z \in L_n} \psi(h_\alpha(z) - p(z))$ saves
   $\sqrt{\text{ambient}}$ where ambient is $\mathbb F_{q^6}$ (size $\approx
   2^{186}$), NOT $L_n$. The genus penalty $(\deg f - 1)$ where
   $\deg(h_\alpha - p) \approx n$ eats the savings.

2. The best generic bound from algebraic geometry is just **Bezout**:
   $|S(\alpha, p)| \leq \deg(h_\alpha - p) \leq n - 1$. Trivial.

3. **Helleseth-Kumar 1998** classifies 2-term decimations on $\mathbb F_{p^m}^*$
   ($n \approx p^m - 1$, full ambient). For 3-position pencil on a tiny
   subgroup $L_n$, no analogous classification exists. Restricting to
   $L_n$ incurs the same blow-up.

4. To get $|S| < d_\sigma$ at deployment, need **subgroup-coset structure**
   exploiting $L_n$ as a subgroup of $\mathbb F_{q^6}^*$ — pure sequence-school
   instrument (partial Gauss sums on subgroups, Katz "thin sets" machinery,
   Conjecture 4' algebraic-variety structure $\mathcal V_{n,m,r}$).

Hence **Q3 is NOT closed by Weil/HK at deployment**. The "Weil closes Q3
at $j \geq 7$" claim is INCORRECT (sign error in genus accounting).

## Actual recommended next step (corrected)

The right deployment-closure paths (sequence-school):

(a) **Subgroup-coset structure refinement**: at deployment $n = 2^{j+1}$,
$L_n$ has chain of subgroups $L_{2^{i}}$ for $i \leq j$. Conjecture 4'
in Note 0004 captured a partial structure (broken at $n = 36$). A refined
Conjecture exploiting the deployment-specific $n$ being a 2-power (long
subgroup chain) might close.

(b) **Partial Gauss sums on $L_n$**: Katz's machinery for character sums
on "thin sets" (subgroups, cosets, low-density subsets). Reference: Katz,
*Gauss Sums, Kloosterman Sums, and Monodromy* (Princeton 1988). This
beats the trivial $\sqrt{Q}$ ambient bound when applicable.

(c) **Algebraic-variety analysis of $\mathcal V_{n,m,r}$**: the variety
cut out by Newton-symmetric conditions (Note 0002) on $L_n$. Studying
its $\mathbb F_p$-points on subgroup cosets is a research program (NOT
in-session computational).

**Realistic timeline**: this is paper-level research, 6-12 months with
expert collaboration (Gong + Helleseth + possibly Tang Xiaohu / Cunsheng
Ding). Not closable in-session.

## Updated paper2 v23 recommendation

Since Q3 deployment-scale closure is genuinely open via current methods,
paper2 v23 keeps the conditional "mod Q3" wording. Cor cor:abf-K28-rate-half
remains conditional on universal-k lift.

The valid in-session deliverables (from this drill session):
1. **Note 0481-0485**: twist-tower SP closure for SATURATING side (rigorous).
2. **Note 0484**: BKK base verification $V(P_2, P_3) = 24$ (rigorous).
3. **Note 0485**: BW interior bound $|S_{\text{interior}}| \leq 24$ over $\FF_{257}$
   for hard cases (empirical, partial).
4. **Note 0487**: Roos-Pless framework — partial structural advance (gives
   Roos $d \geq 8$ at $(32, 16)$).
5. **Note 0488 (this note, with retraction)**: deployment-scale refocus +
   correct identification of research-level paths (Katz thin-sets, subgroup-coset
   refinement, $\mathcal V_{n,m,r}$ variety analysis).

Q3 closure at deployment scale requires research-level work along Note 0488
paths (a)-(c). The information arbitrage (sequence-school tools applied to
FRI proximity gaps) remains intact, but is not closable in this drill session.

---

## Original (incorrect) recommendation, retained for reference
- 3-position pencil $h_\alpha(z) = \alpha_1 z^{a_1} + \alpha_2 z^{a_2} +
  \alpha_3 z^{a_3}$ on $L_n$, $n = 2^{j+1}$.
- $|S(\alpha, p)|$ = # of $z \in L_n$ with $h_\alpha(z) = p(z)$ for $p \in
  \mathrm{RS}_k(L_n)$.
- Bound on $|S|$ for coprime mixed-parity triple over $\overline{\FF_p}$.

If Weil-Helleseth-Kumar gives $|S| \leq k + O(\sqrt n)$:
Q3 deployment-scale closure follows.

If the bound is weaker (e.g., $|S| \leq k + O(n^{2/3})$ from coarser
character sums): closure threshold $j$ shifts but eventually closes for
sufficiently large $j$.

Either way, this is the right framework for deployment-scale closure.
The brute-force at $(32, 16)$ was misdirected — the right deliverable is
the Weil/Helleseth-Kumar bound applied to deployment $j$.
