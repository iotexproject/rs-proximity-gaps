"""
Test list-decoding size M for RS[n, k] on multiplicative subgroups
at distances ABOVE the Johnson bound, for GENERAL k.

Key question: is M = O(1) on multiplicative subgroups for all k?

Method: for each word w, count the number of codewords h in RS_k
with agreement |{x in L : w(x) = h(x)}| >= t = (1-delta)*n.

For small n: brute force over all codewords (p^k of them).
For larger n: use random sampling of codewords and/or algebraic shortcuts.
"""
import random
import math
from itertools import product as iter_product

def find_prim_root(p, n):
    """Find element of order n in F_p."""
    assert (p - 1) % n == 0
    g = 2
    while True:
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) == 1 and all(pow(w, n // q, p) != 1 for q in prime_factors(n)):
            return w
        g += 1

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def eval_poly(coeffs, x, p):
    """Evaluate polynomial with given coefficients at x mod p."""
    val = 0
    xi = 1
    for c in coeffs:
        val = (val + c * xi) % p
        xi = xi * x % p
    return val

def list_decode_bruteforce(w_vals, L, k, p, t):
    """Count codewords within distance n-t from w on L.
    w_vals: values of w on L (length n).
    Returns: list size M.
    """
    n = len(L)
    M = 0
    best_agreement = 0

    # For very small k and p: enumerate all codewords
    if k <= 3 and p <= 50:
        for coeffs in iter_product(range(p), repeat=k):
            agreement = sum(1 for i in range(n)
                          if eval_poly(coeffs, L[i], p) == w_vals[i])
            if agreement >= t:
                M += 1
            best_agreement = max(best_agreement, agreement)
        return M, best_agreement

    # For larger k: random sampling to estimate M
    # (we can't enumerate p^k codewords)
    # Instead: use DFT projection to find the nearest codeword
    # and check if there are multiple within distance delta

    # DFT approach: compute syndrome of w, then search for
    # error patterns of weight <= delta*n with matching syndromes

    # For moderate n and k: use the fact that list-decoding
    # at distance delta is equivalent to finding low-weight
    # vectors in a coset of the RS code.

    # Simplified approach for testing: random codewords
    num_samples = min(p**k, 100000)
    for _ in range(num_samples):
        coeffs = [random.randint(0, p-1) for _ in range(k)]
        agreement = sum(1 for i in range(n)
                       if eval_poly(coeffs, L[i], p) == w_vals[i])
        if agreement >= t:
            M += 1
        best_agreement = max(best_agreement, agreement)

    if num_samples < p**k:
        # Estimate: M_true ≈ M_found * p^k / num_samples
        return M, best_agreement  # report found count (lower bound)

    return M, best_agreement

def test_list_size(n, k, p, delta, num_words=10):
    """Test list-decoding size for multiple random words."""
    omega = find_prim_root(p, n)
    L = [pow(omega, i, p) for i in range(n)]

    rho = k / n
    delta_J = 1 - math.sqrt(rho)
    t = int((1 - delta) * n)

    print(f"\nn={n}, k={k}, p={p}, rho={rho:.3f}, delta={delta:.3f}")
    print(f"delta_J={delta_J:.3f}, t={t}, regime={'ABOVE Johnson' if delta > delta_J else 'below Johnson'}")

    if p**k > 10**7 and k > 3:
        print(f"  Skipping: p^k = {p}^{k} too large for brute force. Using random sampling.")
        method = "sample"
    else:
        method = "brute"

    max_M = 0
    max_agree = 0

    for trial in range(num_words):
        # Random word w
        w_vals = [random.randint(0, p-1) for _ in range(n)]

        if method == "brute":
            M, best_agree = list_decode_bruteforce(w_vals, L, k, p, t)
        else:
            M, best_agree = list_decode_bruteforce(w_vals, L, k, p, t)

        max_M = max(max_M, M)
        max_agree = max(max_agree, best_agree)

        if M > 0:
            print(f"  word {trial}: M={M}, best_agree={best_agree}/{n}")

    if max_M == 0:
        print(f"  All {num_words} words: M=0 (best agreement: {max_agree}/{n}, need {t})")
    else:
        print(f"  Max M={max_M} over {num_words} words")

    return max_M

random.seed(42)

print("="*60)
print("LIST SIZE TEST: General k on Multiplicative Subgroups")
print("="*60)

# Test 1: k=2 (known: M = O(1))
test_list_size(n=16, k=2, p=17, delta=0.35, num_words=20)

# Test 2: k=3
test_list_size(n=16, k=3, p=17, delta=0.35, num_words=20)

# Test 3: k=4
test_list_size(n=16, k=4, p=17, delta=0.35, num_words=20)

# Test 4: k=8 (rate 1/2 on n=16)
test_list_size(n=16, k=8, p=17, delta=0.35, num_words=20)

# Test 5: Larger n with k=2,3,4
test_list_size(n=32, k=2, p=97, delta=0.35, num_words=10)
test_list_size(n=32, k=3, p=97, delta=0.35, num_words=10)
test_list_size(n=32, k=4, p=97, delta=0.40, num_words=10)

# Test 6: n=24, k=12 (rate 1/2), above Johnson
# delta_J(1/2) = 1 - sqrt(1/2) ≈ 0.293
test_list_size(n=24, k=12, p=73, delta=0.35, num_words=10)

# Test 7: n=16, k=8 with larger field
test_list_size(n=16, k=8, p=97, delta=0.35, num_words=10)

print("\n" + "="*60)
print("CRITICAL TEST: rate 1/2, above Johnson, varying n")
print("="*60)

# For rate 1/2: delta_J ≈ 0.293. Test at delta = 0.35.
for n in [8, 12, 16, 20, 24]:
    k = n // 2
    # Find prime p with (p-1) divisible by n
    p = n + 1
    while True:
        if all(p % i != 0 for i in range(2, int(p**0.5)+1)) and (p-1) % n == 0:
            break
        p += n
    if p < 200:  # only test if p is reasonable
        test_list_size(n=n, k=k, p=p, delta=0.35, num_words=10)
    else:
        print(f"\nn={n}, k={k}: smallest suitable prime p={p} (skipping if too large)")
        if p**k <= 10**7:
            test_list_size(n=n, k=k, p=p, delta=0.35, num_words=5)
