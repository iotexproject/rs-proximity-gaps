"""
Verify: for valid error sets (Λ splits over L), x^n mod Λ = ?

Key claim: if all roots of Λ are in L = {n-th roots of unity}, then x^n ≡ 1 mod Λ.
Proof: each root ζ ∈ L satisfies ζ^n = 1, so (x^n - 1) vanishes at all roots → Λ | (x^n - 1) → x^n ≡ 1 mod Λ.

If this is true, then V_{012} = V(r_0-1, r_1, r_2) with r_0 = coeff of x^{w-1}
NEVER contains valid error sets (since R(x)=1 has r_0=0).

This would mean M = |Σ ∩ V(r_0-1, ..., r_{w-1})| depends on which convention is used for r_0.
"""

def find_primitive_root(n, p):
    if (p - 1) % n != 0: return None
    for g in range(2, p):
        omega = pow(g, (p-1)//n, p)
        if pow(omega, n, p) == 1:
            ok = all(pow(omega, d, p) != 1 for d in range(1, n) if n % d == 0 and d < n)
            if ok: return omega
    return None

def poly_mod(dividend_coeffs, divisor_coeffs, p):
    """Compute dividend mod divisor over F_p.
    Coefficients: [a_0, a_1, ...] for a_0 + a_1 x + a_2 x^2 + ...
    divisor must be monic (leading coeff = 1).
    Returns remainder coefficients."""
    d = list(dividend_coeffs)
    w = len(divisor_coeffs) - 1  # degree of divisor
    deg_d = len(d) - 1

    while len(d) > w:
        if d[-1] != 0:
            coeff = d[-1]
            deg = len(d) - 1
            for i in range(w + 1):
                d[deg - w + i] = (d[deg - w + i] - coeff * divisor_coeffs[i]) % p
        d.pop()

    # Pad to length w
    while len(d) < w:
        d.append(0)

    return d  # [r_const, r_x, r_x2, ..., r_{x^{w-1}}]

def companion_remainder(sigma, n, p):
    """Companion matrix method: state[0]=coeff of x^{w-1}, ..., state[w-1]=const."""
    w = len(sigma)
    state = [0] * w
    state[w-1] = 1  # x^0 = 1

    for _ in range(n):
        top = state[0]
        new_state = [0] * w
        for j in range(w - 1):
            new_state[j] = state[j + 1]
        for i in range(w):
            sign = (-1) ** (i + 1)
            new_state[i] = (new_state[i] + top * sign * sigma[i]) % p
        state = new_state

    return state  # [coeff of x^{w-1}, ..., const]

def test_basic():
    """Test with RS[10,5] over F_11, E = {5, 10, 7, 6}."""
    n, p = 10, 11
    omega = find_primitive_root(n, p)
    print(f"Primitive {n}-th root mod {p}: ω = {omega}")

    L = [pow(omega, i, p) for i in range(n)]
    print(f"L = {L}")

    # Error set by INDEX
    E_idx = (4, 5, 7, 9)
    E_elems = [L[i] for i in E_idx]
    print(f"E (indices) = {E_idx}")
    print(f"E (elements) = {E_elems}")

    # Verify elements are n-th roots of unity
    for e in E_elems:
        print(f"  {e}^{n} mod {p} = {pow(e, n, p)}")

    # Build Λ(x) = ∏(x - e_i) as coefficient list [a_0, a_1, ..., a_w]
    # a_0 + a_1 x + ... + a_w x^w
    w = len(E_elems)
    coeffs = [1]  # start with constant 1
    for e in E_elems:
        # Multiply by (x - e)
        new_coeffs = [0] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            new_coeffs[i + 1] = (new_coeffs[i + 1] + c) % p  # c * x
            new_coeffs[i] = (new_coeffs[i] - e * c) % p       # -e * c
        coeffs = new_coeffs
    print(f"Λ(x) coefficients (low to high): {coeffs}")
    # Verify monic
    assert coeffs[-1] == 1, f"Not monic: leading = {coeffs[-1]}"

    # Elementary symmetric polynomials
    sigma = []
    for j in range(1, w + 1):
        # σ_j = (-1)^j * coeffs[w-j] (Vieta's)
        # Actually: Λ(x) = x^w - σ_1 x^{w-1} + σ_2 x^{w-2} - ... + (-1)^w σ_w
        # So coefficient of x^{w-j} in Λ is (-1)^j σ_j
        # In our array: coeffs[w-j] = (-1)^j σ_j
        sigma_j = ((-1)**j * coeffs[w - j]) % p
        sigma.append(sigma_j)
    print(f"σ = (σ_1,...,σ_w) = {sigma}")

    # Method 1: Direct polynomial modular arithmetic
    # x^n as coefficients
    xn = [0] * (n + 1)
    xn[n] = 1

    remainder_direct = poly_mod(xn, coeffs, p)
    print(f"\nMethod 1 (direct poly mod):")
    print(f"  x^{n} mod Λ = {remainder_direct}")
    print(f"  = {remainder_direct[0]} + {remainder_direct[1]}x + {remainder_direct[2]}x^2 + {remainder_direct[3]}x^3")

    # Method 2: Companion matrix
    remainder_companion = companion_remainder(sigma, n, p)
    print(f"\nMethod 2 (companion matrix):")
    print(f"  state = {remainder_companion}")
    print(f"  = {remainder_companion[3]} + {remainder_companion[2]}x + {remainder_companion[1]}x^2 + {remainder_companion[0]}x^3")

    # Verify: R(ζ) should equal ζ^n = 1 for each root ζ
    print(f"\nVerification: R(ζ) should equal ζ^n = 1:")
    for e in E_elems:
        # Using direct remainder
        Rval = sum(remainder_direct[i] * pow(e, i, p) for i in range(w)) % p
        print(f"  R({e}) = {Rval}  (should be {pow(e, n, p)})")

    # Check claim: x^n mod Λ = 1
    is_one = remainder_direct == [1, 0, 0, 0]  # const=1, others=0
    print(f"\nx^{n} mod Λ = 1? {is_one}")
    print(f"Direct remainder: {remainder_direct}")

    # Compare conventions
    print(f"\nConvention comparison:")
    print(f"  Direct (low-to-high): {remainder_direct}")
    print(f"  Companion (high-to-low): {remainder_companion}")
    print(f"  Reversed companion: {list(reversed(remainder_companion))}")

def test_many():
    """Test for all w-subsets at various (n,p)."""
    cases = [
        (6, 2, 7), (6, 2, 13), (8, 4, 17), (8, 4, 41),
        (10, 5, 11), (10, 5, 31),
    ]

    for n, k, p in cases:
        omega = find_primitive_root(n, p)
        if omega is None: continue
        L = [pow(omega, i, p) for i in range(n)]

        for c in range(1, min(4, n-k)):
            w = n - k - c
            if w < 2: continue

            import itertools
            count_valid = 0  # R(x) = 1
            count_r0_lead_1 = 0  # leading coefficient of R = 1
            count_r0_const_1 = 0  # constant of R = 1

            for E in itertools.combinations(range(n), w):
                elems = [L[i] for i in E]
                sigma = []
                # Build Λ
                coeffs = [1]
                for e in elems:
                    new_coeffs = [0] * (len(coeffs) + 1)
                    for i, cc in enumerate(coeffs):
                        new_coeffs[i+1] = (new_coeffs[i+1] + cc) % p
                        new_coeffs[i] = (new_coeffs[i] - e * cc) % p
                    coeffs = new_coeffs

                # Direct remainder
                xn = [0] * (n + 1)
                xn[n] = 1
                rem = poly_mod(xn, coeffs, p)

                # Check R(x) = 1
                is_one = (rem[0] == 1) and all(rem[j] == 0 for j in range(1, w))
                if is_one: count_valid += 1

                # Check leading coeff = 1 (rem[w-1] = 1)
                if rem[w-1] == 1: count_r0_lead_1 += 1

                # Check constant = 1 (rem[0] = 1)
                if rem[0] == 1: count_r0_const_1 += 1

            import math
            total = math.comb(n, w)
            print(f"RS[{n},{k}] p={p}, c={c}, w={w}: "
                  f"R(x)=1: {count_valid}/{total}, "
                  f"lead=1: {count_r0_lead_1}, "
                  f"const=1: {count_r0_const_1}")

if __name__ == "__main__":
    test_basic()
    print("\n" + "="*60)
    print("Testing many cases:")
    print("="*60)
    test_many()
