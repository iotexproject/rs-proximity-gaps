"""
T2.1 Proof attempt: Resultant approach for bounding list size.

For k=2: the agreement polynomial is P(x) = w(x) - h0 - h1*x.
P has all roots in L iff Res_x(P, x^n - 1) = 0.

This resultant R(h0, h1) is a polynomial in (h0, h1) over F_p.
Its degree is n in each variable (from Bezout).

A t-rich point (h0, h1) is one where P has ≥ t roots in L.
This means (h0, h1) lies on the "t-th secant variety" of the curve
{(w(ω^i) - h1·ω^i, h1) : h1 ∈ F_p} (varying i).

Alternative: define R_i(h0, h1) = w(ω^i) - h0 - h1·ω^i for each i.
The agreement set is S = {i : R_i = 0}. So |S| ≥ t iff h lies on ≥ t
of the n hyperplanes R_i = 0.

For k=2: each R_i = 0 is a LINE in (h0, h1)-plane. So we're counting
t-rich points of n lines. The structure of these lines (their slopes
form a multiplicative subgroup) is the key.

Approach: compute the polynomial Π_{|T|=t, T⊂[n]} Σ_{i∈T} R_i(h0,h1)
or some symmetric function that detects t-rich points.

Actually, a cleaner approach: define
  F(h0, h1, z) = Π_{i=0}^{n-1} (1 + z·R_i(h0, h1))
  = Π_i (1 + z·(w(ω^i) - h0 - h1·ω^i))

Expand: the coefficient of z^t in F gives (a sum over t-subsets) whose
zeros include the t-rich points.

For specific w and small n: compute this explicitly.
"""
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

def main():
    # Small case: n=12, p=13 (n = p-1, full group)
    # Also n=12 with proper subgroup: p=37 (ratio 3)
    cases = [(12, 13), (12, 37), (24, 73)]

    for n, p in cases:
        omega = find_omega(p, n)
        L = [pow(omega, i, p) for i in range(n)]

        print(f"\n=== n={n}, p={p}, ratio={(p-1)//n} ===")

        # For w = x^6 + lam*x^5 (worst case from scaling):
        for lam in [0, 1]:
            c = [(pow(L[i], 6, p) + lam * pow(L[i], 5, p)) % p for i in range(n)]

            print(f"\n  w = x^6 + {lam}*x^5:")

            # The n lines are: h0 + h1*ω^i = c_i, i.e., h0 = c_i - h1*ω^i
            # slopes: ω^i (form the subgroup L)
            # intercepts: c_i

            # For each h1 ∈ F_p: the function g(i) = c_i - h1*ω^i maps [n] → F_p
            # Agreement with h0: |{i : g(i) = h0}|
            # = multiplicity of h0 in the multiset {g(0), g(1), ..., g(n-1)}

            # The "agreement profile" of h1 is the partition of n into level sets of g
            # A t-rich h0 exists iff max level set ≥ t

            # Compute the agreement profile for each h1:
            t_thresh = 6
            rich_points = []
            profile_dist = {}

            for h1 in range(p):
                level_sets = {}
                for i in range(n):
                    h0 = (c[i] - h1 * L[i]) % p
                    level_sets[h0] = level_sets.get(h0, 0) + 1
                sizes = sorted(level_sets.values(), reverse=True)
                profile = tuple(sizes)
                profile_dist[profile] = profile_dist.get(profile, 0) + 1

                for h0, cnt in level_sets.items():
                    if cnt >= t_thresh:
                        rich_points.append((h0, h1, cnt))

            print(f"    #rich points (agree≥{t_thresh}): {len(rich_points)}")
            if rich_points:
                max_agree = max(r[2] for r in rich_points)
                print(f"    max agreement: {max_agree}")

            # Show profile distribution
            print(f"    Agreement profiles (top 10):")
            for prof, cnt in sorted(profile_dist.items(), key=lambda x: -x[1])[:10]:
                print(f"      {prof}: {cnt} h1-values")

            # Key question: what's the algebraic degree of the "rich locus"?
            # For each h1 with a t-rich h0: the rich h0 is determined by h1.
            # So the rich locus is a set of (h0(h1), h1) points where h0 is an
            # explicit function of h1 (the t-popular level of g_{h1}).

            # The function h0(h1) = argmax_{h0} |{i : c_i - h1*ω^i = h0}|
            # This is a combinatorial function, not algebraic. But the LOCUS
            # {(h0, h1) : exactly t of the c_i - h1*ω^i equal h0} is defined
            # by a system of polynomial equations.

            # Specifically: for S = {i_1,...,i_t} ⊂ [n], the condition
            # c_{i_j} - h1*ω^{i_j} = h0 for all j gives:
            # h0 = c_{i_1} - h1*ω^{i_1}, and
            # c_{i_j} - h1*ω^{i_j} = c_{i_1} - h1*ω^{i_1} for j=2,...,t
            # i.e., h1 = (c_{i_1} - c_{i_j})/(ω^{i_j} - ω^{i_1}) for each j

            # All these must give the SAME h1. This constrains S to have
            # a specific algebraic structure.

            # For t=6: 5 equations h1 = f(i_1, i_j) must all agree.
            # This is equivalent to: the 6 points (ω^{i_j}, c_{i_j}) are collinear.

            # The number of collinear t-tuples on the graph G determines M.
            # Already explored in s1_collinear_triples.py.

            # NEW IDEA: the graph G = {(ω^i, c_i)} lies on an algebraic curve
            # C: y = x^6 + lam*x^5 of degree 6 (in x, not in y).
            # A line L: y = h0 + h1*x intersects C at the roots of
            # x^6 + lam*x^5 - h1*x - h0 = 0, a degree-6 polynomial.
            # The roots lie in L (subgroup) iff all 6 roots are n-th roots of unity.

            # Condition: Π_{roots α} (α^n - 1) = 0... no, each root must satisfy α^n = 1.
            # Equivalently: gcd(x^6 + lam*x^5 - h1*x - h0, x^n - 1) has degree ≥ t.

            # The RESULTANT R(h0, h1) = Res_x(x^6 + lam*x^5 - h1*x - h0, x^n - 1)
            # is zero iff they share a common root. It's a polynomial in (h0, h1).

            # Compute R for our small cases:
            # Method: R = Π_{ω^i ∈ L} (ω^{6i} + lam*ω^{5i} - h1*ω^i - h0)
            #         = Π_i (c_i - h0 - h1*ω^i)
            # (since x^n - 1 = Π_i (x - ω^i))

            # R(h0, h1) = Π_{i=0}^{n-1} (c_i - h0 - h1*ω^i)

            # This is a degree-n polynomial in h0 (and degree n in h1 after expansion).

            # The t-rich points have R vanishing to order ≥ t.
            # More precisely: (h0, h1) is t-rich iff exactly t factors vanish.

            # The "t-fold vanishing locus" of R:
            # Compute Σ_{S ⊂ [n], |S|=t} Π_{i ∈ S} (c_i - h0 - h1*ω^i) = 0
            # This is the (n-t)-th elementary symmetric polynomial of
            # {c_i - h0 - h1*ω^i}.

            # e_{n-t}(c_0 - h0 - h1*ω^0, ..., c_{n-1} - h0 - h1*ω^{n-1}) = 0
            # when evaluated at (h0, h1).

            # For t=6 and n=12: this is e_6 of 12 linear forms in (h0, h1).
            # Degree: 6 in (h0, h1) jointly.

            # Wait: each factor (c_i - h0 - h1*ω^i) is degree 1 in (h0, h1).
            # e_{n-t} of n linear forms has degree n-t.
            # For n=12, t=6: degree 6.
            # For n=24, t=6: degree 18.

            # A degree-d polynomial in 2 variables has at most d^2 zeros (by Bezout)
            # if it's not degenerate. But it could have curves of zeros.

            # The condition for t-rich is: ALL of e_{n-t+1}, e_{n-t+2}, ..., e_n vanish
            # (these are the higher elementary symmetric functions, which force ≥ t factors to vanish).

            # Actually: the condition |S| ≥ t is equivalent to
            # R_j(h0, h1) = 0 for j = n-t+1, ..., n, where R_j is e_j of the n linear forms.

            # No wait. If e_n = Π_i (c_i - h0 - h1*ω^i) = 0, that means at least 1 factor is 0.
            # e_{n-1} = Σ_i Π_{j≠i} (c_j - h0 - h1*ω^j) vanishes when ≥ 2 factors are 0.
            # In general: e_{n-t+1} = ... vanishes when ≥ t factors are 0.

            # So the t-rich locus is defined by e_{n-t+1} = 0.
            # Its degree is n-t+1 in (h0, h1).

            # For n=12, t=6: degree 7.
            # For n=24, t=6: degree 19.
            # For general n: degree n-5.

            # By Bezout: a degree-(n-5) polynomial in 2 variables has at most (n-5)^2
            # isolated zeros. But it could have positive-dimensional components.

            # If the t-rich locus is a curve: it has degree n-5, with at most
            # (n-5)*p points in F_p^2 (Hasse-Weil). The number of t-rich points
            # is ≤ (n-5)*p + O(sqrt(p)*genus).

            # But this gives M = O(n*p), not O(n). We need ISOLATED points, not curves.

            # The t-rich locus has ANOTHER condition: e_{n-t} also vanishes when ≥ t+1
            # factors vanish. The "exactly t" condition is e_{n-t+1} = 0 but e_{n-t} ≠ 0.

            # But for list-size: we want ≥ t, not exactly t. So it's just e_{n-t+1} = 0.

            # deg(e_{n-t+1}) = n-t+1 in the 2 variables (h0, h1).

            # KEY OBSERVATION: e_{n-t+1} is a polynomial of degree n-t+1 in (h0, h1).
            # But h0 and h1 are SEPARATE variables, and each factor is DEGREE 1 in (h0, h1).
            # So e_{n-t+1} has degree n-t+1 as a polynomial in 2 variables.
            # In h0 alone: degree n-t+1. In h1 alone: also degree n-t+1.

            # For a polynomial of degree d in F_p[h0, h1]:
            # Schwartz-Zippel: for random (h0, h1), Pr[f = 0] ≤ d/p.
            # Total zeros: ≤ d*p (by fixing h1 and counting h0-roots).

            # So M ≤ (n-t+1) * p. Way too much.

            # But we want M per WORD (fixed w), so (h0, h1) ranges over F_p^2.
            # The bound (n-5)*p is useless.

            # HOWEVER: if we can show e_{n-t+1} factors as a product of lower-degree
            # polynomials using the MULTIPLICATIVE structure of L, the bound improves.

            # The n linear forms are c_i - h0 - h1*ω^i. Their coefficients involve
            # the n-th roots of unity ω^i. The elementary symmetric polynomial of
            # these forms is a SYMMETRIC FUNCTION of the roots of unity.

            # e_m({c_i - h0 - h1*ω^i}) = Σ_{|S|=m} Π_{i∈S} (c_i - h0 - h1*ω^i)

            # For c_i = ω^{6i} + lam*ω^{5i} (the specific word):
            # c_i - h0 - h1*ω^i = ω^{6i} + lam*ω^{5i} - h1*ω^i - h0

            # Substituting x = ω^i: this is x^6 + lam*x^5 - h1*x - h0 evaluated at x = ω^i.

            # So e_m = e_m({P(ω^i)}) where P(x) = x^6 + lam*x^5 - h1*x - h0.

            # Now: Π_{i=0}^{n-1} (z - P(ω^i)) = Res_x(z - P(x), x^n - 1) / leading coeff.

            # This resultant in z and x is a polynomial in z of degree n.
            # Its roots are P(ω^0), P(ω^1), ..., P(ω^{n-1}).
            # So e_m({P(ω^i)}) is the m-th elementary symmetric polynomial of these roots.

            # By Newton's identities: e_m relates to power sums p_k = Σ P(ω^i)^k.

            # p_k = Σ_{i=0}^{n-1} P(ω^i)^k

            # For k=1: p_1 = Σ P(ω^i) = Σ (ω^{6i} + lam*ω^{5i} - h1*ω^i - h0)
            #          = Σω^{6i} + lam*Σω^{5i} - h1*Σω^i - n*h0

            # Character orthogonality: Σω^{ji} = n if n|j, else 0.

            # For gcd(6,n) > 0: Σω^{6i} = n if n|6, i.e., n ∈ {1,2,3,6}, else 0.
            # Similarly for other exponents.

            # For n=12: Σω^{6i} = Σ(ω^6)^i. ω^6 has order 12/gcd(6,12) = 2.
            # So Σ(ω^6)^i = 0 (sum of n-th roots of (ω^6) ... actually
            # Σ_{i=0}^{11} ω^{6i} = Σ_{i=0}^{11} (ω^6)^i. ω^6 is a primitive 2nd root
            # of unity (since ord(ω)=12, ord(ω^6)=12/6=2). So Σ = 0 (6 copies of 1 + 6 copies of -1).
            # Wait: ω^{6*0}=1, ω^{6*1}=ω^6, ω^{6*2}=ω^{12}=1, etc. It's periodic with period 2.
            # Sum = 6*(1 + ω^6) = 6*(1 + (-1)) = 0 (if ω^6 = -1 in F_p, which it is when p≡1 mod 12).
            # For p=13: ω = primitive 12th root. ω^6 ≡ -1 mod 13. So Σ = 0. ✓

            # So for n=12: p_1 = 0 + 0 - 0 - 12*h0 = -12*h0 (mod p).

            # For n=24, same exponents: Σω^{6i} over i=0..23. ω^6 has order 24/gcd(6,24)=4.
            # Sum of all 24th roots of ω^6 = sum of {(ω^6)^i : i=0..23} = 0. So p_1 = -24*h0 = -nh0.

            # In general: p_1 = -n*h0 (since all character sums vanish for n ≥ 7).
            # (The sums Σω^{ji} = 0 for j ∈ {1,5,6} and n > 6.)

            # So e_1 = p_1 = -n*h0. (First elementary symmetric = sum = -n*h0.)

            # For t-rich: e_{n-5} = 0. The relationship between e_{n-5} and power sums
            # involves all p_k for k ≤ n-5. These p_k involve character sums:
            # p_k = Σ P(ω^i)^k = expansion using multinomial theorem and character orthogonality.

            # This is getting deep. Let me just compute e_{n-t+1} for small cases.

            # For n=12, t=6: need e_7 = 0.
            # 12 linear forms L_i = c_i - h0 - h1*ω^i.
            # e_7(L_0, ..., L_{11}) is a degree-7 polynomial in (h0, h1).

            # Compute it by expanding:
            from itertools import combinations
            e_val = {}
            for h1_val in range(p):
                for h0_val in range(p):
                    forms = [(c[i] - h0_val - h1_val * L[i]) % p for i in range(n)]
                    # count zeros
                    nz = sum(1 for f in forms if f == 0)
                    if nz >= t_thresh:
                        e_val[(h0_val, h1_val)] = nz

            print(f"    t-rich locus size: {len(e_val)}")
            if e_val:
                # Analyze: for each h1, how many h0?
                h1_counts = {}
                for (h0, h1), nz in e_val.items():
                    h1_counts[h1] = h1_counts.get(h1, 0) + 1
                print(f"    h1 distribution: {sorted(h1_counts.values(), reverse=True)[:10]}")
                print(f"    max agree: {max(e_val.values())}")

if __name__ == "__main__":
    main()
