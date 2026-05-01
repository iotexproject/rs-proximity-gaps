#!/usr/bin/env python3 -u
"""For non-tet configs where lemma's escape fails, verify if all m γ realize.

If yes: there are bound-violating (s_1, s_2) NOT in any tet variety →
        Conjecture v6 (V_bad ⊂ ∪_V V_tet) is FALSE.

If no: the lemma's escape failing doesn't directly mean realization;
       additional combinatorial obstruction exists.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_witness_full_M import compute_M_full

def test_specific(n, k, c, p, Es, gammas):
    D = n - k; w = D - c
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]
    NEs = make_NEs(Es, L, p, D, c, w)
    A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
    print(f"\n  Es={Es}")
    print(f"  γ={gammas}")
    print(f"  rank A = {rA}, ker dim = {len(ker)}")
    if not ker:
        print(f"  No kernel; can't realize.")
        return
    # For each kernel basis, derive realized γ values
    rng = np.random.default_rng(0)
    max_M = 0
    best_v = None
    for v in ker[:8]:
        s1 = v[:D].astype(np.int64); s2 = v[D:].astype(np.int64)
        if not np.any(s2 != 0): continue
        # Check derived γ's
        derived = []
        for i_ in range(len(Es)):
            N = NEs[i_]
            aE = (N @ s2) % p; bE = (N @ s1) % p
            nz = None
            for j in range(c):
                if aE[j] != 0: nz = j; break
            if nz is None: derived.append(None); continue
            prop = all(
                (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
                for j_ in range(c) for k_ in range(c)
            )
            if not prop: derived.append(None); continue
            gd = (-int(bE[nz]) * pow(int(aE[nz]), p-2, p)) % p
            derived.append(gd)
        # Check if all m γ's are distinct and match given γ
        distinct_all = len(set(g for g in derived if g is not None)) == len(Es) and \
                       all(g is not None for g in derived) and \
                       all(derived[i_] == gammas[i_] for i_ in range(len(Es)))
        if distinct_all:
            print(f"    ker[?]: ALL {len(Es)} γ realized DISTINCTLY (s_2={s2.tolist()})")
            best_v = (s1, s2)
            # Compute full M to see if more γ's realize beyond chosen supports
            full_M = compute_M_full(s1, s2, L, p, n, c, w)
            print(f"    Full M(s_1, s_2) = {len(full_M)}")
            print(f"    Realized γ values: {sorted(full_M.keys())}")
            return len(full_M)
        else:
            n_realized = sum(1 for g in derived if g is not None)
            n_match = sum(1 for i_, g in enumerate(derived) if g is not None and g == gammas[i_])
            print(f"    ker[?]: realized {n_realized}/{len(Es)}, matched {n_match}")
    return None

if __name__ == '__main__':
    n, k, c = 12, 6, 3
    p = 1009
    print(f"=== Counterexamples to lemma at n={n} c={c} ===")
    # From op2_shifted_syzygy.py output
    examples = [
        ([(7, 8, 9), (3, 4, 9), (2, 10, 11), (3, 7, 8)], None),
        ([(8, 9, 11), (1, 2, 9), (2, 4, 10), (1, 4, 10)], None),
        ([(3, 5, 7), (1, 5, 9), (6, 8, 10), (1, 7, 9)], None),
    ]
    # Need to regenerate γ tuple — use deterministic seed matching shifted_syzygy.py
    rng = np.random.default_rng(0)
    # Skip to find the ones from earlier
    for Es, _ in examples:
        # Build γ via fresh trial — the actual γ's used in counterexample
        # were random; here we test if ANY γ tuple works
        for trial in range(20):
            gammas = []; seen = set()
            while len(gammas) < len(Es):
                g = int(rng.integers(2, p))
                if g not in seen: gammas.append(g); seen.add(g)
            test_specific(n, k, c, p, Es, gammas)
            break
