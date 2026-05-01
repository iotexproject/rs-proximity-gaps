#!/usr/bin/env python3 -u
"""g3_all_ab_classification.py — full (a, b) classification at deployment scales.

For each (a, b) pencil h_ρ(z) = ρ z^a + z^b at scale n = 4k (k ≥ 2), compute:
1. Φ(ρ) via Singular-style GB on cert+div ideal (over Q via SymPy).
2. Number of distinct ρ-roots of Φ (= |B| in algebraic closure).
3. orbit_size = n / gcd(b - a, n).
4. m = |B| / orbit_size (= number of bad-ρ orbits).

Goal: verify m ≤ 2 universal across all (a, b) at (n, k) = (8, 2), (16, 4) and
identify any potential m ≥ 3 outliers.

Theorem 0281 (this branch, just established) gives m = 2 RIGOROUS for (3k/2, 2k);
Notes 0218, 0219 give m ≤ 1 for sign-paired and (k, 2k). For OTHER (a, b),
status open. This script gives empirical data.
"""
import sympy as sp
from math import gcd as ggcd
import time
import multiprocessing as mp


def _gb_worker(eqs_str, p_names, rho_name, conn):
    import sympy as sp
    rho = sp.Symbol(rho_name)
    p = sp.symbols(",".join(p_names))
    if not isinstance(p, tuple):
        p = (p,)
    eqs = [sp.sympify(s) for s in eqs_str]
    G = sp.groebner(eqs, *p, rho, order="lex")
    conn.send([str(g) for g in G])
    conn.close()


def _run_gb_with_timeout(eqs, p_vars, rho, timeout_s=30):
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
        gstrs = parent_conn.recv()
        return [sp.sympify(s) for s in gstrs]
    return None

def classify_ab(n, k, a, b):
    """Compute eliminator Φ(ρ) and orbit info for (a, b) on L_n."""
    if a == b:
        return None
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    t = max(2 * k, 1)  # cert sigma degree = 2k (Johnson agreement)
    # Build sigma with all coefs free
    p = sp.symbols("p0:" + str(t))
    sigma = z**t + sum(p[i] * z**i for i in range(t))
    # Cert: pencil h_ρ = ρ z^a + z^b mod σ_S has degree < k
    rem_a = sp.Poly(sp.rem(z**a, sigma, z), z)
    rem_b = sp.Poly(sp.rem(z**b, sigma, z), z)
    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(z**d) + rem_b.coeff_monomial(z**d))
        for d in range(k, t)
    ]
    # Div: σ_S | z^n - 1
    rem_n = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]
    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    if not eqs:
        return {'a': a, 'b': b, 'phi': None, 'note': 'degenerate (no eqs)'}
    G = _run_gb_with_timeout(eqs, list(p), rho, timeout_s=30)
    if G is None:
        return {'a': a, 'b': b, 'phi': None, 'note': 'GB TIMEOUT (30s)'}
    last = G[-1]
    if rho not in last.free_symbols and any(pp in last.free_symbols for pp in p):
        # Last poly is in p_j only — eliminator vacuous (all ρ valid in some way)
        return {'a': a, 'b': b, 'phi': None, 'note': 'last G is in p_j only (degenerate)'}
    # Try to get univariate ρ-poly: subst all p_j -> 0 in last? Use the lex order
    # — last poly should be in ρ alone if generic. Otherwise scan G for ρ-univariate.
    rho_polys = [g for g in G if g.free_symbols == {rho}]
    if rho_polys:
        phi = rho_polys[-1]
    else:
        phi = last
    phi = sp.factor(phi)
    return {'a': a, 'b': b, 'phi': phi, 'GB_size': len(G)}


def main():
    for n, k in [(8, 2), (16, 4)]:
        print(f"=" * 60)
        print(f"=== n = {n}, k = {k}, deployment scale ===")
        print(f"=" * 60)
        results = {}
        for a in range(1, n):
            for b in range(a + 1, n):
                t0 = time.time()
                res = classify_ab(n, k, a, b)
                if res is None:
                    continue
                elapsed = time.time() - t0
                d = ggcd(b - a, n)
                orbit_size = n // d
                phi = res.get('phi')
                phi_str = str(phi) if phi is not None else res.get('note', '?')
                # Truncate if too long
                if len(phi_str) > 120:
                    phi_str = phi_str[:115] + "..."
                results[(a, b)] = res
                print(f"  (a={a:>2}, b={b:>2}) gcd={d} orb={orbit_size:>2} | {elapsed:.1f}s | Φ = {phi_str}")
        print()
        # Tabulate by family
        print("Summary:")
        nontrivial = [(ab, r) for ab, r in results.items()
                       if r.get('phi') is not None and not r['phi'].free_symbols == set()]
        print(f"  Nontrivial Φ ({len(nontrivial)}):")
        for (a, b), r in nontrivial:
            print(f"    ({a:>2}, {b:>2}): Φ = {r['phi']}")
        print()


if __name__ == "__main__":
    mp.set_start_method('fork', force=True)
    main()
