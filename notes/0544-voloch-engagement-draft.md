# Note 0544 — Voloch Engagement Email (Draft)

**Date:** 2026-05-07
**Status:** Cold-mail draft, ready for forwarding via Gong → Tang Xiaohu → Voloch chain.

---

**Subject:** Trinomial pencil sub-saturation on $\mu_n \subset \mathbb{F}_p^*$ — descended monodromy question

Dear Professor Voloch,

I'm writing on the recommendation of Guang Gong (and indirectly via Tang Xiaohu)
about a sequence-school question that intersects your 1990 torus-complement
Weil bound work in a concrete way.

**The question.** For $n = 2^{j+1}$, $k = 2^j$ (rate $1/2$), $L = \mu_n \subset \mathbb{F}_p^*$
with $p \equiv 1 \pmod n$, and any coprime mixed-parity triple
$(a_1, a_2, a_3) \in [k, n-1]^3$: does the trinomial pencil
$f_\alpha(z) = \alpha_1 z^{a_1} + \alpha_2 z^{a_2} + \alpha_3 z^{a_3}$
ever agree with a Reed-Solomon codeword in $\geq \lceil\sqrt{nk}\rceil$
positions on $L$, over interior $(\alpha_1, \alpha_2, \alpha_3) \in (\mathbb{F}_p^*)^3$?

**Conjecture (Q3):** No, never.

**Empirical state.** Three independent verification axes confirm at deployment scale:
1. Berlekamp-Welch interior count: **24,576 cells across $j \in \{6, 7\}$, all $K = 0$**, with $\tau$ swept to within 1-2 of the BW unique-decoding boundary.
2. Sato-Tate 4th moment (Larsen invariant): $M_4/M_2^2 \in [1.92, 2.09]$ across **38 cells, $j \in \{6, 7\}$, 5 parity strata, primes F_257, F_641, F_769** — uniformly Sato-Tate $\mathrm{Sp}$.
3. msolve eliminator structure at $j=3$: $p_0^4 - 1 = \Phi_1 \Phi_2 \Phi_4$, field-uniform across F_113, F_193, F_241, F_257.

**Where we think you come in.** Our reading after a 5-round informal expert
panel (Helleseth/Wan/Charpin/Lisonek, then D. Katz/Zhu, then yourself + N.
Katz, then Sawin, then Litt) is that Q3 reduces to a uniform descended-
$\mathrm{Sp}$-monodromy theorem on $\mu_n$ for trinomial pencils. The
bibliography toolkit is:
1. Adolphson-Sperber 1989 (Newton polygon nondegeneracy)
2. Deligne Weil II (pointwise bound)
3. Katz 2002 *Twisted L-functions and monodromy* (geometric monodromy on $\mathbb{G}_m$)
4. Your 1990 torus-complement Weil bound
5. Liu-Wan 2010 (T-adic family Newton polygon)
6. Sawin-Shusterman 2022 (descended-monodromy adaptation template — the new piece)

The technical heart is Component 6 — adapting Sawin-Shusterman's function-field
descended-monodromy template to multiplicative cyclotomic-subgroup sums.

**The ask.** We have a complete empirical envelope and a precise theorem
target. We're looking for 1-3 collaborators to write the descended-monodromy
theorem itself. Daniel Litt and Will Sawin are the second/third names we
plan to approach, but you're our first contact because the torus-complement
Weil component is yours and you were the most concretely actionable in
our internal panel modeling.

**Why this matters.** The Ethereum Foundation Proximity Prize ($\$1$M,
announced 2026-01-26) covers the Reed-Solomon proximity gap problem.
The headline up-to-capacity conjecture was disproven Nov 2025 (Crites-
Stewart 2025 on $\mathbb{G}_m$); the prize money rides on the open
intermediate zone $\sqrt\rho < \delta < 1 - \rho$, where the analogous
question on $\mu_n \subset \mathbb{F}_p^*$ is wide open. Q3 is the
sequence-school answer to the analog of Crites-Stewart for the
cyclotomic-subgroup case. The judges (Boneh / Fenzi / Arnon) are
succinct-proof people, not sequence-school; the descended-monodromy
toolkit is information-arbitrage for the sequence community.

**What's attached.**
- Full empirical state (notes 0540, 0541, 0542 in the repo)
- 3-axis empirical tables
- Reproducible scripts (`g3_BW_*.py`, `g3_cc_*.py`)
- Theorem statement + proof outline (Note 0542)

I can send the materials packaged as a tarball, or arrange a short call.

Best,
[name]

P.S. We also have the j=5 EOO sub-stratum $M_4/M_2^2 \approx 2.51$ outlier —
finite-scale phenomenology that washes out at $j=6$ ($M_4/M_2^2 \approx 2.05$).
This was originally a worry but the $j=6$ test resolved it into deployment-
scale uniformity. Happy to send the trajectory plot.

---

**Notes for sender:**
- Length: ~600 words, ~4 minute read
- Structure: question → empirics → ask → relevance → attachments
- Calibrated to Voloch's likely interests: torus-complement Weil, finite-field arithmetic, character sums
- Prize relevance up front but not pushy
- Specific theorem target named, not vague
- Honest about where we think we are (empirical envelope strong, theorem write-up still to do)
- Soft on commitment ("looking for 1-3 collaborators")
- Polite postscript on the EOO outlier — preempts "is this conjecture really clean?"
