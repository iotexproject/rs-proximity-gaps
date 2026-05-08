# Note 0477 — Roos / BCH cannot close Conjecture A: structural reason

**Date:** 2026-05-04 evening (post Note 0476)
**Status:** PATH A (Roos / van Lint-Wilson) FALSIFIED for Conjecture A's natural form.

---

## TL;DR

The "Roos / van Lint-Wilson bound on cyclic code with non-consecutive
defining set" path proposed in Notes 0473, 0475, 0476 for closing
Conjecture A is **structurally infeasible**: the cyclic code naturally
associated with the problem ($C + D$ with defining set
$\Sigma = [32, 128) \setminus \{32, 36, \ldots, 124\}$) has empirical
**min distance exactly 48** — achieved at K=2 saturating cases by
$g_\alpha$ itself.

So any cyclic-code distance bound $\geq 49$ is automatically false,
and Roos cannot help.

## 1. Setup

Define cyclic codes on $L_0 = \mu_{128}$:
- $C := \mathrm{RS}_{32}(L_0)$: defining set $[32, 128)$ (length-96 consecutive run).
- $D :=$ "lifted" code: DFT support $\{32, 36, \ldots, 124\}$ (24 frequencies, multiples of 4).
- $C + D$: cyclic code with DFT support $[0, 32) \cup \{32, 36, \ldots, 124\}$.

Defining set of $C + D$:
$$
\Sigma = [128] \setminus ([0, 32) \cup \{32, 36, \ldots, 124\})
       = \{r \in [32, 128) : r \not\equiv 0 \pmod 4\}.
$$

$|\Sigma| = 72$.

## 2. Why Conjecture A is naturally a question about $C + D$

Conjecture A says: for our specific lifted $g_\alpha$ (Fourier-canonical
representative of its coset modulo $C$), $g_\alpha$ is the minimum-weight
element in $g_\alpha + C$.

Equivalently: for any $c \in C \setminus \{0\}$, $\mathrm{wt}(g_\alpha + c) \geq \mathrm{wt}(g_\alpha)$.

Since $g_\alpha \in D$, we have $g_\alpha + c \in C + D$ for all $c \in C$.
A natural attack: **bound the minimum distance of $C + D$ from below**.

If $d_{\min}(C + D) \geq 80$, then any non-zero element of $C + D$ has
weight $\geq 80$, so for $g_\alpha$ with $\mathrm{wt}(g_\alpha) = 48$ at
K=2 cases, no element of $g_\alpha + C \subset C + D$ can have weight $< 48$.

But this reasoning ALREADY FAILS because $g_\alpha$ itself is in $C + D$
with weight 48. So $d_{\min}(C + D) \leq 48$.

## 3. Numerical verification (Roos-bound exploration)

Script: `issue419_roos_bound_explore.py` computes:

| Bound | Value |
|---|---|
| BCH (longest consecutive run in $\Sigma$) | 4 |
| Hartmann-Tzeng (HT) | 3 |
| **Empirical min dist** | **≤ 48** (via $g_\alpha$ at K=2) |

Even the strongest Roos-type extensions (longest AP in $\Sigma$ for any
common difference $d$ not coprime to 128) give bounds:

| $d$ | $\gcd(d, 128)$ | AP length in $\Sigma$ | Bound (if applicable) |
|---|---|---|---|
| 1 | 1 | 3 | 4 |
| 2 | 2 | 48 | 49 (NOT VALID — see below) |
| 4 | 4 | 24 | 25 (NOT VALID) |
| 64 | 64 | 128 | trivial |

The "AP of odd numbers $\{33, 35, \ldots, 127\}$ of length 48 with $d=2$"
does NOT yield a Roos bound because $\gcd(2, 128) = 2 > 1$. The classical
Roos / BCH bound requires $\gcd(d, n) = 1$.

## 4. Why the simple cyclic-code lens fails

The min-distance of $C + D$ is the minimum weight over **all cosets of
$C$ contained in $C + D$**. There are $|D| / |C \cap D|$ such cosets.

But Conjecture A is **per-coset**: for each $\alpha$, the minimum-weight
representative of $g_\alpha + C$ should be $g_\alpha$ itself.

Roos / BCH bounds the **global minimum** $d_{\min}(C + D)$ across all
cosets — they cannot detect per-coset structure.

Empirically:
- Cosets containing $g_\alpha$ with $\mathrm{wt}(g_\alpha) = 48$: at K=2 saturating $\alpha$.
- All other cosets: $\mathrm{wt}(g_\alpha) > 48$, with $g_\alpha$ being THE min representative (Conjecture A claim).

Roos cannot distinguish these regimes.

## 5. What this means for the closure

Notes 0473, 0475 listed three paths to close Conjecture A:
1. **Roos / van Lint-Wilson** — FALSIFIED (this note).
2. **Hollmann-Xiang Niho-curve point counting** — open, requires character-sum machinery.
3. **Schmidt-Willems LP bound** — open, polynomial-rank machinery.

Path (1) is dead. Path (2) — the HKM-2011 / Hollmann-Xiang approach
proceeds via 3-valued cross-correlation (Note 0473), which gives the
agreement DISTRIBUTION not the per-coset min-distance. So it doesn't
directly attack Conjecture A either; it gives the K_BW count via
distribution + budget.

Actually, **the HKM/Niho approach attacks $K_1$ structurally (= our
unconditional bound), not Conjecture A.** This means the prize-relevant
goal of proving 3-valued distribution structurally is consistent with
having Conjecture A remain empirical.

## 6. Refined attack plan for Conjecture A

The right tool is NOT min-distance of cyclic codes. It's **list-decoding
volume bounds at coset level**:

- For each coset of $C$, the number of low-weight elements (weight $< 80$).
- For our specific cosets (parameterized by $\alpha$), via Fourier analysis.

Possibilities:
- **Sudan-Guruswami algorithmic bound** at $\tau = 80$: returns at most
  one element per coset. So $K_{\mathrm{BW}}$ is exactly the count of
  cosets with a weight-$\leq 48$ element. This gives our $K_1 \leq 2$
  bound DIRECTLY (no Conjecture A needed).
- **Roth-Ruckenstein analyses**: per-coset moment bounds.
- **Polynomial method** on the variety $V := \{(α, c) : \mathrm{wt}(g_\alpha + c) \leq 48\}$ to bound projections.

The clean statement: $K_{\mathrm{BW}} = K_1 \leq 2$ unconditional iff
each "high-agr coset" contains exactly one $g_\alpha$ (with $\alpha$
fixed). This may follow from the Sudan-Guruswami uniqueness, BUT
Sudan-Guruswami at $\tau = 80$ on a length-128 dim-32 RS code gives BW
unique decoding, which is what defines $K_{\mathrm{BW}}$ in the first
place.

So the closure question becomes: does each coset of $C$ contain at
most ONE lifted $g_\alpha$? If yes, then $K_{\mathrm{BW}} = K_1$ trivially.

**Lemma sketch** (to verify): Two lifted pencils $g_\alpha, g_\beta$
with $\alpha \neq \beta$ are in different cosets of $C$ unless their
difference $g_\alpha - g_\beta = (\alpha - \beta) f_v^{(0)}$ is in $C$.
But $f_v^{(0)}$ has DFT support on $\{4r : r \equiv 2, 3 \pmod 4\}$,
which is disjoint from $C$'s support $[0, 32)$ — so $f_v^{(0)} \notin C$
unless $f_v^{(0)} = 0$. Hence $g_\alpha - g_\beta \notin C$ for
$\alpha \neq \beta$, so different $\alpha$'s land in different cosets.

WAIT — this means different $\alpha$'s are in different cosets, so
each coset contains at most one $g_\alpha$. So Conjecture A (zero
codeword optimal) is the claim that $g_\alpha$ is the min-weight rep
of ITS OWN coset.

This doesn't reduce Conjecture A to $K_1$ bound directly. The K_1 bound
asks: **how many** $\alpha$ have $\mathrm{wt}(g_\alpha) \leq 48$. The
Conjecture A asks: when $\mathrm{wt}(g_\alpha) > 48$, is there any
SHIFT $g_\alpha + c$ with weight $\leq 48$.

These are genuinely different questions.

## 7. Updated path: weighted-Fourier rigidity

The "right" framing for Conjecture A's closure:

**Lemma (target):** Let $g \in F_p^{L_0}$ with DFT support
$\subset \{32, 36, \ldots, 124\}$. Then $\mathrm{wt}(g + c) \geq \mathrm{wt}(g)$
for all $c \in C = \{c \in F_p^{L_0} : \hat c|_{[32, 128)} = 0\}$.

This is a **L^1-type Fourier rigidity** statement. It says: removing
low-frequency content from $g$ (subtracting any $c$ with DFT support
in $[0, 32)$) cannot reduce $g$'s weight.

The natural tool: **uncertainty principles for cyclic groups**.

For Z/128: Donoho-Stark gives $|\mathrm{supp}(g)| \cdot |\mathrm{supp}(\hat g)| \geq 128$. With $|\mathrm{supp}(\hat g)| = 24$: $|\mathrm{supp}(g)| \geq 128/24 \approx 5.3$. Compatible with our values $\mathrm{wt}(g) \in [16, 128]$.

Tao's uncertainty $|\mathrm{supp}(g)| + |\mathrm{supp}(\hat g)| \geq p+1$
applies only to prime $p$, not to $\mathbb{Z}/128$. So NO bite here.

**Coset-refined uncertainty (task #311):** for cyclic groups with
specific subgroup structure, refined bounds exist (e.g., Meshulam,
Petridis). These could give stronger lower bounds on $\mathrm{wt}(g + c)$
specifically when $c$ has support on a different "frequency stratum"
than $g$.

This is the natural next drill — and matches exactly task #311
(Coset-refined uncertainty + lift rigidity formalization, Helleseth
recommendation #2).

## 8. Conclusion

| Path | Status |
|---|---|
| Roos / van Lint-Wilson | FALSIFIED (this note) |
| Hollmann-Xiang Niho 3-valued (HKM-2011) | open, but attacks K_1 not Conj A |
| Coset-refined uncertainty (task #311) | natural next drill |
| Schmidt-Willems LP | open |

The closure of Conjecture A is harder than initially thought. The
empirical evidence is overwhelming (805 tests, 0 counterexamples), but
the natural cyclic-code distance approach is dead.

For prize submission: Conjecture A remains a clean technical
conjecture, flagged as such in paper2 v23 §7.4. The unconditional
$K_1 \leq 2$ bound is the "headline" result from the structural side.

## 9. Files

- This note 0477
- `notes/scripts/issue419_roos_bound_explore.py` + output
- Notes 0470-0476 (preceding context)
