# Note 0006 — Bridge Note: Sequence-Theory Tools for the RS Proximity Gap

**Date**: 2026-04-20  
**Purpose**: Self-contained summary for Prof. Gong (and sequence-school collaborators). Assumes familiarity with finite fields, character sums, and cross-correlation, but NOT with FRI/STARK/IOP.

---

## 1. The problem (in one paragraph)

The Ethereum Foundation posted a [$1M prize](https://blog.ethereum.org/2026/01/26/proximity-prize) for progress on **Reed-Solomon proximity gap conjectures**. These control the soundness of STARK proof systems (the backbone of Ethereum's L2 scaling). The "up-to-capacity" version was already disproven (Nov 2025), but the **intermediate zone** (between the Johnson bound and capacity) remains wide open. We reformulated the problem as a pure Fourier-analysis question on cyclic groups, and found that the key objects are **norms of character sums over multiplicative subgroups** — exactly the Golomb-Gong-Helleseth toolkit.

## 2. Setup

- $\mathbb{F}_p$: prime field, $p \equiv 1 \pmod{n}$
- $L = \langle\omega\rangle \subset \mathbb{F}_p^*$: multiplicative subgroup of order $n$
- $\mathrm{RS}_k$: Reed-Solomon code on $L$ with degree bound $k$, rate $\rho = k/n$
- $\delta$: proximity parameter. A word $w \in \mathbb{F}_p^n$ is $\delta$-close to RS if $\exists h \in \mathrm{RS}_k$ agreeing with $w$ on $\geq (1-\delta)n$ points of $L$.

**Proximity gap conjecture** (informal): If $\delta$ is in the "Johnson-to-capacity" zone, the fraction of RS codewords $\delta$-close to a random word $w$ drops sharply. The precise threshold and rate of decay are unknown.

## 3. Our DFT reformulation (Note 0001)

Identify $\mathbb{F}_p^L$ with functions on $\mathbb{Z}/n\mathbb{Z}$ via $f \leftrightarrow (f(\omega^0), f(\omega^1), \ldots, f(\omega^{n-1}))$. The DFT on $\mathbb{Z}/n\mathbb{Z}$ is:

$$\hat{f}_j = \sum_{i=0}^{n-1} f_i \omega^{-ij}, \quad j \in \mathbb{Z}/n\mathbb{Z}.$$

Then $\mathrm{RS}_k = \{c : \hat{c}_j = 0 \text{ for } j \in [k, n-1]\}$ — codewords have Fourier support in $[0, k-1]$.

**Translation Theorem**: The list-decoding count equals

$$L_\delta(w) = \#\{e \in \mathbb{F}_p^n : \mathrm{wt}(e) \leq \delta n, \; \hat{e}_j = \hat{w}_j \text{ for } j \in [k, n-1]\}.$$

**Result**: The RS proximity gap is equivalent to counting **low-weight vectors on $\mathbb{Z}/n\mathbb{Z}$ with prescribed Fourier values on a window of length $n - k$.**

## 4. The Crites-Stewart construction in this framework (Note 0002)

CS uses $f = X^{rm}$, $g = X^{(r-1)m}$ where $n = sm$. Both monomials have single-spike DFTs. The "agreement polynomial" (whose roots form the agreement set $S$) is:

$$X^{rm} + \lambda X^{(r-1)m} - h(X) = 0, \quad \deg h < k = (r-2)m.$$

For $k = 2$: the polynomial is $x^6 + \lambda x^4 - h_1 x - h_0$. By Vieta, the 6-element root set $S = \{\alpha_1, \ldots, \alpha_6\} \subset L$ satisfies:

$$e_1(S) = 0, \quad e_3(S) = 0, \quad e_4(S) = 0$$

where $e_j$ are elementary symmetric polynomials.

## 5. The norm mechanism (Note 0005 — main new result)

### 5.1 Setup

For $S = \{i_1, \ldots, i_6\} \subset \mathbb{Z}/n\mathbb{Z}$, define the **algebraic character sum**:

$$\alpha_j(S) = e_j(\zeta_n^{i_1}, \ldots, \zeta_n^{i_6}) \in \mathbb{Z}[\zeta_n]$$

where $\zeta_n = e^{2\pi i / n}$ is the $n$-th root of unity in $\mathbb{C}$.

### 5.2 Key observation

$S$ is a valid CS witness at prime $p$ (with embedding $\zeta_n \to \omega \in \mathbb{F}_p$) **only if** $\alpha_j(S) \equiv 0$ modulo a prime ideal above $p$ in $\mathbb{Z}[\zeta_n]$.

In particular: $p \mid \mathrm{Norm}_{\mathbb{Q}(\zeta_n)/\mathbb{Q}}(\alpha_j(S))$.

### 5.3 The finiteness theorem

**Theorem**: *For the CS construction with parameters $(n, m, r)$, the set of primes $p \equiv 1 \pmod{n}$ admitting non-subgroup-aligned witnesses is finite, bounded by $p \leq (rm)^{\varphi(n)}$.*

*Proof*: For any 6-element $S \subset \mathbb{Z}/n\mathbb{Z}$, $|\alpha_1(S)| \leq 6$ (triangle inequality for sums of roots of unity). Therefore $|\mathrm{Norm}(\alpha_1)| \leq 6^{\varphi(n)}$, and $p \mid \mathrm{Norm}(\alpha_1)$ implies $p \leq 6^{\varphi(n)}$.

A "subgroup-aligned" $S$ (union of cosets of a subgroup of $\mathbb{Z}/n\mathbb{Z}$) has $\alpha_1(S) = 0$ **identically** in $\mathbb{Z}[\zeta_n]$ (character orthogonality). So subgroup-aligned witnesses exist at ALL primes. Non-aligned witnesses require $\alpha_1 \neq 0$ but $\mathrm{Norm}(\alpha_1)$ divisible by $p$ — constraining $p$ to a finite set. $\square$

### 5.4 Empirical confirmation

| $n$ | $\varphi(n)$ | Non-alignment primes (complete for $n=36$) |
|-----|-------------|---------------------------------------------|
| 36 | 12 | $\{37, 181\}$ |
| 48 | 16 | $\{97\}$ (only 1 out of 14 tested) |
| 60 | 16 | $\{61, 181, 241, 601, \ldots\}$ |

At every non-alignment prime: $\mathrm{Norm}(\alpha_1) = p$ and $\mathrm{Norm}(\alpha_4) = p$ (first power). The non-aligned witnesses form free orbits under cyclic shift, one orbit per "algebraic point."

### 5.5 Connection to character sums

The norm $\mathrm{Norm}(\alpha_1(S))$ is:

$$\mathrm{Norm}(\alpha_1) = \prod_{k \in (\mathbb{Z}/n\mathbb{Z})^*} \left(\sum_{j \in S} \zeta_n^{kj}\right)$$

This is a **product of character-sum values** — the product runs over all primitive $n$-th roots of unity, and each factor is a partial exponential sum restricted to the index set $S$.

**This is exactly the kind of object studied in the Golomb-Gong-Helleseth tradition** (cross-correlation of $m$-sequences, partial period auto-correlation, etc.).

## 6. What we need from the sequence community

### Question 1: Norm bounds

For a $t$-element subset $S \subset \mathbb{Z}/n\mathbb{Z}$ (not a subgroup-coset union), what are the sharpest lower bounds on

$$\left|\prod_{k \in (\mathbb{Z}/n\mathbb{Z})^*} \sum_{j \in S} \zeta_n^{kj}\right|?$$

If this product is always $\geq p_0(n,t)$ for some explicit function, then non-alignment is impossible for $p > p_0$.

The Welch bound, Sidelnikov bound, and cross-correlation distribution results all give information about individual factors $|\sum \zeta^{kj}|$. The PRODUCT over all $k$ is less studied but may be accessible.

### Question 2: Generalization beyond CS

For a **general** received word $w$ (not CS), the agreement polynomial is $w(x) - h(x)$ with arbitrary degree. The Vieta conditions change: we no longer have $e_3 = e_4 = 0$ automatically. The norm mechanism still applies to each $e_j$, but:

- More conditions → harder to satisfy → potentially STRONGER proximity gap
- Or: fewer structural constraints → more freedom → weaker proximity gap

**Empirically**: structured non-CS words ($w = x^a + \lambda x^b$ for various $a, b$) produce non-aligned witnesses at primes where CS does not. This means CS is NOT the worst case. Understanding the true worst case requires **bounding the maximum over all $w$ of the list-decoding count** — a character-sum optimization problem.

### Question 3: Does the Helleseth school have results on cross-correlation distributions for arbitrary exponent pairs?

The CS construction uses the specific pair $(a, b) = (rm, (r-1)m)$. The general case involves arbitrary monomial pairs. The cross-correlation distribution $C_d(\tau) = \sum_{x \in L} \chi(x^d + x^{d'})$ for varying $d, d'$ is the natural object. Helleseth 1976, Niho 1972, and the Kasami-Welch-Niho classification give complete answers for specific $(d, d')$. Is there a general bound that works for all $(d, d')$?

### Question 4: Characteristic 2

FRI (and Binius) use $\mathbb{F}_{2^t}$. The multiplicative group is cyclic of order $2^t - 1$. Does the norm mechanism survive? In char 2, $\mathbb{Z}[\zeta_n]$ with $n | 2^t - 1$ behaves differently (no $\zeta_n \in \mathbb{Z}$; must work in $\mathbb{Z}[\zeta_n]$ with $\gcd(n, 2) = 1$, which is fine since $n$ is odd in this case).

## 7. What's at stake

The proximity gap controls the **soundness error** of STARK-based proof systems. A tight bound in the Johnson-to-capacity zone would:
- Improve the efficiency of Ethereum's zkEVM rollups
- Reduce proof sizes in recursive SNARKs (WHIR, STIR)
- Settle a fundamental question in algebraic coding theory

The sequence-school tools (character sums, cross-correlation, partial Gauss sums) have never been applied to this problem. The DFT reformulation makes the connection precise and exploitable.

## 8. Concrete ask

1. **Sanity check**: Is the norm-product $\prod_k \sum_{j \in S} \zeta^{kj}$ a known object in the sequence/correlation literature? Does it have a name?
2. **Lower bound literature**: Any result bounding $|\prod_k \sum_{j \in S} \zeta^{kj}|$ away from zero for non-coset $S$ would directly strengthen our theorem.
3. **Collaboration**: If this looks promising, can we bring in Helleseth / Tang / Katz for the character-sum estimates needed for the general case?

---

## Appendix: File map

```
notes/
  0001-translation-theorem.md   — DFT reformulation (proved)
  0002-cs-translation.md        — CS in DFT language, Conjecture 4
  0003-state-of-investigation.md — strategic overview  
  0004-sweep-results.md          — n=36 transition, Conjecture 4'
  0005-s1-proper-subgroup.md     — THIS SESSION: proper subgroups, norm theorem
  0006-bridge-for-gong.md        — THIS NOTE (summary for Gong)
  scripts/                       — all computation scripts + saved output
```
