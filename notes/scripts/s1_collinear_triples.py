"""
Compute collinear triples on the graph G = {(x, w(x)) : x ∈ L} for various
words w, and derive list-size bounds.

Key identity: for k=2 (lines), each pair of G-points determines a unique line.
  Σ_h C(|S_h|, 2) = C(n, 2)  (trivially)
  Σ_h C(|S_h|, 3) = T  (collinear triples — depends on w)

The number of t-rich lines (list size for w) satisfies:
  M ≤ T / C(t, 3)

And T can be computed in O(n³) or faster.

Also: T = #{(i,j,k) : i<j<k, w(x_i), w(x_j), w(x_k) are collinear with x_i, x_j, x_k}
i.e., the determinant |1 x_i w(x_i); 1 x_j w(x_j); 1 x_k w(x_k)| = 0 mod p.
"""
from math import gcd
from itertools import combinations

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

def collinear_triples(x_vals, y_vals, p):
    """Count collinear triples among points (x_i, y_i) in F_p²."""
    n = len(x_vals)
    T = 0
    # For efficiency: for each pair (i,j), compute the line, then count
    # how many other points are on it. Use the "line through pairs" approach.
    # Line through (x_i, y_i) and (x_j, y_j):
    #   slope = (y_j - y_i) / (x_j - x_i)  (x_i ≠ x_j since x_vals are distinct ω^i)
    #   For point k to be collinear: (y_k - y_i)(x_j - x_i) = (y_j - y_i)(x_k - x_i) mod p
    #
    # Efficient: for each pair (i,j), count #{k > j : collinear}.
    # Total T = sum of these counts.

    for i in range(n):
        for j in range(i + 1, n):
            dx = (x_vals[j] - x_vals[i]) % p
            dy = (y_vals[j] - y_vals[i]) % p
            for k in range(j + 1, n):
                dx2 = (x_vals[k] - x_vals[i]) % p
                dy2 = (y_vals[k] - y_vals[i]) % p
                # collinear iff dy * dx2 = dx * dy2 mod p
                if (dy * dx2 - dx * dy2) % p == 0:
                    T += 1
    return T

def collinear_triples_fast(x_vals, y_vals, p):
    """Faster: for each point i, compute slopes to all other points,
    count pairs with same slope."""
    n = len(x_vals)
    T = 0
    for i in range(n):
        # slopes from point i to all other points
        slopes = {}
        for j in range(n):
            if j == i: continue
            dx = (x_vals[j] - x_vals[i]) % p
            dy = (y_vals[j] - y_vals[i]) % p
            # normalize slope: (dy/dx) mod p. Since x_vals are distinct, dx ≠ 0.
            s = (dy * modinv(dx, p)) % p
            slopes[s] = slopes.get(s, 0) + 1
        # collinear triples through i: for each slope with count c, C(c, 2) triples
        for c in slopes.values():
            T += c * (c - 1) // 2
    # Each triple is counted 3 times (once for each vertex)
    assert T % 3 == 0
    return T // 3

def list_size_bound_from_T(T, t):
    """Upper bound on number of t-rich lines from collinear triples count."""
    ct3 = t * (t-1) * (t-2) // 6
    if ct3 == 0: return float('inf')
    return T / ct3

def compute_max_list_size(x_vals, y_vals, p, threshold):
    """Directly compute max per-word list size by sweeping all lines."""
    n = len(x_vals)
    # For each pair, determine line, count agreement
    line_agree = {}
    for i in range(n):
        for j in range(i+1, n):
            dx = (x_vals[j] - x_vals[i]) % p
            dy = (y_vals[j] - y_vals[i]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (y_vals[i] - h1 * x_vals[i]) % p
            key = (h0, h1)
            if key not in line_agree:
                count = sum(1 for k in range(n)
                            if (h0 + h1 * x_vals[k]) % p == y_vals[k])
                line_agree[key] = count
    rich = sum(1 for c in line_agree.values() if c >= threshold)
    max_agree = max(line_agree.values()) if line_agree else 0
    return rich, max_agree

def main():
    threshold = 6
    print(f"=== Collinear triples analysis ===")
    print(f"threshold t={threshold}, C(t,3)={threshold*(threshold-1)*(threshold-2)//6}\n")

    results = []

    for n in [36, 48, 60, 72, 96, 120]:
        # find proper-subgroup prime
        p = n + 1
        while not is_prime(p): p += n
        if p - 1 == n:  # full group, try next
            p2 = p + n
            while not is_prime(p2): p2 += n
        else:
            p2 = p
        # use the first "proper" prime, or the full-group one
        primes_to_test = []
        p_full = n + 1
        while not is_prime(p_full): p_full += n
        if p_full - 1 == n:
            primes_to_test.append((p_full, "full"))
        p_prop = p_full + n
        while not is_prime(p_prop): p_prop += n
        primes_to_test.append((p_prop, "proper"))

        for p, ptype in primes_to_test:
            omega = find_omega(p, n)
            L = [pow(omega, i, p) for i in range(n)]

            print(f"--- n={n}, p={p} ({ptype}, ratio={(p-1)//n}) ---")

            # test several word types
            words = {
                "CS(6,4)": lambda L, lam, p: [(pow(x,6,p)+lam*pow(x,4,p))%p for x in L],
                "(6,5)": lambda L, lam, p: [(pow(x,6,p)+lam*pow(x,5,p))%p for x in L],
                "(7,6)": lambda L, lam, p: [(pow(x,7,p)+lam*pow(x,6,p))%p for x in L],
                "(8,5)": lambda L, lam, p: [(pow(x,8,p)+lam*pow(x,5,p))%p for x in L],
            }

            print(f"  {'word':>10} {'λ':>4} {'T':>8} {'M_bound':>8} {'actual_M':>9} {'max_agr':>8}")
            for name, wfunc in words.items():
                # Find the worst lambda (maximize list size)
                best_lam = 0; best_M = 0; best_T = 0; best_maxagr = 0
                for lam in range(min(p, 50)):  # sample 50 lambdas
                    y_vals = wfunc(L, lam, p)
                    T = collinear_triples_fast(L, y_vals, p)
                    M_bound = list_size_bound_from_T(T, threshold)
                    actual_M, max_agr = compute_max_list_size(L, y_vals, p, threshold)
                    if actual_M > best_M:
                        best_lam = lam; best_M = actual_M; best_T = T; best_maxagr = max_agr

                M_bound = list_size_bound_from_T(best_T, threshold)
                print(f"  {name:>10} {best_lam:>4} {best_T:>8} {M_bound:>8.1f} {best_M:>9} {best_maxagr:>8}")
                results.append((n, p, name, best_T, M_bound, best_M, best_maxagr))
            print()

    # Summary: T vs n scaling
    print("\n=== SUMMARY: T scaling ===")
    print(f"{'n':>4} {'p':>6} {'word':>10} {'T':>8} {'T_bound':>8} {'actual_M':>9} {'n/5':>5}")
    for n, p, name, T, Mb, aM, ma in results:
        if aM > 0:
            print(f"{n:>4} {p:>6} {name:>10} {T:>8} {Mb:>8.1f} {aM:>9} {n//5:>5}")

if __name__ == "__main__":
    main()
