# Note 0456 -- HANDOFF after compact

**Date:** 2026-05-03 late evening (before user-requested compact)
**Branch:** `main` (clean, all committed and pushed up to commit 06d4fb0)

This note is the AUTHORITATIVE handoff state after this session.  Read this
first when continuing.

---

## 1.  Where we are (one sentence)

L3 (deployment $L_2=(32, 8)$) Q2 LOCAL closure: **~90% structural via the
unified Q-Class Decomposition + (1±t^{n_2/2}) extension framework (Notes
0453-0454)**, with one honest residual: K=14, 16 rare cross-side rank-def at
random no-full $S$ that appear primitive rank-2 in W(γ) sense (Note 0455).

---

## 2.  Today's note chain (READ IN THIS ORDER)

1. **0451** — AUDIT: side-pure vs cross-side conflation; morning's claims
   reduced to ~80% honest cross-side coverage.
2. **0452** — Final L3 status pre-unification: cross-side configurations at
   L_2=(32, 8) by K and parity.
3. **0453** — **Q-Class Decomposition Theorem** (the beautiful core):
   ker(M_S) = ⊕_q ker_q(M_S) at concentrated S.  Predicts kernel dim
   exactly via Σ max(0, m_q - 4).
4. **0454** — (1 ± t^{n_2/2}) extension framework for non-concentrated S
   with +16-paired kernels.
5. **0455** — FINAL HONEST STATUS: ~90% structural + ~10% K=14, 16 residual.

Earlier today's notes (0438-0450) are in scope but per Note 0451 are largely
"bonus" (same-side closures auto-covered by paper2's `thm:no-full-base-closure`).
The morning's "Side-Row Vanishing Lemma" framework is technically true at base
$L_2=(16, 4)$ but unnecessary for Q2 LOCAL.

---

## 3.  The "beautiful unified formula" (best honest version)

For cross-side rank-def $f$ at $L_2 = (n_2, n_2/4)$:

$$
\boxed{
f(t) =
\begin{cases}
\bigoplus_q f_q & \text{(q-class direct sum, at concentrated } S\text{)} \\
(1 \pm t^{n_2/2}) g(t) & \text{(at +n_2/2-paired kernel)} \\
\text{recursive descent via } t \to t^2 & \text{(base case } L_2=(16,4)\text{)} \\
\text{?primitive at K=14, 16?} & \text{(rare residual, OPEN)}
\end{cases}
}
$$

The first three cases reduce $f$ to side-pure rank-1, automatically excluded
by paper2's `thm:no-full-base-closure`.  The fourth case is the residual.

---

## 4.  THE RESIDUAL (what's actually open)

**Empirical**: at random no-full $S$ with **trivial multiplicative stabilizer**,
cross-side rank-def occurs RARELY:
- K=12 (6,6): 1 / 1500 (0.07%)
- K=14 (7,7): 2 / 1500 (0.13%)
- K=16 (8,8): 23 / 1500 (1.5%)

K=14 cases: all have +16-pairing structure (c_{r+16} = ±c_r).  Covered by
Note 0454's (1±t^16) extension.

**K=16 cases**: SOME have **no +k pairing for any k ∈ {2, 4, 8, 16}**.
K_eff = 16 with ALL coefs nonzero.  In W(γ):
- Cross-side ✓
- u_γ has both q=0 and q=1 (non-trivial α-twist on u-side) ✓
- v_γ has both q=2 and q=3 (non-trivial α-twist on v-side) ✓
- W(γ) = (u_γ, v_γ) is rank-2 over $\mathbb{F}_p[\gamma]$ (disjoint t-supports)

**This appears to be a PRIMITIVE rank-2 obstruction at K=16 > 10**, which
would VIOLATE paper2's K ≤ 10 conjecture.

But paper2's 4.6M certs supposedly found 0 counter-examples.  So one of:
1. paper2's "primitive rank-2" definition is stricter than I assumed (excludes these).
2. paper2's empirical sample didn't include these specific patterns.
3. paper2 K ≤ 10 has a counter-example.

---

## 5.  Concrete next steps (in order of payoff)

### Option A (fastest, 1-2 days): Read paper2's exact primitive definition

Look at paper2 source for the precise definition of "primitive rank-2 W(γ)
obstruction" and "no-full base closure".  Check if my K=16 cases satisfy ALL
the criteria or are excluded by some subtler condition (e.g., σ-orbit
non-stabilization, action-orbit triviality, specific Vandermonde rank, etc.).

Specifically check:
- `paper2/proofs/no-full-base-closure.tex` (or similar)
- `paper2/notation/primitive-rank-2.tex`
- `paper2/sec_K10/` directory

If paper2 implicitly excludes my K=16 cases: GREAT, just verify and update
Note 0455 to close the residual.

If paper2 doesn't exclude them: investigate Option B.

### Option B (deeper, 2-3 days): W(γ) + action-orbit analysis of K=16 cases

For the 23 K=16 (8,8) rank-def cases at random S:
- Compute W(γ) explicitly.
- Verify rank-2 over $\mathbb{F}_p[\gamma]$.
- Compute action-orbit (orbit of f under multiplicative group of $\mathbb{F}_p^*$ acting on coefs).
- Check σ-orbit (size 1 or 2).
- Check translation orbit (rare since random S has trivial stab).
- Check Bluher-style structure (per Notes 0306, 0310).

Identify the "type" of these cases.  If they fit some paper2-known
exclusion category, document and close.

### Option C (sanity check, 1 day): Larger random-S sample

Currently tested with 500 random no-full S × ~50 configs = ~25k tests per (K, parity).
Run 5x more samples (~125k) to verify residual rate is ~1.5% at K=16, not artifact.

If rate stable: the residual is real.  If rate drops sharply with more samples:
maybe it's sample-size artifact.

### Option D (alternative, 1-2 days): Switch to L1+L2 work

User mentioned earlier: "或者先 pause L3, 搞 L1+L2, 回头再看".

L1 (Tier 1c |A|=2 / |A|=0 strict $\mathbb{Z}[\omega_{16}]$ closure): tedious
but well-defined; use sympy/SageMath.  3-5 days.

L2 (side-(3,1)/(1,3) parity at $L_2=(16, 4)$): structurally OPEN per Note
0417.  Three approaches sketched in handoff.  1-3 weeks for first insight.

---

## 6.  Key scripts (recently created, all on git)

Q-Class Decomposition + Extensions:
- `notes/scripts/issue419_unified_theorem_verify.py` — Q-Class Decomp empirical
- `notes/scripts/issue419_critical_K_gt_10_check.py` — K > 10 check
- `notes/scripts/issue419_K20_concentrated_check.py` — K=20 specific
- `notes/scripts/issue419_crossside_concentrated_S.py` — concentrated S scan
- `notes/scripts/issue419_crossside_unified_scan.py` — random S scan

(1+ct²)/(1±t^16) extensions:
- `notes/scripts/issue419_qclass_decomp_general_S.py` — q-class at general S
- `notes/scripts/issue419_nonconc_kernel_inspect.py` — kernel structure
- `notes/scripts/issue419_sigma_isotype_check.py` — σ-iso check (deprecated)
- `notes/scripts/issue419_sigma_decomp_kernel_space.py` — σ-iso kernel space
- `notes/scripts/issue419_plus16_decomp.py` — +16 decomposition

Residual investigation:
- `notes/scripts/issue419_S_stabilizer_kernel.py` — stabilizer / rank-def correlation
- `notes/scripts/issue419_rare_random_kernel.py` — rare K=14, 16 cases inspection

K=12 closure (Note 0448):
- `notes/scripts/issue419_k12_*.py` (5 scripts)
- `notes/scripts/issue419_k_full_scale_lift.py`

Other afternoon work:
- `notes/scripts/issue419_kall_parityedge_n32.py`
- `notes/scripts/issue419_k4_parity31_uside_n32.py`
- `notes/scripts/issue419_k4_5_sameq_n32.py`
- `notes/scripts/issue419_k6_33_n64.py`
- `notes/scripts/issue419_k6_sameq_*.py`
- `notes/scripts/issue419_k6_33_targeted.py`

---

## 7.  Memory log entry

`memory/logs/2026-05-03.md` has full session log including the Notes 0451-0455
afternoon/evening progression.  See "Late afternoon / evening (post Notes
0448-0450)" section.

---

## 8.  Repo state

- Branch: `main`
- Latest commit: 06d4fb0 (Note 0455)
- Working tree: CLEAN (after STATE.md + memory log updates committed below)
- Pushed to: github.com/raullenchai/ef1m

---

## 9.  My recommendation for next session

**Start with Option A** (read paper2's primitive definition).  It's the cheapest
path to either close the residual or confirm a real gap.

If Option A inconclusive after 1 day: switch to Option C (larger sample) to
verify residual rate, then Option B (W(γ) analysis).

**Don't claim L3 100% structural** without resolving the residual.  Note 0451
documented the morning's overstatement; don't repeat.

The unified Q-Class Decomposition (Note 0453) is the "beautiful theorem" the
user asked for.  It's mathematically tight and elegant.  The residual (~10%)
is honest and documented.
