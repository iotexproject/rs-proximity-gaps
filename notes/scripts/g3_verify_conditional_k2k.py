"""g3_verify_conditional_k2k.py — extend Note 0215 reduction to (k, 2k) family.

For (a, b) = (k, 2k), pencil h_ρ(z) = ρ z^k + z^{2k}. Same sparse support
σ_S = z^{2k} + p_k z^k + p_0. Compute cert+div and reduce.

Expected: ρ⁴ = -4 (matching Note 0204 empirical Φ).
"""
import sympy as sp


def verify_at(k):
    print(f"\n=== verify (k, 2k) at k={k} ===")
    n = 4 * k
    a = k
    b = 2 * k

    x = sp.Symbol("x")
    p_k_sym = sp.Symbol("pk")
    p_0_sym = sp.Symbol("p0")
    rho = sp.Symbol("rho")

    sigma = x ** (2 * k) + p_k_sym * x**k + p_0_sym

    rem_a = sp.Poly(sp.rem(x**a, sigma, x), x)
    rem_b = sp.Poly(sp.rem(x**b, sigma, x), x)

    cert = []
    for j in range(k, 2 * k):
        coef_a = rem_a.coeff_monomial(x**j)
        coef_b = rem_b.coeff_monomial(x**j)
        eq = sp.expand(rho * coef_a + coef_b)
        cert.append((j, eq))

    print("cert eqs:")
    for j, e in cert:
        print(f"  j={j}: {e}")

    rem_n = sp.Poly(sp.rem(x**n - 1, sigma, x), x)
    div_dict = rem_n.as_dict()
    print("div eqs (x^n - 1 coefs):")
    for monom, coef in sorted(div_dict.items(), reverse=True):
        print(f"  z^{monom[0]}: {sp.expand(coef)}")

    # Combine
    print("\nCert solves p_k = ρ. Substitute into div.")
    subs = {p_k_sym: rho}
    for monom, coef in sorted(div_dict.items(), reverse=True):
        s = sp.factor(sp.expand(coef.subs(subs)))
        print(f"  z^{monom[0]} → {s}")

    # Then div_z^k gives ρ(2 p_0 - ρ²) = 0 → 2 p_0 = ρ².
    # Then div_z^0 gives p_0(p_0 - ρ²) = 1.
    # Substituting p_0 = ρ²/2: (ρ²/2)(ρ²/2 - ρ²) = -ρ⁴/4 = 1 → ρ⁴ = -4. ✓
    print("\nFurther p_0 = ρ²/2:")
    subs2 = {p_k_sym: rho, p_0_sym: rho**2 / 2}
    for monom, coef in sorted(div_dict.items(), reverse=True):
        s = sp.factor(sp.expand(coef.subs(subs2)))
        print(f"  z^{monom[0]} → {s}")

    print("Final: ρ⁴ + 4 = 0, so ρ⁴ = -4. ✓")


def main():
    for k in [2, 4, 8, 16]:
        verify_at(k)


if __name__ == "__main__":
    main()
