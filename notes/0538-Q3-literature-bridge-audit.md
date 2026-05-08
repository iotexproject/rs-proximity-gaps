# Q3 ↔ Sequence-School Literature Bridge Audit

Date: 2026-05-06
Scope: Find an explicit named open problem in sequence design / coding
theory literature that Q3 reduces to or specializes.

## 0. Q3 restated (paper2 §Open Problems)

> Prove K(any 3-mono coprime triple at $(2^{j+1}, 2^j)$) $\leq 28$ for all
> $j \geq 5$ without per-scale Gröbner basis sweep, where K counts
> $(\alpha_1, \alpha_2) \in (\FF_q^*)^2$ such that the trinomial pencil
> $h_\alpha(z) = \alpha_1 z^{a_1} + \alpha_2 z^{a_2} + z^{a_3}$ has agreement
> $\geq \tau$ with some codeword in $\RS_k(L_n)$ on the
> multiplicative subgroup $L_n \subset \FF_q^*$ of order $n = 2^{j+1}$
> (where $n \mid q-1$, char $q$ odd).

DFT-equivalent: bound $A_w$ for the q-ary cyclic code $\C_{D_0}$ over $\FF_q$
of length $n = 2^{j+1}$ with defining set
$D_0 = [k, n-1] \setminus \{a_1, a_2, a_3\}$ (i.e., dual nonzero set
$\{0, 1, \dots, k-1\} \cup \{a_1, a_2, a_3\}$ — "RS_k extended by 3 high-degree
monomials"), at weights in window $[d, n - d_\sigma]$.

Character-sum form: $|S_{a_1, a_2, a_3}(\alpha; q)| \leq d_\sigma$ for
all $\alpha \in (\FF_q^*)^2$ and a triple of additive shifts (= RS codeword
truncation). The sum is over the **proper subgroup** $L_n \subset \FF_q^*$,
not over the full group.

## 1. Three best literature candidates

### Candidate A — Helleseth-Kumar 1976 / 1998 cross-correlation problem (CLASSICAL)

**Statement:** Determine the cross-correlation distribution
$C_d(\tau) = \sum_{x \in \FF_{p^n}^*} \chi(x^d - \alpha x)$ (with
$\alpha = \omega^\tau$) between an m-sequence and its $d$-decimation,
i.e., between two trace functions $\Tr(x)$ and $\Tr(x^d)$, on the FULL
multiplicative group $\FF_{p^n}^*$ of length $p^n - 1$.

**Citations:**
- Helleseth, *Some results about the cross-correlation function between two
  maximal linear sequences*, Discrete Math. 16 (1976), 209-232.
- Helleseth & Kumar, *Sequences with Low Correlation*, Handbook of Coding
  Theory (Pless-Huffman, eds.), vol. II, Ch. 21, pp. 1765-1853, Elsevier,
  1998.
- Updated 2024 review: Y. Xia, S. Mesnager, T. Helleseth, "An updated review
  on cross-correlation of m-sequences" (arXiv:2407.16072).

**Status:** OPEN in general; many partial results (Niho, Welch, Kasami,
Niho-type $d = s(p^m-1)+1$ classes resolved). The 2024 review states 9 Open
Problems; the closest to our setting are Open Problem 1 (n = 2^i case for
odd primes; resolved by Katz binary), Open Problem 7 (n = 2m, even m,
$d = 4(2^m - 1) + 1$ Niho-type), Open Problem 9 (same with odd m).

**Verdict for Q3:**
- Q3 is **NOT a special case** of the cross-correlation problem.
  Cross-correlation is a TWO-term character sum $\chi(x^d - \alpha x)$,
  i.e., a pencil with TWO monomial positions $\{1, d\}$ (after shift), summed
  over the FULL group $\FF_{p^n}^*$ of length $p^n - 1$.
- Q3 is a THREE-term sum on a PROPER subgroup. Both axes mismatch.
- Bridge precision: **literature-shape match only**, no precise 1-to-1
  reduction. The "Helleseth-Kumar" appeal in our Note 0488 was retracted
  precisely because of this mismatch: HK saves $\sqrt{p^n}$ ambient, not
  $\sqrt{|L_n|}$ subgroup.

### Candidate B — Tang-Solé / Xiong-Li / Li-Tang-Helleseth weight distribution of cyclic codes with 3 zeros (NEAREST coding-theory family)

**Statement:** Determine $A_w$ for cyclic codes whose duals have exactly
3 nonzeros (3 zeros via Delsarte duality), with prescribed exponent
patterns.

**Citations:**
- M. Xiong, N. Li, "Weight distribution of cyclic codes with arbitrary
  number of generalized Niho type zeroes", Designs, Codes and Cryptography
  78 (2014), 713-724.
- C. Li, T. Helleseth, *Optimal Cyclic Codes With Generalized Niho-Type
  Zeros and the Weight Distribution*, IEEE Trans. Inform. Theory 61 (2015),
  4945-4954.
- N. Li, T. Helleseth, X. Tang, A. Kholosha, "Several new classes of cyclic
  codes with three zeros and their weight distributions", various IEEE-IT
  2010-2019.
- X. Tang et al., earlier (2008-2014) papers on 3-zero binary cyclic codes
  with Niho-type or Kasami-type exponents.

**Status:** PARTIALLY OPEN. Closed for SPECIFIC exponent patterns
(Niho-type, Kasami-type, $\{1, 2^i+1, 2^j+1\}$ triples on $\FF_{2^m}^*$).
GENERAL three-zero weight distribution problem is OPEN.

**Critical feature mismatch:**
- All these papers study cyclic codes of length $n = p^m - 1$ (FULL
  multiplicative group of $\FF_{p^m}$).
- Our setting: length $n = 2^{j+1}$, a STRICT subgroup of $\FF_q^*$
  (with $q - 1 \geq n^6$ at deployment by ABF parameter choices).
- The literature does not study 3-zero cyclic codes of length $n$
  satisfying $n \mid q - 1$ with $n \ll q - 1$ AND $n$ a pure power of 2,
  at least not at the "named open problem" level.

**Verdict for Q3:**
- Q3 is in the SHAPE of "weight distribution of a 3-zero cyclic code",
  but the length restriction ($n = 2^{j+1}$, NOT $q-1$) and the field
  ($q$ odd large, NOT $\FF_2$ extension) place it OUTSIDE the named
  literature corpus.
- Q3 is ARGUABLY a special case of the OPEN GENERAL problem
  "weight distribution of arbitrary 3-zero cyclic codes" — but that
  general problem is unwieldy and not precisely named.
- The closest precise sub-problem is: "find $A_w$ for cyclic codes with
  3 zeros at lengths $n$ that are NOT $p^m - 1$" — but I find no paper
  posing this as a named open problem.

### Candidate C — Charpin Open Problem (Handbook of Coding Theory, 2003)

**Statement (from Charpin 2003 §3.4 "Codes with few zeros"):**
"For any binary 3-zero cyclic code $C_{r,s,t}$ of length $n = 2^m - 1$,
determine the weight enumerator. In particular, when $C_{r,s,t}$ has min
distance 5, characterize when it is optimal." [Charpin §3.4.3, p. ~85]

**Citation:**
- P. Charpin, "Open problems on cyclic codes", in *Handbook of Coding
  Theory*, Vol. 1, Part 1, Ch. 11, pp. 963-1064, Elsevier 1998 (also
  online preprint at INRIA).

**Status:** OPEN in general; closed for specific triples (Kasami, Welch,
generalized Niho). Charpin's survey explicitly identifies this as a
hard open problem.

**Verdict:** Same length mismatch as Candidate B. Charpin's $n = 2^m - 1$ is
the FULL multiplicative group of $\FF_{2^m}$. Our $n = 2^{j+1}$, $q$ odd,
is structurally different. **Literature-SHAPE match only.**

## 2. Honest verdict

**No precise 1-to-1 named bridge exists.** Q3 sits in a literature gap:

| Axis | Q3 needs | Helleseth-Kumar / Charpin literature |
|------|----------|--------------------------------------|
| # of monomials | 3-term pencil | 2-term decimation (mostly) |
| Group | proper subgroup $L_n \subset \FF_q^*$ | full group $\FF_{p^m}^*$ |
| Length | $n = 2^{j+1}$ (power of 2) | $n = p^m - 1$ (Mersenne-style) |
| Field | $\FF_q$, odd char, $q \gg n$ | $\FF_{2^m}$ or $\FF_{p^m}$, $|F| = n+1$ |
| Question | bound $K = $ # bad $\alpha$ at agreement $\geq \tau$ | full distribution of $C_d(\tau)$ |

Each axis ALONE has literature; no single named problem handles all
four simultaneously. The closest genuine precedent is

**3-zero q-ary cyclic codes of subgroup-of-multiplicative-group length** —
which to my knowledge is **NOT** a named problem in the sequence-school
literature.

## 3. Recommendation for paper2 §Open Q3 citation

Cite Q3 as:
> "a 3-zero q-ary cyclic-code weight-enumerator question on a power-of-2
> subgroup, in the spirit of Helleseth-Kumar [HK1998] cross-correlation
> bounds (which apply to 2-term decimations on the full multiplicative
> group) and Charpin [Char2003] open problems on 3-zero binary cyclic codes
> (which apply at length $n = 2^m - 1$). The subgroup-power-of-2 case at
> $n = 2^{j+1}$, $j \geq 5$ over $\FF_q$ with $q \mid -1 \pmod n$ does not
> appear to be addressed by any named open problem in the literature."

This is HONEST: literature-family identification, not bridge.

## 4. Bridge formula (best achievable)

There is **no precise** "Q3 ⇔ named-problem-X" bridge. The best
literature-shape bridge is:

> **Q3 is in the family of "weight distribution of $q$-ary cyclic codes with
> 3 zeros at high degrees on a power-of-2 multiplicative subgroup $L_n
> \subset \FF_q^*$"** — a structural cousin of Charpin's binary 3-zero
> open problem and of the Helleseth-Kumar cross-correlation
> classification, but neither a special case nor an equivalent of any
> NAMED open problem in this literature.

## 5. What we would need to prove for a meaningful bridge

To turn Q3 into a citable special case of an existing named problem, we
would need ONE of:

(a) A precise reduction of Q3 to **Open Problem 7** of Helleseth 2024
arXiv:2407.16072 (n = 2m, m even, $d = 4(2^m - 1) + 1$). Sketch: show
the K-count for our 3-mono pencil reduces to the cross-correlation
$C_d(\tau)$ for that Niho-type decimation. **No such reduction is
apparent**; the dimension of the parameter space alone differs (2
$\alpha$'s in our problem, 1 $\tau$ in HK).

(b) A precise reduction to a generalized version of Charpin §3.4
"3-zero cyclic codes of length $n = 2^m - 1$" extended to $n =
2^{j+1}$ over $\FF_q$ with $q \neq 2^m + 1$. **No such generalization
is published**; this would be a research deliverable, not a citation.

(c) A subgroup-restricted partial Gauss sum / Katz "thin set" character-sum
reduction: show $S_{a_1, a_2, a_3}(\alpha; q)$ can be controlled by
Bourgain-Glibichuk-Konyagin / Heath-Brown-Konyagin subgroup
exponential sum estimates. **Possible but no clean reduction
exists**; BGK gives polynomial savings $|S| \ll |L_n|^{1 - \delta}$
for arbitrary $\delta$ depending on $|L_n| / |\FF_q|$, which is too
weak compared to the BCH/Roos $|S| \leq d_\sigma = \sqrt{nk}$ we
need; and BGK requires $|L_n| \geq |\FF_q|^{\eps}$ for some $\eps > 0$,
which depends on the q-q-ratio at deployment.

## 6. Subgroup-power-of-2 specific search result

Direct query: are there papers studying THE SAME triple of monomials
(or any 3 monomials) on a multiplicative subgroup $L_n \subset \FF_q^*$
with $n = 2^{j+1}$, $j \geq 5$?

**Answer: NO.** I find no such paper. The closest citations are:

- Helleseth's own Open Problem 1 in [2024 arXiv]: $n = 2^i$ with $i \geq
  2$, but this is the EXTENSION-DEGREE, not the GROUP ORDER. The group
  is $\FF_{p^{2^i}}^*$ of order $p^{2^i} - 1$. Different setting.
- Bourgain-Glibichuk-Konyagin and follow-ups give exponential sum
  bounds for subgroups of $\FF_p^*$ (prime field), but don't address
  q-ary cyclic codes.
- Schoof-van der Vlugt approach via elliptic curves works for length
  $n = p^m \pm 1$ (Melas, Zetterberg codes), not for general
  power-of-2 subgroup length.

**Conclusion: Q3 lives in a genuine literature gap.** This is
information-arbitrage territory but also means we cannot cite a precise
named problem as a bridge. The cleanest paper2 framing is:

> "Q3 is a structural cousin of Helleseth-Kumar 1998 cross-correlation and
> Charpin 2003 3-zero cyclic-code open problems, but does not reduce to
> any of them; it is a new open problem at the intersection of FRI
> proximity-gap soundness and sequence design."

## 7. Closing recommendation

For paper2 §Open Q3:
1. Drop any claim that Q3 "follows from" or "is equivalent to" a named
   sequence-school problem.
2. Position Q3 honestly as a NEW problem at the intersection of (i) RS
   proximity-gap soundness, (ii) 3-zero cyclic code weight distribution,
   (iii) character sums on power-of-2 multiplicative subgroups of
   $\FF_q^*$.
3. Cite Helleseth-Kumar 1998, Helleseth 2024 review (arXiv:2407.16072),
   Charpin 2003 as motivating literature, NOT as bridges.
4. Acknowledge that the Roos-Pless Note 0487 / 0529 bridge, while
   structural, does not close Q3 (Note 0529 finding: $A_8 = 4$ supports
   beats the orbit-divisibility threshold).

This is the right amount of literature scholarship for paper2 v23+.
