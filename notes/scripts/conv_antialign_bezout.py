#!/usr/bin/env python3
"""
Bézout / GCD approach to bounding M on a line.

KEY IDEA:
For w=3, the σ-image lies on the variety {g(T) | T^n - 1} where
g(T) = T^3 - σ_1 T^2 + σ_2 T - σ_3.

On a line σ = a + t·b in F_p^3:
  g_t(T) = T^3 - (a_1+tb_1)T^2 + (a_2+tb_2)T - (a_3+tb_3)

T^n mod g_t(T) = r_2(t)T^2 + r_1(t)T + r_0(t)

σ-image point on line ⟺ r_2(t) = 0, r_1(t) = 0, r_0(t) = 1.

M ≤ deg gcd(r_0-1, r_1, r_2).

EXPERIMENTS:
  E1. Compute r_i(t) as polynomials over F_p[t]
  E2. Compute gcd and its degree for Toeplitz lines
  E3. Compare with random lines
  E4. Factor analysis: WHY is the gcd low-degree?
"""

import itertools
import random

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g
def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0: factors.add(d); n //= d
        d += 1
    if n > 1: factors.add(n)
    return factors
def find_omega(p, n):
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

# Polynomial arithmetic over F_p[t]
# A polynomial is a list of coefficients [c0, c1, ..., cd] = c0 + c1*t + ... + cd*t^d

def poly_zero():
    return [0]

def poly_one(p):
    return [1]

def poly_const(c, p):
    return [c % p]

def poly_t(p):
    return [0, 1]

def poly_add(a, b, p):
    n = max(len(a), len(b))
    r = [0] * n
    for i in range(len(a)):
        r[i] = (r[i] + a[i]) % p
    for i in range(len(b)):
        r[i] = (r[i] + b[i]) % p
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r

def poly_sub(a, b, p):
    return poly_add(a, [(-x) % p for x in b], p)

def poly_mul(a, b, p):
    if a == [0] or b == [0]:
        return [0]
    r = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            r[i+j] = (r[i+j] + a[i] * b[j]) % p
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r

def poly_scale(a, c, p):
    r = [(x * c) % p for x in a]
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r

def poly_deg(a):
    if a == [0]:
        return -1
    return len(a) - 1

def poly_lead(a):
    return a[-1] if a else 0

def poly_divmod(a, b, p):
    """Divide a by b over F_p[t]. Returns (quotient, remainder)."""
    if b == [0]:
        raise ZeroDivisionError
    if poly_deg(a) < poly_deg(b):
        return [0], list(a)

    inv_lead = pow(b[-1], p-2, p)
    a = list(a)
    q = [0] * (len(a) - len(b) + 1)

    for i in range(len(a) - len(b), -1, -1):
        if len(a) > i + len(b) - 1:
            coeff = (a[i + len(b) - 1] * inv_lead) % p
        else:
            continue
        q[i] = coeff
        for j in range(len(b)):
            a[i+j] = (a[i+j] - coeff * b[j]) % p

    # Trim
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return q, a

def poly_gcd(a, b, p):
    """GCD of two polynomials over F_p[t]."""
    while b != [0]:
        _, r = poly_divmod(a, b, p)
        a, b = b, r
    # Make monic
    if a != [0]:
        inv_lead = pow(a[-1], p-2, p)
        a = [(x * inv_lead) % p for x in a]
    return a

def poly_eval(a, t, p):
    """Evaluate polynomial at t over F_p."""
    val = 0
    for c in reversed(a):
        val = (val * t + c) % p
    return val

def compute_remainders_on_line(n, w, a, b, p):
    """
    Compute T^n mod g_t(T) where g_t(T) = T^w - Σ (a_j + t·b_j) σ_{w-j}...

    For w=3: g_t = T^3 - (a1+t·b1)T^2 + (a2+t·b2)T - (a3+t·b3)

    We work in (F_p[t])[T], computing T^n mod g_t.
    Each coefficient is a polynomial in t.

    Returns (r0, r1, r2) where T^n mod g_t = r2·T^2 + r1·T + r0.
    """
    # State: (a_k, b_k, c_k) as polynomials in t
    # Recurrence (for w=3):
    # a_{k+1} = σ_3(t) · c_k
    # b_{k+1} = a_k - σ_2(t) · c_k
    # c_{k+1} = b_k + σ_1(t) · c_k

    # σ_j(t) = a_j + t · b_j (affine in t)
    s1 = [a[0], b[0]]  # a1 + t·b1
    s2 = [a[1], b[1]]  # a2 + t·b2
    s3 = [a[2], b[2]]  # a3 + t·b3

    # Initial: T^0 mod g = 1 → (a0,b0,c0) = (1,0,0)
    ak = [1]  # polynomial 1 in t
    bk = [0]
    ck = [0]

    for step in range(n):
        new_ak = poly_mul(s3, ck, p)
        new_bk = poly_sub(ak, poly_mul(s2, ck, p), p)
        new_ck = poly_add(bk, poly_mul(s1, ck, p), p)
        ak, bk, ck = new_ak, new_bk, new_ck

    return ak, bk, ck

def experiment_1_gcd_analysis(n, k, w, p):
    """E1: Compute gcd(r0-1, r1, r2) for Toeplitz lines."""
    omega = find_omega(p, n)
    conds = n - k - w
    print(f"\n{'='*60}")
    print(f"n={n}, k={k}, w={w}, p={p}, conds={conds}")
    print(f"{'='*60}")

    # Toeplitz line: σ_j = (condition matrix row 0) · ... + (condition matrix row 1) · ...
    # For conds=2, w=3:
    # Line in F_p^3 parameterized by syndrome (c_k,...,c_{n-1})
    # But the line is an affine line in σ-space, not syndrome-space.

    # Actually, for each fixed syndrome, the compatible σ's lie on an affine line (codim-2 = 1D).
    # But different syndromes give different lines.

    # What we want: for a generic line in σ-space, what's deg gcd(r0-1, r1, r2)?

    # Let's take a random line σ = a + t·b and compute
    print(f"\n--- Random lines in F_{p}^{w} ---")

    gcd_degs = []
    for trial in range(100):
        a = [random.randint(0, p-1) for _ in range(w)]
        b = [random.randint(0, p-1) for _ in range(w)]
        if all(x == 0 for x in b):
            continue

        r0, r1, r2 = compute_remainders_on_line(n, w, a, b, p)

        # r0 - 1
        r0_minus_1 = poly_sub(r0, [1], p)

        # gcd(r0-1, r1, r2)
        g = poly_gcd(r0_minus_1, r1, p)
        g = poly_gcd(g, r2, p)

        d = poly_deg(g)
        gcd_degs.append(d)

        if trial < 5 or d > 2:
            # Count actual zeros (σ-image points on this line)
            n_zeros = 0
            for t in range(p):
                if poly_eval(r0_minus_1, t, p) == 0 and poly_eval(r1, t, p) == 0 and poly_eval(r2, t, p) == 0:
                    n_zeros += 1
            print(f"  Trial {trial}: deg(gcd) = {d}, actual zeros = {n_zeros}, "
                  f"deg(r0-1)={poly_deg(r0_minus_1)}, deg(r1)={poly_deg(r1)}, deg(r2)={poly_deg(r2)}")

    print(f"\n  GCD degree distribution: min={min(gcd_degs)}, max={max(gcd_degs)}, "
          f"avg={sum(gcd_degs)/len(gcd_degs):.1f}")
    from collections import Counter
    print(f"  {Counter(gcd_degs).most_common(10)}")

    # Now check Toeplitz lines
    print(f"\n--- Toeplitz lines ---")
    # For each syndrome, the affine subspace is Ax = b with A Toeplitz.
    # For conds=2, w=3: the subspace is a line.
    # We need to extract the line parameterization from the Toeplitz matrix.

    gcd_degs_toeplitz = []
    for trial in range(100):
        c_synd = [random.randint(0, p-1) for _ in range(n-k)]
        if all(c == 0 for c in c_synd):
            continue

        # Toeplitz matrix
        A = []
        bvec = []
        for r in range(conds):
            row = [((-1)**(j+1) * c_synd[r+j+1]) % p for j in range(w)]
            A.append(row)
            bvec.append((-c_synd[r]) % p)

        # Solve for the line: Ax = bvec, codim-2 → 1D solution set
        # x = x0 + t·v where Av = 0 and Ax0 = bvec

        # Find null space of A (1D for rank-2 matrix)
        # Gaussian elimination
        inv_table = [0]*p
        for aa in range(1,p):
            inv_table[aa] = pow(aa, p-2, p)

        # Check rank
        mat = [list(row) for row in A]
        pivots = []
        for col in range(w):
            found = -1
            for row in range(len(pivots), conds):
                if mat[row][col] % p != 0:
                    found = row
                    break
            if found == -1:
                continue
            mat[len(pivots)], mat[found] = mat[found], mat[len(pivots)]
            scale = inv_table[mat[len(pivots)][col]]
            mat[len(pivots)] = [(x * scale) % p for x in mat[len(pivots)]]
            for row in range(conds):
                if row != len(pivots) and mat[row][col] % p != 0:
                    factor = mat[row][col]
                    mat[row] = [(mat[row][j] - factor * mat[len(pivots)][j]) % p for j in range(w)]
            pivots.append(col)

        rank = len(pivots)
        if rank != conds:
            continue  # rank-deficient, skip

        # Null space vector: free variable is the non-pivot column
        free_cols = [j for j in range(w) if j not in pivots]
        if not free_cols:
            continue  # no free variables (shouldn't happen for w > conds)

        v = [0] * w
        v[free_cols[0]] = 1
        for i, pc in enumerate(pivots):
            # aug matrix: mat[i] is [row | b_i']
            # Particular solution: set free vars = 0
            pass

        # Actually, let me solve this differently.
        # Augmented system [A | b]
        aug = [list(A[r]) + [bvec[r]] for r in range(conds)]
        # Row reduce
        for col in range(w):
            found = -1
            for row in range(len(pivots) if col < len(pivots) else conds, conds):
                pass
        # Too complex, let me just parameterize directly

        # For w=3, conds=2: one free variable.
        # After Gaussian elimination, the solution is:
        # σ_{free} = t (free parameter)
        # σ_{pivot_j} = x0_j + ... * t

        # Re-do elimination on augmented matrix
        aug = [list(A[r]) + [bvec[r]] for r in range(conds)]
        pivots2 = []
        for col in range(w):
            found = -1
            for row in range(len(pivots2), conds):
                if aug[row][col] % p != 0:
                    found = row
                    break
            if found == -1:
                continue
            aug[len(pivots2)], aug[found] = aug[found], aug[len(pivots2)]
            scale = inv_table[aug[len(pivots2)][col]]
            aug[len(pivots2)] = [(x * scale) % p for x in aug[len(pivots2)]]
            for row in range(conds):
                if row != len(pivots2) and aug[row][col] % p != 0:
                    factor = aug[row][col]
                    aug[row] = [(aug[row][j] - factor * aug[len(pivots2)][j]) % p for j in range(w+1)]
            pivots2.append(col)

        if len(pivots2) != conds:
            continue

        free_cols2 = [j for j in range(w) if j not in pivots2]
        if not free_cols2:
            continue

        # Parameterize: σ_{free} = t, σ_{pivot_i} = aug[i][w] - aug[i][free]*t
        fc = free_cols2[0]
        line_a = [0] * w
        line_b = [0] * w
        line_a[fc] = 0
        line_b[fc] = 1
        for i, pc in enumerate(pivots2):
            line_a[pc] = aug[i][w]
            line_b[pc] = (-aug[i][fc]) % p

        # Now compute remainders on this line
        r0, r1, r2 = compute_remainders_on_line(n, w, line_a, line_b, p)
        r0_minus_1 = poly_sub(r0, [1], p)
        g = poly_gcd(r0_minus_1, r1, p)
        g = poly_gcd(g, r2, p)
        d = poly_deg(g)
        gcd_degs_toeplitz.append(d)

        # Count actual zeros
        n_zeros = 0
        for t in range(p):
            if poly_eval(r0_minus_1, t, p) == 0 and poly_eval(r1, t, p) == 0 and poly_eval(r2, t, p) == 0:
                n_zeros += 1

        if trial < 5 or d > 2:
            print(f"  Trial {trial}: deg(gcd) = {d}, actual zeros = {n_zeros}")

    if gcd_degs_toeplitz:
        print(f"\n  Toeplitz GCD degree: min={min(gcd_degs_toeplitz)}, max={max(gcd_degs_toeplitz)}")
        from collections import Counter
        print(f"  {Counter(gcd_degs_toeplitz).most_common(10)}")

def main():
    experiment_1_gcd_analysis(10, 5, 3, 11)
    experiment_1_gcd_analysis(10, 5, 3, 31)
    experiment_1_gcd_analysis(10, 5, 3, 41)

if __name__ == '__main__':
    main()
