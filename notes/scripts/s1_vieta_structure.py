"""
For general word w(x) = x^a + λ*x^b, the agreement polynomial is
w(x) - h(x) where h has degree < k.

For k=2: w(x) - h0 - h1*x. If a > b > 1, this is a polynomial of degree a:
  x^a + λ*x^b - h1*x - h0

which has nonzero terms at degrees a, b, 1, 0 (and zero elsewhere).

By Vieta: e_j = 0 for each "missing" degree (between a and 0).

For CS (a=6, b=4): missing degrees 5, 3, 2 → e_1 = e_3 = e_4 = 0 (3 conditions)
For (a=5, b=3): missing degrees 4, 2 → e_2 = e_4 = 0 (2 conditions)
For (a=7, b=2): missing degrees 6, 5, 4, 3 → e_1 = e_2 = e_3 = e_4 = 0 (4 conditions!)

More missing degrees → more Vieta conditions → stronger constraints.
Fewer conditions → more freedom → potentially more non-aligned witnesses.

Hypothesis: the worst case (most non-aligned witnesses) minimizes the number
of Vieta conditions, i.e., maximizes the number of nonzero terms.

For degree-a polynomial with terms at degrees a, b, 1, 0: the missing degrees
are {a-1, a-2, ..., 2} \ {b}. That's (a-2) - 1 = a-3 conditions (if b∈{2,...,a-1}).

For a=6 (CS): 6-3=3 conditions.
For a=5: 5-3=2 conditions.
For a=4: 4-3=1 condition.
For a=3: 3-3=0 conditions! But then the polynomial is x^3 + λx^b - h1x - h0.
  If b=2: x^3 + λx^2 - h1x - h0, ALL terms present → 0 Vieta conditions.
  The root set S has |S|=3, and e_1, e_2, e_3 are free.

So the "least constrained" case is small degree a. But then |S| = a is also
small, which means threshold = a. For threshold to be meaningful, a = rm ≥ 6.

For the CS parameters (m=2, r=3): a = rm = 6, which gives 3 conditions.
Could we do better (fewer conditions) with different CS parameters?

Actually, the agreement polynomial has degree max(deg w, deg h) in general.
For w of degree d and h of degree k-1:
  If d > k-1: degree d, missing degrees from k to d-1 except where w has terms.
  If d ≤ k-1: just h - w of degree k-1.

For the proximity gap, deg w can be up to n-1 (arbitrary word). The worst case
for non-alignment is when deg(w-h) is minimized (fewer roots possible) but
the conditions are also minimized.

Let me just tabulate: for each (a,b) pair, how many Vieta conditions, and
how many non-aligned witnesses at p=37 (n=36)?
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

def count_vieta_conditions(a, b):
    """Number of e_j = 0 conditions from polynomial x^a + λx^b - h1x - h0."""
    # Nonzero term positions: a, b, 1, 0
    # Missing: {a-1, ..., 2} \ {b}
    if b <= 1 or b >= a:
        return max(0, a - 3)
    missing = set(range(2, a)) - {b}
    return len(missing)

def sweep_ab(a, b, p, n, omega, L, threshold):
    """Sweep over λ ∈ F_p for word w = x^a + λx^b, find non-aligned witnesses."""
    total = 0
    non_aligned = 0
    for lam in range(p):
        w_vals = [(pow(L[i], a, p) + lam * pow(L[i], b, p)) % p for i in range(n)]
        # Lagrange trick for k=2
        seen_h = {}
        for i in range(n):
            for j in range(i+1, n):
                dx = (L[i] - L[j]) % p
                dy = (w_vals[i] - w_vals[j]) % p
                h1 = (dy * modinv(dx, p)) % p
                h0 = (w_vals[i] - h1 * L[i]) % p
                key = (h0, h1)
                if key in seen_h: continue
                agree = sum(1 for idx in range(n)
                            if (h0 + h1 * L[idx]) % p == w_vals[idx])
                seen_h[key] = agree
                if agree >= threshold:
                    total += 1
                    agree_set = {idx for idx in range(n)
                                 if (h0 + h1 * L[idx]) % p == w_vals[idx]}
                    if is_subgroup_aligned(agree_set, n) is None:
                        non_aligned += 1
    return total, non_aligned

def main():
    n = 36
    threshold = 6  # rm = 6

    print(f"=== Vieta structure analysis: n={n}, k=2, threshold={threshold} ===\n")

    print(f"{'(a,b)':>10} {'#Vieta':>7} {'p=37_total':>10} {'p=37_NOT':>10} "
          f"{'p=73_total':>10} {'p=73_NOT':>10} {'p=181_total':>11} {'p=181_NOT':>10}")
    print("-" * 90)

    # Precompute for each prime
    primes = [37, 73, 181]
    prime_data = {}
    for p in primes:
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]
        prime_data[p] = (omega, L)

    # Test (a,b) pairs with 2 ≤ b < a ≤ 12 (keep a manageable)
    for a in range(3, 13):
        for b in range(2, a):
            if a > n: continue
            nv = count_vieta_conditions(a, b)

            results = []
            for p in primes:
                omega, L = prime_data[p]
                tot, na = sweep_ab(a, b, p, n, omega, L, threshold)
                results.append((tot, na))

            if any(r[0] > 0 for r in results):  # only show if there are witnesses
                print(f"  ({a:>2},{b:>2}) {nv:>7} "
                      f"{results[0][0]:>10} {results[0][1]:>10} "
                      f"{results[1][0]:>10} {results[1][1]:>10} "
                      f"{results[2][0]:>11} {results[2][1]:>10}")

    # Summary
    print(f"\nNote: CS is (a,b) = (6,4), #Vieta = 3")
    print(f"Minimum-Vieta cases: (3,2) with 0 conditions, (4,2) or (4,3) with 1 condition")

if __name__ == "__main__":
    main()
