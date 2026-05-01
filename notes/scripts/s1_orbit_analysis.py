"""
Verify: do the 36 non-aligned subsets at p=37 and p=181 form
a single orbit under cyclic shift in Z/36Z?

If yes: the non-subgroup component of V is a single algebraic orbit,
rational over F_p for a finite set of primes. The number field K
over which this orbit is defined determines which primes see it.
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
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in pf):
            return pow(g, (p-1)//n, p)
    raise RuntimeError

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

def cyclic_shift(S, k, n):
    """Shift all elements of S by k mod n."""
    return tuple(sorted((s + k) % n for s in S))

def cyclic_orbit(S, n):
    """Full orbit of S under Z/nZ cyclic shift."""
    orbit = set()
    for k in range(n):
        orbit.add(cyclic_shift(S, k, n))
    return orbit

def find_non_aligned(p, n=36):
    omega = find_omega(p, n)
    w = [[pow(omega, k * i, p) for i in range(n)] for k in range(5)]
    inv2 = modinv(2, p)
    non_aligned = []

    for S in combinations(range(n), 6):
        p1 = sum(w[1][i] for i in S) % p
        if p1 != 0: continue
        p3 = sum(w[3][i] for i in S) % p
        if p3 != 0: continue
        p2 = sum(w[2][i] for i in S) % p
        p4 = sum(w[4][i] for i in S) % p
        if p4 != (p2 * p2 % p) * inv2 % p: continue
        if is_subgroup_aligned(set(S), n) is None:
            non_aligned.append(S)

    return non_aligned

def analyze_orbits(p, n=36):
    print(f"\n=== p={p}, n={n} ===")
    non_aligned = find_non_aligned(p, n)
    print(f"  #non-aligned = {len(non_aligned)}")

    if not non_aligned:
        print("  (none)")
        return

    # group into orbits
    remaining = set(non_aligned)
    orbits = []
    while remaining:
        rep = next(iter(remaining))
        orb = cyclic_orbit(rep, n)
        orbit_members = remaining & orb
        orbits.append((rep, len(orbit_members)))
        remaining -= orbit_members

    print(f"  #orbits = {len(orbits)}")
    for rep, size in orbits:
        stabilizer = n // size
        print(f"    orbit: rep={rep}, size={size}, stabilizer_order={stabilizer}")
        # show the "shape" (differences)
        diffs = tuple((rep[i+1] - rep[0]) % n for i in range(len(rep)-1))
        print(f"    shape (diffs from first): {diffs}")

    # check if orbits are related by some other symmetry
    if len(orbits) > 1:
        print(f"\n  Multiple orbits detected. Checking multiplicative symmetry...")
        # check if any automorphism of Z/nZ maps one orbit rep to another
        auts = [a for a in range(1, n) if gcd(a, n) == 1]  # (Z/nZ)* = Aut(Z/nZ)
        for a in auts:
            scaled = tuple(sorted((a * s) % n for s in orbits[0][0]))
            for j, (rep2, _) in enumerate(orbits[1:], 1):
                # check if scaled is in the orbit of rep2
                for k in range(n):
                    if cyclic_shift(scaled, k, n) == rep2:
                        print(f"    orbit 0 --(*{a}, +{k})--> orbit {j}")

def main():
    for p in [37, 181]:
        analyze_orbits(p, 36)

    # Also check: what happens for n=60 at the non-alignment primes?
    # n=60 had #NOT=240 at p=61, #NOT=120 at p=181, #NOT=60 at p=241
    print("\n" + "=" * 70)
    print("n=60 orbit structure:")
    for p in [61, 181, 241]:
        n = 60
        print(f"\n--- p={p}, n={n} ---")
        omega = find_omega(p, n)
        w = [[pow(omega, k * i, p) for i in range(n)] for k in range(5)]
        inv2 = modinv(2, p)
        non_aligned = []
        for S in combinations(range(n), 6):
            p1 = sum(w[1][i] for i in S) % p
            if p1 != 0: continue
            p3 = sum(w[3][i] for i in S) % p
            if p3 != 0: continue
            p2 = sum(w[2][i] for i in S) % p
            p4 = sum(w[4][i] for i in S) % p
            if p4 != (p2 * p2 % p) * inv2 % p: continue
            if is_subgroup_aligned(set(S), n) is None:
                non_aligned.append(S)
        print(f"  #non-aligned = {len(non_aligned)}")
        if non_aligned:
            remaining = set(non_aligned)
            orbits = []
            while remaining:
                rep = next(iter(remaining))
                orb = cyclic_orbit(rep, n)
                orbit_members = remaining & orb
                orbits.append((rep, len(orbit_members)))
                remaining -= orbit_members
            print(f"  #orbits = {len(orbits)}")
            for rep, size in orbits[:5]:
                stab = n // size
                diffs = tuple((rep[i+1] - rep[0]) % n for i in range(len(rep)-1))
                print(f"    orbit: rep={rep}, size={size}, stab={stab}, diffs={diffs}")
            if len(orbits) > 5:
                print(f"    ... ({len(orbits)} total orbits)")

if __name__ == "__main__":
    main()
