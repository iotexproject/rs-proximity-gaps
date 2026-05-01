"""g3_stage2_general_h.py — automated Stage 2 derivation at general h.

Following the framework of Notes 0226 (h=2) and 0227 (h=3), compute the
residue-c block equations of P*R = x^{8h} - 1 modulo Stage 1 and present
them as a polynomial system in (p_a, p_{h+a})_{a=1..h-1} with parameters
(rho, eps).

Then run Groebner basis to confirm locator gap and report the
"bad characteristic" content of the eliminator.
"""
import sys
import sympy as sp


def stage1_P0_R0(rho, eps):
    """Stage 1 result for P^(0)(y) and R^(0)(y) at general h (Note 0225).
    Both have degree 4 in y."""
    y = sp.Symbol("y")
    P0 = y**4 + rho * y**3 - sp.Rational(1, 2) * rho**3 * y - eps
    R0 = y**4 - rho * y**3 + rho**2 * y**2 - sp.Rational(1, 2) * rho**3 * y + eps
    return P0, R0, y


def compute_R_offblock(h, rho, eps, p_low, p_high):
    """Compute R coefficients at off-h-lattice positions via top recursion.
    p_low[a] = p_a (a=1..h-1), p_high[a] = p_{h+a} (a=1..h-1).
    Returns r_low[a] = R_a, r_high[a] = R_{h+a}."""
    # Build full P array (P_d for d in [0, 4h]).
    P = [None] * (4 * h + 1)
    P[0] = -eps
    P[h] = -sp.Rational(1, 2) * rho**3
    P[2 * h] = sp.Integer(0)
    P[3 * h] = rho
    P[4 * h] = sp.Integer(1)
    for a in range(1, h):
        P[a] = p_low[a]
        P[h + a] = p_high[a]
        # Off-block residues a at top positions (>= 2h+1):
        # Positions 2h+a, 3h+a have P = 0 (only on-h-lattice has nonzero
        # high coefs except 3h itself).
        P[2 * h + a] = sp.Integer(0)
        P[3 * h + a] = sp.Integer(0)
    # Top recursion: R_{4h-d} = -P_{4h-d} - sum_{l=1..d-1} P_{4h-l} R_{4h-d+l}
    R = [None] * (4 * h + 1)
    R[4 * h] = sp.Integer(1)
    for d in range(1, 4 * h + 1):
        rhs = -P[4 * h - d]
        for ell in range(1, d):
            rhs -= P[4 * h - ell] * R[4 * h - d + ell]
        R[4 * h - d] = sp.expand(rhs)
    r_low = {a: R[a] for a in range(1, h)}
    r_high = {a: R[h + a] for a in range(1, h)}
    return r_low, r_high, P, R


def residue_polys(h, P_full, R_full, y):
    """Compute P^(a)(y), R^(a)(y) for a in [0, h-1]."""
    Pa = [sp.Integer(0)] * h
    Ra = [sp.Integer(0)] * h
    for d in range(4 * h + 1):
        a = d % h
        e = d // h
        Pa[a] += P_full[d] * y**e
        Ra[a] += R_full[d] * y**e
    return [sp.expand(p) for p in Pa], [sp.expand(r) for r in Ra]


def residue_equations(h, Pa, Ra, y):
    """For c in [1, h-1], compute residue-c equation = 0."""
    eqs_by_c = {}
    for c in range(1, h):
        s = sp.Integer(0)
        for a in range(h):
            b = c - a
            if 0 <= b < h:
                s += Pa[a] * Ra[b]
        # wrap: a + b = c + h
        wrap = sp.Integer(0)
        for a in range(h):
            b = c + h - a
            if 0 <= b < h:
                wrap += Pa[a] * Ra[b]
        s = sp.expand(s + y * wrap)
        eqs_by_c[c] = s
    return eqs_by_c


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=4)
    parser.add_argument("--show-eqs", action="store_true")
    parser.add_argument("--show-R", action="store_true")
    parser.add_argument("--gb", action="store_true", default=True)
    args = parser.parse_args()

    h = args.h
    rho, eps = sp.symbols("rho eps")
    p_low_syms = sp.symbols(f"pL1:{h}")  # p_1, ..., p_{h-1}
    p_high_syms = sp.symbols(f"pH1:{h}")  # p_{h+1}, ..., p_{2h-1}
    p_low = {a: p_low_syms[a - 1] for a in range(1, h)}
    p_high = {a: p_high_syms[a - 1] for a in range(1, h)}

    print(f"=== h={h}, k={2*h}, n={8*h}, deg P = {4*h} ===")
    print(f"Off-block unknowns: {2 * (h - 1)} (p_low and p_high for a=1..{h-1})")

    r_low, r_high, P_full, R_full = compute_R_offblock(h, rho, eps, p_low, p_high)
    if args.show_R:
        print("\nR off-block coefs:")
        for a in range(1, h):
            print(f"  R_{a} = {r_low[a]}")
            print(f"  R_{h + a} = {r_high[a]}")

    y = sp.Symbol("y")
    Pa, Ra = residue_polys(h, P_full, R_full, y)
    if args.show_R:
        for a in range(h):
            print(f"  P^({a})(y) = {Pa[a]}")
            print(f"  R^({a})(y) = {Ra[a]}")

    eqs_by_c = residue_equations(h, Pa, Ra, y)

    all_eqs = []
    for c, expr in eqs_by_c.items():
        # Extract coefficients
        deg = sp.degree(expr, y) if expr != 0 else -1
        print(f"\nResidue-{c} equation polynomial degree in y: {deg}")
        for k in range(deg + 1):
            ck = sp.expand(expr.coeff(y, k))
            if ck != 0:
                if args.show_eqs:
                    print(f"  y^{k}: {ck} = 0")
                else:
                    nterms = len(sp.Add.make_args(ck))
                    print(f"  y^{k}: <{nterms} terms>")
                all_eqs.append(ck)

    print(f"\nTotal non-trivial equations: {len(all_eqs)}")
    print(f"Variables: {2*(h-1)} (p_low + p_high), plus eps, rho.")

    if args.gb:
        print("\nGroebner basis (lex, p first, eps, rho last)...")
        all_vars = list(p_low_syms) + list(p_high_syms) + [eps, rho]
        try:
            G = sp.groebner(all_eqs, *all_vars, order="lex")
        except Exception as e:
            print(f"  GB failed: {e}")
            return
        print(f"  GB has {len(G)} polys.")

        # Reduce each p_var mod GB.
        print("\nReduction of unknowns mod GB:")
        for sym in p_low_syms + p_high_syms:
            try:
                rem = G.reduce(sym)[1]
                print(f"  {sym} reduces to: {rem}")
            except Exception as e:
                print(f"  {sym}: reduce failed ({e})")

        # Find pure (eps, rho) elements in GB.
        elim = []
        offblock_syms = set(p_low_syms) | set(p_high_syms)
        for g in G:
            if g.free_symbols.isdisjoint(offblock_syms):
                elim.append(g)
        print(f"\nEliminator polynomials (in eps, rho only): {len(elim)}")
        for e in elim:
            print(f"  {e}")


if __name__ == "__main__":
    main()
