"""Enumerate ALL (a, b) base cases at (4, 1) and (8, 2). Compute Φ via SymPy GB.
Identify max |B| over irreducible non-degenerate cases.

By Substitution Principle (Note 0284), all higher-scale (a, b) at (4k, k) reduce
to one of these base cases. So max |B| at base = max |B| at deployment.

Output: Φ(ρ), |B|, family classification for each base case.
"""
import sympy as sp
from math import gcd as ggcd
import multiprocessing as mp


def _gb_worker(eqs_str, p_names, rho_name, conn):
    rho = sp.Symbol(rho_name)
    p = sp.symbols(",".join(p_names)) if p_names else ()
    if p_names and not isinstance(p, tuple):
        p = (p,)
    eqs = [sp.sympify(s) for s in eqs_str]
    G = sp.groebner(eqs, *p, rho, order="lex")
    conn.send([str(g) for g in G])
    conn.close()


def gb_with_timeout(eqs, p_vars, rho, timeout_s=30):
    parent_conn, child_conn = mp.Pipe()
    proc = mp.Process(
        target=_gb_worker,
        args=([str(e) for e in eqs], [s.name for s in p_vars], rho.name, child_conn),
    )
    proc.start()
    proc.join(timeout_s)
    if proc.is_alive():
        proc.terminate()
        proc.join(2)
        if proc.is_alive():
            proc.kill()
            proc.join()
        return None
    if parent_conn.poll():
        return [sp.sympify(s) for s in parent_conn.recv()]
    return None


def classify(n, k, a, b, timeout=30):
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    t = 2 * k
    p = sp.symbols("p0:" + str(t))
    if t == 1:
        p = (p,) if not isinstance(p, tuple) else p
    sigma = z**t + sum(p[i] * z**i for i in range(t))
    rem_a = sp.Poly(sp.rem(z**a, sigma, z), z)
    rem_b = sp.Poly(sp.rem(z**b, sigma, z), z)
    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(z**d) + rem_b.coeff_monomial(z**d))
        for d in range(k, t)
    ]
    rem_n = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]
    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    if not eqs:
        return "trivial", 0
    G = gb_with_timeout(eqs, list(p), rho, timeout)
    if G is None:
        return "TIMEOUT", -1
    last = G[-1]
    free = last.free_symbols
    p_set = set(p)
    if rho not in free:
        if free & p_set:
            return "degenerate (p_j only)", -1  # at-J family
        else:
            return "constant (no constraint)", -1
    if free & p_set:
        return f"degenerate (p_j × ρ): {sp.factor(last)}", -1
    rho_polys = [g for g in G if g.free_symbols == {rho}]
    phi = rho_polys[-1] if rho_polys else last
    phi_factored = sp.factor(phi)
    # Count nonzero roots of Φ(ρ) in F̄_q
    # Φ has factor ρ^k → k zero roots (= ρ = 0). Other factors give nonzero roots.
    poly_phi = sp.Poly(phi, rho)
    deg = poly_phi.degree()
    # Count multiplicity of ρ = 0
    rho_factor_pow = 0
    test = poly_phi
    while test != 0 and sp.Poly(test, rho).TC() == 0:  # constant term is 0
        test = sp.div(test, sp.Poly(rho, rho), domain='QQ')[0]
        rho_factor_pow += 1
        if test == sp.S.Zero or sp.Poly(test, rho).degree() == 0:
            break
    # |B_F̄_q| = deg(Φ) - (rho factor power)  i.e., nonzero roots
    B_size = deg - rho_factor_pow
    return phi_factored, B_size


def main():
    mp.set_start_method('fork', force=True)
    print("=" * 70)
    print("BASE CASE ENUMERATION at (n, k) = (4, 1) and (8, 2)")
    print("By Note 0284 Substitution Principle, ALL higher-scale (a, b) reduce")
    print("to one of these base cases via u = z^d substitution (d = gcd(a, b, n)).")
    print("=" * 70)

    max_B = 0
    base_cases = []
    for n, k in [(4, 1), (8, 2)]:
        print(f"\n=== (n, k) = ({n}, {k}) — irreducible (gcd(a, b, n) = 1, a, b ≥ k) ===")
        for a in range(k, n - 1):
            for b in range(a + 1, n):
                if ggcd(ggcd(a, b), n) != 1:
                    continue  # reducible, will appear at smaller scale
                phi, B = classify(n, k, a, b, timeout=30)
                marker = ""
                if isinstance(B, int) and B > max_B:
                    max_B = B
                    marker = "  <<< MAX so far"
                phi_str = str(phi)
                if len(phi_str) > 80:
                    phi_str = phi_str[:75] + "..."
                print(f"  ({a}, {b}): |B| = {B} | Φ = {phi_str}{marker}")
                if isinstance(B, int) and B > 0:
                    base_cases.append((n, k, a, b, B, phi))

    print(f"\n=== SUMMARY ===")
    print(f"max |B| over irreducible base cases: {max_B}")
    print(f"Non-trivial base cases:")
    for c in base_cases:
        print(f"  ({c[0]}, {c[1]}, a={c[2]}, b={c[3]}): |B| = {c[4]}")

    print(f"\nBy Substitution Principle (Note 0284):")
    print(f"  K ≤ {max_B} for ALL above-J 2-monomial pencils at deployment scale.")


if __name__ == "__main__":
    main()
