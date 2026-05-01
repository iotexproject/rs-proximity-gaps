#!/usr/bin/env python3
"""
Direction A — Round 2: Clique analysis

Key reformulation: Given center c, the list {f_1,...,f_M} within distance w
means the differences g_i = f_1 - f_i (i=2,...,M) are min-weight codewords,
AND all pairwise differences g_i - g_j are also min-weight.

Equivalently: find the largest set S of min-weight RS codewords such that
ALL pairwise differences in S are also min-weight.

This is a max clique in the "min-weight difference graph" G:
  V = all min-weight codewords (up to scalar? no, exact)
  E = {(g1, g2) : g1 - g2 is also min-weight}

Key question: what limits the clique size?

Experiments:
A. Build the min-weight difference graph and find max clique
B. Analyze the zero-set intersection structure of cliques
C. Relate clique size to the "shared zero" constraint
D. Check if the max clique size grows with n or stays bounded
"""

import itertools
from collections import defaultdict
import math

def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        val = 1
        for _ in range(p - 1):
            seen.add(val)
            val = val * g % p
        if len(seen) == p - 1:
            return g

def find_omega(g, p, n):
    return pow(g, (p - 1) // n, p)

def poly_eval(coeffs, x, p):
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = xpow * x % p
    return val

def johnson_w(n, k):
    return int(math.floor(n - math.sqrt(n * (k - 1))))


def build_minweight_graph(n, p):
    """
    Build graph on min-weight codewords.
    A min-weight codeword of RS[n,k] has weight d_min = n-k+1 and degree < k.
    It's determined by: zero set Z (k-1 elements from [n]) + leading coefficient a.

    For the DIFFERENCE constraint, we work with evaluation vectors directly.
    """
    k = n // 2
    d_min = n - k + 1
    w = johnson_w(n, k)

    g = find_primitive_root(p)
    omega = find_omega(g, p, n)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"RS[{n},{k}] over F_{p}, d_min={d_min}, w={w}")

    # Generate ALL min-weight codewords (evaluation vectors)
    # f(x) = a * Prod_{i in Z} (x - L[i]), a in F_p*, Z in C([n], k-1)
    # Evaluation: f(L[j]) = a * Prod_{i in Z} (L[j] - L[i])

    # First, for each zero set Z, compute the evaluation vector (up to scalar)
    zero_set_evals = {}
    for Z in itertools.combinations(range(n), k - 1):
        Z_set = frozenset(Z)
        evals = []
        for j in range(n):
            if j in Z_set:
                evals.append(0)
            else:
                val = 1
                for i in Z:
                    val = val * (L[j] - L[i]) % p
                evals.append(val)
        zero_set_evals[Z] = tuple(evals)

    print(f"  Total zero sets: {len(zero_set_evals)}")

    # For the clique problem, we need: for codewords g1, g2 (with scalars a1, a2),
    # g1 - g2 is also min-weight, i.e., has weight exactly d_min.
    #
    # g1 = a1 * e_Z1, g2 = a2 * e_Z2
    # g1 - g2 at position j: a1*e_Z1[j] - a2*e_Z2[j]
    #   = 0 when j in Z1 ∩ Z2 (both zero)
    #   = a1*e_Z1[j] when j in Z1^c ∩ Z2 (only Z1 nonzero... wait no, Z1 contains j means eval is 0)

    # Let me re-think. If j ∈ Z1 (zero of g1): g1[j]=0, g2[j] may be 0 or not.
    # If j ∈ Z1 ∩ Z2: g1[j]=g2[j]=0, so (g1-g2)[j]=0.
    # If j ∈ Z1 \ Z2: g1[j]=0, g2[j]≠0, so (g1-g2)[j] = -a2*e_Z2[j] ≠ 0.
    # If j ∈ Z2 \ Z1: (g1-g2)[j] = a1*e_Z1[j] ≠ 0.
    # If j ∉ Z1 ∪ Z2: (g1-g2)[j] = a1*e_Z1[j] - a2*e_Z2[j], could be 0 or not.

    # For g1-g2 to have weight d_min = n-k+1:
    # It needs exactly k-1 zeros.
    # Guaranteed zeros: |Z1 ∩ Z2| (from shared zero positions)
    # Additional zeros: positions j ∉ Z1 ∪ Z2 where a1*e_Z1[j] = a2*e_Z2[j]
    # Total zeros needed: k-1
    # So we need: |Z1 ∩ Z2| + #{j ∉ Z1∪Z2 : a1*e_Z1[j] = a2*e_Z2[j]} = k-1

    # Since |Z1| = |Z2| = k-1:
    # Let s = |Z1 ∩ Z2|. Then |Z1 ∪ Z2| = 2(k-1) - s.
    # Positions outside both: n - 2(k-1) + s = n - 2k + 2 + s = d_min - 1 + s
    # Need: s + #{coincidences outside} = k-1
    # So #{coincidences} = k - 1 - s
    # Out of d_min - 1 + s = n - 2k + 2 + s positions

    # For this to be possible: k-1-s ≤ n-2k+2+s, i.e., 3k-3 ≤ n+2s
    # For k=n/2: 3n/2 - 3 ≤ n + 2s → s ≥ n/4 - 3/2

    # For n=8, k=4: s ≥ 0.5, so s ≥ 1
    # For n=10, k=5: s ≥ 1, so s ≥ 1
    # For n=12, k=6: s ≥ 1.5, so s ≥ 2

    print(f"\n  Minimum intersection for d_min difference: s ≥ ceil((3k-3-n)/2) = {math.ceil((3*k - 3 - n) / 2)}")

    # Build graph: for each pair (Z1, a1), (Z2, a2), check if difference is min-weight
    # This is O(C(n,k-1)^2 * p) which is manageable for small cases

    # Simplification: work with Z-pairs first, then find valid scalars
    zero_sets = list(zero_set_evals.keys())

    # For each pair of zero sets, find the set of scalar ratios a1/a2
    # that make g1-g2 min-weight
    pair_data = {}

    for idx1, Z1 in enumerate(zero_sets):
        e1 = zero_set_evals[Z1]
        for idx2, Z2 in enumerate(zero_sets):
            if idx2 <= idx1:
                continue
            e2 = zero_set_evals[Z2]

            Z1s = frozenset(Z1)
            Z2s = frozenset(Z2)
            s = len(Z1s & Z2s)

            # Positions outside both
            outside = [j for j in range(n) if j not in Z1s and j not in Z2s]
            # Need k-1-s coincidences: a1*e1[j] = a2*e2[j]
            # i.e., a1/a2 = e2[j]/e1[j] for k-1-s positions

            needed = k - 1 - s
            if needed < 0:
                continue  # too much overlap, difference has too many zeros automatically

            if needed == 0:
                # ANY scalar ratio works (difference always has exactly |Z1∩Z2| ≥ k-1 zeros)
                # But wait, some positions outside might also coincide
                # Check: for ratio r = a1/a2, how many positions have e1[j]*r = e2[j]?
                # r = e2[j]/e1[j] for each j
                ratios_at_pos = {}
                for j in outside:
                    r = e2[j] * pow(e1[j], p - 2, p) % p
                    ratios_at_pos.setdefault(r, []).append(j)

                # For most ratios, 0 additional coincidences → weight = n - s exactly
                # s = k-1 → weight = n - k + 1 = d_min ✓
                # But some ratios give MORE zeros → weight < d_min (supercodeword!)
                valid_ratios = []
                for r in range(1, p):
                    extra = len(ratios_at_pos.get(r, []))
                    if s + extra == k - 1:
                        valid_ratios.append(r)

                if valid_ratios:
                    pair_data[(idx1, idx2)] = valid_ratios
                continue

            # For each outside position, compute the ratio that makes it zero
            ratio_from_pos = {}
            for j in outside:
                # a1*e1[j] = a2*e2[j] ↔ r = a1/a2 = e2[j]/e1[j]
                r = e2[j] * pow(e1[j], p - 2, p) % p
                ratio_from_pos[j] = r

            # Count how many positions give each ratio
            ratio_count = defaultdict(list)
            for j, r in ratio_from_pos.items():
                ratio_count[r].append(j)

            # Valid ratio: one that appears for EXACTLY k-1-s positions
            # (if more, weight < d_min; if fewer, weight > d_min)
            valid_ratios = []
            for r, positions in ratio_count.items():
                extra_zeros = len(positions)
                total_zeros = s + extra_zeros
                if total_zeros == k - 1:
                    valid_ratios.append(r)

            if valid_ratios:
                pair_data[(idx1, idx2)] = valid_ratios

    print(f"  Pairs with valid scalar ratios: {len(pair_data)}")
    total_pairs = len(zero_sets) * (len(zero_sets) - 1) // 2
    print(f"  Total pairs: {total_pairs}")
    print(f"  Density: {len(pair_data)/total_pairs:.4f}")

    # Now build the actual graph on (Z, scalar) pairs
    # A vertex is (zero_set_index, scalar_a)
    # Edge (v1, v2) if their difference is min-weight

    # For the clique problem, we want: for ANY triplet in the clique,
    # g_i - g_j is min-weight for all i,j.

    # Key insight: fix f_1 = 0 (WLOG). Then the list is {0, g_2, ..., g_M}.
    # Each g_i is min-weight. Each g_i - g_j is min-weight.
    # So we need a clique in the graph on min-weight codewords.

    # But there are (p-1)*C(n,k-1) min-weight codewords total.
    # For n=8, p=17: 16*56 = 896 vertices.

    num_cw = (p - 1) * len(zero_sets)
    print(f"\n  Total min-weight codewords: {num_cw}")

    if num_cw > 5000:
        print("  Too many for full graph, using sampling approach")
        return None, None, None

    # Build adjacency: vertex = (Z_idx, a) where a in {1,...,p-1}
    vertices = []
    for idx in range(len(zero_sets)):
        for a in range(1, p):
            vertices.append((idx, a))

    vert_to_idx = {v: i for i, v in enumerate(vertices)}

    # Compute evaluation vectors
    vert_evals = []
    for idx, a in vertices:
        e = zero_set_evals[zero_sets[idx]]
        vert_evals.append(tuple(a * e[j] % p for j in range(n)))

    # Build adjacency
    print(f"  Building adjacency matrix ({num_cw} vertices)...")
    adj = [set() for _ in range(num_cw)]
    edge_count = 0

    for i in range(num_cw):
        for j in range(i + 1, num_cw):
            # Check if difference has weight d_min
            diff_wt = sum(1 for l in range(n) if (vert_evals[i][l] - vert_evals[j][l]) % p != 0)
            if diff_wt == d_min:
                adj[i].add(j)
                adj[j].add(i)
                edge_count += 1

    print(f"  Edges: {edge_count}")
    print(f"  Edge density: {2*edge_count/(num_cw*(num_cw-1)):.4f}")

    # Find max clique using greedy + BFS expansion
    # (Exact max clique is NP-hard but feasible for small graphs)

    def find_max_clique_greedy(adj, n_verts):
        """Find approximate max clique by greedy + expansion."""
        best_clique = []

        # Sort vertices by degree (descending)
        degrees = [(len(adj[i]), i) for i in range(n_verts)]
        degrees.sort(reverse=True)

        for _, start in degrees[:min(50, n_verts)]:
            clique = [start]
            candidates = set(adj[start])

            while candidates:
                # Pick candidate with most connections to current clique
                best = max(candidates, key=lambda v: len(adj[v] & set(clique)))
                # Check if it connects to ALL clique members
                if all(best in adj[c] for c in clique):
                    clique.append(best)
                    candidates &= adj[best]
                else:
                    candidates.discard(best)

            if len(clique) > len(best_clique):
                best_clique = clique

        return best_clique

    def find_max_clique_exact(adj, n_verts, max_size=20):
        """Exact max clique via branch and bound (for small graphs)."""
        best = []

        def bron_kerbosch(R, P, X):
            nonlocal best
            if not P and not X:
                if len(R) > len(best):
                    best = list(R)
                return
            if len(R) + len(P) <= len(best):
                return  # prune

            # Choose pivot
            pivot = max(P | X, key=lambda v: len(adj[v] & P)) if P | X else None

            for v in list(P - (adj[pivot] if pivot else set())):
                bron_kerbosch(R | {v}, P & adj[v], X & adj[v])
                P.remove(v)
                X.add(v)

        if n_verts <= 1000:
            bron_kerbosch(set(), set(range(n_verts)), set())
        else:
            best = find_max_clique_greedy(adj, n_verts)

        return best

    print(f"\n  Finding max clique...")
    clique = find_max_clique_exact(adj, num_cw)
    print(f"  Max clique size: {len(clique)}")

    # Analyze the clique
    if clique:
        print(f"\n  Clique members:")
        for v in clique:
            idx, a = vertices[v]
            Z = zero_sets[idx]
            print(f"    Z={Z}, a={a}, evals={vert_evals[v][:8]}...")

        # Zero set intersection structure
        print(f"\n  Pairwise zero set intersections:")
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                idx_i = vertices[clique[i]][0]
                idx_j = vertices[clique[j]][0]
                Z_i = set(zero_sets[idx_i])
                Z_j = set(zero_sets[idx_j])
                inter = Z_i & Z_j
                print(f"    ({i},{j}): |Z_i ∩ Z_j| = {len(inter)}, shared = {sorted(inter)}")

    return clique, vertices, zero_sets


# ============================================================
# Experiment: Clique size vs n
# ============================================================
def exp_clique_scaling():
    """How does max clique size scale with n?"""
    print(f"\n{'='*60}")
    print(f"Clique size scaling")
    print(f"{'='*60}")

    test_cases = [
        (6, 7),
        (8, 17),
        (10, 11),
        (10, 31),
        (12, 13),
    ]

    for n, p in test_cases:
        k = n // 2
        d_min = n - k + 1
        w = johnson_w(n, k)
        num_cw = (p - 1) * math.comb(n, k - 1)

        print(f"\n  n={n}, p={p}, k={k}, d_min={d_min}, w={w}, #min_wt_cw={num_cw}")

        if num_cw > 5000:
            print(f"    Skipping (too large)")
            continue

        clique, vertices, zero_sets = build_minweight_graph(n, p)
        if clique:
            print(f"    MAX CLIQUE SIZE: {len(clique)}")

            # This gives M_actual - 1 (since we fixed f_1 = 0)
            # But the center c isn't necessarily a codeword...
            # Actually, the clique gives us a set of min-weight codewords
            # {g_2,...,g_M} with all pairwise diffs also min-weight.
            # The "list" is {0, g_2, ..., g_M}, so M = clique_size + 1.

            # But to match M_actual from Johnson list-decoding,
            # we also need all g_i within distance w of some center c.
            # Zero (f_1=0) must be within distance w of c, and each g_i within w of c.

            # Check: in the clique, what's the max number that are all within
            # Johnson radius of SOME common center?
            print(f"\n    Checking Johnson-radius compatibility...")

            # The "center" in list-decoding can be any received word.
            # f_i within distance w of center c ↔ d(f_i, c) ≤ w
            # f_i = 0 + g_i (where g_i is min-weight, weight d_min = n-k+1)
            # d(g_i, c) ≤ w and d(0, c) ≤ w

            # For 0 to be within distance w of c: wt(c) ≤ w
            # For g_i to be within distance w of c: wt(g_i - c) ≤ w

            # wt(c) ≤ w = n - sqrt(n(k-1))
            # wt(g_i - c) ≤ w

            # Triangle inequality: wt(g_i) ≤ wt(g_i - c) + wt(c)
            # → d_min ≤ 2w → w ≥ d_min/2 = (n-k+1)/2 ≈ n/4
            # This is satisfied at Johnson radius.

            # For the clique to correspond to a Johnson list:
            # we need a CENTER c with wt(c) ≤ w and wt(g_i - c) ≤ w for all i.

            # This is more restrictive than just pairwise d_min!
            print(f"    (Full Johnson compatibility check requires center search)")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    exp_clique_scaling()
