"""Print full GB to see what q_j's are forced to.

If σ_S = Π(z^{k/2}), then q_j = 0 for j ∉ {0, k/2}, q_0 = -ρ^4/4, q_{k/2} = -ρ^3/2.

Verify by reading the GB.
"""
import sympy as sp
import time

def full_gb(k):
    n = 4 * k
    a = 3 * k // 2
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    q = sp.symbols("q0:" + str(k))
    sigma = z**(2*k) + rho * z**a + sum(q[j] * z**j for j in range(k))
    rem = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    coeffs = list(rem.all_coeffs())
    eqs = [sp.expand(c) for c in coeffs if c != 0]
    print(f"  k={k}: {len(eqs)} eqs, {1+k} unknowns")
    t0 = time.time()
    G = sp.groebner(eqs, *q, rho, order="lex")
    print(f"  k={k}: GB done {time.time()-t0:.1f}s, |G|={len(G)}")
    for i, g in enumerate(G):
        gf = sp.factor(g)
        print(f"  G[{i}] = {gf}")
    print()

for k in [2, 4, 6]:
    print(f"=== k = {k} ===")
    full_gb(k)
