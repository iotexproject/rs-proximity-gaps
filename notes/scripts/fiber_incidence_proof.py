"""
fiber_incidence_proof.py — Verify the incidence-geometric proof of M = O(1) for d=2.

THEOREM (Incidence Fiber Bound for d=2):
For a d=2 flat V in F_p^w with w ≥ 3, the list size satisfies:

    M ≤ C(n,2)/C(w,2) + n(w-2)/2

where the first term comes from non-coincident line intersections (KST)
and the second from coincident-line groups.

For rate 1/2 (w ≈ 0.29n):
    C(n,2)/C(w,2) ≈ (n/w)^2 ≈ 12
    n(w-2)/2 ≈ 0.14n^2  ... this is NOT O(1)!

Problem: the coincident-line contribution is O(n^2), not O(1).

REVISED APPROACH: Each coincident-line GROUP has ≤ w-1 elements.
Within a group, all lines coincide → a single line with multiplicity k_g.
A w-rich point on this line needs ≥ w elements total, using ≤ k_g from
this group and the rest from other groups' lines passing through the point.

Key insight: even within a coincident group, the w-rich point condition
still requires w DISTINCT elements from L, not just w elements on the same line.

So: if a group has k_g ≤ w-1 coincident elements, it can contribute at most
k_g elements to any w-subset. The remaining w - k_g must come from OTHER groups.

The bound becomes: for a point s with |I_s| = w, at most w-1 come from any
one group, and the rest from ≥ 2 other groups' lines (which pass through s).

This is equivalent to a COLORED incidence problem.

Let me verify the group structure and the corrected bound.
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

def test_incidence(n, p, w, c):
    """Analyze the line arrangement for d=2 flats.

    For each T ∈ L, the line in (s_1, s_2) space is:
    φ_0(T) + s_1 φ_1(T) + s_2 φ_2(T) = 0

    where φ_i depend on the parameterization of the flat.
    """
    d = w - c
    k = n - w - c
    if k < 1 or d != 2:
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

    print(f"\nn={n}, p={p}, w={w}, c={c}, d={d}, k={k}")
    print(f"  KST = C(n,2)/C(w,2) = {comb(n,2)/comb(w,2):.1f}")
    print(f"  Bézout = (n-w)^d = {(n-w)**d}")

    random.seed(42)

    # Sample random d=2 flats and analyze the line arrangement
    num_trials = min(500, p**(w*c))

    for trial in range(num_trials):
        # Random flat: c conditions
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        # Find compatible subsets
        on_flat = []
        for i, sig in enumerate(sigma_images):
            ok = True
            for j in range(c):
                if sum(a*s for a,s in zip(normals[j], sig)) % p != offsets[j]:
                    ok = False
                    break
            if ok:
                on_flat.append(subsets[i])
        M = len(on_flat)

        if M < 5:
            continue

        # Check pinned
        common = set(on_flat[0])
        for B in on_flat[1:]:
            common &= set(B)
        if len(common) > 0:
            continue  # Skip pinned

        # Parameterize the 2D flat by choosing 2 free variables
        # For the c conditions α_j · σ = β_j (j=0,...,c-1):
        # Solve for c variables in terms of d=2 free ones

        # Find basis for the flat: solve the c×w system
        # normals[j] · σ = offsets[j]

        # Gaussian elimination to find the parameterization
        # Build c×(w+1) augmented matrix
        mat = [[normals[j][i] for i in range(w)] + [offsets[j]] for j in range(c)]

        # Row reduce
        pivots = []
        for col in range(w):
            if len(pivots) >= c:
                break
            row = len(pivots)
            found = False
            for r in range(row, c):
                if mat[r][col] != 0:
                    mat[row], mat[r] = mat[r], mat[row]
                    found = True
                    break
            if not found:
                continue
            inv = pow(mat[row][col], p-2, p)
            for j in range(w+1):
                mat[row][j] = (mat[row][j] * inv) % p
            for r in range(c):
                if r != row and mat[r][col] != 0:
                    fac = mat[r][col]
                    for j in range(w+1):
                        mat[r][j] = (mat[r][j] - fac * mat[row][j]) % p
            pivots.append(col)

        if len(pivots) < c:
            continue  # Rank-deficient, skip

        # Free variables
        free_vars = [j for j in range(w) if j not in pivots]
        if len(free_vars) != d:
            continue

        # Parameterization: σ_j = a_j + Σ_i s_i b_{j,i}
        # For j ∈ pivots: σ_j = mat[row][w] - Σ_{free} mat[row][free] s_free
        a = [0]*w
        b = [[0]*d for _ in range(w)]  # b[j][i] = coefficient of s_i for σ_j
        for idx, piv in enumerate(pivots):
            a[piv] = mat[idx][w]
            for fi, fv in enumerate(free_vars):
                b[piv][fi] = (-mat[idx][fv]) % p
        for fi, fv in enumerate(free_vars):
            a[fv] = 0
            b[fv][fi] = 1

        # For each T ∈ L, compute (φ_0, φ_1, φ_2) where
        # P_s(T) = T^w + Σ_j (-1)^j σ_j(s) T^{w-j} = 0
        # = T^w + Σ_j (-1)^j (a_j + s_1 b_{j,0} + s_2 b_{j,1}) T^{w-j} = 0
        # = [T^w + Σ_j (-1)^j a_j T^{w-j}] + s_1[Σ_j (-1)^j b_{j,0} T^{w-j}] + s_2[...] = 0
        # = φ_0(T) + s_1 φ_1(T) + s_2 φ_2(T) = 0

        lines = []  # (φ_0, φ_1, φ_2) for each T ∈ L
        for idx_T in range(n):
            T = L[idx_T]
            T_powers = [1]
            for j in range(1, w+1):
                T_powers.append((T_powers[-1] * T) % p)

            phi0 = T_powers[w]  # T^w
            for j in range(1, w+1):
                sign = (-1)**j % p
                phi0 = (phi0 + sign * a[j-1] * T_powers[w-j]) % p

            phi1 = 0
            for j in range(1, w+1):
                sign = (-1)**j % p
                phi1 = (phi1 + sign * b[j-1][0] * T_powers[w-j]) % p

            phi2 = 0
            for j in range(1, w+1):
                sign = (-1)**j % p
                phi2 = (phi2 + sign * b[j-1][1] * T_powers[w-j]) % p

            lines.append((phi0, phi1, phi2))

        # Group by direction: two lines (φ_0, φ_1, φ_2) and (φ_0', φ_1', φ_2')
        # are coincident iff they're proportional.
        # Direction = [φ_1 : φ_2] in P^1 (if φ_1 = φ_2 = 0, it's a "point" not a line)
        groups = {}
        for idx_T in range(n):
            phi0, phi1, phi2 = lines[idx_T]
            if phi1 == 0 and phi2 == 0:
                # Not a line, it's a trivial constraint
                dir_key = 'trivial'
            elif phi1 == 0:
                dir_key = (0, 1)
            elif phi2 == 0:
                dir_key = (1, 0)
            else:
                # Normalize: (1, phi2/phi1)
                ratio = (phi2 * pow(phi1, p-2, p)) % p
                dir_key = (1, ratio)
            if dir_key not in groups:
                groups[dir_key] = []
            groups[dir_key].append(idx_T)

        # Check coincidence: same direction AND same offset
        coincident_groups = {}
        for dir_key, members in groups.items():
            if dir_key == 'trivial':
                continue
            if len(members) <= 1:
                continue
            # Check which members have same (normalized) line
            by_line = {}
            for idx_T in members:
                phi0, phi1, phi2 = lines[idx_T]
                # Normalize: divide by first nonzero of (phi1, phi2)
                if phi1 != 0:
                    inv = pow(phi1, p-2, p)
                else:
                    inv = pow(phi2, p-2, p)
                norm_line = tuple((x * inv) % p for x in (phi0, phi1, phi2))
                if norm_line not in by_line:
                    by_line[norm_line] = []
                by_line[norm_line].append(idx_T)

            for line_key, coinc_members in by_line.items():
                if len(coinc_members) > 1:
                    if dir_key not in coincident_groups:
                        coincident_groups[dir_key] = []
                    coincident_groups[dir_key].append(coinc_members)

        num_groups = len(groups)
        max_group_size = max(len(m) for m in groups.values()) if groups else 0
        num_coinc = sum(len(m) for g in coincident_groups.values() for m in g)

        if M >= comb(n,d)/comb(w,d) or trial < 3:
            print(f"\n  Trial {trial}: M={M}, #groups={num_groups}, max_group={max_group_size}, #coincident={num_coinc}")
            if coincident_groups:
                for dk, gs in list(coincident_groups.items())[:3]:
                    for g in gs[:2]:
                        print(f"    Coincident group dir={dk}: members={g}")

            # Count w-rich points
            rich_points = {}
            for idx_T in range(n):
                phi0, phi1, phi2 = lines[idx_T]
                if phi1 == 0 and phi2 == 0:
                    continue
                # For each other element, find intersection
                for idx_T2 in range(idx_T+1, n):
                    phi0b, phi1b, phi2b = lines[idx_T2]
                    if phi1b == 0 and phi2b == 0:
                        continue
                    det = (phi1 * phi2b - phi2 * phi1b) % p
                    if det == 0:
                        continue  # Parallel or coincident
                    det_inv = pow(det, p-2, p)
                    s1 = (((-phi0) * phi2b - (-phi0b) * phi2) * det_inv) % p
                    s2 = ((phi1 * (-phi0b) - phi1b * (-phi0)) * det_inv) % p
                    key = (s1, s2)
                    if key not in rich_points:
                        rich_points[key] = set()
                    rich_points[key].add(idx_T)
                    rich_points[key].add(idx_T2)

            # Find w-rich points
            w_rich = [(k, len(v)) for k, v in rich_points.items() if len(v) >= w]
            if w_rich:
                max_richness = max(r for _, r in w_rich)
                print(f"    w-rich points: {len(w_rich)}, max richness={max_richness}")

                # Verify: these should equal M
                # Each w-rich point with exactly w incident lines → one valid w-subset
                actual_M = 0
                for (s1, s2), incident in rich_points.items():
                    if len(incident) == w:
                        actual_M += 1
                    elif len(incident) > w:
                        print(f"    WARNING: point ({s1},{s2}) has {len(incident)} > w={w} incident")
                if actual_M != M:
                    # Some M might come from coincident lines
                    print(f"    w-rich count={actual_M} vs M={M} (diff={M-actual_M} from coincident)")

    return

# Test
for n, p, w in [(10, 11, 4), (10, 13, 4), (12, 13, 4), (12, 13, 5), (14, 17, 5)]:
    c = w - 2
    if p > n and n - w - c >= 1:
        test_incidence(n, p, w, c)
