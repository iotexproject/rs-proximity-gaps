"""Probe the ConjE N_g alignment-kernel pattern.

This is the ConjE-side analogue of reviewed branch's M_s verification, but it
is intentionally labeled as a probe: the final symbolic N_g matrix still needs
to be extracted from the observed rank dichotomy.

For a half-set S, let

    A_S = high_coeffs(interp_S(z^a)),  B_S = high_coeffs(interp_S(z^b)).

S certifies a bad nonzero ratio rho iff the rows (A_j, B_j) have the common
right-kernel vector (rho, 1), i.e. A_S*rho + B_S = 0.

For two certificates S,T and a candidate multiplier g, align T by replacing
B_T with B_T/g.  Then the stacked two-column matrix

    N_g(S,T) = rows( A_S, B_S ) union rows( A_T, B_T/g )

has a nontrivial right kernel exactly when g = rho_T/rho_S for these concrete
certificates.  ConjE predicts that true certificate multipliers are contained
in the Theorem-0187 action subgroup, except for the routed sign-paired
fourth-root obstruction.
"""

from __future__ import annotations

import argparse
import random
from collections import Counter
from itertools import combinations
from math import gcd, isqrt

from g3_arising_pair_obstruction_sweep import arising_pairs
from g3_conjE_exact_halfset import (
    high_coeff_vector,
    orbit_representative,
    rho_for_halfset,
    subgroup,
)


def inv(x: int, q: int) -> int:
    return pow(x % q, q - 2, q)


def rank_2col(rows: list[tuple[int, int]], q: int) -> int:
    nonzero = [(a % q, b % q) for a, b in rows if a % q or b % q]
    if not nonzero:
        return 0
    a0, b0 = nonzero[0]
    for a, b in nonzero[1:]:
        if (a0 * b - a * b0) % q:
            return 2
    return 1


def certificate_rows(A: list[int], B: list[int]) -> list[tuple[int, int]]:
    return list(zip(A, B))


def aligned_rank(
    cert_s: dict[str, object],
    cert_t: dict[str, object],
    g: int,
    q: int,
) -> int:
    gin = inv(g, q)
    rows = certificate_rows(cert_s["A"], cert_s["B"])
    rows += [(a, b * gin % q) for a, b in certificate_rows(cert_t["A"], cert_t["B"])]
    return rank_2col(rows, q)


def random_halfsets(n: int, t: int, count: int, seed: int) -> list[tuple[int, ...]]:
    rng = random.Random(seed)
    seen: set[tuple[int, ...]] = set()
    out = []
    while len(out) < count:
        indices = tuple(sorted(rng.sample(range(n), t)))
        if indices not in seen:
            seen.add(indices)
            out.append(indices)
    return out


def structured_halfsets(n: int, t: int) -> list[tuple[int, ...]]:
    out = []
    if n % 4 == 0 and t == n // 2:
        classes = [[i for i in range(n) if i % 4 == r] for r in range(4)]
        for r, s in combinations(range(4), 2):
            out.append(tuple(sorted(classes[r] + classes[s])))
    return out


def halfset_indices(n: int, t: int, max_sets: int | None, seed: int) -> list[tuple[int, ...]]:
    structured = structured_halfsets(n, t)
    total_small = n <= 16
    if total_small and max_sets is None:
        return list(dict.fromkeys(structured + list(combinations(range(n), t))))
    if total_small and max_sets is not None:
        return list(dict.fromkeys(structured + list(combinations(range(n), t))))[:max_sets]
    sampled = random_halfsets(n, t, max_sets or 5000, seed)
    return list(dict.fromkeys(structured + sampled))


def certificates(
    n: int,
    k: int,
    q: int,
    a: int,
    b: int,
    max_sets: int | None,
    seed: int,
) -> list[dict[str, object]]:
    t2 = k * n
    t = isqrt(t2)
    if t * t != t2:
        raise ValueError(f"sqrt(k*n) is not integral for n={n}, k={k}")

    L = subgroup(q, n)
    certs = []
    for indices in halfset_indices(n, t, max_sets, seed):
        points = [L[i] for i in indices]
        kind, rho = rho_for_halfset(points, a, b, k, q)
        if kind != "one" or rho in (None, 0):
            continue
        A = high_coeff_vector(points, a, k, t, q)
        B = high_coeff_vector(points, b, k, t, q)
        certs.append({"indices": indices, "rho": rho, "A": A, "B": B})
    return certs


def action_subgroup(n: int, q: int, a: int, b: int) -> set[int]:
    L = subgroup(q, n)
    gen = pow(L[1], (a - b) % n, q)
    out = set()
    x = 1
    while x not in out:
        out.add(x)
        x = x * gen % q
    return out


def fourth_roots(q: int) -> set[int]:
    return {x for x in range(1, q) if pow(x, 4, q) == 1}


def analyze_pair(
    n: int,
    k: int,
    q: int,
    a: int,
    b: int,
    max_sets: int | None,
    seed: int,
    max_cert_pairs: int,
) -> dict[str, object]:
    certs = certificates(n, k, q, a, b, max_sets, seed)
    action = action_subgroup(n, q, a, b)
    sign_paired = abs(a - b) == n // 2
    sign_set = fourth_roots(q) if sign_paired else set()

    L = subgroup(q, n)
    action_gen = pow(L[1], (a - b) % n, q)
    orbits = {
        orbit_representative(c["rho"], q, action_gen)
        for c in certs
    }

    stats: Counter[str] = Counter()
    bad_examples = []
    checked_pairs = 0
    for i, cert_s in enumerate(certs):
        for cert_t in certs[i + 1 :]:
            checked_pairs += 1
            if checked_pairs > max_cert_pairs:
                break
            g = cert_t["rho"] * inv(cert_s["rho"], q) % q
            rank_true = aligned_rank(cert_s, cert_t, g, q)
            rank_wrong = aligned_rank(cert_s, cert_t, (g * 2) % q or 1, q)
            allowed = g in action or g in sign_set
            stats["pairs"] += 1
            stats[f"true_rank_{rank_true}"] += 1
            stats[f"wrong_rank_{rank_wrong}"] += 1
            stats["allowed" if allowed else "forbidden"] += 1
            if (not allowed or rank_true != 1) and len(bad_examples) < 8:
                bad_examples.append(
                    {
                        "rho_s": cert_s["rho"],
                        "rho_t": cert_t["rho"],
                        "g": g,
                        "rank_true": rank_true,
                        "rank_wrong_x2": rank_wrong,
                        "S": cert_s["indices"],
                        "T": cert_t["indices"],
                    }
                )
        if checked_pairs > max_cert_pairs:
            break

    return {
        "n": n,
        "k": k,
        "q": q,
        "a": a,
        "b": b,
        "cert_count": len(certs),
        "ratio_count": len({c["rho"] for c in certs}),
        "orbit_count": len(orbits),
        "orbit_size": n // gcd(abs(a - b), n),
        "sign_paired": sign_paired,
        "stats": stats,
        "bad_examples": bad_examples,
    }


def candidate_pairs(n0: int, k0: int, max_pairs: int | None) -> list[tuple[int, int]]:
    pairs = sorted(arising_pairs(n0, k0))
    n2 = n0 // 4
    k2 = k0 // 4
    above = [(a, b) for a, b in pairs if a >= k2 and b >= k2 and a != b]
    return above[:max_pairs] if max_pairs is not None else above


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n0", type=int, default=32)
    parser.add_argument("--k0", type=int, default=None)
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--a", type=int, default=None)
    parser.add_argument("--b", type=int, default=None)
    parser.add_argument("--max-pairs", type=int, default=12)
    parser.add_argument("--max-sets", type=int, default=None)
    parser.add_argument("--max-cert-pairs", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260428)
    args = parser.parse_args()

    k0 = args.k0 if args.k0 is not None else args.n0 // 4
    n = args.n0 // 4
    k = k0 // 4
    pairs = [(args.a, args.b)] if args.a is not None else candidate_pairs(args.n0, k0, args.max_pairs)

    print(f"N_g probe n0={args.n0} k0={k0} n={n} k={k} q={args.q}")
    print(f"pairs={pairs}")
    for a, b in pairs:
        row = analyze_pair(n, k, args.q, a, b, args.max_sets, args.seed, args.max_cert_pairs)
        stats = row["stats"]
        print(
            f"(a,b)=({a},{b}) certs={row['cert_count']} ratios={row['ratio_count']} "
            f"orbits={row['orbit_count']} orbit_size={row['orbit_size']} "
            f"sign_paired={row['sign_paired']}"
        )
        print(
            f"  cert_pairs={stats['pairs']} allowed={stats['allowed']} forbidden={stats['forbidden']} "
            f"true_rank1={stats['true_rank_1']} true_rank2={stats['true_rank_2']} "
            f"wrong_rank1={stats['wrong_rank_1']} wrong_rank2={stats['wrong_rank_2']}"
        )
        for ex in row["bad_examples"]:
            print(
                f"  bad g={ex['g']} rho=({ex['rho_s']},{ex['rho_t']}) "
                f"rank_true={ex['rank_true']} rank_wrong_x2={ex['rank_wrong_x2']} "
                f"S={list(ex['S'])} T={list(ex['T'])}"
            )


if __name__ == "__main__":
    main()
