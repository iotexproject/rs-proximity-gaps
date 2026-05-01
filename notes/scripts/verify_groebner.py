import time, sys
import sympy as sp

def get_eqs(n, k, a, b):
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(n // 2))
    rho = sp.Symbol("rho")
    t = n // 2
    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)
    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    div_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
    return cert_eqs, div_eqs, p, rho

def proposed_basis(n, k, p, rho):
    t = n // 2
    G = []
    for i in range(t):
        if i not in {0, k}:
            G.append(p[i])
    G.append(p[0] - rho**3)
    G.append(p[k]**2 - rho**3 + rho)
    G.append(p[k] * (rho**2 + 1))
    G.append(rho**4 - 1)
    return G

def verify(n, k, a, b):
    print(f"\n=== (n={n}, k={k}, a={a}, b={b}) ===", flush=True)
    cert_eqs, div_eqs, p, rho = get_eqs(n, k, a, b)
    G = proposed_basis(n, k, p, rho)
    all_eqs = cert_eqs + div_eqs
    print(f"  G has {len(G)} gens, cert+div has {len(all_eqs)} eqs", flush=True)

    t0 = time.time()
    GB_certdiv = sp.groebner(all_eqs, *p, rho, order="grevlex")
    print(f"  GB(cert+div) in {time.time()-t0:.1f}s, {len(GB_certdiv.polys)} polys", flush=True)

    fails_d1 = []
    for g in G:
        red = sp.reduced(g, list(GB_certdiv.polys), *p, rho, order="grevlex")[1]
        if red != 0:
            fails_d1.append((g, red))
    if fails_d1:
        print(f"  D1 FAIL: {len(fails_d1)}/{len(G)}", flush=True)
        for g, r in fails_d1[:3]:
            print(f"    {g} has residue {str(r)[:80]}", flush=True)
    else:
        print(f"  D1 PASS", flush=True)

    t0 = time.time()
    GB_G = sp.groebner(G, *p, rho, order="grevlex")
    print(f"  GB(G) in {time.time()-t0:.1f}s, {len(GB_G.polys)} polys", flush=True)

    fails_d2 = []
    for f in all_eqs:
        red = sp.reduced(f, list(GB_G.polys), *p, rho, order="grevlex")[1]
        if red != 0:
            fails_d2.append((f, red))
    if fails_d2:
        print(f"  D2 FAIL: {len(fails_d2)}/{len(all_eqs)}", flush=True)
        for f, r in fails_d2[:3]:
            print(f"    {str(f)[:60]}: residue {str(r)[:80]}", flush=True)
    else:
        print(f"  D2 PASS", flush=True)

if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else "16-4"
    if case == "16-4":
        verify(16, 4, 4, 12)
    elif case == "32-8":
        verify(32, 8, 8, 24)
    elif case == "8-2":
        verify(8, 2, 2, 6)
