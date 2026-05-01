"""g3_k3_check.py — verify GB structure at (n=12, k=3) for k=3 sanity check.

(12, 3) is not strictly a "power-of-2 deployment", but the (k, 2k)
family at k=3 gives n=12. Check if the GB has the same Φ(ρ) = ρ⁵ + 4ρ
form as toy.
"""
import sympy as sp
import time


def get_groebner(n, k, a, b):
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

    t0 = time.time()
    G = sp.groebner(eqs, *p, rho, order="lex")
    t1 = time.time()
    print(f"  GB ({len(G)} polys) in {t1-t0:.2f}s")
    return G, p, rho


def main():
    cases = [
        # (n=12, k=3) (k, 2k) family
        (12, 3, 3, 6),
        # (n=12, k=3) sign-paired-like (b - a = n/2 = 6)
        (12, 3, 3, 9),
    ]
    for n, k, a, b in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}) ===")
        try:
            G, p, rho = get_groebner(n, k, a, b)
            for i, g in enumerate(G):
                print(f"  G[{i}] = {g}")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
