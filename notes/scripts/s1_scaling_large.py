"""
Confirm M ≈ n/(t-1) scaling for larger n.
Test n ∈ {144, 180, 240, 360} with proper-subgroup primes.

Optimized: only compute max per-word list size (skip collinear triples).
Test the worst (a,b) from smaller n: (6,5), (7,6), CS(6,4).
Sample λ values instead of exhaustive sweep for large p.
"""
import random
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

def modinv(a, p): return pow(a, p - 2, p)

def max_list_size_for_word(L, w_vals, p, n, threshold):
    """Count t-rich lines for one word. Return (num_rich, max_agreement)."""
    line_agree = {}
    for i in range(n):
        for j in range(i + 1, n):
            dx = (L[j] - L[i]) % p
            dy = (w_vals[j] - w_vals[i]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (w_vals[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in line_agree: continue
            c = 0
            for k in range(n):
                if (h0 + h1 * L[k]) % p == w_vals[k]:
                    c += 1
            line_agree[key] = c
    rich = sum(1 for c in line_agree.values() if c >= threshold)
    ma = max(line_agree.values()) if line_agree else 0
    return rich, ma

def find_proper_prime(n, min_ratio=2, max_p=10000):
    p = n * min_ratio + 1
    while p < max_p:
        if p % n == 1 and is_prime(p):
            return p
        p += 1
    return None

def main():
    random.seed(42)
    threshold = 6

    print(f"=== Large-n scaling test: M vs n/(t-1) ===")
    print(f"threshold t={threshold}, predicted M ≈ n/{threshold-1} = n/5\n")

    ab_pairs = [(6, 4), (6, 5), (7, 6)]

    test_ns = [36, 48, 60, 72, 96, 120, 144, 180, 240, 360]

    print(f"{'n':>4} {'p':>6} {'ratio':>6} {'(a,b)':>8} {'max_M':>6} {'max_agr':>8} "
          f"{'n/5':>5} {'M*5/n':>7}")
    print("-" * 70)

    for n in test_ns:
        p = find_proper_prime(n, min_ratio=2, max_p=50000)
        if p is None:
            print(f"{n:>4}  -- no prime found --")
            continue

        ratio = (p - 1) // n
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        # precompute powers
        L_pow = {}
        for a in set(a for a, b in ab_pairs) | set(b for a, b in ab_pairs):
            L_pow[a] = [pow(x, a, p) for x in L]

        # For each (a,b), sample lambdas and find worst case
        for a, b in ab_pairs:
            best_M = 0
            best_ma = 0
            La = L_pow[a]
            Lb = L_pow[b]

            # sample λ values: all if p ≤ 300, else sample 200
            if p <= 300:
                lam_range = range(p)
            else:
                lam_range = random.sample(range(p), min(200, p))

            for lam in lam_range:
                w_vals = [(La[i] + lam * Lb[i]) % p for i in range(n)]
                M, ma = max_list_size_for_word(L, w_vals, p, n, threshold)
                if M > best_M:
                    best_M = M
                    best_ma = ma

            r = best_M * 5 / n if n > 0 else 0
            print(f"{n:>4} {p:>6} {ratio:>6} ({a:>2},{b:>2}) {best_M:>6} {best_ma:>8} "
                  f"{n//5:>5} {r:>7.2f}", flush=True)

if __name__ == "__main__":
    main()
