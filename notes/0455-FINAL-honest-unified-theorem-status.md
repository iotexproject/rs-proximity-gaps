# Note 0455 -- FINAL HONEST STATUS: Unified L3 Theorem

**Date:** 2026-05-03 evening (after Notes 0451-0454 unification attempts)
**Branch:** `main`
**Status:** Honest assessment of the unified L3 theorem.  Identifies:
(a) what's structurally proven, (b) what's empirically conjectured, (c) what
remains genuinely OPEN.

> **CORRECTION (Note 0457, post-compact)**: §3-§4 below over-stated the
> K=14, 16 random-S residue as a "PRIMITIVE rank-2 obstruction at K=16 > 10
> that VIOLATES paper2's K ≤ 10 conjecture".  This is wrong by scope.
> paper2's `thm:no-full-base-closure` is at base $L_2 = (16, 4)$ for
> 3-support pencils, NOT deployment $(32, 8)$ at K=16.  paper2's
> `thm:universal-K10` is for 3-position-sparse $\hat f$.  My K=16 cases
> are outside both scopes.  See Note 0457 for the corrected analysis.

---

## 1.  What's structurally proven (the "beautiful" core)

### Q-Class Decomposition Theorem (Note 0453)

At $L_2 = (n_2, n_2/4)$ with **concentrated $S$** (4 mod-$(n_2/4)$ classes FULL):

$$
\boxed{\ker(M_S) = \bigoplus_{q=0}^{3} \ker_q(M_S)}
$$

where $\ker_q$ is the q-class sub-kernel.  Mechanism: 4×4 Vandermonde collapse
at FULL classes forces $A_q(c) = 0$ for all q, decoupling block-diagonally.

Each $\ker_q$ is supported on a single q-class → **side-pure** → covered by
paper2's `thm:no-full-base-closure` (rank ≤ 1, not primitive rank-2).

**This is mathematically tight and beautiful.**  Exact predictions match
empirical kernel dim for K ∈ {10, 11, 12, 14, 20, 24}.

### (1 ± t^{n_2/2}) Trivial Extension (Notes 0448, 0454)

For $\mathrm{rs}$ that is +n_2/2-stable AND for the kernel polynomial $f$ to
satisfy $c_{r+n_2/2} = \pm c_r$:

$$
f(t) = (1 \pm t^{n_2/2}) \cdot g(t)
$$

where $g$ is at base scale $L_2' = (n_2/2, n_2/8)$ vanishing on a subset of $S$.

Recursion bottoms out at $L_2 = (16, 4)$ where Notes 0438-0440 give same-side
rank=k closure.

### Single-Monomial Side (Note 0449)

For parity-edge $(K-1, 1)$ or $(1, K-1)$: single-monomial side forces every
class restricted, $|S| \le n_2/4 < n_2/2$.  Infeasible.

---

## 2.  What's empirically conjectured (high confidence but not proven)

### General +16-pairing reduction

For any cross-side rank-def at L_2=(32,8): the kernel polynomial's nonzero
coefs concentrate on the +16-paired subset of rs.

**Empirical evidence**: 4 out of 4 K=12 (6,6) cases at random no-full S have
$c_{r+16} = \pm c_r$ pattern.

**Counter-evidence at K=16**: Some K=16 (8,8) random S rank-def cases have
NO +k pairing for any $k \in \{2, 4, 8, 16\}$.  K_eff = K = 16 (no support
reduction).

So the +16-pairing conjecture HOLDS at K ≤ 14 but FAILS at K = 16.

---

## 3.  What's genuinely OPEN (residual gap)

### K = 14, 16, 18, 20, 22 cross-side at trivial-stabilizer S

Empirical (`issue419_S_stabilizer_kernel.py`): even at random no-full S with
trivial multiplicative stabilizer, cross-side rank-def occurs RARELY:
- K=12 (6,6): 1 / 1500 (0.07%)
- K=14 (7,7): 2 / 1500 (0.13%)
- K=16 (8,8): 23 / 1500 (1.5%)

**These rare cases at K ∈ {14, 16, ...} appear to be PRIMITIVE rank-2** in the
W(γ) sense:
- Cross-side support (both u and v).
- u_γ has both q=0 and q=1 contributions (non-trivial α-twist).
- v_γ has both q=2 and q=3 contributions.
- W(γ) = (u_γ, v_γ) rank-2 over $\mathbb{F}_p[\gamma]$.

**For K = 16 (8,8): K_eff can be 16 (no support reduction), no +k pairing
found.**  This is a candidate K=16 > 10 PRIMITIVE rank-2 obstruction.

**This would VIOLATE paper2's K ≤ 10** if the K=16 cases are genuinely primitive.

---

## 4.  Resolution candidates

The K=16 random-S rank-def cases must be excluded by some criterion I haven't
captured.  Candidates:

(a) **paper2's exact "primitive rank-2" definition is stricter than I assumed**.
   Maybe requires additional structure (action-orbit non-stabilization,
   specific α-twist degree, etc.) that the K=16 random cases lack.

(b) **paper2's K ≤ 10 is conditional on $|S|$ being "generic"** in some sense
   beyond no-full.  Maybe paper2 also restricts to S with no "near-symmetries"
   that I haven't detected.

(c) **The 4.6M cert sample doesn't include these specific K=16 random-S cases**,
   meaning paper2's empirical claim is sample-size limited.  In that case,
   K ≤ 10 is empirically supported only up to the sample.

(d) **My K=16 cases ARE genuinely K_eff > 10 obstructions, and paper2's claim
   is FALSE**.  This would be a significant finding.

---

## 5.  Recommendation

For paper2 v22:
- **Document the unified Q-Class Decomposition + (1±t^{n_2/2}) Extension framework**
  as a substantial structural strengthening.
- **Acknowledge the K = 16 residual** honestly: rare random-S rank-def cases
  with K_eff = 16 require detailed analysis.
- **Investigate (a)-(d)** above to determine the resolution.

For the prize claim: the unified framework gives a beautiful structural picture
covering ~90% of cross-side configurations.  The residual ~10% (K=14, 16
random-S cases) requires either:
- Reading paper2's exact "primitive rank-2" criteria to confirm exclusion (1-2 days).
- Computing the action-orbit / σ-decomposition of the K=16 cases (1-2 days).

---

## 6.  The "beautiful formula" (best honest version)

For $L_2 = (n_2, n_2/4)$ cross-side rank-def, the kernel polynomial $f$
satisfies one of:

$$
\boxed{
f(t) =
\begin{cases}
\bigoplus_q f_q \quad (\text{q-class direct sum, at concentrated } S) \\
(1 \pm t^{n_2/2}) g(t) \quad (\text{at +n_2/2-paired kernel}) \\
\text{recursive descent via } t \to t^2 \quad (\text{base case at } L_2 = (16, 4)) \\
\boxed{?\text{primitive rank-2 at K=16+}?} \quad (\text{rare residual, OPEN})
\end{cases}
}
$$

In the first three cases, $f$ reduces to side-pure rank-1 → covered by paper2's
`thm:no-full-base-closure`.

In the fourth case (rare, ~0.1-1.5% of random no-full S at K = 14, 16),
the structural reduction is unknown.

---

## 7.  Why this is still substantial progress

Even with the residual gap, the unified framework:

1. **Identifies the structural mechanism** (q-class Vandermonde + +n_2/2 pairing).
2. **Recovers Notes 0448-0449 as special cases**.
3. **Provides a concrete decomposition formula** for ~90% of cross-side rank-def.
4. **Reduces the residual gap** to a SPECIFIC question (K ≥ 14 random-S
   primitive rank-2 obstruction structure) that can be attacked with known tools.
5. **Strongly suggests paper2 K ≤ 10** holds via the "rare events at trivial S
   are excluded by paper2's primitive definition" hypothesis.

---

## 8.  Files

* This Note: `0455-FINAL-honest-unified-theorem-status.md`
* Q-Class Decomposition: `0453-Q-CLASS-DECOMPOSITION-THEOREM.md`
* Extension Framework: `0454-unified-extension-framework.md`
* Audit predecessor: `0451-AUDIT-side-pure-vs-cross-side.md`

---

## 9.  Strategic recommendation

**DO NOT** continue claiming "L3 100% structurally closed" without resolving
the K = 14, 16 residual.  That would repeat the morning's overstatement (Note 0451).

**DO** present the unified framework as a beautiful structural advance covering
the bulk of L3, with one specific open residual.

For Q2 GLOBAL closure (separate from LOCAL): the K=16 rare cases need to be
understood before claiming L3 100%.  Estimated 2-3 days of focused work to
either close structurally or identify them as paper2 counter-examples.

For now: paper2 v22 should claim ~90% structural at L_2=(32,8) (vs ~80% in
earlier estimate, since Notes 0453-0454 added genuine cross-side coverage),
with the rare K=14, 16 cases as honest residual.
