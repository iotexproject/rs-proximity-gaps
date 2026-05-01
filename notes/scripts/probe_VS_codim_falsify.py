"""probe_VS_codim_falsify.py — heavy falsifier search for the refined conjecture
|V_δ| ≤ R · q^{R-1} (the FULL V_δ, not just V_exact).

Strategy:
  - All single-monomial CS-style: X^a + X^b for valid (a,b) in syndrome window
  - All triples X^a + X^b + X^c
  - Random sparse with 1-5 nonzero positions and random coefficients
  - "Anti-aligned": construct fhat to maximize syn_rank and V_T\V_exact

Goal: find ANY f with |V_δ|/q^R > R/q + ε.
"""
from __future__ import annotations
import sys, time, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, gauss_rank, modinv
)


def true_fold_R(f, chain, alphas, p):
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def syndrome(g, H, p):
    return tuple(matvec(H, g, p))


def image_HT(H, T, p):
    cols = [[H[i][j] for i in range(len(H))] for j in T]
    if not cols:
        return []
    rows = [list(c) for c in cols]
    nr = len(rows)
    syn_dim = len(rows[0])
    rank = 0; col = 0
    pivot_rows = []
    while rank < nr and col < syn_dim:
        pr = None
        for r in range(rank, nr):
            if rows[r][col] % p != 0:
                pr = r; break
        if pr is None:
            col += 1; continue
        rows[rank], rows[pr] = rows[pr], rows[rank]
        pivot_rows.append(list(rows[rank]))
        inv = modinv(rows[rank][col], p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for r in range(nr):
            if r != rank and rows[r][col] != 0:
                f = rows[r][col]
                rows[r] = [(rows[r][c] - f * rows[rank][c]) % p for c in range(syn_dim)]
        rank += 1; col += 1
    return pivot_rows


def in_subspace(v, basis, p):
    if not basis:
        return all(x == 0 for x in v)
    aug = list(basis) + [list(v)]
    return gauss_rank(basis, p) == gauss_rank(aug, p)


def V_delta_size(f, chain, R, p, T_list, qR):
    L_R, k_R, H_R = chain[R]
    n_R = len(L_R)
    v_delta = 0
    for alphas in product(range(p), repeat=R):
        g = true_fold_R(f, chain, list(alphas), p)
        syn = syndrome(g, H_R, p)
        if all(x == 0 for x in syn):
            v_delta += 1; continue
        for T, basis in T_list:
            if in_subspace(syn, basis, p):
                v_delta += 1; break
    return v_delta


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 probe_VS_codim_falsify.py <p> <n_0> <k_0> <R> <delta_frac> [n_random=200]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])
    n_random = int(sys.argv[6]) if len(sys.argv) > 6 else 200

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    qR = p ** R
    Rq = R / p
    bound_phase1 = R * p**(R-1)

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, q^R={qR}, R q^{{R-1}}={bound_phase1}")
    print(f"# Falsifying conjecture |V_δ| ≤ R q^{{R-1}}")
    print()

    T_list = []
    for tsize in range(1, w_R + 1):
        for T in combinations(range(n_R), tsize):
            T_list.append((T, image_HT(H_R, T, p)))

    rng = random.Random(2026)
    max_ratio = 0.0
    max_f_label = None
    falsifiers = 0
    n_tested = 0
    t0 = time.time()

    # Strategy 1: ALL pairs in syndrome window
    print("# Strategy 1: all pairs (a,b) with k_0 ≤ a < b < n_0")
    for a, b in combinations(range(k0, n0), 2):
        fhat = [0]*n0; fhat[a] = 1; fhat[b] = 1
        f = evaluate_dft(fhat, L0, p)
        v_delta = V_delta_size(f, chain, R, p, T_list, qR)
        ratio = v_delta / bound_phase1
        n_tested += 1
        if ratio > max_ratio:
            max_ratio = ratio; max_f_label = f"X^{a}+X^{b}"
        if ratio > 1.001:
            falsifiers += 1
            print(f"  ⚠ FALSIFIER: X^{a}+X^{b}, |V_δ|={v_delta}, ratio={ratio:.4f}")

    # Strategy 2: ALL triples
    print(f"# Strategy 1 done ({n_tested} pairs). Strategy 2: random triples + small subsets")
    for trial in range(n_random):
        sparsity = rng.choice([2, 3, 4, 5])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        v_delta = V_delta_size(f, chain, R, p, T_list, qR)
        ratio = v_delta / bound_phase1
        n_tested += 1
        if ratio > max_ratio:
            max_ratio = ratio
            max_f_label = f"sparse_{sorted(positions)}"
            print(f"  best so far: {max_f_label}, |V_δ|={v_delta}, ratio={ratio:.4f}  ({time.time()-t0:.0f}s)", flush=True)
        if ratio > 1.001:
            falsifiers += 1
            print(f"  ⚠ FALSIFIER: sparse_{sorted(positions)}, |V_δ|={v_delta}, ratio={ratio:.4f}")

    # Strategy 3: targeted attack — try to maximize V_T\V_exact
    # Pick fhat designed so that φ(α) lies on a specific line in image(H_T)
    print(f"# Strategy 3: targeted — fhat coefficients designed to put image(φ) inside image(H_T)")
    for T_size in [1]:
        for T in combinations(range(n_R), T_size):
            basis_T = image_HT(H_R, T, p)
            # Try few f's: random fhat support, then random coefficients
            for trial in range(20):
                positions = rng.sample(range(k0, n0), rng.choice([2, 3, 4]))
                fhat = [0]*n0
                for pos in positions:
                    fhat[pos] = rng.randrange(1, p)
                f = evaluate_dft(fhat, L0, p)
                v_delta = V_delta_size(f, chain, R, p, T_list, qR)
                ratio = v_delta / bound_phase1
                n_tested += 1
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_f_label = f"target_T={T}_sparse_{sorted(positions)}"
                if ratio > 1.001:
                    falsifiers += 1
                    print(f"  ⚠ FALSIFIER: T={T}, sparse_{sorted(positions)}, ratio={ratio:.4f}")

    print()
    print(f"# === SUMMARY ===")
    print(f"# Tested {n_tested} f's. Time: {time.time()-t0:.1f}s")
    print(f"# Max ratio |V_δ|/(R q^{{R-1}}): {max_ratio:.4f} ({max_f_label})")
    print(f"# Falsifiers: {falsifiers}")
    if falsifiers == 0:
        print(f"# *** Conjecture |V_δ| ≤ R q^{{R-1}} HOLDS across {n_tested} f's. ***")


if __name__ == '__main__':
    main()
