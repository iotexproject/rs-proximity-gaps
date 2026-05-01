"""
Direct check: V_{012} ∩ Σ for RS codes.

V_{012} = {σ ∈ A^w : r_0(σ)=1, r_1(σ)=0, r_2(σ)=0}
Σ = {σ(E) : E ∈ C(L,w)} = sigma-image of all w-subsets of L

M=0 on ALL RS-compatible flats ⟺ V_{012} ∩ Σ = ∅

For each w-subset E of L:
  1. Compute σ(E) = (e_1(E), ..., e_w(E))
  2. Compute r_0, r_1, r_2 at σ(E) via companion matrix
  3. Check if r_0=1, r_1=0, r_2=0

If NO subset satisfies these conditions, then V_{012} ∩ Σ = ∅.

Also check: for codim c ≥ 1, how many subsets satisfy r_0=1?
And for c ≥ 2, how many satisfy r_0=1, r_1=0?
"""

import itertools
import sys

def find_primitive_root(n, p):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        omega = pow(g, (p-1)//n, p)
        if pow(omega, n, p) == 1:
            ok = all(pow(omega, d, p) != 1 for d in range(1, n) if n % d == 0 and d < n)
            if ok:
                return omega
    return None

def companion_matrix_remainder(sigma, n, p):
    """Compute R(x) = x^n mod Λ(x;σ) via companion matrix recurrence.
    Returns (r_0, r_1, ..., r_{w-1}) where R(x) = r_0 x^{w-1} + r_1 x^{w-2} + ...

    Λ(x) = x^w - σ_1 x^{w-1} + σ_2 x^{w-2} - ... + (-1)^w σ_w
    """
    w = len(sigma)
    # Start with x^w = σ_1 x^{w-1} - σ_2 x^{w-2} + ... + (-1)^{w+1} σ_w
    # State vector = coefficients of current polynomial of degree < w
    # state[0] = coeff of x^{w-1}, state[1] = coeff of x^{w-2}, etc.

    # Initialize: x^0 = 1 → state = [0, 0, ..., 0, 1]
    state = [0] * w
    state[w-1] = 1  # x^0 has const term 1

    # Multiply by x repeatedly: n times gives x^n mod Λ
    for _ in range(n):
        # Multiply by x: shift left
        # x * (a_0 x^{w-1} + ... + a_{w-1}) = a_0 x^w + a_1 x^{w-1} + ...
        # Replace x^w = σ_1 x^{w-1} - σ_2 x^{w-2} + ...
        top = state[0]
        new_state = [0] * w
        for j in range(w - 1):
            new_state[j] = state[j + 1]
        # Add top * (σ_1 x^{w-1} - σ_2 x^{w-2} + ...)
        # = top * Σ (-1)^{i+1} σ_i x^{w-1-i+1}... no wait
        # Λ(x) = x^w - σ_1 x^{w-1} + σ_2 x^{w-2} - ... + (-1)^w σ_w = 0
        # So x^w = σ_1 x^{w-1} - σ_2 x^{w-2} + ... + (-1)^{w+1} σ_w
        for i in range(w):
            sign = (-1) ** (i + 1)  # alternating: +σ_1, -σ_2, +σ_3, ...
            new_state[i] = (new_state[i] + top * sign * sigma[i]) % p
        state = new_state

    return state  # [r_0, r_1, ..., r_{w-1}]

def elem_sym(subset, L, p):
    """Compute elementary symmetric polynomials of the elements L[i] for i in subset."""
    elems = [L[i] for i in subset]
    w = len(elems)
    # e_k via dynamic programming
    e = [0] * (w + 1)
    e[0] = 1
    for x in elems:
        for j in range(w, 0, -1):
            e[j] = (e[j] + x * e[j-1]) % p
    return e[1:]  # [e_1, e_2, ..., e_w]

def check_v012_intersection(n, k, p, codim_check=3):
    """Check V_{012} ∩ Σ for RS[n,k] over F_p.

    codim_check: how many remainder conditions to check (c ≥ codim_check → those conditions)
    """
    omega = find_primitive_root(n, p)
    if omega is None:
        return None

    L = [pow(omega, i, p) for i in range(n)]

    # For different codimension excesses c, check different remainder conditions
    # c=1: just r_0=1
    # c=2: r_0=1, r_1=0
    # c=3: r_0=1, r_1=0, r_2=0
    results = {}

    for c in range(1, min(codim_check + 1, n - k)):
        w = n - k - c
        if w < 2 or w >= n:
            continue

        count_r0 = 0
        count_r01 = 0
        count_r012 = 0
        total = 0
        examples = []

        for E in itertools.combinations(range(n), w):
            total += 1
            sigma = elem_sym(E, L, p)
            remainder = companion_matrix_remainder(sigma, n, p)

            if remainder[0] == 1:
                count_r0 += 1
                if w >= 2 and remainder[1] == 0:
                    count_r01 += 1
                    if w >= 3 and remainder[2] == 0:
                        count_r012 += 1
                        if len(examples) < 3:
                            examples.append((E, sigma, remainder))

        results[c] = {
            'w': w,
            'total': total,
            'r0_eq_1': count_r0,
            'r0r1': count_r01,
            'r0r1r2': count_r012,
            'examples': examples,
        }

    return results

def main():
    print("=" * 70)
    print("V_{012} ∩ Σ intersection check")
    print("Does ANY w-subset of L satisfy r_0=1, r_1=0, r_2=0?")
    print("=" * 70)

    # Test parameters
    test_cases = [
        # (n, k, [primes])
        (6, 2, [7, 13, 31, 43, 67, 97]),
        (6, 3, [7, 13, 31, 43, 67, 97]),
        (8, 4, [17, 41, 73, 89, 97, 113]),
        (10, 5, [11, 31, 41, 61, 71, 101]),
        (12, 6, [13, 37, 61, 73, 97]),
        (14, 7, [29, 43, 71, 113]),
        (16, 8, [17, 97, 193]),
    ]

    for n, k, primes in test_cases:
        print(f"\n{'='*60}")
        print(f"RS[{n},{k}]  (rate {k/n:.2f})")
        print(f"{'='*60}")

        for p in primes:
            if p <= n:
                continue
            if (p - 1) % n != 0:
                continue

            results = check_v012_intersection(n, k, p)
            if results is None:
                continue

            for c, data in sorted(results.items()):
                w = data['w']
                status_r0 = f"r0=1: {data['r0_eq_1']}/{data['total']}"
                status_r01 = f"r0r1: {data['r0r1']}"
                status_r012 = f"r012: {data['r0r1r2']}"

                flag = ""
                if c >= 2 and data['r0r1'] > 0:
                    flag = " ⚠️"
                if c >= 3 and data['r0r1r2'] > 0:
                    flag = " 🚨"

                print(f"  p={p:>4d}, c={c}, w={w}: {status_r0}, {status_r01}, {status_r012}{flag}")

                if data['examples']:
                    for E, sigma, rem in data['examples'][:1]:
                        print(f"    EXAMPLE: E={E}, σ={sigma[:3]}..., r={rem[:4]}...")

    # Focus test: RS[8,4] across many primes
    print(f"\n{'='*60}")
    print("Focus: RS[8,4] across many primes (c=1,2,3)")
    print(f"{'='*60}")

    n, k = 8, 4
    for p in range(17, 500):
        if not is_prime(p):
            continue
        if (p - 1) % n != 0:
            continue

        results = check_v012_intersection(n, k, p, codim_check=3)
        if results is None:
            continue

        line = f"  p={p:>4d}: "
        parts = []
        for c in sorted(results.keys()):
            d = results[c]
            parts.append(f"c={c}(w={d['w']}): r0={d['r0_eq_1']}, r01={d['r0r1']}, r012={d['r0r1r2']}")
        print(line + " | ".join(parts))

def is_prime(n):
    if n < 2: return False
    for d in range(2, int(n**0.5)+1):
        if n % d == 0: return False
    return True

if __name__ == "__main__":
    main()
