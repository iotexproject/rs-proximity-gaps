#!/usr/bin/env python3
"""
Deep analysis of E_w(t) · G(t) phase correlation.

Goal: understand WHY |Σ_t E_w(t) G(t)| << Σ_t |E_w(t)| |G(t)|.

Key questions:
1. How are phases of E_w(t)·G(t) distributed across t?
2. Is there a Parseval-type identity for Σ_t |E_w(t)|^2?
3. Does the phase correlation improve with p? With n?
4. Can we find a TIGHT bound (not just triangle inequality)?
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
    return pow(find_primitive_root(p), (p - 1) // n, p)


def psi_p(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)


def psi_n(x, n):
    return cmath.exp(1j * PI2 * x / n)


def elem_sym_complex(z_vals, w):
    """e_w of complex numbers z_0, ..., z_{n-1}."""
    n = len(z_vals)
    # [u^w] Π(1 + u·z_j)
    poly = [1 + 0j]
    for z in z_vals:
        new = [0j] * (len(poly) + 1)
        for j, c in enumerate(poly):
            new[j] += c
            new[j+1] += c * z
        poly = new
    return poly[w] if w < len(poly) else 0j


# ================================================================
print("=" * 70)
print("PHASE CORRELATION ANALYSIS: E_w(t) · G(t)")
print("=" * 70)

for n, p_list in [(6, [7, 13, 31, 61, 127]),
                   (8, [17, 41, 73, 89, 137]),
                   (10, [11, 31, 41, 61, 101])]:
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, w={w}, N={N}")
    print(f"{'='*70}")

    for p in p_list:
        if (p - 1) % n != 0:
            continue
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]

        # Scan over alpha_1, alpha_w to find the max |S| case
        best_alpha = None
        best_S = 0
        best_data = None

        for a1 in range(1, min(p, 20)):
            for aw in range(1, min(p, 20)):
                # Compute E_w(t) and G(t) for all t
                E_vals = []
                G_vals = []
                for t in range(n):
                    z = [psi_p(a1 * L[j], p) * psi_n(t * j, n) for j in range(n)]
                    E_vals.append(elem_sym_complex(z, w))
                    G_vals.append(sum(psi_p(aw * L[s], p) * psi_n(-t * s, n)
                                      for s in range(n)))

                S = sum(E_vals[t] * G_vals[t] for t in range(n)) / n
                S_mag = abs(S)
                if S_mag > best_S:
                    best_S = S_mag
                    best_alpha = (a1, aw)
                    best_data = (E_vals[:], G_vals[:])

        if best_data is None:
            continue

        a1, aw = best_alpha
        E_vals, G_vals = best_data

        # Detailed analysis of this (α_1, α_w) pair
        print(f"\n  p={p}, best α=({a1},{aw}), |S|={best_S:.4f}")

        # 1. Magnitudes
        E_mags = [abs(e) for e in E_vals]
        G_mags = [abs(g) for g in G_vals]
        print(f"  |E_w(t)|: {['%.3f'%m for m in E_mags]}")
        print(f"  |G(t)|  : {['%.3f'%m for m in G_mags]}")

        # 2. Phases of E_w(t) · G(t)
        products = [E_vals[t] * G_vals[t] for t in range(n)]
        phases = [cmath.phase(z) / math.pi for z in products if abs(z) > 1e-10]
        print(f"  arg(E·G)/π: {['%.3f'%ph for ph in phases]}")

        # 3. Bounds comparison
        bound_triangle = sum(E_mags[t] * G_mags[t] for t in range(n)) / n
        bound_cs = (math.sqrt(sum(e**2 for e in E_mags)) *
                    math.sqrt(sum(g**2 for g in G_mags))) / n
        print(f"  |S|       = {best_S:.4f}")
        print(f"  Σ|E||G|/n = {bound_triangle:.4f} (triangle)")
        print(f"  ||E||·||G||/n = {bound_cs:.4f} (Cauchy-Schwarz)")
        print(f"  ratio actual/triangle = {best_S/bound_triangle:.4f}")
        print(f"  √N = {math.sqrt(N):.4f}, √(pN)/n = {math.sqrt(p*N)/n:.4f}")

        # 4. Parseval check for E_w
        E_sq_sum = sum(abs(e)**2 for e in E_vals)
        print(f"  Σ|E_w(t)|² = {E_sq_sum:.4f}")
        print(f"  N = {N}, n·N/n = {N:.4f}")

        # 5. Phase structure: is arg(E·G) uniformly distributed?
        # Compute the "phase coherence" = |Σ exp(i·arg(E·G))| / count
        if len(phases) > 0:
            phase_sum = sum(cmath.exp(1j * ph * math.pi) for ph in phases)
            coherence = abs(phase_sum) / len(phases)
            print(f"  phase coherence = {coherence:.4f} (0=random, 1=aligned)")

        # 6. Separate t=0 from t≠0
        EG_t0 = abs(E_vals[0] * G_vals[0]) / n
        EG_rest = abs(sum(E_vals[t] * G_vals[t] for t in range(1, n))) / n
        print(f"  |E·G|_t0/n = {EG_t0:.4f}")
        print(f"  |sum_tne0 E·G|/n = {EG_rest:.4f}")
        rest_bound = sum(E_mags[t]*G_mags[t] for t in range(1,n))/n
        print(f"  cancellation in t!=0: actual/bound = {EG_rest / rest_bound:.4f}")


# ================================================================
print("\n\n" + "=" * 70)
print("PARSEVAL FOR E_w: CLOSED FORM?")
print("=" * 70)

# Σ_t |E_w(t)|² should relate to something combinatorial.
# E_w(t) = Σ_{B∈C(n,w)} Π_{i∈B} z_i(t) where z_i(t) = ψ_p(α_1 ω^i) ψ_n(ti)
# |E_w(t)|² = E_w(t)·conj(E_w(t))
#            = Σ_B Σ_{B'} Π_{i∈B} z_i · Π_{j∈B'} z̄_j
# Summing over t:
# Σ_t Π_{i∈B} ψ_n(ti) · Π_{j∈B'} ψ_n(-tj)
# = Σ_t ψ_n(t(ΣB - ΣB'))
# = n · 𝟙[ΣB ≡ ΣB' mod n]
#
# So: Σ_t |E_w(t)|² = n · Σ_{B,B': ΣB≡ΣB'} Π_{i∈B} ψ_p(α_1 ω^i) · Π_{j∈B'} ψ̄_p(α_1 ω^j)
#
# The ψ_p parts are just unit complex numbers that depend on (B,B').
# When B = B': the product is 1. There are N such pairs.
# When B ≠ B' but ΣB ≡ ΣB': there's an additional phase.
#
# For ΣB ≡ ΣB' mod n: σ_w(B) = σ_w(B'), so the σ_w values match.
# The ψ_p product is ψ_p(α_1(σ_1(B) - σ_1(B'))).
#
# So: Σ_t |E_w(t)|² = n · Σ_{ΣB≡ΣB'} ψ_p(α_1(σ_1(B)-σ_1(B')))

for n, p in [(6, 7), (8, 17), (10, 11), (10, 31)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    N = math.comb(n, w)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\nn={n}, p={p}, w={w}, N={N}")

    for alpha1 in [1, 3]:
        # Method 1: direct computation
        E_sq_direct = 0.0
        for t in range(n):
            z = [psi_p(alpha1 * L[j], p) * psi_n(t * j, n) for j in range(n)]
            E = elem_sym_complex(z, w)
            E_sq_direct += abs(E)**2

        # Method 2: via combinatorial formula
        all_B = list(combinations(range(n), w))
        E_sq_comb = 0j
        for B1 in all_B:
            s1 = sum(B1) % n
            sig1_B1 = sum(L[i] for i in B1) % p
            for B2 in all_B:
                s2 = sum(B2) % n
                if s1 != s2:
                    continue
                sig1_B2 = sum(L[i] for i in B2) % p
                E_sq_comb += n * psi_p(alpha1 * (sig1_B1 - sig1_B2), p)

        print(f"  α_1={alpha1}: Σ|E|² direct={E_sq_direct:.4f}, "
              f"comb={E_sq_comb.real:.4f}, imag={E_sq_comb.imag:.2e}")

        # Method 3: count pairs by (σ_1(B)-σ_1(B'))
        diff_counts = {}
        for B1 in all_B:
            s1 = sum(B1) % n
            sig1_B1 = sum(L[i] for i in B1) % p
            for B2 in all_B:
                if sum(B2) % n != s1:
                    continue
                diff = (sig1_B1 - sum(L[i] for i in B2)) % p
                diff_counts[diff] = diff_counts.get(diff, 0) + 1

        print(f"  σ_1 diff distribution: {len(diff_counts)} distinct values, "
              f"count[0]={diff_counts.get(0,0)}")


# ================================================================
print("\n\n" + "=" * 70)
print("E_w(t) AS A FUNCTION OF t: STRUCTURE")
print("=" * 70)

# For fixed α_1, E_w(t) = [u^w] Π_j (1 + u·ψ(α_1·ω^j)·e^{2πitj/n})
# The twist e^{2πitj/n} rotates the j-th factor by an angle that
# depends linearly on j. As t varies, this sweeps the factors around.
#
# Key insight: for t=0, E_w = e_w(ψ(α_1·ω^0), ..., ψ(α_1·ω^{n-1}))
# For t=k, the j-th argument is rotated by e^{2πikj/n}.
# This is like TWISTING the polynomial Π(1+u·z_j) by a Galois automorphism.
#
# If n|p-1 and α_1 is chosen so that {ψ(α_1·ω^j)} are n-th roots of a
# higher order root of unity, the twist just permutes the factors.
# Then |E_w(t)| = |E_w(0)| for all t — no cancellation at all!
#
# When does the twist NOT just permute? When the ψ(α_1·ω^j) values
# are NOT related by the n-th root twist.

for n, p in [(8, 17), (10, 31)]:
    if (p - 1) % n != 0:
        continue
    k = n // 2
    w = math.ceil((1 - math.sqrt(k / n)) * n)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\nn={n}, p={p}, w={w}")

    for alpha1 in range(1, min(p, 10)):
        # Check: does the twist permute the z_j values?
        z0 = [psi_p(alpha1 * L[j], p) for j in range(n)]

        E_mags = []
        for t in range(n):
            z = [z0[j] * psi_n(t * j, n) for j in range(n)]
            E = elem_sym_complex(z, w)
            E_mags.append(abs(E))

        # Is |E_w(t)| constant?
        spread = max(E_mags) - min(E_mags)
        cv = (max(E_mags) / (min(E_mags) + 1e-15)) if min(E_mags) > 1e-10 else float('inf')
        if spread < 0.01 * max(E_mags):
            status = "FLAT"
        else:
            status = f"VARIED (ratio {cv:.2f})"

        print(f"  α_1={alpha1}: |E_w(t)| = {['%.2f'%m for m in E_mags]} → {status}")

        # Check if z0 values are related by n-th root twists
        # i.e., does z0[(j+1)%n] = z0[j] * e^{2πi·something/n}?
        ratios = [z0[(j+1) % n] / z0[j] for j in range(n)]
        ratio_mags = [abs(r) for r in ratios]
        ratio_phases = [cmath.phase(r) / PI2 * n for r in ratios]
        if all(abs(rm - 1.0) < 1e-10 for rm in ratio_mags):
            print(f"    z-ratio phases (×n): {['%.3f'%rp for rp in ratio_phases]}")
