# Note 0486 — Q3 Expert Roundtable Round 2 (post-BW interior result)

**Date:** 2026-05-05
**Trigger:** User request "咨询老专家?" after BW interior $|S| \leq 24$ result.
**Method:** Two parallel subagents acting as Gong (Waterloo) and Helleseth
(Bergen) school senior researchers, briefed on the new BW empirical data
and the standing structural picture.

## Convergent diagnosis

Both subagents agree:

1. **Saturating tower** is closed via BKK + SP forward (Note 0484).
   The tight $V_{\mathrm{BKK}}(P_2, P_3) = 24$ at base is "vertex-non-degenerate"
   in Bernstein's sense.

2. **Mixed-parity universal-$k$** is genuinely open and not closable in
   one shot — it's a 6-10 week (Helleseth) to 2-3 paper (Gong) program.

3. The **bridge** that needs to be built is from a pointwise $|S(\alpha)|$
   upper bound (which BKK/Niho/Roos can give) to a count-of-bad-$\alpha$
   $K$ bound (which is what the conjecture needs). This requires a
   power-moment / Pless / MacWilliams-style identity.

## Helleseth path (concrete deliverable)

**Specific lemma to prove** (Helleseth subagent's recommendation):
$$
\sum_{\alpha \in (\FF_p^\ast)^3} (|S(\alpha)| - d_\sigma)_+ \leq \text{(explicit Roos-bound expression)}
$$
with RHS computable from the defining set $[k, d_\sigma - 1] \setminus
\{a_1, a_2, a_3\}$ via Roos 1983 / Hartmann-Tzeng 1972.

If RHS $< n$ for $j \geq 4$, this **closes Q3** combined with the
action-orbit Lemma (which gives $K_{\text{interior}} \in \{0, n, 2n, \ldots\}$).

**Key references**:
- Roos 1983, *IEEE-IT* 29: "AP with deletions" cyclic distance bound.
- Hartmann-Tzeng 1972, *Information & Control* 20: two coprime APs version.
- Helleseth 1976, *Discrete Math.* 16, Theorem 4.1: parity/decimation
  obstruction.
- Lahtonen-McGuire-Ward 2007 (Adv. Math. Comm., not FFA per Note 0483):
  finite list of "saturating structures" matching SP twist-tower lifts.
- van Lint-Wilson 1986: AB method, sometimes beats HT/Roos with
  multiplicative defining-set structure.

## Gong path (concrete deliverable)

**Specific computation to do** (Gong subagent's recommendation):
For a hard mixed-parity triple, e.g. $(17, 22, 25)$ at $(32, 16)$,
**write down the Newton polytope of the eliminator BY HAND**:
1. Parametrize $\sigma = \prod_{d \in D} \Phi_d(z)$ for $D \subseteq
   \mathrm{Div}(32) = \{1, 2, 4, 8, 16, 32\}$ with
   $\sum_{d \in D} \varphi(d) = d_\sigma = 23$.
2. For each admissible $D$: compute the linear system on
   $(\alpha_1, \alpha_2)$ that $\sigma | (h_\alpha - p)$ imposes.
3. Take the union of supports → "true" Newton polytope (not the GB one).
4. Check whether $V_{\mathrm{BKK}} \leq 28$ holds **combinatorially**
   (before any algebra). If yes: universal-$j$ proof candidate.

**Key references**:
- Khovanskii 1991, *Fewnomials* (AMS): Thm 3.3 fewnomial bound,
  $2^{\binom{k}{2}}(n+1)^k$ for $k$ monomials in $n$ variables.
  *Universal in $j$* for our 3-term system.
- Bernstein 1975, *Funct. Anal. Appl.* 9: vertex-non-degeneracy.
- Gel'fand-Kapranov-Zelevinsky, *Discriminants*: sparse resultants under
  monomial maps.
- Filaseta-Schinzel 2004, *Acta Arith.*: cyclotomic factorization of
  sparse polynomials over $z^n - 1$.

## Realistic timeline

| Path | 6-10 wk deliverable | Full universal-$k$ |
|------|---------------------|---------------------|
| Helleseth | Roos+power-moment lemma; rules out $K_{\text{interior}} = n$ | Genuinely open |
| Gong | NP-by-hand for one hard case + fewnomial scaffold | 2-3 paper program |

Neither path closes Q3 in-session. Both give clear paper-level
deliverables for follow-up.

## Recommendation for paper2 v23

Keep the current §sec:open Q3 wording (rigorous mod Q3 + structural
framework + 3 closure paths). The Notes 0483-0486 + scripts in
`notes/scripts/g3_*` form a complete in-session computational
audit-trail.

Mobilization plan when actual paper-level work begins:
- **Helleseth path**: pull in Helleseth or Tang Xiaohu (formal
  cross-correlation moment bounds).
- **Gong path**: pull in Gong + a polymake/Sage-versed collaborator
  (NP enumeration via cyclotomic factor parameterization).
- Both consult on Lahtonen-McGuire-Ward 2007 result interpretation
  (subagent flagged caveat in Note 0483 — exact citation venue
  needs verification).

## Status

Q3 mixed-parity sub-saturation conjecture: still empirically supported
at $j \in \{3, 4\}$, formally open at $j \geq 5$. Two clean
research-level closure paths identified; in-session compute exhausted.
