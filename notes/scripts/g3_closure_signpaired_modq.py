"""g3_closure_signpaired_modq.py — Groebner closure over F_q (faster than over Q).

Working over a specific F_q where q satisfies n | q-1 (so x^n - 1 splits) is
typically orders of magnitude faster than over Z. Loses generality (only
verifies at that q), but combined with (q ≥ 4·deg) any polynomial identity
holds over F_q iff over Z.
"""
import sys, time
import sympy as sp
from sympy.polys.domains import GF


def closure_modq(n, k, a, b, q):
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

    print(f"  computing Groebner over F_{q} ({len(cert_eqs)+len(div_eqs)} eqs in {len(p)+1} vars)...")
    t0 = time.time()
    domain = GF(q)
    G = sp.groebner(cert_eqs + div_eqs, *p, rho, order="grevlex", domain=domain)
    print(f"  Groebner done in {time.time()-t0:.1f}s, basis size {len(G.polys)}")

    forced_zero = []
    not_forced = []
    for i in range(t):
        if i == 0 or i == k:
            continue
        red = sp.reduced(p[i], list(G.polys), *p, rho, order="grevlex", domain=domain)[1]
        if red == 0:
            forced_zero.append(i)
        else:
            not_forced.append((i, red))
    return forced_zero, not_forced, G


def main():
    cases = [
        (8, 2, 2, 6, 17),
        (8, 2, 2, 6, 97),
        (16, 4, 4, 12, 17),
        (16, 4, 4, 12, 97),
        (32, 8, 8, 24, 97),
        (32, 8, 8, 24, 193),
        (32, 8, 9, 25, 97),
    ]
    for n, k, a, b, q in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}, q={q}) sign-paired ===")
        try:
            forced, not_f, G = closure_modq(n, k, a, b, q)
            t = n // 2
            allowed = {0, k}
            target = [i for i in range(t) if i not in allowed]
            if forced == target and not not_f:
                print(f"  ✓ All p_i (i ∉ {{0, {k}}}) forced to 0 → COSET-RIGIDITY HOLDS over F_{q}")
                print(f"    forced: {forced}")
                # Print rho-only polys
                for poly in G.polys:
                    expr = poly.as_expr()
                    if not any(expr.has(var) for var in [sp.Symbol(f'p{i}') for i in range(t)]):
                        print(f"    rho-only: {sp.factor(expr)}")
            else:
                print(f"  forced: {forced}; NOT forced: {[(i, str(r)[:60]) for i, r in not_f]}")
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
