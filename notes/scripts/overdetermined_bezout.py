"""
overdetermined_bezout.py — Attack on Gap 1 via overdetermined Bézout reduction.

GOAL: Show that w equations of degree D = n-w in d variables over F_p
have at most D^d / p^{w-d} + O(sqrt) solutions, not D^d.

APPROACH:
1. For d=2 flat parameterized by (s_1, s_2):
   σ_j = a_j + s_1 b_j1 + s_2 b_j2
2. Companion matrix recurrence gives r_0(s), r_1(s), ..., r_{w-1}(s)
   each of degree ≤ D = n-w
3. Valid w-subsets ↔ (r_0-1, r_1, ..., r_{w-1}) = 0
4. Check: are r_0-1 and r_1 coprime in F_p[s_1, s_2]?
5. If yes: |V(r_0-1, r_1)| ≤ D^2 by Bézout
6. Then: |V(r_0-1, r_1) ∩ V(r_2)| ≤ ??? (need Weil-type bound)
"""

import itertools
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
    """Elementary symmetric polynomials of B in F_p."""
    w = len(B)
    e = [0] * (w + 1)
    e[0] = 1
    for b in B:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * b) % p
    return tuple(e[1:])

def companion_step(state, sigma, p):
    """One step of companion matrix recurrence: multiply by x mod Λ(x).

    Λ(x) = x^w - σ_1 x^{w-1} + σ_2 x^{w-2} - ... + (-1)^w σ_w
    x^w ≡ σ_1 x^{w-1} - σ_2 x^{w-2} + ... + (-1)^{w+1} σ_w

    state = (a_0, a_1, ..., a_{w-1}) represents a_0 + a_1 x + ... + a_{w-1} x^{w-1}
    """
    w = len(state)
    top = state[w-1]  # coefficient of x^{w-1}
    new_state = [0] * w
    # b_0 = top * (-1)^{w+1} * σ_w
    new_state[0] = (top * pow(-1, w+1, p) * sigma[w-1]) % p
    for j in range(1, w):
        # b_j = a_{j-1} + top * (-1)^{w-j+1} * σ_{w-j}
        sign = pow(-1, w-j+1, p)
        new_state[j] = (state[j-1] + top * sign * sigma[w-j-1]) % p  # σ indexed from 0
        # Wait: sigma[0] = σ_1, sigma[1] = σ_2, ..., sigma[w-1] = σ_w
        # We need σ_{w-j}, which is sigma[w-j-1]
    return tuple(new_state)

def compute_remainder(sigma, n, p):
    """Compute x^n mod Λ(x) where Λ has elementary symmetric coefficients sigma.

    Returns (r_0, r_1, ..., r_{w-1}) such that
    x^n ≡ r_0 + r_1 x + ... + r_{w-1} x^{w-1} mod Λ(x)

    Valid w-subset ↔ (r_0, r_1, ..., r_{w-1}) = (1, 0, ..., 0)
    """
    w = len(sigma)
    state = [0] * w
    state[0] = 1  # x^0 = 1
    for _ in range(n):
        state = list(companion_step(tuple(state), sigma, p))
    return tuple(state)

def analyze_overdetermined(n, p, w, c, num_trials=20):
    """Analyze the overdetermined system for d=2 flats."""
    d = w - c
    k = n - w - c
    D = n - w  # degree bound

    if k < 1 or d < 2:
        return

    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    # Precompute all w-subsets and their σ-images
    subsets_idx = list(itertools.combinations(range(n), w))
    sigma_map = {}  # sigma -> list of B indices
    for B_idx in subsets_idx:
        B = tuple(L[i] for i in B_idx)
        sig = elem_sym(B, p)
        if sig not in sigma_map:
            sigma_map[sig] = []
        sigma_map[sig].append(B_idx)

    print(f"\n{'='*70}")
    print(f"n={n}, p={p}, w={w}, c={c}, d={d}, k={k}, D={D}")
    print(f"  Bézout bound: D^d = {D**d}")
    print(f"  Overdetermined target: D^w/p^c = {D**w / p**c:.2f}")
    print(f"  KST bound: C(n,d)/C(w,d) = {comb(n,d)/comb(w,d):.1f}")
    print(f"  Total subsets: {len(subsets_idx)}, distinct σ: {len(sigma_map)}")

    random.seed(42)

    for trial in range(num_trials):
        # Generate an RS-compatible flat from a random center
        # Random polynomial f of degree < k
        coeffs = [random.randint(0, p-1) for _ in range(k)]
        f_vals = []
        for alpha in L:
            val = 0
            for j in range(k-1, -1, -1):
                val = (val * alpha + coeffs[j]) % p
            f_vals.append(val)

        # Syndrome = DFT of f on [k, n-k-1] window
        # Actually, the syndrome determines the flat.
        # The flat is: {σ : T_s · e = b_s} where s is the syndrome

        # For the companion matrix approach, we need the parameterization
        # of the flat. Let's do it differently:
        #
        # The compatible σ satisfy c linear conditions.
        # Find these conditions from the Vandermonde structure.

        # Alternative: just enumerate all (s_1, s_2) ∈ F_p^2 and for each,
        # compute σ(s) = a + s_1 b_1 + s_2 b_2, then check x^n mod Λ(x) = (1,0,...,0)

        # First, find the flat parameterization.
        # Pick c random conditions on σ = (σ_1, ..., σ_w)
        # For RS-compatibility, use actual syndrome conditions.

        # Syndrome from f: s_j = sum_{i=0}^{n-1} f(L_i) L_i^j for j = k, ..., n-k-1
        # But actually, the conditions on σ come from the key equation:
        # S(x) · Λ(x) ≡ Ω(x) mod x^{n-k}
        # For the error set B (weight w), Λ(x) = prod_{b in B} (1 - bx) (reciprocal form)
        # or Λ(x) = x^w - σ_1 x^{w-1} + ... (standard form)

        # Let me use a simpler approach: pick c random normal vectors and offsets
        # to define the flat, then use companion matrix.
        normals = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(c)]
        offsets = [random.randint(0, p-1) for _ in range(c)]

        # Row-reduce to get parameterization
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

        # Parameterization: σ_j = a_j + Σ_i s_i b_{j,i}
        a = [0]*w
        b = [[0]*d for _ in range(w)]
        for idx, piv in enumerate(pivots):
            a[piv] = mat[idx][w]
            for fi, fv in enumerate(free_vars):
                b[piv][fi] = (-mat[idx][fv]) % p
        for fi, fv in enumerate(free_vars):
            a[fv] = 0
            b[fv][fi] = 1

        # Now enumerate all (s_1, s_2) ∈ F_p^d and check companion matrix condition
        # For d=2: iterate over F_p^2

        # For each point, compute σ(s) and then x^n mod Λ(x)
        V_r0 = set()  # zeros of r_0 - 1
        V_r1 = set()  # zeros of r_1
        V_r = [set() for _ in range(w)]  # zeros of each r_i (shifted)
        V_all = set()  # zeros of all conditions

        for s1 in range(p):
            for s2 in range(p):
                s = (s1, s2) if d == 2 else (s1,)
                # Compute σ(s)
                sigma = tuple((a[j] + sum(s[i] * b[j][i] for i in range(d))) % p for j in range(w))

                # Compute x^n mod Λ(x) via companion matrix
                remainder = compute_remainder(sigma, n, p)

                # Check each condition
                if remainder[0] == 1:
                    V_r0.add((s1, s2))
                if remainder[1] == 0:
                    V_r1.add((s1, s2))

                for j in range(w):
                    target = 1 if j == 0 else 0
                    if remainder[j] == target:
                        V_r[j].add((s1, s2))

                # Check all conditions
                if remainder[0] == 1 and all(remainder[j] == 0 for j in range(1, w)):
                    V_all.add((s1, s2))

        M = len(V_all)

        # Intersection analysis
        V_01 = V_r0 & V_r1  # V(r_0-1) ∩ V(r_1)

        if trial < 5 or M > 0:
            print(f"\n  Trial {trial}: M={M}")
            print(f"    |V(r_0-1)| = {len(V_r0)},  expected ≈ p^{d-1}·D = {p**(d-1) * D}")
            print(f"    |V(r_1)|   = {len(V_r1)},  expected ≈ p^{d-1}·D = {p**(d-1) * D}")
            print(f"    |V(r_0-1) ∩ V(r_1)| = {len(V_01)},  Bézout bound = {D**d}")

            # Progressive intersection
            running = V_r0.copy()
            sizes = [len(running)]
            for j in range(1, w):
                running = running & V_r[j]
                sizes.append(len(running))
                print(f"    |V(r_0-1,...,r_{j})| = {len(running)}")

            # Summary: total reduction
            print(f"    Reduction: {sizes[0]} → {sizes[-1]} (factor {sizes[0]/max(sizes[-1],1):.1f}x)")

            # Key test: is |V_01| close to D^2 or much smaller?
            if len(V_01) > 0 and w > 2:
                V_012 = V_01 & V_r[2]
                factor = len(V_012) / len(V_01)
                print(f"    Reduction r_2|V_01: {len(V_01)}→{len(V_012)} ({factor:.4f}), D/p = {D/p:.4f}")

                if w > 3 and len(V_012) > 0:
                    V_0123 = V_012 & V_r[3]
                    factor2 = len(V_0123) / len(V_012)
                    print(f"    Reduction r_3|V_012: {len(V_012)}→{len(V_0123)} ({factor2:.4f}), D/p = {D/p:.4f}")

def verify_companion(n, p, w):
    """Verify companion matrix gives correct results by comparing with direct σ computation."""
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\nVerification: n={n}, p={p}, w={w}")

    # Pick a random w-subset
    random.seed(123)
    B_idx = tuple(sorted(random.sample(range(n), w)))
    B = tuple(L[i] for i in B_idx)
    sigma = elem_sym(B, p)

    print(f"  B = {B_idx}, σ = {sigma}")

    # Check: does Λ(x) = prod(x - b) for b in B divide x^n - 1?
    # Since B ⊂ L and L consists of n-th roots of unity, yes.

    # Compute x^n mod Λ via companion matrix
    remainder = compute_remainder(sigma, n, p)
    print(f"  x^n mod Λ = {remainder}")
    print(f"  Expected: (1, 0, ..., 0) → {remainder == (1,) + (0,)*(w-1)}")

    # Also check a random (non-subset) sigma
    bad_sigma = tuple(random.randint(0, p-1) for _ in range(w))
    bad_rem = compute_remainder(bad_sigma, n, p)
    print(f"  Random σ = {bad_sigma}")
    print(f"  x^n mod Λ = {bad_rem}")
    print(f"  Is (1,0,...,0)? {bad_rem == (1,) + (0,)*(w-1)}")

# Verify the companion matrix computation
verify_companion(10, 11, 4)

# Main analysis
print("\n" + "="*70)
print("OVERDETERMINED BÉZOUT REDUCTION ANALYSIS")
print("="*70)

# d=2 cases
for n, p, w in [(10, 11, 4), (10, 13, 4), (10, 31, 4), (12, 13, 4), (12, 13, 5), (14, 17, 5)]:
    c = w - 2  # d=2
    if n - w - c >= 1:
        analyze_overdetermined(n, p, w, c, num_trials=30)

# d=3 case
for n, p, w in [(10, 11, 5), (12, 13, 5)]:
    c = w - 3  # d=3
    if n - w - c >= 1:
        analyze_overdetermined(n, p, w, c, num_trials=10)
