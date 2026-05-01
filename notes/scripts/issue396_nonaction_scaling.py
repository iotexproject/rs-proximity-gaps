"""q-scaling split of action vs non-action bad fibers for issue #396.

For each Note 0306 mixed rank-3 support and each q in the usual panel, this
script counts L1-good alpha1 rows with nonempty L2 bad alpha2 fibers and splits
their contribution by the Note 0310 stabilizer order:

    action      = stabilizer order > 1,
    non-action  = identity only.

This is the scaling diagnostic for the remaining non-action/Bezout side of
the #396 proof split identified in Note 0311.
"""

from __future__ import annotations

import math
import os
import sys
import time
from collections import defaultdict

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import g3_pacc_qscaling as qscale
from fri_2round_attack import even_odd_parts, find_prim_root
from issue396_action_stabilizer import residual_uv, stabilizer_exponents
from issue396_mixed_fiber_scaling import MIXED_SUPPORTS, stable_coefs


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

    rows_total = rows_action = rows_nonaction = 0
    pairs_total = pairs_action = pairs_nonaction = 0
    max_action_fiber = max_nonaction_fiber = 0
    l1_bad_rows = 0

    for alpha1 in range(p):
        fold1_arr = (fe_arr + alpha1 * fo_arr) % p
        extras_l1 = qscale.batched_extras(
            ctx["info_sets_n1"], fold1_arr, ctx["L1_arr"], ctx["D1"], ctx["inv_D1"], p
        )
        d1 = n1 - k1 - int(extras_l1.max())
        if d1 <= w_J_L1:
            l1_bad_rows += 1
            continue

        fold1_e, fold1_o = even_odd_parts(fold1_arr.tolist(), ctx["L1"], p)
        bad_count, _ = qscale.compute_d2_and_count(
            fold1_e, fold1_o, ctx["lagrange_pairs"], p, n2, k2, w_J_L2
        )
        if bad_count == 0:
            continue

        rows_total += 1
        pairs_total += bad_count
        u, v = residual_uv(support, coefs, alpha1, p, n2)
        stab_order = len(stabilizer_exponents(u, v, omega2, p))
        if stab_order > 1:
            rows_action += 1
            pairs_action += bad_count
            max_action_fiber = max(max_action_fiber, bad_count)
        else:
            rows_nonaction += 1
            pairs_nonaction += bad_count
            max_nonaction_fiber = max(max_nonaction_fiber, bad_count)

    return {
        "l1_bad_rows": l1_bad_rows,
        "rows_total": rows_total,
        "rows_action": rows_action,
        "rows_nonaction": rows_nonaction,
        "pairs_total": pairs_total,
        "pairs_action": pairs_action,
        "pairs_nonaction": pairs_nonaction,
        "max_action_fiber": max_action_fiber,
        "max_nonaction_fiber": max_nonaction_fiber,
    }


def main():
    n0, k0, R = 32, 8, 2
    primes = [97, 193, 257, 449, 577, 769, 1153]
    print("Issue #396 non-action scaling diagnostic")
    print(f"(n0,k0)=({n0},{k0}), R={R}")
    print("rows_* count L1-good alpha1 rows with nonempty L2 bad fibers")
    print()

    aggregate = defaultdict(lambda: defaultdict(list))
    t0 = time.time()
    for p in primes:
        print(f"=== q={p} ===", flush=True)
        ctx = qscale.setup_q_context(p, n0, k0, R)
        for support in MIXED_SUPPORTS:
            r = analyze_support(support, ctx)
            for key, value in r.items():
                aggregate[support][key].append(value)
            print(
                f"sup={support} mod4={tuple(j % 4 for j in support)} "
                f"l1bad={r['l1_bad_rows']} "
                f"rows={r['rows_total']} action_rows={r['rows_action']} "
                f"nonaction_rows={r['rows_nonaction']} "
                f"pairs={r['pairs_total']} action_pairs={r['pairs_action']} "
                f"nonaction_pairs={r['pairs_nonaction']} "
                f"maxA={r['max_action_fiber']} maxNA={r['max_nonaction_fiber']}",
                flush=True,
            )
        del ctx
        print(flush=True)

    print("=== per-support non-action summary ===")
    for support in MIXED_SUPPORTS:
        rows = aggregate[support]["rows_nonaction"]
        pairs = aggregate[support]["pairs_nonaction"]
        action_pairs = aggregate[support]["pairs_action"]
        print(
            f"sup={support} "
            f"nonaction_rows={rows} "
            f"nonaction_pairs={pairs} "
            f"action_pairs={action_pairs}"
        )
    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
