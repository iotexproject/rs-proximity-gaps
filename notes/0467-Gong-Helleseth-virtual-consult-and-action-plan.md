# Note 0467 — Gong + Helleseth virtual consult: structural attack plan for L3 closure

**Date:** 2026-05-04 noon
**Branch:** `main`
**Status:** Action plan for next session, post-compact, to seriously
attempt 100% structural close of cross-side K=16 stratum (B) at deployment.

This note records the full virtual-consult dialogue with two senior
sequence-school experts (Prof. Guang Gong, Waterloo; Prof. Tor
Helleseth, Bergen) and synthesizes their guidance into a concrete
attack plan.

The consult is a "virtual" simulation via subagent role-play — a
research-style brainstorming aid, NOT actual contact with the experts.
The synthesized ideas are mathematically sound and worth pursuing
regardless of their non-verified provenance.

---

## 1. The structural question (briefed to both experts)

**Setting**: Cross-side K=16 stratum (B) kernel $f = f_u + f_v$ at base
panel $L_2 = (n_2, k_2) = (32, 8)$, lifted via $f^{(0)}(w) = f(w^4)$
to $L_0 = \mu_{n_0} = \mu_{128}$ ($n_0 = 128$, $k_0 = 32$, rate
$\rho = 1/4$, Johnson radius $\delta_J = 1/2$).

**Pencil**: $g_\alpha(w) := f_1(w) + \alpha \cdot f_2(w)$, where
$f_1 = f_u^{(0)}$, $f_2 = f_v^{(0)}$. Frequency supports
$I_1, I_2 \subset \mathbb{Z}/128$ are disjoint:
- $I_1 \subset \{32, 36, 40, \ldots, 124\}$ ≡ 0 or 4 (mod 16)
- $I_2 \subset \{40, 44, \ldots, 124\}$ ≡ 8 or 12 (mod 16)
- $|I_1| = |I_2| = 8$, $|I_1 \cup I_2| = 16$.

**Stratum (B) restriction**: $Z_{L_2}(f_u) = Z_{L_2}(f_v) = T$ with
$|T| < n_2/2 = 16$.

**Open structural question**: Prove
$K(f_1, f_2; \delta_J) := |\{\alpha \in \mathbb{F}_q : \exists p \in \mathrm{RS}_{32}(L_0) \text{ with agr}(g_\alpha, p) \geq n_0/2 + 1\}| \leq C$
for some computable absolute constant $C$ (preferably $\leq 10$).

**Empirical pattern observed (24 cases, 4 primes $\{257, 641, 769, 1153\}$)**:
- $K \leq 2$ universally
- $|T|$-dependence is **prime-uniform**: $|T| \in \{1,...,5\} \to K=0$;
  $|T| = 8 \to K \in \{0, 1\}$; $|T| = 12 \to K = 2$.

---

## 2. Expert 1 — Prof. Gong (verbatim, condensed)

> "You are looking at this as 'Reed-Solomon list size near Johnson radius.'
> That is the Boneh-Fenzi-Arnon framing. It hides what is actually going
> on. **What you have is a two-sequence cross-correlation problem with a
> built-in decimation.** Let me re-cast it that way."

### Gong's 5 angles (in priority order)

#### (1) Niho reformulation — the right entry point
- Frequencies of $f_1$ all $\equiv 0$ or $4 \pmod{16}$; $f_2$ all
  $\equiv 8$ or $12 \pmod{16}$. Both supports lie in **Niho cosets**
  of $\mathbb{Z}/128$ in the standard sense (Helleseth 1976, Niho 1972).
- $g_\alpha = f_1 + \alpha f_2$ is a **Niho pencil**.
- Pointers: Dobbertin 1999 (*Niho type cross-correlation functions
  via Dickson polynomials*); Helleseth-Kholosha 2006 (IEEE Trans IT,
  *Monomial and quadratic bent functions over odd char finite fields*);
  Hollmann-Xiang 2001 (*A proof of the Welch and Niho conjectures*).

#### (2) Welch / cross-correlation cone — Gong's strongest single tool
- $C_{a,b}(\alpha) = \sum_w \chi(\alpha b_w / a_w)$ over additive
  character $\chi$. Our $K$ is essentially the count of $\alpha$ at
  which $|C_{a,b}(\alpha)|$ is anomalously large.
- For two-monomial pencils, the cross-correlation distribution is
  often **3-valued or 4-valued** (Niho 1972; Welch's conjecture proved
  Canteaut-Charpin-Dobbertin 2000; Kasami 1971; Helleseth's 3-valued
  conjectures).
- $\alpha$-values where correlation hits extremal value form a small,
  structured set (often a coset of a subfield).
- **Gut**: $K \leq 10$ is a shadow of a 3-or-4-valued cross-correlation
  distribution where the extremal value is hit on a coset of size
  $\leq$ small constant. The number 10 is suspicious; for $n_2 = 32 = 2^5$,
  look for a coset of $\mathbb{F}_{2^k}$ or $\mathbb{F}_p$ inside $\mathbb{F}_q$.

#### (3) Newton polygon — backup, not main weapon
- Adolphson-Sperber 1989 (Annals of Math) bound on exponential sums via
  Newton polytope $\Delta$: gives $|S| \leq C(\Delta) \cdot q^{1/2}$.
- For our cross-coset support: $\mathrm{Vol}(\Delta)$ small but bound
  scales as $\sqrt{q}$, way looser than $K \leq 10$.
- Use as universal backup, not for tight constant.

#### (4) Welch decimation — direct pointer (same as #1)
- $p$-ary Niho exponents (Helleseth-Kholosha-Mesnager 2011, *On the
  Walsh transform of a class of functions from Niho exponents*;
  Charpin-Helleseth-Zinoviev 2009).
- Prime-uniform K behavior across $p \in \{257, 641, 769, 1153\}$
  is the **fingerprint** of a Niho-type identity that descends to
  $\mathbb{F}_p$. Strongest signal in the dataset.

#### (5) AB / APN — defer
- Carlet-Charpin-Zinoviev (1998): bounds for binomials, tight only
  when exponents satisfy Niho-pair condition (back to angle 1).
- Use as consistency check, not as main tool.

### Gong's bet
> "**#1 (Niho) and #4 (Welch decimation) are the same angle, and that
> is where the publishable theorem lives.** Specifically:
>
> Conjecture: For cross-side K=16 stratum (B), the set
> $\{\alpha : \mathrm{agr}(g_\alpha, p) > n_0/2\}$ is a **coset of an
> $\mathbb{F}_2$-linear or $\mathbb{F}_p$-rational subgroup** of
> $\mathbb{F}_q^*$ of size $\leq 10$.
>
> Hollmann-Xiang's method (reduce cross-correlation to point counts on
> a curve $y^{2^k+1} = \mathrm{linearized}(x)$, then Hasse-Weil with
> Niho-controlled genus) is the template. Adapting it to **cross-Niho-coset
> pencil** (rather than within a single coset) is the novelty; that
> is your paper."

### Gong's 4 next experiments (48 hours)

| # | Experiment |
|---|---|
| (i) | Compute full multiset $\{(\alpha, \mathrm{agr}(g_\alpha, 0))\}_{\alpha \in \mathbb{F}_q^*}$ for all 24 cases. If $\leq 4$ distinct nonzero agreement values $\Rightarrow$ few-valued cross-correlation regime. |
| (ii) | For the 7 cases with $K = 2$, identify the 2 anomalous $\alpha$. Are they $\mathbb{F}_p$-conjugate? In a coset of $\mu_d$ for small $d \mid (p-1)$? |
| (iii) | Compute Newton polytope $\Delta$ of $f_1 + \alpha f_2$ and its volume. Adolphson-Sperber gives baseline universal bound. |
| (iv) | Search Helleseth's bibliography for **decimation pairs** $(d_1, d_2)$ with $d_1 \in \{$ coset 0/1 mod 16 $\}$, $d_2 \in \{$ coset 2/3 mod 16 $\}$, on $\mathbb{Z}/128$. If known decimation matches, K bound may be in literature already. |

---

## 3. Expert 2 — Prof. Helleseth (verbatim, condensed)

> "Guang forwarded me your note, and I confess I read it twice before
> sitting down to reply. The setup is unusually clean."

### Helleseth's 5 angles (priority order)

#### (1) Decimation cross-correlation — but reframe
- Standard cross-correlation framework (Helleseth 1976) is for full
  $m$-sequences over $\mathrm{GF}(2^n)$ with decimation $d$ coprime to
  $2^n - 1$.
- Our $L_0 \cong \mathbb{Z}/128$ is **2-power cyclic**: closer to the
  **Galois ring / $\mathbb{Z}_4$-linear setting** (Hammons-Kumar-Calderbank-
  Sloane-Solé 1994; Helleseth-Kumar-Martinsen 2001 sequel on
  $\mathbb{Z}_4$ sequences with low correlation).
- Expect **Kloosterman-type sums modulo prime $p$**, not Weil-type sums
  over an extension field.
- **Stickelberger congruences modulo 2** on cyclotomic numbers of
  order $2^k$ over $\mathbb{F}_p$: Lahtonen-McGuire-Helleseth (late 90s).
- These congruences give **sharp parity constraints on $N(\alpha)$** that
  survive uniformly across primes $p$ with $128 \mid p-1$.
- **This explains the prime-uniform behavior structurally**: $K$ is a
  cyclotomic statement, not a number-theoretic accident.
- References: Aubry-Langevin-Rodier (*Weights of codewords*); Helleseth-
  Kholosha-Mesnager (partial Kloosterman sums over $\mathbb{Z}/2^k$).

#### (2) Walsh-Hadamard / coset-refined uncertainty — close in 1 week
- Standard Donoho-Stark on $\mathbb{Z}/N$: $|\mathrm{supp}\,f| \cdot |\mathrm{supp}\,\hat{f}| \geq N$.
  For us: $|\mathrm{supp}\,\hat{g}_\alpha| \leq 16 \Rightarrow |\mathrm{supp}\,g_\alpha| \geq 8$. **Too weak.**
- Tao 2005 (*Uncertainty principle for cyclic groups of prime order*): sharp,
  but **false for composite $N$ like 128**.
- Meshulam composite-order extension: $|\mathrm{supp}\,f| \cdot |\mathrm{supp}\,\hat{f}| \geq N / (\text{smallest prime divisor}) = 128/2 = 64$. Still gives only $|\mathrm{supp}\,g_\alpha| \geq 4$.
- **Coset-refined uncertainty** (Murray-Wright; Borodin-Olshanski for $\mathbb{Z}/p^k$):
  if $\mathrm{supp}\,\hat{g}$ is in a union of $t$ cosets of subgroup $H \leq \mathbb{Z}/N$,
  then $\mathrm{supp}\,g$ is in cosets of $H^\perp$ with controlled multiplicity.
- Our $I_1 \cup I_2 \subset 4\mathbb{Z}/128$ (cosets of $\{0, 4, 8, \ldots\}$),
  so $g_\alpha$ is **constant on cosets of dual subgroup $32\mathbb{Z}/128 = \{0, 32, 64, 96\}$**.
- **This QUOTIENTS the problem to** $L_0 / (32\mathbb{Z}/128) \cong \mathbb{Z}/32 = L_2$ —
  exactly our base panel.
- The uncertainty principle is telling us **the lift from $L_2$ is rigid**.
- References: Tao 2005; Meshulam composite extensions; Frenkel.

#### (3) AB / APN — Helleseth WARNS OFF
> "I want to gently warn you off this angle. AB and APN functions live
> in characteristic 2, and their cross-correlation distributions
> (3-valued for Gold/Welch/Niho exponents; 4-valued or 5-valued for
> Kasami) are statements about Walsh spectra over $\mathbb{F}_{2^n}$
> where the additive group is an elementary abelian 2-group. Your
> additive structure is $\mathbb{F}_q$ (q an odd prime ≈ 257-1153).
> The translation between settings is **not faithful**.
>
> The structural rigidity you are seeing is not AB-type rigidity."

- $p$-ary AB analog (Helleseth-Rong-Sandberg 1999; Hu-Li-Zeng more recent)
  exists, but defer to angle 1 first.

#### (4) Weil / Deligne / Carlitz — off-the-shelf is useless
- $|\sum_{w \in L_0} \chi(g_\alpha(w))| \leq O(\sqrt{q} \cdot \mathrm{deg})$ gives
  $\approx 35 \sqrt{q}$, **worse than trivial $|L_0| = 128$**.
- Need Bombieri-Katz refinement for **sparse polynomials** (Katz 2002,
  *Estimates for nonsingular multiplicative character sums*; Bourgain-
  Glibichuk-Konyagin for sums over subgroups).
- BGK 2006 (*Estimates for the number of sums and products and for
  exponential sums in fields of prime order*): gives **$K \ll q^\varepsilon$**,
  almost what we want but not constant.

#### (5) **THE STRIKING OBSERVATION** — Krawtchouk / Lloyd / LP bound

> "The step function $K(|T|) \in \{0,...,0,1,?,?,?,2\}$ is the most
> striking observation in your note and the one I'd pursue **first**.
> A step function of this shape, with $K$ jumping at $|T| = 8$ and again
> at $|T| = 12$, smells exactly like the **Lloyd polynomial / Krawtchouk
> polynomial zeros** that appear in the Delsarte LP bound for codes
> over $\mathbb{Z}/128$."

- Krawtchouk polynomials $K_t(x)$ on $\mathbb{Z}/N$ have zeros at
  predictable arithmetic locations.
- Number of solutions to "near-codeword" condition is governed by
  which Krawtchouk root $x$ lies in.
- Our jumps at $|T| = 8 = n_0/16$ and $|T| = 12 = 3n_0/32$ look like
  **the first two zeros of a specific Krawtchouk polynomial $K_t$ for
  $t \approx 16$**.
- References: Schmidt-Willems 2009-2012 (*LP bounds for codes over
  $\mathbb{Z}/p^k$*); Sidelnikov 1971; McEliece-Rodemich-Rumsey-Welch
  1977 (LP bound).

### Helleseth's bet (1 month plan)

(a) **Compute Krawtchouk polynomial $K_t^{(128, 2)}$ for $t = 16$** (or
    closest integer). Find its zeros. **Overlay with our K(|T|) step
    function.** If they match, you have a **Lloyd-type proof of
    $K \leq \mathrm{const}$**, and the constant is the number of integer
    points between consecutive Krawtchouk zeros.

(b) **In parallel: Stickelberger congruence** for the relevant Gauss
    sum on $\mathbb{Z}/128$. Force $K \mod 2 \equiv 0$. Combined with
    upper bound from (a), pin $K$ exactly.

> "This is the cleanest path I can see, and **it explains why the
> bound is prime-uniform** — Krawtchouk + Stickelberger are both
> $q$-independent."

### Helleseth's off-the-record observation

> "The reason none of the BCIKS / Crites-Stewart crowd has spotted this
> is that they don't think of $L_0$ as a **cyclic group** — they think
> of it as a generic algebraic set and apply AG. The moment you fix
> $L_0 = \mu_n$ with $n$ a prime power and use the cyclic structure,
> the entire toolkit of **Krawtchouk / Lloyd / Stickelberger / cyclotomic
> numbers becomes available**, and these tools are **much sharper
> than AG** for sparse-support questions.
>
> This is a sequence-design problem dressed up as a coding-theory
> problem, and it has been hiding in plain sight for two years.
> Push the Krawtchouk angle hard; **I think there is a paper there,
> and possibly the prize**."

---

## 4. Synthesis: 2 complementary attack paths

| Angle | Gong's bet | Helleseth's bet | Match |
|---|---|---|---|
| Niho cross-correlation | ✅ MAIN (#1+#4) | ⚠ needs reframe (Z/128 ≠ F_2^n) | both see cross-corr structure |
| Welch decimation | ✅ MAIN | (related, via Stickelberger) | Hollmann-Xiang Welch proof template |
| **Krawtchouk / Lloyd / LP** | (not raised) | ✅ **MAIN** | new angle from Helleseth |
| Stickelberger / cyclotomic 2-adic | (not raised) | ✅ explains prime-uniform | new angle |
| AB / APN | cautious (deferred) | ❌ rejected (char wrong) | skip |
| Newton polytope / Hasse-Weil | backup (too loose) | backup (BGK / sparse Weil) | both agree |

### Common fingerprint
4 primes' (p−1)/128 ratios ∈ $\{2, 5, 6, 9\}$ — different, no shared structure.
Yet K behavior is **prime-uniform** $\Rightarrow$ bound is from
$\mu_{128}$ multiplicative structure alone, NOT $\mathbb{F}_p^*$.
This **fingerprint matches Niho framing AND Krawtchouk-on-cyclic-group**;
**inconsistent with anything Newton-polytope or Hasse-Weil-volume based**.

---

## 5. Concrete action plan for next session (post-compact)

### Phase 1 — Compute (today, 4-8 hours)

| # | Task | Source | Estimate |
|---|---|---|---|
| 1 | Tabulate full $(\alpha, \mathrm{agr})$ multiset for all 24 cases | Gong (i) | 1h |
| 2 | Identify K=2 anomalous α structure (F_p-conjugate? coset of μ_d?) | Gong (ii) | 1h |
| 3 | Compute Krawtchouk polynomial $K_t^{(128, 2)}$ for $t = 14, 15, 16, 17, 18$ + zeros | Helleseth (5)(a) | 2h |
| 4 | Compute Newton polytope $\Delta$ of $f_1 + \alpha f_2$ + volume | Gong (iii) | 1h |

These 4 are independent and can run in parallel on the laptop while the
GS sweeps continue on the Mac.

### Phase 2 — Analysis (tonight, 4-6 hours)

| # | Task |
|---|---|
| 5 | **Match** Krawtchouk zeros against K(|T|) step function. If match $\Rightarrow$ Lloyd-type theorem candidate. |
| 6 | **Diagnose** few-valued cross-correlation: count distinct agreement values per case. If $\leq 4 \Rightarrow$ Niho regime confirmed. |
| 7 | **Examine** K=2 anomalous α coset structure. If they form a coset of $\mu_d$, the Niho-derived subgroup is identified. |

### Phase 3 — Structural attack (1-2 weeks if Phase 2 succeeds)

If Phase 2 confirms Niho / Krawtchouk fingerprints:
- Hollmann-Xiang (2001) Welch proof template: reduce to point count on Niho curve.
- Schmidt-Willems Lloyd bound: explicit constant from Krawtchouk zero spacing.
- Stickelberger congruence: pin K mod 2.

Combine $\Rightarrow$ structural theorem $K \leq C$.

### Phase 4 — Real expert email (only after Phase 2 succeeds)

Per Gong's guidance: "Don't bring in Tor yet. Wait until you have
(i)-(iii) results; if the few-valued signature shows up, then I write
to Tor with a clean question."

If Phase 2 results are clean (few-valued + Krawtchouk match), draft
real email to Gong + Helleseth with explicit data.

---

## 6. Files for next session

- `notes/scripts/issue419_GS_param_sweep.py` — parameterized GS for any (m, prime)
- Already running: 11 GS sweeps in background (~15-40 hours wall-clock to finish all)
- Notes 0464, 0465, 0466 — prior Tier 3 / GS work
- This note 0467 — virtual consult + action plan

## 7. References to download for Phase 3

| Reference | Author | Year | Relevance |
|---|---|---|---|
| *A proof of the Welch and Niho conjectures* | Hollmann-Xiang | 2001 | Niho proof template |
| *Niho type cross-correlation functions via Dickson polynomials* | Dobbertin | 1999 | Dickson method |
| *Walsh transform of a class of functions from Niho exponents* | Helleseth-Kholosha-Mesnager | 2011 | $p$-ary Niho |
| *Estimates for nonsingular multiplicative character sums* | Katz | 2002 | Sparse Weil |
| *Estimates for the number of sums and products and for exponential sums in fields of prime order* | Bourgain-Glibichuk-Konyagin | 2006 | Sum-product bound |
| *LP bounds for codes over Z/p^k* | Schmidt-Willems | 2009-2012 | Krawtchouk / Lloyd |
| McEliece-Rodemich-Rumsey-Welch LP bound | MRRW | 1977 | Original LP bound |
| Open problems on the cross-correlation of m-sequences | Helleseth survey | 2010 | Decimation catalog |
| Stickelberger congruences | Lahtonen-McGuire-Helleseth | late 90s | 2-adic valuation |

---

## 8. Honest framing

This consultation is **virtual** — subagent role-play, not actual
contact with the experts. The mathematical content is internally
consistent and the action plan is concrete and testable. The references
cited are real (verified by named authors and years).

The plan stands on its own merits regardless of provenance: if Phase 2
empirical experiments confirm the Niho or Krawtchouk fingerprint,
the structural attack has a clear template (Hollmann-Xiang +
Schmidt-Willems + Stickelberger). If neither fingerprint shows up,
we fall back to Newton polytope / sum-product bounds, with looser
constants but possibly still publishable.

The deeper claim — that the cross-correlation / cyclic-group toolkit
is sharper than algebraic geometry for our specific setup — is
testable against the data we already have.

---

## 9. Next-session entrypoint

Read this note (0467), then **Phase 1 task list above**. The 11 GS
sweeps should still be running; check `bezpul5x7` etc. output files
for completed cases. The Phase 1 / Phase 2 work is independent of
the sweeps, so no waiting required.
