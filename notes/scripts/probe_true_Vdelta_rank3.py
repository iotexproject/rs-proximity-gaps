"""probe_true_Vdelta_rank3.py — direct |V_δ| count for the worst rank-3 cases.

For rank-3 above-J f at n_0=32, R=2: |U ∩ B_w| can be up to 961 (10 bad lines × 96 + 1).
But Im(φ) is a 2-dim subvariety of 3-dim U, so |Im(φ) ∩ B_w| ≤ |U ∩ B_w| with potentially
much smaller actual count. Direction A target: |V_δ| ≤ R q^{R-1} = 2q = 194.

This script picks the worst rank-3 cases by hand and computes |V_δ| directly via
brute-force α ∈ F_q^R enumeration + sw check. Validates whether the conjecture holds
even when the linear-span overcount fails.
"""
from __future__ import annotations
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import product
from fri_2round_attack import setup_chain, parity_check, matvec
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, evaluate_dft, fold_at_alpha, min_wt_via_MDS,
)


# Worst rank-3 cases from probe_direction_a_n32_p97_rank3.output.txt:
#   pos=(8, 14, 21, 23, 30): bad=10, |U∩B_w|=961  (the worst)
#   pos=(12, 17, 23): bad=8, |U∩B_w|=769
#   pos=(11, 20, 25): bad=8, |U∩B_w|=769
WORST_CASES = [
    ((8, 14, 21, 23, 30), None),  # coefs to be filled
    ((12, 17, 23), None),
    ((11, 20, 25), None),
]


def main():
    chain = setup_chain(P, N0, K0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, P)
    m = N_R - k_R
    W_R = 3
    target_bound = R * P  # 2q = 194

    # We need to know the coefs that the original probe used.
    # The probe's seed=2026 + RNG flow generates coefs for triples and quintuples.
    # To match exactly, we'd need to replay that RNG. Instead, take the simpler
    # approach: try the all-1's coef variant and a few random variants per support.
    import random
    rng = random.Random(2027)
    cases = []
    for positions, _ in WORST_CASES:
        for trial in range(5):
            coefs = tuple(rng.randrange(1, P) for _ in range(len(positions)))
            cases.append((positions, coefs))
        cases.append((positions, tuple(1 for _ in positions)))  # all-1's

    print(f"# probe_true_Vdelta_rank3.py — direct |V_δ| count")
    print(f"# Setup: p={P}, n_0={N0}, k_0={K0}, R={R}, w_R={W_R}")
    print(f"# Target Direction A bound: |V_δ| ≤ 2q = {target_bound}")
    print()
    print(f"# {'positions':<25} {'coefs':<25} {'|V_δ|':>8} {'/2q':>6}")
    print("-" * 75)

    for positions, coefs in cases:
        fhat = [0] * N0
        for pos, c in zip(positions, coefs):
            fhat[pos] = c
        f = evaluate_dft(fhat, L0, P)

        v_delta = 0
        for alphas in product(range(P), repeat=R):
            g = fold_at_alpha(f, chain, list(alphas), P)
            syn = matvec(H_R, g, P)
            if all(x == 0 for x in syn):
                v_delta += 1
                continue
            w, _T, _e = min_wt_via_MDS(syn, H_R, N_R, P, max_w=W_R)
            if w is not None:
                v_delta += 1
        ratio = v_delta / target_bound
        marker = "  ← EXCEEDS" if v_delta > target_bound else ""
        print(f"  {str(positions):<25} {str(coefs):<25} {v_delta:>8} {ratio:>6.3f}{marker}")


if __name__ == '__main__':
    main()
