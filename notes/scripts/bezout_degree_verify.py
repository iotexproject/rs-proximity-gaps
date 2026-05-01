#!/usr/bin/env python3
"""
Verify the Bézout degree structure for the density bound proof.

Key equation: x^n mod Λ_t(x) = r(t) where Λ_t is parameterized by
d = w-c free parameters. The degree of r_j(t) in the parameters t
determines the Bézout bound: M ≤ deg^d.

Also verify: for c ≥ 2 and large p, max M ≤ deg^d / p^c (heuristic).
"""
import numpy as np
import itertools
import math
import time
from multiprocessing import Pool, cpu_count

def primitive_root(p):
    for g in range(2, p):
        if pow(g, (p-1)//2, p) != 1:
            ok = True
            d = p-1; i = 2
            while i*i <= d:
                if d%i == 0 and pow(g, d//i, p) == 1: ok = False; break
                i += 1
            if ok: return g

def poly_mod(poly_x, mod_poly, p):
    """Compute poly_x mod mod_poly over F_p. Returns remainder."""
    r = list(poly_x)
    d = len(mod_poly)
    while len(r) >= d:
        coeff = r[-1] * pow(mod_poly[-1], p-2, p) % p
        for i in range(d):
            r[len(r)-d+i] = (r[len(r)-d+i] - coeff * mod_poly[i]) % p
        r.pop()
    return r

def compute_remainder_degree(n, w, p, L, V_basis):
    """
    For V parameterized by t = (t_1,...,t_d):
    Λ_t(x) = x^w + Σ_j f_j(t) x^{w-1-j} where f_j is linear in t.
    
    Compute x^n mod Λ_t symbolically to find degree in t.
    
    We use NUMERICAL approach: evaluate at many t-values and interpolate degree.
    """
    d = len(V_basis)  # dimension
    if d == 0:
        return 0, 0  # point, trivial
    
    # Method: compute M for many random subspaces at varying p,
    # or directly compute the degree by evaluating the remainder polynomial.
    
    # Direct method: for each monomial in t, compute the coefficient.
    # For degree D in d variables: there are C(D+d, d) monomials.
    # We need D ≈ n-w evaluations.
    
    # Instead, use the INTERPOLATION approach:
    # Pick many random t values, compute r(t), check the degree.
    
    import random
    random.seed(42)
    
    # V_basis: list of d vectors in F_p^w (basis of the subspace)
    # V_offset: a vector in F_p^w (the affine offset)
    # Λ_t = x^w + Σ_{j=1}^w (-1)^j (a_j + Σ_i t_i b_{ij}) x^{w-j}
    
    # For simplicity, use a_j = 0 (homogeneous case) and test degree.
    
    # Evaluate x^n mod Λ_t for random t ∈ F_p^d
    n_samples = min(p**d if p**d < 10000 else 5000, 5000)
    
    M_by_t = {}
    for _ in range(n_samples):
        t = tuple(random.randint(0, p-1) for _ in range(d))
        
        # Construct Λ_t coefficients
        e = [0] * w
        for j in range(w):
            e[j] = sum(t[i] * V_basis[i][j] for i in range(d)) % p
        
        # Λ_t(x) = x^w - e_1 x^{w-1} + e_2 x^{w-2} - ... + (-1)^w e_w
        # As coefficient list (low to high): [(-1)^w e_w, ..., -e_1, 1]
        lam = [0] * (w + 1)
        lam[w] = 1
        for j in range(1, w + 1):
            lam[w - j] = (-1)**j * e[j-1] % p
        
        # Compute x^n mod Λ_t
        # x^n as coefficient list: [0, ..., 0, 1] (length n+1)
        xn = [0] * (n + 1)
        xn[n] = 1
        
        r = poly_mod(xn, lam, p)
        # Pad to length w
        while len(r) < w:
            r.append(0)
        
        r_tuple = tuple(x % p for x in r)
        
        # Check if Λ_t has all roots in L
        # i.e., r = (1, 0, ..., 0) in our convention
        # Actually x^n mod Λ_t = 1 iff all roots are n-th roots of unity
        is_valid = (r_tuple == tuple([1] + [0]*(w-1)))
        
        if is_valid:
            M_by_t[t] = 1
        else:
            M_by_t[t] = 0
    
    n_valid = sum(M_by_t.values())
    
    return n_valid, n_samples

def verify_bezout(n, k, p):
    """Full Bézout verification for one config."""
    if (p-1) % n != 0: return
    g = primitive_root(p)
    L = sorted(set(pow(g, j*((p-1)//n), p) for j in range(n)))
    if len(L) != n: return
    
    w = n - int(math.sqrt(n*(k-1)))
    c = n - k - w
    d = w - c
    if c < 1 or w < 2 or d < 0: return
    
    Cnw = math.comb(n, w)
    density = Cnw / p**c if p**c < 10**15 else 0.0
    bezout = (n - w) ** d if d > 0 else 1
    
    # Build σ-image for actual M computation
    if Cnw <= 200000:
        sigma_pts = []
        for B in itertools.combinations(L, w):
            coeffs = [1]
            for x in B:
                new = [0]*(len(coeffs)+1)
                for i, cc in enumerate(coeffs):
                    new[i] = (new[i]+cc) % p
                    new[i+1] = (new[i+1]-cc*x) % p
                coeffs = new
            e = tuple((-1)**(j+1)*coeffs[j] % p for j in range(1, w+1))
            sigma_pts.append(e)
        sigma_np = np.array(sigma_pts, dtype=np.int64)
        
        # Test random full-rank Toeplitz conditions
        import random; random.seed(42)
        max_M = 0
        nk = n - k
        n_trials = min(50000, p**(nk) if p**nk < 50000 else 50000)
        
        for _ in range(n_trials):
            s = [random.randint(0, p-1) for _ in range(nk)]
            # Build Toeplitz matrix and check rank
            T = np.zeros((c, w), dtype=np.int64)
            b = np.zeros(c, dtype=np.int64)
            for ell in range(c):
                b[ell] = (-s[w+ell]) % p if (w+ell) < nk else 0
                for i in range(1, w+1):
                    idx = w + ell - i
                    if 0 <= idx < nk:
                        T[ell, i-1] = ((-1)**i * s[idx]) % p
            
            # Check rank
            rk = np.linalg.matrix_rank(T.astype(float))  # approx
            if rk < c: continue
            
            # Count M
            product = (T @ sigma_np.T) % p
            target = b.reshape(c, 1)
            M = int(np.sum(np.all(product == target, axis=0)))
            max_M = max(max_M, M)
        
        actual_max = max_M
    else:
        actual_max = "?"
    
    print(f"  n={n:2d} k={k:2d} p={p:5d} | w={w} c={c} d={d} | "
          f"C(n,w)={Cnw:7d} | Bézout=(n-w)^d={bezout:>10d} | "
          f"density={density:9.4f} | maxM={actual_max}")

def main():
    print("="*90)
    print("BÉZOUT DEGREE VERIFICATION")
    print("="*90)
    print(f"Theorem: M ≤ (n-w)^d where d = w-c, for full-rank Toeplitz syndrome")
    print(f"For FRI: need (n-w)^d / p^c → 0, which holds when p >> (n-w)^{{d/c}}")
    print()
    
    configs = [
        # c=1 (line case, fiber bound applies)
        (8, 4, 17),  # d=2
        (10, 5, 31), # d=3
        # c=2
        (16, 8, 17),   # d=4
        (16, 8, 97),
        (16, 8, 257),
        (16, 8, 1153), # large p
        # c=3
        (20, 10, 41),  # d=4
        (20, 10, 101),
        (20, 10, 241),
        (20, 10, 601),
        # c=4
        (24, 12, 97),  # w=8, c=4, d=4
        (24, 12, 241),
        # Larger n, larger c
        (30, 15, 31),  # w=10, c=5, d=5
        (30, 15, 61),
        (30, 15, 151),
        (30, 15, 241),
    ]
    
    for n, k, p in configs:
        if (p-1) % n != 0: continue
        verify_bezout(n, k, p)
    
    # Summary: verify (n-w)^d / p^c as threshold
    print("\n" + "="*90)
    print("THRESHOLD ANALYSIS: (n-w)^d / p^c")
    print("="*90)
    print(f"{'n':>3} {'k':>3} {'p':>5} {'w':>3} {'c':>3} {'d':>2} "
          f"{'(n-w)^d':>12} {'p^c':>15} {'ratio':>12} {'expected_M':>10}")
    print("—"*80)
    for n, k, p in configs:
        if (p-1) % n != 0: continue
        w = n - int(math.sqrt(n*(k-1)))
        c = n - k - w
        d = w - c
        if c < 1 or d < 0: continue
        
        bezout = (n-w)**d
        pc = p**c
        ratio = bezout / pc
        expected = math.comb(n,w) / pc
        
        print(f"{n:3d} {k:3d} {p:5d} {w:3d} {c:3d} {d:2d} "
              f"{bezout:12d} {pc:15d} {ratio:12.4f} {expected:10.4f}")

if __name__ == '__main__':
    main()
