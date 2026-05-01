"""Scan saturated interpolation pairs for issue #396 base L2 pencils.

At L2=(8,2), a fixed-row pencil u+alpha v has a full-q bad fiber if some
information pair T and two extra points x,y have zero interpolation residuals
for both u and v.  This script counts such alpha1 rows.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import g3_pacc_qscaling as qscale
from issue396_action_stabilizer import residual_uv
from issue396_mixed_fiber_scaling import MIXED_SUPPORTS, stable_coefs


SEPARATED_SUPPORTS = [
    (8, 9, 20), (8, 9, 21), (10, 11, 22), (10, 11, 23),
    (12, 13, 16), (12, 13, 17), (14, 15, 18), (14, 15, 19),
    (16, 28, 29), (17, 28, 29), (18, 30, 31), (19, 30, 31),
    (20, 24, 25), (21, 24, 25), (22, 26, 27), (23, 26, 27),
    (9, 20, 21), (11, 22, 23), (13, 16, 17), (15, 18, 19),
    (16, 17, 29), (18, 19, 31), (20, 21, 25), (22, 23, 27),
]


def eval_coeffs(coeffs, L, p):
    out = []
    for x in L:
        val = 0
        for e, c in enumerate(coeffs):
            if c:
                val = (val + c * pow(x, e, p)) % p
        out.append(val)
    return out


def residual_at(values, pair_data, p):
    _T_idx, (_i, _j), kpairs = pair_data
    residuals = {}
    for k, c_ik, c_jk in kpairs:
        residuals[k] = (c_ik * values[_i] + c_jk * values[_j] - values[k]) % p
    return residuals


def saturated_pair_count_for_row(u_coeff, v_coeff, ctx):
    p = ctx["p"]
    u_vals = eval_coeffs(u_coeff, ctx["L2"], p)
    v_vals = eval_coeffs(v_coeff, ctx["L2"], p)
    sat = 0
    examples = []
    for pair_data in ctx["lagrange_pairs"]:
        _T_idx, T, kpairs = pair_data
        ru = residual_at(u_vals, pair_data, p)
        rv = residual_at(v_vals, pair_data, p)
        extras = [k for k, _cik, _cjk in kpairs if ru[k] == 0 and rv[k] == 0]
        if len(extras) >= 2:
            c = len(extras) * (len(extras) - 1) // 2
            sat += c
            if len(examples) < 3:
                examples.append((T, tuple(extras[:4]), c))
    return sat, examples


def analyze_support(support, ctx):
    p = ctx["p"]
    n2 = ctx["n2"]
    coefs = stable_coefs(support)
    row_hist = Counter()
    first_examples = []
    for alpha1 in range(p):
        u, v = residual_uv(support, coefs, alpha1, p, n2)
        sat_count, examples = saturated_pair_count_for_row(u, v, ctx)
        row_hist[sat_count] += 1
        if sat_count and len(first_examples) < 4:
            first_examples.append((alpha1, sat_count, examples))
    sat_rows = p - row_hist[0]
    return sat_rows, row_hist, first_examples


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def main():
    n0, k0, R = 32, 8, 2
    primes = [97, 193, 257, 449, 577, 769, 1153]
    panels = [("mixed", MIXED_SUPPORTS), ("separated", SEPARATED_SUPPORTS)]
    print("Issue #396 saturated-pair scan")
    print("sat_count is number of (T,{x,y}) saturated witnesses per alpha1 row")
    print()

    for p in primes:
        print(f"=== q={p} ===", flush=True)
        ctx = qscale.setup_q_context(p, n0, k0, R)
        for label, supports in panels:
            total_sat_rows = 0
            sat_supports = []
            sat_row_hist = Counter()
            sat_alpha0 = 0
            print(f"-- {label} --", flush=True)
            for support in supports:
                sat_rows, row_hist, examples = analyze_support(support, ctx)
                total_sat_rows += sat_rows
                sat_row_hist[sat_rows] += 1
                if sat_rows:
                    alpha0_saturated = bool(examples and examples[0][0] == 0)
                    sat_alpha0 += int(alpha0_saturated)
                    sat_supports.append((support, sat_rows, fmt_hist(row_hist), alpha0_saturated))
            print(f"{label} total_sat_rows={total_sat_rows}", flush=True)
            print(f"{label} sat_rows_per_support_hist={fmt_hist(sat_row_hist)}", flush=True)
            print(f"{label} alpha0_saturated_supports={sat_alpha0}", flush=True)
            for support, sat_rows, hist, alpha0_saturated in sat_supports:
                print(
                    f"  sup={support} mod4={tuple(j % 4 for j in support)} "
                    f"sat_rows={sat_rows} hist={hist} alpha0_sat={int(alpha0_saturated)}",
                    flush=True,
                )
        print(flush=True)


if __name__ == "__main__":
    main()
