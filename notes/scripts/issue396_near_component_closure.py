"""Verify quarter-pair plus defect-root near-cosets close issue #396 panels.

For each non-full row in the (64,16)->L2=(16,4) panels, compare:

  A. exhaustive saturated components S, |S|=8, W|_S subset RS_4(S);
  B. components generated from quarter-pair bases H and Note 0319
     single-substitution defect roots.

The target is that A=B for every non-full row in the current panels.
"""

from __future__ import annotations

import os
import sys
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_action_stabilizer import residual_uv
from issue396_component_family_scan import (
    precompute_component_tests,
    saturated_component_indices_fast,
)
from issue396_component_polynomial_audit import generator_poly, poly_mod, subgroup
from issue396_quarter_pair_incidence import high_tail_for_subset, quarter_pairs
from issue396_saturated_witness_general_k import (
    PANEL_64_3POS,
    PANEL_64_4POS,
    stable_coefs,
)


def eval_poly(coeffs, x, p):
    acc = 0
    power = 1
    for c in coeffs:
        acc = (acc + (c % p) * power) % p
        power = (power * x) % p
    return acc


def low_representative(coeffs, H, L2, p):
    g = generator_poly(H, L2, p)
    rem = poly_mod(coeffs, g, p)
    return tuple(rem[:4])


def is_quarter_component(u, v, H, L2, p):
    tails = high_tail_for_subset(u, H, L2, p) + high_tail_for_subset(v, H, L2, p)
    return not any(t % p for t in tails)


def generated_components(u, v, L2, p):
    """Generate quarter-pair and single-substitution near-coset components."""
    out = set()
    for _label, H in quarter_pairs():
        H = tuple(H)
        H_set = set(H)
        if not is_quarter_component(u, v, H, L2, p):
            continue
        out.add(H)

        ru = low_representative(u, H, L2, p)
        rv = low_representative(v, H, L2, p)
        for b in range(16):
            if b in H_set:
                continue
            xb = L2[b]
            if (eval_poly(u, xb, p) - eval_poly(ru, xb, p)) % p:
                continue
            if (eval_poly(v, xb, p) - eval_poly(rv, xb, p)) % p:
                continue
            for a in H:
                S = tuple(sorted((H_set - {a}) | {b}))
                out.add(S)
    return out


def analyze_support(support, p, tests, L2):
    coefs = stable_coefs(support, p)
    full_count = 12870
    hist = Counter()
    residual_examples = []
    for alpha1 in range(p):
        u, v = residual_uv(support, coefs, alpha1, p, 16)
        exhaustive = {
            tests["subsets"][int(i)]
            for i in saturated_component_indices_fast(u, v, tests, p)
        }
        if len(exhaustive) == full_count:
            hist["full"] += 1
            continue
        generated = generated_components(u, v, L2, p)
        missing = exhaustive - generated
        extra = generated - exhaustive
        if missing or extra:
            hist["mismatch"] += 1
            if len(residual_examples) < 4:
                residual_examples.append((alpha1, len(exhaustive), len(generated), missing, extra))
        else:
            hist["closed"] += 1
    return hist, residual_examples


def main():
    p = 193
    L2 = subgroup(16, p)
    tests = precompute_component_tests(L2, p)
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]
    print("Issue #396 near-component closure")
    print(f"q={p}, L2=(16,4)")
    print("Checks exhaustive saturated components against quarter-pair + defect-root generation.")
    print()

    grand = Counter()
    for panel, supports in panels:
        print(f"=== {panel} ===")
        panel_total = Counter()
        for support in supports:
            hist, examples = analyze_support(support, p, tests, L2)
            panel_total.update(hist)
            grand.update(hist)
            print(f"sup={support} mod4={tuple(j % 4 for j in support)} hist={dict(sorted(hist.items()))}")
            for alpha1, n_ex, n_gen, missing, extra in examples:
                print(
                    f"  mismatch alpha1={alpha1} exhaustive={n_ex} generated={n_gen} "
                    f"missing={sorted(missing)[:3]} extra={sorted(extra)[:3]}"
                )
        print(f"panel_total={dict(sorted(panel_total.items()))}")
        print()
    print(f"grand_total={dict(sorted(grand.items()))}")
    if grand.get("mismatch", 0):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
