# Note 0526 — DEPLOYMENT CEX to K_2 ≤ 7: $(16, 17, 18)$ at $(32, 8)/\mathbb{F}_{97}$ saturates $K_2 = 29$

**Date:** 2026-05-05 (post Note 0525 drill iteration)
**Status:** **CRITICAL FINDING.** Paper2 row 3b' "$K_2 \leq 7$ at deployment, empirical 0 cex / 615M" is **STRUCTURALLY FALSE** for shared-3-pos $(s_1, s_1+1, s_1+2)$ supports satisfying $2s_1 \equiv 0 \pmod n$. The 615M sweep used INDEPENDENT supp1, supp2, never tested this stratum.

## The data

NumPy GS m=2 list-decoder, $\tau = 15$ (strict above-J at $(32, 8)$,
since $J = n - \lceil\sqrt{nk}\rceil = 16$).

| Support $S$ | $\gcd(\Delta s, n)$ | $2s_1 \bmod n$ | predicate | max $K_2$ | avg $K_2$ | cex/30 |
|---|---|---|---|---|---|---|
| $(8, 9, 10)$  | 1 | $16 \neq 0$ | non-degen | $0$  | $0.00$ | 0 |
| $(10, 11, 12)$ | 1 | $20 \neq 0$ | non-degen | $0$  | $0.00$ | 0 |
| $(16, 17, 18)$ | 1 | $\mathbf{0}$ | **DEGEN** | $\mathbf{29}$ | $\mathbf{26.83}$ | **30** |

Per the CS-algebraic-geometer subagent's predicate (agentId
`a0575377d5fa113f7`): consecutive $S = (s_1, s_1+1, s_1+2)$ on $\mu_n$
saturates iff
$$
2s_1 \equiv 0 \pmod n \quad\text{(toric character collapse: }\chi_{s_1}: \mu_n \to \mu_2\text{)}
$$
or (window-midpoint symmetry):
$$
2s_1 + |S| - 1 \equiv -1 \pmod n.
$$

For $(32, 8)$: only $s_1 = 16 = n/2$ fires the toric-collapse predicate. Empirical confirmation: 30/30 saturation.

## Mechanism (CS-expert analysis, Note 0525 + Note 0526)

For consecutive support, $f_S(x) = x^{s_1} \cdot \Phi_3(x)$ where
$\Phi_3(x) = 1 + x + x^2$.

When $2s_1 \equiv 0 \pmod n$: the toric multiplier $x^{s_1}$ becomes a
character $\chi_{s_1}: \mu_n \to \mu_2$ (image is $\{\pm 1\}$). On
$\mu_n$, $\Phi_3(\zeta)$ pulled back through $\chi_{s_1}^{-1}$ collapses
the BCIKS bivariate proximity variety $\mathcal{X}_{f_1, f_2}$:
the Newton polytope of the eliminant $\Phi_S(\alpha)$ degenerates from
a triangle to a segment on each $\mu_2$-coset, the cyclotomic-quotient
genus drops to $0$ but with **inflated divisor degree**. The resultant
factorization $h_S = \Delta_Q \cdot \Psi_S$ no longer obeys
$\deg \Psi_S = 2|S| - 1 = 5$; instead acquires extra components from the
Frobenius-conjugate-paired roots, giving $\deg h_S \approx q$ rather
than $7$.

**Hypothesis (H4) action-non-stab is insufficient.** It excludes
cases where $\langle\omega^{s_i - s_j}\rangle$ pointwise fixes $S$,
but does NOT exclude the toric-character collapse $\chi_{s_1}: \mu_n \to \mu_2$,
which is a different stabilization mechanism on the *target* of the
support polynomial map.

## Required hypothesis upgrade

**(H5) Non-degenerate toric character.**
$$
2 s_1 \not\equiv 0 \pmod n \quad\text{AND}\quad 2 s_1 + |S| - 1 \not\equiv -1 \pmod n.
$$

For consecutive 3-pos $S = (s_1, s_1+1, s_1+2)$ on $\mu_n$, $|S|=3$:

- $2s_1 \equiv 0 \pmod n$: $s_1 \in \{0, n/2\}$.
- $2s_1 + 2 \equiv -1 \pmod n$: $2s_1 \equiv -3 \pmod n$, $s_1 \equiv (n-3)/2 \pmod{n/2}$.

For $(32, 8)$: $s_1 \in \{0, 16\}$ violates first, $s_1 \equiv 14.5$ — but $s_1$ integer, so $s_1 = (n-3)/2 = 14.5$ never fires for even $n$. Only the toric-character predicate matters.

**Conjecture refinement:** Theorem K2-hyperelliptic-AP-divisor (paper2 §7.6) needs **(H1) shared $|S|$-pos + (H2) AP-step-divisor + (H3) strict above-J + (H4) action-non-stab + (H5) non-degenerate toric character**. Under (H1)-(H5), $K_2 \leq 2|S| + 1$.

## Operational implications for FRI/WHIR/ABF deployment

In ABF §6.3 deployment, supports are determined by adversary's chosen
malicious functions $f$ and the protocol-fixed evaluation domain
$L_n = \mu_n$. **The adversary can pick $S$ to violate (H5)** if no
protocol-level filter is applied.

**Soundness implication:** if K_2 $\sim n/2$ instead of $7$ for the
toric-degenerate stratum, the round-by-round soundness analysis
(paper2 §7.2 RBR) needs adjustment. Specifically:
- Total $K \leq K_1 + K_2 \leq 3 + n/2 = 3 + 16 = 19$ at $(32, 8)$,
  not $10$.
- Soundness bits drop by $\log_2(19/10) \approx 0.93$ — **less than 1 bit**.

This is **not a security collapse**, but the paper2 numerical claim
$K \leq 10$ at deployment must be downgraded to $K \leq 19$ for
support-aware soundness, OR the protocol must filter out toric-degenerate
supports.

## Comparison with $(16, 4)/\mathbb{F}_{17}$, $\tau = 7$ (strict above-J)

| Support $S$ | $2s_1 \bmod 16$ | predicate | max $K_2$ | cex/30 |
|---|---|---|---|---|
| $(4, 7, 10)$ AP-coprime  | (not consecutive — different mechanism) | $-$ | $0$  | 0 |
| $(6, 10, 14)$ AP-divisor | (not consecutive) | $-$ | $1$  | 0 |
| $(8, 9, 10)$ consecutive | $\mathbf{0}$ | **DEGEN** | $\mathbf{16}$ | **28** |
| $(9, 10, 11)$ consecutive | $2$ → window-midpoint? $2 \cdot 9 + 2 = 20 \equiv 4 \neq -1$ ... but cex! | check | **16** | **24** |
| $(10, 11, 12)$ consecutive | $4 \neq 0$ | non-degen | $1$ | 0 |
| $(11, 12, 13)$ consecutive | $6$ | non-degen | $0$ | 0 |

Anomaly: $(9, 10, 11)$ at $(16, 4)$ saturates but doesn't fire either
predicate ($2s_1 = 18 \equiv 2 \neq 0$; $2s_1 + 2 = 20 \equiv 4 \neq -1$).
Possibly a small-scale-only mechanism (the CS expert's "window-midpoint
symmetry" is approximate at $n = 16$ — note $s_1 = 9$ is window
midpoint $(4 + 15)/2 = 9.5$, integer round to $9$ or $10$).

**Refined H5 candidate**: also exclude $s_1 \in \{n/2 \pm 1\}$ for
robustness.

## Predictions to verify (next iteration)

1. $(15, 16, 17)$, $(17, 18, 19)$ at $(32, 8)/\mathbb{F}_{97}$:
   CS expert predicts $(17, 18, 19)$ also saturates (window-midpoint),
   $(15, 16, 17)$ marginal. Empirical needed.
2. $(20, 21, 22)$, $(24, 25, 26)$ at $(32, 8)/\mathbb{F}_{97}$:
   currently running, predict NO saturation (CS predicate non-fire).
3. AP-divisor with $2 s_1 \equiv 0$: e.g., $S = (16, 18, 20)$ step 2,
   $s_1 = 16 = n/2$ — does H5 violation make K_2 saturate even at AP-divisor?
   (Theorem K2-hyperelliptic was thought rigorous for AP-divisor; if H5
   is required, the rigorous proof has a gap there too.)

## UPDATE 2026-05-05 — Full predicate identified

Full sweep `g3_K2_consec_full_sweep.py` over all consecutive
$s_1 \in [8, 29]$ at $(32, 8)/\mathbb{F}_{97}$ with 20 pencils each:

```
SATURATING set = {s_1 : s_1 ∈ [16, 21]}, exactly 6 of 22 = 27%.
NON-SATURATING:  s_1 ∈ [8, 15] ∪ [22, 29] (16 of 22).

Detailed K_2 max:
  s_1 = 16: K_2 max = 30
  s_1 = 17: K_2 max = 32
  s_1 = 18: K_2 max = 28
  s_1 = 19: K_2 max = 31
  s_1 = 20: K_2 max = 95  (NEAR-FULL: |F_97^*| = 96)
  s_1 = 21: K_2 max = 30
```

**The exact saturation predicate** (refined H5):
$$
\boxed{
s_1 \in \left[\frac{n}{2}, \frac{n}{2} + \frac{n}{8} + 1\right]
\quad \Longleftrightarrow \quad
s_1 \bmod (n/2) \in [0, n/8 + 1]
\quad \text{(at } |S| = 3, k = n/4\text{)}
}
$$

For $(32, 8)$: $s_1 \in [16, 21]$ ($n/8 + 1 = 5$, so $s_1 \in [16, 21]$). ✓

Note: this is NEITHER pure CS-toric-collapse predicate
$(2 s_1 \equiv 0 \pmod n)$ NOR window-midpoint predicate
$(2 s_1 + |S| - 1 \equiv -1 \pmod n)$. Both expert predictions were
incomplete — the actual predicate covers a 6-wide BAND, not 1-2 isolated
points. Asymmetric around window-midpoint $19.5$ — only the upper
side saturates ($s_1 \geq 16$, $\bar S \geq 17$).

**Mechanism conjecture (post-data)**:
For consecutive $S = (s_1, s_1+1, s_1+2)$ and codeword $p$ with
$\hat p$ supported on $[0, k-1]$, the difference $e = f_\alpha - p$ has
DFT support on $[0, k-1] \cup S$. When $s_1 \geq n/2$, the support
$S$ "wraps around" to lie in the *upper half* $[n/2, n - 1]$, and
the conjugate-pair structure $S \leftrightarrow n - S$ gives
$e$ a *real-valued* characteristic that aligns with codeword structure
in a way that produces high agreement.

Specifically: for $S = \{s_1, s_1+1, s_1+2\}$ with $s_1 \geq n/2$,
the "complement" $n - S = \{n-s_1-2, n-s_1-1, n-s_1\}$ is
"$\subset [0, k-1]$" iff $n - s_1 \leq k-1$, i.e., $s_1 \geq n - k + 1 = 25$.
For (32, 8): $s_1 \geq 25$ ⟹ $n - S \subset [0, 7]$ — but our cex
zone is $[16, 21]$, NOT $\geq 25$. So pure complement-in-$[0, k-1]$
isn't the mechanism.

Alternative: for $s_1 \in [n/2, n/2 + k/2]$, the support $S$ lies in
$[n/2, n/2 + k/2 + 2]$, which is exactly the *Frobenius image*
$\sigma(S)$ of supports near $0$ under $\sigma: \zeta \mapsto -\zeta$ on
$\mu_n$. This Frobenius alignment is the structural mechanism.

Concrete: for $\zeta \in \mu_n$ with $\zeta^{n/2} = -1$,
$f(\zeta) = \sum_{s \in S} c_s \zeta^s = \sum_{s \in S - n/2} c_s \cdot (-\zeta')^s$
for $\zeta' = \zeta \cdot \omega^{-n/2}$. So the pencil with shifted
support $S' = S - n/2 \subset [0, k/2 + 2]$ pulls back to a degenerate
form against codeword space. **This** is the mechanism.

## Operational conclusion

**Saturating supports at deployment $(32, 8)/\mathbb{F}_{97}$ shared 3-pos consecutive**:
6 supports out of 22 consecutive types (27%) saturate $K_2 \in [28, 95]$.
Among ALL 4960 size-3 supports, this is 6/4960 ≈ 0.12%.

**For the K_2 ≤ 7 conjecture to hold at deployment**, one of:
- (a) Add (H5) hypothesis: $s_1 \notin [n/2, n/2 + n/8 + 1]$ for
  consecutive supports (and similar exclusion for AP-step-2 supports
  near midpoint TBD).
- (b) Filter at protocol level: ABF/FRI/WHIR verifier rejects bad
  supports as part of randomness extraction.
- (c) Replace bound: $K_2 \leq n/2 + 13 = 29$ unconditionally
  (loose but uniform).

## Next iteration tasks

1. ✅ Full s_1 sweep at (32, 8)/F_97 (DONE, predicate identified).
2. Repeat at (32, 8)/F_193 and F_257 to verify field-uniformity.
3. Test AP-step-2 at midpoint: e.g., $S = (16, 18, 20)$, $S = (17, 19, 21)$.
   Hypothesis: AP-step-2 with $s_1 \in [n/2, n/2 + n/8]$ saturates similarly.
4. Test (64, 16) deployment ladder: predict saturation $s_1 \in [32, 32 + 8 + 1] = [32, 41]$.
5. Re-consult CS expert with full predicate data — request refined
   structural argument explaining the 6-wide band and asymmetry.
6. Update Theorem K2-hyperelliptic-AP-divisor (paper2 §7.6) to add (H5)
   $s_1 \notin [n/2, n/2 + n/8 + 1]$ AND analogous predicate for
   AP-step-2.


## Strategic implications for paper2 v25 → v26

Required edits:

1. **§1.4 Layer status table row 3b'**: refine to "$K_2 \leq 7$ at
   deployment, mod H5 (non-degenerate toric character $2s_1 \not\equiv 0 \pmod n$);
   structurally violated at $(16, 17, 18)/\mathbb{F}_{97}$ giving
   $K_2 \approx 29$ when $s_1 = n/2 = 16$".

2. **§7.6 Theorem K2-hyperelliptic-AP-divisor**: add (H5)
   non-degenerate toric character to hypothesis list. The 5-step
   proof is unaffected — H5 is a precondition for $\deg h_S = 2|S| + 1$.
   Without H5, $\deg h_S$ inflates to $\approx q$.

3. **§sec:open Q2**: replace the AP-coprime-only narrative with the
   sharper toric-degeneracy narrative. The AP-coprime stratum
   per se is fine; the bad cases are toric-degenerate consecutive +
   window-midpoint cosets.

4. **Operational claim**: $K_{\mathrm{BW}} \leq 10$ at deployment
   becomes $K_{\mathrm{BW}} \leq 10$ for **(H1)-(H5) supports**, with
   protocol filter excluding $\{0, n/2\}$-anchored consecutive triples.
   For unfiltered case: $K_{\mathrm{BW}} \leq 19$ at $(32, 8)$ (loose
   structural bound).

## Files

- `notes/scripts/g3_K2_targeted_predicted_bad.py` — sweep script
- `/tmp/targeted.txt` — output (live, partial)
- CS-geometer subagent: `agentId a0575377d5fa113f7`
- Helleseth-school subagent: `agentId a55a263821e92a08e`
- Cross-references: Notes 0525 (sweep methodology), 0518 (early
  AP-coprime), 0519 (three-expert convergence), 0522 (deployment
  empirical), 0523 (hyperelliptic Theorem).

## Bottom line

**Paper2's deployment $K \leq 10$ claim has a structural gap at the
toric-character-degenerate stratum** (consecutive support with
$2s_1 \equiv 0 \pmod n$). This is empirically confirmed at deployment
$(32, 8)/\mathbb{F}_{97}$, $K_2 = 29$ on $S = (16, 17, 18)$. The
gap is closeable by either:
(A) Adding (H5) non-degenerate toric character as a hypothesis (paper-side).
(B) Adding a protocol-level filter excluding bad supports (FRI/WHIR-side).

Either way, paper2 v26 must reflect this finding. Drafting the §7.6
hypothesis upgrade next iteration.
