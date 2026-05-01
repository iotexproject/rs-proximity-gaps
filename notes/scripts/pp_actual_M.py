#!/usr/bin/env python3
"""
CRITICAL TEST: For pinned-pair centers, is M_actual = O(1)?

M_alg counts sigma-image points on the compatible subspace.
M_actual counts ACTUAL codewords within distance w.

M_alg can overcount when sigma-image points don't correspond to valid codewords.
"""
import itertools, random, math
from collections import Counter

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g
def prime_factors(n):
    f=set(); d=2
    while d*d<=n:
        while n%d==0: f.add(d); n//=d
        d+=1
    if n>1: f.add(n)
    return f
def find_omega(p, n):
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

def test_pp_M_actual(n_ord, k, p):
    """
    For each pinned-pair (w-1)-subset S of L:
    1. Construct a center c whose compatible subspace passes through
       the sigma-images of {S ∪ {gamma}} for all gamma ∈ L \ S
    2. Compute M_actual = #{f ∈ RS_k : d(c, f) ≤ w}
    """
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    w = n_ord - int(math.sqrt(n_ord * (k-1)))
    c = n_ord - k - w
    
    print(f"\nn={n_ord}, k={k}, p={p}, w={w}, c={c}")
    print(f"  n-w+1 = {n_ord-w+1} (pinned-pair M_alg)")
    
    if w > n_ord or w < 2: return
    
    # For each codeword f ∈ RS_k: f(x) = a_0 + a_1*x + ... + a_{k-1}*x^{k-1}
    # Enumerate all codewords (only feasible for small p^k)
    if p**k > 500000:
        print(f"  p^k = {p**k}, too large for exhaustive. Sampling.")
        sampling = True
    else:
        sampling = False
    
    # Take a few pinned-pair centers
    max_M_actual = 0
    M_actual_list = []
    
    tested = 0
    for fixed_idx in itertools.combinations(range(n_ord), w-1):
        if tested >= 20: break
        tested += 1
        
        fixed_elts = [L[i] for i in fixed_idx]
        
        # Choose a specific gamma to define the center
        remaining = [i for i in range(n_ord) if i not in fixed_idx]
        gamma_idx = remaining[0]
        gamma = L[gamma_idx]
        
        # The w-subset B0 = fixed ∪ {gamma}: this defines a specific codeword+error pattern
        B0 = list(fixed_idx) + [gamma_idx]
        B0_set = set(B0)
        agree_set = [i for i in range(n_ord) if i not in B0_set]
        
        # We need a center c and a codeword f such that f(ω^i) = c(ω^i) for i in agree_set
        # and f(ω^i) ≠ c(ω^i) for i in B0.
        
        # Choose f = 0 (zero codeword). Then c(ω^i) = 0 for i in agree_set, c(ω^i) ≠ 0 for i in B0.
        # Set c(ω^i) = 1 for i in B0, c(ω^i) = 0 otherwise.
        c_eval = [0]*n_ord
        for i in B0:
            c_eval[i] = 1
        
        # Compute M_actual: count codewords f with d(c,f) ≤ w
        M_actual = 0
        
        if not sampling:
            # Enumerate all codewords
            for coeffs in itertools.product(range(p), repeat=k):
                f_eval = [0]*n_ord
                for i in range(n_ord):
                    val = 0; xpow = 1
                    for j in range(k):
                        val = (val + coeffs[j] * xpow) % p
                        xpow = (xpow * L[i]) % p
                    f_eval[i] = val
                
                dist = sum(1 for i in range(n_ord) if f_eval[i] != c_eval[i])
                if dist <= w:
                    M_actual += 1
        else:
            # Sample random codewords
            for _ in range(100000):
                coeffs = [random.randint(0, p-1) for _ in range(k)]
                f_eval = [0]*n_ord
                for i in range(n_ord):
                    val = 0; xpow = 1
                    for j in range(k):
                        val = (val + coeffs[j] * xpow) % p
                        xpow = (xpow * L[i]) % p
                    f_eval[i] = val
                dist = sum(1 for i in range(n_ord) if f_eval[i] != c_eval[i])
                if dist <= w:
                    M_actual += 1
            # Also check f=0 (should have d = w)
            dist_zero = sum(1 for i in range(n_ord) if c_eval[i] != 0)
            print(f"  [Sample] d(c,0) = {dist_zero}")
        
        M_actual_list.append(M_actual)
        max_M_actual = max(max_M_actual, M_actual)
    
    print(f"  M_actual for pinned-pair centers: {Counter(M_actual_list).most_common(10)}")
    print(f"  Max M_actual = {max_M_actual}")
    print(f"  Compare: M_alg(PP) = {n_ord-w+1}, fiber bound(non-PP) = {n_ord//w}")

# Test small cases
for n_ord, k, p in [
    (8, 2, 17),
    (8, 4, 17),
    (10, 2, 11),
    (10, 5, 11),
    (10, 2, 31),
    (10, 5, 31),
    (12, 2, 13),
    (12, 6, 13),
    (12, 6, 37),
]:
    if (p-1) % n_ord != 0: continue
    test_pp_M_actual(n_ord, k, p)
