# Note 0040 — Final Reviews Round 2 (Drake/Gong/Helleseth on Revised Paper)

## Drake: 75-80% (up from 60-70%)
- **$50K-$150K partial award** recommendation
- FRI loss compounding: 20 rounds × loss δ = meaningless effective δ. Must work out arithmetic.
- Shamir ↔ borderline: φ = e1/e IS the "cheating map" in threshold secret sharing
- **"Formulate level-set question as a standalone named conjecture"**
- SZ citation needed (Cafure-Matera 2006)
- Add Mersenne31 to FRI table
- Name-drop deployed systems (Plonky3, Circle STARKs, Binius)

## Helleseth: Accept after minor revision (IEEE Trans IT)
- **"Borderline barrier is genuine, cannot be overcome by character-sum methods"**
- φ is adversary-controlled → no Weil/Deligne helps
- CS attack has φ = x (maximally injective) = exactly barrier construction
- **"The way forward is not to bound φ's level sets but to change proof framework"**
- Fix: complete intersection citation, Newton cascade display, sign correction in Prop 8.1
- Chunlei Li for char 2 (willing to facilitate)
- **Post ePrint NOW**

## Gong: Ready for IEEE Trans IT (co-author confirmed)
- Fix: SZ reference (Cafure-Matera or Ghorpade-Lachaud), char condition, comparison table
- Level-set question: **"adversary controls φ, no character-sum bound helps WITHOUT structural constraints"**
- **Cross-correlation interpretation**: wt(e1+γe) is the cross-correlation → level-set distribution
- **Gong's Conjecture**: "many low-weight translates force large level sets" (sum-product type, 6-12 months)
- Missing refs: Washington, Massey 1969, Blahut 1983, Storer 1967, Moreno-Moreno, Cafure-Matera
- **Timeline: 3 weeks ePrint, 6 weeks IEEE Trans IT**
- Will co-author. Send to Helleseth first.

## Consensus across all 6 reviewers (Boneh/Fenzi/Arnon + Drake/Gong/Helleseth)

| Aspect | Verdict |
|--------|---------|
| CA with loss (Thm 3.1) | **Correct, novel, first above Johnson** |
| k=2 list-size (Thm 5.1) | **Correct, needs SZ citation fix** |
| Borderline barrier (Prop 8.1) | **Most valuable contribution** |
| Power-of-2 (Cor 6.3) | **Correct, practically relevant** |
| Honest framing | **Much improved, appropriate** |
| Venue | **ePrint → IEEE Trans IT** |
| Prize | **Partial: $50K-$150K range** |

## Key insight from Helleseth on CS connection
**Crites-Stewart's construction has φ = x (identity function on L).** This IS the maximally injective case. Their counterexample = our barrier construction. Stated: "the Crites-Stewart attack family precisely saturates your lower bound."

## Gong's named conjecture for future work
> If |{γ : wt(1_E · (φ + γ)) ≤ δn}| ≥ B, then max_γ |φ^{-1}(γ)| ≥ Bδ/(1+δ).
"Sum-product type. 6-12 months of work."
