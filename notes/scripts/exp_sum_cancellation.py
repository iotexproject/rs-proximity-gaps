#!/usr/bin/env python3
"""
Direction C, Round 3: Cancellation analysis in the Gauss+e_w decomposition.

Key decomposition (for w=2):
  S(α_1,α_2) = (1/p) Σ_τ G(α_2/2, α_1-τ) · e_w(ψ(c_2·ω^{2i} + τ·ω^i))

where G(a,b) = ε√p · ψ(-b²/(4a)) is a Gauss sum with KNOWN phase.

Triangle inequality gives: |S| ≤ (√p/p) Σ_τ |e_w(τ)| ≤ √p · max|e_w|

But the Gauss sum G has a quadratic phase in τ, and e_w might have correlated phase.
If the phases CANCEL: |S| << √p · max|e_w|. This cancellation IS observed (factor ~2x).

Question: Is this cancellation systematic? Can we prove it?

Also: for c≥2 conditions, the sum over t ∈ F_p^c might have additional cancellation
beyond what max|S(t)| gives.

Focus:
1. Phase correlation between G and e_w
2. Super-cancellation in Σ_t S(t)
3. Comparison with MULTIPLICATIVE character sum bounds (Weil)
4. Can we express S as a multilinear Kloosterman-type sum?
"""

import math
import cmath
from itertools import combinations, product
from collections import defaultdict

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

def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e

def psi(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)

def johnson_w_mds(n, k):
    return int(n - math.sqrt(n * (k - 1)))

def primes_1modn(n, count=10):
    result = []
    pp = n + 1
    while len(result) < count:
        if pp % n == 1:
            ok = True
            for d in range(2, int(pp**0.5) + 1):
                if pp % d == 0:
                    ok = False
                    break
            if ok:
                result.append(pp)
        pp += 1
    return result


def compute_ew_array(n, w, phases):
    """Compute e_w(phases[0], ..., phases[n-1]) via generating function."""
    poly = [0j] * (w + 1)
    poly[0] = 1
    for ph in phases:
        for j in range(w, 0, -1):
            poly[j] += poly[j-1] * ph
    return poly[w]


# ========== 1: Phase correlation analysis ==========
def phase_correlation(n, k, p):
    """
    In the decomposition S = (1/p) Σ_τ G(τ) · e_w(τ),
    study the PHASE relationship between G and e_w as functions of τ.

    If G(τ) = |G|·exp(iφ_G(τ)) and e_w(τ) = |e_w|·exp(iφ_e(τ)),
    then the product has phase φ_G + φ_e.

    The sum Σ G·e_w cancels when φ_G + φ_e is uniformly distributed.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    inv2 = pow(2, p-2, p)

    print(f"\n{'='*70}")
    print(f"PHASE CORRELATION — RS[{n},{k}], p={p}, w={w}, N={N}")
    print(f"{'='*70}")

    # Test several α_2 values
    for alpha2 in [1, 2, (p+1)//2]:
        if alpha2 >= p:
            continue
        coeff_2 = (-alpha2 * inv2) % p
        a = alpha2 * inv2 % p  # for Gauss sum

        # For each α_1: compute S directly and via decomposition
        max_cancel_ratio = 0
        min_cancel_ratio = 1

        for alpha1 in range(p):
            # Direct S(α_1, α_2) via σ
            S_direct = 0j
            for B in combinations(range(n), w):
                roots = [L[i] for i in B]
                es = elem_sym(roots, p)
                S_direct += psi((alpha1 * es[1] + alpha2 * es[2]) % p, p)

            # Decomposition
            sum_abs = 0  # triangle inequality
            for tau in range(p):
                b = (alpha1 - tau) % p
                G = sum(psi((a * v * v + b * v) % p, p) for v in range(p))
                phases = [psi((coeff_2 * pow(L[i], 2, p) + tau * L[i]) % p, p) for i in range(n)]
                ew = compute_ew_array(n, w, phases)
                sum_abs += abs(G) * abs(ew)

            sum_abs /= p
            ratio = abs(S_direct) / sum_abs if sum_abs > 0 else 0

            if ratio > max_cancel_ratio:
                max_cancel_ratio = ratio
            if abs(S_direct) > 0.01:
                min_cancel_ratio = min(min_cancel_ratio, ratio)

        print(f"  α_2={alpha2}: cancel ratio range [{min_cancel_ratio:.4f}, {max_cancel_ratio:.4f}]")


# ========== 2: Actual M_alg character sum cancellation ==========
def malg_cancellation(n, k, p):
    """
    For the ACTUAL M_alg computation:
    M_alg(c) = (1/p^c) [N + Σ_{t≠0} S(t,c)]

    For a center c that gives M_alg = M: Σ_{t≠0} S(t) = p^c·M - N.
    For M = O(1): |Σ S| ≈ |p^c·M - N| ≈ N (since p^c·M << N for c≥2).

    Question: what does the DISTRIBUTION of S(t) look like?
    Are there a few large |S(t)| or many small ones?
    """
    w = johnson_w_mds(n, k)
    c = n - k - w
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    nk = n - k

    print(f"\n{'='*70}")
    print(f"M_alg CANCELLATION — RS[{n},{k}], p={p}, w={w}, c={c}, N={N}")
    print(f"{'='*70}")

    if c < 2:
        print("  c < 2, skipping")
        return

    # Precompute all σ
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p))

    import random

    # Find center with large M_alg
    best_M = 0
    best_c_high = None
    for _ in range(5000):
        c_high = [random.randint(0, p-1) for _ in range(nk)]
        cnt = 0
        for es in all_sigma:
            ok = True
            for m_off in range(c):
                val = 0
                for j in range(w + 1):
                    c_idx = m_off + j
                    if c_idx < nk:
                        val += pow(-1, j, p) * es[j] * c_high[c_idx]
                if val % p != 0:
                    ok = False
                    break
            if ok:
                cnt += 1
        if cnt > best_M:
            best_M = cnt
            best_c_high = c_high[:]

    c_high = best_c_high
    print(f"  Best center: M_alg = {best_M}")

    # Compute D values
    D_values = []
    for es in all_sigma:
        d_row = []
        for m_off in range(c):
            val = 0
            for j in range(w + 1):
                c_idx = m_off + j
                if c_idx < nk:
                    val += pow(-1, j, p) * es[j] * c_high[c_idx]
            d_row.append(val % p)
        D_values.append(d_row)

    # Compute all S(t) for t ∈ F_p^c
    pc = p ** c
    if pc > 500000:
        print(f"  p^c = {pc} too large, sampling")
        return

    S_vals = []  # (|S|, phase, t)
    total = complex(N, 0)

    for t in product(range(p), repeat=c):
        if all(ti == 0 for ti in t):
            continue
        St = 0j
        for b_idx in range(N):
            arg = sum(t[m] * D_values[b_idx][m] for m in range(c)) % p
            St += psi(arg, p)
        total += St
        S_vals.append((abs(St), cmath.phase(St), t, St))

    M_check = total.real / pc
    print(f"  M_char = {M_check:.6f} (should be {best_M})")

    # Distribution analysis
    S_vals.sort(reverse=True)
    total_abs = sum(s[0] for s in S_vals)

    print(f"\n  Character sum distribution (t ≠ 0):")
    print(f"    count = {len(S_vals)}")
    print(f"    max|S| = {S_vals[0][0]:.4f}")
    print(f"    avg|S| = {total_abs/len(S_vals):.4f}")
    print(f"    √N = {math.sqrt(N):.4f}")

    print(f"\n  Top 10 |S(t)|:")
    for mag, phase, t, St in S_vals[:10]:
        print(f"    |S|={mag:8.4f}, phase={phase:+.4f}rad, t={t}")

    # Check: does the sum Σ_{t≠0} S(t) show cancellation?
    sum_S = sum(s[3] for s in S_vals)
    print(f"\n  Σ_{{t≠0}} S(t) = {sum_S.real:.4f} + {sum_S.imag:.4f}i")
    print(f"  |Σ S| = {abs(sum_S):.4f}")
    print(f"  Predicted: p^c·M - N = {pc * best_M - N}")
    print(f"  Max if no cancel: Σ|S| = {total_abs:.4f}")
    print(f"  Cancel ratio: |Σ S|/Σ|S| = {abs(sum_S)/total_abs:.6f}")

    # Fraction of total contribution from top k
    cum = 0
    for i, (mag, _, _, _) in enumerate(S_vals):
        cum += mag
        if cum > total_abs * 0.5:
            print(f"  50% of Σ|S| from top {i+1}/{len(S_vals)} terms")
            break

    cum = 0
    for i, (mag, _, _, _) in enumerate(S_vals):
        cum += mag
        if cum > total_abs * 0.9:
            print(f"  90% of Σ|S| from top {i+1}/{len(S_vals)} terms")
            break


# ========== 3: Product formula and multiplicative character sum ==========
def product_formula_analysis(n, k, p):
    """
    Correct identity: Π_{i=0}^{n-1}(1+β·ω^i) = 1-(-β)^n

    Proof: x^n - 1 = Π(x-ω^i). Set x = -1/β:
    (-1/β)^n - 1 = Π(-1/β - ω^i) = Π(-(1/β)(1+βω^i)) = (-1/β)^n Π(1+βω^i)
    So Π(1+βω^i) = [(-1/β)^n - 1]/(-1/β)^n = 1 - (-β)^n. ∎

    For S(β,...,β^w) = Σ_{|B|=w} ψ(Π_{i∈B}(1+βω^i) - 1):
    Using Π_{i∈B}(1+βω^i) = [1-(-β)^n] / Π_{j∉B}(1+βω^j):

    S = Σ_B ψ([1-(-β)^n] · Π_{j∉B}(1+βω^j)^{-1} - 1)

    When (-β)^n = 1 (i.e., -β ∈ L): Π_{i∈B}(1+βω^i) = 0 for B containing the zero
    position j₀ where 1+βω^{j₀} = 0. For other B: product can be computed from complement.

    When (-β)^n ≠ 1: all factors nonzero, and:
    Π_{i∈B}(1+βω^i) = (1-(-β)^n) · Π_{j∉B}(1+βω^j)^{-1}

    Setting Γ = 1-(-β)^n ≠ 0:
    S = Σ_B ψ(Γ/Q_B - 1) where Q_B = Π_{j∉B}(1+βω^j)

    This is a sum of ψ(Γ/Q) where Q ranges over products of (n-w) factors from a fixed set.

    KEY: This looks like a KLOOSTERMAN-type sum (ψ(a/x) summed over structured x)!
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"PRODUCT FORMULA — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    # Verify corrected identity
    print(f"\n  Corrected identity: Π(1+βω^i) = 1-(-β)^n")
    for beta in range(1, min(p, 10)):
        prod = 1
        for i in range(n):
            prod = prod * (1 + beta * L[i]) % p
        expected = (1 - pow((-beta) % p, n, p)) % p
        print(f"    β={beta}: Π={prod}, 1-(-β)^n={expected}, {'OK' if prod == expected else 'FAIL'}")

    all_B = list(combinations(range(n), w))

    # For β where (-β)^n ≠ 1 (i.e., -β ∉ L):
    print(f"\n  Kloosterman structure: S = Σ_B ψ(Γ/Q_B - 1)")

    neg_L = set((-l) % p for l in L)  # -L = {-ω^i}

    for beta in range(1, min(p, 30)):
        if beta in neg_L:
            print(f"    β={beta}: -β ∈ L, skip (Γ=0)")
            continue

        Gamma = (1 - pow((-beta) % p, n, p)) % p

        # Compute Q_B = Π_{j∉B}(1+βω^j) and Γ/Q_B for each B
        factors = [(1 + beta * L[i]) % p for i in range(n)]

        # Full product
        full_prod = 1
        for f in factors:
            full_prod = full_prod * f % p

        Q_values = []
        S_prod = 0j
        for B in all_B:
            # Q_B = full_prod / Π_{i∈B} factors[i]
            prod_B = 1
            for i in B:
                prod_B = prod_B * factors[i] % p
            Q_B = full_prod * pow(prod_B, p-2, p) % p
            val = (Gamma * pow(Q_B, p-2, p) - 1) % p
            Q_values.append(Q_B)
            S_prod += psi(val, p)

        # Distribution of Q_B values
        Q_dist = defaultdict(int)
        for q in Q_values:
            Q_dist[q] += 1

        # Character sum: Σ ψ(Γ/Q - 1) = ψ(-1) · Σ ψ(Γ/Q) = ψ(-1) · Kloosterman-like
        S_kloos = sum(psi(Gamma * pow(q, p-2, p) % p, p) for q in Q_values)

        print(f"    β={beta}: Γ={Gamma}, |S|={abs(S_prod):.4f}, |Kl|={abs(S_kloos):.4f}, "
              f"Q distinct={len(Q_dist)}/{N}")

        if beta <= 5:
            # What fraction of F_p* is hit by Q_B?
            Q_hit = len(Q_dist)
            print(f"      Q coverage: {Q_hit}/{p} = {Q_hit/p:.3f}")
            max_Q_fiber = max(Q_dist.values())
            print(f"      max Q fiber: {max_Q_fiber}, avg: {N/Q_hit:.2f}")

    # Kloosterman bound: for Σ_{x∈S} ψ(a/x) where S ⊂ F_p*:
    # If S = F_p*: classic Kloosterman sum, |K| ≤ 2√p
    # If S is a proper subset: depends on structure
    #
    # Our case: S = {Q_B : |B|=w} is the set of COMPLEMENT PRODUCTS.
    # This has algebraic structure from the evaluation domain L.


# ========== 4: e_w of Gauss sum phases (analytic structure) ==========
def ew_gauss_phases(n, k, p):
    """
    When z_i = ψ(f(ω^i)) for polynomial f of degree d:
    e_w(z_0,...,z_{n-1}) = Σ_{|B|=w} Π_{i∈B} ψ(f(ω^i))
                         = Σ_B ψ(Σ_{i∈B} f(ω^i))

    For f(x) = αx: Σ_{i∈B} f(ω^i) = α·p_1(B) — linear in indicators
    For f(x) = αx²: Σ_{i∈B} f(ω^i) = α·p_2(B) — still linear!
    For f(x) = αx + βx²: Σ = α·p_1 + β·p_2 — linear combination of power sums

    So e_w(ψ(αω^i + βω^{2i})) = Σ_B ψ(α·p_1(B) + β·p_2(B))

    This is the POWER SUM character sum — computable via DFT!

    Key: p_k(B) = Σ_{i∈B} ω^{ki} = character sum on subset B.
    The joint distribution of (p_1, p_2,...,p_w) over random w-subsets
    determines all e_w values.

    For p_1: N(n,w,s) = |{B : Σ_{i∈B} ω^i = s}| has known structure.
    For (p_1,p_2): joint distribution = DFT analysis on Z/nZ.

    Since {ω^i} and {ω^{2i}} live on the SAME cyclic group:
    ω^{2i} = (ω^2)^i = (ω')^i where ω' = ω² is primitive if gcd(2,n)=1.

    When n is even: ω² has order n/2 (not n), so p_2(B) = Σ (ω²)^i sums
    roots of order n/2. The cosets {i, i+n/2} contribute ω^{2i}+ω^{2(i+n/2)} = 2ω^{2i}.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"e_w ANALYTIC STRUCTURE — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    # Compute (p_1, p_2) joint distribution
    joint = defaultdict(int)
    p1_vals = []
    p2_vals = []
    for B in all_B:
        p1 = sum(L[i] for i in B) % p
        p2 = sum(pow(L[i], 2, p) for i in B) % p
        joint[(p1, p2)] += 1
        p1_vals.append(p1)
        p2_vals.append(p2)

    print(f"  (p_1,p_2) joint distribution:")
    print(f"    distinct pairs: {len(joint)} (out of p²={p**2})")
    max_fiber = max(joint.values())
    print(f"    max fiber: {max_fiber}, avg: {N/len(joint):.2f}")

    # e_w(ψ(αω^i+βω^{2i})) = Σ_B ψ(α·p_1 + β·p_2)
    # This is the DFT of the joint distribution at frequency (α,β).
    # By Parseval: Σ_{α,β} |e_w|² = p² · Σ fiber² = p² · ||joint||²

    sum_fiber_sq = sum(v**2 for v in joint.values())
    parseval_pred = p**2 * sum_fiber_sq
    parseval_lhs = 0
    max_ew = 0
    ew_data = []
    for alpha in range(p):
        for beta in range(p):
            S = sum(psi((alpha * p1_vals[i] + beta * p2_vals[i]) % p, p) for i in range(N))
            mag = abs(S)
            parseval_lhs += mag**2
            ew_data.append((mag, alpha, beta))
            if mag > max_ew:
                max_ew = mag

    print(f"\n  Parseval check: Σ|e_w|² = {parseval_lhs:.1f}, p²·Σf² = {parseval_pred}")
    print(f"  max|e_w| over all (α,β) = {max_ew:.4f}")
    print(f"  max/N = {max_ew/N:.6f}")
    print(f"  max/√N = {max_ew/math.sqrt(N):.4f}")

    # Extreme values
    ew_data.sort(reverse=True)
    print(f"\n  Top 5 |e_w(α,β)|:")
    for mag, a, b in ew_data[:5]:
        print(f"    |e_w|={mag:.4f}  (α,β)=({a},{b})")

    # For the ACTUAL character sum S(α_1,α_2) = Σ_B ψ(α_1 σ_1 + α_2 σ_2):
    # σ_1 = p_1, σ_2 = (p_1²-p_2)/2
    # So α_1 σ_1 + α_2 σ_2 = α_1 p_1 + α_2(p_1² - p_2)/2
    # The p_1² term prevents this from being e_w of phases.
    # BUT: the Gauss decomposition handles it.

    # Alternative: bound via the JOINT distribution of (σ_1, σ_2)
    sigma_joint = defaultdict(int)
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_joint[(es[1], es[2])] += 1

    max_sigma_fiber = max(sigma_joint.values())
    print(f"\n  (σ_1,σ_2) joint distribution:")
    print(f"    distinct: {len(sigma_joint)}, max fiber: {max_sigma_fiber}")

    # The σ map: (σ_1,...,σ_w)(B) for |B|=w
    # If this map is "nearly injective" (max fiber ~ 1), then
    # the character sum has √N cancellation by CLT.
    # If max fiber = O(1): |S| ≤ O(√N) by square-root cancellation.

    # Check injectivity of full σ map
    sigma_full = defaultdict(int)
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma_full[tuple(es[1:])] += 1

    max_full_fiber = max(sigma_full.values())
    print(f"\n  Full σ = (σ_1,...,σ_w) injectivity:")
    print(f"    distinct: {len(sigma_full)}/{N}")
    print(f"    max fiber: {max_full_fiber}")
    if max_full_fiber == 1:
        print(f"    FULLY INJECTIVE → Parseval gives rms|S| = √N = {math.sqrt(N):.2f}")

    return max_ew, max_sigma_fiber


# ========== 5: Conditional variance / concentration ==========
def conditional_concentration(n, k, p):
    """
    Given the Newton-Gauss decomposition:
    S(α_1,α_2) = (1/p) Σ_τ G(a, α_1-τ) · T(τ)
    where T(τ) = e_w(ψ(c_2·ω^{2i} + τ·ω^i)) = Σ_B ψ(c_2·p_2(B) + τ·p_1(B))

    T(τ) is the DFT of the joint (p_1,p_2) distribution at (τ, c_2).

    The sum S = (1/p) Σ_τ G(a, α_1-τ)·T(τ) is a CONVOLUTION in the τ variable.

    By Plancherel: |S|² ≤ (1/p²) · (Σ|G|²) · (Σ|T|²) ??? NO, Plancherel doesn't apply
    to a product. It applies to CONVOLUTION.

    Actually: S(α_1) = (G * T)(α_1) / p (convolution at shift α_1).
    By Young's inequality: ||G*T||_∞ ≤ ||G||_2 · ||T||_2 / √p
    ||G||_2² = p·Σ|G|² = p²·√p... no.

    Actually G(τ) = G(a, α_1-τ) as a function of τ has |G(τ)| = √p for τ≠α_1
    and |G(a,0)| depends on whether a=0.

    Hmm, let me just compute the key quantities.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    inv2 = pow(2, p-2, p)

    if w != 2:
        return

    print(f"\n{'='*70}")
    print(f"CONDITIONAL CONCENTRATION — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    for alpha2 in [1]:
        a = alpha2 * inv2 % p
        coeff_2 = (-alpha2 * inv2) % p

        # Compute T(τ) = e_w(ψ(c_2·ω^{2i} + τ·ω^i))
        T_vals = []
        for tau in range(p):
            phases = [psi((coeff_2 * pow(L[i], 2, p) + tau * L[i]) % p, p) for i in range(n)]
            T = compute_ew_array(n, w, phases)
            T_vals.append(T)

        # ||T||_2²
        T_norm2 = sum(abs(T)**2 for T in T_vals)
        # ||T||_∞
        T_inf = max(abs(T) for T in T_vals)
        # ||T||_1
        T_norm1 = sum(abs(T) for T in T_vals)

        print(f"  α_2={alpha2}:")
        print(f"    ||T||_1 = {T_norm1:.4f}")
        print(f"    ||T||_2 = {math.sqrt(T_norm2):.4f}")
        print(f"    ||T||_∞ = {T_inf:.4f}")
        print(f"    √(p·N) = {math.sqrt(p*N):.4f}")
        print(f"    √N = {math.sqrt(N):.4f}")

        # ||G||_2² = Σ_b |G(a,b)|² = p·Σ... = p²√p? Let me compute.
        G_norm2_sq = sum(abs(sum(psi((a * v * v + b * v) % p, p) for v in range(p)))**2 for b in range(p))
        print(f"    ||G||_2 = {math.sqrt(G_norm2_sq):.4f}")
        print(f"    p·√p = {p*math.sqrt(p):.4f}")

        # S(α_1) = (1/p) Σ_τ G(a, α_1-τ) · T(τ) — convolution
        # By CS on convolution: |S|² ≤ (1/p²) ||G||_2² · ||T||_2²
        cs_bound = math.sqrt(G_norm2_sq * T_norm2) / p
        # By Young: |S| ≤ (1/p) ||G||_1 · ||T||_∞ or (1/p) ||G||_∞ · ||T||_1
        G_norm1 = sum(abs(sum(psi((a * v * v + b * v) % p, p) for v in range(p))) for b in range(p))
        G_inf = max(abs(sum(psi((a * v * v + b * v) % p, p) for v in range(p))) for b in range(p))
        young1 = G_norm1 * T_inf / p
        young2 = G_inf * T_norm1 / p

        print(f"\n    Bounds on max|S(α_1)|:")
        print(f"    Cauchy-Schwarz: {cs_bound:.4f}")
        print(f"    Young (||G||_1·||T||_∞): {young1:.4f}")
        print(f"    Young (||G||_∞·||T||_1): {young2:.4f}")

        # Actual max
        max_S = 0
        for alpha1 in range(p):
            S = sum(psi((alpha1 * es[1] + alpha2 * es[2]) % p, p) for es in
                    [elem_sym([L[i] for i in B], p) for B in all_B])
            if abs(S) > max_S:
                max_S = abs(S)
        print(f"    Actual max|S|: {max_S:.4f}")
        print(f"    Tightness: actual/CS = {max_S/cs_bound:.4f}")
        print(f"    Tightness: actual/Young = {max_S/min(young1,young2):.4f}")


# ========== 6: Weil bound for the product character sum ==========
def weil_product_bound(n, k, p):
    """
    For α = (β, β², ..., β^w): S = Σ_B ψ(Π_{i∈B}(1+βω^i) - 1)

    The product P_B = Π_{i∈B}(1+βω^i) takes values in F_p.
    S = Σ_B ψ(P_B - 1) = ψ(-1) Σ_B ψ(P_B)

    If we parametrize B by its complement B^c (of size n-w):
    P_B = Γ / Q_{B^c} where Γ = 1-(-β)^n and Q = Π_{j∈B^c}(1+βω^j)

    So S = ψ(-1) Σ_{|C|=n-w} ψ(Γ/Q_C)

    This is a SUM OF ψ(Γ/Q) over COMPLEMENT PRODUCTS.

    For the FULL sum (complement = F_p*): Σ_{x∈F_p*} ψ(Γ/x) is a Ramanujan sum,
    bounded by √p.

    For partial sums over SUBSET PRODUCTS: related to Katz's work on
    exponential sums over multiplicative characters of polynomial arguments.

    Can we bound |Σ ψ(Γ/Q_C)| using the structure of Q_C?

    Note: Q_C = Π_{j∈C} f_j where f_j = 1+βω^j are FIXED nonzero field elements.
    So Q_C ranges over {Π_{j∈C} f_j : |C|=n-w} — products of (n-w) elements from
    the set {f_0,...,f_{n-1}}.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    r = n - w  # complement size

    print(f"\n{'='*70}")
    print(f"WEIL/KLOOSTERMAN ANALYSIS — RS[{n},{k}], p={p}, w={w}, r={r}")
    print(f"{'='*70}")

    neg_L = set((-l) % p for l in L)

    for beta in range(1, min(p, 20)):
        if beta in neg_L:
            continue

        Gamma = (1 - pow((-beta) % p, n, p)) % p
        factors = [(1 + beta * L[i]) % p for i in range(n)]

        # All Q_C values (C = complement of B)
        Q_vals = []
        for C in combinations(range(n), r):
            Q = 1
            for j in C:
                Q = Q * factors[j] % p
            Q_vals.append(Q)

        Q_dist = defaultdict(int)
        for q in Q_vals:
            Q_dist[q] += 1

        # The character sum: Σ_C ψ(Γ/Q_C)
        S = sum(psi(Gamma * pow(q, p-2, p) % p, p) for q in Q_vals)

        # Multiplicative Fourier: Γ/Q_C ≡ Γ · Q_C^{-1}
        # As Q_C ranges over products: Q_C^{-1} = Π f_j^{-1}
        # So Γ/Q_C = Γ · Π f_j^{-1} for j ∈ C.

        # Setting g_j = f_j^{-1}: Q_C^{-1} = Π_{j∈C} g_j.
        # Σ ψ(Γ · Π g_j) = e_{n-w}(z_0,...,z_{n-1}) where...
        # NO: the product Π g_j goes INSIDE ψ, not outside.
        # ψ(Γ·Π g_j) ≠ Π ψ(Γ·g_j) because ψ is additive, not multiplicative.

        # But we can use MULTIPLICATIVE characters:
        # ψ(x) = (1/p) Σ_χ τ(χ) χ(x)  (Fourier inversion with Gauss sums)
        # Wait: ψ(x) = 1/(p-1) Σ_χ g(χ) χ^{-1}(x) for x ≠ 0
        # where g(χ) = Σ_{t} χ(t) ψ(t) is the Gauss sum.

        # So: Σ_C ψ(Γ/Q_C) = 1/(p-1) Σ_χ g(χ) χ^{-1}(Γ) · Σ_C χ^{-1}(1/Q_C)
        #                   = 1/(p-1) Σ_χ g(χ) χ^{-1}(Γ) · Σ_C Π_{j∈C} χ^{-1}(1/f_j)
        #                   = 1/(p-1) Σ_χ g(χ) χ^{-1}(Γ) · e_{r}(χ^{-1}(1/f_0),...,χ^{-1}(1/f_{n-1}))

        # This is a sum over multiplicative characters χ of the group F_p*!
        # |g(χ)| = √p for χ ≠ χ_0, |g(χ_0)| = 1.
        # The e_r values are elementary symmetric polynomials of ROOTS OF UNITY
        # (since |χ^{-1}(x)| = 1 for multiplicative characters).

        # BOUND: |S| ≤ 1/(p-1) [1·|e_r(1,...,1)| + (p-2)·√p·max_χ |e_r(χ^{-1}(1/f_j))|]
        #       = 1/(p-1) [C(n,r) + (p-2)√p · max_χ |e_r(χ)|]

        # For TRIVIAL character: e_r(1,...,1) = C(n,r) = N.
        # For NONTRIVIAL χ: e_r(χ(g_j)) = e_r of unit complex numbers.
        # By "e_w of random phases" heuristic: |e_r| ~ √(C(n,r)) = √N.

        # So: |S| ≤ [N + (p-2)√p·√N] / (p-1) ≈ √(pN) for p >> 1.

        # This gives the SAME √(pN) bound as the additive approach!

        if beta <= 3:
            print(f"\n  β={beta}: Γ={Gamma}")
            print(f"    |S| = {abs(S):.4f}, N = {N}")
            print(f"    Q distinct: {len(Q_dist)}, max fiber: {max(Q_dist.values())}")

            # Verify multiplicative Fourier expansion
            # Need all multiplicative characters of F_p*
            # χ_k(x) = ω_{p-1}^{k·ind(x)} for k=0,...,p-2
            g = find_primitive_root(p)
            # ind(x) = discrete log base g
            ind = {}
            v = 1
            for i in range(p-1):
                ind[v] = i
                v = v * g % p

            inv_factors = [pow(f, p-2, p) for f in factors]

            S_mult = 0j
            for k in range(p-1):
                # Gauss sum g(χ_k)
                gauss = sum(psi(pow(g, j, p), p) * cmath.exp(2j * PI2 * k * j / (p-1))
                            for j in range(p-1))

                # χ_k^{-1}(Γ) = exp(-2πi k·ind(Γ)/(p-1))
                chi_inv_Gamma = cmath.exp(-2j * PI2 * k * ind[Gamma] / (p-1))

                # e_r(χ_k^{-1}(1/f_j)) where χ_k^{-1}(x) = exp(-2πi k·ind(x)/(p-1))
                char_vals = [cmath.exp(-2j * PI2 * k * ind[inv_factors[j]] / (p-1))
                             for j in range(n)]
                er = compute_ew_array(n, r, char_vals)

                S_mult += gauss * chi_inv_Gamma * er / (p-1)

            diff = abs(S - S_mult)
            print(f"    Multiplicative Fourier: |S_mult|={abs(S_mult):.4f}, diff={diff:.2e}")

            # Compute max|e_r| over all nontrivial characters
            max_er = 0
            for k in range(1, p-1):
                char_vals = [cmath.exp(-2j * PI2 * k * ind[inv_factors[j]] / (p-1))
                             for j in range(n)]
                er = compute_ew_array(n, r, char_vals)
                if abs(er) > max_er:
                    max_er = abs(er)
            print(f"    max|e_r| (nontrivial χ) = {max_er:.4f}")
            print(f"    √N = {math.sqrt(N):.4f}")
            print(f"    Bound: [N + (p-2)√p·max|e_r|]/(p-1) = {(N + (p-2)*math.sqrt(p)*max_er)/(p-1):.4f}")

        break  # just one β for now


# ========== MAIN ==========
if __name__ == '__main__':
    print("DIRECTION C, ROUND 3: CANCELLATION ANALYSIS")
    print("=" * 70)

    # 4: e_w analytic structure (fast, informative)
    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        ew_gauss_phases(n, k, p)

    # 3: Product formula / Kloosterman
    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        product_formula_analysis(n, k, p)

    # 6: Weil bound for product sum
    for n, k, p in [(6, 3, 7), (8, 4, 17)]:
        weil_product_bound(n, k, p)

    # 2: M_alg cancellation
    for n, k, p in [(10, 5, 11), (10, 5, 31), (12, 6, 13)]:
        malg_cancellation(n, k, p)

    # 1: Phase correlation
    for n, k, p in [(6, 3, 7)]:
        phase_correlation(n, k, p)

    # 5: Conditional concentration (w=2 only)
    for n, k, p in [(6, 3, 7)]:
        conditional_concentration(n, k, p)

    print("\n\nDONE.")
