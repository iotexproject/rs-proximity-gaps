"""g3_step4_mixed_case_check.py — verify Note 0218 Step 4 (sparse-support).

For sign-paired pencil at k=2 toy, ρ=ι, check that no NON-sparse σ_{S_+}
(i.e., σ_{S_+} with mixed i ∈ {1, ..., k-1}) satisfies the joint
constraint:
  σ_{S_+} | x^{2k} - 1 (degree-k divisor)
  σ_{S_-} = (1+ι) z^k - ι σ_{S_+} divides x^{2k} + 1

If no such σ_{S_+} exists for k=2 over F_q (q=17), this confirms Step 4
empirically at toy.
"""
import sympy as sp
from itertools import combinations


def check_at_q(q, k, ι_val, ζ_4k_val):
    """Enumerate degree-k divisors of x^{2k} - 1 in F_q and check σ_{S_-}
    divisibility constraint.

    ζ_4k_val should be a primitive 4k-th root of unity in F_q.
    """
    print(f"\n=== q={q}, k={k} ===")

    # μ_{2k} = ⟨ζ_4k²⟩ (subgroup of order 2k)
    g = pow(ζ_4k_val, 2, q)
    mu_2k = [pow(g, j, q) for j in range(2 * k)]

    # μ_{4k} = ⟨ζ_4k⟩
    mu_4k = [pow(ζ_4k_val, j, q) for j in range(4 * k)]

    # Primitive 4k-th roots = μ_4k \ μ_2k = roots of x^{2k} + 1
    primitive_4k = [z for z in mu_4k if z not in mu_2k]
    print(f"  μ_2k = {mu_2k}, μ_4k = {mu_4k}")
    print(f"  primitive 4k-th roots (roots of x^{2*k}+1): {primitive_4k}")

    # All degree-k divisors of x^{2k} - 1: choose k of 2k roots
    z_sym = sp.Symbol("z")
    valid_count = 0
    sparse_count = 0
    nonsparse_valid = 0
    for chosen in combinations(mu_2k, k):
        # σ_{S_+}(z) = ∏(z - α) for α in chosen
        sigma_plus = sp.Poly(1, z_sym, domain=sp.GF(q))
        for α in chosen:
            sigma_plus = sigma_plus * sp.Poly(z_sym - α, z_sym, domain=sp.GF(q))

        # σ_{S_-}(z) = (1+ι) z^k - ι σ_{S_+}(z), reduce mod q
        sigma_minus = sp.Poly(
            (1 + ι_val) * z_sym**k, z_sym, domain=sp.GF(q)
        ) - sp.Poly(ι_val, z_sym, domain=sp.GF(q)) * sigma_plus

        # Check sigma_minus divides x^{2k} + 1
        target = sp.Poly(z_sym ** (2 * k) + 1, z_sym, domain=sp.GF(q))
        rem = target.rem(sigma_minus)
        if rem == sp.Poly(0, z_sym, domain=sp.GF(q)):
            valid_count += 1
            # Check if sparse: σ_{S_+} should be z^k - r for some r
            coefs = sigma_plus.all_coeffs()
            # coefs[0] = leading (1), then rest
            non_leading_zero = all(c == 0 for c in coefs[1:-1])
            if non_leading_zero:
                sparse_count += 1
                print(f"  SPARSE: chosen={chosen}, σ_+={sigma_plus.as_expr()}, σ_-={sigma_minus.as_expr()}")
            else:
                nonsparse_valid += 1
                print(f"  ⚠ NON-SPARSE valid: chosen={chosen}, σ_+={sigma_plus.as_expr()}, σ_-={sigma_minus.as_expr()}")

    print(f"\n  Total valid (σ_+, σ_-) pairs: {valid_count}")
    print(f"  Sparse: {sparse_count}, Non-sparse valid: {nonsparse_valid}")

    if nonsparse_valid == 0:
        print(f"  ✓ STEP 4 CONFIRMED: only sparse σ_{{S_+}} gives valid σ_{{S_-}}")
    else:
        print(f"  ✗ Step 4 FAILS: non-sparse σ_{{S_+}} also gives valid σ_{{S_-}}")


def find_primitive_nth_root(n, q):
    """Find a primitive n-th root of unity in F_q."""
    if (q - 1) % n != 0:
        return None
    # F_q* is cyclic. Try elements until finding one of order exactly n.
    for g in range(2, q):
        if pow(g, n, q) == 1 and pow(g, n // 2, q) != 1:
            # Check more thoroughly: order should be exactly n
            ok = True
            for d in [n // p for p in [2, 3, 5, 7, 11, 13] if n % p == 0]:
                if pow(g, d, q) == 1:
                    ok = False
                    break
            if ok:
                return g
    return None


def main():
    # k=2: q=17 with ζ_8=9, ι=ζ_8^2=13
    check_at_q(17, 2, 13, 9)

    # k=2: q=41
    # ζ_8 in F_41: needs order 8. F_41* has order 40. element of order 8: order 40/gcd(j,40) = 8, gcd=5.
    # 6 is primitive of F_41*, so 6^5 = 27 has order 8. ι = 27^2 = 32.
    check_at_q(41, 2, 32, 27)

    # k=4: need primitive 16-th root in F_q. q=17 has ζ_16 = 3 (primitive root).
    # ι = ζ_16^4 = 81 mod 17 = 13.
    check_at_q(17, 4, 13, 3)

    # k=4: q=97 (97-1=96=2^5·3, primitive 16-th root exists since 16 | 96).
    z16 = find_primitive_nth_root(16, 97)
    if z16:
        ι_97 = pow(z16, 4, 97)
        print(f"\n[INFO] q=97: ζ_16 = {z16}, ι = ζ_16^4 = {ι_97}")
        check_at_q(97, 4, ι_97, z16)


if __name__ == "__main__":
    main()
