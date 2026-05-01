"""
Fast incidence bound verification using numpy vectorization + multiprocessing.

For each syndrome s, the Toeplitz flat V_c(s) is defined by c linear conditions
on σ ∈ F_p^w. We check which of the C(n,w) σ-image points satisfy these conditions.

Key optimization: precompute σ-image as (N × w) matrix, then for each syndrome
compute T·σ^T and check which columns equal b. All mod p arithmetic via numpy.
"""

import numpy as np
from math import comb, gcd
from itertools import combinations
from multiprocessing import Pool, cpu_count
import time
import sys

def find_primitive_root(p):
    for g in range(2, p):
        if pow(g, (p-1)//2, p) != 1:  # quick filter
            ok = True
            x = 1
            for i in range(1, p-1):
                x = x * g % p
                if x == 1 and i < p-2:
                    ok = False
                    break
            if ok:
                return g
    return None

def get_subgroup(p, n):
    if (p-1) % n != 0:
        return None
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    return [pow(omega, i, p) for i in range(n)]

def build_sigma_image(L, w, p):
    """Build σ-image as numpy array (N × w) over Z_p."""
    N = comb(len(L), w)
    sigma = np.zeros((N, w), dtype=np.int64)
    idx = 0
    subsets = []
    for B in combinations(L, w):
        # Elementary symmetric polynomials
        e = [0] * (w + 1)
        e[0] = 1
        for x in B:
            for j in range(w, 0, -1):
                e[j] = (e[j] + e[j-1] * x) % p
        sigma[idx] = e[1:]
        subsets.append(B)
        idx += 1
    return sigma, subsets

def build_toeplitz_matrix(syndrome, w, p):
    """
    Build Toeplitz matrix T (c × w) and vector b (c × 1).
    Conditions: Σ_{j=1}^w (-1)^j σ_j s_{w+ℓ-j} = -s_{w+ℓ} for ℓ=0,...,c-1
    """
    nk = len(syndrome)
    c = nk - w
    if c <= 0:
        return None, None

    T = np.zeros((c, w), dtype=np.int64)
    b = np.zeros(c, dtype=np.int64)

    for ell in range(c):
        for j in range(1, w + 1):
            idx = w + ell - j
            if 0 <= idx < nk:
                sign = (-1) ** j % p
                T[ell, j-1] = (sign * syndrome[idx]) % p
        rhs_idx = w + ell
        b[ell] = (-syndrome[rhs_idx]) % p if rhs_idx < nk else 0

    return T, b

def count_M_vectorized(sigma_matrix, T, b, p):
    """Count how many σ-image points satisfy T·σ = b (mod p)."""
    # T: (c × w), sigma_matrix: (N × w), b: (c,)
    # Compute T @ sigma^T: (c × N)
    product = (T @ sigma_matrix.T) % p  # each column is T·σ_i
    # Check which columns equal b
    target = b.reshape(-1, 1)  # (c × 1)
    matches = np.all(product == target, axis=0)
    return int(np.sum(matches)), np.where(matches)[0]

def process_syndrome_batch(args):
    """Process a batch of syndromes. Returns (max_M, M_dist_update, violation_count)."""
    syndrome_batch, sigma_matrix, w, p = args
    nk = sigma_matrix.shape[1]  # Wait, this is wrong
    # Actually sigma_matrix is N × w
    local_max = 0
    local_dist = {}
    local_violations = 0

    for syn in syndrome_batch:
        T, b = build_toeplitz_matrix(syn, w, p)
        if T is None:
            continue

        # Check rank of T
        # For speed, skip rank check — just count
        M, _ = count_M_vectorized(sigma_matrix, T, b, p)

        local_dist[M] = local_dist.get(M, 0) + 1
        if M > local_max:
            local_max = M

    return local_max, local_dist, local_violations

def run_experiment(n, k, p, w, n_samples=None):
    """Run incidence bound experiment."""
    L = get_subgroup(p, n)
    if L is None:
        print(f"  No subgroup of order {n} in F_{p}*")
        return None

    c = n - k - w
    d = w - c
    if c <= 0 or d <= 0:
        print(f"  Invalid: c={c}, d={d}")
        return None

    nk = n - k
    total_syndromes = p ** nk
    incidence_bound = comb(n, d) / comb(w, d)
    bezout = (n - w + 1) ** d
    density = comb(n, w) / p ** c

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}, c={c}, d={d}")
    print(f"C(n,w)={comb(n,w)}, incidence bound={incidence_bound:.2f}, "
          f"Bézout={bezout}, density={density:.4f}")
    print(f"Total syndromes: {total_syndromes}")

    # Build σ-image
    t0 = time.time()
    sigma_matrix, subsets = build_sigma_image(L, w, p)
    N = sigma_matrix.shape[0]
    print(f"σ-image built: {N} points ({time.time()-t0:.2f}s)")

    # Generate syndromes
    if n_samples is None:
        if total_syndromes <= 200000:
            n_samples = total_syndromes  # exhaustive
        else:
            n_samples = min(50000, total_syndromes)

    t0 = time.time()
    if n_samples == total_syndromes and total_syndromes <= 200000:
        print(f"Exhaustive enumeration of {total_syndromes} syndromes...")
        syndromes = []
        for val in range(total_syndromes):
            syn = []
            v = val
            for _ in range(nk):
                syn.append(v % p)
                v //= p
            syndromes.append(syn)
    else:
        print(f"Random sampling {n_samples} of {total_syndromes} syndromes...")
        rng = np.random.RandomState(42)
        syndromes = [list(rng.randint(0, p, size=nk)) for _ in range(n_samples)]

    # Process with multiprocessing
    n_workers = max(1, cpu_count() - 1)
    batch_size = max(1, len(syndromes) // (n_workers * 4))
    batches = []
    for i in range(0, len(syndromes), batch_size):
        batch = syndromes[i:i+batch_size]
        batches.append((batch, sigma_matrix, w, p))

    print(f"Processing {len(syndromes)} syndromes with {n_workers} workers, "
          f"{len(batches)} batches...")

    max_M = 0
    M_dist = {}

    if n_workers > 1 and len(batches) > 1:
        with Pool(n_workers) as pool:
            results = pool.map(process_syndrome_batch, batches)
    else:
        results = [process_syndrome_batch(b) for b in batches]

    for local_max, local_dist, _ in results:
        max_M = max(max_M, local_max)
        for m, cnt in local_dist.items():
            M_dist[m] = M_dist.get(m, 0) + cnt

    elapsed = time.time() - t0
    n_tested = sum(M_dist.values())
    print(f"Done in {elapsed:.2f}s ({n_tested/elapsed:.0f} syndromes/s)")

    # Results
    print(f"\n--- Results ---")
    print(f"Max M = {max_M}")
    print(f"Incidence bound = {incidence_bound:.2f}")
    print(f"Bézout bound = {bezout}")
    bound_ok = "✓" if max_M <= incidence_bound else "✗"
    print(f"Incidence bound holds: {bound_ok}")

    avg_M = sum(m * cnt for m, cnt in M_dist.items()) / n_tested if n_tested > 0 else 0
    print(f"avg M = {avg_M:.4f} (predicted density: {density:.4f})")

    print(f"\nM distribution:")
    for m in sorted(M_dist.keys()):
        pct = 100 * M_dist[m] / n_tested
        if pct > 0.01 or m <= 5 or m == max_M:
            print(f"  M={m}: {M_dist[m]:>8} ({pct:>6.2f}%)")

    # Find worst-case syndrome for analysis
    if max_M > 0:
        print(f"\n--- Worst-case analysis ---")
        worst_syn = None
        for syn in syndromes:
            T, b = build_toeplitz_matrix(syn, w, p)
            if T is None:
                continue
            M, idxs = count_M_vectorized(sigma_matrix, T, b, p)
            if M == max_M:
                worst_syn = syn
                worst_idxs = idxs
                break

        if worst_syn is not None and d >= 2:
            T, b = build_toeplitz_matrix(worst_syn, w, p)
            # Compute flat basis via null space of T
            # T is c × w over F_p
            # ... (use numpy for approximate null space, then correct mod p)
            print(f"  Worst syndrome: {worst_syn}")
            print(f"  Matching subsets ({max_M}):")
            for idx in worst_idxs[:8]:
                print(f"    B = {subsets[idx]}")

            # Check shared elements between matching subsets
            if len(worst_idxs) >= 2:
                all_B = [set(subsets[idx]) for idx in worst_idxs]
                for i in range(min(len(all_B), 4)):
                    for j in range(i+1, min(len(all_B), 4)):
                        shared = all_B[i] & all_B[j]
                        print(f"    |B_{i} ∩ B_{j}| = {len(shared)}: {shared}")

    return {
        'n': n, 'k': k, 'p': p, 'w': w, 'c': c, 'd': d,
        'max_M': max_M, 'incidence': incidence_bound,
        'bezout': bezout, 'density': density,
        'avg_M': avg_M, 'n_tested': n_tested,
        'exhaustive': n_samples == total_syndromes
    }

def main():
    print("=" * 70)
    print("INCIDENCE BOUND: M ≤ C(n,d)/C(w,d) — Fast Verification")
    print(f"CPUs available: {cpu_count()}")
    print("=" * 70)

    # Carefully chosen test cases with (p-1) % n == 0
    test_cases = [
        # d=1 cases (lines)
        (10, 5, 11, 3),    # c=2, d=1, exhaustive (11^5=161K)
        (10, 5, 31, 3),    # c=2, d=1, sample
        (12, 6, 13, 4),    # c=2, d=2, exhaustive (13^6=4.8M -> sample)
        (8, 4, 17, 3),     # c=1, d=2, exhaustive (17^4=83K)
        (10, 4, 11, 4),    # c=2, d=2, exhaustive (11^6=1.77M -> sample)

        # Higher d
        (8, 4, 17, 4),     # c=0 -> skip
        (8, 3, 17, 3),     # c=2, d=1
        (10, 3, 11, 3),    # c=4, d=-1 -> skip
        (12, 4, 13, 4),    # c=4, d=0 -> skip

        # d=2 with various p
        (10, 4, 31, 4),    # c=2, d=2, sample
        (12, 6, 37, 4),    # c=2, d=2, sample

        # d=3
        (14, 7, 29, 5),    # c=2, d=3, sample
        (10, 4, 11, 5),    # c=1, d=4, exhaustive (11^6=1.77M)
    ]

    results = []
    for n, k, p, w in test_cases:
        c = n - k - w
        d = w - c
        if c <= 0 or d <= 0:
            continue
        if (p - 1) % n != 0:
            continue

        res = run_experiment(n, k, p, w)
        if res:
            results.append(res)

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}")
    hdr = f"{'n':>3} {'k':>3} {'p':>3} {'w':>3} {'c':>2} {'d':>2} " \
          f"{'maxM':>5} {'C(n,d)/C(w,d)':>13} {'Bezout':>8} {'density':>8} " \
          f"{'avgM':>8} {'exh':>4} {'ok':>3}"
    print(hdr)
    print("-" * 80)
    for r in results:
        exh = "yes" if r['exhaustive'] else "no"
        ok = "✓" if r['max_M'] <= r['incidence'] else "✗"
        print(f"{r['n']:>3} {r['k']:>3} {r['p']:>3} {r['w']:>3} "
              f"{r['c']:>2} {r['d']:>2} "
              f"{r['max_M']:>5} {r['incidence']:>13.1f} {r['bezout']:>8} "
              f"{r['density']:>8.3f} {r['avg_M']:>8.4f} {exh:>4} {ok:>3}")

    print(f"\n{'='*80}")
    violations = [r for r in results if r['max_M'] > r['incidence']]
    if violations:
        print(f"⚠ {len(violations)} VIOLATIONS of incidence bound!")
        for r in violations:
            print(f"  n={r['n']},k={r['k']},p={r['p']},w={r['w']}: "
                  f"maxM={r['max_M']} > {r['incidence']:.1f}")
    else:
        print("✓ All cases satisfy incidence bound C(n,d)/C(w,d)")

if __name__ == "__main__":
    main()
