# Note 0038 — Final Review Action Items

## Boneh (B-, borderline revision)

### Must fix:
1. **Concrete comparison table** vs BCHKS/ACFY/Diamond-Gruen for STARK params (n=2^20, |F|=2^64, ρ=1/8)
2. **k=2 limitation in abstract** — flag prominently, not buried
3. **Coset extraction proof** — spell out Newton → x^{t-1}=c step in detail
4. **Expand computation** — more fields, rates, n values; full table not summary
5. **CA definition clarity** — which definition, how loss-δ interacts with FRI

### Suggested structure:
- Lead with Prop 8.1 (barrier) + Thm 3.1 (CA)
- k=2 results in appendix
- CS material in separate note

### Positive:
- Barrier (Prop 8.1) "most valuable contribution"
- Volume packing "clean and elementary"
- Direction "sound"

## Fenzi (B-, borderline revision)

### Must fix:
1. **Remove overclaiming** — "resolving key case" is borderline OK; "Both Challenges resolved" is NOT
2. **FRI soundness theorem** — concrete numbers for BabyBear, Goldilocks
3. **Full coset extraction proof** — "proof sketch" is a red flag
4. **k≥3 barrier discussion** — why SZ fails (dim V = k)
5. **More computation** — scaling graphs, edge cases
6. **Bibliography fix** — BCIKS vs BCHKS author lists

### Positive:
- CA with loss "correct and useful"
- Borderline barrier "genuine and important, may be most important result"
- Sequence-theory angle "fresh, could inspire further work"
- Prize estimate: 10-20% of allocation

## Arnon (Major Revision)

### Must fix:
1. **Thm 5.1 proof rigorous** — complete intersection verification, characteristic condition
2. **FRI soundness corollary** — explicit theorem connecting CA to per-round error
3. **Abstract tone** — "resolving key case" → "making progress on" or "first bounds for"
4. **CS results** — either expand or remove (feels like different paper)
5. **k≥3 discussion** — why SZ fails, what's needed

### Assessment:
- Volume packing "valid new observation, BCHKS could have stated it but didn't"
- Borderline barrier "useful conceptual contribution, not fundamentally new as barrier"
- Prize: "20-30% of what prize looks for, not the 90% claimed"
- Venue: TCC 2026 or IEEE Trans IT after revision. Not STOC/FOCS.

### Key quote:
"First positive results above Johnson for plain RS proximity gaps. This is a genuine contribution."

## Consensus: B- (Boneh + Fenzi)

Paper is publishable with revision. ePrint immediately. TCC/CRYPTO after fixes.
Prize: partial contribution, not resolution. 10-20% estimate.

Key revision priorities:
1. Comparison table (Boneh)
2. FRI theorem (Fenzi)
3. Full proofs (both)
4. More computation (both)
5. Honest abstract (both)
