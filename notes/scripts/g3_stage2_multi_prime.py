"""g3_stage2_multi_prime.py — extend Stage 2 modular check to multiple primes.

For each prime p ≡ 1 mod 8 (or with 16 as 8th power), find rho with
rho^8 ≡ 16 mod p, set eps = rho^4/4, run Stage 2 GB.

Reports success across all primes tested.
"""
import sys

import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_h5_modular import test_h_modular


def find_rho_eps(p):
    """Find (rho, eps) in F_p satisfying rho^8 ≡ 16 and eps = rho^4/4.
    Returns None if no such rho exists."""
    for rho in range(2, p):
        if pow(rho, 8, p) == 16 % p:
            inv4 = pow(4, p - 2, p)
            eps = (pow(rho, 4, p) * inv4) % p
            return rho, eps
    return None


def main():
    primes = [17, 41, 73, 97, 113, 137, 193, 241, 257]
    for h in [5, 6]:
        print(f"\n========== h={h} ==========")
        for p in primes:
            re = find_rho_eps(p)
            if re is None:
                print(f"  p={p}: no rho with rho^8 = 16; skip")
                continue
            rho_val, eps_val = re
            # Verify: rho^8 ≡ 16, eps^2 ≡ 1
            assert pow(rho_val, 8, p) == 16 % p
            assert pow(eps_val, 2, p) == 1 % p
            test_h_modular(h, p, rho_val, eps_val)


if __name__ == "__main__":
    main()
