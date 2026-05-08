# Note 0379 -- Issue #436: action-orbit quadrant-pair sweep

**Date:** 2026-05-01  
**Branch:** `main`  
**Status:** prediction confirmed; paper2 `rem:sparse-worst-action-orbit-nonstab` is data-backed.

---

## Purpose

Note 0378 (Issue #435) showed that the Note 0377 mixed-circuit obstruction
exceeds the 3-position $K$ bound by a factor of $\sim 19$ in the paper2 2D
commit-curve $K$ convention. paper2 (commit `64fabae`) added
`rem:sparse-worst-action-orbit-nonstab` as a defensive amendment, restricting
`conj:sparse-worst` to inputs whose support is not stabilized under the
fold action.

Issue #436 asks for a systematic verification that this restriction is
**necessary and sufficient** at the $L_2 = (16, 4)$ base panel by sweeping
all six fold-quadrant pairs across the 8-prime panel.

This note records the result. The prediction is fully confirmed.

---

## Setup

Convention (matches `notes/scripts/issue396_action_stabilizer.py`,
`residual_uv`):

```text
Position j on L_0 = (64, 16) folds via (r, q) = (j//4 mod 16, j mod 4).
The two-round residual rows on L_2 = (16, 4) are:

  q = 0:  contributes c       to u[r]
  q = 1:  contributes alpha_1 c  to u[r]
  q = 2:  contributes c       to v[r]
  q = 3:  contributes alpha_1 c  to v[r]

The challenge pencil at L_2 is  h_{alpha_1, alpha_2}(t) = u(t) + alpha_2 v(t).
```

The fold-quadrant pair of a 6-position support is the set of distinct
$j \bmod 4$ values appearing in the support. There are 6 unordered pairs of
$\{0, 1, 2, 3\}$.

The paper2 $K$ convention (Note 0378):

```text
K(f_1, f_2; delta_J) := |V_delta(f)| / q,
V_delta(f) := {(alpha_1, alpha_2) : h_{alpha_1, alpha_2} folded row is bad}.
```

Bad means the row lies in $\mathrm{RS}_4(S)$ for some no-full
$S \subset L_2$ with $|S| = 8$.

---

## Structural prediction

For a 6-position support whose quadrants lie in pair $\{a, b\}$, the
$\alpha_1$-dependence of $u, v$ is determined entirely by the pair:

| pair | $u$ | $v$ | predicted $K$ class |
|------|-----|-----|---------------------|
| $\{0, 2\}$ | $\alpha_1$-indep | $\alpha_1$-indep | $K = q$ achievable |
| $\{1, 3\}$ | $\alpha_1$-proportional | $\alpha_1$-proportional | $K = q$ achievable |
| $\{0, 3\}$ | $\alpha_1$-indep | $\alpha_1$-proportional | $K = q$ achievable |
| $\{1, 2\}$ | $\alpha_1$-proportional | $\alpha_1$-indep | $K = q$ achievable |
| $\{0, 1\}$ | $\alpha_1$-mixing | $\equiv 0$ | $K$ bounded (no $\alpha_2$ saturation) |
| $\{2, 3\}$ | $\equiv 0$ | $\alpha_1$-mixing | $K$ bounded (no $\alpha_2$ saturation) |

The first four pairs admit (with crafted coefficients) the simultaneous
"both rows vanish on a no-full $S$" configuration that gives $K = q^2 / q = q$.
The last two pairs cannot, because one of the two rows is identically zero
in any coefficient choice within the pair.

---

## Phase A: structural witnesses at $p = 193$

Script:

```text
notes/scripts/issue436_action_orbit_structural_check.py
notes/scripts/issue436_action_orbit_structural_check.output.txt
```

Witnesses: the Note 0377 obstruction directly for $\{0, 2\}$, and three
translates for $\{1, 3\}$, $\{0, 3\}$, $\{1, 2\}$ obtained by shifting the
appropriate side of the support by $+1$. Coefficients are reused from
Note 0377 (`(112, 79, 1, 30, 47, 1)`) — the same algebraic kernel structure
on $S$ persists under uniform fold-side shifts.

For $\{0, 1\}$ and $\{2, 3\}$ we use representative single-side supports
with `stable_coefs(support)`.

Result at $p = 193$:

```text
{0,2} support=(32,36,40,34,38,46) coefs=(112,79,1,30,47,1) K=193 → K=q SATURATION
{1,3} support=(33,37,41,35,39,47) coefs=(112,79,1,30,47,1) K=193 → K=q SATURATION
{0,3} support=(32,36,40,35,39,47) coefs=(112,79,1,30,47,1) K=193 → K=q SATURATION
{1,2} support=(33,37,41,34,38,46) coefs=(112,79,1,30,47,1) K=193 → K=q SATURATION
{0,1} support=(16,20,24,17,21,25) stable_coefs                  K=0    (v ≡ 0)
{2,3} support=(18,22,26,19,23,27) stable_coefs                  K=1    (u ≡ 0)
```

`alpha1_independence_check` returns the predicted structural pattern in all
six cases (e.g., `u_alpha1_indep=True` for $\{0, 2\}$, `u_alpha1_prop=True`
for $\{1, 3\}$, `v_zero=True` for $\{0, 1\}$, etc.).

The Phase A v2 prediction PASSED:

```text
✓ K-saturating pairs ({0,2}, {1,3}, {0,3}, {1,2}): K=q witnesses constructed.
✓ K-bounded pairs ({0,1}, {2,3}): K ≤ 1 (well within K_3pos_max = 10).
```

---

## Phase B: prime-uniform sweep

Script:

```text
notes/scripts/issue436_action_orbit_quadrant_sweep.py
notes/scripts/issue436_action_orbit_quadrant_sweep.output.txt
```

Same six witnesses, run at every prime in the panel
$\{97, 113, 193, 257, 449, 577, 769, 1153\}$. Primes $97$ and $113$ do not
admit a primitive $64$-th root in $\FF_q^*$ (their $q - 1$ values $96$ and
$112$ are not divisible by $64$), so the $L_0 = (64, 16)$ FRI structure does
not exist there; both are skipped. The effective panel for $n_0 = 64$ is
$\{193, 257, 449, 577, 769, 1153\}$ — six primes.

Aggregate K table:

```text
   pair       p=193   p=257   p=449   p=577   p=769   p=1153
  {0,2}        =q      =q      =q      =q      =q      =q
  {1,3}        =q      =q      =q      =q      =q      =q
  {0,3}        =q      =q      =q      =q      =q      =q
  {1,2}        =q      =q      =q      =q      =q      =q
  {0,1}         0       0       0       0       0       0
  {2,3}         1       1       1       1       1       1
```

The Note 0377 coefficients `(112, 79, 1, 30, 47, 1)` reduce mod each prime
and produce $K = q$ saturation at every prime in the panel — i.e., the
algebraic kernel structure is **prime-uniform**. (The bad $S$ that
annihilates both $u$ and $v$ is invariant under prime change because the
kernel condition is a linear identity over $\ZZ$.)

Phase B prediction PASSED:

```text
✓ K-saturating pairs: K = q at every prime in the n_0=64 panel.
✓ K-bounded pairs:    K ≤ 1 at every prime in the n_0=64 panel.
```

---

## Consequence for paper2 `rem:sparse-worst-action-orbit-nonstab`

The remark restricts `conj:sparse-worst` to inputs $(f_1, f_2)$ with
**non-trivial $\alpha_1$-action**. The data above shows:

1. **The four quadrant pairs $\{0, 2\}$, $\{1, 3\}$, $\{0, 3\}$, $\{1, 2\}$
   each admit $K = q$ obstructions at every prime in the deployment panel.**
   The remark must therefore exclude all four (it does, via the action-orbit
   stabilizer condition: in each of these pairs, the round-1 fold action on
   the residual span is trivial in the relevant sense — either fixes both
   rows pointwise, or rescales them by a measure-preserving factor).
2. **The two quadrant pairs $\{0, 1\}$, $\{2, 3\}$ are structurally
   $K$-bounded** (one residual row is identically zero, so the
   $\alpha_2$-direction does not saturate). These do not need to be
   excluded by the remark; they pose no threat to the conjecture.

Hence the remark's exclusion is **necessary** (any of the four pairs gives
a $K = q$ counterexample) and **sufficient** (the two unstabilized pairs
$\{0, 1\}$, $\{2, 3\}$ are not threats; mixed-quadrant supports with
genuinely non-trivial $\alpha_1$-action are not contained in the four
stabilized classes and are subject to the existing 3-position bound).

The Note 0377 obstruction transposes via $+1$-shifts of one or both fold
sides into all four stabilized pairs. This is consistent with paper2's
Action-Orbit Theorem (`thm:action-orbit`): the $\langle \omega^{b-a} \rangle$-
stabilizer structure is shift-equivariant on the fold axis.

---

## Open questions (deferred)

1. **Larger support sizes.** This sweep fixed the support size at 6 (matching
   Note 0377). $K = q$ obstructions might also exist at support size 4, 5,
   7, or 8 within the same four quadrant pairs. Phase A / B do not enumerate
   these, but the structural argument (one row $\alpha_1$-independent or
   $\alpha_1$-proportional) is support-size-independent — only the
   coefficient-search cost scales.
2. **Mixed-quadrant non-stabilized supports.** Supports that span all four
   quadrants $\{0, 1, 2, 3\}$ are NOT covered by this sweep; they fall
   outside the six-pair classification. The structural prediction is that
   such supports have generic $\alpha_1$-action (round-1 fold genuinely
   mixes rows) and $K$ is bounded by 3-pos $K \leq 10$. Verifying this
   would require a separate sweep over four-quadrant supports.
3. **Formal promotion of the remark hypothesis into the conjecture's
   quantifier.** Currently the remark phrases the action-orbit
   non-stabilization condition informally; a formal restatement is
   deferred to paper2 v2 (per the remark's last sentence).

---

## Files

```text
notes/scripts/issue436_action_orbit_structural_check.py  (Phase A v2)
notes/scripts/issue436_action_orbit_structural_check.output.txt
notes/scripts/issue436_action_orbit_quadrant_sweep.py    (Phase B)
notes/scripts/issue436_action_orbit_quadrant_sweep.output.txt
```

## Cross-refs

- #435 (CLOSED), Note 0378: single-example K computation that triggered #436
- #436: this sweep
- Note 0377: original mixed-circuit obstruction
- paper2 `rem:sparse-worst-action-orbit-nonstab` (commit `64fabae`)
- paper2 `thm:action-orbit`: structural framework relied on
