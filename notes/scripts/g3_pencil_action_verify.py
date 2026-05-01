"""g3_pencil_action_verify.py — verify multiplicative-orbit structure of bad α.

Claim: bad-α set is closed under α ↦ α·ν for ν ∈ ⟨ω_n^{b-a}⟩.

For (43, 47, 64, 16, 193): bad-α should be ≥ 16 (orbit closed under μ_16 action).
Direct verification by checking dist(h(α), RS_k) for predicted orbit elements.
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
    return [pow(w, i, p) for i in range(n)], w


def compute_dist_via_T(h, L_arr, info_sets, D, inv_D, p, n, k):
    """Compute dist via given info_sets (returns max extras)."""
    info_arr = np.array(info_sets, dtype=np.int64)
    h_arr = np.array(h, dtype=np.int64) if not isinstance(h, np.ndarray) else h
    ext = batched_extras(info_arr, h_arr, L_arr, D, inv_D, p)
    return n - k - int(ext.max())


def main():
    q = 193
    n, k = 64, 16
    a, b = 43, 47
    w_J = n - int(round(np.sqrt(k * n)))

    L, w_n = find_subgroup(q, n)
    L_arr = np.array(L, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, q)
    print(f"Primitive {n}-th root w_n = {w_n}")
    print(f"L_n = ⟨{w_n}⟩ in F_{q}*")

    # Predicted action subgroup: ⟨w_n^{b-a}⟩ = ⟨w_n^4⟩
    diff = (b - a) % n
    nu_gen = pow(w_n, diff, q)
    nu_order = n // np.gcd(diff, n)
    print(f"Action subgroup: ⟨w_n^{diff}⟩ generator = {nu_gen}, order {nu_order}")
    nu_orbit = [pow(nu_gen, k, q) for k in range(nu_order)]
    print(f"Orbit elements: {sorted(nu_orbit)}")

    z_a = np.array([pow(int(x), a, q) for x in L], dtype=np.int64)
    z_b = np.array([pow(int(x), b, q) for x in L], dtype=np.int64)

    # Use VERY large sample to approximate full enumeration
    rng = np.random.default_rng(2026)
    sample_size = 100000
    sample = []; seen = set()
    while len(sample) < sample_size:
        T = tuple(sorted(rng.choice(n, size=k, replace=False).tolist()))
        if T not in seen: seen.add(T); sample.append(T)
    print(f"Sample size: {len(sample)} info_sets (~ negligible fraction of C(64,16))")

    # Test: for α = 3 (known bad), compute the predicted orbit {3·ν : ν ∈ ⟨ω_n^4⟩}
    # and check distance for each
    target_alphas = sorted(set((3 * nu) % q for nu in nu_orbit))
    print(f"\nPredicted orbit of α=3 under action: {target_alphas}")

    print(f"\nDistances for predicted orbit elements:")
    print(f"{'α':>5} {'dist':>5} {'bad?':>6}")
    print("-" * 25)
    for alpha in target_alphas:
        h = (z_a + alpha * z_b) % q
        d = compute_dist_via_T(h, L_arr, sample, D, inv_D, q, n, k)
        is_bad = d <= w_J
        marker = "BAD" if is_bad else "ok"
        print(f"{alpha:>5} {d:>5} {marker:>6}")

    # Also test some non-orbit elements
    print(f"\nDistances for some non-orbit elements (sanity):")
    for alpha in [1, 5, 7, 11, 13, 100]:
        if alpha in target_alphas: continue
        h = (z_a + alpha * z_b) % q
        d = compute_dist_via_T(h, L_arr, sample, D, inv_D, q, n, k)
        is_bad = d <= w_J
        marker = "BAD" if is_bad else "ok"
        print(f"{alpha:>5} {d:>5} {marker:>6}")


if __name__ == "__main__":
    main()
