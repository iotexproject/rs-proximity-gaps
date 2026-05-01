"""issue396_l2_fiber_distribution.py

Extract the L_2 bad-fiber distribution behind Note 0168.

For each fixed alpha_1, let

    B_2(alpha_1) = {alpha_2 in F_q : fold^2_{alpha_1,alpha_2}(f)
                    is within the Johnson threshold on L_2}.

Note 0168 only records sum_alpha1 |B_2(alpha_1)|.  Issue #396 needs the
distribution of these fiber sizes: full columns, residual singletons, and
zero columns.  This script reuses the Note 0168 computation but prints the
fiber histogram, split by whether alpha_1 is already bad at L_1.
"""

import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import g3_pacc_qscaling as qscale
from fri_2round_attack import even_odd_parts
from mds_decoder import batched_extras


SIGMA_EMPTY_SUPPORTS = [
    (8, 9, 20), (8, 9, 21), (10, 11, 22), (10, 11, 23),
    (12, 13, 16), (12, 13, 17), (14, 15, 18), (14, 15, 19),
    (16, 28, 29), (17, 28, 29), (18, 30, 31), (19, 30, 31),
    (20, 24, 25), (21, 24, 25), (22, 26, 27), (23, 26, 27),
]
SIGMA_9_SUPPORTS = [
    (9, 20, 21), (11, 22, 23), (13, 16, 17), (15, 18, 19),
    (16, 17, 29), (18, 19, 31), (20, 21, 25), (22, 23, 27),
]
ALL_SUPPORTS = [(s, "sigma=()") for s in SIGMA_EMPTY_SUPPORTS] + [
    (s, "sigma_9=0") for s in SIGMA_9_SUPPORTS
]


def deterministic_coefs(support):
    rng = random.Random(hash(support) & 0xFFFFFFFF)
    return [rng.randrange(1, 10**6) for _ in range(3)]


def fiber_distribution_for_support(support, coefs, ctx):
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
    d_f_lower = n0 - k0 - int(extras_l0.max())
    if d_f_lower <= w_J_L0:
        return None

    f_e, f_o = even_odd_parts(f, ctx["L0"], p)
    fe_arr = np.array(f_e, dtype=np.int64)
    fo_arr = np.array(f_o, dtype=np.int64)

    hist_all = Counter()
    hist_l1_bad = Counter()
    hist_l1_good = Counter()
    V_delta = 0
    bad_a1 = 0

    for a1 in range(p):
        fold1_arr = (fe_arr + a1 * fo_arr) % p
        extras_l1 = batched_extras(
            ctx["info_sets_n1"], fold1_arr, ctx["L1_arr"],
            ctx["D1"], ctx["inv_D1"], p
        )
        d1 = n1 - k1 - int(extras_l1.max())
        is_l1_bad = d1 <= w_J_L1
        if is_l1_bad:
            bad_a1 += 1

        fold1 = fold1_arr.tolist()
        fold1_e, fold1_o = even_odd_parts(fold1, ctx["L1"], p)
        fiber_size, _ = qscale.compute_d2_and_count(
            fold1_e, fold1_o, ctx["lagrange_pairs"], p, n2, k2, w_J_L2
        )

        V_delta += fiber_size
        hist_all[fiber_size] += 1
        if is_l1_bad:
            hist_l1_bad[fiber_size] += 1
        else:
            hist_l1_good[fiber_size] += 1

    return {
        "d_f_lower": d_f_lower,
        "bad_a1": bad_a1,
        "V_delta": V_delta,
        "hist_all": hist_all,
        "hist_l1_bad": hist_l1_bad,
        "hist_l1_good": hist_l1_good,
    }


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def class_name(support):
    residues = {j % 4 for j in support}
    if residues <= {0, 1}:
        return "sym01"
    if residues <= {2, 3}:
        return "anti23"
    return "mixed"


def main():
    n0, k0, R = 32, 8, 2
    primes = [97, 193, 257, 449, 577, 769, 1153]

    print("Issue #396 L2 fiber distribution behind Note 0168")
    print(f"(n0,k0)=({n0},{k0}), R={R}")
    print("hist format: {fiber_size:number_of_alpha1}")
    print()

    global_pattern_counts = Counter()
    class_pattern_counts = defaultdict(Counter)
    t0 = time.time()

    for p in primes:
        print(f"=== q={p} ===", flush=True)
        ctx = qscale.setup_q_context(p, n0, k0, R)
        per_q_patterns = Counter()
        for idx, (support, label) in enumerate(ALL_SUPPORTS, start=1):
            result = fiber_distribution_for_support(
                support, deterministic_coefs(support), ctx
            )
            if result is None:
                print(f"[{idx:02d}/24] sup={support} below-J/skipped", flush=True)
                continue

            cls = class_name(support)
            hist_all = result["hist_all"]
            pattern = tuple(sorted(hist_all.items()))
            per_q_patterns[pattern] += 1
            global_pattern_counts[pattern] += 1
            class_pattern_counts[cls][pattern] += 1

            expected_sym = result["bad_a1"] * p
            expected_anti = result["bad_a1"] * p + (p - result["bad_a1"])
            if result["V_delta"] == expected_sym:
                formula = "bad_a1*q"
            elif result["V_delta"] == expected_anti:
                formula = "bad_a1*q+(q-bad_a1)"
            else:
                formula = "other"

            print(
                f"[{idx:02d}/24] sup={support} mod4={tuple(j % 4 for j in support)} "
                f"{label} {cls} d0>J_lower={result['d_f_lower']} "
                f"bad_a1={result['bad_a1']} V={result['V_delta']} formula={formula} "
                f"all={fmt_hist(result['hist_all'])} "
                f"L1bad={fmt_hist(result['hist_l1_bad'])} "
                f"L1good={fmt_hist(result['hist_l1_good'])}",
                flush=True,
            )
        print("patterns this q:")
        for pattern, count in sorted(per_q_patterns.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {count:2d} x {dict(pattern)}")
        print(flush=True)
        del ctx

    print("=== aggregate patterns over all q/support cases ===")
    for pattern, count in sorted(global_pattern_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{count:3d} x {dict(pattern)}")

    print("=== aggregate by mod-4 class ===")
    for cls in sorted(class_pattern_counts):
        print(cls)
        for pattern, count in sorted(class_pattern_counts[cls].items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {count:3d} x {dict(pattern)}")

    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
