#!/usr/bin/env python3
"""
Direction A — Round 3: Center-constrained analysis

Key insight from Round 2: pairwise d_min clique has size p-1 (trivial),
but M_actual ≤ 7. The CENTER constraint is the real bottleneck.

Setup: center c (evaluation vector on L), Johnson radius w.
Each f_i satisfies d(f_i, c) ≤ w, i.e. f_i agrees with c on ≥ n-w positions.

Error: e_i = c - f_i, wt(e_i) ≤ w, supp(e_i) = B_i ⊂ [n]
Agreement: A_i = [n] \ B_i, |A_i| ≥ n-w

For difference f_i - f_j = e_j - e_i:
  supp(f_i - f_j) ⊂ B_i ∪ B_j
  [n] \ (B_i∪B_j) ⊂ zeros(f_i - f_j)

Key structural question:
  f_i - P_c vanishes on A_i. f_i has degree < k, P_c has degree < n.
  So f_i(x) = P_c(x) mod R_i(x) where R_i(x) = Π_{j∈A_i}(x-ω^j).
  Since deg f_i < k and deg R_i = n-w ≥ k (at Johnson), this means:
  f_i is the unique poly of degree < k that agrees with c on A_i.

  Given A_i, f_i is DETERMINED! So M_actual = #{A_i ⊂ [n]: |A_i|≥n-w,
  the unique degree-<k interpolant from A_i agrees with c on ALL of A_i}.

  Wait, that's circular. Let me re-think.

  Given any A ⊂ L with |A| ≥ k, there's a unique f of degree < k matching c on A.
  (Because RS_k is MDS, k points determine f.)
  Then wt(e) = #{j ∈ [n]: f(ω^j) ≠ c[j]} = n - |A| + #{j ∈ A: f(ω^j) ≠ c[j]}...

  No. If |A| > k, the system is overdetermined. Not every A gives a valid f.
  A valid list-decoding A must be such that c restricted to A lies in RS_k|_A.

  Concretely: take any k positions from A, interpolate f, then CHECK that f
  matches c on the remaining |A|-k positions. If yes → valid. If no → invalid.

  So: M_actual = #{A ⊂ [n]: |A| ≥ n-w, c|_A ∈ RS_k|_A}
    (distinct f's, so distinct A's that give distinct interpolants)

  Actually different A's can give the same f! If f matches c on A1 and A2,
  then f matches c on A1 ∪ A2. The MAXIMAL agreement set of f is unique.

  So M_actual = #{f ∈ RS_k: d(f,c) ≤ w}. Period.

Experiments:
A. For actual max-M lists, analyze the ERROR POLYNOMIAL structure
B. Key object: the INTERPOLATION POLYNOMIAL R_i(x) from c's perspective
C. How do the agreement sets A_i relate to each other?
D. What does the polynomial R_i(x) · f_i(x) look like mod x^n - 1?
E. The key equation: f_i(x) ≡ P_c(x) mod Π_{j∈A_i}(x-ω^j)
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
    """Multiply two polynomials mod p."""
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i + j] = (result[i + j] + ai * bj) % p
    return result

def poly_mod(a, b, p):
    """Compute a mod b (polynomial division remainder) over F_p."""
    a = list(a)
    while len(a) >= len(b):
        if a[-1] != 0:
            coeff = a[-1] * pow(b[-1], p - 2, p) % p
            for i in range(len(b)):
                a[len(a) - len(b) + i] = (a[len(a) - len(b) + i] - coeff * b[i]) % p
        a.pop()
    return a

def lagrange_interp(xs, ys, p):
    """Lagrange interpolation mod p. Returns coefficients [c0, c1, ...]."""
    n = len(xs)
    result = [0] * n
    for i in range(n):
        # Build basis polynomial: Π_{j≠i} (x - x_j) / (x_i - x_j)
        basis = [1]
        denom = 1
        for j in range(n):
            if j == i:
                continue
            # multiply by (x - x_j)
            new_basis = [0] * (len(basis) + 1)
            for k, c in enumerate(basis):
                new_basis[k + 1] = (new_basis[k + 1] + c) % p
                new_basis[k] = (new_basis[k] - c * xs[j]) % p
            basis = new_basis
            denom = denom * (xs[i] - xs[j]) % p

        denom_inv = pow(denom, p - 2, p)
        for k in range(len(basis)):
            result[k] = (result[k] + ys[i] * denom_inv * basis[k]) % p

    # Trim trailing zeros
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def analyze_max_M_list(n, p):
    """Find and deeply analyze the max-M list."""
    k = n // 2
    d_min = n - k + 1
    w = johnson_w(n, k)

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*60}")
    print(f"RS[{n},{k}] over F_{p}, d_min={d_min}, w={w}")
    print(f"omega={omega}")
    print(f"{'='*60}")

    # Generate all codewords
    if p**k > 500000:
        print(f"  p^k={p**k} too large")
        return

    codewords = []
    for coeffs_tuple in itertools.product(range(p), repeat=k):
        evals = tuple(poly_eval(list(coeffs_tuple), L[i], p) for i in range(n))
        codewords.append((list(coeffs_tuple), evals))

    # Find max-M center
    import random
    random.seed(42)

    best_M = 0
    best_center = None
    best_list = None

    # Try codeword centers
    for coeffs, evals in codewords[:500]:
        close = [(c, e) for c, e in codewords if sum(1 for i in range(n) if e[i] != evals[i]) <= w]
        if len(close) > best_M:
            best_M = len(close)
            best_center = evals
            best_list = close

    # Try random non-codeword centers
    for _ in range(500):
        center = tuple(random.randint(0, p-1) for _ in range(n))
        close = [(c, e) for c, e in codewords if sum(1 for i in range(n) if e[i] != center[i]) <= w]
        if len(close) > best_M:
            best_M = len(close)
            best_center = center
            best_list = close

    print(f"\n  Best M_actual = {best_M}")
    print(f"  Center c = {best_center}")

    if best_M < 2:
        return

    # P_c: polynomial of degree < n interpolating c on L
    # P_c(L[i]) = center[i] for all i
    P_c_coeffs = lagrange_interp(L, list(best_center), p)
    print(f"  P_c degree = {len(P_c_coeffs)-1}")
    print(f"  P_c high coeffs (deg k..n-1) = {P_c_coeffs[k:] if len(P_c_coeffs) > k else 'all < k'}")

    # Is center a codeword?
    is_codeword_center = len(P_c_coeffs) <= k or all(c == 0 for c in P_c_coeffs[k:])
    print(f"  Center is codeword: {is_codeword_center}")

    # For each f_i in the list:
    print(f"\n  List analysis:")
    print(f"  {'i':>3} {'dist':>4} {'B_i (error positions)':>30} {'|A_i∩A_j|':>12}")

    all_B = []
    all_A = []
    all_errors = []

    for idx, (coeffs, evals) in enumerate(best_list):
        dist = sum(1 for i in range(n) if evals[i] != best_center[i])
        B_i = tuple(i for i in range(n) if evals[i] != best_center[i])
        A_i = tuple(i for i in range(n) if evals[i] == best_center[i])
        error_vals = tuple((best_center[i] - evals[i]) % p for i in B_i)

        all_B.append(set(B_i))
        all_A.append(set(A_i))
        all_errors.append({B_i[j]: error_vals[j] for j in range(len(B_i))})

        print(f"  {idx:>3} {dist:>4} {str(B_i):>30} ", end="")
        # Print A_i intersections with first item
        if idx > 0:
            inter = len(all_A[0] & all_A[idx])
            print(f" |A_0∩A_{idx}|={inter}", end="")
        print()

    # Pairwise error set analysis
    print(f"\n  Pairwise B_i analysis:")
    print(f"  {'(i,j)':>6} {'|B_i∩B_j|':>10} {'|B_i∪B_j|':>10} {'d(fi,fj)':>8} {'B_i∩B_j':>15}")
    for i in range(len(best_list)):
        for j in range(i+1, len(best_list)):
            inter = all_B[i] & all_B[j]
            union = all_B[i] | all_B[j]
            dist = sum(1 for l in range(n) if best_list[i][1][l] != best_list[j][1][l])

            # Positions where they differ
            diff_pos = [l for l in range(n) if best_list[i][1][l] != best_list[j][1][l]]

            # Check: disagreement = symmetric diff of B_i, B_j + {j in B_i∩B_j: e_i[j]≠e_j[j]}
            sym_diff = all_B[i].symmetric_difference(all_B[j])
            both = all_B[i] & all_B[j]
            coincide = sum(1 for l in both if all_errors[i].get(l,0) == all_errors[j].get(l,0))

            print(f"  ({i},{j}) {len(inter):>10} {len(union):>10} {dist:>8} {str(sorted(inter)):>15}  coin={coincide}")

    # THE KEY STRUCTURAL ANALYSIS:
    # For each f_i: f_i(x) ≡ P_c(x) mod R_i(x)
    # where R_i(x) = Π_{j∈A_i}(x - L[j])
    #
    # Since f_i has degree < k and R_i has degree |A_i| = n - d_i ≥ n - w,
    # and n - w > k (at Johnson), this means:
    #
    # P_c(x) = R_i(x) · Q_i(x) + f_i(x) for some Q_i(x)
    #
    # where deg Q_i = deg P_c - deg R_i = (n-1) - (n-d_i) = d_i - 1
    #
    # So f_i(x) = P_c(x) - R_i(x) · Q_i(x)
    # and Q_i(x) has degree d_i - 1 ≤ w - 1

    print(f"\n  Quotient polynomial analysis:")
    print(f"  P_c(x) = R_i(x) · Q_i(x) + f_i(x)")

    for idx, (coeffs, evals) in enumerate(best_list):
        A_i = sorted(all_A[idx])
        B_i = sorted(all_B[idx])
        dist = len(B_i)

        # R_i(x) = Π_{j∈A_i}(x - L[j])
        R_i = poly_from_roots([L[j] for j in A_i], p)

        # f_i(x) coefficients (padded to length n)
        f_i = list(coeffs) + [0] * (n - k)

        # P_c(x) - f_i(x) should be divisible by R_i(x)
        diff = [(P_c_coeffs[j] if j < len(P_c_coeffs) else 0) - (f_i[j] if j < len(f_i) else 0)
                for j in range(max(len(P_c_coeffs), len(f_i)))]
        diff = [d % p for d in diff]

        # Compute Q_i = diff / R_i
        remainder = poly_mod(diff, R_i, p)
        is_divisible = all(r == 0 for r in remainder)

        # Q_i by polynomial division
        if is_divisible:
            # Do actual division to get quotient
            Q_i = [0] * (len(diff) - len(R_i) + 1)
            temp = list(diff)
            for j in range(len(Q_i) - 1, -1, -1):
                Q_i[j] = temp[j + len(R_i) - 1] * pow(R_i[-1], p - 2, p) % p
                for l in range(len(R_i)):
                    temp[j + l] = (temp[j + l] - Q_i[j] * R_i[l]) % p

            while len(Q_i) > 1 and Q_i[-1] == 0:
                Q_i.pop()

            print(f"  f_{idx}: d={dist}, deg Q={len(Q_i)-1}, Q={Q_i}")
        else:
            print(f"  f_{idx}: d={dist}, NOT DIVISIBLE (bug!), rem={remainder}")

    # KEY QUESTION: What constrains the Q_i polynomials?
    #
    # For two list members f_i, f_j:
    # f_i = P_c - R_i · Q_i
    # f_j = P_c - R_j · Q_j
    # f_i - f_j = R_j · Q_j - R_i · Q_i
    #
    # This must have degree < k and weight d_min.
    #
    # Also: R_i · Q_i ≡ R_j · Q_j mod (f_i - f_j)
    #       Both have the same high-degree part (that of P_c minus f_i or f_j)

    print(f"\n  Cross-product analysis: R_i · Q_i ≡ R_j · Q_j mod stuff")
    print(f"  f_i - f_j = R_j·Q_j - R_i·Q_i, must have deg < k, weight = d_min")
    print()

    for i in range(min(len(best_list), 4)):
        for j in range(i+1, min(len(best_list), 4)):
            A_i_list = sorted(all_A[i])
            A_j_list = sorted(all_A[j])

            R_i = poly_from_roots([L[l] for l in A_i_list], p)
            R_j = poly_from_roots([L[l] for l in A_j_list], p)

            f_i_coeffs = list(best_list[i][0]) + [0] * (n - k)
            f_j_coeffs = list(best_list[j][0]) + [0] * (n - k)

            diff_fi_fj = [(f_i_coeffs[l] - f_j_coeffs[l]) % p for l in range(n)]
            while len(diff_fi_fj) > 1 and diff_fi_fj[-1] == 0:
                diff_fi_fj.pop()

            print(f"  f_{i}-f_{j}: deg={len(diff_fi_fj)-1}, coeffs={diff_fi_fj}")

            # Common factor: A_i ∩ A_j gives shared roots
            common_A = all_A[i] & all_A[j]
            R_common = poly_from_roots([L[l] for l in sorted(common_A)], p)

            # f_i - f_j vanishes on A_i ∩ A_j (both agree with c there)
            # Plus possibly more positions
            zeros_of_diff = [l for l in range(n) if (best_list[i][1][l] - best_list[j][1][l]) % p == 0]
            extra_zeros = set(zeros_of_diff) - common_A

            print(f"    |A_i∩A_j| = {len(common_A)}, extra zeros = {sorted(extra_zeros)}")
            print(f"    total zeros = {len(zeros_of_diff)}, k-1 = {k-1}")

            # Factor out the zero polynomial
            zero_poly = poly_from_roots([L[l] for l in zeros_of_diff], p)
            remainder = poly_mod(diff_fi_fj, zero_poly, p)
            is_div = all(r == 0 for r in remainder)
            print(f"    f_i-f_j divisible by zero_poly: {is_div}")

            # The remaining factor has degree k-1 - len(zeros_of_diff) = ...
            if is_div and len(zeros_of_diff) > 0:
                # quotient = diff / zero_poly
                Q = [0] * (len(diff_fi_fj) - len(zero_poly) + 1)
                temp = list(diff_fi_fj)
                for l in range(len(Q) - 1, -1, -1):
                    Q[l] = temp[l + len(zero_poly) - 1] * pow(zero_poly[-1], p - 2, p) % p
                    for m in range(len(zero_poly)):
                        temp[l + m] = (temp[l + m] - Q[l] * zero_poly[m]) % p
                while len(Q) > 1 and Q[-1] == 0:
                    Q.pop()
                print(f"    remaining factor: deg={len(Q)-1}, coeffs={Q}")
            print()


if __name__ == "__main__":
    for n, p in [(8, 17), (10, 11), (6, 7)]:
        analyze_max_M_list(n, p)
