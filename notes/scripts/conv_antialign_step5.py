#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Step 5: Incidence geometry perspective.

KEY REALIZATION from Steps 1-4:
- Cauchy-Schwarz on character sums gives M ≤ √N (useless)
- Need INCIDENCE GEOMETRY: bound max|σ-image ∩ V| for (w-c)-flats V

For conds=2, w=3: V is a LINE in F_p^3. Question: max collinear σ-images?
For conds=2, w=4: V is a 2-PLANE in F_p^4. Question: max coplanar σ-images?

The σ-image has algebraic structure: σ_j = e_j(ω^{i_1},...,ω^{i_w}).
If the σ-image is a "low-degree" curve/surface, Bézout bounds the intersection.

EXPERIMENTS:
  E1. For w=3, conds=2: max # collinear σ-images (exhaustive)
  E2. For w=4, conds=2: max # coplanar σ-images (sampled)
  E3. Algebraic degree of the σ-image variety
  E4. Stepanov-type construction: auxiliary polynomial
"""

import itertools
import random
from collections import Counter

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g
def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0: factors.add(d); n //= d
        d += 1
    if n > 1: factors.add(n)
    return factors
def find_omega(p, n):
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)
def elem_sym(B, omega, p):
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    e = [0]*(w+1); e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1]*r) % p
    return tuple(e[1:])

def max_collinear(points, p):
    """Max number of points from a list that are collinear in F_p^d."""
    if len(points) <= 2:
        return len(points)
    max_on = 2
    n_pts = len(points)
    for i in range(n_pts):
        for j in range(i+1, n_pts):
            # Direction vector
            d = tuple((points[j][k] - points[i][k]) % p for k in range(len(points[0])))
            count = 2
            for k2 in range(j+1, n_pts):
                d2 = tuple((points[k2][l] - points[i][l]) % p for l in range(len(points[0])))
                # Check collinear: d2 = λ*d for some λ
                # Find λ from first nonzero d component
                lam = None
                collinear = True
                for l in range(len(d)):
                    if d[l] != 0:
                        if lam is None:
                            lam = d2[l] * pow(d[l], p-2, p) % p
                        elif d2[l] != (lam * d[l]) % p:
                            collinear = False
                            break
                    elif d2[l] != 0:
                        collinear = False
                        break
                if collinear:
                    count += 1
            max_on = max(max_on, count)
    return max_on

def max_coplanar(points, p, dim=2, n_sample=10000):
    """Estimate max # points on a dim-flat in F_p^d (sampled)."""
    if len(points) <= dim+1:
        return len(points)
    w = len(points[0])
    max_on = 0

    for _ in range(n_sample):
        # Pick dim+1 random points, define the flat
        basis_idx = random.sample(range(len(points)), dim+1)
        origin = points[basis_idx[0]]
        dirs = [tuple((points[basis_idx[j+1]][k] - origin[k]) % p for k in range(w))
                for j in range(dim)]

        # Check all points
        count = 0
        for pt in points:
            diff = tuple((pt[k] - origin[k]) % p for k in range(w))
            # Check if diff is in span of dirs
            # Solve: diff = Σ a_j dirs_j (mod p) — dim equations in dim unknowns
            # Build matrix and check
            mat = [list(dirs[j]) for j in range(dim)]
            # Gaussian elimination to check if diff is in column space
            # Actually, we need: is diff in the span of dirs?
            # System: [dirs[0]^T | dirs[1]^T | ... ] a = diff^T
            # This is a w × dim system, overdetermined for w > dim
            if in_span(diff, dirs, p, w):
                count += 1
        max_on = max(max_on, count)

    return max_on

def in_span(vec, dirs, p, w):
    """Check if vec is in the span of dirs over F_p."""
    dim = len(dirs)
    # Augmented matrix [dirs | vec], each column is a dir/vec
    # We need to solve Σ a_j dirs[j][i] = vec[i] for all i
    # Build as dim × (w) system? No, it's w equations in dim unknowns
    # Build as matrix M (w × dim), solve Ma = v

    M = [[dirs[j][i] for j in range(dim)] for i in range(w)]
    v = [vec[i] for i in range(w)]

    # Row reduce [M | v]
    aug = [list(M[i]) + [v[i]] for i in range(w)]
    pivot_row = 0
    for col in range(dim):
        found = -1
        for row in range(pivot_row, w):
            if aug[row][col] % p != 0:
                found = row
                break
        if found == -1:
            continue
        aug[pivot_row], aug[found] = aug[found], aug[pivot_row]
        scale = pow(aug[pivot_row][col], p-2, p)
        aug[pivot_row] = [(x * scale) % p for x in aug[pivot_row]]
        for row in range(w):
            if row != pivot_row and aug[row][col] % p != 0:
                factor = aug[row][col]
                aug[row] = [(aug[row][j] - factor * aug[pivot_row][j]) % p for j in range(dim+1)]
        pivot_row += 1

    # Check consistency: for rows with all-zero LHS, RHS must be zero
    for row in range(pivot_row, w):
        if aug[row][dim] % p != 0:
            return False
    return True

def experiment_1_max_collinear(cases):
    """E1: Max collinear σ-images for w=3."""
    print("=== E1: Max collinear σ-images ===\n")

    for n, k, w, primes in cases:
        if w != 3:
            continue
        conds = n - k - w
        if conds < 2:
            continue

        for p in primes:
            omega = find_omega(p, n)
            points = [elem_sym(B, omega, p) for B in itertools.combinations(range(n), w)]
            N = len(points)

            print(f"n={n}, k={k}, w={w}, p={p}: N={N}, conds={conds}")
            mc = max_collinear(points, p)
            print(f"  Max collinear = {mc}")
            print(f"  N/p^c = {N/p**conds:.2f}")
            print()

def experiment_2_max_coplanar(cases):
    """E2: Max coplanar σ-images for w≥4."""
    print("=== E2: Max coplanar σ-images ===\n")

    for n, k, w, primes in cases:
        if w < 4:
            continue
        conds = n - k - w
        if conds < 2:
            continue

        for p in primes:
            omega = find_omega(p, n)
            points = [elem_sym(B, omega, p) for B in itertools.combinations(range(n), w)]
            N = len(points)

            print(f"n={n}, k={k}, w={w}, p={p}: N={N}, conds={conds}")
            # For conds=2, dim of flat = w-2
            flat_dim = w - conds
            mc = max_coplanar(points, p, dim=flat_dim, n_sample=5000)
            print(f"  Max on {flat_dim}-flat = {mc} (sampled)")
            print(f"  N/p^c = {N/p**conds:.2f}")
            print()

def experiment_3_degree(cases):
    """E3: Algebraic structure of σ-image.
    For w=3: σ = (e_1, e_2, e_3) of {ω^{i_1}, ω^{i_2}, ω^{i_3}}.
    e_1 = ω^{i_1} + ω^{i_2} + ω^{i_3}
    e_2 = ω^{i_1}ω^{i_2} + ω^{i_1}ω^{i_3} + ω^{i_2}ω^{i_3}
    e_3 = ω^{i_1}ω^{i_2}ω^{i_3}

    Let x = ω^{i_1}, y = ω^{i_2}, z = ω^{i_3}. Then:
    σ_1 = x+y+z, σ_2 = xy+xz+yz, σ_3 = xyz.

    The map (x,y,z) ↦ (σ_1,σ_2,σ_3) is the Vieta map.
    Its image (for x,y,z ∈ L) lies on: discriminant conditions, etc.

    For a line ℓ: σ_1 = a + bt, σ_2 = c + dt, (and σ_3 determined or free)
    The pre-image in (x,y,z) satisfies polynomial equations.
    """
    print("=== E3: Algebraic degree of σ-image ===\n")

    for n, k, w, primes in cases:
        if w != 3:
            continue
        p = primes[0]
        omega = find_omega(p, n)

        print(f"n={n}, w={w}, p={p}")
        print(f"  σ = (e_1, e_2, e_3) of (ω^i1, ω^i2, ω^i3)")
        print(f"  Vieta map from L^3/S_3 → F_p^3")
        print(f"  L = {{1, ω, ..., ω^{{n-1}}}}, |L| = {n}")

        # Count: how many (σ_1, σ_3) pairs determine σ_2?
        # If σ-image is a curve in F_p^3, projection to (σ_1,σ_3) should be ~N-to-1
        points = [elem_sym(B, omega, p) for B in itertools.combinations(range(n), w)]
        N = len(points)

        # Project to (σ_1, σ_3)
        proj_13 = {}
        for pt in points:
            key = (pt[0], pt[2])
            proj_13.setdefault(key, []).append(pt[1])

        fibers = [len(v) for v in proj_13.values()]
        print(f"  N = {N}, # distinct (σ_1,σ_3) = {len(proj_13)}")
        print(f"  Fiber sizes: min={min(fibers)}, max={max(fibers)}, avg={N/len(proj_13):.2f}")

        # Project to (σ_1, σ_2)
        proj_12 = {}
        for pt in points:
            key = (pt[0], pt[1])
            proj_12.setdefault(key, []).append(pt[2])

        fibers = [len(v) for v in proj_12.values()]
        print(f"  # distinct (σ_1,σ_2) = {len(proj_12)}")
        print(f"  Fiber sizes: min={min(fibers)}, max={max(fibers)}, avg={N/len(proj_12):.2f}")

        # If σ is injective, # distinct (σ_1,σ_2,σ_3) = N
        distinct_triples = len(set(points))
        print(f"  # distinct σ = {distinct_triples} (injective: {distinct_triples == N})")

        # Check: can we find a polynomial relation F(σ_1, σ_2, σ_3) = 0?
        # If σ-image is contained in a surface of degree d, at most d × (line degree) points on a line
        # For the Vieta map: Newton's identity gives p_k = power sum in terms of σ_j
        # And x^n = 1 gives Σ x_i^n = sum of n-th powers = n (or 0 if char divides n)
        # p_1 = σ_1, p_2 = σ_1^2 - 2σ_2, p_3 = σ_1^3 - 3σ_1σ_2 + 3σ_3
        # p_n = Σ ω^{n·i_j} = w (since ω^n = 1 and we have w roots)
        # So p_n(σ_1,...,σ_w) = w gives a polynomial relation of degree n in σ_j

        print(f"\n  Newton identity: p_n(σ) = w gives degree-{n} surface containing σ-image")
        print(f"  By Bézout: line ∩ surface ≤ {n} points")
        print(f"  So max collinear σ-images ≤ {n}")

        # But wait — there are MORE Newton identities: p_1 = σ_1 (trivial)
        # p_2 = σ_1^2 - 2σ_2 (determines σ_2 from σ_1 and p_2)
        # p_k for k dividing n give additional relations

        # For w=3 and x,y,z ∈ L (order n):
        # x^n = y^n = z^n = 1
        # p_n = x^n + y^n + z^n = 3 (in char > 3)
        # Newton: p_n = σ_1 p_{n-1} - σ_2 p_{n-2} + σ_3 p_{n-3}
        # This gives a SINGLE polynomial relation of degree n

        # But also p_{n-1}, p_{n-2}, etc. give MORE relations
        # Total: we have n relations p_k(σ) = Σ ω^{k·i_j} for k=1,...,n
        # But only 3 free variables (σ_1,σ_2,σ_3)
        # So the σ-image is the intersection of many degree-k surfaces

        # The LOWEST degree non-trivial relation:
        # p_2 = σ_1^2 - 2σ_2 gives σ_2 = (σ_1^2 - p_2)/2
        # But p_2 = Σ ω^{2i_j} depends on B, not just σ(B)!
        # p_2 is a FUNCTION of B that's NOT captured by σ alone (for w≥3)

        # Actually, for the Vieta map, the σ_j ARE the elem syms,
        # and p_k ARE determined by σ_j (via Newton). So p_k is a polynomial in σ.
        # The constraint is: the SPECIFIC p_k values for subsets of roots of unity.

        # For subsets of L: p_k(B) = Σ_{i∈B} ω^{ik}
        # This depends on B (NOT just on σ(B)). But σ(B) determines B (injectivity).
        # So p_k is determined by σ, but it's a complicated function.

        # The algebraic relation: there's NO polynomial F(σ_1,σ_2,σ_3) = 0 for all B
        # (since σ is injective → σ-image is 0-dimensional → no common variety)

        # What about the DEGREE of interpolation?
        # Given N = C(n,3) points in F_p^3, the vanishing ideal has generators of degree O(N^{1/3})

        # For a line ℓ parameterized as σ = a + tb:
        # |ℓ ∩ σ-image| ≤ degree of the vanishing polynomial of σ-image restricted to ℓ
        # This polynomial has degree ≤ N (trivially), but might be much smaller

        # STEPANOV: construct F(t) vanishing on {t : a+tb ∈ σ-image}
        # If deg F = D, then |ℓ ∩ σ-image| ≤ D

        # The ELEMENTARY construction: F(t) = Π_{B : σ(B) ∈ ℓ} (t - t_B)
        # has degree = |ℓ ∩ σ-image|. Not helpful.

        # Stepanov trick: construct F with degree D < N using AUXILIARY vanishing conditions
        # E.g., F vanishes to order 2 at each σ(B) → D ≥ 2M but F has form with D = O(√N)

        print(f"\n  For a line: intersection ≤ N = {N} trivially")
        print(f"  Stepanov method might give: ≤ O(N^{{1/2}}) = {int(N**0.5)}")
        print(f"  Newton identity gives: ≤ {n} (degree of p_n relation)")
        print()

def main():
    cases = [
        # (n, k, w, [primes])
        (10, 5, 3, [11, 31, 41]),
        (12, 6, 4, [13, 37]),
        (14, 7, 5, [29]),
        (16, 8, 5, [17]),
    ]

    experiment_1_max_collinear(cases)
    experiment_2_max_coplanar(cases)
    experiment_3_degree(cases)

if __name__ == '__main__':
    main()
