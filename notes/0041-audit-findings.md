# Note 0041 — Deep Audit Findings (2026-04-21)

## Finding 1: ABF uses joint/product Hamming for pair distance

$$\Delta((f_1,f_2), C^{=2}) = \frac{1}{n}\min_{g_1,g_2\in C}|\{x: f_1(x)\neq g_1(x) \text{ OR } f_2(x)\neq g_2(x)\}|$$

NOT the infinity-norm. Confirmed via BCIKS/Habook definitions.

Consequence: $\max(\Delta_1,\Delta_2) \leq \Delta_{\text{joint}} \leq \Delta_1+\Delta_2$.

## Finding 2: Thm 3.1 Case 2 IS correct (not vacuous)

With the joint definition: the paper's proof is correct. On $S_\gamma$: $e_1 = -\gamma e_2$, so $\text{supp}(e_1)\cap S_\gamma = \text{supp}(e_2)\cap S_\gamma$. Therefore:

$$|\text{supp}(e_1)\cup\text{supp}(e_2)| \leq |E_2| + |L\setminus S_\gamma| \leq \delta n + \delta n = 2\delta n$$

Joint distance $\leq 2\delta$. Not a CA violation at $\delta_{\text{nt}}=2\delta$. ✓

The bound IS non-vacuous because the adversary CAN make $\Delta_{\text{joint}} > 2\delta$ (via disjoint error supports when both components are far).

## Finding 3: FRI coupling inequality

$$\Delta_{\text{joint}}((f_{\text{even}}, f_{\text{odd}}), C^{=2}) \geq \Delta(f, \text{RS}_k)$$

**Proof:** For any $g = g_{\text{even}}(x^2)+x\cdot g_{\text{odd}}(x^2) \in \text{RS}_k$: each $y\in L'$ with $e_{\text{even}}(y)\neq 0$ OR $e_{\text{odd}}(y)\neq 0$ contributes $\geq 1$ error to $f-g$ on $L$. So $|$errors in $f|\ \geq\ |$joint errors$|$. Dividing: $\Delta(f,g) \geq \Delta_{\text{joint-for-this-}g}/2$... 

Actually more precisely: $\text{wt}(e_f) \leq 2\cdot|\text{joint errors}|$, so $\Delta(f,g) \leq \Delta_{\text{joint}}$. Taking min over $g$: $\Delta(f,\text{RS}_k) \leq \Delta_{\text{joint}}$. ✓

Verified: 12,000 random trials + adversarial constructions. Zero violations. Ratio $\in [1.0, 2.0]$.

## Finding 4: Halved threshold — per-round O(1) but loss kills multi-round

The CA bound at $(\delta/2, \delta)$ gives:
- Case 1 ($f_2$ far): packing $\leq \lceil 1/(1-\delta/2)\rceil \leq 3$
- Case 2 ($f_2$ close): joint $\leq \delta$, no CA violation ✓
- FRI coupling: $\Delta_{\text{joint}} > \delta$ when $\Delta(f)>\delta$ ✓

**Per-round proximity gap: O(1)/|F| above Johnson, ALL k.** This is real.

**BUT: loss $\delta/2$ per round compounds.**
- Round $i$: effective distance $\delta/2^i$
- After $R$ rounds: distance $\delta/2^R \to 0$
- Final-round check fails (can't detect $\delta/2^R$-far with $O(1)$ queries)

**Loss $\delta/2$ is TIGHT for volume-packing:** Case 2 requires $2(\delta-\varepsilon) \leq \delta$, giving $\varepsilon \geq \delta/2$.

## Finding 5: The REAL obstacle

Zero-loss CA above Johnson is blocked by the **borderline barrier** (Prop 8.1):

When $\Delta(f_1,C) = \delta+\varepsilon$, $\Delta(f_2,C)\leq\delta$: the adversary makes $\phi = e_1/e$ injective on $E$, creating $\Theta(n)$ MCA violations.

The barrier is NOT a proof artifact — the Crites-Stewart construction saturates it ($\phi = x$).

**No volume-packing method can achieve zero-loss CA above Johnson.** Need fundamentally different tools.

## Status after audit

| Claim | Verdict |
|-------|---------|
| Thm 3.1 correct | ✓ (with joint definition) |
| Thm 3.1 non-vacuous | ✓ (Case 1 is the real content) |
| Thm 5.1 (k=2 list-size) | ✓ solid |
| Coset extraction | ✓ solid |
| Borderline barrier | ✓ tight |
| k-independence (notes) | ✗ overclaimed for large k |
| "Grand Challenges solved" (notes) | ✗ overclaimed |
| Per-round O(1) proximity gap | ✓ NEW (halved threshold) |
| FRI multi-round soundness improvement | ✗ loss compounds |
| Distance to $1M | 30-40% (need zero-loss CA) |
