# Note 0312 — Rate 1/2 framework degeneracy: σ at n = 2k is non-trivial

**Date:** 2026-04-30
**Status:** Working note. **#411 reclassified as part of #408** —
empirical de-risk requires the same framework adaptation as the
analytic re-derivation.

## Setup recap

paper2 K10 (`thm:universal-K10`) reduces all 2-mono pencils at rate-1/4
deployment $(n_0, k_0) = (4 k_0, k_0)$ to a base case at $(n, k) = (8, 2)$
or $(4, 1)$ via the Substitution Principle (Note 0284). Note 0286 RIGOROUS
gives $K \leq 8$ at base case via Singular GB elimination of the cert + div
ideal:

```
ring R = 0, (z, p_0, ..., p_{2k-1}, alpha, rho), (dp(1), lp(2k+2));
poly sigma = z^{2k} + sum p_i z^i;        // degree 2k = n/2 at rate 1/4
poly z_a = reduce(z^a, std(sigma));       // wraps for a >= 2k
poly h = rho * z_a + alpha * z_b;
matrix M = coeffs(h, z);
poly cert_c = M[c+1, 1] for c in [k, 2k-1];   // high-half coefficients
poly div_c = coeffs(z^n - 1 mod sigma, z)[c]; // sigma divides z^n - 1
ideal I = cert + div;
ideal E = eliminate(I, p_0...p_{2k-1});
deg_alpha(E[size(E)]) = K bound.
```

This works at rate 1/4 because:
1. $\deg \sigma = 2k < n = 4k$: $z^a \mod \sigma$ wraps for $a \geq 2k$,
   producing a polynomial of degree $< 2k$ with $p_i$ coefficients — the
   "freedom" parameter that encodes choice of error pattern.
2. $\sigma \mid z^n - 1$ forces $\sigma$ to be one of $\binom{n}{2k}$
   monic divisors — the parameterization of error patterns of
   $n - 2k = 2k$ wrong positions.

## Naive port to rate 1/2 — degeneracy

For rate 1/2 base case at $(n, k) = (8, 4)$: $2k = 8 = n$. Then:
- $\deg \sigma = 8 = n$, so $z^a$ for $a < n$ does **not** wrap — $z_a = z^a$
  with no $p_i$ coefficients.
- The pencil $h = \rho z^a + \alpha z^b$ with $a, b \in \{4, 5, 6, 7\}$
  (above-J) has support exactly $\{a, b\}$, no other coefficients.
- $\mathrm{cert}_c$ for $c \in [k, 2k - 1] = [4, 7]$ extracts the $z^c$
  coefficient of $h$:
  - $\mathrm{cert}_a = \rho$, $\mathrm{cert}_b = \alpha$, others = 0.
- Setting $\mathrm{cert} = 0$: $\rho = \alpha = 0$. **Trivial constraint.**
- Eliminator $\Phi$ in $\alpha$: degree 1 (just $\Phi = \alpha$).

**Singular run** confirms this:

```
$ python3 g3_2mono_rate_half_base.py
=== Rate 1/2 base case 2-mono Singular GB elimination ===
--- (n, k) = (4, 2) rate 0.50, 1 above-J coprime pairs ---
  ✓ (a, b)=(2, 3): deg=1 (0.0s)        # n = 2k = 4: degenerate
--- (n, k) = (8, 4) rate 0.50, 5 above-J coprime pairs ---
  ✗ (4, 5): matrix M out of range      # h has degree 5, M has 6 rows; need padding
  ✓ (4, 7): deg=1 (0.0s)                # same degeneracy
  ✗ (5, 6): same
  ✓ (5, 7): deg=1 (0.0s)
  ✓ (6, 7): deg=1 (0.0s)
```

`deg_alpha = 1` is **not informative** — it reflects the trivial
"$\rho = \alpha = 0$" constraint, not the genuine algebraic K bound.

## Why the framework collapses at $n = 2k$

The rate 1/4 framework's $\sigma$ of degree $2k = n/2$ encodes
\"$n - 2k = 2k$ error positions\" via the choice of $\sigma$ as a divisor
of $z^n - 1$. The $\binom{n}{2k}$ monic divisors of $z^n - 1$ of degree $2k$
parameterize agreement subsets of size $2k$.

At $n = 2k$ (rate 1/2), \"$n - 2k = 0$ error positions\" has only one
choice: $\sigma = z^n - 1$ itself. No freedom. $h \mod \sigma$ is just $h$
itself (since $\deg h < n$). The cert constraint then says $h$ has zero
coefficients at positions $\geq k$, which for $h = \rho z^a + \alpha z^b$
with $a, b \geq k$ forces $\rho = \alpha = 0$. Trivial.

**Correct rate 1/2 framework** must use a different $\sigma$:
- Rate 1/2 above-J: $t < \sqrt{nk} = \sqrt{2 k^2} = k \sqrt{2}$. For
  integer above-J: $t \leq \lfloor k \sqrt{2} \rfloor$.
- $\sigma_C$ should have degree $n - t$ (the error-position polynomial),
  parameterized by $\binom{n}{t}$ choices.
- For $(8, 4)$: $t \leq 5$, $\sigma$ degree 3 (not 8!), parameterized by
  $\binom{8}{5} = 56$ subsets.

This is structurally **different** from the rate 1/4 setup — not a simple
parameter change.

## Implication for #411 / #408

**#411 was scoped as "1-2 day empirical de-risk"** — the assumption was
that a quick port of the Note 0286 GB framework to rate 1/2 base case
$(8, 4)$ would yield an empirical $K$ value to inform the analytic
re-derivation effort of #408.

**Reality**: the framework adaptation IS the analytic re-derivation. The
rate 1/2 cert + div ideal needs new $\sigma_C$ parameterization at degree
$n - t$, not just a parameter swap. The same Singular machinery applies but
with structurally different cert equations.

**Action**: reclassify #411 as part of #408. The 1-2 day estimate was
incorrect — the work is the same as #408's analytic re-derivation, not
a separate empirical pre-step.

## What's next for paper2 prize-grade

1. **#408 (rate 1/2 K10 extension)**: now subsumes #411. Estimated 1-2
   weeks. Needs:
   - Re-derivation of cert + div with $\sigma_C$ of degree $n - t$ for
     above-J $t$ at rate 1/2.
   - Singular GB enumeration of all $\binom{n}{t}$ $\sigma$ choices at
     base $(8, 4)$.
   - Verify $K_{\text{rate-1/2}} \leq$ small constant.
   - Substitution Principle lift to deployment scale.

2. **#406 (K_4 (1, 2, 6, 7) RIGOROUS)**: 1-3 day quick win. Move to this
   while #408 is open.

## Files

- `notes/scripts/g3_2mono_rate_half_base.py` — naive port (degenerate, see above)
- `notes/scripts/g3_2mono_rate_half_base.output.txt` — naive output
- `notes/scripts/g3_2mono_rate_half_base.example_n4k2.txt` — example Singular log

## Cross-refs

- Issue #408 (paper2 K10 rate 1/2 extension)
- Issue #411 (this companion empirical, now reclassified)
- Note 0286 (rate 1/4 K ≤ 8 RIGOROUS via Substitution Principle)
- Note 0299 (single-recursive ≡ above-J at L_0 for 4 | k_0)
