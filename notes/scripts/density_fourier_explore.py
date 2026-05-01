#!/usr/bin/env python3
"""
Density Bound Exploration via Fourier Analysis
================================================
Goal: Understand WHY M ≈ C(n,w)/p^c by computing the Fourier transform
of the σ-image indicator function.

Key quantity: f̂(u) = Σ_{B ∈ L^{(w)}} exp(2πi u·e(B)/p)

If max_{u≠0} |f̂(u)| is small relative to C(n,w), then for ANY codim-c subspace V:
  |Σ ∩ V| = C(n,w)/p^c + error
  where error ≤ max|f̂(u)| (roughly)

Experiments:
1. Full Fourier transform for small (n,p,w)
2. Density verification across varying codimension c
3. Character sum structure: does |f̂(u)| depend on u in a structured way?
4. Second moment of intersection sizes
5. Weil-type bound verification: |f̂(u)| vs p^{w/2} / w!
"""

import itertools
import math
import cmath
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool, cpu_count

# ========== CORE ARITHMETIC ==========

def primitive_root(p):
    """Find a primitive root mod p."""
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = (val * g) % p
        if len(seen) == p - 1:
            return g
    return None

def elem_sym(subset, w):
    """Compute elementary symmetric polynomials e_1,...,e_w of a subset."""
    # Use the product formula: Π(1 + x_i T) = Σ e_j T^j
    coeffs = [1]
    for x in subset:
        new_coeffs = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new_coeffs[i] = (new_coeffs[i] + c)
            new_coeffs[i + 1] = (new_coeffs[i + 1] + c * x)
        coeffs = new_coeffs
    # coeffs[j] = e_j(subset) (as integers, reduce mod p later)
    return coeffs[1:w+1]  # e_1, ..., e_w

def comb(n, k):
    return math.comb(n, k)

# ========== EXPERIMENT 1: Full Fourier Transform ==========

def exp1_full_fourier(n, p, w):
    """
    Compute f̂(u) for ALL u ∈ F_p^w.
    Returns: dict of stats including max|f̂|, distribution of |f̂|, etc.
    """
    print(f"\n{'='*60}")
    print(f"EXP 1: Full Fourier Transform  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = [(pow(g, j * ((p-1)//n), p)) for j in range(n)]
    L = sorted(set(L))
    assert len(L) == n, f"Expected {n} elements, got {len(L)}"
    
    # Compute all σ-image points
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    N = len(sigma_pts)
    print(f"  |Σ| = C({n},{w}) = {N}")
    
    # For w ≤ 3, we can compute full Fourier transform
    if p**w > 200000:
        print(f"  p^w = {p**w} too large for full Fourier, sampling instead")
        return exp1_sampled_fourier(n, p, w, L, sigma_pts)
    
    omega = cmath.exp(2j * cmath.pi / p)
    
    # f̂(u) = Σ_B ω^{u·e(B)}
    max_fhat = 0
    max_u = None
    fhat_magnitudes = []
    
    # Generate all u ∈ F_p^w
    total_u = p**w
    count = 0
    for u_tuple in itertools.product(range(p), repeat=w):
        if u_tuple == (0,) * w:
            # Main term
            fhat_magnitudes.append(N)
            continue
        
        # Compute u · e(B) for all B
        fhat = 0
        for e in sigma_pts:
            dot = sum(u_tuple[j] * e[j] for j in range(w)) % p
            fhat += omega ** dot
        
        mag = abs(fhat)
        fhat_magnitudes.append(mag)
        
        if mag > max_fhat:
            max_fhat = mag
            max_u = u_tuple
        
        count += 1
        if count % 10000 == 0:
            print(f"    processed {count}/{total_u} u-values...")
    
    # Statistics
    fhat_magnitudes_nonzero = [m for m in fhat_magnitudes if m > 0.01]
    
    print(f"\n  Results:")
    print(f"  f̂(0) = C(n,w) = {N}")
    print(f"  max|f̂(u)| (u≠0) = {max_fhat:.4f}")
    print(f"  max u = {max_u}")
    print(f"  ratio max|f̂|/f̂(0) = {max_fhat/N:.6f}")
    print(f"  √N = {math.sqrt(N):.4f}")
    print(f"  p^(w/2) = {p**(w/2):.4f}")
    print(f"  p^(w/2)/w! = {p**(w/2)/math.factorial(w):.6f}")
    print(f"  √(N) = {math.sqrt(N):.4f}")
    
    # Histogram of |f̂| magnitudes
    bins = [0, 0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, float('inf')]
    hist = Counter()
    for m in fhat_magnitudes:
        for i in range(len(bins)-1):
            if bins[i] <= m < bins[i+1]:
                hist[f"[{bins[i]},{bins[i+1]})"] += 1
                break
    
    print(f"\n  Distribution of |f̂(u)|:")
    for k in sorted(hist.keys()):
        print(f"    {k}: {hist[k]}")
    
    # Check Parseval: Σ|f̂|^2 = p^w · N
    parseval_sum = sum(m**2 for m in fhat_magnitudes)
    parseval_expected = p**w * N
    print(f"\n  Parseval check:")
    print(f"    Σ|f̂|^2 = {parseval_sum:.1f}")
    print(f"    p^w · N = {parseval_expected}")
    print(f"    ratio = {parseval_sum/parseval_expected:.6f}")
    
    return {
        'max_fhat': max_fhat,
        'max_u': max_u,
        'N': N,
        'ratio': max_fhat / N
    }

def exp1_sampled_fourier(n, p, w, L, sigma_pts):
    """Sample random u-vectors for large parameter spaces."""
    import random
    random.seed(42)
    
    N = len(sigma_pts)
    omega = cmath.exp(2j * cmath.pi / p)
    
    max_fhat = 0
    max_u = None
    n_samples = min(50000, p**w)
    
    # Also test structured u-vectors:
    # u = (a, 0, ..., 0): tests equidistribution of e_1
    # u = (0, a, 0, ..., 0): tests e_2
    # etc.
    structured_us = []
    for j in range(w):
        for a in range(1, min(p, 100)):
            u = [0]*w
            u[j] = a
            structured_us.append(tuple(u))
    
    # Random u-vectors
    random_us = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(n_samples)]
    
    all_us = structured_us + random_us
    
    results = []
    for idx, u_tuple in enumerate(all_us):
        if u_tuple == (0,)*w:
            continue
        
        fhat = 0
        for e in sigma_pts:
            dot = sum(u_tuple[j] * e[j] for j in range(w)) % p
            fhat += omega ** dot
        
        mag = abs(fhat)
        results.append((mag, u_tuple))
        
        if mag > max_fhat:
            max_fhat = mag
            max_u = u_tuple
        
        if (idx+1) % 5000 == 0:
            print(f"    processed {idx+1}/{len(all_us)} u-values, current max = {max_fhat:.4f}")
    
    print(f"\n  Results ({len(all_us)} u-vectors sampled):")
    print(f"  f̂(0) = C(n,w) = {N}")
    print(f"  max|f̂(u)| = {max_fhat:.4f}")
    print(f"  max u = {max_u}")
    print(f"  ratio max|f̂|/N = {max_fhat/N:.6f}")
    print(f"  √N = {math.sqrt(N):.4f}")
    
    # Top 10
    results.sort(reverse=True)
    print(f"\n  Top 10 |f̂(u)|:")
    for mag, u in results[:10]:
        print(f"    |f̂({u})| = {mag:.4f}")
    
    # Check structured vs random
    n_struct = len(structured_us)
    struct_max = max(r[0] for r in results[:n_struct] if r[1] in set(structured_us)) if structured_us else 0
    rand_max = max(r[0] for r in results[n_struct:]) if results[n_struct:] else 0
    print(f"\n  Structured u max = {struct_max:.4f}")
    print(f"  Random u max = {rand_max:.4f}")
    
    return {'max_fhat': max_fhat, 'max_u': max_u, 'N': N, 'ratio': max_fhat/N}


# ========== EXPERIMENT 2: Density vs Codimension ==========

def exp2_density_vs_codim(n, p, w):
    """
    For each codimension c = 1,...,w-1: sample random codim-c subspaces,
    count |Σ ∩ V|, compare with C(n,w)/p^c.
    """
    import random
    random.seed(123)
    
    print(f"\n{'='*60}")
    print(f"EXP 2: Density vs Codimension  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = sorted(set((pow(g, j * ((p-1)//n), p)) for j in range(n)))
    assert len(L) == n
    
    # Compute all σ-image points
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    N = len(sigma_pts)
    print(f"  |Σ| = {N}")
    
    for c in range(1, w):
        d = w - c  # dimension of V
        predicted = N / (p**c)
        n_trials = 2000
        
        counts = []
        for _ in range(n_trials):
            # Random codim-c affine subspace:
            # c random linear forms ℓ_j(σ) = r_j
            # ℓ_j = Σ a_{ji} σ_i, r_j ∈ F_p
            A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(c)]
            r = [random.randint(0, p-1) for _ in range(c)]
            
            cnt = 0
            for e in sigma_pts:
                ok = True
                for j in range(c):
                    val = sum(A[j][i] * e[i] for i in range(w)) % p
                    if val != r[j]:
                        ok = False
                        break
                if ok:
                    cnt += 1
            counts.append(cnt)
        
        mean_M = sum(counts) / len(counts)
        max_M = max(counts)
        var_M = sum((x - mean_M)**2 for x in counts) / len(counts)
        
        print(f"\n  c={c} (dim={d}): predicted={predicted:.3f}")
        print(f"    mean M = {mean_M:.3f}")
        print(f"    max M = {max_M}")
        print(f"    var M = {var_M:.4f}")
        print(f"    mean/predicted = {mean_M/predicted:.4f}" if predicted > 0.001 else f"    predicted ≈ 0")
        print(f"    distribution: {Counter(counts).most_common(10)}")


# ========== EXPERIMENT 3: Character Sum Structure ==========

def exp3_character_structure(n, p, w):
    """
    Compute |f̂(u)| for u along coordinate axes and diagonals.
    Check: does |f̂| depend on which e_j we probe?
    Key question: is the cancellation UNIFORM across all directions?
    """
    print(f"\n{'='*60}")
    print(f"EXP 3: Character Sum Structure  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = sorted(set((pow(g, j * ((p-1)//n), p)) for j in range(n)))
    assert len(L) == n
    
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    N = len(sigma_pts)
    omega = cmath.exp(2j * cmath.pi / p)
    
    print(f"  N = C({n},{w}) = {N}")
    
    # For each coordinate j: scan all a ∈ F_p^*
    for j in range(w):
        mags = []
        for a in range(1, p):
            u = [0]*w
            u[j] = a
            fhat = sum(omega ** (sum(u[i]*e[i] for i in range(w)) % p) for e in sigma_pts)
            mags.append(abs(fhat))
        
        max_mag = max(mags)
        mean_mag = sum(mags) / len(mags)
        rms_mag = math.sqrt(sum(m**2 for m in mags) / len(mags))
        
        print(f"\n  e_{j+1} axis: max|f̂| = {max_mag:.3f}, mean = {mean_mag:.3f}, RMS = {rms_mag:.3f}")
        
        # Weil prediction for e_1 axis: S(a)^w / w! where S(a) = Σ_{x∈L} ψ(ax)
        if j == 0:
            # e_1 = x_1 + ... + x_w, so f̂ ≈ (S(a))^w/w! (for distinct tuples)
            gauss_sums = []
            for a in range(1, p):
                s = sum(omega ** ((a * x) % p) for x in L)
                gauss_sums.append(abs(s))
            print(f"    Gauss sums |S(a)|: max={max(gauss_sums):.3f}, mean={sum(gauss_sums)/len(gauss_sums):.3f}")
            print(f"    max|S|^{w}/{w}! = {max(gauss_sums)**w / math.factorial(w):.3f}")
            print(f"    Compare: max|f̂| on e1 axis = {max_mag:.3f}")
    
    # Diagonal: u = (a, a, ..., a)
    mags_diag = []
    for a in range(1, p):
        u = [a]*w
        fhat = sum(omega ** (sum(u[i]*e[i] for i in range(w)) % p) for e in sigma_pts)
        mags_diag.append(abs(fhat))
    
    print(f"\n  Diagonal u=(a,...,a): max|f̂| = {max(mags_diag):.3f}, mean = {sum(mags_diag)/len(mags_diag):.3f}")


# ========== EXPERIMENT 4: Intersection Second Moment ==========

def exp4_second_moment(n, p, w):
    """
    For codimension c: compute E[M^2] exactly (over all codim-c subspaces).
    If Var(M) = E[M^2] - E[M]^2 ≈ E[M], then M is Poisson-distributed.
    """
    import random
    random.seed(456)
    
    print(f"\n{'='*60}")
    print(f"EXP 4: Second Moment Analysis  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = sorted(set((pow(g, j * ((p-1)//n), p)) for j in range(n)))
    assert len(L) == n
    
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    N = len(sigma_pts)
    
    # Second moment: E[M^2] = (1/p^w) Σ_σ Σ_{σ'} P(σ ∈ V ∧ σ' ∈ V)
    # For random codim-c V: P(σ ∈ V) = 1/p^c
    # P(σ ∈ V ∧ σ' ∈ V) = 1/p^{2c}  if σ, σ' are lin. indep (mod V)
    #                      = 1/p^c    if σ = σ'
    #                      = 1/p^{2c-dim(span)} otherwise
    
    # Instead of exact computation, just do Monte Carlo
    for c in range(1, w):
        n_trials = 5000
        M_values = []
        
        for _ in range(n_trials):
            # Random codim-c subspace
            A = [[random.randint(0, p-1) for _ in range(w)] for _ in range(c)]
            r = [random.randint(0, p-1) for _ in range(c)]
            
            cnt = 0
            for e in sigma_pts:
                ok = True
                for j in range(c):
                    if sum(A[j][i] * e[i] for i in range(w)) % p != r[j]:
                        ok = False
                        break
                if ok:
                    cnt += 1
            M_values.append(cnt)
        
        mean = sum(M_values) / len(M_values)
        var = sum((x - mean)**2 for x in M_values) / len(M_values)
        E_M2 = sum(x**2 for x in M_values) / len(M_values)
        predicted_mean = N / p**c
        
        # Poisson check: Var ≈ mean
        print(f"\n  c={c}: E[M]={mean:.4f} (predicted {predicted_mean:.4f})")
        print(f"    Var[M]={var:.4f}")
        print(f"    Var/E[M]={var/mean:.4f}" if mean > 0.01 else "    mean ≈ 0")
        print(f"    max M = {max(M_values)}")
        print(f"    P(M=0) = {M_values.count(0)/len(M_values):.3f}")
        print(f"    P(M≥2) = {sum(1 for x in M_values if x >= 2)/len(M_values):.3f}")


# ========== EXPERIMENT 5: σ-Image General Position ==========

def exp5_sigma_geometry(n, p, w):
    """
    Check if σ-image points are in "general position" in F_p^w.
    Specifically: how many σ-image points lie on any hyperplane?
    This bounds max|f̂(u)|.
    """
    import random
    random.seed(789)
    
    print(f"\n{'='*60}")
    print(f"EXP 5: σ-Image Geometry  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = sorted(set((pow(g, j * ((p-1)//n), p)) for j in range(n)))
    assert len(L) == n
    
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    N = len(sigma_pts)
    print(f"  N = {N}")
    
    # For each hyperplane (codim 1): count σ-image points on it
    # A hyperplane: Σ a_i σ_i = r
    # Max over all hyperplanes = max Fourier coefficient (essentially)
    
    # Sample many random hyperplanes
    n_hyp = 5000
    max_on_hyp = 0
    predicted = N / p
    
    hyp_counts = []
    for _ in range(n_hyp):
        a = [random.randint(0, p-1) for _ in range(w)]
        if all(x == 0 for x in a):
            continue
        r = random.randint(0, p-1)
        
        cnt = sum(1 for e in sigma_pts if sum(a[i]*e[i] for i in range(w)) % p == r)
        hyp_counts.append(cnt)
        if cnt > max_on_hyp:
            max_on_hyp = cnt
    
    print(f"  Predicted N/p = {predicted:.3f}")
    print(f"  Max points on any hyperplane (out of {n_hyp}): {max_on_hyp}")
    print(f"  Mean: {sum(hyp_counts)/len(hyp_counts):.3f}")
    print(f"  Max/predicted = {max_on_hyp/predicted:.3f}" if predicted > 0.01 else "  predicted ≈ 0")
    
    # EXHAUSTIVE for small p: check ALL hyperplanes through origin (projective)
    if p <= 31 and w <= 3:
        print(f"\n  Exhaustive hyperplane check (p={p}, w={w}):")
        max_exhaust = 0
        for a_tuple in itertools.product(range(p), repeat=w):
            if all(x == 0 for x in a_tuple):
                continue
            # Normalize: first nonzero = 1
            first_nz = next(i for i, x in enumerate(a_tuple) if x != 0)
            if a_tuple[first_nz] != 1:
                continue  # skip non-canonical
            
            for r in range(p):
                cnt = sum(1 for e in sigma_pts 
                         if sum(a_tuple[i]*e[i] for i in range(w)) % p == r)
                if cnt > max_exhaust:
                    max_exhaust = cnt
                    max_hyp = (a_tuple, r)
        
        print(f"  TRUE max points on hyperplane: {max_exhaust}")
        print(f"  Achieving hyperplane: a={max_hyp[0]}, r={max_hyp[1]}")
        print(f"  Ratio to N/p: {max_exhaust/predicted:.3f}" if predicted > 0.01 else "  predicted ≈ 0")


# ========== EXPERIMENT 6: Weil Bound for Subgroup Sums ==========

def exp6_weil_check(n, p, w):
    """
    Compute the exact character sums S_j(a) = Σ_{x ∈ L} ψ(a·x^j) for j=1,...,w
    and check if |S_j| ≤ √p (Weil bound).
    
    Then compute |f̂(u)| for u = (u_1, 0,..., 0) and compare with S_1(u_1)^w / w!
    """
    print(f"\n{'='*60}")
    print(f"EXP 6: Weil Bound Check  n={n}, p={p}, w={w}")
    print(f"{'='*60}")
    
    g = primitive_root(p)
    L = sorted(set((pow(g, j * ((p-1)//n), p)) for j in range(n)))
    assert len(L) == n
    
    omega = cmath.exp(2j * cmath.pi / p)
    
    # S(a) = Σ_{x ∈ L} ψ(ax)
    print(f"  Gauss-type sums S(a) = Σ_{{x ∈ L}} ψ(ax):")
    max_S = 0
    for a in range(1, p):
        s = sum(omega ** ((a * x) % p) for x in L)
        mag = abs(s)
        if mag > max_S:
            max_S = mag
    
    print(f"  max|S(a)| = {max_S:.4f}")
    print(f"  √p = {math.sqrt(p):.4f}")
    print(f"  n = {n}")
    print(f"  ratio max|S|/√p = {max_S/math.sqrt(p):.4f}")
    
    # S_j(a) = Σ_{x ∈ L} ψ(a·x^j)
    for j in range(1, w+1):
        max_Sj = 0
        for a in range(1, p):
            s = sum(omega ** ((a * pow(x, j, p)) % p) for x in L)
            mag = abs(s)
            if mag > max_Sj:
                max_Sj = mag
        print(f"  S_{j}(a): max|S_{j}| = {max_Sj:.4f}, ratio to √p: {max_Sj/math.sqrt(p):.4f}")
    
    # Compare f̂ on e_1-axis with S^w/w!
    sigma_pts = []
    for B in itertools.combinations(L, w):
        e = tuple(x % p for x in elem_sym(B, w))
        sigma_pts.append(e)
    
    print(f"\n  Comparing f̂(a,0,...,0) with S(a)^{w}/{w}!:")
    for a in [1, 2, g % p]:
        # Exact f̂
        u = [a] + [0]*(w-1)
        fhat = sum(omega ** (sum(u[i]*e[i] for i in range(w)) % p) for e in sigma_pts)
        fhat_mag = abs(fhat)
        
        # S(a)^w / w!
        s = sum(omega ** ((a * x) % p) for x in L)
        s_mag = abs(s)
        predicted = s_mag**w / math.factorial(w)
        
        print(f"  a={a}: |f̂| = {fhat_mag:.4f}, |S|^w/w! = {predicted:.4f}, ratio = {fhat_mag/predicted:.4f}" if predicted > 0.001 else f"  a={a}: |f̂| = {fhat_mag:.4f}, predicted ≈ 0")


# ========== MAIN ==========

if __name__ == '__main__':
    # Test configurations: (n, p, w)
    configs = [
        # Small, exact
        (6, 7, 3),
        (8, 17, 3),
        (10, 11, 3),
        (10, 31, 3),
        (12, 13, 3),
        (12, 37, 3),
        # Larger p
        (10, 61, 3),
        (10, 101, 3),
        # w = 4
        (8, 17, 4),
        (10, 11, 4),
    ]
    
    for n, p, w in configs:
        if (p - 1) % n != 0:
            print(f"\nSKIP ({n},{p},{w}): n does not divide p-1")
            continue
        
        print(f"\n{'#'*70}")
        print(f"# Configuration: n={n}, p={p}, w={w}, c_max={w-1}")
        print(f"# C(n,w) = {comb(n,w)}, C(n,w)/p = {comb(n,w)/p:.3f}")
        print(f"# C(n,w)/p^2 = {comb(n,w)/p**2:.6f}")
        print(f"{'#'*70}")
        
        # Run experiments
        exp1_full_fourier(n, p, w)
        exp2_density_vs_codim(n, p, w)
        exp3_character_structure(n, p, w)
        # exp4 and exp5 are slower, run selectively
        if n <= 10 and p <= 31:
            exp4_second_moment(n, p, w)
            exp5_sigma_geometry(n, p, w)
        exp6_weil_check(n, p, w)
