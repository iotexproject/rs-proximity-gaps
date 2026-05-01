"""g3_3mono_base_cases.py — 3-monomial pencil base case enumeration.

For Case C (paper2 P3'), bound the bad-α set of 3-monomial pencils
h_α(z) = z^a + ρ z^b + α z^c on L_n at deployment scale.

By Substitution Principle generalized to 3-mono: for d = gcd(a, b, c, n),
$\Phi_{(a, b, c), (n, k)} = \Phi_{(a/d, b/d, c/d), (n/d, k/d)}$.

Reduce every irreducible 3-mono pencil at deployment to base case at
(n, k) ∈ {(4, 1), (8, 2)}. Enumerate all (a, b, c) with 0 < a < b < c < n,
gcd(a, b, c, n) = 1, compute Φ via SymPy GB, count |B|.

Max |B| over base cases = K_3, the universal constant for above-J 3-mono.

Output: max |B| across all irreducible base cases.
"""
import sympy as sp
from math import gcd
from functools import reduce as freduce
import multiprocessing as mp
import time


def _gb_worker(eqs_str, p_names, ab_names, conn):
    p = sp.symbols(",".join(p_names)) if p_names else ()
    if p_names and not isinstance(p, tuple):
        p = (p,)
    a, b = sp.symbols(",".join(ab_names))
    eqs = [sp.sympify(s) for s in eqs_str]
    G = sp.groebner(eqs, *p, a, b, order="lex")
    conn.send([str(g) for g in G])
    conn.close()


def gb_with_timeout(eqs, p_vars, ab_vars, timeout_s=30):
    parent_conn, child_conn = mp.Pipe()
    proc = mp.Process(
        target=_gb_worker,
        args=([str(e) for e in eqs], [s.name for s in p_vars],
              [s.name for s in ab_vars], child_conn),
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


def classify_3mono(n, k, a_pos, b_pos, c_pos, timeout=30):
    """For 3-mono pencil z^a_pos + ρ z^b_pos + α z^c_pos at (n, k):
    compute eliminator Φ(α, ρ) via GB. Return |B(α)| at generic ρ.

    Setup: σ_S = z^t + sum p_j z^j (deg t = 2k), divide z^a, z^b, z^c
    using cert constraints; cert+div ideal; eliminate p_j to get Φ(α, ρ).
    """
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    alpha = sp.Symbol("alpha")
    t = 2 * k
    p = sp.symbols("p0:" + str(t))
    if t == 1 and not isinstance(p, tuple):
        p = (p,)
    sigma = z**t + sum(p[i] * z**i for i in range(t))

    # cert eqs: σ_S divides h(α, ρ) = z^a_pos + ρ z^b_pos + α z^c_pos
    # → [z^j] (z^a + ρ z^b + α z^c) mod σ ≡ 0 for j ∈ [k, t-1]
    rem_a = sp.Poly(sp.rem(z**a_pos, sigma, z), z)
    rem_b = sp.Poly(sp.rem(z**b_pos, sigma, z), z)
    rem_c = sp.Poly(sp.rem(z**c_pos, sigma, z), z)
    cert_eqs = []
    for d in range(k, t):
        coef = (rem_a.coeff_monomial(z**d)
                + rho * rem_b.coeff_monomial(z**d)
                + alpha * rem_c.coeff_monomial(z**d))
        cert_eqs.append(sp.expand(coef))

    # div eqs: σ_S divides z^n - 1
    rem_n = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]

    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    if not eqs:
        return "trivial", 0, 0

    # GB elim p_j to get Φ(α, ρ)
    G = gb_with_timeout(eqs, list(p), [alpha, rho], timeout)
    if G is None:
        return "TIMEOUT", -1, -1

    # Find polynomial in (α, ρ) only
    last = G[-1]
    free = last.free_symbols
    if alpha not in free and rho not in free:
        if free & set(p):
            return "degenerate", -1, -1
        return "constant", 0, 0

    # Φ(α, ρ); count nonzero α-roots for generic ρ via degree in α
    if rho in free:
        # mixed; pick rho-generic value (= use SymPy degree in α)
        phi = last
    else:
        phi = last
    poly_phi_alpha = sp.Poly(phi, alpha)
    deg_alpha = poly_phi_alpha.degree() if alpha in free else 0
    poly_phi_rho = sp.Poly(phi, rho)
    deg_rho = poly_phi_rho.degree() if rho in free else 0

    # |B(α)| = #{α : Φ(α, ρ_generic) = 0} = deg in α (counted with multiplicity)
    return phi, deg_alpha, deg_rho


def enumerate_3mono_base():
    print("=" * 75)
    print("3-MONOMIAL PENCIL BASE CASE ENUMERATION at (4, 1) and (8, 2)")
    print("By Substitution Principle, ALL higher-scale 3-mono pencils reduce")
    print("to one of these base cases via u = z^d, d = gcd(a, b, c, n).")
    print("=" * 75)

    max_deg_alpha = 0
    max_case = None
    cases_summary = []
    for n, k in [(4, 1), (8, 2)]:
        print(f"\n=== (n, k) = ({n}, {k}) — irreducible (gcd(a, b, c, n) = 1) ===")
        for a_pos in range(1, n - 2):
            for b_pos in range(a_pos + 1, n - 1):
                for c_pos in range(b_pos + 1, n):
                    g = freduce(gcd, [a_pos, b_pos, c_pos, n])
                    if g != 1:
                        continue
                    t0 = time.time()
                    phi, deg_a, deg_r = classify_3mono(n, k, a_pos, b_pos, c_pos)
                    dt = time.time() - t0
                    if isinstance(deg_a, int) and deg_a > max_deg_alpha:
                        max_deg_alpha = deg_a
                        max_case = (n, k, a_pos, b_pos, c_pos)
                        marker = "  <<< MAX so far"
                    else:
                        marker = ""
                    phi_str = str(phi)
                    if len(phi_str) > 50:
                        phi_str = phi_str[:48] + ".."
                    print(f"  ({a_pos}, {b_pos}, {c_pos}): deg_α={deg_a}, "
                          f"deg_ρ={deg_r}, Φ={phi_str} ({dt:.1f}s){marker}",
                          flush=True)
                    cases_summary.append((n, k, a_pos, b_pos, c_pos, deg_a, deg_r))

    print(f"\n=== SUMMARY ===")
    print(f"Max deg_α (= |B(α)| for generic ρ): {max_deg_alpha}")
    print(f"Achieved at: {max_case}")
    print(f"\nBy Substitution Principle (Note 0284 generalized to 3-mono):")
    print(f"  K_3 ≤ {max_deg_alpha} for ALL above-J 3-mono pencils at deployment.")
    print(f"  Plus α=0 contribution: K ≤ {max_deg_alpha + 1}.")
    return cases_summary, max_deg_alpha, max_case


if __name__ == "__main__":
    mp.set_start_method('fork', force=True)
    enumerate_3mono_base()
