"""g3_pencil_alpha_id.py — identify WHICH α give bad pencil h(α) = z^a + α z^b.

Focus: (a, b) = (43, 47) at n=64, k=16, q=193 — N = 4.
Identify the 4 α values, their structure (multiplicative orbit, polynomial roots).

Also (a, b) = (21, 25) at n=32, k=8, q=193 — N = 9.
Identify the 9 α values.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from mds_decoder import precompute_diff_inv, batched_extras


def find_subgroup(p, n):
    assert (p - 1) % n == 0
    g = None
    for cand in range(2, p):
        ok = True
        for d in range(1, n):
            if pow(cand, (p - 1) * d // n, p) == 1: ok = False; break
        if ok: g = cand; break
    if g is None: g = 3
    w = pow(g, (p - 1) // n, p)
    return [pow(w, i, p) for i in range(n)]


def identify_bad_alphas(a, b, n, k, q, n_samples=20000):
    L = find_subgroup(q, n)
    L_arr = np.array(L, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, q)
    w_J = n - int(round(np.sqrt(k * n)))

    z_a = np.array([pow(int(x), a, q) for x in L], dtype=np.int64)
    z_b = np.array([pow(int(x), b, q) for x in L], dtype=np.int64)

    rng = np.random.default_rng(2026)
    sample = []; seen = set()
    while len(sample) < n_samples:
        T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    info_arr = np.array(sample, dtype=np.int64)

    bad_alphas = []
    for alpha in range(q):
        h = (z_a + alpha * z_b) % q
        ext = batched_extras(info_arr, h, L_arr, D, inv_D, q)
        d = n - k - int(ext.max())
        if d <= w_J:
            bad_alphas.append((alpha, d))
    return bad_alphas, w_J


def analyze_orbit(alphas, q, n):
    """Check if alphas form a multiplicative orbit under various group actions."""
    print(f"  Bad alphas: {[a for a, _ in alphas]}")
    if len(alphas) == 0: return

    # Check if forms a coset of a subgroup of F_q^*
    raw = sorted(set(a for a, _ in alphas if a != 0))
    if not raw: return

    # Check ratios
    if len(raw) >= 2:
        a0 = raw[0]
        if a0 == 0: a0 = raw[1] if len(raw) > 1 else None
        if a0 is not None and a0 != 0:
            inv_a0 = pow(a0, q - 2, q)
            ratios = sorted(set((a * inv_a0) % q for a in raw))
            print(f"  Ratios α/α₀ (α₀={a0}): {ratios}")

            # Check if ratios are all (q-1)/n powers of unity
            unity_n = sorted(set(pow(g, k, q) for k in range(n) for g in [3] if pow(g, n, q) == 1))
            print(f"  These ratios as multiplicative orbit?")

    # Check if alphas are roots of a low-degree polynomial over F_q
    # Compute elementary symmetric: σ_i for i = 1..len(alphas)
    if len(raw) <= 10:
        # Polynomial Π(x - α_i) — coefficients
        from functools import reduce
        coefs = [1]
        for r in raw:
            new_coefs = [0] * (len(coefs) + 1)
            for i, c in enumerate(coefs):
                new_coefs[i] = (new_coefs[i] + c) % q  # x term
                new_coefs[i+1] = (new_coefs[i+1] - c * r) % q  # const term
            coefs = new_coefs
        print(f"  Annihilating polynomial coefs (highest-deg first): {[c % q for c in coefs]}")
        print(f"  In symmetric form, σ_1 = {sum(raw) % q}, σ_n = {reduce(lambda x, y: x*y % q, raw)}")


def main():
    cases = [
        # (a, b, n, k, q)
        (43, 47, 64, 16, 193),
        (21, 25, 32, 8, 193),
        (5, 3, 8, 2, 193),
    ]

    for a, b, n, k, q in cases:
        print(f"\n=== (a,b) = ({a},{b}), n={n}, k={k}, q={q} ===")
        t0 = time.time()
        bad, w_J = identify_bad_alphas(a, b, n, k, q)
        print(f"  Found {len(bad)} bad α (w_J={w_J}); elapsed {time.time()-t0:.0f}s")
        analyze_orbit(bad, q, n)


if __name__ == "__main__":
    main()
