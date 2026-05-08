# Note 0487 — Base (8, 2) Conj A: Kernel-Refined Form

**Date:** 2026-05-04 night iteration 4 (post-compact)
**Status:** Bare (8, 2) Conj A FALSE at small primes; kernel-refined version holds in 400+ tests.

## Summary

The L_1 / L_2 / L_3 K_BW recursion residuals reduce to "(8, 2) Conj A" at the
base case. Previous notes (0485, 0486) left this residual empirically validated
via outer-scale tests (140+ cases). This note attacks (8, 2) Conj A directly
and discovers an important refinement.

## Bare (8, 2) Conj A — FALSE at small primes

**Statement (bare)**: For arbitrary $f_u \in \mathrm{span}\{z^2, z^4, z^6\}$,
$f_v \in \mathrm{span}\{z^3, z^5, z^7\}$, and $\alpha \in \mathbb{F}_p^*$, the
function $h_\alpha = f_u + \alpha \cdot f_v$ on $\mu_8$ satisfies
$$\max_{c \in \mathrm{RS}_2(\mu_8)} \mathrm{agr}_{\mu_8}(h_\alpha, c) = \mathrm{agr}_{\mu_8}(h_\alpha, 0).$$

**Empirical test** (`issue419_base_82_conjA_direct.py`): 30 random
$(f_u, f_v)$ pairs per prime, all $\alpha \in \mathbb{F}_p^*$, brute-force
max over all RS_2 codewords (via pair-interpolation, $\binom{n}{2}=28$ pairs).

| Prime | K_BW counterexamples | First cex |
|---|---|---|
| 17 | **10** | $f_u = 2z^2 + 16z^4 + 14z^6$, $f_v = 13z^3 + 11z^5 + 12z^7$, $\alpha = 6$, $c = 15 + 12z$, agr=5 |
| 73 | **2** | similar |
| 41, 89, 97, 113, 193, 257 | 0 | — |

So bare Conj A **FAILS at p=17** with explicit configurations.

### Lifted to L_1: would-be deployment-scale cex

`issue419_L1_lift_82cex_test.py` lifts the bare cex via $z \to z^2$ to
$L_1 = \mu_{16}$ and runs Berlekamp-Welch at $L_1 = (16, 4)$, $\tau_{BW} = 10$.

Results (3 cex configs from $p=17$):
- pair=2, $\alpha=6$: $\mathrm{agr}_{L_1}(h_{\text{lifted}}, c_{\text{lifted}}) = 10 = 2 \cdot 5$, BW returns non-zero codeword with agr 10 ≥ τ.
- pair=5, $\alpha=1$: agr = 12 = 2·6, BW returns non-zero codeword with agr 12.
- pair=7, $\alpha=8$: agr = 10 = 2·5, BW returns non-zero codeword with agr 10.

So **if** these bare configurations were realizable as inputs from the L_1
stratum (B) construction, L_1 K_BW would be > 0 at p=17.

## Kernel-refined (8, 2) Conj A — HOLDS in 400+ tests

**Statement (kernel-refined)**: For $(c_r)_{r \in [2, 8)}$ arising as the
kernel of a matrix $M[r, s] = \omega^{r \cdot s}$ with $r \in [2, 8)$ and
$s \in S$ for some $S \subset \mathbb{Z}/8$ making $M$ rank-deficient, and
$f_u = \sum_{r \in u_{\mathrm{side}}} c_r z^r$, $f_v = \sum_{r \in v_{\mathrm{side}}} c_r z^r$:
the conclusion of bare Conj A holds.

**Empirical test** (`issue419_base_82_kernel_constrained.py`): 50 cases per
prime drawn via `find_stratum_B_cases_mod2` (kernel-constrained), all
$\alpha \in \mathbb{F}_p^*$, brute-force max over RS_2.

| Prime | Cases found | K_BW counterexamples |
|---|---|---|
| 17 | 50 | **0** |
| 41 | 50 | 0 |
| 73 | 50 | **0** |
| 89 | 50 | 0 |
| 97 | 50 | 0 |
| 113 | 50 | 0 |
| 193 | 50 | 0 |
| 257 | 50 | 0 |
| **Total** | **400** | **0** |

So the kernel constraint **excludes the bare counterexamples** at p=17 and
p=73 — and indeed, the L_1 random sweep at p=17 (`issue419_L1_kbw_p17_test.py`,
20 kernel-constrained cases) found K_BW = 0 in all cases.

## Interpretation and recursion adjustment

The bare Conj A formulation in Notes 0485 and 0486 is too strong; the actual
residual from the L_1 / L_2 / L_3 reduction passes through (cu, cv) with the
kernel constraint inherited from the inner stratum (B) construction. The
correct statement is the kernel-refined version above.

### Why kernel constraint excludes the bare cex

Bare cex at p=17, pair=2: $cu = (2, 16, 14)$, $cv = (13, 11, 12)$. For this to
arise as a kernel of $M[r, s]$ with $r \in \{2,3,4,5,6,7\}$, $s \in S$, the
6-vector $(2, 13, 16, 11, 14, 12)$ (in increasing $r$ order: 2,3,4,5,6,7) must
satisfy $\sum_r c_r \omega^{r s} = 0$ for all $s \in S$. For $|S| = 6$ this
fully determines $c$ (rank deficient by 1 in a 6-dim space requires 5
independent constraints; $|S| \geq 6$ samples typically give full rank).

The kernel structure imposes a **vanishing condition on $\omega$-valued sums**,
which is a non-trivial algebraic constraint over $\mathbb{F}_p$. At $p = 17$,
the admissible kernels form a strict subset of all $(c_r)$ tuples, and that
subset happens to exclude the bare counterexamples.

### Practical implication

For paper2 §7, the residual statement should be **kernel-refined (8, 2)
Conj A**, not the bare version. Notes 0485 and 0486 implicitly used the
correct (kernel-constrained) form when running outer-scale tests, so the
empirical claims (140+ cases, 0 cex) are valid. The structural close in
paper2 still has the kernel-refined Conj A as a residual, but with stronger
empirical backing (now 540+ cases counting this note's tests).

## Toward a structural close of kernel-refined Conj A

The kernel constraint says: $(c_r)_{r \in [2, 8)}$ is in the row null space
of a Vandermonde-like submatrix on $\mu_8$. Over $\mathbb{F}_p$ this is a
constraint involving Gauss sums / character sums on $\mathbb{Z}/8$.

**Conjecture A_*** (refined): For all $S \subset \mathbb{Z}/8$ with
$|S| \geq 1$ such that $\det M[r,s]_{r \in [2,8), s \in S} = 0$ (rank deficit)
and corresponding kernel $(c_r)$, every $\alpha \in \mathbb{F}_p^*$ has
$\max_{c \in \mathrm{RS}_2} \mathrm{agr}(h_\alpha, c) = \mathrm{agr}(h_\alpha, 0)$.

**Approaches to prove**:
1. **Inversion via the dual code argument**: $(c_r)$ being in the kernel
   means $(c_r)$ corresponds to a function on $\mu_8$ vanishing on $S^*$
   (some shift). This translates to a Hamming weight constraint on $h_\alpha$.
2. **Character-sum argument** (Gong / Helleseth tradition): the Gauss-sum
   structure of $\omega^{r \cdot s}$ provides an additive invariant that
   constrains $\max_c \mathrm{agr}$.
3. **Direct exhaustion** for all $S$ choices and all $p$ in deployment-relevant
   range — finite and computable.

## Status update

| Component | Empirical | Structural |
|---|---|---|
| L_1 K_BW = 0, sub-case A | unconditional ≤ 9 < 10 (G1+G2+G3+IP) ✓ | unconditional ✓ |
| L_2 K_BW = 0, sub-case A | unconditional ≤ 16 < 20 ✓ | unconditional ✓ |
| L_3 K_BW ≤ 2, non-induced | 4/5 unconditional ✓ | residual to L_2 Conj A |
| L_1 sub-case B | 80+20 cases, 0 cex | reduces to **kernel-refined** (8,2) Conj A |
| L_2 sub-case B | 60 cases, 0 cex | reduces to **kernel-refined** (8,2) Conj A |
| L_3 L_1-factored sub-case | empirical | reduces to (64, 16) intermediate + Conj A |
| **Kernel-refined (8,2) Conj A** | **540 cases, 0 cex** | **OPEN — but precise statement** |

## Files

- `issue419_base_82_conjA_direct.py` (bare Conj A, finds cex at p=17, 73)
- `issue419_L1_lift_82cex_test.py` (lifts cex to L_1, shows agr=10 if realizable)
- `issue419_L1_kbw_p17_test.py` (L_1 K_BW with kernel constraint at p=17, gets 0)
- `issue419_base_82_kernel_constrained.py` (refined Conj A test, 400 cases, 0 cex)

## Next

1. Update paper2 §7 status remark: residual is **kernel-refined** (8, 2)
   Conj A, not bare.
2. Try structural attack on kernel-refined Conj A via character-sum / Gauss-sum
   argument.
3. Continue (64, 16) intermediate K_BW empirical (#324, in progress).
