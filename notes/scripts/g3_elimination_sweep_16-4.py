"""g3_elimination_sweep_16-4.py — sweep ρ-elimination polynomial across all (a, b) at (16, 4).

For each (a, b) ∈ [k, n) × [k, n), a ≠ b, compute the constant-degree
elimination polynomial Φ_{a,b}(ρ) (codex Note 0200 framework) and tabulate:
- degree
- factorization
- whether nonzero degree matches orbit_size (Theorem 0187 prediction)
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from math import gcd

from derive_ratio_elimination_polynomial import rho_polynomials
import sympy as sp


def main():
    n, k = 16, 4
    rho = sp.Symbol("rho")
    rows = []

    # All (a, b) ∈ [k, n)² with a ≠ b
    pairs = [(a, b) for a in range(k, n) for b in range(k, n) if a != b]
    print(f"sweep {len(pairs)} (a, b) pairs at (n={n}, k={k})")
    t0 = time.time()

    for idx, (a, b) in enumerate(pairs):
        polys = rho_polynomials(n, k, a, b)
        if not polys:
            deg_total = -1  # no rho-only polynomial
            poly_str = "<none>"
            deg_nonzero = -1
        else:
            # There may be multiple (cyclotomic factors etc.) — typically one master polynomial
            # Take the LARGEST degree polynomial as the elimination master
            best = max(polys, key=lambda p: sp.Poly(p, rho).degree())
            deg_total = sp.Poly(best, rho).degree()
            poly_str = str(best)
            # Nonzero part: divide out any rho^k factor
            f = sp.factor(best)
            # Count rho's exponent at rho=0
            rho_factor_pow = 0
            test = best
            while sp.simplify(test.subs(rho, 0)) == 0:
                test = sp.simplify(test / rho)
                rho_factor_pow += 1
            deg_nonzero = deg_total - rho_factor_pow

        r = (b - a) % n
        gcd_rn = gcd(r, n)
        orbit_size = n // gcd_rn
        sign_paired = r == n // 2

        rows.append({
            "a": a, "b": b, "r": r, "gcd": gcd_rn,
            "orbit_size": orbit_size, "sign_paired": sign_paired,
            "deg_total": deg_total, "deg_nonzero": deg_nonzero,
            "poly": poly_str,
        })

        elapsed = time.time() - t0
        eta = elapsed / (idx+1) * (len(pairs) - idx - 1)
        if (idx+1) % 10 == 0 or idx < 3:
            print(f"  [{idx+1}/{len(pairs)}] (a={a},b={b}) deg={deg_total} (nonzero={deg_nonzero}) "
                  f"orbit={orbit_size} sign_paired={sign_paired} ETA={eta:.0f}s")

    # Summary
    print()
    print(f"=== Summary ({time.time()-t0:.1f}s) ===")
    print()
    # Group by gcd
    from collections import defaultdict
    by_gcd = defaultdict(list)
    for r in rows:
        by_gcd[r["gcd"]].append(r)

    for g, rs in sorted(by_gcd.items()):
        degs = [r["deg_nonzero"] for r in rs]
        orbits = [r["orbit_size"] for r in rs]
        sign_paired_in = [r["sign_paired"] for r in rs]
        n_sp = sum(sign_paired_in)
        print(f"  gcd(r, n) = {g}, orbit_size = {n//g}: {len(rs)} pairs, {n_sp} sign-paired")
        print(f"    deg_nonzero distribution: {sorted(set(degs))}; max={max(degs)}")
        # Match check: deg_nonzero == orbit_size for non-sign-paired
        nsp = [r for r in rs if not r["sign_paired"]]
        if nsp:
            match = sum(1 for r in nsp if r["deg_nonzero"] == r["orbit_size"])
            print(f"    non-sign-paired: deg_nonzero == orbit_size in {match}/{len(nsp)}")

    # Print some sample polynomials
    print()
    print("=== Sample polynomials ===")
    seen_polys = set()
    for r in rows:
        if r["deg_total"] > 0 and r["poly"] not in seen_polys:
            seen_polys.add(r["poly"])
            print(f"  (a={r['a']},b={r['b']}, r={r['r']}, gcd={r['gcd']}, "
                  f"orbit={r['orbit_size']}, sign_paired={r['sign_paired']}): "
                  f"deg={r['deg_total']} (nonzero={r['deg_nonzero']})")
            print(f"    {r['poly']}")


if __name__ == "__main__":
    main()
