#!/usr/bin/env python3
"""
M_intermediate_zone.py — Map list-size landscape in the intermediate zone.

Part 1: Exact M_max(w) for RS[n,k] over F_p (small parameters)
Part 2: Analytic bound evaluation for FRI parameters (large n)
Part 3: Smooth domain indicator analysis

Goal: verify M = O(1) in intermediate zone [Johnson, capacity),
      check if M = 0 for specific centers (evidence for OP3).
"""

import numpy as np
from itertools import product
from math import comb, sqrt, floor, ceil, log, lgamma
import time

# ─── Part 1: Exact computation ───

def eval_poly(coeffs, x, p):
    """coeffs = [a0, a1, ..., a_{k-1}], evaluate at x mod p."""
    val = 0
    for c in reversed(coeffs):
        val = (val * x + c) % p
    return val


def generate_codewords_np(n, k, p, L):
    """Generate all RS codewords as numpy array."""
    # Total: p^k codewords
    total = p ** k
    cw = np.zeros((total, n), dtype=np.int32)

    for idx in range(total):
        # Decode idx into polynomial coefficients
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        # Evaluate
        for j, x in enumerate(L):
            val = 0
            for c in reversed(coeffs):
                val = (val * x + c) % p
            cw[idx, j] = val

    return cw


def exact_M_landscape(n, k, p, max_centers=2000):
    """Compute exact M_max(w) for RS[n,k] over F_p."""
    L = list(range(1, n + 1))
    total_cw = p ** k

    rho = k / n
    wJ = n * (1 - sqrt(rho))
    cap = n - k

    print(f"\nRS[{n},{k}] over F_{p}  (p^k = {total_cw})")
    print(f"  ρ = {rho:.3f}, wJ = {wJ:.2f}, capacity = {cap}")
    print(f"  Intermediate zone: w ∈ [{ceil(wJ)}, {cap})")

    t0 = time.time()
    cw = generate_codewords_np(n, k, p, L)
    print(f"  Generated {total_cw} codewords in {time.time()-t0:.1f}s")

    M_max_cw = np.zeros(n + 1, dtype=int)
    M_max_rand = np.zeros(n + 1, dtype=int)

    # Codeword-centered list sizes
    t0 = time.time()
    num_centers = min(max_centers, total_cw)
    indices = np.random.choice(total_cw, num_centers, replace=False) if total_cw > max_centers else np.arange(total_cw)

    for i in indices:
        dists = np.sum(cw[i] != cw, axis=1)  # Hamming distance to all codewords
        hist = np.bincount(dists, minlength=n + 1)
        cum = np.cumsum(hist)
        M_max_cw = np.maximum(M_max_cw, cum[:n+1])

    print(f"  Codeword centers ({num_centers}) in {time.time()-t0:.1f}s")

    # Random non-codeword centers
    t0 = time.time()
    np.random.seed(42)
    num_rand = min(2000, p ** n)
    for _ in range(num_rand):
        u = np.random.randint(0, p, size=n)
        dists = np.sum(u != cw, axis=1)
        hist = np.bincount(dists, minlength=n + 1)
        cum = np.cumsum(hist)
        M_max_rand = np.maximum(M_max_rand, cum[:n+1])

    print(f"  Random centers ({num_rand}) in {time.time()-t0:.1f}s")

    M_max = np.maximum(M_max_cw, M_max_rand)

    # Report
    print(f"\n  {'w':>3} | {'M_cw':>6} | {'M_rand':>6} | {'M_max':>6} | zone")
    print(f"  {'---':>3} | {'---':>6} | {'---':>6} | {'---':>6} | ---")

    for w in range(n + 1):
        zone = ""
        if w < ceil(wJ):
            zone = "< Johnson"
        elif w < cap:
            zone = "INTERMEDIATE"
        elif w == cap:
            zone = "= capacity"
        else:
            zone = "> capacity"

        mc = int(M_max_cw[w])
        mr = int(M_max_rand[w])
        mm = int(M_max[w])

        # Always show intermediate zone, show others only if interesting
        if zone == "INTERMEDIATE" or mm > 1 or w in [floor(wJ), ceil(wJ), cap-1, cap]:
            marker = " <<<" if zone == "INTERMEDIATE" and mm > 1 else ""
            print(f"  {w:3d} | {mc:6d} | {mr:6d} | {mm:6d} | {zone}{marker}")

    return M_max


# ─── Part 2: Analytic bound ───

def log2_binom(n, k):
    """log2(C(n,k)) via lgamma."""
    if k <= 0 or k >= n:
        return 0.0
    return (lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)) / log(2)


def analytic_bound(n, k, p):
    """Evaluate M bound in intermediate zone for RS[n,k] over F_p."""
    rho = k / n
    wJ = n * (1 - sqrt(rho))
    cap = n - k
    log2p = log(p) / log(2)

    print(f"\nAnalytic bounds: RS[{n},{k}] over F_{p}  (log2 p = {log2p:.1f})")
    print(f"  ρ = {rho:.3f}, wJ = {wJ:.1f}, capacity = {cap}")

    w_lo = max(1, ceil(wJ) - 1)
    w_hi = min(n - 1, cap + 1)

    print(f"\n  {'w':>8} | {'t=n-w':>8} | {'t|n':>4} | {'(t-1)|n':>7} | {'log2(spor)':>10} | {'bound':>12} | zone")
    print(f"  {'---':>8} | {'---':>8} | {'---':>4} | {'---':>7} | {'---':>10} | {'---':>12} | ---")

    for w in range(w_lo, w_hi + 1):
        t = n - w
        if t <= 1:
            continue

        t_div = (n % t == 0)
        tm1_div = (n % (t - 1) == 0) if t > 1 else False

        ind1 = n // t if t_div else 0
        ind2 = n // (t - 1) if tm1_div else 0

        log2_spor = log2_binom(n, t) - (t - 2) * log2p

        if ind1 + ind2 > 0:
            bound = f"{ind1}+{ind2}+2^{log2_spor:.0f}"
        elif log2_spor < -20:
            bound = "≈ 0"
        elif log2_spor < 0:
            bound = f"2^{log2_spor:.1f}"
        else:
            bound = f"2^{log2_spor:.0f}"

        zone = "INTERMEDIATE" if ceil(wJ) <= w < cap else ("<J" if w < ceil(wJ) else "≥cap")

        print(f"  {w:8d} | {t:8d} | {'YES' if t_div else 'no':>4} | {'YES' if tm1_div else 'no':>7} | {log2_spor:10.1f} | {bound:>12} | {zone}")


# ─── Part 3: Smooth domain indicator analysis ───

def smooth_domain_analysis(K_values):
    """For n=2^K, ρ=1/2: how many t in intermediate zone have t|n or (t-1)|n?"""
    print(f"\n{'='*70}")
    print(f"Smooth domain indicator analysis (n=2^K, ρ=1/2)")
    print(f"{'='*70}")

    for K in K_values:
        n = 2 ** K
        k = n // 2
        wJ = n * (1 - sqrt(0.5))

        # Intermediate zone: w ∈ [ceil(wJ), cap), t = n-w ∈ (k, n-ceil(wJ)]
        t_lo = k + 1
        t_hi = n - ceil(wJ)
        total = t_hi - t_lo + 1

        if total <= 0:
            print(f"\n  n=2^{K}={n}: intermediate zone empty")
            continue

        t_div = [t for t in range(t_lo, t_hi + 1) if n % t == 0]
        tm1_div = [t for t in range(t_lo, t_hi + 1) if t > 1 and n % (t - 1) == 0]
        either = set(t_div) | set(tm1_div)
        clean = total - len(either)

        print(f"\n  n=2^{K}={n}, k={k}, t ∈ ({k}, {t_hi}], total={total}")
        print(f"    t|n:     {len(t_div):>5}  {t_div[:8]}")
        print(f"    (t-1)|n: {len(tm1_div):>5}  {tm1_div[:8]}")
        print(f"    either:  {len(either):>5}")
        print(f"    CLEAN (both=0): {clean} / {total}  ({100*clean/total:.1f}%)")

        # For clean t values, what is the sporadic bound at FRI parameters?
        # Use p = 2^31 - 1 (Mersenne prime)
        p = 2**31 - 1
        log2p = 31.0
        if clean > 0:
            # Pick a few clean t values and evaluate
            clean_ts = [t for t in range(t_lo, t_hi + 1) if t not in either]
            samples = clean_ts[::max(1, len(clean_ts)//5)][:5]
            print(f"    Sample clean t values, log2(C(n,t)/p^{{t-2}}):")
            for t in samples:
                w = n - t
                log2_spor = log2_binom(n, t) - (t - 2) * log2p
                print(f"      t={t:>8}, w={w:>8}: log2(sporadic) = {log2_spor:>12.1f}")


# ─── Part 4: Intermediate zone M for n=16 via error-pattern enumeration ───

def interpolate_fp(xs, ys, p):
    """Lagrange interpolation over F_p. Returns coefficients [a0,...,a_{k-1}]."""
    k = len(xs)
    # Build Lagrange basis
    coeffs = [0] * k
    for i in range(k):
        # Compute L_i(x) = prod_{j!=i} (x - xj)/(xi - xj)
        numer = [1]  # polynomial 1
        denom = 1
        for j in range(k):
            if j == i:
                continue
            # Multiply numer by (x - xj)
            new_numer = [0] * (len(numer) + 1)
            for m in range(len(numer)):
                new_numer[m] = (new_numer[m] + numer[m] * (-xs[j])) % p
                new_numer[m + 1] = (new_numer[m + 1] + numer[m]) % p
            numer = new_numer
            denom = (denom * (xs[i] - xs[j])) % p

        # Multiply by yi / denom
        inv_denom = pow(denom, p - 2, p)
        scale = (ys[i] * inv_denom) % p
        for m in range(len(numer)):
            coeffs[m] = (coeffs[m] + numer[m] * scale) % p

    return coeffs


def exact_M_n16(n, k, p, num_u_samples=500):
    """Exact M computation for n=16 using error-pattern enumeration."""
    L = list(range(1, n + 1))
    rho = k / n
    wJ = n * (1 - sqrt(rho))
    cap = n - k

    print(f"\nRS[{n},{k}] over F_{p} (error-pattern method)")
    print(f"  ρ = {rho:.3f}, wJ = {wJ:.2f}, capacity = {cap}")

    # Precompute Vandermonde-like data for interpolation
    # For a fixed (n-w)-subset of agreement positions, interpolating k points gives the polynomial

    M_max = np.zeros(n + 1, dtype=int)

    # Sample received words: some codewords + random
    np.random.seed(42)

    # Generate some codewords as centers
    cw_centers = []
    for _ in range(min(200, p**k)):
        coeffs = [np.random.randint(0, p) for _ in range(k)]
        word = tuple(eval_poly(coeffs, x, p) for x in L)
        cw_centers.append(word)

    # Random non-codeword centers
    rand_centers = [tuple(np.random.randint(0, p, n)) for _ in range(num_u_samples)]

    all_centers = cw_centers + rand_centers

    t0 = time.time()
    for ci, u in enumerate(all_centers):
        if ci % 100 == 0 and ci > 0:
            print(f"  ... processed {ci}/{len(all_centers)} centers ({time.time()-t0:.1f}s)")

        found_codewords = set()

        # For each w in intermediate zone
        for w in range(max(1, ceil(wJ) - 1), cap + 2):
            if w >= n:
                continue
            agree = n - w  # number of agreement positions
            if agree < k:
                continue  # underdetermined

            # Enumerate all (n choose agree) subsets of agreement positions
            # But C(16, agree) can be large. Limit: only do if C(n, min(w, agree)) is manageable
            enum_size = comb(n, min(w, agree))
            if enum_size > 50000:
                continue  # skip too-large cases

            # Enumerate error-position subsets (smaller when w < n/2)
            if w <= agree:
                # Enumerate w-subsets of error positions
                for err_pos in __import__('itertools').combinations(range(n), w):
                    agr_pos = [j for j in range(n) if j not in err_pos]
                    xs = [L[j] for j in agr_pos[:k]]
                    ys = [u[j] for j in agr_pos[:k]]

                    try:
                        coeffs = interpolate_fp(xs, ys, p)
                    except:
                        continue

                    if len(coeffs) < k:
                        coeffs += [0] * (k - len(coeffs))

                    # Check polynomial agrees on ALL agreement positions
                    valid = True
                    for j in agr_pos[k:]:
                        if eval_poly(coeffs, L[j], p) != u[j]:
                            valid = False
                            break

                    if valid:
                        word = tuple(eval_poly(coeffs, x, p) for x in L)
                        found_codewords.add(word)

        # Compute list size at each distance w
        if found_codewords:
            for cw in found_codewords:
                d = sum(1 for a, b in zip(u, cw) if a != b)
                # This codeword contributes to M(w) for all w >= d
                for w in range(d, n + 1):
                    M_max[w] = max(M_max[w], 1)  # at least 1

            # Actually recount properly
            for w in range(n + 1):
                cnt = sum(1 for cw in found_codewords
                         if sum(1 for a, b in zip(u, cw) if a != b) <= w)
                M_max[w] = max(M_max[w], cnt)

    print(f"  Total time: {time.time()-t0:.1f}s")

    # Report
    print(f"\n  {'w':>3} | {'M_max':>6} | zone")
    print(f"  {'---':>3} | {'---':>6} | ---")
    for w in range(n + 1):
        zone = "INTERMEDIATE" if ceil(wJ) <= w < cap else ("<J" if w < ceil(wJ) else "≥cap")
        mm = int(M_max[w])
        if zone == "INTERMEDIATE" or mm > 0:
            print(f"  {w:3d} | {mm:6d} | {zone}")

    return M_max


# ═══════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 70)
    print("LIST SIZE M IN THE INTERMEDIATE ZONE")
    print("=" * 70)

    # ─── Part 1: Exact for small n ───
    print("\n" + "=" * 70)
    print("PART 1: Exact M_max(w)")
    print("=" * 70)

    configs = [
        (8, 4, 11),   # p^k = 14641
        (8, 4, 17),   # p^k = 83521
        (8, 4, 31),   # p^k = 923521
        (8, 4, 43),   # p^k = 3418801 — might be slow
        (8, 2, 11),   # p^k = 121, very fast
        (8, 2, 17),   # p^k = 289
        (8, 2, 31),   # p^k = 961
        (8, 3, 11),   # p^k = 1331
        (8, 3, 17),   # p^k = 4913
    ]

    for n, k, p in configs:
        if p <= n:
            continue
        if p ** k > 4_000_000:
            print(f"\nRS[{n},{k}] over F_{p}: SKIPPED (p^k = {p**k})")
            continue
        exact_M_landscape(n, k, p)

    # ─── Part 2: n=16 error-pattern method ───
    print("\n" + "=" * 70)
    print("PART 2: n=16 exact (error-pattern enumeration)")
    print("=" * 70)

    exact_M_n16(16, 8, 17, num_u_samples=300)
    exact_M_n16(16, 8, 31, num_u_samples=200)

    # ─── Part 3: Analytic bounds for large n ───
    print("\n" + "=" * 70)
    print("PART 3: Analytic bound evaluation")
    print("=" * 70)

    # Small n (compare with exact)
    analytic_bound(8, 4, 11)
    analytic_bound(8, 4, 31)
    analytic_bound(16, 8, 17)

    # FRI-scale parameters
    analytic_bound(2**10, 2**9, 2**31 - 1)
    analytic_bound(2**15, 2**14, 2**31 - 1)
    analytic_bound(2**20, 2**19, 2**31 - 1)

    # ─── Part 4: Smooth domain indicators ───
    smooth_domain_analysis([3, 4, 5, 6, 8, 10, 15, 20])

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
