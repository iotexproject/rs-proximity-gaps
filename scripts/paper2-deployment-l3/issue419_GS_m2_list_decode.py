"""Guruswami-Sudan multiplicity-2 list decoder for RS(128, 32) at L_0 = mu_128.

For each L3 stratum (B) case, lift to (f_1, f_2) at L_0.
For each alpha in F_p, build pencil g_alpha = f_1 + alpha * f_2.
Run GS m=2 list decode at agreement threshold tau >= 71.
Count K_GS_2 := #{alpha : list non-empty}.

GS m=2 parameters at (n=128, k=32):
  Multiplicity m = 2 (3 constraints per point)
  Weighted (1, 31) degree D such that #monomials > 384 (= n * m(m+1)/2)
  Decoding threshold: t > D/m
  Choosing D = 140: #mon = 395 > 384, t > 70 -> tau >= 71

This UPGRADES "K_BW <= 2 unique-decoding" (agreement >= 80) to
"K_GS_2 <= ?" at agreement >= 71. Combined with empirical sweep, addresses
the [65, 79] gap to a large extent.
"""

from __future__ import annotations

import os
import random
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from _l3_helpers import subgroup
from issue419_K16_K_count import (
    split_kernel,
    evaluate_at_L0,
    hamming_zero,
)
from _l3_helpers import rank_mod_p, kernel_mod_p, sample_no_full_S
from issue419_decouple_check import zeros_on_L2


# ------------------------------------------------------------------
# Mod-p linear algebra (pure Python, int arithmetic)
# ------------------------------------------------------------------

def mod_inv(a, p):
    return pow(a, p - 2, p)


def gauss_null_space(A, p, n_cols):
    """Return basis of null space of A over F_p. Rows-by-row Gauss-Jordan.

    A: list of rows (each a list of ints), rows do not all need same length.
    n_cols: total #cols.
    """
    M = [row[:] for row in A]
    n_rows = len(M)
    pivot_col_for_row = [-1] * n_rows
    rank = 0
    col = 0
    while rank < n_rows and col < n_cols:
        # Find pivot
        pivot = None
        for r in range(rank, n_rows):
            if M[r][col] % p:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        inv = mod_inv(M[rank][col], p)
        M[rank] = [(x * inv) % p for x in M[rank]]
        for r in range(n_rows):
            if r != rank and M[r][col] % p:
                f = M[r][col]
                M[r] = [(a - f * b) % p for a, b in zip(M[r], M[rank])]
        pivot_col_for_row[rank] = col
        rank += 1
        col += 1

    pivot_set = set(pivot_col_for_row[:rank])
    free_cols = [c for c in range(n_cols) if c not in pivot_set]
    null = []
    for fc in free_cols:
        v = [0] * n_cols
        v[fc] = 1
        for r in range(rank):
            pc = pivot_col_for_row[r]
            v[pc] = (-M[r][fc]) % p
        null.append(v)
    return null


# ------------------------------------------------------------------
# GS interpolation (multiplicity 2)
# ------------------------------------------------------------------

def enum_monomials(D, k):
    """Enumerate (i, j) with i >= 0, j >= 0, i + (k-1)*j <= D."""
    out = []
    j = 0
    while (k - 1) * j <= D:
        for i in range(D - (k - 1) * j + 1):
            out.append((i, j))
        j += 1
    return out


def build_gs_m2_matrix(g_vals, x_vals, p, monomials):
    """Build interpolation matrix for multiplicity-2 GS.

    Constraints per point (x, g):
      Q(x, g) = 0
      d/dx Q (x, g) = 0
      d/dy Q (x, g) = 0

    Q(x, y) = sum_{(i,j) in mon} q_{i,j} x^i y^j
    Q(x, g)        = sum q_{i,j} * x^i * g^j
    d/dx Q (x, g)  = sum i * q_{i,j} * x^{i-1} * g^j
    d/dy Q (x, g)  = sum j * q_{i,j} * x^i * g^{j-1}
    """
    n = len(x_vals)
    max_i = max(i for i, _ in monomials)
    max_j = max(j for _, j in monomials)
    rows = []
    for idx in range(n):
        x = x_vals[idx] % p
        g = g_vals[idx] % p
        # Powers
        x_pow = [1] * (max_i + 2)
        for i in range(1, len(x_pow)):
            x_pow[i] = (x_pow[i - 1] * x) % p
        g_pow = [1] * (max_j + 2)
        for j in range(1, len(g_pow)):
            g_pow[j] = (g_pow[j - 1] * g) % p

        # Build three rows for this point
        row0 = [(x_pow[i] * g_pow[j]) % p for (i, j) in monomials]
        row1 = [
            (i * x_pow[i - 1] * g_pow[j]) % p if i >= 1 else 0
            for (i, j) in monomials
        ]
        row2 = [
            (j * x_pow[i] * g_pow[j - 1]) % p if j >= 1 else 0
            for (i, j) in monomials
        ]
        rows.append(row0)
        rows.append(row1)
        rows.append(row2)
    return rows


# ------------------------------------------------------------------
# Roth-Ruckenstein y-root extraction
# ------------------------------------------------------------------

def Q_eval_y(Q, c, p):
    """Evaluate Q(0, c) as polynomial in y."""
    R = []
    for (i, j), q in Q.items():
        if i == 0:
            while len(R) <= j:
                R.append(0)
            R[j] = (R[j] + q) % p
    s = 0
    cp = 1
    for coef in R:
        s = (s + coef * cp) % p
        cp = (cp * c) % p
    return s % p


def find_y_roots_at_x0(Q, p):
    """Find all c in F_p such that Q(0, c) = 0.

    Returns (roots, R_zero) where R_zero is True iff Q(0, y) is the zero
    polynomial (in which case the caller should factor x out of Q and
    recurse, since every c is formally a root)."""
    R = []
    for (i, j), q in Q.items():
        if i == 0:
            while len(R) <= j:
                R.append(0)
            R[j] = (R[j] + q) % p
    while R and R[-1] % p == 0:
        R.pop()
    if not R:
        return [], True
    roots = []
    for c in range(p):
        s = 0
        cp = 1
        for coef in R:
            s = (s + coef * cp) % p
            cp = (cp * c) % p
        if s % p == 0:
            roots.append(c)
    return roots, False


def factor_x_out(Q):
    """If x | Q(x, y), return Q' such that Q(x, y) = x * Q'(x, y); else None."""
    if not Q:
        return None
    m = min(i for (i, j) in Q.keys())
    if m <= 0:
        return None
    return {(i - m, j): v for (i, j), v in Q.items()}


def binomial(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(k):
        num *= n - i
        den *= i + 1
    return num // den


def Q_substitute_and_shift(Q, c0, p):
    """Compute Q'(x, y) = Q(x, c0 + x * y) / x^{m1}.

    Returns (Q', m1). If m1 = 0 means the substitution did not introduce a
    common x factor (shouldn't happen if c0 was a true root of Q(0, y)).
    """
    Q_subst = {}
    # (c0 + x y)^j = sum_l C(j, l) c0^{j-l} x^l y^l
    for (i, j), q in Q.items():
        if q % p == 0:
            continue
        # Precompute powers of c0
        c0_pow = [1] * (j + 1)
        for u in range(1, j + 1):
            c0_pow[u] = (c0_pow[u - 1] * c0) % p
        for l in range(j + 1):
            coef = (q * binomial(j, l) * c0_pow[j - l]) % p
            if coef == 0:
                continue
            key = (i + l, l)
            Q_subst[key] = (Q_subst.get(key, 0) + coef) % p
    # Trim zeros
    Q_subst = {k_: v for k_, v in Q_subst.items() if v % p != 0}
    if not Q_subst:
        return {}, 0
    m1 = min(i for (i, j) in Q_subst.keys())
    Q_next = {(i - m1, j): v for (i, j), v in Q_subst.items()}
    return Q_next, m1


def roth_ruckenstein(Q, depth_limit, p):
    """Return all coefficient lists [c_0, c_1, ..., c_{t-1}] (t <= depth_limit)
    of polynomials p(x) with deg < depth_limit and Q(x, p(x)) = 0.

    We use depth_limit = k (deg p < k).
    """
    if depth_limit == 0:
        # No more coefficients; verify Q(x, 0) is not "needed" -- handled by caller.
        return [[]]

    # Find roots c_0 of Q(0, y). If Q(0, y) ≡ 0 then x | Q(x, y); factor x out
    # and retry. This recovers messages whose interpolation polynomial vanishes
    # along x = 0 (the case codex flagged 2026-05-06).
    roots, R_zero = find_y_roots_at_x0(Q, p)
    if R_zero:
        Q_x_factored = factor_x_out(Q)
        if Q_x_factored is None or not Q_x_factored:
            return []
        return roth_ruckenstein(Q_x_factored, depth_limit, p)
    if not roots:
        return []

    results = []
    for c0 in roots:
        Q_next, m1 = Q_substitute_and_shift(Q, c0, p)
        if not Q_next:
            # Q'(x, y) is identically zero -> any extension works. In particular,
            # p(x) = c_0 (constant) is a root.
            results.append([c0])
            continue
        # If Q' is a nonzero constant, then no further root extension yields 0.
        # In that case (and if Q'(0, 0) != 0), no root has p(0) = c_0.
        # But if Q' has a nonzero constant + nontrivial variable terms, we recurse.
        sub_roots = roth_ruckenstein(Q_next, depth_limit - 1, p)
        for sr in sub_roots:
            # Reconstruct: full root coefficients
            full = [c0] + sr
            results.append(full)
    return results


# ------------------------------------------------------------------
# GS m=2 list decoder (full pipeline)
# ------------------------------------------------------------------

def gs_m2_list_decode(g_vals, x_vals, p, k, D):
    """Run GS m=2 with weighted (1, k-1) degree D.

    Returns list of polynomials p(x) (as coefficient lists, low to high)
    such that Q(x, p(x)) = 0 for some Q in nullspace.
    """
    monomials = enum_monomials(D, k)
    n_mon = len(monomials)
    n = len(g_vals)
    n_constraints = 3 * n
    if n_constraints >= n_mon:
        # System over-determined; nullspace might still be non-trivial but rare.
        pass

    A = build_gs_m2_matrix(g_vals, x_vals, p, monomials)
    null = gauss_null_space(A, p, n_mon)
    if not null:
        return []

    candidates_set = set()
    candidates = []
    for v in null:
        # Build Q from coefficients
        Q = {}
        for (mon, coef) in zip(monomials, v):
            if coef % p != 0:
                Q[mon] = coef % p
        if not Q:
            continue
        roots = roth_ruckenstein(Q, k, p)
        for r in roots:
            # Trim trailing zeros to canonicalize
            r2 = list(r)
            while r2 and r2[-1] % p == 0:
                r2.pop()
            tup = tuple(c % p for c in r2)
            if tup in candidates_set:
                continue
            candidates_set.add(tup)
            candidates.append(r2)
    return candidates


# ------------------------------------------------------------------
# Agreement verification
# ------------------------------------------------------------------

def poly_eval(P, x, p):
    s = 0
    xp = 1
    for c in P:
        s = (s + c * xp) % p
        xp = (xp * x) % p
    return s


def agreement(P, g_vals, x_vals, p):
    return sum(1 for i, x in enumerate(x_vals) if poly_eval(P, x, p) == g_vals[i] % p)


# ------------------------------------------------------------------
# Main: stratify and decode
# ------------------------------------------------------------------

def stratify(c, rs, p, omega_L2, n2):
    u_terms, v_terms = split_kernel(c, rs)
    Z_u = set(zeros_on_L2(u_terms, omega_L2, p, n2))
    Z_v = set(zeros_on_L2(v_terms, omega_L2, p, n2))
    T = Z_u & Z_v
    if Z_u != Z_v:
        return 'C', len(T)
    if len(T) >= n2 // 2:
        return 'A', len(T)
    return 'B', len(T)


def find_stratum_B_cases(rng, n_per_seed, p, omega_L2, n2, k2, n_u=8, n_v=8, max_seeds=200):
    samples = sample_no_full_S(n2, k2, 500)
    u_side = [r for r in range(k2, n2) if r % 4 in (0, 1)]
    v_side = [r for r in range(k2, n2) if r % 4 in (2, 3)]

    found = []
    for _ in range(max_seeds):
        if len(found) >= n_per_seed:
            break
        u_cfg = rng.sample(u_side, n_u)
        v_cfg = rng.sample(v_side, n_v)
        rs = sorted(u_cfg + v_cfg)
        for S in samples[:50]:
            M = [[pow(omega_L2, r * s, p) for s in S] for r in rs]
            if rank_mod_p(M, p) < len(rs):
                c = kernel_mod_p(M, p)
                if c:
                    stratum, T_size = stratify(c, rs, p, omega_L2, n2)
                    if stratum == 'B':
                        found.append((rs, S, c, T_size))
                        break
    return found


def run_for_prime(p, n_cases, n2, k2, n0, k0, D_gs, tau_gs, seed, out_handle=None):
    L2 = subgroup(n2, p)
    omega_L2 = L2[1]
    L0 = subgroup(n0, p)
    omega_L0 = L0[1]
    x_vals = [pow(omega_L0, i, p) for i in range(n0)]

    def emit(line):
        print(line, flush=True)
        if out_handle is not None:
            out_handle.write(line + "\n")
            out_handle.flush()

    rng = random.Random(seed)
    cases = find_stratum_B_cases(
        rng, n_per_seed=n_cases, p=p, omega_L2=omega_L2, n2=n2, k2=k2
    )
    emit(f"\n##### prime p={p}: found {len(cases)} stratum (B) cases #####")

    K_BW_arr = []
    K_GS_arr = []
    max_list_arr = []

    for case_idx, (rs, S, c, T_size) in enumerate(cases):
        u_terms, v_terms = split_kernel(c, rs)
        f1 = evaluate_at_L0(u_terms, omega_L0, p, n0)
        f2 = evaluate_at_L0(v_terms, omega_L0, p, n0)

        K_BW = 0
        K_GS = 0
        max_agr_zero = 0
        max_list = 0

        for alpha in range(p):
            g = [(f1[i] + alpha * f2[i]) % p for i in range(n0)]
            agr_zero = hamming_zero(g, p)
            if agr_zero >= 80:
                K_BW += 1
            if agr_zero > max_agr_zero:
                max_agr_zero = agr_zero
            if agr_zero >= tau_gs:
                K_GS += 1
                if 1 > max_list:
                    max_list = 1
                continue
            try:
                cands = gs_m2_list_decode(g, x_vals, p, k0, D_gs)
            except Exception as e:
                # An exception means we don't know K_GS for this alpha; an empty
                # list would silently undercount the upper bound. Fail loudly so
                # the run is flagged rather than silently misreported.
                raise RuntimeError(
                    f"gs_m2_list_decode raised at alpha={alpha} (T_size={T_size}, "
                    f"prime={p}, support={S}); cannot continue without "
                    f"undercounting K_GS_2"
                ) from e
            verified = [c for c in cands if agreement(c, g, x_vals, p) >= tau_gs]
            if verified:
                K_GS += 1
                if len(verified) > max_list:
                    max_list = len(verified)

        emit(
            f"  case {case_idx+1}/{len(cases)} |T|={T_size}: "
            f"K_BW={K_BW}, K_GS_2={K_GS}, "
            f"max_agr_to_0={max_agr_zero}, max_list={max_list}"
        )
        K_BW_arr.append(K_BW)
        K_GS_arr.append(K_GS)
        max_list_arr.append(max_list)

    emit(
        f"  prime p={p} totals: max(K_BW)={max(K_BW_arr) if K_BW_arr else 0}, "
        f"max(K_GS_2)={max(K_GS_arr) if K_GS_arr else 0}, "
        f"max(list)={max(max_list_arr) if max_list_arr else 0}"
    )
    return K_BW_arr, K_GS_arr, max_list_arr


def main():
    n2, k2 = 32, 8
    n0, k0 = 128, 32
    D_gs = 140
    tau_gs = 71

    primes = [257, 641, 769, 1153]
    n_cases_per_prime = 6  # tunable
    seed_base = 0xCAFEBABE

    monomials = enum_monomials(D_gs, k0)
    out_path = os.path.join(SCRIPT_DIR, "issue419_GS_m2_list_decode_output.txt")
    with open(out_path, "w") as f:
        def emit(s):
            print(s, flush=True)
            f.write(s + "\n")
            f.flush()

        emit(f"GS m=2 setup: D={D_gs}, #mon={len(monomials)}, "
             f"#constraints={3*n0}, tau_gs={tau_gs}")
        emit(f"primes={primes}, n_cases_per_prime={n_cases_per_prime}")

        all_K_BW = []
        all_K_GS = []
        all_max_list = []
        for p in primes:
            K_BW, K_GS, M_list = run_for_prime(
                p, n_cases_per_prime, n2, k2, n0, k0, D_gs, tau_gs,
                seed=seed_base + p,
                out_handle=f,
            )
            all_K_BW.extend(K_BW)
            all_K_GS.extend(K_GS)
            all_max_list.extend(M_list)

        emit("\n" + "=" * 60)
        emit("OVERALL SUMMARY (all primes)")
        emit("=" * 60)
        emit(f"Total cases: {len(all_K_BW)}")
        emit(f"max(K_BW) across all cases     = "
             f"{max(all_K_BW) if all_K_BW else 0}")
        emit(f"max(K_GS_2) across all cases   = "
             f"{max(all_K_GS) if all_K_GS else 0}")
        emit(f"max(list size) across all cases= "
             f"{max(all_max_list) if all_max_list else 0}")
        emit(f"K_GS_2 distribution: {Counter(all_K_GS)}")
        emit(f"\nVerdict: max(K_GS_2) <= 10 means structural upgrade at agreement >= {tau_gs}.")
        emit(f"Remaining empirical gap: agreement in [65, {tau_gs - 1}].")


if __name__ == "__main__":
    main()
