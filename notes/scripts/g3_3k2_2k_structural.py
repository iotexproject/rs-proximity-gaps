"""Test structural claim: σ_S(z) = Π(z^{k/2}) where Π(u) = u^4 + ρ u^3 - (ρ^3/2) u - ρ^4/4
is a k-INDEPENDENT degree-4 polynomial.

If true, σ_S | z^{4k} - 1 ⟺ Π(u) | u^8 - 1 (since z^{4k} - 1 = (z^{k/2})^8 - 1).

This reduces the universal-k question to a fixed degree-4 problem in u.
"""
import sympy as sp

def test_at_k(k):
    n = 4 * k
    a = 3 * k // 2
    z = sp.Symbol("z")
    rho = sp.Symbol("rho")
    q = sp.symbols("q0:" + str(k))

    # Conjecture: q_{k/2} = -ρ^3/2, q_0 = -ρ^4/4, q_j = 0 else.
    Q_conj = {}
    for j in range(k):
        if j == 0:
            Q_conj[j] = -rho**4 / 4
        elif j == k // 2:
            Q_conj[j] = -rho**3 / 2
        else:
            Q_conj[j] = sp.S.Zero

    sigma = z**(2*k) + rho * z**a + sum(Q_conj[j] * z**j for j in range(k))
    rem = sp.Poly(sp.rem(z**n - 1, sigma, z), z)
    coeffs = rem.all_coeffs()
    nonzero = [(i, sp.factor(sp.expand(c))) for i, c in enumerate(coeffs) if sp.expand(c) != 0]
    print(f"k={k}: σ_S(z) = z^{2*k} + ρ z^{a} - ρ^3/2 · z^{k//2} - ρ^4/4")
    if not nonzero:
        print(f"  z^{n} - 1 ≡ 0 (mod σ_S) IDENTICALLY — conjecture WRONG (need extra ρ-eq)")
    else:
        print(f"  z^{n} - 1 mod σ_S has {len(nonzero)} nonzero coefs (in z and ρ):")
        for i, c in nonzero[:5]:
            print(f"    coef of z^{rem.degree() - i} (mod σ_S): {c}")
    print()

for k in [2, 4, 6, 8, 10, 12]:
    if k % 2 == 0:
        test_at_k(k)

# Also test the substitution u = z^{k/2} explicitly
print("=" * 60)
print("Substitution test: σ_S = Π(z^{k/2}) where Π(u) = u^4 + ρ u^3 - (ρ^3/2) u - ρ^4/4")
print()
u = sp.Symbol("u")
rho = sp.Symbol("rho")
Pi = u**4 + rho * u**3 - (rho**3 / 2) * u - rho**4 / 4
print(f"Π(u) = {Pi}")
print()
# Π | u^8 - 1?
rem_Pi = sp.rem(u**8 - 1, Pi, u)
print(f"u^8 - 1 mod Π(u) = {sp.expand(rem_Pi)}")
print(f"  → factor: {sp.factor(sp.expand(rem_Pi))}")
