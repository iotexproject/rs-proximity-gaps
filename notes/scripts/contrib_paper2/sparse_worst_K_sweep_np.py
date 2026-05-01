"""NumPy-optimized K(f_1, f_2) sweep for sparse-worst empirical.

Vectorized Hamming-K computation. Suitable for (16, 4) intermediate testing.

K(f_1, f_2; δ) := #{ α ∈ F_q^* : ∃ codeword c ∈ RS(n, k) with d_H(f_1 + α·f_2, c) ≤ δ }
"""
from __future__ import annotations

import itertools
import random
import sys
import time

import numpy as np


def primitive_root_of_unity(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        if pow(g, n, p) == 1:
            ok = True
            for q in range(2, n + 1):
                if n % q == 0 and pow(g, n // q, p) == 1:
                    ok = False
                    break
            if ok:
                return g
    return None


def build_codeword_set(p, n, k):
    """Build all q^k codewords as np.array of shape (q^k, n)."""
    omega = primitive_root_of_unity(p, n)
    L = np.array([pow(omega, j, p) for j in range(n)], dtype=np.int64)
    # message [m_0, ..., m_{k-1}], codeword[j] = sum_i m_i * L[j]^i mod p
    powers = np.zeros((n, k), dtype=np.int64)
    for j in range(n):
        x = 1
        for i in range(k):
            powers[j, i] = x
            x = (x * int(L[j])) % p
    # iterate messages
    cws = np.zeros((p ** k, n), dtype=np.int64)
    for idx, msg in enumerate(itertools.product(range(p), repeat=k)):
        m = np.array(msg, dtype=np.int64)
        cw = (powers @ m) % p
        cws[idx] = cw
    return cws, L, omega


def make_sparse_pencil(p, n, k, omega, supp1, supp2, c1, c2):
    """f_i[j] = sum_{a ∈ supp_i} c_a · ω^(a*j) mod p."""
    f1 = np.zeros(n, dtype=np.int64)
    f2 = np.zeros(n, dtype=np.int64)
    for j in range(n):
        for a, c in zip(supp1, c1):
            f1[j] = (f1[j] + c * pow(omega, a * j, p)) % p
        for a, c in zip(supp2, c2):
            f2[j] = (f2[j] + c * pow(omega, a * j, p)) % p
    return f1, f2


def K_vectorized(p, codewords, f1, f2, delta):
    """Vectorized Hamming-K over all α ∈ F_q^*."""
    n = codewords.shape[1]
    count = 0
    for alpha in range(1, p):
        h = (f1 + alpha * f2) % p
        # Hamming distances to all codewords: sum (cws != h)
        dists = (codewords != h).sum(axis=1)
        if (dists <= delta).any():
            count += 1
    return count


def focused_sweep(p, n, k, delta_J, n_random_per_s, seed=42):
    rng = random.Random(seed)
    print(f"\n=== Focused sweep at p={p}, ({n}, {k}), δ ≤ {delta_J} ===")
    t0 = time.time()
    cws, L, omega = build_codeword_set(p, n, k)
    print(f"  built {cws.shape[0]} codewords in {time.time()-t0:.1f}s")

    above_J = list(range(k, n))
    print(f"  above-J pool: {above_J} (size {len(above_J)})")

    rows = []
    for s in range(2, len(above_J) + 1):
        if s > len(above_J):
            break
        max_K = 0
        best = None
        t1 = time.time()
        for trial in range(n_random_per_s):
            supp1 = sorted(rng.sample(above_J, s))
            supp2 = sorted(rng.sample(above_J, s))
            cs1 = [rng.randint(1, p - 1) for _ in supp1]
            cs2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(p, n, k, omega, supp1, supp2, cs1, cs2)
            K = K_vectorized(p, cws, f1, f2, delta_J)
            if K > max_K:
                max_K = K
                best = (supp1, supp2, cs1, cs2)
        joint = len(set(best[0]) | set(best[1])) if best else None
        rows.append((s, max_K, joint))
        print(f"  s={s}: max K = {max_K} (|S*|={joint}) [{time.time()-t1:.1f}s, {n_random_per_s} trials]")

    # Dense
    max_K_dense = 0
    t1 = time.time()
    for trial in range(n_random_per_s):
        f1 = np.array([rng.randint(0, p - 1) for _ in range(n)], dtype=np.int64)
        f2 = np.array([rng.randint(0, p - 1) for _ in range(n)], dtype=np.int64)
        K = K_vectorized(p, cws, f1, f2, delta_J)
        if K > max_K_dense:
            max_K_dense = K
    print(f"  dense: max K = {max_K_dense} [{time.time()-t1:.1f}s, {n_random_per_s} trials]")

    return rows, max_K_dense


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'big':
        # (16, 4) at p=17, more trials. δ ∈ {8, 9, 10}: at-Johnson, just-above-J,
        # 1-above-J. Conj:sparse-worst is for δ above Johnson; δ=9, 10.
        for delta in [8, 9, 10]:
            label = {8: 'at Johnson', 9: 'above-J', 10: '+1 above-J'}[delta]
            print(f"\n--- (16, 4) at p=17, δ={delta} ({label}) ---")
            focused_sweep(p=17, n=16, k=4, delta_J=delta, n_random_per_s=80)
    elif len(sys.argv) > 1 and sys.argv[1] == 'p97':
        # (16, 4) at p=97, q^k=88M codewords. Heavy memory. Reduce trials.
        print("--- (16, 4) at p=97, δ=8 (Johnson) ---")
        focused_sweep(p=97, n=16, k=4, delta_J=8, n_random_per_s=10)
    else:
        # (8, 2) sanity check
        print("--- (8, 2) at p=17, δ=4 (Johnson) — sanity ---")
        focused_sweep(p=17, n=8, k=2, delta_J=4, n_random_per_s=30)


if __name__ == '__main__':
    main()
