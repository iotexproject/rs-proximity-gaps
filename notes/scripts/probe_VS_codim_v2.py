"""probe_VS_codim_v2.py — extended version: more f's + per-T fine analysis.

Key new diagnostics:
  - For each f, report dim of image of α -> H·g(α) (the "effective syndrome rank")
  - Per-T: not just count, but also rank of H·g(α) restricted to V_T
  - Check refined conjecture: |V_exact| + |V_δ \ V_exact| ≤ R q^{R-1} + O(q^{R-2})

Goal: find ANY f where |V_δ|/q^R > R/q + ε. If none, the bound is empirically tight.
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
    syn_dim = len(cols[0])
    rows = [list(c) for c in cols]
    nr = len(rows)
    rank = 0
    col = 0
    pivot_rows = []
    while rank < nr and col < syn_dim:
        pr = None
        for r in range(rank, nr):
            if rows[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            col += 1
            continue
        rows[rank], rows[pr] = rows[pr], rows[rank]
        pivot_rows.append(list(rows[rank]))
        inv = modinv(rows[rank][col], p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for r in range(nr):
            if r != rank and rows[r][col] != 0:
                f = rows[r][col]
                rows[r] = [(rows[r][c] - f * rows[rank][c]) % p for c in range(syn_dim)]
        rank += 1
        col += 1
    return pivot_rows


def in_subspace(v, basis, p):
    if not basis:
        return all(x == 0 for x in v)
    aug = list(basis) + [list(v)]
    r1 = gauss_rank(basis, p)
    r2 = gauss_rank(aug, p)
    return r1 == r2


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 probe_VS_codim_v2.py <p> <n_0> <k_0> <R> <delta_frac> [n_random=20]", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])
    n_random = int(sys.argv[6]) if len(sys.argv) > 6 else 20

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
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, n_R-k_R={n_R-k_R}, q^R={qR}, R/q={Rq:.6e}")
    print(f"# Phase 1 bound R·q^{{R-1}}={bound_phase1}, ratio_to_R/q=1.000")
    print()

    # f's: CS variants + many sparse above-Johnson
    f_list = []

    # CS lifts: r = 2*2^R - 1 saturates exactly (note 0097)
    cs_a = 2 * (2**R) - 1
    cs_b = 2 * (2**R) - 2
    if cs_a < n0 and cs_b < n0:
        fhat = [0]*n0; fhat[cs_a] = 1; fhat[cs_b] = 1
        f_list.append((f"CS:X^{cs_a}+X^{cs_b}", evaluate_dft(fhat, L0, p)))

    # Other CS-style with various offsets
    for offset in [1, 2, 3]:
        a = cs_a + offset
        b = cs_b + offset
        if k0 <= a < n0 and k0 <= b < n0:
            fhat = [0]*n0; fhat[a] = 1; fhat[b] = 1
            f_list.append((f"CS+{offset}:X^{a}+X^{b}", evaluate_dft(fhat, L0, p)))

    # Random sparse above-J
    rng = random.Random(2026)
    for trial in range(n_random):
        sparsity = rng.choice([2, 3, 4, 5])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f_list.append((f"sparse_{sorted(positions)}", evaluate_dft(fhat, L0, p)))

    # Pre-compute T list
    T_list = []
    for tsize in range(1, w_R + 1):
        for T in combinations(range(n_R), tsize):
            basis = image_HT(H_R, T, p)
            T_list.append((T, basis))

    # Summary table
    max_ratio_to_Rq = 0.0
    max_ratio_to_Phase1 = 0.0
    falsifiers = 0
    print(f"{'f':40s} {'|V_exact|':>10s} {'|V_δ\\V_e|':>10s} {'|V_δ|':>10s} {'V_δ/R q^{R-1}':>14s} {'syn_rank':>9s}")
    print("-" * 95)

    for fname, f in f_list:
        # Compute syndrome rank: dim of {H g(α) : α}
        all_syns = []
        v_exact = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = syndrome(g, H_R, p)
            all_syns.append(syn)
            if all(x == 0 for x in syn):
                v_exact += 1

        # Reduce to basis
        syn_rank = gauss_rank([list(s) for s in all_syns[:200] if any(x != 0 for x in s)] or [[0]*(n_R-k_R)], p)
        # Actually use full set if small; sample if huge
        if R <= 2:
            nonzero_syns = [list(s) for s in all_syns if any(x != 0 for x in s)]
            syn_rank = gauss_rank(nonzero_syns, p) if nonzero_syns else 0

        # V_δ: count α with syn ∈ image(H_T) for some T
        v_delta = v_exact
        for syn in all_syns:
            if all(x == 0 for x in syn):
                continue
            for T, basis in T_list:
                if in_subspace(syn, basis, p):
                    v_delta += 1
                    break

        v_diff = v_delta - v_exact
        ratio_Rq = v_delta / qR / Rq
        ratio_phase1 = v_delta / bound_phase1
        if ratio_Rq > max_ratio_to_Rq:
            max_ratio_to_Rq = ratio_Rq
        if ratio_phase1 > max_ratio_to_Phase1:
            max_ratio_to_Phase1 = ratio_phase1
        if ratio_Rq > 1.001:
            falsifiers += 1
            marker = "★FALSIFIER★"
        else:
            marker = ""
        print(f"{fname:40s} {v_exact:10d} {v_diff:10d} {v_delta:10d} {ratio_phase1:14.4f} {syn_rank:9d} {marker}")

    print("-" * 95)
    print(f"# Total f's tested: {len(f_list)}")
    print(f"# Max |V_δ|/(R q^{{R-1}}) ratio: {max_ratio_to_Phase1:.4f}")
    print(f"# Max |V_δ|/q^R ratio to R/q: {max_ratio_to_Rq:.4f}")
    print(f"# Falsifiers: {falsifiers}")


if __name__ == '__main__':
    main()
