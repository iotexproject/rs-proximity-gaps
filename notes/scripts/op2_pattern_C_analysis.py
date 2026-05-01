#!/usr/bin/env python3 -u
"""Pattern C analysis: the 3 non-tet bad configs with NO sub-tetrahedron.

Empirical: at n=12 c=3 m=4, Pattern C has degree distribution {1:6, 2:3} on
union of size 9. NO sub-tetrahedron embeds.

Question: what is Pattern C's structural invariant? Is it the bipartite-like
matching structure? Hypergraph rank? Steiner triple-system-ish?

Test: enumerate Pattern C systematically — what are the (s_1, s_2)-space
implications? What's the codim of V_bad ∩ Pattern_C?
"""

import sys
import numpy as np
from itertools import combinations, permutations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron
from op2_shifted_syzygy import shifted_syzygy_solvable
from op2_subperiod_test import find_sub_tet


def is_pattern_C(Es, n):
    """Pattern C signature: degree distribution {0: n-9, 1: 6, 2: 3} and
    pairwise intersections all size ≤ 1, no sub-tetrahedron."""
    deg = [0] * n
    for E in Es:
        for v in E: deg[v] += 1
    deg_dist = sorted(Counter(deg).items())
    if not (deg_dist and deg_dist[-1] == (2, 3)):
        return False
    if not any(d == (1, 6) for d in deg_dist):
        return False
    return True


def hypergraph_signature(Es):
    """Combinatorial signature: pair intersection sizes + triple intersections."""
    m = len(Es)
    pair_int = sorted(len(set(Es[i]) & set(Es[j])) for i, j in combinations(range(m), 2))
    triple_int = sorted(
        len(set(Es[i]) & set(Es[j]) & set(Es[k]))
        for i, j, k in combinations(range(m), 3)
    )
    quad_int = len(set.intersection(*[set(E) for E in Es])) if m >= 4 else 0
    return (tuple(pair_int), tuple(triple_int), quad_int)


def find_pattern_C(n, k, c, p, m, n_trials=5000):
    """Find Pattern C configs more aggressively."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(42)
    findings = []
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        if not is_pattern_C(Es, n): continue
        # Generate random γ and check if it gives bad config
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        if has_tetrahedron(Es, w)[0]: continue
        sub_tets = find_sub_tet(Es, n)
        if sub_tets: continue
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue
        any_i = any(shifted_syzygy_solvable(NEs, gammas, i_, p, D, c)
                    for i_ in range(m))
        if any_i: continue
        # Check realization
        v = ker[0]
        s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
        all_realize = True
        for i_ in range(m):
            N = NEs[i_]
            aE = (N @ s2) % p; bE = (N @ s1) % p
            nz = next((j for j in range(c) if aE[j] != 0), None)
            if nz is None: all_realize = False; break
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop: all_realize = False; break
            gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
            if gd != gammas[i_]: all_realize = False; break
        if all_realize:
            findings.append({'Es': Es, 'gammas': gammas, 'rank': rA,
                             'ker_dim': len(ker)})
            if len(findings) >= 20: break
    return findings


def measure_codim_pattern_C(n, k, c, p, m, sample_size=100000):
    """Measure density of Pattern C bad set across (s_1, s_2)."""
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    rng = np.random.default_rng(123)
    findings = find_pattern_C(n, k, c, p, m, n_trials=10000)
    if not findings:
        print("No Pattern C configs found.")
        return
    # Use first finding to estimate
    Es = findings[0]['Es']
    print(f"Pattern C example: Es={Es}")
    print(f"  hypergraph signature: {hypergraph_signature(Es)}")
    deg = [0] * n
    for E in Es:
        for v in E: deg[v] += 1
    print(f"  degree: {deg}")
    print(f"  union: {sorted(set().union(*Es))}")
    # Count distinct Pattern C bad configs at varying p
    return findings


def enumerate_pattern_C_canonical(n, w, m):
    """Enumerate canonical Pattern C combinatorial types up to permutation.

    Pattern C: 4 size-3 supports on 9 vertices with degree {1:6, 2:3} and
    pairwise intersections all size 0 or 1.
    """
    # Generate by fixing union = {0, 1, ..., 8} and iterating
    union = list(range(9))
    all_supports = list(combinations(union, w))
    canonical = set()
    for combo in combinations(all_supports, m):
        Es = list(combo)
        if not is_pattern_C(Es, n): continue
        # Skip if has sub-tet
        if find_sub_tet(Es, n): continue
        # Canonicalize by relabeling: smallest permutation form
        # Just use sorted tuple of sorted supports
        key = tuple(sorted(tuple(sorted(E)) for E in Es))
        canonical.add(key)
    return canonical


if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    print(f"=== Pattern C analysis at n={n} c={c} m={m} ===\n")

    findings = find_pattern_C(n, k, c, p, m, n_trials=10000)
    print(f"Found {len(findings)} Pattern C bad configs in 10000 trials\n")

    sigs = Counter()
    for f in findings:
        sig = hypergraph_signature(f['Es'])
        sigs[sig] += 1
        if sigs[sig] <= 2:
            print(f"  Es={f['Es']}, sig={sig}")

    print(f"\nDistinct hypergraph signatures: {len(sigs)}")
    for sig, count in sigs.most_common(5):
        print(f"  {sig}: {count}")

    print("\n=== Canonical Pattern C enumeration on 9 vertices ===")
    canonical = enumerate_pattern_C_canonical(9, w, m)
    print(f"Canonical Pattern C configs (up to relabeling, on union=[0..8]): {len(canonical)}")
    if canonical and len(canonical) <= 5:
        for k_ in canonical:
            print(f"  {k_}")
