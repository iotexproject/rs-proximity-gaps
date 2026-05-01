"""g3_verify_basis_template.py — verify proposed Groebner basis at sign-paired (n=4k).

Claim: For sign-paired pencil h_ρ(z) = ρz^a + z^{a+n/2} at deployment scale n=4k,
the Groebner basis of (cert eqs + div eqs) is:

  G = { p_i (for i ∉ {0, k}),
        p_0 - ρ³,
        p_k² - (ρ³ - ρ),
        p_k (ρ² + 1),
        ρ⁴ - 1 }

To verify (via reduction):
1. Each generator g ∈ G reduces to 0 modulo (cert + div)? — i.e., g ∈ ideal.
2. Each cert/div eq reduces to 0 modulo G? — i.e., G generates the ideal.

If both: G IS a Groebner basis of the ideal, and coset-rigidity holds.
This bypasses the slow Buchberger algorithm.
"""
import sys, time
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
    # p_i for i ∉ {0, k}
    for i in range(t):
        if i not in {0, k}:
            G.append(p[i])
    # p_0 - ρ³
    G.append(p[0] - rho**3)
    # p_k² - (ρ³ - ρ)
    G.append(p[k]**2 - rho**3 + rho)
    # p_k(ρ² + 1)
    G.append(p[k] * (rho**2 + 1))
    # ρ⁴ - 1
    G.append(rho**4 - 1)
    return G


def verify(n, k, a, b):
    print(f"\n=== verifying basis template at (n={n}, k={k}, a={a}, b={b}) ===")
    cert_eqs, div_eqs, p, rho = get_eqs(n, k, a, b)
    G = proposed_basis(n, k, p, rho)
    all_eqs = cert_eqs + div_eqs

    # Direction 1: Each g ∈ G reduces to 0 modulo all_eqs?
    print(f"  (D1) Reducing G ({len(G)} generators) modulo (cert+div={len(all_eqs)} eqs)...")
    t0 = time.time()
    fails = []
    for i, g in enumerate(G):
        red = sp.reduced(g, all_eqs, *p, rho, order="grevlex")[1]
        if red != 0:
            fails.append((i, g, red))
    if fails:
        print(f"  D1 FAIL: {len(fails)} generators NOT in ideal.")
        for i, g, red in fails[:3]:
            print(f"    G[{i}] = {g}: reduces to {str(red)[:80]}")
    else:
        print(f"  D1 ✓ All G generators in ideal ({time.time()-t0:.1f}s)")

    # Direction 2: Each cert/div eq reduces to 0 modulo G?
    print(f"  (D2) Reducing (cert+div={len(all_eqs)} eqs) modulo G ({len(G)} gens)...")
    t0 = time.time()
    fails2 = []
    for i, f in enumerate(all_eqs):
        red = sp.reduced(f, G, *p, rho, order="grevlex")[1]
        if red != 0:
            fails2.append((i, f, red))
    if fails2:
        print(f"  D2 FAIL: {len(fails2)} eqs NOT in proposed-basis ideal.")
        for i, f, red in fails2[:3]:
            print(f"    eq[{i}] = {f}: reduces to {str(red)[:80]}")
    else:
        print(f"  D2 ✓ All cert+div eqs in proposed-basis ideal ({time.time()-t0:.1f}s)")

    if not fails and not fails2:
        print(f"  ✓✓✓ BASIS TEMPLATE VERIFIED at (n={n}, k={k}) — coset-rigidity holds!")


def main():
    cases = [
        (8, 2, 2, 6),
        (8, 2, 3, 7),
        (16, 4, 4, 12),
        (16, 4, 5, 13),
        (16, 4, 6, 14),
        (16, 4, 7, 15),
        (32, 8, 8, 24),
        (32, 8, 9, 25),
        (32, 8, 10, 26),
        (64, 16, 16, 48),
    ]
    for n, k, a, b in cases:
        try:
            verify(n, k, a, b)
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
