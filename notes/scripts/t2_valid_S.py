"""
T2.1: Find ALL valid 6-subsets S at the worst case and analyze their structure.

For (6,5), λ=1: S must satisfy e_1=-1, e_2=e_3=e_4=0.
Equivalently: p_1 = -1, p_2 = 1, p_3 = -1, p_4 = 1.
(p_k = c^k where c = -λ = -1.)

Enumerate all C(n,6) subsets and check.
For n ≤ 120: C(120,6) ≈ 3.5 × 10^9 — too many for brute force.

Instead: use the Lagrange trick. For each pair (i,j), compute h1 = D(i,j).
Then for that h1, find the full level set. If size ≥ 6, record S.

This is O(n^2 * n) = O(n^3) per word.
"""
from math import gcd
from collections import defaultdict

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

def main():
    t = 6; a = 6; b = 5; lam = 1

    for n in [36, 60, 120]:
        p = find_proper_prime(n, min_ratio=2)
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]
        c = [(pow(L[i],a,p) + lam*pow(L[i],b,p)) % p for i in range(n)]

        print(f"\n=== n={n}, p={p}, w=x^6+x^5 ===")

        # Find all rich (h0, h1) via pair enumeration
        seen_h = {}
        for i in range(n):
            for j in range(i+1, n):
                dx = (L[j] - L[i]) % p
                dy = (c[j] - c[i]) % p
                h1 = (dy * modinv(dx, p)) % p
                h0 = (c[i] - h1 * L[i]) % p
                key = (h0, h1)
                if key in seen_h: continue
                S = tuple(sorted(idx for idx in range(n)
                                 if (h0 + h1*L[idx]) % p == c[idx]))
                seen_h[key] = S

        rich = {k: S for k, S in seen_h.items() if len(S) >= t}
        print(f"  #rich (h0,h1) = {len(rich)}")

        # Analyze the valid S
        all_S = [S for S in rich.values()]
        print(f"  #valid S = {len(all_S)}")

        # Check: are S related by multiplication mod n?
        # S' = {(a*i) % n : i ∈ S} for a ∈ (Z/nZ)*
        coprime = [a for a in range(1, n) if gcd(a, n) == 1]

        # Group S into orbits under (Z/nZ)* action
        S_set = set(all_S)
        orbits = []
        remaining = set(all_S)
        while remaining:
            rep = next(iter(remaining))
            orbit = set()
            for aa in coprime:
                rotated = tuple(sorted((aa * i) % n for i in rep))
                if rotated in S_set:
                    orbit.add(rotated)
            orbits.append((rep, orbit))
            remaining -= orbit

        print(f"  #orbits under (Z/nZ)*: {len(orbits)}")
        for rep, orb in orbits:
            print(f"    orbit size {len(orb)}: rep={rep}")

        # Check: are S related by cyclic shift + scaling?
        # S' = {(i + s) % n : i ∈ S} shifts e_1 by factor ω^s.
        # For e_1 = -1 to be preserved: ω^s * (-1) = -1, so ω^s = 1, s = 0.
        # So cyclic shift does NOT preserve the condition (unless s=0).

        # Check: difference sets structure
        # For each S, compute the difference set {(i-j) % n : i,j ∈ S, i≠j}
        if len(all_S) <= 30:
            diff_profiles = {}
            for S in all_S:
                diffs = tuple(sorted(set((S[i]-S[j]) % n for i in range(len(S)) for j in range(len(S)) if i != j)))
                diff_profiles[S] = diffs
            # Are all difference sets the same?
            unique_diffs = set(diff_profiles.values())
            print(f"  #unique difference sets: {len(unique_diffs)}")

        # Check: are the h1 values forming any algebraic pattern?
        h1_vals = sorted(set(h1 for (h0, h1) in rich.keys()))
        print(f"  Rich h1 values ({len(h1_vals)}): {h1_vals[:20]}{'...' if len(h1_vals)>20 else ''}")

        # Check if h1 values form a coset of a subgroup of F_p*
        if len(h1_vals) >= 2 and h1_vals[0] != 0:
            ratios = set()
            for i in range(len(h1_vals)):
                for j in range(i+1, len(h1_vals)):
                    r = (h1_vals[j] * modinv(h1_vals[i], p)) % p
                    ratios.add(r)
            # If all ratios form a subgroup: the h1's are a coset
            print(f"  #distinct h1 ratios: {len(ratios)} (out of C({len(h1_vals)},2)={len(h1_vals)*(len(h1_vals)-1)//2})")

        # Check: what's the image of S under the DFT?
        # Compute p_k(S) = Σ_{j∈S} ω^{kj} for k=0,...,n-1
        if all_S and n <= 60:
            S0 = all_S[0]
            print(f"  DFT of S={S0}:")
            for k in range(min(8, n)):
                pk = sum(pow(omega, k*j, p) for j in S0) % p
                print(f"    p_{k} = {pk}", end="")
                if k <= 4:
                    expected = pow((-lam) % p, k, p) if k > 0 else len(S0)
                    print(f"  (expected: {expected})", end="")
                print()

if __name__ == "__main__":
    main()
