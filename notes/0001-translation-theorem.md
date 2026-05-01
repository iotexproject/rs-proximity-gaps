# Note 0001 — The Translation Theorem

*Working note. 2026-04-20. Draft for Prof. Gong's review.*

## 0. Purpose

Reformulate the Ethereum Foundation Proximity Prize problem so it can be attacked with the Golomb-Gong-Helleseth toolkit. The reformulation turns the prize problem into a question about **low-weight vectors with prescribed DFT values on a cyclic group** — pure Fourier analysis on $\mathbb{Z}/n\mathbb{Z}$.

## 1. Setup (sequence-school conventions)

Let $q$ be a prime power, $\mathbb{F}_q$ a finite field. Fix $n \mid q - 1$ (smooth in FRI applications, e.g. $n = 2^t$ when $q - 1$ has large power-of-2 part) and let $\omega \in \mathbb{F}_q^*$ be a primitive $n$-th root of unity. Set
$$L = \langle \omega \rangle = \{1, \omega, \omega^2, \ldots, \omega^{n-1}\} \subset \mathbb{F}_q^*,$$
and write $\rho = k/n \in (0, 1)$ for the *rate*, with $k$ the RS degree bound.

**Reed-Solomon code.**
$$\mathrm{RS}_k := \left\{\, (p(\omega^0), p(\omega^1), \ldots, p(\omega^{n-1})) : p \in \mathbb{F}_q[X],\ \deg p < k \,\right\} \subset \mathbb{F}_q^L.$$

**DFT on the cyclic group $\mathbb{Z}/n\mathbb{Z}$.** For $f \in \mathbb{F}_q^L$ identified with $(f_0, \ldots, f_{n-1})$,
$$\hat f_j \;=\; \sum_{i=0}^{n-1} f_i\, \omega^{-ij}, \qquad j \in \mathbb{Z}/n\mathbb{Z}.$$

**Weight** $\mathrm{wt}(f) = |\{i : f_i \neq 0\}|$. **Proximity** $\Delta(f, g) = \mathrm{wt}(f - g)/n$.

**List-decoding count.** For $w \in \mathbb{F}_q^L$ and $\delta \in [0, 1)$,
$$L_\delta(w) \;:=\; \# \left\{ c \in \mathrm{RS}_k : \Delta(w, c) \leq \delta \right\}.$$

## 2. The translation theorem

**Lemma 2.1 (RS = truncated Fourier support).** $c \in \mathrm{RS}_k \iff \hat c_j = 0 \text{ for all } j \in \{k, k+1, \ldots, n-1\}.$

*Proof.* If $c_i = p(\omega^i) = \sum_{j'=0}^{k-1} p_{j'} \omega^{ij'}$, then by orthogonality of characters on $\mathbb{Z}/n\mathbb{Z}$,
$$\hat c_j = \sum_i c_i \omega^{-ij} = \sum_{j'=0}^{k-1} p_{j'} \sum_{i=0}^{n-1} \omega^{i(j'-j)} = n \cdot p_j \cdot \mathbf{1}[0 \leq j < k].$$
So $\hat c$ is supported in $[0, k-1]$. Conversely, any $c$ with this Fourier support comes from the polynomial $p(X) = \tfrac{1}{n} \sum_{j < k} \hat c_j X^j$ (working in $\mathbb{F}_q$; $n$ is invertible since $n \mid q-1$ and $\gcd(n, q) = 1$). $\square$

**Theorem 2.2 (Translation theorem).** Let $w \in \mathbb{F}_q^L$ with fixed *syndrome* $s := (\hat w_k, \hat w_{k+1}, \ldots, \hat w_{n-1}) \in \mathbb{F}_q^{n-k}$. Then
$$L_\delta(w) \;=\; \#\left\{\,e \in \mathbb{F}_q^L : \mathrm{wt}(e) \leq \delta n,\ \hat e_j = s_j \text{ for } j = k, \ldots, n-1\,\right\}.$$

*Proof.* Each $c \in \mathrm{RS}_k$ with $\Delta(w,c) \leq \delta$ is in bijection with $e = w - c$ satisfying $\mathrm{wt}(e) \leq \delta n$ and $\hat e_j = \hat w_j - \hat c_j = \hat w_j - 0 = s_j$ for $j \in [k, n-1]$ by Lemma 2.1. $\square$

**Consequence.** *The Proximity Prize problem reduces to:*
> **(Q)** Over $\mathbb{Z}/n\mathbb{Z}$, count the vectors $e \in \mathbb{F}_q^L$ of weight $\leq \delta n$ whose DFT matches a prescribed pattern on a window of size $n - k$. Bound this count uniformly in the pattern, or construct patterns witnessing explosion.

This is a question **purely in Fourier analysis on cyclic groups**. No mention of polynomials, codes, or proofs-of-proximity remains. It is native territory for the sequence/cross-correlation community.

## 3. Sanity calculation A: Unique decoding from Tao's uncertainty

**Tao's uncertainty principle** (*Math. Res. Lett.* 2005). For $n$ prime and any $0 \neq f : \mathbb{Z}/n\mathbb{Z} \to \mathbb{C}$:
$$\mathrm{wt}(f) + |\mathrm{supp}(\hat f)| \geq n + 1.$$

Suppose $e_1 \neq e_2$ both witness $L_\delta(w) \geq 2$. Let $f := e_1 - e_2$. Then $\mathrm{wt}(f) \leq 2\delta n$ (triangle inequality on weights) and $\hat f_j = s_j - s_j = 0$ for $j \in [k, n-1]$, so $|\mathrm{supp}(\hat f)| \leq k$. Tao gives
$$2\delta n + k \geq n + 1 \quad\Longleftrightarrow\quad \delta \geq \tfrac{1 - \rho}{2} + \tfrac{1}{2n}.$$

So for $\delta < (1-\rho)/2$, $L_\delta(w) \leq 1$ — the **Singleton unique-decoding bound**, recovered for free on prime-order cyclic groups. $\checkmark$

## 4. Sanity calculation B: The smooth-$n$ obstruction

Tao's result requires $n$ prime. For smooth $n$ (the FRI case), the replacement bound (Meshulam) is much weaker, and this is structurally why the up-to-capacity conjecture **cannot** hold.

**Example.** Suppose $n = dm$ with $d, m > 1$. Let $H = d \mathbb{Z}/n\mathbb{Z} \leq \mathbb{Z}/n\mathbb{Z}$, a subgroup of size $m$, and let $H^\perp = m \mathbb{Z}/n\mathbb{Z}$, its annihilator, of size $d$. A direct computation of the DFT of the indicator:
$$\widehat{\mathbf{1}_H}_j = \sum_{i \in H} \omega^{-ij} = \begin{cases} m & j \in H^\perp \\ 0 & \text{else.} \end{cases}$$

So $\mathrm{wt}(\mathbf{1}_H) = m$ and $|\mathrm{supp}(\widehat{\mathbf{1}_H})| = d$; sum $= d + m$, minimized at $\approx 2\sqrt n \ll n + 1$. **The uncertainty principle fails dramatically for smooth $n$.**

Take $n = 2^t$ (FRI case): choosing $d = m = 2^{t/2}$ gives a vector of weight $\sqrt n$ with Fourier support of size $\sqrt n$. Such vectors provide the structural raw material for constructing counterexamples to up-to-capacity conjectures, because they allow many low-weight vectors to share most of their Fourier coefficients with each other (consider translates $\mathbf{1}_{H+t}$).

**Task 1 (immediate).** Translate the Crites-Stewart counterexample (*ePrint* 2025/2046) into this Fourier language. Prediction: the disproof vectors are linear combinations / convolutions of subgroup-indicator type objects, and the "failure curve" of the conjecture should be expressible as a subgroup-lattice condition.

## 5. The technical core — where new content must enter

Sections 3 and 4 frame the two extremes. The **prize zone** lies between:
$$\underbrace{\tfrac{1-\rho}{2}}_{\text{unique dec.}} \;<\; \delta \;<\; \underbrace{1 - \rho}_{\text{capacity (disproven)}}, \qquad \text{and specifically } \delta > 1 - \sqrt\rho \text{ (Johnson)}.$$

Between Johnson and capacity, both (a) global uncertainty-principle arguments and (b) subgroup-indicator constructions are too blunt. We need **quantitative Fourier control**.

### 5.1 Fourth-moment attack with partial Gauss sums

Write $A(p, w) := |\{x \in L : p(x) = w(x)\}|$. Using the additive character $\chi$ of $\mathbb{F}_q$,
$$A(p, w) = \frac{n}{q} + \frac{1}{q} \sum_{c \in \mathbb{F}_q^*} \sum_{x \in L} \chi\!\big(c(p(x) - w(x))\big).$$

Markov with fourth moment:
$$L_\delta(w) \leq \frac{\mathbb{E}_p\, A(p, w)^4}{((1-\delta)n)^4} \cdot q^k.$$

Expanding $A(p,w)^4$ into a 4-fold sum and taking expectation over uniform $p$ of degree $< k$, the diagonal ($x_1, \ldots, x_4$ span $\leq k$ distinct values) gives the standard 2nd-moment / Johnson term. The off-diagonal terms reduce to **character sums over $L$ of the form**
$$S(c_1, \ldots, c_4; j_1, \ldots, j_4) \;=\; \sum_{x \in L} \chi\!\left(\sum_{i=1}^4 c_i x^{j_i}\right), \qquad j_i \in \{0, \ldots, k-1\}.$$

**When $L = \mathbb{F}_q^*$**, these are complete character sums bounded by Weil: $|S| \leq (k-1)\sqrt q$. **When $L$ is a proper multiplicative subgroup** (the realistic FRI case, $n \mid q-1$, $n < q-1$), these become *partial* Gauss sums, which admit sharper bounds in the Gong-Helleseth-Schmidt tradition via decomposition into pure Gauss sums and Jacobi sums.

**This is the first technical wedge.** *The BCIKS / Crites-Stewart analyses do not distinguish between $L = \mathbb{F}_q^*$ and $L$ a proper subgroup; they use only generic algebraic-geometric bounds.* The sharper partial-Gauss-sum estimates should translate into strictly better Johnson-beating bounds in the realistic $n < q-1$ regime.

**Task 2.** Expand $\mathbb{E}_p\, A(p,w)^4$ carefully; identify which off-diagonal terms carry the binding constraint. Quote the partial-Gauss-sum bound literature (Shparlinski, Bourgain-Glibichuk-Konyagin, Heath-Brown) to estimate. Target: an explicit Johnson-improving bound of the form $\delta < 1 - \sqrt\rho + \eta(\rho, n/q)$ for a concrete positive $\eta$.

### 5.2 Structured-$w$ attack via Niho / Welch cross-correlation

For $w(x) = \mathrm{Tr}_{\mathbb{F}_{q^m}/\mathbb{F}_q}(\alpha x^d)$ with $d$ a Niho or Welch exponent and $\alpha \in \mathbb{F}_{q^m}^*$, the distribution of $A(p, w)$ for random $p$ is governed by the **cross-correlation distribution of $d$-decimations of m-sequences** — a subject with decades of explicit formulas (Helleseth 1976, Niho 1972, Dobbertin, Katz, Schmidt).

**Conjecture 5.2.1 (working).** For $w$ the trace of a Niho monomial, $L_\delta(w)$ is bounded by $(q / (1-\delta)^c)$ for some explicit constant $c > 2$, *uniformly* for $\delta$ up to a value strictly exceeding $1 - \sqrt\rho$.

If this holds, it gives a "restricted prover" version of the proximity gap: honest arithmetic circuits that only produce monomial-trace witnesses already enjoy soundness beyond Johnson without any conjecture.

**Task 3.** Pick a specific Niho exponent (e.g., $d = 2^{(t+1)/2} + 1$ on $\mathbb{F}_{2^t}$), a specific $n, k$, and compute $L_\delta(w)$ exhaustively for $t \leq 12$. Compare to the Johnson bound and to the generic counterexample growth rate.

### 5.3 MCA from partial-period correlation

Mutual correlated agreement requires a *single* set $D \subset L$ of size $\geq (1-\delta)n$ that serves as the agreement set simultaneously for all members of a family $\{u_1, \ldots, u_m\}$ of received words.

In sequence language: given a family of Fourier-patterns $\{s^{(1)}, \ldots, s^{(m)}\}$ on the window $[k, n-1]$, does there exist a common position-subset $D$, $|D| \geq (1-\delta)n$, such that *every* $s^{(\ell)}$ can be realized by a function supported on $D$?

This is a **partial-period common-correlation** question and, to my knowledge, has not been systematically studied in the sequence literature — even though the machinery is available. MCA up-to-Johnson is the most valuable sub-target in the prize, and the sequence community has a probable monopoly on the right tools.

**Task 4.** Formalize the "common $D$" condition as a simultaneous partial-Gauss-sum constraint. Determine whether Schmidt-style partial-correlation bounds immediately give MCA in some sub-Johnson regime as a trivial consequence.

## 6. What we need from Prof. Gong (concretely)

1. **Reality check on §5.1's partial-Gauss-sum plan.** The right citation chain for the sharpest known bounds on $\sum_{x \in L} \chi(f(x))$ when $L$ is a proper multiplicative subgroup of $\mathbb{F}_q^*$ and $f$ is low-degree. (I suspect the Shparlinski / Bourgain papers are the correct entry, but Gong's archive of Helleseth-school work will have tighter unpublished numerics.)

2. **Niho exponent selection for §5.2.** Which specific decimation exponents $d$ have the sharpest cross-correlation distributions that would translate into the cleanest $L_\delta(w)$ bounds?

3. **Pipeline to Helleseth / Katz / Schmidt.** If §5.1 gives a non-trivial Johnson improvement, we need a co-author from the cross-correlation school to ratify the partial-Gauss-sum estimates — both for correctness and for credibility with the prize judges.

## 7. Risks / honest caveats

- **Characteristic transfer.** The sequence-school toolkit is sharpest in characteristic 2. FRI on Binius is characteristic 2, but the broader zkVM ecosystem has migrated to Mersenne / Goldilocks / BN254 fields. Any bound we prove should be stated characteristic-agnostically from the start.
- **MCA may require genuinely new tools.** Task 4 is speculative. If classical partial-period bounds turn out to be too weak, we may need to develop "MCA-specific" correlation inequalities from scratch.
- **Competitors.** Crites-Stewart (Web3 Foundation) are already attacking from the disproof side; BCIKS continue from the positive side. First-mover advantage favors speed.

---

## Next action items

- [ ] **Task 1**: Translate Crites-Stewart counterexample into Fourier-on-$\mathbb{Z}/n\mathbb{Z}$ language. *(Target: 1 week.)*
- [ ] **Task 2**: Execute the 4th-moment expansion of §5.1 with partial-Gauss-sum bounds. *(Target: 3 weeks, first-pass theorem.)*
- [ ] **Task 3**: Small-field exhaustive computation of $L_\delta(w)$ for Niho-monomial $w$. *(Target: 2 weeks.)*
- [ ] **Task 4**: Formalize MCA partial-period framing. *(Target: 2 weeks sketch, longer for real bound.)*
- [ ] **Meeting with Prof. Gong**: walk through §1–§5.1 and §6. *(Target: within 2 weeks.)*
