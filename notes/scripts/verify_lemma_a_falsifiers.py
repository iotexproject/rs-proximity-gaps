"""verify_lemma_a_falsifiers.py — verify the 6 candidate Lemma A falsifiers.

probe_dmin_W_rank2 found 6 rank-2 above-J f's with d_min(W) ≤ 3, contradicting
note 0108's "443/443 zero bad lines" claim. Reasons for discrepancy:
  - Different spec generators / sample sizes.
  - Possibly above-J false positive (FPR ~ exp(-61) ≈ 0 but nonzero).

For each candidate, we:
  1. Re-verify above-J with 3 independent seeds (each 50K samples).
  2. Recompute corner syndromes, image rank.
  3. Recompute d_min(W) and identify the weight-≤3 W-codeword.
  4. Compute true |V_δ| via brute-force α ∈ F_q^R enumeration.
  5. Check whether |V_δ| ≤ R q^(R-1) = 194 still holds.

If true |V_δ| > 194: Direction A's |V_δ| ≤ R q^(R-1) bound is FALSIFIED for rank-2.
If true |V_δ| ≤ 194: Direction A holds, but Lemma A as formulated needs refinement.
"""
from __future__ import annotations
import sys, os
from itertools import product, combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, parity_check, gauss_rank, matvec, modinv
from mds_decoder import is_above_johnson_sampling
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J,
    evaluate_dft, fold_at_alpha, compute_corner_syndromes, min_wt_via_MDS,
)
from probe_dmin_W_rank2 import build_G_W, dmin_W


CANDIDATES = [
    ((12, 18, 22), (59, 73, 36)),
    ((14, 18, 31), (90, 90, 88)),
    ((9, 19, 27),  (16, 86, 49)),
    ((13, 22, 30), (23, 17, 17)),
    ((9, 10, 22, 25, 26), (30, 38, 58, 50, 69)),
    ((14, 18, 28, 30), (91, 88, 70, 22)),
]


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    target_bound = R * P  # 2q = 194

    print(f"# verify_lemma_a_falsifiers — checking 6 candidates")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, w_R=3, w_J={W_J}, target |V_δ| ≤ {target_bound}")
    print()

    for positions, coefs in CANDIDATES:
        print(f"\n=== positions={positions}, coefs={coefs} ===")
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, P)

        # 1. Multi-seed above-J verification
        verdicts = []
        max_extras_seen = 0
        for sd in [10001, 20002, 30003]:
            above, max_e, _ = is_above_johnson_sampling(
                f, L0, K0, P, W_J, n_samples=50000, batch=4096, seed=sd,
                return_evidence=True,
            )
            verdicts.append(above)
            max_extras_seen = max(max_extras_seen, max_e)
        all_above = all(verdicts)
        dist_lb = (N0 - K0) - max_extras_seen
        print(f"  above-J (3 seeds): {verdicts}  (consistent={all_above}, dist_lb≥{dist_lb})")
        print(f"  w_J = {W_J}, dist_lb = {dist_lb}, above-J: {dist_lb > W_J}")

        # 2. Image rank
        corner_syns = compute_corner_syndromes(f, chain, R, P, H_R)
        nz = [s for s in corner_syns.values() if any(x != 0 for x in s)]
        rank = gauss_rank([list(s) for s in nz], P) if nz else 0
        print(f"  image rank = {rank}")

        # 3. d_min(W) and identify the bad codeword
        G_W, dim_W = build_G_W(f, chain, R, P, k_R, N_R, L_R)
        d_min = dmin_W(G_W, N_R, P, max_w_to_check=5)
        print(f"  dim(W) = {dim_W}, d_min(W) = {d_min}")

        # Find the weight-d_min codeword (any one)
        if d_min <= 3:
            for T in combinations(range(N_R), d_min):
                T_c = [j for j in range(N_R) if j not in T]
                G_proj = [[row[j] for j in T_c] for row in G_W]
                rk = gauss_rank([list(r) for r in G_proj], P)
                if rk < dim_W:
                    # Find the codeword: vector u in F_q^4 (dim_W=4) with G_W^T u nonzero on T only.
                    # Equivalent: find linear comb of rows that vanishes on T_c.
                    # Solve u s.t. for j in T_c: sum_i u_i G_W[i][j] = 0.
                    A = [[G_W[i][j] for i in range(dim_W)] for j in T_c]
                    # Find non-trivial null vector of A
                    M = [list(r) for r in A]
                    n_rows = len(M)
                    pivot = {}
                    cur = 0
                    for col in range(dim_W):
                        if cur >= n_rows:
                            break
                        pr = None
                        for r in range(cur, n_rows):
                            if M[r][col] % P != 0:
                                pr = r; break
                        if pr is None:
                            continue
                        M[cur], M[pr] = M[pr], M[cur]
                        inv = modinv(M[cur][col], P)
                        M[cur] = [(x * inv) % P for x in M[cur]]
                        for rr in range(n_rows):
                            if rr != cur and M[rr][col] != 0:
                                ff = M[rr][col]
                                M[rr] = [(M[rr][c] - ff * M[cur][c]) % P for c in range(dim_W)]
                        pivot[col] = cur
                        cur += 1
                    free_cols = [c for c in range(dim_W) if c not in pivot]
                    if not free_cols:
                        continue
                    u = [0] * dim_W
                    fc = free_cols[0]
                    u[fc] = 1
                    for c, r in pivot.items():
                        u[c] = (-M[r][fc]) % P
                    # Compute codeword w = u^T G_W
                    w = [sum(u[i] * G_W[i][j] for i in range(dim_W)) % P for j in range(N_R)]
                    print(f"  weight-{d_min} codeword: support={T}, w={w}")
                    break

        # 4. True |V_δ| via brute-force
        from probe_step5_n32_studio import min_wt_via_MDS
        v_delta = 0
        for alphas in product(range(P), repeat=R):
            g = fold_at_alpha(f, chain, list(alphas), P)
            syn = matvec(H_R, g, P)
            if all(x == 0 for x in syn):
                v_delta += 1
                continue
            w_min, _T, _e = min_wt_via_MDS(syn, H_R, N_R, P, max_w=3)
            if w_min is not None:
                v_delta += 1
        ratio = v_delta / target_bound
        marker = " ★ EXCEEDS BOUND" if v_delta > target_bound else ""
        print(f"  |V_δ| = {v_delta}, ratio = {ratio:.3f}{marker}")


if __name__ == '__main__':
    main()
