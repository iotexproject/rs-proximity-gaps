#!/usr/bin/env python3
"""
density_scaling.py — Verify M ~ C · (n-w+1)^d / p^c for general k.

If this scaling law holds, then M = O(1) for p >> n, proving the density heuristic.

Test: RS[n,k] at rate 1/2, vary p, measure M_max at each w in intermediate zone.
Plot M_max vs (n-w+1)^d / p^c.
"""

import numpy as np
from math import sqrt, ceil, comb
import time


def generate_codewords(n, k, p):
    """Generate all RS[n,k] codewords over F_p. Eval domain = {1,...,n}."""
    L = list(range(1, n + 1))
    total = p ** k
    cw = np.zeros((total, n), dtype=np.int16)

    for idx in range(total):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        for j, x in enumerate(L):
            val = 0
            for c in reversed(coeffs):
                val = (val * x + c) % p
            cw[idx, j] = val
    return cw


def compute_M_max(cw, n, w_range, num_centers=300, num_rand=300):
    """Compute M_max(w) for each w in w_range."""
    total = cw.shape[0]
    M = {w: 0 for w in w_range}

    np.random.seed(42)

    # Codeword centers
    nc = min(num_centers, total)
    indices = np.random.choice(total, nc, replace=False) if total > nc else np.arange(total)

    for idx in indices:
        dists = np.sum(cw[idx].astype(np.int16) != cw, axis=1)
        for w in w_range:
            cnt = int(np.sum(dists <= w))
            if cnt > M[w]:
                M[w] = cnt

    # Random centers
    p_est = int(np.max(cw)) + 1
    for _ in range(num_rand):
        u = np.random.randint(0, p_est, size=n, dtype=np.int16)
        dists = np.sum(u != cw, axis=1)
        for w in w_range:
            cnt = int(np.sum(dists <= w))
            if cnt > M[w]:
                M[w] = cnt

    return M


def density_test(n, k, primes):
    """For RS[n,k], compute M_max at each w for each prime. Check density scaling."""
    rho = k / n
    wJ = n * (1 - sqrt(rho))
    cap = n - k
    w_lo = ceil(wJ)
    w_hi = cap - 1

    if w_lo > w_hi:
        print(f"  RS[{n},{k}]: empty intermediate zone, skip")
        return

    w_range = list(range(w_lo, w_hi + 1))

    print(f"\n{'='*70}")
    print(f"RS[{n},{k}], ρ={rho:.2f}, wJ={wJ:.2f}, cap={cap}")
    print(f"Intermediate zone: w ∈ [{w_lo}, {w_hi}]")
    print(f"{'='*70}")

    results = {}  # (w, p) -> M

    for p in primes:
        if p <= n:
            continue
        total = p ** k
        if total > 20_000_000:
            print(f"  p={p}: SKIP (p^k={total} too large)")
            continue

        t0 = time.time()
        cw = generate_codewords(n, k, p)
        M = compute_M_max(cw, n, w_range,
                          num_centers=min(500, total),
                          num_rand=min(500, total))
        elapsed = time.time() - t0

        for w in w_range:
            results[(w, p)] = M[w]

        print(f"  p={p:>4} (p^k={total:>10}): M = {[M[w] for w in w_range]}  ({elapsed:.1f}s)")

    # Density analysis for each w
    for w in w_range:
        t = n - w  # agreements
        c = t - k  # codimension (for general code: c = n - k - w ... wait)
        # Actually: for RS[n,k] at distance w,
        # the number of "agreement positions" is n - w = t
        # A degree-<k polynomial is determined by k points
        # The "codimension" of the syndrome equations is c = t - k (overdetermined by this much)
        # But in the companion matrix framework: c = n - k - w, d = w - c = 2w - n + k

        c_cm = n - k - w  # companion matrix codimension
        d_cm = w - c_cm   # companion matrix dimension

        print(f"\n  w={w}: c={c_cm}, d={d_cm}")
        print(f"  {'p':>6} | {'M':>5} | {'(n-w+1)^d':>12} | {'ratio=M·p^c/(n-w+1)^d':>24} | {'M·p^c':>15}")

        for p in primes:
            if (w, p) not in results:
                continue
            M_val = results[(w, p)]
            bezout = (n - w + 1) ** d_cm if d_cm > 0 else 1
            pc = p ** c_cm if c_cm > 0 else 1

            if bezout > 0:
                ratio = M_val * pc / bezout
            else:
                ratio = float('inf')

            Mpc = M_val * pc
            print(f"  {p:6d} | {M_val:5d} | {bezout:12d} | {ratio:24.4f} | {Mpc:15.0f}")

        # Also show n^2/(t(t-1)) for k=2 comparison
        if t > 1:
            k2_bound = n * n / (t * (t - 1))
            print(f"  (k=2 bound: n²/(t(t-1)) = {k2_bound:.2f})")

        # Expected from density: M ≈ bezout / p^c = (n-w+1)^d / p^c
        if d_cm > 0 and c_cm > 0:
            for p in primes:
                if p <= n:
                    continue
                pred = (n - w + 1) ** d_cm / p ** c_cm
                print(f"  density prediction at p={p}: M ≈ {pred:.6f}")
                break


def general_k_M_vs_p():
    """Systematic: fix (n,k,w), vary p, check M ∝ 1/p^c."""
    print(f"\n{'='*70}")
    print(f"SYSTEMATIC: M vs p scaling")
    print(f"{'='*70}")

    configs = [
        # (n, k, primes)
        (8, 4, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]),
        (8, 3, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]),
        (8, 2, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 79, 83, 89, 97]),
        (10, 5, [11, 13, 17, 19, 23, 29, 31, 37, 41, 43]),
        (12, 6, [13, 17, 19, 23, 29, 31]),
    ]

    for n, k, primes in configs:
        density_test(n, k, primes)


def interleaved_list_size():
    """Compute list size for C^{≡2} (2-interleaved RS code).
    |Λ(C^{≡2}, δ)| = max over (u1,u2) of |{(f1,f2) : d(fi,ui) ≤ w for i=1,2}|.
    For RS[n,k]: this is max_u1,u2 |list(u1,w)| · |list(u2,w)| ... no, that's the product.
    Actually: |Λ(C^{≡m}, δ)| = max_u |{f ∈ C^m : d(f,u) ≤ δ}| where d is on the interleaved code.
    For ABF: d((f1,...,fm), (u1,...,um)) = max_i Δ(fi, ui)... or is it the fraction of positions
    where all m coordinates agree?

    Actually the interleaved distance is: Δ = fraction of positions where ANY coordinate disagrees.
    So d(f,u) counts the positions where (f1,...,fm) ≠ (u1,...,um) in at least one coordinate.
    """
    print(f"\n{'='*70}")
    print(f"INTERLEAVED C^≡2 LIST SIZE")
    print(f"{'='*70}")

    n, k = 8, 4
    for p in [11, 17, 31]:
        if p <= n:
            continue
        L = list(range(1, n + 1))
        total = p ** k

        t0 = time.time()
        cw = generate_codewords(n, k, p)
        print(f"\nRS[{n},{k}]^≡2 over F_{p}  (|C|={total})")

        rho = k / n
        wJ = n * (1 - sqrt(rho))
        cap = n - k

        # For interleaved code: received word is (u1, u2) ∈ F_p^n × F_p^n
        # Codeword is (f1, f2) ∈ C × C
        # Distance: number of positions i where (f1(i),f2(i)) ≠ (u1(i),u2(i))
        # = number of i where f1(i) ≠ u1(i) OR f2(i) ≠ u2(i)

        # For random (u1, u2): list at distance w = {(f1,f2) : |{i: f1(i)≠u1(i) or f2(i)≠u2(i)}| ≤ w}
        # This is tighter than requiring d(f1,u1) ≤ w AND d(f2,u2) ≤ w.

        # Simpler question: for random (u1,u2), how many (f1,f2) ∈ C×C have
        # |{i : f1(i)=u1(i) and f2(i)=u2(i)}| ≥ n-w?

        np.random.seed(42)
        M2_max = {w: 0 for w in range(ceil(wJ), cap)}

        num_trials = 100
        for trial in range(num_trials):
            # Random or codeword centers
            if trial < 50:
                u1 = cw[np.random.randint(total)]
                u2 = cw[np.random.randint(total)]
            else:
                u1 = np.random.randint(0, p, n, dtype=np.int16)
                u2 = np.random.randint(0, p, n, dtype=np.int16)

            # For each pair (f1, f2), compute interleaved distance
            # This is O(|C|^2) per trial — too expensive for large |C|
            # Instead: for each f1, compute agreement with u1 at each position
            # Then for each f2, compute agreement with u2 at each position
            # Joint agreement at position i requires f1(i)=u1(i) AND f2(i)=u2(i)

            # Efficient: for each position i, the set of f1 with f1(i)=u1(i) is ~|C|/p
            # But we need pairs...

            # For small |C|: just compute both distance vectors and find pairs
            d1 = np.sum(cw != u1, axis=1)  # (|C|,) distance of each f from u1
            d2 = np.sum(cw != u2, axis=1)  # (|C|,) distance of each f from u2

            for w in range(ceil(wJ), cap):
                # List for base code: L1 = {f : d(f,u1) ≤ w}, L2 = {f : d(f,u2) ≤ w}
                # Interleaved list at distance w:
                # conservative upper bound: |L1| · |L2|
                # But actual interleaved distance is different.

                # For joint distance: Hamming distance of (f1,f2) from (u1,u2)
                # = |{i : f1(i)≠u1(i) or f2(i)≠u2(i)}|
                # = n - |{i : f1(i)=u1(i) and f2(i)=u2(i)}|

                # Agreement positions for f1: S1(f1) = {i : f1(i) = u1(i)}
                # Joint for (f1,f2): |S1(f1) ∩ S2(f2)| ≥ n-w

                # This requires checking all pairs. For |C|=14641: |C|^2 = 214M — too many.
                # Skip for now, just report base-code M.
                pass

            # Base code list sizes
            for w in range(ceil(wJ), cap):
                cnt1 = int(np.sum(d1 <= w))
                cnt2 = int(np.sum(d2 <= w))
                # Upper bound on interleaved: |L1|·|L2|
                M2_max[w] = max(M2_max[w], cnt1 * cnt2)

        print(f"  Intermediate zone w ∈ [{ceil(wJ)}, {cap-1}]")
        print(f"  {'w':>3} | {'M1_max':>6} | {'M1*M2':>8} | note")
        for w in range(ceil(wJ), cap):
            # Re-derive M1 from the data
            # Actually, just get it from the earlier computation
            M1 = 0
            for idx in range(min(200, total)):
                d = int(np.sum(cw[idx] != cw, axis=1).max())  # wrong
                pass
            print(f"  {w:3d} | {'?':>6} | {M2_max[w]:8d} | product bound")

        print(f"  ({time.time()-t0:.1f}s)")


if __name__ == '__main__':
    print("=" * 70)
    print("DENSITY SCALING VERIFICATION")
    print("=" * 70)

    general_k_M_vs_p()

    print("\n" + "=" * 70)
    print("ALL DONE")
    print("=" * 70)
