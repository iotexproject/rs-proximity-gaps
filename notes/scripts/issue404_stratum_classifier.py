#!/usr/bin/env python3
"""Issue #404 small-parameter paper2/paper3 stratum classifier.

For small cyclic RS parameters, compute:
  * K(s1,s2) = #{alpha in F_p : s1 + alpha s2 is decodable with weight <= w}
  * minimal joint paper3 Vandermonde support |S*(s1,s2)|
  * whether high-K samples lie on leading paper3 components |S*| = w+1

This is intended as a fast falsification/triage tool for the proposed
paper2 sparse-worst + paper3 codim composition.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import random
from itertools import combinations


def modinv(a: int, p: int) -> int:
    return pow(a % p, p - 2, p)


def rank_mod_p(matrix: list[list[int]], p: int) -> int:
    rows = [row[:] for row in matrix if any(x % p for x in row)]
    if not rows:
        return 0
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % p:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = modinv(rows[rank][col], p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for row in range(row_count):
            if row == rank or rows[row][col] % p == 0:
                continue
            factor = rows[row][col] % p
            rows[row] = [(rows[row][j] - factor * rows[rank][j]) % p for j in range(col_count)]
        rank += 1
        if rank == row_count:
            break
    return rank


def rref_mod_p(matrix: list[list[int]], p: int) -> tuple[list[list[int]], list[int]]:
    rows = [row[:] for row in matrix]
    if not rows:
        return [], []
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    pivots: list[int] = []
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % p:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = modinv(rows[rank][col], p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for row in range(row_count):
            if row == rank or rows[row][col] % p == 0:
                continue
            factor = rows[row][col] % p
            rows[row] = [(rows[row][j] - factor * rows[rank][j]) % p for j in range(col_count)]
        pivots.append(col)
        rank += 1
        if rank == row_count:
            break
    return rows[:rank], pivots


def nullspace_mod_p(matrix: list[list[int]], p: int, cols: int) -> list[list[int]]:
    rref, pivots = rref_mod_p(matrix, p)
    pivot_set = set(pivots)
    free_cols = [col for col in range(cols) if col not in pivot_set]
    basis: list[list[int]] = []
    for free_col in free_cols:
        vector = [0] * cols
        vector[free_col] = 1
        for row_index, pivot_col in enumerate(pivots):
            vector[pivot_col] = (-rref[row_index][free_col]) % p
        basis.append(vector)
    return basis


def dot(left: list[int], right: list[int], p: int) -> int:
    return sum(x * y for x, y in zip(left, right)) % p


def primitive_root(p: int) -> int:
    factors: list[int] = []
    value = p - 1
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        factors.append(value)
    for candidate in range(2, p):
        if all(pow(candidate, (p - 1) // factor, p) != 1 for factor in factors):
            return candidate
    raise RuntimeError(f"no primitive root for p={p}")


def syndrome_of_monomial(exp: int, n: int, k: int, p: int, domain: list[int]) -> list[int]:
    syndrome_len = n - k
    return [sum(pow(z, exp + degree, p) for z in domain) % p for degree in range(syndrome_len)]


def add_scaled(target: list[int], source: list[int], scalar: int, p: int) -> list[int]:
    return [(x + scalar * y) % p for x, y in zip(target, source)]


def random_sparse_syndrome(
    rng: random.Random,
    n: int,
    k: int,
    p: int,
    domain: list[int],
    support_size: int,
) -> tuple[list[int], tuple[int, ...]]:
    exponents = tuple(sorted(rng.sample(range(k, n), support_size)))
    syndrome = [0] * (n - k)
    terms: list[tuple[int, int]] = []
    for exp in exponents:
        coeff = rng.randrange(1, p)
        terms.append((exp, coeff))
        syndrome = add_scaled(syndrome, syndrome_of_monomial(exp, n, k, p, domain), coeff, p)
    return syndrome, tuple(terms)


def random_dense_syndrome(rng: random.Random, syndrome_len: int, p: int) -> list[int]:
    return [rng.randrange(p) for _ in range(syndrome_len)]


_WORKER: dict[str, object] = {}


def init_worker(config: dict[str, object]) -> None:
    global _WORKER
    _WORKER = config


def worker_sparse_sample(seed: int) -> tuple[dict[str, object], int]:
    rng = random.Random(seed)
    attempts = 0
    while True:
        attempts += 1
        n = int(_WORKER["n"])
        k = int(_WORKER["k"])
        p = int(_WORKER["p"])
        domain = _WORKER["domain"]
        normal_sets = _WORKER["normal_sets"]
        require_endpoints_above = bool(_WORKER["require_endpoints_above"])
        require_joint_above = bool(_WORKER["require_joint_above"])
        s1, terms1 = random_sparse_syndrome(rng, n, k, p, domain, 3)
        s2, terms2 = random_sparse_syndrome(rng, n, k, p, domain, 3)
        if require_endpoints_above and (
            not admissible_above_j(s1, normal_sets, p) or not admissible_above_j(s2, normal_sets, p)
        ):
            continue
        if require_joint_above and not joint_above_delta(s1, s2, normal_sets, p):
            continue
        return (
            {
                "K": k_value(s1, s2, normal_sets, p),
                "Sstar": "?",
                "s1": s1,
                "s2": s2,
                "terms1": terms1,
                "terms2": terms2,
            },
            attempts,
        )


def worker_dense_sample(seed: int) -> tuple[dict[str, object], int]:
    rng = random.Random(seed)
    attempts = 0
    while True:
        attempts += 1
        p = int(_WORKER["p"])
        syndrome_len = int(_WORKER["syndrome_len"])
        normal_sets = _WORKER["normal_sets"]
        require_endpoints_above = bool(_WORKER["require_endpoints_above"])
        require_joint_above = bool(_WORKER["require_joint_above"])
        d1 = random_dense_syndrome(rng, syndrome_len, p)
        d2 = random_dense_syndrome(rng, syndrome_len, p)
        if require_endpoints_above and (
            not admissible_above_j(d1, normal_sets, p) or not admissible_above_j(d2, normal_sets, p)
        ):
            continue
        if require_joint_above and not joint_above_delta(d1, d2, normal_sets, p):
            continue
        return (
            {
                "K": k_value(d1, d2, normal_sets, p),
                "Sstar": "?",
                "s1": d1,
                "s2": d2,
            },
            attempts,
        )


def precompute_normals(ev: list[list[int]], w: int, p: int) -> list[tuple[tuple[int, ...], list[tuple[int, ...]]]]:
    syndrome_len = len(ev[0])
    result: list[tuple[tuple[int, ...], list[tuple[int, ...]]]] = []
    for support in combinations(range(len(ev)), w):
        normals = nullspace_mod_p([ev[index] for index in support], p, syndrome_len)
        result.append((support, [tuple(normal) for normal in normals]))
    return result


def is_decodable(
    syndrome: tuple[int, ...], normal_sets: list[tuple[tuple[int, ...], list[tuple[int, ...]]]], p: int
) -> bool:
    for _support, normals in normal_sets:
        if all(dot(normal, syndrome, p) == 0 for normal in normals):
            return True
    return False


def k_value(s1: list[int], s2: list[int], normal_sets: list[tuple[tuple[int, ...], list[tuple[int, ...]]]], p: int) -> int:
    """Count alphas for which the syndrome line meets some weight-w span.

    For a fixed support E with normal rows n_j, membership is the linear
    system n_j(s1 + alpha s2)=0.  It contributes either no alpha, one alpha,
    or all alphas.  This avoids the slower q-by-support membership scan.
    """
    alphas: set[int] = set()
    for _support, normals in normal_sets:
        forced_alpha: int | None = None
        feasible = True
        all_alpha = True
        for normal in normals:
            left = dot(normal, s1, p)
            slope = dot(normal, s2, p)
            if slope == 0:
                if left != 0:
                    feasible = False
                    break
                continue
            all_alpha = False
            alpha = (-left * modinv(slope, p)) % p
            if forced_alpha is None:
                forced_alpha = alpha
            elif forced_alpha != alpha:
                feasible = False
                break
        if not feasible:
            continue
        if all_alpha:
            return p
        if forced_alpha is not None:
            alphas.add(forced_alpha)
            if len(alphas) == p:
                return p
    return len(alphas)


def admissible_above_j(syndrome: list[int], normal_sets: list[tuple[tuple[int, ...], list[tuple[int, ...]]]], p: int) -> bool:
    """Return True when the endpoint is not decodable at the configured weight."""
    return not is_decodable(tuple(syndrome), normal_sets, p)


def precompute_support_normals_by_size(
    ev: list[list[int]], p: int, max_size: int
) -> list[list[tuple[tuple[int, ...], list[tuple[int, ...]]]]]:
    syndrome_len = len(ev[0])
    result: list[list[tuple[tuple[int, ...], list[tuple[int, ...]]]]] = []
    for size in range(max_size + 1):
        size_result: list[tuple[tuple[int, ...], list[tuple[int, ...]]]] = []
        if size >= syndrome_len:
            size_result.append((tuple(range(size)), []))
        else:
            for support in combinations(range(len(ev)), size):
                normals = nullspace_mod_p([ev[index] for index in support], p, syndrome_len)
                size_result.append((support, [tuple(normal) for normal in normals]))
        result.append(size_result)
    return result


def minimal_joint_support_size(
    s1: list[int],
    s2: list[int],
    support_normals_by_size: list[list[tuple[tuple[int, ...], list[tuple[int, ...]]]]],
    p: int,
    max_size: int | None = None,
) -> int | str | None:
    upper = len(support_normals_by_size) - 1 if max_size is None else min(max_size, len(support_normals_by_size) - 1)
    for size in range(upper + 1):
        for _support, normals in support_normals_by_size[size]:
            if all(dot(normal, s1, p) == 0 and dot(normal, s2, p) == 0 for normal in normals):
                return size
    return None if max_size is None else f">{upper}"


def joint_above_delta(
    s1: list[int],
    s2: list[int],
    normal_sets: list[tuple[tuple[int, ...], list[tuple[int, ...]]]],
    p: int,
) -> bool:
    """Return True iff the syndrome pair has no common support of size <= w.

    The supplied normal_sets are for supports of exactly size w.  Membership in
    a smaller support implies membership in a size-w superset, so scanning
    exactly size-w supports is equivalent to the joint-distance condition.
    """
    for _support, normals in normal_sets:
        if all(dot(normal, s1, p) == 0 and dot(normal, s2, p) == 0 for normal in normals):
            return False
    return True


def summarize(samples: list[dict[str, object]], label: str, leading_size: int, threshold: int) -> None:
    if not samples:
        print(f"{label}: no samples")
        return
    max_k = max(int(sample["K"]) for sample in samples)
    high = [sample for sample in samples if int(sample["K"]) > threshold]
    leading_high = [sample for sample in high if sample["Sstar"] == leading_size]
    leading_cap_high = [
        sample for sample in high if isinstance(sample["Sstar"], int) and int(sample["Sstar"]) <= leading_size
    ]
    print(
        f"{label}: samples={len(samples)} maxK={max_k} "
        f"high(K>{threshold})={len(high)} "
        f"Sstar_le_leading_high={len(leading_cap_high)} exact_leading_high={len(leading_high)}"
    )
    for sample in sorted(samples, key=lambda item: int(item["K"]), reverse=True)[:8]:
        print(f"  top {sample}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=12)
    parser.add_argument("--k", type=int, default=6)
    parser.add_argument("--p", type=int, default=13)
    parser.add_argument("--c", type=int, default=3)
    parser.add_argument("--samples", type=int, default=60)
    parser.add_argument("--seed", type=int, default=404)
    parser.add_argument(
        "--sstar-top",
        type=int,
        default=8,
        help="compute S* only for high-K samples and the top N samples in each class; use -1 for all",
    )
    parser.add_argument(
        "--require-endpoints-above",
        action="store_true",
        help="discard samples where either endpoint is decodable at weight w",
    )
    parser.add_argument(
        "--require-joint-above",
        action="store_true",
        help="discard samples whose syndrome pair has a common support of size <= w",
    )
    parser.add_argument("--jobs", type=int, default=1, help="parallel worker processes for K scoring")
    parser.add_argument(
        "--show-syndromes",
        action="store_true",
        help="keep syndrome vectors in top-sample output for concrete witnesses",
    )
    parser.add_argument(
        "--full-sstar",
        action="store_true",
        help="compute exact minimal S* instead of stopping at the leading size",
    )
    args = parser.parse_args()

    if (args.p - 1) % args.n != 0:
        raise SystemExit("need n | p-1")
    syndrome_len = args.n - args.k
    w = syndrome_len - args.c
    threshold = (2 * syndrome_len - 1) // args.c
    leading_size = w + 1
    sstar_cap = None if args.full_sstar else leading_size
    generator = primitive_root(args.p)
    omega = pow(generator, (args.p - 1) // args.n, args.p)
    domain = [pow(omega, index, args.p) for index in range(args.n)]
    ev = [[pow(z, degree, args.p) for degree in range(syndrome_len)] for z in domain]

    print(
        f"PARAM n={args.n} k={args.k} p={args.p} D={syndrome_len} "
        f"w={w} c={args.c} T={threshold} leading_size={leading_size}"
    )
    normal_sets = precompute_normals(ev, w, args.p)
    print(f"precomputed {len(normal_sets)} support normal systems")
    if sstar_cap is None:
        sstar_precompute_cap = min(len(ev), syndrome_len)
    else:
        sstar_precompute_cap = min(max(sstar_cap, w if args.require_joint_above else 0), len(ev), syndrome_len)
    support_normals_by_size = precompute_support_normals_by_size(ev, args.p, sstar_precompute_cap)
    print(
        "precomputed S* support normal systems "
        f"through size {sstar_precompute_cap}: "
        f"{sum(len(bucket) for bucket in support_normals_by_size)} supports"
    )

    rng = random.Random(args.seed)
    sparse_samples: list[dict[str, object]] = []
    dense_samples: list[dict[str, object]] = []
    sparse_attempts = 0
    dense_attempts = 0
    if args.jobs > 1:
        jobs = min(args.jobs, os.cpu_count() or args.jobs)
        config = {
            "n": args.n,
            "k": args.k,
            "p": args.p,
            "domain": domain,
            "normal_sets": normal_sets,
            "syndrome_len": syndrome_len,
            "require_endpoints_above": args.require_endpoints_above,
            "require_joint_above": args.require_joint_above,
        }
        sparse_seeds = [args.seed * 1000003 + index for index in range(args.samples)]
        dense_seeds = [args.seed * 2000003 + index for index in range(args.samples)]
        with mp.Pool(processes=jobs, initializer=init_worker, initargs=(config,)) as pool:
            sparse_results = pool.map(worker_sparse_sample, sparse_seeds)
            dense_results = pool.map(worker_dense_sample, dense_seeds)
        sparse_samples = [sample for sample, _attempts in sparse_results]
        dense_samples = [sample for sample, _attempts in dense_results]
        sparse_attempts = sum(attempts for _sample, attempts in sparse_results)
        dense_attempts = sum(attempts for _sample, attempts in dense_results)
    else:
        while len(sparse_samples) < args.samples:
            sparse_attempts += 1
            s1, terms1 = random_sparse_syndrome(rng, args.n, args.k, args.p, domain, 3)
            s2, terms2 = random_sparse_syndrome(rng, args.n, args.k, args.p, domain, 3)
            if args.require_endpoints_above and (
                not admissible_above_j(s1, normal_sets, args.p) or not admissible_above_j(s2, normal_sets, args.p)
            ):
                continue
            if args.require_joint_above and not joint_above_delta(s1, s2, normal_sets, args.p):
                continue
            sparse_samples.append(
                {
                    "K": k_value(s1, s2, normal_sets, args.p),
                    "Sstar": "?",
                    "s1": s1,
                    "s2": s2,
                    "terms1": terms1,
                    "terms2": terms2,
                }
            )
        while len(dense_samples) < args.samples:
            dense_attempts += 1
            d1 = random_dense_syndrome(rng, syndrome_len, args.p)
            d2 = random_dense_syndrome(rng, syndrome_len, args.p)
            if args.require_endpoints_above and (
                not admissible_above_j(d1, normal_sets, args.p) or not admissible_above_j(d2, normal_sets, args.p)
            ):
                continue
            if args.require_joint_above and not joint_above_delta(d1, d2, normal_sets, args.p):
                continue
            dense_samples.append(
                {
                    "K": k_value(d1, d2, normal_sets, args.p),
                    "Sstar": "?",
                    "s1": d1,
                    "s2": d2,
                }
            )
    if args.require_endpoints_above or args.require_joint_above:
        print(
            "admissibility filter accepted "
            f"sparse={len(sparse_samples)}/{sparse_attempts}, dense={len(dense_samples)}/{dense_attempts}"
        )

    def fill_sstar(samples: list[dict[str, object]]) -> None:
        selected: set[int] = {index for index, sample in enumerate(samples) if int(sample["K"]) > threshold}
        if args.sstar_top < 0:
            selected.update(range(len(samples)))
        else:
            top_indices = sorted(range(len(samples)), key=lambda index: int(samples[index]["K"]), reverse=True)[
                : args.sstar_top
            ]
            selected.update(top_indices)
        for index in selected:
            sample = samples[index]
            sample["Sstar"] = minimal_joint_support_size(
                sample["s1"], sample["s2"], support_normals_by_size, args.p, sstar_cap
            )
        if not args.show_syndromes:
            for sample in samples:
                del sample["s1"]
                del sample["s2"]

    fill_sstar(sparse_samples)
    fill_sstar(dense_samples)

    summarize(sparse_samples, "sparse", leading_size, threshold)
    summarize(dense_samples, "dense", leading_size, threshold)


if __name__ == "__main__":
    main()
