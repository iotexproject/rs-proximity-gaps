"""
FRI folding analysis: connect list-size bounds to per-round soundness.

FRI folding:
  - Domain L of order n, split as L = L_0 ∪ L_1 (cosets of L^2)
  - Word f on L decomposed: f(x) = f_even(x^2) + x·f_odd(x^2)
  - Verifier sends random α
  - Folded word: f'(y) = f_even(y) + α·f_odd(y) on L' = {x^2 : x ∈ L}

If f is δ-close to RS_k:
  - ∃h ∈ RS_k with agree(f, h) ≥ (1-δ)n
  - h decomposes: h(x) = h_even(x^2) + x·h_odd(x^2)
  - Folded: h'(y) = h_even(y) + α·h_odd(y) ∈ RS_{k/2} on L'
  - agree(f', h') ≥ ... (need to analyze)

If f is δ-FAR from RS_k (list-size = 0):
  - f' should also be far from RS_{k/2}
  - The proximity gap says: fraction of α where f' is close ≤ ε

Our contribution: bound the list size M at the operating point.
For power-of-2 domains (Thm 6): M = O(1). This means:
  - Only O(1) codewords are δ-close to f
  - For each, the folding maps it to a specific h' ∈ RS_{k/2}
  - The probability that f' agrees with h' is ≈ 1 (if f was genuinely close)
  - The probability that f' agrees with ANY h' (when f is far) is ≤ M/(p·something)

Let me simulate FRI folding and measure the actual soundness.
"""
from math import gcd

def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    d=5
    while d*d<=n:
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

def fri_fold(f_vals, L, alpha, p, n):
    """FRI folding: f on L of order n → f' on L' of order n/2.
    L is ordered as (x_0, x_1, ..., x_{n-1}) where x_i = ω^i.
    L^2 = {x^2 : x ∈ L} has order n/2.
    For each y ∈ L^2: there are exactly 2 preimages x, -x in L.
    f'(y) = (f(x) + f(-x))/2 + α·(f(x) - f(-x))/(2x).
    """
    n2 = n // 2
    omega = L[1] * modinv(L[0], p) % p if L[0] != 1 else L[1]
    # actually L[i] = ω^i, so -x for x = ω^i is ω^{i+n/2} (since ω^{n/2} = -1)

    f_prime = []
    L_prime = []
    for i in range(n2):
        x = L[i]
        neg_x = L[i + n2]  # ω^{i+n/2} = -ω^i
        y = (x * x) % p  # y = x^2
        L_prime.append(y)

        fx = f_vals[i]
        fnx = f_vals[i + n2]

        inv2 = modinv(2, p)
        inv2x = modinv((2 * x) % p, p)

        f_even = ((fx + fnx) * inv2) % p
        f_odd = ((fx - fnx) * inv2x) % p

        f_prime.append((f_even + alpha * f_odd) % p)

    return f_prime, L_prime

def count_close_codewords(f_vals, L, p, n, k, threshold):
    """Count degree-<k polynomials h with agree(f, h) ≥ threshold."""
    if k != 2:
        raise NotImplementedError("only k=2")
    seen = {}
    for i in range(n):
        for j in range(i+1, n):
            dx = (L[j] - L[i]) % p
            dy = (f_vals[j] - f_vals[i]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (f_vals[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen: continue
            ag = sum(1 for idx in range(n) if (h0 + h1*L[idx]) % p == f_vals[idx])
            seen[key] = ag
    return sum(1 for v in seen.values() if v >= threshold)

def main():
    import random; random.seed(42)

    # Power-of-2 domain
    n = 64; p = 193  # n = 2^6
    omega_val = find_omega(p, n)
    L = [pow(omega_val, i, p) for i in range(n)]

    k = 2; t = 6
    delta = 1 - t/n  # ≈ 0.906

    print(f"FRI folding analysis: n={n}, p={p}, k={k}, t={t}, δ={delta:.3f}")
    print(f"Thm 6: power-of-2, gcd(5,64)=1 → M = O(1)\n")

    # Test 1: f = codeword (should be close after folding)
    print("Case 1: f IS a codeword (h0=5, h1=3)")
    h0, h1 = 5, 3
    f_codeword = [(h0 + h1 * L[i]) % p for i in range(n)]

    for alpha in [1, 7, 42]:
        f_prime, L_prime = fri_fold(f_codeword, L, alpha, p, n)
        M_after = count_close_codewords(f_prime, L_prime, p, n//2, k, t)
        print(f"  α={alpha}: folded list size = {M_after}")

    # Test 2: f = worst-case word (x^6 + x^5)
    print(f"\nCase 2: f = x^6 + x^5 (worst-case from Thm 4)")
    lam = 1
    f_worst = [(pow(L[i],6,p) + lam*pow(L[i],5,p)) % p for i in range(n)]
    M_before = count_close_codewords(f_worst, L, p, n, k, t)
    print(f"  Before folding: M = {M_before}")

    fold_Ms = []
    for alpha in range(min(p, 50)):
        f_prime, L_prime = fri_fold(f_worst, L, alpha, p, n)
        M_after = count_close_codewords(f_prime, L_prime, p, n//2, k, t)
        fold_Ms.append(M_after)

    print(f"  After folding (50 alphas): max M' = {max(fold_Ms)}, "
          f"mean M' = {sum(fold_Ms)/len(fold_Ms):.2f}, "
          f"#(M'>0) = {sum(1 for m in fold_Ms if m > 0)}")

    # Test 3: f = random word (should be far from RS)
    print(f"\nCase 3: f = random word (should be far from RS)")
    for trial in range(5):
        f_random = [random.randint(0, p-1) for _ in range(n)]
        M_before = count_close_codewords(f_random, L, p, n, k, t)

        fold_Ms = []
        for alpha in range(min(p, 50)):
            f_prime, L_prime = fri_fold(f_random, L, alpha, p, n)
            M_after = count_close_codewords(f_prime, L_prime, p, n//2, k, t)
            fold_Ms.append(M_after)

        print(f"  trial {trial}: before M={M_before}, after max M'={max(fold_Ms)}, "
              f"#(M'>0)={sum(1 for m in fold_Ms if m > 0)}")

    # Test 4: Soundness game — how often does folding "leak" closeness?
    print(f"\nSoundness test: 100 random far-words, check if ANY alpha gives M'>0 after fold")
    leaks = 0
    for trial in range(100):
        f_random = [random.randint(0, p-1) for _ in range(n)]
        M_before = count_close_codewords(f_random, L, p, n, k, t)
        if M_before > 0: continue  # skip close words

        for alpha in range(p):  # check ALL alphas
            f_prime, L_prime = fri_fold(f_random, L, alpha, p, n)
            M_after = count_close_codewords(f_prime, L_prime, p, n//2, k, t)
            if M_after > 0:
                leaks += 1
                break
    print(f"  Leaks: {leaks}/100")

if __name__ == "__main__":
    main()
