#!/usr/bin/env python3
"""
Direction C, Round 2: Deep exponential sum analysis.

Key findings from Round 1:
1. Product formula VERIFIED: S(β,β²,...,β^w) = Σ_B ψ(Π(1+βω^i)-1)
2. Correct product identity: Π_{i=0}^{n-1}(1+βω^i) = 1-(-β)^n
3. Power sum factorization: Σ_B ψ(Σ α_k p_k) = e_w(φ_0,...,φ_{n-1}) for LINEAR combos of power sums
4. σ_j for j≥2 introduces NONLINEAR coupling (σ_2 = (p_1²-p_2)/2)

Focus areas:
A. What α directions actually arise from compatibility conditions? (c-dim subspace)
B. Bound on e_w(z_1,...,z_n) for structured phases z_i = ψ(f(ω^i))
C. Gauss sum structure when L = F_p* vs proper subgroup
D. Nonlinear (quadratic) character sum: can we handle σ_2?
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


# ========== A: Compatibility subspace analysis ==========
def exp_A_subspace(n, k, p):
    """
    The compatibility conditions D_m(σ) = 0 give α_j(t) = (-1)^j Σ_m t_m c_{k+m+j}.
    For a center c_high = (c_k,...,c_{n-1}), the map t → α = (α_1,...,α_w) is linear.
    Its IMAGE is a c-dim subspace V_c of F_p^w.

    Question: is max_{α∈V_c} |S(α)| << max_{all α} |S(α)|?
    """
    w = johnson_w_mds(n, k)
    c = n - k - w
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    nk = n - k

    print(f"\n{'='*70}")
    print(f"EXP A: Subspace analysis — RS[{n},{k}], p={p}, w={w}, c={c}")
    print(f"{'='*70}")

    # Precompute σ for all B
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p)[1:])

    import random

    # Try multiple centers, find the one with max M_alg
    best_M = 0
    best_c_high = None
    best_V = None

    for trial in range(3000):
        c_high = [random.randint(0, p-1) for _ in range(nk)]

        # Compute α_j(t) for basis vectors t = e_m
        # α_j(e_m) = (-1)^j c_{k + m + j} where c_{k+m+j} = c_high[m+j] if m+j < nk else 0
        V_basis = []
        for m in range(c):
            alpha_vec = []
            for j in range(w):
                c_idx = m + j + 1  # +1 because j goes 0..w-1 but σ goes σ_1..σ_w
                # Wait: α_j for j=0..w-1 corresponds to σ_{j+1}... no.
                # Actually: the condition uses Σ_{j=0}^w (-1)^j σ_j c_{m+j}
                # Setting σ_0 = 1: the sum = c_m + Σ_{j=1}^w (-1)^j σ_j c_{m+j}
                # So the char sum exponent for condition m is:
                # t_m · [c_m + Σ_j (-1)^j σ_j c_{m+j}]
                # = t_m c_m + Σ_j t_m (-1)^j c_{m+j} σ_j
                # So α_j = Σ_m t_m (-1)^j c_{k+w+m+j} ← wait, need to be careful with indexing
                pass

        # Actually: for center c_high = (c_k, c_{k+1},...,c_{n-1}), the conditions are:
        # D_{k+w+m}(σ) = Σ_{j=0}^w (-1)^j σ_j c_high[w+m-j] for m=0,...,c-1
        # Wait, from Note 0065: D_m(σ) = Σ_{j=0}^w (-1)^j σ_j c_{m-w+j}
        # For m = k+w+m_off: c_{m-w+j} = c_{k+m_off+j} = c_high[m_off+j]
        #
        # The character sum exponent:
        # Σ_{m_off=0}^{c-1} t_{m_off} D_{k+w+m_off}(σ)
        # = Σ_{m_off} t_{m_off} [Σ_j (-1)^j σ_j c_high[m_off+j]]
        # = Σ_j [Σ_{m_off} t_{m_off} (-1)^j c_high[m_off+j]] σ_j
        # = σ_0 term + Σ_{j=1}^w α_j σ_j
        # where α_j = Σ_{m_off} t_{m_off} (-1)^j c_high[m_off+j]
        #
        # σ_0 = 1, so the σ_0 term = Σ_{m_off} t_{m_off} c_high[m_off]
        # This shifts the phase globally but doesn't affect |S|.

        # Build V_c basis: for each basis vector e_{m_off} (t = (0,...,1,...,0)):
        V_basis = []
        for m_off in range(c):
            alpha_row = []
            for j in range(1, w + 1):
                c_idx = m_off + j
                coeff = pow(-1, j, p) * (c_high[c_idx] if c_idx < nk else 0)
                alpha_row.append(coeff % p)
            V_basis.append(tuple(alpha_row))

        # Count compatible B's (M_alg)
        cnt = 0
        for sig in all_sigma:
            ok = True
            for m_off in range(c):
                val = c_high[m_off]  # σ_0 term
                for j in range(1, w + 1):
                    c_idx = m_off + j
                    if c_idx < nk:
                        val += pow(-1, j, p) * sig[j-1] * c_high[c_idx]
                if val % p != 0:
                    ok = False
                    break
            if ok:
                cnt += 1

        if cnt > best_M:
            best_M = cnt
            best_c_high = c_high[:]
            best_V = V_basis[:]

    print(f"  Best M_alg = {best_M}, center = {best_c_high[:6]}...")
    print(f"  V_c basis vectors (α_1,...,α_w):")
    for i, v in enumerate(best_V):
        print(f"    v_{i} = {v}")

    # Now compute max|S(α)| over V_c vs over all α
    # Over V_c: α = Σ t_m v_m, enumerate all t ∈ F_p^c
    max_S_Vc = 0
    for t in product(range(p), repeat=c):
        if all(ti == 0 for ti in t):
            continue
        alpha = tuple(sum(t[m] * best_V[m][j] for m in range(c)) % p for j in range(w))
        if all(a == 0 for a in alpha):
            continue
        S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p) for sig in all_sigma)
        mag = abs(S)
        if mag > max_S_Vc:
            max_S_Vc = mag

    # Over ALL α (sample if too big)
    max_S_all = 0
    max_S_all_note = ""
    if p**w <= 100000:
        for alpha in product(range(p), repeat=w):
            if all(a == 0 for a in alpha):
                continue
            S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p) for sig in all_sigma)
            mag = abs(S)
            if mag > max_S_all:
                max_S_all = mag
    else:
        import random
        for _ in range(50000):
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            if all(a == 0 for a in alpha):
                continue
            S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p) for sig in all_sigma)
            mag = abs(S)
            if mag > max_S_all:
                max_S_all = mag
        max_S_all_note = " (sampled)"

    print(f"\n  max|S| over V_c (dim {c}): {max_S_Vc:.4f}  ({max_S_Vc/N:.4f} N)")
    print(f"  max|S| over all α{max_S_all_note}: {max_S_all:.4f}  ({max_S_all/N:.4f} N)")
    print(f"  Ratio V_c/all: {max_S_Vc/max_S_all:.4f}" if max_S_all > 0 else "")
    print(f"  √N = {math.sqrt(N):.4f}")

    return max_S_Vc, max_S_all


# ========== B: e_w bound for structured phases ==========
def exp_B_ew_bound(n, k, p):
    """
    S_linear(α_1,...,α_w) = e_w(φ_0,...,φ_{n-1})
    where φ_i = ψ(Σ_k α_k ω^{ki})

    For LINEAR combinations of power sums only.

    Bound: by Cauchy's inequality on the slice {0,1}^n ∩ {Σ=w}:
    |e_w(z)| ≤ C(n,w)^{1/2} · (Σ|z_i|^2)^{w/2} = C(n,w)^{1/2} · n^{w/2}

    But |z_i| = 1, so trivially |e_w| ≤ C(n,w).
    Better: Parseval on the slice gives E[|e_w|²] = C(n,w).
    So typical |e_w| ~ √C(n,w).

    Question: when z_i = ψ(f(ω^i)) for polynomial f, is there extra cancellation?
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP B: e_w bound for structured phases — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    # Compute |e_w(z)| for z_i = ψ(f(ω^i)) where f is polynomial of degree d

    # Degree 1: f(x) = αx → z_i = ψ(α·ω^i)
    print(f"\n  Degree 1 phases: z_i = ψ(α·ω^i)")
    max_ew_d1 = 0
    for alpha in range(1, p):
        phases = [psi(alpha * L[i], p) for i in range(n)]
        # Compute e_w via generating function
        poly = [0j] * (w + 1)
        poly[0] = 1
        for ph in phases:
            for j in range(w, 0, -1):
                poly[j] += poly[j-1] * ph
        mag = abs(poly[w])
        if mag > max_ew_d1:
            max_ew_d1 = mag
    print(f"    max|e_w| = {max_ew_d1:.6f}")

    # Degree 2: f(x) = αx + βx²
    print(f"\n  Degree 2 phases: z_i = ψ(α·ω^i + β·ω^2i)")
    max_ew_d2 = 0
    best_d2 = None
    for alpha in range(p):
        for beta in range(1, p):
            phases = [psi((alpha * L[i] + beta * pow(L[i], 2, p)) % p, p) for i in range(n)]
            poly = [0j] * (w + 1)
            poly[0] = 1
            for ph in phases:
                for j in range(w, 0, -1):
                    poly[j] += poly[j-1] * ph
            mag = abs(poly[w])
            if mag > max_ew_d2:
                max_ew_d2 = mag
                best_d2 = (alpha, beta)
    print(f"    max|e_w| = {max_ew_d2:.6f} at (α,β)={best_d2}")

    # Degree w: f(x) = Σ α_k x^k
    print(f"\n  Degree {w} phases: z_i = ψ(Σ_k α_k ω^{{ki}})")
    if p**w <= 50000:
        max_ew_dw = 0
        best_dw = None
        for alpha in product(range(p), repeat=w):
            if all(a == 0 for a in alpha):
                continue
            phases = [psi(sum(alpha[k] * pow(L[i], k+1, p) for k in range(w)) % p, p) for i in range(n)]
            poly = [0j] * (w + 1)
            poly[0] = 1
            for ph in phases:
                for j in range(w, 0, -1):
                    poly[j] += poly[j-1] * ph
            mag = abs(poly[w])
            if mag > max_ew_dw:
                max_ew_dw = mag
                best_dw = alpha
        print(f"    max|e_w| = {max_ew_dw:.6f} at α={best_dw}")
    else:
        import random
        max_ew_dw = 0
        for _ in range(20000):
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            if all(a == 0 for a in alpha):
                continue
            phases = [psi(sum(alpha[k] * pow(L[i], k+1, p) for k in range(w)) % p, p) for i in range(n)]
            poly = [0j] * (w + 1)
            poly[0] = 1
            for ph in phases:
                for j in range(w, 0, -1):
                    poly[j] += poly[j-1] * ph
            mag = abs(poly[w])
            if mag > max_ew_dw:
                max_ew_dw = mag
        print(f"    max|e_w| = {max_ew_dw:.6f} (sampled)")

    print(f"\n  Summary:")
    print(f"    N = C({n},{w}) = {N}")
    print(f"    √N = {math.sqrt(N):.4f}")
    print(f"    max|e_w| (deg 1): {max_ew_d1:.4f}  ratio to √N: {max_ew_d1/math.sqrt(N):.4f}")
    print(f"    max|e_w| (deg 2): {max_ew_d2:.4f}  ratio to √N: {max_ew_d2/math.sqrt(N):.4f}")
    print(f"    max|e_w| (deg w): {max_ew_dw:.4f}  ratio to √N: {max_ew_dw/math.sqrt(N):.4f}")


# ========== C: Quadratic character sum (σ_2 direction) ==========
def exp_C_quadratic(n, k, p):
    """
    σ_2 = (p_1² - p_2)/2 has a QUADRATIC term in p_1.

    ψ(α·σ_2) = ψ(α(p_1²-p_2)/2) = ψ(α·p_1²/2) · ψ(-α·p_2/2)

    The p_2 part: ψ(-α·p_2/2) = Π_{i∈B} ψ(-α·ω^{2i}/2) → FACTORS!
    The p_1² part: ψ(α·(Σ ω^i)²/2) = ψ(α·Σ_{i,j} ω^{i+j}/2) → does NOT factor

    But we can use GAUSS SUM trick for the quadratic:
    ψ(a·x²) = Σ_{y∈F_p} ψ(xy) · δ(x²=y²/4a)...

    Better: Fourier expand ψ(a·p_1²) over all values of p_1.

    ψ(a·p_1²) = (1/p) Σ_{τ} G(a,τ) ψ(τ·p_1)
    where G(a,τ) = Σ_{x∈F_p} ψ(ax² + τx) is a Gauss sum = ε_p √p · ψ(-τ²/4a)

    So: Σ_B ψ(α·σ_2) = Σ_B ψ(α(p_1²-p_2)/2)
        = Σ_B ψ(α·p_1²/2) · ψ(-α·p_2/2)
        = (1/p) Σ_τ G(α/2, τ) · Σ_B ψ(τ·p_1) · ψ(-α·p_2/2)
        = (1/p) Σ_τ G(α/2, τ) · Σ_B Π_{i∈B} ψ(τ·ω^i - α·ω^{2i}/2)
        = (1/p) Σ_τ G(α/2, τ) · e_w(ψ(τ·ω^0 - α·ω^0/2), ..., ψ(τ·ω^{n-1} - α·ω^{2(n-1)}/2))

    THIS REDUCES THE QUADRATIC CHARACTER SUM TO A SUM OF e_w TERMS!

    |Σ_B ψ(α·σ_2)| ≤ (1/p) Σ_τ |G| · |e_w(...)| = (√p/p) Σ_τ |e_w(...)|
    = (1/√p) · Σ_τ |e_w(φ^{(τ)}_0,...,φ^{(τ)}_{n-1})|

    If max|e_w| ~ √N, then: |S| ≤ (1/√p) · p · √N = √p · √N = √(pN)

    This is the same O(√(pN)) bound from Note 0065! But now with a PROOF path.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    inv2 = pow(2, p-2, p)

    print(f"\n{'='*70}")
    print(f"EXP C: Quadratic Gauss expansion of σ_2 — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    # Compute σ_2(B) and (p_1, p_2) for all B
    sigma2_vals = []
    p1_vals = []
    p2_vals = []
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma2_vals.append(es[2])
        p1_vals.append(sum(roots) % p)
        p2_vals.append(sum(pow(r, 2, p) for r in roots) % p)

    # Direct computation of Σ_B ψ(α·σ_2)
    for alpha in [1, 2, 3]:
        S_direct = sum(psi(alpha * s2, p) for s2 in sigma2_vals)

        # Gauss expansion
        # G(a, τ) = Σ_{x=0}^{p-1} ψ(a·x² + τ·x) = ε √p · ψ(-τ²/(4a))
        # where ε = Legendre(a,p) · Gauss sum
        a = alpha * inv2 % p  # α/2
        inv4a = pow(4 * a % p, p-2, p)

        S_gauss = 0j
        ew_mags = []
        for tau in range(p):
            # G(a, τ)
            G = sum(psi((a * t * t + tau * t) % p, p) for t in range(p))

            # e_w of phases φ_i = ψ(τ·ω^i - α·ω^{2i}/2)
            phases = [psi((tau * L[i] - alpha * inv2 * pow(L[i], 2, p)) % p, p)
                      for i in range(n)]
            poly = [0j] * (w + 1)
            poly[0] = 1
            for ph in phases:
                for j in range(w, 0, -1):
                    poly[j] += poly[j-1] * ph
            ew = poly[w]
            ew_mags.append(abs(ew))

            S_gauss += G * ew / p

        diff = abs(S_direct - S_gauss)
        max_ew_here = max(ew_mags)
        avg_ew_here = sum(ew_mags) / len(ew_mags)

        print(f"\n  α={alpha}:")
        print(f"    |S_direct| = {abs(S_direct):.6f}")
        print(f"    |S_gauss|  = {abs(S_gauss):.6f}  diff = {diff:.2e}")
        print(f"    max|e_w(τ)| = {max_ew_here:.4f}")
        print(f"    avg|e_w(τ)| = {avg_ew_here:.4f}")
        print(f"    Bound √p·max|e_w|/p = {math.sqrt(p)*max_ew_here/p:.4f}")
        print(f"    Tight bound (1/p)·Σ|G|·|e_w| = {sum(abs(sum(psi((a*t*t+tau*t)%p,p) for t in range(p)))*ew_mags[tau] for tau in range(p))/p:.4f}")


# ========== D: General σ-decomposition via Newton ==========
def exp_D_newton_decomposition(n, k, p):
    """
    For w conditions at once:
    Σ_{j=1}^w α_j σ_j = Σ_{j=1}^w α_j · N_j(p_1,...,p_j)

    where N_j are the Newton polynomials:
    N_1 = p_1
    N_2 = (p_1² - p_2)/2
    N_3 = (p_1³ - 3p_1p_2 + 2p_3)/6

    The TOTAL expression is a polynomial F(p_1,...,p_w) of degree w.

    Expand ψ(F(p_1,...,p_w)) using multi-dimensional Gauss sums?
    For degree-2 terms: one Gauss expansion per quadratic term.
    For degree-3+: higher-order exponential sums.

    Alternative: COMPLETE the square / diagonalize.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP D: Newton decomposition — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    # For w=2: F = α_1 p_1 + α_2(p_1²-p_2)/2
    # This is QUADRATIC in p_1, LINEAR in p_2.
    # Can diagonalize via Gauss sum on p_1.

    # For w=3: F = α_1 p_1 + α_2(p_1²-p_2)/2 + α_3(p_1³-3p_1p_2+2p_3)/6
    # This is CUBIC in (p_1,p_2,p_3) with leading term α_3 p_1³/6.
    # Gauss sum trick: Fourier expand p_1³ term...
    # For CUBIC: no clean diagonalization. Need cubic Gauss sums.

    if w == 2:
        print(f"  w=2: F = α_1·p_1 + α_2·(p_1²-p_2)/2")
        print(f"  Quadratic in p_1, reducible via Gauss sum")
    elif w == 3:
        print(f"  w=3: F = α_1·p_1 + α_2·(p_1²-p_2)/2 + α_3·(p_1³-3p_1p_2+2p_3)/6")
        print(f"  Cubic in p_1 — needs cubic exponential sums")

    # KEY IDEA: Instead of the full Newton decomposition,
    # try a HYBRID approach:
    #
    # S(α) = Σ_B ψ(Σ α_j σ_j(B))
    #       = Σ_B ψ(linear(B) + quadratic(B) + ... )
    #
    # Separate into:
    # S(α) = Σ_{v∈F_p} [Σ_{B: p_1(B)=v} ψ(Σ α_j σ_j(B))]
    #       = Σ_v [Σ_{B: p_1=v} ψ(F_v(p_2,...,p_w))]
    #
    # where F_v is the polynomial with p_1 FIXED to v.
    # When p_1 is fixed: σ_1 = v is fixed, σ_2 = (v²-p_2)/2 is LINEAR in p_2, etc.
    # So the INNER sum factors!

    all_B = list(combinations(range(n), w))

    # Group by p_1 value
    p1_groups = defaultdict(list)
    for idx, B in enumerate(all_B):
        roots = [L[i] for i in B]
        p1 = sum(roots) % p
        p1_groups[p1].append(idx)

    print(f"\n  p_1 fiber sizes: min={min(len(v) for v in p1_groups.values())}, "
          f"max={max(len(v) for v in p1_groups.values())}, "
          f"avg={N/len(p1_groups):.1f}")

    # For each p_1=v: what is σ_j(B)?
    # σ_1 = v (fixed)
    # σ_2 = (v² - p_2)/2 — linear in p_2 = Σ ω^{2i}
    # So σ_2 given p_1: ψ of linear function of B → FACTORS as e_w!
    #
    # Wait, p_2 = Σ_{i∈B} ω^{2i} is still LINEAR in indicators.
    # But conditioning on p_1 = v restricts B to the set {B: Σ ω^i ≡ v}.
    # The inner sum is not just e_w anymore.

    # Actually let me think again. Given p_1 is fixed:
    # σ_2 = (p_1² - p_2)/2 = (v² - p_2)/2
    # α_2 σ_2 = α_2(v² - p_2)/2 = α_2 v²/2 - α_2 p_2/2
    # α_1 σ_1 = α_1 v
    #
    # Total = α_1 v + α_2 v²/2 - α_2 p_2/2 + higher order terms
    #
    # The terms α_1 v + α_2 v²/2 are CONSTANT (since p_1 = v is fixed)
    # The remaining: -α_2 p_2/2 + α_3(σ_3 terms)...
    #
    # For w=2: only σ_1 and σ_2, so remaining = -α_2 p_2/2
    # This is LINEAR in p_2, so the inner sum FACTORS:
    # Σ_{B:p_1=v} ψ(-α_2 p_2/2) = Σ_{B:p_1=v} Π_{i∈B} ψ(-α_2 ω^{2i}/2)

    # For w=3: σ_3 = (p_1³ - 3p_1 p_2 + 2p_3)/6
    # Given p_1=v: σ_3 = (v³ - 3v·p_2 + 2p_3)/6
    # α_3 σ_3 = α_3(v³ - 3v·p_2 + 2p_3)/6
    # = α_3 v³/6 - α_3 v p_2/2 + α_3 p_3/3
    #
    # Total remaining (non-constant): (-α_2/2 - α_3 v/2) p_2 + (α_3/3) p_3
    # This is LINEAR in (p_2, p_3), so the inner sum FACTORS:
    # Σ_{B:p_1=v} Π_{i∈B} ψ((-α_2/2 - α_3 v/2)ω^{2i} + (α_3/3)ω^{3i})

    # BEAUTIFUL! The ONLY non-factoring part is the p_1 condition.
    # Once we condition on p_1, everything else is LINEAR in (p_2,...,p_w)!

    print(f"\n  *** KEY INSIGHT ***")
    print(f"  Conditioned on p_1 = v, σ_j for j≥2 becomes LINEAR in (p_2,...,p_w)")
    print(f"  So: S(α) = Σ_v ψ(const(v)) · [Σ_{{B:p_1=v}} Π_{{i∈B}} ψ(g_v(ω^i))]")
    print(f"  where g_v(x) = Σ_{{k=2}}^w β_k(v) x^k is polynomial in x")
    print(f"")
    print(f"  The INNER sum is e_w restricted to {{B: Σ ω^i = v}} — ")
    print(f"  i.e., e_w of phases ψ(g_v(ω^i)) on the FIBER over p_1=v.")

    # Verify for w=2
    if w >= 2:
        inv2 = pow(2, p-2, p)
        alpha = (1, 1)  # test direction

        S_direct = 0j
        for B in all_B:
            roots = [L[i] for i in B]
            es = elem_sym(roots, p)
            S_direct += psi((alpha[0] * es[1] + alpha[1] * es[2]) % p, p)

        S_fiber = 0j
        for v in range(p):
            # Constant part
            const = (alpha[0] * v + alpha[1] * v * v * inv2) % p
            # g_v(x) coefficient for x²: -α_2/(2) = -alpha[1] * inv2
            coeff_2 = (-alpha[1] * inv2) % p

            if w == 2:
                # Inner sum: Σ_{B:p_1=v} Π_{i∈B} ψ(coeff_2 · ω^{2i})
                phases = [psi(coeff_2 * pow(L[i], 2, p), p) for i in range(n)]

                # Need: Σ_{B:p_1=v} Π_{i∈B} phases[i]
                # This is NOT e_w of phases! It's e_w restricted to p_1=v subset.
                inner = 0j
                for idx in p1_groups.get(v, []):
                    prod = 1
                    for i in all_B[idx]:
                        prod *= phases[i]
                    inner += prod

                S_fiber += psi(const, p) * inner

            elif w == 3:
                inv3 = pow(3, p-2, p)
                # Coefficients for p_2 and p_3
                coeff_2 = (-alpha[1] * inv2) % p if len(alpha) > 1 else 0
                coeff_3 = 0
                if len(alpha) > 2:
                    coeff_2 = (coeff_2 - alpha[2] * v * inv2) % p
                    coeff_3 = (alpha[2] * inv3) % p

                phases = [psi((coeff_2 * pow(L[i], 2, p) + coeff_3 * pow(L[i], 3, p)) % p, p)
                          for i in range(n)]
                inner = 0j
                for idx in p1_groups.get(v, []):
                    prod = 1
                    for i in all_B[idx]:
                        prod *= phases[i]
                    inner += prod
                S_fiber += psi(const, p) * inner

        diff = abs(S_direct - S_fiber)
        print(f"\n  Verification (w={w}, α={alpha}):")
        print(f"    |S_direct| = {abs(S_direct):.6f}")
        print(f"    |S_fiber|  = {abs(S_fiber):.6f}")
        print(f"    diff = {diff:.2e}")

    # Now: the p_1 = v condition.
    # p_1 = Σ_{i∈B} ω^i ≡ v (mod p) — this is a SINGLE linear constraint.
    # The set {B : p_1(B) = v} is a "level set" of the first power sum.
    #
    # For the inner sum over this level set:
    # Σ_{B:p_1=v} Π_{i∈B} φ_i = (1/p) Σ_τ ψ(-τv) · Σ_B ψ(τ·p_1) Π φ_i
    #                           = (1/p) Σ_τ ψ(-τv) · e_w(φ_0·ψ(τω^0), ..., φ_{n-1}·ψ(τω^{n-1}))

    print(f"\n  Fiber extraction via Fourier:")
    print(f"  Σ_{{B:p_1=v}} Π φ_i = (1/p) Σ_τ ψ(-τv) · e_w(φ_i · ψ(τω^i))")

    # So the FULL sum becomes:
    # S(α) = Σ_v ψ(const(v)) · (1/p) Σ_τ ψ(-τv) · e_w(φ_i(v) · ψ(τω^i))
    #       = (1/p) Σ_τ Σ_v ψ(const(v) - τv) · e_w(...)
    #       = (1/p) Σ_τ e_w(ψ(τω^i + g_v(ω^i))) · Σ_v ψ(F(v) - τv)
    #
    # Wait, g_v depends on v too! So this doesn't quite factor.
    #
    # For w=2: g_v(x) = coeff_2 · x² doesn't depend on v.
    # const(v) = α_1 v + α_2 v²/(2)
    #
    # S(α) = (1/p) Σ_τ e_w(ψ(coeff_2·ω^{2i} + τ·ω^i)) · Σ_v ψ(α_1 v + α_2 v²/2 - τv)
    #       = (1/p) Σ_τ e_w(ψ(coeff_2·ω^{2i} + τ·ω^i)) · G_2(α_2/2, α_1 - τ)
    #
    # where G_2(a,b) = Σ_v ψ(av² + bv) is a GAUSS SUM = ε√p · ψ(-b²/(4a))

    if w == 2:
        inv2 = pow(2, p-2, p)
        alpha = (1, 1)
        coeff_2 = (-alpha[1] * inv2) % p

        S_fourier = 0j
        ew_list = []
        for tau in range(p):
            # e_w of phases ψ(coeff_2·ω^{2i} + τ·ω^i)
            phases = [psi((coeff_2 * pow(L[i], 2, p) + tau * L[i]) % p, p)
                      for i in range(n)]
            poly = [0j] * (w + 1)
            poly[0] = 1
            for ph in phases:
                for j in range(w, 0, -1):
                    poly[j] += poly[j-1] * ph
            ew = poly[w]
            ew_list.append(abs(ew))

            # Gauss sum G_2(α_2/2, α_1 - τ)
            a = alpha[1] * inv2 % p
            b = (alpha[0] - tau) % p
            G = sum(psi((a * v * v + b * v) % p, p) for v in range(p))

            S_fourier += ew * G / p

        S_direct2 = 0j
        for B in all_B:
            roots = [L[i] for i in B]
            es = elem_sym(roots, p)
            S_direct2 += psi((alpha[0] * es[1] + alpha[1] * es[2]) % p, p)

        diff = abs(S_direct2 - S_fourier)
        print(f"\n  Full Gauss + e_w decomposition (w=2, α={alpha}):")
        print(f"    |S_direct| = {abs(S_direct2):.6f}")
        print(f"    |S_fourier| = {abs(S_fourier):.6f}")
        print(f"    diff = {diff:.2e}")
        print(f"    max|e_w(τ)| = {max(ew_list):.4f}")
        print(f"    avg|e_w(τ)| = {sum(ew_list)/len(ew_list):.4f}")
        print(f"    √N = {math.sqrt(N):.4f}")

        # BOUND: |S| ≤ (1/p) Σ_τ |e_w(τ)| · |G(τ)| ≤ (√p/p) Σ_τ |e_w(τ)|
        # = (1/√p) · Σ_τ |e_w(τ)|
        # By Cauchy-Schwarz: ≤ (1/√p) · √p · √(Σ|e_w|²) = √(Σ|e_w|²/1)
        # Parseval: Σ|e_w|² = ... (need to compute)

        sum_ew2 = sum(x**2 for x in ew_list)
        print(f"\n    Σ|e_w|² = {sum_ew2:.4f}")
        print(f"    p·N = {p*N}")
        print(f"    CS bound: √(Σ|e_w|²) = {math.sqrt(sum_ew2):.4f}")
        print(f"    Full bound: (1/√p)·Σ|e_w| = {sum(ew_list)/math.sqrt(p):.4f}")

    # For w=3: g_v depends on v through -α_3 v/2 coefficient.
    # So we need DOUBLE Fourier: over τ (for p_1 constraint) and over v (for v-dependent coefficients).
    # This gives a DOUBLE exponential sum... more complex but still structured.

    if w >= 3:
        print(f"\n  For w≥3: g_v depends on v, need iterated Gauss expansion")
        print(f"  Structure: S = (1/p) Σ_τ Σ_v ψ(cubic(v)-τv) · e_w(ψ(linear_v(ω^i)+τω^i))")


# ========== E: Refined p-scaling with decomposition ==========
def exp_E_refined_scaling(n, k):
    """Test the Gauss+e_w decomposition bound across p values."""
    w = johnson_w_mds(n, k)
    N = math.comb(n, w)
    c = n - k - w
    ps = primes_1modn(n, 10)

    print(f"\n{'='*70}")
    print(f"EXP E: Refined p-scaling — RS[{n},{k}], w={w}, c={c}")
    print(f"{'='*70}")

    if w != 2:
        print(f"  Skipping (w={w} ≠ 2, decomposition is for w=2)")
        return

    print(f"\n  {'p':>5} {'max|S(σ2)|':>12} {'GS+ew bound':>12} {'ratio':>8} {'√(pN)':>8}")

    for p in ps:
        if N > 3000 or p > 200:
            continue
        omega = find_omega(n, p)
        L = [pow(omega, i, p) for i in range(n)]
        inv2 = pow(2, p-2, p)

        all_B = list(combinations(range(n), w))
        sigma2_vals = [elem_sym([L[i] for i in B], p)[2] for B in all_B]

        # max|S| for σ_2 direction
        max_S = 0
        for alpha in range(1, p):
            S = sum(psi(alpha * s2, p) for s2 in sigma2_vals)
            mag = abs(S)
            if mag > max_S:
                max_S = mag

        # Gauss+ew bound
        max_ew_bound = 0
        for alpha in range(1, p):
            coeff_2 = (-alpha * inv2) % p
            ew_sum = 0
            for tau in range(p):
                phases = [psi((coeff_2 * pow(L[i], 2, p) + tau * L[i]) % p, p) for i in range(n)]
                poly = [0j] * (w + 1)
                poly[0] = 1
                for ph in phases:
                    for j in range(w, 0, -1):
                        poly[j] += poly[j-1] * ph
                ew_sum += abs(poly[w])
            bound = ew_sum / math.sqrt(p)  # using |G| ≤ √p
            if bound > max_ew_bound:
                max_ew_bound = bound

        sqrtpN = math.sqrt(p * N)
        print(f"  {p:5d} {max_S:12.4f} {max_ew_bound:12.4f} {max_S/max_ew_bound:8.4f} {sqrtpN:8.2f}")


# ========== MAIN ==========
if __name__ == '__main__':
    print("DIRECTION C, ROUND 2: DEEP EXPONENTIAL SUM ANALYSIS")
    print("=" * 70)

    # D first: the Newton decomposition insight
    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp_D_newton_decomposition(n, k, p)

    # C: Quadratic Gauss expansion
    for n, k, p in [(6, 3, 7), (8, 4, 17)]:
        exp_C_quadratic(n, k, p)

    # A: Subspace analysis
    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp_A_subspace(n, k, p)

    # B: e_w bound for structured phases
    for n, k, p in [(6, 3, 7), (8, 4, 17)]:
        exp_B_ew_bound(n, k, p)

    # E: Refined scaling
    for n, k in [(6, 3)]:
        exp_E_refined_scaling(n, k)

    print("\n\nDONE.")
