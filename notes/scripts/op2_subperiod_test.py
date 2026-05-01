#!/usr/bin/env python3 -u
"""Test H1 from Note 0108: do non-tet bad patterns embed sub-tetrahedra?

For each non-tet bad config (E_1, ..., E_m), check whether some subset of
size w'+1 ≤ |union| of [n] is fully covered by m' = w'+1 of the supports
(i.e., the supports restricted to that subset form a (w'+1)-clique on it,
possibly after dropping duplicates).

If H1 holds: every non-tet bad config has a hidden tetrahedron, and the
"non-tet" routes are actually "subperiod tetrahedra" with codim controlled
by the smaller (w'+1)-clique.
"""

import sys
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_nontet_pattern_analysis import find_all_nontet_realizable


def find_sub_tet(Es, n):
    """For a tuple Es of supports of equal size w, check if any subset
    V ⊂ ⋃Es of size w'+1 (w' < w) has the property that there exist
    w'+1 supports E_i in Es such that V \\ {v_i} ⊂ E_i for some labeling.

    Returns list of (V, mapping) where V is the witness set and mapping is
    {v_i: index of E covering V \\ {v_i}}.

    Equivalently: for the sub-V indexing, consider E_j ∩ V — it has size
    ≤ w'. We want |V| - |E_j ∩ V| ≤ 1 (i.e., E_j misses at most one v in V),
    AND one specific v_i is missed exactly.
    """
    w = len(Es[0])
    union = set().union(*Es)
    sub_tets = []
    # candidate V sizes: w'+1 from 3 (smallest meaningful) to |union|
    for size_V in range(3, min(w + 2, len(union) + 1)):
        for V in combinations(union, size_V):
            V_set = set(V)
            # For each v ∈ V, find E_j with V \ {v} ⊂ E_j
            mapping = {}
            ok = True
            used_indices = set()
            for v in V:
                target = V_set - {v}
                # Find some E_j (not yet used) with target ⊂ E_j
                found = None
                for j, E in enumerate(Es):
                    if j in used_indices: continue
                    if target.issubset(set(E)):
                        found = j; break
                if found is None:
                    ok = False; break
                mapping[v] = found
                used_indices.add(found)
            if ok:
                sub_tets.append((tuple(sorted(V)), mapping))
    return sub_tets


if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    D = n - k; w = D - c
    T = (2 * D - 1) // c
    print(f"=== Sub-tetrahedron test for non-tet bad configs at n={n} c={c} m={T+1} ===")
    findings = find_all_nontet_realizable(n, k, c, p, T + 1, n_trials=3000)
    print(f"Found {len(findings)} non-tet bad configs.\n")

    has_sub_tet = 0
    no_sub_tet = 0
    no_sub_tet_examples = []

    by_pattern = {}

    for f in findings:
        Es = f['Es']
        deg = [0] * n
        for E in Es:
            for v in E: deg[v] += 1
        deg_dist = tuple(sorted(Counter(deg).items()))
        union_size = len(set().union(*Es))
        ker_dim = f['ker_dim']
        key = (deg_dist, union_size, ker_dim)
        sub_tets = find_sub_tet(Es, n)
        by_pattern.setdefault(key, {'count': 0, 'has_sub': 0, 'examples': []})
        by_pattern[key]['count'] += 1
        if sub_tets:
            has_sub_tet += 1
            by_pattern[key]['has_sub'] += 1
            if len(by_pattern[key]['examples']) < 1:
                by_pattern[key]['examples'].append({
                    'Es': Es, 'sub_tets': sub_tets[:3],
                })
        else:
            no_sub_tet += 1
            if len(no_sub_tet_examples) < 3:
                no_sub_tet_examples.append({'Es': Es, 'deg': deg, 'union_size': union_size})

    print(f"Out of {len(findings)} non-tet bad configs:")
    print(f"  {has_sub_tet} embed a sub-tetrahedron (≤ w'+1 cover, w' < w)")
    print(f"  {no_sub_tet} do NOT embed any sub-tetrahedron\n")

    print("By pattern:")
    for key, info in sorted(by_pattern.items()):
        deg_dist, union_size, ker_dim = key
        print(f"  Pattern {dict(deg_dist)}, |union|={union_size}, "
              f"ker_dim={ker_dim}: {info['has_sub']}/{info['count']} have sub-tet")
        if info['examples']:
            ex = info['examples'][0]
            print(f"    example Es={ex['Es']}")
            for V, mp in ex['sub_tets'][:2]:
                print(f"    -> V={V}, mapping={mp}")
    if no_sub_tet_examples:
        print(f"\nNo-sub-tet examples (first {len(no_sub_tet_examples)}):")
        for ex in no_sub_tet_examples:
            print(f"  Es={ex['Es']}, deg={ex['deg']}, |union|={ex['union_size']}")
