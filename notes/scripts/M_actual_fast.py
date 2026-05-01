#!/usr/bin/env python3
"""
Fast M_actual search. Key optimizations:
1. Precompute σ(B) for all B
2. Check linear conditions as dot products
3. Only interpolate for the best center
"""

from itertools import combinations
import random
import math

random.seed(42)


def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def elem_sym(roots, p):
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e


def smallest_prime_cong_1(n, start=2):
    p = start
    while True:
        if p % n == 1:
            is_prime = p > 1
            for d in range(2, int(p ** 0.5) + 1):
                if p % d == 0:
                    is_prime = False
                    break
            if is_prime:
                return p
        p += 1


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def run_case(n, k, p, w):
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    conds = n - w - k
    n_B = math.comb(n, w)

    print(f"\n{'=' * 70}")
    print(f"RS[{n},{k}] over F_{p}, w={w}, conds/B={conds}, C({n},{w})={n_B}")
    print(f"Avg M_alg = {n_B / p ** conds:.2f}")

    # Precompute σ(B) for all error sets
    all_B = list(combinations(range(n), w))
    # Store σ as list of lists for fast access
    # σ[idx] = (σ_1, ..., σ_w) for all_B[idx]
    all_sv = []
    for B in all_B:
        roots = [L[i] for i in B]
        sigma = elem_sym(roots, p)
        all_sv.append([sigma[j] % p for j in range(1, w + 1)])

    # The conditions [P_B · c]_m = 0 for m = k+w,...,n-1 become:
    #
    # For each m: Σ_{i=0}^{w} (-1)^{w-i} σ_{w-i} c_{m-i} = 0  (σ_0 = 1)
    #
    # = (-1)^w c_{m-w} + Σ_{i=1}^{w} (-1)^{w-i} c_{m-i} σ_{w-i} = 0
    #
    # Written as: Σ_{j=1}^{w} A_{m,j} σ_j = b_m
    # where A_{m,j} = (-1)^{w-(w-j)} c_{m-(w-j)} = (-1)^j c_{m-w+j}
    # Wait, let me re-derive carefully.
    #
    # The condition: Σ_{i=0}^w p_B[i] c[m-i] = 0
    # where p_B[i] is coeff of x^i in P_B(x) = Σ (-1)^{w-i} σ_{w-i} x^i
    # So p_B[i] = (-1)^{w-i} σ_{w-i} for i=0,...,w
    #
    # Condition: Σ_i (-1)^{w-i} σ_{w-i} c[m-i] = 0
    #
    # Let j = w-i (so i = w-j):
    # Σ_{j=0}^w (-1)^j σ_j c[m-w+j] = 0
    # = σ_0 c[m-w] - σ_1 c[m-w+1] + ... + (-1)^w σ_w c[m]
    #
    # Separating σ_0 = 1:
    # c[m-w] + Σ_{j=1}^w (-1)^j σ_j c[m-w+j] = 0
    # Σ_{j=1}^w (-1)^j c[m-w+j] σ_j = -c[m-w]

    # We parameterize center by c_high = (c_k, c_{k+1}, ..., c_{n-1}).
    # c_0 = ... = c_{k-1} = 0 (WLOG: shifting by codeword doesn't change M).
    #
    # For condition at m (where m = k+w, ..., n-1):
    #   c[m-w+j] for j=0,...,w. These indices are m-w, m-w+1, ..., m.
    #   m-w ranges from k to n-1-w.
    #   So all indices m-w+j for j=0,...,w are in [k, n-1]. Good (all from c_high).

    def build_conditions(c_high):
        """Build the linear system A*σ = b from c_high."""
        rows = []  # list of (A_row, b_val)
        for m in range(k + w, n):
            A_row = [0] * w
            # RHS: -c[m-w] (from σ_0 = 1 term)
            c_mw = c_high[m - w - k] if 0 <= m - w - k < len(c_high) else 0
            b_val = (-c_mw) % p
            for j in range(1, w + 1):
                c_idx = m - w + j - k  # index into c_high
                c_val = c_high[c_idx] if 0 <= c_idx < len(c_high) else 0
                A_row[j - 1] = (pow(-1, j, p) * c_val) % p
            rows.append((A_row, b_val))
        return rows

    def count_compat(conditions):
        """Count how many σ values satisfy all conditions."""
        count = 0
        for sv in all_sv:
            ok = True
            for A_row, b_val in conditions:
                val = 0
                for j in range(w):
                    val += A_row[j] * sv[j]
                if val % p != b_val:
                    ok = False
                    break
            if ok:
                count += 1
        return count

    # Search for worst-case M_alg
    best_M_alg = 0
    best_c = None
    n_trials = 0

    # Strategy 1: sparse c_high (1-3 nonzero entries)
    nk = n - k
    for nz in range(1, min(4, nk + 1)):
        for positions in combinations(range(min(nk, 8)), min(nz, min(nk, 8))):
            max_vals = min((p - 1) ** nz, 2000)
            for vi in range(max_vals):
                vals = []
                temp = vi
                for _ in range(nz):
                    vals.append(temp % (p - 1) + 1)
                    temp //= (p - 1)
                c_high = [0] * nk
                for j2, pos in enumerate(positions):
                    c_high[pos] = vals[j2]
                conds_list = build_conditions(c_high)
                M_alg = count_compat(conds_list)
                if M_alg > best_M_alg:
                    best_M_alg = M_alg
                    best_c = c_high[:]
                n_trials += 1
        if n_trials > 30000:
            break

    # Strategy 2: random
    for _ in range(20000):
        c_high = [random.randint(0, p - 1) for _ in range(nk)]
        conds_list = build_conditions(c_high)
        M_alg = count_compat(conds_list)
        if M_alg > best_M_alg:
            best_M_alg = M_alg
            best_c = c_high[:]
        n_trials += 1

    print(f"Best M_alg = {best_M_alg} ({n_trials} trials)")

    # Now compute M_actual for the best center
    if best_c is not None and best_M_alg > 0:
        conds_list = build_conditions(best_c)

        # Build center evaluation
        c_coeffs = [0] * k + best_c
        c_vals = [sum(c_coeffs[j2] * pow(L[i], j2, p) for j2 in range(n)) % p
                  for i in range(n)]

        # For each compatible B, interpolate to find codeword
        codewords = set()
        dist_hist = {}

        for idx, (B, sv) in enumerate(zip(all_B, all_sv)):
            ok = True
            for A_row, b_val in conds_list:
                val = sum(A_row[j] * sv[j] for j in range(w)) % p
                if val != b_val:
                    ok = False
                    break
            if not ok:
                continue

            # Interpolate c on S = L\B
            S = [i for i in range(n) if i not in B]
            # Build and solve Vandermonde system
            m_sys = len(S)
            aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
                   for i in range(m_sys)]
            # Gaussian elimination
            pivot_cols = []
            for col in range(k):
                piv = -1
                for row in range(len(pivot_cols), m_sys):
                    if aug[row][col] % p != 0:
                        piv = row
                        break
                if piv == -1:
                    continue
                r2 = len(pivot_cols)
                aug[r2], aug[piv] = aug[piv], aug[r2]
                inv_p = pow(aug[r2][col], p - 2, p)
                for row in range(m_sys):
                    if row != r2 and aug[row][col] % p != 0:
                        f2 = aug[row][col] * inv_p % p
                        for j2 in range(k + 1):
                            aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
                pivot_cols.append(col)

            # Check consistency
            consistent = True
            for row in range(len(pivot_cols), m_sys):
                if aug[row][k] % p != 0:
                    consistent = False
                    break

            if not consistent:
                continue

            # Extract f coefficients
            a = [0] * k
            for idx2, col in enumerate(pivot_cols):
                a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p

            f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                          for i in range(n))
            d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
            codewords.add(f_vals)
            dist_hist[d] = dist_hist.get(d, 0) + 1

        M_actual = len(codewords)
        print(f"M_actual = {M_actual}, M_alg = {best_M_alg}")
        print(f"Distance histogram: {dict(sorted(dist_hist.items()))}")
        print(f"c_high = {best_c}")

        if best_M_alg > M_actual:
            # Overcounting detected. Try to find center where M_actual = M_alg.
            # These are centers at distance ≥ w from all codewords.
            print(f"\nOvercounting detected. Searching for M_actual=M_alg centers...")

            best_actual = M_actual
            best_c2 = best_c[:]
            best_info2 = (best_M_alg, dist_hist.copy())

            for _ in range(30000):
                c_high = [random.randint(0, p - 1) for _ in range(nk)]
                conds_list = build_conditions(c_high)
                M_alg = count_compat(conds_list)
                if M_alg <= 1:
                    continue

                # Quick check: build c_vals and check all compatible B's
                c_coeffs = [0] * k + c_high
                c_vals = [sum(c_coeffs[j2] * pow(L[i], j2, p) for j2 in range(n)) % p
                          for i in range(n)]

                cws = set()
                dists = {}
                overcount = False
                for idx, (B, sv) in enumerate(zip(all_B, all_sv)):
                    ok = True
                    for A_row, b_val in conds_list:
                        val = sum(A_row[j] * sv[j] for j in range(w)) % p
                        if val != b_val:
                            ok = False
                            break
                    if not ok:
                        continue

                    S = [i for i in range(n) if i not in B]
                    m_sys = len(S)
                    aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
                           for i in range(m_sys)]
                    pivot_cols = []
                    for col in range(k):
                        piv = -1
                        for row in range(len(pivot_cols), m_sys):
                            if aug[row][col] % p != 0:
                                piv = row
                                break
                        if piv == -1:
                            continue
                        r2 = len(pivot_cols)
                        aug[r2], aug[piv] = aug[piv], aug[r2]
                        inv_p = pow(aug[r2][col], p - 2, p)
                        for row in range(m_sys):
                            if row != r2 and aug[row][col] % p != 0:
                                f2 = aug[row][col] * inv_p % p
                                for j2 in range(k + 1):
                                    aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
                        pivot_cols.append(col)
                    consistent = True
                    for row in range(len(pivot_cols), m_sys):
                        if aug[row][k] % p != 0:
                            consistent = False
                            break
                    if not consistent:
                        continue
                    a = [0] * k
                    for idx2, col in enumerate(pivot_cols):
                        a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
                    f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                                  for i in range(n))
                    d = sum(1 for i in range(n) if c_vals[i] != f_vals[i])
                    if d < w:
                        overcount = True
                        break
                    cws.add(f_vals)
                    dists[d] = dists.get(d, 0) + 1

                if not overcount and len(cws) > best_actual:
                    best_actual = len(cws)
                    best_c2 = c_high[:]
                    best_info2 = (M_alg, dists.copy())

            print(f"Best M_actual (no overcount) = {best_actual}")
            print(f"M_alg = {best_info2[0]}, dists = {best_info2[1]}")
            print(f"c_high = {best_c2}")
        else:
            print("No overcounting — M_actual = M_alg")

    return best_M_alg


# ===== Known cases =====
print("=" * 70)
print("CORRECT M_actual WITH OVERCOUNTING DETECTION")
print("=" * 70)

for n, k, p, w in [(6, 3, 7, 2), (8, 4, 17, 3), (10, 5, 11, 3), (12, 6, 13, 4)]:
    run_case(n, k, p, w)

# New cases
for n in [14, 16]:
    k = n // 2
    w = johnson_radius(n, k)
    p = smallest_prime_cong_1(n, n + 1)
    run_case(n, k, p, w)
