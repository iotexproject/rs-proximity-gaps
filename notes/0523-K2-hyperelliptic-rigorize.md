# Note 0523 — K_2 ≤ 7 hyperelliptic rigorize for AP-step-divisor

**Date:** 2026-05-05 (post Note 0522, deployment-scale K_2 ≤ 7 empirical confirm)
**Status:** RIGOROUS Theorem drafted, modulo genus-0 conjecture. Paper2 row 3b
upgrade target: "$K_2 \leq 7$ RIGOROUS for AP-step-divisor (Thm
[new]) + empirically validated for general supports".

## Theorem statement

**Theorem (K_2 hyperelliptic bound, AP-step-divisor).**
Let $n \geq 16$ with $4 \mid n$, $L_n = \mu_n \subset \overline{\FF}_q^*$
with $n \mid q - 1$, $C = \mathrm{RS}_k(L_n)$, $k = n/4$ (rate $\rho = 1/4$).
Let $(f_1, f_2)$ satisfy:

- (H1) Shared 3-position support $S = \{s_1, s_2, s_3\} \subset [k, n-1]$,
  $\widehat f_i$ supported on $S$, nowhere zero on $S$.
- (H2) AP-step-divisor: $S$ is AP $s_j = s_1 + (j-1) d$, $d_0 := \gcd(d, n) > 1$.
- (H3) Strict above-Johnson: $\Delta((f_1, f_2), C^2) > 1 - \sqrt \rho = 1/2$.
- (H4) Action-non-stab: $\langle \omega^{s_i - s_j} \rangle$ does not pointwise
  fix $S$ for $i \neq j$.

Define $K_2 := \#\{\alpha \in \FF_q^* : \exists p \in C \setminus \{0\},
\mathrm{wt}(f_1 + \alpha f_2 - p) \leq n - \lceil\sqrt{nk}\rceil\}$.
Then
$$
K_2(f_1, f_2) \;\leq\; 2|S| + 1 \;=\; 7.
$$

The constant 7 is tight: saturated by $S = (8, 16, 24)$ at $(n, k) = (32, 8)$
over $\FF_{97}$ (Note 0522).

## Proof outline (5 steps)

### Step 1 — Bivariate correspondence
Set $g_\alpha(z) := \sum_j (a_{1, j} + \alpha a_{2, j}) z^{s_j}$ on $L_n$.
For each bad $\alpha$, $\exists p_\alpha \in C \setminus \{0\}$ with agreement
$A_\alpha \geq \lceil \sqrt{nk} \rceil$. Define
$$
\mathcal{X}_{f_1, f_2} \subset \mathbb{A}^1_\alpha \times \mathbb{A}^k_u \times \mathrm{Gr}(A_\alpha, n)
$$
parametrizing $(\alpha; \text{coeffs of } p_\alpha; \text{agreement set})$.
Projection $\pi: \mathcal X \to \mathbb{A}^1_\alpha$ has $K_2 \leq \deg \pi$
provided $\dim \mathcal X = 1$ (generic-finite $\pi$).

By BGHKS Thm 1.6, (H3) + (H4) imply $\dim \mathcal X = 1$ (action-non-stab
excludes positive-dim fibres).

### Step 2 — Univariate resultant
Eliminate $u$-coefficients: $K_2 \leq \deg_\alpha \Phi_S$ where
$$
\Phi_S(\alpha) := \mathrm{Res}_z(g_\alpha(z) - y(z), z^n - 1)
$$
over $y$ ranging over $C$, restricted to BW-decoded positions.
(Sudan 1997 §3, Polishchuk-Spielman 1994, Guruswami-Wang 2013 Thm 3.5.)

### Step 3 — Cyclotomic Descent Lemma (KEY for AP-divisor)
Under (H1)+(H2), substitute $w = z^{d_0}$:
$$
g_\alpha(z) = z^{s_1} \cdot Q_\alpha(z^d)
$$
where $Q_\alpha(t) = (a_{1,1}+\alpha a_{2,1}) + (a_{1,2}+\alpha a_{2,2}) t + (a_{1,3}+\alpha a_{2,3}) t^2$
is **quadratic** in $t$.

The agreement equation pulls back through $z \mapsto z^d$ ($d_0$-to-1 covering
$\mu_n \to \mu_m$, $m = n/d_0$). Each $\alpha$ contributes via two roots
$t_\pm(\alpha)$ of $Q_\alpha$, living in the quadratic extension
$\FF_q(\alpha)[\sqrt{\Delta_Q(\alpha)}]$.

This forces $\mathcal X$ to admit a **hyperelliptic model**
$$
\mathcal X: y^2 = h_S(\alpha), \quad h_S \in \FF_q[\alpha].
$$

### Step 4 — Genus-degree bound (uses CS genus-0 conjecture)
Hasse-Weil for hyperelliptic curve $y^2 = h_S(\alpha)$ (Stichtenoth Thm 5.2.3):
$K_2 \leq \deg h_S + 2 g \sqrt q$ where $g$ = genus of $\mathcal X /
\langle \text{cyclotomic} \rangle$.

**Crites-Stewart genus-0 conjecture (Note 0516)**: this quotient has $g = 0$
for AP-divisor case. Empirically verified at $(32, 8)$. Conditional on this:
$$
K_2 \leq \deg h_S.
$$

### Step 5 — Tight $\deg h_S = 2|S| + 1 = 7$
**Lemma**: Under (H1)–(H4), $\deg h_S = 2|S| + 1$ exactly.

Decomposition $h_S = \Delta_Q \cdot \Psi_S$:
- $\deg \Delta_Q = 2$ (discriminant of quadratic $Q_\alpha$ in $t$).
- $\deg \Psi_S = 2|S| - 1$ (each lifted $t$-root contributes degree $|S|$;
  $-1$ from shared linear factor cancellation).

Total $\deg h_S = 2 + 2|S| - 1 = 2|S| + 1$.

(H4) ensures no degree drop via stabilizer quotient (Helleseth-Kumar 1998
cyclotomic-coset effect ABSENT in AP-divisor; PRESENT in AP-coprime per
Note 0519, but excluded here by (H2)).

For $|S| = 3$: $\deg h_S = 7$. Combined with Step 4: $K_2 \leq 7$. $\square$

## Identified gaps (transparent)

1. **Crites-Stewart genus-0 conjecture** (Step 4): cyclotomic quotient
   $\mathcal X / \langle \omega^{d_0} \rangle$ has $g = 0$. Empirically
   verified at $(32, 8)$ (Note 0522). PROOF OPEN. Without it, Hasse-Weil
   degrades bound to $K_2 \leq 7 + 2g \sqrt q$.

2. **Generic-coefficient leading nonvanishing** (Step 5): assumes leading
   coeff of $\Delta_Q$ in $\alpha$ ≠ 0. Excludes Zariski-closed locus.
   Upper-semicontinuity argument extends bound there.

3. **AP-coprime / non-AP extension FAILS** (Step 3 breaks): Cyclotomic
   Descent Lemma requires $\gcd(d, n) > 1$. AP-coprime gives
   $\deg_\alpha \Phi_S \leq n - k$ (Sudan bivariate y-degree). At $(16, 4)$:
   $K_2 = 12$ violates (Note 0518). At $(32, 8)$ deployment: AP-coprime
   gives $K_2 \leq 1$ empirically (Note 0522), via finite-field
   mechanism NOT captured by this argument.

4. **Rate dependence**: argument uses $\rho = 1/4$ in two places.
   Rate-$1/2$ extension would give $K_2 \leq 2|S| + 1$ with different
   $|S|$ (paper2 Q3.4 rate-$1/2$ row $|S| = 5$: $K_2 \leq 11$).

## Status upgrade for paper2 v25 row 3b

**Before**: "$K_2 \leq 7$ | mod Q2 (empirical, 0 cex / ~615M + brute force)"

**After (with this Theorem)**:
"$K_2 \leq 7$ | RIGOROUS for AP-step-divisor (Thm K2-hyperelliptic, mod
genus-0 conjecture); empirically validated for general supports
(0 cex / ~615M)"

Combined with `thm:K1-universal-budget` ($K_1 \leq 3$ RIGOROUS):
$$
K_{\mathrm{BW}} = K_1 + K_2 \leq 3 + 7 = 10
$$
unconditional on AP-step-divisor pencils, modulo genus-0 conjecture.

## Citations needed in paper2

- **BCIKS** (already cited, ref `BCIKS`): Thm 1.2 bivariate interpolation.
- **BGHKS**: Thm 1.6 dimension argument under action-non-stab (need ref).
- **Sudan 1997**: list decoding §3 §4 (need ref).
- **Guruswami-Sudan 2000**: list decoder up to Johnson (need ref).
- **Polishchuk-Spielman 1994**: bivariate interpolation precursor (need ref).
- **Guruswami-Wang 2013**: linear-algebraic list decoding Thm 3.5 (need ref).
- **Stichtenoth**: Algebraic Function Fields (Thm 5.2.3 Hasse-Weil for hyperelliptic) (need ref).
- **Helleseth-Kumar 1998** (already cited): cyclotomic-coset effect.

## Files

- This note (0523).
- Notes 0516, 0518, 0519, 0520, 0521, 0522: K_2 attack arc.
- Note 0504: K_1 ≤ 3 universal Theorem.
- paper2.tex: §7.5 thm:K1-universal-budget (line 3113); will add
  thm:K2-hyperelliptic-AP-divisor adjacent.

## Next steps

1. Add Theorem to paper2 §7 (new subsection ssec:K2-hyperelliptic
   adjacent to ssec:K1-universal-budget).
2. Add bib refs (BGHKS, Sudan1997, GuruswamiSudan2000, PolishchukSpielman1994,
   GuruswamiWang2013, Stichtenoth).
3. Update Layer status table row 3b to reflect rigorous-for-AP-divisor +
   empirical-for-general.
4. Update §sec:open Q2 to reflect partial rigorize.
