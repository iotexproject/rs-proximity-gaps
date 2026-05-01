"""issue396_mixed_fiber_scaling.py

Probe the L_2 bad-fiber distribution for mixed mod-4 rank-3 supports.

Note 0305 showed that the Note 0168 separated supports have trivial
fiber histograms ({0,q} or {1,q}).  Issue #396 then asks whether the
remaining mixed supports are the genuine Niho/cross-correlation regime.

This script uses stable, q-independent coefficients and tracks the
per-alpha_1 fiber histogram for a fixed panel of mixed supports across
several q == 1 mod 32 primes.
"""

import math
import os
import random
import sys
import time
from collections import Counter, defaultdict

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import g3_pacc_qscaling as qscale
from fri_2round_attack import even_odd_parts
from mds_decoder import batched_extras


MIXED_SUPPORTS = [
    (13, 14, 16),
    (9, 19, 27),
    (18, 25, 26),
    (21, 29, 30),
    (10, 24, 30),
    (11, 16, 23),
    (23, 25, 31),
    (8, 21, 26),
    (8, 14, 23),
    (11, 12, 30),
    (15, 21, 24),
    (8, 18, 29),
    (22, 24, 29),
    (19, 21, 24),
    (16, 23, 24),
    (10, 12, 14),
]


def stable_coefs(support):
    seed = 0x39600000
    for j in support:
        seed = ((seed * 1000003) ^ (j + 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    return [rng.randrange(1, 10**6) for _ in support]


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def analyze_support(support, coefs, ctx):
    p = ctx["p"]
    n0 = ctx["n0"]
    k0 = ctx["k0"]
    n1 = ctx["n1"]
    k1 = ctx["k1"]
    n2 = ctx["n2"]
    k2 = ctx["k2"]
    w_J_L0 = n0 - int(math.isqrt(k0 * n0))
    w_J_L1 = n1 - int(math.isqrt(k1 * n1))
    w_J_L2 = n2 - int(math.isqrt(k2 * n2))

    fhat = [0] * n0
    for j, c in zip(support, coefs):
        fhat[j] = c % p

    f = qscale.evaluate_dft(fhat, ctx["L0"], p)
    f_arr = np.array(f, dtype=np.int64)
    extras_l0 = batched_extras(
        ctx["info_sets_n0"], f_arr, ctx["L0_arr"], ctx["D0"], ctx["inv_D0"], p
    )
    # This is a sampled lower bound at L0, inherited from qscale setup.
    d0_lower = n0 - k0 - int(extras_l0.max())

    f_e, f_o = even_odd_parts(f, ctx["L0"], p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    hist = Counter()
    hist_l1_bad = Counter()
    hist_l1_good = Counter()
    b1 = 0
    v_delta = 0
    max_fiber_good = 0
    max_fiber = 0

    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        extras_l1 = batched_extras(
            ctx["info_sets_n1"], fold1_arr, ctx["L1_arr"], ctx["D1"], ctx["inv_D1"], p
        )
        d1 = n1 - k1 - int(extras_l1.max())
        is_l1_bad = d1 <= w_J_L1
        if is_l1_bad:
            b1 += 1

        fold1_e, fold1_o = even_odd_parts(fold1_arr.tolist(), ctx["L1"], p)
        fiber_size, _ = qscale.compute_d2_and_count(
            fold1_e, fold1_o, ctx["lagrange_pairs"], p, n2, k2, w_J_L2
        )
        hist[fiber_size] += 1
        v_delta += fiber_size
        max_fiber = max(max_fiber, fiber_size)
        if is_l1_bad:
            hist_l1_bad[fiber_size] += 1
        else:
            hist_l1_good[fiber_size] += 1
            max_fiber_good = max(max_fiber_good, fiber_size)

    return {
        "d0_lower": d0_lower,
        "l0_sample_above": d0_lower > w_J_L0,
        "b1": b1,
        "v_delta": v_delta,
        "v_over_q": v_delta / p,
        "hist": hist,
        "hist_l1_bad": hist_l1_bad,
        "hist_l1_good": hist_l1_good,
        "max_fiber": max_fiber,
        "max_fiber_good": max_fiber_good,
    }


def main():
    n0, k0, R = 32, 8, 2
    primes = [97, 193, 257, 449, 577, 769, 1153]

    print("Issue #396 mixed-support L2 fiber scaling")
    print(f"(n0,k0)=({n0},{k0}), R={R}")
    print("stable coefficients: q-independent deterministic seed")
    print("hist format: {fiber_size:number_of_alpha1}")
    print()

    t0 = time.time()
    aggregate_max = defaultdict(int)
    aggregate_v_over_q = defaultdict(list)

    for p in primes:
        print(f"=== q={p} ===", flush=True)
        ctx = qscale.setup_q_context(p, n0, k0, R)
        for support in MIXED_SUPPORTS:
            result = analyze_support(support, stable_coefs(support), ctx)
            key = tuple(j % 4 for j in support)
            aggregate_max[support] = max(aggregate_max[support], result["max_fiber_good"])
            aggregate_v_over_q[support].append(result["v_over_q"])
            print(
                f"sup={support} mod4={key} "
                f"d0_lower={result['d0_lower']} "
                f"l0_sample_above={int(result['l0_sample_above'])} "
                f"b1={result['b1']} V={result['v_delta']} "
                f"V/q={result['v_over_q']:.4f} "
                f"max_fiber_good={result['max_fiber_good']} "
                f"hist={fmt_hist(result['hist'])} "
                f"L1bad={fmt_hist(result['hist_l1_bad'])} "
                f"L1good={fmt_hist(result['hist_l1_good'])}",
                flush=True,
            )
        print(flush=True)
        del ctx

    print("=== per-support scaling summary ===")
    for support in MIXED_SUPPORTS:
        vals = aggregate_v_over_q[support]
        vals_s = ", ".join(f"{v:.4f}" for v in vals)
        print(
            f"sup={support} mod4={tuple(j % 4 for j in support)} "
            f"max_good_fiber_any_q={aggregate_max[support]} "
            f"V/q=[{vals_s}]"
        )

    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
