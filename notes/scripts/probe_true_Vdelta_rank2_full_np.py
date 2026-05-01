"""probe_true_Vdelta_rank2_full_np.py — NumPy-vectorized brute-force |V_δ|.

Same task as probe_true_Vdelta_rank2_full.py but ~30-100x faster:
  - All q^R = 9409 alpha-syndromes computed as one (q^R, m) batch.
  - For each support T ⊂ [n_R], |T| ≤ 3: precompute parity-check matrix H_T^⊥
    (kernel of H_R[:, T]^T) and check H_T^⊥ · σ ≡ 0 mod p across the entire batch.
  - σ ∈ B_w ⟺ exists T of size ≤ w with σ in colspan(H_R[:, T]) ⟺ H_T^⊥ σ = 0.

Per-f cost dominated by ~92 batched mod-p matmuls of size (m-w) × m × q^R. With
m=6, n_R=8, w=3, q=97: ~5M ops/f. NumPy float64 with mod handles this in ~50 ms.
With multiprocessing on 8+ cores: 1316 rank-2 f's in seconds.

Usage:
  python3 probe_true_Vdelta_rank2_full_np.py [n_random=2000] [n_workers=auto] [seed=2026]
"""
from __future__ import annotations
import sys, os, time, random
from itertools import product, combinations
from multiprocessing import Pool, cpu_count
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes,
)


# ---- modular linear algebra helpers (numpy, int64) ----

def kernel_mod_p(M, p):
    """Right-kernel basis of M (rows × cols) over F_p as list of column-vectors.
    Returns array of shape (cols, kernel_dim).
    """
    M = [list(r) for r in M]
    rows = len(M)
    cols = len(M[0]) if rows else 0
    pivot_col = {}
    cur = 0
    for col in range(cols):
        if cur >= rows:
            break
        pr = None
        for r in range(cur, rows):
            if M[r][col] % p != 0:
                pr = r; break
        if pr is None:
            continue
        M[cur], M[pr] = M[pr], M[cur]
        from fri_2round_attack import modinv
        inv = modinv(M[cur][col], p)
        M[cur] = [(x * inv) % p for x in M[cur]]
        for rr in range(rows):
            if rr != cur and M[rr][col] != 0:
                ff = M[rr][col]
                M[rr] = [(M[rr][c] - ff * M[cur][c]) % p for c in range(cols)]
        pivot_col[col] = cur
        cur += 1
    free_cols = [c for c in range(cols) if c not in pivot_col]
    kernel = []
    for fc in free_cols:
        v = [0] * cols
        v[fc] = 1
        for c, r in pivot_col.items():
            v[c] = (-M[r][fc]) % p
        kernel.append(v)
    if not kernel:
        return np.zeros((cols, 0), dtype=np.int64)
    return np.array(kernel, dtype=np.int64).T  # (cols, kernel_dim)


def left_kernel_mod_p(M, p):
    """Left-kernel of M (rows × cols): rows v with v M ≡ 0. Equivalent to right-kernel of M^T.
    Returns (kernel_dim, rows)."""
    MT = [list(col) for col in zip(*M)]  # cols × rows
    K = kernel_mod_p(MT, p)  # (rows, kernel_dim)
    return K.T  # (kernel_dim, rows)


def precompute_HT_perp(H_R, n_R, p, max_w):
    """For each T ⊂ [n_R] with |T| ≤ max_w, compute H_T^⊥: (m - rank, m) such that
    H_T^⊥ · σ ≡ 0 mod p iff σ ∈ colspan(H_R[:, T]).
    Returns list of (T_tuple, H_T_perp_array)."""
    m = len(H_R)
    out = []
    for w in range(1, max_w + 1):
        for T in combinations(range(n_R), w):
            H_T = [[H_R[i][j] for j in T] for i in range(m)]  # m × w
            H_T_perp = left_kernel_mod_p(H_T, p)  # (m - rank(H_T)) × m
            out.append((T, H_T_perp))
    return out


def alpha_syndromes_batch_np(f, chain, R_local, p, H_R, m, n_R, q):
    """Compute (q^R, m) array of all syndromes σ_α = H_R · fold(f, α) for α ∈ F_q^R.
    Vectorized via numpy."""
    # The 4 Q_b vectors (b ∈ {0,1}^R).
    Qs = []
    for b in product([0, 1], repeat=R_local):
        Qs.append(fold_at_alpha(f, chain, list(b), p))
    Qs = np.array(Qs, dtype=np.int64)  # (2^R, n_R)
    H_R_np = np.array(H_R, dtype=np.int64)  # (m, n_R)
    # Syndromes of Q_b: v_b = H_R Q_b, shape (2^R, m)
    v = (Qs @ H_R_np.T) % p
    # σ_α = Σ_b α^b v_b where α^b = α_0^{b_0} ... α_{R-1}^{b_{R-1}} for bit-tuple b
    # Generate all α ∈ F_q^R as (q^R, R) array, in a fixed order
    grid = np.array(list(product(range(q), repeat=R_local)), dtype=np.int64)  # (q^R, R)
    # Compute α^b for each bit b ∈ {0,1}^R: shape (q^R, 2^R)
    bit_tuples = list(product([0, 1], repeat=R_local))
    alpha_pow = np.ones((grid.shape[0], len(bit_tuples)), dtype=np.int64)
    for j, b in enumerate(bit_tuples):
        for r, br in enumerate(b):
            if br == 1:
                alpha_pow[:, j] = (alpha_pow[:, j] * grid[:, r]) % p
    # σ = alpha_pow (q^R, 2^R) · v (2^R, m) = (q^R, m)
    sigmas = (alpha_pow @ v) % p
    return sigmas  # (q^R, m)


def count_v_delta_np(sigmas, HT_perp_list, p):
    """Count |{α : σ_α ∈ B_{w_R} ∪ {0}}|. sigmas is (B, m).
    σ_α ∈ B_w ⟺ ∃ T with H_T^⊥ · σ_α ≡ 0 mod p.
    σ_α = 0 also counted (V_exact membership).
    """
    B = sigmas.shape[0]
    is_in = np.zeros(B, dtype=bool)
    # Zero syndromes are in V_exact ⊆ V_δ
    is_in |= (sigmas == 0).all(axis=1)
    for T, H_T_perp in HT_perp_list:
        if H_T_perp.shape[0] == 0:
            # H_T spans full F_q^m; every σ is in colspan trivially → all sigmas in B_w.
            is_in[:] = True
            break
        # H_T_perp: (k, m). residual = (B, k) = σ @ H_T_perp.T mod p.
        # σ ∈ colspan(H_R[:, T]) iff residual = 0.
        residual = (sigmas @ H_T_perp.T) % p  # (B, k)
        in_T = (residual == 0).all(axis=1)
        is_in |= in_T
        if is_in.all():
            break
    return int(is_in.sum())


# ---- worker ----

# Module-level globals so each worker initializes once.
_chain = None
_HT_perp_list = None
_H_R = None
_L0 = None
_k_R = None
_L_R = None
_m = None


def _init_worker():
    global _chain, _HT_perp_list, _H_R, _L0, _k_R, _L_R, _m
    _chain = setup_chain(P, N0, K0, R=R)
    _L0 = _chain[0][0]
    _L_R, _k_R, _ = _chain[R]
    _H_R = parity_check(_L_R, N_R, _k_R, P)
    _m = N_R - _k_R
    _HT_perp_list = precompute_HT_perp(_H_R, N_R, P, max_w=3)


def process_one_f(args):
    positions, coefs, seed = args
    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, _L0, P)

    above_J, _, _ = is_above_johnson_sampling(
        f, _L0, K0, P, W_J, n_samples=50000, batch=4096, seed=seed,
        return_evidence=True,
    )
    if not above_J:
        return {'positions': positions, 'status': 'BELOW_J', 'rank': None, 'v_delta': None}

    corner_syns = compute_corner_syndromes(f, _chain, R, P, _H_R)
    nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    rank = gauss_rank([list(s) for s in nz], P) if nz else 0
    if rank != 2:
        return {'positions': positions, 'status': f'ABOVE_J_RANK_{rank}', 'rank': rank, 'v_delta': None}

    sigmas = alpha_syndromes_batch_np(f, _chain, R, P, _H_R, _m, N_R, P)
    v_delta = count_v_delta_np(sigmas, _HT_perp_list, P)
    return {'positions': positions, 'coefs': coefs, 'status': 'ABOVE_J_RANK_2',
            'rank': 2, 'v_delta': v_delta}


def build_specs(n_random, seed):
    rng = random.Random(seed)
    specs = []
    for a, b in combinations(range(K0, N0), 2):
        specs.append(((a, b), (1, 1), rng.randrange(2**31)))
    triples = list(combinations(range(K0, N0), 3))
    rng.shuffle(triples)
    for t in triples[:min(len(triples), max(0, n_random // 2))]:
        specs.append((t, tuple(rng.randrange(1, P) for _ in range(3)), rng.randrange(2**31)))
    n_left = max(0, n_random - len(specs) + len(list(combinations(range(K0, N0), 2))))
    for _ in range(n_left):
        sparsity = rng.choice([2, 3, 4, 5])
        pos = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        cs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        specs.append((pos, cs, rng.randrange(2**31)))
    return specs


def main():
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    n_workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, cpu_count() - 1)
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    target_bound = R * P  # 194

    print(f"# probe_true_Vdelta_rank2_full_np — vectorized")
    print(f"# Setup: p={P}, n_0={N0}, R={R}, w_R=3, target |V_δ| ≤ {target_bound}")
    print(f"# n_workers={n_workers}, n_random={n_random}, seed={seed}")
    print()

    specs = build_specs(n_random, seed)
    print(f"# Generated {len(specs)} specs.")
    print()

    t0 = time.time()
    rank2 = []
    counts = {}
    n_done = 0
    breaches = []
    with Pool(n_workers, initializer=_init_worker) as pool:
        for r in pool.imap_unordered(process_one_f, specs, chunksize=4):
            n_done += 1
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if r['status'] == 'ABOVE_J_RANK_2':
                rank2.append(r)
                if r['v_delta'] > target_bound:
                    breaches.append(r)
                    print(f"# ★★★ EXCEEDS BOUND ★★★ positions={r['positions']}, coefs={r['coefs']}, |V_δ|={r['v_delta']}", flush=True)
            if n_done % 100 == 0:
                rate = n_done / (time.time() - t0)
                print(f"#  {n_done}/{len(specs)}  rate {rate:.1f}/sec  {dict(counts)}", flush=True)

    elapsed = time.time() - t0
    print()
    print(f"# === DONE in {elapsed:.0f}s ({len(specs)/elapsed:.1f} f/sec) ===")
    for k, v in counts.items():
        print(f"#   {k}: {v}")
    print()

    if not rank2:
        print("# No rank-2 above-J f.")
        return

    print(f"# === Rank-2 above-J: {len(rank2)} cases ===")
    vd_list = [r['v_delta'] for r in rank2]
    max_vd = max(vd_list)
    print(f"#   max |V_δ| = {max_vd}, target = {target_bound}, breaches = {len(breaches)}")
    print(f"#   |V_δ| histogram (top 20 values):")
    hist = {}
    for v in vd_list:
        hist[v] = hist.get(v, 0) + 1
    for v in sorted(hist)[-20:]:
        marker = " ← EXCEEDS" if v > target_bound else ""
        print(f"#     {v:>5d}: {hist[v]:>4d}{marker}")

    if breaches:
        print()
        print(f"# ★★★ {len(breaches)} BREACHES OF DIRECTION A BOUND ★★★")
        for r in breaches[:30]:
            print(f"#   positions={r['positions']}, coefs={r['coefs']}, |V_δ|={r['v_delta']}")
    else:
        print()
        print(f"# ✓ Direction A bound holds for all {len(rank2)} rank-2 above-J cases.")
        print(f"#   max |V_δ| = {max_vd}/{target_bound} = {max_vd/target_bound:.3f}")


if __name__ == '__main__':
    main()
