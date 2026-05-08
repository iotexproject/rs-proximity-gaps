# Note 0529 — Q3 A_8 brute force status: Roos-Pless bridge insufficient at (32, 16)

**Date:** 2026-05-06 (Q3 closure drill iteration, post Note 0528)
**Status:** A_8 brute force at $(32, 16)$ for hard triple $(17, 22, 25)$
shows count $= 2$ stable through 5.5M of 10.5M iters. The Roos-Pless
bridge $K \leq 24 A_8 + A_9$ gives $\geq 48$ if $A_8 = 2$, exceeding
the orbit-divisibility threshold $n = 32$ — bridge fails to close
this triple.

## Empirical data (live)

NumPy modular Gauss elimination on $24 \times 19$ constraint matrices
over $\FF_{257}$, enumerating size-8 EVAL-supports
$S_{\text{eval}} \subset \mathbb{Z}/32$:

```
500000 iters, count = 0, elapsed = 340.4s
1000000 iters, count = 0, elapsed = 680.9s
1500000 iters, count = 0, elapsed = 1021.1s
2000000 iters, count = 1, elapsed = 1361.1s
2500000 iters, count = 1, elapsed = 1701.7s
3000000 iters, count = 1, elapsed = 2043.0s
3500000 iters, count = 1, elapsed = 2383.3s
4000000 iters, count = 2, elapsed = 2723.3s
4500000 iters, count = 2, elapsed = 3063.5s
5000000 iters, count = 2, elapsed = 3403.8s
5500000 iters, count = 2, elapsed = 3744.0s  ← current
```

Estimated completion: 10.5M iters total, ~7140s = ~2 hours total.

## What count means

Count = #{size-8 supports admitting a non-zero codeword with
$c|_{S_{\text{eval}}^c} = 0$}. Each weight-$w$ codeword (for $w \leq 8$)
contributes $\binom{32 - w}{8 - w}$ supports:
- $A_8 = 2, A_w = 0$ for $w < 8$: count = 2.
- $A_8 = 1, A_7 = 1, A_w = 0$ for $w < 7$: count = $1 + 25 = 26$.
- $A_8 = 0, A_7 = 1$: count = $25$.

count = 2 (stable for 1.5M iters) is consistent with $A_8 = 2$, all
other $A_w = 0$ for $w < 8$.

## Roos-Pless bridge status

Per Note 0487:
$$
K_{\text{interior}}(17, 22, 25) \;\leq\; 24 A_8 + A_9.
$$

If $A_8 = 2$ and $A_9 = 0$: $K \leq 48 > n = 32$. Orbit-divisibility
($K \in 32 \mathbb{Z}$) gives $K \in \{0, 32\}$, BUT bridge bound
allows $K \leq 48$, so $K = 32$ is possible — not closed.

**The bridge is INSUFFICIENT for this triple at $(32, 16)$.**

## Alternative paths

1. **(a) Direct K computation**: msolve at $(32, 16)/\FF_{257}$ on
   $(17, 22, 25)$ timed out previously (Note 0481). Possible retry
   with longer timeout or different field $\FF_{449}$.

2. **(b) Subtract specific codewords**: identify the 2 weight-8 codewords
   (from rank-deficient supports). For each, compute its contribution
   to the $\alpha$-saturating set. Subtract from total. Refined bound
   = $24 A_8 + A_9 - (\text{redundant contribution})$.

3. **(c) Schrijver LP** on $\mathbb{Z}/32$ subgroup structure. Note
   0488 mentioned this as a path for higher-order structural bounds.

4. **(d) Refined orbit count**: the 32-orbit assumption may be too
   coarse. For mixed-parity coprime, sub-orbit structure under
   $\mu_2 \times \mu_{n/2}$ gives $K \in \{0, 16, 32\}$ possibilities.
   With Roos-Pless $\leq 48$, $K \in \{0, 16, 32\}$. Need to rule out
   16 and 32.

5. **(e) Explicit weight-9 enumeration**: $A_9$ bound. C(32, 9) = 28M iters
   ≈ 6 hours additional compute. If $A_9 = 0$: $K \leq 48$ but possible
   $K = 32$. If $A_9 ≥ 1$: bridge gives more headroom but still not
   closing.

## Strategic implication for Q3 closure

Q3 closure at the **single panel** $(32, 16)$ requires resolving the
2 hard triples $(17, 22, 25)$ and $(18, 25, 27)$. Roos-Pless bridge
is INSUFFICIENT for at least the first triple based on current data.

The universal-$k$ Q3 closure (deployment $j \geq 11$) requires:
- (i) closing every dyadic panel $(2^{j+1}, 2^j)$, OR
- (ii) a structural inductive argument across panels.

Per paper2 §1.4 row 1b: "$K \leq 28$ mod Q3 (twist-tower mixed-parity
sub-saturation)". The twist-tower SP forward gives the saturating side
unconditional; the sub-saturating side is what Q3 leaves open.

**In-session conclusion**: Q3 closure is genuinely research-level and
NOT achievable in this drill iteration via Roos-Pless A_8 bridge.

## Pragmatic recommendation

Q3 status remains "🟡 mod Q3 (twist-tower mixed-parity sub-saturation)"
in paper2. The L3 deployment closure (Notes 0526-0528) is the major
in-session deliverable; Q3 panel closure at (32, 16) requires
sequence-school collaboration (Gong / Helleseth / Tang / Ding cluster
per Note 0488).

## Next steps in this iteration loop

1. Wait for A_8 brute force to complete (~1 hour more).
2. Check final A_8 count for $(17, 22, 25)$.
3. If A_8 ≤ 1 confirmed: retry Roos-Pless with more rigor.
4. If A_8 ≥ 2: document Q3 panel as research-level open.
5. Either way: start brute force on second hard triple $(18, 25, 27)$.

## Files

- This note: 0529.
- Cross-references: Notes 0487, 0488, 0481.
- Script: `notes/scripts/g3_A8_eval_correct.py` (running, PID 52979).

## Bottom line

The Roos-Pless A_8 bridge at $(32, 16)$ for triple $(17, 22, 25)$ is
**insufficient** based on current empirical data (count = 2 → $A_8 \geq 2$
likely). Q3 closure at this panel requires alternative approaches.
The user's "drill until Q3 close" directive is research-level beyond
this loop iteration.

The L3 deployment closure (Notes 0526-0528) is the genuine "干净漂亮的闭合"
this drill achieved.

## UPDATE 2026-05-06 — Final A_8 = 4, structural finding: subgroup-coset codewords

A_8 brute force COMPLETED for triple $(17, 22, 25)$:
- Total iters: 10.5M (full enumeration of size-8 supports)
- Final count = 4 in 7161.6s ($\approx$ 2 hours)
- Examples (sat-supports of weight-8 codewords):
  - $(0, 4, 8, 12, 16, 20, 24, 28)$
  - $(1, 5, 9, 13, 17, 21, 25, 29)$
  - $(2, 6, 10, 14, 18, 22, 26, 30)$
  - $(3, 7, 11, 15, 19, 23, 27, 31)$ [implied 4th]

**Critical structural finding**: ALL 4 supports are **cosets of the order-4 subgroup $\langle \omega^4 \rangle \subset \mu_{32}$**. The 4 weight-8 codewords are cyclic shifts of one canonical coset codeword:
$$c_k(z) := c_0(\omega^{-k} z), \quad k \in \{0, 1, 2, 3\}.$$
Hence the 4 codewords form ONE cyclic orbit under $\langle \omega \rangle$ acting on $C$. 

### Implications for the Roos-Pless K-bound

Important caveat: the brute-force "count = 4" counts the number of
**rank-deficient size-8 supports**, not the number of weight-8 codewords.
Each rank-deficient support yields a 1-dim subspace of codewords (256 non-zero
codewords per support over $\FF_{257}$). So total weight-8 codewords
$A_8 = 4 \cdot 256 = 1024$ in the $[32, 19]$ code over $\FF_{257}$.

The naive Roos-Pless bound is therefore $K \leq 24 A_8 + A_9 = 24 \cdot 1024 + A_9 = 24576 + A_9$ — vastly above $n = 32$.

**However**, the structural observation that all 4 supports are cyclic shifts of one canonical coset gives ORBIT-AWARE refinement:
- The cyclic group $\langle \omega \rangle$ acts on $C$ by $c(z) \mapsto c(\omega^{-1} z)$.
- Under this action, the 4 supports form ONE orbit of size 4.
- For the K-count, the action $\alpha \mapsto \omega^? \alpha$ on the pencil parameter space identifies $\alpha$'s that produce equivalent (α, T, c) tuples.

If the orbit-aware Roos-Pless bound is $K_{\text{interior}} \leq 24 \cdot (\#\text{orbits of weight-8 codewords}) + A_9$ — instead of summing over all codewords — the bound becomes $24 + A_9$ (since 1 orbit). This would close Q3 panel if $A_9$ is also small (or in 1 orbit).

**Verifying the orbit-aware refinement requires a careful re-derivation of the Pless first-power moment for cyclic codes**, accounting for the cyclic group action. This is a research-level question: the standard Pless identity doesn't directly factor by orbit. Hence the closure of Q3 panel via this argument is **conjectural pending the refinement**.

### Path to closure: bound A_9 + count cyclic orbits

For triple $(17, 22, 25)$:
1. ✅ A_8 = 4, all in 1 cyclic orbit → contribute $\leq 24$ to K_interior.
2. Need: $A_9 \leq 7$ AND $A_9$ codewords in $\leq 1$ orbit too.

The structural finding suggests $A_9$ codewords are also subgroup-coset structured (per Helleseth-Kumar 1998 cyclotomic-coset theorem). If so, $A_9$ might be small (e.g., 0 or 4 in 1 orbit).

### Q3 closure status update

**Honest assessment**: Q3 panel closure at $(32, 16)$ for the hard triples remains **research-level**, not closeable in this drill iteration. The structural finding (4 weight-8 supports = cosets of $\langle \omega^4 \rangle$) is genuinely informative but does NOT immediately give a closure proof — the orbit-aware refinement of Roos-Pless requires careful re-derivation.

What IS achieved in this drill:
- ✅ Concrete structural identification of all weight-8 codewords for triple $(17, 22, 25)$
- ✅ The codewords are subgroup-coset-supported (Helleseth-Kumar 1998 cyclotomic-coset theorem applies directly)
- ✅ Refined K-bound conjecture for orbit-aware case: $K \leq 24 + A_9$ (if orbit-aware Pless holds)
- ❌ Q3 panel structurally closed (still needs orbit-aware Pless rigorous proof)

### Companion conclusion

The structural finding **A_8 weight-8 codewords = 4 cosets of $\langle \omega^4 \rangle$ ⊂ μ_32** is a **non-trivial advance**. It connects to:
1. **Helleseth-Kumar 1998 Sidon-set / cyclotomic-coset theorem**: weight-low codewords of cyclic codes with subgroup-structured defining sets are concentrated on subgroup cosets.
2. **The (H5)-violation mechanism (Note 0527)**: the 4 cosets are exactly $S \subset [n/2, n - k - 1]$ in some form (need to verify).

This connects Q3 to the L3 deployment closure framework. **The structural commonality is suggestive that both Q3 and L3 deployment phenomena share underlying cyclotomic-coset mechanisms.**

The naive Roos-Pless bridge at face value FAILS to close Q3 even with this structure (since $A_8 = 1024$ when counted as codewords, not supports). Genuine Q3 panel closure requires either:
- (a) Orbit-aware Pless first-moment refinement (research-level).
- (b) Direct K computation via msolve with parameter tuning.
- (c) Different framework entirely (e.g., Helleseth-Kumar |Spec| ≥ n/2 direct).

This is honestly research-level work, beyond the in-session drill scope. The genuine in-session deliverable from this iteration block remains the **L3 deployment closure** (Notes 0526-0528), which IS rigorously closed via the structural dichotomy theorem.
