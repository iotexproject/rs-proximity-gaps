"""
FRI Folding analysis with correct parameters from Note 0066.
Uses w = n - k - c where c is the number of compatibility conditions.

Parameters from Note 0066:
  n=12 k=6 w=4 c=2  (max M_actual=4 at p=13)
  n=14 k=7 w=5 c=2  (max M_actual=6 at p=29)
  n=16 k=8 w=5 c=3  (max M_actual=3 at p=17)
  n=18 k=9 w=6 c=3  (max M_actual=7 at p=19)
"""
import math, random
from itertools import combinations
from collections import Counter

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

def poly_eval(coeffs, x, p):
    v, xi = 0, 1
    for c in coeffs:
        v = (v + c * xi) % p
        xi = xi * x % p
    return v

def lagrange_interp(pts, vals, x, p):
    n = len(pts)
    r = 0
    for i in range(n):
        num, den = vals[i], 1
        for j in range(n):
            if i != j:
                num = num * (x - pts[j]) % p
                den = den * (pts[i] - pts[j]) % p
        r = (r + num * pow(den, p-2, p)) % p
    return r

def hdist(a, b, p):
    return sum(1 for x, y in zip(a, b) if (x-y)%p)

def fold_center(center, omega_pows, n, p, alpha):
    n2 = n // 2
    inv2 = pow(2, p-2, p)
    gc = []
    for i in range(n2):
        fi, fi2 = center[i], center[i + n2]
        fe = (fi + fi2) * inv2 % p
        inv_oi = pow(omega_pows[i], p-2, p)
        fo = (fi - fi2) * inv2 % p * inv_oi % p
        gc.append((fe + alpha * fo) % p)
    return gc

def fold_poly(co, alpha, cur_k, p):
    nk = cur_k // 2
    fc = []
    for j in range(nk):
        ce = co[2*j] if 2*j < len(co) else 0
        co2 = co[2*j+1] if 2*j+1 < len(co) else 0
        fc.append((ce + alpha * co2) % p)
    return fc

def johnson_w(n, k):
    return int(math.floor(n - math.sqrt(n * (k - 1))))


def find_list(center, omega, pw, n, k, w, p):
    """Find M_actual by enumerating w-subsets and checking compatibility."""
    codewords = {}

    for B_tuple in combinations(range(n), w):
        B = set(B_tuple)
        A = [i for i in range(n) if i not in B]

        if len(A) < k:
            continue

        # Interpolate on first k points
        x_pts = [pw[i] for i in A[:k]]
        y_pts = [center[i] for i in A[:k]]

        # Check remaining c = len(A) - k conditions
        ok = True
        for ci in range(k, len(A)):
            y_check = lagrange_interp(x_pts, y_pts, pw[A[ci]], p)
            if y_check != center[A[ci]]:
                ok = False
                break

        if not ok:
            continue

        # Get codeword coefficients
        # Solve Vandermonde
        coeffs = [lagrange_interp(x_pts, y_pts, pow(omega, 0, p) if j == 0
                                  else pow(omega, 0, p), p) for j in range(k)]
        # Actually, easier: evaluate at all n points
        vals = [lagrange_interp(x_pts, y_pts, pw[i], p) for i in range(n)]

        # Extract coefficients via DFT
        # c_j = (1/n) sum_i vals[i] * omega^{-ij}
        inv_n = pow(n, p-2, p)
        coeffs = []
        for j in range(k):
            cj = 0
            for i in range(n):
                cj = (cj + vals[i] * pow(pw[i], (p-1-j) * 1, p)) % p
                # Actually: omega^{-ij} = omega^{i*(n-j)} = pw[i]^{n-j}... no
                # omega^{-ij} = omega^{i*(p-1-j)}... no, that's modular inverse
                # omega^{-j} = omega^{n-j} since omega^n = 1
                pass
            # Redo: c_j = (1/n) sum_i vals[i] * omega^{-ij}
            cj = 0
            omega_neg_j = pow(omega, (n - j) % n, p) if j > 0 else 1
            x_power = 1
            for i in range(n):
                cj = (cj + vals[i] * x_power) % p
                x_power = x_power * omega_neg_j % p
            cj = cj * inv_n % p
            coeffs.append(cj)

        key = tuple(vals)
        if key not in codewords:
            d = hdist(vals, center, p)
            eset = frozenset(i for i in range(n) if (vals[i] - center[i]) % p)
            codewords[key] = (coeffs, vals, d, eset)

    return list(codewords.values())


def analyze(n, k, w, p_override=None):
    if p_override:
        p = p_override
        for g in range(2, p):
            x, seen = 1, set()
            for _ in range(p-1): seen.add(x); x = x*g%p
            if len(seen) == p-1:
                omega = pow(g, (p-1)//n, p); break
    else:
        p, omega = find_params(n)

    c = n - k - w
    n2, k2 = n//2, k//2
    w2_j = johnson_w(n2, k2)  # Johnson radius for folded code
    w2 = w // 2  # Naive: half the original w... but this is wrong
    # The folded code has rate rho' = k2/n2 = k/n = rho (same rate)
    # Johnson radius for RS[n2, k2]: floor(n2 - sqrt(n2*(k2-1)))
    w2 = w2_j
    c2 = n2 - k2 - w2

    pw = [pow(omega, i, p) for i in range(n)]
    pw2 = [pow(omega, 2*i, p) for i in range(n2)]

    print(f"\n{'='*60}")
    print(f"n={n} k={k} p={p} w={w} c={c}")
    print(f"Folded: n'={n2} k'={k2} w'_J={w2_j} c'={c2}")
    print(f"C(n,w)={math.comb(n,w)}")
    print(f"{'='*60}")

    # Search for best center
    random.seed(42)
    best_M, best_data = 0, None

    n_trials = 1000
    for trial in range(n_trials):
        center = [random.randrange(p) for _ in range(n)]
        cws = find_list(center, omega, pw, n, k, w, p)
        M = len(cws)
        if M > best_M:
            best_M = M
            best_data = (center, cws)
            print(f"  trial {trial}: NEW BEST M={M}", flush=True)

    print(f"\nBest M_actual = {best_M}")
    if best_M <= 1:
        print("  M too small for interesting folding analysis.\n")
        return

    center, cws = best_data
    inv2 = pow(2, p-2, p)

    # Error pairing
    print(f"\nError structure:")
    for idx, (co, va, d, eset) in enumerate(cws):
        E = set(eset)
        paired = sum(1 for i in E if (i + n//2) % n in E) // 2
        unp = len(E) - 2 * paired
        # Image size under squaring
        E_image = set(i % (n//2) for i in E)
        print(f"  cw{idx}: d={d} E={sorted(E)} p={paired} u={unp} "
              f"|E'|={len(E_image)}")

    # FRI folding
    max_test = min(p-1, 50)
    print(f"\nFRI folding ({max_test} alpha values):")

    survive_counts = []
    for alpha in range(1, max_test+1):
        gc = fold_center(center, pw, n, p, alpha)
        surv = 0
        for co, va, d, eset in cws:
            fc = fold_poly(co, alpha, k, p)
            fv = [poly_eval(fc, pw2[i], p) for i in range(n2)]
            df = hdist(fv, gc, p)
            if df <= w2:
                surv += 1
        survive_counts.append(surv)

    dist = Counter(survive_counts)
    print(f"  M' dist: {dict(sorted(dist.items()))}")
    print(f"  Mean={sum(survive_counts)/len(survive_counts):.3f} Max={max(survive_counts)}")

    # Per-codeword survival
    print(f"\nPer-codeword:")
    for idx, (co, va, d, eset) in enumerate(cws):
        E = set(eset)
        paired = sum(1 for i in E if (i+n//2)%n in E) // 2
        unp = len(E) - 2*paired
        E_im = set(i%(n//2) for i in E)
        cnt = 0
        for alpha in range(1, max_test+1):
            gc = fold_center(center, pw, n, p, alpha)
            fc = fold_poly(co, alpha, k, p)
            fv = [poly_eval(fc, pw2[i], p) for i in range(n2)]
            df = hdist(fv, gc, p)
            if df <= w2:
                cnt += 1
        need_cancel = len(E_im) - w2
        print(f"  cw{idx}: d={d} |E'|={len(E_im)} w'={w2} "
              f"need_cancel={max(0,need_cancel)} survive={cnt}/{max_test}")

    # Multi-round folding
    print(f"\nMulti-round (20 trials):")
    random.seed(777)
    for trial in range(20):
        cur_c = center[:]
        cur_list = [(co[:], va[:], d) for co, va, d, _ in cws]
        cur_n, cur_k = n, k
        cur_om = omega
        chain = [len(cur_list)]

        while cur_n >= 4 and cur_k >= 2 and len(cur_list) > 0:
            al = random.randrange(1, p)
            nn, nk = cur_n//2, cur_k//2
            if nk < 1: break
            nw = johnson_w(nn, nk)
            nom = pow(cur_om, 2, p)
            npw = [pow(nom, i, p) for i in range(nn)]

            nc = fold_center(cur_c, [pow(cur_om, i, p) for i in range(cur_n)],
                             cur_n, p, al)
            nl = []
            for co, va, d in cur_list:
                fc = fold_poly(co, al, cur_k, p)
                fv = [poly_eval(fc, npw[i], p) for i in range(nn)]
                df = hdist(fv, nc, p)
                if df <= nw:
                    nl.append((fc, fv, df))

            cur_c, cur_list = nc, nl
            cur_n, cur_k, cur_om = nn, nk, nom
            chain.append(len(cur_list))

        print(f"  trial {trial}: {chain}")


# Run with parameters matching Note 0066
analyze(12, 6, 4, p_override=13)
analyze(14, 7, 5, p_override=29)
analyze(16, 8, 5, p_override=17)
