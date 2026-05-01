"""
Deeper investigation of list-size bounds.

Key finding from first run: p=31, n=15, t=3 binomial gives M=15 > n/(t-1)=7.5.
This violates M ≤ n/(t-1)!

Need to understand:
1. Is the bound M ≤ n/(t-1) wrong even for binomials when t=3?
2. What is the correct bound?
3. How does general w compare to binomial w?
"""
from itertools import combinations

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p - 1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p - 1:
            return g
    return None

def find_subgroup(p, n):
    assert (p - 1) % n == 0
    g = find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    L = []
    x = 1
    for _ in range(n):
        L.append(x)
        x = (x * omega) % p
    return omega, L

def eval_poly(coeffs, x, p):
    result = 0
    xpow = 1
    for c in coeffs:
        result = (result + c * xpow) % p
        xpow = (xpow * x) % p
    return result

def compute_M_detailed(p, n, w_coeffs, t_threshold):
    """Return list of (h0, h1, agreement_set) tuples."""
    omega, L = find_subgroup(p, n)
    w_vals = [eval_poly(w_coeffs, L[i], p) for i in range(n)]

    results = []
    for h0 in range(p):
        for h1 in range(p):
            S = []
            for i in range(n):
                h_val = (h0 + h1 * L[i]) % p
                if w_vals[i] == h_val:
                    S.append(i)
            if len(S) >= t_threshold:
                results.append((h0, h1, S))
    return results

def systematic_scan():
    """Systematic scan: for each (p, n, t), compare binomial vs trinomial vs general."""

    print("=" * 90)
    print("SYSTEMATIC SCAN: M for various word types")
    print("=" * 90)

    configs = [
        # (p, n, t)
        (31, 5, 3),
        (31, 5, 4),
        (31, 6, 3),
        (31, 6, 4),
        (31, 10, 3),
        (31, 10, 4),
        (31, 10, 5),
        (31, 15, 3),
        (31, 15, 4),
        (31, 15, 5),
        (37, 6, 3),
        (37, 6, 4),
        (37, 9, 3),
        (37, 9, 4),
        (37, 12, 3),
        (37, 12, 4),
        (37, 18, 3),
        (37, 18, 4),
        (37, 18, 5),
        (41, 8, 3),
        (41, 8, 4),
        (41, 10, 3),
        (41, 10, 4),
        (41, 20, 3),
        (41, 20, 4),
        (41, 20, 5),
    ]

    for p, n, t in configs:
        if (p - 1) % n != 0:
            continue
        if t > n:
            continue

        bound_t1 = n / (t - 1)

        # For each config, try MAX over all λ for binomial,
        # and MAX over all (λ, μ) for trinomial
        # Binomial: x^t + λ*x^{t-1}
        max_M_binom = 0
        best_binom = None
        for lam in range(1, p):
            w = [0] * t + [1]  # x^t
            w[t-1] = lam       # + λ*x^{t-1}
            # Wait, indexing: w[j] = coeff of x^j
            w2 = [0] * (t + 1)
            w2[t] = 1
            w2[t-1] = lam
            results = compute_M_detailed(p, n, w2, t)
            M = len(results)
            if M > max_M_binom:
                max_M_binom = M
                best_binom = lam

        # Trinomial: x^t + λ*x^{t-1} + μ*x^{t-2}
        max_M_trinom = 0
        best_trinom = None
        if t >= 3:
            for lam in range(p):
                for mu in range(1, p):  # mu ≠ 0
                    w2 = [0] * (t + 1)
                    w2[t] = 1
                    w2[t-1] = lam
                    w2[t-2] = mu
                    results = compute_M_detailed(p, n, w2, t)
                    M = len(results)
                    if M > max_M_trinom:
                        max_M_trinom = M
                        best_trinom = (lam, mu)

        # Dense: x^t + all lower terms nonzero (sample a few random)
        import random
        random.seed(42)
        max_M_dense = 0
        for _ in range(min(50, p**(t-1))):
            w2 = [0] * (t + 1)
            w2[t] = 1
            for j in range(t):
                w2[j] = random.randint(0, p-1)
            results = compute_M_detailed(p, n, w2, t)
            M = len(results)
            if M > max_M_dense:
                max_M_dense = M

        marker = ""
        if max(max_M_binom, max_M_trinom, max_M_dense) > bound_t1 * 1.01:
            marker = " ***EXCEEDS***"

        print(f"\np={p}, n={n}, t={t}, bound n/(t-1)={bound_t1:.2f}{marker}")
        print(f"  Binomial  max M = {max_M_binom} (λ={best_binom})")
        print(f"  Trinomial max M = {max_M_trinom} (best={best_trinom})")
        print(f"  Dense(50) max M = {max_M_dense}")

def investigate_violation():
    """Look at the p=31, n=15, t=3 violation in detail."""
    print("\n" + "=" * 90)
    print("DETAILED: p=31, n=15, t=3 — binomial x^3 + λx^2")
    print("=" * 90)

    p, n = 31, 15
    omega, L = find_subgroup(p, n)
    print(f"ω = {omega}, L = {L}")

    for lam in range(1, p):
        w = [0, 0, lam, 1]  # x^3 + lam*x^2
        results = compute_M_detailed(p, n, w, 3)
        if results:
            print(f"\nλ={lam}: M={len(results)}")
            for h0, h1, S in results:
                # Check: is S\{j*} a coset?
                c = (-lam) % p  # e_1(S) = -λ
                # Which element of L equals c?
                j_star = None
                for i in range(n):
                    if L[i] == c:
                        j_star = i
                        break
                coset_info = ""
                if j_star is not None and j_star in S:
                    T = [i for i in S if i != j_star]
                    # Check if T is a coset of order-2 subgroup
                    # Order 2 subgroup of Z/15: {0, 15/gcd(2,15)} — wait, 2 doesn't divide 15
                    # t-1 = 2, need order-2 subgroup of Z/15Z... but 15 is odd, no order-2 subgroup
                    coset_info = f" j*={j_star}(ω^{j_star}={L[j_star]}), T={T}"
                    # T has 2 elements. For T to be a coset of order-2 subgroup,
                    # need n/(t-1) = 15/2 = 7.5, not integer!
                    # So the subgroup argument can't work directly.
                    coset_info += f" [n/(t-1)=7.5, NOT INTEGER]"
                elif j_star is not None:
                    coset_info = f" j*={j_star} NOT IN S={S}"
                else:
                    coset_info = f" c={c} NOT IN L"

                print(f"  (h0={h0},h1={h1}): S={S}{coset_info}")

if __name__ == "__main__":
    investigate_violation()
    systematic_scan()
