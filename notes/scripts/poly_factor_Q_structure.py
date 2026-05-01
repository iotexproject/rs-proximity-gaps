#!/usr/bin/env python3
"""
Direction A — Round 4: Q-polynomial structure analysis

KEY FINDING FROM ROUND 3:
  P_c(x) = R_i(x) · Q_i(x) + f_i(x), deg f_i < k
  where R_i = Π_{j∈A_i}(x-ω^j), Q_i has degree w-1.

Q_i determines f_i, and Q_i's coefficients are determined by B_i.
Q_i all share the same LEADING coefficient (= leading coeff of P_c / 1).

Question: What algebraic variety do the Q_i coefficients live on?

Also: Key identity: f_i - f_j = R_j·Q_j - R_i·Q_i, deg < k.
Since R_i = (x^n-1)/S_i, this becomes:
(x^n-1)(Q_j/S_j - Q_i/S_i) = f_i - f_j (deg < k)

So (Q_j·S_i - Q_i·S_j) / (S_i·S_j) · (x^n-1) has degree < k.
Equivalently: Q_j·S_i - Q_i·S_j ≡ 0 mod (x^n-1)/(S_i·S_j/gcd) up to low degree terms.

Experiments:
A. Parametric structure of Q_i coefficients for multiple (n,p)
B. Do Q_i coefficients lie on an algebraic curve?
C. Relationship between σ(B_i) and Q_i coefficients
D. The S_i · Q_i product structure (mod x^n - 1)
E. Exploring n=12 with larger list
"""

import itertools
from collections import defaultdict
import math

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = val * g % p
        if len(seen) == p - 1:
            return g

def find_omega(g, p, n):
    return pow(g, (p - 1) // n, p)

def poly_eval(coeffs, x, p):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = xpow * x % p
    return val

def johnson_w(n, k):
    return int(math.floor(n - math.sqrt(n * (k - 1))))

def poly_from_roots(roots, p):
    poly = [1]
    for r in roots:
        new_poly = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new_poly[i + 1] = (new_poly[i + 1] + c) % p
            new_poly[i] = (new_poly[i] - c * r) % p
        poly = new_poly
    return poly

def poly_mult(a, b, p):
    if not a or not b:
        return [0]
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] = (result[i + j] + ai * bj) % p
    return result

def poly_mod(a, b, p):
    a = list(a)
    while len(a) >= len(b):
        if a[-1] != 0:
            coeff = a[-1] * pow(b[-1], p - 2, p) % p
            for i in range(len(b)):
                a[len(a) - len(b) + i] = (a[len(a) - len(b) + i] - coeff * b[i]) % p
        a.pop()
    while a and a[-1] == 0:
        a.pop()
    return a if a else [0]

def lagrange_interp(xs, ys, p):
    n = len(xs)
    result = [0] * n
    for i in range(n):
        basis = [1]
        denom = 1
        for j in range(n):
            if j == i:
                continue
            new_basis = [0] * (len(basis) + 1)
            for k_idx, c in enumerate(basis):
                new_basis[k_idx + 1] = (new_basis[k_idx + 1] + c) % p
                new_basis[k_idx] = (new_basis[k_idx] - c * xs[j]) % p
            basis = new_basis
            denom = denom * (xs[i] - xs[j]) % p
        denom_inv = pow(denom, p - 2, p)
        for k_idx in range(len(basis)):
            result[k_idx] = (result[k_idx] + ys[i] * denom_inv * basis[k_idx]) % p
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result

def poly_div(a, b, p):
    """Return (quotient, remainder) of a / b over F_p."""
    a = list(a)
    q = []
    while len(a) >= len(b):
        if a[-1] == 0:
            q.append(0)
            a.pop()
            continue
        coeff = a[-1] * pow(b[-1], p - 2, p) % p
        q.append(coeff)
        for i in range(len(b)):
            a[len(a) - len(b) + i] = (a[len(a) - len(b) + i] - coeff * b[i]) % p
        a.pop()
    q.reverse()
    while a and a[-1] == 0:
        a.pop()
    return q if q else [0], a if a else [0]

def elem_sym(values, p):
    """Elementary symmetric functions of values over F_p."""
    w = len(values)
    sigma = [0] * (w + 1)
    sigma[0] = 1
    for v in values:
        for j in range(w, 0, -1):
            sigma[j] = (sigma[j] + sigma[j-1] * v) % p
    return sigma[1:]  # sigma_1, ..., sigma_w


def full_analysis(n, p):
    """Complete Q-polynomial structure analysis."""
    k = n // 2
    d_min = n - k + 1
    w = johnson_w(n, k)

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] over F_{p}, d_min={d_min}, w={w}, omega={omega}")
    print(f"{'='*70}")

    # Generate all codewords
    if p**k > 500000:
        print(f"  p^k={p**k} too large, using brute force search on B_i")
        return brute_force_analysis(n, p, k, d_min, w, L, omega)

    codewords = []
    for coeffs_tuple in itertools.product(range(p), repeat=k):
        evals = tuple(poly_eval(list(coeffs_tuple), L[i], p) for i in range(n))
        codewords.append((list(coeffs_tuple), evals))

    # Find ALL centers giving maximum M
    import random
    random.seed(42)

    max_M = 0
    max_centers = []

    # Try codeword centers + random
    test_centers = [e for _, e in codewords[:1000]]
    for _ in range(2000):
        test_centers.append(tuple(random.randint(0, p-1) for _ in range(n)))

    for center in test_centers:
        close = [(c, e) for c, e in codewords if sum(1 for i in range(n) if e[i] != center[i]) <= w]
        M = len(close)
        if M > max_M:
            max_M = M
            max_centers = [(center, close)]
        elif M == max_M:
            max_centers.append((center, close))

    print(f"  Max M_actual = {max_M}, found {len(max_centers)} centers with this M")

    # Analyze the BEST center in detail
    center, best_list = max_centers[0]

    # P_c interpolation
    P_c = lagrange_interp(L, list(center), p)
    while len(P_c) < n:
        P_c.append(0)

    print(f"  Center: {center}")
    print(f"  P_c high coeffs: {P_c[k:]}")

    # For each list member, compute B_i, Q_i, σ(B_i)
    print(f"\n  List member analysis:")
    print(f"  {'i':>3} {'B_i':>20} {'Q_i':>25} {'σ(B_i)':>30}")

    Q_list = []
    B_list = []
    sigma_list = []
    f_list = []

    for idx, (coeffs, evals) in enumerate(best_list):
        B_i = [i for i in range(n) if evals[i] != center[i]]
        A_i = [i for i in range(n) if evals[i] == center[i]]
        B_list.append(B_i)
        f_list.append(coeffs)

        # R_i = Π_{j∈A_i}(x - L[j])
        R_i = poly_from_roots([L[j] for j in A_i], p)

        # f_i padded
        f_i_full = list(coeffs) + [0] * (n - k)

        # P_c - f_i
        diff = [(P_c[j] - f_i_full[j]) % p for j in range(n)]

        # Q_i = diff / R_i
        Q_i, rem = poly_div(diff, R_i, p)
        Q_list.append(Q_i)

        # σ(B_i) = elementary symmetric functions of {L[j]: j ∈ B_i}
        B_vals = [L[j] for j in B_i]
        sigma_B = elem_sym(B_vals, p)
        sigma_list.append(sigma_B)

        print(f"  {idx:>3} {str(B_i):>20} {str(Q_i):>25} {str(sigma_B[:3]):>30}")

    # Analyze Q_i coefficient patterns
    print(f"\n  Q_i coefficient analysis:")
    if w >= 2:
        print(f"  Degree w-1 = {w-1}")
        print(f"  Leading coeffs: {[Q[w-1] if len(Q) > w-1 else Q[-1] for Q in Q_list]}")

        if w >= 3:
            print(f"  Second coeffs:  {[Q[w-2] if len(Q) > w-2 else '?' for Q in Q_list]}")

        # Check if lower coefficients satisfy polynomial relations
        if w == 3 and len(Q_list) >= 3:
            # Q_i = a*x^2 + b_i*x + c_i
            # Check: do (b_i, c_i) lie on a curve?
            bcs = [(Q[1] if len(Q) > 1 else 0, Q[0]) for Q in Q_list]
            print(f"\n  (b_i, c_i) pairs: {bcs}")

            # Try to find polynomial relation F(b,c) = 0
            # Degree 1: Ab + Bc + C = 0 → line
            # Check if collinear
            if len(bcs) >= 3:
                # Check all triples for collinearity
                all_collinear = True
                for i in range(len(bcs)):
                    for j in range(i+1, len(bcs)):
                        for l in range(j+1, len(bcs)):
                            det = ((bcs[j][0]-bcs[i][0])*(bcs[l][1]-bcs[i][1]) -
                                   (bcs[l][0]-bcs[i][0])*(bcs[j][1]-bcs[i][1])) % p
                            if det != 0:
                                all_collinear = False
                                break
                        if not all_collinear:
                            break
                    if not all_collinear:
                        break
                print(f"  All collinear (on a line): {all_collinear}")

                if not all_collinear:
                    # Try degree 2: check if on a conic
                    # Ab² + Bbc + Cc² + Db + Ec + F = 0
                    # Need 6 points to determine, or check with fewer
                    print(f"  Checking conic...")

        elif w == 2 and len(Q_list) >= 2:
            # Q_i = a + b_i*x → just b_i varies (constant a shared)
            # Wait, Q_i = [c_i, a] where a is shared leading coeff
            consts = [Q[0] for Q in Q_list]
            print(f"\n  Constant coefficients: {consts}")

    # Relationship between σ(B_i) and Q_i
    print(f"\n  σ(B_i) → Q_i mapping:")
    for idx in range(len(B_list)):
        # Q_i should be a function of σ(B_i)
        # Specifically, Q_i coefficients are rational functions of σ_1,...,σ_w
        print(f"    σ={sigma_list[idx]} → Q={Q_list[idx]}")

    # KEY ANALYSIS: S_i · Q_i product (mod x^n - 1)
    print(f"\n  S_i · Q_i product analysis:")
    xn_minus_1 = [(-1 if i == 0 else 0) if i < n else (1 if i == n else 0) for i in range(n + 1)]
    # Actually: x^n - 1 = -1 + 0*x + ... + 0*x^{n-1} + 1*x^n
    xn_minus_1 = [0] * (n + 1)
    xn_minus_1[0] = p - 1  # -1
    xn_minus_1[n] = 1

    for idx in range(min(len(B_list), 5)):
        S_i = poly_from_roots([L[j] for j in B_list[idx]], p)
        SQ = poly_mult(S_i, Q_list[idx], p)
        SQ_mod = poly_mod(SQ, xn_minus_1, p)
        print(f"    S_{idx}·Q_{idx} mod(x^n-1) = {SQ_mod}")

        # Also compute S_i · Q_i WITHOUT mod
        print(f"    S_{idx}·Q_{idx} (raw, deg {len(SQ)-1}) high={SQ[k:]}")

    # KEY: f_i - f_j = R_j·Q_j - R_i·Q_i
    # = (x^n-1)/S_j · Q_j - (x^n-1)/S_i · Q_i
    #
    # Multiply both sides by S_i·S_j / (x^n-1):
    # (f_i - f_j) · S_i · S_j / (x^n-1) = Q_j · S_i - Q_i · S_j
    #
    # LHS: (f_i-f_j) is degree < k, S_i·S_j is degree 2w (or less with common factors)
    # Product is degree < k + 2w ≤ k + 2w.
    # Divided by x^n-1 (degree n): only makes sense if S_i·S_j | something...
    #
    # Actually: Q_j · S_i - Q_i · S_j has degree ≤ 2w-1 (leading terms cancel).
    # And this equals R_j·Q_j·S_i - R_i·Q_i·S_j... no wait.
    #
    # f_i - f_j = R_j·Q_j - R_i·Q_i
    # R_j = (x^n-1)/S_j.
    # Multiply by S_i·S_j:
    # (f_i-f_j)·S_i·S_j = (x^n-1)·Q_j·S_i - (x^n-1)·Q_i·S_j = (x^n-1)(Q_j·S_i - Q_i·S_j)
    #
    # So: (f_i-f_j)·S_i·S_j = (x^n-1)·(Q_j·S_i - Q_i·S_j)
    #
    # This is an EXACT identity! Let's verify and analyze.

    print(f"\n  Key identity: (f_i-f_j)·S_i·S_j = (x^n-1)·(Q_j·S_i - Q_i·S_j)")
    for i_idx in range(min(len(B_list), 3)):
        for j_idx in range(i_idx+1, min(len(B_list), 4)):
            diff_fij = [(f_list[i_idx][c_idx] - f_list[j_idx][c_idx]) % p for c_idx in range(k)]
            while diff_fij and diff_fij[-1] == 0:
                diff_fij.pop()

            S_i = poly_from_roots([L[j] for j in B_list[i_idx]], p)
            S_j = poly_from_roots([L[j] for j in B_list[j_idx]], p)

            # LHS: (f_i-f_j) · S_i · S_j
            lhs = poly_mult(poly_mult(diff_fij, S_i, p), S_j, p)

            # RHS: (x^n-1) · (Q_j·S_i - Q_i·S_j)
            QjSi = poly_mult(Q_list[j_idx], S_i, p)
            QiSj = poly_mult(Q_list[i_idx], S_j, p)
            maxlen = max(len(QjSi), len(QiSj))
            N_poly = [(QjSi[l] if l < len(QjSi) else 0) - (QiSj[l] if l < len(QiSj) else 0)
                       for l in range(maxlen)]
            N_poly = [c % p for c in N_poly]
            while N_poly and N_poly[-1] == 0:
                N_poly.pop()

            rhs = poly_mult(xn_minus_1, N_poly, p)

            # Compare
            max_deg = max(len(lhs), len(rhs))
            match = all((lhs[l] if l < len(lhs) else 0) == (rhs[l] if l < len(rhs) else 0)
                       for l in range(max_deg))

            print(f"    ({i_idx},{j_idx}): match={match}")
            print(f"      N = Q_{j_idx}·S_{i_idx} - Q_{i_idx}·S_{j_idx}, deg N = {len(N_poly)-1 if N_poly else -1}")
            print(f"      N coeffs = {N_poly}")

            # N has degree ≤ 2w-2 (leading terms cancel since Q_i, Q_j share leading coeff)
            # N = Q_j · S_i - Q_i · S_j
            # N(ω^l) for l ∈ B_i: Q_j(ω^l)·S_i(ω^l) - Q_i(ω^l)·0 = Q_j(ω^l)·S_i(ω^l)
            # N(ω^l) for l ∈ B_j: Q_j(ω^l)·0 - Q_i(ω^l)·S_j(ω^l) = -Q_i(ω^l)·S_j(ω^l)
            # N(ω^l) for l ∉ B_i∪B_j: Q_j(ω^l)·S_i(ω^l) - Q_i(ω^l)·S_j(ω^l)

    # THE CRITICAL CONSTRAINT:
    # (f_i - f_j) · S_i · S_j = (x^n - 1) · N_{ij}
    # where N_{ij} = Q_j·S_i - Q_i·S_j has degree ≤ 2w-2
    #
    # Since x^n - 1 = Π_l (x - ω^l), and S_i·S_j = Π_{l∈B_i∪B_j}(x-ω^l) · possibly common factors:
    #
    # x^n - 1 = R_common · S_i · S_j / gcd(S_i, S_j)  ... no, x^n-1 = Π all roots
    #
    # For l ∉ B_i ∪ B_j: (f_i-f_j)(ω^l) = 0 (both agree with c there)
    # Wait, not necessarily. f_i and f_j agree with c on A_i and A_j respectively.
    # They agree with EACH OTHER on A_i ∩ A_j = complement of B_i ∪ B_j.
    # So (f_i-f_j)(ω^l) = 0 for l ∉ B_i ∪ B_j.
    #
    # Also (f_i-f_j)(ω^l) = 0 for some l ∈ B_i ∩ B_j if e_i[l] = e_j[l].
    # And (f_i-f_j)(ω^l) ≠ 0 for l ∈ B_i △ B_j (symmetric difference).

    return Q_list, B_list, sigma_list, f_list, center, P_c, L


def brute_force_analysis(n, p, k, d_min, w, L, omega):
    """For larger cases, search for valid B by brute force compatibility check."""
    print(f"  Brute force search for compatible B sets...")

    # The compatibility conditions from P_c's high coefficients
    # For a random non-codeword center:
    import random
    random.seed(42)
    center = [random.randint(0, p-1) for _ in range(n)]

    P_c = lagrange_interp(L, center, p)
    while len(P_c) < n:
        P_c.append(0)

    high_coeffs = P_c[k:]
    print(f"  P_c high coeffs: {high_coeffs}")

    # For each w-subset B of [n], check if P_c mod R_B has degree < k
    # Equivalent: does there exist f ∈ RS_k with d(f, c) ≤ w?
    # Where B = error positions and A = [n]\B = agreement positions

    valid_B = []
    valid_Q = []

    total = math.comb(n, w)
    print(f"  Total C({n},{w}) = {total} subsets to check")

    count = 0
    for B in itertools.combinations(range(n), w):
        count += 1
        A = [i for i in range(n) if i not in B]

        # Interpolate f on A: f(L[j]) = center[j] for j ∈ A
        # If |A| = n-w ≥ k, this is overdetermined
        # Use first k positions of A to interpolate, then check rest
        if len(A) < k:
            continue

        xs = [L[j] for j in A[:k]]
        ys = [center[j] for j in A[:k]]
        f_coeffs = lagrange_interp(xs, ys, p)
        while len(f_coeffs) < k:
            f_coeffs.append(0)

        # Check remaining A positions
        valid = True
        for j in A[k:]:
            if poly_eval(f_coeffs, L[j], p) != center[j]:
                valid = False
                break

        if valid:
            valid_B.append(list(B))
            # Compute Q
            R = poly_from_roots([L[j] for j in A], p)
            f_full = list(f_coeffs) + [0] * (n - k)
            diff = [(P_c[j] - f_full[j]) % p for j in range(n)]
            Q, _ = poly_div(diff, R, p)
            valid_Q.append(Q)

    print(f"  Valid B sets: {len(valid_B)}")

    if valid_B:
        # Check for distinct f's (overcounting)
        f_set = set()
        unique_f = []
        for B in valid_B:
            A = [i for i in range(n) if i not in B]
            xs = [L[j] for j in A[:k]]
            ys = [center[j] for j in A[:k]]
            f_coeffs = lagrange_interp(xs, ys, p)
            while len(f_coeffs) < k:
                f_coeffs.append(0)
            f_key = tuple(f_coeffs)
            if f_key not in f_set:
                f_set.add(f_key)
                unique_f.append(f_coeffs)

        M_actual = len(unique_f)
        print(f"  M_actual (distinct codewords) = {M_actual}")

        # Show Q polynomials
        for idx in range(min(len(valid_B), 10)):
            B = valid_B[idx]
            B_vals = [L[j] for j in B]
            sigma_B = elem_sym(B_vals, p)
            print(f"    B={B}, Q={valid_Q[idx]}, σ(B)={sigma_B[:3]}")

        return valid_Q, valid_B

    return None, None


if __name__ == "__main__":
    # Detailed analysis for small cases
    for n, p in [(6, 7), (8, 17), (10, 11), (10, 31), (12, 13)]:
        full_analysis(n, p)
