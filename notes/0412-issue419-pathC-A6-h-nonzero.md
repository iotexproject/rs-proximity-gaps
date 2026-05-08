# Note 0412 -- Issue #419: Path C field-uniform proof for |A|=6 stratum at L_2=(16, 4)

**Date:** 2026-05-02 (Tier 1c iteration 7 — extend to |A|=6 stratum)
**Branch:** `main`
**Status:** **All 1280 no-full $|A|=6$ S at $L_2 = (16, 4)$ are FIELD-UNIFORM**
across all opp-parity $(r, r')$ pairs at every prime $q$ with $16 \mid q-1$.

Combined with |A|=8 (Note 0397, scale+field uniform) and |A|=4
(Notes 0405–0411, field uniform), this brings the cumulative
field-uniform total at $L_2=(16,4)$ to:
$$
16 + 1280 + 5760 = 7056 \;/\; 10896 \;\approx\; 64.8\%.
$$

---

## 1.  Setup recap

For $|A| = 6$: $A$ has 3 σ-orbit reps $\{a_1, a_2, a_3\} \subset \{0, \ldots, 7\}$
giving roots $\zeta_i := \omega^{2 a_i}$ of $G_A(y) = (y-\zeta_1)(y-\zeta_2)(y-\zeta_3)$,
of degree 3.

(D-P) (Note 0398 §6): $G_A(y) \mid (P(y) + y^{r/2})$ where $P$ has degree $\le 1$ (2 free params).

Equivalently: residue $y^{r/2} \bmod G_A(y)$ has degree $\le 1$.  Otherwise (D-P) FAILS,
and (I) ∧ (II) is inconsistent for the fixed $(S, r, r')$.

For $r \in \{4, 6, 8, 10, 12, 14\}$, residue $y^{r/2} \bmod G_A$ has the form
$a_{r/2} y^2 + b_{r/2} y + c_{r/2}$ where $a_k$ satisfies the recursion
$$
a_{k+1} = a_k e_1(\zeta_1, \zeta_2, \zeta_3) + b_k, \quad
b_{k+1} = -a_k e_2 + c_k, \quad
c_{k+1} = a_k e_3.
$$
With base $a_2 = 1, b_2 = c_2 = 0$, the leading coefficient becomes
$a_{r/2} = h_{r/2 - 2}(\zeta_1, \zeta_2, \zeta_3)$,
the $(r/2-2)$-th complete homogeneous symmetric polynomial in 3 variables.

So **(D-P) HOLDS iff $h_{r/2-2}(\zeta_1, \zeta_2, \zeta_3) \ne 0$**.

---

## 2.  Field-uniform check in $\mathbb{Z}[\omega_8]$

$\mathbb{Q}(\omega_8) = \mathbb{Q}(\zeta)$ where $\zeta$ is a primitive 8th root,
$\Phi_8(x) = x^4 + 1$, $[K : \mathbb{Q}] = 4$, Galois group $(\mathbb{Z}/8)^* = \{1, 3, 5, 7\}$.

Script: `issue419_pathC_A6_h_nonzero.py`.  For each $r \in \{4, ..., 14\}$
and each unordered 3-subset of $\mu_8 = \{\omega_8^a : a \in \mathbb{Z}/8\}$
(56 triples), compute $h_{r/2-2}$ ∈ $\mathbb{Z}[\omega_8]$ and integer norms.

**Result:**

| $r$ | $n = r/2 - 2$ | Zero in $\mathbb{Z}[\omega_8]$ | Nonzero | max $|N|$ |
|---|---|---|---|---|
| 4 | 0 | 0 | 56 | 1 |
| 6 | 1 | 0 | 56 | 9 |
| 8 | 2 | **8** | 48 | 4 |
| 10 | 3 | **8** | 48 | 4 |
| 12 | 4 | 0 | 56 | 9 |
| 14 | 5 | 0 | 56 | 1 |

For $r \in \{4, 6, 12, 14\}$: $h_n \ne 0$ for ALL 56 triples; field-uniform automatic
(no bad primes since norms are at most 9, and primes $q \equiv 1 \pmod 8$ with
$q \le 9$: only $q = 17$, but max $|N| = 9 < 17$, so vacuous).

For $r \in \{8, 10\}$: 8 of 56 triples have $h_n = 0$ identically in $\mathbb{Z}[\omega_8]$.
These would be "structural failures" of the (D-P) closure — UNLESS they correspond
to no S in the |A|=6 stratum.

---

## 3.  The 8 bad triples don't extend to no-full S

The 8 "bad" triples are:

* $(0, 2, 4), (0, 2, 6), (0, 4, 6), (2, 4, 6)$ — all 4 even-mod-2 3-subsets of $\{0..7\}$
* $(1, 3, 5), (1, 3, 7), (1, 5, 7), (3, 5, 7)$ — all 4 odd-mod-2 3-subsets

These are precisely the 3-subsets contained in either parity class of $\mu_8$.

**Claim.**  For each bad triple, the σ-symmetric closure $A := \{a, a+8 : a \in \text{triple}\}$
already contains a fully-populated quadrant of $\mathbb{Z}/16$.

**Proof.**  Consider triple $(0, 2, 4)$:
$$
A = \{0, 8, 2, 10, 4, 12\}.
$$
Mod-4 distribution: $\{0 \bmod 4 = 0, 8 \bmod 4 = 0, 4 \bmod 4 = 0, 12 \bmod 4 = 0\}$
gives 4 elements in quadrant $0$.  Quadrant 0 of $\mathbb{Z}/16$ has exactly 4 elements
$\{0, 4, 8, 12\}$ — all in $A$.  **Quadrant 0 is full → S ⊇ A is FULL.**

Similar analysis for the other 7 bad triples: each contains a quadrant-aligned σ-orbit
that triggers a full quadrant in $S$ regardless of the choice of $B$.

Empirically verified by `issue419_pathC_A6_h_nonzero.py`'s "no-full extension" loop:
for each of the 8 bad triples, **0 valid no-full extensions** ($S \in \{\text{no-full } |A|=6\}$).

---

## 4.  Theorem statement

> **Theorem (Path C, $|A|=6$).**
> For every odd prime $q$ with $16 \mid q-1$, every no-full $S \subset \mathbb{Z}/16$
> with $|S| = 8$ and $|A| = 6$ (where $A = S \cap \sigma S$), and every even $r \in \{4, 6, 8, 10, 12, 14\}$:
> the residue $y^{r/2} \bmod G_A(y)$ has nonzero $y^2$-coefficient.
>
> Hence (D-P) HOLDS, and the (I) ∧ (II) system is inconsistent for any opp-parity
> $(r, r')$.  No proportionality $\mathrm{HT}(t^r) \propto \mathrm{HT}(t^{r'})$ exists.

The proof: $h_{r/2-2}(\zeta_1, \zeta_2, \zeta_3) \ne 0$ in $\mathbb{Z}[\omega_8]$ for all
3-subsets of $\mu_8$ that admit no-full extension.  The 8 "bad" 3-subsets where
$h_n$ vanishes (for $r \in \{8, 10\}$) all force a full quadrant in their σ-symmetric
closure $A$, hence have no no-full extensions.

For $r \in \{4, 6, 12, 14\}$: $h_n \ne 0$ for all 56 triples, even before no-full filtering.

For $r \in \{8, 10\}$: 48 of 56 triples have $h_n \ne 0$ field-uniformly; the other
8 are excluded by no-full.

**FIELD-UNIFORM at every prime $q \equiv 1 \pmod{16}$**, no exceptions (since
$\max |N(h_n)| \le 9$ over all triples, and the smallest prime $q \equiv 1 \pmod 8$
exceeding 9 is $q = 17$).

---

## 5.  Cumulative status

| Stratum | Count | Tier 1c (field-uniform) status | Notes |
|---|---|---|---|
| $|A| = 8$ | 16 | ✓ FIELD+SCALE-UNIFORM | 0397 |
| **$|A| = 6$** | **1280** | **✓ FIELD-UNIFORM (this Note)** | **0412** |
| $|A| = 4$ | 5760 | ✓ FIELD-UNIFORM | 0405-0411 |
| $|A| = 2$ | 3584 | empirical at 3 primes (Note 0401) | (next) |
| $|A| = 0$ | 256 | empirical at 3 primes (Note 0402) | (next) |
| **TOTAL field-uniform** | **7056 / 10896** | **64.8%** | |

---

## 6.  Next concrete artifact

Tier 1c iteration 8: extend Z[ω_16] framework to |A|=2 stratum.

For $|A|=2$: $\deg G_A = 1$, $G_A(y) = y - \zeta_1$.  (D-P) gives 1 condition
on 2 unknowns of $P$ (degree ≤ 1) — trivially satisfiable.  So (D-P) is vacuous.

The closure mechanism for |A|=2 (Note 0401) is the **6×3 over-determination**
of the (II) test at the 6 roots of $H$ (since $|B|=6$).

In Z[ω_16] terms: the (II) test has 6 derived λ values, all required equal.
5 pairwise constraints in Z[ω_16] per S × pair.  Same Vieta + minor framework
as Note 0411, but with 5 constraints instead of 3.

5760 (was 3584?) wait — 3584 S at |A|=2.  Let me re-derive.

Output target: Note 0413.

Estimated: ~1 day for |A|=2 + |A|=0 batch closure.

After that: full $L_2 = (16, 4)$ Tier 1c FIELD-UNIFORM.

---

## 7.  Strategic reflection

The Z[ω_*]-norm framework continues to scale gracefully:
* |A|=8: Z[ω_*] structure trivial (parity preservation).
* |A|=6: $\mathbb{Z}[\omega_8]$-arithmetic, 56 triples × 6 r values, 10 minutes.
* |A|=4: $\mathbb{Z}[\omega_{16}]$-arithmetic, 5760 S × 36 pairs × 6 minors, ~3 minutes per pair.
* |A|=2 (next): same $\mathbb{Z}[\omega_{16}]$ framework, more constraints.
* |A|=0 (next): smallest stratum.

The "bad-prime norm bound" pattern recurs at every stratum.  The framework
is now fully general; remaining work is mechanical extension.

**Q2 closure status: substantially advanced.** Tier 1c is ~2/3 done at L_2=(16,4)
field-uniform; remaining 1/3 (|A| ∈ {0, 2}) is a mechanical day's work.
After that, scale extension to L_2=(2^d, 2^{d-2}) for d ≥ 5 (Tier 1b ladder).
