"""exact_above_J.py — exact dist(f, RS_k(L)) via full info-set enumeration.

For n=32, k=8: C(32, 8) = 10,518,300 info sets. ~22s/candidate via batched_extras.

is_above_J_exact(f, L, k, w_J, p) returns (above_J: bool, exact_dist: int).

Use as oracle for above-J detection (vs the heuristic is_above_johnson_sampling).

Usage as module: from exact_above_J import is_above_J_exact, exact_distance.
"""
from __future__ import annotations
import sys, os
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mds_decoder import precompute_diff_inv, batched_extras


def exact_distance(f, L, k, p, batch_size=20000):
    """Exact dist(f, RS_k(L)) via full info-set enumeration.

    Returns int distance. Time ~ C(n, k) / 1e6 seconds at our scale.
    """
    n = len(L)
    L_arr = np.array(L, dtype=np.int64)
    f_arr = np.array(f, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, p)
    max_extras = -1
    info_set_iter = combinations(range(n), k)
    while True:
        batch = []
        try:
            for _ in range(batch_size):
                batch.append(next(info_set_iter))
        except StopIteration:
            pass
        if not batch:
            break
        T_batch = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_batch, f_arr, L_arr, D, inv_D, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
    return n - k - max_extras


def is_above_J_exact(f, L, k, w_J, p, batch_size=20000):
    """Returns (is_above_J: bool, exact_dist: int)."""
    d = exact_distance(f, L, k, p, batch_size=batch_size)
    return d > w_J, d


def is_above_J_early_exit(f, L, k, w_J, p, batch_size=20000):
    """Early-exit version: stops as soon as a witness for below-J is found.

    Returns (is_above_J: bool, dist_or_witness_extras: int).

    For BELOW-J f's this is much faster (often <1s instead of 22s).
    For above-J f's it still does full enumeration to certify.
    """
    n = len(L)
    threshold = n - k - w_J  # extras < threshold ⟺ above-J
    L_arr = np.array(L, dtype=np.int64)
    f_arr = np.array(f, dtype=np.int64)
    D, inv_D = precompute_diff_inv(L_arr, p)
    max_extras = -1
    info_set_iter = combinations(range(n), k)
    while True:
        batch = []
        try:
            for _ in range(batch_size):
                batch.append(next(info_set_iter))
        except StopIteration:
            pass
        if not batch:
            break
        T_batch = np.array(batch, dtype=np.int64)
        extras = batched_extras(T_batch, f_arr, L_arr, D, inv_D, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        if max_extras >= threshold:
            return False, n - k - max_extras  # certified below-J or at-J
    return True, n - k - max_extras


if __name__ == '__main__':
    import time
    sys.path.insert(0, '<repo>/notes/scripts')
    from probe_step5_n32_studio import P, N0, K0, W_J, evaluate_dft
    from fri_2round_attack import setup_chain
    chain = setup_chain(P, N0, K0, R=2)
    L0 = chain[0][0]

    cases = [
        ((15, 23), (10, 17), "K=1 leader (above-J)"),
        ((14, 22), (72, 45), "even-even outlier (at-J)"),
        ((16, 24), (15, 73), "even-even outlier (at-J)"),
    ]
    for pos, coefs, label in cases:
        fhat = [0] * N0
        for x, c in zip(pos, coefs):
            fhat[x] = c
        f = evaluate_dft(fhat, L0, P)
        t0 = time.time()
        above_J, d = is_above_J_exact(f, L0, K0, W_J, P)
        t_full = time.time() - t0
        t0 = time.time()
        above_J_e, d_e = is_above_J_early_exit(f, L0, K0, W_J, P)
        t_early = time.time() - t0
        assert above_J == above_J_e
        print(f"  {label}: pos={pos} coefs={coefs}")
        print(f"    full enum: above_J={above_J} dist={d}    ({t_full:.1f}s)")
        print(f"    early-exit: above_J={above_J_e} (>=)dist={d_e}  ({t_early:.1f}s)")
