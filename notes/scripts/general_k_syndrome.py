"""
List-decoding via syndrome search: find all low-weight error vectors
with prescribed syndromes, for RS on multiplicative subgroups.

For a word w: syndromes c_j = DFT(w)(j) for j = k, ..., n-1.
List size M = #{error vectors e : wt(e) <= delta*n, DFT(e)(j) = c_j for j >= k}

Approach: enumerate supports T of size w = delta*n.
For each T: the syndrome conditions are a linear system in |T| unknowns.
For MDS codes: the system has 0 or 1 solutions.
"""
import random
import math
from itertools import combinations

def find_prim_root(p, n):
    assert (p - 1) % n == 0
    g = 2
    while True:
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) == 1:
            # Check order is exactly n
            ok = True
            d = 2
            temp = n
            while d * d <= temp:
                while temp % d == 0:
                    if pow(w, n // d, p) == 1:
                        ok = False
                    temp //= d
                d += 1
            if temp > 1 and pow(w, n // temp, p) == 1:
                ok = False
            if ok:
                return w
        g += 1

def modinv(a, p):
    return pow(a, p - 2, p)

def solve_linear_system(matrix, rhs, p):
    """Solve matrix * x = rhs over F_p. Returns x or None if inconsistent."""
    m = len(matrix)  # equations
    n_vars = len(matrix[0]) if m > 0 else 0
    # Augmented matrix
    aug = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]

    pivot_col = 0
    pivot_rows = []
    for row in range(m):
        if pivot_col >= n_vars:
            break
        # Find pivot
        found = -1
        for r in range(row, m):
            if aug[r][pivot_col] % p != 0:
                found = r
                break
        if found == -1:
            pivot_col += 1
            continue
        aug[row], aug[found] = aug[found], aug[row]
        inv = modinv(aug[row][pivot_col], p)
        aug[row] = [(x * inv) % p for x in aug[row]]
        for r in range(m):
            if r != row and aug[r][pivot_col] % p != 0:
                factor = aug[r][pivot_col]
                aug[r] = [(aug[r][j] - factor * aug[row][j]) % p for j in range(n_vars + 1)]
        pivot_rows.append((row, pivot_col))
        pivot_col += 1

    # Check consistency
    for r in range(len(pivot_rows), m):
        if aug[r][n_vars] % p != 0:
            return None  # inconsistent

    # Extract solution (free variables = 0)
    x = [0] * n_vars
    for row, col in pivot_rows:
        x[col] = aug[row][n_vars] % p
    return x

def list_decode_syndrome(n, k, p, delta, w_vals, omega):
    """Find all codewords within distance delta*n from w on L = <omega>."""
    L = [pow(omega, i, p) for i in range(n)]
    t = int((1 - delta) * n)
    max_errors = n - t  # = delta*n (rounded)

    # Compute syndromes of w: c_j = sum_i w(omega^i) * omega^{-ij} for j = k,...,n-1
    omega_inv = modinv(omega, p)
    syndromes = []
    for j in range(k, n):
        s = 0
        for i in range(n):
            s = (s + w_vals[i] * pow(omega_inv, i * j, p)) % p
        syndromes.append(s)
    # syndromes[j-k] = DFT(w)(j)

    # Build parity check matrix: H[j-k][i] = omega^{-ij} for j=k,...,n-1, i=0,...,n-1
    # Actually: H * e^T = syndromes, where e = w - h is the error.
    # H[r][i] = omega^{-(r+k)*i}

    # For each support T of size <= max_errors:
    # Solve H_T * e_T = syndromes
    # H_T is (n-k) x |T| submatrix

    codewords_found = []

    for w_err in range(1, max_errors + 1):
        if math.comb(n, w_err) > 500000:
            # Too many supports; skip
            break
        for T in combinations(range(n), w_err):
            # Build H_T
            H_T = []
            for r in range(n - k):
                j = r + k
                row = [pow(omega_inv, j * i, p) for i in T]
                H_T.append(row)

            sol = solve_linear_system(H_T, syndromes, p)
            if sol is not None:
                # Check all entries nonzero (actual error, not just matching support)
                if all(s % p != 0 for s in sol):
                    # Found a valid error pattern
                    e = [0] * n
                    for idx, i in enumerate(T):
                        e[i] = sol[idx] % p
                    # The codeword: h = w - e
                    h_vals = [(w_vals[i] - e[i]) % p for i in range(n)]
                    codewords_found.append((w_err, T, h_vals))

    # Also check w itself (zero error)
    # DFT(w)(j) for j=0,...,k-1: if all syndromes for j>=k are 0, then w in RS_k
    if all(s % p == 0 for s in syndromes):
        codewords_found.append((0, (), w_vals))

    return codewords_found

def run_test(n, k, p, delta, num_words=10):
    omega = find_prim_root(p, n)
    rho = k / n
    delta_J = 1 - math.sqrt(rho)
    t = int((1 - delta) * n)
    max_errors = n - t

    regime = "ABOVE Johnson" if delta > delta_J else "below Johnson"
    print(f"\nn={n}, k={k}, p={p}, rho={rho:.3f}, delta={delta:.3f}, delta_J={delta_J:.3f}")
    print(f"t={t}, max_errors={max_errors}, regime={regime}")
    print(f"C(n, max_errors) = {math.comb(n, max_errors)}")

    if math.comb(n, max_errors) > 2000000:
        print("  Too many support combinations. Reducing max_errors or skipping.")
        # Try with fewer errors
        max_errors_try = max_errors
        while math.comb(n, max_errors_try) > 500000 and max_errors_try > 1:
            max_errors_try -= 1
        if max_errors_try < max_errors:
            print(f"  Testing only up to {max_errors_try} errors (of max {max_errors})")
            delta_eff = 1 - (n - max_errors_try) / n
            # Still run but with a note that we're only checking partial
        else:
            return

    max_M = 0
    for trial in range(num_words):
        w_vals = [random.randint(0, p - 1) for _ in range(n)]
        results = list_decode_syndrome(n, k, p, delta, w_vals, omega)
        M = len(results)
        max_M = max(max_M, M)
        if M > 0:
            errors = [r[0] for r in results]
            print(f"  word {trial}: M={M}, error weights={errors}")

    if max_M == 0:
        print(f"  All {num_words} words: M=0")
    else:
        print(f"  MAX M = {max_M}")

    return max_M

random.seed(42)

print("=" * 60)
print("LIST-DECODING VIA SYNDROME SEARCH")
print("=" * 60)

# Rate 1/2, above Johnson (delta_J ≈ 0.293)
print("\n--- Rate 1/2, delta=0.35 (above Johnson) ---")
run_test(n=8, k=4, p=17, delta=0.35, num_words=20)
run_test(n=12, k=6, p=13, delta=0.35, num_words=20)
run_test(n=16, k=8, p=17, delta=0.35, num_words=20)
run_test(n=20, k=10, p=41, delta=0.35, num_words=10)

# Rate 1/4, above Johnson (delta_J ≈ 0.5)
print("\n--- Rate 1/4, delta=0.55 (above Johnson) ---")
run_test(n=8, k=2, p=17, delta=0.55, num_words=20)
run_test(n=12, k=3, p=13, delta=0.55, num_words=20)
run_test(n=16, k=4, p=17, delta=0.55, num_words=20)

# Rate 1/2, closer to capacity
print("\n--- Rate 1/2, delta=0.45 (deep intermediate zone) ---")
run_test(n=8, k=4, p=17, delta=0.45, num_words=20)
run_test(n=12, k=6, p=13, delta=0.45, num_words=20)
run_test(n=16, k=8, p=17, delta=0.45, num_words=20)

# Power-of-2 domains
print("\n--- Power-of-2 domain, rate 1/2, delta=0.35 ---")
run_test(n=8, k=4, p=17, delta=0.35, num_words=20)
run_test(n=16, k=8, p=97, delta=0.35, num_words=10)
run_test(n=32, k=16, p=97, delta=0.35, num_words=5)
