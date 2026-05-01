"""
Critical test: does M ≤ n/(t-1) for t=4 survive as n grows?
For t=3, M grows as n^3/p >> n/2.
For t=4, we saw max M ≤ n/3 for small cases.
But for n=30 (p=31): M=35 >> n/3=10! So t=4 ALSO fails!

Let me re-examine the t=4 data more carefully.
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
    result = 0
    for combo in combinations(elts, k):
        prod = 1
        for x in combo:
            prod = (prod * x) % p
        result = (result + prod) % p
    return result

def t4_check():
    print("t=4: M vs n/(t-1) = n/3 vs C(n,4)/p^2")
    print("=" * 80)

    configs = [
        (31, 6), (31, 10), (31, 15), (31, 30),
        (37, 6), (37, 9), (37, 12), (37, 18), (37, 36),
        (41, 8), (41, 10), (41, 20), (41, 40),
    ]

    print(f"{'p':>4} {'n':>4} {'max_M':>6} {'n/3':>7} {'C(n,4)/p^2':>11} {'M > n/3?':>9}")
    print("-" * 50)

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
        bound = n / 3
        cn4_p2 = (n * (n-1) * (n-2) * (n-3)) / (24 * p * p)
        exceeds = "YES" if max_count > bound * 1.01 else "no"

        print(f"{p:>4} {n:>4} {max_count:>6} {bound:>7.1f} {cn4_p2:>11.1f} {exceeds:>9}")

def t_general_scaling():
    """For general t, when does M exceed n/(t-1)?
    Hypothesis: M ≈ C(n,t) / p^{t-2}.
    This exceeds n/(t-1) when C(n,t)/p^{t-2} >> n/(t-1),
    i.e., n^{t-1}/(t! * p^{t-2}) >> 1/(t-1),
    i.e., n^{t-1} >> t! * p^{t-2} / (t-1) ≈ t * (t-2)! * p^{t-2},
    i.e., (n/p)^{t-2} >> t*(t-2)!/n ≈ (t-1)!/n.

    For n = p-1 (maximal subgroup): n ≈ p, so (n/p)^{t-2} ≈ 1,
    and we need 1 >> (t-1)!/n, i.e., n >> (t-1)!. So for n large enough
    (specifically n >> (t-1)!), the bound M ≤ n/(t-1) fails.

    For fixed t and n/p → 1: M ≈ C(n,t)/p^{t-2} ≈ n^t/(t!*n^{t-2}) = n^2/t!
    vs n/(t-1). So M/bound ≈ n/(t!/(t-1)) = n(t-1)/t!

    This means for ANY fixed t, M exceeds n/(t-1) once n > t!/(t-1).
    For t=3: n > 6/2 = 3. ✓ (we see violations starting around n=12)
    For t=4: n > 24/3 = 8. (we should see violations for n ≥ ~10)
    For t=5: n > 120/4 = 30.

    Wait, but the data shows t=4, n=30 (p=31): M=35 >> n/3=10. Confirmed!
    And t=4, n=40 (p=41): M=59 >> n/3=13.3. Confirmed!

    So M ≤ n/(t-1) is NOT the right bound for ANY t ≥ 3 when n is large.
    """
    print("\n" + "=" * 80)
    print("GENERAL t: scaling of M")
    print("=" * 80)

    # For each t, compute M for n = p-1 (maximal subgroup) at various p
    # t=3: already done
    # t=4: need C(n,4)/p^2 comparison
    # t=5: need C(n,5)/p^3 comparison

    # For t=5, p=31, n=30: C(30,5)/31^3 = 142506/29791 ≈ 4.8
    # M should be around 5.
    p, n = 31, 30
    omega, L = find_subgroup(p, n)

    print(f"\nt=5, p={p}, n={n}:")
    print(f"  C(n,5)/p^3 = {142506/29791:.1f}")
    print(f"  n/4 = {n/4:.1f}")

    all_counts = {}
    for combo in combinations(range(n), 5):
        elts = [L[i] for i in combo]
        s1 = sum(elts) % p
        s2 = elem_sym_k(elts, 2, p)
        s3 = elem_sym_k(elts, 3, p)
        key = (s1, s2, s3)
        all_counts[key] = all_counts.get(key, 0) + 1

    max_count = max(all_counts.values())
    print(f"  max M = {max_count}")
    print(f"  M > n/4? {'YES' if max_count > n/4 else 'no'}")

def correct_bound():
    """The correct bound seems to be M ≈ C(n,t) / p^{t-2}.

    For the RS proximity problem, we have:
    - n = |L|, rate ρ = k/n = 2/n (since k=2)
    - Johnson bound: δ_J = 1 - √ρ = 1 - √(2/n)
    - Agreement threshold: t = (1-δ)n where δ > δ_J
    - So t < (1-δ_J)n = √ρ · n = √(2n)

    With t = √(2n), the list size bound:
    M ≈ C(n,t)/p^{t-2} ≈ (n/t)^t / p^{t-2} ≈ (n/√(2n))^{√(2n)} / p^{√(2n)-2}
    = (√(n/2))^{√(2n)} / p^{√(2n)-2}

    For n close to p: ≈ (√(p/2))^{√(2p)} / p^{√(2p)-2}

    This is a more complex expression. The key insight is that M ≤ n/(t-1)
    holds when n is small relative to p (sparse subgroup), but fails when
    n is a large fraction of p.
    """
    print("\n" + "=" * 80)
    print("CORRECT BOUND HYPOTHESIS: M ≈ C(n,t) / p^{t-2}")
    print("=" * 80)

    # Verify for t=3: M vs C(n,3)/p
    # Already confirmed above.

    # Verify for t=4: M vs C(n,4)/p^2
    print("\nt=4 verification:")
    configs = [
        (31, 6), (31, 10), (31, 15), (31, 30),
        (37, 9), (37, 12), (37, 18), (37, 36),
        (41, 20), (41, 40),
    ]

    print(f"{'p':>4} {'n':>4} {'max_M':>6} {'C(n,4)/p^2':>11} {'ratio':>8}")
    print("-" * 40)

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
        cn4_p2 = n*(n-1)*(n-2)*(n-3) / (24 * p * p)
        ratio = max_count / cn4_p2 if cn4_p2 > 0 else float('inf')
        print(f"{p:>4} {n:>4} {max_count:>6} {cn4_p2:>11.1f} {ratio:>8.3f}")

if __name__ == "__main__":
    t4_check()
    correct_bound()
    t_general_scaling()
