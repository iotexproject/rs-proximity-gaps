"""
List-size M for general degree-t words over F_p.

Setup:
  L = <ω> ⊂ F_p*, |L| = n, ω primitive n-th root of unity
  w(x) = general polynomial of degree t
  RS_2 codeword h(x) = h0 + h1*x
  Agreement set S = {i ∈ Z/nZ : w(ω^i) = h(ω^i)}
  M = #{(h0, h1) : |S| ≥ t}

We compute M for various word structures and compare to n/(t-1).
"""
from itertools import combinations

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

def find_subgroup(p, n):
    """Find multiplicative subgroup of order n in F_p*.
    Requires n | (p-1). Returns (omega, L) where L = [1, omega, omega^2, ..., omega^{n-1}]."""
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    L = []
    x = 1
    for _ in range(n):
        L.append(x)
        x = (x * omega) % p
    assert len(set(L)) == n
    return omega, L

def eval_poly(coeffs, x, p):
    """Evaluate polynomial with given coefficients at x mod p.
    coeffs[j] is coefficient of x^j."""
    result = 0
    xpow = 1
    for c in coeffs:
        result = (result + c * xpow) % p
        xpow = (xpow * x) % p
    return result

def compute_M(p, n, w_coeffs, t_threshold=None):
    """Compute M = #{(h0,h1) with |agreement set| >= t}.

    w_coeffs: list of coefficients [a0, a1, ..., a_d] for w(x) = sum a_j x^j
    t_threshold: minimum agreement size (default: degree of w)

    Returns: (M, details) where details is dict mapping (h0,h1) -> agreement_size
    """
    omega, L = find_subgroup(p, n)
    d = len(w_coeffs) - 1  # degree
    if t_threshold is None:
        t_threshold = d

    # Precompute w(ω^i) for each i
    w_vals = []
    for i in range(n):
        w_vals.append(eval_poly(w_coeffs, L[i], p))

    results = {}
    for h0 in range(p):
        for h1 in range(p):
            # Count agreement: w(ω^i) = h0 + h1*ω^i
            count = 0
            for i in range(n):
                h_val = (h0 + h1 * L[i]) % p
                if w_vals[i] == h_val:
                    count += 1
            if count >= t_threshold:
                results[(h0, h1)] = count

    return len(results), results

def elem_sym(roots, k, p):
    """Compute k-th elementary symmetric polynomial of roots mod p."""
    if k == 0:
        return 1
    result = 0
    for combo in combinations(roots, k):
        prod = 1
        for x in combo:
            prod = (prod * x) % p
        result = (result + prod) % p
    return result

# ============================================================
# Experiments
# ============================================================

def run_experiments():
    # We need p prime, n | (p-1), and n large enough for interesting t
    # Let's use p = 31, n = 6 (6 | 30), t = 3,4,5
    # And p = 37, n = 6 (6 | 36), t = 3,4,5
    # And p = 43, n = 6 (6 | 42), t = 3,4,5

    test_cases = []

    # --- p=31, n=6 ---
    # Binomial: w = x^4 + 3*x^3, t=4
    # General: w = x^4 + 3*x^3 + 2*x^2, t=4
    # General: w = x^4 + 3*x^3 + 2*x^2 + x, t=4  (note: x term overlaps with h1*x)

    p = 31
    for n in [5, 6, 10, 15]:
        if (p - 1) % n != 0:
            continue

        bound = n  # n/(t-1) when t varies

        # t = 3: degree 3 words
        # Binomial: x^3 + λx^2
        for lam in [1, 2, 3]:
            w = [0, 0, lam, 1]  # x^3 + lam*x^2
            test_cases.append((p, n, w, 3, f"p={p},n={n}: x^3+{lam}x^2 (binomial)"))

        # Trinomial: x^3 + λx^2 + μx^1  (but x^1 overlaps with h1!)
        # Actually wait - the overlap doesn't matter for counting,
        # because h1 is free. Let me think...
        # w(ω^i) - h0 - h1*ω^i = a3*ω^{3i} + a2*ω^{2i} + (a1-h1)*ω^i + (a0-h0)
        # The degree-3 polynomial has roots among L.
        # Vieta: e1 = -a2/a3, e2 = (a1-h1)/a3
        # So e1 is fixed, e2 varies with h1. Only 1 free parameter (not 2).
        # Wait, e3 = -(a0-h0)/a3 varies with h0. So 2 free: e2, e3.
        # And e1 = -a2/a3 is fixed.
        # For t=3: we have t-2 = 1 fixed condition (e1). Free: e2, e3.
        # Hmm but the polynomial is degree 3 with 3 roots, so 3 elem sym funcs,
        # of which 1 is fixed and 2 are free. That's the 2 params (h0, h1).

        # For t=4: degree 4 polynomial, 4 elem sym funcs.
        # Fixed: e1, e2. Free: e3 (from h1), e4 (from h0).
        # Binomial x^4 + λx^3: e1 = -λ, e2 = 0.
        # General x^4 + λx^3 + μx^2: e1 = -λ, e2 = μ.

        if n >= 4:
            for lam in [1]:
                # Binomial
                w = [0, 0, 0, lam, 1]  # x^4 + lam*x^3
                test_cases.append((p, n, w, 4, f"p={p},n={n}: x^4+{lam}x^3 (binomial)"))

                # Trinomial with x^2 term
                for mu in [1, 2]:
                    w = [0, 0, mu, lam, 1]  # x^4 + lam*x^3 + mu*x^2
                    test_cases.append((p, n, w, 4, f"p={p},n={n}: x^4+{lam}x^3+{mu}x^2 (trinomial)"))

                # Full: x^4 + lam*x^3 + mu*x^2 + nu*x + sigma
                # But nu*x and sigma overlap with h1*x + h0
                # Still: e1 = -lam, e2 = mu are fixed. e3, e4 free.
                for mu in [1]:
                    for nu in [1, 2]:
                        w = [0, nu, mu, lam, 1]  # x^4 + lam*x^3 + mu*x^2 + nu*x
                        test_cases.append((p, n, w, 4, f"p={p},n={n}: x^4+{lam}x^3+{mu}x^2+{nu}x"))

    # Also try p=37, n=9 (larger)
    p2 = 37
    for n2 in [6, 9, 12, 18]:
        if (p2 - 1) % n2 != 0:
            continue
        for lam in [1]:
            # Binomial t=4
            w = [0, 0, 0, lam, 1]
            test_cases.append((p2, n2, w, 4, f"p={p2},n={n2}: x^4+{lam}x^3 (binomial)"))
            # Trinomial t=4
            for mu in [1, 2]:
                w = [0, 0, mu, lam, 1]
                test_cases.append((p2, n2, w, 4, f"p={p2},n={n2}: x^4+{lam}x^3+{mu}x^2 (trinomial)"))

    # Now also try HIGHER DEGREE words with threshold t < degree
    # w of degree d > t, asking for at least t agreements
    p3 = 31
    n3 = 10
    if (p3 - 1) % n3 == 0:
        # degree 6 word, threshold t=4
        w = [0, 0, 0, 1, 0, 1, 1]  # x^6 + x^5 + x^3
        test_cases.append((p3, n3, w, 4, f"p={p3},n={n3}: x^6+x^5+x^3, t≥4 (d>t)"))

        # degree 8 word, threshold t=4
        w = [0, 0, 0, 0, 1, 0, 0, 0, 1]  # x^8 + x^4
        test_cases.append((p3, n3, w, 4, f"p={p3},n={n3}: x^8+x^4, t≥4 (d>t)"))

    print("=" * 80)
    print(f"{'Description':<55} {'M':>5} {'n/(t-1)':>8} {'ratio':>8}")
    print("=" * 80)

    for p, n, w_coeffs, t, desc in test_cases:
        M, details = compute_M(p, n, w_coeffs, t)
        bound = n / (t - 1)
        ratio = M / bound if bound > 0 else float('inf')
        marker = " ***" if ratio > 1.01 else ""
        print(f"{desc:<55} {M:>5} {bound:>8.2f} {ratio:>8.3f}{marker}")

        # Show agreement size distribution
        if details:
            size_dist = {}
            for (h0, h1), cnt in details.items():
                size_dist[cnt] = size_dist.get(cnt, 0) + 1
            dist_str = ", ".join(f"|S|={k}: {v}" for k, v in sorted(size_dist.items()))
            print(f"  └─ distribution: {dist_str}")

if __name__ == "__main__":
    run_experiments()
