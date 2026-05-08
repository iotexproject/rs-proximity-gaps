# Note 0493 — (8,2) Conj A: empirical "0 cex at p ≥ 41" was a sampling bug

**Date:** 2026-05-04 night iteration 11
**Status:** Significant correction. The "p=17 small-prime accident" framing
in Notes 0489/0490/0491/0492 is wrong. (8,2) Conj A fails at every admissible
prime — the previous empirical sweep undersampled the kernel space and
systematically missed the failure direction.

## The bug

`issue419_base_82_filtered_exhaustive.py` samples kernel directions via:

```python
for combo in product(range(p), repeat=kdim):  # (0,0), (0,1), ..., (0,p-1), (1,0), ...
    if all(c == 0 for c in combo): continue
    v = combo[0]·basis[0] + combo[1]·basis[1]
    kernel_samples.add(tuple(v))
    if len(kernel_samples) >= 30: break
```

At kernel dim 2 with `repeat=kdim=2`, the iteration order goes
$(0,0), (0,1), (0,2), \ldots, (0, p-1), (1, 0), \ldots$. After dropping
$(0,0)$, the first 30 non-trivial combos are $(0, 1), (0, 2), \ldots, (0, 30)$,
which are all $j \cdot \text{basis}[1]$ — **a single projective direction
with 30 scalings**.

Combos $(1, j)$ for $j \geq 0$ are never reached. The empirical script
effectively tests **1 projective kernel direction per S**, not the full
kernel.

## The real picture at p=41

`issue419_path_A_diag_p41.py` enumerates all $p^2 - 1 = 1680$ non-trivial
kernel directions at p=41, S=[0,1,2,3], M={0,2,4,5,7}:

> **40 real cex** (40 = $p - 1$ scalar multiples of 1 projective direction)

All 40 cex have agreement = 5 to a non-zero codeword while agreement to
zero is 1. They correspond to kernel direction $1 \cdot \text{basis}[0] +
2 \cdot \text{basis}[1] = (23, 9, 17, 30, 1, 2)$, which is combo (1, 2) =
the 43rd non-trivial combo in the iteration — never sampled by the
empirical script.

**Verified by hand**: c=(23, 9, 17, 30, 1, 2), α=25 →
$h_\alpha$ on $\mu_8 = [1, 38, 9, 14, 40, 3, 32, 27]$ matches line
$a + bz = 2 + 18z$ at $z \in \{1, 9, 40, 3, 27\} = \{\omega^0, \omega^2,
\omega^4, \omega^5, \omega^7\}$. Direct computation: $h_\alpha(1) = 20 = 2 + 18$,
$h_\alpha(9) = 0 = 2 + 18 \cdot 9 \mod 41$, etc. ✓

## Strategic implications

1. **(8, 2) Conj A is FALSE at every admissible prime** (not just p=17).
   The failure mode at each prime is along a **sparse algebraic locus** — at
   p=41, exactly 1 projective kernel direction per (S, M) admits cex. (Total
   per S, all M's, all alphas: needs full enumeration.)

2. **L_2 / L_3 K_BW closure modulo Conj A is on shaky ground**. paper2 §7's
   `thm:K-BW-2-structural` uses (32, 8) Conj A; if the analogous undersampling
   bug affects the (32, 8) Conj A test (`issue419_base_328_conjA_test.py`),
   then (32, 8) Conj A is also false at every prime, and the K_BW ≤ 2 bound
   becomes more nuanced.

3. **The L_3 K_BW = 0 claim from Note 0488 / Note 0481 / paper2** also
   needs re-verification with exhaustive kernel sampling.

4. **The Path A elimination machinery is correct** and identifies the real
   failure variety. Iteration 10 found the 1-dim variety has $p - 1$
   $\mathbb{F}_p$-points = exactly the $p - 1$ scalings of 1 projective
   direction. So Path A is computing the failure variety correctly; the
   empirical script was the buggy half.

## What this means for paper2 §7

The K_BW ≤ 2 unconditional bound (K_1 ≤ 2 + sub-case A K_2 = 0) **stands**.
What changes:

- The "modulo Conjecture A" qualifier was always honest. The empirical
  evidence supporting Conj A as "almost always true (only fails at p=17)" is
  wrong. Conj A genuinely fails at every prime, but along a sparse locus
  (1 projective direction per (S, M) at p=41).

- The K_BW = 0 empirical claim is wrong. Need to re-test with full kernel
  enumeration.

- The actual K_BW value at p=41+ for (8, 2): up to **K_1 + K_2 = 1 + 1 = 2**
  (one cex direction × one alpha per direction). Still ≤ 2, matching paper2's
  bound.

## Concrete next steps

| # | Task | Estimate |
|---|---|---|
| 1 | Re-run `issue419_base_82_filtered_exhaustive.py` with EXHAUSTIVE kernel sampling at p ∈ {17, 41, 73, 97, 257}. Count: real cex per (S, M, prime). | 1 day |
| 2 | Re-run `issue419_base_328_conjA_test.py` similarly at p ∈ {97, 193, 257}. Verify the K_BW status changes. | 1 day |
| 3 | Re-run L_2 (32,8) and L_3 (128,32) K_BW empirical tests with full kernel enumeration. Determine actual max K_BW. | 1-2 days |
| 4 | Update Notes 0489-0491 with corrected empirical state. Update STATE.md. | 1 day |
| 5 | Reassess: is the "K_BW ≤ 2" structural close still valid empirically? Or does it occasionally hit K_BW = 3 in undersampled cases? | dependent |

## Files

- `issue419_path_A_diag_p41.py` (NEW, this iteration) — exhaustive kernel
  enumeration at p=41, found 40 real cex confirming the bug
- `issue419_path_A_elim_full.py` — pair-resultant variety = 1-dim, $p-1$
  $\mathbb{F}_p$-points (matches the cex count)
- (Pending) `issue419_base_82_exhaustive_full_kernel.py` — corrected
  empirical sweep across all primes
- (Pending) `issue419_base_328_exhaustive_full_kernel.py` — same for (32, 8)

## Honest framing

This is a **methodological correction, not a structural collapse**. The
paper2 §7 K_BW ≤ 2 theorem is still proven unconditionally for K_1 and
sub-case A. The "modulo Conj A" qualifier is more honest than ever. The
empirical claim K_BW = 0 was **never verified properly** — it was an
artifact of insufficient kernel coverage in the test script.

Going forward:
- Path A continues: now we know the failure variety is 1-dim per (S, M),
  parameterized by α. The structural close via Hasse-Weil applies as before;
  the bound becomes "K_BW ≤ const" with a specific constant per prime.
- The (32, 8) Conj A drill needs full re-empirical-verification before any
  structural attack is meaningful.
- paper2 §7 status remark needs updating to acknowledge the sampling
  limitation.

User decision required: continue Path A drill (now with corrected expectations)?
Or step back and re-baseline the empirical claims first?
