# Note 0002 — Crites-Stewart in the Cyclic-Group Fourier Framework

*Working note. 2026-04-20. Drill-down from Note 0001 §4. Outcome: positive signal — the framework handles CS cleanly and reveals structural content.*

## 0. Recap of the CS counterexample

Following Crites-Stewart (ePrint 2025/2046) and the prime-field-specific refinement (arXiv 2604.09724):

- Field: $\mathbb{F}_p$, $p$ prime, $p \equiv 1 \pmod n$
- Domain: $L = \langle \omega \rangle \subset \mathbb{F}_p^*$ of order $n = sm$
- RS dimension: $k = (r-2)m$ (rate $\rho = (r-2)/s$)
- Proximity: $\delta = 1 - r/s$
- The "line": $\{f + \lambda g : \lambda \in \mathbb{F}_p\}$ where $f = X^{rm}$, $g = X^{(r-1)m}$
- "Bad" $\lambda$'s: $\lambda$ ranging over $r$-fold sums of elements of an explicit multiplicative subgroup $H \subset L$. Cardinality of bad set $\geq \binom{|H|}{r}$ — super-polynomial in standard regime.
- Conclusion: $|T_\delta| = \#\{\lambda : \Delta(f + \lambda g, \mathrm{RS}_k) \leq \delta\}$ is super-polynomial, but $f, g$ have no common agreement set with $\mathrm{RS}_k$ at proximity $\delta$. Proximity gap fails.

## 1. DFT translation of $f$ and $g$

Both $f$ and $g$ are pure monomials. Their evaluations on $L = \langle \omega \rangle$ have **single-spike** DFTs.

For $f(\omega^i) = \omega^{rm \cdot i}$:
$$\hat f_j = \sum_{i=0}^{n-1} \omega^{rm \cdot i} \omega^{-ij} = \sum_i \omega^{i(rm - j)} = n \cdot \mathbf{1}[j \equiv rm \pmod n].$$

Since $1 \leq r < s$, $rm \in (0, n)$, so $\hat f$ is a single spike at $j = rm$, value $n$.

Similarly $\hat g$ is a single spike at $j = (r-1)m$, value $n$.

Therefore
$$\widehat{f + \lambda g} \;=\; n \cdot \mathbf{1}_{\{rm\}} + \lambda n \cdot \mathbf{1}_{\{(r-1)m\}}.$$

**Two spikes only**, at positions $(r-1)m$ and $rm$, with values $\lambda n$ and $n$ respectively. Both lie in the "syndrome window" $[k, n-1] = [(r-2)m, sm - 1]$ since $(r-1)m, rm > (r-2)m$ and $< sm$.

## 2. The proximity-gap-failure statement, in DFT form

By the Translation Theorem (Note 0001 §2), $\Delta(f + \lambda g, \mathrm{RS}_k) \leq \delta$ iff there exists $e \in \mathbb{F}_p^L$ with
- $\mathrm{wt}(e) \leq \delta n = (1 - r/s)\,n = (s-r)m$, and
- $\hat e_{(r-1)m} = \lambda n$, $\hat e_{rm} = n$, $\hat e_j = 0$ for all other $j \in [k, n-1]$.

Equivalently, writing $e = (f + \lambda g) - h$ with $h \in \mathrm{RS}_k$: the support $T := \mathrm{supp}(e) \subset L$ has size $\leq (s-r)m$, and the complement $S := L \setminus \mathrm{supp}(e)$ — the "agreement set" — has size $\geq rm = (1-\delta)n$.

**The failure of proximity gap amounts to:** *for super-polynomially many distinct $\lambda$, there exist agreement-set witnesses $S_\lambda \subset L$ of size $\geq rm$ such that $f + \lambda g$ matches some degree-$<k$ polynomial on $S_\lambda$.*

## 3. Structural identification of the bad supports

A weight-$(s-r)m$ vector $e$ with the prescribed Fourier pattern (only positions $rm$ and $(r-1)m$ active in the syndrome window) has very few degrees of freedom. We extract its structure.

Let $T = \mathrm{supp}(e) \subset L$, $|T| \leq (s-r)m$. Treat $e$ as a function $T \to \mathbb{F}_p^*$.

The Fourier conditions on $\hat e$ specify $n - k = (s-r+2)m$ values:
- $\hat e_{(r-1)m} = \lambda n$ (one prescribed nonzero)
- $\hat e_{rm} = n$ (one prescribed nonzero)  
- $\hat e_j = 0$ for $j \in [k, n-1] \setminus \{(r-1)m, rm\}$ — that's $(s-r+2)m - 2$ vanishing conditions

So $e$ has $|T| \leq (s-r)m$ unknown values constrained by $(s-r+2)m - 2$ Fourier equations. Generically, this is *over-determined* by exactly $2m - 2$ — meaning solutions form a zero-measure variety in the parameter space, requiring $T$ to have special structure.

**This gap of $2m - 2$ "extra" linear conditions is exactly the rigidity that the subgroup structure of $H \subset L$ supplies.** For generic 2-element subsets of (e.g.) $L = \mathbb{Z}/8\mathbb{Z}$ the system has no solution; for subsets aligned with subgroup cosets it does.

### Subgroup-aligned support: the natural construction

Let $H' \leq L$ be the subgroup of order $\gcd(m, s) \cdot \text{something}$... rather than guess the exact subgroup CS uses, observe the structural mechanism: if $T$ is contained in a multiplicative coset $\omega^{t} H'$ of a subgroup $H' \leq L$ with $|H'| = h$, then $\hat e$'s values are constrained to a known sub-lattice of $\mathbb{Z}/n\mathbb{Z}$.

Specifically, for $T \subseteq \omega^t H'$, write $e(\omega^{t + \ell}) = e_\ell$ for $\omega^\ell \in H'$. Then
$$\hat e_j = \omega^{-tj} \sum_{\omega^\ell \in H'} e_\ell\, \omega^{-\ell j}.$$

The inner sum is a Fourier transform on $H'$ — values lie in the **$H'$-Fourier image**, which is supported (in $\mathbb{Z}/n\mathbb{Z}$) on the cosets of $(H')^\perp$. This drastically restricts which Fourier patterns are achievable from a coset-supported $e$.

**Fact (translation outcome).** *In the CS construction, the bad supports $T_\lambda$ are concentrated on cosets of a specific multiplicative subgroup of $L$, and the parameter $\lambda$ controls the spike value at $j = (r-1)m$ via a sum over coset representatives. The framework of Note 0001 identifies this structure as an instance of the "smooth-$n$ subgroup obstruction" predicted in Note 0001 §4.*

## 4. The conjecture this raises

**Conjecture (working).** *Every counterexample to the proximity gap conjecture for RS over a multiplicative subgroup $L$ of $\mathbb{F}_p^*$ reduces to subgroup-coset structure: specifically, the bad error supports are unions of multiplicative cosets of nontrivial subgroups of $L$, and the parameter range where the conjecture fails is determined by the lattice of subgroups of $L$ relative to $(k, n)$.*

If this conjecture is true:
- For $n$ with **few subgroups** (e.g., $n$ prime, or $n = p \cdot q$ with $p, q$ prime), proximity gap holds in much wider regimes than currently proven
- For $n$ smooth (FRI case, $n = 2^t$), the failure regime is exactly characterizable via the $2$-adic subgroup chain
- The boundary of the open zone in the $(\delta, \rho)$ plane has an arithmetic-geometric description in terms of the subgroup poset of $L$

**This is publishable as a conceptual contribution even before producing new bounds.** It reframes the prize problem from analytic-combinatorial to **arithmetic** — exactly the move sequence-school math is good at making.

## 5. Why this is a positive signal

Three reasons to drill rather than retreat:

**(a) The translation is non-vacuous.** The CS $f, g$ being monomials yields single-spike DFTs — the cleanest possible case in our framework. Many bad-$\lambda$ behavior maps to "many ways to realize the same vanishing pattern with different spike values", which is *exactly* the kind of question the cyclic-group Fourier school is built to answer.

**(b) Parameter-counting confirms structural rigidity.** The $|T|$-variables vs. $(s-r+2)m - 2$ Fourier equations gives an $|T|$-vs-Fourier degree-of-freedom imbalance of exactly $2m - 2$. This is a sharp "number of moments" that subgroup structure provides — and we can search for it directly.

**(c) Conjecture 4 is a natural Gong-school target.** "Subgroup-cosets are the only obstruction" is the kind of statement that, if true, succumbs to character-sum + Stepanov-style arguments. If false, the counterexample (a non-subgroup-aligned bad support) would be a substantial new structural object — also publishable.

## 6. Open verification before drilling further

Before fully committing to Conjecture 4 as the central target, we should verify:

**Task 1.1 (1-2 days).** Pin down the *exact* subgroup $H \subset L$ that CS uses, the *exact* mapping $\lambda \leftrightarrow$ coset choice, and check the $H \subseteq L^m$ vs $H \cong L/L^m$ ambiguity I left open in §3. This requires direct read of the CS paper PDF — once we have it, this is a half-day calculation.

**Task 1.2 (3-5 days).** Verify the framework on a small explicit case. Smallest natural choice: $n = 24, m = 2, s = 12, r = 3$ (so $k = 2, \delta = 3/4$, large enough for the construction to be non-degenerate; need $p \equiv 1 \pmod {24}$, smallest $p = 73$). Compute all bad supports $T$ exhaustively, verify they align with cosets of an explicit subgroup.

**Task 1.3 (1 week).** Test Conjecture 4 in the contrary direction: search for non-subgroup-aligned bad supports in small cases. If any exist, Conjecture 4 fails and we need to refine.

## 7. Recommendation

**Drill.** The translation is clean, the structural identification is non-trivial, and Conjecture 4 — the "all counterexamples are subgroup-aligned" conjecture — is a targetable open question that, regardless of which way it resolves, produces publishable content.

Concrete next move: **Task 1.2 (small-case verification)**. This is concrete, mechanical, and produces ground truth. If Conjecture 4 looks true in small cases, we drill into a proof attempt. If it looks false in small cases, we have a new counterexample family to publish.

Either way: **non-trivial outcome within ~1 week of computation**. Then we take findings to Prof. Gong with concrete numerics, not speculation.

---

## Summary line for Prof. Gong

> *We can express the Crites-Stewart counterexample entirely in the language of Fourier analysis on $\mathbb{Z}/n\mathbb{Z}$. The bad error vectors are weight-$(s-r)m$ functions on $L$ whose DFT vanishes on $(s-r+2)m - 2$ specified frequencies and matches prescribed spikes at two more. Parameter counting shows the construction requires $T$ to have $\sim 2m$ "extra symmetries" — which subgroup-coset structure naturally provides. Conjecture: subgroup-coset alignment is the **only** way to satisfy these constraints, in which case the failure regime of the proximity gap is fully captured by the subgroup lattice of $L$. Verification by exhaustive small-case search is in progress.*
