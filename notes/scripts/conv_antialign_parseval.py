#!/usr/bin/env python3
"""
Convolutional Anti-Alignment — Restricted Parseval Test.

KEY THEORETICAL FORMULATION:

M_alg = (1/p^c) Σ_{t ∈ V^⊥} S(t)
      = N/p^c + (1/p^c) Σ_{t ∈ V^⊥ \ {0}} S(t)

For M_alg = O(1), need the error E = (1/p^c) Σ_{t≠0} S(t) to be O(1).

By Cauchy-Schwarz:
|E|^2 ≤ (|V^⊥|-1)/p^{2c} · Σ_{t∈V^⊥\{0}} |S(t)|^2
      = (p^c-1)/p^{2c} · R(V^⊥)

where R(V^⊥) = Σ_{t∈V^⊥\{0}} |S(t)|^2 is the RESTRICTED second moment.

Full Parseval: Σ_{t∈F_p^w} |S(t)|^2 = N·p^w

If S(t) is "pseudorandom": R(V^⊥) ≈ (p^c-1)/(p^w-1) · (Np^w - N^2) ≈ Np^c
Then |E|^2 ≈ (p^c/p^{2c}) · Np^c = N → |E| ≈ √N

Hmm that gives M_alg = N/p^c + O(√N/p^c). For large p^c: O(√N/p^c) → 0. But for p ≈ n:
N/p^c is already O(1), so √N/p^c ≈ √N / N = 1/√N → 0. Good!

Wait, let me recompute. If R(V^⊥) ≈ Np^c, then:
|E|^2 ≤ ((p^c-1)/p^{2c}) · Np^c = N(p^c-1)/p^c ≈ N
|E| ≤ √N

M_alg = N/p^c ± √N/p^c... no wait:
M_alg = N/p^c + E where |E| ≤ √(N(p^c-1))/p^c ≈ √N/p^c... hmm, that's |E| ≤ √(N)/p^{c/2}?

Let me redo: Cauchy-Schwarz gives
|E| = |(1/p^c) Σ_{t≠0∈V^⊥} S(t)|
    ≤ (1/p^c) √((p^c-1) · R(V^⊥))
    ≈ (1/p^c) √(p^c · Np^c)
    = (1/p^c) · p^c · √(N/p^c)... no.

Let me be precise:
|E| ≤ (1/p^c) · √(|V^⊥\{0}| · R(V^⊥))   [Cauchy-Schwarz]
    = (1/p^c) · √((p^c-1) · R)

If R ≈ (p^c-1)·Np^w/(p^w-1) ≈ N·p^c (assuming equidist):
|E| ≤ (1/p^c) · √((p^c-1) · N·p^c)
    ≈ (1/p^c) · p^c · √(N/p^c)... wait:
    = (1/p^c) · √(N·p^{2c})... no.

R ≈ N·p^c. Then:
|E| ≤ (1/p^c) · √((p^c-1)·N·p^c)
    ≈ (1/p^c) · √(N·p^{2c})
    = √N

So |E| ≤ √N and M_alg ≤ N/p^c + √N. For N/p^c = O(1): M_alg ≤ O(1) + O(√N).
This DOESN'T help — √N → ∞!

Hmm. So Cauchy-Schwarz with equidistributed |S(t)|^2 gives M_alg ≤ √N. Not useful.

The issue: we need CANCELLATION in the sum Σ S(t), not just bounds on individual |S(t)|.

Alternative approach: what if S(t) has STRUCTURED PHASES on V^⊥?

Let me compute S(t) for all t ∈ V^⊥ and check the actual cancellation.

EXPERIMENTS:
  E1. Compute S(t) for all t in F_p^w
  E2. For each Toeplitz V^⊥, compute M_alg = (1/p^c) Σ S(t)
  E3. Check: does the sum Σ_{t∈V^⊥} S(t) have cancellation beyond √(N·p^c)?
  E4. Compare Toeplitz V^⊥ vs random V^⊥
"""

import itertools
import random
import cmath
from collections import Counter

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

def elem_sym(B, omega, p):
    roots = [pow(omega, i, p) for i in B]
    w = len(roots)
    e = [0] * (w + 1)
    e[0] = 1
    for r in roots:
        for j in range(w, 0, -1):
            e[j] = (e[j] + e[j-1] * r) % p
    return tuple(e[1:])

def compute_S_all(sigma_tuples, w, p):
    """Compute S(t) for all t ∈ F_p^w.
    S(t) = Σ_B exp(2πi/p · Σ_j t_j σ_j(B))
    Returns dict t -> S(t) (complex number).
    """
    zeta = cmath.exp(2j * cmath.pi / p)
    S = {}
    # Enumerate all t
    for idx in range(p**w):
        t = []
        tmp = idx
        for _ in range(w):
            t.append(tmp % p)
            tmp //= p
        t = tuple(t)
        val = 0
        for sig in sigma_tuples:
            phase = sum(t[j] * sig[j] for j in range(w)) % p
            val += zeta**phase
        S[t] = val
    return S

def toeplitz_row_space(n, k, w, c_synd, p):
    """Return the row space of the Toeplitz matrix as a list of vectors in F_p^w."""
    conds = n - k - w
    rows = []
    for r in range(conds):
        row = tuple(((-1)**(j+1) * c_synd[r+j+1]) % p for j in range(w))
        rows.append(row)
    return rows

def span(rows, p):
    """Generate all linear combinations of rows over F_p."""
    if not rows:
        return [(0,)*len(rows[0])] if rows else [()]
    w = len(rows[0])
    conds = len(rows)
    result = set()
    for coeffs_idx in range(p**conds):
        coeffs = []
        tmp = coeffs_idx
        for _ in range(conds):
            coeffs.append(tmp % p)
            tmp //= p
        t = tuple(sum(coeffs[r] * rows[r][j] for r in range(conds)) % p for j in range(w))
        result.add(t)
    return list(result)

def main():
    test_cases = [
        (10, 5, 3, 11),  # conds=2
        (8, 4, 3, 17),   # conds=1
    ]

    for n, k, w, p in test_cases:
        omega = find_omega(p, n)
        conds = n - k - w

        print(f"\n{'='*70}")
        print(f"n={n}, k={k}, w={w}, p={p}, conds={conds}")
        print(f"{'='*70}")

        sigma_tuples = [elem_sym(B, omega, p) for B in itertools.combinations(range(n), w)]
        N = len(sigma_tuples)
        print(f"N = {N}, N/p^c = {N/p**conds:.2f}")

        # Skip if p^w too large
        if p**w > 50000:
            print("p^w too large for full S computation, sampling...")
            continue

        print("Computing S(t) for all t...")
        S_all = compute_S_all(sigma_tuples, w, p)
        print(f"Done. {len(S_all)} values.")

        # Verify Parseval
        total_sq = sum(abs(v)**2 for v in S_all.values())
        print(f"\nParseval: Σ|S(t)|^2 = {total_sq:.1f}, N·p^w = {N*p**w}")
        print(f"Ratio: {total_sq/(N*p**w):.6f}")

        # S(0) = N
        print(f"S(0) = {S_all[(0,)*w]:.1f} (should be {N})")

        # Distribution of |S(t)|^2 for t ≠ 0
        nz_sq = [abs(S_all[t])**2 for t in S_all if t != (0,)*w]
        avg_sq = sum(nz_sq)/len(nz_sq)
        print(f"|S(t)|^2: avg={avg_sq:.2f}, max={max(nz_sq):.2f}, min={min(nz_sq):.2f}")
        print(f"Expected avg = (Np^w - N^2)/(p^w - 1) = {(N*p**w - N**2)/(p**w - 1):.2f}")
        print(f"√(pN) = {(p*N)**0.5:.2f}, max|S|/√(pN) = {max(nz_sq)**0.5/(p*N)**0.5:.2f}")

        # Now: for Toeplitz row spaces, compute Σ_{t∈V^⊥} S(t)
        print(f"\n--- Toeplitz restricted sums ---")
        n_synd = n - k
        n_trials = min(5000, p**n_synd)

        sums_toeplitz = []
        sums_random = []

        for trial in range(n_trials):
            if trial < p**n_synd:
                c_synd = []
                tmp = trial
                for _ in range(n_synd):
                    c_synd.append(tmp % p)
                    tmp //= p
            else:
                c_synd = [random.randint(0, p-1) for _ in range(n_synd)]

            rows = toeplitz_row_space(n, k, w, c_synd, p)
            V_perp = span(rows, p)

            # Sum S(t) over V^⊥
            total = sum(S_all.get(t, 0) for t in V_perp)
            M_alg = total.real / p**conds  # Should be a real integer
            sums_toeplitz.append(M_alg)

        # Compare with random V^⊥
        for trial in range(n_trials):
            rows = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(conds)]
            V_perp = span(rows, p)
            total = sum(S_all.get(t, 0) for t in V_perp)
            M_alg = total.real / p**conds
            sums_random.append(M_alg)

        # Round to nearest integer (should be exact)
        sums_toeplitz_int = [round(m) for m in sums_toeplitz]
        sums_random_int = [round(m) for m in sums_random]

        print(f"\n  Toeplitz V^⊥ (n={n_trials}):")
        print(f"    M_alg distribution: {Counter(sums_toeplitz_int).most_common(10)}")
        print(f"    max M_alg = {max(sums_toeplitz_int)}")

        print(f"\n  Random V^⊥ (n={n_trials}):")
        print(f"    M_alg distribution: {Counter(sums_random_int).most_common(10)}")
        print(f"    max M_alg = {max(sums_random_int)}")

        # KEY: Restricted second moment
        print(f"\n--- Restricted second moment analysis ---")
        # For each Toeplitz V^⊥, compute R = Σ_{t∈V^⊥\{0}} |S(t)|^2
        R_toeplitz = []
        R_random = []

        for trial in range(min(1000, n_trials)):
            if trial < p**n_synd:
                c_synd = []
                tmp = trial
                for _ in range(n_synd):
                    c_synd.append(tmp % p)
                    tmp //= p
            else:
                c_synd = [random.randint(0, p-1) for _ in range(n_synd)]

            rows = toeplitz_row_space(n, k, w, c_synd, p)
            V_perp = span(rows, p)
            R = sum(abs(S_all.get(t, 0))**2 for t in V_perp if t != (0,)*w)
            R_toeplitz.append(R)

        for trial in range(min(1000, n_trials)):
            rows = [tuple(random.randint(0, p-1) for _ in range(w)) for _ in range(conds)]
            V_perp = span(rows, p)
            R = sum(abs(S_all.get(t, 0))**2 for t in V_perp if t != (0,)*w)
            R_random.append(R)

        expected_R = (p**conds - 1) * (N * p**w - N**2) / (p**w - 1)
        print(f"  Expected R (equidistributed) = {expected_R:.1f}")
        print(f"  ≈ N·p^c = {N * p**conds}")

        print(f"\n  Toeplitz R(V^⊥):")
        print(f"    avg={sum(R_toeplitz)/len(R_toeplitz):.1f}, max={max(R_toeplitz):.1f}, min={min(R_toeplitz):.1f}")
        print(f"    avg/expected = {sum(R_toeplitz)/len(R_toeplitz)/expected_R:.3f}")

        print(f"\n  Random R(V^⊥):")
        print(f"    avg={sum(R_random)/len(R_random):.1f}, max={max(R_random):.1f}, min={min(R_random):.1f}")
        print(f"    avg/expected = {sum(R_random)/len(R_random)/expected_R:.3f}")

        # For the highest-M Toeplitz cases, what is R?
        top_M_indices = sorted(range(len(sums_toeplitz_int)), key=lambda i: sums_toeplitz_int[i], reverse=True)[:5]
        print(f"\n  Top-5 Toeplitz M cases:")
        for idx in top_M_indices:
            if idx < len(R_toeplitz):
                print(f"    M={sums_toeplitz_int[idx]}, R={R_toeplitz[idx]:.1f}, R/expected={R_toeplitz[idx]/expected_R:.2f}")

if __name__ == '__main__':
    main()
