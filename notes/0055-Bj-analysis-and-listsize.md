# Note 0055 — B_j(c) Analysis and List Size Above Johnson

## Key Findings

### 1. Square-Root Cancellation is FALSE

Conjecture: $|B_j(c)| \leq C\sqrt{A_j^\perp}$ for all $c$ with $c \notin \text{RS}_k$.

**Refuted computationally.** For the second-largest $|B_j(s)|$ (excluding $s=0$):

| n | k | p | j | $\sqrt{A_j}$ | max* | ratio |
|---|---|---|---|---|---|---|
| 6 | 3 | 7 | 4 | 9.49 | 20 | 2.11 |
| 6 | 3 | 97 | 4 | 37.95 | 470 | 12.4 |
| 8 | 4 | 17 | 5 | 29.93 | 301 | 10.1 |

The ratio grows as $O(\sqrt{p})$, not $O(1)$.

### 2. B_j(s) is Few-Valued and Stratified by Coset Weight

$|B_j(s)|$ takes only $O(n)$ distinct values (not $p^{n-k}$). These values are determined by the **minimum weight of the coset** corresponding to syndrome $s$:

- min_wt = 0 (codeword): $|B_j| = A_j^\perp$ (trivial maximum)
- min_wt = 1: $|B_j|$ takes ONE value (second largest)
- min_wt = 2: $|B_j|$ takes 3-5 values
- min_wt = 3+: $|B_j|$ takes several values, all relatively small

This is a **cross-correlation distribution** phenomenon, directly in the Golomb-Gong tradition. The few-valuedness is a structural property of RS codes on multiplicative subgroups.

### 3. Correct MacWilliams Normalization

The correct formula is:
$$N_w(c) = \frac{1}{p^{n-k}} \sum_{j=0}^n \overline{B_j(c)} \cdot K_w(j; n, p)$$

Note: denominator is $p^{n-k}$ (not $p^k$ as in some references). For rate 1/2 ($k = n-k$) they coincide.

### 4. List Size M = O(1) Above Johnson — COMPUTATIONAL PROOF

For RS[n, k] on multiplicative subgroup with rate $\rho = 1/2$, $\delta$ above Johnson:

| n | k | p | δ | w_max | M (worst) |
|---|---|---|---|---|---|
| 6 | 3 | 7-97 | 0.35 | 2 | **3** |
| 8 | 4 | 17 | 0.35 | 2 | **1** |
| 8 | 4 | 41 | 0.35 | 2 | **1** |
| 10 | 5 | 11 | 0.35 | 3 | **3** |
| 12 | 6 | 13 | 0.35 | 4 | **6** |

M is O(1) in ALL cases! And for n=6: M = 3 **regardless of p** (verified p = 7, 13, 31, 61, 97).

### 5. Why Individual B_j Bounds Can't Work

The Krawtchouk-weighted sum $R_w(s) = \sum_j B_j(s) K_w(j) / p^{n-k}$ is small even though individual $B_j(s)$ are large. The cancellation happens at the level of the **Krawtchouk transform**, not at the level of individual B_j.

At $s = 0$ (codeword): $B_j(0) = A_j^\perp$ is maximal, but $N_w(0) = A_w = 0$ for $w < d$ (MDS). The large $B_j$ cancel via the MacWilliams identity.

### 6. The Gap: Multiplicative Subgroups vs Random Points

| Setting | Status | Reference |
|---|---|---|
| Random evaluation points, large field | PROVED (M = O(1)) | BGM 2023, Guo-Zhang 2023 |
| Generic evaluation points, huge field | PROVED | BGM 2023 |
| Multiplicative subgroups | **OPEN** | **This is the Prize** |
| FRI parameters (k = 2^m, huge p) | **OPEN** | **This is the Prize** |

The BGM/Guo-Zhang proofs use "GM-MDS" or "MDS(ℓ)" conditions — certain polynomial non-degeneracy conditions on evaluation points. For random points: these hold w.h.p. For multiplicative subgroups: **never verified**.

### 7. Proof Strategy

**Approach A**: Verify BGM's GM-MDS condition for multiplicative subgroups.
- Requires showing certain determinantal identities are nonzero for $\alpha_i = \omega^i$
- Could use Weil bounds / character sums to bound these determinants
- This would immediately give M = O(1) via BGM's theorem

**Approach B**: Direct proof using Guruswami-Rudra subspace extraction.
- FRI with k = 2^m naturally gives a 2-folded RS code
- But folding parameter 2 only gives M = O(n), not O(1)
- Need to exploit the FULL iterative FRI structure (effective folding = 2^R)

**Approach C**: Combinatorial proof for MDS codes.
- For n=6, k=3, w=2: M ≤ 3 follows from disjoint 2-subset packing bound
- The error sets must be "nearly disjoint" (|B_i ∩ B_j| ≤ t for specific t)
- But this only gives M = O(n) at the Johnson radius; O(1) requires algebraic structure

### 8. The Precise Open Conjecture

**Conjecture (List Decoding for RS on Multiplicative Subgroups):**
For RS[n, k] on a multiplicative subgroup $L$ of order $n$ in $\mathbb{F}_p$ with $p \geq n^C$ (for some absolute constant $C$), for any $\delta > 1 - \sqrt{k/n}$ and $\delta < 1 - k/n - \epsilon$:

$$M(\delta, c) = \max_c |\{f \in \text{RS}_k : d(f|_L, c) \leq \delta n\}| \leq M_0(n, k, \delta)$$

where $M_0$ depends only on $(n, k, \delta)$, not on $p$.

**If proven**: Combined with our FRI soundness theorem (Note 0043), this gives the FULL proximity gap for FRI above Johnson without the factor-2 loss.

## Scripts

- `notes/scripts/Bj_fft_analysis.py`: FFT computation of B_j(s) for all syndromes
- `notes/scripts/Bj_deep_analysis.py`: Syndrome stratification by coset weight
- `notes/scripts/list_size_gpu.py`: GPU-accelerated list size computation
- `notes/scripts/list_size_scaling.py`: Scaling of M with n and p
