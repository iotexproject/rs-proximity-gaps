"""g3_closure_signpaired_general.py — generalize closure proof to (n, k, a, a+n/2).

For deployment scale n=4k and sign-paired b=a+n/2, compute Groebner closure
and verify p_i ∈ ideal for all i ∉ {0, k}.
"""
import sys, time
import sympy as sp


def closure(n, k, a, b, max_time=600):
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

    print(f"  computing Groebner ({len(cert_eqs)} cert + {len(div_eqs)} div eqs in {len(p)+1} vars)...")
    t0 = time.time()
    G = sp.groebner(cert_eqs + div_eqs, *p, rho, order="lex")
    print(f"  Groebner done in {time.time()-t0:.1f}s, basis size {len(G.polys)}")

    # Check coset-rigidity: p_i ∈ ideal for i ∉ {0, k}
    forced_zero = []
    not_forced = []
    for i in range(t):
        if i == 0 or i == k:
            continue
        red = sp.reduced(p[i], list(G.polys), *p, rho, order="lex")[1]
        if red == 0:
            forced_zero.append(i)
        else:
            not_forced.append((i, red))

    # rho-only polynomials
    rho_polys = []
    for poly in G.polys:
        expr = sp.factor(poly.as_expr())
        if not any(expr.has(var) for var in p) and expr != 0:
            rho_polys.append(expr)

    return {
        "forced_zero": forced_zero,
        "not_forced": not_forced,
        "rho_polys": rho_polys,
        "basis_size": len(G.polys),
        "elapsed": time.time() - t0,
    }


def main():
    cases = [
        (8, 2, 2, 6),
        (8, 2, 3, 7),
        (16, 4, 4, 12),
        (16, 4, 5, 13),
        (32, 8, 8, 24),
    ]
    for n, k, a, b in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}) sign-paired ===")
        try:
            res = closure(n, k, a, b)
            t = n // 2
            print(f"  forced-zero p_i (i ∉ {{0, {k}}}): {res['forced_zero']}")
            if res["not_forced"]:
                print(f"  NOT forced: {[(i, str(r)[:80]) for i, r in res['not_forced']]}")
            else:
                print(f"  ALL p_i (i ∉ {{0, {k}}}) forced to 0 → COSET-RIGIDITY HOLDS")
            print(f"  rho-only polys: {res['rho_polys']}")
        except Exception as e:
            print(f"  FAILED: {e}")


if __name__ == "__main__":
    main()
