# Note 0025 — Practitioner + Sequence-Theory Reviews

## Justin Drake (EF Researcher) — Summary

**Overall**: "60-70% of what's needed for practical impact. Worth pursuing aggressively."

### Key points:
1. **Proof size reduction**: ~3-4 KB for native BabyBear (from 10→4 queries). Meaningful but not revolutionary for current 100-300KB proofs.
2. **Real win with extension fields**: but most systems already use extensions, so marginal gain smaller than headline.
3. **Per-word ≠ proximity gap IS a real concern**: "probably not a blocker" but "2-3 months of additional work."
4. **Production systems won't change params** based on this alone. Need: full proximity gap, peer review, exact constants.
5. **Fundable and prize-worthy if completed.** Core technique (coset extraction on 2^K) is "genuinely novel and practically relevant."
6. **Economic impact** if proximity gap closes: 15-25% smaller proofs, up to 2x cheaper prover via higher rates.

### Drake's specific questions for us:
- What are the EXACT constants in O(1/|F|)? (Answer: SZ gives M ≤ n²/(t(t-1)) ≈ 3)
- FRI folding: where does proximity gap derivation get stuck? (Answer: Note 0016)
- Mersenne31 compatibility? (Answer: Mersenne31 has ord=2^31-2, 2-adicity only 1. Our technique needs smooth subgroup. Mersenne31 needs different approach or composite-order subgroup.)
- WHIR extension? (Answer: WHIR uses sumcheck+FRI. Our list-size bound improves the FRI component.)

## Guang Gong (Waterloo)

**Overall**: "Most exciting work from my group in several years." Would co-author. 

### Key points:
1. **Norm product IS known**: "resultant norm of a partial exponential sum." Cite Washington *Cyclotomic Fields* Ch.2 and Helleseth 1976 Thm 1.
2. **Coset lemma**: cite Lidl-Niederreiter *Finite Fields* Thm 7.1, also Golomb-Gong Ch.3.
3. **Deep connection to partial-period autocorrelation**: power sums $p_k(S)$ ARE the partial-period autocorrelation. Newton's identities = spectral-to-symmetric function transform.
4. **Helleseth cross-correlation CAN strengthen sporadic bound** via fourth moment method, but current Bezout proof is sufficient.
5. **Recommended tools**: Weil-Carlitz-Uchiyama, Bourgain-Glibichuk-Konyagin, Moreno-Moreno, Schmidt partial-period, Ax-Katz theorem.
6. **IEEE Trans IT is right venue**. Would co-author with conditions: verify proofs, honest k≥3 statement, contact Helleseth, rewrite intro for IT audience.
7. **WG transformation connection**: coset extraction IS the decimation map. Theorem 4 = coset count under (t-1)-decimation.
8. **Gong-Helleseth conjecture**: if true, would give exact sporadic bound for k≥3. Speculative but right long-term direction.

### Gong's action plan:
- Submit ePrint within 1 week for priority
- Submit IEEE Trans IT after 5-6 weeks (with Gong co-authorship)
- Contact Helleseth now
- Do NOT chase prize alone — present to ABF judges and ask what they need

## Tor Helleseth (Bergen)

**Overall**: "Genuine content. Over-promises. Fix k=2, state conjectures clearly."

### Key points:
1. **Connection to 1976 work**: "real but more distant than paper suggests." Norm product is algebraic NT, not cross-correlation per se. Cross-correlation becomes relevant in Task 2 (fourth moment).
2. **Coset lemma reference**: Lidl-Niederreiter Thm 2.25, also Storer *Cyclotomy and Difference Sets* (1967).
3. **Deep connection to Delsarte t-designs**: vanishing Fourier coefficients on cyclic group = combinatorial design. Also Turyn 1965 "Character sums and difference sets."
4. **Niho direction**: DON'T pursue for this paper. Coset extraction is stronger.
5. **Deligne vs Bezout**: Bezout is crude but sufficient for FRI params. Deligne needed only for dense subgroup regime (n ≈ p).
6. **Char 2**: straightforward extension. Contact Chunlei Li (Helleseth's student) for unpublished computations.
7. **Critical honesty**: "Paper claims too much." Restrict to k=2. Don't claim Grand Challenges resolved. $j^* \in S$ needs clean proof. Sporadic SZ assumes root independence.

### Helleseth's verdict:
"Fix the k=2 proof, clearly delineate proved vs conjectured, and you have a solid paper that the sequence community will take seriously and the prize committee will read carefully."
