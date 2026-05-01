#!/usr/bin/env python3 -u
"""Direct measurement of V_tet_sub codim at c=4, w'=3.

V_tet_sub(V; E_1, ..., E_{w'+1}) := {(s_1, s_2) ∈ F_p^{2D} :
   for each i, ∃ γ_i ∈ F_p^* with s_1 + γ_i s_2 ∈ ker N_{E_i},
   and γ_i pairwise distinct}.

Conjecture: dim V_tet_sub = w + 1, codim 2D - w - 1 = 2D - T - 2 (target).

At c=4, n=16, w=4, T=3: codim 11 = 2D-T-2. dim 5.

Sampling strategy: Monte Carlo over (s_1, s_2). For each, check if it
realizes the sub-tet with distinct γ_i's.

Realization check: for each E_i, N_{E_i} is c×D. N(s_1) ∝ N(s_2) iff
the 2×c matrix [N(s_1); N(s_2)] has rank ≤ 1, iff all 2x2 minors vanish.
Then γ_i is determined.
"""

import sys
import numpy as np
from itertools import combinations
from collections import Counter
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs


def realizes_bad_gamma(N, s1, s2, p, c):
    """For c×D matrix N, check if N(s1) is parallel to N(s2). If yes,
    return γ = -(N(s1)[k]/N(s2)[k]) for some non-zero k. Else None."""
    Ns1 = (N @ s1) % p
    Ns2 = (N @ s2) % p
    # Find a non-zero entry in Ns2
    nz = next((k for k in range(c) if Ns2[k] != 0), None)
    if nz is None:
        # Ns2 = 0. Then s2 ∈ ker N. Need Ns1 = 0 too for proportionality
        # of any factor. But that means s_1+γ s_2 ∈ ker N for ALL γ.
        # We say this is degenerate; skip.
        return None if any(Ns1) else 'all'
    # Check proportionality
    gamma = (-int(Ns1[nz]) * pow(int(Ns2[nz]), p - 2, p)) % p
    for k in range(c):
        if (int(Ns1[k]) + gamma * int(Ns2[k])) % p != 0:
            return None
    return gamma


def measure_v_tet_sub_density(Es, L, p, D, c, n_samples):
    """Sample (s_1, s_2) and count those realizing the sub-tet (all m supports)."""
    m = len(Es)
    w = len(Es[0])
    NEs = make_NEs(Es, L, p, D, c, w)
    rng = np.random.default_rng(0)
    realize_count = 0
    distinct_realize = 0
    for trial in range(n_samples):
        s1 = rng.integers(0, p, D)
        s2 = rng.integers(0, p, D)
        if all(s == 0 for s in s2): continue
        gammas = []
        ok = True
        for N in NEs:
            g = realizes_bad_gamma(N, s1, s2, p, c)
            if g is None or g == 'all':
                ok = False; break
            gammas.append(g)
        if ok:
            realize_count += 1
            if len(set(gammas)) == m and 0 not in gammas:
                distinct_realize += 1
    return realize_count, distinct_realize


def find_sub_tet_example(n, c, p, n_trials=20000):
    """Find a w'=3 sub-tet config example."""
    from op2_subperiod_test import find_sub_tet
    k = n // 2; D = n - k; w = D - c
    m = (2 * D - 1) // c + 1
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    all_supports = list(combinations(range(n), w))
    rng = np.random.default_rng(13)
    for trial in range(n_trials):
        idx = rng.choice(len(all_supports), size=m, replace=False)
        Es = [all_supports[i] for i in idx]
        sub_tet = find_sub_tet(Es, n)
        if sub_tet:
            # find one with w' = 3 (i.e., V of size 4)
            for V_tup, mapping in sub_tet:
                if len(V_tup) == 4:  # w'+1 = 4
                    return Es, V_tup, mapping, L
    return None, None, None, None


if __name__ == '__main__':
    n = 16; c = 4
    primes = [97, 193, 257, 449, 577, 1009]
    p = next((q for q in primes if (q - 1) % n == 0), None)
    k = n // 2; D = n - k; w = D - c
    print(f"n={n}, k={k}, c={c}, w={w}, D={D}")
    print(f"Target codim 2D-T-2 = {2*D - (2*D-1)//c - 2}")
    print()

    Es, V, mapping, L = find_sub_tet_example(n, c, p, n_trials=50000)
    if Es is None:
        print("No w'=3 sub-tet found.")
        sys.exit(1)

    print(f"Sub-tet w'=3 example: V={V}")
    print(f"  Es={Es}")
    print(f"  V \\ {{V[i]}} ⊂ E_{{mapping[v_i]}}: {dict(mapping)}")

    # Measure density for varying p
    for p_test in primes[:4]:
        if (p_test - 1) % n != 0: continue
        omega = find_omega(n, p_test)
        L_test = [pow(omega, i, p_test) for i in range(n)]
        n_samples = min(2 * 10**6, p_test ** (D - 4))  # adapt to p
        n_samples = min(n_samples, 5 * 10**5)
        rc, drc = measure_v_tet_sub_density(Es, L_test, p_test, D, c, n_samples)
        density = rc / n_samples
        ddensity = drc / n_samples
        # Empirical codim
        codim_emp = -np.log(ddensity) / np.log(p_test) if ddensity > 0 else np.inf
        print(f"\n  p = {p_test}:")
        print(f"    samples = {n_samples}")
        print(f"    realize all m γ's: {rc}/{n_samples} = {density:.6e}")
        print(f"    realize distinct γ's: {drc}/{n_samples} = {ddensity:.6e}")
        print(f"    empirical codim = {codim_emp:.3f}")
        print(f"    target 2D-T-2 = 11")
