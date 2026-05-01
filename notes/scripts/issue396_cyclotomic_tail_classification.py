"""Exact cyclotomic classification for issue #396 monomial tails.

This is the proof-certificate companion to Note 0331.  It works over

    Z[zeta_16] = Z[t] / (t^8 + 1)

instead of over finite fields.  For roots x_i in a candidate set T of five
16th roots, the determinant with exponent rows {0,1,2,3,e} factors as

    det(x_i^a)_{a in {0,1,2,3,e}} = Vandermonde(T) * h_{e-4}(T),

where h_m is the complete homogeneous symmetric polynomial.  Since the roots
in T are distinct, the determinant vanishes exactly when h_{e-4}(T)=0.

Therefore x^e can agree with a degree <4 polynomial on an 8-subset S only if
h_{e-4}(T)=0 for every five-subset T of S.  This script classifies those S
exactly in Z[zeta_16].
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations


N = 16
PHI_DEG = 8


def add(a, b):
    return tuple(ai + bi for ai, bi in zip(a, b))


def mul(a, b):
    raw = [0] * (2 * PHI_DEG - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj:
                raw[i + j] += ai * bj
    for k in range(len(raw) - 1, PHI_DEG - 1, -1):
        if raw[k]:
            raw[k - PHI_DEG] -= raw[k]
    return tuple(raw[:PHI_DEG])


ZERO = (0,) * PHI_DEG
ONE = (1,) + (0,) * (PHI_DEG - 1)


def zeta_power(exp):
    exp %= N
    sign = 1
    if exp >= PHI_DEG:
        exp -= PHI_DEG
        sign = -1
    out = [0] * PHI_DEG
    out[exp] = sign
    return tuple(out)


ROOTS = [zeta_power(i) for i in range(N)]


def complete_homogeneous(indices, degree):
    """Return h_degree(ROOTS[i] for i in indices) in Z[zeta_16]."""
    coeffs = [ZERO] * (degree + 1)
    coeffs[0] = ONE
    for idx in indices:
        z = ROOTS[idx]
        powers = [ONE]
        for _ in range(degree):
            powers.append(mul(powers[-1], z))
        new = [ZERO] * (degree + 1)
        for old_deg, old_coeff in enumerate(coeffs):
            if old_coeff == ZERO:
                continue
            for add_deg in range(degree - old_deg + 1):
                new[old_deg + add_deg] = add(
                    new[old_deg + add_deg], mul(old_coeff, powers[add_deg])
                )
        coeffs = new
    return coeffs[degree]


def occupancy(S):
    counts = [0, 0, 0, 0]
    for i in S:
        counts[i % 4] += 1
    return tuple(counts)


def has_full_quarter(S):
    return max(occupancy(S)) == 4


def main():
    print("Issue #396 exact cyclotomic monomial-tail classification")
    print("ring=Z[zeta_16]=Z[t]/(t^8+1)")
    print()
    all_eight = list(combinations(range(N), 8))
    for e in range(4, 16):
        m = e - 4
        zero_fives = {
            T for T in combinations(range(N), 5) if complete_homogeneous(T, m) == ZERO
        }
        good_eights = [
            S
            for S in all_eight
            if all(T in zero_fives for T in combinations(S, 5))
        ]
        occ_hist = Counter(occupancy(S) for S in good_eights)
        full_count = sum(1 for S in good_eights if has_full_quarter(S))
        no_full_count = len(good_eights) - full_count
        print(f"e={e} h_degree={m}")
        print(f"  zero_five_subsets={len(zero_fives)}")
        print(f"  eight_subsets={len(good_eights)} full={full_count} no_full={no_full_count}")
        print(f"  occupancy_hist={dict(sorted(occ_hist.items()))}")
        if good_eights:
            for S in good_eights:
                print(f"    S={S}")
        print()
        if no_full_count:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
