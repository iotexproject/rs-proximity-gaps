"""Bad-alpha orbit decomposition for issue #396 residual pencils.

This combines the Note 0310 stabilizer test with the actual L2 bad-alpha2
sets.  The goal is to distinguish:

  * action-controlled rows, where bad alpha2 values are unions of projective
    orbits under a nontrivial diagonal substitution action; and
  * non-action rows, where the bad set must be bounded by a different
    incidence/Bezout argument.

The distance computation is the same L2 interpolation-pair test used in
issue396_mixed_fiber_scaling.py.
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import g3_pacc_qscaling as qscale
from fri_2round_attack import even_odd_parts, find_prim_root, modinv
from issue396_action_stabilizer import (
    RANK4_PROBES,
    residual_uv,
    stabilizer_exponents,
)
from issue396_mixed_fiber_scaling import MIXED_SUPPORTS, stable_coefs


SELECTED_SUPPORTS = [
    (13, 14, 16),  # Note 0306 worst: V=9q.
    (9, 19, 27),  # V=7q-6, order-2 generic action.
    (18, 25, 26), # V=5q-4, full action for most alpha1.
    (10, 24, 30), # identity-only but V=0.
    (8, 18, 29),  # identity-only generic, O(1) total badness.
    (1, 2, 6, 7), # Note 0304 rank-4 K=12 probe.
]


def bad_alpha2_set(fold1_e, fold1_o, lagrange_pairs, p, n2, k2, w_J_L2):
    extras_per_alpha = np.zeros(p, dtype=np.int16)
    # Need max over T, so maintain per-T row then maximize incrementally.
    max_extras = np.zeros(p, dtype=np.int16)
    fe = [int(x) for x in fold1_e]
    fo = [int(x) for x in fold1_o]
    for _T_idx, (i, j), kpairs in lagrange_pairs:
        extras_per_alpha.fill(0)
        always_count = 0
        targets = []
        for k, c_ik, c_jk in kpairs:
            de = (c_ik * fe[i] + c_jk * fe[j] - fe[k]) % p
            do = (c_ik * fo[i] + c_jk * fo[j] - fo[k]) % p
            if do == 0:
                if de == 0:
                    always_count += 1
            else:
                targets.append((-de * modinv(do, p)) % p)
        if always_count:
            extras_per_alpha += always_count
        for alpha2 in targets:
            extras_per_alpha[alpha2] += 1
        np.maximum(max_extras, extras_per_alpha, out=max_extras)
    d2 = (n2 - k2 - max_extras).astype(np.int16)
    return set(np.nonzero(d2 <= w_J_L2)[0].tolist())


def rank2_coordinates(u, v, target, p):
    n = len(u)
    for i in range(n):
        for j in range(i + 1, n):
            det = (u[i] * v[j] - u[j] * v[i]) % p
            if det:
                inv_det = modinv(det, p)
                a = ((target[i] * v[j] - target[j] * v[i]) * inv_det) % p
                b = ((u[i] * target[j] - u[j] * target[i]) * inv_det) % p
                return a, b
    return None


def action_matrix(u, v, omega2, mu_exp, p):
    n2 = len(u)
    du = [(u[e] * pow(omega2, mu_exp * e, p)) % p for e in range(n2)]
    dv = [(v[e] * pow(omega2, mu_exp * e, p)) % p for e in range(n2)]
    ac = rank2_coordinates(u, v, du, p)
    bd = rank2_coordinates(u, v, dv, p)
    if ac is None or bd is None:
        return None
    a, c = ac
    b, d = bd
    return a, b, c, d


def mobius_apply(M, alpha, p):
    a, b, c, d = M
    den = (a + alpha * b) % p
    num = (c + alpha * d) % p
    if den == 0:
        return None
    return (num * modinv(den, p)) % p


def orbit_decomp(bad, M, p):
    bad = set(bad)
    seen = set()
    sizes = []
    escapes = 0
    closed = True
    for alpha in sorted(bad):
        if alpha in seen:
            continue
        cur = alpha
        orbit = []
        local = set()
        while cur is not None and cur not in local:
            local.add(cur)
            orbit.append(cur)
            nxt = mobius_apply(M, cur, p)
            cur = nxt
        for x in local:
            seen.add(x)
        if cur is None:
            escapes += 1
            closed = False
        if any(x not in bad for x in local):
            closed = False
        sizes.append(len(local & bad))
    return closed, tuple(sorted(sizes)), escapes


def analyze_support(support, ctx):
    p = ctx["p"]
    n0 = ctx["n0"]
    n1 = ctx["n1"]
    k1 = ctx["k1"]
    n2 = ctx["n2"]
    k2 = ctx["k2"]
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))
    omega0 = find_prim_root(p, n0)
    omega2 = pow(omega0, 4, p)

    coefs = stable_coefs(support)
    fhat = [0] * n0
    for j, c in zip(support, coefs):
        fhat[j] = c % p

    f = qscale.evaluate_dft(fhat, ctx["L0"], p)
    f_e, f_o = even_odd_parts(f, ctx["L0"], p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    rows = []
    for alpha1 in range(p):
        fold1_arr = (fe_arr + alpha1 * fo_arr) % p
        extras_l1 = qscale.batched_extras(
            ctx["info_sets_n1"], fold1_arr, ctx["L1_arr"], ctx["D1"], ctx["inv_D1"], p
        )
        d1 = n1 - k1 - int(extras_l1.max())
        if d1 <= w_J_L1:
            continue

        fold1_e, fold1_o = even_odd_parts(fold1_arr.tolist(), ctx["L1"], p)
        bad = bad_alpha2_set(
            fold1_e, fold1_o, ctx["lagrange_pairs"], p, n2, k2, w_J_L2
        )
        if not bad:
            continue

        u, v = residual_uv(support, coefs, alpha1, p, n2)
        exps = stabilizer_exponents(u, v, omega2, p)
        non_id = [e for e in exps if e != 0]
        if non_id:
            M = action_matrix(u, v, omega2, non_id[0], p)
            if M is None:
                orbit_status = ("rank<2", (), 0)
            else:
                orbit_status = orbit_decomp(bad, M, p)
        else:
            orbit_status = (False, (), 0)
        rows.append((alpha1, len(bad), len(exps), exps, orbit_status, sorted(bad)[:16]))
    return rows


def summarize_rows(rows):
    size_hist = Counter(row[1] for row in rows)
    stab_hist = Counter(row[2] for row in rows)
    closed_hist = Counter(row[4][0] for row in rows)
    orbit_hist = Counter(row[4][1] for row in rows if row[4][1])
    return size_hist, stab_hist, closed_hist, orbit_hist


def main():
    p = 1153
    n0, k0, R = 32, 8, 2
    ctx = qscale.setup_q_context(p, n0, k0, R)
    print("Issue #396 bad-alpha2 orbit decomposition")
    print(f"field F_{p}, (n0,k0)=({n0},{k0}), L2 size={ctx['n2']}")
    print("Only L1-good rows with nonempty bad alpha2 set are shown/summarized.")
    print()

    for support in SELECTED_SUPPORTS:
        if support in MIXED_SUPPORTS:
            panel = "rank3-mixed"
        elif support in RANK4_PROBES:
            panel = "rank4-probe"
        else:
            panel = "custom"
        rows = analyze_support(support, ctx)
        size_hist, stab_hist, closed_hist, orbit_hist = summarize_rows(rows)
        print(f"=== {support} {panel} mod4={tuple(j % 4 for j in support)} ===")
        print(f"nonempty L1-good rows: {len(rows)}")
        print(f"bad_size_hist={dict(sorted(size_hist.items()))}")
        print(f"stab_order_hist={dict(sorted(stab_hist.items()))}")
        print(f"orbit_closed_hist={dict(sorted(closed_hist.items(), key=lambda kv: str(kv[0])))}")
        print(f"orbit_size_patterns={dict(orbit_hist.most_common(6))}")
        for row in rows[:5]:
            alpha1, bad_size, stab_order, exps, orbit_status, sample = row
            print(
                f"  a1={alpha1} bad={bad_size} stab={stab_order} "
                f"exps={exps} orbit={orbit_status} bad_sample={sample}"
            )
        if len(rows) > 5:
            print(f"  ... {len(rows) - 5} more rows")
        print()


if __name__ == "__main__":
    main()
