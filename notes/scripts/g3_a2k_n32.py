"""Verify (3k/2, 2k) = (12, 16) at n=32, k=8 — eliminator structure."""
import sympy as sp
import time

def get_last_lex(n, k, a, b):
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
    last = G[-1]
    print(f"(n={n},k={k},a={a},b={b}): {time.time()-t0:.1f}s, last (lex) = {last}")

# (32, 8): 3k/2 = 12, 2k = 16
get_last_lex(32, 8, 12, 16)
