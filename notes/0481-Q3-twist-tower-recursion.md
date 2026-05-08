# Note 0481 — Q3 Closure: Twist-Tower Recursion for K=28 Saturation

**Date:** 2026-05-05
**Status:** STRUCTURAL CONJECTURE with empirical verification at (16, 8);
extension to (32, 16) in progress via F_p Singular GB.

## The structural conjecture

**Conjecture (Twist-Tower Decomposition)**:
At rate 1/2 deployment $(n, k) = (2^j, 2^{j-1})$ for $j \geq 3$, the
saturating set
$$
S^*(n, k) := \{(a_1, a_2, a_3) \subset [k, n-1]^3 : v_\delta(h_{\vec\alpha}; \mathrm{RS}_k(L_n)) \text{ has } \mathrm{vdim} = 28\}
$$
decomposes as
$$
S^*(n, k) = \iota_0(S^*(n/2, k/2)) \;\sqcup\; \iota_1(S^*(n/2, k/2))
$$
where
- $\iota_0$ (standard SP doubling): $(a_1, a_2, a_3) \mapsto (2a_1, 2a_2, 2a_3)$
- $\iota_1$ (twist-1 SP): $(a_1, a_2, a_3) \mapsto (2a_1 + 1, 2a_2 + 1, 2a_3 + 1)$

**Base case** ($j = 3$, panel $(8, 4)$):
$S^*(8, 4) = \{(4, 5, 6), (4, 5, 7), (5, 6, 7)\}$.
The fourth above-J triple $(4, 6, 7)$ is sub-saturating: vdim = 24 (further
reduces under standard SP since $\gcd(4, 6) = 2$).

**Verified by direct Singular GB**
(`g3_3mono_base_8x4.output.txt`): vdim = 28 at $(4, 5, 6)$, $(4, 5, 7)$,
$(5, 6, 7)$; vdim = 24 at $(4, 6, 7)$.

**Paper2 §C correction**: paper2 currently states "vdim + K_2mono = 28 across
all 4 triples", interpreting K = 28 as the TOTAL bad-α count including 2-mono
boundary contribution. The vdim alone is 28 only at 3 of 4 base triples;
the (4, 6, 7) base triple has vdim = 24 + K_2mono(4, 6) = 28 with K_2mono(4, 6)
= 4 from the gcd-reducible 2-mono boundary.

**Inductive count**: $|S^*(2^j, 2^{j-1})| = 2 \cdot |S^*(2^{j-1}, 2^{j-2})|
= 3 \cdot 2^{j-3}$.

For $j = 3$ (panel $(16, 8)$): predicted $|S^*| = 6$. **Verified by full
sweep** (Note 0480, $g3\_rate\_half\_K28\_lift\_16x8.py$).

For $j = 4$ (panel $(32, 16)$): predicted $|S^*| = 12$. Verification
in progress (`g3_rate_half_K28_brute_32x16.py`, F_p Singular GB).

## The structural argument (forward direction)

**Lemma (Twist-1 forward direction)**:
For all-odd 3-position pencil $h_{\vec\alpha}(z) = \sum_i \alpha_i z^{a_i}$
on $L_{2k}$ with $a_i = 2c_i + 1$ odd, $c_i \in [k-1]/2$:
$$
v_\delta(h_{\vec\alpha}; \mathrm{RS}_k(L_{2k})) \supseteq v_\delta(\tilde h_{\vec\alpha}; \mathrm{RS}_{k/2}(L_k))
$$
where $\tilde h_{\vec\alpha}(u) = \sum_i \alpha_i u^{c_i}$ on $L_k$.

**Proof**: Define $u := z^2$, $\pi: L_{2k} \to L_k$, $z \mapsto z^2$. The
factoring $h_{\vec\alpha}(z) = z \cdot \tilde h_{\vec\alpha}(z^2) =
z \cdot \tilde h_{\vec\alpha}(u)$ is identical. For
$\tilde p \in \mathrm{RS}_{k/2}(L_k)$, the lift
$p(z) := z \cdot \tilde p(z^2)$ has degree $\leq 1 + 2(k/2 - 1) = k - 1$,
hence $p \in \mathrm{RS}_k(L_{2k})$. Per-fiber agreement: for $\zeta \in
\mu_2$, $h_{\vec\alpha}(\zeta z) - p(\zeta z) = \zeta z (\tilde h - \tilde p)(z^2)$,
which vanishes iff $(\tilde h - \tilde p)(z^2) = 0$ (since $\zeta z \neq 0$).
Thus the agreement set on $L_{2k}$ equals $\pi^{-1}(\tilde S)$ where $\tilde S$
is the agreement set on $L_k$, with multiplicity 2. Hence
$|S| = 2 \cdot |\tilde S|$, distance preserved by factor 2.
$\square$

This proves $\iota_1$ maps base saturating to deployment saturating.
Combined with the standard SP forward direction (Prop. substitution), both
$\iota_0$ and $\iota_1$ map $S^*(n/2, k/2)$ injectively into $S^*(n, k)$.

## The structural conjecture: completeness

The remaining piece is **completeness**: $S^*(n, k) \subseteq \iota_0(S^*) \cup \iota_1(S^*)$.

Equivalently: triples NOT in $\iota_0 \cup \iota_1$ image (i.e., neither all-odd
nor gcd-divisible) have vdim < 28.

**Empirical at (16, 8)**: 52 coprime triples, of which 4 are all-odd. The 3
all-odd saturating triples are in $\iota_1$ image; the other 48 mixed-parity
coprime have vdim ≤ 4 (checked by full sweep, Note 0480).

**Empirical at (32, 16)** (in progress): 12 sample mixed-parity coprime
triples being checked. If all give vdim < 28, completeness holds at $j=4$.

**Structural intuition** (per Helleseth subagent advice on Niho exponents):
mixed-parity 3-monomial pencils don't admit a single $z^\sigma$-factorization
that descends to a smaller scale; their syndrome window has 3 nonzero
coordinates with no compatible action-orbit closure. The K-bound is
governed by Sudan-type list decoding at smaller multiplicity, giving
$K \leq O(1)$ rather than $K = 28$.

A rigorous proof of mixed-parity $K < 28$ at all $(2^j, 2^{j-1})$ would
close Q3 universally. Currently this is the open structural piece.

## Mixed-parity orbit-size Lemma (paper2 §3 Lemma lem:mixed-parity-orbit)

The Action-Orbit Theorem applied to 3-monomial pencils gives a
structural lower bound on the interior bad-set orbits.

**Lemma**: For mixed-parity coprime triple $(a_1, a_2, a_3)$ at
$(n, k) = (2^{j+1}, 2^j)$, $j \geq 3$, with $\alpha_3 = 1$ normalization,
any orbit of the Action-Orbit subgroup in the bad-$(\alpha_1, \alpha_2)$
set with $\alpha_1, \alpha_2 \neq 0$ has size exactly $n$.

**Proof sketch**: WLOG $a_1$ even, $a_2, a_3$ odd. The Action-Orbit
generator $g = (\omega^{a_1 - a_3}, \omega^{a_2 - a_3})$ has
$a_1 - a_3$ odd, so $\gcd(a_1 - a_3, 2^{j+1}) = 1$, giving
$\text{ord}(g) = n$.

**Consequence at $j \geq 4$**: $n \geq 32 > 28$. If $K \leq 28$ holds
universally (the sought a priori upper bound), then interior
$K(\text{mixed-parity}) = 0$, leaving total $K \leq$ boundary $\leq 8$
(from rate-half-K4 boundary contribution).

**Q3 reduction**: closes mixed-parity sub-saturation conditionally on
the a priori upper bound. The residual $j \geq 4$ a priori bound is
the only remaining open piece.

## Q3 closure status

After the twist-tower framework + mixed-parity Lemma (Notes 0480 + 0481,
paper2 §3 Lemmas `lem:twist1-substitution`, `lem:mixed-parity-orbit`):

| Component | Status |
|-----------|--------|
| Twist-1 SP forward direction (Lemma) | ✅ Rigorous, in paper2 §3 |
| Standard SP forward direction | ✅ Rigorous (paper2 §3 Prop. substitution) |
| Saturating set at base $(8, 4)$ | ✅ Rigorous via Singular GB (3 of 4 triples) |
| Saturating set at $(16, 8)$ matches twist-tower | ✅ Verified empirically (6 = 3+3) |
| Saturating set at $(32, 16)$ matches twist-tower | ❌ Singular GB times out at σ-degree 23; F_p mod-p attempt also timed out at 600s |
| Mixed-parity sub-saturation at all scales | 🔄 Empirical at $(16, 8)$, structural conjecture for $j \geq 5$ |

Q3 is REDUCED to: prove mixed-parity coprime triples have $K < 28$ at every
$(2^j, 2^{j-1})$.

## What "Q3 closed" would require

Three-pronged structural attack:
1. **Sudan/Guruswami-Sudan list decoder verification at (32, 16)** to extend
   empirical evidence to next dyadic scale. (Implementation pending; existing
   GS m=2 code in `notes/scripts/issue419_GS_m2_list_decode.py` for (128, 32)
   could be adapted.)
2. **Helleseth-Kumar 1998 cross-correlation classification** to prove
   mixed-parity sub-saturation universally. The Niho exponent framework
   characterizes 3-valued cross-correlation distributions on cyclic groups,
   and the K-saturation count corresponds to such a distribution.
3. **Cyclotomic-resultant Nullstellensatz certificate** (per Gong subagent
   advice) to verify Φ-eliminator equality at the dyadic tower up to
   deployment scale, via 2-adic recursive factorization.

Per current paper2 §sec:open Q3, the universal-$k$ closure remains
conditional; the rate-1/2 K=28 bound is rigorous at base and verified
at $(16, 8)$, with structural extension expected via the twist-tower.

## Connection to Helleseth's Niho framework

The twist-1 SP corresponds to **decimation $a \to (a-1)/2$ on Z/n** for
all-odd positions, and the standard SP corresponds to **decimation $a \to a/2$**
for all-even positions. Both decimations are length-halving group homs
$\mathbb{Z}/n^* \to \mathbb{Z}/(n/2)^*$.

Helleseth's classical Niho exponent classification (1976) characterizes
3-valued cross-correlation distributions on $\mathbb{F}_{q^n}$ via specific
decimation patterns. The K=28 saturation corresponds to a specific
3-valued distribution; its decimation structure under Niho's classification
should give a closed-form characterization of $S^*(n, k)$, i.e., proof
of the completeness conjecture.

This is the recommended path for the universal-k closure: import
Helleseth-Kumar 1998 cross-correlation classification.
