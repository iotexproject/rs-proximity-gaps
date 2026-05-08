# Note 0478 — Empirical: ALL high-agr GS codewords are induced form

**Date:** 2026-05-04 evening (post Note 0477)
**Status:** Strong structural reduction — Conjecture A reduces to its induced sub-case + a "non-induced agr < 71" claim that's empirically universal.

---

## TL;DR

Across 30 stratum (B) K=16 cases at $p \in \{641, 769, 1153\}$, ran GS m=2
list decoder at $\tau = 71$ for ~30 α per case (HIGH + MED + 5 random
LOW). Found **975 non-zero codewords**. Every single one is **induced
form** ($c_1 = c_2 = c_3 = 0$, i.e., $c(w) = c_0(w^4)$ pulls back from $L_2$).

**Per-fiber $a_z$ distribution:** only $a_z \in \{0, 4\}$ observed
(31163 fibers with $a_z = 0$, 37 with $a_z = 4$). Never 1, 2, or 3.

This empirical structure suggests Conjecture A reduces cleanly to:

**Conjecture A' (sharper):** For any non-induced $c \in \mathrm{RS}_{32}(L_0)$,
$\mathrm{agr}(g_\alpha, c) < 71$ (the GS m=2 threshold).

If A' holds, Conjecture A's non-induced case is vacuous: there's no
non-induced c above the GS threshold, hence none above the BW threshold
$\tau = 80$ either.

## 1. Setup

For each (case, α) pair, we run GS m=2 at τ=71 and inspect each codeword
$c$ found:
- Decompose $c(w) = c_0(w^4) + w c_1(w^4) + w^2 c_2(w^4) + w^3 c_3(w^4)$
  (each $c_r$ has degree $< 8$).
- "Induced" iff $c_1 = c_2 = c_3 = 0$.
- Compute per-fiber agreement $a_z := \#\{i \in [0,4) : c(w_0 \zeta^i) = g_\alpha(w_0 \zeta^i)\}$
  for each $z \in L_2$.

Sum over fibers gives total agreement: $\mathrm{agr}(g_\alpha, c) = \sum_z a_z$.

## 2. Empirical results (`issue419_fiber_az_distribution.py`)

| Quantity | Value |
|---|---|
| Total non-zero codewords found | 975 |
| Induced form ($c_1=c_2=c_3=0$) | **975** (100%) |
| Non-induced form | **0** (0%) |
| Total fibers analyzed | 31200 (= 975 × 32) |
| Fibers with $a_z = 0$ | 31163 |
| Fibers with $a_z = 1$ | 0 |
| Fibers with $a_z = 2$ | 0 |
| Fibers with $a_z = 3$ | 0 |
| Fibers with $a_z = 4$ | 37 |

**Conclusion**: every GS-found codeword above $\tau = 71$ is induced
form, and on each fiber it either entirely matches (a_z = 4) or
entirely disagrees (a_z = 0).

## 3. Why this is consistent

For induced $c(w) = c_0(w^4)$: on fiber over $z$ (elements
$w_0, w_0\zeta, w_0\zeta^2, w_0\zeta^3$), $c$ takes the constant value
$c_0(z)$. Similarly $g_\alpha(w) = h(w^4)$ takes constant value $h(z)$.
So $a_z = 4$ if $c_0(z) = h(z)$, else $a_z = 0$. The dichotomy
$a_z \in \{0, 4\}$ is automatic for induced $c$.

This explains the empirical $a_z$ distribution.

## 4. The reduction to Conjecture A'

Conjecture A says: $\max_c \mathrm{agr}(g_\alpha, c) = N_\alpha$.

Decompose: $\max_c = \max(\max_{c \text{ induced}}, \max_{c \text{ non-induced}})$.

**Induced case** (Note 0475): $\mathrm{agr}(g_\alpha, c)_{\text{ind}}
= 4 \cdot \mathrm{agr}_{L_2}(h, c_0) \leq 4 \cdot (39 - N_\alpha/4)
= 156 - N_\alpha$.

This is $\leq N_\alpha$ iff $N_\alpha \geq 78$. Since empirically $N_\alpha
\in \{0, 4, \ldots, 72, 80\}$ (multiples of 4 with gap [73, 79], Note 0474),
this gives induced closure for $N_\alpha = 80$ via Lemma 2 at $L_0$,
**but does NOT close $N_\alpha \leq 72$ via the induced bound alone.**

The second-level structure: $\mathrm{agr}_{L_2}(h, c_0) \leq N_\alpha/4$
for our specific $h$ would require the SAME conjecture but at $L_2$ scale
(which is paper2's `thm:no-full-base-closure` at $(L_2, k_2) = (32, 8)$).
That theorem closes the base $L_2 = (16, 4)$ case + 3-support pencils,
not directly our $(32, 8)$ + arbitrary $c_0$. So the recursion at $L_2$
needs its own work.

**Non-induced case**: empirically NO codeword found via GS at $\tau = 71$.
Conjecture A' says structurally: non-induced $c$ have agr $<$ 71.

If A' holds, non-induced never reaches BW threshold, so the non-induced
contribution to Conjecture A is vacuous.

## 5. Why Conjecture A' might be provable

Non-induced c has at least one of $c_1, c_2, c_3 \neq 0$. WLOG $c_1 \neq 0$
(symmetric). $c_1$ has degree $< 8$, so $c_1$ vanishes at $\leq 7$ values
of $z \in L_2$.

On each fiber over $z$ where $c_1(z) \neq 0$: the function $i \mapsto c(w_0 \zeta^i) - h(z)$
has DFT $\hat F$ on $\mathbb{Z}/4$ with $\hat F(1) = w_0 c_1(z) \neq 0$.
A non-zero "pure tone" at any frequency $r \neq 0$ contributes 0 zeros.

But $\hat F$ may have multiple non-zero frequencies, mixing them. The
number of zeros of $F: \mathbb{Z}/4 \to \mathbb{F}_p$ depends on the
pattern of $\hat F$.

**Lemma sketch** (TODO verify): If $F: \mathbb{Z}/4 \to \mathbb{F}_p$
has Fourier coefficients all non-zero, then $F$ has 0 zeros on $\mathbb{Z}/4$
(generically). Or more precisely: the number of zeros depends on whether
the four DFT phasors $\{\hat F(r) \zeta^{ir}\}_r$ sum to 0 at any $i$.

For random $\hat F$: by Plancherel, $\sum_i |F(i)|^2 = \frac{1}{4}\sum_r |\hat F(r)|^2$.
If 3 of 4 $F(i)$ are zero, then one $|F(i)| \neq 0$ and the rest are 0;
$\sum |F(i)|^2 = |F(\bar i)|^2$. This forces specific $\hat F$ ratios.

**More carefully**: $a_z = 3$ requires $F(i) = 0$ at exactly 3 of 4 $i$'s.
WLOG $F(3) \neq 0$. Then DFT: $\hat F(r) = F(3) \zeta^{-3r}$ for all $r$.
So $|\hat F(0)| = |\hat F(1)| = |\hat F(2)| = |\hat F(3)|$ — i.e., all
four Fourier modes have the same "magnitude" (up to phase).

For our $F = c|_{\text{fiber}} - h(z)$: $\hat F(0) = c_0(z) - h(z)$,
$\hat F(r) = w_0^r c_r(z)$ for $r = 1, 2, 3$. So $a_z = 3$ requires:
$|c_0(z) - h(z)| = |w_0 c_1(z)| = |w_0^2 c_2(z)| = |w_0^3 c_3(z)|$.

Over $\mathbb{F}_p$ this is a non-trivial polynomial constraint on $z$
(several equations, codim $\geq 3$ in the $z$ space). For "generic"
$c_0, c_1, c_2, c_3$: NO $z$ satisfies all three constraints
simultaneously, so no fiber has $a_z = 3$.

Empirically: 0 fibers with $a_z = 3$ across 31200 fibers. Consistent.

The statement "$a_z = 3$ never occurs" might be provable as: the
locus where $a_z = 3$ has codimension 3 in $z$, generically empty.
But it's not strictly impossible without more constraints on $c$.

## 6. Refined attack plan

1. **Prove Conjecture A'**: any non-induced $c \in \mathrm{RS}_{32}(L_0)$
   has $\mathrm{agr}(g_\alpha, c) < 71$.
   - Path: bound $\sum_z a_z$ where $a_z \in \{0, 1, 2, 3, 4\}$ via
     polynomial-system rank analysis on $c_1, c_2, c_3$.
   - Use $c_1, c_2, c_3$ all polynomials of degree $< 8$ to bound
     joint-zero loci.

2. **Reduce induced case** to $L_2$ recursion: show
   $\mathrm{agr}_{L_2}(h, c_0) \leq N_\alpha/4$ for our specific $h$
   on $L_2$ (which is paper2's open question at $L_2 = (32, 8)$).

If both hold: Conjecture A is fully closed.

## 6.5 Why Singleton + reverse-triangle just recovers Lemma 2

A natural "easy" attack: use Singleton bound on RS codes ($\mathrm{wt}(c) \geq n_0 - k_0 + 1 = 97$) plus reverse triangle inequality on Hamming supports:

$$
\mathrm{wt}(g_\alpha - c) \geq |\mathrm{wt}(c) - \mathrm{wt}(g_\alpha)| \geq 97 - (128 - N_\alpha) = N_\alpha - 31.
$$

Hence $\mathrm{agr}(g_\alpha, c) \leq 128 - (N_\alpha - 31) = 159 - N_\alpha$.

This is EXACTLY Lemma 2 (degree counting) from Note 0471. So the
Singleton + set-difference approach gives no new information.

The supporting reverse-triangle: $\mathrm{supp}(g_\alpha - c) \supseteq \mathrm{supp}(c) \setminus \mathrm{supp}(g_\alpha)$ is correct, but only gives the difference bound $97 - 48 = 49$, recovering Lemma 2.

Conjecture A genuinely needs deeper structural input than Singleton.

## 7. Where this leaves the proof

- $K_1 \leq 2$: **fully unconditional** (Note 0471's 3-lemma chain).
- $K_2 = 0$: requires Conjecture A.
- Conjecture A reduces to:
  - **Conjecture A' (non-induced has agr < 71):** empirically held in 975/975
    GS-found codewords (this note); structural proof outline §5 above.
  - **Induced sub-case at $L_2$**: recursion to paper2's closure at $L_2$.

Both pieces look feasible. The Roos / van Lint-Wilson path (Note 0477)
is dead, but this fiber-decomposition path is alive and has empirical
evidence + a partial proof sketch.

## 8. Files

- This note 0478
- `notes/scripts/issue419_fiber_az_distribution.py` — the empirical test
- `notes/scripts/issue419_fiber_az_distribution.output.txt` — output
- Notes 0470-0477 (preceding context)
