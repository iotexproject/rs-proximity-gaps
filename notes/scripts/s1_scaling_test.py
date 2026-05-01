"""
Path B: does per-word list size stay O(1) as n grows?

For each n ∈ {36, 48, 60, 72, 96, 120}, pick p ≡ 1 (mod n) with p ≈ 2n,
test several (a,b) pairs, record max per-word list size.

Key: for k=2, the Lagrange trick costs O(p * n^2) per word.
Total: O(p^2 * n^2) per (a,b) pair.

Also test: for the WORST (a,b) found per n, what's the max list size?
"""
from math import gcd
from multiprocessing import Pool, cpu_count

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0: return False
        d += 6
    return True

def prime_factors(n):
    out = set(); d = 2; nn = n
    while d * d <= nn:
        while nn % d == 0: out.add(d); nn //= d
        d += 1
    if nn > 1: out.add(nn)
    return list(out)

def find_omega(p, n):
    pf = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in pf):
            return pow(g, (p-1)//n, p)
    raise RuntimeError

def modinv(a, p): return pow(a, p - 2, p)

def divisors(n): return [d for d in range(1, n+1) if n % d == 0]

def cosets_of_index_subgroup(n, d):
    step = n // d; H = [(i * step) % n for i in range(d)]
    seen = set(); out = []
    for t in range(step):
        c = tuple(sorted((t + h) % n for h in H))
        if c not in seen: seen.add(c); out.append(c)
    return out

def is_subgroup_aligned(S_set, n):
    for d in divisors(n):
        if d == 1 or d == n: continue
        if len(S_set) % d != 0: continue
        cs = cosets_of_index_subgroup(n, d)
        covered = [c for c in cs if set(c).issubset(S_set)]
        if covered and sum(len(c) for c in covered) == len(S_set):
            return d
    return None

def find_proper_prime(n, min_ratio=2):
    """Find smallest prime p ≡ 1 (mod n) with (p-1)/n ≥ min_ratio."""
    p = n * min_ratio + 1
    while True:
        if p % n == 1 and is_prime(p):
            return p
        p += 1

def sweep_word_k2(w_vals, L, n, p, threshold):
    """For word w, find all degree-<2 polynomials agreeing on ≥ threshold points.
    Returns list of (agreement_size, is_non_aligned)."""
    results = []
    seen_h = {}
    for i in range(n):
        for j in range(i + 1, n):
            dx = (L[i] - L[j]) % p
            dy = (w_vals[i] - w_vals[j]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (w_vals[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen_h: continue
            agree_set = set()
            for idx in range(n):
                if (h0 + h1 * L[idx]) % p == w_vals[idx]:
                    agree_set.add(idx)
            seen_h[key] = len(agree_set)
            if len(agree_set) >= threshold:
                na = 1 if is_subgroup_aligned(agree_set, n) is None else 0
                results.append((len(agree_set), na))
    return results

def test_ab_pair(args):
    """Test one (a,b) pair at one prime."""
    a, b, p, n, omega, threshold = args
    L = [pow(omega, i, p) for i in range(n)]

    max_list = 0
    max_list_not = 0
    total_wits = 0
    total_not = 0
    n_lam_with_wits = 0

    for lam in range(p):
        w_vals = [(pow(L[i], a, p) + lam * pow(L[i], b, p)) % p for i in range(n)]
        wits = sweep_word_k2(w_vals, L, n, p, threshold)
        if wits:
            n_lam_with_wits += 1
            list_size = len(wits)
            not_aligned = sum(na for _, na in wits)
            max_list = max(max_list, list_size)
            max_list_not = max(max_list_not, not_aligned)
            total_wits += list_size
            total_not += not_aligned

    return (a, b, total_wits, total_not, max_list, max_list_not, n_lam_with_wits)

def main():
    threshold = 6  # rm = 6 for CS with m=2, r=3

    # (a,b) pairs to test: CS + worst cases from n=36 analysis
    ab_pairs = [
        (6, 4),   # CS
        (6, 5),   # close to CS
        (7, 6),   # worst at n=36 (non-alignment at all p)
        (8, 5),   # high per-word list size at n=36
        (8, 7),   # another a=b+1 pair
        (10, 9),  # another a=b+1 pair
        (12, 11), # a=b+1 with larger a
    ]

    # n values and corresponding primes
    test_cases = []
    for n in [36, 48, 60, 72, 96, 120]:
        # use a "proper subgroup" prime (not n=p-1)
        p = find_proper_prime(n, min_ratio=2)
        # also test full-group prime
        p_full = n + 1
        while not is_prime(p_full): p_full += n
        test_cases.append((n, p, (p-1)//n))
        if p_full != p and (p_full - 1 == n):
            test_cases.append((n, p_full, 1))

    print(f"=== Path B: Per-word list size scaling ===")
    print(f"threshold={threshold}, k=2")
    print(f"Testing {len(ab_pairs)} (a,b) pairs at {len(test_cases)} (n,p) settings\n")

    for n, p, ratio in test_cases:
        omega = find_omega(p, n)

        print(f"--- n={n}, p={p}, (p-1)/n={ratio} ---")
        print(f"  {'(a,b)':>8} {'total':>7} {'NOT':>5} {'max_L':>6} {'max_NOT':>8} {'#λ_bad':>7}")

        for a, b in ab_pairs:
            if a > n: continue
            result = test_ab_pair((a, b, p, n, omega, threshold))
            a2, b2, tot, not_a, ml, mln, nlam = result
            if tot > 0:
                print(f"  ({a:>2},{b:>2}) {tot:>7} {not_a:>5} {ml:>6} {mln:>8} {nlam:>7}")

        print()

    # Summary: extract max per-word list size per n
    print("=== SUMMARY: max per-word list size by n ===")
    print(f"{'n':>4} {'p':>6} {'ratio':>6} {'max_L_overall':>14} {'worst_(a,b)':>12}")
    for n, p, ratio in test_cases:
        omega = find_omega(p, n)
        best_ml = 0
        best_ab = None
        for a, b in ab_pairs:
            if a > n: continue
            _, _, _, _, ml, _, _ = test_ab_pair((a, b, p, n, omega, threshold))
            if ml > best_ml:
                best_ml = ml
                best_ab = (a, b)
        print(f"{n:>4} {p:>6} {ratio:>6} {best_ml:>14} {str(best_ab):>12}")

if __name__ == "__main__":
    main()
