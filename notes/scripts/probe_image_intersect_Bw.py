"""probe_image_intersect_Bw.py — verify proof attempt 3 of note 0099.

For each f, compute:
  - r := dim(span(image(φ)))         (linear span of all syndrome values)
  - image(φ) := {H g(α) : α ∈ F_q^R}    (the actual SET of syndromes attained)
  - B_w := {H e : wt(e) ≤ w}            (low-weight syndrome variety)
  - |image(φ) ∩ B_w|                    (intersection size)

Conjecture: |image(φ) ∩ B_w| ≤ R q^{r-1}, where r = effective rank.

Together with avg fiber size ~ q^{R-r}: |V_δ| ≈ |image(φ) ∩ B_w| · q^{R-r} ≤ R q^{R-1}.

Usage: python3 probe_image_intersect_Bw.py <p> <n_0> <k_0> <R> <delta>
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


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    w_R = int(delta * n_R)
    qR = p ** R

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, n_R-k_R={n_R-k_R}, q^R={qR}")
    print(f"# Conjecture: |image(φ) ∩ B_w| ≤ R q^{{r-1}}")
    print()

    # Build B_w = {H e : wt(e) ≤ w_R}
    print(f"# Building B_w (low-weight syndrome variety)...")
    B_w = set()
    B_w.add(tuple([0]*(n_R-k_R)))  # zero error
    for w in range(1, w_R + 1):
        for T in combinations(range(n_R), w):
            for vals in product(range(1, p), repeat=w):
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = vals[idx]
                syn = tuple(matvec(H_R, e, p))
                B_w.add(syn)
    print(f"# |B_w| = {len(B_w)}")

    # Test f's
    rng = random.Random(2026)
    f_list = []
    cs_a = 2 * (2**R) - 1; cs_b = 2 * (2**R) - 2
    if cs_a < n0 and cs_b < n0:
        fhat = [0]*n0; fhat[cs_a] = 1; fhat[cs_b] = 1
        f_list.append((f"CS:X^{cs_a}+X^{cs_b}", evaluate_dft(fhat, L0, p)))
    for trial in range(20):
        sparsity = rng.choice([2, 3, 4])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f_list.append((f"sparse_{sorted(positions)}", evaluate_dft(fhat, L0, p)))

    print(f"# {'f':40s} {'|im(φ)|':>8s} {'lin rank r':>10s} {'|im∩B_w|':>10s} {'R q^(r-1)':>10s} {'ratio':>7s} {'|V_δ|':>8s}")
    print("-" * 110)

    for fname, f in f_list:
        # Compute image of φ
        image_set = set()
        v_delta = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = syndrome(g, H_R, p)
            image_set.add(syn)
            if syn in B_w:
                v_delta += 1
        # Linear rank of image (treat as vectors)
        nonzero = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero, p) if nonzero else 0

        # Intersection
        intersection = image_set & B_w
        i_size = len(intersection)
        bound = R * p**max(0, r-1) if r > 0 else 1
        ratio = i_size / bound if bound > 0 else float('inf')

        print(f"  {fname:40s} {len(image_set):8d} {r:10d} {i_size:10d} {bound:10d} {ratio:7.3f} {v_delta:8d}")


if __name__ == '__main__':
    main()
