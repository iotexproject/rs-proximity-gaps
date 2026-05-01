"""g3_stage2_subset_enumerate.py — verify Note 0248 reformulation.

Enumerate 4h-element subsets S of μ_{8h} ⊂ F_p satisfying:
  (C1)  e_{2h}(S) = 0
  (C2)  e_k(S) = 0 for k ∈ {2h+1..3h-1, 3h+1..4h-1}
  (C3)  e_h(S) = ρ * (-1)^h
  (C4)  e_{3h}(S) = (-1)^{h+1} * ρ³/2
  (C5)  e_{4h}(S) = -ρ⁴/4

Each valid S corresponds to a Stage 2 solution (α*, β*).

Run for small h (h=2 fully feasible at C(16,8) = 12870 subsets).
"""
import argparse
import sys
import os
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import find_rho


def get_mu_8h(p, h):
    """Return list of 8h-th roots of unity in F_p (assume 8h | p-1)."""
    n = 8 * h
    if (p - 1) % n != 0:
        return None
    # Find primitive root
    from sympy.ntheory import factorint
    pf = list(factorint(p - 1).keys())
    g = None
    for cand in range(2, p):
        if all(pow(cand, (p-1) // f, p) != 1 for f in pf):
            g = cand
            break
    omega = pow(g, (p-1) // n, p)
    return [pow(omega, i, p) for i in range(n)]


def elem_sym(roots, k, p):
    """Compute e_k(roots) mod p via direct expansion."""
    n = len(roots)
    if k < 0 or k > n:
        return 0
    if k == 0:
        return 1
    # Use polynomial multiplication: prod (1 + x*r_i) and read coefficient of x^k
    poly = [0] * (k + 1)
    poly[0] = 1
    for r in roots:
        new_poly = poly[:]
        for j in range(min(k, len(poly)-1), -1, -1):
            if poly[j]:
                if j + 1 <= k:
                    new_poly[j + 1] = (new_poly[j + 1] + poly[j] * r) % p
        poly = new_poly
    return poly[k]


def enumerate_h2(p):
    """For h=2: enumerate all 8-subsets of μ_{16}."""
    h = 2
    rho = sorted(find_rho(p))[0]
    print(f"h={h}, p={p}, rho={rho}")
    inv2 = pow(2, p-2, p)
    inv4 = pow(4, p-2, p)

    # Constraints
    # e_{2h}(S) = e_4(S) = 0
    # e_k(S) = 0 for k ∈ {5} (3h-1 = 5 only since 3h+1=7, 4h-1=7, so k ∈ {5, 7})
    # Actually: 2h+1..3h-1 = 5..5; 3h+1..4h-1 = 7..7. So k ∈ {5, 7}.
    # e_h(S) = e_2(S) = ρ * (-1)^2 = ρ
    # e_{3h}(S) = e_6(S) = (-1)^3 * ρ³/2 = -ρ³/2
    # e_{4h}(S) = e_8(S) = -ρ⁴/4
    target_e = {
        2: rho,
        4: 0,
        5: 0,
        6: (-pow(rho, 3, p) * inv2) % p,
        7: 0,
        8: (-pow(rho, 4, p) * inv4) % p,
    }
    print(f"Target e_k: {target_e}")

    mu16 = get_mu_8h(p, h)
    if mu16 is None:
        print(f"FAIL: {8*h} ∤ {p-1}")
        return
    print(f"|μ_{{16}}| = {len(mu16)}")

    valid = []
    total = 0
    for S in itertools.combinations(mu16, 8):
        total += 1
        ok = True
        for k, target in target_e.items():
            if elem_sym(list(S), k, p) != target:
                ok = False
                break
        if ok:
            valid.append(S)

    print(f"Total subsets checked: {total}")
    print(f"Valid (satisfying all constraints): {len(valid)}")
    for i, S in enumerate(valid):
        print(f"  S_{i}: {sorted(S)}")
    return valid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=2)
    parser.add_argument("--p", type=int, default=193)
    args = parser.parse_args()
    if args.h == 2:
        enumerate_h2(args.p)
    else:
        print(f"h={args.h} enumeration not implemented (would be C({8*args.h}, {4*args.h}) subsets)")


if __name__ == "__main__":
    main()
