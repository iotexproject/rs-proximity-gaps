"""
T1.3: Extend scaling test to k=3.

For k=3: h(x) = h0 + h1*x + h2*x^2, RS code of dimension 3.
Agreement polynomial w(x) - h(x) has degree max(deg w, 2).
Threshold t: for CS with m=3, r=3: t = rm = 9, k = (r-2)m = 3.

Lagrange-k trick for k=3: enumerate TRIPLES of L-points, solve for (h0,h1,h2)
via Vandermonde, count agreement. Cost: O(|F| * C(n,3) * n).
For n=36, |F|=37: 37 * C(36,3) * 36 ≈ 37 * 7140 * 36 ≈ 9.5M. Feasible.

Use multiprocessing with 28 cores.
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
    p = n * min_ratio + 1
    while True:
        if p % n == 1 and is_prime(p):
            return p
        p += 1

def solve_vandermonde_3(x0, x1, x2, y0, y1, y2, p):
    """Solve h0 + h1*x + h2*x^2 = y at three points. Return (h0, h1, h2) or None."""
    d01 = (x0 - x1) % p; d02 = (x0 - x2) % p; d12 = (x1 - x2) % p
    if d01 == 0 or d02 == 0 or d12 == 0: return None
    inv01 = modinv(d01, p); inv02 = modinv(d02, p); inv12 = modinv(d12, p)
    # Divided differences
    f01 = ((y0 - y1) * inv01) % p
    f02 = ((y0 - y2) * inv02) % p
    h2 = ((f01 - f02) * inv12) % p
    h1 = (f01 - h2 * (x0 + x1)) % p
    h0 = (y0 - h1 * x0 - h2 * x0 % p * x0 % p) % p
    return (h0, h1, h2)

def sweep_one_word_k3(args):
    """For one word (given as w_vals on L), find all degree-<3 polynomials
    with agreement >= threshold."""
    w_vals, L, n, p, threshold = args
    seen_h = {}
    for i in range(n):
        for j in range(i+1, n):
            for k_idx in range(j+1, n):
                result = solve_vandermonde_3(L[i], L[j], L[k_idx],
                                             w_vals[i], w_vals[j], w_vals[k_idx], p)
                if result is None: continue
                key = result
                if key in seen_h: continue
                h0, h1, h2 = key
                agree = 0
                for idx in range(n):
                    val = (h0 + h1 * L[idx] + h2 * L[idx] * L[idx] % p) % p
                    if val == w_vals[idx]:
                        agree += 1
                seen_h[key] = agree
    rich = [(h, a) for h, a in seen_h.items() if a >= threshold]
    return len(rich), max((a for _, a in rich), default=0)

def main():
    print("=== k=3 scaling test ===")
    print(f"Using {cpu_count()} cores\n")

    # CS parameters for k=3: m=3, r=3 → t=9, k=3, n=3s
    # Or keep m=2, r=4 → t=8, k=4... too high.
    # Let's use m=2, r=3 but just k=3 (not tied to CS formula).
    # Just test: with k=3 and threshold t=6 (same as before), does M scale?

    k = 3
    threshold = 6
    # Also test threshold = 9 (CS with m=3, r=3)
    thresholds = [6, 9]

    for thresh in thresholds:
        print(f"\n--- threshold = {thresh}, k = {k} ---")
        print(f"{'n':>4} {'p':>6} {'(a,b)':>8} {'max_M':>6} {'max_agr':>8} {'n/(t-1)':>8}")

        for n in [36, 48, 60, 72]:
            p = find_proper_prime(n, min_ratio=2)
            omega = find_omega(p, n)
            L = [pow(omega, i, p) for i in range(n)]

            # test (a,b) = (9,7) [CS-like for t=9] and (6,5) [worst case for t=6]
            if thresh == 6:
                ab_pairs = [(6, 5), (7, 6)]
            else:
                ab_pairs = [(9, 8), (9, 7)]

            for a, b in ab_pairs:
                best_M = 0
                best_ma = 0
                for lam in range(min(p, 40)):
                    w_vals = [(pow(L[i], a, p) + lam * pow(L[i], b, p)) % p for i in range(n)]
                    M, ma = sweep_one_word_k3((w_vals, L, n, p, thresh))
                    best_M = max(best_M, M)
                    best_ma = max(best_ma, ma)

                nt1 = n / (thresh - 1)
                print(f"{n:>4} {p:>6} ({a:>2},{b:>2}) {best_M:>6} {best_ma:>8} {nt1:>8.1f}",
                      flush=True)

if __name__ == "__main__":
    main()
