"""g3_path_D_inflation_lift.py — Path D: inflation morphism.

Hypothesis: every half-set witness σ at (n=4k, k) is the inflation
of a half-set witness σ' at (8, 2):

    σ(z) = σ'(z^{k/2})

i.e., σ has support only on multiples of k/2.

If true: V_(n,k) → V_(8,2) is well-defined and surjective on ρ-projection,
giving |B_(n,k)| ≤ |B_(8,2)| = 4 (sign-paired) at all deployment scales.

This script:
1. Compute V(cert+div) at (16, 4) sign-paired via Groebner.
2. For each witness in V, check if support of σ is contained in
   multiples of k/2 = 2 (i.e., p_1 = p_3 = p_5 = p_7 = 0).
3. Confirm: every (16, 4) sign-paired witness inflates from (8, 2).
"""
import time
import sympy as sp


def get_groebner(n, k, a, b, order="lex"):
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(2 * k))
    rho = sp.Symbol("rho")
    t = 2 * k

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    rem_n = sp.Poly(sp.rem(x**n - 1, P, x), x)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]

    eqs = [e for e in cert_eqs + div_eqs if e != 0]
    t0 = time.time()
    G = sp.groebner(eqs, *p, rho, order=order)
    t1 = time.time()
    print(f"  GB ({order}) in {t1-t0:.2f}s: {len(G)} polys")
    return G, p, rho


def check_support_constraint(G, p, n, k):
    """For each odd-index p_i (where i % (k/2) != 0), check if p_i is in
    the GB as a generator (forced to zero).

    For (16, 4): k/2 = 2, allowed support = {0, 2, 4, 6}.
    Forced zero: p_1, p_3, p_5, p_7.
    """
    half = k // 2
    forced_zero_idx = [i for i in range(2 * k) if i % half != 0]
    print(f"  expected forced zero: p_i for i in {forced_zero_idx}")

    found_forced = []
    for g in G:
        # Each g is a polynomial; check if it equals p_i for some forced index
        for i in forced_zero_idx:
            if g == p[i]:
                found_forced.append(i)
    print(f"  found p_i = 0 in GB for i in {sorted(set(found_forced))}")
    if set(found_forced) >= set(forced_zero_idx):
        print(f"  ✓ INFLATION HYPOTHESIS VERIFIED: every p_i (i not multiple of k/2) is forced zero.")
        return True
    else:
        missing = set(forced_zero_idx) - set(found_forced)
        print(f"  ✗ Missing forced zeros: {sorted(missing)}")
        return False


def analyze(n, k, a, b):
    print(f"\n=== (n={n}, k={k}, a={a}, b={b}) ===")
    G, p, rho = get_groebner(n, k, a, b, order="lex")
    print(f"  GB:")
    for i, g in enumerate(G):
        print(f"    [{i}] {g}")
    success = check_support_constraint(G, p, n, k)
    return success


def main():
    # Sign-paired toy and (16, 4)
    cases_signpaired = [
        (8, 2, 2, 6),   # toy
        (16, 4, 4, 12), # deployment
    ]
    # Non-sign-paired (k, 2k) at toy and (16, 4)
    cases_k2k = [
        (8, 2, 2, 4),
        (16, 4, 4, 8),
    ]
    for case in cases_signpaired + cases_k2k:
        analyze(*case)


if __name__ == "__main__":
    main()
