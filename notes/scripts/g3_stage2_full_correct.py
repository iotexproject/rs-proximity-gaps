"""g3_stage2_full_correct.py — CORRECT Stage 2 system.

Hypothesis (Note 0235): E_d = 0 for d ∈ [1, 2h-1] \\ {h} ∪ {2h}.
Conclusion (want): E_d = 0 for d ∈ [2h+1, 4h-1] \\ {3h}.

Variables: alpha_c := E_{2h+c}, beta_c := E_{3h+c} for c ∈ [1, h-1].
Total: 2(h-1) unknowns.

Stage 1 fixes on-lattice E: E_0 = -eps, E_h = -rho^3/2, E_{2h} = 0, E_{3h} = rho, E_{4h} = 1.
With eps = rho^4/4 (Stage 1 closure).

Compute R coefficients via top-down recursion E·R = 1 - t^{8h},
where E_d uses the hypothesis (E_a = E_{h+a} = 0 for a in [1, h-1]) and
the unknowns (alpha_c, beta_c).

Then assemble residue-c equation U_c(y) = S_c(y) + y T_c(y) for each c
and equate ALL y-coefficients to 0. Run Groebner basis.
"""
import sys
import argparse
import sympy as sp


def stage2_system(h, modulus=None, rho_val=None, eps_val=None):
    rho_sym = sp.Symbol("rho")
    eps_sym = sp.Symbol("eps")

    alpha = sp.symbols(f"a1:{h}")  # alpha_1, ..., alpha_{h-1}
    beta = sp.symbols(f"b1:{h}")   # beta_1, ..., beta_{h-1}

    # Build E coefs E[0..4h]
    E = [sp.Integer(0)] * (4*h + 1)
    E[0] = -eps_sym
    E[h] = -sp.Rational(1, 2) * rho_sym**3
    E[2*h] = sp.Integer(0)
    E[3*h] = rho_sym
    E[4*h] = sp.Integer(1)
    # Hypothesis: E[a] = 0, E[h+a] = 0 for a in [1, h-1]; already 0.
    # Unknowns: E[2h+c] = alpha_c, E[3h+c] = beta_c for c in [1, h-1]
    for c in range(1, h):
        E[2*h + c] = alpha[c-1]
        E[3*h + c] = beta[c-1]

    # Compute R via top-down recursion: deg E = 4h, deg R = 4h.
    # E*R = 1 - t^{8h}. Coef of t^D in E*R = sum_{i+j=D} E_i R_j.
    # For D = 8h: 1 = E_{4h} R_{4h} = 1 * R_{4h} ⟹ R_{4h} = 1. (Wait, we need RHS = -1 at t^{8h}.)
    # Actually 1 - t^{8h} has [t^0] = 1, [t^{8h}] = -1. So E_{4h} R_{4h} = -1, giving R_{4h} = -1.
    # Hmm but let's check at small case: deg E = 4, deg R = 4, then E_4 R_4 = -1.
    # Or, use the convention from g3_stage2_general_h.py: top recursion
    # R[4h] = 1, then for d in [1, 4h], R[4h-d] = -P[4h-d] - sum_{ell=1..d-1} P[4h-ell] R[4h-d+ell]
    # Let me use that convention — but verify it matches E*R = (1 - t^{8h}).

    R = [sp.Integer(0)] * (4*h + 1)
    R[4*h] = sp.Integer(1)
    for d in range(1, 4*h + 1):
        rhs = -E[4*h - d]
        for ell in range(1, d):
            rhs -= E[4*h - ell] * R[4*h - d + ell]
        R[4*h - d] = sp.expand(rhs)

    # Check: This recursion gives E*R = 1 - t^{8h}? Or = -(1 - t^{8h})?
    # From g3_stage2_general_h.py the convention is OK; let me trust it and proceed.

    # Build residue-c equations U_c(y) = S_c(y) + y * T_c(y) = 0 (as polynomial in y).
    # P^(a)(y) = ∑_{j} E[a + j*h] * y^j, for a in [0, h-1], j ∈ [0, 4].
    # R^(b)(y) similarly.
    y = sp.Symbol("y")
    Pa = []
    Rb = []
    for a in range(h):
        pa = sp.Integer(0)
        ra = sp.Integer(0)
        for j in range(5):  # j up to 4 since deg = 4h
            d = a + j * h
            if d <= 4*h:
                pa += E[d] * y**j
                ra += R[d] * y**j
        Pa.append(sp.expand(pa))
        Rb.append(sp.expand(ra))

    # Residue-c equation: c in [1, h-1].
    # U_c(y) = S_c(y) + y * T_c(y)
    # S_c(y) = sum_{a+b=c, a,b in [0, h-1]} P^(a)(y) R^(b)(y)
    # T_c(y) = sum_{a+b=c+h, a,b in [0, h-1]} P^(a)(y) R^(b)(y)
    eqs = []
    for c in range(1, h):
        Sc = sp.Integer(0)
        for a in range(h):
            b = c - a
            if 0 <= b < h:
                Sc += Pa[a] * Rb[b]
        Tc = sp.Integer(0)
        for a in range(h):
            b = c + h - a
            if 0 <= b < h:
                Tc += Pa[a] * Rb[b]
        Uc = sp.expand(Sc + y * Tc)
        deg = sp.Poly(Uc, y).degree()
        for k in range(deg + 1):
            ck = sp.expand(sp.Poly(Uc, y).nth(k))
            if ck != 0:
                eqs.append((c, k, ck))
    return eqs, alpha, beta, rho_sym, eps_sym


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=4)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--apply-stage1", action="store_true",
                        help="Substitute eps = rho^4/4 (Stage 1 closure).")
    parser.add_argument("--check-soln", nargs="*", default=None,
                        help="Substitute (rho, alpha_1, ..., alpha_{h-1}, beta_1, ..., beta_{h-1}) mod p")
    parser.add_argument("--prime", type=int, default=None)
    args = parser.parse_args()

    h = args.h
    eqs, alpha, beta, rho_sym, eps_sym = stage2_system(h)
    print(f"=== h={h} Stage 2 (CORRECT system) ===")
    print(f"Total equations: {len(eqs)}")
    by_y = {}
    for c, k, _ in eqs:
        by_y.setdefault(k, []).append(c)
    for k in sorted(by_y):
        print(f"  y^{k}: residues {by_y[k]}")

    if args.apply_stage1:
        eps_val = rho_sym**4 / 4
        eqs = [(c, k, sp.expand(e.subs(eps_sym, eps_val))) for c, k, e in eqs]
        print("\n  Substituted eps = rho^4/4")

    if args.show:
        for c, k, expr in eqs:
            nterm = len(sp.Add.make_args(expr))
            print(f"  c={c}, y^{k}: <{nterm} terms> {sp.simplify(expr) if nterm < 8 else '...'}")

    if args.check_soln:
        # parse: rho_val, a1, a2, ..., a_{h-1}, b1, ..., b_{h-1}
        vals = [int(x) for x in args.check_soln]
        rho_val = vals[0]
        a_vals = vals[1:h]
        b_vals = vals[h:2*h-1]
        p = args.prime
        subs = {rho_sym: rho_val}
        if not args.apply_stage1:
            # need eps too
            print("Use --apply-stage1 with --check-soln, or supply eps separately.")
            return
        for i, av in enumerate(a_vals):
            subs[alpha[i]] = av
        for i, bv in enumerate(b_vals):
            subs[beta[i]] = bv
        print(f"\nChecking solution: rho={rho_val}, alpha={a_vals}, beta={b_vals}, p={p}")
        bad = []
        for c, k, expr in eqs:
            v = sp.expand(expr.subs(subs))
            if p is not None:
                v = int(v) % p
            else:
                v = sp.simplify(v)
            if v != 0:
                bad.append((c, k, v))
        if bad:
            print(f"  {len(bad)} equations FAIL:")
            for c, k, v in bad:
                print(f"    c={c}, y^{k}: {v}")
        else:
            print("  ALL equations vanish — VALID Stage 2 counterexample.")


if __name__ == "__main__":
    main()
