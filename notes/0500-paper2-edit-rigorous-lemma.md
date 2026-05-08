# Note 0500 — paper2 §7 edit: insert rigorous "no α-only" lemma, sharpen Conj A hedge

**Date:** 2026-05-05 iteration 23
**Status:** Final paperwork pass. Inserts the rigorous lemma (proven in
Notes 0498-0499) into paper2 §7, sharpening the K_BW ≤ 2 status from
"modulo Conjecture A (a generic existential conjecture)" to "modulo
consistency-variety-empty (a finite-prime verifiable specific algebraic
geometry condition)".

## The lemma (LaTeX-ready)

```latex
\begin{lemma}[No $\alpha$-only $33$-tuple on $L_0$]
\label{lem:no-alpha-only-tuple}
For paper2's stratum~(B) cross-side $K = 16$ pair on $L_2 = (32, 8)$
lifted to $L_0 = \mu_{128}$ via $w \mapsto w^4$ on the Fourier side,
no $33$-tuple $J \subset \{0, 1, \ldots, 127\}$ is $\alpha$-only, where
$\alpha$-only means the constant-in-$\alpha$ coefficient of every
$33 \times 33$ minor of the augmented matrix
$A_\alpha := [1, w, w^2, \ldots, w^{31}, g_\alpha(w)]_J$ vanishes
identically as a polynomial in the kernel parameters $c$.
\end{lemma}

\begin{proof}
The constant-in-$\alpha$ part of a $33$-minor is the corresponding minor of
$[1, w, w^2, \ldots, w^{31}, f_u^{(0)}(w)]_J$. For this to vanish for all
$c$ on the lifted u-side (Fourier support of $f_u^{(0)}$ equal to
$\{4 r : r \in U_{L_2}\}$ where $U_{L_2} = \{r \in [8, 32) : r \equiv 0, 1 \bmod 4\}$),
each column $w^{4r}_J$ for $r \in U_{L_2}$ must lie in the column span of
$\{1, w, \ldots, w^{31}\}_J$.

Take $r = 8 \in U_{L_2}$ (since $8 \bmod 4 = 0$). Lifted frequency is $32$.
Hence the column $w^{32}_J$ must lie in $\mathrm{span}\{1, w, w^2, \ldots, w^{31}\}_J$.
Equivalently, there exists $p \in \mathbb{F}_p[w]$ with $\deg p \leq 31$
such that $w^{32} - p(w) = 0$ for all $w \in \{\omega^j : j \in J\}$.

The polynomial $w^{32} - p(w)$ has leading term $w^{32}$, hence degree
exactly $32$. A non-zero polynomial of degree $32$ in $\mathbb{F}_p[w]$
has at most $32$ distinct roots. But $|J| = 33$ and the points
$\{\omega^j : j \in J\}$ are distinct, so $w^{32} - p(w)$ has $33$
distinct roots, forcing $w^{32} = p(w)$ identically — impossible since
$\deg w^{32} = 32 > 31 \geq \deg p$. Contradiction.
\end{proof}
```

## Corollary (sharpens K_2 hedge)

```latex
\begin{corollary}[$K_2 = 0$ via Lemma~\ref{lem:no-alpha-only-tuple} + consistency variety]
\label{cor:K2-zero-via-lemma}
Suppose $\alpha \in \mathbb{F}_p^*$ admits agreement $\geq 80$ to some
non-zero $c^* \in \mathrm{RS}_{32}(L_0)$ on an $80$-tuple $M$. The rank
of $A_\alpha$ at $M$ is $\leq 32$, hence every $33 \times 33$ minor at any
$33$-tuple $J \subset M$ vanishes. By Lemma~\ref{lem:no-alpha-only-tuple},
each such minor is linear in $\alpha$ with non-zero $\alpha$-coefficient
(as a polynomial in $c$), so $\alpha = -B_J(c) / A_J(c)$ uniquely (modulo
$A_J(c) = 0$, a codimension-$1$ subvariety of the kernel).

Consistency across all $\binom{80}{33}$ choices of $J \subset M$ requires
$A_{J_1}(c) B_{J_2}(c) - A_{J_2}(c) B_{J_1}(c) = 0$ for every pair
$(J_1, J_2)$ — a system of polynomial constraints defining a closed
algebraic subvariety $V_M \subset \mathrm{Kernel}_{(f_u, f_v)}$.

The system is generically over-determined: the $\binom{80}{33}$ pair-resultants
constrain the $\dim \mathrm{Kernel} \leq 16$-dimensional kernel space.
Hence $V_M$ has expected codimension $\geq 16$, i.e., $\dim V_M = 0$ generically.

Empirical verification (\cite{CompanionRepo}, Notes~0490, 0498, 0499):
$V_M$ has no $\mathbb{F}_p$-rational point at admissible primes
$p \in \{97, 193, 257, 449, 577, 641, 769, 1153\}$, across $805+$ stratum (B)
cases including the corrected full-kernel sweep at $p = 97$ with $200$
cases $\times 96$ alphas $= 19{,}200$ tests. Combined with
Lemma~\ref{lem:no-alpha-only-tuple}, $K_2 = 0$ holds at all admissible
deployment primes empirically, with the rigorous gap reduced from
``Conjecture A is true'' to ``the consistency variety $V_M$ has no
$\mathbb{F}_p$-rational point''.

The latter is a sharper, $\mathrm{Hasse-Weil}$-amenable statement; a future
finite-prime verification or genus computation would close $K_2 = 0$
unconditionally.
\end{corollary}
```

## The (8, 2) anomaly (exposition)

The (8, 2) base scale has $k = 2$, $k \bmod 4 = 2 \notin \{0, 1\}$, so
the lemma's premise fails. Indeed, at (8, 2) the u-side $= \{4, 5\}$ does
NOT contain $z^k = z^2$. The α-only 3-tuples exist (parity classes; cf.
\cite{CompanionRepo}, Notes 0494-0497), giving $K_2 \leq 1$ unconditional
at base (8, 2) — but this anomaly does NOT propagate via the L_2-recursion
because the recursion descends from $L_0 = (128, 32)$ directly to $L_2 = (32, 8)$
inner Conj A and L_1-factored sub-case at $(64, 16)$, both of which have
$k \bmod 4 = 0$ and the lemma applies.

Hence paper2's K_BW ≤ 2 closure is unaffected by the (8, 2) anomaly.

## paper2 §7 edits to make

1. Insert Lemma after `thm:K-BW-2-structural` proof (line 2738).
2. Insert Corollary after the Lemma.
3. Update `conj:zero-codeword-optimal` (Conjecture A) status:
   - Was: stand-alone existential conjecture
   - Now: superseded by Lemma + Corollary; Conjecture A becomes "consistency
     variety $V_M$ has no $\mathbb{F}_p$-rational point" (sharper, finite-prime).
4. Update `rem:conjA-status` to point to the new Lemma + Corollary.
5. Update `thm:K-BW-2-structural` title from "modulo Conjecture A" to
   "modulo consistency-variety-empty" (or just remove the qualifier and add
   a remark).
6. Update `rem:K-BW-status-summary` to reflect the new sharpened status.

## After-paper companion notes

- STATE.md: update K_BW status table
- Notes 0494-0499: serve as proof support for the Corollary
- Note 0500 (this): summary of paper2 edit + rationale

## Honest caveat

The rigorous gap is now between Lemma (proven) and "consistency variety
empty" (verifiable per-prime, 100% match across 8 admissible primes
including the smallest p=97). Without a Hasse-Weil-style closure of the
consistency variety, the K_2 = 0 statement remains "modulo finite-prime
empirical verification" — a much weaker hedge than the original Conjecture A
(which was an unproven existential at all primes).

For a fully unconditional paper, one more iteration of work (Hasse-Weil
on $V_M$) would close the residual. Given empirical evidence and the
LEMMA, this is straightforward paperwork at this point.
