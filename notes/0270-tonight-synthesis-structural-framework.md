# Note 0270 — Tonight's synthesis: structural framework for universal Stage 2 closure

**Date:** 2026-04-29 night (final synthesis)
**Status:** Comprehensive synthesis of tonight's structural results.
The (3k/2, 2k) Stage 2 closure problem at any h is now reduced to a
SINGLE empirical verification per h: "E_{h/2} at h-chain is non-vanishing
on V_h^primitive."

## Tonight's structural theorems (all RIGOROUSLY PROVED)

### Theorem 0265 (Z/h-orbit obstruction)

For Z/h-homogeneous f of degree c on V(I_chain^{(h)}), if O is a length-d
orbit, then `f|_O ≡ 0` whenever `(h/d) ∤ c`. [Proof: stabilizer
ζ^d action argument.]

### Theorem 0266a (NO length-2 orbits, universal)

For all h ≥ 2 even, V(I_chain^{(h)}) contains no length-2 orbits.
[Proof: chain restriction to length-2 slice forces x_{h/2} = 0.]

### Theorem 0266b (length-3 orbit existence, universal)

For all h with 3 | h, V(I_chain^{(h)}) contains exactly ONE length-3
orbit, with 3 nontrivial points satisfying:
```
x_{2h/3}³ = -1/4,    x_{h/3} = x_{2h/3}².
```
[Proof: chain restriction + sympy solve, h-independent.]

### Theorem 0267 (CHAIN SELF-SIMILARITY)

For all h, d with d | h, the h-chain restricted to the length-d slice
(after rescaling y_j := x_{j·h/d}) EQUALS the d-chain in (y_1, …, y_{d-1}).

[Proof: change of variables w = z^{h/d} maps X(z) at slice to X̃(w);
all chain coefficients V, W, XW, W² respect this transformation.]

**CONSEQUENCE (Möbius decomposition):**
```
V(I_chain^{(h)}) = ⨆_{d | h, d ≥ 1} V_d^primitive,
```
where V_d^primitive is INTRINSIC to d (independent of h).

### Theorem 0269 (E_1 ≡ 0 mod chain, universal)

For all d ≥ 2, E_1 = 14 V_1 - 3 [z^1] U² satisfies E_1 = 6 W_0 · c_1 ∈ I_chain.
[Proof: V_1 = 0, [z^1] U² = -2 W_0 (x_1 - W_1), and c_1 = x_1 - W_1.]

## Universal endpoint criterion (refined)

For h-chain + endpoint E_c to close, ALL must hold:
1. **Z/h-divisibility:** for each d | h with V_d^prim ≠ ∅, (h/d) | c.
2. **Avoid E_1 reduction:** for each such d, c ≠ h/d (else E_c|_slice = E_1 = 0).
3. **Intrinsic non-vanishing:** E_{c·d/h} at d-chain ≠ 0 on V_d^prim.

For h = 2^k with V_d^prim ≠ ∅ for d ∈ {4, 8, …, 2^k}:
- (1) requires lcm{2^(k-j) : j=2,…,k} | c, i.e., 2^(k-2) | c.
- (2) requires c ∉ {2^(k-2), 2^(k-3), …, 2^0}.
- (3) requires non-vanishing per d.

**Smallest c satisfying (1) and (2): c = 2^(k-1) = h/2.**

(c = 2^(k-2) fails by (2); c = 0 trivial.)

## What remains for universal proof at h = 2^k

The ONE remaining empirical condition:
```
For each d = 2^j (j ≥ 2): E_{2^(j-1)} at d-chain is non-vanishing on V_d^primitive.
```

This is intrinsic to d (by Self-Similarity), so EACH verification is per-d.

Verified:
- d = 4 (j=2): E_2 at d=4 chain. Verified analytically:
  V_2 = i/32 ≠ 0 at p_1 ∈ V_4^prim.
  E_2 = 37i/64 ≠ 0. ✓
- d = 8 (j=3): E_4 at d=8 chain. Verified empirically:
  h=8 + E_4 alone closes (vdim = 1), so E_4 kills ALL of V_8^prim.

Pending:
- d = 16 (j=4): h=16 + E_8 — currently being computed (slow).
- d = 32, 64, ..., 2^19: each is a finite verification.

## Strategic implications

For deployment fields h = 2^k (k = 9, ..., 19):
- **By Theorem 0267 (Self-Similarity):** closure reduces to verification
  at each divisor d = 2^j, j = 2, 3, …, k.
- **By Theorems 0266 + 0269:** the structural "no obstruction at length-2"
  + "E_1 zero" are universal.
- **Per-d verification:** O(log h) verifications, each at a fixed d-chain.
  d=16 verification in progress; subsequent require larger machine /
  modular GB / batch verification.

## Inductive conjecture C270 (open)

**Conjecture:** For all d = 2^k (k ≥ 2), E_{2^(k-1)} at d-chain is
non-vanishing on V_d^primitive.

If true, single endpoint E_{h/2} closes Stage 2 for ALL h = 2^k.

The conjecture is supported by:
- Verified at k = 2, 3.
- Generic non-vanishing argument (E_{2^(k-1)} is a "generic" polynomial
  on V_d^prim, no structural reason for it to vanish identically).

## Implications for Lemma A (G_h irreducibility)

By Self-Similarity, the variety V_d^primitive corresponds to length-d
orbits (free Z/d action). For prime d, V_d is shape-position and G_d(s)
is the minimal polynomial of x_{d-1}^d. Irreducibility of G_d ⟺ V_d^prim
is a single Galois orbit.

For composite d, V_d decomposes by self-similarity into V_{d'}^prim's
for d' | d. The "intrinsic" piece V_d^primitive (length-d orbits at
d-chain) is what generates a NEW factor over Q (compared to smaller d).

**Conjecture C270b:** For d = 2^k, the length-d orbits in V_d^primitive
are a SINGLE Galois orbit over Q (i.e., V_d^primitive is irreducible
as Q-variety).

If true, the polynomial defining V_d^primitive (call it H_d(s)) is
irreducible over Q. By self-similarity, G_h(s) = ∏_{d | h} H_d(s)
factors into irreducible pieces of degree |V_d^primitive| / d each.

For h = 2^k: G_h(s) = H_4 · H_8 · H_16 · ... · H_h, with each H_{2^j}
irreducible.

This refines Lemma A: G_h is NOT irreducible (it factors into divisor-pieces),
but each piece is irreducible.

## Files

- Notes 0265-0269: structural theorems.
- Note 0270: this synthesis.
- Empirical verifications: g3_orbit_existence_proofs.py, single_ep tests.

## Where we stand

**Universal Stage 2 closure for (3k/2, 2k) family at h = 2^k:**

Conditional theorem: holds, given Conjecture C270 (intrinsic non-vanishing
of E_{2^(k-1)} at d=2^k chain).

C270 verified empirically at k = 2, 3. h=16 (k=4) verification pending.

Strategic value: even without C270 universally, the empirical verification
at deployment h ∈ {2^9, …, 2^19} is FINITE and mechanical. Combined with
Note 0263 (N_B ⊆ {7}), gives prize-ready Lemma B + C for h = 2^k.

For h NOT power of 2 (e.g., h = 2^a · 3): need ω(h) endpoints, structural
analysis similar but more complex.
