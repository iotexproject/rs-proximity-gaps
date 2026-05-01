"""g3_stage2_h3_verify.py — verify Stage 2 hand derivation at h=3.

Compute residue-1 and residue-2 equations of P*R = x^{24} - 1 modulo Stage 1
results, then symbolically check the case analysis forces all off-block
coefficients to zero.
"""
import sympy as sp


def main():
    h = 3
    rho, eps = sp.symbols("rho eps")
    p1, p2, p4, p5 = sp.symbols("p1 p2 p4 p5")

    # Stage 1 result: P^(0)(y) = y^4 + rho y^3 - (rho^3/2) y - eps
    # R^(0)(y) = y^4 - rho y^3 + rho^2 y^2 - (rho^3/2) y + eps
    # Off-block: P^(1) = p1 + p4 y, P^(2) = p2 + p5 y
    # By top-recursion: r_1 = -p_1 + 2 rho p_4, r_2 = -p_2 + 2 rho p_5,
    # r_4 = -p_4, r_5 = -p_5, r_7 = r_8 = r_{10} = r_{11} = 0
    u1 = -p1 + 2 * rho * p4
    u2 = -p2 + 2 * rho * p5

    y = sp.Symbol("y")
    P0 = y**4 + rho * y**3 - sp.Rational(1, 2) * rho**3 * y - eps
    R0 = y**4 - rho * y**3 + rho**2 * y**2 - sp.Rational(1, 2) * rho**3 * y + eps
    P1 = p1 + p4 * y
    R1 = u1 - p4 * y
    P2 = p2 + p5 * y
    R2 = u2 - p5 * y

    # Residue-2: P^(0) R^(2) + P^(1) R^(1) + P^(2) R^(0) = 0
    res2 = sp.expand(P0 * R2 + P1 * R1 + P2 * R0)

    # Residue-1: P^(0) R^(1) + P^(1) R^(0) + y * P^(2) R^(2) = 0
    res1 = sp.expand(P0 * R1 + P1 * R0 + y * P2 * R2)

    print("=" * 60)
    print("Residue-2 coefficients (must = 0 for k=0..5):")
    eqs = []
    for k in range(6):
        c = res2.coeff(y, k)
        c = sp.expand(c)
        print(f"  y^{k}: {c} = 0")
        if c != 0:
            eqs.append(c)

    print("=" * 60)
    print("Residue-1 coefficients (must = 0 for k=0..5):")
    for k in range(6):
        c = res1.coeff(y, k)
        c = sp.expand(c)
        print(f"  y^{k}: {c} = 0")
        if c != 0:
            eqs.append(c)

    print("=" * 60)
    print(f"Total non-trivial equations: {len(eqs)}")

    # Compute Groebner basis over (p1, p2, p4, p5, eps, rho)
    print("\nGroebner basis (lex, p_i first, eps, rho last):")
    G = sp.groebner(eqs, p1, p2, p4, p5, eps, rho, order="lex")
    for g in G:
        print(f"  {g}")

    print("\nReduce p_d mod GB:")
    for sym, name in [(p1, "p1"), (p2, "p2"), (p4, "p4"), (p5, "p5")]:
        rem = G.reduce(sym)[1]
        print(f"  {name} reduces to: {rem}")

    # Verify the hand derivation case analysis:
    # Case A: p_5 = 0 forces all to zero
    print("\n" + "=" * 60)
    print("Hand-derivation cross-check:")
    # Eq from y^3 of res2: -2*rho*p2 + 3*rho^2*p5
    # Eq from y^2 of res2: rho^2 * p2 - p4^2
    # Eq from y^0 of res1: 2*eps*(p1 - rho*p4)
    # Eq from y^2 of res1: rho*(rho*p1 - p5^2)
    eq_y3_r2 = -2 * rho * p2 + 3 * rho**2 * p5
    eq_y2_r2 = rho**2 * p2 - p4**2
    eq_y0_r1 = 2 * eps * (p1 - rho * p4)
    eq_y2_r1 = rho * (rho * p1 - p5**2)

    actual_y3_r2 = sp.expand(res2.coeff(y, 3))
    actual_y2_r2 = sp.expand(res2.coeff(y, 2))
    actual_y0_r1 = sp.expand(res1.coeff(y, 0))
    actual_y2_r1 = sp.expand(res1.coeff(y, 2))

    print(f"  res2 y^3 expected: {sp.expand(eq_y3_r2)}, actual: {actual_y3_r2}, match: {sp.expand(eq_y3_r2 - actual_y3_r2) == 0}")
    print(f"  res2 y^2 expected: {sp.expand(eq_y2_r2)}, actual: {actual_y2_r2}, match: {sp.expand(eq_y2_r2 - actual_y2_r2) == 0}")
    print(f"  res1 y^0 expected: {sp.expand(eq_y0_r1)}, actual: {actual_y0_r1}, match: {sp.expand(eq_y0_r1 - actual_y0_r1) == 0}")
    print(f"  res1 y^2 expected: {sp.expand(eq_y2_r1)}, actual: {actual_y2_r1}, match: {sp.expand(eq_y2_r1 - actual_y2_r1) == 0}")


if __name__ == "__main__":
    main()
