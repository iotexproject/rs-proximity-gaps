"""
FRI Folding for n=12, k=6, p=13, with CORRECT Johnson radius w=4.
Also test n=12 with larger primes to get higher M.
"""
import math, random
from itertools import product as iprod
from collections import Counter

def johnson_w(n, k):
    """Correct Johnson radius for MDS codes: w = floor(n - sqrt(n(k-1)))."""
    return int(math.floor(n - math.sqrt(n * (k - 1))))

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

def eval_poly(co, points, p):
    vals = []
    for x in points:
        v, xi = 0, 1
        for c in co:
            v = (v + c*xi) % p; xi = xi*x%p
        vals.append(v)
    return vals

def hdist(a, b, p):
    return sum(1 for x,y in zip(a,b) if (x-y)%p)

def fold_center(center, omega, n, p, alpha):
    n2 = n//2
    inv2 = pow(2, p-2, p)
    gc = []
    for i in range(n2):
        fi, fi2 = center[i], center[i+n2]
        fe = (fi + fi2) * inv2 % p
        inv_oi = pow(pow(omega, i, p), p-2, p)
        fo = (fi - fi2) * inv2 % p * inv_oi % p
        gc.append((fe + alpha*fo) % p)
    return gc

def fold_poly(co, alpha, cur_k, p):
    nk = cur_k // 2
    fc = []
    for j in range(nk):
        ce = co[2*j] if 2*j < len(co) else 0
        co2 = co[2*j+1] if 2*j+1 < len(co) else 0
        fc.append((ce + alpha * co2) % p)
    return fc

def run_case(n, k, p_override=None):
    if p_override:
        p = p_override
        # Find omega
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
    c = n - k - w  # number of conditions

    print(f"\n{'='*60}")
    print(f"n={n} k={k} p={p} omega={omega} w={w} c={c}")
    print(f"Folded: n'={n2} k'={k2} w'={w2}")
    print(f"Search: {p}^{k} = {p**k}")
    print(f"{'='*60}")

    pw = [pow(omega, i, p) for i in range(n)]
    pw2 = [pow(omega, 2*i, p) for i in range(n2)]

    # Build all codewords
    print("Building codewords...", flush=True)
    all_cws = []
    cnt = 0
    for ct in iprod(range(p), repeat=k):
        vals = eval_poly(list(ct), pw, p)
        all_cws.append((list(ct), vals))
        cnt += 1
        if cnt % 1000000 == 0:
            print(f"  {cnt}/{p**k}", flush=True)
    print(f"  Done: {len(all_cws)}")

    # Search for best center
    print("Searching for high-M centers...", flush=True)
    random.seed(42)
    best_M, best_data = 0, None

    n_trials = 200
    for trial in range(n_trials):
        center = [random.randrange(p) for _ in range(n)]
        close = []
        for co, vals in all_cws:
            d = hdist(vals, center, p)
            if d <= w:
                close.append((co, vals, d))
        M = len(close)
        if M > best_M:
            best_M = M
            best_data = (center, close)
            print(f"  trial {trial}: NEW BEST M={M}")

    print(f"\nBest M_actual = {best_M}")
    if best_M == 0:
        print("  No close codewords.")
        return

    center, cws = best_data

    # Error pairing
    print(f"\nError structure (M={best_M}):")
    for idx, (co, va, d) in enumerate(cws):
        E = {i for i in range(n) if (va[i]-center[i])%p}
        paired = sum(1 for i in E if (i+n//2)%n in E) // 2
        unp = len(E) - 2*paired
        # Check if E is union of pairs {i, i+n/2}
        is_paired = (unp == 0)
        print(f"  cw{idx}: d={d} E={sorted(E)} paired={paired} unp={unp} "
              f"{'FULLY PAIRED' if is_paired else ''}")

    # FRI folding: ALL alpha
    print(f"\nFRI folding (all {p-1} alphas):")

    survive_data = {}
    for alpha in range(1, p):
        gc = fold_center(center, omega, n, p, alpha)
        survs = []
        for idx, (co, va, d) in enumerate(cws):
            fc = fold_poly(co, alpha, k, p)
            fv = eval_poly(fc, pw2, p)
            df = hdist(fv, gc, p)
            if df <= w2:
                survs.append((idx, df))
        survive_data[alpha] = survs

    scounts = [len(v) for v in survive_data.values()]
    dist = Counter(scounts)
    print(f"  M' distribution: {dict(sorted(dist.items()))}")
    print(f"  Mean M' = {sum(scounts)/len(scounts):.3f}")
    print(f"  Max M' = {max(scounts)}")
    frac_zero = scounts.count(0) / len(scounts)
    print(f"  Fraction with M'=0: {frac_zero:.3f}")

    # Per-codeword survival
    if best_M <= 10:
        print(f"\nPer-codeword survival:")
        for idx, (co, va, d) in enumerate(cws):
            E = {i for i in range(n) if (va[i]-center[i])%p}
            paired = sum(1 for i in E if (i+n//2)%n in E) // 2
            unp = len(E) - 2*paired
            cnt2 = sum(1 for a in range(1, p)
                       if any(i2==idx for i2,_ in survive_data[a]))
            print(f"  cw{idx}: d={d} p/u={paired}/{unp} "
                  f"survive={cnt2}/{p-1} ({100*cnt2/(p-1):.1f}%)")

    # Multi-round folding
    print(f"\nMulti-round folding (20 trials):")
    random.seed(777)
    for trial in range(20):
        cur_c = center[:]
        cur_list = [(co[:], va[:], d) for co, va, d in cws]
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

            nc = fold_center(cur_c, cur_om, cur_n, p, al)
            nl = []
            for co, va, d in cur_list:
                fc = fold_poly(co, al, cur_k, p)
                fv = eval_poly(fc, npw, p)
                df = hdist(fv, nc, p)
                if df <= nw:
                    nl.append((fc, fv, df))

            cur_c, cur_list = nc, nl
            cur_n, cur_k, cur_om = nn, nk, nom
            chain.append(len(cur_list))

        print(f"  trial {trial}: M chain = {chain}")

    # Check if folded list contains NON-surviving codewords
    print(f"\nFolded list vs survivors (alpha=1):")
    alpha = 1
    gc = fold_center(center, omega, n, p, alpha)
    # Build all RS[n2, k2] codewords
    all_cws2 = []
    for ct in iprod(range(p), repeat=k2):
        vals = eval_poly(list(ct), pw2, p)
        all_cws2.append((list(ct), vals))

    folded_close = []
    for co2, v2 in all_cws2:
        d2 = hdist(v2, gc, p)
        if d2 <= w2:
            folded_close.append((co2, v2, d2))

    print(f"  Full folded list (RS[{n2},{k2}] at w'={w2}): M_fold={len(folded_close)}")
    print(f"  Survivors from original: {len(survive_data.get(alpha, []))}")

    # Check which folded codewords come from original list
    for co2, v2, d2 in folded_close:
        # Check if this is a fold of any original codeword
        is_fold = False
        for idx, (co, va, d) in enumerate(cws):
            fc = fold_poly(co, alpha, k, p)
            if fc == co2:
                is_fold = True
                print(f"    h={co2} d'={d2}: fold of cw{idx}")
                break
        if not is_fold:
            print(f"    h={co2} d'={d2}: NOT from original list!")


# Run cases
run_case(12, 6)  # p=13, w=4

