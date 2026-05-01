"""g3_path_C_32_8.py — extend orbit-count probe to (32, 8) sign-paired.

If Φ(ρ) at (32, 8, 8, 24) = ρ⁴ - 1 (matching toy), this is direct
empirical evidence for Path D (scale-invariant eliminator).

NB: previous Sympy lex Groebner at (32, 8) timed out at 35+ minutes.
Try with smaller field tricks: use grevlex first then convert via FGLM,
or use elimination-ideal approach.
"""
import time
import signal
import sympy as sp


def with_timeout(seconds):
    def handler(signum, frame):
        raise TimeoutError(f"{seconds}s exceeded")
    return handler


def get_eqs(n, k, a, b):
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
    return cert_eqs + div_eqs, p, rho


def try_grevlex_then_fglm(n, k, a, b, time_limit_s=600):
    eqs, p, rho = get_eqs(n, k, a, b)
    eqs = [e for e in eqs if e != 0]
    print(f"  total eqs: {len(eqs)} in {len(p) + 1} vars")

    # Try grevlex first (usually faster), then convert
    print(f"  attempting grevlex...")
    signal.signal(signal.SIGALRM, with_timeout(time_limit_s))
    signal.alarm(time_limit_s)
    try:
        t0 = time.time()
        G = sp.groebner(eqs, *p, rho, order="grevlex")
        t1 = time.time()
        signal.alarm(0)
        print(f"  grevlex GB in {t1-t0:.1f}s: {len(G)} polynomials")
    except TimeoutError as e:
        signal.alarm(0)
        print(f"  grevlex TIMEOUT after {time_limit_s}s — abandoning this case")
        return None

    # Find the polynomial in only rho via successive elimination
    # Look for univariate-in-rho element
    phi = None
    for g in G:
        free_vars = g.free_symbols
        if rho in free_vars and not any(p_i in free_vars for p_i in p):
            phi = g
            break

    if phi is None:
        # Need explicit elimination — use lex on (p_..., rho)
        print(f"  no pure-rho polynomial in grevlex GB; converting to lex...")
        signal.alarm(time_limit_s)
        try:
            t0 = time.time()
            Glex = sp.groebner(eqs, *p, rho, order="lex")
            t1 = time.time()
            signal.alarm(0)
            print(f"  lex GB in {t1-t0:.1f}s: {len(Glex)} polynomials")
            for g in Glex:
                free_vars = g.free_symbols
                if rho in free_vars and not any(p_i in free_vars for p_i in p):
                    phi = g
                    break
        except TimeoutError:
            signal.alarm(0)
            print(f"  lex TIMEOUT after {time_limit_s}s")

    return phi


def main():
    print("=== (32, 8, 8, 24) sign-paired ===")
    phi = try_grevlex_then_fglm(32, 8, 8, 24, time_limit_s=1800)
    if phi is not None:
        print(f"\n  Φ(ρ) = {phi}")
        print(f"  factor: {sp.factor(phi)}")
        print(f"  deg = {sp.Poly(phi, sp.Symbol('rho')).degree()}")
    else:
        print(f"\n  Φ NOT obtained in time limit")


if __name__ == "__main__":
    main()
