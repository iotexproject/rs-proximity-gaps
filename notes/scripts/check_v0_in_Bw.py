"""check_v0_in_Bw.py — for the 2 special rank-1 above-J f's at p=97 R=2,
check if v_0 = (1, 0, 0) is in B_w for various w.

This decides whether Path γ structural claim extends to higher w.
"""
import sys
from itertools import combinations, product

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, parity_check, matvec
)


def main():
    p = 97; n0 = 16; k0 = 4; R = 2
    chain = setup_chain(p, n0, k0, R=R)
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    m = n_R - k_R

    print(f"# Setup: p={p}, n_R={n_R}, k_R={k_R}, m={m}")
    print(f"# H_R columns:")
    for j in range(n_R):
        H_j = [H_R[i][j] for i in range(m)]
        print(f"#   H_{j} = {H_j}")
    print()

    target = (1, 0, 0)
    print(f"# Looking for min-weight e with H · e = {target}")

    for w in range(1, n_R + 1):
        found = False
        for T in combinations(range(n_R), w):
            for vals in product(range(1, p), repeat=w):
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = vals[idx]
                syn = tuple(matvec(H_R, e, p))
                if syn == target:
                    print(f"  Found wt-{w} solution: e_T={T}, vals={vals}")
                    found = True
                    break
            if found: break
        if found:
            print(f"# *** Min weight = {w} for syndrome (1,0,0) ***")
            break
    else:
        print(f"# No solution found up to wt {n_R}")

    # Conclusion:
    # If min wt = 1: v_0 ∈ B_1 → falsifier (we know it's NOT in B_1 from prior probe)
    # If min wt = 2: v_0 ∈ B_2 → falsifier of Path γ for w_R=2
    # If min wt = 3: v_0 ∉ B_2 → safe at w_R=2
    # If min wt = 4: v_0 ∉ B_3 → safe at w_R=3 (full code)


if __name__ == '__main__':
    main()
