"""
Identify the number field controlling non-alignment for n=36.

For S = {0, a, b, c, d, e} ⊂ Z/36Z, define:
  F_S(X) = Σ X^i for i ∈ S
  G_S(X) = Σ X^{3i} for i ∈ S
  H_S(X) = 2·Σ X^{4i} - (Σ X^{2i})^2

S is a variety point iff X = ω (primitive 36th root in F_p) satisfies F=G=H=0.

Strategy:
1. For each non-aligned orbit rep from p=37, compute which primitive 36th
   roots of unity (in C) satisfy F=G=H=0.
2. These roots determine a factor of Φ_36(X), hence a subfield of Q(ζ_36).
3. The primes p for which S exists are those where this factor has a root in F_p.

Also: enumerate ALL non-subgroup-aligned S with 0∈S, and for each,
compute the common roots with Φ_36 using exact arithmetic mod a large prime.
"""
import cmath
from math import gcd, pi
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

def find_omega_Fp(p, n):
    pf = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in pf):
            return pow(g, (p-1)//n, p)
    raise RuntimeError

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

# ---------- Part 1: complex-analytic approach ----------

def check_roots_complex(S, n=36):
    """For subset S ⊂ Z/nZ, find which primitive n-th roots of unity
    satisfy F_S = G_S = H_S = 0 (up to numerical tolerance)."""
    coprime_to_n = [k for k in range(1, n) if gcd(k, n) == 1]
    zeta = cmath.exp(2j * pi / n)

    good_k = []
    for k in coprime_to_n:
        z = zeta ** k
        # F_S: sum z^i for i in S
        F = sum(z ** i for i in S)
        # G_S: sum z^{3i} for i in S
        G = sum(z ** (3*i) for i in S)
        # H_S: 2*sum(z^{4i}) - (sum(z^{2i}))^2
        p2 = sum(z ** (2*i) for i in S)
        p4 = sum(z ** (4*i) for i in S)
        H = 2 * p4 - p2 ** 2

        if abs(F) < 1e-10 and abs(G) < 1e-10 and abs(H) < 1e-10:
            good_k.append(k)

    return good_k

# ---------- Part 2: exact arithmetic mod large prime ----------

def check_roots_exact(S, n=36, P=None):
    """Same check but exact mod a large prime P ≡ 1 (mod n).
    Returns list of k coprime to n where conditions hold."""
    if P is None:
        # find large prime ≡ 1 mod n
        P = n + 1
        while not is_prime(P) or P < 10**6:
            P += n

    omega_P = find_omega_Fp(P, n)
    coprime_to_n = [k for k in range(1, n) if gcd(k, n) == 1]
    inv2 = pow(2, P-2, P)

    good_k = []
    for k in coprime_to_n:
        w = pow(omega_P, k, P)
        F = sum(pow(w, i, P) for i in S) % P
        G = sum(pow(w, 3*i, P) for i in S) % P
        p2 = sum(pow(w, 2*i, P) for i in S) % P
        p4 = sum(pow(w, 4*i, P) for i in S) % P
        H = (2 * p4 - p2 * p2) % P

        if F == 0 and G == 0 and H == 0:
            good_k.append(k)

    return good_k

# ---------- Part 3: enumerate all non-aligned S with 0 ∈ S ----------

def enumerate_all_non_aligned(n=36):
    """Find all non-aligned S ⊂ Z/nZ with 0 ∈ S, |S|=6,
    and classify by which Φ_n roots they use."""

    # Use a large prime for exact computation
    P = n + 1
    while not is_prime(P) or P < 10**7:
        P += n

    omega_P = find_omega_Fp(P, n)
    coprime_to_n = [k for k in range(1, n) if gcd(k, n) == 1]

    # precompute all powers
    w_powers = {}
    for k in coprime_to_n:
        w = pow(omega_P, k, P)
        w_powers[k] = [pow(w, i, P) for i in range(n)]

    results = defaultdict(list)  # frozenset(good_k) -> list of S

    for rest in combinations(range(1, n), 5):
        S = (0,) + rest
        if is_subgroup_aligned(set(S), n) is not None:
            continue

        good_k = []
        for k in coprime_to_n:
            wp = w_powers[k]
            F = sum(wp[i] for i in S) % P
            if F != 0: continue
            G = sum(wp[(3*i) % n] for i in S) % P
            if G != 0: continue
            p2 = sum(wp[(2*i) % n] for i in S) % P
            p4 = sum(wp[(4*i) % n] for i in S) % P
            H = (2 * p4 - p2 * p2) % P
            if H == 0:
                good_k.append(k)

        if good_k:
            results[frozenset(good_k)].append(S)

    return results, P

def main():
    n = 36
    print(f"=== Number field identification for n={n} ===\n")

    # Known orbit reps from p=37 and p=181
    # p=37: orbit rep (4,5,17,29,32,33) → shifted to (0,1,13,25,28,29)
    S_37 = (0, 1, 13, 25, 28, 29)
    # p=181: orbit rep (1,3,12,14,15,27) → shifted to (0,2,11,13,14,26)
    S_181 = (0, 2, 11, 13, 14, 26)

    print("--- Complex-analytic check ---")
    for label, S in [("p=37 orbit", S_37), ("p=181 orbit", S_181)]:
        good_k = check_roots_complex(S, n)
        print(f"  {label}: S={S}")
        print(f"    Roots ζ^k with F=G=H=0: k ∈ {good_k}")
        if good_k:
            print(f"    #roots = {len(good_k)} out of φ(36)=12")
            # These k values determine the number field:
            # the factor of Φ_36 with these roots has degree len(good_k)
            # and corresponds to a subfield of Q(ζ_36) of degree 12/len(good_k)
            print(f"    ⟹ factor of Φ_36 has degree {len(good_k)}")
            print(f"    ⟹ number field has degree {len(good_k)} over Q")

    print(f"\n--- Exact check mod large prime ---")
    # Use several large primes to confirm
    for P_cand in [1000037, 2000089]:
        # adjust to ≡ 1 mod 36
        P = P_cand + (-P_cand % 36) + 1
        while not is_prime(P): P += 36
        for label, S in [("p=37 orbit", S_37), ("p=181 orbit", S_181)]:
            good_k = check_roots_exact(S, n, P)
            print(f"  P={P}: {label}: k ∈ {good_k}")

    print(f"\n--- Full enumeration of non-aligned S with 0 ∈ S ---")
    results, P = enumerate_all_non_aligned(n)
    print(f"  (computed mod P={P})")
    print(f"  {len(results)} distinct root-sets found:")
    for ks, S_list in sorted(results.items(), key=lambda x: (-len(x[1]), sorted(x[0]))):
        ks_sorted = sorted(ks)
        print(f"    roots k={ks_sorted} (deg {len(ks_sorted)}): {len(S_list)} subsets")
        for S in S_list[:3]:
            print(f"      ex: {S}")
        if len(S_list) > 3:
            print(f"      ... ({len(S_list)} total)")

    # Key question: do different root-sets correspond to conjugate factors?
    print(f"\n--- Galois structure ---")
    print(f"  (Z/36Z)* = {sorted(k for k in range(1,36) if gcd(k,36)==1)}")
    print(f"  |G| = {sum(1 for k in range(1,36) if gcd(k,36)==1)}")

    # Check: are the root-sets Galois-conjugate?
    # σ_a: ζ^k → ζ^{ak}, so the root set {k} maps to {ak mod 36}
    G = sorted(k for k in range(1, 36) if gcd(k, 36) == 1)
    print(f"  Checking if root-sets are orbits under Galois action...")
    all_root_sets = list(results.keys())
    for rs in all_root_sets:
        rs_sorted = sorted(rs)
        conjugates = set()
        for a in G:
            conj = frozenset((a * k) % 36 for k in rs)
            conjugates.add(conj)
        print(f"    root-set {rs_sorted} has {len(conjugates)} Galois conjugates")
        # check which of these are also in our results
        present = sum(1 for c in conjugates if c in results)
        print(f"      of which {present} are present in our enumeration")

    # Prime characterization
    print(f"\n--- Which primes p ≡ 1 (mod 36) give non-alignment? ---")
    print(f"  At prime p, the Frobenius acts as multiplication by p on Z/36Z")
    print(f"  ω = g^{{(p-1)/36}} where g is a primitive root mod p")
    print(f"  The embedding sends ζ → ω, i.e., ζ^k → ω^k")
    print(f"  S exists at p iff the Frobenius orbit of some root-set contains")
    print(f"  an element k such that ζ^k → ω gives F_S=G_S=H_S=0")
    print(f"")
    print(f"  Concretely: p gives non-alignment iff p (mod 36) generates")
    print(f"  a coset that intersects one of the root-sets.")
    print(f"")

    # For each prime p �� 1 mod 36, the Frobenius at p in Gal(Q(ζ_36)/Q)
    # is the automorphism σ_p: ζ → ζ^p, i.e., multiplication by p mod 36.
    # A root ζ^k is "available" at p iff k ≡ p^j (mod 36) for some j,
    # i.e., k is in the cyclic group generated by p mod 36 in (Z/36Z)*.
    # BUT since p splits completely (p ≡ 1 mod 36), σ_p = identity!
    # So ALL roots are available at every such p.

    # Wait — that's not right. p ≡ 1 mod 36 means Frobenius = identity,
    # which means EVERY factor of Φ_36 has a root mod p.
    # So if any root-set is non-empty, S should exist at ALL p ≡ 1 mod 36.
    # But empirically it doesn't!

    print(f"  WARNING: p ≡ 1 (mod 36) ⟹ Frob_p = id in Gal(Q(ζ_36)/Q)")
    print(f"  This means ALL roots of Φ_36 exist in F_p.")
    print(f"  So if root-set is non-empty, S should exist at ALL such p!")
    print(f"  But empirically non-alignment only at p=37,181.")
    print(f"  ⟹ The number field is NOT a subfield of Q(ζ_36)!")
    print(f"  ⟹ The conditions involve MORE than just ω (they involve")
    print(f"     the specific embedding Z[ζ_36] → F_p, not just which")
    print(f"     roots of Φ_36 exist).")
    print(f"")
    print(f"  Resolution: the conditions F_S=0 depend on S AND ω jointly.")
    print(f"  For different p, even though all ζ^k are available, the")
    print(f"  specific S that works CHANGES. The variety V lives in a")
    print(f"  mixed space (discrete × algebraic), and the number field")
    print(f"  is the splitting field of the variety equations, which is")
    print(f"  larger than Q(ζ_36).")

if __name__ == "__main__":
    main()
