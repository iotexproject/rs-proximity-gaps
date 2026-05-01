#!/usr/bin/env python3
"""
GPU/Multi-core accelerated density bound verification.
Uses numpy vectorization + multiprocessing for massive speedup.

Core idea: precompute all C(n,w) sigma-image points as a matrix,
then for each syndrome check ALL simultaneously via matrix multiply mod p.
"""

import numpy as np
import itertools
import math
import sys
import time
from multiprocessing import Pool, cpu_count, shared_memory
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
                        ok = False
                        break
                i += 1
            if ok:
                return g
    return None

def build_sigma_image(L, w, p):
    """Build all C(n,w) elem-sym tuples as numpy array."""
    n = len(L)
    pts = []
    for B in itertools.combinations(L, w):
        # Compute (e_1,...,e_w) via product expansion
        coeffs = [1]
        for x in B:
            new = [0] * (len(coeffs) + 1)
            for i, c in enumerate(coeffs):
                new[i] = (new[i] + c) % p
                new[i+1] = (new[i+1] + c * x) % p
            coeffs = new
        # Λ(x) = Π(x-α) = x^w + Σ (-1)^j e_j x^{w-j}
        # coeffs[j] is coefficient of x^{w-j} with sign (-1)^j
        e = tuple((-1)**(j+1) * coeffs[j] % p for j in range(1, w+1))
        pts.append(e)
    return np.array(pts, dtype=np.int64)  # shape (N, w)

def count_M_batch(sigma_matrix, syndrome_batch, w, c, p):
    """
    For a batch of syndromes, count M for each.
    
    syndrome_batch: list of syndrome vectors (length n-k each)
    sigma_matrix: (N, w) array of elem-sym tuples
    
    KEY EQUATION condition for syndrome s:
    For each ℓ = 0,...,c-1:
      Σ_{i=0}^w (-1)^i e_i s_{w+ℓ-i} = 0  (e_0 = 1)
    
    Rewrite: s_{w+ℓ} + Σ_{i=1}^w (-1)^i e_i s_{w+ℓ-i} = 0
    → Σ_{i=1}^w [(-1)^i s_{w+ℓ-i}] e_i = -s_{w+ℓ}
    
    This is: A_s · e^T = b_s  where A_s is c×w, b_s is c×1.
    """
    N = sigma_matrix.shape[0]
    results = []
    
    for s in syndrome_batch:
        # Build Toeplitz matrix A (c × w) and target b (c,)
        A = np.zeros((c, w), dtype=np.int64)
        b = np.zeros(c, dtype=np.int64)
        
        for ell in range(c):
            b[ell] = (-s[w + ell]) % p  # = -s_{w+ℓ}
            for i in range(1, w + 1):
                idx = w + ell - i
                if 0 <= idx < len(s):
                    A[ell, i-1] = ((-1)**i * s[idx]) % p
        
        # Compute A @ sigma^T  → shape (c, N), mod p
        product = (A @ sigma_matrix.T) % p  # (c, N)
        
        # Check which columns equal b
        target = b.reshape(c, 1)  # (c, 1)
        matches = np.all(product == target, axis=0)  # (N,)
        M = int(np.sum(matches))
        results.append(M)
    
    return results

def worker_random_syndromes(args):
    """Worker for parallel random syndrome testing."""
    shm_name, shape, dtype_str, w, c, p, nk, n_trials, seed = args
    
    shm = shared_memory.SharedMemory(name=shm_name)
    sigma = np.ndarray(shape, dtype=np.dtype(dtype_str), buffer=shm.buf)
    
    rng = np.random.RandomState(seed)
    
    max_M = 0
    M_values = []
    
    batch_size = min(100, n_trials)
    for start in range(0, n_trials, batch_size):
        end = min(start + batch_size, n_trials)
        batch = []
        for _ in range(end - start):
            s = rng.randint(0, p, size=nk).tolist()
            batch.append(s)
        
        results = count_M_batch(sigma, batch, w, c, p)
        M_values.extend(results)
        batch_max = max(results)
        if batch_max > max_M:
            max_M = batch_max
    
    shm.close()
    return M_values

def sweep_config(n, k, p, n_trials=10000, exhaustive_threshold=500000):
    """Run density verification for one (n, k, p) config."""
    if (p - 1) % n != 0:
        return None
    
    g = primitive_root(p)
    L = sorted(set(pow(g, j * ((p-1)//n), p) for j in range(n)))
    if len(L) != n:
        return None
    
    # Johnson radius
    w = n - int(math.sqrt(n * (k - 1)))
    c = n - k - w
    if c < 1 or w < 2 or w >= n:
        return None
    
    Cnw = math.comb(n, w)
    if Cnw > 500000:
        print(f"  SKIP n={n},k={k},p={p}: C(n,w)={Cnw} too large")
        return None
    
    density = Cnw / p**c if p**c < 10**18 else 0.0
    nk = n - k
    
    t0 = time.time()
    
    # Build sigma image
    sigma = build_sigma_image(L, w, p)
    N = sigma.shape[0]
    
    t1 = time.time()
    
    # Create shared memory for sigma matrix
    shm = shared_memory.SharedMemory(create=True, size=sigma.nbytes)
    shared_sigma = np.ndarray(sigma.shape, dtype=sigma.dtype, buffer=shm.buf)
    np.copyto(shared_sigma, sigma)
    
    # Parallel random syndrome testing
    n_workers = min(cpu_count(), 24)
    trials_per_worker = n_trials // n_workers
    
    args_list = [
        (shm.name, sigma.shape, sigma.dtype.str, w, c, p, nk, 
         trials_per_worker, 1000 * i + 42)
        for i in range(n_workers)
    ]
    
    with Pool(n_workers) as pool:
        results = pool.map(worker_random_syndromes, args_list)
    
    # Aggregate
    all_M = []
    for r in results:
        all_M.extend(r)
    
    t2 = time.time()
    
    mean_M = sum(all_M) / len(all_M)
    max_M = max(all_M)
    
    # Also test STRUCTURED syndromes (potentially adversarial)
    # 1. Zero syndrome (s = 0 → center is a codeword)
    zero_s = [0] * nk
    M_zero = count_M_batch(sigma, [zero_s], w, c, p)[0]
    
    # 2. Unit syndromes (s = e_j)
    max_M_unit = 0
    for j in range(nk):
        unit_s = [0] * nk
        unit_s[j] = 1
        M_unit = count_M_batch(sigma, [unit_s], w, c, p)[0]
        max_M_unit = max(max_M_unit, M_unit)
    
    # 3. Syndromes from specific centers: center = (1,0,...,0), (1,1,...,1), etc.
    max_M_struct = max(M_zero, max_M_unit)
    
    # Try more structured syndromes
    for _ in range(200):
        # Random sparse syndrome
        s = [0] * nk
        for idx in np.random.choice(nk, size=min(3, nk), replace=False):
            s[idx] = np.random.randint(1, p)
        M_s = count_M_batch(sigma, [s], w, c, p)[0]
        max_M_struct = max(max_M_struct, M_s)
    
    overall_max = max(max_M, max_M_struct)
    
    t3 = time.time()
    
    shm.close()
    shm.unlink()
    
    ratio = f"{overall_max/density:.1f}" if density > 0.001 else "∞"
    
    print(f"  n={n:2d} k={k:2d} p={p:5d} | w={w} c={c} | "
          f"C(n,w)={Cnw:7d} dens={density:9.4f} | "
          f"maxM={overall_max:4d} meanM={mean_M:7.3f} M0={M_zero:3d} | "
          f"ratio={ratio:>6} | {t2-t1:.1f}s")
    
    return {
        'n': n, 'k': k, 'p': p, 'w': w, 'c': c,
        'Cnw': Cnw, 'density': density,
        'max_M': overall_max, 'mean_M': mean_M, 'M_zero': M_zero,
    }

def main():
    print("="*80)
    print("DENSITY BOUND VERIFICATION — GPU/Multi-core Accelerated")
    print(f"  Using {cpu_count()} CPU cores")
    print("="*80)
    
    configs = [
        # Small: exact verification
        (6, 3, 7),
        (8, 4, 17),
        (10, 5, 11),
        (10, 5, 31),
        (10, 5, 61),
        (10, 5, 101),
        # Moderate
        (12, 6, 13),
        (12, 6, 37),
        (12, 6, 61),
        # Varying k
        (10, 3, 11),
        (10, 3, 31),
        (10, 7, 11),
        (10, 7, 31),
        (10, 7, 61),
        (10, 8, 11),
        (10, 8, 31),
        # Larger n
        (16, 8, 17),
        (16, 8, 97),
        (16, 8, 257),
        (20, 10, 41),
        (20, 10, 61),
        (20, 10, 101),
        (20, 10, 241),
        (24, 12, 97),
        (24, 12, 241),
        (30, 15, 31),
        (30, 15, 61),
        (30, 15, 151),
        (30, 15, 241),
        # Large n, large p (FRI-like)
        (36, 18, 37),
        (36, 18, 73),
        (36, 18, 109),
        (40, 20, 41),
        (40, 20, 241),
        (48, 24, 97),
        (60, 30, 61),
    ]
    
    results = []
    for n, k, p in configs:
        r = sweep_config(n, k, p, n_trials=20000)
        if r is not None:
            results.append(r)
    
    # Summary table
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"{'n':>3} {'k':>3} {'p':>5} {'w':>3} {'c':>3} {'C(n,w)':>8} "
          f"{'density':>10} {'maxM':>5} {'meanM':>8} {'max/dens':>9}")
    print("—" * 75)
    for r in results:
        ratio = f"{r['max_M']/r['density']:.1f}" if r['density'] > 0.001 else "∞"
        print(f"{r['n']:3d} {r['k']:3d} {r['p']:5d} {r['w']:3d} {r['c']:3d} "
              f"{r['Cnw']:8d} {r['density']:10.4f} {r['max_M']:5d} "
              f"{r['mean_M']:8.3f} {ratio:>9}")
    
    # Key finding: for which configs is max M > density + O(1)?
    print("\n\nKEY: configs where max M > 2*density + 3:")
    for r in results:
        if r['max_M'] > 2 * r['density'] + 3:
            print(f"  n={r['n']} k={r['k']} p={r['p']}: "
                  f"maxM={r['max_M']}, density={r['density']:.2f}")
    
    print("\nKEY: configs where max M ≤ 3 (O(1) regime):")
    for r in results:
        if r['max_M'] <= 3:
            print(f"  n={r['n']} k={r['k']} p={r['p']}: "
                  f"maxM={r['max_M']}, density={r['density']:.4f}, c={r['c']}")

if __name__ == '__main__':
    main()
