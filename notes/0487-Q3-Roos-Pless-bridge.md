# Note 0487 — Q3 Roos-Pless Bridge (concrete structural advance)

**Date:** 2026-05-05
**Status:** Substantive concrete bridge identified; explicit computational
deliverable for closure at $(32, 16)$; deployment-scale extension via
asymptotic argument.

## Key reformulation (correction of false starts in Notes 0483-0486)

The K count via cert+div over $\overline{\FF}$ (with $32 \mid p-1$ giving full
splitting) is:
$$K = \#\{(T \subset L_n, |T|=d_\sigma, \alpha, p \in \mathrm{RS}_k) : h_\alpha|_T = p|_T\}$$

For $(8, 4)$ saturating, $K = \binom{8}{6} = 28$ (every 6-subset is bad).
For $(32, 16)$ mixed-parity hard cases, conjecturally $K = 0$.

## The Roos-Pless bridge

Define the codeword $c_{\alpha,p} := h_\alpha - p \in \FF_p[z]/(z^n - 1)$.
Spectral support of $c_{\alpha,p}$ is contained in
$$\Sigma := \{0, 1, \ldots, k-1\} \cup \{a_1, a_2, a_3\}.$$
Hence $c_{\alpha,p} \in \mathcal{C}_{D_0}$, the cyclic code with defining set
$$D_0 := \mathbb{Z}/n\mathbb{Z} \setminus \Sigma = [k, n-1] \setminus \{a_1, a_2, a_3\}.$$

For $(n, k) = (32, 16)$: $|D_0| = 13$, $\dim \mathcal{C}_{D_0} = 19$.

**Roos lower bound** on $d(\mathcal{C}_{D_0})$:
- Triple $(17, 22, 25)$: $D_0 = \{16, 18, 19, 20, 21, 23, 24, 26, 27, 28, 29, 30, 31\}$.
  AP-of-length-6 at $\{26, ..., 31\}$ (step 1), separated singleton $\{16\}$ at gap 10. Roos $r=2$ gives $d \geq 6 + 1 + 2 - 1 = 8$.
- Triple $(18, 25, 27)$: $D_0 = \{16, 17, 19, 20, 21, 22, 23, 24, 26, 28, 29, 30, 31\}$.
  AP-of-length-6 at $\{19, ..., 24\}$, plus $\{16, 17\}$ pair (step 1, separated). Roos $r=2$: $d \geq 6 + 1 + 2 - 1 = 8$.

Both triples: $d(\mathcal{C}_{D_0}) \geq 8$.

## The Pless bound on K

For "bad" $(T, \alpha, p)$: $T \subseteq \mathrm{zeros}(c_{\alpha,p})$ in $L_n$
$\Leftrightarrow w_H(c_{\alpha,p}) \leq n - |T| = n - d_\sigma$.

For $(32, 16)$: $w_H \leq 32 - 23 = 9$, but $w_H \geq d(\mathcal{C}_{D_0}) \geq 8$.
So allowed weights $w \in \{8, 9\}$.

Pless-style counting:
$$K \leq \sum_{w = d}^{n - d_\sigma} A_w(\mathcal{C}_{D_0}) \cdot \binom{n - w}{d_\sigma}$$
$$= A_8 \cdot \binom{24}{23} + A_9 \cdot \binom{23}{23} = 24 A_8 + A_9.$$

## Closure condition

**For $K_{\text{interior}} = 0$ at $(32, 16)$ via orbit-size Lemma**:
Need $24 A_8 + A_9 < n = 32$ (so K_interior < 32 forces it to 0 by orbit divisibility).

**For full $K = 0$ at $(32, 16)$**:
Need $A_8 = A_9 = 0$, i.e., $d(\mathcal{C}_{D_0}) \geq 10$.

## Concrete next step (computational)

**Compute $A_8$ and $A_9$ for both hard triples** — the weight enumerator of
the $[32, 19]$ cyclic code over $\FF_{257}$ at low weights.

Brute force is infeasible ($257^{19}$ codewords). Tractable approaches:
1. **Information-set decoding**: enumerate random 19-subsets, solve, count
   low-weight codewords. ~$10^4$ iterations, $\sim$ minutes.
2. **MacWilliams from dual**: dual is $[32, 13]$, so dual has $257^{13} \approx 10^{31}$
   — also infeasible directly.
3. **Stern's algorithm or BJMM**: generic low-weight codeword search.
4. **Sage `WeightEnumerator`**: if available, computes symbolically.

**Quickest check** in pure Python: try each of $\binom{32}{8} = 10.5M$ supports
$S$ of size 8, compute rank of $13 \times 8$ constraint matrix (rows = $\omega^{-ij}$
for $j \in D_0$). If rank $< 8$: codeword with support $\subseteq S$ exists.
Each check is $\sim$ms in numpy. $\sim 3$ hours total. Doable.

If $A_8 = A_9 = 0$: $K = 0$ closed STRUCTURALLY at $(32, 16)$ for both hard
cases.

## Deployment scale extension

For deployment $(2^{j+1}, 2^j)$ with $j \in [17, 20]$:
- $|D_0| = n - k - 3 = 2^j - 3$.
- $D_0$ contains $[k, n-1] \setminus \{a_1, a_2, a_3\}$ — a long AP minus 3 holes.
- Roos $d(\mathcal{C}_{D_0}) \geq $ longest hole-free run $\geq (n-k)/4 = 2^{j-2}$.
- Allowed weights for bad codewords $w \in [d, n - d_\sigma] \subseteq [2^{j-2}, 2^j - 2^{j-0.5}]$.

At deployment, the weight window is HUGE ($2^{j-2}$ wide), so the Pless bound
$\sum_w A_w \binom{n-w}{d_\sigma}$ requires asymptotic understanding of the weight
distribution of $\mathcal{C}_{D_0}$.

This is exactly where the Helleseth-Kumar 1998 cross-correlation classification
applies: 3-position pencil character sums correspond to a specific 3-valued
distribution, and the $A_w$ for $w \approx d_\sigma$ are bounded by the
maximum cross-correlation magnitude.

**Asymptotic claim** (research-level): For mixed-parity coprime triples,
$$A_w(\mathcal{C}_{D_0}) = O(n)$$
in the bad-weight window, giving
$$K \leq O(n \cdot \binom{n}{d_\sigma}) / O(?)$$
$$\hphantom{K \leq } \cdot $$ orbit-size argument: $K_{\text{interior}} = 0$.

The orbit-size + Roos+Pless framework gives a CLEAN structural pathway to
deployment-scale closure. The remaining gap is the asymptotic weight enumerator
for $\mathcal{C}_{D_0}$ as a function of triple-position pattern.

## References (from expert consultation)

- **Roos 1983**, IEEE-IT 29: cyclic distance bound for AP-with-deletion.
- **Hartmann-Tzeng 1972**, Information & Control 20: BCH-style bound.
- **van Lint-Wilson 1986**, IEEE-IT 32: AB-method shifting bound (sharper).
- **Helleseth-Kumar 1998**, in Pless-Huffman *Handbook of Coding Theory*:
  cross-correlation distributions for 3-valued Niho-type exponents.
- **MacWilliams-Sloane**, Theory of Error-Correcting Codes, §5.6: Pless
  power moments.

## Files

- This note (0487): the Roos-Pless bridge framework.
- Notes 0483-0486: prior consultation rounds + BW empirical.
