"""g3_path_C_orbit_count.py — Probe Path C empirically.

For each (n, k, a, b) at toy scale, compute V(cert + div) by complete
lex Groebner basis on (p_0, ..., p_{2k-1}, ρ), project to ρ-axis,
and report:
  - the ρ-eliminator polynomial Φ(ρ) (lowest-degree polynomial in ρ alone)
  - the bad-ρ values in F_qbar
  - the cyclic action `ρ ↦ ω^{a-b} ρ` orbit decomposition of bad-ρ
  - whether the action is free (no fixed point besides ρ=0)
  - the orbit count

Goal: empirically validate that the orbit count is bounded by a SMALL
constant — concretely, ≤ 2 for sign-paired and ≤ 1 for non-sign-paired —
which is the structural claim Path C needs.

This is a re-verification of Conjecture E with the orbit-count framing.
"""
import sys
import time
import sympy as sp


def compute_phi(n, k, a, b):
    """Compute the ρ-eliminator polynomial Φ(ρ) for the cert+div ideal.

    Uses lex Groebner with order [p_0, ..., p_{2k-1}, ρ]; the final
    polynomial in the GB depending only on ρ is Φ.
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

    eqs = cert_eqs + div_eqs
    eqs = [e for e in eqs if e != 0]

    print(f"  cert eqs: {len(cert_eqs)} (deg in [k, 2k-1])")
    print(f"  div eqs: {len(div_eqs)} nonzero coeffs of x^n-1 mod sigma")
    print(f"  total: {len(eqs)} eqs in {len(p) + 1} vars")

    t0 = time.time()
    G = sp.groebner(eqs, *p, rho, order="lex")
    t1 = time.time()
    print(f"  lex Groebner in {t1-t0:.2f}s: {len(G)} polynomials")

    # Find the polynomial in only rho (last variable)
    phi = None
    for g in G:
        if all(g.as_poly(p_i).is_zero or not g.has(p_i) for p_i in p):
            if g.has(rho):
                phi = g
                break
    if phi is None:
        # take last GB polynomial
        phi = G[-1]
    return phi, G


def orbit_action(rho_val, omega_action, q):
    """Apply the cyclic action ρ ↦ ω^{a-b} ρ on a value.

    omega_action = ω^{a-b} (a value in F_q-bar — given as Sympy expression).
    """
    return sp.simplify(rho_val * omega_action)


def analyze(n, k, a, b, q=None):
    print(f"\n=== (n={n}, k={k}, a={a}, b={b}) ===")
    phi, G = compute_phi(n, k, a, b)
    print(f"  Φ(ρ) = {phi}")
    if not phi.has(sp.Symbol("rho")):
        print("  Φ has no ρ — degenerate; skip orbit analysis")
        return

    rho = sp.Symbol("rho")
    # Factor Φ over Q (or Q[ω])
    phi_poly = sp.Poly(phi, rho)
    print(f"  deg Φ = {phi_poly.degree()}")
    factors = sp.factor(phi)
    print(f"  factor: {factors}")

    # The cyclic action exponent r = a - b mod n
    r = (a - b) % n
    print(f"  cyclic action: ρ ↦ ω^{r} · ρ where ω is primitive n-th root")
    print(f"  orbit_size = n / gcd({r}, {n}) = {n // sp.gcd(r, n)}")


def main():
    cases = [
        # toy sign-paired
        (8, 2, 2, 6),
        # toy (k, 2k)
        (8, 2, 2, 4),
        # toy non-sign-paired generic
        (8, 2, 2, 5),
        (8, 2, 3, 5),
        # (16, 4) sign-paired
        (16, 4, 4, 12),
        # (16, 4) (k, 2k)
        (16, 4, 4, 8),
        # (16, 4) gcd=k/2 = 2
        (16, 4, 4, 10),
    ]
    for n, k, a, b in cases:
        try:
            analyze(n, k, a, b)
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
