# Note 0047 — List Size vs Field Size: The Empirical Law

## Key data (rate 1/2, δ=0.35, above Johnson)

### n=12, k=6
```
p      p/n    M
13     1.1    50
37     3.1    26
97     8.1    12
229    19     6
541    45     3
997    83     2
```
M decreases roughly as O(n/p) or O(n²/p).

### n=16, k=8
```
p      p/n    M
17     1.1    23
97     6.1    1
193+   12+    0-1
```
M drops to O(1) once p > ~6n.

## The pattern

For RS[n, k, F_p] on multiplicative subgroup, above Johnson:

$$M \approx \begin{cases} O(n^2/p) & \text{if } p \ll n^2 \\ O(1) & \text{if } p \gg n^2 \end{cases}$$

Transition around p ≈ n². For FRI: p = 2^{31} ≫ n² = 2^{40} ... wait, n² = (2^{20})² = 2^{40} > 2^{31} = p!

Hmm, for BabyBear: p ≈ 2^{31} and n ≈ 2^{20}. So p/n ≈ 2^{11} but p/n² ≈ 2^{-9}. We're in the p < n² regime!

But empirically: M drops to O(1) around p ≈ 6n (not p ≈ n²). Let me re-examine.

For n=16, p=97: p/n ≈ 6, M=1. For n=12, p=97: p/n ≈ 8, M=12.

The transition seems to depend on BOTH p/n AND the error weight w = δn:
- The system has n-k equations in w unknowns
- For w < n-k: overdetermined → few solutions
- The "random" count: C(n,w) / p^{n-k-w} (each excess equation cuts by 1/p)
- For this < 1: p^{n-k-w} > C(n,w), i.e., p > C(n,w)^{1/(n-k-w)}

For n=12, k=6, w=4: n-k-w = 2. C(12,4) = 495. Need p > √495 ≈ 22.
For n=16, k=8, w=5: n-k-w = 3. C(16,5) = 4368. Need p > 4368^{1/3} ≈ 16.

For n=2^20, k=2^19, w=0.35·2^20 ≈ 367000: n-k-w = 2^19 - 367000 ≈ 157000.
Need p > C(2^20, 367000)^{1/157000}.
C(n, δn)^{1/(n-k-w)} ≈ 2^{H(δ)n / ((1-ρ-δ)n)} = 2^{H(δ)/(1-ρ-δ)}.
For ρ=1/2, δ=0.35: H(0.35)/0.15 ≈ 0.93/0.15 ≈ 6.2. So need p > 2^{6.2} ≈ 73.

**For BabyBear (p ≈ 2^{31}): p ≫ 73. M = 0 with astronomical confidence.**

## Rigorous target

**Theorem (to prove)**: For RS[F_p, L, k] with L multiplicative subgroup of order n, δ > δ_J, and p > 2^{H(δ)/(1-ρ-δ)} · poly(n):

$$M_δ(w) = 0 \quad \text{for all } w.$$

The threshold p > 2^{H(δ)/(1-ρ-δ)} is independent of n (just depends on ρ and δ)! For rate 1/2 at δ=0.35: threshold ≈ 73. Any prime > 73 gives M=0.

## Why this should be provable

The system H_T · x = c has:
- n-k equations (syndromes)
- w unknowns (error values on support T)
- n-k-w excess equations

For MDS codes: any n-k columns of H are independent. The system is consistent iff c lies in the w-dimensional column span of H_T. Probability (for "random" c): p^{-(n-k-w)}.

Total: Σ_{T: |T|=w} p^{-(n-k-w)} = C(n,w) · p^{-(n-k-w)}.

For this < 1: done (M = 0). This requires p^{n-k-w} > C(n,w).

**But**: c is NOT random — it's the syndrome of the specific word w. The question: can c be "unluckily" aligned with many column spans?

For RS codes on multiplicative subgroups: the parity check matrix H has a specific Vandermonde structure. The column spans {Col(H_T)} for different T are NOT independent — they're determined by the geometry of L.

The rigorous proof needs to show: for ANY c (not just random), the number of T with c ∈ Col(H_T) is at most C(n,w)/p^{n-k-w} + error.

This is a COUNTING problem on the Grassmannian: how many w-dimensional subspaces of F_p^{n-k} (spanned by w columns of H) contain a given vector c?

For generic H: the answer is C(n,w) · p^{-(n-k-w)} (heuristic). For the Vandermonde H: maybe the same (or close), by the "pseudorandomness" of Vandermonde matrices.

**This is provable using the LANG-WEIL theorem** (or Cafure-Matera): the condition c ∈ Col(H_T) defines an algebraic variety, and Lang-Weil gives point counts.
