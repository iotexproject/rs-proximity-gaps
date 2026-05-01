"""Audit the polynomial equations behind issue #396 saturated components.

For L2=(16,4), an 8-subset S is a saturated component for a row span
W=span(u,v) iff both u and v reduce modulo

    g_S(x) = prod_{i in S} (x - L2[i])

to remainders of degree < 4.  This script prints the generator-polynomial
shape of the observed component families.  The goal is to expose the hard
algebraic constraint rather than just count raw (T,E) interpolation witnesses.
"""

from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root, modinv
from issue396_action_stabilizer import residual_uv
from issue396_saturated_subset_components import component_signature, saturated_components
from issue396_saturated_witness_general_k import eval_coeffs, stable_coefs


CASES = [
    ((33, 44, 45), [0, 5]),
    ((33, 35, 47), [0, 1]),
    ((24, 35, 46, 57), [25, 26]),
]


def subgroup(n, p):
    omega = find_prim_root(p, n)
    if omega is None:
        raise ValueError(f"F_{p} has no primitive {n}-th root")
    return [pow(omega, i, p) for i in range(n)]


def poly_mul(a, b, p):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + ai * bj) % p
    return out


def generator_poly(S, L, p):
    g = [1]
    for idx in S:
        g = poly_mul(g, [(-L[idx]) % p, 1], p)
    return g


def poly_mod(f, g, p):
    r = [x % p for x in f]
    inv_lc = modinv(g[-1], p)
    while len(r) >= len(g):
        c = r[-1] * inv_lc % p
        shift = len(r) - len(g)
        if c:
            for i, gi in enumerate(g):
                r[shift + i] = (r[shift + i] - c * gi) % p
        while r and r[-1] == 0:
            r.pop()
    return r + [0] * (len(g) - 1 - len(r))


def high_tail(rem, k=4):
    return tuple(c for c in rem[k:] if c)


def sparse_poly_terms(poly, p):
    terms = []
    for i, c in enumerate(poly):
        if c % p:
            terms.append((i, c % p))
    return tuple(terms)


def centered(c, p):
    c %= p
    return c - p if c > p // 2 else c


def centered_terms(poly, p):
    return tuple((i, centered(c, p)) for i, c in sparse_poly_terms(poly, p))


def parity_label(S):
    residues4 = tuple(sum(1 for i in S if i % 4 == r) for r in range(4))
    if sorted(residues4) == [0, 0, 4, 4]:
        active = tuple(r for r, c in enumerate(residues4) if c)
        return f"quarter-pair{active}"
    if all(i % 2 == 0 for i in S):
        return "even-half"
    if all(i % 2 == 1 for i in S):
        return "odd-half"
    evens = [i for i in S if i % 2 == 0]
    odds = [i for i in S if i % 2 == 1]
    if len(evens) == 7 and len(odds) == 1:
        missing_even = sorted(set(range(0, 16, 2)) - set(evens))
        return f"near-even(+{odds[0]},-{missing_even[0]})"
    if len(odds) == 7 and len(evens) == 1:
        missing_odd = sorted(set(range(1, 16, 2)) - set(odds))
        return f"near-odd(+{evens[0]},-{missing_odd[0]})"
    return "other"


def family_label(S):
    residues4 = tuple(sum(1 for i in S if i % 4 == r) for r in range(4))
    if sorted(residues4) == [0, 0, 4, 4]:
        active = tuple(r for r, c in enumerate(residues4) if c)
        return f"quarter-pair{active}"
    if all(i % 2 == 0 for i in S):
        return "even-half"
    if all(i % 2 == 1 for i in S):
        return "odd-half"
    evens = [i for i in S if i % 2 == 0]
    odds = [i for i in S if i % 2 == 1]
    if len(evens) == 7 and len(odds) == 1:
        return f"near-even(+{odds[0]})"
    if len(odds) == 7 and len(evens) == 1:
        return f"near-odd(+{evens[0]})"
    return "other"


def audit_case(support, alpha1, p):
    n2, k2 = 16, 4
    L2 = subgroup(n2, p)
    coefs = stable_coefs(support, p)
    u_coeff, v_coeff = residual_uv(support, coefs, alpha1, p, n2)
    u_vals = eval_coeffs(u_coeff, L2, p)
    v_vals = eval_coeffs(v_coeff, L2, p)
    comps = saturated_components(u_vals, v_vals, L2, p)

    print(f"=== support={support} alpha1={alpha1} component_count={len(comps)} ===")
    print(f"u_terms={centered_terms(u_coeff, p)}")
    print(f"v_terms={centered_terms(v_coeff, p)}")
    if len(comps) == 12870:
        print("full saturation: u and v are both zero/RS_4 on L2, so every 8-subset is a component")
        print()
        return

    gen_hist = Counter()
    labels = Counter()
    families = Counter()
    tails = defaultdict(Counter)
    examples = {}
    for S in comps:
        g = generator_poly(S, L2, p)
        u_rem = poly_mod(u_coeff, g, p)
        v_rem = poly_mod(v_coeff, g, p)
        if high_tail(u_rem, k2) or high_tail(v_rem, k2):
            raise AssertionError("component failed polynomial remainder check")
        key = centered_terms(g, p)
        label = parity_label(S)
        family = family_label(S)
        gen_hist[key] += 1
        labels[label] += 1
        families[family] += 1
        tails[label][key] += 1
        examples.setdefault(label, S)

    print(f"label_hist={dict(sorted(labels.items()))}")
    print(f"family_hist={dict(sorted(families.items()))}")
    for label in sorted(tails):
        print(f"  {label}: count={labels[label]} example={examples[label]}")
        print(f"    signature={component_signature(examples[label])}")
        for key, count in tails[label].most_common(3):
            print(f"    g_terms_x_ascending_count={count}: {key}")
    print()


def main():
    p = 193
    print("Issue #396 component polynomial audit")
    print("Condition: rem(u,g_S), rem(v,g_S) have degree < 4.")
    print()
    for support, alphas in CASES:
        for alpha1 in alphas:
            audit_case(support, alpha1, p)

    print("=== all 8-subset generator sparsity distribution ===")
    L2 = subgroup(16, p)
    hist = Counter()
    for S in combinations(range(16), 8):
        g = generator_poly(S, L2, p)
        hist[sum(1 for c in g if c % p)] += 1
    print(dict(sorted(hist.items())))


if __name__ == "__main__":
    main()
