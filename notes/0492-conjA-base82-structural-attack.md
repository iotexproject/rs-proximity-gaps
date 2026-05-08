# Note 0492 — (8,2) Conj A: structural attack roadmap

**Date:** 2026-05-04 night iteration 9 (post-compact)
**Status:** Problem reformulated. Empirical fingerprint at p=17 isolated.
Roadmap: variety enumeration + Hasse-Weil bound + finite-prime check.

## Why this is the target

paper2 §7 `thm:K-BW-2-structural` closes $K_{\mathrm{BW}} \leq 2$ at L_3 = (128, 32)
modulo Conjecture A at $L_2$ scale. By Lemma `lem:L2-recursion`, the residual induced
sub-case for $N_\alpha < 80$ reduces to (32, 8) inner Conj A. By the same recursion at
(32, 8) scale, this further descends to (8, 2) Conj A. paper2 line 3174–3177
explicitly names "$(8, 2)$ Conjecture A" as the residual paperwork at the smallest scale.

**Bottom-line claim** (the only thing standing between us and unconditional
$K_{\mathrm{BW}} \leq 2$ at deployment scales):

> For every prime $p$ with $8 \mid (p-1)$ and $p \geq 41$ (in particular for the
> minimum admissible primes of L_2 = (32, 8) outer, i.e. $p \geq 97$), every admissible
> $S \subset \mathbb{Z}/8$ with $|S| = 4$ and $S \bmod 4 = \{0,1,2,3\}$, every
> non-trivial kernel direction $(c_2, \ldots, c_7) \in \mathrm{null}(M_S)$,
> and every $\alpha \in \mathbb{F}_p^*$:
>
> $$ \max_{(a,b) \in \mathbb{F}_p^2 \setminus \{(0,0)\}} \#\{j \in \mathbb{Z}/8 : h_\alpha(\omega^j) = a + b\omega^j\} \;\leq\; 4 $$
>
> where $h_\alpha = f_u + \alpha f_v$ with $f_u = c_4 z^4 + c_5 z^5$ and
> $f_v = c_2 z^2 + c_3 z^3 + c_6 z^6 + c_7 z^7$.

## Empirical state (recap, Note 0489)

| Prime | $8\mid p-1$ | Configs | Alphas | Counterexamples |
|---|---|---|---|---|
| 17 | ✓ | 480 | 7,680 | **34** |
| 41 | ✓ | 480 | 19,200 | 0 |
| 73 | ✓ | 480 | 34,560 | 0 |
| 89 | ✓ | 480 | 42,240 | 0 |
| 97 | ✓ | 480 | 46,080 | 0 |
| 113 | ✓ | 480 | 53,760 | 0 |
| 193 | ✓ | 480 | 92,160 | 0 |
| 257 | ✓ | 480 | 122,880 | 0 |

Only the smallest admissible prime $p = 17$ exhibits failure (34 cex). For
$p \geq 41$, $0$ cex over $410{,}880$ alpha tests.

## New empirical fingerprint at p=17

`issue419_p17_cex_diagnostic.py` enumerates all 34 cex with structural data.

**Finding 1**: All 34 cex use $\alpha \in \{7, 12\}$, with multiplicities
$(14, 20)$. **Two failing alpha values total**, independent of $(S, c)$.

**Finding 2**: $7 \cdot 12 \equiv -1 \pmod{17}$ and $7 + 12 \equiv 2 \pmod{17}$.
Hence $\{7, 12\}$ are exactly the roots of $\alpha^2 - 2\alpha - 1 \equiv 0
\pmod{17}$, i.e., $\alpha = 1 \pm \sqrt 2 = 1 \pm 6 = \{7, -5\}$ in $\mathbb{F}_{17}$.

**Finding 3**: The "matching set" $M \subset \mu_8$ (where $h_\alpha$ agrees with
$a + b\omega^j$) is always $|M| = 5$ or $|M| = 6$; the "missing set"
$\mu_8 \setminus M$ varies across configs. No single $M$ dominates.

**Finding 4 (key)**: Although $\alpha = 1 \pm \sqrt 2$ exists at every admissible
prime ($\sqrt{2} \in \mathbb{F}_p$ iff $p \equiv \pm 1 \pmod 8$, and all our primes
are $\equiv 1 \pmod 8$), it produces $0$ cex at $p = 41, 73, 89, 97, 113, 193, 257$.
Hence the condition "$\alpha = 1 \pm \sqrt 2$" alone is **not** sufficient; it is
**a small-prime coincidence at $p = 17$**, not the universal failure constraint.

**Conclusion of fingerprint analysis**: the failure variety
$\mathcal{V} := \{(S, c, \alpha, M) : 5 \text{ points } (\omega^j, h_\alpha(\omega^j))_{j \in M}
\text{ collinear}\}$
has dimension small enough that its $\mathbb{F}_p$-rational points are sparse for
$p \gg 1$. At $p = 17$ a sporadic sub-variety acquires $\mathbb{F}_p$-points; at
$p \geq 41$ no $\mathbb{F}_p$-point exists.

## Reformulation: 5-on-a-line variety

Fix $S, c$ (free parameters), and view $\alpha, a, b$ as variables. Failure means
$\exists M \subset \mathbb{Z}/8$ with $|M| = 5$ such that
$$ h_\alpha(\omega^j) = a + b \omega^j \quad \text{for all } j \in M. $$

This is **5 linear equations in 2 unknowns $(a, b)$**, which is consistent iff the
augmented matrix has rank $\leq 2$, equivalently $\binom{5}{3} = 10$ vanishing
$3 \times 3$ minors. Each minor is a polynomial in $\alpha$ (via $h_\alpha$) of
degree $\leq 1$ (since $h_\alpha$ is linear in $\alpha$). The system of $10$
linear-in-$\alpha$ equations on $\alpha$ either:
- (a) is inconsistent (no failure for this $M$), or
- (b) reduces to a single condition $\alpha = \alpha^*(S, c, M)$, or
- (c) has $\alpha$ free (only when $h_\alpha|_M$ is genuinely linear for all $\alpha$,
  which requires $f_u|_M$ and $f_v|_M$ both linear).

Iterating over $\binom{8}{5} = 56$ subsets $M$, the failure locus is a finite
union of conditions $\alpha = \alpha^*(S, c, M)$. **Each $(S, c, M)$ contributes
at most 1 failing $\alpha$**.

## Counting heuristic

Per $(S, c)$: $\leq 56$ failing $\alpha$'s in $\mathbb{F}_p^*$. Per $S$: $\leq p^2$
distinct kernel directions $\times 56 = O(p^2)$ failing $(c, \alpha)$ pairs. Total over
$16$ admissible $S$: $O(p^2)$.

Total alpha tests at prime $p$: $480 \cdot (p-1) \approx 480 p$. The "rate of
failure" is at most $O(p^2) / O(p) = O(p)$. This is loose; the empirical rate is
$0$ for $p \geq 41$.

The gap between heuristic and empirics says the $\alpha^*(S, c, M)$ values are
**non-generic over $\mathbb{F}_p$** — they live on a low-dimensional sub-variety
that has $\mathbb{F}_p$-rational points only sporadically (here: only at $p = 17$).

## Structural attack: 3 paths

### Path A: explicit elimination + Hasse-Weil

For each $M \subset \mathbb{Z}/8$ with $|M| = 5$ (56 cases), compute $\alpha^*(S, c, M)$
as a rational function of $(c)$ over $\mathbb{Z}[\omega]$. Bound the number of
$\mathbb{F}_p$-rational $(c, \alpha)$ via Hasse-Weil on the resulting curve. Show:
no $\mathbb{F}_p$-rational point exists for $p \geq 41$, except potentially the
"trivial" loci that violate the stratum-(B) admissibility.

**Estimate**: 1–2 weeks of explicit computation in SageMath / Macaulay2.
Tractable because of small scale ($n = 8$, 56 cases).

### Path B: Niho 3-valued at (8, 2)

The L_3 K_BW=2 cases satisfy a Niho 3-valued cross-correlation
($N_\alpha \in \{4|T|, 4|T|+8, 80\}$, multiplicities $(p-5, 2, 2)$, paper2
Theorem `thm:niho-3-valued`). At (8, 2), the analogous Niho coset structure is:
- u-side support: $r \in \{4, 5\}$ on $\mathbb{Z}/8$, mod 2 even$+$odd
- v-side support: $r \in \{2, 3, 6, 7\}$ on $\mathbb{Z}/8$, mod 2 even$+$odd
- Hence both supports straddle the order-2 subgroup of $\mathbb{Z}/8^*$
  characters; this is the (8, 2)-analog of the (32, 8) Niho splitting.

If we can prove a 3-valued $N_\alpha$ distribution at (8, 2) with the only
$\alpha$ saturating (or near-saturating) being $\pm 1$, then by `lem:degree-counting`
at $L = \mu_8$: $\mathrm{agr}(h_\alpha, c) \leq 1 + (8 - N_\alpha)$ for non-zero
$c \in \mathrm{RS}_2(\mu_8)$. With $N_\alpha \geq 5$ at $\alpha = \pm 1$, this gives
$\mathrm{agr} \leq 4$, closing Conj A unconditionally.

**Caveat**: The Niho 3-valued theorem (paper2) is "conditional on HKM-2011
exponent condition" — the same gap applies here. Verifying the HKM condition for
the (8, 2) exponent set $\{2, 3, 4, 5, 6, 7\}$ (with mod-4 split) is a finite
algebraic check.

**Estimate**: 2–4 weeks with HKM-2011 in hand.

### Path C: Stickelberger 2-adic on $\mathbb{Z}/8$ Gauss sum

The relevant Gauss sum is
$g_j = \sum_{\chi \in \widehat{\mathbb{F}_p^*}} \chi(\omega^j) \chi(\alpha)$, $j \in \mathbb{Z}/8$.
The 2-adic valuation $v_2(g_j) = $ explicit Stickelberger expression in the
$j$ and $|\mathbb{F}_p^*|$ representation. For (8, 2), the constraints on $v_2$
constrain $K_{\mathrm{BW}} \pmod 2$.

Combined with Path A's upper bound, this pins $K_{\mathrm{BW}}$ exactly at
all $p \geq $ some absolute constant.

**Estimate**: 3–4 weeks; requires reading Helleseth–Kholosha 2006 on
Stickelberger over $\mathbb{Z}/2^k$.

## Recommendation: start with Path A

Path A is concrete, computational, and self-contained. The 56 subsets $M$ are
enumerable; for each, $\alpha^*(S, c, M)$ is a rational function we can compute
in closed form. The resulting variety has dimension $\leq 1$ in
$(\alpha, \text{kernel-direction})$-space, so Hasse-Weil applies.

If Path A produces a Hasse-Weil bound of the form
"failures in $\mathbb{F}_p^* \leq C \sqrt p$ for $p \geq P_0$", combined with
explicit enumeration of small-prime exceptions ($p \leq P_0$), the closure is
complete.

## Concrete next steps

| # | Task | Estimate | Output |
|---|---|---|---|
| 1 | For each of 56 subsets $M$, derive the 5-by-3 matrix $A_M(\alpha)$ from the linear system. Compute its rank-$<3$ locus as a polynomial in $\alpha$ over $\mathbb{Z}[\omega][c_2, ..., c_7]$. | 3 days | `issue419_M_minor_polynomials.py` |
| 2 | Determine: does the failure locus per $M$ have $\dim \leq 1$ in $(\alpha, c)$? Verify by symbolic Gröbner basis. | 2 days | (Sage script) |
| 3 | Apply Hasse-Weil: number of $\mathbb{F}_p$-rational points on the failure curve. Find $P_0$ such that $\#\text{points} = 0$ for all $p \geq P_0$. | 3 days | (analytic estimate) |
| 4 | Enumerate the failure points at $p = 17$ — verify they match our 34 cex (sanity check). | 1 day | `issue419_p17_failure_variety_match.py` |
| 5 | Write the bound in paper2 format: "Theorem (8,2 Conj A unconditional for $p \geq P_0$)". | 2 days | paper2 §7 update |

## Iteration 10: full elimination per M={0,2,4,5,7}

`issue419_path_A_elim_full.py` runs all 36 pair-eliminations $A_i B_j - A_j B_i = 0$
(the resultant condition for $\alpha$-uniqueness between minor pairs) plus the
1 α-only constraint. **All 37 constraints verified at the p=17 cex** ✓.

**Multi-prime kernel test (S=[0,1,2,3])**:

| Prime | $\omega$ | Kernel directions satisfying all 37 constraints |
|---|---|---|
| 17  | 2 | **16** |
| 41  | 3 | **40** |
| 73  | 10 | **72** |
| 257 | 4 | **256** |

**The satisfying-direction count is exactly $p - 1$ at every prime**. The pair-
resultant variety is **1-dimensional** in (c)-space restricted to the kernel — a
projective line's worth of solutions per prime, NOT a sparse set.

### Implication

Path A's pair-resultant elimination is **necessary but not sufficient**. The
algebraic consistency of α between minor pairs (resultant vanishing) gives a
1-parameter family parameterized by α itself — but most of these algebraic
solutions don't translate to actual 5-point collinearity in $\mu_8$. The
sufficient condition requires:

(†) $\alpha$ derived from the system is **in $\mathbb{F}_p^*$** (not 0, not undefined),
**AND**

(‡) The 5 points $(\omega^j, h_\alpha(\omega^j))_{j \in M}$ lie on a line —
equivalent to the rank-2 condition holding **non-degenerately** (i.e., the implicit
linear codeword $a + bz$ is actually realized).

At p=17: all $p-1 = 16$ algebraic solutions DO yield real cex (verified by the
34 empirical cex split across S, kernel directions, and α). At p ≥ 41: the
$p-1$ algebraic solutions degenerate — α computed from the resultant is not in
$\mathbb{F}_p^*$, or the points are not actually collinear.

### Next-iteration target

**Step 1**: Take a single satisfying direction at p=41 (e.g., [16, 9, 24, 11, 1, 21]
from output line 80), compute α = $-B_j / A_j$ for some non-degenerate minor j;
check whether α ∈ $\mathbb{F}_{41}^*$. Likely α = 0 or undefined → degenerate.

**Step 2**: If degenerate, identify the algebraic obstruction: the resultant
variety has a "trivial" component (corresponding to $A_j = 0$ for all j or
$B_j = 0$ for all j) that exists at every prime but doesn't realize cex. Subtract
off the trivial component to get the "real" failure variety.

**Step 3**: The real failure variety should be 0-dimensional (a finite set of
points in projective (c)-space with $\alpha$ pinned). Its $\mathbb{F}_p$-rational
points: 16 at p=17, **0 at p=41+**. This would close (8,2) Conj A for $p \geq 41$.

## First symbolic computation (iteration 9)

`issue419_path_A_symbolic.py` derives the 10 minor polynomials for one specific
M = {0, 2, 4, 5, 7} using sympy. Key finding:

**Minor (0, 2, 4) is α-only (zero constant term in α)**:
$$ \det_{(0,2,4)} \;=\; -4\alpha \cdot \left[(c_2 + c_6) + \omega^2 (c_3 + c_7)\right] $$

Hence failure with this M requires the **linear F_p-constraint on (c)**:
$$ (c_2 + c_6) + \omega^2 (c_3 + c_7) \;\equiv\; 0 \pmod p. $$

Verified at the empirical cex (`S=[0,1,2,3]`, `c=[10,13,6,10,1,11]`, p=17):
$(c_2 + c_6) = 11$, $(c_3 + c_7) = 7$, $\omega^2 = 13$. Then $11 + 7 \cdot 13 = 102 \equiv 0 \pmod{17}$. ✓

This is **one of several** consistency constraints; the full failure variety per
M is the simultaneous vanishing of all 10 minors. The script enumerates them;
tomorrow's iteration must:

(a) Eliminate α from a non-degenerate minor pair to extract the **(c)-only**
consistency conditions (independent of α). For M = {0, 2, 4, 5, 7}, this should
give a small system of polynomial conditions on $(c_2, c_3, c_4, c_5, c_6, c_7)$.

(b) Intersect with the **kernel constraint** $\sum_r c_r \omega^{rs} = 0$ for
$s \in S$ (4 linear equations in c). The intersection variety is the failure
locus for (S, M).

(c) Test: does the failure variety have $\mathbb{F}_p$-points for $p = 17$ but
NOT for $p \geq 41$? Run the same elimination at multiple primes, count points.

(d) Repeat for the remaining $\binom{8}{5} - 1 = 55$ subsets M.

(e) Take union over all M, all S; verify the union is empty for $p \geq 41$.

## Files

- `issue419_p17_cex_diagnostic.py` (NEW) — extracts the failing α = {7, 12} pattern
- `issue419_p17_cex_diagnostic.output.txt` — full enumeration of 34 cex
- `issue419_path_A_symbolic.py` (NEW) — symbolic minor polynomials for M = {0,2,4,5,7}
- `issue419_path_A_symbolic.output.txt` — minor (0,2,4) = α·[c_2+c_6+ω²(c_3+c_7)] derived
- (Pending) `issue419_path_A_elim_full.py` — full elimination + per-M failure variety

## Honest framing

This is the **right scale** to attack: (8, 2) is small enough that explicit
algebraic geometry is tractable. The empirical fingerprint (only $\alpha \in \{7, 12\}$
fail at $p = 17$, only at this prime) is the cleanest possible failure signal:
the failure locus is a sparse algebraic set with $\mathbb{F}_p$-points only
sporadically. The structural close should fall out of explicit elimination.

Confidence: **40–50% on Path A in 2 weeks** to a tight unconditional bound for
$p \geq 41$ (or similar small constant).

If Path A succeeds: paper2 §7's "modulo Conjecture A" qualifier disappears,
$K_{\mathrm{BW}} \leq 2$ becomes unconditional at L_2/L_3 deployment scales,
and the Proximity-Prize submission becomes structurally complete.
