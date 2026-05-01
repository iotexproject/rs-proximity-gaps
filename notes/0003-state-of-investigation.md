# Note 0003 — State of Investigation

*2026-04-20. A comprehensive status document: where we are, what we've tried, what's running, what I believe, and what could still break the program.*

---

## Part I — The strategic picture

### I.1 The prize is not what it looks like at first glance

The EF Proximity Prize is framed as "prove or disprove Reed-Solomon proximity gaps conjectures." But the up-to-capacity version was **already disproven** by Crites-Stewart, BGHKS, and Diamond-Gruen in Nov 2025 — *before* the prize announcement (Jan 26, 2026). So the prize money is not riding on the headline conjecture.

What remains:
1. **Locate the exact boundary** in the $(\delta, \rho)$ plane between regimes where proximity gap holds and fails.
2. **Upgrade MCA** (mutual correlated agreement) from its current "plausible" status to a theorem, in some sub-capacity regime — this is the part WHIR and recursive hash-based SNARKs actually depend on.
3. **Improve soundness constants** in the proven Johnson regime, which directly translates to proof size in zkVMs.

The survey paper ePrint 2026/680 (Arnon-Boneh-Fenzi) phrases this as four problem families: list-decoding bounds, proximity gaps, correlated agreement, mutual correlated agreement.

### I.2 Our angle: sequence-school tools

The prize judges (Boneh/Fenzi/Arnon) are all succinct-proof / IOP community. The recent results (BCIKS, Crites-Stewart, BGHKS) are proven with **generic algebraic-geometric machinery** that does not exploit specific structural features of the evaluation domain $L$.

But in every practical protocol (FRI, STIR, WHIR), $L$ is a **multiplicative subgroup of $\mathbb{F}_q^*$** (or an affine coset), typically of smooth order $2^t$. This is exactly the setting where **sequence theory** lives — Golomb-Gong-Helleseth tools for character sums, cross-correlation distributions, Welch / Niho / Kasami exponents, partial Gauss sums.

Hypothesis: the open zone between Johnson and capacity has an **arithmetic-structural** description in terms of the subgroup lattice of $L$. Generic AG tools can't see it; sequence-school tools can.

---

## Part II — What we've built

### II.1 The translation theorem (Note 0001)

For $L = \langle\omega\rangle \subset \mathbb{F}_q^*$ of order $n$, viewing $\mathbb{F}_q^L$ as functions on $\mathbb{Z}/n\mathbb{Z}$ via the DFT:

$$\mathrm{RS}_k = \{c : \hat c_j = 0 \text{ for } j \in [k, n-1]\}.$$

The list-decoding count equals:
$$L_\delta(w) = \#\{e : \mathrm{wt}(e) \leq \delta n, \ \hat e_j = \hat w_j \text{ for } j \in [k, n-1]\}.$$

**Corollary**: the prize problem is *equivalent* to "count low-weight vectors on the cyclic group $\mathbb{Z}/n\mathbb{Z}$ with prescribed Fourier values on a window of length $n-k$."

No more polynomials. No more codes. Pure Fourier analysis on cyclic groups.

### II.2 Sanity check: the extremes work

- **Unique decoding** $\delta < (1-\rho)/2$: falls out directly from Tao's uncertainty principle on $\mathbb{Z}/n\mathbb{Z}$ for $n$ prime. One-line proof.
- **Capacity failure** $\delta \to 1-\rho$ for smooth $n$: subgroup indicators $\mathbf{1}_H$ saturate Fourier uncertainty at $|H| + |H^\perp| \approx 2\sqrt n$ instead of $n+1$, structurally enabling counterexamples.

These extremes are *predicted* by the framework. The middle (Johnson to capacity) is the contested zone.

### II.3 Crites-Stewart in DFT language (Note 0002)

CS picks $f = X^{rm}$, $g = X^{(r-1)m}$. Both monomials → both have **single-spike DFTs**. So $f + \lambda g$ has DFT supported on exactly two frequencies $\{(r-1)m,\ rm\}$, both in the syndrome window $[k, n-1]$.

For each bad $\lambda$: there's an error vector $e$ of weight $(s-r)m$ with $\hat e_{(r-1)m} = \lambda n$, $\hat e_{rm} = n$, and $\hat e_j = 0$ for $(s-r+2)m - 2$ other frequencies in $[k, n-1]$.

**Parameter counting**: $|T| \leq (s-r)m$ error positions vs. $(s-r+2)m - 2$ Fourier equations. Over-determined by exactly $2m - 2$. This is the "rigidity budget" that must come from structural alignment of $T$ with subgroups of $L$.

**Empirical verification** (`cs_small_case.py`, $n=24, p=73, m=2, s=12, r=3$):
- 1 bad $\lambda$ found (value 0), 4 witnesses
- All 4 agreement sets are exactly the 4 cosets of the subgroup $H = \langle\omega^4\rangle$ of order 6 in $L$

Caveat: $\lambda = 0$ is degenerate ($X^6$ is already $H$-invariant because $6 \cdot 4 = 24 \equiv 0 \pmod{24}$). So the small case is consistent with Conjecture 4 but doesn't rule out trivial coincidence.

### II.4 The central conjecture we're attacking

**Conjecture 4 (Note 0002)**: Every bad agreement set $S$ in a proximity-gap-failure witness, over a multiplicative-subgroup evaluation domain $L$, equals a disjoint union of cosets of some nontrivial multiplicative subgroup of $L$.

If true ⇒ the failure region of proximity gap is *fully captured* by the subgroup lattice of $L$, and the prize problem reduces to a **concrete arithmetic question** (when do subgroup-coset decompositions realize the right Fourier patterns).

If false ⇒ there exist "non-subgroup" bad sets, which would be genuinely new structural objects, themselves worth publishing.

---

## Part III — Currently running

### III.1 The sweep (`cs_sweep.py`)

Testing Conjecture 4 across 11 parameter sets, varying $(n, m, s, r)$ with $n \in \{12, 24, 30\}$ and various subgroup structures. For each $(n, m, s, r)$:
1. Find smallest $p \equiv 1 \pmod n$ and primitive $n$-th root $\omega$
2. Enumerate all $\lambda \in \mathbb{F}_p$
3. For each $\lambda$, enumerate all polynomials $h \in \mathbb{F}_p[X]_{<k}$
4. Record every $(λ, h)$ with agreement size $\geq (1-\delta)n$
5. Check whether each agreement set aligns with some subgroup of $\mathbb{Z}/n\mathbb{Z}$

**Expected output form**: a table
$$(n,m,s,r) \ \mid\ p\ \mid\ k\ \mid\ \delta\ \mid\ \#\text{bad } \lambda\ \mid\ \#\text{wits}\ \mid\ \#\text{aligned}\ \mid\ \#\text{NOT}$$

If the `#NOT` column is all zero, Conjecture 4 gets strong empirical support. If anything appears there, we have a new counterexample family.

**Risk**: the larger cases ($n=30, k=5, p=31$) have search space $p \cdot p^k = 31 \cdot 31^5 \approx 900\text{M}$, which is slow in pure Python. May need to prune or abort the largest cases and focus on mid-sized ones.

### III.2 What I'll do with the result

- **All aligned** → drill: formalize Conjecture 4 as a theorem target; start looking at proof strategies (partial Gauss sums, Fourier uncertainty for smooth $n$, Stepanov-like arguments).
- **Some aligned, some not** → refine: characterize the non-aligned counterexamples. Are they "perturbations" of subgroup-aligned ones? Are they still expressible in terms of unions of cosets of *different* subgroups? Modify conjecture.
- **Mostly not aligned** → retreat. Fall back to Task 3 (Niho-exponent $w$, Note 0001 §5.2) — structured-$w$ bounds via cross-correlation literature. Still publishable even if Conjecture 4 fails.

---

## Part IV — What I actually believe

### IV.1 Where the signal is strong

1. **The translation is clean and tight.** Not a "morally equivalent" reformulation — a provable bijection, with the unique-decoding bound falling out for free as proof of no-loss-in-translation.
2. **The parameter count is sharp.** $2m - 2$ extra rigidity degrees is exactly what subgroup alignment provides (structural Fourier vanishing). This isn't coincidence.
3. **The CS choice of monomial $f, g$ is the maximally clean case in our framework.** If Conjecture 4 fails, it would most likely fail for *generic* $f, g$ — not for the very-structured monomial case. So empirical verification on CS-style small cases is a strong test.
4. **The sequence literature has 30 years of partial-Gauss-sum estimates that BCIKS and Crites-Stewart do not cite.** There's free information to harvest.

### IV.2 Where I'm less confident

1. **Characteristic transfer.** CS's construction requires $p \equiv 1 \pmod n$ and prime $p$. The sequence-school toolkit is sharpest in characteristic 2 ($\mathbb{F}_{2^n}$). For binary fields (Binius), the story may have a different flavor. Conjecture 4 might need different formulations in different characteristics.
2. **The "single-spike" advantage is special to CS.** Other counterexample constructions (BGHKS, Diamond-Gruen) use different $f, g$. The DFT structure may not be as clean. Have to translate each separately.
3. **MCA is not directly addressed yet.** MCA's "single common agreement set for a family" constraint goes beyond pairwise proximity gap. The framework handles it (each $u_\ell$ has its own syndrome; MCA requires the single $D$ to be an agreement set for all of them simultaneously) — but partial-period-correlation tools are underdeveloped.
4. **The step from "Conjecture 4 holds" to "publishable theorem" requires actual character-sum bounds.** Knowing that bad sets are subgroup-aligned is not the same as bounding how many subgroup-aligned bad sets exist. The latter is the actual prize-relevant result.

### IV.3 The most likely failure mode

Not "Conjecture 4 is false for an exotic counterexample." Rather: **Conjecture 4 is true but weak** — subgroup-coset structure is necessary but not sufficient; many subgroup-aligned sets don't witness proximity-gap failure, and the question of *which* do reduces to a hard Gauss-sum computation that has been implicitly solved in the 1970s Helleseth literature but never extracted for coding-theory purposes.

If this is the shape of things, our paper would be: *"Proximity gap failure over multiplicative subgroups reduces to evaluating [specific character sum]; this character sum's asymptotic behavior is given by [Helleseth 1976 + refinements]; combining, we get sharp boundary of open zone."*

Not $1M-sized alone. But a clean, correct, publishable bridge between two literatures — and a necessary foundation for the MCA attack that *is* $1M-sized.

---

## Part V — What we need from Prof. Gong

Sharp, focused questions (not "what do you think?"):

1. **Partial Gauss sum literature orientation.** For $\chi$ a multiplicative (or additive) character of $\mathbb{F}_p$, $L = \langle\omega\rangle \subset \mathbb{F}_p^*$ of order $n | p-1$ with $n \ll p$, and $f(x) = \sum c_i x^{j_i}$ with $j_i \in [0, n-1]$: what are the sharpest known bounds on $\sum_{x \in L} \chi(f(x))$, with explicit dependence on $n, p, \deg f, \#c_i$? Shparlinski 1999? Bourgain-Glibichuk-Konyagin 2006? Heath-Brown-Konyagin? Is there a definitive reference?

2. **Cross-correlation distribution for Niho exponents — cleanest entry point.** Niho 1972 is the original; Helleseth 1976 is the systematic treatment. But what's the modern reference that most concretely gives $|\{x \in L : \mathrm{Tr}(x^d) = a\}|$ for various $d, a$ in a form usable for $L_\delta(w)$ bounding?

3. **Do Conjecture 4-type "subgroup-aligned" statements already appear in the sequence-design literature?** It's structurally natural that sequences with prescribed auto/cross-correlation decompose via subgroup-coset structure. Is there known precedent?

4. **Collaboration path to Helleseth / Tang / Katz / Schmidt.** If §5.1 / §5.2 from Note 0001 look viable after the sweep, which specific person is the right ally to ratify the character-sum estimates and co-author?

---

## Part VI — Near-term action tree

```
Currently running: cs_sweep.py
    ├── Result: ALL aligned
    │     → Note 0004: formalize Conjecture 4 + first analytic attack
    │     → Pitch to Gong in next meeting
    │     → Draft a 6-page bridging note for public release
    │
    ├── Result: SOME non-aligned
    │     → Note 0004: characterize non-aligned counterexamples
    │     → Refine Conjecture 4 accordingly (may still be publishable)
    │     → Pitch to Gong
    │
    └── Result: MOSTLY non-aligned
          → Abandon Conjecture 4
          → Task 3: structured-w bounds via Niho cross-correlation
            (Note 0001 §5.2; still a reasonable Plan B)
```

Regardless of outcome: draft the 6-page bridging note that positions sequence-school tools for the proximity-prize problem. This is publishable even as a survey/bridge, and it's what gets Helleseth-school people interested.

---

## Appendix — Inventory

```
EF1M/
  notes/
    0001-translation-theorem.md    — the framework
    0002-cs-translation.md         — CS translated; Conjecture 4
    0003-state-of-investigation.md — this note
    scripts/
      cs_small_case.py             — ran: 4/4 witnesses aligned
      cs_sweep.py                  — running: multi-parameter test
  refs/                            — empty; to be filled with PDFs
```

Tasks (snapshot):
- #7 in_progress — cs_sweep computation
- #4, #5, #6 completed — framework, sanity, core identification

---

## One-line distillation for Prof. Gong

> *The Ethereum Foundation's open proximity-gap problem is equivalent, via a clean DFT translation, to counting low-weight vectors on $\mathbb{Z}/n\mathbb{Z}$ with prescribed Fourier values on a window. The existing disproof (Crites-Stewart) uses monomial $f, g$, making the DFTs single-spike — the cleanest possible instance in this framework. Parameter counting predicts, and small-case computation supports, that bad agreement sets are unions of multiplicative-subgroup cosets in $L$. If this conjecture holds up, the open zone of the proximity gap is fully captured by the subgroup lattice of $L$, and the analytic technology required to extract sharp bounds is partial Gauss sums on multiplicative subgroups — the Golomb-Gong-Helleseth toolkit.*
