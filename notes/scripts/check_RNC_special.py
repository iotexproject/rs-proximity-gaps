"""Check the 2 special above-J f's: image ⊂ Cone(RNC). Verify V_δ ≤ R q^{R-1}."""
import sys, math
from itertools import product

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full,
    gauss_rank, modinv
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


def main():
    p = 97; n0 = 16; k0 = 4; R = 2; delta = 0.45
    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    bound = R * p**(R-1)

    # The 2 special f's from probe_image_in_RNC: sparse_[5,7] and sparse_[4,5]
    # With random coeffs from rng.Random(2026) trial 38 and 46.
    # Just regenerate with monomial coeffs = 1 for both positions.
    cases = [(5, 7), (4, 5)]
    for a, b in cases:
        fhat = [0]*n0; fhat[a] = 1; fhat[b] = 1
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=15)
        # Compute V_δ
        v_delta = 0
        v_exact = 0
        image = set()
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image.add(syn)
            if all(x == 0 for x in syn):
                v_exact += 1
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
            if d is not None and d <= w_R:
                v_delta += 1
        # Linear rank
        nonzero = [list(s) for s in image if any(x != 0 for x in s)]
        r = gauss_rank(nonzero, p) if nonzero else 0
        # Check normalize first nonzero
        v_0 = nonzero[0] if nonzero else None
        v_0_norm = None
        if v_0:
            for i, x in enumerate(v_0):
                if x != 0:
                    inv = modinv(x, p)
                    v_0_norm = tuple((y * inv) % p for y in v_0)
                    break
        # H-lines normalized
        H_lines = []
        for j in range(n_R):
            H_j = [H_R[i][j] for i in range(n_R - k_R)]
            for i, x in enumerate(H_j):
                if x != 0:
                    inv = modinv(x, p)
                    H_lines.append(tuple((y * inv) % p for y in H_j))
                    break
        is_H_line = v_0_norm in H_lines if v_0_norm else None
        print(f"# X^{a}+X^{b}: dist_C0={d0}, image_rank={r}, v_0_norm={v_0_norm}")
        print(f"#   |V_exact|={v_exact}, |V_δ|={v_delta}, bound R·q^{{R-1}}={bound}")
        print(f"#   ratio={v_delta/bound:.4f}, image=H-line? {is_H_line}")
        print()


if __name__ == '__main__':
    main()
