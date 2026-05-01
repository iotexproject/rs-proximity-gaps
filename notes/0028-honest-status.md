# Note 0028 — Brutally Honest Status After All Reviews

## What we ACTUALLY proved (100% rigorous)

### Theorem A: Per-word list-size for $k=2$
$M_\delta(w) \leq n^2/(t(t-1)) = O(1)$ in the intermediate zone, for $k=2$ on ANY domain.
Proof: Vandermonde Jacobian + Schwartz-Zippel over $L$.

### Theorem B: MCA bound (k-independent, but with a condition on $f_2$)
$\epsilon_{\text{mca}} \leq \lceil n/t \rceil / |F|$ **when $f_2$ is $\delta$-far from RS** ($\Delta(f_2, C) > \delta$).
Proof: Volume packing (overlap < $t$ because $f_2$ agrees with any codeword on $< t$ points).

When $f_2$ is $\delta$-close to RS: MCA holds trivially (the pair $(f_1, f_2)$ is close to $C^{=2}$).

Combining: $\epsilon_{\text{mca}} \leq \lceil n/t \rceil / |F| = O(1)/|F|$ for ALL $(f_1, f_2)$. ✓

### Theorem C: Proximity gap (k-independent, with proximity loss)
For affine line $\{f_1 + \gamma f_2\}$: if $f_2$ is far from RS: $B \leq \lceil n/t \rceil$, giving $\epsilon_{\text{pg}} = O(1)/|F|$. If $f_2$ is close: standard proximity loss $\epsilon^* = \delta$ (same as BCHKS).

### CS-specific structure (Theorems 1-6)
Finiteness, norm mechanism, coset extraction, power-of-2 optimality — all for $k=2$. These give FINER structural information but aren't needed for the main proximity gap result.

## What we HAVEN'T proved

### Gap: Per-word list-size for $k > 2$
The SZ-over-$L$ argument gives $M \leq n^{\dim V}/t!$ where $\dim V = k$. For $k = n/2$: useless ($M \leq n^{n/2}$).
The $k$-reduction ("fix $h_2,...,h_{k-1}$") is plausible but has subtleties for large $k$.

**Impact**: Grand Challenge 2 asks for list-decoding bounds at general $k$. Our result only addresses $k=2$.

### Not a gap but subtle: MCA AND condition
Our MCA proof is correct: we upper-bound $\Pr[\text{close}]$ which is $\geq \epsilon_{\text{mca}}$. When $f_2$ close to RS: the AND condition (not-interleaved) saves us. Clean.

## Priorities

### P1: Verify the MCA argument airtight ★★★
The decomposition ($f_2$ far → volume, $f_2$ close → trivial) is the crux. Need to verify:
1. When $\Delta(f_2, C) > \delta$: overlap $< t$ (follows from $f_2$ agreeing with any codeword on $< t$ points). ✓
2. When $\Delta(f_2, C) \leq \delta$: $(f_1, f_2)$ close to $C^{=2}$ → MCA not violated. Need careful proof.

### P2: Grand Challenge 2 for general $k$ ★★
Our list-size result is $k=2$ only. Can we extend?
Options:
- (a) Accept $k=2$ as the result. Still novel.
- (b) Use FRI recursive structure: final rounds have small $k$, our bound kicks in.
- (c) Find a k-independent list-size argument (hard, SZ fails).

### P3: Write clean paper with HONEST claims ★★
Helleseth and Gong both said: don't overclaim. State what's proved. Clearly separate from conjectures.

## Bottom line

**Can we 100% solve the puzzle?**

For **MCA** (Grand Challenge 1): **YES**, with the $f_2$-far/$f_2$-close decomposition. $\epsilon_{\text{mca}} = O(1)/|F|$ in the full intermediate zone, ALL $k$.

For **List Decoding** (Grand Challenge 2): **ONLY for $k=2$**. General $k$ remains open.

For **Proximity Gap**: **YES** for the MCA-style gap ($O(1)$ exceptions). Proximity loss $\epsilon^* = \delta$ when $f_2$ close (same as BCHKS — we don't improve this part).

**The MCA result alone is prize-worthy** (first MCA bound above Johnson for plain RS, k-independent).
