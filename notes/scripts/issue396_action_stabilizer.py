"""Classify residual alpha2 pencils by cyclic diagonal action.

For a sparse fhat on L0 with (n0,k0)=(32,8), the two FRI folds send a
monomial z^j to

    j = 4r     ->          t^r
    j = 4r + 1 -> alpha1  t^r
    j = 4r + 2 -> alpha2  t^r
    j = 4r + 3 -> alpha1 alpha2 t^r

on L2.  For fixed alpha1 this is an alpha2-pencil

    h_{alpha1,alpha2}(t) = u_{alpha1}(t) + alpha2 v_{alpha1}(t).

Note 0310 says a Bluher-style multiplicative/projective alpha2 action exists
for a subgroup element mu in L2 exactly when

    D_mu span(u_{alpha1}, v_{alpha1}) = span(u_{alpha1}, v_{alpha1}).

This script checks that criterion over F_q for the Note 0306 mixed supports
and a few rank-4 probes.
"""

from __future__ import annotations

import os
import random
import sys
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fri_2round_attack import find_prim_root, gauss_rank


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


RANK4_PROBES = [
    (1, 2, 6, 7),      # Note 0304 K=12 counterexample to naive K4<=9.
    (8, 9, 10, 11),   # all four fold quadrants, same L2 exponent.
    (8, 13, 18, 23),  # all four quadrants, spread L2 exponents.
    (9, 14, 20, 27),
    (10, 15, 21, 28),
]


def stable_coefs(support):
    seed = 0x396A7000
    for j in support:
        seed = ((seed * 1000003) ^ (j + 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    return [rng.randrange(1, 10**6) for _ in support]


def residual_uv(support, coefs, alpha1, p, n2):
    u = [0] * n2
    v = [0] * n2
    for j, c in zip(support, coefs):
        r = (j // 4) % n2
        c = c % p
        q = j % 4
        if q == 0:
            u[r] = (u[r] + c) % p
        elif q == 1:
            u[r] = (u[r] + alpha1 * c) % p
        elif q == 2:
            v[r] = (v[r] + c) % p
        else:
            v[r] = (v[r] + alpha1 * c) % p
    return u, v


def vector_rank(vectors, p):
    return gauss_rank([v for v in vectors if any(x % p for x in v)], p)


def stabilizer_exponents(u, v, omega2, p):
    """Return m such that mu=omega2^m preserves span(u,v)."""
    n2 = len(u)
    base_rank = vector_rank([u, v], p)
    good = []
    for m in range(n2):
        du = [(u[e] * pow(omega2, m * e, p)) % p for e in range(n2)]
        dv = [(v[e] * pow(omega2, m * e, p)) % p for e in range(n2)]
        if vector_rank([u, v, du, dv], p) == base_rank:
            good.append(m)
    return tuple(good)


def subgroup_order_from_exponents(exponents, n2):
    return len(exponents)


def support_signature(u, v):
    su = tuple(i for i, x in enumerate(u) if x)
    sv = tuple(i for i, x in enumerate(v) if x)
    return su, sv


def analyze_support(support, p=1153, n0=32):
    n2 = n0 // 4
    omega0 = find_prim_root(p, n0)
    if omega0 is None:
        raise ValueError(f"no primitive {n0}-th root in F_{p}")
    omega2 = pow(omega0, 4, p)
    coefs = stable_coefs(support)

    hist = Counter()
    sig_hist = Counter()
    nontriv_alpha = []
    examples = {}

    for alpha1 in range(p):
        u, v = residual_uv(support, coefs, alpha1, p, n2)
        exps = stabilizer_exponents(u, v, omega2, p)
        order = subgroup_order_from_exponents(exps, n2)
        hist[order] += 1
        sig_hist[support_signature(u, v)] += 1
        if order > 1:
            nontriv_alpha.append(alpha1)
            examples.setdefault(order, (alpha1, exps, support_signature(u, v)))

    return {
        "support": support,
        "mod4": tuple(j % 4 for j in support),
        "hist": hist,
        "sig_hist": sig_hist,
        "nontriv_alpha": nontriv_alpha,
        "examples": examples,
    }


def fmt_hist(hist):
    return "{" + ", ".join(f"{k}:{hist[k]}" for k in sorted(hist)) + "}"


def fmt_examples(examples):
    if not examples:
        return "-"
    pieces = []
    for order in sorted(examples):
        alpha1, exps, sig = examples[order]
        pieces.append(f"ord{order}@a1={alpha1},mu_exp={exps},sig={sig}")
    return "; ".join(pieces)


def main():
    p = 1153
    panels = [
        ("rank3-mixed", MIXED_SUPPORTS),
        ("rank4-probes", RANK4_PROBES),
    ]
    print("Issue #396 cyclic-action stabilizer classifier")
    print(f"field F_{p}, n0=32, n2=8")
    print("hist keys are stabilizer orders inside L2; order 1 means identity only")
    print()

    totals = defaultdict(Counter)
    for label, supports in panels:
        print(f"=== {label} ===")
        for support in supports:
            r = analyze_support(support, p=p)
            totals[label].update(r["hist"])
            print(
                f"sup={r['support']} mod4={r['mod4']} "
                f"stab_hist={fmt_hist(r['hist'])} "
                f"nontriv_alpha={len(r['nontriv_alpha'])} "
                f"examples={fmt_examples(r['examples'])}"
            )
        print()

    print("=== totals ===")
    for label in totals:
        print(f"{label}: {fmt_hist(totals[label])}")


if __name__ == "__main__":
    main()
