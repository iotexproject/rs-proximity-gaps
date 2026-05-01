"""g3_closure_signpaired_fast.py — fast coset-rigidity test via degrevlex Groebner.

For sign-paired (n, k, a, b=a+n/2), use degrevlex Groebner (faster than lex)
to test if p_i is in the ideal of (cert + divisor) eqs for i ∉ {0, k}.

This avoids the slow lex elimination but still gives the membership test.
"""
import sys, time
import sympy as sp


def fast_coset_check(n, k, a, b):
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

    print(f"  computing Groebner (degrevlex, {len(cert_eqs)+len(div_eqs)} eqs in {len(p)+1} vars)...")
    t0 = time.time()
    G = sp.groebner(cert_eqs + div_eqs, *p, rho, order="grevlex")
    print(f"  Groebner done in {time.time()-t0:.1f}s, basis size {len(G.polys)}")

    forced_zero = []
    not_forced = []
    for i in range(t):
        if i == 0 or i == k:
            continue
        red = sp.reduced(p[i], list(G.polys), *p, rho, order="grevlex")[1]
        if red == 0:
            forced_zero.append(i)
        else:
            not_forced.append((i, red))
    return forced_zero, not_forced


def main():
    cases = [
        (8, 2, 2, 6),
        (8, 2, 3, 7),
        (16, 4, 4, 12),
        (16, 4, 5, 13),
        (16, 4, 6, 14),
        (16, 4, 7, 15),
        (32, 8, 8, 24),
    ]
    for n, k, a, b in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}) sign-paired ===")
        try:
            forced, not_f = fast_coset_check(n, k, a, b)
            t = n // 2
            allowed = {0, k}
            target = [i for i in range(t) if i not in allowed]
            if forced == target and not not_f:
                print(f"  ✓ All p_i (i ∉ {{0, {k}}}) forced to 0 → COSET-RIGIDITY HOLDS")
                print(f"    forced: {forced}")
            else:
                print(f"  forced: {forced}")
                if not_f:
                    print(f"  NOT forced: {[(i, str(r)[:60]) for i, r in not_f]}")
        except Exception as e:
            print(f"  FAILED: {e}")


if __name__ == "__main__":
    main()
