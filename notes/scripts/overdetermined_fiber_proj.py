"""
overdetermined_fiber_proj.py — Analyze the projection and fiber structure of V_all.

For d=2 flat parameterized by (s_1, s_2):
- Projection: For how many s_2 values does V_all have a point?
- Fiber: For each active s_2, how many s_1 values?

KEY INSIGHT: If each s_2-fiber is a d=1 problem with M ≤ n/w,
and the projection has ≤ K active s_2 values,
then M ≤ K · n/w. For M = O(1): need K · n/w = O(1).

Also test: after eliminating s_1 between r_0-1 and r_j (j=1,...,w-1),
count how many s_2 have common roots for ALL j.
"""

import itertools
import random
from math import comb
from collections import Counter

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

def companion_step(state, sigma, p):
    w = len(state)
    top = state[w-1]
    new_state = [0] * w
    new_state[0] = (top * pow(-1, w+1, p) * sigma[w-1]) % p
    for j in range(1, w):
        sign = pow(-1, w-j+1, p)
        new_state[j] = (state[j-1] + top * sign * sigma[w-j-1]) % p
    return tuple(new_state)

def compute_remainder(sigma, n, p):
    w = len(sigma)
    state = [0] * w
    state[0] = 1
    for _ in range(n):
        state = list(companion_step(tuple(state), sigma, p))
    return tuple(state)

def univariate_gcd(f, g, p):
    """GCD of univariate polynomials over F_p. Returns degree of GCD."""
    # f, g as lists [a_0, a_1, ...] with a_deg at the end
    f = list(f)
    g = list(g)
    while f and f[-1] % p == 0: f.pop()
    while g and g[-1] % p == 0: g.pop()

    while g:
        if len(f) < len(g):
            f, g = g, f
        # f = f mod g
        while len(f) >= len(g) and g:
            lc_f = f[-1] % p
            lc_g = g[-1] % p
            if lc_g == 0: break
            inv_g = pow(lc_g, p-2, p)
            ratio = (lc_f * inv_g) % p
            shift = len(f) - len(g)
            for i in range(len(g)):
                f[shift + i] = (f[shift + i] - ratio * g[i]) % p
            while f and f[-1] % p == 0: f.pop()
        f, g = g, f

    return len(f) - 1 if f else -1

def analyze_projection(n, p, w, c, num_trials=50):
    """Analyze projection of V_all onto s_2."""
    d = w - c
    k = n - w - c
    D = n - w

    if k < 1 or d != 2:
        return

    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, k={k}, D={D}")
    print(f"  d=1 fiber bound: n/w = {n/w:.1f}")

    random.seed(42)
    max_M = 0
    max_proj = 0
    max_fib = 0

    M_list = []
    proj_sizes = []
    fib_sizes = []

    for trial in range(num_trials):
        # Random flat
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        mat = [[normals[j][i] for i in range(w)] + [offsets[j]] for j in range(c)]
        pivots = []
        for col in range(w):
            if len(pivots) >= c:
                break
            row = len(pivots)
            found = False
            for r in range(row, c):
                if mat[r][col] % p != 0:
                    mat[row], mat[r] = mat[r], mat[row]
                    found = True
                    break
            if not found:
                continue
            inv = pow(mat[row][col], p-2, p)
            for j in range(w+1):
                mat[row][j] = (mat[row][j] * inv) % p
            for r in range(c):
                if r != row and mat[r][col] % p != 0:
                    fac = mat[r][col]
                    for j in range(w+1):
                        mat[r][j] = (mat[r][j] - fac * mat[row][j]) % p
            pivots.append(col)

        if len(pivots) < c:
            continue

        free_vars = [j for j in range(w) if j not in pivots]
        if len(free_vars) != d:
            continue

        a_vals = [0]*w
        b_vals = [[0]*d for _ in range(w)]
        for idx, piv in enumerate(pivots):
            a_vals[piv] = mat[idx][w]
            for fi, fv in enumerate(free_vars):
                b_vals[piv][fi] = (-mat[idx][fv]) % p
        for fi, fv in enumerate(free_vars):
            a_vals[fv] = 0
            b_vals[fv][fi] = 1

        # For each (s_1, s_2), compute remainder and check
        V_all_points = []
        V_01_points = []

        for s2 in range(p):
            for s1 in range(p):
                sigma = tuple((a_vals[j] + s1 * b_vals[j][0] + s2 * b_vals[j][1]) % p for j in range(w))
                rem = compute_remainder(sigma, n, p)

                if rem[0] == 1 and rem[1] == 0:
                    V_01_points.append((s1, s2))
                if rem == (1,) + (0,)*(w-1):
                    V_all_points.append((s1, s2))

        M = len(V_all_points)

        # Projection analysis
        proj_all = Counter(s2 for _, s2 in V_all_points)  # s2 -> count of s1
        proj_01 = Counter(s2 for _, s2 in V_01_points)

        active_s2_all = len(proj_all)  # Number of active s_2 values
        active_s2_01 = len(proj_01)
        max_fiber_all = max(proj_all.values()) if proj_all else 0
        max_fiber_01 = max(proj_01.values()) if proj_01 else 0

        M_list.append(M)
        proj_sizes.append(active_s2_all)
        fib_sizes.append(max_fiber_all)

        if M > max_M:
            max_M = M
        if active_s2_all > max_proj:
            max_proj = active_s2_all
        if max_fiber_all > max_fib:
            max_fib = max_fiber_all

        if trial < 5 or M >= 3:
            print(f"  Trial {trial}: M={M}, |V_01|={len(V_01_points)}")
            print(f"    Proj(V_all): {active_s2_all} active s_2, max fiber={max_fiber_all}")
            print(f"    Proj(V_01):  {active_s2_01} active s_2, max fiber={max_fiber_01}")
            if V_all_points:
                print(f"    Points: {V_all_points[:10]}")

            # Also: for active s_2, check if the s_1 fiber problem is "pinned"
            if M > 0:
                # For each s_2, check the w-subsets
                subsets_idx = list(itertools.combinations(range(n), w))
                for s2_val, count in sorted(proj_all.items()):
                    s1_vals = [s1 for s1, s2 in V_all_points if s2 == s2_val]
                    # Find the actual w-subsets for each (s1, s2_val)
                    B_list = []
                    for s1 in s1_vals:
                        sigma = tuple((a_vals[j] + s1 * b_vals[j][0] + s2_val * b_vals[j][1]) % p for j in range(w))
                        for B_idx in subsets_idx:
                            B = tuple(L[i] for i in B_idx)
                            if elem_sym(B, p) == sigma:
                                B_list.append(B_idx)
                                break
                    # Check pairwise overlap (pinning)
                    if len(B_list) > 1:
                        common = set(B_list[0])
                        for B in B_list[1:]:
                            common &= set(B)
                        print(f"      s_2={s2_val}: {count} points, subsets={B_list}, common={common}")
                    elif B_list:
                        print(f"      s_2={s2_val}: {count} point, subset={B_list[0]}")

    # Summary statistics
    print(f"\n  Summary ({num_trials} trials):")
    print(f"    max M = {max_M}")
    print(f"    max |proj(V_all)| = {max_proj}")
    print(f"    max fiber size = {max_fib}")
    print(f"    M distribution: {Counter(M_list)}")
    print(f"    M ≤ proj × max_fiber: {max_proj * max_fib}")
    print(f"    avg M = {sum(M_list)/len(M_list):.2f}")

# Test cases
for n, p, w in [(10, 11, 4), (10, 13, 4), (10, 31, 4),
                (12, 13, 4), (12, 13, 5), (14, 17, 5)]:
    c = w - 2
    k = n - w - c
    if k >= 1:
        analyze_projection(n, p, w, c, num_trials=30)
