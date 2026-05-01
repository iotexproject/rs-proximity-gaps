#!/usr/bin/env python3
"""
Fixed density sweep: exclude degenerate syndromes, check Toeplitz rank.
Multi-core accelerated with numpy.

Key fix: s=0 gives rank-0 Toeplitz → trivial conditions → M0=C(n,w).
We only care about FULL-RANK Toeplitz (rank = c).
"""
import numpy as np
import itertools
import math
import time
from multiprocessing import Pool, cpu_count
from collections import Counter

def primitive_root(p):
    for g in range(2, p):
        if pow(g, (p-1)//2, p) != 1:
            ok = True
            d = p - 1
            i = 2
            while i * i <= d:
                if d % i == 0:
                    if pow(g, d // i, p) == 1:
                        ok = False; break
                i += 1
            if ok: return g
    return None

def modinv(a, p):
    return pow(a, p-2, p)

def gauss_rank_mod_p(M, p):
    """Compute rank of matrix M over F_p."""
    A = np.array(M, dtype=np.int64) % p
    rows, cols = A.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if A[row, col] % p != 0:
                pivot = row; break
        if pivot is None: continue
        A[[rank, pivot]] = A[[pivot, rank]]
        inv = modinv(int(A[rank, col] % p), p)
        A[rank] = A[rank] * inv % p
        for row in range(rows):
            if row != rank and A[row, col] % p != 0:
                A[row] = (A[row] - A[row, col] * A[rank]) % p
        rank += 1
    return rank

def build_all_lambda(L, w, p):
    """Build all C(n,w) error-locator coefficient tuples (e_1,...,e_w)."""
    pts = []
    for B in itertools.combinations(L, w):
        coeffs = [1]
        for x in B:
            new = [0] * (len(coeffs) + 1)
            for i, c in enumerate(coeffs):
                new[i] = (new[i] + c) % p
                new[i+1] = (new[i+1] - c * x) % p
            coeffs = new
        e = tuple((-1)**(j+1) * coeffs[j] % p for j in range(1, w+1))
        pts.append(e)
    return np.array(pts, dtype=np.int64)

def toeplitz_matrix(s, w, c, p):
    """Build Toeplitz condition matrix T (c×w) and target b (c,) from syndrome s.
    
    Condition: Σ_{i=0}^w (-1)^i e_i s_{w+ℓ-i} = 0 for ℓ=0,...,c-1
    With e_0 = 1:  s_{w+ℓ} + Σ_{i=1}^w (-1)^i e_i s_{w+ℓ-i} = 0
    → T·e = b where T[ℓ,i-1] = (-1)^{i+1} s_{w+ℓ-i}, b[ℓ] = s_{w+ℓ}
    
    Wait, let me be more careful.
    Σ_{i=0}^w (-1)^i e_i s_{w+ℓ-i} = 0
    s_{w+ℓ} + Σ_{i=1}^w (-1)^i e_i s_{w+ℓ-i} = 0
    Σ_{i=1}^w (-1)^i s_{w+ℓ-i} e_i = -s_{w+ℓ}
    """
    T = np.zeros((c, w), dtype=np.int64)
    b = np.zeros(c, dtype=np.int64)
    ns = len(s)
    for ell in range(c):
        b[ell] = (-s[w + ell]) % p if (w + ell) < ns else 0
        for i in range(1, w + 1):
            idx = w + ell - i
            if 0 <= idx < ns:
                T[ell, i-1] = ((-1)**i * s[idx]) % p
    return T, b

def count_M_for_syndrome(sigma_np, s, w, c, p):
    """Count M = #{Λ ∈ sigma_set : Toeplitz conditions hold} for syndrome s."""
    T, b = toeplitz_matrix(s, w, c, p)
    product = (T @ sigma_np.T) % p  # (c, N)
    target = b.reshape(c, 1)
    matches = np.all(product == target, axis=0)
    return int(np.sum(matches)), gauss_rank_mod_p(T, p)

def worker_sweep(args):
    """Worker: test random syndromes."""
    sigma_list, w, c, p, nk, n_trials, seed = args
    sigma_np = np.array(sigma_list, dtype=np.int64)
    rng = np.random.RandomState(seed)
    
    results = []
    for _ in range(n_trials):
        s = rng.randint(0, p, size=nk).tolist()
        M, rank = count_M_for_syndrome(sigma_np, s, w, c, p)
        results.append((M, rank))
    return results

def sweep_one(n, k, p, n_trials=20000):
    if (p-1) % n != 0: return None
    g = primitive_root(p)
    L = sorted(set(pow(g, j*((p-1)//n), p) for j in range(n)))
    if len(L) != n: return None
    
    w = n - int(math.sqrt(n*(k-1)))
    c = n - k - w
    if c < 1 or w < 2 or w >= n: return None
    
    Cnw = math.comb(n, w)
    if Cnw > 200000: return None
    
    nk = n - k
    density = Cnw / p**c if p**c < 10**18 else 0.0
    
    t0 = time.time()
    sigma_np = build_all_lambda(L, w, p)
    N = sigma_np.shape[0]
    sigma_list = sigma_np.tolist()
    
    # Parallel sweep
    nw = min(cpu_count(), 24)
    tpw = n_trials // nw
    args = [(sigma_list, w, c, p, nk, tpw, 1000*i+42) for i in range(nw)]
    
    with Pool(nw) as pool:
        raw = pool.map(worker_sweep, args)
    
    all_results = []
    for r in raw:
        all_results.extend(r)
    
    # Split by rank
    full_rank = [(M, rk) for M, rk in all_results if rk == c]
    low_rank = [(M, rk) for M, rk in all_results if rk < c]
    
    t1 = time.time()
    
    if full_rank:
        M_full = [x[0] for x in full_rank]
        max_M_full = max(M_full)
        mean_M_full = sum(M_full) / len(M_full)
        dist_full = Counter(M_full).most_common(8)
    else:
        max_M_full = 0
        mean_M_full = 0
        dist_full = []
    
    pct_full = len(full_rank) / len(all_results) * 100
    
    print(f"  n={n:2d} k={k:2d} p={p:5d} w={w} c={c} | "
          f"N={Cnw:7d} dens={density:9.4f} | "
          f"maxM(rank=c)={max_M_full:5d} mean={mean_M_full:7.3f} | "
          f"%fullrank={pct_full:.1f}% | {t1-t0:.1f}s")
    if dist_full:
        print(f"    distribution (rank=c): {dist_full}")
    
    return {
        'n': n, 'k': k, 'p': p, 'w': w, 'c': c,
        'Cnw': Cnw, 'density': density,
        'max_M_full': max_M_full, 'mean_M_full': mean_M_full,
        'pct_full': pct_full,
    }

def main():
    print("="*80)
    print("DENSITY BOUND v2 — Full-rank Toeplitz only")
    print(f"  {cpu_count()} cores")
    print("="*80)
    
    configs = [
        (6, 3, 7),
        (8, 4, 17),
        (10, 5, 11), (10, 5, 31), (10, 5, 61), (10, 5, 101),
        (12, 6, 13), (12, 6, 37), (12, 6, 61),
        (10, 3, 11), (10, 3, 31), (10, 3, 61),
        (10, 7, 11), (10, 7, 31), (10, 7, 61),
        (10, 8, 11), (10, 8, 31),
        (16, 8, 17), (16, 8, 97), (16, 8, 257),
        (20, 10, 41), (20, 10, 61), (20, 10, 101), (20, 10, 241),
        (24, 12, 97), (24, 12, 241),
    ]
    
    results = []
    for n, k, p in configs:
        r = sweep_one(n, k, p, n_trials=30000)
        if r: results.append(r)
    
    print("\n" + "="*80)
    print("SUMMARY — Full-rank Toeplitz (the actual bound)")
    print("="*80)
    print(f"{'n':>3} {'k':>3} {'p':>5} {'w':>3} {'c':>3} {'C(n,w)':>8} "
          f"{'density':>10} {'maxM':>6} {'mean':>8} {'max/d':>7} {'regime':>8}")
    print("—"*75)
    for r in results:
        d = r['density']
        mx = r['max_M_full']
        ratio = f"{mx/d:.1f}" if d > 0.001 else "∞"
        regime = "O(1)" if mx <= 5 else ("O(n)" if mx > 20 else "small")
        print(f"{r['n']:3d} {r['k']:3d} {r['p']:5d} {r['w']:3d} {r['c']:3d} "
              f"{r['Cnw']:8d} {d:10.4f} {mx:6d} {r['mean_M_full']:8.3f} "
              f"{ratio:>7} {regime:>8}")
    
    print("\n\nO(1) REGIME (max M ≤ 5):")
    for r in results:
        if r['max_M_full'] <= 5:
            print(f"  n={r['n']} k={r['k']} p={r['p']}: max={r['max_M_full']}, "
                  f"density={r['density']:.4f}, c={r['c']}")

if __name__ == '__main__':
    main()
