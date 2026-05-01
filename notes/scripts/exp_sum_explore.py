#!/usr/bin/env python3
"""
Direction C: Exponential sum exploration.

Key object: S(α) = Σ_{B∈([n],w)} ψ(Σ_j α_j σ_j(B))

where σ_j = j-th elem sym poly of {ω^i : i∈B}, ψ = additive char of F_p.

Questions:
1. What is the FULL landscape of |S(α)| for all α ∈ F_p^w?
2. Which directions α give max|S|? What's their algebraic structure?
3. Can we decompose S via Newton identities (power sums p_k)?
4. Product formula: S = e_w(ψ-weighted phases)?
5. Ratio max|S|/N as function of p (for fixed n)?
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

def power_sums(roots, p, max_k):
    """Compute power sums p_k = Σ r^k mod p for k=1..max_k."""
    ps = []
    for k in range(1, max_k + 1):
        ps.append(sum(pow(r, k, p) for r in roots) % p)
    return ps

def psi(x, p):
    return cmath.exp(1j * PI2 * (x % p) / p)

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

def johnson_w_mds(n, k):
    """Johnson radius for MDS code: w = floor(n - sqrt(n(k-1)))."""
    return int(n - math.sqrt(n * (k - 1)))

# ========== Experiment 1: Full α-landscape for small cases ==========
def exp1_alpha_landscape(n, k, p):
    """Compute |S(α)| for ALL α ∈ F_p^w and find structure of maximizers."""
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    # Precompute σ(B) for all B
    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p)[1:])  # (σ_1,...,σ_w)

    print(f"\n{'='*70}")
    print(f"EXP 1: α-landscape — RS[{n},{k}], p={p}, w={w}, N={N}")
    print(f"{'='*70}")

    if p**w > 200000:
        print(f"  p^w = {p**w} too large, sampling 50000 directions")
        import random
        max_mag = 0
        max_alpha = None
        mags = []
        for _ in range(50000):
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            if all(a == 0 for a in alpha):
                continue
            S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p) for sig in all_sigma)
            mag = abs(S)
            mags.append((mag, alpha))
            if mag > max_mag:
                max_mag = mag
                max_alpha = alpha
        mags.sort(reverse=True)
        print(f"  max|S| = {max_mag:.4f}  at α = {max_alpha}")
        print(f"  max|S|/N = {max_mag/N:.6f}")
        print(f"  Top 10 directions:")
        for mag, alpha in mags[:10]:
            print(f"    |S|={mag:.4f}  α={alpha}")
        return max_mag, max_alpha

    # Exhaustive for small p^w
    max_mag = 0
    max_alpha = None
    mag_histogram = defaultdict(int)
    top_alphas = []

    for alpha in product(range(p), repeat=w):
        if all(a == 0 for a in alpha):
            continue
        S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p) for sig in all_sigma)
        mag = abs(S)
        bucket = int(mag / N * 20)
        mag_histogram[bucket] += 1
        if mag > max_mag * 0.95 or len(top_alphas) < 20:
            top_alphas.append((mag, alpha))
            top_alphas.sort(reverse=True)
            top_alphas = top_alphas[:20]
        if mag > max_mag:
            max_mag = mag
            max_alpha = alpha

    print(f"  max|S| = {max_mag:.4f}  at α = {max_alpha}")
    print(f"  max|S|/N = {max_mag/N:.6f}")
    print(f"  √N = {math.sqrt(N):.4f},  max|S|/√N = {max_mag/math.sqrt(N):.4f}")
    print(f"\n  Top 10 directions:")
    for mag, alpha in top_alphas[:10]:
        print(f"    |S|={mag:.4f} ({mag/N:.4f}N)  α={alpha}")

    print(f"\n  |S|/N histogram:")
    for b in sorted(mag_histogram):
        lo, hi = b*5, (b+1)*5
        cnt = mag_histogram[b]
        bar = '#' * min(cnt * 40 // max(max(mag_histogram.values()), 1), 40)
        print(f"    [{lo:3d}%-{hi:3d}%]: {cnt:6d} {bar}")

    return max_mag, max_alpha


# ========== Experiment 2: Power sum decomposition ==========
def exp2_power_sum_structure(n, k, p):
    """
    σ_j relates to power sums via Newton's identities.
    p_k(B) = Σ_{i∈B} ω^{ki} — partial character sum.

    Question: Is S(α) expressible in terms of power sum character sums?
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP 2: Power sum structure — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    # Precompute both σ and power sums for all B
    all_B = list(combinations(range(n), w))
    all_sigma = []  # σ_1,...,σ_w
    all_ps = []     # p_1,...,p_w

    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p)[1:])
        all_ps.append(power_sums(roots, p, w))

    # Verify Newton's identities
    print("\n  Verifying Newton's identities (σ_j from p_k)...")
    errors = 0
    for b_idx in range(min(100, len(all_B))):
        sig = [1] + list(all_sigma[b_idx])  # σ_0=1, σ_1,...,σ_w
        ps = all_ps[b_idx]  # p_1,...,p_w

        # Newton: k·σ_k = Σ_{i=1}^{k} (-1)^{i-1} σ_{k-i} p_i
        for kk in range(1, w + 1):
            lhs = kk * sig[kk] % p
            rhs = 0
            for i in range(1, kk + 1):
                rhs += pow(-1, i - 1, p) * sig[kk - i] * ps[i - 1]
            rhs %= p
            if lhs != rhs:
                errors += 1
    print(f"    Newton identity errors: {errors}")

    # Key question: For the maximizing α, which power sums dominate?
    # Compute correlation between Σ α_j σ_j and individual p_k's

    # Find a maximizing α first (just use σ_1 direction as baseline)
    S_sigma1 = sum(psi(sig[0], p) for sig in all_sigma)
    print(f"\n  σ_1-only: |S(1,0,...,0)| = {abs(S_sigma1):.4f}")
    S_sigmaw = sum(psi(sig[-1], p) for sig in all_sigma)
    print(f"  σ_w-only: |S(0,...,0,1)| = {abs(S_sigmaw):.4f}")

    # Compare with power sum character sums
    for kk in range(1, min(w + 1, 6)):
        S_pk = sum(psi(ps[kk - 1], p) for ps in all_ps)
        print(f"  p_{kk}-only: |S_p{kk}| = {abs(S_pk):.4f}")

    # Correlation matrix between σ and p values
    print(f"\n  Correlation: σ_j values vs p_k values (mod p, on [0,p))")
    print(f"  (Checking if σ_j ≈ linear function of p_1,...,p_j)")

    # For σ_2: Newton says 2σ_2 = σ_1 p_1 - p_2 = p_1² - p_2 (since σ_1=p_1)
    # So σ_2 = (p_1² - p_2)/2 mod p (if 2 is invertible)
    if p > 2:
        inv2 = pow(2, p - 2, p)
        match = 0
        for b_idx in range(len(all_B)):
            sig2 = all_sigma[b_idx][1]  # σ_2
            ps = all_ps[b_idx]
            predicted = (ps[0] * ps[0] - ps[1]) * inv2 % p
            if predicted == sig2:
                match += 1
        print(f"  σ_2 = (p_1²-p_2)/2: {match}/{len(all_B)} match")

    return


# ========== Experiment 3: Product formula / generating function ==========
def exp3_generating_function(n, k, p):
    """
    S(α) = Σ_B ψ(Σ α_j σ_j(B))

    For α_j = β^j: Σ α_j σ_j = [Π_{i∈B}(1+β·ω^i)] - 1

    So S(β,β²,...,β^w) = Σ_B ψ(Π_{i∈B}(1+β·ω^i) - 1)

    This is a CHARACTER SUM OF A PRODUCT — multiplicative Weil bound applicable!
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP 3: Generating function / product formula — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))
    all_sigma = []
    for B in all_B:
        roots = [L[i] for i in B]
        all_sigma.append(elem_sym(roots, p)[1:])

    # Test: S(β, β², ..., β^w) = Σ_B ψ(Π(1+β·ω^i) - 1)
    print("\n  Testing product formula S(β,β²,...,β^w) = Σ_B ψ(Π(1+βω^i)-1)")

    for beta in range(1, min(p, 20)):
        # Via σ
        alpha = tuple(pow(beta, j + 1, p) for j in range(w))
        S_sigma = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                      for sig in all_sigma)

        # Via product
        S_prod = 0j
        for B in all_B:
            prod = 1
            for i in B:
                prod = prod * (1 + beta * L[i]) % p
            S_prod += psi((prod - 1) % p, p)

        diff = abs(S_sigma - S_prod)
        print(f"    β={beta:3d}: |S_σ|={abs(S_sigma):.4f}, |S_prod|={abs(S_prod):.4f}, diff={diff:.2e}")

    # Now: for the PRODUCT form, can we apply Weil-type bounds?
    # S = Σ_B ψ(Π_{i∈B}(1+β·ω^i) - 1)
    #
    # The product Π_{i∈B}(1+β·ω^i) is a MULTIPLICATIVE function of B.
    # Under ψ, it becomes additive character of a multiplicative expression.
    #
    # Key: Π_{i∈B}(1+β·ω^i) = P(β) / Q(β) where P(x) = Π_{i∈[n]}(1+x·ω^i) = 1+x^n
    # and Q(β) = Π_{j∉B}(1+β·ω^j).
    #
    # So Π_{i∈B}(1+β·ω^i) = (1+β^n) / Π_{j∉B}(1+β·ω^j)
    #
    # For β ≠ root of -1: this is well-defined.

    print(f"\n  Full product identity: Π_{{all i}}(1+β·ω^i) = 1+β^n mod p")
    for beta in range(1, min(p, 10)):
        full_prod = 1
        for i in range(n):
            full_prod = full_prod * (1 + beta * L[i]) % p
        expected = (1 + pow(beta, n, p)) % p
        print(f"    β={beta}: Π(1+βω^i) = {full_prod}, 1+β^n = {expected}, {'OK' if full_prod == expected else 'FAIL'}")

    # So for any B of size w, complement B^c of size n-w:
    # Π_{i∈B}(1+βω^i) = (1+β^n) / Π_{j∈B^c}(1+βω^j)
    #
    # S = Σ_B ψ((1+β^n) · inv(Π_{j∈B^c}(1+βω^j)) - 1)
    #   = Σ_B ψ((1+β^n) · Π_{j∈B^c}(1+βω^j)^{-1} - 1)
    #
    # Setting r = n-w (complement size), this is a sum over (n-w)-subsets.

    # Even more interesting: for β such that 1+β^n = 0 (β is n-th root of -1):
    # Π_{i∈B}(1+βω^i) = 0 for ALL B (since the full product = 0 and (1+βω^i)≠0 individually... wait)
    # Actually no: 1+β^n = 0 means β^n = -1, so β^n + 1 = 0.
    # But Π(1+βω^i) = 1+β^n = 0 means at least one factor is 0, i.e., 1+βω^i = 0 for some i.
    # That means βω^i = -1, i.e., ω^i = -1/β.
    # If -1/β ∈ L then exactly one factor vanishes.
    # If -1/β ∉ L then... the product = 1+β^n = 0 but no single factor is 0. Contradiction!
    # Actually Π(1+βω^i) = 1+β^n is a THEOREM (since x^n-1 = Π(x-ω^i), so Π(1+βω^i) = Π((-ω^i)(-(1+βω^i)/ω^i))... hmm let me check.
    # Actually: Π_{i=0}^{n-1}(x - ω^i) = x^n - 1. Set x = -1/β (assuming β≠0):
    # Π((-1/β) - ω^i) = (-1/β)^n - 1 = (-1)^n/β^n - 1
    # Π(-(1/β + ω^i)) = (-1)^n (Π(1/β + ω^i)) = (-1)^n / β^n · Π(1 + βω^i)
    # Hmm let me just verify computationally.

    return


# ========== Experiment 4: Scaling of max|S| with p ==========
def exp4_p_scaling(n, k):
    """For fixed n, how does max|S(α)|/N scale with p?"""
    w = johnson_w_mds(n, k)
    N = math.comb(n, w)
    c = n - k - w

    ps = primes_1modn(n, 8)

    print(f"\n{'='*70}")
    print(f"EXP 4: p-scaling — RS[{n},{k}], w={w}, c={c}, N={N}")
    print(f"{'='*70}")

    print(f"\n  {'p':>5} {'p^c':>8} {'N/p^c':>8} {'max|S|':>10} {'max/N':>8} {'max/√N':>8} {'max/√(Np^c)':>12} {'√p':>6}")
    print(f"  {'-'*75}")

    for p in ps:
        if p**c > 500000 or N > 5000:
            continue
        omega = find_omega(n, p)
        L_vals = [pow(omega, i, p) for i in range(n)]

        # Precompute σ
        all_B = list(combinations(range(n), w))
        all_sigma = []
        for B in all_B:
            roots = [L_vals[i] for i in B]
            all_sigma.append(elem_sym(roots, p)[1:])

        # For each condition-compatible α direction, compute S
        # Actually: the relevant α's come from a CENTER c_high via:
        # α_j(t) = (-1)^j Σ_m t_m c_{k+m+j}
        # But for WORST CASE over centers, we should scan all α.
        # For small p^w: scan all α. For large: sample.

        max_S = 0
        total_tested = 0

        if p**w <= 100000:
            for alpha in product(range(p), repeat=w):
                if all(a == 0 for a in alpha):
                    continue
                S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                        for sig in all_sigma)
                mag = abs(S)
                if mag > max_S:
                    max_S = mag
                total_tested += 1
        else:
            import random
            for _ in range(min(50000, p**w)):
                alpha = tuple(random.randint(0, p-1) for _ in range(w))
                if all(a == 0 for a in alpha):
                    continue
                S = sum(psi(sum(alpha[j] * sig[j] for j in range(w)) % p, p)
                        for sig in all_sigma)
                mag = abs(S)
                if mag > max_S:
                    max_S = mag
                total_tested += 1

        pc = p**c
        sqrtNpc = math.sqrt(N * pc)
        sqrtN = math.sqrt(N)
        sqrtp = math.sqrt(p)
        print(f"  {p:5d} {pc:8d} {N/pc:8.3f} {max_S:10.4f} {max_S/N:8.5f} {max_S/sqrtN:8.4f} {max_S/sqrtNpc:12.6f} {sqrtp:6.2f}")


# ========== Experiment 5: σ_2 character sum structure ==========
def exp5_sigma2_charsum(n, k, p):
    """
    σ_2(B) = Σ_{i<j, i,j∈B} ω^i · ω^j = Σ_{i<j} ω^{i+j}

    This is the "pairwise product sum". Character sum:
    Σ_B ψ(α·σ_2(B)) = Σ_B ψ(α · Σ_{i<j∈B} ω^{i+j})

    Key: σ_2 = (σ_1² - p_2)/2 = (p_1² - p_2)/2.
    So ψ(α·σ_2) = ψ(α(p_1² - p_2)/2)

    For p_1 = Σ_{i∈B} ω^i and p_2 = Σ_{i∈B} ω^{2i}:
    these are PARTIAL CHARACTER SUMS on the cyclic group.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)
    inv2 = pow(2, p - 2, p) if p > 2 else 0

    print(f"\n{'='*70}")
    print(f"EXP 5: σ_2 character sum — RS[{n},{k}], p={p}, w={w}, N={N}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    # Compute σ_2(B) and (p_1², p_2) for all B
    sigma2_vals = []
    p1_vals = []
    p2_vals = []

    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        sigma2_vals.append(es[2])
        p1 = sum(roots) % p
        p2 = sum(pow(r, 2, p) for r in roots) % p
        p1_vals.append(p1)
        p2_vals.append(p2)

        # Verify: σ_2 = (p_1² - p_2)/2
        predicted = (p1 * p1 - p2) * inv2 % p
        assert predicted == es[2], f"Newton fail at B={B}"

    # Distribution of σ_2 values
    sigma2_dist = defaultdict(int)
    for v in sigma2_vals:
        sigma2_dist[v] += 1

    max_fiber = max(sigma2_dist.values())
    avg_fiber = N / p
    print(f"  σ_2 distribution: {len(sigma2_dist)} distinct values (out of p={p})")
    print(f"  max fiber = {max_fiber}, avg = {avg_fiber:.2f}, ratio = {max_fiber/avg_fiber:.2f}")

    # Joint (p_1, p_2) distribution
    joint_dist = defaultdict(int)
    for i in range(N):
        joint_dist[(p1_vals[i], p2_vals[i])] += 1
    max_joint = max(joint_dist.values())
    avg_joint = N / p**2
    print(f"  (p_1,p_2) joint: {len(joint_dist)} distinct, max={max_joint}, avg={avg_joint:.2f}")

    # Character sum Σ_B ψ(α·σ_2) for all α
    max_S2 = 0
    for alpha in range(1, p):
        S = sum(psi(alpha * v, p) for v in sigma2_vals)
        mag = abs(S)
        if mag > max_S2:
            max_S2 = mag
    print(f"  max|Σ ψ(α·σ_2)| = {max_S2:.4f}, /N = {max_S2/N:.6f}, /√N = {max_S2/math.sqrt(N):.4f}")

    # Character sum Σ_B ψ(α·p_1 + β·p_2) — additive structure!
    # p_1 = Σ ω^i, p_2 = Σ ω^{2i}: these are LINEAR in the indicator vars x_i.
    # So ψ(α·p_1 + β·p_2) = Π_{i∈B} ψ(α·ω^i + β·ω^{2i})
    #
    # Therefore: Σ_B ψ(α·p_1 + β·p_2) = e_w(ψ(α·ω^0+β·ω^0), ψ(α·ω^1+β·ω^2), ...)
    #
    # This is the w-th elementary symmetric polynomial of UNIT COMPLEX NUMBERS!

    print(f"\n  KEY INSIGHT: Σ_B ψ(α·p_1 + β·p_2) = e_w(φ_0,...,φ_{{n-1}})")
    print(f"  where φ_i = ψ(α·ω^i + β·ω^{{2i}})")
    print(f"  Verifying...")

    for alpha, beta in [(1, 0), (0, 1), (1, 1), (2, 3)]:
        if alpha >= p or beta >= p:
            continue
        # Direct
        S_direct = 0j
        for B in all_B:
            val = (alpha * p1_vals[all_B.index(B)] + beta * p2_vals[all_B.index(B)]) % p
            S_direct += psi(val, p)

        # Via generating function
        phases = [psi(alpha * L[i] + beta * pow(L[i], 2, p), p) for i in range(n)]
        # e_w of phases = Σ_{|B|=w} Π_{i∈B} phases[i]
        S_gf = 0j
        for B in all_B:
            prod = 1
            for i in B:
                prod *= phases[i]
            S_gf += prod

        diff = abs(S_direct - S_gf)
        print(f"    (α,β)=({alpha},{beta}): |S_direct|={abs(S_direct):.4f}, |S_gf|={abs(S_gf):.4f}, diff={diff:.2e}")

    # Bound on e_w of unit complex numbers?
    # |e_w(z_1,...,z_n)| where |z_i|=1
    # Trivial: |e_w| ≤ C(n,w)
    # For i.i.d. uniform on unit circle: E[|e_w|²] = C(n,w) (by Parseval on {0,1}^n)
    # So typical |e_w| ~ √C(n,w) = √N

    # Now: σ_2 = (p_1² - p_2)/2, which is QUADRATIC in p_1.
    # So ψ(α·σ_2) = ψ(α(p_1² - p_2)/2) = ψ(α·p_1²/2) · ψ(-α·p_2/2)
    # The p_2 part factors: ψ(-α·p_2/2) = Π_{i∈B} ψ(-α·ω^{2i}/2)
    # But p_1² = (Σ_{i∈B} ω^i)² DOES NOT FACTOR — it couples all pairs!
    #
    # Decompose: p_1² = Σ_{i∈B} ω^{2i} + 2·Σ_{i<j∈B} ω^{i+j} = p_2 + 2σ_2
    # So σ_2 = (p_1² - p_2)/2, circular.
    #
    # The key obstacle: σ_2 involves ALL PAIRS in B, creating coupling.

    return


# ========== Experiment 6: DFT decomposition of S ==========
def exp6_dft_decomposition(n, k, p):
    """
    Decompose S(α) via DFT on the cyclic group Z/nZ.

    Key: for α = (0,...,0,α_w): S factors as (N/n)·Σ_{x∈L} ψ(α_w·x)
    For general α: what's the DFT structure?

    Idea: write S(α) = Σ_{s∈Z/nZ} S_s(α) where S_s sums over B with Σ B ≡ s (mod n).
    Then S_s(α) has a fixed σ_w = ω^s, so the sum is over (σ_1,...,σ_{w-1}) with σ_w fixed.
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP 6: DFT decomposition — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    # Group B's by subset sum mod n
    groups = defaultdict(list)
    for idx, B in enumerate(all_B):
        s = sum(B) % n
        groups[s].append(idx)

    print(f"  Subset sum distribution (mod {n}):")
    sizes = [len(groups[s]) for s in range(n)]
    print(f"    sizes: {sizes}")
    print(f"    all equal = {len(set(sizes)) == 1}")
    if len(set(sizes)) == 1:
        print(f"    N/n = {N/n:.2f} = {sizes[0]}")

    # For σ_1-only direction:
    # S(α,0,...,0) = Σ_B ψ(α·σ_1(B)) = Σ_B ψ(α·Σ_{i∈B} ω^i)
    # This = Σ_B Π_{i∈B} ψ(α·ω^i) = e_w(ψ(αω^0),...,ψ(αω^{n-1}))
    #
    # Generating function: [u^w] Π_{i=0}^{n-1} (1 + u·ψ(αω^i))
    #
    # For α∈F_p*: the phases ψ(αω^i) are n distinct roots of unity (up to their distribution in C)

    print(f"\n  Generating function approach for σ_1-only:")
    for alpha in range(1, min(p, 8)):
        phases = [psi(alpha * L[i], p) for i in range(n)]

        # Build the generating function coefficients
        # poly[j] = e_j(phases)
        poly = [0j] * (n + 1)
        poly[0] = 1
        for ph in phases:
            for j in range(n, 0, -1):
                poly[j] = poly[j] + poly[j-1] * ph
        ew = poly[w]

        # Direct computation
        S_direct = sum(psi(alpha * sum(L[i] for i in B) % p, p) for B in all_B)

        print(f"    α={alpha}: |e_w|={abs(ew):.4f}, |S_direct|={abs(S_direct):.4f}, diff={abs(ew-S_direct):.2e}")

    # Key question: for the generating function [u^w] Π(1+u·z_i),
    # when z_i = ψ(a·ω^i), what's the MAXIMUM of |e_w(z)| over a?
    #
    # This is related to the Littlewood problem / flat polynomials.

    print(f"\n  Max |e_w| over α ∈ F_p*:")
    max_ew = 0
    max_alpha_ew = 0
    all_ew = []
    for alpha in range(1, p):
        phases = [psi(alpha * L[i], p) for i in range(n)]
        poly = [0j] * (w + 1)
        poly[0] = 1
        for ph in phases:
            for j in range(w, 0, -1):
                poly[j] = poly[j] + poly[j-1] * ph
        mag = abs(poly[w])
        all_ew.append(mag)
        if mag > max_ew:
            max_ew = mag
            max_alpha_ew = alpha

    print(f"    max|e_w| = {max_ew:.4f} at α={max_alpha_ew}")
    print(f"    max/N = {max_ew/N:.6f}")
    print(f"    avg|e_w| = {sum(all_ew)/len(all_ew):.4f}")
    print(f"    √N = {math.sqrt(N):.4f}")

    # Interpretation: the σ_1 character sum is bounded by the max of |e_w|
    # over all phase configurations {ψ(α·ω^i)}.
    #
    # For L = F_p*: e_w = 1 for all w (perfect cancellation! — Note 0065)
    # For proper subgroup L: e_w can be up to O(√N)


# ========== Experiment 7: Multi-variable Weil bound attempt ==========
def exp7_weil_attempt(n, k, p):
    """
    For the product formula α_j = β^j:
    S(β,...,β^w) = Σ_B ψ(Π_{i∈B}(1+β·ω^i) - 1)

    Can we bound this using Weil's theorem?

    Weil: |Σ_{x∈F_p} ψ(f(x))| ≤ (deg f - 1)√p for f not a perfect p-th power.

    Our sum is over SUBSETS not field elements. But:
    Π_{i∈B}(1+β·ω^i) ranges over a specific subset of F_p as B varies.
    Its "image" = {Π_{i∈B}(1+β·ω^i) : |B|=w} ⊂ F_p.

    How big is this image? How distributed?
    """
    w = johnson_w_mds(n, k)
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    N = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"EXP 7: Product image analysis — RS[{n},{k}], p={p}, w={w}")
    print(f"{'='*70}")

    all_B = list(combinations(range(n), w))

    for beta in [1, 2, 3]:
        if beta >= p:
            continue
        # Compute product values
        prods = []
        for B in all_B:
            prod = 1
            for i in B:
                prod = prod * (1 + beta * L[i]) % p
            prods.append(prod)

        # Distribution
        val_counts = defaultdict(int)
        for v in prods:
            val_counts[v] += 1

        n_distinct = len(val_counts)
        max_fiber = max(val_counts.values())
        zero_count = val_counts.get(0, 0)

        print(f"\n  β={beta}: Π(1+β·ω^i) over {N} subsets")
        print(f"    distinct values: {n_distinct} (out of p={p})")
        print(f"    max fiber: {max_fiber}, avg: {N/p:.2f}")
        print(f"    zero count: {zero_count}")

        # Character sum of the product
        S_prod = sum(psi(v, p) for v in prods)
        print(f"    |Σ ψ(prod)| = {abs(S_prod):.4f}")
        print(f"    |Σ ψ(prod)|/N = {abs(S_prod)/N:.6f}")

        # Compare with: if products were uniform on F_p,
        # |S| ~ √N by central limit
        print(f"    √N = {math.sqrt(N):.4f}")

    return


# ========== MAIN ==========
if __name__ == '__main__':
    print("DIRECTION C: EXPONENTIAL SUM EXPLORATION")
    print("=" * 70)

    # Small cases for exhaustive analysis
    cases = [
        (6, 3, 7),
        (8, 4, 17),
        (10, 5, 11),
        (10, 5, 31),
        (12, 6, 13),
    ]

    for n, k, p in cases:
        exp3_generating_function(n, k, p)

    print("\n\n" + "=" * 70)
    print("GENERATING FUNCTION EXPERIMENTS DONE. Now power sum structure...\n")

    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp2_power_sum_structure(n, k, p)

    print("\n\n" + "=" * 70)
    print("POWER SUM DONE. Now σ_2 analysis...\n")

    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp5_sigma2_charsum(n, k, p)

    print("\n\n" + "=" * 70)
    print("σ_2 DONE. Now DFT decomposition...\n")

    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp6_dft_decomposition(n, k, p)

    print("\n\n" + "=" * 70)
    print("DFT DONE. Now product image analysis...\n")

    for n, k, p in [(6, 3, 7), (8, 4, 17), (10, 5, 11)]:
        exp7_weil_attempt(n, k, p)

    print("\n\n" + "=" * 70)
    print("PRODUCT IMAGE DONE. Now p-scaling...\n")

    for n, k in [(6, 3), (8, 4), (10, 5)]:
        exp4_p_scaling(n, k)

    print("\n\nDONE.")
