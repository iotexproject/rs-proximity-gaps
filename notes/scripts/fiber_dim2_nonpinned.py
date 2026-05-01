"""
fiber_dim2_nonpinned.py — Find max M over NON-PINNED hyperplanes (c=1).

Key finding from fiber_dim2_explore.py: ALL maximum-M hyperplanes are pinned-1
(one element shared by all subsets), with M = C(n-1, w-1).

This script isolates the non-pinned maximum to find the actual gap.
"""

import itertools
from collections import Counter

def find_primitive_root(p):
    for g in range(2, p):
        if pow(g, (p-1)//2, p) != 1:
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

def run(n, p, w_list=None):
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    if w_list is None:
        w_list = list(range(3, min(n//2 + 1, 7)))

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}")

    for w in w_list:
        k = n - w - 1  # c=1
        if k < 1:
            continue

        subsets = list(itertools.combinations(range(n), w))
        sigma_images = []
        for B_idx in subsets:
            B = tuple(L[i] for i in B_idx)
            sigma_images.append(elem_sym(B, p))

        N = len(sigma_images)
        print(f"\n  w={w}, k={k}, c=1, d={w-1}, N={N}")
        print(f"  Pinned-1 max = C({n-1},{w-1}) = {N * w // n}")

        # For exhaustive search: iterate over all hyperplanes
        # A hyperplane: α·σ = β, with α normalized (first nonzero = 1)

        max_M_nonpinned = 0
        max_M_pinned = 0
        best_nonpinned = []
        nonpinned_Ms = []
        pinned_Ms = []

        if p**w > 500000 and p > 23:
            # Too many hyperplanes for exhaustive; sample
            import random
            random.seed(42)
            hyperplanes = set()
            for _ in range(5000):
                alpha = tuple(random.randint(0, p-1) for _ in range(w))
                if all(a == 0 for a in alpha):
                    continue
                beta = random.randint(0, p-1)
                hyperplanes.add((alpha, beta))
            hyperplanes = list(hyperplanes)
        else:
            # Exhaustive over normalized α
            hyperplanes = []
            for alpha in itertools.product(range(p), repeat=w):
                if all(a == 0 for a in alpha):
                    continue
                first_nz = next(i for i, a in enumerate(alpha) if a != 0)
                if alpha[first_nz] != 1:
                    continue  # normalized
                for beta in range(p):
                    hyperplanes.append((alpha, beta))

        for alpha, beta in hyperplanes:
            # Find subsets on this hyperplane
            on_hp = []
            for i, sig in enumerate(sigma_images):
                if sum(a * s for a, s in zip(alpha, sig)) % p == beta:
                    on_hp.append(subsets[i])

            M = len(on_hp)
            if M == 0:
                continue

            # Check pinned: common elements
            common = set(on_hp[0])
            for B in on_hp[1:]:
                common &= set(B)

            is_pinned = len(common) > 0

            if is_pinned:
                pinned_Ms.append(M)
                max_M_pinned = max(max_M_pinned, M)
            else:
                nonpinned_Ms.append(M)
                if M > max_M_nonpinned:
                    max_M_nonpinned = M
                    best_nonpinned = [(alpha, beta, M, on_hp)]
                elif M == max_M_nonpinned:
                    best_nonpinned.append((alpha, beta, M, on_hp))

        print(f"  Pinned:     max M = {max_M_pinned}, count = {len(pinned_Ms)}")
        print(f"  Non-pinned: max M = {max_M_nonpinned}, count = {len(nonpinned_Ms)}")
        print(f"  Ratio non-pinned/pinned = {max_M_nonpinned}/{max_M_pinned} = {max_M_nonpinned/max(max_M_pinned,1):.3f}")
        print(f"  Bound (n/w)^(w-1) = {(n/w)**(w-1):.1f}")
        print(f"  Bound n^2/w^3 + n/w = {n**2/w**3 + n/w:.1f}")
        print(f"  C(n,w)/p = {N/p:.1f}")

        # Non-pinned distribution
        if nonpinned_Ms:
            np_counter = Counter(nonpinned_Ms)
            top5 = sorted(np_counter.items(), key=lambda x: -x[0])[:5]
            print(f"  Non-pinned top M values: {top5}")

        # Analyze best non-pinned
        if best_nonpinned and max_M_nonpinned > 1:
            alpha, beta, M, on_hp = best_nonpinned[0]
            print(f"\n  Best non-pinned: α={alpha}, β={beta}, M={M}")

            # Pairwise overlaps
            overlaps = Counter()
            for i in range(min(len(on_hp), 20)):
                for j in range(i + 1, min(len(on_hp), 20)):
                    ov = len(set(on_hp[i]) & set(on_hp[j]))
                    overlaps[ov] += 1
            print(f"  Pairwise overlap distribution: {dict(sorted(overlaps.items()))}")

            # Element frequency
            freq = Counter()
            for B in on_hp:
                for x in B:
                    freq[x] += 1
            max_freq = max(freq.values())
            min_freq = min(freq.values())
            print(f"  Element freq: max={max_freq}/{M}, min={min_freq}/{M}, total elements used={len(freq)}/{n}")

            # Show first few subsets
            for B in on_hp[:5]:
                print(f"    B = {B}")

# Run
for n, p in [(8, 11), (10, 11), (10, 13), (10, 31), (12, 13), (14, 17), (14, 29), (16, 17)]:
    if p > n:
        run(n, p, w_list=[3, 4])

print("\n" + "="*70)
print("KEY QUESTION: For non-pinned hyperplanes (c=1),")
print("does max M = O(C(n,w)/p) = O(1) for p large?")
