"""Classify issue #396 saturated rows explained by half-subdomains.

At (64,16), L2=(16,4) and Johnson badness is agreement on 8 points.  If both
basis vectors u,v of an alpha2 row pencil restrict to RS_4 on one parity
half-subdomain of L2, then every alpha2 is bad on that row.  This script
counts those rows and separates them from full-code rows.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root, modinv
from issue396_action_stabilizer import residual_uv
from issue396_saturated_witness_general_k import (
    PANEL_64_3POS,
    PANEL_64_4POS,
    eval_coeffs,
    stable_coefs,
)


def subgroup(n, p):
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError(f"F_{p} has no primitive {n}-th root")
    return [pow(omega, i, p) for i in range(n)]


def lagrange_coeffs_at(T_indices, x_idx, L, p):
    x = L[x_idx]
    out = []
    for i in T_indices:
        xi = L[i]
        num = 1
        den = 1
        for j in T_indices:
            if j == i:
                continue
            xj = L[j]
            num = (num * (x - xj)) % p
            den = (den * (xi - xj)) % p
        out.append((i, (num * modinv(den, p)) % p))
    return out


def in_rs_k_on_indices(vals, indices, L, k, p):
    T = tuple(indices[:k])
    for x_idx in indices[k:]:
        pred = 0
        for i, c in lagrange_coeffs_at(T, x_idx, L, p):
            pred = (pred + c * vals[i]) % p
        if pred != vals[x_idx] % p:
            return False
    return True


def classify_row(u_vals, v_vals, L2, p):
    n2, k2 = 16, 4
    full_indices = tuple(range(n2))
    even_indices = tuple(range(0, n2, 2))
    odd_indices = tuple(range(1, n2, 2))

    full = (
        in_rs_k_on_indices(u_vals, full_indices, L2, k2, p)
        and in_rs_k_on_indices(v_vals, full_indices, L2, k2, p)
    )
    half_count = 0
    for indices in (even_indices, odd_indices):
        if in_rs_k_on_indices(u_vals, indices, L2, k2, p) and in_rs_k_on_indices(
            v_vals, indices, L2, k2, p
        ):
            half_count += 1
    return full, half_count


def analyze_support(support, p):
    n0, k0 = 64, 16
    n2 = n0 // 4
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)
    hist = Counter()
    examples = {}
    for alpha1 in range(p):
        u_coeff, v_coeff = residual_uv(support, coefs, alpha1, p, n2)
        u_vals = eval_coeffs(u_coeff, L2, p)
        v_vals = eval_coeffs(v_coeff, L2, p)
        full, half_count = classify_row(u_vals, v_vals, L2, p)
        key = (int(full), half_count)
        hist[key] += 1
        examples.setdefault(key, alpha1)
    return hist, examples


def fmt_hist(hist):
    parts = []
    for key in sorted(hist):
        full, half_count = key
        parts.append(f"full{full}/half{half_count}:{hist[key]}")
    return "{" + ", ".join(parts) + "}"


def main():
    p = 193
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]
    print("Issue #396 half-subdomain classifier")
    print("At L2=(16,4), half_count is number of parity half-domains where")
    print("both row basis vectors restrict to RS_4.")
    print()
    for label, supports in panels:
        print(f"=== {label} q={p} ===")
        total = Counter()
        for support in supports:
            hist, examples = analyze_support(support, p)
            total.update(hist)
            example_s = ", ".join(
                f"full{key[0]}/half{key[1]}@a1={examples[key]}" for key in sorted(examples)
            )
            print(
                f"sup={support} mod4={tuple(j % 4 for j in support)} "
                f"hist={fmt_hist(hist)} examples={example_s}"
            )
        print(f"total={fmt_hist(total)}")
        print()


if __name__ == "__main__":
    main()
