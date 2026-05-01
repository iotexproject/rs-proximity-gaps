"""
Sweep multiple (n, m, s, r) parameter sets to test:

Conjecture 4 (Note 0002): every bad agreement set in CS-style proximity-gap
failure aligns with cosets of a multiplicative subgroup of L.

For each parameter set, we enumerate all lambda in F_p, find every
witness h of degree < k achieving >= (1-delta)n agreement with f + lambda*g,
extract S = agreement set, and check coset-alignment.

Output: tally of subgroup-aligned vs non-aligned witnesses across the sweep.
"""

from itertools import product

def find_omega(p, n, n_factors):
    for cand in range(2, p):
        if pow(cand, n, p) != 1:
            continue
        if all(pow(cand, n // q, p) != 1 for q in n_factors):
            return cand
    raise RuntimeError("no primitive root")

def prime_factors(n):
    out = set()
    d = 2
    nn = n
    while d * d <= nn:
        while nn % d == 0:
            out.add(d)
            nn //= d
        d += 1
    if nn > 1:
        out.add(nn)
    return list(out)

def divisors(n):
    return [d for d in range(1, n+1) if n % d == 0]

def cosets_of_index_subgroup(n, d):
    """Subgroup of order d (index n/d) in Z/nZ; return its cosets as sorted index tuples."""
    H = [(i * (n // d)) % n for i in range(d)]
    seen = set()
    out = []
    for t in range(n // d):
        c = tuple(sorted((t + h) % n for h in H))
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out

def is_subgroup_aligned(S_set, n):
    """True iff S equals a disjoint union of cosets of some nontrivial subgroup of Z/nZ."""
    for d in divisors(n):
        if d == 1 or d == n:
            continue
        if len(S_set) % d != 0:
            continue
        cs = cosets_of_index_subgroup(n, d)
        covered = [c for c in cs if set(c).issubset(S_set)]
        if covered and sum(len(c) for c in covered) == len(S_set):
            return d
    return None

def smallest_p_cong_1_mod(n, max_search=10000):
    cand = n + 1
    while cand < max_search:
        # primality test
        if all(cand % i != 0 for i in range(2, int(cand**0.5) + 1)):
            return cand
        cand += n
    raise RuntimeError("no p found")

def run_case(n, m, s, r, p=None, verbose=False):
    assert n == s * m
    k = (r - 2) * m
    if k < 1:
        return None
    delta = 1 - r / s
    if delta <= 0:
        return None
    threshold = r * m  # (1 - delta) n
    err_wt = (s - r) * m
    if p is None:
        p = smallest_p_cong_1_mod(n)
    nf = prime_factors(n)
    omega = find_omega(p, n, nf)
    L = [pow(omega, i, p) for i in range(n)]
    f_vals = [pow(x, r * m, p) for x in L]
    g_vals = [pow(x, (r - 1) * m, p) for x in L]

    bad_witnesses = []  # list of (lambda, h_coeffs_tuple, S_indices_tuple)
    for lam in range(p):
        target = [(f_vals[i] + lam * g_vals[i]) % p for i in range(n)]
        # Enumerate h of degree < k, i.e., k coefficients.
        for hc in product(range(p), repeat=k):
            agree = []
            for i in range(n):
                hv = 0
                xpw = 1
                for j in range(k):
                    hv = (hv + hc[j] * xpw) % p
                    xpw = (xpw * L[i]) % p
                if hv == target[i]:
                    agree.append(i)
            if len(agree) >= threshold:
                bad_witnesses.append((lam, hc, tuple(agree)))

    return {
        "params": dict(n=n, m=m, s=s, r=r, p=p, k=k, delta=delta,
                       threshold=threshold, err_wt=err_wt, omega=omega),
        "n_lambdas": len(set(w[0] for w in bad_witnesses)),
        "n_witnesses": len(bad_witnesses),
        "witnesses": bad_witnesses,
    }

def analyze_witnesses(result):
    """For each witness, check subgroup-alignment of agreement set S."""
    n = result["params"]["n"]
    aligned = 0
    not_aligned = []
    for lam, hc, S in result["witnesses"]:
        S_set = set(S)
        d = is_subgroup_aligned(S_set, n)
        if d is not None:
            aligned += 1
        else:
            not_aligned.append((lam, hc, S))
    return aligned, not_aligned

# Run a sweep of small parameter sets.
cases = [
    # (n, m, s, r)
    (12, 2, 6, 3),    # k=2, delta=1/2, threshold=6
    (12, 2, 6, 4),    # k=4, delta=1/3, threshold=8
    (24, 2, 12, 3),   # k=2, delta=3/4, threshold=6  (the main case)
    (24, 2, 12, 4),   # k=4, delta=2/3, threshold=8
    (24, 2, 12, 5),   # k=6, delta=7/12, threshold=10
    (24, 3, 8, 3),    # k=3, delta=5/8, threshold=9
    (24, 3, 8, 4),    # k=6, delta=1/2, threshold=12
    (30, 2, 15, 3),   # k=2, delta=4/5, threshold=6
    (30, 2, 15, 4),   # k=4, delta=11/15, threshold=8
    (30, 3, 10, 3),   # k=3, delta=7/10, threshold=9
    (30, 5, 6, 3),    # k=5, delta=1/2, threshold=15
]

print("="*90)
print(f"{'(n,m,s,r)':<14} {'p':<5} {'k':<3} {'delta':<8} {'#lam':<5} {'#wits':<6} {'#aligned':<10} {'#NOT':<6}")
print("="*90)
total_wits = 0
total_aligned = 0
total_not = []
for (n, m, s, r) in cases:
    res = run_case(n, m, s, r)
    if res is None:
        continue
    a, na = analyze_witnesses(res)
    pp = res["params"]
    print(f"({n:>2},{m:>2},{s:>2},{r:>2})   {pp['p']:<5} {pp['k']:<3} {pp['delta']:<8.4f} "
          f"{res['n_lambdas']:<5} {res['n_witnesses']:<6} {a:<10} {len(na):<6}")
    total_wits += res["n_witnesses"]
    total_aligned += a
    for entry in na:
        total_not.append(((n, m, s, r), entry))

print("="*90)
print(f"\nTotal witnesses across sweep: {total_wits}")
print(f"Total subgroup-aligned: {total_aligned}")
print(f"Total NOT aligned: {len(total_not)}")

if total_not:
    print("\n--- NON-aligned witnesses (counter-examples to Conjecture 4) ---")
    for (params, (lam, hc, S)) in total_not[:10]:  # show first 10
        print(f"  Case {params}: lambda={lam}, h={hc}, S={S}")
else:
    print("\n>>> Every witness across the sweep is subgroup-coset aligned. <<<")
