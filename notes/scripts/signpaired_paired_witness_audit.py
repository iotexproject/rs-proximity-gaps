#!/usr/bin/env python3
"""
Audit the paired-compatibility repair proposed for the sign-paired upper bound.

The current paper proof tries to prove that every sign-paired half-set witness
must be balanced between the two z^(2k)=+/-1 half-cosets.  A one-side proof is
false (see signpaired_balance_audit.py).  This script checks the stronger paired
claim on a minimal explicit example.

Result: the all-k paired-balancing statement is false.  Over F_13 with n=12,
k=3, c=1, rho=10, the degree-<k polynomial r(z)=z^2+10 agrees with the
sign-paired pencil on an imbalanced half-set: two plus-coset points and four
minus-coset points.  Since rho^4=3 != 1, this is not one of the four expected
fourth-root ratios.

This does not hit deployment powers of two directly, but it invalidates the
paper's current "for every k >= 1" sign-paired upper-bound statement and shows
that any correct theorem needs extra hypotheses, most likely k a power of two
(or another arising/deployment restriction).
"""

from __future__ import annotations


def primitive_root_of_order(order: int, p: int) -> int:
    for candidate in range(2, p):
        if pow(candidate, order, p) != 1:
            continue
        if all(pow(candidate, divisor, p) != 1 for divisor in range(1, order) if order % divisor == 0):
            return candidate
    raise ValueError(f"no element of order {order} in F_{p}")


def eval_poly(coeffs: list[int], z: int, p: int) -> int:
    return sum(coeff * pow(z, degree, p) for degree, coeff in enumerate(coeffs)) % p


def verify_counterexample() -> None:
    p = 13
    k = 3
    c = 1
    n = 4 * k
    exponent = k + c
    omega = primitive_root_of_order(n, p)
    domain = [pow(omega, index, p) for index in range(n)]

    rho = 10
    r_coeffs = [10, 0, 1]  # r(z) = z^2 + 10, degree < k.
    plus_indices = (0, 6)  # z = +/-1, inside z^(2k)=+1.
    minus_indices = (1, 3, 7, 9)

    assert pow(rho, 4, p) != 1
    assert len(plus_indices) + len(minus_indices) == 2 * k
    assert len(plus_indices) != k

    print("PAIRED IMBALANCED COUNTEREXAMPLE")
    print(f"  field: F_{p}")
    print(f"  n={n}, k={k}, c={c}, exponent={exponent}, omega={omega}")
    print(f"  rho={rho}, rho^4={pow(rho, 4, p)} != 1")
    print(f"  r coeffs={r_coeffs}  # r(z)=z^2+10")
    print(f"  plus indices={plus_indices}, minus indices={minus_indices}")

    for side, indices, scalar in (
        ("plus", plus_indices, rho + 1),
        ("minus", minus_indices, rho - 1),
    ):
        for index in indices:
            z = domain[index]
            lhs = eval_poly(r_coeffs, z, p)
            rhs = (scalar * pow(z, exponent, p)) % p
            half_coset = pow(z, 2 * k, p)
            expected_half = 1 if side == "plus" else p - 1
            print(
                f"  {side:5s} index={index:2d} z={z:2d} "
                f"z^(2k)={half_coset:2d} r(z)={lhs:2d} target={rhs:2d}"
            )
            assert half_coset == expected_half
            assert lhs == rhs

    print("  verified=True")


if __name__ == "__main__":
    verify_counterexample()
