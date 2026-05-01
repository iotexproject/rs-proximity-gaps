"""g3_stage2_h7_grevlex.py — h=7 modular GB with grevlex order (often much faster).
Falls back to lex if grevlex hits issues.
"""
import sys
import time

import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_general_h import (
    compute_R_offblock,
    residue_polys,
    residue_equations,
)


def test_h_grevlex(h, prime, rho_val, eps_val):
    print(f"\n=== h={h}, char={prime}, rho={rho_val}, eps={eps_val} ===")
    rho_sym, eps_sym = sp.symbols("rho eps")
    p_low_syms = sp.symbols(f"pL1:{h}")
    p_high_syms = sp.symbols(f"pH1:{h}")
    p_low = {a: p_low_syms[a - 1] for a in range(1, h)}
    p_high = {a: p_high_syms[a - 1] for a in range(1, h)}

    t0 = time.time()
    _, _, P_full, R_full = compute_R_offblock(
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
    print(f"  System built in {time.time()-t0:.2f}s, {len(all_eqs)} eqs.")

    subs = {rho_sym: rho_val, eps_sym: eps_val}
    eqs_sub = [sp.expand(e.subs(subs)) for e in all_eqs]
    eqs_sub = [e for e in eqs_sub if e != 0]

    p_vars = list(p_low_syms) + list(p_high_syms)
    print(f"  vars={len(p_vars)}, eqs={len(eqs_sub)}")

    # Try grevlex
    t1 = time.time()
    print("  Computing GB (grevlex)...")
    try:
        G = sp.groebner(
            eqs_sub, *p_vars, order="grevlex", domain=sp.GF(prime)
        )
    except Exception as exc:
        print(f"  GB failed: {exc}")
        return
    print(f"  GB ({len(G)} polys, grevlex) in {time.time()-t1:.2f}s.")

    # Reduction check — for grevlex, p_a in ideal iff reduction = 0
    print("  Reduction of p_vars mod GB:")
    all_zero = True
    for sym in p_vars:
        rem = G.reduce(sym)[1]
        if rem != 0:
            all_zero = False
        print(f"    {sym}: {rem}")
    print(f"  All p_vars → 0: {all_zero}")


def main():
    for h in [7, 8, 9, 10, 12, 16]:
        test_h_grevlex(h, 17, 3, 16)


if __name__ == "__main__":
    main()
