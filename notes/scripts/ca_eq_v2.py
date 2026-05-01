"""
Equal-threshold CA test v2: heavily optimized.
Key insight: avoid O(|C|^2) joint dist by decomposing.

Δ_joint((f1,f2), C²) = min_{g1,g2} |supp(f1-g1) ∪ supp(f2-g2)| / n
                      = min_{g1} min_{g2} popcount(mask1[g1] | mask2[g2]) / n

For fixed g1: min_{g2} popcount(mask1[g1] | mask2[g2])
            = min_{g2} popcount(mask1[g1]) + popcount(mask2[g2] & ~mask1[g1])
            = popcount(mask1[g1]) + min_{g2} popcount(mask2[g2] & ~mask1[g1])

So: precompute for each "complement mask" the min-weight codeword error restricted to it.
This is still O(|C|^2) in worst case but with early termination.

Even simpler for tiny n: just use bitmask operations.
"""
import sys

def make_rs(n, k, p, omega):
    L = [pow(omega, i, p) for i in range(n)]
    cw = []
    coeffs_list = []
    # generate all k-tuples
    def gen(depth, acc):
        if depth == k:
            w = []
            for x in L:
                v, xi = 0, 1
                for c in acc:
                    v = (v + c * xi) % p
                    xi = xi * x % p
                w.append(v)
            cw.append(tuple(w))
            return
        for c in range(p):
            gen(depth + 1, acc + [c])
    gen(0, [])
    return L, cw

def find_prim_root(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) == 1:
            ok = True
            for d in range(1, n):
                if n % d == 0 and d < n and pow(w, d, p) == 1:
                    ok = False
                    break
            if ok:
                return w
    return None

def popcount(x):
    c = 0
    while x:
        c += 1
        x &= x - 1
    return c

def run_test(n, k, p, omega, w_thr):
    delta = w_thr / n
    delta_J = 1.0 - (k / n) ** 0.5
    print(f"RS[{n},{k}]/F_{p}  ω={omega}  ρ={k/n:.3f}  δ_J={delta_J:.4f}  δ={delta:.4f}  w={w_thr}", flush=True)
    if delta <= delta_J + 1e-9:
        print("  SKIP: not above Johnson\n", flush=True)
        return

    L, cw = make_rs(n, k, p, omega)
    NC = len(cw)
    print(f"  |C|={NC}", flush=True)

    # Precompute: for each word (as int), distance to code
    total = p ** n
    if total > 500000:
        print(f"  SKIP: p^n={total} too large\n", flush=True)
        return

    # Encode words as ints: w = sum w_j * p^j (little-endian in digits)
    def encode(word):
        r = 0
        for j in range(n-1, -1, -1):
            r = r * p + word[j]
        return r

    def decode(wint):
        w = []
        tmp = wint
        for _ in range(n):
            w.append(tmp % p)
            tmp //= p
        return w  # little-endian: w[j] = coeff of p^j

    # Precompute distance to code for all words
    dist = [n] * total
    for c in cw:
        ci = encode(c)
        dist[ci] = 0

    # For each word, compute its distance
    for wi in range(total):
        if dist[wi] == 0:
            continue
        w = decode(wi)
        best = n
        for c in cw:
            d = sum(1 for j in range(n) if w[j] != c[j])
            if d < best:
                best = d
                if best == 0:
                    break
        dist[wi] = best

    # Precompute codeword encodings
    cw_encoded = [encode(c) for c in cw]

    # For the joint distance optimization:
    # mask(f, g) = bitmask of positions where f[j] != g[j]
    # We compute masks on the fly.

    max_bad = 0
    max_info = None
    hist = {}
    n_tested = 0

    # Iterate over all f1
    for f1i in range(total):
        f1 = decode(f1i)

        # Precompute error masks of f1 vs each codeword
        masks1 = []
        for c in cw:
            mask = 0
            for j in range(n):
                if f1[j] != c[j]:
                    mask |= (1 << j)
            masks1.append(mask)

        # For each f2
        for f2i in range(total):
            f2 = decode(f2i)

            # Precompute error masks of f2 vs each codeword
            masks2 = []
            for c in cw:
                mask = 0
                for j in range(n):
                    if f2[j] != c[j]:
                        mask |= (1 << j)
                masks2.append(mask)

            # Compute min joint = min_{g1,g2} popcount(masks1[g1] | masks2[g2])
            min_jt = n + 1
            for m1 in masks1:
                pc1 = popcount(m1)
                if pc1 >= min_jt:
                    continue  # can't improve
                for m2 in masks2:
                    jt = popcount(m1 | m2)
                    if jt < min_jt:
                        min_jt = jt
                        if min_jt <= w_thr:
                            break
                if min_jt <= w_thr:
                    break

            if min_jt <= w_thr:
                continue  # Δ_joint ≤ δ, not a CA premise

            n_tested += 1

            # Count bad gammas
            bad = 0
            for gamma in range(p):
                fg = [0] * n
                for j in range(n):
                    fg[j] = (f1[j] + gamma * f2[j]) % p
                fg_i = encode(fg)
                if dist[fg_i] <= w_thr:
                    bad += 1

            hist[bad] = hist.get(bad, 0) + 1
            if bad > max_bad:
                max_bad = bad
                max_info = (f1, f2, min_jt, bad)
                print(f"  ★ NEW MAX: {bad} bad γ  f1={f1} f2={f2} Δjoint={min_jt}", flush=True)

        if (f1i + 1) % max(1, total // 20) == 0:
            pct = 100 * (f1i + 1) / total
            print(f"  [{pct:.0f}%] f1={f1i+1}/{total} tested={n_tested} max_bad={max_bad}", flush=True)

    print(f"\n  RESULT: max_bad_γ = {max_bad}  (over {n_tested} pairs with Δ_joint > δ)", flush=True)
    print(f"  Histogram: {dict(sorted(hist.items()))}", flush=True)
    if max_bad <= 2:
        print(f"  ✓ ε_ca(C,δ,δ) ≤ {max_bad}/{p} = O(1)/|F|  →  OP1 holds for this case!", flush=True)
    else:
        print(f"  ✗ max_bad = {max_bad} — potential obstruction to OP1", flush=True)
    print(flush=True)
    return max_bad


if __name__ == "__main__":
    print("=" * 60, flush=True)
    print("EQUAL-THRESHOLD CA: ε_ca(C, δ, δ) EXHAUSTIVE TEST", flush=True)
    print("=" * 60, flush=True)

    results = []

    # RS[4,2]/F_5: n=4,k=2,ρ=1/2,δ_J≈0.293,δ=1/2(w=2)
    w = find_prim_root(5, 4)
    if w:
        r = run_test(4, 2, 5, w, 2)
        results.append(("RS[4,2]/F_5", r))

    # RS[4,2]/F_13
    w = find_prim_root(13, 4)
    if w:
        r = run_test(4, 2, 13, w, 2)
        results.append(("RS[4,2]/F_13", r))

    # RS[6,3]/F_7: n=6,k=3,ρ=1/2,δ_J≈0.293,δ=1/2(w=3)
    w = find_prim_root(7, 6)
    if w:
        r = run_test(6, 3, 7, w, 3)
        results.append(("RS[6,3]/F_7", r))

    # RS[4,2]/F_29
    w = find_prim_root(29, 4)
    if w:
        r = run_test(4, 2, 29, w, 2)
        results.append(("RS[4,2]/F_29", r))

    print("\n" + "=" * 60, flush=True)
    print("SUMMARY", flush=True)
    print("=" * 60, flush=True)
    for name, r in results:
        status = "✓ O(1)/|F|" if r is not None and r <= 2 else ("✗ LARGE" if r is not None else "SKIPPED")
        rval = r if r is not None else "?"
        print(f"  {name}: max_bad_γ = {rval}  {status}", flush=True)
