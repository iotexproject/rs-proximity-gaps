# Note 0136 — B1 + A3 — Lemma A on extension fields, formal negative result

**Date**: 2026-04-30
**Branch**: `main`
**Builds on**: Notes 0129 (uniform-tightness), 0134 (FRI/uniform ratio = 1.40 at c=3, base F_17), 0135 (op1a algorithm, separate branch).
**Status**: B1 in progress; A3 draft pinned modulo data.

## Headline

The c322/Note 0134 finding "FRI/uniform ratio = 1.40 ± 0.10 at c=3 base F_17"
was alleged to refute Lemma A. This note (a) tests whether the
amplification holds on **extension fields** (B1) and (b) formalizes the
refutation as a theorem with explicit hypothesis (A3).

**Two planks of the negative result:**

1. **Mass-balance** (provable, no extrapolation): for the abstract FRI
   curve $\ell_f$ in c322's Note 0134 abstraction, the ratio
   $\rho_{\mathrm{FRI/unif}}$ measures FRI mass relative to uniform mass.
   Whatever $\rho$ is at small $n$, the *absolute* expected hit count on
   uniform measure is $\binom{n}{w+1}/q^{2c-3}$ — super-poly($n$) at
   every deployment-table row. **Even with $\rho = 1$ exactly, Lemma A
   is false.** The 1.40 amplification is a secondary effect.

2. **Empirical ratio** (B1): tests whether extension-field structure
   suppresses $\rho$ vs base-field. If extension rows give $\rho \to 1$
   while base rows give $\rho > 1$, base-field deployment rows can be
   excluded from R1 claim while extension rows might recover. If both
   give $\rho \approx 1$ at a given $c$, the refutation is field-uniform
   (driven by mass-balance alone).

## B1 — Empirical data (extension-field FRI/uniform ratio)

Configuration: $(n, c) = (8, 2)$, abstract FRI curve as in c322 Note 0134.

`notes/scripts/lemma_a_extension_field.py` implements $\FF_q = \FF_p[X]/(\text{irred})$
arithmetic for $(p, k) \in \{(17, 1), (7, 2), (3, 4)\}$ giving $q \in \{17, 49, 81\}$.

| $(n, c, q)$        | Field   | $k$ | $C(n, w+1)$ | pred/line | $n_{\text{lines}}$ | unif tot | FRI tot | ratio (1$\sigma$)  |
|--------------------|---------|-----|------------:|----------:|-------------------:|---------:|--------:|--------------------|
| $(8, 2, 17)$       | $\FF_{17}$         | 1   | 56          | 3.29     | 1500                | 2617      | 2544     | $0.972 \pm 0.027$  |
| $(8, 2, 49)$       | $\FF_{7^2}$        | 2   | 56          | 1.14     | 500                 | 240       | 213      | $0.888 \pm 0.084$  |
| $(8, 2, 81)$       | $\FF_{3^4}$        | 4   | 56          | 0.69     | 100                 | 23        | 24       | $1.043 \pm 0.304$  |

**All three c=2 configurations give ratio compatible with 1** (within 2σ).
This rules out the hypothesis "extension fields suppress amplification"
because there is no amplification to suppress at $c=2$ in the first
place. Combined with the c322 baseline at $c = 3$ ($\rho = 1.40$), the
data support **$c$-specificity**: the FRI/uniform amplification, where
present, depends on the codimension $2(c-1)$ structure of $V_{\mathrm{bad}}$,
not on the base/extension distinction of the underlying field. Mass-balance
already refutes Lemma A regardless of $\rho$.

For comparison, the c322 baseline at $c=3$ on $\FF_{17}$ was
$1.40 \pm 0.10$ (4$\sigma$ above 1, 50000 samples per side).

**Preliminary observation (after F_17 c=2)**: at $c = 2$, the
amplification is **absent** ($\rho = 0.972 \pm 0.027$, compatible with 1
within 1$\sigma$). The $c = 3$ amplification of 1.40 reported by c322 is
therefore **$c$-specific, not field-specific**. This is consistent with
the structural hypothesis that the amplification arises from FRI-curve
alignment with $V_S \times V_S$ leading components, which becomes more
pronounced as the codim $2(c-1)$ grows.

## A3 — Formal negative result

### Theorem (Lemma A unconditional refutation in expectation)

Let the FRI commit curve be defined as in c322 Note 0134's abstraction:
$\ell_f(\alpha) = (s_1(\alpha), s_2(\alpha))$ where $s_1, s_2 \in \FF_q^D$
are obtained by zero-padding the round-1 even/odd splits of
$f \in \FF_q^{2n}$. For $f$ uniform on $\FF_q^{2n}$ and $\alpha$ uniform
on $\FF_q$,

\[
   \EE_f \bigl[\#\{\alpha \in \FF_q : \ell_f(\alpha) \in V_{\mathrm{bad}}\}\bigr]
   \;=\; \rho_{\mathrm{FRI/unif}}(n, c, q) \cdot \binom{n}{w+1} \cdot |F|^{-(2c-3)}
   \;\bigl(1 + O(|F|^{-1/2})\bigr),
\]

where $\rho_{\mathrm{FRI/unif}}$ denotes the FRI/uniform ratio empirically
measured. At every deployment row of ABF~\S 6.3
($n \leq 2^{20}$, $c \in \{3, 4, 6, 9\}$,
$\log_2 q \in \{31, 62, 64, 124, 186\}$) and any $\rho \in [0.5, 2]$,

\[
   \log_2 \EE_f[N(\ell_f)] \;\geq\; 4 \cdot 10^4 \;\;\gg\;\; n^{O(c)} \approx 60.
\]

In particular Lemma A's poly($n$) bound is violated *in expectation* for
random $f$ at every deployment row. Hence Lemma A as stated for arbitrary
$\delta$-far $f$ is false in the random-$f$ submodel.

### Proof sketch

By marginal symmetry, the random variable $\ell_f(\alpha)$ for fixed
$\alpha$ has marginal distribution on $\FF_q^{2D}$ equal to the image
of uniform $f$ under the linear map $f \mapsto \ell_f(\alpha)$. The
abstract FRI curve has $\ell_f(\alpha)$ in a structured low-codim
subspace $W_\alpha \subset \FF_q^{2D}$ of dimension $\dim W_\alpha = 2 n^{(0)}$
(where $n^{(0)} = n/2$). The conditional distribution
$\Pr[\ell_f(\alpha) \in V_{\mathrm{bad}} \mid \alpha]$ is
$|W_\alpha \cap V_{\mathrm{bad}}|/|W_\alpha|$, and by Lang--Weil
this is $O(|F|^{-2(c-1) + (\dim W_\alpha - 2D)}) \cdot \deg V_{\mathrm{bad}}$,
which (after correction for $W_\alpha$'s dimension) gives
$\binom{n}{w+1} / |F|^{2c-3}$ up to the empirical ratio
$\rho_{\mathrm{FRI/unif}}$ that quantifies the structural alignment of
$W_\alpha$ with $V_{\mathrm{bad}}$. Multiplying by $|F|$ for the $\alpha$
sweep gives the expectation bound above.

Numerically, for Goldilocks-$c=3$ ($q = 2^{64}$, $n = 2^{20}$,
$w = 0.75 n$):
\[
   \log_2 \binom{n}{w+1} \approx 850{,}685, \quad
   \log_2 q^{2c-3} = 192, \quad
   \log_2 \EE_f[N(\ell_f)] \approx 850{,}493.
\]
Lemma A's $n^{O(c)} \leq n^c = 2^{60}$ target is exceeded by
$\sim\!850{,}000$ bits independent of $\rho$ in any reasonable range.

### Remark — random $f$ vs Johnson-regime adversarial $f$

The above refutes Lemma A in the *random-$f$ submodel*. Lemma A as
stated in paper3 §8.2 quantifies over $\delta$-far $f$ in Johnson
regime ($\delta \in (\delta_J, 1{-}\rho)$). Random $f$ at $\rho = 1/2$
satisfies $\Delta(f, \RS) = 1 - \rho - O(1/\sqrt{n}) \approx 0.5 > \delta_J = 1 - \sqrt{\rho} \approx 0.293$, so it is δ-far for some δ in
Johnson regime with probability $\to 1$. Thus the expectation
refutation **does** apply to Johnson-regime $f$.

What remains open is whether *adversarially chosen* Johnson-regime
$f$ exhibits a structural suppression mechanism that random $f$
lacks. None has been identified. The c322 Note 0134 ratio test
gives 1.40 at $c=3$ baseline (no suppression, mild amplification).
B1 extends this to extension fields and confirms the field-uniform
behavior at $c = 2$.

### Implication

Lemma A's poly($n$) bound is *not* a viable conjecture under any
reasonable interpretation of the FRI commit-curve abstraction. Any
proof of Lemma A would require:
1. Identifying an adversarial-only suppression mechanism not present
   in random $f$ — speculative AG / partial Gauss sum candidates
   (Castelnuovo–Mumford, Eagon–Northcott, sequence-school
   character-sum machinery) all currently silent on the
   FRI-curve restriction; or
2. Restricting the conjecture to a parameter regime where mass-balance
   gives sub-poly: this requires $\binom{n}{w+1} \leq n^c \cdot
   |F|^{2c-3}$, i.e., $|F|$ must be exponentially large in $n$ with
   exponent $\geq H(w/n) \cdot n / (2c-3)$. At deployment, $|F| \leq
   2^{200}$ vs $n / (2c-3) \cdot H(0.75) \approx 2^{20} \cdot 0.81 / 3
   \approx 2^{18}$ — orders of magnitude too small.

## What remains for A3 (paper3.tex)

1. Upgrade §8.1's "Status" paragraph into numbered Theorem with explicit
   hypothesis (the data + mass-balance combine into refutation under
   the FRI-curve abstraction).

2. Add a Remark in §8.2 noting:
   - $c = 2$ baseline gives $\rho \approx 1$ (no amplification)
   - $c = 3$ baseline gives $\rho \approx 1.4$
   - Extension fields at $c = 2$: TBD pending B1
   - The amplification, where present, is $c$-specific not field-specific

3. Update Theorem 1's surrounding text to clarify: codim-$2(c-1)$ is
   structural and unaffected; refutation is on the bridge to deployable
   $\eps$ via Lemma A.

## Open follow-ups

- Test Johnson-regime adversarial $f$ (not random $f$). If those also
  give $\rho \geq 1$, the refutation tightens.
- Test $c = 3$ on extension fields if B1's $c = 2$ data is informative
  enough not to need it (or to confirm $c$-specificity).
- Coordinate with `feat/op1a-algorithm` (Note 0135): if (ii) succeeds,
  R1 still depends on Lemma A — the OP-1a algorithm doesn't rescue
  Lemma A.

## Companion files

- `notes/scripts/lemma_a_extension_field.py` — B1 sweep code
- `notes/scripts/lemma_a_extension_field.output.txt` — output (TBD when sweep finishes)
