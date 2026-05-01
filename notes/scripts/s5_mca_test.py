"""
S5 — Mutual Correlated Agreement (MCA) test.

MCA: given M words w_1,...,w_M, does there exist a COMMON agreement set D ⊂ L
with |D| ≥ (1-δ)n such that for each w_ℓ, there exists h_ℓ ∈ RS_k with
w_ℓ agrees with h_ℓ on D?

This is MUCH harder to satisfy than individual proximity: the SAME D must
work for all w_ℓ simultaneously.

For k=2: each h_ℓ is a line. The condition is: ∀ℓ, ∀x∈D: w_ℓ(x) = h_{ℓ,0} + h_{ℓ,1}·x.

Equivalently: D ⊂ L with |D| ≥ t, and for each ℓ, the restriction w_ℓ|_D
is a degree-<k polynomial (a line).

Test: for M=2 words w_1, w_2, find pairs (h_1, h_2) with |S_1 ∩ S_2| ≥ t.

For M=3: find triples (h_1, h_2, h_3) with |S_1 ∩ S_2 ∩ S_3| ≥ t.
"""
from math import gcd
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

def find_rich_lines(L, w_vals, p, n, threshold):
    """Find all (h0, h1) with agreement ≥ threshold. Return dict: (h0,h1)->agreement_set."""
    rich = {}
    seen = {}
    for i in range(n):
        for j in range(i + 1, n):
            dx = (L[j] - L[i]) % p
            dy = (w_vals[j] - w_vals[i]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (w_vals[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen: continue
            S = frozenset(idx for idx in range(n)
                          if (h0 + h1 * L[idx]) % p == w_vals[idx])
            seen[key] = S
            if len(S) >= threshold:
                rich[key] = S
    return rich

def test_mca_M2(L, w1_vals, w2_vals, p, n, threshold):
    """MCA test for M=2: find common agreement sets."""
    rich1 = find_rich_lines(L, w1_vals, p, n, threshold)
    rich2 = find_rich_lines(L, w2_vals, p, n, threshold)

    mca_pairs = []
    for h1, S1 in rich1.items():
        for h2, S2 in rich2.items():
            D = S1 & S2  # common agreement
            if len(D) >= threshold:
                mca_pairs.append((h1, h2, D))
    return mca_pairs

def main():
    threshold = 6
    print(f"=== S5: MCA test ===")
    print(f"threshold t={threshold}, k=2\n")

    test_cases = [
        (36, 37), (36, 73),
        (60, 61), (60, 181),
        (72, 73),
        (96, 97),
    ]

    for n, p in test_cases:
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        print(f"--- n={n}, p={p}, (p-1)/n={(p-1)//n} ---")

        # Single-word list sizes (for reference)
        # Test with CS and (6,5) words
        ab_pairs = [(6, 4), (6, 5), (7, 6)]
        for a, b in ab_pairs:
            max_M = 0
            for lam in range(min(p, 50)):
                w_vals = [(pow(L[i], a, p) + lam * pow(L[i], b, p)) % p for i in range(n)]
                rich = find_rich_lines(L, w_vals, p, n, threshold)
                max_M = max(max_M, len(rich))
            print(f"  Single word ({a},{b}): max_M = {max_M}")

        # MCA M=2: two independent CS words with different λ
        print(f"\n  MCA M=2 tests:")

        # Test 1: two CS words w1 = x^6 + λ1*x^4, w2 = x^6 + λ2*x^4
        mca_count = 0
        mca_max_D = 0
        for lam1 in range(min(p, 30)):
            w1 = [(pow(L[i], 6, p) + lam1 * pow(L[i], 4, p)) % p for i in range(n)]
            for lam2 in range(lam1 + 1, min(p, 30)):
                w2 = [(pow(L[i], 6, p) + lam2 * pow(L[i], 4, p)) % p for i in range(n)]
                pairs = test_mca_M2(L, w1, w2, p, n, threshold)
                if pairs:
                    mca_count += len(pairs)
                    for _, _, D in pairs:
                        mca_max_D = max(mca_max_D, len(D))
        print(f"    CS+CS: {mca_count} MCA pairs, max |D|={mca_max_D}")

        # Test 2: CS + (6,5) words
        mca_count2 = 0
        mca_max_D2 = 0
        for lam1 in range(min(p, 30)):
            w1 = [(pow(L[i], 6, p) + lam1 * pow(L[i], 4, p)) % p for i in range(n)]
            for lam2 in range(min(p, 30)):
                w2 = [(pow(L[i], 6, p) + lam2 * pow(L[i], 5, p)) % p for i in range(n)]
                pairs = test_mca_M2(L, w1, w2, p, n, threshold)
                if pairs:
                    mca_count2 += len(pairs)
                    for _, _, D in pairs:
                        mca_max_D2 = max(mca_max_D2, len(D))
        print(f"    CS+(6,5): {mca_count2} MCA pairs, max |D|={mca_max_D2}")

        # Test 3: two (7,6) words
        mca_count3 = 0
        mca_max_D3 = 0
        for lam1 in range(min(p, 20)):
            w1 = [(pow(L[i], 7, p) + lam1 * pow(L[i], 6, p)) % p for i in range(n)]
            for lam2 in range(lam1 + 1, min(p, 20)):
                w2 = [(pow(L[i], 7, p) + lam2 * pow(L[i], 6, p)) % p for i in range(n)]
                pairs = test_mca_M2(L, w1, w2, p, n, threshold)
                if pairs:
                    mca_count3 += len(pairs)
                    for _, _, D in pairs:
                        mca_max_D3 = max(mca_max_D3, len(D))
        print(f"    (7,6)+(7,6): {mca_count3} MCA pairs, max |D|={mca_max_D3}")

        # Key comparison: MCA list size vs single-word list size
        # If MCA pairs = 0: MCA is MUCH stronger than single proximity
        print()

if __name__ == "__main__":
    main()
