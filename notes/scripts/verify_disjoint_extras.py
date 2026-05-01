"""verify_disjoint_extras.py — verify the rigorous disjointness claim.

CLAIM (RIGOROUS, from Cor~cor:pairwise-stable):
For above-J f and any distinct α, α' ∈ F_q*:
    S_1(α) ∩ S_1(α') = S_1*(f) (with equality).

Hence E_α := S_1(α) \ S_1*(f) are PAIRWISE DISJOINT subsets of L_1 \ S_1*(f).

CONSEQUENCE: |{α : |S_1(α)| ≥ √ρ_0 n_1}| ≤ ⌊(n_1 - |S_1*|)/(√ρ_0 n_1 - |S_1*|)⌋ ≤ 9
for our toy parameters, q-UNIFORMLY.

This script: empirically verifies disjointness across many K=2 dense above-J f
at q ∈ {97, 193, 449}.
"""
from __future__ import annotations
import sys, os, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import setup_chain, even_odd_parts, dist_to_code_full, parity_check

import probe_step5_n32_studio
from probe_step5_n32_studio import N0, K0, R, evaluate_dft

W_J = N0 // 2  # 16


def closest_codeword_agreement(fold, L1, k1, p):
    """Return (closest c ∈ RS_k1(L1), agreement set as frozenset of L_1 indices).

    Uses brute-force enumeration over all info-sets T ⊂ [n_1] of size k1.
    """
    from itertools import combinations
    n1 = len(L1)
    best_agree = -1
    best_S = None
    for T in combinations(range(n1), k1):
        # Lagrange interp at L_1 points using values at T
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
        if agree > best_agree:
            best_agree = agree
            best_S = frozenset(i for i in range(n1) if c_full[i] == fold[i])
    return best_S, best_agree


def gen_random_above_J(rng, p, L0, n_pos_choices=(3, 4, 5, 6)):
    from mds_decoder import dist_lower_bound_sampling
    while True:
        n_pos = rng.choice(n_pos_choices)
        positions = sorted(rng.sample(range(K0, N0), n_pos))
        fhat = [0] * N0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d = dist_lower_bound_sampling(f, L0, K0, p, n_samples=2000, batch=2048, seed=rng.randrange(10**9))
        if d > W_J:
            return f, positions


def main():
    print("=== Verifying disjointness: S_1(α) ∩ S_1(α') = S_1*(f) ===")
    print()
    for p in [97, 193, 449]:
        if (p - 1) % N0 != 0:
            continue
        chain = setup_chain(p, N0, K0, R=R)
        L0 = chain[0][0]
        L1, k1, _ = chain[1]
        n1 = len(L1)
        rng = random.Random(2026 + p)
        n_tests = 5
        ok_disjoint = 0
        ok_count = 0
        max_count_at_p = 0
        max_S1_star_at_p = 0
        for trial in range(n_tests):
            f, pos = gen_random_above_J(rng, p, L0)
            f_e, f_o = even_odd_parts(f, L0, p)
            agreement_sets = {}
            for a in range(p):
                fold = [(f_e[j] + a * f_o[j]) % p for j in range(n1)]
                S, agree = closest_codeword_agreement(fold, L1, k1, p)
                agreement_sets[a] = (S, agree)
            S1_star = None
            for S, _ in agreement_sets.values():
                S1_star = S if S1_star is None else (S1_star & S)
            count_geq_8 = sum(1 for S, ag in agreement_sets.values() if ag >= 8)
            disjoint = True
            extras = {a: agreement_sets[a][0] - S1_star for a in agreement_sets}
            alphas_with_S1_geq_8 = [a for a in agreement_sets if agreement_sets[a][1] >= 8]
            for i in range(len(alphas_with_S1_geq_8)):
                for j in range(i + 1, len(alphas_with_S1_geq_8)):
                    a, b = alphas_with_S1_geq_8[i], alphas_with_S1_geq_8[j]
                    if extras[a] & extras[b]:
                        disjoint = False
                        break
                if not disjoint: break
            theorem_bound = (n1 - len(S1_star)) // max(1, 8 - len(S1_star))
            print(f"  q={p} trial {trial} (pos={pos}): |S_1*|={len(S1_star)}, count_8={count_geq_8}, bound={theorem_bound}, disjoint={disjoint}")
            if disjoint: ok_disjoint += 1
            if count_geq_8 <= theorem_bound: ok_count += 1
            max_count_at_p = max(max_count_at_p, count_geq_8)
            max_S1_star_at_p = max(max_S1_star_at_p, len(S1_star))
        print(f"  q={p}: disjointness {ok_disjoint}/{n_tests}, count-bound {ok_count}/{n_tests}, max count_8={max_count_at_p}, max |S_1*|={max_S1_star_at_p}")
        print()


if __name__ == "__main__":
    main()
