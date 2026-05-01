"""
fiber_general_bound.py — Verify the General Fiber Bound for d-dimensional flats.

THEOREM (General Fiber Bound):
For a non-pinned d-dimensional flat V ⊂ F_p^w (d = w-c), the number M of
w-subsets of L with σ-image on V satisfies:

    M ≤ C(n, d) / C(w, d)

PROOF IDEA:
- Each T ∈ L defines a (d-1)-flat in the d-dimensional parameter space F_p^d
- A valid w-subset ↔ w-rich point (d lines/flats passing through one point)
- d generic (d-1)-flats meet in ≤ 1 point
- KST-type counting: M × C(w,d) ≤ C(n,d) + O(non-generic)

This script tests:
1. c = w-2 (d=2): 2-planes in F_p^w, lines in F_p^2
2. c = w-3 (d=3): 3-planes in F_p^w, planes in F_p^3
3. Various (n, w, p) combinations
"""

import itertools
from collections import Counter
from math import comb
import random

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p-1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p-1:
            return g
    return None

def elem_sym(B, p):
    w = len(B)
    e = [0] * (w + 1)
    e[0] = 1
    for b in B:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * b) % p
    return tuple(e[1:])

def test_fiber_bound(n, p, w, c):
    """Test fiber bound for specific (n, p, w, c).
    d = w - c is the flat dimension.
    k = n - w - c.
    """
    d = w - c
    k = n - w - c
    if k < 1 or d < 2:
        return

    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # All w-subsets and σ-images
    subsets = list(itertools.combinations(range(n), w))
    sigma_images = []
    for B_idx in subsets:
        B = tuple(L[i] for i in B_idx)
        sigma_images.append(elem_sym(B, p))

    N = len(sigma_images)
    bound = comb(n, d) / comb(w, d)

    print(f"\nn={n}, p={p}, w={w}, c={c}, d={d}, k={k}")
    print(f"  N = C({n},{w}) = {N}")
    print(f"  Bound C(n,d)/C(w,d) = C({n},{d})/C({w},{d}) = {comb(n,d)}/{comb(w,d)} = {bound:.1f}")
    print(f"  Density C(n,w)/p^c = {N / p**c:.2f}")

    # Generate random d-dimensional flats in F_p^w
    # A d-flat: V = {a + Σ_{i=1}^d s_i b_i : s ∈ F_p^d}
    # Defined by c = w-d linear equations: α^(j) · σ = β_j for j=1,...,c

    random.seed(42)
    max_M_all = 0
    max_M_nonpinned = 0
    M_dist_nonpinned = Counter()
    num_trials = min(3000, p**(w*c) // max(1, p**(w*c) // 3000))
    num_trials = max(num_trials, 1000)

    for trial in range(num_trials):
        # Random c-codimensional flat: c normal vectors + offsets
        normals = []
        offsets = []
        for j in range(c):
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            beta = random.randint(0, p-1)
            normals.append(alpha)
            offsets.append(beta)

        # Count σ-images on this flat
        on_flat = []
        for i, sig in enumerate(sigma_images):
            on = True
            for j in range(c):
                dot = sum(a*s for a,s in zip(normals[j], sig)) % p
                if dot != offsets[j]:
                    on = False
                    break
            if on:
                on_flat.append(subsets[i])

        M = len(on_flat)
        if M > max_M_all:
            max_M_all = M

        if M == 0:
            continue

        # Check pinned
        common = set(on_flat[0])
        for B in on_flat[1:]:
            common &= set(B)
        is_pinned = len(common) > 0

        if not is_pinned:
            M_dist_nonpinned[M] += 1
            if M > max_M_nonpinned:
                max_M_nonpinned = M
                best_info = (normals, offsets, on_flat)

    print(f"  Random flats ({num_trials} trials):")
    print(f"    max M (all)       = {max_M_all}")
    print(f"    max M (non-pinn.) = {max_M_nonpinned}")
    print(f"    BOUND satisfied?  {max_M_nonpinned <= bound + 0.5} (bound={bound:.1f})")

    top_vals = sorted(M_dist_nonpinned.items(), key=lambda x: -x[0])[:5]
    print(f"    Non-pinned top M: {top_vals}")

    if max_M_nonpinned > 0 and 'best_info' in dir():
        normals, offsets, on_flat = best_info
        overlaps = Counter()
        for i in range(min(len(on_flat), 20)):
            for j in range(i+1, min(len(on_flat), 20)):
                ov = len(set(on_flat[i]) & set(on_flat[j]))
                overlaps[ov] += 1
        print(f"    Best non-pinned overlap dist: {dict(sorted(overlaps.items()))}")
        freq = Counter()
        for B in on_flat:
            for x in B:
                freq[x] += 1
        print(f"    Element freq: max={max(freq.values())}/{M}, min={min(freq.values())}/{M}, elems={len(freq)}/{n}")

    return max_M_nonpinned, bound

# === Test cases ===
print("=" * 70)
print("GENERAL FIBER BOUND: M ≤ C(n,d)/C(w,d)")
print("=" * 70)

results = []

# d=2 cases (c = w-2)
print("\n--- d=2 (2-planes, c=w-2) ---")
for n, p, w in [(10, 11, 4), (10, 13, 4), (10, 31, 4),
                (12, 13, 4), (12, 13, 5), (12, 29, 4),
                (14, 17, 5), (14, 29, 5), (14, 29, 6),
                (16, 17, 5), (16, 17, 6)]:
    c = w - 2
    if n - w - c >= 1 and p > n:
        r = test_fiber_bound(n, p, w, c)
        if r:
            results.append(("d=2", n, p, w, c, r[0], r[1]))

# d=3 cases (c = w-3)
print("\n\n--- d=3 (3-planes, c=w-3) ---")
for n, p, w in [(10, 11, 5), (10, 13, 5), (12, 13, 5), (12, 13, 6),
                (14, 17, 6), (14, 29, 6)]:
    c = w - 3
    if n - w - c >= 1 and c >= 1 and p > n:
        r = test_fiber_bound(n, p, w, c)
        if r:
            results.append(("d=3", n, p, w, c, r[0], r[1]))

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"{'type':>5} {'n':>3} {'p':>3} {'w':>3} {'c':>3} {'maxM':>6} {'bound':>8} {'OK?':>5}")
for dtype, n, p, w, c, maxM, bound in results:
    ok = "YES" if maxM <= bound + 0.5 else "NO"
    print(f"{dtype:>5} {n:>3} {p:>3} {w:>3} {c:>3} {maxM:>6} {bound:>8.1f} {ok:>5}")
