"""
Enumerate all 6-element non-aligned S ⊂ Z/36Z with 0∈S and e_3(S) = 0
identically in Z[ζ_36]. Then compute Norm(e_1) and Norm(e_4) to find
all non-alignment primes.

Key finding from norm computation:
  - Non-aligned witnesses at p=37,181 all have Norm(e_3) = 0
  - This means e_3 = 0 as identity in Z[ζ_36], not just mod p
  - Only e_1 and e_4 are nonzero; they vanish mod p for specific p
  - The non-alignment primes are exactly the common prime divisors
    of Norm(e_1) and Norm(e_4) that are ≡ 1 (mod 36)
"""
import cmath
from math import pi, gcd
from itertools import combinations
from functools import reduce
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

def factorize(n):
    if n == 0: return "0"
    neg = n < 0
    if neg: n = -n
    out = []; d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0: e += 1; n //= d
            out.append((d, e))
        d += 1
    if n > 1: out.append((n, 1))
    s = "*".join(f"{b}^{e}" if e > 1 else str(b) for b, e in out) if out else "1"
    return ("-" + s) if neg else s

def prime_factors_list(n):
    if n == 0: return []
    if n < 0: n = -n
    out = []; d = 2
    while d * d <= n:
        if n % d == 0:
            while n % d == 0: n //= d
            out.append(d)
        d += 1
    if n > 1: out.append(n)
    return out

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

def compute_e3(S, zeta):
    """Compute e_3 of {ζ^i : i∈S}."""
    elts = [zeta ** i for i in S]
    return sum(elts[a]*elts[b]*elts[c]
               for a in range(len(elts))
               for b in range(a+1, len(elts))
               for c in range(b+1, len(elts)))

def compute_norm_of_element(elem_func, S, n):
    """Compute Norm_{Q(ζ_n)/Q}(elem_func(S)) = Π_{k coprime to n} σ_k(elem_func(S))."""
    zeta = cmath.exp(2j * pi / n)
    coprime = [k for k in range(1, n) if gcd(k, n) == 1]
    prod = 1 + 0j
    for k in coprime:
        S_k = [(k * i) % n for i in S]
        val = elem_func(S_k, zeta)
        prod *= val
    return int(round(prod.real))

def e1_func(S, zeta):
    return sum(zeta ** i for i in S)

def e3_func(S, zeta):
    elts = [zeta ** i for i in S]
    return sum(elts[a]*elts[b]*elts[c]
               for a in range(6) for b in range(a+1,6) for c in range(b+1,6))

def e4_func(S, zeta):
    elts = [zeta ** i for i in S]
    return sum(elts[a]*elts[b]*elts[c]*elts[d]
               for a in range(6) for b in range(a+1,6)
               for c in range(b+1,6) for d in range(c+1,6))

def main():
    n = 36
    zeta = cmath.exp(2j * pi / n)
    coprime = [k for k in range(1, n) if gcd(k, n) == 1]

    print(f"=== Enumerating S with e_3 = 0 (identity in Z[ζ_{n}]), n={n} ===\n")

    # Step 1: find all 6-element S with 0∈S, not subgroup-aligned, and e_3 = 0 identically
    # e_3 = 0 identically iff e_3(S_k, ζ) = 0 for ALL k coprime to n
    # Quick check: just verify e_3(S, ζ) = 0 (the k=1 case). If Norm = 0,
    # this is equivalent (since Z[ζ] is a domain).

    e3_zero_aligned = []
    e3_zero_non_aligned = []

    for rest in combinations(range(1, n), 5):
        S = (0,) + rest
        # check e_3(S, ζ) = 0
        val = e3_func(S, zeta)
        if abs(val) > 1e-8: continue

        if is_subgroup_aligned(set(S), n) is not None:
            e3_zero_aligned.append(S)
        else:
            e3_zero_non_aligned.append(S)

    print(f"  6-element S with 0∈S and e_3=0: "
          f"{len(e3_zero_aligned)} aligned + {len(e3_zero_non_aligned)} non-aligned "
          f"= {len(e3_zero_aligned) + len(e3_zero_non_aligned)} total")

    # Step 2: for non-aligned ones, compute Norm(e_1) and Norm(e_4)
    print(f"\n--- Non-aligned S with e_3=0 ---")
    print(f"{'S':>40} {'N(e1)':>12} {'N(e4)':>12} {'gcd':>8} {'primes':>20}")
    print("-" * 100)

    all_primes = set()
    norm_pairs = defaultdict(list)  # (N1, N4) -> list of S

    for S in e3_zero_non_aligned:
        N1 = compute_norm_of_element(e1_func, S, n)
        N4 = compute_norm_of_element(e4_func, S, n)
        g = gcd(abs(N1), abs(N4))
        pfs = prime_factors_list(g)
        pfs_mod36 = [p for p in pfs if p % n == 1]
        all_primes.update(pfs_mod36)
        norm_pairs[(abs(N1), abs(N4))].append(S)
        print(f"  {str(S):>38} {N1:>12} {N4:>12} {g:>8} {str(pfs_mod36):>20}")

    print(f"\n  ALL primes ≡ 1 (mod 36) appearing: {sorted(all_primes)}")

    # Step 3: group by (|N1|, |N4|) to see patterns
    print(f"\n--- Grouping by (|Norm(e_1)|, |Norm(e_4)|) ---")
    for (n1, n4), S_list in sorted(norm_pairs.items()):
        g = gcd(n1, n4)
        print(f"  (N1={n1}, N4={n4}): {len(S_list)} subsets, gcd={g} = {factorize(g)}")
        for S in S_list:
            print(f"    {S}")

    # Step 4: also check aligned ones to understand the full variety structure
    print(f"\n--- Aligned S with e_3=0 (for comparison) ---")
    for S in e3_zero_aligned[:10]:
        N1 = compute_norm_of_element(e1_func, S, n)
        N4 = compute_norm_of_element(e4_func, S, n)
        print(f"  {S}  N1={N1}  N4={N4}")

    # Step 5: is there a pattern in the non-aligned S?
    print(f"\n--- Structure of non-aligned e_3=0 subsets ---")
    for S in e3_zero_non_aligned:
        diffs = tuple((S[i] - S[0]) % n for i in range(1, 6))
        # check if S contains a coset of order 3 subgroup {0, 12, 24}
        order3 = {0, 12, 24}
        coset_parts = []
        residue = set(S)
        for t in range(12):  # 12 cosets of order-3 subgroup
            coset = {(t + h) % n for h in order3}
            if coset.issubset(residue):
                coset_parts.append(t)
                residue -= coset
        print(f"  S={S}  order-3 cosets: shifts={coset_parts}  residue={sorted(residue)}")

if __name__ == "__main__":
    main()
