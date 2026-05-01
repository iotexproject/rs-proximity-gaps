"""g3_stage2_h4_numeric.py — numerically solve Stage 2 system at h=4.

Substitute generic rho values, leave eps as symbol, run sympy groebner
to confirm off-block coefficients vanish under generic conditions.
"""
import sympy as sp
import sys

sys.path.insert(0, "notes/scripts")
from g3_stage2_general_h import (
    compute_R_offblock,
    residue_polys,
    residue_equations,
)


def stage2_eqs(h):
    rho_sym, eps_sym = sp.symbols("rho eps")
    p_low_syms = sp.symbols(f"pL1:{h}")
    p_high_syms = sp.symbols(f"pH1:{h}")
    p_low = {a: p_low_syms[a - 1] for a in range(1, h)}
    p_high = {a: p_high_syms[a - 1] for a in range(1, h)}

    _r_low, _r_high, P_full, R_full = compute_R_offblock(
        h, rho_sym, eps_sym, p_low, p_high
    )
    y = sp.Symbol("y")
    Pa, Ra = residue_polys(h, P_full, R_full, y)
    eqs_by_c = residue_equations(h, Pa, Ra, y)

    all_eqs = []
    for c, expr in eqs_by_c.items():
        deg = sp.degree(expr, y) if expr != 0 else -1
        for k in range(deg + 1):
            ck = sp.expand(expr.coeff(y, k))
            if ck != 0:
                all_eqs.append(ck)
    return all_eqs, p_low_syms, p_high_syms, rho_sym, eps_sym


def test_h(h):
    print(f"\n=== h={h} ===")
    eqs, p_low_syms, p_high_syms, rho_sym, eps_sym = stage2_eqs(h)
    print(f"  {len(eqs)} non-trivial equations, {2*(h-1)} unknowns.")

    e_v = sp.Symbol("e_v")
    for rho_val in [2, 3, 5, 7]:
        subs = {rho_sym: rho_val, eps_sym: e_v}
        eqs_sub = [sp.expand(e.subs(subs)) for e in eqs]
        eqs_sub = [e for e in eqs_sub if e != 0]

        all_p_vars = list(p_low_syms) + list(p_high_syms) + [e_v]
        try:
            G = sp.groebner(eqs_sub, *all_p_vars, order="lex")
        except Exception as exc:
            print(f"  rho={rho_val}: GB failed ({exc})")
            continue
        zeroed = []
        for sym in p_low_syms + p_high_syms:
            rem = G.reduce(sym)[1]
            zeroed.append(rem == 0)
        print(f"  rho={rho_val}: GB has {len(G)} polys, all p_vars → 0: {all(zeroed)}")


def main():
    for h in [2, 3, 4]:
        test_h(h)


if __name__ == "__main__":
    main()
