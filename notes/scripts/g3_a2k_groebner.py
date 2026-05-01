"""g3_a2k_groebner.py — compute GB for (a, 2k) family across all a at toy.

For (n=8, k=2), the (a, 2k) family with b = 2k = 4 has constant-shift
form on L_n^±. Note 0219 handles a=k=2 case rigorously. We want to
characterize the GB for other a ∈ {1, 2, 3} to see if a similar
ρ-polynomial emerges.

Focus: the eliminator polynomial Φ(ρ) — the last element of the lex GB.
"""
import sympy as sp
import time


def get_ideal(n, k, a, b):
    """Build cert+div ideal for the 2-monomial pencil (a, b) at deployment scale (n, k).

    σ_S has degree 2k (Johnson radius). Coefficients p_0, ..., p_{2k-1}.
    """
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(2 * k))
    rho = sp.Symbol("rho")
    t = 2 * k

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    rem_n = sp.Poly(sp.rem(x**n - 1, P, x), x)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]
    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    return eqs, p, rho


def compute_GB(n, k, a, b):
    eqs, p, rho = get_ideal(n, k, a, b)
    print(f"\n=== (n={n}, k={k}, a={a}, b={b}): {len(eqs)} eqs ===")
    t0 = time.time()
    G = sp.groebner(eqs, *p, rho, order="lex")
    t1 = time.time()
    print(f"  GB ({len(G)} polys) in {t1 - t0:.2f}s")
    for i, g in enumerate(G):
        print(f"    G[{i}] = {g}")
    return G


def main():
    n, k = 8, 2
    # (a, 2k) family
    for a in [1, 2, 3]:
        b = 2 * k
        compute_GB(n, k, a, b)

    # And for comparison: sign-paired (a, a + n/2)
    for a in [1, 2, 3]:
        b = a + n // 2
        compute_GB(n, k, a, b)


if __name__ == "__main__":
    main()
