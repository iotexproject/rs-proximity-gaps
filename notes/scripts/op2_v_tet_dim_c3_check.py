#!/usr/bin/env python3 -u
"""Check dim V_tet at c=3 full tet via density-in-span method.

Note 0099 claims dim V_tet = w+1 at c=3 full tet. Verify with the same
methodology used to disprove Note 0113 at c=4."""

import sys, math
import numpy as np
from itertools import product
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs, solve_for_witness
from op2_v_tet_sub_density_in_span import build_8dim_span, is_in_v_tet_sub


def measure_at_c3():
    n = 12; c = 3
    D = n - n // 2  # k = n//2 = 6, D = 6
    w = D - c       # 3
    V = [0, 1, 2, 3]
    Es = [tuple(v for v in V if v != V[i]) for i in range(len(V))]
    print(f"=== c=3 full tet at n={n}, V={V}, Es={Es} ===")

    primes = [13, 37, 61, 109, 181, 277, 349, 1009]
    for p in primes:
        if (p - 1) % n != 0: continue
        omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
        NEs = make_NEs(Es, L, p, D, c, w)
        # Compute span dim
        rng = np.random.default_rng(0)
        accumulated = []
        for trial in range(200):
            gammas = (rng.choice(p - 1, size=4, replace=False) + 1).tolist()
            A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
            for v in ker: accumulated.append(v)
        M = np.array(accumulated, dtype=np.int64)
        D_span = rank_mod(M, p)

        # Get a basis of the span
        basis_built = build_8dim_span(NEs, p, D, c, n_gammas=200)

        # Sample random points in span, check if in V_tet
        rng = np.random.default_rng(123)
        n_in = 0; n_samples = 1500
        for trial in range(n_samples):
            coefs = rng.integers(0, p, basis_built.shape[0])
            v = (coefs @ basis_built) % p
            s1 = v[:D]; s2 = v[D:]
            in_v, _ = is_in_v_tet_sub(s1, s2, NEs, p, c)
            if in_v: n_in += 1
        density = n_in / n_samples
        log_p = math.log(density) / math.log(p) if density > 0 else float('-inf')
        dim_est = basis_built.shape[0] + log_p
        print(f"  p={p}: D_span={basis_built.shape[0]}, in V_tet: {n_in}/{n_samples}, "
              f"dim≈{dim_est:.3f}")


if __name__ == '__main__':
    measure_at_c3()
