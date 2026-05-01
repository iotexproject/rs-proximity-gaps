"""
intersection_rs_flat.py — Compare M on RS-compatible flats vs random flats.

Key question: Is the RS flat "special" (giving smaller M than random)?
Or is M = C(n,w)/p^{w-2} the truth even for RS?

At p ≡ 1 mod n: V_all = {all C(n,w) subsets of n-th roots} in σ-space.
M = |V_c ∩ V_all| where V_c is the RS-compatible flat for center c.

We compute M for EVERY center codeword c (degree < k polynomial evaluated on L).
"""

import random
from math import comb
from itertools import combinations

def find_primitive_root(p):
    """Find a primitive root mod p."""
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = (val * g) % p
        if len(seen) == p - 1:
            return g
    return None

def elem_sym(subset, p):
    """Elementary symmetric polynomials of a subset of F_p elements."""
    w = len(subset)
    # e_j via Newton's identities or direct expansion
    e = [0] * (w + 1)
    e[0] = 1
    for x in subset:
        for j in range(min(w, len(subset)), 0, -1):
            e[j] = (e[j] + x * e[j-1]) % p
    return tuple(e[1:])  # (e_1, ..., e_w)

def rs_codeword(coeffs, L, p):
    """Evaluate polynomial with given coeffs on L."""
    return tuple(sum(c * pow(x, i, p) for i, c in enumerate(coeffs)) % p for x in L)

def main():
    print("=" * 70)
    print("RS-COMPATIBLE FLAT vs RANDOM FLAT: M comparison")
    print("=" * 70)

    test_cases = [
        # (n, w, c) — c = number of RS conditions = n - k - w
        # k = n - w - c, so k must be positive: c < n - w
        (8, 3, 1),   # k=4, rate 1/2
        (8, 3, 2),   # k=3, rate 3/8
        (10, 3, 1),  # k=6
        (10, 3, 2),  # k=5, rate 1/2
        (10, 4, 1),  # k=5
        (10, 4, 2),  # k=4
        (12, 3, 1),  # k=8
        (12, 3, 2),  # k=7
        (12, 4, 1),  # k=7
        (12, 4, 2),  # k=6, rate 1/2
    ]

    for n, w, c in test_cases:
        k = n - w - c
        if k <= 0:
            continue
        d = w - c  # flat dimension

        # Find smallest prime p ≡ 1 mod n, p > n
        p = n + 1
        while True:
            if all(p % i != 0 for i in range(2, int(p**0.5) + 2)):
                if (p - 1) % n == 0:
                    break
            p += 1
            if p > 500:
                break

        if p > 200:
            # Try a larger search
            p = None
            for pp in range(n + 1, 1000):
                if all(pp % i != 0 for i in range(2, int(pp**0.5) + 2)):
                    if (pp - 1) % pp == 0 or (pp - 1) % n == 0:
                        if (pp - 1) % n == 0 and pp > n:
                            p = pp
                            break
            if p is None or p > 200:
                continue

        g = find_primitive_root(p)
        omega = pow(g, (p - 1) // n, p)  # primitive n-th root of unity
        L = [pow(omega, i, p) for i in range(n)]

        print(f"\n{'='*60}")
        print(f"n={n}, w={w}, c={c}, k={k}, d={d}, p={p}, ω={omega}")
        print(f"C(n,w)={comb(n,w)}, C(n,w)/p^c ≈ {comb(n,w)/p**c:.2f}")
        print(f"{'='*60}")

        # Enumerate all w-subsets and their σ-vectors
        all_subsets = list(combinations(range(n), w))
        sigma_to_subsets = {}
        for B_idx in all_subsets:
            B = tuple(L[i] for i in B_idx)
            sigma = elem_sym(B, p)
            key = sigma
            if key not in sigma_to_subsets:
                sigma_to_subsets[key] = []
            sigma_to_subsets[key].append(B_idx)

        print(f"  #distinct σ-vectors: {len(sigma_to_subsets)} (out of C(n,w)={comb(n,w)})")

        # For each RS codeword c (polynomial of degree < k), compute M
        # M = #{B : c agrees with some degree < k poly on L\B}
        # Equivalently: M = #{B ⊂ L : ∃ f of deg < k with f(β) = c(β) for β ∈ L\B}
        # Which is: the evaluation c - f vanishes outside B, so c - f has support ⊂ B.
        # Since deg(c-f) < max(deg c, k) < k + ... hmm, this is just the list decoding.

        # Simpler approach: enumerate all codewords f (deg < k), check agreement.
        # For each center vector v ∈ F_p^n, M(v) = #{B : σ(B) satisfies the RS conditions for v}

        # Actually, for a center v ∈ F_p^n, B is "compatible" if:
        # Σ_j σ_j(B) · v_{m-j} = [something] for c values of m.
        # This is the linear condition on σ(B).

        # Simpler direct approach: for each codeword f (deg < k), find all other codewords
        # g (deg < k) with |{β ∈ L : f(β) ≠ g(β)}| ≤ w.
        # Then M(f) = #{g ≠ f : d(f,g) ≤ w} where d is Hamming distance on L.

        # But this overcounts: we want M = #{codewords within distance w of c}, where
        # c is not necessarily a codeword.

        # For the analysis, let's just compute M for codeword centers.
        # For a codeword center f, B = support of (f - g)|_L for another codeword g.
        # |B| = d(f,g). We want d(f,g) ≤ w.

        # Since RS[n,k] has minimum distance n-k+1, and w < n-k+1 for our params:
        # Actually, d_min = n - k + 1. For k=n-w-c: d_min = w + c + 1.
        # So d(f,g) ≥ w + c + 1 > w. So M(f) = 1 for codeword centers!

        # For non-codeword centers, we need to enumerate more carefully.
        # Let's use the σ-space approach: for a random center vector v ∈ F_p^n,
        # define c conditions on σ, and count how many σ-points satisfy them.

        # The conditions: for positions m = k, k+1, ..., k+c-1:
        # Σ_{j=0}^{w} (-1)^j σ_j v_{m-j} = 0 (where σ_0 = 1)
        # This is: v_m - σ₁ v_{m-1} + σ₂ v_{m-2} - ... + (-1)^w σ_w v_{m-w} = 0

        # These are LINEAR conditions on σ = (σ₁, ..., σ_w).

        # Let's compute M for many random centers.

        sigma_list = list(sigma_to_subsets.keys())  # all valid σ-vectors

        M_values = []
        n_centers = min(200, p**w) if p**w <= 200 else 200

        # Generate random centers (vectors in F_p^n, not necessarily codewords)
        random.seed(123)
        for trial in range(n_centers):
            # Random vector v ∈ F_p^n
            v = [random.randrange(p) for _ in range(n)]

            # Compute the c linear conditions on σ
            # For syndrome positions m = k, k+1, ..., k+c-1:
            # v_m - σ₁·v_{m-1} + σ₂·v_{m-2} - ... + (-1)^w·σ_w·v_{m-w} = 0

            # Count how many σ-vectors from sigma_list satisfy ALL c conditions
            count = 0
            for sigma in sigma_list:
                ok = True
                for m_offset in range(c):
                    m = k + m_offset
                    val = v[m % n]
                    for j in range(1, w + 1):
                        val = (val + (-1)**j * sigma[j-1] * v[(m - j) % n]) % p
                    if val != 0:
                        ok = False
                        break
                if ok:
                    count += 1
            M_values.append(count)

        print(f"\n  RS M for {n_centers} random centers:")
        print(f"    min={min(M_values)}, max={max(M_values)}, avg={sum(M_values)/len(M_values):.2f}")
        M_sorted = sorted(M_values)
        print(f"    histogram: {M_sorted[:10]}...{M_sorted[-10:]}")
        print(f"    #zeros: {M_values.count(0)}/{len(M_values)}")
        # Distribution
        from collections import Counter
        dist = Counter(M_values)
        print(f"    distribution: {dict(sorted(dist.items()))}")

        # Compare with random flat
        print(f"\n  Random flat M (for comparison):")
        M_rand = []
        for trial in range(n_centers):
            # Random affine c-codim flat: pick c random linear constraints on σ
            count = 0
            # Generate c random linear forms a·σ = b
            A = [[random.randrange(p) for _ in range(w)] for _ in range(c)]
            b = [random.randrange(p) for _ in range(c)]

            for sigma in sigma_list:
                ok = True
                for eq in range(c):
                    val = sum(A[eq][j] * sigma[j] for j in range(w)) % p
                    if val != b[eq] % p:
                        ok = False
                        break
                if ok:
                    count += 1
            M_rand.append(count)

        print(f"    min={min(M_rand)}, max={max(M_rand)}, avg={sum(M_rand)/len(M_rand):.2f}")
        M_rand_sorted = sorted(M_rand)
        print(f"    histogram: {M_rand_sorted[:10]}...{M_rand_sorted[-10:]}")
        dist_rand = Counter(M_rand)
        print(f"    distribution: {dict(sorted(dist_rand.items()))}")

main()
