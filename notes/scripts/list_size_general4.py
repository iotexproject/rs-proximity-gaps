"""
Final analysis:

1. t=3: M ≈ C(n,3)/p = n(n-1)(n-2)/(6p), NOT n/(t-1) = n/2.
   The bound M ≤ n/2 fails badly for large n.
   The correct bound is M = O(n^2/p + 1) ≈ O(n^3/p).

2. t≥4: M ≤ n/(t-1) seems to hold. Need to verify with larger cases
   and understand WHY t=3 is different.

3. The reason: for t=3, we have t-2 = 1 fixed condition (e1 = prescribed sum).
   A single additive constraint on a subset of L is very weak.
   For t=4, we have t-2 = 2 conditions (e1 and e2). The MULTIPLICATIVE structure
   of e2 (sum of products of pairs) interacts with the multiplicative structure of L,
   giving much more cancellation.

Key question: for t ≥ 4, is M ≤ n/(t-1) TIGHT (achieved)?

Also: the bound for general w (all coefficients) vs binomial —
for t≥4, we saw trinomial can sometimes beat binomial (p=31,n=10,t=4: trinom=2 vs binom=1).
But both stay ≤ n/(t-1).
"""

from itertools import combinations

def find_primitive_root(p):
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
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    L = []
    x = 1
    for _ in range(n):
        L.append(x)
        x = (x * omega) % p
    return omega, L

def elem_sym_k(elts, k, p):
    """k-th elementary symmetric polynomial of elts, mod p."""
    result = 0
    for combo in combinations(elts, k):
        prod = 1
        for x in combo:
            prod = (prod * x) % p
        result = (result + prod) % p
    return result

def t4_tightness():
    """Check when M = n/3 is achieved for t=4."""
    print("=" * 80)
    print("t=4: TIGHTNESS — when does M = n/3?")
    print("=" * 80)

    configs = [
        (31, 6), (31, 15), (31, 30),
        (37, 9), (37, 12), (37, 18), (37, 36),
        (41, 8), (41, 20), (41, 40),
        (61, 12), (61, 15), (61, 20), (61, 30), (61, 60),
    ]

    print(f"\n{'p':>4} {'n':>4} {'max_M':>6} {'n/3':>6} {'best (e1,e2)':>25} {'3|n?':>5} {'tight?':>7}")
    print("-" * 70)

    for p, n in configs:
        if (p - 1) % n != 0:
            continue
        omega, L = find_subgroup(p, n)

        all_counts = {}
        for combo in combinations(range(n), 4):
            elts = [L[i] for i in combo]
            s1 = sum(elts) % p
            s2 = elem_sym_k(elts, 2, p)
            key = (s1, s2)
            all_counts[key] = all_counts.get(key, 0) + 1

        max_count = max(all_counts.values())
        best_key = max(all_counts, key=all_counts.get)
        bound = n / 3
        divides = "yes" if n % 3 == 0 else "no"
        tight = "YES" if abs(max_count - bound) < 0.01 else "no"

        print(f"{p:>4} {n:>4} {max_count:>6} {bound:>6.1f} {str(best_key):>25} {divides:>5} {tight:>7}")

def t4_where_achieved():
    """For t=4, when M achieves n/3, what are the agreement sets?
    They should be unions of cosets of order-3 subgroup (after extraction)."""
    print("\n" + "=" * 80)
    print("t=4: STRUCTURE of maximizers")
    print("=" * 80)

    p, n = 37, 18
    omega, L = find_subgroup(p, n)
    print(f"p={p}, n={n}, ω={omega}")
    print(f"L = {L}")

    # Find order-3 subgroup of Z/18Z: {0, 6, 12}
    # Its cosets: {0,6,12}, {1,7,13}, {2,8,14}, {3,9,15}, {4,10,16}, {5,11,17}
    print(f"Order-3 subgroup of Z/{n}Z: {{0, 6, 12}}")
    print(f"Cosets: " + ", ".join(f"{{{i},{i+6},{i+12}}}" for i in range(6)))

    # Find 4-subsets with (e1, e2) maximizing count
    all_4subsets = {}
    for combo in combinations(range(n), 4):
        elts = [L[i] for i in combo]
        s1 = sum(elts) % p
        s2 = elem_sym_k(elts, 2, p)
        key = (s1, s2)
        if key not in all_4subsets:
            all_4subsets[key] = []
        all_4subsets[key].append(combo)

    # Find the key with max count
    best_key = max(all_4subsets, key=lambda k: len(all_4subsets[k]))
    print(f"\nBest (e1,e2) = {best_key}, count = {len(all_4subsets[best_key])}")

    for combo in all_4subsets[best_key]:
        elts = [L[i] for i in combo]
        # Check: is this {j*} ∪ (coset of order-3)?
        for idx in range(4):
            remaining = [combo[j] for j in range(4) if j != idx]
            # Is remaining a coset of order-3 subgroup?
            diffs = [(remaining[1] - remaining[0]) % n, (remaining[2] - remaining[0]) % n]
            is_coset = set(diffs) == {6, 12} or set(diffs) == {6, 0} or \
                       (remaining[1] - remaining[0]) % n == 6 and (remaining[2] - remaining[1]) % n == 6
            # More careful: order-3 coset is {a, a+6, a+12} mod 18
            a = remaining[0]
            is_coset = set(remaining) == {a, (a+6)%n, (a+12)%n}
            if is_coset:
                print(f"  {combo} = {{{combo[idx]}}} ∪ coset({a},{(a+6)%n},{(a+12)%n})")
                break
        else:
            print(f"  {combo} — NOT extraction+coset structure!")

def d_greater_than_t():
    """Case d > t: word has degree d > t, asking for ≥ t agreements.
    The polynomial w(x) - h0 - h1*x has degree d, can have up to d roots in L.
    We want ≥ t of them to be in L.

    Key difference: we're not requiring EXACTLY t roots. The polynomial has degree d,
    and some number of its roots (between t and d, possibly) lie in L.
    """
    print("\n" + "=" * 80)
    print("d > t CASE")
    print("=" * 80)

    from itertools import combinations

    def eval_poly(coeffs, x, p):
        result = 0
        xpow = 1
        for c in coeffs:
            result = (result + c * xpow) % p
            xpow = (xpow * x) % p
        return result

    # p=31, n=10, various degrees, threshold t=4
    p, n, t = 41, 20, 4
    if (p - 1) % n != 0:
        return

    g = find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    L = []
    x = 1
    for _ in range(n):
        L.append(x)
        x = (x * omega) % p

    bound = n / (t - 1)
    print(f"p={p}, n={n}, t={t}, n/(t-1)={bound:.2f}")

    # Try various degrees d > t
    import random
    random.seed(123)

    for d in [5, 6, 8, 10, 15]:
        max_M = 0
        # Sample random degree-d words
        for trial in range(100):
            w_coeffs = [random.randint(0, p-1) for _ in range(d)] + [1]  # monic degree d
            # Count M
            w_vals = [eval_poly(w_coeffs, L[i], p) for i in range(n)]
            M = 0
            for h0 in range(p):
                for h1 in range(p):
                    count = 0
                    for i in range(n):
                        if (w_vals[i] - h0 - h1 * L[i]) % p == 0:
                            count += 1
                    if count >= t:
                        M += 1
            max_M = max(max_M, M)

        exceeds = " ***EXCEEDS***" if max_M > bound * 1.01 else ""
        print(f"  d={d}: max M (over 100 random words) = {max_M}{exceeds}")

    # Also try: degree d word that is a PRODUCT of lower degree factors
    # e.g., w(x) = (x-a)(x-b)(x-c)(x-d) * q(x) where a,b,c,d ∈ L
    # Then for h0=0, h1=0 (if w has no constant or linear term... hmm)
    # Actually: w(x) - h0 - h1*x has roots a,b,c,d iff
    # w(a)=h0+h1*a, etc. If we choose w to have many roots in L...

    print("\n  Structured degree-d words (products of linear factors from L):")
    for d in [5, 6, 8]:
        max_M = 0
        for trial in range(50):
            # Choose d random elements of L, form w(x) = prod(x - L[i]) for random i
            indices = random.sample(range(n), min(d, n))
            roots = [L[i] for i in indices]
            # Build polynomial from roots
            # Start with [1], multiply by (x - r) for each r
            poly = [1]
            for r in roots:
                new_poly = [0] * (len(poly) + 1)
                for j, c in enumerate(poly):
                    new_poly[j+1] = (new_poly[j+1] + c) % p
                    new_poly[j] = (new_poly[j] - c * r) % p
                poly = new_poly
            # poly is now the coefficients [a0, a1, ..., a_d]
            w_coeffs = poly

            w_vals = [eval_poly(w_coeffs, L[i], p) for i in range(n)]
            M = 0
            for h0 in range(p):
                for h1 in range(p):
                    count = 0
                    for i in range(n):
                        if (w_vals[i] - h0 - h1 * L[i]) % p == 0:
                            count += 1
                    if count >= t:
                        M += 1
            max_M = max(max_M, M)

        exceeds = " ***EXCEEDS***" if max_M > bound * 1.01 else ""
        print(f"  d={d} (products): max M (over 50 trials) = {max_M}{exceeds}")

if __name__ == "__main__":
    t4_tightness()
    t4_where_achieved()
    d_greater_than_t()
