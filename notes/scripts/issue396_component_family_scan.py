"""Scan issue #396 saturated components by structured family type.

This is a follow-up to Note 0319.  It checks whether non-full saturated rows
in the current (64,16)->L2=(16,4) panels are explained by parity cosets and
single-substitution near-cosets, or whether genuinely unstructured 8-subsets
already appear at this scale.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_action_stabilizer import residual_uv
from issue396_component_polynomial_audit import family_label, generator_poly, poly_mod, subgroup
from issue396_saturated_witness_general_k import (
    PANEL_64_3POS,
    PANEL_64_4POS,
    stable_coefs,
)


def family_counter(components):
    return Counter(family_label(S) for S in components)


def precompute_component_tests(L2, p):
    """For each 8-subset S, precompute high coefficients of x^e mod g_S.

    A polynomial lies in RS_4(S) iff the high tail coefficients 4..7 of its
    remainder modulo g_S vanish.  The row polynomials are sparse, so this
    precomputation makes the full panel scan cheap.
    """
    subsets = []
    families = []
    tails_by_subset = []
    monomials = [[0] * e + [1] for e in range(16)]
    for S in combinations(range(16), 8):
        g = generator_poly(S, L2, p)
        tails = []
        for mono in monomials:
            rem = poly_mod(mono, g, p)
            tails.append(tuple(rem[i] % p for i in range(4, 8)))
        subsets.append(S)
        families.append(family_label(S))
        tails_by_subset.append(tails)
    return {
        "subsets": tuple(subsets),
        "families": tuple(families),
        "tails": np.array(tails_by_subset, dtype=np.int64),
    }


def in_rs4_from_coeffs(coeffs, tails, p):
    acc = [0, 0, 0, 0]
    for e, c in enumerate(coeffs):
        c %= p
        if c == 0:
            continue
        tail = tails[e]
        for i in range(4):
            acc[i] = (acc[i] + c * tail[i]) % p
    return all(x == 0 for x in acc)


def saturated_component_indices_fast(u_coeff, v_coeff, tests, p):
    tails = tests["tails"]
    u = np.array([(c % p) for c in u_coeff[:16]], dtype=np.int64)
    v = np.array([(c % p) for c in v_coeff[:16]], dtype=np.int64)
    u_acc = np.tensordot(tails, u, axes=([1], [0])) % p
    v_acc = np.tensordot(tails, v, axes=([1], [0])) % p
    mask = np.all(u_acc == 0, axis=1) & np.all(v_acc == 0, axis=1)
    return np.flatnonzero(mask)


def family_counter_from_indices(indices, tests):
    return Counter(tests["families"][int(i)] for i in indices)


def coarse_key(counter, full_count):
    if not counter:
        return "empty"
    if sum(counter.values()) == full_count:
        return "full"
    if any(k == "other" for k in counter):
        return "has-other"
    if any(k.startswith("near-") for k in counter):
        return "coset+near"
    return "coset-only"


def analyze_support(support, p, tests):
    n2 = 16
    full_count = 12870
    coefs = stable_coefs(support, p)
    coarse = Counter()
    exact = Counter()
    examples = {}

    for alpha1 in range(p):
        u_coeff, v_coeff = residual_uv(support, coefs, alpha1, p, n2)
        indices = saturated_component_indices_fast(u_coeff, v_coeff, tests, p)
        fams = family_counter_from_indices(indices, tests)
        ck = coarse_key(fams, full_count)
        coarse[ck] += 1
        exact_key = tuple(sorted(fams.items()))
        exact[exact_key] += 1
        examples.setdefault(ck, (alpha1, exact_key))
    return coarse, exact, examples


def fmt_counter(counter):
    return "{" + ", ".join(f"{k}:{counter[k]}" for k in sorted(counter)) + "}"


def main():
    p = 193
    L2 = subgroup(16, p)
    tests = precompute_component_tests(L2, p)
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]
    print("Issue #396 component family scan")
    print("coarse keys: empty, full, coset-only, coset+near, has-other")
    print()
    total = Counter()
    for label, supports in panels:
        print(f"=== {label} q={p} ===")
        panel_total = Counter()
        for support in supports:
            coarse, exact, examples = analyze_support(support, p, tests)
            panel_total.update(coarse)
            total.update(coarse)
            example_s = "; ".join(
                f"{k}@a1={examples[k][0]} fam={examples[k][1]}" for k in sorted(examples)
            )
            print(
                f"sup={support} mod4={tuple(j % 4 for j in support)} "
                f"coarse={fmt_counter(coarse)} examples={example_s}"
            )
        print(f"panel_total={fmt_counter(panel_total)}")
        print()
    print(f"grand_total={fmt_counter(total)}")


if __name__ == "__main__":
    main()
