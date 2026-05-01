"""
FRI Folding for n=14,16 — use Mactual approach (interpolation) instead of
full codeword enumeration. Much faster for larger n.

For each random center c_high:
1. Enumerate all w-subsets B of [n]
2. Check compatibility conditions
3. For compatible B, interpolate to get actual codeword
4. Count distinct codewords = M_actual
5. Analyze error pairing and folding survival
"""
import math, random
from itertools import combinations
from collections import Counter, defaultdict

def find_params(n):
    p = n + 1
    while True:
        if p % n == 1:
            ok = True
            for i in range(2, int(p**0.5)+1):
                if p % i == 0: ok = False; break
            if ok:
                for g in range(2, p):
                    x, seen = 1, set()
                    for _ in range(p-1): seen.add(x); x = x*g%p
                    if len(seen) == p-1:
                        return p, pow(g, (p-1)//n, p)
        p += n

def johnson_w(n, k):
    return int(math.floor(n - math.sqrt(n * (k - 1))))

def poly_eval(coeffs, x, p):
    v, xi = 0, 1
    for c in coeffs:
        v = (v + c * xi) % p
        xi = xi * x % p
    return v

def lagrange_interpolate(points, values, x_eval, p):
    """Evaluate the interpolating polynomial at x_eval."""
    n_pts = len(points)
    result = 0
    for i in range(n_pts):
        num, den = values[i], 1
        for j in range(n_pts):
            if i != j:
                num = num * (x_eval - points[j]) % p
                den = den * (points[i] - points[j]) % p
        result = (result + num * pow(den, p-2, p)) % p
    return result

def interpolate_poly(points, values, p, max_deg):
    """Get polynomial coefficients from point evaluations."""
    # Coefficients in monomial basis: use Newton or direct
    coeffs = []
    for d in range(max_deg):
        # Evaluate at x = 0, 1, 2, ... to get coefficients
        # Actually, just use lagrange to evaluate at standard points
        pass
    # Simpler: solve the Vandermonde system
    n = len(points)
    # Build matrix
    mat = []
    for i in range(n):
        row = []
        xi = 1
        for j in range(n):
            row.append(xi)
            xi = xi * points[i] % p
        mat.append(row)

    # Gaussian elimination
    mat_aug = [row + [values[i]] for i, row in enumerate(mat)]
    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if mat_aug[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        mat_aug[col], mat_aug[pivot] = mat_aug[pivot], mat_aug[col]
        inv = pow(mat_aug[col][col], p-2, p)
        for j in range(n + 1):
            mat_aug[col][j] = mat_aug[col][j] * inv % p
        for row in range(n):
            if row != col and mat_aug[row][col] != 0:
                factor = mat_aug[row][col]
                for j in range(n + 1):
                    mat_aug[row][j] = (mat_aug[row][j] - factor * mat_aug[col][j]) % p

    return [mat_aug[i][n] for i in range(n)]


def power_sum(B_elements, omega, j, p):
    """Compute p_j(B) = sum_{i in B} omega^{i*j} mod p."""
    return sum(pow(omega, i*j, p) for i in B_elements) % p


def run_case(n, k, p_target=None):
    if p_target:
        p = p_target
        for g in range(2, p):
            x, seen = 1, set()
            for _ in range(p-1): seen.add(x); x = x*g%p
            if len(seen) == p-1:
                omega = pow(g, (p-1)//n, p)
                break
    else:
        p, omega = find_params(n)

    w = johnson_w(n, k)
    n2, k2 = n//2, k//2
    w2 = johnson_w(n2, k2)
    c = n - k - w
    N = 1
    for i in range(w):
        N = N * (n - i) // (i + 1)

    print(f"\n{'='*60}")
    print(f"n={n} k={k} p={p} w={w} c={c} N=C({n},{w})={N}")
    print(f"Folded: n'={n2} k'={k2} w'={w2}")
    print(f"{'='*60}")

    pw = [pow(omega, i, p) for i in range(n)]

    # Determine compatibility conditions
    # The conditions are: certain power sums of B equal prescribed values
    # For the CS-style conditions at rate 1/2:
    # p_j(B) = c_j for j = k, k+1, ..., k+c-1 (the c conditions)

    # For testing: sample random c_high (the prescribed high coefficients)
    random.seed(42)
    best_M = 0
    best_data = None

    n_trials = 500

    for trial in range(n_trials):
        # Random center as a function on L
        center = [random.randrange(p) for _ in range(n)]

        # Compute syndromes of center: hat_c_j for j = k, ..., n-1
        # hat_c_j = (1/n) * sum_i c_i * omega^{-ij}
        # But for our purpose: we need to find codewords close to center

        # A codeword f at distance d from center has error e = center - f
        # with wt(e) = d. The high DFT coeffs of e equal those of center.

        # For each w-subset B, check if there exists a codeword f that
        # agrees with center outside B and is degree < k.
        # This is equivalent to: interpolate center on [n]\B gives degree < k.

        codewords = {}  # tuple(coeffs) -> (coeffs, vals, dist, error_set)

        for B_tuple in combinations(range(n), w):
            B = set(B_tuple)
            A = [i for i in range(n) if i not in B]

            # Interpolate center values on A to get degree < k polynomial
            # Agreement set has n - w = k + c points
            # We need the interpolating polynomial to have degree < k
            # This means the c "extra" conditions must be satisfied

            if len(A) < k:
                continue

            # Use first k points to interpolate, check remaining c
            x_pts = [pw[i] for i in A[:k]]
            y_pts = [center[i] for i in A[:k]]

            # Interpolate to get degree < k polynomial
            # Use Lagrange to evaluate at remaining c check points
            ok = True
            for check_idx in range(k, len(A)):
                x_check = pw[A[check_idx]]
                y_interp = lagrange_interpolate(x_pts, y_pts, x_check, p)
                if y_interp != center[A[check_idx]]:
                    ok = False
                    break

            if not ok:
                continue

            # Compatible B found! Get the codeword
            # Evaluate the interpolated polynomial at all points
            coeffs = interpolate_poly(x_pts, y_pts, p, k)
            vals = [poly_eval(coeffs, pw[i], p) for i in range(n)]

            # Verify distance
            d = sum(1 for i in range(n) if (vals[i] - center[i]) % p != 0)

            key = tuple(coeffs[:k])
            if key not in codewords:
                error_set = frozenset(i for i in range(n) if (vals[i] - center[i]) % p != 0)
                codewords[key] = (coeffs[:k], vals, d, error_set)

        M = len(codewords)
        if M > best_M:
            best_M = M
            best_data = (center, list(codewords.values()))
            if trial < 50 or M > best_M - 1:
                print(f"  trial {trial}: NEW BEST M={M}")

    print(f"\nBest M_actual = {best_M}")
    if best_M == 0:
        print("  No close codewords.")
        return

    center, cws = best_data

    # Error pairing analysis
    print(f"\nError structure (M={best_M}):")
    for idx, (co, va, d, eset) in enumerate(cws):
        E = set(eset)
        paired = sum(1 for i in E if (i + n//2) % n in E) // 2
        unp = len(E) - 2 * paired
        print(f"  cw{idx}: d={d} E={sorted(E)} paired={paired} unp={unp}")

    # FRI folding
    inv2 = pow(2, p-2, p)
    omega2 = pow(omega, 2, p)
    pw2 = [pow(omega, 2*i, p) for i in range(n2)]

    def do_fold_center(center, alpha):
        gc = []
        for i in range(n2):
            fi, fi2 = center[i], center[i + n2]
            fe = (fi + fi2) * inv2 % p
            inv_oi = pow(pw[i], p-2, p)
            fo = (fi - fi2) * inv2 % p * inv_oi % p
            gc.append((fe + alpha * fo) % p)
        return gc

    def do_fold_poly(co, alpha):
        nk = k // 2
        fc = []
        for j in range(nk):
            ce = co[2*j] if 2*j < len(co) else 0
            co2 = co[2*j+1] if 2*j+1 < len(co) else 0
            fc.append((ce + alpha * co2) % p)
        return fc

    def hdist(a, b):
        return sum(1 for x, y in zip(a, b) if (x - y) % p != 0)

    # Test all alpha values (if p is small enough)
    max_alpha = min(p - 1, 100)
    print(f"\nFRI folding ({max_alpha} alpha values):")

    survive_counts = []
    for alpha in range(1, max_alpha + 1):
        gc = do_fold_center(center, alpha)
        surv = 0
        for co, va, d, eset in cws:
            fc = do_fold_poly(co, alpha)
            fv = [poly_eval(fc, pw2[i], p) for i in range(n2)]
            df = hdist(fv, gc)
            if df <= w2:
                surv += 1
        survive_counts.append(surv)

    dist = Counter(survive_counts)
    print(f"  M' distribution: {dict(sorted(dist.items()))}")
    print(f"  Mean M' = {sum(survive_counts)/len(survive_counts):.3f}")
    print(f"  Max M' = {max(survive_counts)}")

    # Per-codeword survival
    if best_M <= 12:
        print(f"\nPer-codeword survival:")
        for idx, (co, va, d, eset) in enumerate(cws):
            E = set(eset)
            paired = sum(1 for i in E if (i + n//2) % n in E) // 2
            unp = len(E) - 2 * paired
            cnt = 0
            for alpha in range(1, max_alpha + 1):
                gc = do_fold_center(center, alpha)
                fc = do_fold_poly(co, alpha)
                fv = [poly_eval(fc, pw2[i], p) for i in range(n2)]
                df = hdist(fv, gc)
                if df <= w2:
                    cnt += 1
            print(f"  cw{idx}: d={d} p/u={paired}/{unp} "
                  f"survive={cnt}/{max_alpha}")

    # Multi-round folding
    print(f"\nMulti-round folding (20 trials):")
    random.seed(777)
    for trial in range(20):
        cur_c = center[:]
        cur_list = [(co[:], va[:], d) for co, va, d, _ in cws]
        cur_n, cur_k = n, k
        cur_om = omega
        chain = [len(cur_list)]

        while cur_n >= 4 and cur_k >= 2 and len(cur_list) > 0:
            al = random.randrange(1, p)
            nn, nk = cur_n // 2, cur_k // 2
            if nk < 1: break
            nw = johnson_w(nn, nk)
            nom = pow(cur_om, 2, p)
            npw = [pow(nom, i, p) for i in range(nn)]
            inv2_ = pow(2, p-2, p)

            nc = []
            for i in range(nn):
                fi, fi2 = cur_c[i], cur_c[i + nn]
                fe = (fi + fi2) * inv2_ % p
                inv_oi = pow(pow(cur_om, i, p), p-2, p)
                fo = (fi - fi2) * inv2_ % p * inv_oi % p
                nc.append((fe + al * fo) % p)

            nl = []
            for co, va, d in cur_list:
                nk2 = cur_k // 2
                fc = []
                for j in range(nk2):
                    ce = co[2*j] if 2*j < len(co) else 0
                    co2 = co[2*j+1] if 2*j+1 < len(co) else 0
                    fc.append((ce + al * co2) % p)
                fv = [poly_eval(fc, npw[i], p) for i in range(nn)]
                df = hdist(fv, nc)
                if df <= nw:
                    nl.append((fc, fv, df))

            cur_c, cur_list = nc, nl
            cur_n, cur_k, cur_om = nn, nk, nom
            chain.append(len(cur_list))

        print(f"  trial {trial}: M chain = {chain}")


# Run cases
run_case(14, 7)
run_case(16, 8)
