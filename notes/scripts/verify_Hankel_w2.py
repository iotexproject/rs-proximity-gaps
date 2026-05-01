"""verify_Hankel_w2.py — verify that B_w (weight-≤w syndrome variety) is contained
in the zero locus of (w+1)×(w+1) Hankel determinants.

For w=2, m = n_R - k_R = 6: σ ∈ F_q^6. B_2 ⊂ {σ : det(H_3(σ)) = 0} where
H_3(σ) = [[σ_0,σ_1,σ_2],[σ_1,σ_2,σ_3],[σ_2,σ_3,σ_4]].

For the FRI test n_0=32, k_0=8, R=2: n_R=8, k_R=2, m=6.
δ=0.45 → w_R = 3.

Test:
  - All weight-w errors generate syndromes in B_w
  - All those syndromes satisfy det(H_{w+1}) = 0  ✓ (theoretically)
  - Pulling back through φ: V_δ ⊂ {det(H_{w+1}(φ(α))) = 0}
  - This polynomial has α-degree ≤ (w+1)R, by SZ: |V_δ| ≤ (w+1)R q^{R-1}

Generalization: actually for the right structure, we use (n_R - k_R - w + 1) ×
(n_R - k_R - w + 1) cofactor or similar.
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, gauss_rank, modinv
)


def hankel_det(sigma, w_plus_1, p):
    """Compute det of (w+1)x(w+1) Hankel matrix from sigma."""
    n = len(sigma)
    if w_plus_1 > n - w_plus_1 + 1:
        return None  # not enough sigma entries
    M = [[sigma[i+j] for j in range(w_plus_1)] for i in range(w_plus_1)]
    return det_mod(M, p)


def det_mod(M, p):
    """Determinant of square matrix mod p via Gaussian elimination."""
    M = [row[:] for row in M]
    n = len(M)
    sign = 1
    det = 1
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if M[r][col] % p != 0:
                pivot = r; break
        if pivot is None:
            return 0
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            sign = -sign
        det = (det * M[col][col]) % p
        inv = modinv(M[col][col], p)
        for r in range(col + 1, n):
            if M[r][col] != 0:
                factor = (M[r][col] * inv) % p
                for c in range(col, n):
                    M[r][c] = (M[r][c] - factor * M[col][c]) % p
    return (sign * det) % p


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    m = n_R - k_R

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, m=n_R-k_R={m}")
    print(f"# Test: every wt-≤w_R syndrome σ has det(H_{{w_R+1}}(σ)) = 0")
    print()

    # Enumerate all wt-≤w_R errors and check Hankel det
    n_total = 0
    n_zero = 0
    for w in range(0, w_R + 1):
        for T in combinations(range(n_R), w):
            for vals in product(range(1, p), repeat=w) if w > 0 else [()]:
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = vals[idx]
                sigma = matvec(H_R, e, p)
                d = hankel_det(sigma, w_R + 1, p)
                if d is None:
                    print(f"  ⚠ insufficient σ entries for Hankel size {w_R+1}")
                    return
                n_total += 1
                if d == 0:
                    n_zero += 1
                else:
                    if n_total - n_zero < 5:
                        print(f"  ⚠ wt-{w} error e_T={T} vals={vals}: σ={sigma}, det={d} ≠ 0")

    print(f"# Total wt-≤{w_R} syndromes tested: {n_total}")
    print(f"# Hankel det = 0: {n_zero}")
    if n_zero == n_total:
        print(f"# *** Hankel det vanishes on ALL wt-≤{w_R} syndromes ✓ (Hankel approach valid) ***")
    else:
        print(f"# ★ {n_total - n_zero} counterexamples — Hankel approach needs different size or formulation")


if __name__ == '__main__':
    main()
