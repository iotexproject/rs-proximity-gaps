"""
Focused investigation:
1. The bound M ≤ n/(t-1) FAILS for t=3 when (t-1)=2 does not divide n.
   But even when 2|n, it can fail (p=37, n=12, t=3: M=7 > 6).
2. For t≥4, the bound seems to hold. Why?
3. What is the TRUE bound for t=3?

Key insight: for t=3, the agreement polynomial is degree 3 with 3 roots in L.
  x^3 + a2*x^2 + (a1-h1)*x + (a0-h0) = 0
  e1 = -a2 (fixed), e2 = a1-h1 (free via h1), e3 = -(a0-h0) (free via h0)

So ANY 3-subset {α,β,γ} ⊂ L with α+β+γ = -a2 gives a valid (h0,h1).
M = #{3-subsets of L with prescribed sum}.

For the BINOMIAL x^3 + λx^2: e1 = -λ.
M = #{3-subsets of L summing to -λ}.

This is a classic additive combinatorics question!
"""

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

def count_3subsets_with_sum(L, target, p):
    """Count 3-element subsets of L summing to target mod p."""
    count = 0
    n = len(L)
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n):
                if (L[i] + L[j] + L[k]) % p == target:
                    count += 1
    return count

def analyze_t3():
    """For t=3, M = #{3-subsets of L with given sum}. Study this."""
    print("=" * 80)
    print("t=3 ANALYSIS: M = #{3-subsets of L summing to target}")
    print("=" * 80)

    configs = [
        (31, 5), (31, 6), (31, 10), (31, 15), (31, 30),
        (37, 6), (37, 9), (37, 12), (37, 18), (37, 36),
        (41, 8), (41, 10), (41, 20), (41, 40),
        (43, 6), (43, 7), (43, 14), (43, 21), (43, 42),
        (61, 10), (61, 12), (61, 15), (61, 20), (61, 30), (61, 60),
    ]

    print(f"\n{'p':>4} {'n':>4} {'max_M':>6} {'n/(t-1)':>8} {'n^2/6':>8} {'C(n,3)/p':>10} {'ratio_to_n2/6':>14}")
    print("-" * 70)

    for p, n in configs:
        if (p - 1) % n != 0:
            continue
        omega, L = find_subgroup(p, n)

        # Count 3-subsets for each possible sum
        max_count = 0
        sum_counts = {}
        for target in range(p):
            c = count_3subsets_with_sum(L, target, p)
            sum_counts[target] = c
            if c > max_count:
                max_count = c

        bound1 = n / 2  # n/(t-1)
        bound2 = n * n / 6  # heuristic: C(n,3)/n ≈ n^2/6
        cn3_over_p = n * (n-1) * (n-2) / (6 * p)

        print(f"{p:>4} {n:>4} {max_count:>6} {bound1:>8.1f} {bound2:>8.1f} {cn3_over_p:>10.1f} {max_count/bound2 if bound2>0 else 0:>14.3f}")

        # Also show: is the maximum achieved at target=0?
        # And: distribution of counts
        counts_list = sorted(sum_counts.values())
        min_c = counts_list[0]
        max_c = counts_list[-1]
        avg_c = sum(counts_list) / len(counts_list)
        # Check: total should be C(n,3)
        total = sum(counts_list)
        assert total == n * (n-1) * (n-2) // 6, f"total={total}, C(n,3)={n*(n-1)*(n-2)//6}"

def analyze_t4_bound():
    """For t=4, check if M ≤ n/(t-1) = n/3 always holds."""
    print("\n" + "=" * 80)
    print("t=4 ANALYSIS: does M ≤ n/3 hold?")
    print("=" * 80)

    # For t=4, agreement polynomial: x^4 + a3*x^3 + a2*x^2 + (a1-h1)*x + (a0-h0)
    # Fixed: e1 = -a3, e2 = a2
    # Free: e3 (via h1), e4 (via h0)
    # So M = #{4-subsets of L with prescribed e1 AND e2}
    # = #{4-subsets with prescribed sum AND prescribed sum-of-products-of-pairs}

    configs = [
        (31, 6), (31, 10), (31, 15),
        (37, 9), (37, 12), (37, 18),
        (41, 8), (41, 10), (41, 20),
    ]

    for p, n in configs:
        if (p - 1) % n != 0:
            continue
        omega, L = find_subgroup(p, n)
        bound = n / 3

        # For each (e1, e2), count 4-subsets of L
        # with that prescribed (sum, sum-of-pairs)
        from itertools import combinations
        max_count = 0
        best_e1e2 = None
        all_counts = {}

        for combo in combinations(range(n), 4):
            elts = [L[i] for i in combo]
            s1 = sum(elts) % p  # = e1
            s2 = 0  # = e2
            for i in range(4):
                for j in range(i+1, 4):
                    s2 = (s2 + elts[i] * elts[j]) % p
            key = (s1, s2)
            all_counts[key] = all_counts.get(key, 0) + 1

        max_count = max(all_counts.values())
        best_key = max(all_counts, key=all_counts.get)

        exceeds = " ***EXCEEDS***" if max_count > bound * 1.01 else ""
        print(f"p={p}, n={n}: max M = {max_count}, n/3 = {bound:.2f}, "
              f"best at (e1,e2)={best_key}{exceeds}")

def analyze_t5_bound():
    """For t=5, check M ≤ n/4."""
    print("\n" + "=" * 80)
    print("t=5 ANALYSIS: does M ≤ n/4 hold?")
    print("=" * 80)

    configs = [
        (31, 10), (31, 15),
        (37, 12), (37, 18),
        (41, 20),
    ]

    for p, n in configs:
        if (p - 1) % n != 0:
            continue
        omega, L = find_subgroup(p, n)
        bound = n / 4

        from itertools import combinations
        all_counts = {}

        for combo in combinations(range(n), 5):
            elts = [L[i] for i in combo]
            s1 = sum(elts) % p
            s2 = 0
            for i in range(5):
                for j in range(i+1, 5):
                    s2 = (s2 + elts[i] * elts[j]) % p
            s3 = 0
            for i in range(5):
                for j in range(i+1, 5):
                    for k in range(j+1, 5):
                        s3 = (s3 + elts[i] * elts[j] * elts[k]) % p
            key = (s1, s2, s3)
            all_counts[key] = all_counts.get(key, 0) + 1

        max_count = max(all_counts.values())
        best_key = max(all_counts, key=all_counts.get)

        exceeds = " ***EXCEEDS***" if max_count > bound * 1.01 else ""
        print(f"p={p}, n={n}: max M = {max_count}, n/4 = {bound:.2f}, "
              f"best at (e1,e2,e3)={best_key}{exceeds}")

def understand_t3_combinatorics():
    """For t=3, M is just C(n,3)/p (approximately) if L is 'generic'.
    But L is NOT generic — it's a multiplicative subgroup.
    The question: what's the max number of 3-subsets of a mult subgroup summing to a given value?

    Key: for n close to p, this is ~n^2/6. For n << p, this should be ~n^2/(6p)·p = n^2/6... no.
    Actually C(n,3)/p ≈ n^3/(6p). For n|p-1, the expected count per target is C(n,3)/(p) if
    sums are uniform mod p, but they might not be since L ⊂ F_p*.

    But wait: we count over ALL targets, not just those in L.
    So for large n/p ratio, concentration effects dominate.
    """
    print("\n" + "=" * 80)
    print("t=3: UNDERSTANDING THE CORRECT BOUND")
    print("=" * 80)

    # Key test: C(n,3)/p vs actual max
    configs = [
        (31, 5), (31, 6), (31, 10), (31, 15), (31, 30),
        (37, 6), (37, 9), (37, 12), (37, 18), (37, 36),
        (41, 8), (41, 10), (41, 20), (41, 40),
        (61, 10), (61, 12), (61, 15), (61, 20), (61, 30), (61, 60),
        (67, 6), (67, 11), (67, 22), (67, 33), (67, 66),
    ]

    print(f"\n{'p':>4} {'n':>4} {'max_M':>6} {'C(n,3)/p':>9} {'n/2':>6} {'n^2/p':>7} {'actual/Cn3p':>12}")
    print("-" * 65)

    for p, n in configs:
        if (p - 1) % n != 0:
            continue
        omega, L = find_subgroup(p, n)

        max_count = 0
        for target in range(p):
            c = count_3subsets_with_sum(L, target, p)
            max_count = max(max_count, c)

        cn3 = n * (n-1) * (n-2) // 6
        cn3_p = cn3 / p
        ratio = max_count / cn3_p if cn3_p > 0 else 0

        print(f"{p:>4} {n:>4} {max_count:>6} {cn3_p:>9.1f} {n/2:>6.1f} {n*n/p:>7.2f} {ratio:>12.3f}")

if __name__ == "__main__":
    analyze_t3()
    analyze_t4_bound()
    analyze_t5_bound()
    understand_t3_combinatorics()
