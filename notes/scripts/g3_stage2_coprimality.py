"""g3_stage2_coprimality.py — verify Res_y(q0, r0) = rho^16/2 under Stage 1.

Establishes that q^(0)(y) and r^(0)(y) (the on-h-lattice forms after Stage 1)
are coprime in char != 2. This is the structural ingredient for the linear
injectivity of the residue-c equation in Note 0229.
"""
import sympy as sp


def main():
    y, rho, eps = sp.symbols("y rho eps")
    q0 = y**4 + rho * y**3 - sp.Rational(1, 2) * rho**3 * y - eps
    r0 = y**4 - rho * y**3 + rho**2 * y**2 - sp.Rational(1, 2) * rho**3 * y + eps

    print("q^(0)(y) =", q0)
    print("r^(0)(y) =", r0)
    print()

    res = sp.expand(sp.resultant(q0, r0, y))
    print("Res_y(q^(0), r^(0)) =", res)
    print()

    # Verify under Stage 1: eps = rho^4/4 and rho^8 = 16.
    res_s1 = sp.expand(res.subs([(eps, rho**4 / 4)]))
    print("Res after eps=rho^4/4:", res_s1)
    # Should be rho^16/2.

    # Check product = y^8 - 1 under Stage 1.
    prod = sp.expand(q0 * r0)
    prod_s1 = sp.expand(prod.subs([(eps, rho**4 / 4)]))
    diff_from_y8m1 = sp.expand(prod_s1 - (y**8 - 1))
    print("\nq0 * r0 (after eps=rho^4/4) - (y^8 - 1) =", diff_from_y8m1)
    print("(should equal 1 - rho^8/16, vanishing under rho^8 = 16)")

    # Verify coprimality directly via gcd.
    g = sp.gcd(q0, r0, y)
    print("\nDirect gcd(q0, r0) over Q[y, rho, eps]:", g)


if __name__ == "__main__":
    main()
