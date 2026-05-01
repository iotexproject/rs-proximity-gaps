#!/usr/bin/env python3 -u
"""Verify Note 0114's geometric formula dim V_tet_sub(V) = 2(w'+1) at varying w'.

The disproof in Note 0114 was at w' = w-1 (largest sub-tet at c=4 n=16).
The geometric argument (V_tet_sub(V) = V_V × V_V) predicts the same formula
holds at every w' in the bad-realizing range, independent of extras U.

Bad-realizing conditions:
  (a) w' ≥ T        (sub-tet contributes > T γ-values, qualifies as bad)
  (b) (w'-1)(c-1) - 2(w-w') ≥ 1   (X_γ has positive dim — Note 0110)

We restrict the sweep to w' satisfying (a) AND (b).

Method: density-in-span (Note 0114). dim V_tet_sub ≈ D_span + log_p(density).
"""

import sys, math
import numpy as np
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega
from op2_clique_scan import rank_mod
from op2_tet_consolidated import make_NEs, solve_for_witness


def bad_realizing_X_dim(w_prime, w, c):
    return max(0, (w_prime - 1) * (c - 1) - 2 * (w - w_prime))


def build_span(NEs, p, D, c, m, n_gammas=200, seed=0):
    """Build linear span Σ_γ ker A(γ) ⊂ F_p^{2D} via row-reduction."""
    rng = np.random.default_rng(seed)
    accumulated = []
    for trial in range(n_gammas):
        gammas = (rng.choice(p - 1, size=m, replace=False) + 1).tolist()
        A, ker, rA = solve_for_witness(NEs, gammas, p, D, c)
        for v in ker:
            accumulated.append(v)
    if not accumulated:
        return np.zeros((0, 2 * D), dtype=np.int64)
    M_rref = np.array(accumulated, dtype=np.int64) % p
    R, C = M_rref.shape
    pivot_cols = []
    r = 0
    for col in range(C):
        if r >= R: break
        pv = None
        for i in range(r, R):
            if M_rref[i, col] != 0: pv = i; break
        if pv is None: continue
        M_rref[[r, pv]] = M_rref[[pv, r]]
        inv = pow(int(M_rref[r, col]), p - 2, p)
        M_rref[r] = (M_rref[r] * inv) % p
        for i in range(R):
            if i != r and M_rref[i, col] != 0:
                M_rref[i] = (M_rref[i] - M_rref[i, col] * M_rref[r]) % p
        pivot_cols.append(col); r += 1
    return M_rref[:r]


def is_in_v_tet_sub(s1, s2, NEs, p, c):
    """Check ∃ distinct γ_i ∈ F_p^* s.t. s_1 + γ_i s_2 ∈ V_{E_i}."""
    gammas = []
    for N in NEs:
        aE = (N @ s2) % p
        bE = (N @ s1) % p
        nz = next((j for j in range(c) if aE[j] != 0), None)
        if nz is None:
            if any(bE):
                return False, None
            gammas.append('free'); continue
        g = (-int(bE[nz]) * pow(int(aE[nz]), p - 2, p)) % p
        prop = all(
            (int(aE[j_]) * int(bE[k_]) - int(aE[k_]) * int(bE[j_])) % p == 0
            for j_ in range(c) for k_ in range(c)
        )
        if not prop or g == 0:
            return False, None
        gammas.append(g)
    fixed = [g for g in gammas if g != 'free']
    if len(set(fixed)) != len(fixed): return False, gammas
    n_free = sum(1 for g in gammas if g == 'free')
    if n_free > 0 and len(fixed) + n_free > p - 1:
        return False, gammas
    return True, gammas


def measure_one(n, c, w_prime, V, U, p, n_gammas=200, n_samples=1500):
    D = n - n // 2; w = D - c
    omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
    extras_size = w - w_prime
    m = w_prime + 1
    Es = []
    for i in range(m):
        if extras_size == 0:
            U_i = []
        else:
            U_i = U[i * extras_size:(i + 1) * extras_size]
        E_i = tuple(sorted(set(V) - {V[i]} | set(U_i)))
        if V[i] in E_i: return None
        if len(E_i) != w: return None
        Es.append(E_i)
    NEs = make_NEs(Es, L, p, D, c, w)
    basis = build_span(NEs, p, D, c, m, n_gammas=n_gammas)
    D_span = basis.shape[0]
    if D_span == 0:
        return {'D_span': 0, 'density': 0, 'dim_est': float('-inf'),
                'predicted': 2 * m, 'bad_X': bad_realizing_X_dim(w_prime, w, c),
                'in_v': 0, 'n_samples': n_samples}
    rng = np.random.default_rng(123)
    n_in = 0
    for trial in range(n_samples):
        coefs = rng.integers(0, p, D_span)
        v = (coefs @ basis) % p
        s1 = v[:D]; s2 = v[D:]
        in_v, _ = is_in_v_tet_sub(s1, s2, NEs, p, c)
        if in_v: n_in += 1
    density = n_in / n_samples
    log_p_density = math.log(max(density, 1e-12)) / math.log(p) if density > 0 else float('-inf')
    dim_est = D_span + log_p_density if density > 0 else float('-inf')
    return {
        'D_span': D_span, 'in_v': n_in, 'n_samples': n_samples,
        'density': density, 'dim_est': dim_est,
        'predicted': 2 * m,
        'bad_X': bad_realizing_X_dim(w_prime, w, c),
    }


def sweep():
    """Cases with multiple bad-realizing w'."""
    cases = [
        # (n, c) — sweep w' ∈ [T, w-1] with X-dim ≥ 1
        (12, 3),  # T=3, w=3 → only w'=3 (full tet)
        (16, 4),  # T=3, w=4 → only w'=3 (Note 0114 case)
        (20, 4),  # T=4, w=6 → w' ∈ {4,5}
        (20, 5),  # T=3, w=5 → w' ∈ {3,4}
        (24, 4),  # T=5, w=8 → w' ∈ {5,6,7}
        (24, 5),  # T=4, w=7 → w' ∈ {4,5,6}
    ]
    primes_priority = [1009, 449, 257, 193, 97, 41, 17]
    print("=== dim V_tet_sub vs predicted 2(w'+1) at varying w' ===\n")
    print(f"{'n':>3} {'c':>3} {'w':>3} {'T':>3} {'wp':>3} {'pred':>5} {'D_span':>7} "
          f"{'in/N':>10} {'dim_est':>9} {'X_dim':>6} {'verdict':>10}")
    for n, c in cases:
        D = n - n // 2; w = D - c
        T = (2 * D - 1) // c
        p = next((q for q in primes_priority if (q - 1) % n == 0), None)
        if p is None:
            print(f"  (no prime found for n={n})"); continue
        # Sweep w' ∈ [max(2, T), w] with X_dim ≥ 1
        for w_prime in range(max(2, T), w + 1):
            X_dim = bad_realizing_X_dim(w_prime, w, c)
            if X_dim < 1:
                # not bad-realizing; expect V_tet_sub empty/lower-dim
                continue
            extras_size = w - w_prime
            m = w_prime + 1
            V = list(range(m))
            need_extras = extras_size * m
            U = list(range(m, m + need_extras)) if need_extras > 0 else []
            if m + need_extras > n:
                continue
            result = measure_one(n, c, w_prime, V, U, p)
            if result is None:
                print(f"{n:>3} {c:>3} {w:>3} {T:>3} {w_prime:>3}  (build failed)")
                continue
            pred = result['predicted']
            if result['density'] == 0:
                verdict = 'EMPTY'
            elif abs(result['dim_est'] - pred) < 0.6:
                verdict = 'match'
            else:
                verdict = 'MISMATCH'
            print(f"{n:>3} {c:>3} {w:>3} {T:>3} {w_prime:>3} {pred:>5} "
                  f"{result['D_span']:>7} "
                  f"{result['in_v']:>4}/{result['n_samples']:>3} "
                  f"{result['dim_est']:>9.3f} "
                  f"{result['bad_X']:>6} {verdict:>10} (p={p})")


if __name__ == '__main__':
    sweep()
