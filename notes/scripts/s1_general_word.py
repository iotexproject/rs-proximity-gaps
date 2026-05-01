"""
Generalization test: does the finiteness theorem hold for GENERAL received
words, not just CS line?

Setup: pick random w ∈ F_p^n (polynomial of degree < n evaluated on L).
For each h of degree < k, count agreement |{i : w(x_i) = h(x_i)}|.
If agreement ≥ threshold, record S.

Key question: for random w (not CS), do non-aligned S appear?
If they do: is it still controlled by the norm mechanism?
If they don't: maybe CS is the worst case, and general words are better.

Parameters: n=36, m=2, r=3, k=2, threshold=6 (same as before).
But w = random polynomial of degree up to n-1, not just x^6 + λx^4.

For k=2 (h = h0 + h1*x): use Lagrange trick.
The agreement polynomial is w(x) - h0 - h1*x of degree < n.
For |agreement| ≥ 6, we need w(x) - h0 - h1*x to have ≥ 6 roots in L.
Since w has degree < n, w(x) - h0 - h1*x has degree ≤ n-1, so up to n roots.
But for GENERIC w, the maximum agreement for ANY h is k (= 2) by the
Schwartz-Zippel bound... wait, that's not right.

Actually, for a random w, w(x_i) is basically random in F_p for each i.
The chance that h0 + h1*x_i = w(x_i) for a SPECIFIC h and 6 specific points
is (1/p)^4 (4 = 6 - 2 free parameters). Over all C(n,6)*p^2 choices,
expected count is C(36,6) * p^2 / p^4 = C(36,6) / p^2 ≈ 1.9M / p^2.
For p=37: ≈ 1400. For p > 50: < 800. For large p: → 0.

So for RANDOM w, the expected number of high-agreement witnesses is O(1/p^2)
→ 0 for large p. The CS construction is special because it creates witnesses
by algebraic design.

But the prize is about WORST CASE, not random case. The question is:
what's the worst-case w, and how many witnesses can it have?

For CS: the answer is completely characterized (Theorems 1-2).
For general w: we need to understand what makes CS special.

CS key property: w = f + λg where f = x^{rm}, g = x^{(r-1)m}. The
monomial structure means that for each λ, the polynomial w - h has a
specific algebraic form that allows many roots in L.

For general w, the polynomial w(x) - h0 - h1*x can have at most
min(deg w, n-1) roots in F_p. If deg w < n, it has < n roots.
For the roots to lie in L (subgroup of order n), we need a very special w.

Let's test: for random w of degree < n, how many witnesses appear?
"""
import random
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

def sweep_word(w_vals, L, n, p, threshold=6):
    """Find all (h0, h1) with agreement ≥ threshold for word w on L."""
    bad = []
    seen_h = {}
    for i in range(n):
        for j in range(i+1, n):
            dx = (L[i] - L[j]) % p
            dy = (w_vals[i] - w_vals[j]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (w_vals[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen_h: continue
            agree = []
            for idx in range(n):
                if (h0 + h1 * L[idx]) % p == w_vals[idx]:
                    agree.append(idx)
            seen_h[key] = agree
            if len(agree) >= threshold:
                bad.append((key, tuple(agree)))
    return bad

def main():
    n = 36
    threshold = 6
    random.seed(42)

    print(f"=== General word test: n={n}, k=2, threshold={threshold} ===\n")

    # Test at various primes
    for p in [37, 73, 109, 181]:
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        print(f"--- p={p}, (p-1)/n={(p-1)//n} ---")

        # 1. CS word for comparison
        print(f"  CS words (w = x^6 + λ*x^4):")
        total_cs = 0
        total_cs_not = 0
        for lam in range(p):
            w_vals = [(pow(L[i], 6, p) + lam * pow(L[i], 4, p)) % p for i in range(n)]
            bad = sweep_word(w_vals, L, n, p, threshold)
            for (h0, h1), S in bad:
                total_cs += 1
                if is_subgroup_aligned(set(S), n) is None:
                    total_cs_not += 1
        print(f"    total witnesses={total_cs}, non-aligned={total_cs_not}")

        # 2. Random polynomial words
        print(f"  Random words (w = random poly of degree < n):")
        n_trials = 200
        total_rand = 0
        total_rand_not = 0
        max_agree = 0
        for trial in range(n_trials):
            # random polynomial of degree < n evaluated on L
            coeffs = [random.randint(0, p-1) for _ in range(n)]
            w_vals = []
            for i in range(n):
                v = 0; xpow = 1
                for c in coeffs:
                    v = (v + c * xpow) % p
                    xpow = (xpow * L[i]) % p
                w_vals.append(v)
            bad = sweep_word(w_vals, L, n, p, threshold)
            for (h0, h1), S in bad:
                total_rand += 1
                if is_subgroup_aligned(set(S), n) is None:
                    total_rand_not += 1
                if len(S) > max_agree:
                    max_agree = len(S)
        print(f"    {n_trials} trials: witnesses={total_rand}, non-aligned={total_rand_not}, max_agree={max_agree}")

        # 3. "Structured" non-CS words: w = x^a + λ*x^b for various (a,b)
        print(f"  Structured words (w = x^a + λ*x^b, various a,b):")
        structured_hits = 0
        for a in range(1, 7):
            for b in range(a+1, 13):
                if (a, b) == (6, 4): continue  # skip CS
                for lam in range(p):
                    w_vals = [(pow(L[i], a, p) + lam * pow(L[i], b, p)) % p for i in range(n)]
                    bad = sweep_word(w_vals, L, n, p, threshold)
                    for (h0, h1), S in bad:
                        if is_subgroup_aligned(set(S), n) is None:
                            structured_hits += 1
        print(f"    non-aligned hits across all (a,b,λ): {structured_hits}")

        print()

if __name__ == "__main__":
    main()
