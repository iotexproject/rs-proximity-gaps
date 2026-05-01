"""
gap_resultant_full.py — Compute Res_{σ_w}(r₀-1, r_j) in FULL σ-space.

For w=3: resultants are in Z[σ₁, σ₂]. Check gcd(R₁, R₂).
If gcd = 1 → codim(V₀₁₂) ≥ 3 in A³ → GAP CLOSED for w=3.

Strategy:
1. Compute r₀, r₁, r₂ symbolically in Z[σ₁, σ₂, σ₃]
2. View as univariate in σ₃ with coefficients in Z[σ₁, σ₂]
3. Compute Sylvester determinant → resultant in Z[σ₁, σ₂]
4. Check gcd(Res₀₁, Res₀₂)
"""

# ---- Multivariate polynomial arithmetic over Z ----
# Representation: dict {(e₁, e₂, ...): coeff} with variable-length exponent tuples

def mp_zero():
    return {}

def mp_const(c, nvars=3):
    if c == 0: return {}
    return {tuple([0]*nvars): c}

def mp_var(idx, nvars=3):
    key = [0]*nvars
    key[idx] = 1
    return {tuple(key): 1}

def mp_add(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0: del r[k]
    return r

def mp_sub(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) - v
        if r[k] == 0: del r[k]
    return r

def mp_mul(f, g):
    r = {}
    for e1, c1 in f.items():
        for e2, c2 in g.items():
            key = tuple(a+b for a,b in zip(e1, e2))
            r[key] = r.get(key, 0) + c1 * c2
    # Clean zeros
    return {k: v for k, v in r.items() if v != 0}

def mp_scale(f, c):
    if c == 0: return {}
    return {k: v*c for k, v in f.items() if v*c != 0}

def mp_neg(f):
    return {k: -v for k, v in f.items()}

def mp_is_zero(f):
    return len(f) == 0

# ---- Compute r_i for w=3 in Z[σ₁, σ₂, σ₃] ----

def compute_ri_w3(n):
    """Compute [r₀, r₁, r₂] for w=3, Λ(x) = x³ - σ₁x² + σ₂x - σ₃.
    Returns polynomials in Z[σ₁, σ₂, σ₃] (indices 0,1,2).
    r₀ = coeff of x², r₁ = coeff of x, r₂ = constant.
    """
    s1 = mp_var(0, 3)  # σ₁
    s2 = mp_var(1, 3)  # σ₂
    s3 = mp_var(2, 3)  # σ₃

    # Companion matrix last column: [σ₃, -σ₂, σ₁]
    c0 = s3               # coeff of x⁰ in x³ mod Λ
    c1 = mp_neg(s2)       # coeff of x¹
    c2 = s1               # coeff of x²

    # State: [a₀, a₁, a₂] = coefficients of current power of x mod Λ
    # Initially x⁰ = 1: state = [1, 0, 0]
    state = [mp_const(1, 3), mp_zero(), mp_zero()]

    for step in range(n):
        top = state[2]  # coefficient of x²
        new0 = mp_mul(top, c0)
        new1 = mp_add(state[0], mp_mul(top, c1))
        new2 = mp_add(state[1], mp_mul(top, c2))
        state = [new0, new1, new2]

    # state[j] = coefficient of x^j in x^n mod Λ
    # r₀ = state[2], r₁ = state[1], r₂ = state[0]
    return state[2], state[1], state[0]


# ---- Extract univariate in σ₃ ----

def extract_univariate_s3(f):
    """View f ∈ Z[σ₁,σ₂,σ₃] as univariate in σ₃ with coeffs in Z[σ₁,σ₂].
    Returns dict {power_of_s3: poly_in_s1_s2}.
    Each poly_in_s1_s2 is dict {(e1,e2): coeff}.
    """
    result = {}
    for (e1, e2, e3), c in f.items():
        key2 = (e1, e2)
        if e3 not in result:
            result[e3] = {}
        result[e3][key2] = result[e3].get(key2, 0) + c
        if result[e3][key2] == 0:
            del result[e3][key2]
    # Clean empty
    return {k: v for k, v in result.items() if v}


# ---- Bivariate polynomial arithmetic Z[σ₁,σ₂] ----

def bp_zero():
    return {}

def bp_add(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0: del r[k]
    return r

def bp_sub(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) - v
        if r[k] == 0: del r[k]
    return r

def bp_mul(f, g):
    r = {}
    for e1, c1 in f.items():
        for e2, c2 in g.items():
            key = (e1[0]+e2[0], e1[1]+e2[1])
            r[key] = r.get(key, 0) + c1*c2
    return {k: v for k, v in r.items() if v != 0}

def bp_scale(f, c):
    if c == 0: return {}
    return {k: v*c for k, v in f.items() if v*c != 0}

def bp_neg(f):
    return {k: -v for k, v in f.items()}

def bp_is_zero(f):
    return len(f) == 0

def bp_degree(f):
    if not f: return -1
    return max(e1+e2 for (e1,e2) in f.keys())

def bp_total_terms(f):
    return len(f)


# ---- Sylvester matrix determinant (resultant) ----

def sylvester_det(F, G):
    """Compute Res_{σ₃}(F, G) where F, G are univariate in σ₃
    with coefficients in Z[σ₁,σ₂].
    F = {power: bp_coeff, ...}, G = {power: bp_coeff, ...}
    Returns resultant in Z[σ₁,σ₂].
    """
    deg_f = max(F.keys()) if F else 0
    deg_g = max(G.keys()) if G else 0
    n = deg_f + deg_g  # Sylvester matrix size

    if n == 0:
        return {(0,0): 1}

    # Build Sylvester matrix: deg_g rows from F, deg_f rows from G
    # Row i (0 ≤ i < deg_g): coefficients of σ₃^i · F, shifted
    # Row deg_g + j (0 ≤ j < deg_f): coefficients of σ₃^j · G, shifted

    mat = [[bp_zero() for _ in range(n)] for _ in range(n)]

    for i in range(deg_g):
        for power, coeff in F.items():
            col = i + (deg_f - power)  # column index
            if 0 <= col < n:
                mat[i][col] = bp_add(mat[i][col], coeff)

    for j in range(deg_f):
        for power, coeff in G.items():
            col = j + (deg_g - power)
            if 0 <= col < n:
                mat[deg_g + j][col] = bp_add(mat[deg_g + j][col], coeff)

    # Compute determinant by Leibniz formula (only feasible for small n)
    # For n ≤ 5, this is OK
    if n > 6:
        print(f"  WARNING: Sylvester matrix {n}x{n}, using cofactor expansion (slow)")

    return det_bp(mat, n)


def det_bp(mat, n):
    """Determinant of n×n matrix with entries in Z[σ₁,σ₂] by cofactor expansion."""
    if n == 1:
        return mat[0][0]
    if n == 2:
        return bp_sub(bp_mul(mat[0][0], mat[1][1]), bp_mul(mat[0][1], mat[1][0]))

    # Expand along first row
    result = bp_zero()
    for j in range(n):
        if bp_is_zero(mat[0][j]):
            continue
        # Minor: delete row 0, col j
        minor = []
        for i in range(1, n):
            row = []
            for k in range(n):
                if k != j:
                    row.append(mat[i][k])
            minor.append(row)
        sub_det = det_bp(minor, n-1)
        term = bp_mul(mat[0][j], sub_det)
        if j % 2 == 0:
            result = bp_add(result, term)
        else:
            result = bp_sub(result, term)
    return result


# ---- GCD of bivariate polynomials ----

def bp_eval_s2(f, val):
    """Evaluate f(σ₁, σ₂) at σ₂=val, getting univariate in σ₁."""
    result = {}
    for (e1, e2), c in f.items():
        coeff = c * (val ** e2)
        result[e1] = result.get(e1, 0) + coeff
    return {k: v for k, v in result.items() if v != 0}


def up_gcd_Z(f, g):
    """GCD of univariate polynomials over Z (content + primitive part).
    f, g: dict {power: coeff}.
    Returns monic GCD (approximately — over Z this is content * primitive GCD).
    """
    # Use subresultant or simple Euclidean for small cases
    # For checking coprimality, we just need to know if gcd has degree > 0
    # Strategy: evaluate at several points, check if univariate gcds are constant
    pass  # We'll use a different approach


def bp_specialize_line(f, a, b):
    """Evaluate f(σ₁, σ₂) at σ₂ = a + b·σ₁, getting univariate in σ₁.
    Returns dict {power_of_s1: coeff}.
    """
    # f = Σ c_{i,j} σ₁^i σ₂^j
    # σ₂ = a + b·σ₁ → σ₂^j = (a + b·σ₁)^j = Σ_k C(j,k) a^{j-k} b^k σ₁^k
    from math import comb
    result = {}
    for (e1, e2), c in f.items():
        # σ₁^{e1} · σ₂^{e2} = σ₁^{e1} · Σ_k C(e2,k) a^{e2-k} b^k σ₁^k
        for k in range(e2 + 1):
            power = e1 + k
            coeff = c * comb(e2, k) * (a ** (e2 - k)) * (b ** k)
            result[power] = result.get(power, 0) + coeff
    return {k: v for k, v in result.items() if v != 0}


def up_gcd_degree(f, g):
    """Degree of GCD of two univariate polynomials over Z.
    Uses Euclidean algorithm with pseudo-division.
    """
    if not f: return max(g.keys()) if g else -1
    if not g: return max(f.keys()) if f else -1

    def up_degree(h):
        return max(h.keys()) if h else -1

    def up_pseudo_rem(a, b):
        """Pseudo-remainder of a / b over Z."""
        da = up_degree(a)
        db = up_degree(b)
        if da < db: return a
        lc_b = b[db]
        a = dict(a)
        for _ in range(da - db + 1):
            da = up_degree(a)
            if da < db: break
            lc_a = a.get(da, 0)
            # a = lc_b * a - lc_a * x^{da-db} * b
            new_a = {}
            for k, v in a.items():
                new_a[k] = new_a.get(k, 0) + lc_b * v
            shift = da - db
            for k, v in b.items():
                new_a[k + shift] = new_a.get(k + shift, 0) - lc_a * v
            a = {k: v for k, v in new_a.items() if v != 0}
        return a

    while g and up_degree(g) >= 0:
        f, g = g, up_pseudo_rem(f, g)

    return up_degree(f)


def check_coprimality_bp(R1, R2, label=""):
    """Check if two bivariate polynomials are coprime by specializing σ₂ to various values."""
    print(f"  {label}: deg(R1)={bp_degree(R1)}, terms(R1)={bp_total_terms(R1)}")
    print(f"  {label}: deg(R2)={bp_degree(R2)}, terms(R2)={bp_total_terms(R2)}")

    # Method: specialize σ₂ → integer values and check GCD of univariate results
    # If gcd(R1, R2) has degree d in (σ₁, σ₂), then for generic σ₂=a,
    # gcd(R1(σ₁,a), R2(σ₁,a)) has degree ≥ d' > 0.
    # If all specializations give gcd degree 0 → coprime.

    gcd_degrees = []
    for a in range(-3, 4):
        u1 = bp_eval_s2(R1, a)
        u2 = bp_eval_s2(R2, a)
        d = up_gcd_degree(u1, u2)
        gcd_degrees.append((a, d))

    print(f"  {label}: gcd degrees at σ₂=a: {gcd_degrees}")

    max_gcd = max(d for _, d in gcd_degrees)
    if max_gcd <= 0:
        print(f"  {label}: *** COPRIME (all specializations give gcd degree ≤ 0) ***")
        return True
    else:
        # Also try random lines
        for (a, b) in [(1, 1), (2, 1), (1, 2), (3, 1)]:
            u1 = bp_specialize_line(R1, a, b)
            u2 = bp_specialize_line(R2, a, b)
            d = up_gcd_degree(u1, u2)
            gcd_degrees.append((f"line({a},{b})", d))
        print(f"  {label}: additional line specializations: {gcd_degrees[-4:]}")
        max_gcd2 = max(d for _, d in gcd_degrees)
        if max_gcd2 <= 0:
            print(f"  {label}: *** COPRIME (with line specializations) ***")
            return True
        else:
            print(f"  {label}: *** NOT COPRIME (max gcd degree = {max_gcd2}) ***")
            return False


def print_bp(f, name="f"):
    """Print bivariate polynomial."""
    if not f:
        print(f"    {name} = 0")
        return
    items = sorted(f.items(), key=lambda x: (-sum(x[0]), -x[0][0]))
    parts = []
    for (a, b), c in items[:20]:  # limit output
        vs = []
        if a > 0: vs.append(f"s1^{a}" if a > 1 else "s1")
        if b > 0: vs.append(f"s2^{b}" if b > 1 else "s2")
        var = "*".join(vs) if vs else "1"
        if c == 1 and vs: parts.append(f"+{var}")
        elif c == -1 and vs: parts.append(f"-{var}")
        elif c > 0: parts.append(f"+{c}*{var}")
        else: parts.append(f"{c}*{var}")
    s = " ".join(parts)
    if s.startswith("+"): s = s[1:]
    extra = f" ... (+{len(items)-20} more)" if len(items) > 20 else ""
    print(f"    {name} = {s}{extra}")


def main():
    print("=" * 70)
    print("FULL σ-SPACE RESULTANT: Res_{σ₃}(r₀-1, r_j) for w=3")
    print("=" * 70)

    for n in [7, 8, 10, 11, 13]:
        print(f"\n{'='*60}")
        print(f"n={n}, w=3 (w{'|' if n%3==0 else '∤'}n)")
        print(f"{'='*60}")

        print(f"  Computing r₀, r₁, r₂ in Z[σ₁,σ₂,σ₃]...")
        r0, r1, r2 = compute_ri_w3(n)

        # Print sizes
        print(f"  |r₀| = {len(r0)} terms, |r₁| = {len(r1)} terms, |r₂| = {len(r2)} terms")

        # Extract univariate in σ₃
        r0m1 = mp_sub(r0, mp_const(1, 3))  # r₀ - 1

        F = extract_univariate_s3(r0m1)
        G1 = extract_univariate_s3(r1)
        G2 = extract_univariate_s3(r2)

        deg_F = max(F.keys()) if F else 0
        deg_G1 = max(G1.keys()) if G1 else 0
        deg_G2 = max(G2.keys()) if G2 else 0

        print(f"  deg_σ₃(r₀-1) = {deg_F}")
        print(f"  deg_σ₃(r₁)   = {deg_G1}")
        print(f"  deg_σ₃(r₂)   = {deg_G2}")
        print(f"  Sylvester sizes: Res₀₁ = {deg_F+deg_G1}×{deg_F+deg_G1}, Res₀₂ = {deg_F+deg_G2}×{deg_F+deg_G2}")

        syl_size_1 = deg_F + deg_G1
        syl_size_2 = deg_F + deg_G2

        if syl_size_1 > 6 or syl_size_2 > 6:
            print(f"  SKIPPING: Sylvester matrix too large for cofactor expansion")
            continue

        print(f"  Computing Res₀₁ = Res_σ₃(r₀-1, r₁)...")
        R01 = sylvester_det(F, G1)
        print_bp(R01, "Res₀₁")

        print(f"  Computing Res₀₂ = Res_σ₃(r₀-1, r₂)...")
        R02 = sylvester_det(F, G2)
        print_bp(R02, "Res₀₂")

        # Check coprimality
        coprime = check_coprimality_bp(R01, R02, f"n={n}")

        # Also verify: restrict to bivariate (σ₂=0) matches known result
        R01_biv = bp_eval_s2(R01, 0)
        R02_biv = bp_eval_s2(R02, 0)
        d_biv = up_gcd_degree(R01_biv, R02_biv)
        print(f"  Bivariate check (σ₂=0): gcd degree = {d_biv}")


    # Also test w|n case
    print(f"\n{'='*60}")
    print(f"n=9, w=3 (w|n case)")
    print(f"{'='*60}")
    n = 9
    r0, r1, r2 = compute_ri_w3(n)
    print(f"  |r₀| = {len(r0)} terms, |r₁| = {len(r1)} terms, |r₂| = {len(r2)} terms")
    r0m1 = mp_sub(r0, mp_const(1, 3))
    F = extract_univariate_s3(r0m1)
    G1 = extract_univariate_s3(r1)
    G2 = extract_univariate_s3(r2)
    deg_F = max(F.keys()) if F else 0
    deg_G1 = max(G1.keys()) if G1 else 0
    deg_G2 = max(G2.keys()) if G2 else 0
    print(f"  deg_σ₃(r₀-1) = {deg_F}, deg_σ₃(r₁) = {deg_G1}, deg_σ₃(r₂) = {deg_G2}")
    syl1 = deg_F + deg_G1
    syl2 = deg_F + deg_G2
    if syl1 <= 6 and syl2 <= 6:
        R01 = sylvester_det(F, G1)
        R02 = sylvester_det(F, G2)
        print_bp(R01, "Res₀₁")
        print_bp(R02, "Res₀₂")
        check_coprimality_bp(R01, R02, "n=9")
    else:
        print(f"  SKIPPING: Sylvester {syl1}×{syl1} / {syl2}×{syl2}")


if __name__ == "__main__":
    main()
