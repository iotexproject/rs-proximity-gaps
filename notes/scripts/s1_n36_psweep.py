"""
S1 follow-up: for n=36, m=2, r=3 (k=2), sweep ALL primes p ≡ 1 (mod 36)
up to ~2000. Map out exactly which p give non-aligned witnesses.
"""
from multiprocessing import Pool, cpu_count
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
    nf = prime_factors(n)
    pf = prime_factors(p - 1)
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

def decompose_alignment(S_set, n):
    best_d = None; best_covered = []
    for d in divisors(n):
        if d == 1 or d == n: continue
        cs = cosets_of_index_subgroup(n, d)
        covered = [c for c in cs if set(c).issubset(S_set)]
        cov_size = sum(len(c) for c in covered)
        if cov_size > 0 and (best_d is None or cov_size > sum(len(c) for c in best_covered)):
            best_d = d; best_covered = covered
    if best_d is None:
        return None, S_set
    coset_part = set()
    for c in best_covered: coset_part.update(c)
    return best_d, S_set - coset_part

def sweep_one_lambda(args):
    lam, L, target, n, p, threshold = args
    seen_h = {}
    for i in range(n):
        for j in range(i+1, n):
            dx = (L[i] - L[j]) % p
            dy = (target[i] - target[j]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (target[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen_h: continue
            agree = []
            for idx in range(n):
                if (h0 + h1 * L[idx]) % p == target[idx]:
                    agree.append(idx)
            seen_h[key] = agree
    bad = []
    for (h0, h1), agree in seen_h.items():
        if len(agree) >= threshold:
            bad.append((lam, (h0, h1), tuple(agree)))
    return bad

def run_one_p(p, n=36, m=2, r=3):
    s = n // m
    k = (r - 2) * m
    threshold = r * m
    omega = find_omega(p, n)
    L = [pow(omega, i, p) for i in range(n)]
    f_vals = [pow(x, r*m, p) for x in L]
    g_vals = [pow(x, (r-1)*m, p) for x in L]

    tasks = []
    for lam in range(p):
        target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
        tasks.append((lam, L, target, n, p, threshold))

    ncpu = min(cpu_count(), 8)
    with Pool(ncpu) as pool:
        results = pool.map(sweep_one_lambda, tasks, chunksize=max(1, p // (ncpu * 4)))

    bad = []
    for batch in results:
        bad.extend(batch)

    aligned = sum(1 for _, _, S in bad if is_subgroup_aligned(set(S), n) is not None)
    not_aligned = [(lam, hc, S) for lam, hc, S in bad if is_subgroup_aligned(set(S), n) is None]

    # collect shapes
    from collections import Counter
    shapes = Counter()
    for _, _, S in not_aligned:
        _, residue = decompose_alignment(set(S), n)
        rs = sorted(residue)
        if rs:
            base = rs[0]
            shape = tuple((x - base) % n for x in rs)
            shapes[shape] += 1

    return len(bad), aligned, len(not_aligned), shapes

def main():
    n = 36
    # find all primes p ≡ 1 (mod 36) up to 2000
    primes = [p for p in range(37, 2001) if p % n == 1 and is_prime(p)]

    print(f"n={n}, m=2, r=3, k=2, threshold=6")
    print(f"Primes p ≡ 1 (mod {n}) up to 2000: {len(primes)}")
    print(f"{'p':>6} {'(p-1)/n':>8} {'gcd':>4} {'#wits':>6} {'#aln':>6} {'#NOT':>6}  {'shapes'}")
    print("-" * 90)

    for p in primes:
        ratio = (p - 1) // n
        g = gcd(ratio, n)
        total, aln, not_aln, shapes = run_one_p(p, n=36)
        shape_str = "  ".join(f"{s}:{c}" for s, c in shapes.most_common(3)) if shapes else "-"
        marker = " ***" if not_aln > 0 else ""
        print(f"{p:>6} {ratio:>8} {g:>4} {total:>6} {aln:>6} {not_aln:>6}  {shape_str}{marker}", flush=True)

    # also do n=48 for comparison
    print("\n" + "=" * 90)
    n2 = 48
    primes2 = [p for p in range(97, 1501) if p % n2 == 1 and is_prime(p)]
    print(f"\nn={n2}, m=2, r=3, k=2, threshold=6")
    print(f"Primes p ≡ 1 (mod {n2}) up to 1500: {len(primes2)}")
    print(f"{'p':>6} {'(p-1)/n':>8} {'gcd':>4} {'#wits':>6} {'#aln':>6} {'#NOT':>6}  {'shapes'}")
    print("-" * 90)

    for p in primes2:
        ratio = (p - 1) // n2
        g = gcd(ratio, n2)
        total, aln, not_aln, shapes = run_one_p(p, n=n2)
        shape_str = "  ".join(f"{s}:{c}" for s, c in shapes.most_common(3)) if shapes else "-"
        marker = " ***" if not_aln > 0 else ""
        print(f"{p:>6} {ratio:>8} {g:>4} {total:>6} {aln:>6} {not_aln:>6}  {shape_str}{marker}", flush=True)

if __name__ == "__main__":
    main()
