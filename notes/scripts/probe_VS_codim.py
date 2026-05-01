"""probe_VS_codim.py — Path B Attempt 1: enumerate V_T = {α : H·g(α) ∈ image(H_T)}
and compare with V_exact = {α : H·g(α) = 0}.

For each above-Johnson f, partition α-space:
  - V_exact (g(α) ∈ C_R)
  - For each T ⊂ L_R with 1 ≤ |T| ≤ w_R: V_T \ V_exact

Goal: empirically test the codim-(n_R - k_R - |T|) bound for V_T \ V_exact.

If for the smallest codim |T|=w_R: |V_T \ V_exact| ≤ R · q^{(n_R-k_R-w_R)-1}
times C(n_R, w_R), then we close the gap.

Usage: python3 probe_VS_codim.py <p> <n_0> <k_0> <R> <delta_frac>
"""
from __future__ import annotations
import sys, time
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
    """Return basis (list of column vectors) of span of H[:,T]."""
    cols = [[H[i][j] for i in range(len(H))] for j in T]
    # Reduce to basis via Gauss
    # Cols are vectors in F_p^{n-k}. Basis = independent cols.
    if not cols:
        return []
    syn_dim = len(cols[0])
    rows = [list(c) for c in cols]  # rows = cols transposed for ranking
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
    return pivot_rows  # list of vectors spanning image


def in_subspace(v, basis, p):
    """Is v in the span of basis (rows)?"""
    if not basis:
        return all(x == 0 for x in v)
    syn_dim = len(v)
    aug = [list(b) for b in basis]
    aug.append(list(v))
    r1 = gauss_rank(basis, p)
    r2 = gauss_rank(aug, p)
    return r1 == r2


def main():
    if len(sys.argv) < 6:
        print("Usage: python3 probe_VS_codim.py <p> <n_0> <k_0> <R> <delta_frac>", file=sys.stderr)
        sys.exit(1)
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    qR = p ** R
    Rq = R / p

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, n_R-k_R={n_R-k_R}")
    print(f"# q^R={qR}, R/q={Rq:.6e}")
    print(f"# Bound R·q^{{R-1}}={R*p**(R-1)}")

    # Adversarial f's to test
    # CS lift: f = X^{2^R · 2 - 1} + X^{2^R · 2 - 2} = X^{2*2^R-1} + X^{2*2^R-2}
    # For R=2: X^7 + X^6
    cs_a = 2 * (2**R) - 1
    cs_b = 2 * (2**R) - 2
    cs_a_alt = 2 * (2**R) + 1
    cs_b_alt = 2 * (2**R)

    f_list = []
    if cs_a < n0 and cs_b < n0:
        fhat = [0]*n0; fhat[cs_a] = 1; fhat[cs_b] = 1
        f_list.append((f"CS:X^{cs_a}+X^{cs_b}", evaluate_dft(fhat, L0, p)))
    if cs_a_alt < n0 and cs_b_alt < n0:
        fhat = [0]*n0; fhat[cs_a_alt] = 1; fhat[cs_b_alt] = 1
        f_list.append((f"CS-alt:X^{cs_a_alt}+X^{cs_b_alt}", evaluate_dft(fhat, L0, p)))
    # Two random sparse above-J:
    import random
    rng = random.Random(2026)
    for trial in range(3):
        fhat = [0]*n0
        positions = rng.sample(range(k0, n0), 4)
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f_list.append((f"sparse_{sorted(positions)}", evaluate_dft(fhat, L0, p)))

    # Precompute image(H_T) for all T with 1 ≤ |T| ≤ w_R
    print(f"# Precomputing image(H_T) for all T's of size 1..{w_R}...")
    T_list = []
    for tsize in range(1, w_R + 1):
        for T in combinations(range(n_R), tsize):
            basis = image_HT(H_R, T, p)
            T_list.append((T, basis))
    print(f"# Total T's: {len(T_list)}")
    print()

    for fname, f in f_list:
        print(f"## f = {fname}")
        t0 = time.time()
        # Enumerate all α, compute syndrome H g(α)
        v_exact = 0
        # For each T, count α with syn ∈ image(H_T) AND syn ≠ 0 (so α ∉ V_exact)
        v_T_minus_exact = {T: 0 for T, _ in T_list}
        v_delta_minus_exact = 0  # α with g(α) ∉ C_R but in some V_T

        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = syndrome(g, H_R, p)
            if all(x == 0 for x in syn):
                v_exact += 1
                continue
            # α ∉ V_exact. Check each T.
            in_some_T = False
            for T, basis in T_list:
                if in_subspace(syn, basis, p):
                    v_T_minus_exact[T] += 1
                    in_some_T = True
            if in_some_T:
                v_delta_minus_exact += 1

        elapsed = time.time() - t0
        v_delta = v_exact + v_delta_minus_exact
        print(f"  |V_exact| = {v_exact}  (ratio to q^R: {v_exact/qR:.4e}, to R/q: {v_exact/qR/Rq:.3f})")
        print(f"  |V_δ \\ V_exact| = {v_delta_minus_exact}  (ratio to q^R: {v_delta_minus_exact/qR:.4e})")
        print(f"  |V_δ| = {v_delta}  (ratio to q^R: {v_delta/qR:.4e}, to R/q: {v_delta/qR/Rq:.3f})")

        # Per-T statistics
        nz_Ts = [(T, c) for T, c in v_T_minus_exact.items() if c > 0]
        if nz_Ts:
            print(f"  Per-T |V_T \\ V_exact| (nonzero only, top 10):")
            nz_Ts.sort(key=lambda x: -x[1])
            for T, c in nz_Ts[:10]:
                # Predicted codim: n_R - k_R - |T|
                codim = n_R - k_R - len(T)
                pred = R**min(codim, R) * p**max(0, R - codim) if codim > 0 else qR
                print(f"    T={T}: count={c}, codim_pred={codim}, "
                      f"|V_T| bound={pred}, ratio_to_bound={c/pred:.3f}")
        print(f"  ({elapsed:.1f}s)")
        print()


if __name__ == '__main__':
    main()
