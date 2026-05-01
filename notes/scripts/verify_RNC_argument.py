"""verify_RNC_argument.py — verify that V_δ ⊆ {L_f(α) = 0} where L_f comes from
the rational normal conic equation.

For n_R - k_R = 3: RNC equation in syndrome space σ = (σ_0, σ_1, σ_2):
  Q(σ) = σ_0 σ_2 - σ_1² = 0

V_δ ⊆ φ^{-1}(B_1) ⊆ φ^{-1}(Cone(RNC)) = {α : Q(φ(α)) = 0}.

Test: for each α in V_δ, check Q(φ(α)) = 0.
Also check: |zero locus of Q∘φ| ≤ 2R q^{R-1} (SZ bound).

For multiple syndrome dimensions m = n_R - k_R, RNC is cut by all 2x2 Hankel minors:
  σ_i σ_j - σ_k σ_l = 0 for i+j = k+l, e.g., σ_0 σ_2 - σ_1², σ_1 σ_3 - σ_2², ...
"""
from __future__ import annotations
import sys, time, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full
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


def hankel_2x2_minors(sigma, p):
    """Return list of 2x2 Hankel minors of sigma. Each minor σ_i σ_j - σ_k σ_l
    for i+j = k+l, i,j,k,l ∈ [m] = [len(sigma)]."""
    m = len(sigma)
    minors = []
    # All pairs (a, b) with a < b in [m]: minor = σ_a · σ_b - σ_{(a+b)//2}²
    # But (a+b) must be even; if odd, no Hankel minor.
    # General Hankel minors: σ_a σ_b - σ_c σ_d for a+b = c+d, {a,b} ≠ {c,d}.
    seen = set()
    for s in range(0, 2*(m-1) + 1):  # a+b = s
        pairs = [(a, s-a) for a in range(max(0, s-m+1), min(m-1, s)+1) if a <= s-a < m and a < s-a]
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                (a, b), (c, d) = pairs[i], pairs[j]
                key = tuple(sorted([(a,b), (c,d)]))
                if key in seen: continue
                seen.add(key)
                val = (sigma[a] * sigma[b] - sigma[c] * sigma[d]) % p
                minors.append(((a,b,c,d), val))
        # Also "square" minor σ_a² where a+a = s (if s even, a = s/2): part of above
    # Also include σ_i σ_j - σ_k² for i+j=2k, e.g., (0,2,1,1): σ_0 σ_2 - σ_1²
    for s in range(0, 2*(m-1) + 1):
        if s % 2 == 0:
            k = s // 2
            for a in range(max(0, s-m+1), s):
                b = s - a
                if a < b < m:
                    val = (sigma[a] * sigma[b] - sigma[k] * sigma[k]) % p
                    minors.append(((a,b,k,k), val))
    return minors


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
    bound_phase1 = R * p**(R-1)
    bound_2R = 2 * R * p**(R-1)
    m = n_R - k_R

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}, δ={delta}")
    print(f"# n_R={n_R}, k_R={k_R}, w_R={w_R}, m=n_R-k_R={m}, q^R={qR}")
    print(f"# Phase 1 bound: R q^{{R-1}} = {bound_phase1}")
    print(f"# RNC bound: 2R q^{{R-1}} = {bound_2R}")
    print()

    # Test that all H-columns lie on RNC (sanity check for w=1 case)
    print("# === Sanity check: H_j on RNC ===")
    for j in range(n_R):
        H_j = [H_R[i][j] for i in range(m)]
        minors = hankel_2x2_minors(H_j, p)
        all_zero = all(v == 0 for _, v in minors)
        print(f"#   j={j}: H_j={H_j}, all_minors_zero={all_zero}")
    print()

    # Build f's
    rng = random.Random(2026)
    f_list = []
    cs_a = 2 * (2**R) - 1; cs_b = 2 * (2**R) - 2
    if k0 <= cs_a < n0 and k0 <= cs_b < n0:
        fhat = [0]*n0; fhat[cs_a] = 1; fhat[cs_b] = 1
        f_list.append((f"CS:X^{cs_a}+X^{cs_b}", evaluate_dft(fhat, L0, p)))
    for trial in range(15):
        sparsity = rng.choice([2, 3, 4])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f_list.append((f"sparse_{sorted(positions)}", evaluate_dft(fhat, L0, p)))

    print(f"# === Test: V_δ ⊆ {{Q∘φ = 0}} ===")
    print(f"# {'f':40s} {'|V_δ|':>8s} {'all in RNC?':>12s} {'|RNC pre|':>10s} {'≤ 2R q^{R-1}?':>14s}")
    print("-" * 90)

    for fname, f in f_list:
        v_delta = 0
        v_in_rnc = 0
        all_minors_vanish = True
        rnc_preimage_size = 0
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = matvec(H_R, g, p)
            d, _ = dist_to_code_full(g, H_R, n_R, k_R, p, max_w=w_R)
            in_Vdelta = (d is not None and d <= w_R)

            # Check RNC: all 2x2 Hankel minors should vanish
            minors = hankel_2x2_minors(syn, p)
            in_RNC = all(v == 0 for _, v in minors)

            if in_RNC:
                rnc_preimage_size += 1
            if in_Vdelta:
                v_delta += 1
                if in_RNC:
                    v_in_rnc += 1
                else:
                    all_minors_vanish = False
                    if v_in_rnc < 5:  # report first few violations
                        print(f"  ⚠ V_δ point NOT on RNC: α={alphas}, syn={syn}, minors={minors}")

        status_in_rnc = "YES" if v_in_rnc == v_delta and v_delta > 0 else (
            "vacuous" if v_delta == 0 else "NO ⚠")
        sz_check = "YES" if rnc_preimage_size <= bound_2R else "NO ⚠"
        print(f"  {fname:40s} {v_delta:8d} {status_in_rnc:>12s} {rnc_preimage_size:10d} {sz_check:>14s}")

    print()
    print(f"# Summary: V_δ ⊆ φ^{{-1}}(RNC cone) = sanity + SZ → |V_δ| ≤ 2R q^{{R-1}}")


if __name__ == '__main__':
    main()
