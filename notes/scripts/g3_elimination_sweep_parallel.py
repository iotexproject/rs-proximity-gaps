"""g3_elimination_sweep_parallel.py — parallel ρ-elimination sweep with per-pair timeout.

For each (a, b) at given (n, k), compute Φ_{a,b}(ρ) elimination polynomial via
codex's framework (Note 0200). Use multiprocessing to parallelize and a per-pair
timeout to skip slow Groebner cases.
"""
import sys, os, time, multiprocessing as mp
from math import gcd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def compute_one(args):
    n, k, a, b = args
    try:
        # Local imports to ensure subprocess isolation
        import sympy as sp
        rho = sp.Symbol("rho")
        x = sp.Symbol("x")
        t = n // 2
        p = sp.symbols("p0:" + str(t))
        P = x**t + sum(p[i] * x**i for i in range(t))

        divisor_eqs = [sp.expand(c) for c in sp.Poly(sp.rem(x**n - 1, P, x), x).all_coeffs()]
        rem_a = sp.Poly(sp.rem(x**a, P, x), x)
        rem_b = sp.Poly(sp.rem(x**b, P, x), x)
        cert_eqs = [
            sp.expand(rho * rem_a.coeff_monomial(x**degree) + rem_b.coeff_monomial(x**degree))
            for degree in range(k, t)
        ]
        basis = sp.groebner(divisor_eqs + cert_eqs, *p, rho, order="lex")
        out = []
        for poly in basis.polys:
            expr = sp.factor(poly.as_expr())
            if expr != 0 and not any(expr.has(var) for var in p):
                out.append(expr)

        if not out:
            return (a, b, -1, -1, "<no rho-only>")
        best = max(out, key=lambda p: sp.Poly(p, rho).degree())
        deg_total = sp.Poly(best, rho).degree()
        # Compute deg_nonzero (strip rho^k factor)
        rho_factor_pow = 0
        test = best
        while sp.simplify(test.subs(rho, 0)) == 0:
            test = sp.simplify(test / rho)
            rho_factor_pow += 1
        deg_nonzero = deg_total - rho_factor_pow
        return (a, b, deg_total, deg_nonzero, str(best))
    except Exception as e:
        return (a, b, -2, -2, f"<error: {e}>")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()
    n, k = args.n, args.k

    pairs = [(n, k, a, b) for a in range(k, n) for b in range(k, n) if a != b]
    print(f"sweep {len(pairs)} pairs at (n={n}, k={k}) with {args.workers} workers, timeout={args.timeout}s")

    rows = []
    t0 = time.time()
    with mp.Pool(args.workers) as pool:
        results = [(args_, pool.apply_async(compute_one, (args_,))) for args_ in pairs]
        for idx, (args_, res) in enumerate(results):
            n_, k_, a, b = args_
            try:
                row = res.get(timeout=args.timeout)
            except mp.TimeoutError:
                row = (a, b, -3, -3, "<TIMEOUT>")
            rows.append(row)
            elapsed = time.time() - t0
            if (idx + 1) % 5 == 0 or idx < 3:
                done_ok = sum(1 for r in rows if r[2] >= 0)
                print(f"  [{idx+1}/{len(pairs)}] "
                      f"(a={a},b={b}): deg={row[2]} (nonzero={row[3]}) "
                      f"[ok={done_ok}, elapsed={elapsed:.0f}s]")

    # Summary
    print()
    print(f"=== Summary (total {time.time()-t0:.1f}s) ===")
    by_status = {}
    for a, b, deg_t, deg_nz, _ in rows:
        st = "ok" if deg_t >= 0 else ("timeout" if deg_t == -3 else "error")
        by_status.setdefault(st, []).append((a, b))
    for st, ps in by_status.items():
        print(f"  {st}: {len(ps)} pairs")
    print()

    # Print errors / timeouts explicitly
    err_rows = [(a, b, deg_t, deg_nz, poly) for a, b, deg_t, deg_nz, poly in rows if deg_t < 0]
    if err_rows:
        print("\n=== Errors / timeouts ===")
        for a, b, deg_t, deg_nz, poly in err_rows:
            print(f"  (a={a},b={b}): deg={deg_t} {poly}")

    # Print ALL ok rows
    print("\n=== All rows ===")
    for a, b, deg_t, deg_nz, poly in rows:
        if deg_t < 0: continue
        r = (b - a) % n
        g_ = gcd(r, n)
        print(f"  (a={a:2d},b={b:2d}) r={r:2d} gcd={g_} deg={deg_t} (nz={deg_nz})  {poly[:80]}")

    # Group by gcd(b-a, n)
    from collections import defaultdict
    by_gcd = defaultdict(list)
    for a, b, deg_t, deg_nz, poly in rows:
        if deg_t < 0: continue
        r = (b - a) % n
        g_ = gcd(r, n)
        by_gcd[g_].append((a, b, r, deg_t, deg_nz, poly))

    print("=== Degrees by gcd(b-a, n) ===")
    for g_, lst in sorted(by_gcd.items()):
        orbit_size = n // g_
        sign_paired_count = sum(1 for a, b, r, *_ in lst if r == n // 2)
        deg_nz_set = sorted(set(r[4] for r in lst))
        print(f"  gcd = {g_} (orbit_size = {orbit_size}, sign_paired={sign_paired_count}): "
              f"{len(lst)} pairs, deg_nonzero in {deg_nz_set}")

    # Print one example per gcd
    print()
    print("=== Sample polynomial per gcd ===")
    for g_, lst in sorted(by_gcd.items()):
        ex = lst[0]
        print(f"  gcd={g_}, (a={ex[0]},b={ex[1]}): deg={ex[3]}, nonzero={ex[4]}")
        print(f"    {ex[5]}")


if __name__ == "__main__":
    main()
