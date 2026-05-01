"""
Test: Stage 2 at h=4 universally.

Symbolic Singular elimination over Q[r]/(r^8-16) gave:
    m1 * (m1^8 + 216 r m1^4 - 486 r^2) = 0.

Setting u = m1^4: u^2 + 216 r u - 486 r^2 = 0.
Discriminant: 48600 r^2 = (90)^2 * 6 * r^2.

For Stage 2 to hold (only m1 = 0): need EITHER
  (C1) Disc is non-QR in F_p (i.e., 6 is non-QR)
  OR
  (C2) The roots u_+, u_- are not 4th powers in F_p.

Test: enumerate all primes p in some range with p == 1 mod 8 (so 8th roots exist),
all rho with rho^8 == 16, and check whether m1^8 + 216 r m1^4 - 486 r^2 == 0
has a non-zero solution in F_p.
"""

from sympy import isprime

def test_h4_at_prime(p):
    """Return list of (rho, m1) pairs where m1 != 0 satisfies m1^8 + 216 rho m1^4 - 486 rho^2 = 0."""
    found = []
    for rho in range(1, p):
        if pow(rho, 8, p) != 16 % p:
            continue
        # Find non-zero m1 with m1^8 + 216 rho m1^4 - 486 rho^2 = 0
        for m1 in range(1, p):
            v = (pow(m1, 8, p) + 216 * rho * pow(m1, 4, p) - 486 * rho * rho) % p
            if v == 0:
                found.append((rho, m1))
    return found

def is_qr(a, p):
    a %= p
    if a == 0:
        return True
    return pow(a, (p-1)//2, p) == 1

def is_4th_power(a, p):
    a %= p
    if a == 0:
        return True
    return pow(a, (p-1)//4, p) == 1

primes = [p for p in range(17, 600) if isprime(p) and p % 8 == 1]

print(f"Testing primes p ≡ 1 mod 8 in [17, 600]: count = {len(primes)}")
print()

print(f"{'p':>5} {'p mod 24':>10} {'(6/p)':>8} {'#non-zero m1':>15}  notes")
print("-"*70)

for p in primes:
    sols = test_h4_at_prime(p)
    qr6 = is_qr(6, p)
    note = ""
    if len(sols) == 0:
        note = "Stage 2 holds (no non-zero m1)"
    else:
        note = f"FAILS — sample (rho, m1) = {sols[:2]}"
    print(f"{p:>5} {p%24:>10} {'+1' if qr6 else '-1':>8} {len(sols):>15}  {note}")
