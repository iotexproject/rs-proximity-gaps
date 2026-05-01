"""probe_step5_n32_studio.py — Direction C empirical probe at p=97, n_0=32, k_0=8, R=2.

CRITICAL QUESTION (per note 0105): does w' = 5 < m = 6 ever occur for rank-1 above-J f's?

At p=97, n_0=32, k_0=8, R=2: n_R=8, k_R=2, m=6, w_J=16, ⌈w_J/2^R⌉+1 = 5.
Loose bound forces w' ∈ {5, 6}. If w' = 5 ever occurs → 16/16 "w' = m" finding at
n_0=16 was a parameter coincidence (note 0105 reading). If always w' = 6 → hint of
deeper algebraic structure forcing v_0 ∉ B_5, which would re-open Path γ above Johnson.

Implementation:
  1. Generate many sparse f's. 2-3 nonzero coefs in syndrome window [k_0, n_0).
  2. Filter above-J via mds_decoder.is_above_johnson_sampling (50K random T's per f, FPR ≈ 0).
  3. For each above-J f: compute image at α ∈ {0,1}^R only (image is multilinear in α,
     so 2^R = 4 corner folds suffice). Image rank = rank of the 2^R syndrome vectors.
  4. For rank-1: extract μ_b via Möbius inversion, compute w' via MDS-on-H_R.
  5. Tabulate (positions, dist_lower_bound, w', |S|, v_0_minwt).

Parallelized via multiprocessing.Pool over f's.

Usage:
  python3 probe_step5_n32_studio.py [n_random=2000] [n_workers=auto] [seed=2026]

Output: notes/scripts/probe_step5_n32_p97.output.txt
"""
from __future__ import annotations
import sys, os, time, random, math
from itertools import product, combinations
from multiprocessing import Pool, cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, gauss_rank, modinv
)
from mds_decoder import is_above_johnson_sampling


# Pin parameters for this probe.
P = 97
N0 = 32
K0 = 8
R = 2
N_R = N0 // (2**R)            # 8
W_J = int((1 - math.sqrt(K0/N0)) * N0)  # 16


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def fold_at_alpha(f, chain, alphas, p):
    """Apply R fold rounds with α-values."""
    R_local = len(alphas)
    L_chain = [chain[i][0] for i in range(R_local + 1)]
    fold = list(f)
    for r in range(R_local):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def compute_corner_syndromes(f, chain, R_local, p, H_R):
    """Compute H_R · fold(f, α) for α ∈ {0, 1}^R. Returns dict b_tuple -> syn (list).

    Image (over all α ∈ F_p^R) is the F_p-span of the multilinear function
    ψ(α) v_0 where ψ has 2^R coefficients μ_b. The image is determined by these
    2^R corner samples (Möbius inversion).
    """
    out = {}
    for b in product([0, 1], repeat=R_local):
        Q_b = fold_at_alpha(f, chain, list(b), p)
        syn = matvec(H_R, Q_b, p)
        out[b] = syn
    return out


def image_rank_and_mu(corner_syns, R_local, p, m):
    """Returns (rank, mu_dict_or_None, v0_normalized_or_None, S_size_or_None)."""
    nonzero_syns = [s for s in corner_syns.values() if any(x != 0 for x in s)]
    if not nonzero_syns:
        return 0, None, None, None
    rank = gauss_rank([list(s) for s in nonzero_syns], p)
    if rank != 1:
        return rank, None, None, None
    # rank=1: identify v_0 line
    v0 = next(s for s in corner_syns.values() if any(x != 0 for x in s))
    c_idx = next(i for i, x in enumerate(v0) if x != 0)
    inv_v0c = modinv(v0[c_idx], p)
    v0_n = [(y * inv_v0c) % p for y in v0]  # normalized so v0_n[c_idx] = 1
    # ψ(α) for α at corner b: extract from syn[c_idx]
    psi_at_corner = {}
    for b, syn in corner_syns.items():
        psi_at_corner[b] = (syn[c_idx] * inv_v0c) % p
    # Möbius inversion to recover μ_b, b ∈ {0,1}^R:
    #   ψ(α) = Σ_b α^b μ_b  (multilinear in α_0, ..., α_{R-1})
    #   ⟹ μ_b = Σ_{a ≤ b} (-1)^{|b|-|a|} ψ(a)
    mu = {}
    for b in product([0, 1], repeat=R_local):
        s = 0
        for a in product([0, 1], repeat=R_local):
            if all(a[r] <= b[r] for r in range(R_local)):
                sign = (-1) ** (sum(b) - sum(a))
                s = (s + sign * psi_at_corner[a]) % p
        mu[b] = s % p
    S_size = sum(1 for v in mu.values() if v != 0)
    return rank, mu, v0_n, S_size


def min_wt_via_MDS(target, H, n_R_local, p, max_w):
    """Find min-wt e with H · e = target. Returns (w, T_or_None, e_or_None)."""
    if all(x == 0 for x in target):
        return 0, [], [0] * n_R_local
    H_cols = list(zip(*H))
    syn_dim = len(target)
    for w in range(1, max_w + 1):
        for T in combinations(range(n_R_local), w):
            A = [[H_cols[j][i] for j in T] for i in range(syn_dim)]
            aug = [list(A[i]) + [target[i]] for i in range(syn_dim)]
            ncols = w + 1
            pivot_col = {}
            rank = 0
            col = 0
            while rank < syn_dim and col < w:
                pr = None
                for r in range(rank, syn_dim):
                    if aug[r][col] % p != 0:
                        pr = r; break
                if pr is None:
                    col += 1; continue
                aug[rank], aug[pr] = aug[pr], aug[rank]
                inv = modinv(aug[rank][col], p)
                aug[rank] = [(x * inv) % p for x in aug[rank]]
                for rr in range(syn_dim):
                    if rr != rank and aug[rr][col] != 0:
                        ff = aug[rr][col]
                        aug[rr] = [(aug[rr][c] - ff * aug[rank][c]) % p for c in range(ncols)]
                pivot_col[col] = rank
                rank += 1
                col += 1
            consistent = True
            for r in range(rank, syn_dim):
                if aug[r][w] % p != 0:
                    consistent = False; break
            if not consistent:
                continue
            x = [0] * w
            for c, r in pivot_col.items():
                x[c] = aug[r][w] % p
            if all(xi != 0 for xi in x):
                e = [0] * n_R_local
                for idx, j in enumerate(T):
                    e[j] = x[idx]
                return w, list(T), e
    return None, None, None


# Worker takes a single f-spec and returns the full analysis result.
def process_one_f(args):
    """Worker. Returns dict with keys: positions, status, plus details for above-J/rank-1."""
    positions, coefs, seed = args
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    m = N_R - k_R  # 6

    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, P)

    # Filter above-J
    above_J, max_extras, _cert = is_above_johnson_sampling(
        f, L0, K0, P, W_J, n_samples=50000, batch=4096, seed=seed,
        return_evidence=True,
    )
    sampled_dist_lb = (N0 - K0) - max_extras  # lower bound on dist
    if not above_J:
        return {
            'positions': positions, 'coefs': coefs, 'status': 'BELOW_J',
            'dist_lb': sampled_dist_lb, 'rank': None, 'w_prime': None, 'S_size': None,
            'v0_n': None,
        }

    # Image analysis
    corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
    rank, mu, v0_n, S_size = image_rank_and_mu(corner_syns, R, P, m)
    if rank == 0:
        return {
            'positions': positions, 'coefs': coefs, 'status': 'ABOVE_J_RANK_0',
            'dist_lb': sampled_dist_lb, 'rank': 0, 'w_prime': None, 'S_size': None,
            'v0_n': None,
        }
    if rank != 1:
        return {
            'positions': positions, 'coefs': coefs, 'status': f'ABOVE_J_RANK_{rank}',
            'dist_lb': sampled_dist_lb, 'rank': rank, 'w_prime': None, 'S_size': None,
            'v0_n': None,
        }

    # Rank-1: compute w' = min wt of e with H_R e = v_0
    w_prime, T_min, e_min = min_wt_via_MDS(v0_n, H_R, N_R, P, max_w=m)
    return {
        'positions': positions, 'coefs': coefs, 'status': 'ABOVE_J_RANK_1',
        'dist_lb': sampled_dist_lb, 'rank': 1, 'w_prime': w_prime, 'S_size': S_size,
        'v0_n': tuple(v0_n), 'T_min': T_min, 'mu': mu,
    }


def build_candidate_specs(n_random, seed):
    """Generate (positions, coefs, seed) triples for sparse f-candidates."""
    rng = random.Random(seed)
    specs = []
    # All pairs in syndrome window — total C(24, 2) = 276
    for a, b in combinations(range(K0, N0), 2):
        specs.append(((a, b), (1, 1), rng.randrange(2**31)))
    # All triples — total C(24, 3) = 2024 (probably too many; sample)
    triples = list(combinations(range(K0, N0), 3))
    rng.shuffle(triples)
    for t in triples[:min(len(triples), max(0, n_random // 2))]:
        specs.append((t, tuple(rng.randrange(1, P) for _ in range(3)), rng.randrange(2**31)))
    # Random sparse with 2-5 positions and random coefs
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

    print(f"# probe_step5_n32_studio.py — Direction C")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}")
    print(f"# n_R={N_R}, m={N_R - 2}, w_J={W_J}")
    print(f"# Loose bound: w' >= ceil({W_J}/{2**R}) + 1 = {math.ceil(W_J/(2**R)) + 1}")
    print(f"# max possible w' = m = {N_R - 2}")
    print(f"# CRITICAL QUESTION: does w' = 5 ever occur for rank-1 above-J f's?")
    print(f"#")
    print(f"# n_workers = {n_workers}, n_random = {n_random}")
    print()

    specs = build_candidate_specs(n_random, seed)
    print(f"# Generated {len(specs)} candidate f-specs. Dispatching to {n_workers} workers...")
    print()

    t0 = time.time()
    results = []
    counts = {'BELOW_J': 0, 'ABOVE_J_RANK_0': 0, 'ABOVE_J_RANK_1': 0,
              'ABOVE_J_RANK_2': 0, 'ABOVE_J_RANK_3': 0, 'ABOVE_J_RANK_4': 0}
    n_done = 0
    rank1_results = []
    with Pool(n_workers) as pool:
        for r in pool.imap_unordered(process_one_f, specs, chunksize=4):
            n_done += 1
            results.append(r)
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if r['status'] == 'ABOVE_J_RANK_1':
                rank1_results.append(r)
            if n_done % 50 == 0:
                rate = n_done / (time.time() - t0)
                print(f"#  {n_done}/{len(specs)}  rate {rate:.1f}/sec   "
                      f"counts: {dict(counts)}", flush=True)
    elapsed = time.time() - t0

    print()
    print(f"# === DONE in {elapsed:.0f}s ({len(specs)/elapsed:.1f} f/sec) ===")
    print(f"# Total f's: {len(specs)}")
    for k, v in counts.items():
        print(f"#   {k}: {v}")
    print()

    if not rank1_results:
        print("# ★ NO rank-1 above-J f's found. Try more samples or different f-distribution. ★")
        return

    # Tabulate w' distribution for rank-1
    print(f"# === Rank-1 above-J cases: {len(rank1_results)} ===")
    print(f"# Distribution of w':")
    wp_dist = {}
    for r in rank1_results:
        wp = r['w_prime']
        wp_dist[wp] = wp_dist.get(wp, 0) + 1
    for wp in sorted(wp_dist):
        marker = " ← FALSIFIES 'w' = m'" if wp is not None and wp < N_R - 2 else ""
        print(f"#   w' = {wp}: {wp_dist[wp]}{marker}")

    print()
    print(f"# === First 30 rank-1 cases in detail: ===")
    print(f"# {'positions':<30s} {'dist_lb':>7s} {'w*':>3s} {'|S|':>4s}  v_0_normalized")
    print("-" * 90)
    for r in rank1_results[:30]:
        pos_str = str(r['positions'])
        v0_str = str(r['v0_n'])
        wp_str = f"{r['w_prime']}" if r['w_prime'] is not None else ">m"
        print(f"  {pos_str:<30s} {r['dist_lb']:>7d} {wp_str:>3s} {r['S_size']:>4d}  {v0_str}")

    # If w' = 5 occurs: print all such cases
    falsifiers = [r for r in rank1_results if r['w_prime'] is not None and r['w_prime'] < N_R - 2]
    if falsifiers:
        print()
        print(f"# ★★★ {len(falsifiers)} FALSIFIERS of 'w' = m' found ★★★")
        print(f"# These confirm note 0105's parameter-coincidence reading.")
        for r in falsifiers[:20]:
            print(f"#   positions={r['positions']}, w'={r['w_prime']}, |S|={r['S_size']}, v_0={r['v0_n']}")
    else:
        print()
        print(f"# ★ NO falsifiers of 'w' = m'. All {len(rank1_results)} rank-1 above-J have w' = m = {N_R-2}. ★")
        print(f"# Hints at deeper algebraic structure forcing v_0 ∉ B_5.")
        print(f"# This would reopen Path γ above Johnson — investigate further!")


if __name__ == '__main__':
    main()
