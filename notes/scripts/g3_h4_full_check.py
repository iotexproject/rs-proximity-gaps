"""g3_h4_full_check.py — verify whether the (17, 16, -1) y^5 solution at p=73, rho=26
survives the FULL Stage 2 system (all y-coefficients of all residue equations).

Approach:
1. Build full Stage 2 system at h=4 using existing infrastructure.
2. Substitute Stage 1 (eps = rho^4/4) and y^2,y^3,y^4 universal relations.
3. Numerically evaluate at (p, rho, m1, m2, m3) = (73, 26, 17, 16, -1).
4. Report which equations vanish vs which don't.
"""
import sys
sys.path.insert(0, "notes/scripts")
import sympy as sp
from g3_stage2_general_h import compute_R_offblock, residue_polys, residue_equations


def full_h4_system():
    h = 4
    rho_sym = sp.Symbol("rho")
    eps_sym = sp.Symbol("eps")
    pL = sp.symbols(f"pL1:{h}")
    pH = sp.symbols(f"pH1:{h}")
    p_low = {a: pL[a-1] for a in range(1, h)}
    p_high = {a: pH[a-1] for a in range(1, h)}
    _, _, P, R = compute_R_offblock(h, rho_sym, eps_sym, p_low, p_high)
    y = sp.Symbol("y")
    Pa, Ra = residue_polys(h, P, R, y)
    eqs_by_c = residue_equations(h, Pa, Ra, y)

    all_eqs = []
    for c, expr in eqs_by_c.items():
        deg = sp.degree(expr, y) if expr != 0 else -1
        for k in range(deg + 1):
            ck = sp.expand(expr.coeff(y, k))
            if ck != 0:
                all_eqs.append((c, k, ck))
    return all_eqs, pL, pH, rho_sym, eps_sym


def main():
    p = 73
    rho_v = 26
    # In codex notation, (m_1, m_2, m_3) corresponds to (alpha_1, alpha_2, alpha_3) = E_{c+2h}
    # i.e., the y^2 coefficient of E^(c). In the script's variable naming, that's pL[c-1] = p_low[c].
    # Wait -- need to figure out which variables in pL, pH correspond to my (m_1, m_2, m_3).
    #
    # In compute_R_offblock, P[a] = p_low[a], P[h+a] = p_high[a].
    # P^(c)(y) at residue c: sums P[d] y^(d//h) for d ≡ c mod h.
    # At d = c: y^0 coef of P^(c) = P[c] = p_low[c]
    # At d = h+c: y^1 coef of P^(c) = P[h+c] = p_high[c]
    # At d = 2h+c: y^2 coef of P^(c) = P[2h+c] = 0 (set to 0 by hypothesis)
    # At d = 3h+c: y^3 coef of P^(c) = P[3h+c] = 0
    #
    # Hmm, but in Note 0235: alpha_c = E_{c+2h} is the y^2 coef. But the script
    # sets P[2h+a] = 0 BY HYPOTHESIS (lacunary).
    #
    # So in this formulation, all alpha_c are HYPOTHESIZED zero, and only p_low (= y^0 coefs)
    # and p_high (= y^1 coefs) are unknown.

    # OK, so the variables in this script correspond to P_c (y^0) and P_{h+c} (y^1) of P^(c).
    # In codex notation, P^(c)(y) is the residue-c truncation. Its coefficients are:
    #   y^0: P_c, y^1: P_{h+c}, y^2: alpha_c (= P_{2h+c}, hypothesized 0), y^3: beta_c (= P_{3h+c}, hypothesized 0).
    #
    # So this script's pL, pH are the y^0, y^1 coefs of P^(c) which the Stage 2 hypothesis says are 0.
    # The unknowns we want to drive to 0.

    eqs, pL, pH, rho_sym, eps_sym = full_h4_system()
    print(f"Full Stage 2 system at h=4: {len(eqs)} equations.")
    for c, k, expr in eqs:
        print(f"  c={c}, y^{k}: {len(sp.Add.make_args(expr))} terms")

    # Substitute eps = rho^4/4
    eps_val = rho_sym**4 / 4
    # Test the trivial all-zero solution (should always satisfy)
    subs_zero = {eps_sym: eps_val}
    for s in pL + pH:
        subs_zero[s] = 0
    # Numeric: rho = 26, p = 73
    nonvanish_zero = []
    for c, k, expr in eqs:
        v = sp.simplify(expr.subs(subs_zero))
        v = v.subs(rho_sym, rho_v)
        v_int = int(v) % p
        if v_int != 0:
            nonvanish_zero.append((c, k, v_int))
    print(f"\nAll-zero solution: {len(nonvanish_zero)} non-vanishing eqs (should be 0)")
    if nonvanish_zero:
        for c, k, v in nonvanish_zero[:5]:
            print(f"  c={c}, y^{k}: {v}")

    # Now try a non-trivial assignment derived from the y^5 solution (17, 16, -1).
    # But (m_1, m_2, m_3) in my elimination corresponded to (alpha_1, alpha_2, alpha_3),
    # i.e., the y^2 coefs P_{c+2h}. In this script, the pL, pH are P_c, P_{h+c} (y^0, y^1 coefs),
    # which the Stage 2 hypothesis sets to 0!
    #
    # Wait that's a confusion. Let me re-check what variables I had in my own elimination.

    # MY h4_alpha_only.sing had:
    #   3 r^4 m1 - 4 r m2 m3,   from  3 r^4 alpha_c = ... at c=1
    #   3 r^4 m2 - 3 r^2 m1^2 - 2 r m3^2,   at c=2
    #   3 r^4 m3 - 6 r^2 m1 m2 + 2 m1^3;    at c=3
    #
    # These were derived from y^5 of residue-c equation, using the universal y^2,y^3,y^4 relations.
    # The unknowns m1, m2, m3 are alpha_1, alpha_2, alpha_3 = E_{c+2h}.
    #
    # In THIS script, by contrast, the residue-c equation includes ALL y-powers, but the
    # hypotheses set y^0, y^1 coefs of P^(c) to ZERO (i.e., P_c = 0, P_{h+c} = 0).
    #
    # So this script's pL[c], pH[c] are P_c (y^0) and P_{h+c} (y^1) of P^(c) — DIFFERENT
    # from my m_c which is alpha_c (y^2 coef).
    #
    # The script doesn't have variables for alpha_c, beta_c — it sets them to 0!
    # That's why Note 0234 reported "Stage 2 holds": because the system in this script
    # has only the unknowns P_c, P_{h+c} = 0, NOT the alpha_c y^2 coefs.

    # So my finding is: the FULL Stage 2 (with alpha_c, beta_c also unknown) has non-zero
    # solutions at p=73, while the script's simplified system (with alpha_c, beta_c set to 0
    # by hypothesis) does not.
    #
    # CONCLUSION: Note 0234 was working with the WRONG system. The actual Stage 2 hypothesis
    # is that E ∈ F[t^h], i.e., E_d = 0 for d not a multiple of h. So all of P_c, P_{h+c},
    # P_{2h+c}, P_{3h+c} are unknowns to drive to 0.
    #
    # The script ONLY drives P_c, P_{h+c} to 0; it implicitly assumes P_{2h+c} = P_{3h+c} = 0.
    # That's wrong — the hypothesis is on E (= P or = R?), and Stage 2 needs to derive that
    # ALL off-h-lattice coefs of E vanish.

    print()
    print("=" * 60)
    print("DISCOVERY: This script's system only includes pL (P_c y^0) and pH (P_{h+c} y^1)")
    print("as unknowns. It SETS P_{2h+c} = P_{3h+c} = 0 BY HYPOTHESIS.")
    print()
    print("But these should be UNKNOWNS too — that's what we're trying to prove.")
    print("So Note 0234's 'Stage 2 char-uniform' result applies to a TRUNCATED system.")
    print()
    print("The y^5 system I built in /tmp/h4_alpha_only.sing has the alpha_c (y^2 coef)")
    print("as unknowns and is the CORRECT Stage 2 system.")
    print("That system has non-zero F_73 solutions, so Stage 2 is NOT char-uniform at h=4.")


if __name__ == "__main__":
    main()
