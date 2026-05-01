"""General-k saturated interpolation witness scan for issue #396.

Note 0313 isolated the base L2=(8,2) obstruction: a fixed alpha1 row has a
full alpha2 fiber when some information set T has enough extras whose
interpolation residuals vanish for both basis vectors u and v of the row
pencil u + alpha2 v.

For L2=(n,k) at rate 1/4, Johnson badness means agreement on
s = sqrt(nk) = n/2 points.  Thus a saturated witness is:

    |T|=k and at least s-k extras x outside T
    with residual_u(T,x)=residual_v(T,x)=0.

This script scans that condition beyond the base k=2 case, especially the
(64,16) -> L2=(16,4) deployment toy scale.
"""

from __future__ import annotations

import math
import os
import random
import sys
from collections import Counter
from itertools import combinations

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root, modinv
from issue396_action_stabilizer import residual_uv


PANEL_64_3POS = [
    (33, 35, 47),
    (33, 44, 45),
    (39, 40, 41),
    (38, 40, 46),
    (17, 19, 21),
    (17, 19, 23),
    (19, 21, 23),
    (16, 17, 18),
    (16, 32, 48),
    (17, 33, 49),
    (16, 17, 33),
]

PANEL_64_4POS = [
    (29, 39, 53, 61),  # max-K example from g3_K_bound_4pos_64_16.py
    (16, 17, 18, 19),
    (16, 20, 24, 28),
    (17, 21, 25, 29),
    (24, 35, 46, 57),
    (31, 37, 43, 49),
    (33, 35, 44, 47),
    (38, 40, 44, 46),
]


def stable_coefs(support, p):
    seed = 0x396B0000
    for j in support:
        seed = ((seed * 1000003) ^ (j + 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    return [rng.randrange(1, p) for _ in support]


def subgroup(n, p):
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError(f"F_{p} has no primitive {n}-th root")
    return [pow(omega, i, p) for i in range(n)]


def precompute_lagrange_general(L, k, p):
    out = []
    for T in combinations(range(len(L)), k):
        idxs = tuple(T)
        T_set = set(idxs)
        kpairs = []
        for x_idx in range(len(L)):
            if x_idx in T_set:
                continue
            x = L[x_idx]
            coeffs = []
            for i in idxs:
                xi = L[i]
                num = 1
                den = 1
                for j in idxs:
                    if j == i:
                        continue
                    xj = L[j]
                    num = (num * (x - xj)) % p
                    den = (den * (xi - xj)) % p
                coeffs.append((i, (num * modinv(den, p)) % p))
            kpairs.append((x_idx, tuple(coeffs)))
        out.append((idxs, tuple(kpairs)))
    return tuple(out)


def eval_coeffs(coeffs, L, p):
    vals = []
    for x in L:
        v = 0
        for e, c in enumerate(coeffs):
            if c:
                v = (v + c * pow(x, e, p)) % p
        vals.append(v)
    return vals


def count_saturated_witnesses(u_vals, v_vals, lagrange_data, extras_needed, p):
    witness_count = 0
    first = []
    for idxs, kpairs in lagrange_data:
        good_extras = []
        for x_idx, coeffs in kpairs:
            pred_u = 0
            pred_v = 0
            for i, c in coeffs:
                pred_u = (pred_u + c * u_vals[i]) % p
                pred_v = (pred_v + c * v_vals[i]) % p
            if (pred_u - u_vals[x_idx]) % p == 0 and (pred_v - v_vals[x_idx]) % p == 0:
                good_extras.append(x_idx)
        if len(good_extras) >= extras_needed:
            c = math.comb(len(good_extras), extras_needed)
            witness_count += c
            if len(first) < 3:
                first.append((idxs, tuple(good_extras[: extras_needed + 2]), c))
    return witness_count, first


def analyze_support(support, p, n0, k0, lagrange_data):
    n2 = n0 // 4
    k2 = k0 // 4
    s2 = math.isqrt(n2 * k2)
    if s2 * s2 != n2 * k2:
        raise ValueError("this script expects square nk at L2")
    extras_needed = s2 - k2
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)

    hist = Counter()
    examples = []
    for alpha1 in range(p):
        u_coeff, v_coeff = residual_uv(support, coefs, alpha1, p, n2)
        u_vals = eval_coeffs(u_coeff, L2, p)
        v_vals = eval_coeffs(v_coeff, L2, p)
        sat, first = count_saturated_witnesses(
            u_vals, v_vals, lagrange_data, extras_needed, p
        )
        hist[sat] += 1
        if sat and len(examples) < 4:
            examples.append((alpha1, sat, first))
    return hist, examples


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def main():
    n0, k0 = 64, 16
    n2, k2 = n0 // 4, k0 // 4
    primes = [193, 257, 449]
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]

    print("Issue #396 general-k saturated-witness scan")
    print(f"(n0,k0)=({n0},{k0}), L2=({n2},{k2})")
    print("sat_count is number of (T,E) witnesses per alpha1 row")
    print()

    for p in primes:
        print(f"=== q={p} ===", flush=True)
        L2 = subgroup(n2, p)
        lagrange_data = precompute_lagrange_general(L2, k2, p)
        for label, supports in panels:
            total_sat_rows = 0
            rows_per_support = Counter()
            print(f"-- {label} --", flush=True)
            for support in supports:
                hist, examples = analyze_support(support, p, n0, k0, lagrange_data)
                sat_rows = p - hist[0]
                total_sat_rows += sat_rows
                rows_per_support[sat_rows] += 1
                if sat_rows:
                    example_s = "; ".join(
                        f"a1={a1},sat={sat},first={first[:1]}"
                        for a1, sat, first in examples[:2]
                    )
                    print(
                        f"  sup={support} mod4={tuple(j % 4 for j in support)} "
                        f"sat_rows={sat_rows} hist={fmt_hist(hist)} {example_s}",
                        flush=True,
                    )
            print(f"{label} total_sat_rows={total_sat_rows}", flush=True)
            print(f"{label} sat_rows_per_support_hist={fmt_hist(rows_per_support)}", flush=True)
        print(flush=True)


if __name__ == "__main__":
    main()
