"""
Fast test of equal-threshold CA: ε_ca(C, δ, δ) for small RS codes.
Optimized: precompute all distances, avoid redundant computation.
"""

import sys
from itertools import product as iprod

def make_rs(n, k, p, omega):
    """Build RS[n,k] over F_p. Returns L, list of codewords as tuples."""
    L = [pow(omega, i, p) for i in range(n)]
    codewords = []
    for coeffs in iprod(range(p), repeat=k):
        w = []
        for x in L:
            v, xi = 0, 1
            for c in coeffs:
                v = (v + c * xi) % p
                xi = xi * x % p
            w.append(v)
        codewords.append(tuple(w))
    return L, codewords

def precompute_distances(n, p, codewords):
    """For each word in F_p^n, compute min Hamming distance to code."""
    # Represent words as integers for fast lookup
    dist = {}
    # For each codeword, mark nearby words
    # Start with all distances = n
    total = p ** n
    print(f"  Precomputing distances for {total} words...", flush=True)

    # Build distance array: word_int -> min_dist
    # Initialize all to n
    dist_arr = bytearray(b'\xff' * total)  # 255 = not yet set

    for ci, c in enumerate(codewords):
        c_int = 0
        for j in range(n):
            c_int = c_int * p + c[j]
        dist_arr[c_int] = 0  # codeword itself

    # For small n: just compute each word's distance directly
    if total <= 200000:
        for w_int in range(total):
            # Decode integer to word
            w = []
            tmp = w_int
            for j in range(n):
                w.append(tmp % p)
                tmp //= p
            w = tuple(reversed(w))
            # Compute distance
            best = n
            for c in codewords:
                d = sum(1 for j in range(n) if w[j] != c[j])
                if d < best:
                    best = d
                    if best == 0:
                        break
            dist_arr[w_int] = best

        print(f"  Done.", flush=True)
        return dist_arr
    else:
        print(f"  Too large for exhaustive precompute!", flush=True)
        return None

def word_to_int(w, p):
    r = 0
    for v in w:
        r = r * p + v
    return r

def test_case(n, k, p, omega, w_max):
    """Test ε_ca(C, δ, δ) with δ = w_max/n."""
    delta = w_max / n
    delta_J = 1.0 - (k / n) ** 0.5
    rho = k / n

    print(f"\n{'='*60}", flush=True)
    print(f"RS[{n},{k}] / F_{p}, ω={omega}, ρ={rho:.3f}", flush=True)
    print(f"δ_J = {delta_J:.4f}, δ = {w_max}/{n} = {delta:.4f}", flush=True)
    print(f"w_max = {w_max} (max errors for δ-close)", flush=True)

    if delta <= delta_J:
        print(f"SKIP: δ ≤ δ_J (not above Johnson)", flush=True)
        return

    L, codewords = make_rs(n, k, p, omega)
    print(f"|C| = {len(codewords)}", flush=True)

    total = p ** n
    if total > 200000:
        print(f"SKIP: F_p^n = {total} too large", flush=True)
        return

    dist_arr = precompute_distances(n, p, codewords)
    if dist_arr is None:
        return

    # For joint distance: we need min over (g1,g2) in C^2 of |supp(f1-g1) ∪ supp(f2-g2)|
    # Optimization: for each g1, precompute the error pattern of f1-g1, then find g2 minimizing union
    # But C^2 can be large. For |C| = p^k:
    #   |C^2| = p^(2k). For p=5,k=2: 625. For p=7,k=3: 117649.
    # Alternative: for fixed f1, compute supp(f1-g1) for each g1 as a bitmask.
    # Then for fixed f2, compute supp(f2-g2) for each g2.
    # Joint = |bitmask_g1 | bitmask_g2|. Minimize over (g1,g2).

    # Precompute error bitmasks for all (word, codeword) pairs?
    # Too much memory. Instead: for each f, precompute bitmask for all codewords.

    # Strategy: iterate over f1 (skipping if dist(f1) = 0).
    # For each f1, precompute masks1[g1] = error bitmask of f1-g1.
    # Then iterate over f2. For each f2, precompute masks2[g2].
    # Joint distance = min over g1,g2 of popcount(masks1[g1] | masks2[g2]).
    # If min > w_max: count bad gammas.

    max_bad = 0
    max_pair = None
    hist = {}
    n_tested = 0

    # Only consider f1 with dist(f1) > 0 (codewords can't have Δ_joint > δ easily)
    # Actually codewords CAN be part of a pair with Δ_joint > δ, if f2 is far enough.

    print(f"Iterating over all f1, f2 pairs...", flush=True)

    for f1_int in range(total):
        # Decode f1
        f1 = []
        tmp = f1_int
        for j in range(n):
            f1.append(tmp % p)
            tmp //= p
        f1 = tuple(reversed(f1))

        # Precompute error bitmasks for f1 vs all codewords
        masks1 = []
        for c in codewords:
            mask = 0
            for j in range(n):
                if f1[j] != c[j]:
                    mask |= (1 << j)
            masks1.append(mask)

        for f2_int in range(total):
            # Decode f2
            f2 = []
            tmp = f2_int
            for j in range(n):
                f2.append(tmp % p)
                tmp //= p
            f2 = tuple(reversed(f2))

            # Compute joint distance via bitmask
            min_joint = n + 1
            # Precompute masks2
            masks2 = []
            for c in codewords:
                mask = 0
                for j in range(n):
                    if f2[j] != c[j]:
                        mask |= (1 << j)
                masks2.append(mask)

            for m1 in masks1:
                for m2 in masks2:
                    jt = bin(m1 | m2).count('1')
                    if jt < min_joint:
                        min_joint = jt

            if min_joint <= w_max:
                continue  # Δ_joint ≤ δ

            n_tested += 1

            # Count bad gamma
            bad = 0
            bad_gammas = []
            for gamma in range(p):
                fg = tuple((f1[j] + gamma * f2[j]) % p for j in range(n))
                fg_int = word_to_int(fg, p)
                if dist_arr[fg_int] <= w_max:
                    bad += 1
                    bad_gammas.append(gamma)

            hist[bad] = hist.get(bad, 0) + 1

            if bad > max_bad:
                max_bad = bad
                max_pair = (f1, f2, bad_gammas)
                d1 = dist_arr[f1_int]
                d2 = dist_arr[f2_int]
                print(f"  NEW MAX: {bad} bad γ's = {bad_gammas}", flush=True)
                print(f"    f1={f1} (Δ={d1}), f2={f2} (Δ={d2}), Δ_joint={min_joint}", flush=True)

        if f1_int % 100 == 99:
            print(f"  f1 progress: {f1_int+1}/{total}, tested {n_tested} pairs, max_bad={max_bad}", flush=True)

    print(f"\n{'='*60}", flush=True)
    print(f"RESULTS: RS[{n},{k}] / F_{p}, δ={w_max}/{n}", flush=True)
    print(f"  Pairs with Δ_joint > δ: {n_tested}", flush=True)
    print(f"  Max bad γ: {max_bad}", flush=True)
    print(f"  Histogram: {dict(sorted(hist.items()))}", flush=True)
    if max_bad <= 2:
        print(f"  ✓ ε_ca(C,δ,δ) ≤ {max_bad}/|F| — O(1)/|F| holds!", flush=True)
    else:
        print(f"  ✗ max bad γ = {max_bad}", flush=True)
    print(flush=True)
    return max_bad


def find_prim_root(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) == 1:
            ok = True
            for d in range(1, n):
                if n % d == 0 and d < n and pow(w, d, p) == 1:
                    ok = False
                    break
            if ok:
                return w
    return None


if __name__ == "__main__":
    print("EQUAL-THRESHOLD CA BOUND: COMPUTATIONAL TEST", flush=True)
    print("Testing whether ε_ca(C, δ, δ) = O(1)/|F| for RS codes above Johnson\n", flush=True)

    # Test 1: RS[4,2]/F_5, δ=1/2 (w=2)
    w = find_prim_root(5, 4)
    if w: test_case(4, 2, 5, w, 2)

    # Test 2: RS[4,2]/F_13, δ=1/2 (w=2)
    w = find_prim_root(13, 4)
    if w: test_case(4, 2, 13, w, 2)

    # Test 3: RS[6,3]/F_7, δ=1/2 (w=3)
    w = find_prim_root(7, 6)
    if w: test_case(6, 3, 7, w, 3)

    # Test 4: RS[4,2]/F_29, δ=1/2 (w=2) — larger field
    w = find_prim_root(29, 4)
    if w: test_case(4, 2, 29, w, 2)

    # Test 5: RS[4,2]/F_41, δ=1/2 (w=2)
    w = find_prim_root(41, 4)
    if w: test_case(4, 2, 41, w, 2)

    print("\n=== SUMMARY ===", flush=True)
    print("If all cases show max_bad ≤ 2: strong evidence for OP1", flush=True)
    print("If any case shows max_bad >> 2: obstruction to OP1", flush=True)
