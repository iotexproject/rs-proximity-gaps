# Note 0072 — Pinned Flat Uniqueness Theorem

## Main Result

**Theorem** (Pinned Flat Uniqueness): For RS[n, k] over $\mathbb{F}_p$ with $p > n$,
let $c$ be a center with $d(c, \mathrm{RS}_k) \geq w$ (far center). If the codimension-$c$
affine subspace $V_c$ of compatible $\sigma$-values is a "pinned-(w-c)" flat, then:

$$M_{\mathrm{actual}}(c) = 1$$

In other words: ALL compatible error sets on a pinned flat correspond to the **same** codeword.

## Proof

**Setup**: A "pinned-(w-c)" flat in $\mathbb{F}_p^w$ has compatible $w$-subsets of the form
$B = S \cup T$ where $S = \{s_1, \ldots, s_{w-c}\} \subset \mathbb{Z}/n\mathbb{Z}$ is
**fixed** and $T \subset (\mathbb{Z}/n\mathbb{Z}) \setminus S$ with $|T| = c$ **varies**.

Each compatible $B$ gives a codeword $f_B \in \mathrm{RS}_k$ at distance $w$ from $c$
(by the "far center" assumption and the Case Split from Note 0070).

**Claim**: For any two compatible $B_1 = S \cup T_1$ and $B_2 = S \cup T_2$ sharing
the same fixed set $S$: $f_{B_1} = f_{B_2}$.

**Proof of claim**:

1. $f_{B_i}$ agrees with $c$ on all positions outside $B_i$:
   $$f_{B_i}(\omega^j) = c(\omega^j) \quad \text{for all } j \notin B_i$$

2. The positions where **both** $f_{B_1}$ and $f_{B_2}$ agree with $c$:
   $$\{0, \ldots, n-1\} \setminus (B_1 \cup B_2)$$
   has size $n - |B_1 \cup B_2|$.

3. Since $B_1 \cup B_2 = S \cup T_1 \cup T_2$:
   $$|B_1 \cup B_2| = |S| + |T_1 \cup T_2| \leq (w - c) + 2c = w + c$$

4. Therefore $f_{B_1}$ and $f_{B_2}$ agree on at least
   $$n - (w + c) = n - w - (n - k - w) = k$$
   positions.

5. The polynomial $f_{B_1} - f_{B_2}$ has $\deg < k$ and at least $k$ zeros.
   A polynomial of degree $< k$ with $\geq k$ zeros is identically zero.

6. Therefore $f_{B_1} = f_{B_2}$. $\square$

**Remark**: The computation $n - (w + c) = k$ uses $c = n - k - w$ (the definition of the
number of syndrome conditions). This is **exact** — not an inequality. Step 5 uses
the fundamental theorem of algebra: a nonzero polynomial of degree $d$ has at most $d$ roots.

## Generality

This theorem holds for:
- **All** $(n, k, w)$ at the Johnson radius with $c = n - k - w \geq 1$
- **All** primes $p$ with $p > n$ (so that $L = \langle\omega\rangle$ has order $n$ in $\mathbb{F}_p^*$)
- **All** rates $\rho = k/n$
- **Any** dimension of the flat (the proof does not depend on $c = w-1$ vs $c < w-1$)

## Consequences

### For the proof of $M = O(1)$

Combined with the Case Split (Note 0070) and the pinned-pair characterization (Note 0071):

1. **Near-codeword centers** ($d < w$): $M_{\text{actual}} = 1$ (Case Split)
2. **Far centers, pinned flat**: $M_{\text{actual}} = 1$ (this theorem)
3. **Far centers, non-pinned flat**: $M_{\text{actual}} \leq$ fiber bound

The remaining gap is **only** in case 3: bounding $M$ on non-pinned flats.

For the **line case** ($c = w - 1$, which applies when $w = 3, c = 2$):
Non-pinned lines have fiber bound $M \leq \lfloor n/w \rfloor$ (Note 0071, Theorem 2).
Combined: $M_{\text{actual}} \leq \max(1, \lfloor n/w \rfloor) = O(1)$ for $w = 3$.

### For the FRI regime

At FRI operating parameters ($p \approx 2^{31}$, $n \leq 2^{22}$):
The density $C(n,w)/p^c$ is exponentially small for all intermediate-zone $\delta$.
Combined with this theorem: $M = O(1)$ follows immediately (the non-pinned bound
is trivial when density $\ll 1$).

### What's still needed for a complete proof

The **non-pinned fiber bound for higher-dimensional flats** ($c < w-1$).
For a $(w-c)$-dimensional flat with $w - c \geq 2$: the rational function approach
from Note 0071 extends, but the degree analysis is more complex.

**Conjecture**: On a non-pinned $(w-c)$-flat, $M \leq \lfloor n/w \rfloor^{w-c}$.
This would give $M = O(1)$ at rate $1/2$ for all $(n, k)$.

## Connection to Known Results

The Guruswami-Sudan theorem gives $M \leq O(n/w)$ at the Johnson radius via
algebraic list decoding. Our approach gives a potentially tighter bound with a
**simpler proof** (no Koetter-Vardy or interpolation — just elementary algebra).

The key advantage of our approach: it naturally decomposes by flat type (pinned vs
non-pinned), giving structural insight into WHY $M$ is small.
