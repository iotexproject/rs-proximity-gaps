"""g3_closure_signpaired_substitute.py — faster sign-paired closure via substitution.

For sign-paired b = a + n/2 with a = k + c, c ∈ [0, k):
- Cert eq deg j ∈ [k, 2k-1] (excluding j=a): coeff of x^j in (x^b mod P) = 0
- Cert eq deg a: ρ + coeff of x^a in (x^b mod P) = 0

Use cert eqs deg ≠ a to express k-1 of the locator coords as functions of others,
then check if remaining eqs (divisor + 1 cert eq) force the 2-coset form.

Specifically: given cert eqs are equations in p_{k+1}, ..., p_{2k-1} (k-1 vars),
solving them gives constraints; the remaining variables to determine are
p_0, ..., p_k.

Substituting these into divisor eqs and computing Groebner over fewer variables
should be MUCH faster.
"""
import sys, time
import sympy as sp


def closure_substitute(n, k, a, b):
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(n // 2))
    rho = sp.Symbol("rho")
    t = n // 2

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = {}
    for d in range(k, t):
        cert_eqs[d] = sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))

    # Cert eq deg a determines ρ in terms of p; use as the "ρ-extracting" eq.
    # Other (k-1) cert eqs are constraints on p alone (assuming x^a mod P = x^a, i.e., a < t).
    assert a < t, f"a = {a} must be < t = {t}"

    # Cert eq deg a gives: ρ + (coeff of x^a in x^b mod P) = 0
    rho_eq = cert_eqs[a]
    print(f"ρ-defining eq (deg {a}): {rho_eq}")

    # Other cert eqs constrain locator coords
    other_eqs = [cert_eqs[d] for d in range(k, t) if d != a]
    print(f"Other cert eqs: {len(other_eqs)} polynomials")
    for d, eq in zip([dd for dd in range(k, t) if dd != a], other_eqs):
        print(f"  deg {d}: {sp.simplify(eq)[:100] if isinstance(sp.simplify(eq), str) else sp.simplify(eq)}")

    # Try to symbolically solve these. They typically allow expressing
    # p_{2k-1}, p_{2k-2}, ..., p_{k+1}, p_{k-1}, ..., p_1
    # in terms of (p_0, p_k, p_{k+1}, ..., p_{2k-1}, ρ, ...).
    #
    # As a first pass, substitute solutions where possible.
    return cert_eqs, rho_eq, other_eqs


def main():
    cases = [(8, 2, 2, 6), (16, 4, 4, 12), (32, 8, 8, 24)]
    for n, k, a, b in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}) sign-paired (a = k + {a-k}) ===")
        t0 = time.time()
        try:
            closure_substitute(n, k, a, b)
        except Exception as e:
            print(f"  FAILED: {e}")
        print(f"  elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
