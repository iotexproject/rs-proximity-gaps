"""Deployment-scale empirical harness for paper2 sparse-worst conjecture.

This is the issue #403 follow-up to ``g3_dense_vs_sparse_sweep.py``.  The
toy script used brute-force enumeration of all q^k RS codewords; that stops at
(16, 4).  Here we use information-set sampling for the decision

    dist(w, RS_k(L)) <= delta_n

equivalently, whether some degree-<k polynomial agrees with w on at least
``agreement_target = n - delta_n`` positions.

The sampler is one-sided:
  * FOUND means a concrete information set T interpolates a nearby codeword.
  * NOT FOUND is only high-confidence evidence, with miss probability reported.

So this script is empirical evidence, not a replacement for a GS/Wu list decoder.
It is designed to run safely at (32, 8, q >= 97) and to make the decoder
limitation explicit in the output.
"""
from __future__ import annotations

import argparse
import itertools
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mds_decoder import batched_extras, pow_mod_arr, precompute_diff_inv  # noqa: E402


def prime_factors(n: int) -> set[int]:
    factors: set[int] = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def find_omega(q: int, n: int) -> int:
    """Find a primitive n-th root in F_q."""
    if (q - 1) % n != 0:
        raise ValueError(
            f"no multiplicative subgroup of size n={n} in prime field F_{q}: "
            f"n must divide q-1={q - 1}"
        )
    exp = (q - 1) // n
    factors = prime_factors(n)
    for g in range(2, q):
        omega = pow(g, exp, q)
        if omega == 1:
            continue
        if pow(omega, n, q) != 1:
            continue
        if all(pow(omega, n // p, q) != 1 for p in factors):
            return omega
    raise RuntimeError(f"no primitive {n}-th root found in F_{q}")


def miss_probability(n: int, k: int, agreement: int, samples: int) -> float:
    """Probability that random k-subsets miss a fixed agreement set."""
    if agreement < k:
        return 1.0
    hit = math.comb(agreement, k) / math.comb(n, k)
    return math.exp(samples * math.log1p(-hit))


def clipped_union_bound(events: int, miss: float) -> float:
    """Union bound capped at one, for display-only diagnostics."""
    return min(1.0, events * miss)


@dataclass
class RSDecisionOracle:
    q: int
    n: int
    k: int
    L: list[int]
    agreement_target: int
    samples: int
    batch: int
    seed: int
    limit: int = 0

    def __post_init__(self) -> None:
        self.L_arr = np.array(self.L, dtype=np.int64) % self.q
        self.D, self.inv_D = precompute_diff_inv(self.L_arr, self.q)
        self.rng = np.random.default_rng(self.seed)
        if self.samples == 0:
            total = math.comb(self.n, self.k)
            if total > 50_000_000:
                raise ValueError(
                    f"exact mode would enumerate C({self.n},{self.k})={total}; "
                    "use --membership-samples instead"
                )

    def random_info_sets(self, count: int) -> np.ndarray:
        out = np.empty((count, self.k), dtype=np.int64)
        for b in range(count):
            out[b] = self.rng.choice(self.n, size=self.k, replace=False)
        out.sort(axis=1)
        return out

    def iter_info_set_batches(self) -> Iterable[np.ndarray]:
        emitted = 0
        if self.samples == 0:
            combo_iter = itertools.combinations(range(self.n), self.k)
            while True:
                take = self.batch
                if self.limit:
                    remaining_limit = self.limit - emitted
                    if remaining_limit <= 0:
                        break
                    take = min(take, remaining_limit)
                chunk = list(itertools.islice(combo_iter, take))
                if not chunk:
                    break
                emitted += len(chunk)
                yield np.array(chunk, dtype=np.int64)
            return

        remaining = self.samples if not self.limit else min(self.samples, self.limit)
        while remaining > 0:
            B = min(self.batch, remaining)
            remaining -= B
            yield self.random_info_sets(B)

    def is_close(self, word: Sequence[int]) -> tuple[bool, int, list[int] | None]:
        """Return (found_close_codeword, best_agreement_seen, witness_info_set)."""
        f_arr = np.array(word, dtype=np.int64) % self.q
        best_agree = 0
        best_T: list[int] | None = None

        for T_batch in self.iter_info_set_batches():
            extras = batched_extras(T_batch, f_arr, self.L_arr, self.D, self.inv_D, self.q)
            idx = int(extras.argmax())
            agree = self.k + int(extras[idx])
            if agree > best_agree:
                best_agree = agree
                best_T = T_batch[idx].tolist()
            if agree >= self.agreement_target:
                return True, best_agree, best_T
        return False, best_agree, best_T


def sparse_pencil_eval(
    positions1: Sequence[int],
    coeffs1: Sequence[int],
    positions2: Sequence[int],
    coeffs2: Sequence[int],
    L: Sequence[int],
    q: int,
) -> tuple[list[int], list[int]]:
    f1: list[int] = []
    f2: list[int] = []
    for x in L:
        v1 = sum(c * pow(x, pos, q) for pos, c in zip(positions1, coeffs1)) % q
        v2 = sum(c * pow(x, pos, q) for pos, c in zip(positions2, coeffs2)) % q
        f1.append(v1)
        f2.append(v2)
    return f1, f2


def interp_eval_from_T(
    values: Sequence[int],
    L: Sequence[int],
    T: Sequence[int],
    q: int,
) -> list[int]:
    """Evaluate the degree-<|T| interpolant through values on T at all L."""
    out: list[int] = []
    for x in L:
        acc = 0
        for j in T:
            num = 1
            den = 1
            xj = L[j]
            for s in T:
                if s == j:
                    continue
                num = (num * (x - L[s])) % q
                den = (den * (xj - L[s])) % q
            acc = (acc + values[j] * num * pow(den, q - 2, q)) % q
        out.append(acc)
    return out


def batched_interp_values(
    T_batch: np.ndarray,
    f_arr: np.ndarray,
    D: np.ndarray,
    inv_D: np.ndarray,
    q: int,
) -> np.ndarray:
    """Evaluate each T-interpolant at all domain points.

    This is the value-producing sibling of ``mds_decoder.batched_extras``.
    T positions themselves are filled by continuity with the original values,
    so callers can safely inspect the whole matrix and then mask T if needed.
    """
    B, k = T_batch.shape
    n = D.shape[0]

    DT_self = D[T_batch[:, :, None], T_batch[:, None, :]]
    DT_full = D[:, T_batch].transpose(1, 0, 2)

    diag_mask = np.eye(k, dtype=bool)
    DT_self_masked = np.where(diag_mask[None, :, :], 1, DT_self)
    W_prime = np.ones((B, k), dtype=np.int64)
    for s in range(k):
        W_prime = (W_prime * DT_self_masked[:, :, s]) % q

    W_full = np.ones((B, n), dtype=np.int64)
    for s in range(k):
        W_full = (W_full * DT_full[:, :, s]) % q

    inv_DT_full_at_i = inv_D[:, T_batch].transpose(1, 0, 2)
    inv_W_prime = pow_mod_arr(W_prime, q - 2, q)
    f_T = f_arr[T_batch]
    coeff_j = (f_T * inv_W_prime) % q
    inner_sum = np.einsum("bj,bij->bi", coeff_j, inv_DT_full_at_i) % q
    out = (W_full * inner_sum) % q

    # The barycentric formula above is only used away from T.  Patch the T
    # columns to the interpolated values so diagnostic best-agreement counts are
    # literal agreement counts across all n positions.
    np.put_along_axis(out, T_batch, f_T, axis=1)
    return out


def K_value_by_info_sets(
    f1: Sequence[int],
    f2: Sequence[int],
    q: int,
    oracle: RSDecisionOracle,
    progress_every: int = 0,
    progress_label: str = "",
) -> tuple[int, int, list[tuple[int, int]], int]:
    """Return pencil K lower bound by sampling information sets.

    For each sampled information set T, interpolate f1|T and f2|T.  The
    interpolant for f1 + alpha f2 is c1_T + alpha c2_T.  At every i outside T,
    agreement with f1 + alpha f2 is one linear equation in alpha, so one T gives
    a full set of alpha witnesses at once.
    """
    n = len(f1)
    f1_arr = np.array(f1, dtype=np.int64) % q
    f2_arr = np.array(f2, dtype=np.int64) % q
    alpha_best = [0] * q
    n_info_sets = 0

    for T_batch in oracle.iter_info_set_batches():
        c1 = batched_interp_values(T_batch, f1_arr, oracle.D, oracle.inv_D, q)
        c2 = batched_interp_values(T_batch, f2_arr, oracle.D, oracle.inv_D, q)
        B = T_batch.shape[0]
        n_info_sets += B
        T_mask = np.zeros((B, n), dtype=bool)
        np.put_along_axis(T_mask, T_batch, True, axis=1)

        lhs = (c2 - f2_arr[None, :]) % q
        rhs = (f1_arr[None, :] - c1) % q
        outside = ~T_mask

        zero_lhs = lhs == 0
        all_alpha_bonus = ((rhs == 0) & zero_lhs & outside).sum(axis=1).astype(np.int64)
        nonzero = outside & ~zero_lhs
        counts = np.zeros((B, q), dtype=np.int16)
        if np.any(nonzero):
            row_idx, _ = np.nonzero(nonzero)
            alpha_vals = (rhs[nonzero] * pow_mod_arr(lhs[nonzero], q - 2, q)) % q
            flat = row_idx.astype(np.int64) * q + alpha_vals.astype(np.int64)
            counts = np.bincount(flat, minlength=B * q).reshape(B, q).astype(np.int16)
        agree = counts.astype(np.int64) + oracle.k + all_alpha_bonus[:, None]
        alpha_best = np.maximum(alpha_best, agree.max(axis=0).astype(np.int64)).tolist()
        if progress_every and n_info_sets % progress_every < B:
            print(
                f"    info-set progress {progress_label}: "
                f"{n_info_sets} sets, current K_lb={sum(1 for x in alpha_best if x >= oracle.agreement_target)}, "
                f"best_agree={max(alpha_best) if alpha_best else 0}",
                flush=True,
            )

    hits = [(alpha, agree) for alpha, agree in enumerate(alpha_best) if agree >= oracle.agreement_target]
    return len(hits), max(alpha_best) if alpha_best else 0, hits, n_info_sets


def random_dense_pair(q: int, n: int, rng: random.Random) -> tuple[list[int], list[int]]:
    return (
        [rng.randrange(q) for _ in range(n)],
        [rng.randrange(q) for _ in range(n)],
    )


def parse_support(text: str, expected_size: int = 3) -> tuple[int, ...]:
    vals = tuple(int(x.strip()) for x in text.split(",") if x.strip())
    if len(vals) != expected_size:
        raise ValueError(
            f"expected {expected_size} comma-separated support positions, got {text!r}"
        )
    return tuple(sorted(vals))


def parse_support_list(text: str, expected_size: int = 3) -> list[tuple[int, ...]]:
    return [parse_support(part, expected_size) for part in text.split(";") if part.strip()]


def parse_coeffs(text: str, expected_size: int = 3) -> tuple[int, ...]:
    vals = tuple(int(x.strip()) for x in text.split(",") if x.strip())
    if len(vals) != expected_size:
        raise ValueError(
            f"expected {expected_size} comma-separated coefficients, got {text!r}"
        )
    return vals


def pair_passes_generator_filter(
    f1: Sequence[int],
    f2: Sequence[int],
    oracle: RSDecisionOracle,
) -> tuple[bool, int, int]:
    """Empirical above-J filter for the two pencil generators.

    The oracle is one-sided for close-codeword discovery.  If it finds a close
    codeword, the generator is definitely not above-J at the requested radius.
    If it does not, we accept it as empirical above-J evidence.
    """
    close1, agree1, _ = oracle.is_close(f1)
    close2, agree2, _ = oracle.is_close(f2)
    return (not close1 and not close2), agree1, agree2


def run_cell(args: argparse.Namespace) -> None:
    q, n, k = args.q, args.n, args.k
    delta_n = args.delta_num
    agreement_target = n - delta_n
    omega = find_omega(q, n)
    L = [pow(omega, i, q) for i in range(n)]
    rng = random.Random(args.seed)

    sample_label = "exact" if args.membership_samples == 0 else str(args.membership_samples)
    print(f"=== issue #403 sparse-worst deployment empirical ===")
    print(f"cell: q={q}, n={n}, k={k}, delta_n={delta_n}, agreement_target={agreement_target}")
    print(f"L=<omega>, omega={omega}; membership_samples={sample_label}, batch={args.batch}")
    if args.membership_samples:
        miss = miss_probability(n, k, agreement_target, args.membership_samples)
        print(
            "one-word miss probability at target agreement: "
            f"{miss:.3e}"
        )
        print(
            "one-pencil all-alpha miss union bound: "
            f"{clipped_union_bound(q, miss):.3e}"
        )
    else:
        print("membership decision: exact enumeration of all information sets")
    print()

    oracle = RSDecisionOracle(
        q=q,
        n=n,
        k=k,
        L=L,
        agreement_target=agreement_target,
        samples=args.membership_samples,
        batch=args.batch,
        seed=args.seed + 17,
        limit=args.info_set_limit,
    )

    positions = list(range(k, n))
    support_size = args.support_size
    seeded_supports = [parse_support(x, support_size) for x in args.seed_support]
    sparse_results: list[tuple[int, tuple[int, ...], tuple[int, ...], int, int, int, str]] = []
    t0 = time.time()
    print(f"--- sparse {support_size}-pos samples: target accepted {args.n_sparse} ---", flush=True)
    sparse_attempts = 0
    while len(sparse_results) < args.n_sparse and sparse_attempts < args.max_attempts:
        sparse_attempts += 1
        source = "random"
        if sparse_attempts <= len(seeded_supports):
            supp1 = seeded_supports[sparse_attempts - 1]
            supp2 = supp1 if args.same_support else tuple(sorted(rng.sample(positions, support_size)))
            source = "seed"
        else:
            supp1 = tuple(sorted(rng.sample(positions, support_size)))
            supp2 = supp1 if args.same_support else tuple(sorted(rng.sample(positions, support_size)))
        coeffs1 = tuple(rng.randrange(1, q) for _ in range(support_size))
        coeffs2 = tuple(rng.randrange(1, q) for _ in range(support_size))
        f1, f2 = sparse_pencil_eval(supp1, coeffs1, supp2, coeffs2, L, q)
        if args.filter_generators:
            accepted, agree1, agree2 = pair_passes_generator_filter(f1, f2, oracle)
            if not accepted:
                continue
        else:
            agree1 = agree2 = -1
        K, best_agree, _, n_info_sets = K_value_by_info_sets(f1, f2, q, oracle)
        sparse_results.append((K, supp1, supp2, best_agree, agree1, agree2, source))
        if args.progress and len(sparse_results) % args.progress == 0:
            print(
                f"  sparse accepted {len(sparse_results)}/{args.n_sparse} "
                f"(attempts={sparse_attempts}): current max K={max(r[0] for r in sparse_results)}",
                flush=True,
            )

    sparse_time = time.time() - t0
    sparse_Ks = [r[0] for r in sparse_results]
    K_sparse_max = max(sparse_Ks) if sparse_Ks else -1
    print(f"sparse done in {sparse_time:.1f}s; accepted={len(sparse_results)}, attempts={sparse_attempts}")
    sparse_mean = f"{sum(sparse_Ks)/len(sparse_Ks):.2f}" if sparse_Ks else "NA"
    print(f"K_sparse: min={min(sparse_Ks) if sparse_Ks else 'NA'}, max={K_sparse_max}, mean={sparse_mean}")
    for K, supp1, supp2, best_agree, agree1, agree2, source in sorted(sparse_results, reverse=True)[:5]:
        gen = "" if agree1 < 0 else f", gen_best_agree=({agree1},{agree2})"
        print(f"  sparse top: K_lb={K:3d}, best_agree_seen={best_agree:2d}{gen}, source={source}, supp1={supp1}, supp2={supp2}")

    dense_results: list[tuple[int, int]] = []
    t0 = time.time()
    print(f"\n--- dense random samples: target accepted {args.n_dense} ---", flush=True)
    dense_attempts = 0
    while len(dense_results) < args.n_dense and dense_attempts < args.max_attempts:
        dense_attempts += 1
        f1, f2 = random_dense_pair(q, n, rng)
        if args.filter_generators:
            accepted, _, _ = pair_passes_generator_filter(f1, f2, oracle)
            if not accepted:
                continue
        K, best_agree, _, n_info_sets = K_value_by_info_sets(f1, f2, q, oracle)
        dense_results.append((K, best_agree))
        if args.progress and len(dense_results) % args.progress == 0:
            print(
                f"  dense accepted {len(dense_results)}/{args.n_dense} "
                f"(attempts={dense_attempts}): current max K={max(r[0] for r in dense_results)}",
                flush=True,
            )

    dense_time = time.time() - t0
    dense_Ks = [r[0] for r in dense_results]
    K_dense_max = max(dense_Ks) if dense_Ks else -1
    print(f"dense done in {dense_time:.1f}s; accepted={len(dense_results)}, attempts={dense_attempts}")
    dense_mean = f"{sum(dense_Ks)/len(dense_Ks):.2f}" if dense_Ks else "NA"
    print(f"K_dense: min={min(dense_Ks) if dense_Ks else 'NA'}, max={K_dense_max}, mean={dense_mean}")
    for K, best_agree in sorted(dense_results, reverse=True)[:5]:
        print(f"  dense top: K_lb={K:3d}, best_agree_seen={best_agree:2d}")

    print("\n=== coverage row ===")
    print(
        "| q | n | k | delta_n | membership_samples | one-word miss | "
        "n_sparse | sparse_attempts | K_sparse_lb_max | n_dense | dense_attempts | K_dense_lb_max | runtime_s |"
    )
    miss = 0.0 if args.membership_samples == 0 else miss_probability(n, k, agreement_target, args.membership_samples)
    run_union = clipped_union_bound(q * (len(sparse_results) + len(dense_results)), miss)
    print(
        f"| {q} | {n} | {k} | {delta_n} | {sample_label} | {miss:.3e} | "
        f"{len(sparse_results)} | {sparse_attempts} | {K_sparse_max} | "
        f"{len(dense_results)} | {dense_attempts} | {K_dense_max} | "
        f"{sparse_time + dense_time:.1f} |"
    )
    if args.membership_samples:
        print(
            "sampled-run all-tested-pencils miss union bound: "
            f"{run_union:.3e}"
        )
    if sparse_Ks and dense_Ks and K_dense_max <= K_sparse_max:
        print("empirical lower-bound comparison: dense <= sparse")
    elif sparse_Ks and dense_Ks:
        print("empirical lower-bound comparison: dense > sparse; inspect, because this may be a real refutation")
    else:
        print("empirical lower-bound comparison: skipped because one side has no samples")


def run_support_search(args: argparse.Namespace) -> None:
    q, n, k = args.q, args.n, args.k
    delta_n = args.delta_num
    agreement_target = n - delta_n
    omega = find_omega(q, n)
    L = [pow(omega, i, q) for i in range(n)]
    rng = random.Random(args.seed)
    sample_label = "exact" if args.membership_samples == 0 else str(args.membership_samples)

    support_size = args.support_size
    support_pool: list[tuple[int, ...]] = []
    for text in args.support_pool:
        support_pool.extend(parse_support_list(text, support_size))
    support_pool.extend(parse_support(x, support_size) for x in args.seed_support)
    if not support_pool:
        support_pool = [tuple(sorted(x)) for x in itertools.combinations(range(k, n), support_size)]
        rng.shuffle(support_pool)
        support_pool = support_pool[: args.support_limit]

    oracle = RSDecisionOracle(
        q=q,
        n=n,
        k=k,
        L=L,
        agreement_target=agreement_target,
        samples=args.membership_samples,
        batch=args.batch,
        seed=args.seed + 17,
        limit=args.info_set_limit,
    )

    print("=== issue #403 support-focused sparse search ===")
    print(f"cell: q={q}, n={n}, k={k}, delta_n={delta_n}, agreement_target={agreement_target}")
    print(f"L=<omega>, omega={omega}; membership_samples={sample_label}, batch={args.batch}")
    if args.membership_samples:
        miss = miss_probability(n, k, agreement_target, args.membership_samples)
        print(
            "one-word miss probability at target agreement: "
            f"{miss:.3e}"
        )
        print(
            "one-pencil all-alpha miss union bound: "
            f"{clipped_union_bound(q, miss):.3e}"
        )
    else:
        print("membership decision: exact enumeration of all information sets")
    print(f"supports={len(support_pool)}, coeff_trials_per_support={args.coeff_trials}")
    print()

    positions = list(range(k, n))
    if args.generator_only:
        if len(support_pool) != 1 or not args.fixed_coeffs1 or not args.fixed_coeffs2:
            raise ValueError(
                "--generator-only requires exactly one --support-pool entry plus "
                "--fixed-coeffs1 and --fixed-coeffs2"
            )
        supp1 = support_pool[0]
        supp2 = supp1 if args.same_support else tuple(sorted(rng.sample(positions, support_size)))
        coeffs1 = parse_coeffs(args.fixed_coeffs1, support_size)
        coeffs2 = parse_coeffs(args.fixed_coeffs2, support_size)
        f1, f2 = sparse_pencil_eval(supp1, coeffs1, supp2, coeffs2, L, q)
        t0 = time.time()
        close1, agree1, witness1 = oracle.is_close(f1)
        close2, agree2, witness2 = oracle.is_close(f2)
        runtime = time.time() - t0
        print("=== generator-only row ===")
        print(
            "| q | n | k | delta_n | membership_samples | support | coeffs1 | "
            "coeffs2 | close1 | best_agree1 | close2 | best_agree2 | runtime_s |"
        )
        print(
            f"| {q} | {n} | {k} | {delta_n} | {sample_label} | {supp1} | "
            f"{coeffs1} | {coeffs2} | {close1} | {agree1} | "
            f"{close2} | {agree2} | {runtime:.1f} |"
        )
        print(f"witness_info_set1={witness1}")
        print(f"witness_info_set2={witness2}")
        if close1 or close2:
            print("generator filter: FAIL, at least one generator is within radius")
        else:
            print("generator filter: PASS, no close codeword found")
        return

    best: list[tuple[int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...], int, int]] = []
    accepted = 0
    attempts = 0
    display_coeff_trials = 1 if args.fixed_coeffs1 else args.coeff_trials
    t0 = time.time()
    for support_idx, supp1 in enumerate(support_pool, start=1):
        for _ in range(display_coeff_trials):
            attempts += 1
            supp2 = supp1 if args.same_support else tuple(sorted(rng.sample(positions, support_size)))
            coeffs1 = (
                parse_coeffs(args.fixed_coeffs1, support_size)
                if args.fixed_coeffs1
                else tuple(rng.randrange(1, q) for _ in range(support_size))
            )
            coeffs2 = (
                parse_coeffs(args.fixed_coeffs2, support_size)
                if args.fixed_coeffs2
                else tuple(rng.randrange(1, q) for _ in range(support_size))
            )
            f1, f2 = sparse_pencil_eval(supp1, coeffs1, supp2, coeffs2, L, q)
            if args.filter_generators:
                ok, agree1, agree2 = pair_passes_generator_filter(f1, f2, oracle)
                if not ok:
                    continue
            else:
                agree1 = agree2 = -1
            accepted += 1
            K, best_agree, _, _ = K_value_by_info_sets(
                f1,
                f2,
                q,
                oracle,
                progress_every=args.info_progress_every,
                progress_label=f"supp={supp1}",
            )
            best.append((K, best_agree, supp1, supp2, coeffs1, coeffs2, agree1, agree2))
            best.sort(reverse=True)
            if len(best) > args.top:
                best.pop()
        if args.progress and support_idx % args.progress == 0:
            topK = best[0][0] if best else -1
            print(
                f"  supports {support_idx}/{len(support_pool)}; "
                f"attempts={attempts}, accepted={accepted}, top_K_lb={topK}",
                flush=True,
            )

    runtime = time.time() - t0
    print(f"done in {runtime:.1f}s; attempts={attempts}, accepted={accepted}")
    print("top witnesses:")
    for K, best_agree, supp1, supp2, coeffs1, coeffs2, agree1, agree2 in best:
        gen = "" if agree1 < 0 else f", gen_best_agree=({agree1},{agree2})"
        print(
            f"  K_lb={K:3d}, best_agree_seen={best_agree:2d}{gen}, "
            f"supp1={supp1}, coeffs1={coeffs1}, supp2={supp2}, coeffs2={coeffs2}"
        )

    print("\n=== support-search row ===")
    print(
        "| q | n | k | delta_n | membership_samples | one-word miss | supports | "
        "coeff_trials | attempts | accepted | top_K_sparse_lb | runtime_s |"
    )
    miss = 0.0 if args.membership_samples == 0 else miss_probability(n, k, agreement_target, args.membership_samples)
    run_union = clipped_union_bound(q * max(accepted, 1), miss)
    print(
        f"| {q} | {n} | {k} | {delta_n} | {sample_label} | {miss:.3e} | "
        f"{len(support_pool)} | {display_coeff_trials} | {attempts} | {accepted} | "
        f"{best[0][0] if best else -1} | {runtime:.1f} |"
    )
    if args.membership_samples:
        print(
            "sampled-run all-tested-pencils miss union bound: "
            f"{run_union:.3e}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=97)
    parser.add_argument("--n", type=int, default=32)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--delta-num", type=int, default=None, help="distance radius; default Johnson+1")
    parser.add_argument("--membership-samples", type=int, default=10_000, help="0 means exact information-set enumeration")
    parser.add_argument("--batch", type=int, default=2048)
    parser.add_argument("--n-sparse", type=int, default=20)
    parser.add_argument("--n-dense", type=int, default=20)
    parser.add_argument("--max-attempts", type=int, default=10_000)
    parser.add_argument("--support-size", type=int, default=3, help="monomial support size for sparse/support-search modes")
    parser.add_argument(
        "--seed-support",
        action="append",
        default=[],
        help="support to force into sparse sweep, e.g. 15,18,19; may repeat",
    )
    parser.add_argument(
        "--same-support",
        action="store_true",
        help="use supp2=supp1 for sparse pencils; useful when testing joint support <=3",
    )
    parser.add_argument("--no-filter-generators", dest="filter_generators", action="store_false")
    parser.set_defaults(filter_generators=True)
    parser.add_argument("--seed", type=int, default=403)
    parser.add_argument("--progress", type=int, default=5)
    parser.add_argument("--support-search", action="store_true", help="run sparse coefficient search over a support pool")
    parser.add_argument(
        "--support-pool",
        action="append",
        default=[],
        help="semicolon-separated 3-support list, e.g. '15,18,19;15,21,31'; may repeat",
    )
    parser.add_argument("--support-limit", type=int, default=50, help="random supports if --support-pool is omitted")
    parser.add_argument("--coeff-trials", type=int, default=5)
    parser.add_argument("--fixed-coeffs1", default=None, help="fixed sparse coefficients for support-search, e.g. 88,11,92")
    parser.add_argument("--fixed-coeffs2", default=None, help="fixed sparse coefficients for support-search, e.g. 54,34,86")
    parser.add_argument("--generator-only", action="store_true", help="only test the two fixed sparse generators")
    parser.add_argument("--info-progress-every", type=int, default=0, help="print progress every N information sets")
    parser.add_argument("--info-set-limit", type=int, default=0, help="cap information sets consumed, for exact-throughput benchmarks")
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    try:
        if args.delta_num is None:
            args.delta_num = args.n - int(math.sqrt(args.n * args.k)) + 1
        if args.delta_num < 0 or args.delta_num > args.n:
            raise ValueError("--delta-num must be in [0, n]")
        if args.n < args.k:
            raise ValueError("need n >= k")
        if args.support_size <= 0 or args.support_size > args.n - args.k:
            raise ValueError("--support-size must be in [1, n-k]")
        if args.support_search:
            run_support_search(args)
        else:
            run_cell(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
