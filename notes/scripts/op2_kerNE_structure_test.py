#!/usr/bin/env python3 -u
"""Test what ker N_E actually is, to understand the right parameterization."""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp
from op2_clique_scan import rank_mod, kernel_mod
from op2_tet_consolidated import make_NEs


def poly_mul(a, b, p):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] = (out[i + j] + int(ai) * int(bj)) % p
    return out


def main():
    n = 16; c = 4; p = 17
    D = 8; w = 4
    omega = find_omega(n, p); L = [pow(omega, i, p) for i in range(n)]
    print(f"L = {L}")

    E = (1, 2, 3, 4)  # support of size w=4
    lam = elp(E, L, p)
    print(f"\nE = {E}")
    print(f"Λ_E coefs (low to high): {lam}")

    # Λ_E(x) = ∏(x - L_u). Verify roots.
    for u in E:
        # Eval Λ_E at L_u: should be 0
        val = sum(int(lam[t]) * pow(int(L[u]), t, p) for t in range(len(lam))) % p
        print(f"  Λ_E({L[u]}) = {val}  [should be 0]")

    NEs = make_NEs([E], L, p, D, c, w)
    N = NEs[0]
    print(f"\nN_E (c={c} × D={D}):\n{N}")

    # Compute ker N_E by brute force
    print(f"\nker N_E dimension via kernel_mod:")
    ker = kernel_mod(N, p)
    print(f"  dim = {len(ker)}, expected D - c = {D - c}")

    # Test claim: ker N_E = Λ_E · F_p[x]_{<c}
    print(f"\nTest: is ker N_E = Λ_E * F_p[x]_{{<c={c}}}?")
    # Generate random g ∈ F_p[x]_{<c}, multiply by Λ_E, check if N maps to 0.
    rng = np.random.default_rng(0)
    n_tests = 20
    n_pass = 0
    for trial in range(n_tests):
        g = rng.integers(0, p, c).tolist()  # deg < c, so c coefs
        s = poly_mul(g, lam, p)
        s = s + [0] * (D - len(s))
        s = np.array(s[:D], dtype=np.int64)
        Ns = (N @ s) % p
        if not any(Ns):
            n_pass += 1
        else:
            print(f"  Trial {trial}: FAIL. g={g}, s={s.tolist()}, Ns={Ns.tolist()}")
    print(f"  {n_pass}/{n_tests} of (Λ_E · g) ∈ ker N_E")

    # Reverse: pick basis of ker N_E, check if each is divisible by Λ_E.
    print(f"\nReverse: are basis vectors of ker N_E divisible by Λ_E?")
    for i, b in enumerate(ker):
        # Polynomial division s/Λ_E. If Λ_E divides s, output is exact.
        # Use polynomial long division mod p.
        s = list(b) + [0] * (D - len(b))  # s as list of coefs
        s = s[:D]
        # Divide s(x) by Λ_E(x)
        q, r = poly_divmod(s, list(lam), p)
        print(f"  basis[{i}]: deg quotient = {len(q)-1 if q else -1}, "
              f"remainder = {r if r else 'zero'}")


def poly_divmod(s, lam, p):
    """Polynomial long division s / lam mod p. Return (quotient, remainder)."""
    s = [int(x) % p for x in s]
    lam = [int(x) % p for x in lam]
    # Strip trailing zeros
    while s and s[-1] == 0: s.pop()
    while lam and lam[-1] == 0: lam.pop()
    if not lam:
        raise ValueError("Divide by zero polynomial")
    if not s:
        return [0], [0]
    deg_s = len(s) - 1; deg_lam = len(lam) - 1
    if deg_s < deg_lam:
        return [0], s
    quotient = [0] * (deg_s - deg_lam + 1)
    rem = s[:]
    inv_lc = pow(lam[-1], p - 2, p)
    for i in range(deg_s - deg_lam, -1, -1):
        if i + deg_lam < len(rem) and rem[i + deg_lam] != 0:
            coef = (rem[i + deg_lam] * inv_lc) % p
            quotient[i] = coef
            for j in range(deg_lam + 1):
                rem[i + j] = (rem[i + j] - coef * lam[j]) % p
    while rem and rem[-1] == 0: rem.pop()
    return quotient, rem


if __name__ == '__main__':
    main()
