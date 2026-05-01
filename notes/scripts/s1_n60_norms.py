"""
Same analysis for n=60: enumerate e_3=0 non-aligned S, compute norms,
find the complete set of non-alignment primes.

n=60, m=2, r=3, k=2. threshold=6. 6-subsets of Z/60Z.
C(59,5) ~ 5M — too many for full enum. Use a smarter approach:
  - At each known non-alignment prime (p=61,181,241), find the witnesses
  - Compute norms for those specific S
  - Then predict ALL non-alignment primes

Also: extend to more primes to verify the finite-set prediction.
"""
import cmath
from math import pi, gcd
from itertools import combinations
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
    if n == 0: return "0"
    neg = n < 0; n = abs(n)
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

def find_non_aligned_at_p(p, n=60, with_zero=True):
    """Find non-aligned S at a specific prime, using the sweep method."""
    omega = find_omega_Fp(p, n)
    L = [pow(omega, i, p) for i in range(n)]
    inv2 = modinv(2, p)

    results = []
    for S in combinations(range(n), 6):
        if with_zero and 0 not in S: continue
        p1 = sum(L[i] for i in S) % p
        if p1 != 0: continue
        p2 = sum(pow(L[i], 2, p) for i in S) % p
        p3 = sum(pow(L[i], 3, p) for i in S) % p
        if p3 != 0: continue
        p4 = sum(pow(L[i], 4, p) for i in S) % p
        if p4 != p2 * p2 % p * inv2 % p: continue
        if is_subgroup_aligned(set(S), n) is None:
            results.append(S)
    return results

def compute_norm(elem_func, S, n):
    zeta = cmath.exp(2j * pi / n)
    coprime = [k for k in range(1, n) if gcd(k, n) == 1]
    prod = 1 + 0j
    for k in coprime:
        S_k = tuple((k * i) % n for i in S)
        prod *= elem_func(S_k, zeta)
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
    n = 60
    print(f"=== n={n}: norm computation at known non-alignment primes ===\n")

    # Known non-alignment primes and their witness counts:
    # p=61: 240 NOT (4 orbits), p=181: 120 NOT (2 orbits), p=241: 60 NOT (1 orbit)
    # p=421: 0 NOT

    all_non_alignment_primes = set()

    for p in [61, 181, 241]:
        print(f"--- p={p}, (p-1)/n={(p-1)//n} ---")
        non_aligned = find_non_aligned_at_p(p, n, with_zero=True)
        print(f"  #non-aligned (with 0∈S) = {len(non_aligned)}")

        norm_data = defaultdict(list)
        for S in non_aligned:
            N1 = compute_norm(e1_func, S, n)
            N3 = compute_norm(e3_func, S, n)
            N4 = compute_norm(e4_func, S, n)
            norm_data[(abs(N1), abs(N3), abs(N4))].append(S)

        print(f"  Norm classes:")
        for (n1, n3, n4), S_list in sorted(norm_data.items()):
            g_all = gcd(gcd(n1, n3) if n3 > 0 else n1, n4) if n4 > 0 else gcd(n1, n3)
            if n3 == 0:
                g_all = gcd(n1, n4)
            pfs = [q for q in prime_factors(g_all) if q % n == 1] if g_all > 1 else []
            all_non_alignment_primes.update(pfs)
            print(f"    (N1={n1}, N3={n3}, N4={n4}): "
                  f"{len(S_list)} subsets, gcd={g_all}={factorize(g_all)}, "
                  f"primes≡1(mod {n}): {pfs}")
            if len(S_list) <= 3:
                for S in S_list:
                    print(f"      {S}")

    print(f"\n  ALL non-alignment primes found: {sorted(all_non_alignment_primes)}")

    # Now: predict — if the set of non-alignment primes is finite,
    # verify by checking more primes
    print(f"\n\n=== Verification: check more primes for n={n} ===")
    primes_to_check = [p for p in range(61, 3001) if p % n == 1 and is_prime(p)]
    print(f"  Primes p ≡ 1 (mod {n}) up to 3000: {len(primes_to_check)}")

    from multiprocessing import Pool, cpu_count

    for p in primes_to_check:
        ratio = (p - 1) // n
        omega = find_omega_Fp(p, n)
        L = [pow(omega, i, p) for i in range(n)]
        f_vals = [pow(x, 6, p) for x in L]
        g_vals = [pow(x, 4, p) for x in L]
        threshold = 6

        bad = []
        inv2p = modinv(2, p)
        for lam in range(p):
            target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
            seen_h = {}
            for i in range(n):
                for j in range(i+1, n):
                    dx = (L[i] - L[j]) % p
                    dy = (target[i] - target[j]) % p
                    h1 = (dy * modinv(dx, p)) % p
                    h0 = (target[i] - h1 * L[i]) % p
                    key = (h0, h1)
                    if key in seen_h: continue
                    agree = sum(1 for idx in range(n)
                                if (h0 + h1 * L[idx]) % p == target[idx])
                    seen_h[key] = agree
                    if agree >= threshold:
                        bad.append((lam, key, None))

        # Re-derive S for alignment check — only for bad witnesses
        not_aligned = 0
        for lam, (h0, h1), _ in bad:
            agree_set = set()
            target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
            for idx in range(n):
                if (h0 + h1 * L[idx]) % p == target[idx]:
                    agree_set.add(idx)
            if is_subgroup_aligned(agree_set, n) is None:
                not_aligned += 1
        predicted = "predicted" if p in all_non_alignment_primes else ""
        if not_aligned > 0 or predicted:
            print(f"  p={p:>5} ratio={ratio:>3} #NOT={not_aligned:>4} {predicted}", flush=True)

    print(f"\n  Primes with #NOT=0 not shown (should be all except predicted set)")

if __name__ == "__main__":
    main()
