#!/usr/bin/env python3 -u
"""Test routed dichotomy at c=4 (n=16, c=4, m=?).

At n=16 c=4 with k=8: D=8, w=4, T = ⌊(2D-1)/c⌋ = ⌊15/4⌋ = 3, m = T+1 = 4.

Find non-tet bad configs at this scale; classify by:
1. Sub-tet embedding (sub-tet at w' = 2 or 3)
2. Pattern X (with c=4 analog of Pattern C)

If routed dichotomy holds: most non-tet bad embed sub-tet; rest fall into a
small disjoint-route class.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_bad_set_chars import has_tetrahedron
from op2_shifted_syzygy import shifted_syzygy_solvable
from op2_subperiod_test import find_sub_tet


def test_route_classification(n, c, p, n_trials=10000):
    """Find non-tet bad configs and classify by sub-tet embedding."""
    k = n // 2
    D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    omega = find_omega(n, p)
    if omega is None:
        print(f"  no omega for n={n} at p={p}")
        return
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(0)

    print(f"  n={n}, k={k}, D={D}, w={w}, c={c}, T={m-1}, m={m}, p={p}")
    print(f"  total supports of size {w}: {len(all_supports)}")
    print(f"  trials: {n_trials}")

    n_bad_total = 0
    n_tet = 0
    n_sub_tet = 0
    n_neither = 0
    by_pattern = Counter()
    neither_examples = []

    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        # Skip full tet
        if has_tetrahedron(Es, w)[0]: continue
        gammas = []; seen = set()
        while len(gammas) < m:
            g = int(rng.integers(2, p))
            if g not in seen: gammas.append(g); seen.add(g)
        NEs = make_NEs(Es, L, p, D, c, w)
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        if rA == min(m * c, 2 * D): continue
        # Check shifted syzygy
        any_i = any(shifted_syzygy_solvable(NEs, gammas, i_, p, D, c)
                    for i_ in range(m))
        if any_i: continue
        # Verify realization
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
        if not all_realize: continue
        n_bad_total += 1
        sub_tets = find_sub_tet(Es, n)
        deg = [0] * n
        for E in Es:
            for u in E: deg[u] += 1
        deg_dist = tuple(sorted(Counter(deg).items()))
        union_size = len(set().union(*Es))
        key = (deg_dist, union_size, len(ker))
        if sub_tets:
            n_sub_tet += 1
            by_pattern[(key, 'sub-tet')] += 1
        else:
            n_neither += 1
            by_pattern[(key, 'neither')] += 1
            if len(neither_examples) < 3:
                neither_examples.append({'Es': Es, 'deg': deg, 'union': union_size,
                                          'ker_dim': len(ker)})

    print(f"\n  Non-tet bad configs found: {n_bad_total}")
    print(f"    With sub-tet: {n_sub_tet}")
    print(f"    Without sub-tet (Pattern C analog): {n_neither}")

    print(f"\n  Pattern breakdown:")
    for (key, route), count in by_pattern.most_common(10):
        deg_dist, union_size, ker_dim = key
        print(f"    [{route:>9}] deg={dict(deg_dist)}, |U|={union_size}, ker={ker_dim}: {count}")

    if neither_examples:
        print(f"\n  No-sub-tet examples (first {len(neither_examples)}):")
        for ex in neither_examples:
            print(f"    Es={ex['Es']}, |U|={ex['union']}, ker={ex['ker_dim']}")


if __name__ == '__main__':
    print("=== Routed dichotomy at c=4 (n=16) ===\n")
    # Find a prime ≡ 1 mod 16
    primes = [97, 193, 257, 449, 577, 1009, 1153, 1217]
    valid = [p for p in primes if (p - 1) % 16 == 0]
    if not valid:
        print("No valid prime found.")
    else:
        p = valid[0]
        test_route_classification(16, 4, p, n_trials=5000)

    print("\n\n=== Routed dichotomy at c=3 (n=20, larger scale) ===\n")
    primes = [101, 181, 241, 281, 421, 521, 541, 601, 641, 661, 821, 881, 941, 1021, 1061]
    valid = [p for p in primes if (p - 1) % 20 == 0]
    if valid:
        p = valid[0]
        test_route_classification(20, 3, p, n_trials=3000)
