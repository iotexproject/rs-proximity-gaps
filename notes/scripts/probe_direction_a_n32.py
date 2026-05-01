"""probe_direction_a_n32.py — empirical test of note 0107's per-line bound.

Setup: p=97, n_0=32, k_0=8, R=2 → n_R=8, k_R=2, m=6, w_R = ⌊δ·n_R⌋ = 3 at δ=0.45.

For each above-J rank-r f (r ≥ 2):
  1. Compute corner syndromes {H_R · g(b) : b ∈ {0,1}^R} (4 vectors in F_q^m).
  2. Compute U := span(corner syndromes) ⊆ F_q^m, dim r.
  3. Enumerate all (q^r - 1)/(q - 1) projective lines through 0 in U.
     For each line: pick representative v, check syndrome-weight sw(v) via min_wt_via_MDS.
  4. # bad lines = # of lines with sw(v) ≤ w_R.
  5. |U ∩ B_w| = 1 + (# bad lines) · (q - 1).

Direction A subclaim (note 0107): # bad lines ≤ R = 2 for rank-2 above-J f.
Equivalently: |U ∩ B_w| ≤ 2q - 1 (or 2q in some bookkeeping).

This probe re-runs the full above-J + rank-r filtering from probe_step5_n32_studio.py
to identify the rank-r f's, then for each performs the line enumeration.

Usage:
  python3 probe_direction_a_n32.py [n_random=2000] [n_workers=auto] [seed=2026]
                                   [max_rank=2]

Output: probe_direction_a_n32_p97.output.txt
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
from probe_step5_n32_studio import (
    evaluate_dft, fold_at_alpha, compute_corner_syndromes, min_wt_via_MDS,
)

P = 97
N0 = 32
K0 = 8
R = 2
N_R = N0 // (2**R)             # 8
W_J = int((1 - math.sqrt(K0/N0)) * N0)  # 16
DELTA = 0.45
W_R = int(DELTA * N_R)         # 3


def gauss_basis_rref(vectors, p):
    """Reduce a list of row-vectors (mod p) and return non-zero rows as a basis (RREF)."""
    if not vectors:
        return []
    n = len(vectors[0])
    rows = [list(v) for v in vectors]
    pivot_row = 0
    for col in range(n):
        pr = None
        for r in range(pivot_row, len(rows)):
            if rows[r][col] % p != 0:
                pr = r; break
        if pr is None:
            continue
        rows[pivot_row], rows[pr] = rows[pr], rows[pivot_row]
        inv = modinv(rows[pivot_row][col] % p, p)
        rows[pivot_row] = [(x * inv) % p for x in rows[pivot_row]]
        for r in range(len(rows)):
            if r != pivot_row and rows[r][col] % p != 0:
                ff = rows[r][col]
                rows[r] = [(rows[r][c] - ff * rows[pivot_row][c]) % p for c in range(n)]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    basis = [r for r in rows[:pivot_row] if any(x % p != 0 for x in r)]
    return basis


def enumerate_projective_lines(basis, p):
    """Enumerate (q^r - 1)/(q-1) projective representatives of lines through origin
    in span(basis). Returns a list of representatives (one per line).

    Convention: each rep is the unique vector in its line whose first nonzero
    coord (in the order e_1, e_2, ..., e_r as in basis) is 1.
    """
    r = len(basis)
    if r == 0:
        return []
    if r == 1:
        return [list(basis[0])]
    n = len(basis[0])
    reps = []
    # rep = sum_i a_i * e_i with leading coord a_{i*} = 1, all earlier a_i = 0.
    # i.e., for each i* in 0..r-1: enumerate (a_0=0, ..., a_{i*-1}=0, a_{i*}=1, free).
    for i_star in range(r):
        # free coords: i_star+1 .. r-1, each in {0, ..., p-1}. Total p^(r-1-i_star).
        n_free = r - 1 - i_star
        for free_vals in product(range(p), repeat=n_free):
            coeffs = [0] * r
            coeffs[i_star] = 1
            for j, v in enumerate(free_vals):
                coeffs[i_star + 1 + j] = v
            rep = [0] * n
            for i in range(r):
                if coeffs[i] == 0:
                    continue
                for c in range(n):
                    rep[c] = (rep[c] + coeffs[i] * basis[i][c]) % p
            reps.append(rep)
    return reps


def process_one_f(args):
    """Worker. For each f: above-J check, rank, # bad lines if rank ≥ 1.

    Returns dict with status + (bad_count, n_lines, |U∩B_w|, dist_lb, rank).
    """
    positions, coefs, seed, max_rank = args
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    m = N_R - k_R  # 6

    fhat = [0] * N0
    for pos, c in zip(positions, coefs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, P)

    above_J, max_extras, _ = is_above_johnson_sampling(
        f, L0, K0, P, W_J, n_samples=50000, batch=4096, seed=seed,
        return_evidence=True,
    )
    sampled_dist_lb = (N0 - K0) - max_extras
    if not above_J:
        return {'positions': positions, 'status': 'BELOW_J', 'rank': None,
                'bad_count': None, 'n_lines': None, 'intersect_size': None,
                'dist_lb': sampled_dist_lb}

    corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
    syns = [list(s) for s in corner_syns.values()]
    nonzero = [s for s in syns if any(x != 0 for x in s)]
    if not nonzero:
        rank = 0
    else:
        rank = gauss_rank(nonzero, P)

    if rank == 0:
        return {'positions': positions, 'status': 'ABOVE_J_RANK_0', 'rank': 0,
                'bad_count': 0, 'n_lines': 0, 'intersect_size': 1,
                'dist_lb': sampled_dist_lb}

    # Skip ranks above max_rank to keep runtime tractable.
    if rank > max_rank:
        return {'positions': positions, 'status': f'ABOVE_J_RANK_{rank}', 'rank': rank,
                'bad_count': None, 'n_lines': None, 'intersect_size': None,
                'dist_lb': sampled_dist_lb, 'skipped': True}

    basis = gauss_basis_rref(nonzero, P)
    assert len(basis) == rank, f"basis size {len(basis)} != rank {rank}"

    reps = enumerate_projective_lines(basis, P)
    n_lines = len(reps)

    bad_count = 0
    bad_reps = []
    for rep in reps:
        w, T, _e = min_wt_via_MDS(rep, H_R, N_R, P, max_w=W_R)
        if w is not None:
            bad_count += 1
            bad_reps.append((tuple(rep), w, tuple(T) if T else ()))

    intersect_size = 1 + bad_count * (P - 1)

    return {'positions': positions, 'status': f'ABOVE_J_RANK_{rank}', 'rank': rank,
            'bad_count': bad_count, 'n_lines': n_lines,
            'intersect_size': intersect_size,
            'bad_reps': bad_reps[:5],  # first few for inspection
            'dist_lb': sampled_dist_lb}


def build_candidate_specs(n_random, seed, max_rank):
    rng = random.Random(seed)
    specs = []
    for a, b in combinations(range(K0, N0), 2):
        specs.append(((a, b), (1, 1), rng.randrange(2**31), max_rank))
    triples = list(combinations(range(K0, N0), 3))
    rng.shuffle(triples)
    for t in triples[:min(len(triples), max(0, n_random // 2))]:
        specs.append((t, tuple(rng.randrange(1, P) for _ in range(3)),
                      rng.randrange(2**31), max_rank))
    n_left = max(0, n_random - len(specs) + len(list(combinations(range(K0, N0), 2))))
    for _ in range(n_left):
        sparsity = rng.choice([2, 3, 4, 5])
        pos = tuple(sorted(rng.sample(range(K0, N0), sparsity)))
        cs = tuple(rng.randrange(1, P) for _ in range(sparsity))
        specs.append((pos, cs, rng.randrange(2**31), max_rank))
    return specs


def main():
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    n_workers = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, cpu_count() - 1)
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    max_rank = int(sys.argv[4]) if len(sys.argv) > 4 else 2

    print(f"# probe_direction_a_n32.py — Direction A subclaim test")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, δ={DELTA}")
    print(f"# n_R={N_R}, k_R=2, m={N_R-2}, w_J={W_J}, w_R={W_R}")
    print(f"# Subclaim (rank-2): # bad lines ≤ R = {R}, so |U ∩ B_w| ≤ {R*(P-1)+1} = {R*P-(R-1)}")
    print(f"# Subclaim (rank-r, r ≤ R): # bad lines ≤ (R q^(r-1) - 1)/(q-1)")
    print(f"#   r=2: ≤ {(R*P-1)//(P-1)} (= 2 for q ≥ 3)")
    print(f"#   r=3: ≤ {(R*P*P-1)//(P-1)} (≈ {2*P+1+2})")
    print(f"#   r=4: ≤ {(R*P*P*P-1)//(P-1)}")
    print(f"# max_rank for line enumeration: {max_rank}")
    print(f"# n_workers={n_workers}, n_random={n_random}, seed={seed}")
    print()

    specs = build_candidate_specs(n_random, seed, max_rank)
    print(f"# {len(specs)} candidate f-specs. Dispatching to {n_workers} workers...")
    print()

    t0 = time.time()
    results = []
    counts = {'BELOW_J': 0, 'ABOVE_J_RANK_0': 0, 'ABOVE_J_RANK_1': 0,
              'ABOVE_J_RANK_2': 0, 'ABOVE_J_RANK_3': 0, 'ABOVE_J_RANK_4': 0,
              'SKIPPED_HIGH_RANK': 0}
    n_done = 0
    rank_results = {}  # rank -> list of result dicts (only ones we processed)
    with Pool(n_workers) as pool:
        for r in pool.imap_unordered(process_one_f, specs, chunksize=4):
            n_done += 1
            results.append(r)
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if r.get('skipped'):
                counts['SKIPPED_HIGH_RANK'] += 1
            elif r['rank'] is not None and r['rank'] >= 1:
                rank_results.setdefault(r['rank'], []).append(r)
            if n_done % 20 == 0:
                rate = n_done / (time.time() - t0)
                print(f"#  {n_done}/{len(specs)}  rate {rate:.2f}/sec",
                      flush=True)
    elapsed = time.time() - t0

    print()
    print(f"# === DONE in {elapsed:.0f}s ({len(specs)/elapsed:.2f} f/sec) ===")
    print(f"# Total f's: {len(specs)}")
    for k, v in sorted(counts.items()):
        print(f"#   {k}: {v}")
    print()

    for rank in sorted(rank_results):
        rs = rank_results[rank]
        if not rs:
            continue
        print(f"# === RANK-{rank} ABOVE-J: {len(rs)} processed ===")
        bad_dist = {}
        max_bad = -1
        worst_f = rs[0]
        for r in rs:
            bc = r['bad_count']
            if bc is None:
                continue
            bad_dist[bc] = bad_dist.get(bc, 0) + 1
            if bc > max_bad:
                max_bad = bc; worst_f = r
        n_lines_one = rs[0]['n_lines'] if rs else 0
        # Bound on |U ∩ B_w|: R q^{r-1}. Bound on # bad lines:
        #   if R q^{r-1} ≥ q (i.e., always for r ≥ 2): ⌊(R q^{r-1} - 1)/(q-1)⌋
        #   if R q^{r-1} < q (i.e., r = 1 with R=2 < q): bad lines must be 0
        intersect_bound = R * (P ** (rank - 1))
        target_bound = (intersect_bound - 1) // (P - 1) if intersect_bound >= P else 0
        max_intersect = max((r['intersect_size'] or 1) for r in rs)
        print(f"#   n_lines per f = (q^{rank}-1)/(q-1) = {n_lines_one}")
        print(f"#   Target bound on |U ∩ B_w|: R q^(r-1) = {intersect_bound}")
        print(f"#   Target bound on # bad lines: {target_bound}")
        print(f"#   Max # bad lines observed: {max_bad}")
        print(f"#   Max |U ∩ B_w| observed: {max_intersect}")
        print(f"#   # bad lines distribution: {dict(sorted(bad_dist.items()))}")
        print(f"#   Worst f: positions={worst_f['positions']}, bad={max_bad}, "
              f"|U∩B_w|={worst_f['intersect_size']}")
        if max_bad > target_bound:
            print(f"#   ★★★ FALSIFIES bound {target_bound}: max_bad={max_bad} ★★★")
        else:
            print(f"#   ✓ All within bound {target_bound}")
        print()

    # Print sample worst cases per rank
    for rank in sorted(rank_results):
        rs = sorted(rank_results[rank], key=lambda r: -(r['bad_count'] or -1))[:10]
        if not rs:
            continue
        print(f"# === Top 10 worst rank-{rank} cases (by bad_count) ===")
        for r in rs:
            print(f"#   pos={r['positions']}, dist_lb={r['dist_lb']}, "
                  f"bad={r['bad_count']}, |U∩B_w|={r['intersect_size']}")
            if r['bad_count'] and r['bad_count'] > 0:
                for rep, w, T in r.get('bad_reps', [])[:3]:
                    print(f"#     bad_rep_v={rep}, sw={w}, T={T}")
        print()


if __name__ == '__main__':
    main()
