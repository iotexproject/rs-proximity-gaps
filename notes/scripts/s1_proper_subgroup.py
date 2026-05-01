"""
S1 — CS-line sweep with PROPER multiplicative subgroups (n << p-1).

Key difference from cs_sweep_fast.py:
  - For each n, use multiple primes p where n | (p-1) but n != p-1.
  - For k=2: Lagrange-pair trick (enumerate pairs → deduce h → count agreement).
    Cost: O(p * n^2 * n) instead of O(p * p^2 * n). Huge win when p >> n.
  - Parallelized across lambda with multiprocessing.

Usage: python3 s1_proper_subgroup.py
"""
import sys
from math import gcd
from multiprocessing import Pool, cpu_count
from collections import defaultdict

# --------------- number theory helpers ---------------

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0: return False
        d += 6
    return True

def prime_factors(n):
    out = set(); d = 2; nn = n
    while d * d <= nn:
        while nn % d == 0: out.add(d); nn //= d
        d += 1
    if nn > 1: out.add(nn)
    return list(out)

def find_primes_with_subgroup(n, count=3, min_ratio=2):
    """Find primes p where n | (p-1) and (p-1)/n >= min_ratio."""
    primes = []
    cand = n * min_ratio + 1  # start from p-1 = n * min_ratio
    # align to p ≡ 1 (mod n)
    cand = cand + (-cand % n) + 1 if cand % n != 1 else cand
    # scan upward
    p = n + 1  # start at 2n+1
    while len(primes) < count:
        p += n
        if is_prime(p) and (p - 1) // n >= min_ratio:
            primes.append(p)
    return primes

def find_omega(p, n, n_factors):
    """Find element of order exactly n in F_p*."""
    # g = primitive root, omega = g^((p-1)/n)
    for g in range(2, p):
        if pow(g, (p - 1) // 2, p) == 1:
            continue
        # check g is primitive root (order p-1)
        ok = True
        for q in prime_factors(p - 1):
            if pow(g, (p - 1) // q, p) == 1:
                ok = False; break
        if ok:
            omega = pow(g, (p - 1) // n, p)
            # verify order is exactly n
            assert pow(omega, n, p) == 1
            for q in n_factors:
                assert pow(omega, n // q, p) != 1
            return omega
    raise RuntimeError(f"no primitive root mod {p}")

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

def cosets_of_index_subgroup(n, d):
    """Cosets of the unique subgroup of order d in Z/nZ."""
    step = n // d
    H = [(i * step) % n for i in range(d)]
    seen = set(); out = []
    for t in range(step):
        c = tuple(sorted((t + h) % n for h in H))
        if c not in seen: seen.add(c); out.append(c)
    return out

def is_subgroup_aligned(S_set, n):
    """Check if S is a union of cosets of some subgroup of Z/nZ."""
    for d in divisors(n):
        if d == 1 or d == n: continue
        if len(S_set) % d != 0: continue
        cs = cosets_of_index_subgroup(n, d)
        covered = [c for c in cs if set(c).issubset(S_set)]
        if covered and sum(len(c) for c in covered) == len(S_set):
            return d
    return None

def decompose_alignment(S_set, n):
    """Find the largest subgroup-coset part and the residue."""
    best_d = None; best_covered = []
    for d in divisors(n):
        if d == 1 or d == n: continue
        cs = cosets_of_index_subgroup(n, d)
        covered = [c for c in cs if set(c).issubset(S_set)]
        cov_size = sum(len(c) for c in covered)
        if cov_size > 0 and (best_d is None or cov_size > sum(len(c) for c in best_covered)):
            best_d = d; best_covered = covered
    if best_d is None:
        return None, S_set
    coset_part = set()
    for c in best_covered: coset_part.update(c)
    residue = S_set - coset_part
    return best_d, residue

# --------------- core sweep (k=2, Lagrange trick) ---------------

def modinv(a, p):
    return pow(a, p - 2, p)

def sweep_one_lambda_k2(args):
    """For one value of lambda, find all (h0,h1) with agreement >= threshold."""
    lam, L, target, n, p, threshold = args
    # target[i] = (f + lam*g)(L[i]) mod p
    # For each pair (i,j), compute unique (h0,h1) and count agreement
    seen_h = {}  # (h0, h1) -> agreement set (as list of indices)
    for i in range(n):
        for j in range(i + 1, n):
            dx = (L[i] - L[j]) % p
            dy = (target[i] - target[j]) % p
            h1 = (dy * modinv(dx, p)) % p
            h0 = (target[i] - h1 * L[i]) % p
            key = (h0, h1)
            if key in seen_h:
                continue  # already checked
            # count agreement
            agree = []
            for idx in range(n):
                val = (h0 + h1 * L[idx]) % p
                if val == target[idx]:
                    agree.append(idx)
            seen_h[key] = agree

    bad = []
    for (h0, h1), agree in seen_h.items():
        if len(agree) >= threshold:
            bad.append((lam, (h0, h1), tuple(agree)))
    return bad

# --------------- main experiment ---------------

def run_case(n, m, s, r, p):
    """Run CS-line sweep for given parameters with a specific prime p."""
    k = (r - 2) * m
    if k < 1: return None
    delta = 1 - r / s
    if delta <= 0: return None
    threshold = r * m  # agreement = |S| = rm, S ⊂ L of size n

    nf = prime_factors(n)
    omega = find_omega(p, n, nf)
    L = [pow(omega, i, p) for i in range(n)]

    # precompute f, g on L
    f_vals = [pow(x, r * m, p) for x in L]
    g_vals = [pow(x, (r - 1) * m, p) for x in L]

    if k == 2:
        # Lagrange-pair trick: parallel across lambda
        tasks = []
        for lam in range(p):
            target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
            tasks.append((lam, L, target, n, p, threshold))

        ncpu = min(cpu_count(), 8)
        with Pool(ncpu) as pool:
            results = pool.map(sweep_one_lambda_k2, tasks, chunksize=max(1, p // (ncpu * 4)))

        bad = []
        for batch in results:
            bad.extend(batch)
    else:
        # For k >= 3, fall back to brute-force (only feasible for small p)
        from itertools import product as iprod
        bad = []
        for lam in range(p):
            target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
            for hc in iprod(range(p), repeat=k):
                agree = []
                for i in range(n):
                    hv = 0; xpw = 1
                    for j in range(k):
                        hv = (hv + hc[j] * xpw) % p
                        xpw = (xpw * L[i]) % p
                    if hv == target[i]:
                        agree.append(i)
                if len(agree) >= threshold:
                    bad.append((lam, hc, tuple(agree)))

    # analyze
    aligned = 0; not_aligned_list = []
    for lam, hc, S in bad:
        if is_subgroup_aligned(set(S), n) is not None:
            aligned += 1
        else:
            not_aligned_list.append((lam, hc, S))

    n_lam = len(set(w[0] for w in bad))
    ratio_str = f"{(p-1)//n}" if (p - 1) % n == 0 else "?"
    print(f"  p={p:<5} [(p-1)/n={ratio_str:<3}] | "
          f"#lam={n_lam:<4} #wits={len(bad):<6} #aligned={aligned:<6} #NOT={len(not_aligned_list)}",
          flush=True)

    if not_aligned_list:
        for lam, hc, S in not_aligned_list[:3]:
            d_info, residue = decompose_alignment(set(S), n)
            res_sorted = sorted(residue)
            # normalize residue: translate to start at 0
            if res_sorted:
                base = res_sorted[0]
                shape = tuple((x - base) % n for x in res_sorted)
            else:
                shape = ()
            print(f"       ex: lam={lam} S={S}  coset_d={d_info} residue={res_sorted} shape={shape}",
                  flush=True)
        if len(not_aligned_list) > 3:
            # collect all shapes
            shapes = defaultdict(int)
            for _, _, S in not_aligned_list:
                _, residue = decompose_alignment(set(S), n)
                rs = sorted(residue)
                if rs:
                    base = rs[0]
                    shape = tuple((x - base) % n for x in rs)
                    shapes[shape] += 1
            print(f"       shape distribution ({len(not_aligned_list)} non-aligned):", flush=True)
            for shape, cnt in sorted(shapes.items(), key=lambda x: -x[1]):
                print(f"         {shape}: {cnt}", flush=True)

    return len(bad), aligned, len(not_aligned_list)

# --------------- experiment plan ---------------

# n values to test; for each, pick 2-3 primes with proper subgroup
TEST_NS = [24, 36, 48, 60, 72, 96, 120]
M_VAL = 2  # focus on m=2 (k=2, Lagrange trick)
R_VAL = 3  # r=3 (as in existing sweep)

def main():
    print("=" * 100)
    print("S1 — Proper multiplicative subgroup sweep (n ∤ p-1 degenerate case excluded)")
    print(f"Parameters: m={M_VAL}, r={R_VAL}, k={(R_VAL-2)*M_VAL}")
    print(f"Cores available: {cpu_count()}")
    print("=" * 100)

    grand_total = grand_aligned = grand_not = 0

    for n in TEST_NS:
        s = n // M_VAL
        if n % M_VAL != 0: continue
        if s <= R_VAL: continue  # need delta > 0
        delta = 1 - R_VAL / s
        threshold = R_VAL * M_VAL

        # also run the "full group" case (n = p-1) for comparison
        full_p = n + 1
        while not is_prime(full_p):
            full_p += n
        full_is_degenerate = (full_p - 1 == n)

        # find proper-subgroup primes
        proper_primes = find_primes_with_subgroup(n, count=3, min_ratio=2)

        print(f"\n--- n={n}, m={M_VAL}, s={s}, r={R_VAL}, delta={delta:.3f}, threshold={threshold} ---",
              flush=True)

        # full group baseline (if applicable)
        if full_is_degenerate:
            print(f"  [BASELINE: n=p-1, full group]", flush=True)
            res = run_case(n, M_VAL, s, R_VAL, full_p)
            if res:
                grand_total += res[0]; grand_aligned += res[1]; grand_not += res[2]

        # proper subgroup cases
        for pp in proper_primes:
            res = run_case(n, M_VAL, s, R_VAL, pp)
            if res:
                grand_total += res[0]; grand_aligned += res[1]; grand_not += res[2]

    print("\n" + "=" * 100)
    print(f"GRAND TOTAL: {grand_total} witnesses, {grand_aligned} aligned, {grand_not} NOT aligned")
    print("=" * 100)

if __name__ == "__main__":
    main()
