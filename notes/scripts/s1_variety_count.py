"""
Count F_p-rational points of the variety V_{36,2,3}:
  6-element subsets S ⊂ L (order-36 subgroup) with e1=e3=e4=0.

Equivalently: p1=0, p3=0, p4 = p2^2 * (2^{-1} mod p).

This should EXACTLY match the sweep witness count.
Also do S4 (Lang-Weil): vary p, count variety points, fit dimension.
"""
from itertools import combinations
from math import gcd

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
    nf = prime_factors(n)
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in pf):
            omega = pow(g, (p-1)//n, p)
            assert pow(omega, n, p) == 1
            assert all(pow(omega, n//q, p) != 1 for q in nf)
            return omega
    raise RuntimeError(f"no primitive root mod {p}")

def modinv(a, p):
    return pow(a, p - 2, p)

def divisors(n):
    return [d for d in range(1, n+1) if n % d == 0]

def cosets_of_index_subgroup(n, d):
    step = n // d
    H = [(i * step) % n for i in range(d)]
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

def count_variety_points(p, n=36, m=2, r=3):
    """Count 6-element S ⊂ L with e1=e3=e4=0."""
    threshold = r * m  # = 6
    omega = find_omega(p, n)

    # precompute powers
    w = [[pow(omega, k * i, p) for i in range(n)] for k in range(5)]
    # w[k][i] = ω^{ki}

    inv2 = modinv(2, p)
    aligned = 0
    non_aligned = 0

    for S in combinations(range(n), threshold):
        # power sums
        p1 = sum(w[1][i] for i in S) % p
        if p1 != 0: continue

        p3 = sum(w[3][i] for i in S) % p
        if p3 != 0: continue

        # check e4 = 0 ⟺ p4 = p2^2 / 2
        p2 = sum(w[2][i] for i in S) % p
        p4 = sum(w[4][i] for i in S) % p
        e4_zero = (p4 == (p2 * p2 % p) * inv2 % p)
        if not e4_zero: continue

        if is_subgroup_aligned(set(S), n) is not None:
            aligned += 1
        else:
            non_aligned += 1

    return aligned, non_aligned

def main():
    n = 36

    # primes p ≡ 1 (mod 36) up to ~2000
    primes = [p for p in range(37, 2001) if p % n == 1 and is_prime(p)]

    print(f"Variety V_{{36,2,3}} point count: e1=e3=e4=0 on C(36,6) subsets")
    print(f"{'p':>6} {'ratio':>6} {'aligned':>8} {'non-aln':>8} {'total':>8} {'match_sweep?':>12}")
    print("-" * 60)

    # known sweep results for comparison
    sweep_not = {37: 36, 73: 0, 109: 0, 181: 36}

    for p in primes:
        ratio = (p - 1) // n
        aln, non = count_variety_points(p, n)
        total = aln + non
        # check against sweep
        if p in sweep_not:
            match = "YES" if non == sweep_not[p] else f"NO(sweep={sweep_not[p]})"
        else:
            match = ""
        print(f"{p:>6} {ratio:>6} {aln:>8} {non:>8} {total:>8} {match:>12}", flush=True)

    # S4: Lang-Weil analysis
    # For the NON-ALIGNED count, fit to C * p^d
    # If d=0, the count is bounded ⟹ variety has dimension 0 over Q
    print("\n--- S4: Lang-Weil dimension fitting ---")
    print("If #non-aligned ~ C * p^d, what is d?")
    print("Collect (p, #non-aligned) pairs with non-aligned > 0:")

if __name__ == "__main__":
    main()
