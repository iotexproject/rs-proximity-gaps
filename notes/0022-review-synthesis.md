# Note 0022 — Synthesis of Three Reviews + Action Plan

## Real Issues (must fix)

### Issue 1: Sporadic bound NOT rigorous ★★★
**All three reviewers flagged this.** The norm bound $t^{\varphi(n)}$ is astronomically large for practical parameters. The heuristic $\binom{n}{t}/p^{t-2}$ is not a theorem. Lang-Weil needs irreducibility + degree bounds we haven't computed.

**Impact**: Without rigorous sporadic bound, list-size = O(1) on power-of-2 is NOT proved. The coset terms (n/t and n/(t-1)) ARE proved, but they're 0 on power-of-2 + even t. So the bound becomes M ≤ 0 + 0 + unproved = unproved.

**Fix strategy**: 
- **(a)** Direct Schwartz-Zippel on the variety: the t-2 Newton conditions on 6-subsets of L define a system of polynomial equations. SZ gives: #solutions ≤ D/p^{t-2} where D is the total degree. Compute D.
- **(b)** Or: for the SPECIFIC regime (power-of-2, even t, intermediate zone): show that NO solutions exist by arithmetic argument (the polynomial $x^{t-1} = c$ in L has gcd(t-1,n) = 1 roots, so T has ≤ 1 element. For any S with |S| ≥ t: the extraction FORCES T ≥ t-1 > 1. Contradiction. So S CANNOT EXIST.)

**WAIT — option (b) is actually a proof!** If c ∈ L: extraction gives T with x^{t-1}=c having gcd(t-1,n)=1 root. So |T|=1, |S|=2 < t. Contradiction. If c ∉ L: S must have Σω^j = c "accidentally." The number of such S depends on arithmetic — this is where the sporadic bound enters.

But for c ∉ L: can we show NO such S exists by a different argument? If c ∉ L but c ∈ F_p: the condition Σ_{j∈S} ω^j = c is a single additive condition on a multiplicative subgroup. The number of solutions is exactly:

N = (1/p) Σ_{χ additive} χ(-c) Σ_{|S|=t} χ(Σ ω^j) = C(n,t)/p + error

The error is bounded by character sum estimates. If we can show |error| < C(n,t)/p: then N > 0 and solutions DO exist. If |error| < 1: then N ≈ C(n,t)/p, and we can't say N = 0.

For the additional t-3 conditions (p_2 = ?, ..., p_{t-2} = ?): each cuts by ~1/p additionally. Total: N ≈ C(n,t)/p^{t-2}. For t in the intermediate zone: this IS < 1 (exponentially small). So N = 0 by integrality.

**THIS IS THE PROOF**: N is an integer. N ≈ C(n,t)/p^{t-2} < 1 (for intermediate-zone t). Therefore N = 0.

The key: the "≈" must be made rigorous. Need: N = C(n,t)/p^{t-2} + error, and |error| < 1 - C(n,t)/p^{t-2}, i.e., |error| < 1. This requires character-sum bounds on the error term.

For the error: it involves sums of the form Σ_{|S|=t} χ(P(S)) where P is a polynomial in the power sums. The Weil bound on such sums gives: |error| ≤ O(t · n^{t/2}) or similar. For t in the intermediate zone: this could be comparable to or larger than 1. Need careful analysis.

### Issue 2: MCA definition mismatch ★★
**Arnon and Fenzi flagged this.** Our proof bounds Pr[f1+γf2 close to RS] but MCA requires the AND with "NOT close to C^{=2}."

**Impact**: Our bound IS an upper bound on ε_mca (since we're bounding a LARGER probability). But it's an upper bound on the wrong thing if most "bad γ" are actually benign (closeness explained by interleaved structure).

**Response**: Actually our bound IS valid as stated. ε_mca ≤ Pr[close to C] since ε_mca ≤ Pr[close to C AND not close to C^{=2}] ≤ Pr[close to C]. Our bound on Pr[close to C] is therefore an upper bound on ε_mca. The bound might be LOOSE (over-counting benign γ's) but it's not WRONG.

**However**: The reviewers' point is that our bound might not be TIGHT enough. If ceil(n/t)/|F| is too large to meet ε* = 2^{-128}: we'd need a tighter bound that excludes benign γ's. For BabyBear native (|F| = 2^31): 2/2^31 = 2^{-30}, far from 2^{-128}. Need extension fields OR tighter analysis.

### Issue 3: Characteristic p in Newton's identities ★
**Arnon flagged this.** When p | k, the term k·e_k vanishes in Newton's identity, potentially leaving e_k undetermined.

**Impact**: If p divides some k ≤ t-2: Newton's identity p_k = e_1·p_{k-1} - ... + (-1)^{k-1}·k·e_k doesn't determine e_k from the syndrome conditions. This means e_k could be nonzero even if the syndrome conditions are satisfied.

**Fix**: In the intermediate zone, t ≤ n. For p > n: no k ≤ t has p | k (since k < t < n < p). So the characteristic issue DOESN'T arise when p > n, which is exactly the FRI regime. For p < n (degenerate): need separate analysis.

## False Alarms (no action needed)

### Boneh's "fatal error": e_1(S) ∉ L
Already addressed. e_1(S) = -λ is a Vieta identity from the word, not a property of S.

### "k=2 only applies to degenerate rate"
Misunderstanding: we prove for k=2 as the BASE CASE, then reduce k≥3 to k=2. The result applies to ALL k via the reduction.

## Honest Assessment After Review

**The coset extraction technique is CORRECT and NOVEL.** All three reviewers acknowledge this.

**The sporadic bound is the CRITICAL gap.** Without it, we can prove:
- M = 0 when both t∤n and (t-1)∤n AND the "accidental" solutions can be shown to not exist → requires sporadic bound
- The coset terms are rigorous

**For the prize**: the coset extraction + rigorous sporadic bound = prize-worthy. Without sporadic bound: interesting technique but incomplete result.

## Priority Action

**#1: Prove the sporadic bound rigorously** using character-sum / Weil bound approach. Show that the main term C(n,t)/p^{t-2} < 1 for intermediate-zone t, and the error from character sums is < 1. Then N = 0 by integrality.

This is the SINGLE thing that separates us from a complete proof.
