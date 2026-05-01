"""
T2.1 attack: count #rich h1 values for worst-case words.

For fixed word w and h1: g_{h1}(i) = w(ω^i) - h1·ω^i.
h1 is "rich" if g_{h1} has a t-popular value (some h0 with |g^{-1}(h0)| ≥ t).

Hypothesis: #rich h1 = O(1) (bounded independently of n and p).
If true: M ≤ #rich_h1 · ⌊n/t⌋ = O(n).

Test across many (n, p) and find the WORST λ for (6,5).
Use 28 cores.
"""
from multiprocessing import Pool, cpu_count
from math import gcd

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d = 5
    while d*d <= n:
        if n%d==0 or n%(d+2)==0: return False
        d+=6
    return True

def prime_factors(n):
    out=set(); d=2; nn=n
    while d*d<=nn:
        while nn%d==0: out.add(d); nn//=d
        d+=1
    if nn>1: out.add(nn)
    return list(out)

def find_omega(p,n):
    pf=prime_factors(p-1)
    for g in range(2,p):
        if all(pow(g,(p-1)//q,p)!=1 for q in pf):
            return pow(g,(p-1)//n,p)

def modinv(a,p): return pow(a,p-2,p)

def find_proper_prime(n, min_ratio=2):
    p = n*min_ratio+1
    while True:
        if p%n==1 and is_prime(p): return p
        p+=1

def analyze_word(args):
    """For one (lam, L, c_precomp, n, p, t): count rich h1, M, max per-h1."""
    lam, L, n, p, t, a, b = args
    c = [(pow(L[i],a,p) + lam*pow(L[i],b,p)) % p for i in range(n)]

    rich_h1_count = 0
    total_M = 0
    h1_details = []  # (h1, num_rich_h0, max_popularity)

    for h1 in range(p):
        level = {}
        for i in range(n):
            h0 = (c[i] - h1*L[i]) % p
            level[h0] = level.get(h0, 0) + 1
        max_pop = max(level.values())
        num_rich_h0 = sum(1 for cnt in level.values() if cnt >= t)
        if num_rich_h0 > 0:
            rich_h1_count += 1
            total_M += num_rich_h0
            h1_details.append((h1, num_rich_h0, max_pop))

    return (lam, rich_h1_count, total_M, h1_details)

def main():
    t = 6
    a, b = 6, 5

    print(f"=== T2.1: #rich h1 analysis for (a,b)=({a},{b}), t={t} ===\n")
    print(f"{'n':>4} {'p':>6} {'lam':>5} {'#rich_h1':>9} {'M':>5} "
          f"{'max_per_h1':>11} {'n/t':>5} {'n/(t-1)':>8}")
    print("-"*70)

    ncpu = min(cpu_count(), 16)

    for n in [36, 48, 60, 72, 96, 120, 180, 240, 360]:
        p = find_proper_prime(n, min_ratio=2)
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        # Find worst lambda
        tasks = [(lam, L, n, p, t, a, b) for lam in range(min(p, 100))]

        with Pool(ncpu) as pool:
            results = pool.map(analyze_word, tasks, chunksize=max(1, len(tasks)//(ncpu*4)))

        # Find the lambda with max M
        best = max(results, key=lambda r: r[2])
        lam, rh1, M, details = best

        max_per_h1 = max((d[1] for d in details), default=0) if details else 0

        print(f"{n:>4} {p:>6} {lam:>5} {rh1:>9} {M:>5} "
              f"{max_per_h1:>11} {n//t:>5} {n/(t-1):>8.1f}", flush=True)

        # Show h1 detail for worst case
        if details and n <= 120:
            for h1v, nrich, mpop in sorted(details, key=lambda x:-x[1])[:5]:
                print(f"      h1={h1v}: {nrich} rich h0, max_pop={mpop}")

    # Also test (7,6) for comparison
    print(f"\n--- Same for (a,b)=(7,6) ---")
    a2, b2 = 7, 6
    print(f"{'n':>4} {'p':>6} {'lam':>5} {'#rich_h1':>9} {'M':>5} "
          f"{'max_per_h1':>11} {'n/t':>5} {'n/(t-1)':>8}")
    print("-"*70)

    for n in [36, 60, 120, 240]:
        p = find_proper_prime(n, min_ratio=2)
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        tasks = [(lam, L, n, p, t, a2, b2) for lam in range(min(p, 100))]
        with Pool(ncpu) as pool:
            results = pool.map(analyze_word, tasks, chunksize=max(1, len(tasks)//(ncpu*4)))

        best = max(results, key=lambda r: r[2])
        lam, rh1, M, details = best
        max_per_h1 = max((d[1] for d in details), default=0) if details else 0

        print(f"{n:>4} {p:>6} {lam:>5} {rh1:>9} {M:>5} "
              f"{max_per_h1:>11} {n//t:>5} {n/(t-1):>8.1f}", flush=True)

        if details and n <= 120:
            for h1v, nrich, mpop in sorted(details, key=lambda x:-x[1])[:5]:
                print(f"      h1={h1v}: {nrich} rich h0, max_pop={mpop}")

if __name__ == "__main__":
    main()
