"""g3_stage2_h16_few_primes.py — try h=16 at a couple more primes."""
import sys

sys.path.insert(0, "notes/scripts")
from g3_stage2_h7_grevlex import test_h_grevlex
from g3_stage2_multi_prime import find_rho_eps


def main():
    primes = [41, 73, 97]  # 3 more primes besides 17
    for p in primes:
        re = find_rho_eps(p)
        if re is None:
            print(f"  p={p}: no rho")
            continue
        rho_val, eps_val = re
        test_h_grevlex(16, p, rho_val, eps_val)


if __name__ == "__main__":
    main()
