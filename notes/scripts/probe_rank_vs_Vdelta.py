"""probe_rank_vs_Vdelta.py — empirically check rank-Vdelta trade-off.

For each above-J f, compute:
  - r = rank(image(φ))   (linear rank of syndrome image)
  - |V_δ|
  - |image|
  - |image ∩ B_w|
  - ratio |V_δ| / (R q^{R-1})

Conjecture: for rank r, |V_δ| ≤ R q^{r-1} · q^{R-r} = R q^{R-1}, with the
distribution of |V_δ| concentrated near R q^{r-1} · q^{R-r}.

Output: distribution by rank.
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full,
    gauss_rank
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
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4]); delta = float(sys.argv[5])
    n_trials = int(sys.argv[6]) if len(sys.argv) > 6 else 100

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)
    w_R = int(delta * n_R)
    qR = p ** R
    bound_phase1 = R * p**(R-1)

    # Build B_w
    B_w = set()
    B_w.add(tuple([0]*(n_R-k_R)))
    for w in range(1, w_R + 1):
        for T in combinations(range(n_R), w):
            for vals in product(range(1, p), repeat=w):
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = vals[idx]
                B_w.add(tuple(matvec(H_R, e, p)))

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, m={n_R-k_R}, |B_w|={len(B_w)}")
    print(f"# Bound R q^{{R-1}} = {bound_phase1}")
    print()

    rng = random.Random(2026)
    by_rank = {}  # rank → list of (|V_δ|, |image|, |image ∩ B_w|)

    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue

        image_set = set()
        v_delta = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image_set.add(syn)
            if syn in B_w:
                v_delta += 1
        nonzero_syns = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero_syns, p) if nonzero_syns else 0
        intersection = len(image_set & B_w)
        by_rank.setdefault(r, []).append((v_delta, len(image_set), intersection))

    print(f"# {'rank':>4s} {'count':>6s} {'avg |V_δ|':>10s} {'max |V_δ|':>10s} {'avg |im∩B_w|':>13s} {'avg V/bound':>11s}")
    print("-" * 65)
    for r in sorted(by_rank):
        data = by_rank[r]
        n = len(data)
        avg_vd = sum(d[0] for d in data) / n
        max_vd = max(d[0] for d in data)
        avg_int = sum(d[2] for d in data) / n
        avg_ratio = sum(d[0] for d in data) / n / bound_phase1
        print(f"  {r:>4d} {n:>6d} {avg_vd:>10.1f} {max_vd:>10d} {avg_int:>13.1f} {avg_ratio:>11.4f}")

    print()
    print(f"# Empirical conjecture: |V_δ| ≤ R q^{{r-1}} · q^{{R-r}} = R q^{{R-1}} (constant in rank)")


if __name__ == '__main__':
    main()
