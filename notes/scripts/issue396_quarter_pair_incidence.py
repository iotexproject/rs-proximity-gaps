"""Quarter-pair incidence equations for issue #396.

At (64,16)->L2=(16,4), a quarter-pair is an 8-subset of L2 formed by two
residue classes modulo 4.  For a fixed quarter-pair H, the condition

    span(u_alpha1, v_alpha1)|_H subset RS_4(H)

is a system of affine-linear equations in alpha1, because the folded row
basis vectors u_alpha1 and v_alpha1 are affine-linear in alpha1.  This script
prints the resulting solution type for the current issue #396 panels.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import modinv
from issue396_action_stabilizer import residual_uv
from issue396_component_polynomial_audit import generator_poly, poly_mod, subgroup
from issue396_saturated_witness_general_k import (
    PANEL_64_3POS,
    PANEL_64_4POS,
    stable_coefs,
)


def high_tail_for_subset(coeffs, H, L2, p, k=4):
    g = generator_poly(H, L2, p)
    rem = poly_mod(coeffs, g, p)
    return tuple(rem[i] % p for i in range(k, len(H)))


def solve_affine_equations(equations, p):
    """Solve a_i alpha + b_i = 0 over F_p.

    Return ("none", None), ("all", None), or ("point", alpha).
    """
    candidate = None
    for a, b in equations:
        a %= p
        b %= p
        if a == 0:
            if b != 0:
                return "none", None
            continue
        alpha = (-b * modinv(a, p)) % p
        if candidate is None:
            candidate = alpha
        elif candidate != alpha:
            return "none", None
    if candidate is None:
        return "all", None
    return "point", candidate


def quarter_pairs():
    out = []
    for r, s in combinations(range(4), 2):
        H = tuple(i for i in range(16) if i % 4 in {r, s})
        out.append(((r, s), H))
    return tuple(out)


def incidence_for_support(support, p):
    n2 = 16
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)
    out = []
    for label, H in quarter_pairs():
        u0, v0 = residual_uv(support, coefs, 0, p, n2)
        u1, v1 = residual_uv(support, coefs, 1, p, n2)
        tails0 = high_tail_for_subset(u0, H, L2, p) + high_tail_for_subset(v0, H, L2, p)
        tails1 = high_tail_for_subset(u1, H, L2, p) + high_tail_for_subset(v1, H, L2, p)
        equations = [((t1 - t0) % p, t0) for t0, t1 in zip(tails0, tails1)]
        kind, alpha = solve_affine_equations(equations, p)
        active = sum(1 for a, b in equations if a % p or b % p)
        out.append((label, kind, alpha, active))
    return out


def verify_solution(support, label, H, kind, alpha, p):
    n2 = 16
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)
    alphas = range(p) if kind == "all" else ([] if kind == "none" else [alpha])
    for a1 in alphas:
        u, v = residual_uv(support, coefs, a1, p, n2)
        tails = high_tail_for_subset(u, H, L2, p) + high_tail_for_subset(v, H, L2, p)
        if any(t % p for t in tails):
            raise AssertionError((support, label, kind, alpha, a1, tails))
    if kind == "point":
        for a1 in [(alpha - 1) % p, (alpha + 1) % p]:
            u, v = residual_uv(support, coefs, a1, p, n2)
            tails = high_tail_for_subset(u, H, L2, p) + high_tail_for_subset(v, H, L2, p)
            if not any(t % p for t in tails):
                raise AssertionError(("unexpected neighboring solution", support, label, alpha, a1))


def fmt_incidence(rows):
    parts = []
    for label, kind, alpha, active in rows:
        if kind == "all":
            parts.append(f"{label}:all")
        elif kind == "point":
            parts.append(f"{label}:a1={alpha}")
        else:
            parts.append(f"{label}:none")
    return " ".join(parts)


def main():
    p = 193
    panels = [("3pos-known", PANEL_64_3POS), ("4pos-probes", PANEL_64_4POS)]
    qpairs = dict(quarter_pairs())
    print("Issue #396 quarter-pair incidence")
    print(f"q={p}, L2=(16,4)")
    print("For each quarter-pair H, solution set is affine-linear in alpha1: none, point, or all.")
    print()

    grand = Counter()
    for panel, supports in panels:
        print(f"=== {panel} ===")
        total = Counter()
        for support in supports:
            rows = incidence_for_support(support, p)
            hist = Counter(kind for _, kind, _, _ in rows)
            total.update(hist)
            grand.update(hist)
            for label, kind, alpha, _active in rows:
                verify_solution(support, label, qpairs[label], kind, alpha, p)
            print(
                f"sup={support} mod4={tuple(j % 4 for j in support)} "
                f"hist={dict(sorted(hist.items()))} {fmt_incidence(rows)}"
            )
        print(f"panel_total={dict(sorted(total.items()))}")
        print()
    print(f"grand_total={dict(sorted(grand.items()))}")


if __name__ == "__main__":
    main()
