"""
FRI Folding List Size Reduction

Goal: verify that after each FRI folding round, the list of close codewords
shrinks. Specifically:

- Start with RS[n, k] on L = <omega> of order n in F_p
- Find all codewords within Johnson radius w of a center c
- Fold: g_alpha(y) = f_even(y) + alpha * f_odd(y) on L' = L^2
- Count how many folded codewords are within w' = w/2 of g_alpha
- Repeat for multiple alpha values

Key insight: error set E must be "paired" (closed under i -> i+n/2)
for the codeword to survive folding. This is a severe structural constraint.
"""

import itertools
import random
from collections import defaultdict


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


def find_params(n):
    """Find smallest prime p = 1 mod n and primitive n-th root."""
    p = n + 1
    while True:
        if p % n == 1 and all(p % i != 0 for i in range(2, int(p**0.5) + 1)):
            g = find_primitive_root(p)
            omega = pow(g, (p - 1) // n, p)
            return p, omega
        p += n


def rs_encode(coeffs, omega, n, p):
    """Evaluate polynomial at omega^0, ..., omega^(n-1)."""
    vals = []
    for i in range(n):
        x = pow(omega, i, p)
        v = 0
        xi = 1
        for c in coeffs:
            v = (v + c * xi) % p
            xi = (xi * x) % p
        vals.append(v)
    return vals


def hamming_dist(a, b, p):
    return sum(1 for x, y in zip(a, b) if (x - y) % p != 0)


def find_list(center, omega, n, k, w, p):
    """Find all codewords within distance w of center. Brute force."""
    codewords = []
    # Enumerate all degree < k polynomials
    for coeffs in itertools.product(range(p), repeat=k):
        vals = rs_encode(list(coeffs), omega, n, p)
        d = hamming_dist(vals, center, p)
        if d <= w:
            codewords.append((list(coeffs), vals, d))
    return codewords


def fold_function(vals, omega, n, p, alpha):
    """FRI fold: f(x) = f_even(x^2) + x * f_odd(x^2)
    Returns values on L' = L^2 = {omega^(2i) : i=0..n/2-1}

    For each pair (i, i+n/2):
    f_even(omega^(2i)) = (f(omega^i) + f(omega^(i+n/2))) / 2
    f_odd(omega^(2i))  = (f(omega^i) - f(omega^(i+n/2))) / (2 * omega^i)
    g_alpha(omega^(2i)) = f_even(omega^(2i)) + alpha * f_odd(omega^(2i))
    """
    n2 = n // 2
    inv2 = pow(2, p - 2, p)
    g = []
    for i in range(n2):
        fi = vals[i]
        fi2 = vals[i + n2]  # f(omega^(i+n/2)) = f(-omega^i) since omega^(n/2) = -1

        f_even = (fi + fi2) * inv2 % p
        # f_odd * omega^i = (fi - fi2) / 2
        # f_odd = (fi - fi2) / (2 * omega^i)
        omega_i = pow(omega, i, p)
        inv_omega_i = pow(omega_i, p - 2, p)
        f_odd = (fi - fi2) * inv2 % p * inv_omega_i % p

        gi = (f_even + alpha * f_odd) % p
        g.append(gi)
    return g


def fold_codeword(coeffs, k, p, alpha):
    """Fold a codeword's coefficients.
    f(x) = sum c_j x^j, degree < k.
    f_even(y) = sum c_{2j} y^j, j < k/2
    f_odd(y) = sum c_{2j+1} y^j, j < k/2
    g_alpha(y) = f_even(y) + alpha * f_odd(y) = sum (c_{2j} + alpha*c_{2j+1}) y^j
    """
    k2 = k // 2
    new_coeffs = []
    for j in range(k2):
        c_even = coeffs[2 * j] if 2 * j < len(coeffs) else 0
        c_odd = coeffs[2 * j + 1] if 2 * j + 1 < len(coeffs) else 0
        new_coeffs.append((c_even + alpha * c_odd) % p)
    return new_coeffs


def analyze_error_pairing(error_set, n):
    """Analyze how many errors are paired (i and i+n/2 both in error set)."""
    n2 = n // 2
    paired = 0
    unpaired = 0
    for i in error_set:
        partner = (i + n2) % n
        if partner in error_set:
            paired += 1
    # paired counts each pair twice
    paired //= 2
    unpaired = len(error_set) - 2 * paired
    return paired, unpaired


def main():
    print("=== FRI Folding List Size Reduction ===\n")

    # Test parameters
    test_cases = [
        # (n, rho=1/2)
        (8, 4),
        (10, 5),
        (12, 6),
        (14, 7),
        (16, 8),
    ]

    for n, k in test_cases:
        p, omega = find_params(n)
        w = n - k - int((n * k) ** 0.5)  # Johnson radius: n - k - floor(sqrt(nk))
        # More precisely: w = floor((1 - sqrt(k/n)) * n)
        import math
        w = int(math.floor((1 - math.sqrt(k / n)) * n))
        if w < 1:
            w = 1

        n2 = n // 2
        k2 = k // 2
        w2 = int(math.floor((1 - math.sqrt(k2 / n2)) * n2))
        if w2 < 1:
            w2 = 1

        print(f"n={n}, k={k}, p={p}, w={w} (Johnson)")
        print(f"  Folded: n'={n2}, k'={k2}, w'={w2}")

        # Skip if too large for brute force
        if p ** k > 5_000_000:
            print(f"  SKIP: p^k = {p}^{k} too large\n")
            continue

        # Sample random centers and find lists
        max_M = 0
        max_M_center = None
        num_centers = min(200, p ** (n - k))

        random.seed(42)

        results = []
        for trial in range(num_centers):
            # Random center
            center = [random.randrange(p) for _ in range(n)]

            # Find list
            cw_list = find_list(center, omega, n, k, w, p)
            M = len(cw_list)

            if M > max_M:
                max_M = M
                max_M_center = center
                max_M_list = cw_list

        if max_M == 0:
            print(f"  No codewords found within w={w}")
            print()
            continue

        print(f"  Max M = {max_M} (over {num_centers} random centers)")

        # Analyze the maximum-M center
        center = max_M_center
        cw_list = max_M_list

        # For each codeword, analyze error pairing
        print(f"\n  Error pairing analysis (max-M center):")
        for idx, (coeffs, vals, d) in enumerate(cw_list):
            error_set = set()
            for i in range(n):
                if (vals[i] - center[i]) % p != 0:
                    error_set.add(i)
            paired, unpaired = analyze_error_pairing(error_set, n)
            print(f"    cw {idx}: d={d}, paired={paired}, unpaired={unpaired}, "
                  f"survives_fold={'YES' if unpaired == 0 else 'maybe'}")

        # FRI fold with multiple random alpha values
        print(f"\n  FRI folding (10 random alpha values):")
        omega2 = pow(omega, 2, p)  # primitive root for L'

        for alpha_idx in range(10):
            alpha = random.randrange(1, p)

            # Fold center
            g_center = fold_function(center, omega, n, p, alpha)

            # Count surviving codewords
            surviving = 0
            for coeffs, vals, d in cw_list:
                # Fold the codeword
                folded_coeffs = fold_codeword(coeffs, k, p, alpha)
                folded_vals = rs_encode(folded_coeffs, omega2, n2, p)

                # Distance in folded space
                d_folded = hamming_dist(folded_vals, g_center, p)
                if d_folded <= w2:
                    surviving += 1

            print(f"    alpha={alpha}: surviving={surviving}/{max_M}")

        # Also check: for how many alpha values does each codeword survive?
        print(f"\n  Per-codeword survival rate (100 alpha values):")
        for idx, (coeffs, vals, d) in enumerate(cw_list):
            survive_count = 0
            for _ in range(100):
                alpha = random.randrange(1, p)
                g_center = fold_function(center, omega, n, p, alpha)
                folded_coeffs = fold_codeword(coeffs, k, p, alpha)
                folded_vals = rs_encode(folded_coeffs, omega2, n2, p)
                d_folded = hamming_dist(folded_vals, g_center, p)
                if d_folded <= w2:
                    survive_count += 1

            error_set = {i for i in range(n) if (vals[i] - center[i]) % p != 0}
            paired, unpaired = analyze_error_pairing(error_set, n)
            print(f"    cw {idx}: d={d}, paired/unpaired={paired}/{unpaired}, "
                  f"survive={survive_count}/100 ({survive_count}%)")

        print()

    # Detailed folding chain for n=12
    print("\n=== Detailed Folding Chain (n=12, k=6) ===\n")
    n, k = 12, 6
    p, omega = find_params(n)
    import math
    w = int(math.floor((1 - math.sqrt(k / n)) * n))

    print(f"n={n}, k={k}, p={p}, omega={omega}, w={w}")

    # Find center with maximum M
    max_M = 0
    random.seed(123)
    for trial in range(500):
        center = [random.randrange(p) for _ in range(n)]
        cw_list = find_list(center, omega, n, k, w, p)
        if len(cw_list) > max_M:
            max_M = len(cw_list)
            best_center = center
            best_list = cw_list

    print(f"Max M = {max_M}")

    # Now iteratively fold
    current_center = best_center
    current_list = best_list
    current_n = n
    current_k = k
    current_omega = omega

    round_num = 0
    while current_n > 2 and current_k > 1:
        current_w = int(math.floor((1 - math.sqrt(current_k / current_n)) * current_n))
        if current_w < 1:
            current_w = 1

        print(f"\nRound {round_num}: n={current_n}, k={current_k}, w={current_w}, M={len(current_list)}")

        # Show error pairing for each codeword
        for idx, (coeffs, vals, d) in enumerate(current_list[:5]):
            error_set = {i for i in range(current_n)
                         if (vals[i] - current_center[i]) % p != 0}
            paired, unpaired = analyze_error_pairing(error_set, current_n)
            print(f"  cw {idx}: d={d}, paired={paired}, unpaired={unpaired}")
        if len(current_list) > 5:
            print(f"  ... ({len(current_list) - 5} more)")

        # Fold with a random alpha
        alpha = random.randrange(1, p)
        new_n = current_n // 2
        new_k = current_k // 2
        new_omega = pow(current_omega, 2, p)

        new_center = fold_function(current_center, current_omega, current_n, p, alpha)
        new_w = int(math.floor((1 - math.sqrt(new_k / new_n)) * new_n))
        if new_w < 1:
            new_w = 1

        # Find surviving codewords
        new_list = []
        for coeffs, vals, d in current_list:
            folded_coeffs = fold_codeword(coeffs, current_k, p, alpha)
            folded_vals = rs_encode(folded_coeffs, new_omega, new_n, p)
            d_new = hamming_dist(folded_vals, new_center, p)
            if d_new <= new_w:
                new_list.append((folded_coeffs, folded_vals, d_new))

        print(f"  -> After fold (alpha={alpha}): n'={new_n}, k'={new_k}, w'={new_w}, M'={len(new_list)}")

        current_center = new_center
        current_list = new_list
        current_n = new_n
        current_k = new_k
        current_omega = new_omega
        round_num += 1

    # Final round
    if current_list:
        current_w = int(math.floor((1 - math.sqrt(current_k / current_n)) * current_n))
        if current_w < 1:
            current_w = 1
        print(f"\nFinal: n={current_n}, k={current_k}, w={current_w}, M={len(current_list)}")


if __name__ == "__main__":
    main()
