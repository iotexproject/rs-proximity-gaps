"""
Correct approach to number field identification.

Key insight: over C, the sums e_1(S), e_3(S), e_4(S) are NONZERO elements
of Z[ζ_36]. They vanish mod p only when p divides their norm. The set of
"non-alignment primes" for a given S is {p : p | gcd(Norm(e_1), Norm(e_3), Norm(e_4))}.

More precisely: need p below a common prime ideal dividing all three.
Since p ≡ 1 (mod 36), p splits completely, so the condition is:
∃ k ∈ (Z/36Z)* such that σ_k(e_1) ≡ σ_k(e_3) ≡ σ_k(e_4) ≡ 0 (mod p).

Plan:
1. At p=37 and p=181, find the non-aligned S (normalized with 0 ∈ S)
2. Compute the conjugates σ_k(e_j(S)) as complex numbers
3. Compute Norm(e_j) = Π_k σ_k(e_j), round to integer
4. Factor gcd of norms → candidate primes
5. Verify: union over all non-aligned S of their prime sets should = {37, 181}
"""
import cmath
from math import pi, gcd
from itertools import combinations
from functools import reduce

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
    if n == 0: return [(0, 1)]
    if n < 0: n = -n
    out = []; d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0: e += 1; n //= d
            out.append((d, e))
        d += 1
    if n > 1: out.append((n, 1))
    return out

def find_omega_Fp(p, n):
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

def find_non_aligned_at_p(p, n=36):
    """Find non-aligned 6-subsets S at specific prime p, normalized with 0 ∈ S."""
    omega = find_omega_Fp(p, n)
    L = [pow(omega, i, p) for i in range(n)]
    f_vals = [pow(x, 6, p) for x in L]
    g_vals = [pow(x, 4, p) for x in L]
    inv2 = modinv(2, p)

    results = []
    for S in combinations(range(n), 6):
        if 0 not in S: continue
        # check e1 = e3 = e4 = 0
        # power sums
        p1 = sum(L[i] for i in S) % p
        if p1 != 0: continue
        p2 = sum(pow(L[i], 2, p) for i in S) % p
        p3 = sum(pow(L[i], 3, p) for i in S) % p
        if p3 != 0: continue
        p4 = sum(pow(L[i], 4, p) for i in S) % p
        # e4 = 0 iff p4 = p2^2 / 2
        if p4 != p2 * p2 % p * inv2 % p: continue
        if is_subgroup_aligned(set(S), n) is None:
            results.append(S)
    return results

def compute_elem_sym(S, zeta, n):
    """Compute e_1, e_2, e_3, e_4, e_5, e_6 of {ζ^i : i ∈ S} as complex numbers."""
    elts = [zeta ** i for i in S]
    from itertools import combinations as comb
    e = [0] * 7
    for k in range(1, 7):
        e[k] = sum(reduce(lambda a,b: a*b, c) for c in comb(elts, k))
    return e

def compute_norms(S, n=36):
    """Compute Norm_{Q(ζ_n)/Q}(e_j(S)) for j=1,3,4."""
    zeta = cmath.exp(2j * pi / n)
    coprime = [k for k in range(1, n) if gcd(k, n) == 1]

    # For each Galois conjugate σ_k: ζ → ζ^k, compute e_j of {ζ^{ki} : i ∈ S}
    # which equals σ_k(e_j(S))

    norm_e1 = 1 + 0j
    norm_e3 = 1 + 0j
    norm_e4 = 1 + 0j

    conjugate_e1 = []
    conjugate_e3 = []
    conjugate_e4 = []

    for k in coprime:
        S_conj = [(k * i) % n for i in S]
        e = compute_elem_sym(S_conj, zeta, n)
        norm_e1 *= e[1]
        norm_e3 *= e[3]
        norm_e4 *= e[4]
        conjugate_e1.append((k, e[1]))
        conjugate_e3.append((k, e[3]))
        conjugate_e4.append((k, e[4]))

    # norms should be real integers (up to floating point)
    N1 = int(round(norm_e1.real))
    N3 = int(round(norm_e3.real))
    N4 = int(round(norm_e4.real))

    return N1, N3, N4, conjugate_e1, conjugate_e3, conjugate_e4

def main():
    n = 36
    print(f"=== Norm computation for non-aligned subsets, n={n} ===\n")

    for p in [37, 181]:
        print(f"--- Non-aligned S at p={p} (with 0 ∈ S) ---")
        non_aligned = find_non_aligned_at_p(p, n)
        print(f"  Found {len(non_aligned)} subsets")

        for S in non_aligned:
            print(f"\n  S = {S}")
            N1, N3, N4, conj_e1, conj_e3, conj_e4 = compute_norms(S, n)

            print(f"  Norm(e_1) = {N1}")
            print(f"    factored: {factorize(N1)}")
            print(f"  Norm(e_3) = {N3}")
            print(f"    factored: {factorize(N3)}")
            print(f"  Norm(e_4) = {N4}")
            print(f"    factored: {factorize(N4)}")

            g = gcd(gcd(abs(N1), abs(N3)), abs(N4))
            print(f"  gcd(|N1|, |N3|, |N4|) = {g}")
            if g > 1:
                print(f"    factored: {factorize(g)}")

            # Find which k values have ALL three conjugates small mod p
            # σ_k(e_j) ∈ Z[ζ] → F_p via ζ → ω
            # So σ_k(e_j) mod p = e_j evaluated at ω^k in F_p

            # For which k does σ_k(e_1) ≡ 0 mod p?
            # We can check this modularly
            omega = find_omega_Fp(p, n)
            coprime = [k for k in range(1, n) if gcd(k, n) == 1]
            print(f"\n  Checking which σ_k give e_1≡e_3≡e_4≡0 mod {p}:")
            for k in coprime:
                L_k = [pow(omega, k * i, p) for i in range(n)]
                elts = [L_k[i] for i in S]
                e1_mod = sum(elts) % p
                # e3: sum of products of triples
                e3_mod = 0
                for a in range(6):
                    for b in range(a+1, 6):
                        for c in range(b+1, 6):
                            e3_mod = (e3_mod + elts[a] * elts[b] % p * elts[c]) % p
                # e4: sum of products of quads
                e4_mod = 0
                for a in range(6):
                    for b in range(a+1, 6):
                        for c in range(b+1, 6):
                            for d in range(c+1, 6):
                                e4_mod = (e4_mod + elts[a] * elts[b] % p * elts[c] % p * elts[d]) % p
                if e1_mod == 0 and e3_mod == 0 and e4_mod == 0:
                    print(f"    k={k}: ALL ZERO ✓")
                elif e1_mod == 0:
                    print(f"    k={k}: e1=0, e3={e3_mod}, e4={e4_mod}")

    # Now: try ALL non-aligned S (over all possible prime embeddings)
    # by enumerating S with 0∈S and computing norms
    print(f"\n\n=== Full enumeration: all non-aligned S with 0∈S ===")
    print(f"Computing Norm(e_1), Norm(e_3), Norm(e_4) for each...")
    print(f"Looking for S where gcd of norms is divisible by primes ≡ 1 mod 36\n")

    zeta = cmath.exp(2j * pi / n)
    coprime = [k for k in range(1, n) if gcd(k, n) == 1]

    # precompute zeta^{ki} for all k, i
    zeta_ki = {}
    for k in coprime:
        for i in range(n):
            zeta_ki[(k, i)] = zeta ** ((k * i) % n)

    interesting = []
    count = 0

    for rest in combinations(range(1, n), 5):
        S = (0,) + rest
        if is_subgroup_aligned(set(S), n) is not None:
            continue
        count += 1

        # Quick filter: compute Norm(e_1) first
        norm_e1 = 1.0
        for k in coprime:
            s = sum(zeta_ki[(k, i)] for i in S)
            norm_e1 *= abs(s)
        # Norm(e_1) should be an integer; if it's < 0.5 in magnitude, skip (can't divide by p)
        # Actually, we want |Norm(e_1)| to be divisible by some prime ≡ 1 mod 36
        # For quick filter: compute actual norm
        ne1 = 1 + 0j
        ne3 = 1 + 0j
        ne4 = 1 + 0j
        for k in coprime:
            elts = [zeta_ki[(k, i)] for i in S]
            e1 = sum(elts)
            e3 = sum(elts[a]*elts[b]*elts[c]
                     for a in range(6) for b in range(a+1,6) for c in range(b+1,6))
            e4 = sum(elts[a]*elts[b]*elts[c]*elts[d]
                     for a in range(6) for b in range(a+1,6)
                     for c in range(b+1,6) for d in range(c+1,6))
            ne1 *= e1
            ne3 *= e3
            ne4 *= e4

        N1 = int(round(ne1.real))
        N3 = int(round(ne3.real))
        N4 = int(round(ne4.real))

        if N1 == 0 or N3 == 0 or N4 == 0:
            interesting.append((S, N1, N3, N4, "ZERO_NORM"))
            continue

        g = gcd(gcd(abs(N1), abs(N3)), abs(N4))
        # check if g has prime factors ≡ 1 mod 36
        if g > 1:
            for pf in prime_factors(g):
                if pf % n == 1 or pf == 37 or pf == 181:
                    interesting.append((S, N1, N3, N4, f"p={pf}"))

    print(f"  Checked {count} non-aligned subsets")
    print(f"  Found {len(interesting)} interesting ones:")
    shown_primes = set()
    for S, N1, N3, N4, tag in interesting[:50]:
        g = gcd(gcd(abs(N1), abs(N3)), abs(N4))
        print(f"  S={S}  N1={N1}  N3={N3}  N4={N4}  gcd={g}  tag={tag}")
        if g > 1:
            for pf in prime_factors(g):
                shown_primes.add(pf)

    if shown_primes:
        primes_mod36 = {p for p in shown_primes if p % n == 1}
        print(f"\n  Primes ≡ 1 (mod 36) found in gcd: {sorted(primes_mod36)}")

if __name__ == "__main__":
    main()
