"""
Test equal-threshold CA bound: ε_ca(C, δ, δ) for small RS codes.

For RS[n, k] over F_p:
- Enumerate all (f₁, f₂) with Δ_joint((f₁,f₂), C²) > δ
- For each, count #{γ : Δ(f₁+γf₂, C) ≤ δ}
- Report max count

If max count = O(1) for all tested cases: evidence for OP1.
If max count grows with n or p: counterexample territory.
"""

import itertools
from collections import defaultdict

def rs_code(n, k, p, omega):
    """Generate all codewords of RS[n,k] over F_p with evaluation domain L = {omega^i}."""
    L = [pow(omega, i, p) for i in range(n)]
    codewords = []
    # Enumerate all polynomials of degree < k
    for coeffs in itertools.product(range(p), repeat=k):
        word = []
        for x in L:
            val = 0
            xi = 1
            for c in coeffs:
                val = (val + c * xi) % p
                xi = (xi * x) % p
            word.append(val)
        codewords.append(tuple(word))
    return L, codewords

def hamming_dist(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)

def dist_to_code(word, codewords):
    return min(hamming_dist(word, c) for c in codewords)

def joint_dist(f1, f2, codewords_sq, n):
    """min over (g1,g2) in C^2 of |supp(f1-g1) ∪ supp(f2-g2)| / n"""
    min_joint = n + 1
    for g1, g2 in codewords_sq:
        joint = sum(1 for i in range(n) if f1[i] != g1[i] or f2[i] != g2[i])
        if joint < min_joint:
            min_joint = joint
    return min_joint

def test_ca_equal_threshold(n, k, p, omega, delta_frac_num, delta_frac_den):
    """
    Test ε_ca(C, δ, δ) for RS[n,k] over F_p.
    delta = delta_frac_num / delta_frac_den (as fraction to avoid float issues)
    w = floor(delta * n) = max errors for "close"
    """
    w = (delta_frac_num * n) // delta_frac_den  # max errors for δ-close
    delta_n = w  # threshold in absolute terms: ≤ w errors means ≤ δ

    print(f"\n{'='*60}")
    print(f"RS[{n}, {k}] over F_{p}, ω={omega}")
    print(f"ρ = {k}/{n} = {k/n:.3f}")
    print(f"δ_J = 1 - √ρ = {1 - (k/n)**0.5:.4f}")
    print(f"δ = {delta_frac_num}/{delta_frac_den} = {delta_frac_num/delta_frac_den:.4f}, w = {w}")
    print(f"Testing equal-threshold CA: ε_ca(C, δ, δ)")
    print(f"{'='*60}")

    L, codewords = rs_code(n, k, p, omega)
    print(f"|C| = {len(codewords)}, |L| = {len(L)}, L = {L}")

    # Precompute C^2 for joint distance (expensive but needed)
    # For small codes only
    if len(codewords)**2 > 5_000_000:
        print("C^2 too large, using optimized joint distance")
        codewords_sq = None  # will compute differently
    else:
        codewords_sq = list(itertools.product(codewords, repeat=2))
        print(f"|C²| = {len(codewords_sq)}")

    # Precompute distance to code for all words
    # Only feasible for small p^n
    total_words = p ** n
    if total_words > 500_000:
        print(f"Total words {total_words} too large for exhaustive search.")
        print("Using random sampling instead.")
        return test_ca_sampled(n, k, p, omega, w, L, codewords, codewords_sq)

    print(f"Total words: {total_words}")

    # Precompute dist_to_code for all words
    print("Precomputing distances to code...")
    dist_cache = {}
    for word in itertools.product(range(p), repeat=n):
        d = dist_to_code(word, codewords)
        dist_cache[word] = d
    print(f"Distance cache built: {len(dist_cache)} entries")

    # Enumerate all (f1, f2) pairs with Δ_joint > δ
    max_bad_gamma = 0
    max_bad_pair = None
    total_pairs_tested = 0
    pairs_with_violation = 0

    bad_gamma_histogram = defaultdict(int)  # count of how many pairs have each # of bad γ

    for f1 in itertools.product(range(p), repeat=n):
        for f2 in itertools.product(range(p), repeat=n):
            # Compute joint distance
            if codewords_sq is not None:
                jd = joint_dist(f1, f2, codewords_sq, n)
            else:
                jd = n + 1
                for g1 in codewords:
                    for g2 in codewords:
                        j = sum(1 for i in range(n) if f1[i] != g1[i] or f2[i] != g2[i])
                        if j < jd:
                            jd = j

            if jd <= delta_n:
                continue  # joint distance ≤ δ, not a CA premise

            total_pairs_tested += 1

            # Count bad γ
            bad_count = 0
            for gamma in range(p):
                fg = tuple((f1[i] + gamma * f2[i]) % p for i in range(n))
                if dist_cache[fg] <= w:
                    bad_count += 1

            bad_gamma_histogram[bad_count] += 1

            if bad_count > 0:
                pairs_with_violation += 1

            if bad_count > max_bad_gamma:
                max_bad_gamma = bad_count
                max_bad_pair = (f1, f2)

                # Analyze the worst case
                print(f"\nNew max: {bad_count} bad γ")
                print(f"  f₁ = {f1}, Δ(f₁,C) = {dist_cache[f1]}")
                print(f"  f₂ = {f2}, Δ(f₂,C) = {dist_cache[tuple(f2)]}")
                print(f"  Δ_joint = {jd}/{n}")
                for gamma in range(p):
                    fg = tuple((f1[i] + gamma * f2[i]) % p for i in range(n))
                    d = dist_cache[fg]
                    if d <= w:
                        # Find the closest codeword
                        for c in codewords:
                            if hamming_dist(fg, c) == d:
                                print(f"  γ={gamma}: f₁+γf₂ = {fg}, Δ={d}, closest c={c}")
                                break

    print(f"\n{'='*60}")
    print(f"RESULTS for RS[{n},{k}] over F_{p}, δ={delta_frac_num}/{delta_frac_den} (w={w})")
    print(f"{'='*60}")
    print(f"Total (f₁,f₂) with Δ_joint > δ: {total_pairs_tested}")
    print(f"Pairs with at least 1 bad γ: {pairs_with_violation}")
    print(f"Max bad γ count: {max_bad_gamma}")
    print(f"Bad γ histogram: {dict(sorted(bad_gamma_histogram.items()))}")

    if max_bad_gamma <= 2:
        print(f"✓ Equal-threshold CA ε_ca(C,δ,δ) ≤ {max_bad_gamma}/{p} = {max_bad_gamma/p:.4f}")
        print(f"  This is O(1)/|F| — consistent with OP1!")
    else:
        print(f"✗ Max bad γ = {max_bad_gamma} > 2. ε_ca(C,δ,δ) ≥ {max_bad_gamma}/{p}")
        if max_bad_gamma > 2:
            print(f"  WARNING: This exceeds the reduced-threshold bound of 2/|F|")

    return max_bad_gamma

def test_ca_sampled(n, k, p, omega, w, L, codewords, codewords_sq, num_samples=100000):
    """Sampled version for larger codes."""
    import random

    max_bad_gamma = 0
    for trial in range(num_samples):
        f1 = tuple(random.randint(0, p-1) for _ in range(n))
        f2 = tuple(random.randint(0, p-1) for _ in range(n))

        # Compute joint distance
        jd = n + 1
        for g1 in codewords:
            for g2 in codewords:
                j = sum(1 for i in range(n) if f1[i] != g1[i] or f2[i] != g2[i])
                if j < jd:
                    jd = j

        if jd <= w:
            continue

        # Count bad γ
        bad_count = 0
        for gamma in range(p):
            fg = tuple((f1[i] + gamma * f2[i]) % p for i in range(n))
            d = dist_to_code(fg, codewords)
            if d <= w:
                bad_count += 1

        if bad_count > max_bad_gamma:
            max_bad_gamma = bad_count
            print(f"Trial {trial}: new max {bad_count} bad γ")
            print(f"  f₁ = {f1}, f₂ = {f2}")

    print(f"\nSampled max bad γ: {max_bad_gamma} (over {num_samples} random pairs)")
    return max_bad_gamma


def find_primitive_root(p, n):
    """Find ω such that ω has order n in F_p*."""
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        w = pow(g, (p-1)//n, p)
        if w != 1 and pow(w, n, p) == 1:
            # Check order is exactly n
            ok = True
            for d in range(1, n):
                if n % d == 0 and d < n:
                    if pow(w, d, p) == 1:
                        ok = False
                        break
            if ok:
                return w
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("EQUAL-THRESHOLD CA BOUND TEST")
    print("Testing ε_ca(C, δ, δ) for small RS codes")
    print("=" * 60)

    # Test 1: RS[4, 2] over F_5
    # n=4, k=2, ρ=1/2, δ_J ≈ 0.293
    # L = F_5* = {1,2,3,4}, ω=2 (order 4)
    # δ = 1/2, w = 2
    omega = find_primitive_root(5, 4)
    print(f"\nPrimitive 4th root of unity mod 5: ω = {omega}")
    test_ca_equal_threshold(4, 2, 5, omega, 1, 2)

    # Test 2: RS[4, 2] over F_13
    # Same code structure, larger field
    omega13 = find_primitive_root(13, 4)
    if omega13:
        print(f"\nPrimitive 4th root of unity mod 13: ω = {omega13}")
        test_ca_equal_threshold(4, 2, 13, omega13, 1, 2)

    # Test 3: RS[6, 3] over F_7
    # n=6, k=3, ρ=1/2, δ_J ≈ 0.293
    # Need 6 | (7-1)=6. ω = primitive 6th root mod 7
    omega7 = find_primitive_root(7, 6)
    if omega7:
        print(f"\nPrimitive 6th root of unity mod 7: ω = {omega7}")
        test_ca_equal_threshold(6, 3, 7, omega7, 1, 2)

    # Test 4: RS[6, 3] over F_13
    omega13_6 = find_primitive_root(13, 6)
    if omega13_6:
        print(f"\nPrimitive 6th root of unity mod 13: ω = {omega13_6}")
        test_ca_equal_threshold(6, 3, 13, omega13_6, 1, 2)

    # Test 5: RS[8, 4] over F_17
    omega17 = find_primitive_root(17, 8)
    if omega17:
        print(f"\nPrimitive 8th root of unity mod 17: ω = {omega17}")
        test_ca_equal_threshold(8, 4, 17, omega17, 1, 2)

    # Test 6: RS[10, 5] over F_11
    omega11 = find_primitive_root(11, 10)
    if omega11:
        print(f"\nPrimitive 10th root of unity mod 11: ω = {omega11}")
        test_ca_equal_threshold(10, 5, 11, omega11, 1, 2)
