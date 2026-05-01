"""debug_q193_trial4.py — investigate the apparent disjointness failure.

The case: q=193, pos=[9, 16, 25], |S_1*|=0, count_8=5, disjoint=False.

Question: does the corollary's pairwise-stability claim S_1(α) ∩ S_1(α') = S_1*(f)
actually fail here, or is my agreement-set computation buggy (e.g., picking
inconsistent closest codewords across α)?
"""
from __future__ import annotations
import sys, os, random
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

P = 193


def all_codewords_at_max_agreement(fold, L1, k1, p):
    """Return ALL codewords with maximum agreement to fold, plus their agreement sets."""
    n1 = len(L1)
    best_agree = -1
    candidates = {}  # tuple(c) -> S
    for T in combinations(range(n1), k1):
        c_full = []
        for x_eval in L1:
            v = 0
            for j_loc in range(k1):
                num = 1; den = 1
                xj = L1[T[j_loc]]
                for k_loc in range(k1):
                    if k_loc == j_loc: continue
                    xk = L1[T[k_loc]]
                    num = (num * (x_eval - xk)) % p
                    den = (den * (xj - xk)) % p
                term = (fold[T[j_loc]] * num * pow(den, p - 2, p)) % p
                v = (v + term) % p
            c_full.append(v)
        agree = sum(1 for i in range(n1) if c_full[i] == fold[i])
        key = tuple(c_full)
        if agree > best_agree:
            best_agree = agree
            candidates = {key: agree}
        elif agree == best_agree:
            candidates[key] = agree
    return best_agree, candidates


def main():
    p = P
    chain = setup_chain(p, N0, K0, R=R)
    L0 = chain[0][0]
    L1, k1, _ = chain[1]
    n1 = len(L1)

    # Reproduce the failing trial: rng = Random(2026 + 193), trial 4 of 5 above-J f
    rng = random.Random(2026 + p)
    from mds_decoder import dist_lower_bound_sampling
    W_J = N0 // 2

    # Reproduce the same f as in verify_disjoint_extras.py trial 4
    target_pos = [9, 16, 25]  # The failing positions
    found_f = None
    for trial_idx in range(5):
        # Replicate the same gen_random_above_J calls
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
                    found_f = (f, positions, fhat)
                break
    f, positions, fhat = found_f
    print(f"Reproduced trial 4: positions={positions}")
    assert positions == target_pos

    f_e, f_o = even_odd_parts(f, L0, p)

    # For all α, compute (best_agree, list of agreement sets at max).
    print()
    print("α-scan: (α, max_agree, list_size, agreement_sets):")
    alphas_with_geq_8 = []
    all_S_per_alpha = {}
    for a in range(min(p, 50)):  # limit for tractability
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(n1)]
        best_agree, candidates = all_codewords_at_max_agreement(fold, L1, k1, p)
        if best_agree >= 8:
            agreement_sets = []
            for c, ag in candidates.items():
                S = frozenset(i for i in range(n1) if c[i] == fold[i])
                agreement_sets.append(S)
            all_S_per_alpha[a] = agreement_sets
            alphas_with_geq_8.append(a)
            print(f"  α={a}: best_agree={best_agree}, list_size={len(candidates)}, sets={[sorted(S) for S in agreement_sets]}")

    print()
    print(f"Number of α (≤50) with best_agree ≥ 8: {len(alphas_with_geq_8)}")

    # Now check: for any choice of S per α, can we make pairwise = S_1*?
    if len(alphas_with_geq_8) >= 2:
        a1, a2 = alphas_with_geq_8[0], alphas_with_geq_8[1]
        for S1 in all_S_per_alpha[a1]:
            for S2 in all_S_per_alpha[a2]:
                inter = S1 & S2
                print(f"  α={a1} S={sorted(S1)}, α={a2} S={sorted(S2)}, |∩|={len(inter)}, ∩={sorted(inter)}")


if __name__ == "__main__":
    main()
