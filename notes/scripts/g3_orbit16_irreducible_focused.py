"""Focused (16, 4) orbit-16 irreducible (b-a odd, gcd 1) sweep.

Critical: if any (a, b) with gcd(b-a, 16) = 1 has |B| ≥ 1, then |B| ≥ 16
(orbit_size = 16), breaking K ≤ 8 universal.

Hypothesis: ALL orbit-16 cases have m = 0 (Φ = 1, |B| = 0). Verify.

Use multiprocessing with longer timeout (60s).
"""
import sympy as sp
from math import gcd as ggcd
import multiprocessing as mp
import time


def _gb_worker(eqs_str, p_names, rho_name, conn):
    rho = sp.Symbol(rho_name)
    p = sp.symbols(",".join(p_names))
    if not isinstance(p, tuple):
        p = (p,)
    eqs = [sp.sympify(s) for s in eqs_str]
    G = sp.groebner(eqs, *p, rho, order="lex")
    conn.send([str(g) for g in G])
    conn.close()


def gb_with_timeout(eqs, p_vars, rho, timeout_s=60):
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
        return None, "TIMEOUT"
    if parent_conn.poll():
        gstrs = parent_conn.recv()
        return [sp.sympify(s) for s in gstrs], "OK"
    return None, "no result"


def classify(n, k, a, b, timeout=60):
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    t = 2 * k
    p = sp.symbols("p0:" + str(t))
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
        return "trivial (no eqs)"
    G, status = gb_with_timeout(eqs, list(p), rho, timeout)
    if G is None:
        return status
    last = G[-1]
    if rho not in last.free_symbols and any(pp in last.free_symbols for pp in p):
        return "degenerate (last G is in p_j only)"
    rho_polys = [g for g in G if g.free_symbols == {rho}]
    if rho_polys:
        return sp.factor(rho_polys[-1])
    return sp.factor(last)


def main():
    mp.set_start_method('fork', force=True)
    n, k = 16, 4
    cases = []
    for a in range(k, n - 1):
        for b in range(a + 1, n):
            if (b - a) % 2 == 1 and ggcd(ggcd(a, b), n) == 1:
                cases.append((a, b))
    print(f"=== {len(cases)} orbit-16 irreducible cases at (n={n}, k={k}) ===")
    print(f"=== timeout = 60s per case ===")
    print()
    for a, b in cases:
        t0 = time.time()
        phi = classify(n, k, a, b, timeout=60)
        elapsed = time.time() - t0
        phi_str = str(phi)
        if len(phi_str) > 100:
            phi_str = phi_str[:95] + "..."
        marker = ""
        if phi != "trivial (no eqs)" and "degenerate" not in str(phi) and "TIMEOUT" not in str(phi):
            if phi != 1 and phi != sp.Symbol("rho"):
                marker = "  <<< NONTRIVIAL"
        print(f"  ({a:>2},{b:>2}) | {elapsed:5.1f}s | Φ = {phi_str}{marker}", flush=True)


if __name__ == "__main__":
    main()
