"""
intersection_generic_flat.py — Test |V(r₀-1)∩V(r₁)∩...| on RANDOM 2-flats
in full σ-space F_p[σ₁,...,σ_w].

Key question: is |V₀₁(F_p)| = O(1) on generic flats (not just σ₂=0)?

We know the σ₂=0 bivariate gives O(n) at p ≡ 1 mod n. But the RS-compatible
flat is NOT σ₂=0. Test if generic flats give O(1).
"""

import random
from math import comb

# ---- Multivariate polynomial arithmetic in F_p[σ₁,...,σ_w] ----

def mpoly_zero():
    return {}

def mpoly_const(c, p, w):
    c = c % p
    if c == 0: return {}
    return {(0,)*w: c}

def mpoly_var(idx, w):
    key = tuple(1 if i == idx else 0 for i in range(w))
    return {key: 1}

def mpoly_add(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) + v) % p
        if r[k] == 0: del r[k]
    return r

def mpoly_sub(f, g, p):
    r = dict(f)
    for k, v in g.items():
        r[k] = (r.get(k, 0) - v) % p
        if r[k] == 0: del r[k]
    return r

def mpoly_mul(f, g, p):
    r = {}
    for e1, c1 in f.items():
        for e2, c2 in g.items():
            key = tuple(a+b for a, b in zip(e1, e2))
            r[key] = (r.get(key, 0) + c1 * c2) % p
            if r[key] == 0: del r[key]
    return r

def mpoly_scale(f, c, p):
    c = c % p
    if c == 0: return {}
    return {k: (v * c) % p for k, v in f.items() if (v * c) % p != 0}

def mpoly_eval(f, vals, p):
    r = 0
    for exps, c in f.items():
        term = c
        for i, e in enumerate(exps):
            if e > 0:
                term = (term * pow(vals[i], e, p)) % p
        r = (r + term) % p
    return r

# ---- Companion matrix in full σ-space ----

def compute_all_ri_full(n, p, w):
    """Compute [r₀,...,r_{w-1}] in F_p[σ₁,...,σ_w]."""
    sigma_polys = [mpoly_var(j, w) for j in range(w)]

    c_polys = [None] * w
    for j in range(w):
        sign = pow(-1, w - j + 1, p)
        c_polys[j] = mpoly_scale(sigma_polys[w - j - 1], sign, p)

    state = [mpoly_const(0, p, w) for _ in range(w)]
    state[0] = mpoly_const(1, p, w)

    for step in range(n):
        top = state[w - 1]
        new_state = [None] * w
        new_state[0] = mpoly_mul(top, c_polys[0], p)
        for j in range(1, w):
            new_state[j] = mpoly_add(state[j-1], mpoly_mul(top, c_polys[j], p), p)
        state = new_state

    return state

# ---- Flat parameterization ----

def make_flat(w, base, dir1, dir2):
    """2-flat: σ = base + s₁·dir1 + s₂·dir2.
    Returns function (s1, s2) → (σ₁,...,σ_w).
    """
    def flat_point(s1, s2, p):
        return tuple((base[i] + s1 * dir1[i] + s2 * dir2[i]) % p for i in range(w))
    return flat_point

def random_flat(w, p):
    """Random affine 2-flat in F_p^w."""
    base = tuple(random.randrange(p) for _ in range(w))
    dir1 = tuple(random.randrange(p) for _ in range(w))
    dir2 = tuple(random.randrange(p) for _ in range(w))
    return base, dir1, dir2

def sigma2_zero_flat(w, p):
    """The specific flat σ₂=...=σ_{w-1}=0 (the bivariate case)."""
    base = tuple(0 for _ in range(w))
    dir1 = tuple(1 if i == 0 else 0 for i in range(w))       # σ₁ direction
    dir2 = tuple(1 if i == w-1 else 0 for i in range(w))      # σ_w direction
    return base, dir1, dir2

# ---- Count intersection on a flat ----

def count_on_flat(r_all, flat_params, p, w):
    """Count points on flat where r₀=1, r₁=0, ..., r_{w-1}=0."""
    base, dir1, dir2 = flat_params
    flat_fn = make_flat(w, base, dir1, dir2)

    count_01 = 0  # r₀=1, r₁=0
    count_all = 0  # all r_i conditions
    points_01 = []

    for s1 in range(p):
        for s2 in range(p):
            sigma = flat_fn(s1, s2, p)

            # Evaluate r₀
            v0 = mpoly_eval(r_all[0], sigma, p)
            if v0 != 1:
                continue

            # Evaluate r₁
            v1 = mpoly_eval(r_all[1], sigma, p)
            if v1 != 0:
                continue

            count_01 += 1
            points_01.append((s1, s2))

            # Check remaining
            all_ok = True
            for i in range(2, w):
                vi = mpoly_eval(r_all[i], sigma, p)
                if vi != 0:
                    all_ok = False
                    break
            if all_ok:
                count_all += 1

    return count_01, count_all, points_01

# ---- Direct count in σ-space (no flat restriction) ----

def count_in_sigma_space(r_all, p, w):
    """Count σ ∈ F_p^w with r₀(σ)=1, r₁(σ)=0, ..."""
    from itertools import product as iproduct

    count_0 = 0  # just r₀=1
    count_01 = 0
    count_all = 0

    for sigma in iproduct(range(p), repeat=w):
        v0 = mpoly_eval(r_all[0], sigma, p)
        if v0 != 1:
            continue
        count_0 += 1

        v1 = mpoly_eval(r_all[1], sigma, p)
        if v1 != 0:
            continue
        count_01 += 1

        all_ok = True
        for i in range(2, w):
            vi = mpoly_eval(r_all[i], sigma, p)
            if vi != 0:
                all_ok = False
                break
        if all_ok:
            count_all += 1

    return count_0, count_01, count_all

# ---- Main ----

print("=" * 70)
print("INTERSECTION ON GENERIC 2-FLATS vs σ₂=0 FLAT")
print("=" * 70)

random.seed(42)

test_cases = [
    (8, 3),
    (10, 3),
    (12, 3),
    (8, 4),
    (10, 4),
    (12, 4),
    (10, 5),
    (12, 5),
]

for n, w in test_cases:
    D = n - w + 1
    # Choose primes: one generic (p ≢ 1 mod n) and one special (p ≡ 1 mod n)
    primes_generic = []
    primes_special = []  # p ≡ 1 mod n
    for p in range(n + 1, 200):
        if not all(p % i != 0 for i in range(2, min(p, int(p**0.5)+2))):
            continue
        if (p - 1) % n == 0:
            primes_special.append(p)
        else:
            primes_generic.append(p)

    # Pick first available
    p_gen = primes_generic[0] if primes_generic else None
    p_spec = primes_special[0] if primes_special else None

    for p_label, p in [("generic", p_gen), ("special (p≡1 mod n)", p_spec)]:
        if p is None or p > 60:  # cap for brute force
            continue

        print(f"\n{'='*60}")
        print(f"n={n}, w={w}, D={D}, p={p} ({p_label})")
        print(f"{'='*60}")

        r_all = compute_all_ri_full(n, p, w)

        # Full σ-space count (only if feasible)
        if p**w <= 500000:
            c0, c01, c_all = count_in_sigma_space(r_all, p, w)
            print(f"  Full σ-space: |V(r₀-1)|={c0}, |V₀₁|={c01}, |V_all|={c_all}")
            print(f"  Expected |V(r₀-1)| ≈ p^{w-1} = {p**(w-1)}")
            binom_nw = comb(n, w)
            print(f"  C(n,w) = {binom_nw}, C(n,w)/p = {binom_nw/p:.1f}")

        # σ₂=0 flat
        flat_s2z = sigma2_zero_flat(w, p)
        c01_s2z, c_all_s2z, pts_s2z = count_on_flat(r_all, flat_s2z, p, w)
        print(f"\n  σ₂=0 flat: |V₀₁|={c01_s2z}, |V_all|={c_all_s2z}")

        # Random flats
        n_trials = 20
        v01_list = []
        v_all_list = []
        for trial in range(n_trials):
            flat_rand = random_flat(w, p)
            c01_r, c_all_r, _ = count_on_flat(r_all, flat_rand, p, w)
            v01_list.append(c01_r)
            v_all_list.append(c_all_r)

        print(f"\n  Random flats ({n_trials} trials):")
        print(f"    |V₀₁|: min={min(v01_list)}, max={max(v01_list)}, avg={sum(v01_list)/len(v01_list):.1f}")
        print(f"    |V_all|: min={min(v_all_list)}, max={max(v_all_list)}, avg={sum(v_all_list)/len(v_all_list):.1f}")
        print(f"    V₀₁ histogram: {sorted(v01_list)}")
        print(f"    V_all histogram: {sorted(v_all_list)}")

        # Expected from density
        expected_v01 = D * D / p  # rough heuristic
        print(f"    Expected V₀₁ ≈ D²/p = {expected_v01:.1f}")

print("\n" + "="*70)
print("KEY QUESTION: Is max |V₀₁| on random flats = O(1)?")
print("="*70)
