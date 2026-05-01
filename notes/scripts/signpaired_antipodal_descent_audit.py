#!/usr/bin/env python3
"""Audit the base case used by Note 0096's sign-paired 2-primary descent."""

from __future__ import annotations

from itertools import combinations


def inv(value: int, p: int) -> int:
    return pow(value % p, p - 2, p)


def primitive_root_of_order(order: int, p: int) -> int:
    for candidate in range(2, p):
        if pow(candidate, order, p) != 1:
            continue
        if all(pow(candidate, divisor, p) != 1 for divisor in range(1, order) if order % divisor == 0):
            return candidate
    raise ValueError(f"no element of order {order} in F_{p}")


def solve_mod_p(matrix: list[list[int]], rhs: list[int], p: int) -> list[int] | None:
    augmented = [row[:] + [value % p] for row, value in zip(matrix, rhs)]
    rows = len(augmented)
    cols = len(matrix[0])
    rank = 0
    pivots: list[int] = []

    for col in range(cols):
        pivot = next((row for row in range(rank, rows) if augmented[row][col] % p), None)
        if pivot is None:
            continue
        augmented[rank], augmented[pivot] = augmented[pivot], augmented[rank]
        scale = inv(augmented[rank][col], p)
        augmented[rank] = [(entry * scale) % p for entry in augmented[rank]]
        for row in range(rows):
            if row == rank or augmented[row][col] % p == 0:
                continue
            factor = augmented[row][col] % p
            augmented[row] = [
                (augmented[row][j] - factor * augmented[rank][j]) % p
                for j in range(cols + 1)
            ]
        pivots.append(col)
        rank += 1

    for row in augmented:
        if all(row[col] % p == 0 for col in range(cols)) and row[cols] % p:
            return None

    solution = [0] * cols
    for row, col in enumerate(pivots):
        solution[col] = augmented[row][cols] % p
    return solution


def bad_ratios(k: int, p: int) -> set[int]:
    n = 4 * k
    omega = primitive_root_of_order(n, p)
    domain = [pow(omega, index, p) for index in range(n)]
    ratios: set[int] = set()

    for c in range(k):
        exponent = k + c
        for subset in combinations(range(n), 2 * k):
            matrix = []
            rhs = []
            for index in subset:
                z = domain[index]
                sign = pow(z, 2 * k, p)
                if sign == p - 1:
                    sign = -1
                matrix.append([pow(z, degree, p) for degree in range(k)] + [(-pow(z, exponent, p)) % p])
                rhs.append((sign * pow(z, exponent, p)) % p)
            solution = solve_mod_p(matrix, rhs, p)
            if solution is None:
                continue
            rho = solution[-1] % p
            if rho:
                ratios.add(rho)
    return ratios


def main() -> None:
    for k, p in [(1, 5), (1, 13), (2, 17), (4, 17)]:
        ratios = bad_ratios(k, p)
        fourth_roots = {rho for rho in range(1, p) if pow(rho, 4, p) == 1}
        print(f"k={k}, F_{p}: bad={sorted(ratios)}, fourth_roots={sorted(fourth_roots)}")
        assert ratios <= fourth_roots


if __name__ == "__main__":
    main()
