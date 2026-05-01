"""Enumerate saturated Johnson-sized subsets for issue #396 at L2=(16,4).

For L2=(16,4), a saturated witness (T,E) has |T|=4 and |T union E|=8.
It is cleaner to count the underlying 8-point set S: if both row basis vectors
u,v restrict to RS_4 on S, then S contributes binom(8,4)=70 saturated
interpolation witnesses.  This script enumerates those S components.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root
from issue396_action_stabilizer import residual_uv
from issue396_half_subdomain_classifier import in_rs_k_on_indices
from issue396_saturated_witness_general_k import eval_coeffs, stable_coefs


SELECTED = [
    (33, 44, 45),      # has 16 rows with 700 witnesses = 10 components
    (33, 35, 47),      # q-1 rows with 140 witnesses = 2 components
    (24, 35, 46, 57),  # 2 rows with 70 witnesses = 1 component
]


def subgroup(n, p):
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError(f"F_{p} has no primitive {n}-th root")
    return [pow(omega, i, p) for i in range(n)]


def saturated_components(u_vals, v_vals, L2, p):
    components = []
    for S in combinations(range(16), 8):
        if in_rs_k_on_indices(u_vals, S, L2, 4, p) and in_rs_k_on_indices(
            v_vals, S, L2, 4, p
        ):
            components.append(S)
    return components


def component_signature(S):
    evens = sum(1 for i in S if i % 2 == 0)
    residues4 = tuple(sum(1 for i in S if i % 4 == r) for r in range(4))
    gaps = tuple((S[(i + 1) % len(S)] - S[i]) % 16 for i in range(len(S)))
    return f"even={evens},mod4={residues4},gaps={gaps}"


def analyze_support(support, p):
    n2 = 16
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)
    hist = Counter()
    examples = {}
    for alpha1 in range(p):
        u_coeff, v_coeff = residual_uv(support, coefs, alpha1, p, n2)
        u_vals = eval_coeffs(u_coeff, L2, p)
        v_vals = eval_coeffs(v_coeff, L2, p)
        comps = saturated_components(u_vals, v_vals, L2, p)
        hist[len(comps)] += 1
        if comps and len(comps) not in examples:
            examples[len(comps)] = (alpha1, comps[:12])
    return hist, examples


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def main():
    p = 193
    print("Issue #396 saturated 8-subset component enumerator")
    print("At L2=(16,4), witness_count = component_count * binom(8,4).")
    print()
    for support in SELECTED:
        hist, examples = analyze_support(support, p)
        print(f"=== sup={support} mod4={tuple(j % 4 for j in support)} q={p} ===")
        print(f"component_count_hist={fmt_hist(hist)}")
        for count in sorted(examples):
            alpha1, comps = examples[count]
            print(f"  count={count} example_alpha1={alpha1}")
            for S in comps:
                print(f"    S={S} {component_signature(S)}")
        print()


if __name__ == "__main__":
    main()
