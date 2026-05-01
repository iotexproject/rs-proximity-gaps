#!/usr/bin/env python3
"""
Mixed character sum factorization attempt.

For S(α_1, 0, ..., 0, α_w):
  = Σ_B ψ(α_1 σ_1(B) + α_w σ_w(B))
  = Σ_B ψ(α_1 Σ_{i∈B} ω^i + α_w Π_{i∈B} ω^i)
  = Σ_B ψ(α_1 Σ_{i∈B} ω^i + α_w ω^{Σ_{i∈B} i})

The first term factors: ψ(α_1 Σ ω^i) = Π_i ψ(α_1 ω^i)
The second term depends on Σ B, not on individual elements.

However: σ_w = ω^{Σ B} = ω^{b_1+...+b_w}, and
ψ(α_w ω^{Σ B}) = ψ(α_w · Π ω^{b_i}).

This does NOT factor because ψ(a·b) ≠ ψ(a)·ψ(b).

But we can write ω^{Σ B} = Π ω^{b_i} where ω^{b_i} ∈ L.
So σ_w is multiplicative over B.

Key attempt: use the generating function
  Σ_B Π_{i∈B} f(ω^i) = [u^w] Π_{j=0}^{n-1} (1 + u · f(ω^j))

For the σ_1-only case: f(x) = ψ(α_1 x), and [u^w] gives S.

For the MIXED case: we need f(x) to encode BOTH the σ_1 contribution
(additive per element) and the σ_w contribution (multiplicative over elements).

ψ(α_1 Σ x_i + α_w Π x_i) ≠ Π_i g(x_i) for any g.

BUT: we can use a DIFFERENT variable to track the multiplicative part!

Define: Σ_B ψ(α_1 Σ x_i) · ψ(α_w · Π x_i)
       = Σ_B [Π_i ψ(α_1 x_i)] · ψ(α_w · Π x_i)

The second factor ψ(α_w · Π x_i) depends on the PRODUCT of all x_i.

IDEA: introduce a second formal variable v to track the product.

Σ_B [Π_{i∈B} ψ(α_1 x_i)] · v^{log_ω(Π x_i)}

where v = ψ(α_w ω^{·}) ... hmm, this doesn't quite work.

Actually, let's try:
Σ_B [Π_{i∈B} ψ(α_1 ω^i)] · ψ(α_w ω^{Σ B})

= Σ_B [Π_{i∈B} ψ(α_1 ω^i)] · [Π_{i∈B} ψ'(i)]

where ψ'(i) = something encoding the additive contribution of i to Σ B.

Wait: ψ(α_w ω^{Σ B}) ≠ Π_i ψ(α_w ω^{b_i}) because ψ is additive, not multiplicative.

But ω^{Σ B} = Π ω^{b_i}, so:
ψ(α_w Π ω^{b_i}) ≠ ψ(α_w ω^{b_1}) · ψ(α_w ω^{b_2}) · ...

HOWEVER: if we define φ(x) = ψ(log stuff)... no, there's no clean factorization.

Let me try a completely different approach: FOURIER INVERSION on the product.

S = Σ_B ψ(α_1 σ_1(B)) · ψ(α_w σ_w(B))

Expand ψ(α_w σ_w(B)) using characters:
ψ(α_w · ω^{Σ B}) = (1/p) Σ_s Σ_t ψ(t(ω^s - σ_w(B))) · ψ(α_w ω^s)
                   ... no, that's circular.

Better: replace the σ_w dependence with a sum over Fourier modes.

σ_w(B) = ω^{Σ B}. So Σ B mod n determines σ_w.

Define S_s = Σ_{B: Σ B ≡ s (mod n)} ψ(α_1 σ_1(B))

Then: S = Σ_s ψ(α_w ω^s) · S_s

And S_s = Σ_{B: Σ B ≡ s} Π_{i∈B} ψ(α_1 ω^i)

This is a RESTRICTED sum (subset sum ≡ s mod n) of a product.
Can compute via DFT:

S_s = (1/n) Σ_{t=0}^{n-1} ω^{-ts} Σ_B [Π_{i∈B} ψ(α_1 ω^i)] · ω^{t Σ B}
    = (1/n) Σ_t ω^{-ts} Σ_B Π_{i∈B} [ψ(α_1 ω^i) · ω^{ti}]
    = (1/n) Σ_t ω^{-ts} [u^w] Π_{j=0}^{n-1} (1 + u · ψ(α_1 ω^j) · ω^{tj})
    = (1/n) Σ_t ω^{-ts} E_w(t)

where E_w(t) = [u^w] Π_{j=0}^{n-1} (1 + u · ψ(α_1 ω^j) · ω^{tj}).

So: S = Σ_s ψ(α_w ω^s) · (1/n) Σ_t ω^{-ts} E_w(t)
      = (1/n) Σ_t E_w(t) · Σ_s ψ(α_w ω^s) · ω^{-ts}
      = (1/n) Σ_t E_w(t) · Σ_s ψ(α_w ω^s + (-t)s·2πi/n... )

Wait, I'm mixing additive characters over F_p with n-th root characters.
Let me be more careful.

ω^{-ts} = exp(-2πi ts/n) -- this is an n-th root of unity operation.
ψ(α_w ω^s) = exp(2πi α_w ω^s / p) -- this is an additive character of F_p.

So: Σ_s ψ(α_w ω^s) · ω^{-ts} = Σ_{s=0}^{n-1} exp(2πi α_w ω^s / p) · exp(-2πi ts/n)

This is a "mixed" character sum -- combining additive F_p character with
cyclic Z/nZ character. It's related to a Gauss sum but not quite standard.

This mixed sum CAN be bounded! Let me denote it:

G(α_w, t) = Σ_{s=0}^{n-1} ψ_p(α_w ω^s) · ψ_n(-ts)

where ψ_p is the additive character of F_p and ψ_n is the additive character of Z/nZ.

Then: S = (1/n) Σ_t E_w(t) · G(α_w, t)

And: |S| ≤ (1/n) Σ_t |E_w(t)| · |G(α_w, t)|

Each |G(α_w, t)| is bounded by... what?

For t = 0: G = Σ_s ψ_p(α_w ω^s) = Σ_{x∈L} ψ_p(α_w x)
  Bounded by O(n^2/√p) via Gauss sum expansion.

For t ≠ 0: G is a "twisted" sum. Let me compute it.

Let's verify this decomposition numerically.
"""

import math
import cmath
from itertools import combinations

PI2 = 2 * math.pi


def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def psi_p(x, p):
    """Additive character of F_p."""
    return cmath.exp(1j * PI2 * (x % p) / p)


def psi_n(x, n):
    """Additive character of Z/nZ."""
    return cmath.exp(1j * PI2 * x / n)


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


# ============================================================
print("=" * 70)
print("MIXED SIGMA FACTORIZATION: S(α_1, 0,...,0, α_w)")
print("=" * 70)

for n, p in [(6, 7), (8, 17), (10, 11)]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    omega_val = find_omega(n, p)
    L = [pow(omega_val, i, p) for i in range(n)]

    print(f"\nn={n}, k={k}, w={w}, p={p}")

    for alpha1 in [1, 2]:
        for alpha_w in [1]:
            # Direct computation
            S_direct = 0j
            for B in combinations(range(n), w):
                roots = [L[i] for i in B]
                es = elem_sym(roots, p)
                sigma1 = es[1]  # Σ roots
                sigma_w_val = es[w]  # Π roots
                S_direct += psi_p(alpha1 * sigma1 + alpha_w * sigma_w_val, p)

            # Factored computation via DFT
            # E_w(t) = [u^w] Π_{j=0}^{n-1} (1 + u · ψ_p(α_1 ω^j) · ψ_n(tj))
            # G(α_w, t) = Σ_{s=0}^{n-1} ψ_p(α_w ω^s) · ψ_n(-ts)
            # S = (1/n) Σ_t E_w(t) · G(α_w, t)

            S_factored = 0j
            E_w_mags = []
            G_mags = []

            for t in range(n):
                # Compute E_w(t)
                # z_j = ψ_p(α_1 ω^j) · ψ_n(t·j)
                z_vals = [psi_p(alpha1 * L[j], p) * psi_n(t * j, n) for j in range(n)]

                # Polynomial multiplication: Π(1 + u·z_j)
                poly = [1 + 0j]
                for z in z_vals:
                    new_poly = [0j] * (len(poly) + 1)
                    for jj, c in enumerate(poly):
                        new_poly[jj] += c
                        new_poly[jj + 1] += c * z
                    poly = new_poly

                E_w_t = poly[w]
                E_w_mags.append(abs(E_w_t))

                # Compute G(α_w, t)
                G_t = sum(psi_p(alpha_w * L[s], p) * psi_n(-t * s, n) for s in range(n))
                G_mags.append(abs(G_t))

                S_factored += E_w_t * G_t

            S_factored /= n

            err = abs(S_direct - S_factored)
            print(f"\n  α_1={alpha1}, α_w={alpha_w}:")
            print(f"    S_direct   = {S_direct:.6f}")
            print(f"    S_factored = {S_factored:.6f}")
            print(f"    Error      = {err:.2e}")
            print(f"    |E_w(t)| = {['%.3f' % m for m in E_w_mags]}")
            print(f"    |G(t)|   = {['%.3f' % m for m in G_mags]}")
            print(f"    max|E|   = {max(E_w_mags):.4f}")
            print(f"    max|G|   = {max(G_mags):.4f}")
            print(f"    |S| bound (max|E|·max|G|) = {max(E_w_mags)*max(G_mags):.4f}")
            print(f"    |S| bound (Σ|E|·|G|/n)    = {sum(E_w_mags[t]*G_mags[t] for t in range(n))/n:.4f}")
            print(f"    |S| actual = {abs(S_direct):.4f}")


# Now compute the full S(α) for all α to see what the factorization gives
print("\n\n" + "=" * 70)
print("BOUNDING |S(α)| VIA FACTORIZATION")
print("=" * 70)

for n, p in [(8, 17), (10, 11)]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    omega_val = find_omega(n, p)
    L = [pow(omega_val, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\nn={n}, p={p}, w={w}, N={N}")

    # For all (α_1, α_w) pairs, compute S and the factored bound
    max_S = 0
    max_bound = 0
    max_E = 0
    max_G = 0

    for alpha1 in range(p):
        for alpha_w in range(p):
            if alpha1 == 0 and alpha_w == 0:
                continue

            # Compute E_w(t) for all t
            E_vals = []
            for t in range(n):
                z_vals = [psi_p(alpha1 * L[j], p) * psi_n(t * j, n) for j in range(n)]
                poly = [1 + 0j]
                for z in z_vals:
                    new_poly = [0j] * (len(poly) + 1)
                    for jj, c in enumerate(poly):
                        new_poly[jj] += c
                        new_poly[jj + 1] += c * z
                    poly = new_poly
                E_vals.append(poly[w])

            # Compute G(α_w, t)
            G_vals = [sum(psi_p(alpha_w * L[s], p) * psi_n(-t * s, n) for s in range(n))
                      for t in range(n)]

            # S = (1/n) Σ_t E_w(t) G(t)
            S = sum(E_vals[t] * G_vals[t] for t in range(n)) / n

            S_mag = abs(S)
            bound = sum(abs(E_vals[t]) * abs(G_vals[t]) for t in range(n)) / n
            max_E_local = max(abs(e) for e in E_vals)
            max_G_local = max(abs(g) for g in G_vals)

            max_S = max(max_S, S_mag)
            max_bound = max(max_bound, bound)
            max_E = max(max_E, max_E_local)
            max_G = max(max_G, max_G_local)

    print(f"  max|S(α_1,0,...,0,α_w)| = {max_S:.4f}")
    print(f"  max factored bound      = {max_bound:.4f}")
    print(f"  max|E_w(t)| over all α,t = {max_E:.4f}")
    print(f"  max|G(t)| over all α_w,t = {max_G:.4f}")
    print(f"  N = {N}, √N = {math.sqrt(N):.4f}")
