"""g3_dense_vs_sparse_sweep.py — empirical test of sparse-worst-case conjecture.

Conjecture (paper2, P3 reduction): For plain Reed-Solomon over a multiplicative
subgroup at deployment scale, the (f_1, f_2) maximizing
    K(f_1, f_2, δ) := |{α ∈ F_q : Δ(f_1 + α f_2, RS_k) ≤ δ}|
above the Johnson bound is achieved by 3-position sparse f̂_1, f̂_2.

If true → K10 unconditional (3-pos sparse, paper2 thm:universal-K10) bounds ALL
adversaries → P3 closed → general f above-J unconditional.

This sweep computes K_sparse_max (over sparse 3-pos pairs) vs K_dense_max
(over random dense pairs above-J) at small (n, k) and checks dense ≤ sparse.

Parallel: 8 workers (leave 4 cores for user). Use multiprocessing.
"""
from __future__ import annotations

import argparse
import itertools
import multiprocessing as mp
import os
import random
import time
from typing import List, Sequence, Tuple


def find_omega(q: int, n: int) -> int:
    """Find primitive n-th root of unity in F_q."""
    assert (q - 1) % n == 0, f"n={n} must divide q-1={q-1}"
    g_pow = (q - 1) // n
    for g in range(2, q):
        omega = pow(g, g_pow, q)
        if omega == 1:
            continue
        order_ok = all(pow(omega, n // p, q) != 1 for p in [2, 3, 5, 7]
                       if n % p == 0)
        if order_ok and pow(omega, n, q) == 1:
            return omega
    raise RuntimeError("no primitive n-th root found")


def evaluate_polys(coeffs_list: List[Sequence[int]], xs: Sequence[int],
                   q: int) -> List[List[int]]:
    """Evaluate polynomials at points xs. Returns list of evaluations."""
    out = []
    for coeffs in coeffs_list:
        evs = []
        for x in xs:
            val = 0
            xpow = 1
            for c in coeffs:
                val = (val + c * xpow) % q
                xpow = (xpow * x) % q
            evs.append(val)
        out.append(evs)
    return out


def all_codeword_evals(q: int, k: int, xs: Sequence[int]) -> List[List[int]]:
    """Enumerate all q^k Reed-Solomon codewords (evaluations on xs)."""
    out = []
    for coeffs in itertools.product(range(q), repeat=k):
        evs = []
        for x in xs:
            val = 0
            xpow = 1
            for c in coeffs:
                val = (val + c * xpow) % q
                xpow = (xpow * x) % q
            evs.append(val)
        out.append(evs)
    return out


def min_distance_to_RS(g: Sequence[int], rs_evals: List[List[int]]) -> int:
    """Brute force: min Hamming distance from g to any RS codeword."""
    n = len(g)
    best = n
    for c in rs_evals:
        d = sum(1 for i in range(n) if g[i] != c[i])
        if d < best:
            best = d
            if best == 0:
                return 0
    return best


def K_value(f1: Sequence[int], f2: Sequence[int], q: int,
            rs_evals: List[List[int]], delta_n: int) -> int:
    """Count α ∈ F_q with Δ(f1 + α f2, RS_k) ≤ delta_n (in absolute count)."""
    n = len(f1)
    K = 0
    for a in range(q):
        g = [(f1[i] + a * f2[i]) % q for i in range(n)]
        d = min_distance_to_RS(g, rs_evals)
        if d <= delta_n:
            K += 1
    return K


def sparse_pencil_eval(positions1: Tuple[int, ...], coeffs1: Tuple[int, ...],
                       positions2: Tuple[int, ...], coeffs2: Tuple[int, ...],
                       Lpts: Sequence[int], q: int) -> Tuple[List[int], List[int]]:
    """Build f_1, f_2 from sparse Fourier supports."""
    n = len(Lpts)
    f1 = [0] * n
    f2 = [0] * n
    for i, x in enumerate(Lpts):
        v1 = 0
        for p, c in zip(positions1, coeffs1):
            v1 = (v1 + c * pow(x, p, q)) % q
        v2 = 0
        for p, c in zip(positions2, coeffs2):
            v2 = (v2 + c * pow(x, p, q)) % q
        f1[i] = v1
        f2[i] = v2
    return f1, f2


def random_above_J_dense(q: int, n: int, k: int, Lpts: Sequence[int],
                         delta_n: int, rs_evals: List[List[int]],
                         max_tries: int = 200) -> Tuple[List[int], List[int]] | None:
    """Sample dense (f_1, f_2) with neither in close-to-RS unique decode region.

    We need (f_1, f_2) such that Δ((f_1,f_2), RS²) > δ. A sufficient cond:
    Δ(f_i, RS_k) > δ for both. Sample randomly, accept if conditions hold.
    """
    for _ in range(max_tries):
        f1 = [random.randint(0, q - 1) for _ in range(n)]
        f2 = [random.randint(0, q - 1) for _ in range(n)]
        d1 = min_distance_to_RS(f1, rs_evals)
        d2 = min_distance_to_RS(f2, rs_evals)
        if d1 > delta_n and d2 > delta_n:
            return f1, f2
    return None


def worker_sparse(args):
    """Compute K for a single sparse pencil sample."""
    (sample_idx, q, n, k, Lpts, delta_n, rs_evals,
     supp1, supp2, c1, c2) = args
    f1, f2 = sparse_pencil_eval(supp1, c1, supp2, c2, Lpts, q)
    K = K_value(f1, f2, q, rs_evals, delta_n)
    return (sample_idx, K, supp1, supp2)


def worker_dense(args):
    """Compute K for a single dense pencil sample."""
    (sample_idx, q, n, k, Lpts, delta_n, rs_evals, seed) = args
    random.seed(seed)
    sample = random_above_J_dense(q, n, k, Lpts, delta_n, rs_evals)
    if sample is None:
        return (sample_idx, -1, None)
    f1, f2 = sample
    K = K_value(f1, f2, q, rs_evals, delta_n)
    return (sample_idx, K, (f1, f2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=17)
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--delta-num", type=int, default=10,
                        help="δ * n (bad pos count threshold)")
    parser.add_argument("--n-sparse", type=int, default=2000,
                        help="# sparse pencil samples")
    parser.add_argument("--n-dense", type=int, default=2000,
                        help="# dense pencil samples")
    parser.add_argument("--workers", type=int, default=8,
                        help="parallel workers (leave cores for user)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    q, n, k = args.q, args.n, args.k
    delta_n = args.delta_num
    print(f"=== Dense-vs-Sparse Sweep (q={q}, n={n}, k={k}, δ·n={delta_n}) ===")
    print(f"Johnson radius: t* = sqrt(n*k) = {int((n * k) ** 0.5)} agreement")
    print(f"Above-J means agreement ≤ {int((n * k) ** 0.5) - 1}, "
          f"i.e. distance ≥ {n - int((n * k) ** 0.5) + 1}")
    print(f"Testing δ·n = {delta_n} (agreement = {n - delta_n})")
    print(f"Workers: {args.workers}")

    omega = find_omega(q, n)
    Lpts = [pow(omega, i, q) for i in range(n)]
    print(f"L = ⟨{omega}⟩ ⊂ F_{q}*, |L| = {n}")

    # Pre-enumerate ALL Reed-Solomon codewords (q^k)
    print(f"\nEnumerating {q**k} RS codewords...", flush=True)
    t0 = time.time()
    rs_evals = all_codeword_evals(q, k, Lpts)
    print(f"  done in {time.time() - t0:.1f}s")

    # Above-Johnson supports: positions in [k, n-1]
    above_J_positions = list(range(k, n))
    print(f"Above-Johnson position range: [{k}, {n-1}] "
          f"({len(above_J_positions)} positions)")

    random.seed(args.seed)

    # ================================================================
    # SPARSE SWEEP: 3-position sparse pencils above-J
    # ================================================================
    print(f"\n--- SPARSE: sampling {args.n_sparse} 3-pos sparse pairs ---")
    sparse_jobs = []
    for s_idx in range(args.n_sparse):
        supp1 = tuple(sorted(random.sample(above_J_positions, 3)))
        supp2 = tuple(sorted(random.sample(above_J_positions, 3)))
        c1 = tuple(random.randint(1, q - 1) for _ in range(3))
        c2 = tuple(random.randint(1, q - 1) for _ in range(3))
        sparse_jobs.append((s_idx, q, n, k, Lpts, delta_n, rs_evals,
                            supp1, supp2, c1, c2))

    t0 = time.time()
    with mp.Pool(args.workers) as pool:
        sparse_results = pool.map(worker_sparse, sparse_jobs)
    sparse_time = time.time() - t0

    sparse_Ks = [r[1] for r in sparse_results]
    K_sparse_max = max(sparse_Ks)
    print(f"  done in {sparse_time:.1f}s")
    print(f"  K distribution: min={min(sparse_Ks)}, max={K_sparse_max}, "
          f"mean={sum(sparse_Ks)/len(sparse_Ks):.2f}")
    top_sparse = sorted(sparse_results, key=lambda r: -r[1])[:5]
    print(f"  Top 5 K values:")
    for r in top_sparse:
        print(f"    K={r[1]:3d}  supp1={r[2]}  supp2={r[3]}")

    # ================================================================
    # DENSE SWEEP: random dense pencils above-J
    # ================================================================
    print(f"\n--- DENSE: sampling {args.n_dense} random pairs (above-J both f_i) ---")
    dense_jobs = [(d_idx, q, n, k, Lpts, delta_n, rs_evals,
                   args.seed + 1000 + d_idx)
                  for d_idx in range(args.n_dense)]

    t0 = time.time()
    with mp.Pool(args.workers) as pool:
        dense_results = pool.map(worker_dense, dense_jobs)
    dense_time = time.time() - t0

    dense_Ks = [r[1] for r in dense_results if r[1] >= 0]
    if not dense_Ks:
        print(f"  WARNING: all {args.n_dense} dense samples failed above-J filter!")
        K_dense_max = -1
    else:
        K_dense_max = max(dense_Ks)
        print(f"  done in {dense_time:.1f}s, "
              f"{len(dense_Ks)}/{args.n_dense} passed above-J filter")
        print(f"  K distribution: min={min(dense_Ks)}, max={K_dense_max}, "
              f"mean={sum(dense_Ks)/len(dense_Ks):.2f}")

    # ================================================================
    # CONCLUSION
    # ================================================================
    print(f"\n=== CONCLUSION ===")
    print(f"K_sparse_max = {K_sparse_max}")
    print(f"K_dense_max  = {K_dense_max}")
    if K_dense_max <= K_sparse_max:
        print(f"  ✓ Sparse-worst conjecture HOLDS empirically: dense ≤ sparse")
        print(f"  K10 unconditional sparse bound covers dense in this scale.")
    else:
        print(f"  ✗ Sparse-worst conjecture VIOLATED: dense > sparse!")
        print(f"  K10 sparse bound does NOT cover all adversaries — investigate.")

    print(f"\nTotal wall: {sparse_time + dense_time:.1f}s "
          f"({(sparse_time + dense_time) / 60:.1f} min)")


if __name__ == "__main__":
    main()
