# Note 0485 — Q3 Final State (Drill Session 2026-05-05)

**Date:** 2026-05-05
**Session:** Compute-driven drill session, 1.5-hour total wallclock.
**Status:** Q3 mixed-parity sub-saturation conjecture supported empirically
at j=3 (full sweep, 48 coprime, all $K \leq 4$) and j=4 (6 of 8 sample,
$K = 0$ via msolve $\texttt{[-1]}$). Universal-$j$ closure remains open.

## Computational tally

For 2 hard mixed-parity cases at $(32, 16)$, $(17, 22, 25)$ and
$(18, 25, 27)$:

| Configuration | Outcome |
|---------------|---------|
| msolve $-t 1$ over $\FF_{257}$, 300s timeout | TIMEOUT |
| msolve $-t 1$ over $\FF_{257}$, 1800s timeout | TIMEOUT, 49 GB RSS |
| msolve $-t 1$ over $\FF_{97}$, 900s timeout | TIMEOUT |
| msolve $-t 16$ over $\FF_{257}$, 1800s timeout, 28-core | TIMEOUT, 57 GB RSS peak |

Effective parallelism in msolve was ~1 thread (CPU time ≈ wall clock at
$-t 16$); F4 sequential phases (S-pair generation, interreduction)
dominate matrix reduction. No straightforward speedup path on existing
hardware.

## Structural distinction

The 6 fast cases at $(32, 16)$ all contain position $a = 16$, which
yields $z^{16} \in \{\pm 1\}$ on $L_{32}$. This collapses the cert+div
ideal to a 2-fold Gröbner basis structure that msolve handles in
seconds. The 2 slow cases lack this collapse and produce a "generic"
mixed-parity coprime ideal whose GB is genuinely heavy.

## What was added to paper2 this session

1. **Lemma~\ref{lem:twist1-substitution}** (paper2 §3): Twist-1 SP
   forward direction with full fiber-pullback proof.
2. **Lemma~\ref{lem:mixed-parity-orbit}** (paper2 §3): Mixed-parity
   orbit-size lower bound via Action-Orbit + odd parity differences.
3. **Remark~\ref{rem:twist-tower}** (paper2 §3): Twist-tower recursion
   structure across dyadic scales.
4. **Remark~\ref{rem:mixed-parity-subsat}** (paper2 §3): Mixed-parity
   sub-saturation conjecture statement.
5. **Updated §sec:open Q3** to reflect:
   - BKK-tight base verification (Note 0484, $V(P_2, P_3) = 24$ exactly)
   - Empirical $(32, 16)$ sample (6/8 fast, 2 timeout under 4 configs)
   - Structural reason for slow cases (lack of position-16 collapse)

Paper2 commits this session: `72128af` (BKK base), `40a37d5` (F_97
retry), `4586b87` (final retry tally).

## Q3 closure conditional structure

The chain of implications (paper2 v23 form):
1. Universal $K \leq 28$ for all coprime triples at $(2^{j+1}, 2^j)$
   — verified at $j = 3$ exhaustively, conjectured for $j \geq 4$.
2. ⇒ For mixed-parity at $j \geq 4$, $K_{\text{interior}} < n = 2^{j+1}$.
3. ⇒ Orbit-size Lemma: $K_{\text{interior}}$ multiple of $n$;
   combined with $K_{\text{interior}} < n$ gives $K_{\text{interior}} = 0$.
4. ⇒ $K_{\text{total}} \leq K_{\text{boundary}} \leq 2 K_{2\text{-mono}} \leq 8 < 28$.

Hence rate-$1/2$ Theorem holds rigorously **conditional on (1) at all $j$**.

## Open research-level paths

### Path A: Helleseth Niho exponent classification
- Helleseth-Kumar 1998 cross-correlation classification of 3-valued
  Niho exponents.
- Niho decomposition $h(z) = E(u) + z O(u)$ on $L_{2k}$ via $u = z^2$,
  splitting mixed-parity 3-mono into single-even + 2-mono-odd.
- Combine with Hartmann-Tzeng + Roos bounds on cyclic codes.
- Status: Note 0483 expert consultation outline; implementation pending.

### Path B: Gong BKK / mixed volume
- Verified $V(P_2, P_3) = 24$ tight at base (Note 0484).
- Eliminator polynomial preserved under SP substitution → BKK invariant
  at all dyadic saturating triples.
- Open: NP transformation under non-SP perturbation (mixed-parity at
  higher scales).
- Status: requires polymake/Sage infrastructure for mixed-parity NP
  at $(16, 8)$ and $(32, 16)$.

### Path C: Direct Sudan/GS list-decoder enumeration
- Brute-force enumerate $(\alpha_1, \alpha_2)$ in $\FF_{257}^2$ with
  $\alpha_3 = 1$ via Berlekamp-Welch unique decoding at $\tau = 28$
  (4 errors, RS unique).
- ~100 sec per (triple, $\tau$) value with numpy.
- Caveat: detects $\FF_{257}$-rational bad $\alpha$ only; doesn't rule
  out $\FF_{257^d}$ solutions. But strong heuristic.

**Results this session**:
- `g3_BW_F257_hard_cases.output.txt`: 0 saturating ($\tau = 28$) $\alpha$
  in $\FF_{257}^2$ ($\alpha_3 = 1$, $\alpha_1, \alpha_2$ unrestricted)
  for both hard cases.
- `g3_BW_F257_max_agreement.output.txt`: BW at $t \in \{4, 5, 6, 7\}$
  ($\tau \in \{25, 26, 27, 28\}$) confirmed only boundary
  ($\alpha_1 = 0$ or $\alpha_2 = 0$) bad $\alpha$ at $\tau \leq 27$.
- `g3_BW_F257_interior.output.txt` **(strongest result)**:
  exhaustive INTERIOR enum over $(\FF_{257}^\ast)^2$ ($\alpha_1, \alpha_2 \neq 0$,
  $\alpha_3 = 1$), $\tau \in \{25, 26, 27, 28\}$:
  - $(17, 22, 25)$: 0 interior bad $\alpha$ at every $\tau$.
  - $(18, 25, 27)$: 0 interior bad $\alpha$ at every $\tau$.
  - Total wallclock: 12 minutes (95 sec per ($\tau$, triple)).

**Conclusion**: $|S_{\text{interior}}(\alpha)| \leq 24$ for all
interior $\alpha \in (\FF_{257}^\ast)^2$ in both hard triples — just one
above the cert+div threshold $d_\sigma = 23$. This is INDEPENDENT
empirical confirmation of $K_{\text{interior}}(\FF_{257}) = 0$ at
saturating threshold $\tau \geq 25$, complementing the msolve $\texttt{[-1]}$
result for the 6 fast cases.

The $\tau \in \{23, 24\}$ remainders ($t \in \{9, 8\}$) lie outside
unique-decoding radius and require Sudan list decoding (research-level
implementation: GS multiplicity $m \geq 10$ for $\tau = 23$, beyond
in-session compute).

## Recommended next steps

For paper2 v23 ePrint v2:
- Current §sec:open Q3 wording is ACCURATE: rigorous mod Q3 with
  explicit conditional structure, empirical confirmation at j=3, 4.
- Close Q3 either via:
  (a) Helleseth-Kumar import (research-level paper, weeks of work);
  (b) polymake/Sage NP mixed-volume computation at $(16, 8)$
      mixed-parity (computational, days of work);
  (c) Defer to follow-up paper / leave as open problem with full
      structural framework documented.

Paper2 v23 Table 1 row 1b stays "mod Q3 (twist-tower mixed-parity
sub-saturation)" until one of (a)-(c) lands.
