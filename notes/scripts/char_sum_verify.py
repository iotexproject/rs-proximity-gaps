#!/usr/bin/env python3
"""
Character sum verification for M computation.

Key formula:
  M = (1/p^c) * Σ_{t ∈ F_p^c} Σ_B ψ(t · D(σ(B)))

where:
  D_m(σ) = Σ_{j=0}^w (-1)^j σ_j c_{m-w+j}, m = k+w,...,n-1
  c = n-k-w conditions
  ψ(x) = exp(2πi x/p)

Verifies: (1) formula reproduces known M values
         (2) measures |S(α)| cancellation empirically
         (3) identifies structure in the character sum
"""

import math
import cmath
from itertools import combinations, product

PI2 = 2 * math.pi


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
    """Elementary symmetric polynomials of roots mod p."""
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j - 1] * r) % p
    return e  # e[0]=1, e[1]=σ_1, ..., e[w]=σ_w


def johnson_radius(n, k):
    return math.ceil((1 - math.sqrt(k / n)) * n)


def psi(x, p):
    """Additive character ψ(x) = exp(2πi x/p)."""
    return cmath.exp(1j * PI2 * (x % p) / p)


def direct_M(n, k, p, w, c_high):
    """Compute M by direct enumeration (ground truth)."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w

    # Full center polynomial coefficients
    c_coeffs = [0] * k + list(c_high)
    c_vals = [sum(c_coeffs[j] * pow(L[i], j, p) for j in range(n)) % p
              for i in range(n)]

    codewords = set()
    for B in combinations(range(n), w):
        # Check linear conditions: [P_B · c]_m = 0 for m = k+w,...,n-1
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)  # σ_0=1, σ_1,...,σ_w

        ok = True
        for m_off in range(conds):
            # D_{k+w+m_off} = Σ_j (-1)^j σ_j c_{k+m_off+j}
            val = 0
            for j in range(w + 1):
                c_idx = m_off + j  # index into c_high
                if c_idx < nk:
                    val += pow(-1, j, p) * es[j] * c_high[c_idx]
            if val % p != 0:
                ok = False
                break
        if not ok:
            continue

        # Interpolate to find codeword
        S = [i for i in range(n) if i not in B]
        aug = [[pow(L[S[i]], j, p) for j in range(k)] + [c_vals[S[i]]]
               for i in range(len(S))]
        pivot_cols = []
        for col in range(k):
            piv = -1
            for row in range(len(pivot_cols), len(S)):
                if aug[row][col] % p != 0:
                    piv = row
                    break
            if piv == -1:
                continue
            r2 = len(pivot_cols)
            aug[r2], aug[piv] = aug[piv], aug[r2]
            inv_p = pow(aug[r2][col], p - 2, p)
            for row in range(len(S)):
                if row != r2 and aug[row][col] % p != 0:
                    f2 = aug[row][col] * inv_p % p
                    for j2 in range(k + 1):
                        aug[row][j2] = (aug[row][j2] - f2 * aug[r2][j2]) % p
            pivot_cols.append(col)
        a = [0] * k
        for idx2, col in enumerate(pivot_cols):
            a[col] = aug[idx2][k] * pow(aug[idx2][col], p - 2, p) % p
        f_vals = tuple(sum(a[j] * pow(L[i], j, p) for j in range(k)) % p
                       for i in range(n))
        codewords.add(f_vals)

    return len(codewords)


def char_sum_M(n, k, p, w, c_high):
    """
    Compute M via character sum formula and return diagnostics.

    M = (1/p^c) Σ_{t ∈ F_p^c} Σ_B ψ(Σ_m t_m D_m(σ(B)))

    Returns: (M_char, S_stats) where S_stats = {max|S|, avg|S|, histogram}
    """
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    nk = n - k
    conds = n - k - w
    n_B = math.comb(n, w)

    # Precompute σ for all B's
    all_B = list(combinations(range(n), w))
    all_sigma = []  # list of (σ_1,...,σ_w) for each B
    for B in all_B:
        roots = [L[i] for i in B]
        es = elem_sym(roots, p)
        all_sigma.append(es)  # es[0]=1, es[1]=σ_1, ..., es[w]=σ_w

    # Precompute D_m(σ(B)) for each B and each condition m_off
    # D_{k+w+m_off} = Σ_j (-1)^j σ_j c_{k+m_off+j}
    # = Σ_j (-1)^j es[j] * c_high[m_off+j]  (for c_high index m_off+j < nk)
    D_values = []  # D_values[b_idx][m_off] = D value mod p
    for b_idx in range(n_B):
        es = all_sigma[b_idx]
        d_row = []
        for m_off in range(conds):
            val = 0
            for j in range(w + 1):
                c_idx = m_off + j
                if c_idx < nk:
                    val += pow(-1, j, p) * es[j] * c_high[c_idx]
            d_row.append(val % p)
        D_values.append(d_row)

    # Character sum computation
    # For each t ∈ F_p^c, compute S(t) = Σ_B ψ(Σ_m t_m D_m(σ(B)))
    # Then M = (1/p^c) Σ_t S(t)

    # When t=0: S(0) = n_B (trivially)
    total = complex(n_B, 0)

    S_magnitudes = []  # |S(t)| for t ≠ 0

    # For small p^c, enumerate all t
    if p ** conds > 500000:
        print(f"  p^c = {p**conds} too large for exhaustive char sum, sampling...")
        # Sample random t vectors
        import random
        n_samples = min(50000, p ** conds - 1)
        for _ in range(n_samples):
            t = [random.randint(1, p - 1) if _ == 0 else random.randint(0, p - 1)
                 for _ in range(conds)]
            # At least one nonzero
            if all(ti == 0 for ti in t):
                t[0] = 1

            St = 0j
            for b_idx in range(n_B):
                arg = sum(t[m] * D_values[b_idx][m] for m in range(conds)) % p
                St += psi(arg, p)
            total += St
            S_magnitudes.append(abs(St))

        M_est = total.real / p ** conds
        return M_est, S_magnitudes, True

    # Exhaustive enumeration
    for t in product(range(p), repeat=conds):
        if all(ti == 0 for ti in t):
            continue  # skip t=0, already counted

        St = 0j
        for b_idx in range(n_B):
            arg = sum(t[m] * D_values[b_idx][m] for m in range(conds)) % p
            St += psi(arg, p)

        total += St
        S_magnitudes.append(abs(St))

    M_char = total.real / p ** conds
    return M_char, S_magnitudes, False


def analyze_char_sum(n, k, p, w, c_high, label=""):
    """Full analysis: direct M, char sum M, S(t) statistics."""
    conds = n - k - w
    n_B = math.comb(n, w)

    print(f"\n{'='*70}")
    print(f"RS[{n},{k}] F_{p}, w={w}, conds/B={conds}, C({n},{w})={n_B}")
    if label:
        print(f"Center type: {label}")
    print(f"c_high = {c_high[:8]}{'...' if len(c_high)>8 else ''}")

    # Direct M
    M_direct = direct_M(n, k, p, w, c_high)
    print(f"M_direct = {M_direct}")

    # Character sum M
    M_char, S_mags, sampled = char_sum_M(n, k, p, w, c_high)
    print(f"M_char   = {M_char:.6f} {'(sampled)' if sampled else '(exact)'}")

    if S_mags:
        max_S = max(S_mags)
        avg_S = sum(S_mags) / len(S_mags)
        # How many t give |S(t)| > n_B/2?
        large = sum(1 for s in S_mags if s > n_B / 2)
        # Cancellation ratio: avg|S|/n_B (1 = no cancellation, 0 = perfect)
        cancel_ratio = avg_S / n_B

        print(f"\nCharacter sum statistics (t ≠ 0):")
        print(f"  max|S(t)|   = {max_S:.2f}  (trivial bound = {n_B})")
        print(f"  avg|S(t)|   = {avg_S:.2f}")
        print(f"  cancel ratio= {cancel_ratio:.4f}  (0=perfect, 1=none)")
        print(f"  |S|>N/2     = {large}/{len(S_mags)}")

        # Key bound: M ≤ N/p^c + max|S|·(p^c-1)/p^c
        pc = p ** conds
        bound = n_B / pc + max_S
        print(f"\n  Trivial bound on M: {bound:.2f}")
        print(f"  Needed for M=O(1): max|S(t)| ≈ {M_direct:.0f} (actual M)")

        # Distribution of |S(t)| values
        buckets = [0] * 10
        for s in S_mags:
            b = min(int(s / n_B * 10), 9)
            buckets[b] += 1
        print(f"\n  |S(t)|/N distribution:")
        for i, cnt in enumerate(buckets):
            bar = '#' * min(cnt * 50 // max(max(buckets), 1), 50)
            print(f"    [{i*10:3d}%-{(i+1)*10:3d}%]: {cnt:6d} {bar}")

    return M_direct, M_char


# ===== Tests =====
print("=" * 70)
print("CHARACTER SUM VERIFICATION")
print("=" * 70)

# Test 1: n=6, k=3, w=2, conds=1 (known M=3)
# Optimal center for conds=1: σ_w = const, i.e., c_high = (1,0,1)
# D = c_3 - σ_1 c_4 + σ_2 c_5 = c_high[0] - σ_1 c_high[1] + σ_2 c_high[2]
# For c_high = (1,0,1): D = 1 + σ_2 → σ_2 = -1 mod p
analyze_char_sum(6, 3, 7, 2, [1, 0, 1], "σ_w-only (conds=1)")

# Test 2: n=8, k=4, w=3, conds=1 (known M=7)
analyze_char_sum(8, 4, 17, 3, [1, 0, 0, 1], "σ_w-only (conds=1)")

# Test 3: n=10, k=5, w=3, conds=2 (known M=3 for p=11)
# Need to find optimal center
# From M_actual_fast.py output: search for best center
print("\n\nSearching for optimal center n=10, p=11...")
best_M = 0
best_c = None
for trial in range(5000):
    import random
    c_high = [random.randint(0, 10) for _ in range(5)]
    M = direct_M(10, 5, 11, 3, c_high)
    if M > best_M:
        best_M = M
        best_c = c_high[:]
        if M >= 3:
            break

if best_c:
    analyze_char_sum(10, 5, 11, 3, best_c, f"optimal (M={best_M})")
else:
    print("  No good center found in 5000 trials")

# Test 4: n=12, k=6, w=4, conds=2 (known M=6 for p=13)
print("\n\nSearching for optimal center n=12, p=13...")
best_M = 0
best_c = None
for trial in range(10000):
    c_high = [random.randint(0, 12) for _ in range(6)]
    M = direct_M(12, 6, 13, 4, c_high)
    if M > best_M:
        best_M = M
        best_c = c_high[:]
        if M >= 5:
            break

if best_c:
    analyze_char_sum(12, 6, 13, 4, best_c, f"optimal (M={best_M})")
else:
    print("  No good center found in 10000 trials")

# Extra: character sum for RANDOM center (expect M ≈ C(n,w)/p^c)
print("\n\n--- Random center comparison ---")
c_rand = [random.randint(0, 6) for _ in range(3)]
analyze_char_sum(6, 3, 7, 2, c_rand, "random")

# Test 5: p-dependence check for conds=2
# n=10 with p=11 vs p=31
print("\n\n--- p-dependence (conds=2) ---")
if best_c and best_M >= 2:
    # Use the center found for p=11 and check with p=31
    print(f"Using center from p=11: c_high={best_c}")
    analyze_char_sum(10, 5, 31, 3, best_c, f"p=11 center at p=31")

    # Find new optimal for p=31
    print("\nSearching for optimal center at p=31...")
    best_M2 = 0
    best_c2 = None
    for trial in range(5000):
        c_high = [random.randint(0, 30) for _ in range(5)]
        M = direct_M(10, 5, 31, 3, c_high)
        if M > best_M2:
            best_M2 = M
            best_c2 = c_high[:]
            if M >= 3:
                break
    if best_c2:
        analyze_char_sum(10, 5, 31, 3, best_c2, f"optimal at p=31 (M={best_M2})")
