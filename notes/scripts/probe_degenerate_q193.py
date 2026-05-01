"""probe_degenerate_q193.py — measure tie for the degenerate K=2 case at q=193 pos {9,16,25}.

The case where verify_disjoint_extras.py found list-size = 2 at α=0:
- f_e = c · y^8 on L_1 (single char of order 8 in cyclic group of order 16)
- TWO closest codewords (constants ±c) with disjoint agreement sets

Question: does this give tie > 7/16 (violating master theorem)?
Or is it bounded by the K=1 leader-style bound?
"""
from __future__ import annotations
import sys, os, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts, dist_to_code_full, parity_check

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

P = 193


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L1, k1, H1 = chain[1]
    n1 = len(L1)
    rng = random.Random(2026 + p)

    # Reproduce trial 4
    from mds_decoder import dist_lower_bound_sampling
    W_J = N0 // 2
    f_target = None
    for trial_idx in range(5):
        while True:
            n_pos = rng.choice((3, 4, 5, 6))
            positions = sorted(rng.sample(range(K0, N0), n_pos))
            fhat = [0] * N0
            for pos in positions:
                fhat[pos] = rng.randrange(1, p)
            f = evaluate_dft(fhat, L0, p)
            d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
            if d > W_J:
                if trial_idx == 4:
                    f_target = (f, positions, fhat)
                break

    f, pos, fhat = f_target
    print(f"q={p}, pos={pos}, fhat[pos]={[fhat[p] for p in pos]}")
    f_e, f_o = even_odd_parts(f, L0, p)

    # dist(f_e, C_1), dist(f_o, C_1)
    d_fe, _ = dist_to_code_full(f_e, H1, n1, k1, p)
    d_fo, _ = dist_to_code_full(f_o, H1, n1, k1, p)
    print(f"dist(f_e, C_1) = {d_fe}, dist(f_o, C_1) = {d_fo}")

    # Full d_1 distribution across α ∈ F_q
    d1_dist = {}
    for a in range(p):
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(n1)]
        d1, _ = dist_to_code_full(fold, H1, n1, k1, p)
        d1_dist[d1] = d1_dist.get(d1, 0) + 1

    print(f"d_1 distribution across all {p} α: {sorted(d1_dist.items())}")
    avg_d1 = sum(d * cnt for d, cnt in d1_dist.items()) / p
    print(f"Average d_1 = {avg_d1:.4f}")
    tie_2round = 1 - avg_d1 / n1
    print(f"tie^(2) (1-round approx) = 1 - avg_d1/n_1 = {tie_2round:.4f}")
    print(f"Compared to 7/16 = {7/16:.4f}; (1-δ) = 1/2")
    print()
    print(f"Master theorem rigorous (K=1 multi-round): tie ≤ 7/16 + (R/q)*(9/16) = "
          f"{7/16 + 2/p * 9/16:.4f} at R=2.")
    print()
    if tie_2round > 7/16:
        print(f"⚠ tie {tie_2round:.4f} > 7/16 = {7/16:.4f}. Sub-7/16 fails at finite q.")
    if tie_2round > 1/2:
        print(f"🚨 tie {tie_2round:.4f} > 1/2. CRITICAL: above (1-δ) target!")
    else:
        print(f"✓ tie {tie_2round:.4f} ≤ 1/2 = (1-δ). Standard FRI soundness holds.")


if __name__ == "__main__":
    main()
