"""
Investigate what distinguishes non-alignment primes from alignment primes.

For n=36: non-alignment at p=37,181; alignment at p=73,109,397,...
For n=48: non-alignment at p=97; alignment at p=193,241,...

Hypotheses to test:
  H1: related to gcd((p-1)/n, n)
  H2: related to order of some element mod p
  H3: related to splitting of x^6+1 or x^4+1 mod p
  H4: related to number of solutions of x^n = 1 with extra constraints
"""
from math import gcd
from collections import defaultdict

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

def factorize(n):
    """Full factorization as list of (prime, exponent)."""
    out = []; d = 2; nn = n
    while d * d <= nn:
        if nn % d == 0:
            e = 0
            while nn % d == 0: e += 1; nn //= d
            out.append((d, e))
        d += 1
    if nn > 1: out.append((nn, 1))
    return out

def multiplicative_order(a, n):
    """Order of a in (Z/nZ)*."""
    if gcd(a, n) != 1: return None
    o = 1; x = a % n
    while x != 1:
        x = (x * a) % n
        o += 1
        if o > n: return None
    return o

def num_roots_mod_p(poly_coeffs, p):
    """Count roots of polynomial in F_p. poly_coeffs[i] = coeff of x^i."""
    count = 0
    for x in range(p):
        val = 0; xpow = 1
        for c in poly_coeffs:
            val = (val + c * xpow) % p
            xpow = (xpow * x) % p
        if val == 0:
            count += 1
    return count

def legendre(a, p):
    return pow(a, (p-1)//2, p)

def analyze_n36():
    n = 36
    # All primes p ≡ 1 (mod 36) up to 2000
    primes = [p for p in range(37, 5001) if p % n == 1 and is_prime(p)]
    non_alignment = {37, 181}  # known from sweep

    print(f"=== n={n} ===")
    print(f"{'p':>6} {'ratio':>6} {'gcd_r_n':>7} {'fact(ratio)':>20} "
          f"{'#roots x^6+1':>12} {'#roots x^4+1':>12} {'#roots x^6-x':>13} "
          f"{'leg(-1)':>7} {'leg(-3)':>7} {'leg(5)':>6} {'NON?':>5}")
    print("-" * 130)

    for p in primes:
        ratio = (p - 1) // n
        g = gcd(ratio, n)
        fact = factorize(ratio)
        fact_str = "*".join(f"{b}^{e}" if e > 1 else str(b) for b, e in fact) if fact else "1"

        # number of roots of various polynomials mod p
        # x^6 + 1: coeffs [1, 0, 0, 0, 0, 0, 1]
        r_x6p1 = num_roots_mod_p([1, 0, 0, 0, 0, 0, 1], p)
        # x^4 + 1
        r_x4p1 = num_roots_mod_p([1, 0, 0, 0, 1], p)
        # x^6 - x
        r_x6mx = num_roots_mod_p([0, -1, 0, 0, 0, 0, 1], p)

        leg_m1 = legendre(p - 1, p)  # (-1/p)
        leg_m3 = legendre(p - 3, p)  # (-3/p)
        leg_5 = legendre(5, p)       # (5/p)

        is_non = "YES" if p in non_alignment else ""

        print(f"{p:>6} {ratio:>6} {g:>7} {fact_str:>20} "
              f"{r_x6p1:>12} {r_x4p1:>12} {r_x6mx:>13} "
              f"{leg_m1:>7} {leg_m3:>7} {leg_5:>6} {is_non:>5}")

def analyze_n48():
    n = 48
    primes = [p for p in range(97, 3001) if p % n == 1 and is_prime(p)]
    non_alignment = {97}

    print(f"\n=== n={n} ===")
    print(f"{'p':>6} {'ratio':>6} {'gcd_r_n':>7} {'fact(ratio)':>20} "
          f"{'#roots x^6+1':>12} {'#roots x^4+1':>12} "
          f"{'leg(-1)':>7} {'leg(-3)':>7} {'NON?':>5}")
    print("-" * 110)

    for p in primes:
        ratio = (p - 1) // n
        g = gcd(ratio, n)
        fact = factorize(ratio)
        fact_str = "*".join(f"{b}^{e}" if e > 1 else str(b) for b, e in fact) if fact else "1"

        r_x6p1 = num_roots_mod_p([1, 0, 0, 0, 0, 0, 1], p)
        r_x4p1 = num_roots_mod_p([1, 0, 0, 0, 1], p)

        leg_m1 = legendre(p - 1, p)
        leg_m3 = legendre(p - 3, p)

        is_non = "YES" if p in non_alignment else ""

        print(f"{p:>6} {ratio:>6} {g:>7} {fact_str:>20} "
              f"{r_x6p1:>12} {r_x4p1:>12} "
              f"{leg_m1:>7} {leg_m3:>7} {is_non:>5}")

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

def deeper_analysis_n36():
    """
    Deeper: for n=36, the CS polynomial is x^6 + λx^4 - h1*x - h0.
    The conditions for non-aligned S are e1=e3=e4=0.

    Using Newton's identities: p_k = Σ α_i^k (power sums).
    e1=0 ⟹ p1=0.
    e3=0, e4=0 relate to p1,p2,p3,p4.

    Actually, from Note 0002: the Newton-symmetric conditions are
    p_j(S) = 0 for j ∈ {1,...,2m-1} \ {m} = {1,3} (since m=2).
    Plus p_2(S) = -2λ (determines λ), p_4(S) determines h.

    Wait, let me re-derive. For S = {α1,...,α6} roots of x^6 + a4*x^4 + a1*x + a0:
    By Vieta: e1=0, e2=a4, e3=0, e4=0, e5=-a1, e6=a0.

    Power sums via Newton:
    p1 = e1 = 0
    p2 = e1*p1 - 2*e2 = -2*a4 = -2λ
    p3 = e1*p2 - e2*p1 + 3*e3 = 0
    p4 = e1*p3 - e2*p2 + e3*p1 - 4*e4 = -e2*p2 = -a4*(-2a4) = 2a4^2 = 2λ^2

    So the conditions are:
    p1(S) = Σ αi = 0
    p3(S) = Σ αi^3 = 0
    p4(S) = 2λ^2 where λ = -p2(S)/2

    But p4 is determined by λ, so the INDEPENDENT conditions are just p1=0 and p3=0.

    For S ⊂ L = {ω^0,...,ω^{n-1}}:
    p_j(S) = Σ_{i∈S} ω^{ij} (power sum of n-th roots of unity selected by S).

    So the conditions are:
    Σ_{i∈S} ω^i = 0  (p1=0)
    Σ_{i∈S} ω^{3i} = 0  (p3=0)

    These are DFT conditions! The "syndrome" at frequencies 1 and 3 must vanish.

    For a 6-element subset S of Z/36Z, ω^i are elements of F_p.
    The condition Σ ω^i = 0 (sum over i∈S) and Σ ω^{3i} = 0 depend on WHERE
    ω^1 and ω^3 land in F_p.

    Key insight: ω^3 has order 36/gcd(3,36) = 36/3 = 12 in F_p.
    And ω itself has order 36.

    So the conditions are about 6-element subsets of the cyclic group C_36
    whose "character sums" at characters χ^1 and χ^3 vanish.

    For aligned S (union of cosets of some subgroup H of C_36):
    The character sum Σ_{s∈S} χ(s) vanishes for any character χ that is
    non-trivial on S (which happens when χ is non-trivial on each coset).

    For non-aligned S: the vanishing is "accidental" — a cancellation that
    depends on the specific embedding ω ↦ F_p.

    When does ω change the structure? When p changes, ω changes (it's a
    different primitive 36th root of unity in a different field). The
    "positions" of roots on the unit circle change, affecting which
    cancellations are possible.
    """
    n = 36
    print(f"\n=== Deeper analysis: character-sum conditions for n={n} ===")
    print("Conditions for 6-element S ⊂ C_36: Σ_{i∈S} ω^i = 0 AND Σ_{i∈S} ω^{3i} = 0")
    print()

    # For each prime, count the number of 6-element subsets S ⊂ {0,...,35}
    # such that Σ ω^i = 0 and Σ ω^{3i} = 0 in F_p
    # (These are the "variety points")

    primes_to_test = [37, 73, 109, 181, 397, 433]

    nf = prime_factors(n)

    for p in primes_to_test:
        # find omega
        pf = prime_factors(p - 1)
        omega = None
        for g in range(2, p):
            if all(pow(g, (p-1)//q, p) != 1 for q in pf):
                omega = pow(g, (p-1)//n, p)
                break
        assert omega is not None and pow(omega, n, p) == 1

        # precompute ω^i and ω^{3i}
        w1 = [pow(omega, i, p) for i in range(n)]
        w3 = [pow(omega, 3*i, p) for i in range(n)]

        # Count 6-element subsets with p1=0 and p3=0
        # This is C(36,6) ≈ 1.9M, feasible
        from itertools import combinations
        count_both = 0
        count_p1_only = 0
        aligned_count = 0
        non_aligned_count = 0

        for S in combinations(range(n), 6):
            s1 = sum(w1[i] for i in S) % p
            s3 = sum(w3[i] for i in S) % p
            if s1 == 0 and s3 == 0:
                count_both += 1
                if is_subgroup_aligned(set(S), n) is not None:
                    aligned_count += 1
                else:
                    non_aligned_count += 1
            elif s1 == 0:
                count_p1_only += 1

        ratio = (p - 1) // n
        print(f"p={p:>5} ratio={ratio:>3} | "
              f"#(p1=p3=0)={count_both:>5} "
              f"(aligned={aligned_count}, non-aligned={non_aligned_count}) | "
              f"#(p1=0 only)={count_p1_only}", flush=True)

if __name__ == "__main__":
    analyze_n36()
    analyze_n48()
    deeper_analysis_n36()
