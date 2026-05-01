# Note 0044 — Self-Audit: Does the FRI Composition Actually Work?

## The claim

$$\varepsilon_{\text{FRI}} \leq O(R)/|F|$$

for $f^{(0)}$ that is $\delta$-far from RS_k, $\delta > \delta_J$.

## Potential holes

### Hole 1: Dishonest folding at round 1

The prover commits $f^{(1)}$ BEFORE seeing queries. The prover could send ANY $f^{(1)}$ (not the honest fold). 

For the proximity gap to help: we need that the NUMBER of "good" $f^{(1)}$'s (close to RS_{k/2}) is small. This is exactly the proximity gap: the number of $\alpha$ giving close folds.

But: the prover doesn't choose $\alpha$ — the VERIFIER does (after the prover commits). So the prover commits $f^{(1)}$, then the verifier chooses $\alpha$ and checks consistency.

If $f^{(1)}$ is close to RS_{k/2}: the verifier's consistency check might fail (if $f^{(1)} \neq f^{(0)}_{\text{even}} + \alpha f^{(0)}_{\text{odd}}$ at queried points).

The prover's optimal strategy: choose $f^{(1)}$ to maximize acceptance probability. The prover could choose $f^{(1)}$ to be exactly a codeword in RS_{k/2}. Then: the consistency check fails unless $f^{(1)}$ equals the honest fold at the queried points.

Pr[consistency passes for bad $f^{(1)}$] = Pr[all $q$ queried points are consistent]. If $f^{(1)}$ differs from the honest fold on $\geq \delta n/2$ positions: each query catches with probability $\geq \delta/2$. With $q$ queries: $\Pr[\text{pass}] \leq (1-\delta/2)^q$.

For $q = 128$, $\delta = 0.4$: $\leq (0.8)^{128} \approx 2^{-41}$. Small.

So: the dishonest folding is caught by the query check with high probability.

### Hole 2: What if the prover is dishonest at LATER rounds?

Same argument: the consistency check at each round catches dishonest folds with probability $\leq (1-\delta_i/2)^q$ where $\delta_i$ is the "distance" at round $i$.

But with loss compounding: $\delta_i \approx \delta/2^i$. At round $i$: $(1-\delta/(2^{i+1}))^q \approx 1 - q\delta/2^{i+1}$.

For late rounds: $(1-\delta/2^{R})^q \approx 1$. The consistency check FAILS to catch dishonesty!

This is the same issue as before: the loss degrades the distance, making the consistency check weak at later rounds.

### Hole 3: The "Rounds 2 to R" sub-case analysis is hand-wavy

I claimed: "If $f^{(i-1)}$ is close: the dishonest prover gains nothing from deviating."

This is NOT obviously true. If $f^{(i-1)}$ is close to RS_{k/2^{i-1}}: the honest fold is also close to RS_{k/2^i}. But the prover could send a DIFFERENT $f^{(i)}$ that's EVEN CLOSER (or exactly in RS). The consistency check at round $i$ catches this only if the queries hit inconsistent points.

With $f^{(i-1)}$ close (distance $\delta/2^{i-1}$): the honest fold has error $\sim \delta/2^{i-1}$. The dishonest fold differs on $\sim \delta n/2^i$ positions. Query catches with probability $\sim q\delta/2^i$.

For late rounds: this becomes negligible. The prover CAN cheat at later rounds without getting caught.

## Revised analysis

The honest-folding case: $\varepsilon \leq R/|F|$ (SZ on final check). This is solid.

The dishonest-folding case: the prover can be dishonest at LATER rounds (after round 1) because the consistency check becomes weak. The prover's strategy:

1. Commit honest fold at round 1 (forced by strong consistency check).
2. At round 2+: commit dishonest folds that are exactly codewords.
3. The consistency check at later rounds is weak (distance has degraded).

With this strategy: f^(R) = a codeword. The final check passes. The ONLY check that matters is round 1 consistency.

But: at round 1, the prover must commit f^(1) BEFORE seeing α_1. If f^(1) is the honest fold for some α': then consistency at α = α' passes, but for α ≠ α': consistency fails (f^(1) differs from the honest fold on ≥ 1 positions).

Wait actually: the prover commits f^(1), then the verifier sends α_1, then the verifier checks f^(1)(y) = f^(0)(√y) + α_1 · (f^(0)(√y) - f^(0)(-√y))/(2√y) at random y.

Hmm, the consistency check at round 1 compares f^(1)(y) with the value computed from f^(0) at the COSET {√y, -√y}. The prover committed f^(0) too. Both are committed before α_1 is revealed.

So: the verifier picks y, computes the honest fold at y from f^(0), and checks against the committed f^(1)(y).

If the prover committed HONEST folds: consistency always passes. If DISHONEST: each query catches with probability proportional to the disagreement.

The STANDARD FRI soundness analysis handles this. The result: ε_FRI ≤ (proximity gap) + (query soundness).

The proximity gap bounds the number of "plausibly consistent" f^(1)'s. Our halved threshold gives O(1). The query soundness: the verifier catches inconsistency at each query with probability ≥ distance(f^(1), honest fold)/n.

Hmm, I think I need to be more careful about the BCHKS formalization. Let me just note the potential issue and move on.

## Honest conclusion

The composition argument WORKS for honest folding: ε ≤ R/|F|.

For dishonest folding: the BCHKS framework is needed, and our halved-threshold proximity gap replaces their O(n) bound with O(1). But the late-round consistency check weakness (due to distance degradation) is a REAL concern.

A careful analysis (which I have NOT done) is needed to determine whether the late-round issue affects the total bound. This is the "FRI folding formal theorem" gap identified in our audit.

**Status**: The per-round O(1) proximity gap is proved. The multi-round composition is plausible but needs rigorous formalization within the BCHKS framework.
