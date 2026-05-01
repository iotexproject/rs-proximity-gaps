"""g3_stage2_h8_multi_prime.py — multi-prime sweep at h=8 with grevlex.
Closes the (n=64, k=16) deployment scale char-uniformly (across primes
with 16 as 8th power).
"""
import sys

sys.path.insert(0, "notes/scripts")
from g3_stage2_h7_grevlex import test_h_grevlex
from g3_stage2_multi_prime import find_rho_eps


def main():
    primes = [17, 41, 73, 97, 113, 137, 193, 241, 257]
    h = 8
    print(f"========== h={h} multi-prime grevlex ==========")
    for p in primes:
        re = find_rho_eps(p)
        if re is None:
            print(f"  p={p}: no rho with rho^8 = 16; skip")
            continue
        rho_val, eps_val = re
        test_h_grevlex(h, p, rho_val, eps_val)


if __name__ == "__main__":
    main()
