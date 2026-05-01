"""(3k/2, 2k) family eliminator for k = 2, 4, 6, 8.

Goal: verify Φ(ρ) = ρ^9 - 16ρ universal across k via direct GB on cert+div.

Approach: σ_S = z^{2k} + ρ z^{3k/2} + Q(z), Q deg < k; div constraint
σ_S | z^{4k} - 1; eliminate q_0, ..., q_{k-1} ⟶ Φ(ρ).

For each k, output the GB last polynomial and check it factors as ρ(ρ^8 - 16).
"""
import sympy as sp
import time

def eliminator_via_div(k, ring_order="lex"):
    if k % 2:
        return None
    n = 4 * k
    a = 3 * k // 2
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    q = sp.symbols("q0:" + str(k))
    sigma = z**(2 * k) + rho * z**a + sum(q[j] * z**j for j in range(k))
    rem = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    coeffs = list(rem.all_coeffs())
    # rem has degree < 2k, so up to 2k coeffs (descending).  The constant
    # term is rem at z^0, which after subtracting -1 (from z^n - 1) gives our equations.
    # But rem already represents z^n - 1 mod sigma; for sigma | z^n - 1 we need rem = 0.
    eqs = [sp.expand(c) for c in coeffs if c != 0]
    print(f"  k={k}: {len(eqs)} eqs, {1+k} unknowns ({list(q)}, rho)")
    t0 = time.time()
    G = sp.groebner(eqs, *q, rho, order=ring_order)
    elapsed = time.time() - t0
    print(f"  k={k}: GB done {elapsed:.1f}s, |G|={len(G)}")
    last = G[-1]
    print(f"  k={k}: last = {sp.factor(last)}")
    return last

for k in [2, 4, 6, 8]:
    print(f"=== k = {k}, n = {4*k}, a = {3*k//2}, b = {2*k} ===")
    try:
        eliminator_via_div(k)
    except Exception as e:
        print(f"  FAIL: {e}")
    print()
