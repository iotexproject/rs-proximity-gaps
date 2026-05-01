"""g3_stage2_subset_invariant.py — Z/h-invariant subset enumeration.

For Stage 2 at general h: enumerate 4-element subsets J ⊂ μ_h satisfying:
  e_1(J) = -ρ * (-1)^h
  e_2(J) = 0
  e_3(J) = (-1)^{h+1} * (-ρ³/2) = (-1)^h * ρ³/2  -- with sign factors
  e_4(J) = -ρ⁴/4

Each valid J yields a Z/h-invariant Stage 2 solution via S = ⋃_{j ∈ J} ω^j · μ_h
(where ω generates μ_{8h}). Such S is the 4h-element subset of μ_{8h} fixed
by μ_h-multiplication.

For Z/h-invariant solutions, all (α_c, β_c) = 0 (since E* is lattice-supported)
— so they all correspond to ORIGIN.

Question: are there NON-invariant Stage 2 solutions? If yes, count them.
"""
import argparse
import sys
import os
import itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import find_rho


def get_mu_n(p, n):
    if (p - 1) % n != 0:
        return None
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
    n = len(roots)
    if k < 0 or k > n:
        return 0
    if k == 0:
        return 1
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


def enumerate_invariant(h, p):
    """Enumerate Z/h-invariant Stage 2 solutions.

    A Z/h-invariant 4h-subset of μ_{8h} is a union of 4 of the 8 μ_h-cosets
    in μ_{8h}. So enumerate 4-subsets J ⊂ {0,1,...,7} (coset indices), and
    check the 4 e_k(ζ^J) constraints where ζ = ω^h is a primitive 8th root.
    """
    rho = sorted(find_rho(p))[0]
    inv2 = pow(2, p-2, p)
    inv4 = pow(4, p-2, p)
    print(f"=== h={h}, p={p}, rho={rho} ===")

    mu_8h = get_mu_n(p, 8 * h)
    if mu_8h is None:
        print(f"FAIL: 8h={8*h} ∤ p-1")
        return
    omega = mu_8h[1]  # generator
    # zeta = omega^h is a primitive 8th root of unity
    zeta = pow(omega, h, p)
    # Verify zeta^8 = 1 and is primitive
    print(f"zeta = ω^{h} = {zeta}; zeta^8 = {pow(zeta, 8, p)}")

    # 4 e-constraints on J (selected 4 coset indices from {0..7})
    # E*(t) = ∏_{j ∈ J} (t^h - ζ^j) ... wait, this is wrong for general h.
    #
    # Actually: μ_h-cosets in μ_{8h} correspond to {α_j · μ_h} for j=0..7,
    # where α_j = ω^j (the 8h-th roots that aren't h-th roots).
    # Each coset has h elements: α_j, α_j · ζ_h, α_j · ζ_h², ..., α_j · ζ_h^{h-1},
    # where ζ_h = ω^8 is a primitive h-th root.
    #
    # For 4 cosets to give a 4h-subset: prod_{j ∈ J} prod_{m=0..h-1}(t - α_j · ζ_h^m)
    #   = prod_{j ∈ J} (t^h - α_j^h)
    #   = prod_{j ∈ J} (t^h - ω^{jh}) = prod_{j ∈ J} (t^h - ζ^j) where ζ = ω^h.
    # So E*(t) is a polynomial in u = t^h, of degree 4 in u (= 4h in t).
    #
    # E*(t) = prod_{j ∈ J} (u - ζ^j) where u = t^h.
    # Expanding: E*(t) = u^4 - e_1(J) u^3 + e_2(J) u^2 - e_3(J) u + e_4(J)
    # In terms of t: u^k = t^{kh}. So E*(t) supported on t^{0, h, 2h, 3h, 4h}.
    # Coefs:
    #   coef(t^0) = e_4(ζ^J)
    #   coef(t^h) = -e_3(ζ^J)
    #   coef(t^{2h}) = e_2(ζ^J)
    #   coef(t^{3h}) = -e_1(ζ^J)
    #   coef(t^{4h}) = 1

    # Stage 1 + Stage 2 hypothesis (for 4h-subset):
    # coef(t^0) = -ε = -ρ^4/4
    # coef(t^h) = -ρ^3/2
    # coef(t^{2h}) = 0
    # coef(t^{3h}) = ρ
    # coef(t^{4h}) = 1

    # So:
    target_e1 = (-pow(rho, 1, p)) % p   # -e_1(ζ^J) = ρ ⟹ e_1(ζ^J) = -ρ
    target_e2 = 0                        # e_2(ζ^J) = 0
    target_e3 = pow(rho, 3, p) * inv2 % p  # -e_3(ζ^J) = -ρ^3/2 ⟹ e_3(ζ^J) = ρ^3/2
    target_e4 = (-pow(rho, 4, p) * inv4) % p  # e_4(ζ^J) = -ρ^4/4

    print(f"Targets on ζ^J: e_1 = {target_e1}, e_2 = {target_e2}, "
          f"e_3 = {target_e3}, e_4 = {target_e4}")

    # zeta^j for j=0..7
    zeta_powers = [pow(zeta, j, p) for j in range(8)]
    print(f"ζ powers (j=0..7): {zeta_powers}")

    valid = []
    for J in itertools.combinations(range(8), 4):
        roots = [zeta_powers[j] for j in J]
        e1 = elem_sym(roots, 1, p)
        e2 = elem_sym(roots, 2, p)
        e3 = elem_sym(roots, 3, p)
        e4 = elem_sym(roots, 4, p)
        if e1 == target_e1 and e2 == target_e2 and e3 == target_e3 and e4 == target_e4:
            valid.append((J, e1, e2, e3, e4))

    print(f"\nZ/h-invariant valid J-subsets: {len(valid)} (out of C(8,4) = 70)")
    for J, e1, e2, e3, e4 in valid:
        print(f"  J = {J}: e_1={e1}, e_2={e2}, e_3={e3}, e_4={e4}")
    return valid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=8)
    parser.add_argument("--p", type=int, default=193)
    args = parser.parse_args()
    enumerate_invariant(args.h, args.p)


if __name__ == "__main__":
    main()
