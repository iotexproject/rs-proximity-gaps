"""g3_4mono_base_cases.py — 4-monomial pencil base case enumeration at (8, 2).

For s = 4 positions (full mod-4 quadrant coverage at L_2), the fold² pencil
is 4-monomial: h(α)(z) = c_1 z^{a_1} + c_2 z^{a_2} + c_3 z^{a_3} + α z^{a_4}
parametrized by single α with 3 fixed coefficient ratios ρ_1, ρ_2, ρ_3.

By 4-mono Substitution Principle (generalization of Note 0284):
$\\Phi_{(a_1,a_2,a_3,a_4),(n,k)} = \\Phi_{(a_1/d, ..., a_4/d), (n/d, k/d)}$
where d = gcd(a_1, a_2, a_3, a_4, n).

Reduce to base case at (4, 1) (only (1,2,3,...) but n=4 has only 4 positions
giving (1,2,3) at most for irreducible — 4-mono needs ≥ 4 positions, only at n ≥ 4).

So skip (4, 1) — there's only 1 case (1,2,3,?) which doesn't have 4 positions.

At (8, 2): C(7, 4) = 35 quadruples (a, b, c, d) with 1 ≤ a < b < c < d ≤ 7.
Enumerate, compute Φ via SymPy GB, check max deg_α.
"""
import sympy as sp
from math import gcd
from functools import reduce as freduce
import multiprocessing as mp
import time


def _gb_worker(eqs_str, p_names, all_var_names, conn):
    p = sp.symbols(",".join(p_names)) if p_names else ()
    if p_names and not isinstance(p, tuple):
        p = (p,)
    all_vars = sp.symbols(",".join(all_var_names))
    if not isinstance(all_vars, tuple):
        all_vars = (all_vars,)
    eqs = [sp.sympify(s) for s in eqs_str]
    G = sp.groebner(eqs, *p, *all_vars, order="lex")
    conn.send([str(g) for g in G])
    conn.close()


def gb_with_timeout(eqs, p_vars, all_vars, timeout_s=45):
    parent_conn, child_conn = mp.Pipe()
    proc = mp.Process(
        target=_gb_worker,
        args=([str(e) for e in eqs], [s.name for s in p_vars],
              [s.name for s in all_vars], child_conn),
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


def classify_4mono(n, k, positions, timeout=45):
    """For 4-mono pencil sum c_i z^{a_i} parametrized by α at last position
    with 3 ρ ratios at first 3 positions: compute deg_α(Φ) via GB."""
    z = sp.Symbol("z")
    rho1, rho2, rho3 = sp.symbols("rho1 rho2 rho3")
    alpha = sp.Symbol("alpha")
    t = 2 * k
    p = sp.symbols("p0:" + str(t))
    if t == 1 and not isinstance(p, tuple):
        p = (p,)
    sigma = z**t + sum(p[i] * z**i for i in range(t))

    # cert: σ_S divides h(α, ρ) = z^a1 + ρ1 z^a2 + ρ2 z^a3 + α z^a4
    # Wait: only 1 free α. Actually the problem is 3 ratios + 1 α = 4 parameters
    # for 4-mono. The bad set in α (with ρ's at "bad" values) bounded.
    a1, a2, a3, a4 = positions
    rems = [sp.Poly(sp.rem(z**a, sigma, z), z) for a in positions]
    coefs = [1, rho1, rho2, alpha]
    # Use ρ3 to scale the 3rd: actually let me redo. We have 4 monomials
    # with 4 coefficients, normalize 1st to 1, others are ρ1, ρ2, α.
    # That's only 3 free params + 1 α. So 3 ρ's, 1 α.
    coefs = [1, rho1, rho2, alpha]
    # Actually let me use 3 ρ's as the ratios, then α, but that's 4 params for
    # 3 ratios + 1 free. Or: 4 params total = (rho1, rho2, rho3, alpha).
    # For the "varied" parameter α and 3 fixed ratios ρ_1, ρ_2, ρ_3:
    coefs = [rho1, rho2, rho3, alpha]
    cert_eqs = []
    for d in range(k, t):
        coef = sum(coefs[i] * rems[i].coeff_monomial(z**d) for i in range(4))
        cert_eqs.append(sp.expand(coef))

    rem_n = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]

    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    if not eqs:
        return "trivial", 0

    G = gb_with_timeout(eqs, list(p), [alpha, rho1, rho2, rho3], timeout)
    if G is None:
        return "TIMEOUT", -1

    last = G[-1]
    free = last.free_symbols
    rho_set = {rho1, rho2, rho3}
    if alpha not in free:
        return ("constant" if not (free & rho_set) else "rho-only"), 0

    poly_phi_alpha = sp.Poly(last, alpha)
    deg_alpha = poly_phi_alpha.degree()
    return last, deg_alpha


def main():
    mp.set_start_method('fork', force=True)
    print("=" * 75)
    print("4-MONOMIAL PENCIL BASE CASE ENUMERATION at (n, k) = (8, 2)")
    print("By 4-mono Substitution Principle, ALL higher-scale 4-mono pencils")
    print("reduce via u = z^d, d = gcd(a_1, ..., a_4, n).")
    print("=" * 75)

    n, k = 8, 2
    max_deg = 0
    max_case = None
    for a in range(1, n - 3):
        for b in range(a + 1, n - 2):
            for c in range(b + 1, n - 1):
                for d in range(c + 1, n):
                    g = freduce(gcd, [a, b, c, d, n])
                    if g != 1:
                        continue
                    t0 = time.time()
                    phi, deg = classify_4mono(n, k, [a, b, c, d])
                    dt = time.time() - t0
                    marker = ""
                    if isinstance(deg, int) and deg > max_deg:
                        max_deg = deg
                        max_case = (a, b, c, d)
                        marker = "  <<< MAX so far"
                    phi_str = str(phi)
                    if len(phi_str) > 50:
                        phi_str = phi_str[:48] + ".."
                    print(f"  ({a}, {b}, {c}, {d}): deg_α={deg} | Φ={phi_str} ({dt:.1f}s){marker}",
                          flush=True)

    print(f"\n=== SUMMARY ===")
    print(f"Max deg_α (= |B(α)| for generic ρ): {max_deg}")
    print(f"Achieved at: {max_case}")
    print(f"By Substitution Principle: K_4 ≤ {max_deg} universal at deployment.")


if __name__ == "__main__":
    main()
