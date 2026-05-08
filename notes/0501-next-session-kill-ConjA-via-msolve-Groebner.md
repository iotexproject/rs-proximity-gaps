# Note 0501 — Next session: kill Conjecture A at deployment scale via msolve Gröbner

**Date:** 2026-05-05 iter 25 (post-compact handoff)
**Status:** Plan + state for the next session. Goal: rigorously eliminate
Conjecture A at deployment scale (paper2 §7 K_BW ≤ 2 unconditional at L_0).

## Goal

Make paper2 §7 K_BW ≤ 2 **fully unconditional at deployment scale** (i.e., at
all admissible primes $p \geq 97$, including $p \geq 2^{32}$ deployment primes),
removing the named "Conjecture A" entirely from paper2.tex.

## Current state (commit 2929665, May 5)

paper2 §7 has been upgraded:
- `thm:K-BW-2-structural` — title now reads "modulo consistency-variety
  emptiness" (was "modulo Conjecture A").
- `lem:no-alpha-only-tuple` — **PROVEN RIGOROUSLY** via degree counting:
  for any 33-tuple $J \subset \{0, ..., 127\}$, the column $w^{32}|_J$ cannot
  lie in the span of $\{1, w, ..., w^{31}\}|_J$ (since polynomial $w^{32} - p_{31}(w)$
  has degree 32, ≤ 32 roots, but $|J| = 33$).
- `cor:K2-zero-via-lemma` — derives K_2 = 0 IF $V_M(\mathbb{F}_p) = \emptyset$.
- `rem:V-M-empirical` — empirical verification across 805+ stratum (B) cases
  at $p \in \{97, 193, 257, 449, 577, 641, 769, 1153\}$, all $V_M(\mathbb{F}_p) = \emptyset$.
- Original `conj:zero-codeword-optimal` (Conjecture A) **still in paper2.tex**
  at line 2809-2818, but logically superseded by lemma+corollary.

The remaining gap: $V_M(\mathbb{F}_p) = \emptyset$ is empirical at small primes,
NOT yet proven over $\mathbb{Z}[\zeta_{128}]$. Bezout gives $|V_M(\mathbb{F}_p)| \leq 2^8 = 256$
universal — too loose to give K_2 = 0.

## What needs to happen

**Theorem to prove**: $V_M$ is empty as a scheme over $\mathbb{Z}[\zeta_{128}]$
for every relevant $80$-tuple $M \subset L_0 = \mu_{128}$.

**Equivalently**: $1 \in I_M$, where $I_M = \langle$ pair-resultants
$A_{J_1}(c, \omega) B_{J_2}(c, \omega) - A_{J_2}(c, \omega) B_{J_1}(c, \omega)$
for all $33$-tuple pairs $(J_1, J_2) \subset M \rangle + \langle$ kernel
constraints + cyclotomic relation $\Phi_{128}(\omega) = 0 \rangle$.

This is a Gröbner basis computation in
$\mathbb{Q}[\omega][c_1, \ldots, c_8] / (\Phi_{128}(\omega))$.

## Path: msolve Gröbner basis drill

msolve is installed at `/opt/homebrew/bin/msolve`. We have it.

### Day 1: setup symbolic system

Files to create:
- `notes/scripts/issue419_kill_conjA_genpoly.py` — generate explicit
  $A_J(c, \omega)$ and $B_J(c, \omega)$ for chosen 33-tuples $(J_1, J_2)$.
  Uses sympy. Output the polynomials in a format msolve can parse.

Concrete steps:
1. Pick S = [0, 1, 2, 3] at L_2 = (32, 8) (kernel basis can be derived).
2. Lift to L_0: f_u^{(0)}(w) = sum c_r w^{4r} for r ∈ U_{L_2}, etc.
3. Pick M = first 80 elements of $\{0, 1, ..., 127\}$ (or a more clever choice).
4. Pick $J_1, J_2 \subset M$, sizes 33 each.
5. Compute the augmented matrix $A_\alpha = [1, w^j, w^{2j}, ..., w^{31j},
   g_\alpha(w^j)]_{j \in J}$, take 33×33 determinant, expand into $\alpha A_J(c, \omega) + B_J(c, \omega)$.
6. Output A_J, B_J as polynomials in (c_1, ..., c_8, omega) where omega
   satisfies $\omega^{16} + 1 = 0$ (the minimal polynomial $\Phi_{128}$ has
   degree 64; but we can work with $\omega^{128} = 1$ and reduce).

**Important**: 8-dim kernel comes from S of size 16 → 24 - 16 = 8 free c's.
So 8 c-variables.

### Day 2: msolve run

Files:
- `notes/scripts/issue419_kill_conjA_msolve.in` — msolve input file with the
  polynomial system.
- Run: `msolve -f issue419_kill_conjA_msolve.in -o output.json`

msolve options to try:
- Default: `msolve -f input.ms -o out.json`
- For ideal containment of 1: check if 1 reduces to 0 via the GB.

If msolve takes too long (>1 day): reduce to a smaller test case first
(e.g., (16, 4) instead of (128, 32)). At (16, 4), kernel is 4-dim, much easier.

### Day 3: verify result

If GB contains 1:
- $V_M = \emptyset$ over $\overline{\mathbb{Q}}$ (and hence $\overline{\mathbb{F}_p}$
  for all $p$ NOT in the discriminant of the GB computation).
- Compute the discriminant set: list of "bad primes".
- For each bad prime, verify $V_M(\mathbb{F}_p) = \emptyset$ directly (full kernel
  enumeration).
- For primes outside discriminant: $V_M(\mathbb{F}_p) = \emptyset$ automatic.

If GB does NOT contain 1:
- The computation gives explicit V_M points (= candidate cex directions).
- Lift each to (α, c) and verify whether they actually give cex (rank ≤ 32 at M
  for the implied α).
- If a real cex emerges: paper2 §7 K_BW ≤ 2 needs **strengthening** — but
  empirically across 805+ tests this hasn't happened, so highly unlikely.

### Day 4-7: paper2 edit + cleanup

If V_M = ∅ proven:
1. Convert `cor:K2-zero-via-lemma`'s hypothesis into a Lemma.
2. **Delete** `conj:zero-codeword-optimal` (line 2809-2818).
3. **Delete or transform** `rem:conjA-status` (line 2820-2853).
4. **Update references** at lines 2157, 2921, 3497, 3506 to point to the new
   theorem structure.
5. Update `thm:K-BW-2-structural` title from "modulo $V_M = \emptyset$" to
   simply "Structural $K_{BW} \leq 2$" (no qualifier).
6. Compile paper2.pdf, verify clean.
7. Update STATE.md.
8. Commit + push.

## Fallback strategies if msolve too slow

**(1) Scale-down test**: do (16, 4) first. Kernel 4-dim, kernel constraint 8.
Pair-resultants degree 2 in 4 vars. Should be fast in msolve.
- Verify (16, 4) V_M = ∅ as scheme.
- This proves the (16, 4) inner Conj A unconditional.
- For (32, 8) and (128, 32): apply the same machinery; if msolve handles
  smaller cases, lift to larger.

**(2) Specific subset of pair-resultants**: instead of all $\binom{80}{33}$
pair-resultants, pick a small subset that suffices to cut V_M to 0. By
Bezout, $\leq 8$ pair-resultants suffice generically.
- Pick 8 pair-resultants at random or via heuristic.
- Compute GB on just those 8.
- If GB contains 1: V_M = ∅ proven. (Smaller computation.)
- Risk: 8 pair-resultants might not generate enough to give $1 \in I$. May
  need to add more iteratively.

**(3) Alternative structural argument**: instead of Gröbner, find a
character-sum or Niho-type argument that bounds K_2 by an explicit constant
< 1. Probably 2-4 weeks of math investigation. Lower priority than Gröbner.

## Concrete starting commands (post-compact)

```bash
cd /Users/raullenstudio/work/EF1M

# Verify state
git log --oneline -3
# Should show: 2929665 paper2 §7 Conjecture A: ...

cat notes/0501-next-session-kill-ConjA-via-msolve-Groebner.md

# Start with the (16, 4) scale-down test
ls notes/scripts/issue419_kill_conjA_*  # should be empty initially

# First task: write polynomial generator
# File: notes/scripts/issue419_kill_conjA_16_4_genpoly.py
# Generate the pair-resultants symbolically using sympy
```

## Key technical objects (cheat sheet)

- $L_0 = \mu_{128}$, $\omega \in \mathbb{F}_p$ primitive 128-th root.
- paper2's lifted construction: $g_\alpha(w) = f_u^{(0)}(w) + \alpha f_v^{(0)}(w)$
  on $L_0$, where $f_u, f_v$ live on $L_2 = \mu_{32}$ with stratum (B)
  cross-side $K = 16$ (Fourier supp $[8, 32)$ split mod-4).
- $\tau_{BW} = (n_0 + k_0)/2 = (128 + 32)/2 = 80$.
- Kernel: 16 linear constraints (S of size 16 at L_2) on 24 c-vars
  → 8-dim kernel.
- $A_J(c, \omega), B_J(c, \omega)$: linear in c, polynomial in $\omega$.
- Pair-resultant $R_{J_1, J_2} := A_{J_1} B_{J_2} - A_{J_2} B_{J_1}$:
  degree 2 in c.
- Number of $33$-tuples in $M$: $\binom{80}{33} \approx 1.7 \times 10^{23}$
  — too many to enumerate. Use a small subset.

## Decision tree (for next session)

```
Start →
  Try msolve at (16, 4) scale (simplest)
  ├─ Success → scale up to (32, 8), then (128, 32)
  │   └─ Success → V_M = ∅ proven, do paper edits
  └─ msolve too slow / fails →
     ├─ Try Bezout-style heuristic (8 random pair-resultants)
     ├─ Try alternative structural (Niho cross-correlation bound)
     └─ Fallback: declare Bezout 256 + finite-prime check, accept
        K_BW ≤ 258 unconditional + K_BW ≤ 2 modulo V_M empty
```

## Confidence

- **Complete via msolve in 1-2 weeks**: 75% (computation tractable; main
  risk is wall-clock cost of cyclotomic Gröbner).
- **At (16, 4) only**: 95% (small problem, sympy or msolve trivial).
- **At (128, 32) directly**: 50% (large problem; might need (16, 4) → (32, 8)
  → (128, 32) scale-up via uniform argument).
- **Conj A fully eliminated from paper2 in next session**: 60-70%.

## Honest assessment

This is **paperwork + computation**, not a hard math problem. The lemma +
corollary structure is in place; the only remaining task is to verify
$V_M = \emptyset$ as a scheme. msolve handles 8-variable degree-2 systems
in cyclotomic rings as a standard task.

The session should produce:
- Either: rigorous proof V_M = ∅, hence Conj A killed, paper2 K_BW ≤ 2 unconditional.
- Or: detailed analysis of exact Gröbner output, with explicit identification of
  any unexpected V_M points.

Either outcome is a clear deliverable.

## Files that exist (reference)

- paper2.tex (commit 2929665)
- paper2.pdf (compiled clean, 417 KiB)
- STATE.md
- notes/0492-0500*.md (the structural attack drill log)
- notes/scripts/issue419_path_A_*.py (path A symbolic + diag scripts)

## Files to create next session

- notes/scripts/issue419_kill_conjA_16_4_genpoly.py (sympy: symbolic polys)
- notes/scripts/issue419_kill_conjA_16_4_msolve.in (msolve input)
- notes/scripts/issue419_kill_conjA_16_4_msolve.out (msolve output)
- notes/scripts/issue419_kill_conjA_32_8_genpoly.py (lift to (32, 8))
- notes/scripts/issue419_kill_conjA_128_32_genpoly.py (lift to (128, 32))
- notes/0502-msolve-result-V_M-empty.md (or similar — result note)

## Acknowledged limitation

If msolve takes too long at (128, 32), we can fall back to (16, 4) + (32, 8)
at smaller scales. By the recursion lem:L2-recursion in paper2, the (128, 32)
Conj A (at deployment scale) reduces to (32, 8) and (16, 4) inner Conj A's.
If both inner Conj A's are proven via msolve, the deployment-scale claim
follows.

(8, 2) Conj A is NOT in the recursion path for paper2's L_0 K_BW ≤ 2
(since the recursion descends from L_0 = (128, 32) to L_2 = (32, 8) inner,
and L_1-factored to (16, 4), neither going through (8, 2). The (8, 2) anomaly
where K_2 = 1 holds is irrelevant to the deployment claim.)
