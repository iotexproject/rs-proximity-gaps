"""
Incidence Bound for σ-image on d-flats.

THEOREM: For L ⊂ F_p* of order n, w-element subsets, and any d-flat V in F_p^w:
  M = |{B ∈ C(L,w) : e(B) ∈ V}| ≤ C(n,d) / C(w,d)

PROOF IDEA: On a d-flat parametrized by t ∈ F_p^d, each β ∈ L gives a hyperplane
H_β in F_p^d (the condition "β is root of Λ_t"). At any point t: at most w
hyperplanes pass through it (since deg Λ = w). Each valid w-subset B determines
a unique t(B) and contributes C(w,d) "GP d-subsets". Different valid B's have
DISJOINT GP d-subsets. Total ≤ C(n,d). So M·C(w,d) ≤ C(n,d).

This script verifies the bound for small parameters and analyzes degeneracies.
"""

from math import comb, gcd
from itertools import combinations
import sys

def find_primitive_root(p):
    """Find a primitive root mod p."""
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p - 1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p - 1:
            return g
    return None

def get_subgroup(p, n):
    """Get multiplicative subgroup of order n in F_p*."""
    if (p - 1) % n != 0:
        return None
    g = find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    return [pow(omega, i, p) for i in range(n)]

def elem_sym(subset, p):
    """Compute elementary symmetric polynomials e_1,...,e_w of subset mod p."""
    w = len(subset)
    # e_j = sum of products of j elements
    e = [0] * (w + 1)
    e[0] = 1
    for x in subset:
        # Update from high to low to avoid using updated values
        for j in range(min(len(e) - 1, w), 0, -1):
            e[j] = (e[j] + e[j-1] * x) % p
    return tuple(e[1:])  # (e_1, ..., e_w)

def compute_sigma_image(L, w, p):
    """Compute all σ-image points: {e(B) : B ∈ C(L,w)}."""
    sigma_pts = {}
    for B in combinations(L, w):
        sigma = elem_sym(B, p)
        sigma_pts[sigma] = B
    return sigma_pts

def toeplitz_flat(syndrome, w, p):
    """
    Compute the Toeplitz flat V_c for a given syndrome.

    Syndrome s = (s_0, s_1, ..., s_{n-k-1}).
    Toeplitz conditions: Σ_{j=0}^w (-1)^j σ_j s_{w+ℓ-j} = 0 for ℓ=0,...,c-1
    where σ_0 = 1.

    Returns (offset, basis) where the flat is {offset + Σ t_j basis[j]}.
    """
    c = len(syndrome) - w  # c = (n-k) - w ... wait
    # Actually: syndrome has length n-k. The Toeplitz conditions are c conditions
    # on σ_1,...,σ_w where c = n-k-w.
    nk = len(syndrome)
    c_conds = nk - w
    if c_conds <= 0:
        return None  # No conditions, flat = all of F_p^w

    # Build the c × w Toeplitz matrix T and the c × 1 vector b
    # Condition ℓ (0-indexed): Σ_{j=1}^w (-1)^j σ_j s_{w+ℓ-j} = -s_{w+ℓ}
    # (moving the σ_0 = 1 term to RHS)
    T = []
    b = []
    for ell in range(c_conds):
        row = []
        for j in range(1, w + 1):
            idx = w + ell - j
            if 0 <= idx < nk:
                coeff = ((-1) ** j * syndrome[idx]) % p
            else:
                coeff = 0
            row.append(coeff)
        T.append(row)
        rhs = (-syndrome[w + ell]) % p if (w + ell) < nk else 0
        b.append(rhs)

    # Solve T σ = b over F_p using Gaussian elimination
    # Returns (particular solution, null space basis)
    return solve_linear_system(T, b, w, p)

def solve_linear_system(A, b, nvars, p):
    """Solve A x = b over F_p. Returns (particular_sol, null_basis)."""
    m = len(A)
    n = nvars
    # Augmented matrix [A | b]
    aug = [(row[:] + [b[i]]) for i, row in enumerate(A)]

    pivot_cols = []
    row_idx = 0
    for col in range(n):
        # Find pivot
        found = -1
        for r in range(row_idx, m):
            if aug[r][col] % p != 0:
                found = r
                break
        if found == -1:
            continue
        # Swap
        aug[row_idx], aug[found] = aug[found], aug[row_idx]
        # Scale pivot row
        inv = pow(aug[row_idx][col], p - 2, p)
        aug[row_idx] = [(x * inv) % p for x in aug[row_idx]]
        # Eliminate
        for r in range(m):
            if r != row_idx and aug[r][col] % p != 0:
                factor = aug[r][col]
                aug[r] = [(aug[r][j] - factor * aug[row_idx][j]) % p for j in range(n + 1)]
        pivot_cols.append(col)
        row_idx += 1

    # Check consistency
    for r in range(row_idx, m):
        if aug[r][n] % p != 0:
            return None  # Inconsistent

    # Particular solution
    x0 = [0] * n
    for i, col in enumerate(pivot_cols):
        x0[col] = aug[i][n] % p

    # Null space basis
    free_cols = [c for c in range(n) if c not in pivot_cols]
    basis = []
    for fc in free_cols:
        v = [0] * n
        v[fc] = 1
        for i, col in enumerate(pivot_cols):
            v[col] = (-aug[i][fc]) % p
        basis.append(v)

    return (x0, basis)

def flat_points(offset, basis, p):
    """Enumerate all points on a d-flat over F_p."""
    d = len(basis)
    w = len(offset)

    if d == 0:
        return [tuple(x % p for x in offset)]

    points = []
    # Enumerate all t ∈ F_p^d
    def recurse(depth, current):
        if depth == d:
            pt = tuple((offset[j] + sum(current[i] * basis[i][j] for i in range(d))) % p for j in range(w))
            points.append(pt)
            return
        for t in range(p):
            current.append(t)
            recurse(depth + 1, current)
            current.pop()

    recurse(0, [])
    return points

def hyperplane_coeffs(beta, offset, basis, p):
    """
    For β ∈ L: the condition Λ_t(β) = 0 gives a hyperplane in t-space.
    Λ_t(x) = x^w + Σ_{j=1}^w (-1)^j σ_j(t) x^{w-j}
    where σ_j(t) = offset_j + Σ_i t_i basis[i][j-1] (0-indexed: offset[j-1], basis[i][j-1])

    Returns (a_1,...,a_d, c) such that a·t = c is the hyperplane condition.
    """
    w = len(offset)
    d = len(basis)

    # Λ(β) = β^w + Σ_{j=1}^w (-1)^j σ_j β^{w-j}
    # = β^w + Σ_{j=1}^w (-1)^j (offset[j-1] + Σ_i t_i basis[i][j-1]) β^{w-j}
    # = [β^w + Σ_j (-1)^j offset[j-1] β^{w-j}] + Σ_i t_i [Σ_j (-1)^j basis[i][j-1] β^{w-j}]
    # = c0 + Σ_i t_i a_i = 0
    # So: Σ_i a_i t_i = -c0

    beta_pows = [1]
    for _ in range(w):
        beta_pows.append((beta_pows[-1] * beta) % p)

    # c0 = β^w + Σ_{j=1}^w (-1)^j offset[j-1] β^{w-j}
    c0 = beta_pows[w]
    for j in range(1, w + 1):
        sign = pow(-1, j, p)  # (-1)^j mod p
        c0 = (c0 + sign * offset[j-1] * beta_pows[w-j]) % p

    # a_i = Σ_{j=1}^w (-1)^j basis[i][j-1] β^{w-j}
    a = []
    for i in range(d):
        ai = 0
        for j in range(1, w + 1):
            sign = pow(-1, j, p)
            ai = (ai + sign * basis[i][j-1] * beta_pows[w-j]) % p
        a.append(ai)

    # Hyperplane: Σ a_i t_i = -c0
    rhs = (-c0) % p
    return (a, rhs)

def check_coincident(L, offset, basis, p):
    """Check for coincident hyperplanes in the arrangement."""
    d = len(basis)
    if d < 2:
        return {}

    # For d=2: two lines are coincident/parallel if (a1,a2) are proportional
    # Direction = [a1 : a2] in P^1
    directions = {}
    for beta in L:
        a, c = hyperplane_coeffs(beta, offset, basis, p)
        # Normalize direction
        if a[0] != 0:
            inv = pow(a[0], p-2, p)
            key = tuple((x * inv) % p for x in a)
        elif a[1] != 0:
            inv = pow(a[1], p-2, p)
            key = tuple((x * inv) % p for x in a)
        else:
            key = tuple(a)  # zero vector

        if key not in directions:
            directions[key] = []
        directions[key].append(beta)

    return directions

def count_M_on_flat(sigma_image, offset, basis, p):
    """Count M = |σ-image ∩ flat|."""
    d = len(basis)
    w = len(offset)
    count = 0
    matching = []

    for sigma, B in sigma_image.items():
        # Check if sigma is on the flat: sigma = offset + Σ t_j basis[j]
        # This means: sigma - offset is in the span of basis
        diff = tuple((sigma[j] - offset[j]) % p for j in range(w))

        if d == 0:
            if all(x == 0 for x in diff):
                count += 1
                matching.append(B)
        else:
            # Solve for t: basis^T t = diff (basis is d × w, need d equations)
            # Use the augmented system
            aug = []
            for i in range(w):
                row = [basis[j][i] for j in range(d)] + [diff[i]]
                aug.append(row)

            # Check if consistent
            result = solve_linear_system(
                [row[:-1] for row in aug],
                [row[-1] for row in aug],
                d, p
            )
            if result is not None:
                x0, null = result
                if len(null) == 0:  # unique solution
                    # Verify
                    check = tuple((offset[j] + sum(x0[i] * basis[i][j] for i in range(d))) % p for j in range(w))
                    if check == sigma:
                        count += 1
                        matching.append(B)

    return count, matching

def run_experiment(n, k, p, w_target=None):
    """Run the incidence bound experiment for given parameters."""
    L = get_subgroup(p, n)
    if L is None:
        print(f"  No subgroup of order {n} in F_{p}*")
        return

    if w_target is None:
        # Johnson radius
        import math
        w_target = int(n - math.sqrt(n * k))

    w = w_target
    c = n - k - w
    d = w - c

    if c <= 0 or d <= 0:
        print(f"  Invalid: c={c}, d={d}")
        return

    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, p={p}, w={w}, c={c}, d={d}")
    print(f"C(n,w)={comb(n,w)}, C(n,d)/C(w,d)={comb(n,d)/comb(w,d):.1f}")
    print(f"Bezout=(n-w+1)^d={(n-w+1)**d}")
    print(f"Density=C(n,w)/p^c={comb(n,w)/p**c:.4f}")
    print(f"{'='*60}")

    # Compute σ-image
    sigma_image = compute_sigma_image(L, w, p)
    print(f"|σ-image| = {len(sigma_image)}")

    # Test over random syndromes
    import random
    random.seed(42)

    nk = n - k
    max_M = 0
    max_syndrome = None
    M_dist = {}
    n_tested = 0
    n_test = min(p**nk, 5000)  # Test up to 5000 syndromes

    # For small p^{n-k}: enumerate all syndromes
    if p**nk <= 5000:
        syndromes = []
        def enum_syn(depth, current):
            if depth == nk:
                syndromes.append(current[:])
                return
            for v in range(p):
                current.append(v)
                enum_syn(depth + 1, current)
                current.pop()
        enum_syn(0, [])
    else:
        # Random syndromes
        syndromes = []
        for _ in range(n_test):
            syndromes.append([random.randint(0, p-1) for _ in range(nk)])

    # Analyze each syndrome
    incidence_bound = comb(n, d) / comb(w, d)
    violations = 0

    for syn in syndromes:
        result = toeplitz_flat(syn, w, p)
        if result is None:
            continue

        offset, basis = result
        if len(basis) != d:
            continue  # Rank-deficient Toeplitz matrix

        M, matching = count_M_on_flat(sigma_image, offset, basis, p)

        M_dist[M] = M_dist.get(M, 0) + 1
        n_tested += 1

        if M > max_M:
            max_M = M
            max_syndrome = syn[:]

        if M > incidence_bound:
            violations += 1

    print(f"\nTested {n_tested} syndromes (of {p**nk} total)")
    print(f"Max M = {max_M}")
    print(f"Incidence bound C(n,d)/C(w,d) = {incidence_bound:.1f}")
    print(f"Violations: {violations}")
    print(f"\nM distribution:")
    for m in sorted(M_dist.keys()):
        pct = 100 * M_dist[m] / n_tested
        print(f"  M={m}: {M_dist[m]} ({pct:.1f}%)")

    avg_M = sum(m * cnt for m, cnt in M_dist.items()) / n_tested if n_tested > 0 else 0
    print(f"\navg M = {avg_M:.4f} (predicted: {comb(n,w)/p**c:.4f})")

    # Analyze the worst-case syndrome
    if max_syndrome is not None and max_M > 0:
        print(f"\n--- Worst-case syndrome analysis ---")
        result = toeplitz_flat(max_syndrome, w, p)
        if result:
            offset, basis = result
            M, matching = count_M_on_flat(sigma_image, offset, basis, p)
            print(f"M = {M}, subsets: {matching[:5]}{'...' if len(matching)>5 else ''}")

            if d >= 2:
                # Check for coincident hyperplanes
                dirs = check_coincident(L, offset, basis, p)
                max_group = max(len(v) for v in dirs.values()) if dirs else 0
                n_groups = len(dirs)
                print(f"Hyperplane directions: {n_groups} groups, max group size = {max_group}")
                if max_group > 1:
                    big_groups = {k: v for k, v in dirs.items() if len(v) > 1}
                    for direction, betas in list(big_groups.items())[:3]:
                        print(f"  Group (size {len(betas)}): β ∈ {betas[:5]}")

    return max_M, incidence_bound

def main():
    print("=" * 70)
    print("INCIDENCE BOUND VERIFICATION: M ≤ C(n,d)/C(w,d)")
    print("=" * 70)

    # Test cases: (n, k, p, w) — w=None means Johnson radius
    test_cases = [
        # d=1 (lines): c = w-1
        (10, 5, 11, 3),   # c=2, d=1
        (10, 5, 31, 3),   # c=2, d=1, larger p
        (10, 5, 41, 3),   # c=2, d=1, even larger p

        # d=2 (2-flats): various
        (10, 5, 11, 4),   # c=1, d=3... wait c=n-k-w=5-4=1, d=w-c=3
        (10, 4, 11, 3),   # c=n-k-w=6-3=3, d=0... no
        (12, 6, 13, 4),   # c=2, d=2
        (12, 6, 37, 4),   # c=2, d=2, larger p
        (14, 7, 29, 5),   # c=2, d=3

        # Explicit d=2 cases
        (10, 3, 11, 4),   # c=3, d=1
        (10, 4, 11, 4),   # c=2, d=2 -- wait n-k=6, c=6-4=2, d=2
        (10, 4, 31, 4),   # c=2, d=2
        (12, 4, 13, 4),   # c=4, d=0... no. n-k=8, c=8-4=4, d=0. skip
        (12, 6, 13, 5),   # c=1, d=4
        (14, 7, 29, 4),   # c=3, d=1
        (14, 7, 29, 5),   # c=2, d=3
    ]

    # Filter valid cases
    valid_cases = []
    for tc in test_cases:
        n, k, p, w = tc
        c = n - k - w
        d = w - c
        if c > 0 and d > 0 and (p - 1) % n == 0:
            valid_cases.append(tc)

    results = []
    for n, k, p, w in valid_cases:
        c = n - k - w
        d = w - c
        # Skip if enumeration is too large
        if p**(n-k) > 50000 and comb(n, w) > 50000:
            print(f"\nSkipping n={n},k={k},p={p},w={w}: too large")
            continue
        try:
            max_M, bound = run_experiment(n, k, p, w)
            if max_M is not None:
                results.append((n, k, p, w, n-k-w, w-(n-k-w), max_M, bound))
        except Exception as e:
            print(f"\nError for n={n},k={k},p={p},w={w}: {e}")

    # Summary table
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"{'n':>4} {'k':>4} {'p':>4} {'w':>4} {'c':>4} {'d':>4} {'maxM':>6} {'C(n,d)/C(w,d)':>14} {'Bezout':>10} {'density':>10} {'ok?':>5}")
    print("-" * 70)
    for n, k, p, w, c, d, maxM, bound in results:
        bezout = (n-w+1)**d
        density = comb(n,w) / p**c
        ok = "✓" if maxM <= bound else "✗"
        print(f"{n:>4} {k:>4} {p:>4} {w:>4} {c:>4} {d:>4} {maxM:>6} {bound:>14.1f} {bezout:>10} {density:>10.3f} {ok:>5}")

if __name__ == "__main__":
    main()
