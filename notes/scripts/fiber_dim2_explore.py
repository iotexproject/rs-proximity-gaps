"""
fiber_dim2_explore.py — Explore fiber bound for d=2 (codimension c=1 hyperplanes in F_p^w)

Gap 1: extend fiber bound from lines (c=w-1) to higher-dimensional flats (c<w-1).
First case: c=1, d=w-1 (hyperplanes).

Key setup:
- RS[n,k] with w error positions, c = n-k-w = 1 syndrome condition
- Compatible σ-values form a hyperplane V ⊂ F_p^w (codim 1)
- Each T ∈ L defines a hyperplane H_T in parameter space: φ_0(T) + Σ s_i φ_i(T) = 0
- Valid w-subset ↔ w-rich point of the arrangement of n hyperplanes

For c=1 specifically:
- V is a hyperplane in F_p^w defined by one linear equation α·σ = β
- σ(B) = (e_1(B),...,e_w(B)) for B ∈ C(L,w)
- M = |{B ∈ C(L,w) : α·σ(B) = β}|

Approach: for each hyperplane, count M. Find max over non-pinned hyperplanes.
Compare with conjectured bound M ≤ (n/w)^{w-1}.
"""

import itertools
from collections import Counter

def find_primitive_root(p):
    """Find a primitive root mod p."""
    for g in range(2, p):
        if pow(g, (p-1)//2, p) != 1:  # Check it's not a QR (sufficient for prime p)
            seen = set()
            x = 1
            for _ in range(p-1):
                seen.add(x)
                x = (x * g) % p
            if len(seen) == p-1:
                return g
    return None

def elem_sym(B, p):
    """Elementary symmetric polynomials of subset B over F_p."""
    w = len(B)
    # e_j = sum of products of j elements from B
    e = [0] * (w + 1)
    e[0] = 1
    for b in B:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * b) % p
    return tuple(e[1:])  # (e_1, ..., e_w)

def run_experiment(n, p):
    """Run fiber dim-2 experiment for given n, p."""
    g = find_primitive_root(p)
    omega = pow(g, (p-1)//n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*60}")
    print(f"n={n}, p={p}, |L|={len(L)}")

    # Compute all w-subsets and their σ-images for several w values
    for w in range(3, min(n//2 + 1, 7)):
        c_max = n - 2*w  # For the compatible subspace to have codim c with k reasonable
        # Actually c = n - k - w. For c=1: k = n - w - 1.
        k = n - w - 1  # codimension c=1
        if k < 1:
            continue
        c = 1
        d = w - c  # dimension of compatible subspace = w-1

        subsets = list(itertools.combinations(range(n), w))
        # Map indices to L elements
        sigma_images = []
        for B_idx in subsets:
            B = tuple(L[i] for i in B_idx)
            sigma_images.append(elem_sym(B, p))

        N = len(sigma_images)
        print(f"\n  w={w}, k={k}, c={c}, d={d}, N=C({n},{w})={N}")

        # A hyperplane in F_p^w is defined by normal vector α ∈ F_p^w and offset β:
        # α_1 σ_1 + ... + α_w σ_w = β

        # For each σ-image point, compute α·σ for various α, then count collisions

        # Strategy: sample random hyperplanes AND check structured ones

        # === Random hyperplanes ===
        import random
        random.seed(42)

        max_M_random = 0
        M_dist_random = Counter()

        for trial in range(min(2000, p**w)):  # Sample hyperplanes
            # Random normal vector (nonzero)
            alpha = tuple(random.randint(0, p-1) for _ in range(w))
            if all(a == 0 for a in alpha):
                continue
            beta = random.randint(0, p-1)

            # Count σ-images on this hyperplane
            M = sum(1 for sig in sigma_images if sum(a*s for a,s in zip(alpha, sig)) % p == beta)
            M_dist_random[M] += 1
            if M > max_M_random:
                max_M_random = M

        print(f"  Random hyperplanes (2000 trials):")
        print(f"    max M = {max_M_random}")
        print(f"    distribution: {dict(sorted(M_dist_random.items())[:10])}")
        print(f"    expected M ≈ C({n},{w})/p = {N/p:.1f}")

        # === ALL hyperplanes (feasible for small p) ===
        if p <= 17 and w <= 4:
            print(f"\n  Exhaustive hyperplane search (p={p}):")
            max_M_all = 0
            M_dist_all = Counter()
            best_hyperplanes = []

            # For each possible α·σ value:
            # Group σ-images by α·σ for each α
            for alpha in itertools.product(range(p), repeat=w):
                if all(a == 0 for a in alpha):
                    continue
                # Normalize: first nonzero entry = 1
                first_nz = next(i for i, a in enumerate(alpha) if a != 0)
                inv = pow(alpha[first_nz], p-2, p)
                alpha_norm = tuple((a * inv) % p for a in alpha)

                # Skip duplicates (we'd need to track, but for now just compute all)
                dot_products = [sum(a*s for a,s in zip(alpha, sig)) % p for sig in sigma_images]
                by_beta = Counter(dot_products)

                for beta, count in by_beta.items():
                    M_dist_all[count] += 1
                    if count > max_M_all:
                        max_M_all = count
                        best_hyperplanes = [(alpha, beta, count)]
                    elif count == max_M_all:
                        best_hyperplanes.append((alpha, beta, count))

            print(f"    max M = {max_M_all}")
            print(f"    conjectured bound (n/w)^(w-1) = {(n/w)**(w-1):.1f}")

            # Analyze best hyperplanes: are they pinned?
            print(f"    Top hyperplanes ({len(best_hyperplanes)} with M={max_M_all}):")
            for alpha, beta, count in best_hyperplanes[:5]:
                # Find the actual subsets on this hyperplane
                on_hp = []
                for i, sig in enumerate(sigma_images):
                    if sum(a*s for a,s in zip(alpha, sig)) % p == beta:
                        on_hp.append(subsets[i])

                # Check if pinned: is there a common element in all subsets?
                if on_hp:
                    common = set(on_hp[0])
                    for B in on_hp[1:]:
                        common &= set(B)
                    pinned_size = len(common)

                    # Check pairwise overlaps
                    overlaps = []
                    for i in range(min(len(on_hp), 10)):
                        for j in range(i+1, min(len(on_hp), 10)):
                            overlaps.append(len(set(on_hp[i]) & set(on_hp[j])))
                    avg_overlap = sum(overlaps)/len(overlaps) if overlaps else 0

                    print(f"      α={alpha}, β={beta}: M={count}, common={common} (pinned-{pinned_size}), avg_overlap={avg_overlap:.2f}")

        # === Incidence geometry analysis ===
        # For each T ∈ L: the "hyperplane" H_T in parameter space F_p^{w-1}
        # is defined by P_s(T) = 0 where s parameterizes the hyperplane V.
        #
        # BUT for c=1: V is codim 1 in F_p^w, parameterized by d=w-1 free variables.
        # Need to pick a specific V and parameterize.

        if w == 3 and p <= 17:
            print(f"\n  === Incidence geometry for w={w} ===")

            # Pick a specific hyperplane: σ_1 + σ_2 + σ_3 = 0 (a generic one)
            alpha = (1, 1, 1)

            for beta in range(p):
                M = sum(1 for sig in sigma_images if (sig[0] + sig[1] + sig[2]) % p == beta)
                if M == 0:
                    continue

                # Parameterize: s_1 = σ_1, s_2 = σ_2, then σ_3 = beta - s_1 - s_2
                # P_{s_1,s_2}(T) = T^3 - s_1 T^2 + s_2 T - (beta - s_1 - s_2)
                #                = T^3 - s_1 T^2 + s_2 T - beta + s_1 + s_2
                #                = (T^3 - beta) + s_1(-T^2 + 1) + s_2(T + 1)
                # φ_0(T) = T^3 - beta
                # φ_1(T) = -T^2 + 1 = -(T^2 - 1) = -(T-1)(T+1)
                # φ_2(T) = T + 1

                # Line for each T ∈ L: φ_0(T) + s_1 φ_1(T) + s_2 φ_2(T) = 0
                # This is a line in (s_1, s_2) space.

                lines = []
                for T in L:
                    phi0 = (pow(T, 3, p) - beta) % p
                    phi1 = (-(pow(T, 2, p) - 1)) % p  # -(T^2 - 1)
                    phi2 = (T + 1) % p
                    lines.append((phi0, phi1, phi2))

                # Find all intersection points
                # For each pair (T_i, T_j): solve 2×2 system
                rich_points = Counter()
                for i in range(n):
                    for j in range(i+1, n):
                        # φ_1(T_i) s_1 + φ_2(T_i) s_2 = -φ_0(T_i)
                        # φ_1(T_j) s_1 + φ_2(T_j) s_2 = -φ_0(T_j)
                        a11, a12, b1 = lines[i][1], lines[i][2], (-lines[i][0]) % p
                        a21, a22, b2 = lines[j][1], lines[j][2], (-lines[j][0]) % p
                        det = (a11 * a22 - a12 * a21) % p
                        if det == 0:
                            continue  # Parallel or coincident
                        det_inv = pow(det, p-2, p)
                        s1 = ((b1 * a22 - b2 * a12) * det_inv) % p
                        s2 = ((a11 * b2 - a21 * b1) * det_inv) % p
                        rich_points[(s1, s2)] += 1

                if M > 0:
                    # Count how many points have ≥ C(w,2) = 3 incidences (from pairs)
                    # A w-rich point gets C(w,2) pair incidences
                    w_rich = sum(1 for v in rich_points.values() if v >= w*(w-1)//2)
                    max_pairs = max(rich_points.values()) if rich_points else 0
                    max_inc = 0
                    # Actually count line incidences directly
                    if max_pairs >= 3:
                        for (s1, s2), cnt in rich_points.items():
                            if cnt >= 3:
                                # Count actual incidences
                                inc = sum(1 for T_idx in range(n)
                                         if (lines[T_idx][0] + s1*lines[T_idx][1] + s2*lines[T_idx][2]) % p == 0)
                                max_inc = max(max_inc, inc)

                    if M >= max(2, N//p):
                        print(f"    β={beta}: M={M}, max_inc_at_point={max_inc}, w_rich={w_rich}")

# Run experiments
for n, p in [(8, 11), (10, 11), (10, 13), (10, 31), (12, 13), (14, 29), (16, 17)]:
    if p > n:  # Need p > n for L to exist
        run_experiment(n, p)

# Summary analysis
print("\n" + "="*60)
print("SUMMARY: Fiber bound for d = w-1 (hyperplanes, c=1)")
print("="*60)
print("Conjectured: M ≤ (n/w)^(w-1) for non-pinned hyperplanes")
print("Alternative: M ≤ C·(n^2/w^3 + n/w) via Szemerédi-Trotter")
print("For rate 1/2 (w ≈ 0.29n): both give M = O(1)")
