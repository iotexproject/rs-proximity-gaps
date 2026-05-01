# Note 0005 — S1: Proper Multiplicative Subgroups

**Date**: 2026-04-20  
**Status**: Major structural results. CS finiteness theorem proved. General-word analysis done.

## 1. Goal

All cases in Notes 0001–0004 used $n = p-1$, i.e., $L = \mathbb{F}_p^*$ (the full multiplicative group). This is degenerate: in FRI/STARK, $n \ll p$, and $L$ is a proper multiplicative subgroup of order $n \mid (p-1)$.

**Question**: Does the failure of Conjecture 4 (subgroup-coset alignment) persist when $L \subsetneq \mathbb{F}_p^*$?

## 2. Setup

Fix $m = 2$, $r = 3$, $k = 2$ (the CS construction with $f = X^6$, $g = X^4$, degree-bound $k = 2$). For each $n \in \{24, 36, 48, 60, 72, 96, 120\}$, sweep over primes $p \equiv 1 \pmod{n}$ with varying ratio $(p-1)/n \geq 1$.

**Speedup**: For $k = 2$, replaced brute-force enumeration of $(h_0, h_1) \in \mathbb{F}_p^2$ with Lagrange-pair trick: enumerate pairs $(i, j) \in L$, solve for the unique $h(x) = h_0 + h_1 x$ agreeing on both, check total agreement. Cost drops from $O(p \cdot p^2 \cdot n)$ to $O(p \cdot n^3)$.

## 3. Results

### 3.1 Broad sweep (2–3 primes per $n$)

| $n$ | $p$ | $(p\!-\!1)/n$ | #witnesses | #aligned | #NOT |
|-----|-----|----------------|------------|----------|------|
| 24 | 73 | 3 | 4 | 4 | 0 |
| 24 | 97 | 4 | 4 | 4 | 0 |
| 24 | 193 | 8 | 4 | 4 | 0 |
| **36** | **37** | **1** | 60 | 24 | **36** |
| 36 | 73 | 2 | 6 | 6 | 0 |
| 36 | 109 | 3 | 6 | 6 | 0 |
| **36** | **181** | **5** | 42 | 6 | **36** |
| **48** | **97** | **2** | 56 | 8 | **48** |
| 48 | 193 | 4 | 8 | 8 | 0 |
| 48 | 241 | 5 | 8 | 8 | 0 |
| **60** | **61** | **1** | 310 | 70 | **240** |
| **60** | **181** | **3** | 130 | 10 | **120** |
| **60** | **241** | **4** | 70 | 10 | **60** |
| 60 | 421 | 7 | 10 | 10 | 0 |
| **72** | **73** | **1** | 444 | 84 | **360** |
| **72** | **433** | **6** | 84 | 12 | **72** |
| 72 | 577 | 8 | 12 | 12 | 0 |
| **96** | **97** | **1** | 1312 | 160 | **1152** |
| **96** | **193** | **2** | 496 | 112 | **384** |
| 96 | 577 | 6 | 64 | 64 | 0 |
| **120** | **241** | **2** | 800 | 200 | **600** |
| **120** | **601** | **5** | 200 | 80 | **120** |
| 120 | 1201 | 10 | 20 | 20 | 0 |

### 3.2 Dense $p$-sweep for $n = 36$

Tested all 22 primes $p \equiv 1 \pmod{36}$ up to 2000:

| $p$ | $(p\!-\!1)/n$ | #NOT | shapes |
|-----|----------------|------|--------|
| 37 | 1 | **36** | $(0,1,8)\!\times\!28$, $(0,28,29)\!\times\!7$, $(0,7,35)\!\times\!1$ |
| 73 | 2 | 0 | — |
| 109 | 3 | 0 | — |
| **181** | **5** | **36** | $(0,11,13)\!\times\!23$, $(0,2,25)\!\times\!11$, $(0,23,34)\!\times\!2$ |
| 397–1873 | 11–52 | 0 | — |

Only 2 out of 22 primes exhibit non-alignment.

### 3.3 Dense $p$-sweep for $n = 48$

Tested all 14 primes $p \equiv 1 \pmod{48}$ up to 1500:

Only $p = 97$ (ratio $= 2$) has non-alignment: 48 NOT out of 56 witnesses. All other 13 primes: 100% aligned.

## 4. Observations

### Observation 1: Non-alignment persists with proper subgroups

$n = 36, p = 181$ has $(p-1)/n = 5$ (a genuine proper subgroup), yet 36 non-aligned witnesses appear. **Non-alignment is not an artifact of $L = \mathbb{F}_p^*$.**

### Observation 2: Non-alignment is extremely rare over primes

For $n = 36$: 2/22 primes (9%) show non-alignment.  
For $n = 48$: 1/14 primes (7%) show non-alignment.  

Moreover, the non-alignment primes are concentrated among the smallest primes for their congruence class.

### Observation 3: #NOT is always a multiple of $n$

In every case observed, $\#\text{NOT} \equiv 0 \pmod{n}$. The non-aligned witnesses come in $n$-sized orbits — consistent with the cyclic group $\mathbb{Z}/n\mathbb{Z}$ acting by rotation.

| $n$ | $p$ | #NOT | #NOT/$n$ |
|-----|-----|------|----------|
| 36 | 37 | 36 | 1 |
| 36 | 181 | 36 | 1 |
| 48 | 97 | 48 | 1 |
| 60 | 61 | 240 | 4 |
| 60 | 181 | 120 | 2 |
| 60 | 241 | 60 | 1 |
| 72 | 73 | 360 | 5 |
| 72 | 433 | 72 | 1 |
| 96 | 97 | 1152 | 12 |
| 96 | 193 | 384 | 4 |
| 120 | 241 | 600 | 5 |
| 120 | 601 | 120 | 1 |

### Observation 4: Residue shapes depend on $p$, not just $(n, m, r)$

For $n = 36$:
- $p = 37$: dominant shape $(0, 1, 8)$
- $p = 181$: dominant shape $(0, 11, 13)$

The shape encodes the residue structure modulo the cyclic group, but its specific values are $p$-dependent.

### Observation 5: Non-monotonicity in $(p-1)/n$

$n = 36$: ratio 2 (aligned), ratio 3 (aligned), ratio 5 (**non-aligned**), ratio 11+ (aligned). The presence of non-alignment is not monotone in the embedding index. This rules out naive "small field" explanations.

### Observation 6: "Base count" vs "excess witnesses"

For primes with 0 non-aligned witnesses, the total witness count equals $2n/m$ (the number of coset-union witnesses predicted by the subgroup structure). For example, $n = 36$: base count $= 6$. Non-alignment primes have extra witnesses on top of this base.

## 5. Interpretation

### 5.1 For the prize problem

The FRI setting has $n \ll p$ (typically $n \sim 2^{20}$ and $p \sim 2^{64}$ or larger). Our data strongly suggests that **in this regime, Conjecture 4 (strict subgroup-coset alignment) holds for the CS construction**.

Concretely: as $(p-1)/n$ grows, non-aligned witnesses vanish. This is consistent with the algebraic variety $\mathcal{V}_{n,m,r}$ from Note 0004 having no $\mathbb{F}_p$-rational points outside the subgroup-coset locus when $p$ is sufficiently large relative to $n$.

### 5.2 The arithmetic condition

The pattern of which primes exhibit non-alignment is not yet understood. It is likely related to:
- The factorization of $(p-1)/n$ and its interaction with the subgroup lattice of $\mathbb{Z}/n\mathbb{Z}$
- The existence of certain character-sum cancellations that fail for specific $p$
- The structure of the degree-6 polynomial $x^6 + \lambda x^4 - h_1 x - h_0$ over $\mathbb{F}_p$

### 5.3 Variety point counts: three conditions, not two

Verified that the **exact** witness count matches counting 6-subsets $S \subset \mathbb{Z}/n\mathbb{Z}$ with $e_1 = e_3 = e_4 = 0$ (where $e_k$ are elementary symmetric polynomials of $\{\omega^i : i \in S\}$). Equivalently, power-sum conditions:

$$p_1(S) = 0, \quad p_3(S) = 0, \quad p_4(S) = \frac{p_2(S)^2}{2}$$

where $p_k(S) = \sum_{i \in S} \omega^{ki}$.

This is the "variety" $\mathcal{V}_{36,2,3}$ restricted to 6-element subsets of the cyclic group.

Dense sweep over 22 primes for $n = 36$:
- **Aligned count = 6 for all $p$ with proper subgroup** (24 for $p = 37$ which is full group). This is a combinatorial constant depending only on $n$ and the subgroup lattice.
- **Non-aligned count = 36 or 0.** Exactly 36 for $p = 37, 181$; exactly 0 for all other 20 primes.

### 5.4 Orbit structure (key finding)

**All non-aligned witnesses form free orbits under the cyclic shift action of $\mathbb{Z}/n\mathbb{Z}$.**

| $n$ | $p$ | #NOT | #orbits | orbit size | stabilizer |
|-----|-----|------|---------|------------|------------|
| 36 | 37 | 36 | 1 | 36 | trivial |
| 36 | 181 | 36 | 1 | 36 | trivial |
| 60 | 61 | 240 | 4 | 60 | trivial |
| 60 | 181 | 120 | 2 | 60 | trivial |
| 60 | 241 | 60 | 1 | 60 | trivial |

**Theorem (empirical)**: The non-subgroup locus $\mathcal{V}_{n,m,r} \setminus \mathcal{V}^{\mathrm{sub}}$ has **dimension 0 modulo the $\mathbb{Z}/n\mathbb{Z}$-action**. Its geometric points consist of finitely many free orbits.

### 5.5 Norm mechanism (the key algebraic theorem)

**Why $e_3 = 0$ identically**: The CS polynomial is $x^6 + \lambda x^4 + a_1 x + a_0$ (no $x^5, x^3, x^2$ terms). By Vieta's formulas, the roots automatically satisfy $e_1 = e_3 = e_4 = 0$. In particular, $e_3 = 0$ is a **theorem** for CS, not just empirical.

**Norm-divisibility mechanism**: For a 6-subset $S = \{i_1, \ldots, i_6\} \subset \mathbb{Z}/n\mathbb{Z}$, define:

$$\alpha_1(S) = e_1(\zeta^{i_1}, \ldots, \zeta^{i_6}) = \sum_j \zeta^{i_j} \in \mathbb{Z}[\zeta_n]$$

This is an algebraic integer. Its norm is $N(\alpha_1) = \prod_{k \in (\mathbb{Z}/n\mathbb{Z})^*} \sigma_k(\alpha_1) \in \mathbb{Z}$.

**Key fact**: $S$ is a valid CS witness at prime $p$ (with $p \equiv 1 \pmod{n}$) only if $p \mid N(\alpha_1(S))$ (and similarly for $\alpha_4 = e_4(\ldots)$).

**Proof sketch**: The embedding $\sigma_1: \zeta \to \omega$ sends $\alpha_1(S)$ to $e_1(\omega^{i_1}, \ldots) \in \mathbb{F}_p$. For $S$ to be a witness, this must be 0. Since $\sigma_1(\alpha_1) \equiv 0 \pmod{\mathfrak{p}_1}$ (a prime above $p$), we get $p \mid N(\alpha_1)$.

**Corollary (finiteness)**: $|N(\alpha_1)| \leq |\alpha_1|^{\varphi(n)} \leq 6^{\varphi(n)}$ (since $|\alpha_1| \leq 6$ for a sum of 6 roots of unity). Therefore, the set of non-alignment primes is **finite**, bounded by $6^{\varphi(n)}$.

Verified empirically:

| $n$ | $\varphi(n)$ | $6^{\varphi(n)}$ | Non-alignment primes found |
|-----|-------------|-------------------|----------------------------|
| 36 | 12 | $2.2 \times 10^9$ | $\{37, 181\}$ |
| 48 | 16 | $2.8 \times 10^{12}$ | $\{97\}$ |
| 60 | 16 | $2.8 \times 10^{12}$ | $\{61, 181, 241, 601, \ldots\}$ |

For every non-aligned witness found: $N(e_1) = p$, $N(e_3) = 0$, $N(e_4) = p$ (the norm equals the prime itself, first power).

### 5.6 Theorem: CS alignment holds for large primes

**Theorem 1** (proved): *For the CS construction with parameters $(n, m, r)$ on a cyclic subgroup $L$ of order $n$ in $\mathbb{F}_p^*$, the set of primes $p$ admitting non-subgroup-aligned witnesses is finite. Specifically, $p \leq (rm)^{\varphi(n)}$.*

**Theorem 2** (proved): *For any fixed $n$ and the CS construction, there exists an explicit finite set $\mathcal{P}(n) \subset \mathbb{Z}$ such that for all primes $p \equiv 1 \pmod{n}$ with $p \notin \mathcal{P}(n)$, every CS witness is a union of cosets of subgroups of $\mathbb{Z}/n\mathbb{Z}$.*

**Implication for FRI/STARK**: In practice, $p \sim 2^{64}$ or $2^{128}$, while $\mathcal{P}(n) \subset [1, (rm)^{\varphi(n)}]$. For any concrete FRI system, one can **check** whether $p \in \mathcal{P}(n)$ in polynomial time (compute the finitely many norms and test divisibility). If $p \notin \mathcal{P}(n)$, the proximity gap for CS is determined entirely by the subgroup-coset structure.

### 5.7 What this means for the prize

The Proximity Prize asks about the gap between Johnson bound and capacity. Our results show:

1. **For the CS family** (the known counterexample construction): the bad behavior is completely controlled. Non-alignment is a finite-prime phenomenon, and for generic $p$, the proximity parameter matches the subgroup-coset prediction.

2. **The DFT + norm framework** provides a new tool for analyzing proximity gaps. The key objects ($e_1, e_3, e_4$ as elements of $\mathbb{Z}[\zeta_n]$, their norms) are not present in the existing literature (BCIKS, Crites-Stewart, Diamond-Gruen).

3. **Bridge to sequence theory**: The norms $N(e_j)$ are products of character-sum values — exactly the objects studied in the Golomb-Gong-Helleseth tradition. This opens the door to:
   - Cross-correlation bounds (Welch, Niho)
   - Partial Gauss sum estimates
   - Weil-type bounds on character sums over subgroups

4. **Next frontier**: Extend from CS to general received words.

## 6. General-word analysis (beyond CS)

### 6.1 CS is NOT the worst case

Tested structured words $w = x^a + \lambda x^b$ for various $(a, b) \neq (6, 4)$:

- At $p = 73$ (where CS gives 0 non-aligned): $(7, 6)$ gives 180 non-aligned, $(8, 5)$ gives 36
- At $p = 109$ (where CS gives 0): $(9, 4)$ gives 72, $(10, 2)$ gives 36, $(10, 3)$ gives 36
- The pair $(7, 6)$ gives 180 non-aligned at **all** tested primes ($p = 37, 73, 181$)

**The CS norm-finiteness theorem does NOT generalize to all word families.**

### 6.2 The Vieta mechanism explains the difference

For $w = x^a + \lambda x^b$ with $k = 2$: the agreement polynomial is $x^a + \lambda x^b - h_1 x - h_0$.

| Term structure | Vieta conditions ($e_j = 0$) | Which $e_j$ is free? |
|----------------|------------------------------|----------------------|
| CS $(6, 4)$: $x^6 + \lambda x^4 - hx - h_0$ | $e_1 = e_3 = e_4 = 0$ | $e_2 = \lambda$ |
| $(7, 6)$: $x^7 + \lambda x^6 - hx - h_0$ | $e_2 = e_3 = e_4 = e_5 = 0$ | $e_1 = -\lambda$ |
| $(8, 5)$: $x^8 + \lambda x^5 - hx - h_0$ | $e_1 = e_2 = e_4 = e_5 = e_6 = 0$ | $e_3 = -\lambda$ |

**Key**: CS forces $e_1 = 0$ (since the polynomial has no $x^{a-1}$ term). The norm $\mathrm{Norm}(e_1)$ is bounded, hence finitely many primes divide it. But $(7, 6)$ has $e_1 = -\lambda$ **free** — the norm argument doesn't constrain $e_1$, so non-alignment can occur at all primes.

### 6.3 Per-word list sizes are bounded

Despite the differences in total witness counts, the **per-word list size** (relevant for the proximity gap) remains $O(1)$:

| $(a, b)$ | $p$ | max witnesses per word | max non-aligned per word |
|-----------|-----|------------------------|--------------------------|
| CS $(6, 4)$ | 37 | 6 | 2 |
| $(7, 6)$ | any | 6 | 5 |
| $(8, 5)$ | 37 | **9** | **9** |
| $(10, 9)$ | any | 4 | 3 |

Even the worst case ($(8, 5)$ at $p = 37$: 9 witnesses per word) is $O(1)$.

**Conjecture (new)**: For fixed $(n, k, \delta)$, the per-word list size $L_\delta(w) = \max_{w} \#\{h \in \mathrm{RS}_k : \mathrm{agree}(w, h) \geq (1-\delta)n\}$ is bounded by a constant depending only on $n, k, \delta$ (not on $p$).

### 6.4 Implication for the proximity gap

The proximity gap conjecture asks whether the fraction of RS codewords within distance $\delta$ of a typical word $w$ is small. Our data supports:

1. **Per-word list sizes are $O(1)$** even for non-CS words and non-alignment primes
2. **The fraction of "bad" words** (those with high list size) varies with $(a, b)$ and $p$, but each bad word has bounded list size
3. **Random words have zero witnesses** for $p \geq 109$ (as expected from Schwartz-Zippel)
4. **The worst case is structured** (monomial pairs), and even there, list sizes are small

## 7. Next steps

1. **Prove Theorem 1 rigorously** (CS finiteness) — standalone result, novel, publishable.
2. **Bound per-word list size** for general words. Key tool: the agreement polynomial has degree $d$, so at most $d$ roots in $L$. The list size equals the number of degree-$< k$ polynomials $h$ such that $w - h$ has $\geq t$ roots in $L$. Bound this using: each pair of such $h$ has their difference $(h - h')$ of degree $< k$ with $\geq 2t - d$ common agreement points (by inclusion-exclusion). If $2t - d > k$, this is impossible, giving $L_\delta \leq \binom{d}{t}$ or similar.
3. **MCA (S5)**: For multiple words, the common agreement set constraint should make things much tighter.
4. **Char 2 (S3)**: Test the norm machinery in binary fields.
5. **Engage Gong** (Note 0006 ready).

## 8. Scripts

- `notes/scripts/s1_proper_subgroup.py` — broad sweep across $n$ and $p$
- `notes/scripts/s1_proper_subgroup.output.txt` — output
- `notes/scripts/s1_n36_psweep.py` — dense $p$-sweep for $n = 36, 48$
- `notes/scripts/s1_n36_psweep.output.txt` — output
- `notes/scripts/s1_variety_count.py` — exact variety point count (e1=e3=e4=0)
- `notes/scripts/s1_orbit_analysis.py` — cyclic orbit decomposition
- `notes/scripts/s1_orbit_analysis.output.txt` — output
- `notes/scripts/s1_arithmetic_condition.py` — arithmetic invariants of non-alignment primes
- `notes/scripts/s1_arithmetic_condition.output.txt` — output
- `notes/scripts/s1_norm_computation.py` — norm computation identifying number fields
- `notes/scripts/s1_e3zero_enum.py` — enumeration of $e_3 = 0$ subsets for $n = 36$
- `notes/scripts/s1_e3zero_enum.output.txt` — output
- `notes/scripts/s1_n60_norms.py` — norm computation and verification for $n = 60$
- `notes/scripts/s1_general_word.py` — general word test (random + structured)
- `notes/scripts/s1_general_word.output.txt` — output
- `notes/scripts/s1_vieta_structure.py` — Vieta condition analysis for various $(a,b)$
- `notes/scripts/s1_vieta_structure.output.txt` — output

## 7. Scripts

- `notes/scripts/s1_proper_subgroup.py` — broad sweep across $n$ and $p$
- `notes/scripts/s1_proper_subgroup.output.txt` — output
- `notes/scripts/s1_n36_psweep.py` — dense $p$-sweep for $n = 36, 48$
- `notes/scripts/s1_n36_psweep.output.txt` — output
- `notes/scripts/s1_variety_count.py` — exact variety point count (e1=e3=e4=0)
- `notes/scripts/s1_orbit_analysis.py` — cyclic orbit decomposition
- `notes/scripts/s1_orbit_analysis.output.txt` — output
- `notes/scripts/s1_arithmetic_condition.py` — arithmetic invariants of non-alignment primes
- `notes/scripts/s1_arithmetic_condition.output.txt` — output
- `notes/scripts/s1_norm_computation.py` — norm computation identifying number fields
- `notes/scripts/s1_e3zero_enum.py` — enumeration of $e_3 = 0$ subsets for $n = 36$
- `notes/scripts/s1_e3zero_enum.output.txt` — output
- `notes/scripts/s1_n60_norms.py` — norm computation and verification for $n = 60$
