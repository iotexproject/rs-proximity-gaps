"""g3_k2k_mixed_k3.py — empirically test (k, 2k) family mixed case at k=3.

For (k, 2k) at k=3, n=12: σ_+ degree 3 | x^6 - 1, σ_- degree 3 | x^6 + 1.
For ρ = 1+ι (one of the bad ρ for k=3, k=2 toy): pigeonhole permits
(a, i) = (2, 2) mixed case.

Brute force: enumerate all 9 × 9 = 81 (S_+, σ_-roots) configurations,
check if any non-sparse σ_+ satisfies all constraints AND σ_- divides
x^6 + 1.

Need q with primitive 12-th root: q = 13 (12 | 12). ζ_12 = ?
F_13* has order 12. Primitive root: 2 (since 2 has order 12 mod 13).
"""
import sympy as sp
from itertools import combinations


def main():
    q = 13
    z12 = 2  # primitive 12-th root in F_13
    z6 = pow(z12, 2, q)  # primitive 6-th root: z6^6 = 1
    z3 = pow(z12, 4, q)  # primitive 3-th root
    z4 = pow(z12, 3, q)  # primitive 4-th root = ι
    ι = z4
    print(f"q={q}, ζ_12={z12}, ζ_6={z6}, ζ_3={z3}, ι={ι}")

    # μ_6 = ⟨ζ_6⟩
    mu_6 = [pow(z6, j, q) for j in range(6)]
    # μ_12 = ⟨ζ_12⟩
    mu_12 = [pow(z12, j, q) for j in range(12)]
    # μ_12 \ μ_6 = primitive 12-th non-6-th roots = roots of x^6 + 1
    primitive_12 = [z for z in mu_12 if z not in mu_6]

    print(f"μ_6 = {mu_6}")
    print(f"primitive 12-th non-6-th (roots of x^6+1) = {primitive_12}")

    # 3-rd roots of unity: subset of μ_6 with z^3 = 1
    third_roots = [z for z in mu_6 if pow(z, 3, q) == 1]
    minus_third = [z for z in mu_6 if pow(z, 3, q) == q - 1]
    print(f"z^3 = 1 (in μ_6): {third_roots}")
    print(f"z^3 = -1 (in μ_6): {minus_third}")

    # cube roots of ι and -ι in primitive 12-th roots
    iota = ι
    neg_iota = (q - ι) % q
    cube_root_iota = [z for z in primitive_12 if pow(z, 3, q) == iota]
    cube_root_neg_iota = [z for z in primitive_12 if pow(z, 3, q) == neg_iota]
    print(f"z^3 = ι in primitive 12-th: {cube_root_iota}")
    print(f"z^3 = -ι in primitive 12-th: {cube_root_neg_iota}")

    # ρ = 1 + ι in F_13
    ρ = (1 + ι) % q
    print(f"ρ = 1+ι = {ρ}")
    # Check ρ^4 = -4 mod 13
    print(f"ρ^4 mod q = {pow(ρ, 4, q)}, expected -4 = {q - 4}")

    # Targets:
    # L(α) = -1 if α^3 = 1; L(α) = +1 if α^3 = -1
    # L(γ) = (1+ι)/ι · γ^3 - γ^3? Let me recompute.
    # σ_+(γ) = 2/ρ at σ_-roots.
    # Actually for (k, 2k): from my Note 0218 analysis,
    # σ_+(γ) c = -2 where c = leading of u_+, c = -ρ for the (k, 2k) case.
    # So σ_+(γ) = -2/(-ρ) = 2/ρ.
    # L(γ) = σ_+(γ) - γ^k = 2/ρ - γ^k.

    inv_ρ = pow(ρ, q - 2, q)
    two_over_ρ = (2 * inv_ρ) % q

    # mixed case (a, i) = (2, 2): 2 α with α^3=1, 1 α with α^3=-1; 2 γ with γ^3=ι, 1 γ with γ^3=-ι.

    z_sym = sp.Symbol("z")

    success_count = 0
    sparse_count = 0
    nonsparse_count = 0
    for chosen_pos1 in combinations(third_roots, 2):
        for chosen_neg1 in combinations(minus_third, 1):
            for chosen_pos_iota in combinations(cube_root_iota, 2):
                for chosen_neg_iota in combinations(cube_root_neg_iota, 1):
                    α_set = list(chosen_pos1) + list(chosen_neg1)
                    σ_minus_roots = list(chosen_pos_iota) + list(chosen_neg_iota)

                    # σ_+(z) = ∏(z - α) for α ∈ α_set
                    σ_plus = sp.Poly(1, z_sym, domain=sp.GF(q))
                    for α in α_set:
                        σ_plus = σ_plus * sp.Poly(z_sym - α, z_sym, domain=sp.GF(q))

                    # Check σ_+(γ) = 2/ρ at all σ-_roots
                    valid = True
                    for γ in σ_minus_roots:
                        v = σ_plus.eval(γ)
                        if int(v) % q != two_over_ρ:
                            valid = False
                            break
                    if valid:
                        # Check σ_+ | x^6 - 1
                        x6_minus_1 = sp.Poly(z_sym**6 - 1, z_sym, domain=sp.GF(q))
                        rem = x6_minus_1.rem(σ_plus)
                        if rem != sp.Poly(0, z_sym, domain=sp.GF(q)):
                            valid = False
                    if valid:
                        success_count += 1
                        # Check sparse
                        coefs = σ_plus.all_coeffs()
                        if all(int(c) % q == 0 for c in coefs[1:-1]):  # all middle = 0
                            sparse_count += 1
                            if success_count <= 5:
                                print(f"  SPARSE: α_set={α_set}, σ_-_roots={σ_minus_roots}, σ_+={σ_plus.as_expr()}")
                        else:
                            nonsparse_count += 1
                            if nonsparse_count <= 5:
                                print(f"  ⚠ NON-SPARSE: α_set={α_set}, σ_-_roots={σ_minus_roots}, σ_+={σ_plus.as_expr()}")

    print(f"\nTotal valid configurations: {success_count}")
    print(f"Sparse: {sparse_count}, Non-sparse: {nonsparse_count}")
    if nonsparse_count == 0:
        print("✓ MIXED CASE INFEASIBLE: only sparse σ_+ at (k, 2k) k=3 mixed.")
    else:
        print("✗ Mixed case has solutions!")


if __name__ == "__main__":
    main()
