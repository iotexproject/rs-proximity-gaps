# Note 0257 — Chain + just 2 endpoint constraints close Stage 2

**Date:** 2026-04-29 night
**Status:** **Major structural simplification**. Stage 2 closure (V(I) = {0})
follows from y0 chain (h-1 eqs) + just 2 endpoint constraints, totaling
h+1 polynomial equations in (h-1) variables. Verified at h ∈ {4, 5, 6, 7}
via `g3_chain_endpoint_only.py`.

## The setup

Recall (Notes 0254, 0255):

**y0 chain (h-1 eqs):** for c = 1..h-1, `4 y0_c = (x_c - W_c) + 3 V_c
+ 2 (X·W)_c - (W²)_c = 0`. Equivalent to "x_c = W_c + corr in W's".

**Constraint at c (h-1 eqs):** combining y0+y2 gives
`cubic_c = (11 V_c + 6 (X·W)_c - 3 (W²)_c) / 2`. Decompose:
- **Bulk** (c ∈ [1, h-3]): cubic_c = [z^{2h+c}] X³ ≠ 0 generically.
- **Endpoint** (c ∈ {h-2, h-1}): cubic_c = 0 trivially. Constraint reduces
  to `14 V_c - 3 [z^c] U² = 0 mod I`, with U = X − W (Note 0255).

## The discovery

Let:
```
E_{h-1}(x) := 14 V_{h-1} - 3 [z^{h-1}] U(z)²       (degree 4 in x)
E_{h-2}(x) := 14 V_{h-2} - 3 [z^{h-2}] U(z)²       (degree 4 in x)
```

Then **chain + {E_{h-1}, E_{h-2}} alone** generates an ideal whose radical
is the maximal ideal (x_1, ..., x_{h-1}). I.e., V(chain ∪ {E_{h-1}, E_{h-2}}) = {0}.

This is BENCHMARKED against the full Stage 2 ideal (chain + bulk + endpoint):
both produce identical Groebner bases at small h.

## Verification (`g3_chain_endpoint_only.py`)

| h | chain only | chain + endpt | chain + bulk | chain + bulk + endpt = y0+y2 |
|---|------------|---------------|--------------|-----|
| 4 | NOT close | **close** | close | close |
| 5 | NOT close | **close** | close | close |
| 6 | NOT close | **close** | NOT close (x_2, x_4) | close |
| 7 | NOT close | **close** | close | close |

Notable: at h=6, "chain + bulk" alone fails to kill {x_2, x_4}! The
endpoint constraints are ESSENTIAL — they're not just "simpler" but
genuinely add information that bulk lacks.

## Why this matters

A general-h structural proof of Stage 2 closure for the (3k/2, 2k) family
needs only:

```
∀ c ∈ [1, h-1]:  (x_c - W_c) + 3 V_c + 2 (X·W)_c - (W²)_c = 0     (chain, h-1 eqs)
                  14 V_{h-1} - 3 [z^{h-1}] U² = 0                  (endpoint 1)
                  14 V_{h-2} - 3 [z^{h-2}] U² = 0                  (endpoint 2)
```

⟹ x_1 = ... = x_{h-1} = 0 (in char outside a small bad set).

This is **h+1 equations in h-1 variables**, with explicit polynomial form.

## Pen-and-paper closure scheme

The chain expresses each x_c iteratively in terms of (W_1, ..., W_c).
Inverted: W_a is a polynomial in (x_1, ..., x_a) (Note 0254 inversion).

So all of (V_c, (X·W)_c, (W²)_c, [z^c] U²) become polynomials in x's of
degree 4 (after chain substitution applied).

The endpoint equations become 2 polynomial equations in (x_1, ..., x_{h-1})
of degree ≤ 4. Combined with the chain (which is automatically satisfied
once x's are interpreted via the inversion), we have:

```
E_{h-1}(x_1, ..., x_{h-1}) = 0
E_{h-2}(x_1, ..., x_{h-1}) = 0
```

— 2 polynomial equations in h-1 variables.

**Conjecture (verified h ≤ 7):** for char(F) outside {2, 3, ...}, the
common zero set V(E_{h-1}, E_{h-2}) ⊂ A^{h-1} is exactly {0}.

If this conjecture is provable structurally (via rank or Bezout argument),
we have the **h-uniform closure**.

## h=4 hand-derivation (sanity check)

At h=4: variables x_1, x_2, x_3.

Chain:
- y0_1: (x_1 - W_1) + 0 + 0 - 0 = x_1 - W_1 = 0. W_1 = 2 x_2 x_3. So x_1 = 2 x_2 x_3.
- y0_2: (x_2 - W_2) + 3 V_2 + 2 x_1 W_1 - W_1² = 0. W_2 = x_3². V_2 = x_1². 
  ⟹ x_2 - x_3² + 3 x_1² + 2 x_1 (2 x_2 x_3) - (2 x_2 x_3)² = 0
  ⟹ x_2 - x_3² + 3 x_1² + 4 x_1 x_2 x_3 - 4 x_2² x_3² = 0.
- y0_3: (x_3 - W_3) + 3 V_3 + 2 [(X·W)_3] - [(W²)_3] = 0. W_3 = 0 (no decompositions of 7=h+3 with both ≤3). V_3 = 2 x_1 x_2. (X·W)_3 = x_1 W_2 + x_2 W_1 = x_1 x_3² + 2 x_2² x_3. (W²)_3 = 2 W_1 W_2 = 4 x_2 x_3³.
  ⟹ x_3 + 6 x_1 x_2 + 2 x_1 x_3² + 4 x_2² x_3 - 4 x_2 x_3³ = 0.

Endpoints (h-1=3, h-2=2):
- E_3 = 14 V_3 - 3 [z^3] U². V_3 = 2 x_1 x_2. [z^3] U² = u_1 u_2 + u_2 u_1 = 2 u_1 u_2.
  u_1 = x_1 - W_1 = x_1 - 2 x_2 x_3. u_2 = x_2 - W_2 = x_2 - x_3².
  [z^3] U² = 2 (x_1 - 2 x_2 x_3)(x_2 - x_3²).
  E_3 = 28 x_1 x_2 - 6 (x_1 - 2 x_2 x_3)(x_2 - x_3²) = 28 x_1 x_2 - 6 [x_1 x_2 - x_1 x_3² - 2 x_2² x_3 + 2 x_2 x_3³]
      = 28 x_1 x_2 - 6 x_1 x_2 + 6 x_1 x_3² + 12 x_2² x_3 - 12 x_2 x_3³
      = 22 x_1 x_2 + 6 x_1 x_3² + 12 x_2² x_3 - 12 x_2 x_3³.
- E_2 = 14 V_2 - 3 [z^2] U². V_2 = x_1². [z^2] U² = u_1² = (x_1 - 2 x_2 x_3)².
  E_2 = 14 x_1² - 3 (x_1 - 2 x_2 x_3)² = 14 x_1² - 3 [x_1² - 4 x_1 x_2 x_3 + 4 x_2² x_3²]
      = 14 x_1² - 3 x_1² + 12 x_1 x_2 x_3 - 12 x_2² x_3²
      = 11 x_1² + 12 x_1 x_2 x_3 - 12 x_2² x_3².

So E_3 and E_2 are the two endpoint constraints. Combined with the chain,
they kill {x_1, x_2, x_3}.

## Open question for descent

Can we show V(E_{h-1}, E_{h-2}) ∩ V(chain) = {0} via a clean argument?

Bezout-type: V(E_{h-1}) and V(E_{h-2}) each have codim 1 in V(chain) ⊂ A^{h-1}.
If V(chain) is itself codim h-1 in A^{h-1} (i.e., dim 0), then transversal
intersection gives codim h+1 — but we have only h-1 vars, so this only tells
us "codim ≥ h-1" (which is the maximal possible).

Better: V(chain) is NOT 0-dimensional (chain alone doesn't close); has
positive-dimensional component. The 2 endpoint constraints cut it down.

Via Krull dimension: dim V(chain) = dim Spec F[x]/(chain) ≥ ? Need to
compute. Empirically at h=7: chain GB has 74 elements (LARGE), but the
variety has positive dimension that endpoint constraints kill.

Need to think about V(chain) more carefully. Actually each y0_c is degree
4 polynomial. h-1 eqs of degree 4 in h-1 vars — dim ≤ h-1 - rank, and Bezout
suggests deg ≤ 4^{h-1}.

## Files

- `notes/scripts/g3_chain_endpoint_only.py` — verifies closure (chain + 2 endpoints).
- `notes/scripts/g3_y0y2_only.py` — full layer-by-layer analysis.
